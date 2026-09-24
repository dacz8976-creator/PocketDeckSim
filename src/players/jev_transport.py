"""Persistent Jev transport: one request per line, no retries, optional shared cap."""
import http.client
import json
import os
import sqlite3
import sys
from decimal import Decimal


class BudgetLimitReached(Exception):
    pass


class Budget:
    """Atomic cross-process reservations. Amounts are integer nanodollars.

    Token accounting is a price estimate, not a provider billing receipt. The
    byte-based reservation includes headroom but is not a vendor-guaranteed
    bound. Prepaid account limits remain the final provider-side protection.
    Unknown/failed requests retain their full reservation until reconciliation.
    """
    def __init__(self, path, usd):
        self.cap = int(Decimal(usd) * 1_000_000_000)
        if self.cap <= 0:
            raise ValueError("budget must be positive")
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.db.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), cap INTEGER NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, reserved INTEGER NOT NULL, charged INTEGER, input_tokens INTEGER)")
        self.db.execute("INSERT OR IGNORE INTO budget VALUES (1, ?)", (self.cap,))
        if self.db.execute("SELECT cap FROM budget WHERE id=1").fetchone()[0] != self.cap:
            raise ValueError("budget cap changed; preserve the original ledger cap")

    def reserve(self, wire, payload):
        tokens = len(wire.encode("utf-8")) + 4096 + 1024 * len(payload.get("questions", {}))
        amount = tokens * 42  # $0.042 / million input tokens
        self.db.execute("BEGIN IMMEDIATE")
        try:
            spent = self.db.execute("SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM calls").fetchone()[0]
            if spent + amount > self.cap:
                raise BudgetLimitReached()
            row = self.db.execute("INSERT INTO calls(reserved) VALUES (?)", (amount,)).lastrowid
            self.db.execute("COMMIT")
            return row
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def settle(self, row, response):
        tokens = response.get("usage", {}).get("input_tokens")
        if type(tokens) is not int or tokens < 0:
            return  # Keep the full reservation when usage is unknown.
        self.db.execute("UPDATE calls SET charged=?, input_tokens=? WHERE id=?", (tokens * 42, tokens, row))

    def close(self):
        self.db.close()


def main():
    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key.strip():
        print(json.dumps({"transport_error": "TYPESAFE_API_KEY is missing"}), flush=True)
        return 1
    budget = None
    ledger = os.environ.get("JEV_BUDGET_LEDGER")
    cap = os.environ.get("JEV_BUDGET_USD")
    try:
        if bool(ledger) != bool(cap):
            raise ValueError("both budget settings required")
        if ledger:
            budget = Budget(ledger, cap)
    except Exception as exc:
        print(json.dumps({"transport_error": "BudgetConfigurationError", "error_type": type(exc).__name__}), flush=True)
        return 1
    connection = http.client.HTTPSConnection("api.typesafe.ai", timeout=90)
    try:
        for line in sys.stdin:
            try:
                payload = json.loads(line)
                wire = json.dumps(payload)
                reservation = budget.reserve(wire, payload) if budget else None
                connection.request("POST", "/v1/systemone", wire, {
                    "Authorization": "Bearer " + key,
                    "Content-Type": "application/json",
                })
                response = connection.getresponse()
                body = response.read()
                if response.status != 200:
                    result = {"transport_error": "HTTP error", "http_status": response.status}
                else:
                    parsed = json.loads(body)
                    if budget:
                        budget.settle(reservation, parsed)
                    result = {"response": parsed, "request_id": response.getheader("x-request-id") or response.getheader("request-id"), "http_status": response.status}
                print(json.dumps(result, allow_nan=False), flush=True)
                if "transport_error" in result:
                    return 1
            except Exception as exc:
                print(json.dumps({"transport_error": type(exc).__name__}), flush=True)
                return 1
    finally:
        connection.close()
        if budget:
            budget.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
