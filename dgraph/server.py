"""Newline-delimited JSON-RPC MCP stdio server."""

import json
import sys

from . import __version__
from .service import call_tool, read_resource, resources, tool_definitions
from .viewspec import DgraphError


PROTOCOL = "2025-03-26"
MAX_REQUEST_BYTES = 12 * 1024 * 1024


def _result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code, message, data=None):
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _tool_error(error):
    if isinstance(error, DgraphError):
        value = error.to_dict()
    else:
        value = {
            "ok": False,
            "code": "internal-error",
            "message": "The tool failed unexpectedly.",
            "phase": "execution",
            "retryable": False,
        }
    return _result(
        None,
        {
            "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}],
            "structuredContent": value,
            "isError": True,
        },
    )


def handle(request):
    if not isinstance(request, dict):
        return _error(None, -32600, "JSON-RPC request must be an object.")
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})
    if not isinstance(method, str):
        return _error(request_id, -32600, "JSON-RPC method must be a string.")
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error(request_id, -32602, "JSON-RPC params must be an object.")
    if method.startswith("notifications/"):
        return None
    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {"listChanged": False}, "resources": {"listChanged": False}},
                "serverInfo": {"name": "dgraph", "version": __version__},
                "instructions": "Clients perform natural-language understanding. dgraph deterministically validates, compiles, renders, and inspects diagrams.",
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": tool_definitions()})
    if method == "resources/list":
        return _result(request_id, {"resources": resources()})
    if method == "resources/read":
        uri = params.get("uri", "")
        if not isinstance(uri, str):
            return _error(request_id, -32602, "Resource URI must be a string.")
        try:
            text = read_resource(uri)
            return _result(request_id, {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]})
        except DgraphError as error:
            return _error(request_id, -32602, error.message, error.to_dict())
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(name, str) or not name:
            return _error(request_id, -32602, "Tool name must be a non-empty string.")
        try:
            value = call_tool(name, arguments)
            is_error = isinstance(value, dict) and value.get("ok") is False
            text = json.dumps(value, ensure_ascii=False)
            return _result(
                request_id,
                {
                    "content": [{"type": "text", "text": text}],
                    "structuredContent": value,
                    "isError": is_error,
                },
            )
        except DgraphError as error:
            response = _tool_error(error)
            response["id"] = request_id
            return response
        except Exception:
            response = _tool_error(None)
            response["id"] = request_id
            return response
    return _error(request_id, -32601, f"Method not found: {method}")


def _read_requests(stream):
    while True:
        line = stream.readline(MAX_REQUEST_BYTES + 1)
        if not line:
            return
        if len(line) <= MAX_REQUEST_BYTES:
            yield line
            continue
        while line and not line.endswith(b"\n"):
            line = stream.readline(MAX_REQUEST_BYTES + 1)
        yield None


def main():
    for line in _read_requests(sys.stdin.buffer):
        request_id = None
        if line is None:
            response = _error(None, -32600, f"Request exceeds {MAX_REQUEST_BYTES} bytes.")
        elif not line.strip():
            continue
        else:
            try:
                request = json.loads(line)
                request_id = request.get("id") if isinstance(request, dict) else None
                response = handle(request)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                response = _error(request_id, -32700, f"Invalid JSON: {error}")
        if response is not None:
            payload = (json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            sys.stdout.buffer.write(payload)
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
