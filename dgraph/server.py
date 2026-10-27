"""Newline-delimited JSON-RPC MCP stdio server."""

import json
import sys

from . import __version__
from .service import call_tool, read_resource, resources, tool_definitions
from .viewspec import DgraphError


PROTOCOL = "2025-03-26"


def _result(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(request):
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params") or {}
    if method == "initialize":
        return _result(request_id, {"protocolVersion": params.get("protocolVersion", PROTOCOL), "capabilities": {"tools": {"listChanged": False}, "resources": {"listChanged": False}}, "serverInfo": {"name": "dgraph", "version": __version__}, "instructions": "Clients perform natural-language understanding. dgraph deterministically validates, compiles, renders, and inspects diagrams."})
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": tool_definitions()})
    if method == "resources/list":
        return _result(request_id, {"resources": resources()})
    if method == "resources/read":
        try:
            uri = params.get("uri", "")
            return _result(request_id, {"contents": [{"uri": uri, "mimeType": "application/json", "text": read_resource(uri)}]})
        except DgraphError as error:
            return _error(request_id, -32602, error.message)
    if method == "tools/call":
        try:
            value = call_tool(params.get("name", ""), params.get("arguments") or {})
            return _result(request_id, {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "structuredContent": value, "isError": False})
        except (DgraphError, KeyError, TypeError, ValueError) as error:
            value = {"ok": False, "code": getattr(error, "code", "invalid-request"), "message": str(error)}
            return _result(request_id, {"content": [{"type": "text", "text": str(error)}], "structuredContent": value, "isError": True})
    if method and method.startswith("notifications/"):
        return None
    return _error(request_id, -32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        request_id = None
        try:
            request = json.loads(line)
            request_id = request.get("id")
            response = handle(request)
        except (json.JSONDecodeError, AttributeError) as error:
            response = _error(request_id, -32700, str(error))
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
