import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_render import spec


ROOT = Path(__file__).resolve().parents[1]


class MCPTests(unittest.TestCase):
    def run_mcp(self, requests):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        process = subprocess.Popen(
            ["python3", "-m", "dgraph"], cwd=ROOT, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True,
        )
        payload = "".join(json.dumps(request) + "\n" for request in requests)
        stdout, stderr = process.communicate(payload, timeout=30)
        self.assertEqual(0, process.returncode, stderr)
        self.assertEqual("", stderr)
        return [json.loads(line) for line in stdout.splitlines() if line.strip()]

    def test_initialize_discovery_and_render_over_stdio(self):
        with tempfile.TemporaryDirectory() as tmp:
            responses = self.run_mcp([
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "render_diagram", "arguments": {"spec": spec(tmp)}}},
            ])
            self.assertEqual("dgraph", responses[0]["result"]["serverInfo"]["name"])
            tools = {tool["name"] for tool in responses[1]["result"]["tools"]}
            self.assertEqual({"list_diagram_types", "analyze_sysml", "validate_viewspec", "render_diagram", "inspect_diagram"}, tools)
            self.assertTrue(responses[2]["result"]["resources"])
            self.assertTrue(responses[3]["result"]["structuredContent"]["ok"])
            self.assertTrue(Path(responses[3]["result"]["structuredContent"]["artifacts"]["svg"]).is_file())

    def test_invalid_tool_returns_structured_error(self):
        responses = self.run_mcp([{"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "missing", "arguments": {}}}])
        self.assertTrue(responses[0]["result"]["isError"])
        self.assertIn("Unknown tool", responses[0]["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
