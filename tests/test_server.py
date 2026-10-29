import io
import unittest

from dgraph.server import MAX_REQUEST_BYTES, _read_requests, handle


class JSONRPCHardeningTests(unittest.TestCase):
    def test_oversized_line_is_rejected_and_drained(self):
        payload = b"x" * (MAX_REQUEST_BYTES + 10) + b"\n" + b'{"id":1,"method":"ping"}\n'
        messages = list(_read_requests(io.BytesIO(payload)))
        self.assertEqual(2, len(messages))
        self.assertIsNone(messages[0])
        self.assertIn(b"ping", messages[1])

    def test_non_object_params_return_protocol_error(self):
        response = handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": []})
        self.assertEqual(-32602, response["error"]["code"])

    def test_unexpected_tool_exception_is_sanitized(self):
        response = handle(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "render_diagram", "arguments": {"spec": 1}},
            }
        )
        value = response["result"]["structuredContent"]
        self.assertTrue(response["result"]["isError"])
        self.assertEqual("invalid-spec", value["code"])

    def test_unknown_or_missing_tool_arguments_are_rejected(self):
        response = handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "render_diagram", "arguments": {"specc": {}}},
            }
        )
        value = response["result"]["structuredContent"]
        self.assertTrue(response["result"]["isError"])
        self.assertEqual("invalid-request", value["code"])
        self.assertIn("specc", value["message"])


if __name__ == "__main__":
    unittest.main()
