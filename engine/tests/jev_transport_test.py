"""Offline transport contract tests. No credentials or external service required."""
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("jev_transport", Path(__file__).parents[1] / "src/players/jev_transport.py")
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)


class TransportTests(unittest.TestCase):
    def run_transport(self, payloads, status=200, body=b'{"model":"mock","answers":{},"usage":{"input_tokens":1,"output_tokens":0}}'):
        connection = Mock()
        response = Mock(status=status)
        response.read.return_value = body
        response.getheader.side_effect = lambda name: "fixture-id" if name == "x-request-id" else None
        connection.getresponse.return_value = response
        output = io.StringIO()
        with patch.dict(transport.os.environ, {"TYPESAFE_API_KEY": "offline-secret"}), \
             patch.object(transport.sys, "stdin", io.StringIO("".join(json.dumps(p) + "\n" for p in payloads))), \
             patch.object(transport.sys, "stdout", output), \
             patch.object(transport.http.client, "HTTPSConnection", return_value=connection) as factory:
            status_code = transport.main()
        self.assertNotIn("offline-secret", output.getvalue())
        factory.assert_called_once_with("api.typesafe.ai", timeout=90)
        connection.close.assert_called_once()
        return status_code, connection, [json.loads(line) for line in output.getvalue().splitlines()]

    def test_one_request_per_decision_even_for_forced_move(self):
        forced = {"model": "jev-latest", "state": {}, "questions": {"action_000000": {"type": "score"}}}
        multi = {"model": "jev-latest", "state": {}, "questions": {"action_000000": {}, "action_000001": {}}}
        status, connection, records = self.run_transport([forced, multi])
        self.assertEqual(status, 0)
        self.assertEqual(connection.request.call_count, 2)
        self.assertEqual(len(records), 2)
        for call, expected in zip(connection.request.call_args_list, [forced, multi]):
            self.assertEqual(call.args[:2], ("POST", "/v1/systemone"))
            self.assertEqual(json.loads(call.args[2]), expected)
        self.assertEqual(records[0]["request_id"], "fixture-id")

    def test_http_error_stops_without_retry(self):
        status, connection, records = self.run_transport([{}, {}], status=429)
        self.assertEqual(status, 1)
        self.assertEqual(connection.request.call_count, 1)
        self.assertEqual(records, [{"transport_error": "HTTP error", "http_status": 429}])

    def test_invalid_json_stops_without_retry(self):
        status, connection, records = self.run_transport([{}, {}], body=b'bad-json')
        self.assertEqual(status, 1)
        self.assertEqual(connection.request.call_count, 1)
        self.assertEqual(records, [{"transport_error": "JSONDecodeError"}])


if __name__ == "__main__":
    unittest.main()
