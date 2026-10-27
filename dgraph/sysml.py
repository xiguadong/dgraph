"""Pinned Rust SysML v2 compiler adapter with immutable source snapshots."""

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess

from .artifacts import write_json
from .viewspec import DgraphError


EXPECTED_SHA256 = "674fce28512a772d1886ff2397f5f02dda66265299c67c01f5cc36eaf00207f6"
COMPILER = Path(__file__).resolve().parent.parent / "vendor/sysml/bin/sysml"
MAX_FILES = 128
MAX_TOTAL_BYTES = 10 * 1024 * 1024


def _validate_files(files):
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise DgraphError("invalid-sysml-input", f"Provide 1–{MAX_FILES} source files.")
    total = 0
    names = set()
    for file in files:
        if not isinstance(file, dict) or not isinstance(file.get("name"), str) or not isinstance(file.get("content"), str):
            raise DgraphError("invalid-sysml-input", "Each file requires name and UTF-8 content.")
        path = PurePosixPath(file["name"])
        if path.is_absolute() or ".." in path.parts or path.suffix not in {".sysml", ".kerml"} or file["name"] in names:
            raise DgraphError("invalid-sysml-input", f"Unsafe or duplicate source name: {file['name']}")
        names.add(file["name"])
        total += len(file["content"].encode("utf-8"))
    if total > MAX_TOTAL_BYTES:
        raise DgraphError("sysml-input-limit", "The source workspace exceeds 10 MiB.")


def _run(command, cwd, timeout=30):
    env = os.environ.copy()
    env.update({"NO_COLOR": "1", "TMPDIR": str(cwd)})
    try:
        completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        raise DgraphError("compiler-timeout", f"Compiler exceeded {timeout} seconds.") from error
    return completed


def _diagnostics(parse, check):
    result = []
    if isinstance(parse, dict):
        for file in parse.get("files", []):
            for error in file.get("errors", []):
                result.append({"phase": "parse", "file": file.get("path", ""), "message": error.get("message", str(error)), "line": error.get("line"), "column": error.get("column")})
        for path in parse.get("unreadable", []):
            result.append({"phase": "parse", "file": str(path), "message": "Unreadable source"})
    if isinstance(check, dict):
        for category in ("parseErrors", "unresolved", "collisions", "violations", "unreadable"):
            for error in check.get(category, []):
                result.append({"phase": "check", "category": category, "file": error.get("path", error.get("file", "")) if isinstance(error, dict) else "", "message": error.get("message", error.get("reason", str(error))) if isinstance(error, dict) else str(error)})
    return result


def analyze_sysml(files, output_dir):
    _validate_files(files)
    if not COMPILER.is_file():
        raise DgraphError("compiler-missing", f"Pinned compiler not found: {COMPILER}")
    digest = hashlib.sha256(COMPILER.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise DgraphError("compiler-integrity", "Pinned compiler SHA-256 does not match.")
    output = Path(output_dir).resolve()
    sources = output / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    paths = []
    for file in files:
        target = sources / file["name"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(file["content"], encoding="utf-8")
        paths.append(str(target))
    version = _run([str(COMPILER), "--version"], output).stdout.decode().strip()
    response = {
        "ok": False,
        "compiler": {"project": "haradama/sysml-v2-rs", "version": "v0.1.4", "sha256": digest, "nativeVersion": version},
        "diagnostics": [], "model": None,
        "artifacts": {"sources": str(sources), "parse": str(output / "parse.json"), "check": str(output / "check.json"), "export": None, "report": str(output / "report.json")},
    }
    reports = {}
    for phase in ("parse", "check"):
        completed = _run([str(COMPILER), "--format", "json", "--color", "never", phase, *paths], output)
        (output / f"{phase}.stderr.log").write_bytes(completed.stderr)
        try:
            reports[phase] = json.loads(completed.stdout)
            write_json(output / f"{phase}.json", reports[phase])
        except (json.JSONDecodeError, UnicodeDecodeError):
            reports[phase] = {"ok": False, "stdout": completed.stdout.decode(errors="replace")[:8192]}
            write_json(output / f"{phase}.json", reports[phase])
        if completed.returncode != 0 or not isinstance(reports[phase], dict) or reports[phase].get("ok") is not True:
            response["diagnostics"] = _diagnostics(reports.get("parse"), reports.get("check"))
            if not response["diagnostics"]:
                response["diagnostics"] = [{"phase": phase, "message": completed.stderr.decode(errors="replace")[:8192] or f"{phase} failed."}]
            write_json(output / "report.json", response)
            return response
    completed = _run([str(COMPILER), "--format", "json", "--color", "never", "export", *paths], output)
    if completed.returncode == 0:
        try:
            exported = json.loads(completed.stdout)
            (output / "export.json").write_bytes(completed.stdout)
            response["artifacts"]["export"] = str(output / "export.json")
            named = [element for element in exported if isinstance(element, dict) and not element.get("isLibraryElement") and (element.get("declaredName") or element.get("name"))]
            response["model"] = {"format": "SysML v2 native semantic interchange", "totalElements": len(exported), "elements": [{"id": item.get("@id"), "kind": item.get("@type"), "name": item.get("declaredName") or item.get("name"), "qualifiedName": item.get("qualifiedName")} for item in named]}
            response["ok"] = True
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            response["diagnostics"] = [{"phase": "export", "message": str(error)}]
    else:
        response["diagnostics"] = [{"phase": "export", "message": completed.stderr.decode(errors="replace")[:8192]}]
    response["diagnostics"] = _diagnostics(reports.get("parse"), reports.get("check")) + response["diagnostics"]
    response["rules"] = reports["check"].get("rules", {})
    write_json(output / "report.json", response)
    return response
