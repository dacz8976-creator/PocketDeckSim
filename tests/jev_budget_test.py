"""Offline credit-guard tests, including concurrent writers and network refusal."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location("jev_transport", Path(__file__).parents[1] / "src/players/jev_transport.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


class BudgetTests(unittest.TestCase):
    def test_exact_cap_then_refuse_and_reconcile(self):
        with tempfile.TemporaryDirectory() as folder:
            amount = (2 + 4096) * 42
            b = t.Budget(str(Path(folder)/"budget.sqlite"), str(amount / 1e9))
            row = b.reserve("{}", {})
            with self.assertRaises(t.BudgetLimitReached):
                b.reserve("{}", {})
            b.settle(row, {"usage":{"input_tokens":0}})
            b.reserve("{}", {})
            b.close()

    def test_unknown_usage_preserves_reservation_and_cap_is_immutable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/"budget.sqlite")
            b = t.Budget(path, "0.0002")
            row = b.reserve("{}", {})
            b.settle(row, {})
            with self.assertRaises(t.BudgetLimitReached):
                b.reserve("{}", {})
            with self.assertRaises(ValueError):
                t.Budget(path, "5")
            b.close()

    def test_concurrent_process_connections_share_cap(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/"budget.sqlite")
            t.Budget(path,"0.001").close()
            def attempt(_):
                b = t.Budget(path,"0.001")
                try:
                    b.reserve("{}", {})
                    return True
                except t.BudgetLimitReached:
                    return False
                finally:
                    b.close()
            with ThreadPoolExecutor(max_workers=8) as pool:
                accepted = sum(pool.map(attempt, range(32)))
            self.assertEqual(accepted, 5)

    def test_refused_request_never_touches_network(self):
        with tempfile.TemporaryDirectory() as folder:
            conn = Mock()
            output = io.StringIO()
            with patch.dict(t.os.environ, {"TYPESAFE_API_KEY":"offline-secret", "JEV_BUDGET_LEDGER":str(Path(folder)/"budget.sqlite"), "JEV_BUDGET_USD":"0.000001"}), patch.object(t.sys,"stdin",io.StringIO('{}\n')), patch.object(t.sys,"stdout",output), patch.object(t.http.client,"HTTPSConnection",return_value=conn):
                self.assertEqual(t.main(),1)
            conn.request.assert_not_called()
            self.assertEqual(json.loads(output.getvalue()), {"transport_error":"BudgetLimitReached"})
            self.assertNotIn("offline-secret",output.getvalue())

    def test_transport_settles_usage_in_shared_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/"budget.sqlite")
            conn, response = Mock(), Mock(status=200)
            response.read.return_value = b'{"usage":{"input_tokens":100}}'
            response.getheader.return_value = "fixture"
            conn.getresponse.return_value = response
            with patch.dict(t.os.environ, {"TYPESAFE_API_KEY":"offline-secret", "JEV_BUDGET_LEDGER":path, "JEV_BUDGET_USD":"0.0002"}), patch.object(t.sys,"stdin",io.StringIO('{}\n{}\n')), patch.object(t.sys,"stdout",io.StringIO()), patch.object(t.http.client,"HTTPSConnection",return_value=conn):
                self.assertEqual(t.main(),0)
            b = t.Budget(path,"0.0002")
            self.assertEqual(b.db.execute("SELECT SUM(charged),SUM(input_tokens),COUNT(*) FROM calls").fetchone(),(8400,200,2))
            b.close()


if __name__ == '__main__':
    unittest.main()
