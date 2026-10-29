"""Pinned Rust SysML v2 compiler adapter with isolated source snapshots."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform as host_platform
import shutil
import signal
import subprocess
import sys
import tempfile
import unicodedata

from .artifacts import publish_items, write_json
from .errors import DgraphError
from .viewspec import validate_output_directory


EXPECTED_SHA256 = "674fce28512a772d1886ff2397f5f02dda66265299c67c01f5cc36eaf00207f6"
VENDOR_ROOT = Path(__file__).resolve().parent / "vendor/sysml"
COMPILER = VENDOR_ROOT / "bin/sysml"
TOOLCHAIN = VENDOR_ROOT / "toolchain.json"
MAX_FILES = 128
MAX_SOURCE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_BYTES = 10 * 1024 * 1024
MAX_SOURCE_NAME = 128
MAX_PROCESS_OUTPUT = 16 * 1024 * 1024
COMPILER_TIMEOUT = 30
ANALYSIS_RESULTS = (
    "parse.json",
    "parse.stderr.log",
    "check.json",
    "check.stderr.log",
    "export.json",
)


def _validate_files(files):
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise DgraphError(
            "invalid-sysml-input",
            f"Provide 1-{MAX_FILES} source files.",
            field="files",
            suggestion="Submit a non-empty array of {name, content} objects.",
        )
    total = 0
    names = set()
    result = []
    for index, file in enumerate(files):
        field = f"files[{index}]"
        if not isinstance(file, dict) or set(file) != {"name", "content"}:
            raise DgraphError("invalid-sysml-input", "Each file requires exactly name and content.", field=field)
        name, content = file["name"], file["content"]
        if not isinstance(name, str) or not isinstance(content, str):
            raise DgraphError("invalid-sysml-input", "Each file requires string name and UTF-8 content.", field=field)
        if not name or len(name) > MAX_SOURCE_NAME or "\\" in name or "\x00" in name:
            raise DgraphError("invalid-sysml-input", f"Invalid source name: {name!r}", field=f"{field}.name")
        path = PurePosixPath(name)
        canonical = path.as_posix()
        if path.is_absolute() or ".." in path.parts or canonical in {".", ""} or path.suffix not in {".sysml", ".kerml"}:
            raise DgraphError(
                "invalid-sysml-input",
                f"Unsafe or unsupported source name: {name}",
                field=f"{field}.name",
                suggestion="Use a relative .sysml or .kerml path without '..'.",
            )
        filesystem_key = unicodedata.normalize("NFC", canonical).casefold()
        if filesystem_key in names:
            raise DgraphError("invalid-sysml-input", f"Duplicate source name: {canonical}", field=f"{field}.name")
        names.add(filesystem_key)
        if "\x00" in content:
            raise DgraphError("invalid-sysml-input", f"Source {canonical} contains a NUL byte.", field=f"{field}.content")
        byte_count = len(content.encode("utf-8"))
        if byte_count > MAX_SOURCE_BYTES:
            raise DgraphError("sysml-input-limit", f"Source {canonical} exceeds 5 MiB.", field=f"{field}.content")
        total += byte_count
        result.append({"name": canonical, "content": content})
    if total > MAX_TOTAL_BYTES:
        raise DgraphError("sysml-input-limit", "The source workspace exceeds 10 MiB.")
    return result


def _toolchain():
    try:
        value = json.loads(TOOLCHAIN.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DgraphError("compiler-integrity", f"Cannot read pinned compiler metadata: {error}", path=TOOLCHAIN) from error
    if not isinstance(value, dict):
        raise DgraphError("compiler-integrity", "Pinned compiler metadata is not an object.", path=TOOLCHAIN)
    return value


def compiler_supported():
    """Return whether the bundled binary can execute on this host."""
    if not COMPILER.is_file():
        return False
    try:
        metadata = _toolchain()
        target = metadata.get("platform")
        file_hash = hashlib.sha256(COMPILER.read_bytes()).hexdigest()
    except (DgraphError, OSError):
        return False
    if file_hash != EXPECTED_SHA256:
        return False
    if target == "aarch64-apple-darwin":
        return sys.platform == "darwin" and host_platform.machine().lower() in {"arm64", "aarch64"}
    return False


def _require_compiler():
    if not COMPILER.is_file():
        raise DgraphError(
            "compiler-missing",
            f"Pinned compiler not found: {COMPILER}",
            path=COMPILER,
            suggestion="Install the package with its vendor/sysml payload.",
        )
    digest = hashlib.sha256(COMPILER.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise DgraphError("compiler-integrity", "Pinned compiler SHA-256 does not match.", path=COMPILER)
    target = _toolchain().get("platform")
    if not compiler_supported():
        raise DgraphError(
            "compiler-unavailable",
            f"The bundled SysML compiler targets {target}; this host is {sys.platform}/{host_platform.machine()}.",
            path=COMPILER,
            suggestion="Run dgraph on the pinned compiler platform or provide a separately verified compiler build.",
        )
    return digest, _toolchain()


def _resource_limits():
    try:
        import resource
    except ImportError:
        return
    limits = (
        (resource.RLIMIT_CORE, (0, 0)),
        (resource.RLIMIT_CPU, (COMPILER_TIMEOUT, COMPILER_TIMEOUT + 2)),
        (resource.RLIMIT_FSIZE, (MAX_PROCESS_OUTPUT, MAX_PROCESS_OUTPUT)),
    )
    for name, value in limits:
        try:
            resource.setrlimit(name, value)
        except (OSError, ValueError):
            pass


def _run(command, cwd, timeout=COMPILER_TIMEOUT):
    cwd = Path(cwd)
    stdout_path = None
    stderr_path = None
    process = None
    env = {
        "NO_COLOR": "1",
        "TMPDIR": str(cwd),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", os.environ.get("LANG", "C.UTF-8")),
        "RUST_BACKTRACE": "0",
    }
    try:
        stdout_handle = tempfile.NamedTemporaryFile(prefix=".compiler-stdout-", dir=cwd, delete=False)
        stderr_handle = tempfile.NamedTemporaryFile(prefix=".compiler-stderr-", dir=cwd, delete=False)
        stdout_path, stderr_path = Path(stdout_handle.name), Path(stderr_handle.name)
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=True,
                preexec_fn=_resource_limits,
            )
        finally:
            stdout_handle.close()
            stderr_handle.close()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as error:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                process.kill()
            process.wait()
            raise DgraphError(
                "compiler-timeout",
                f"Compiler exceeded {timeout} seconds and its process group was terminated.",
                path=COMPILER,
                retryable=True,
            ) from error
        if stdout_path.stat().st_size > MAX_PROCESS_OUTPUT or stderr_path.stat().st_size > MAX_PROCESS_OUTPUT:
            raise DgraphError("compiler-output-limit", f"Compiler output exceeded {MAX_PROCESS_OUTPUT} bytes.", path=cwd)
        return subprocess.CompletedProcess(
            command,
            process.returncode,
            stdout_path.read_bytes(),
            stderr_path.read_bytes(),
        )
    except DgraphError:
        raise
    except OSError as error:
        code = "compiler-unavailable" if getattr(error, "errno", None) in {8, 126} else "compiler-launch"
        raise DgraphError(
            code,
            f"Could not launch the SysML compiler: {error}",
            path=COMPILER,
            suggestion="Verify that the bundled binary matches the host platform and is executable.",
        ) from error
    finally:
        if process is not None and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                process.kill()
            process.wait()
        for path in (stdout_path, stderr_path):
            if path is not None:
                try:
                    path.unlink()
                except OSError:
                    pass


def _diagnostics(parse, check):
    result = []
    if isinstance(parse, dict):
        files = parse.get("files", [])
        if not isinstance(files, list):
            files = []
        for file in files:
            if not isinstance(file, dict):
                continue
            for error in file.get("errors", []):
                error = error if isinstance(error, dict) else {"message": str(error)}
                result.append(
                    {
                        "phase": "parse",
                        "file": file.get("path", ""),
                        "message": error.get("message", ""),
                        "line": error.get("line"),
                        "column": error.get("column"),
                    }
                )
        unreadable = parse.get("unreadable", [])
        if not isinstance(unreadable, list):
            unreadable = []
        for path in unreadable:
            result.append({"phase": "parse", "file": str(path), "message": "Unreadable source"})
    if isinstance(check, dict):
        for category in ("parseErrors", "unresolved", "collisions", "violations", "unreadable"):
            errors = check.get(category, [])
            if not isinstance(errors, list):
                errors = [errors]
            for error in errors:
                if isinstance(error, dict):
                    result.append(
                        {
                            "phase": "check",
                            "category": category,
                            "file": error.get("path", error.get("file", "")),
                            "message": error.get("message", error.get("reason", "")),
                        }
                    )
                else:
                    result.append({"phase": "check", "category": category, "message": str(error)})
    return result


def _response(output, digest, version, source_files, input_hash, module):
    return {
        "schema": "sysml-analysis/v1",
        "ok": False,
        "status": "running",
        "code": None,
        "compiler": {
            "project": "haradama/sysml-v2-rs",
            "version": "v0.1.4",
            "sha256": digest,
            "nativeVersion": version,
            "target": "aarch64-apple-darwin",
            "module": module,
        },
        "inputSha256": input_hash,
        "sourceFiles": source_files,
        "diagnostics": [],
        "model": None,
        "rules": {},
        "artifacts": {
            "sources": str(output / "sources"),
            "parse": str(output / "parse.json"),
            "check": str(output / "check.json"),
            "export": None,
            "report": str(output / "report.json"),
        },
    }


def _publish(staging, output, response):
    write_json(staging / "report.json", response)
    names = ["sources", "report.json"]
    names += [name for name in ANALYSIS_RESULTS if (staging / name).exists()]
    publish_items(staging, output, names, remove=ANALYSIS_RESULTS)


def analyze_sysml(files, output_dir):
    files = _validate_files(files)
    output = validate_output_directory(output_dir)
    digest, toolchain = _require_compiler()
    input_hash = hashlib.sha256(
        json.dumps(files, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".dgraph-sysml-", dir=output.parent))
    except OSError as error:
        raise DgraphError("output-io", f"Cannot create SysML staging directory: {error}", path=output, retryable=True) from error
    try:
        sources = staging / "sources"
        sources.mkdir()
        source_files = []
        for file in files:
            target = sources / file["name"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(file["content"], encoding="utf-8")
            source_files.append(
                {
                    "name": file["name"],
                    "bytes": len(file["content"].encode("utf-8")),
                    "sha256": hashlib.sha256(file["content"].encode("utf-8")).hexdigest(),
                }
            )
        paths = [str(sources / file["name"]) for file in files]
        version_result = _run([str(COMPILER), "--version"], staging)
        if version_result.returncode != 0:
            raise DgraphError(
                "compiler-output-invalid",
                f"Compiler version command failed: {version_result.stderr.decode(errors='replace')[:2_048]}",
                path=COMPILER,
            )
        try:
            version = version_result.stdout.decode("utf-8").strip()
        except UnicodeDecodeError as error:
            raise DgraphError("compiler-output-invalid", "Compiler version output is not UTF-8.", path=COMPILER) from error
        response = _response(output, digest, version, source_files, input_hash, toolchain)
        reports = {}
        for phase in ("parse", "check"):
            completed = _run([str(COMPILER), "--format", "json", "--color", "never", phase, *paths], staging)
            (staging / f"{phase}.stderr.log").write_bytes(completed.stderr)
            try:
                reports[phase] = json.loads(completed.stdout)
                write_json(staging / f"{phase}.json", reports[phase])
            except (json.JSONDecodeError, UnicodeDecodeError):
                reports[phase] = {"ok": False, "stdout": completed.stdout.decode(errors="replace")[:8_192]}
                write_json(staging / f"{phase}.json", reports[phase])
            if completed.returncode != 0 or not isinstance(reports[phase], dict) or reports[phase].get("ok") is not True:
                response["status"] = "invalid-model"
                response["code"] = "sysml-compilation-failed"
                response["diagnostics"] = _diagnostics(reports.get("parse"), reports.get("check"))
                if not response["diagnostics"]:
                    response["diagnostics"] = [
                        {
                            "phase": phase,
                            "message": completed.stderr.decode(errors="replace")[:8_192] or f"{phase} failed.",
                        }
                    ]
                _publish(staging, output, response)
                return response
        completed = _run([str(COMPILER), "--format", "json", "--color", "never", "export", *paths], staging)
        if completed.returncode != 0:
            response["status"] = "export-failed"
            response["code"] = "sysml-export-failed"
            response["diagnostics"] = [{"phase": "export", "message": completed.stderr.decode(errors="replace")[:8_192]}]
            _publish(staging, output, response)
            return response
        try:
            exported = json.loads(completed.stdout)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            response["status"] = "export-failed"
            response["code"] = "sysml-export-failed"
            response["diagnostics"] = [{"phase": "export", "message": f"Invalid export JSON: {error}"}]
            _publish(staging, output, response)
            return response
        if not isinstance(exported, list):
            response["status"] = "export-failed"
            response["code"] = "sysml-export-failed"
            response["diagnostics"] = [{"phase": "export", "message": "Compiler export JSON must be an array."}]
            _publish(staging, output, response)
            return response
        (staging / "export.json").write_bytes(completed.stdout)
        response["artifacts"]["export"] = str(output / "export.json")
        named = [
            element
            for element in exported
            if isinstance(element, dict)
            and not element.get("isLibraryElement")
            and (element.get("declaredName") or element.get("name"))
        ]
        response["model"] = {
            "format": "SysML v2 native semantic interchange",
            "totalElements": len(exported),
            "elements": [
                {
                    "id": item.get("@id"),
                    "kind": item.get("@type"),
                    "name": item.get("declaredName") or item.get("name"),
                    "qualifiedName": item.get("qualifiedName"),
                }
                for item in named
            ],
        }
        response["rules"] = reports["check"].get("rules", {}) if isinstance(reports["check"].get("rules"), dict) else {}
        response["diagnostics"] = _diagnostics(reports.get("parse"), reports.get("check"))
        response["ok"] = True
        response["status"] = "ok"
        _publish(staging, output, response)
        return response
    except DgraphError as error:
        response = {
            "schema": "sysml-analysis/v1",
            "ok": False,
            "status": "tool-error",
            "code": error.code,
            "error": error.to_dict(),
            "inputSha256": input_hash,
            "diagnostics": [error.to_dict()],
            "model": None,
            "rules": {},
            "artifacts": {
                "sources": str(output / "sources"),
                "parse": str(output / "parse.json"),
                "check": str(output / "check.json"),
                "export": None,
                "report": str(output / "report.json"),
            },
        }
        try:
            _publish(staging, output, response)
        except DgraphError:
            pass
        error.path = str(output / "report.json")
        raise
    except OSError as error:
        raise DgraphError("output-io", f"Could not write SysML analysis artifacts: {error}", path=output, retryable=True) from error
    finally:
        shutil.rmtree(staging, ignore_errors=True)


__all__ = ["analyze_sysml", "compiler_supported"]
