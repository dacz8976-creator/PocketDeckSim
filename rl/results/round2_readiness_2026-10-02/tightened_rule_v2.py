"""tightened_rule v2 (the cloud, Oct 2; round-2 readiness, job 3). v1 is `../engine_switch_rules_2026-10/tightened_rule.py`,
unchanged. One change, for the "length" kind (one game is a prefix of the other): v1 had no tick to look at and every such game
was unexplained. When R's game is the longer one, its first extra tick k is a move the old engine never offered (its game ended
at k). `extra_tick_hits` explains it ON THE BOARD when an exact counter of a repaired mechanic fires AT that tick k (step 8c's two
pairing-31 games: the Victory Star choice after a Confused attacker's Confusion heads, vs_confused_choice_offered and _chosen at
k). Nothing else changes: `first_difference` returns the same kind, k and cause as v1 for every kind; for "length" (k the common
length, cause none, as in v1) it adds which game is longer ("longer": "new" for R, "old", or none) and R's row at k ("y").

v1's docstring follows.
The tightened mechanic check of the rules switch (F5/F6, the laptop Opus's second read; Oct 1), shared by the three scripts that
classify the changed games of a smoke: `victory_star_repair_2026-09-30/smoke/rerun_R/first_diff.py`,
`coin_prevention_repair_2026-09-30/smoke/rerun_R/counters_check.py` and `coin_lookahead.py` (this folder).

A game the repairs change (the move fingerprints of the old engine and R differ) is classified by the first tick at which the two
engines differ, read from their per-tick traces (`vs_trace.rs`: the chosen move, the offered moves when there are two or more,
their number `n`, the board summary, and "state", a hash of the whole `State` before the tick):

  kind "movegen"   the two engines are in the same state (same hash) and are OFFERED different moves, or a forced move (n = 1) differs.
                   The repaired code changed what is on the table: that is a difference on the board, at this tick (the cause).
  kind "lookahead" the same state, the same offered moves (n >= 2), a different choice: the bots' search saw something different.
  kind "state"     the state differs (different hash) after identical chosen and offered moves up to the tick before: applying the
                   move chosen at the tick before (the cause) had a different effect on the two engines.
  kind "length"    one game is a prefix of the other: no tick to look at.

"ON THE BOARD" (the rule, tightened): an exact counter of the repaired mechanic fired, in R's watch scan, at a tick t at or before the
first differing tick k and in the same turn as k (the rule as the coordinator put it: "in the same turn as the first difference"; the
coordinator accepted this reading, window up to k within its turn plus the cause tick, on Oct 1).
A counter read from the OFFERED moves fires at the tick where they are offered, which for a "state" difference is k itself (the
state after the move that did it); one read from the CHOSEN move fires at the cause tick, k - 1, which is in the turn before k when
the move ends the turn: so the cause tick counts too, whatever its turn (`counter_hits(..., literal=True)` is the rule without that
clause, and the scripts print where the two differ). Counters that fired in the same turn AFTER k are reported separately
("after"); they never explain a game.
Anything that is not on the board and is a "lookahead" difference needs BOTH halves of "lookahead only": the code gate (read in the
code, as the scripts' docstrings say) and a probe that finds the gate's condition inside kog3's three plies at tick k. A "movegen",
"state" or "length" difference without a counter is UNEXPLAINED, and that stops the switch.
"""
import gzip, json


def load_trace(path):
    """Each game's tick rows in order, and its closing row (the move fingerprint)."""
    games, done = {}, {}
    for r in map(json.loads, gzip.open(path, "rt")):
        if r.get("done"):
            done[r["i"]] = r
        else:
            games.setdefault(r["i"], []).append(r)
    return games, done


def _moves(row):
    return (row["chosen"], row["offered"], row["n"])


def first_difference(a, b):
    """First difference of two engines' tick rows (a: the old engine, b: R) for one game. Returns a dict:
    kind, detail, k (the first differing tick), cause (the tick whose move or offer made the difference), x and y (the two rows at k)."""
    m = min(len(a), len(b))
    k_state = next((t for t in range(m) if a[t]["state"] != b[t]["state"]), None)
    k_moves = next((t for t in range(m) if _moves(a[t]) != _moves(b[t])), None)
    if k_state is None and k_moves is None:
        longer = "new" if len(b) > len(a) else "old" if len(a) > len(b) else None
        return {"kind": "length", "detail": f"one game is a prefix of the other ({len(a)} and {len(b)} ticks)", "k": m,
                "cause": None, "longer": longer, "x": None, "y": b[m] if len(b) > m else None}
    if k_moves is not None and (k_state is None or k_moves < k_state):
        x, y = a[k_moves], b[k_moves]
        if x["n"] != y["n"] or x["offered"] != y["offered"]:
            kind, detail = "movegen", "the same state, different offered moves"
        elif x["n"] == 1:
            kind, detail = "movegen", "the same state, a forced move (n = 1) differs"
        else:
            kind, detail = "lookahead", "the same state, the same offered moves, a different choice"
        return {"kind": kind, "detail": detail, "k": k_moves, "cause": k_moves, "x": x, "y": y}
    return {"kind": "state", "detail": "the state differs after identical moves up to the tick before", "k": k_state,
            "cause": max(k_state - 1, 0), "x": a[k_state], "y": b[k_state]}


def counter_hits(watch_row, names, rows, d, after=False, literal=False):
    """{counter: [ticks]}: the ticks of the exact counters `names` (R's watch scan row) that explain the first difference `d` (from
    `first_difference`): at or before its tick k and in the same turn as k, or at its cause tick (`literal`: only the first
    kind). `after`: the ticks strictly after k in the same turn instead. `rows` is R's trace of the game (its rows carry the turn)."""
    k, cause = d["k"], d["cause"]
    turn = rows[k]["turn"]
    out = {}
    for name in names:
        ticks = []
        for t in watch_row[name]["ticks"]:
            if t >= len(rows):
                continue
            same_turn = rows[t]["turn"] == turn
            if (after and same_turn and t > k) or (not after and ((same_turn and t <= k) or (not literal and t == cause))):
                ticks.append(t)
        if ticks:
            out[name] = ticks
    return out


def extra_tick_hits(watch_row, names, d):
    """{counter: [k]}: for a "length" difference `d` whose longer game is R's (the new engine's), the exact counters `names` (R's
    watch scan row) that fire AT R's first extra tick k. Such a counter explains the game on the board: the extra tick is an offer
    of the repaired mechanic, made at k. Empty for any other difference, or when R's game is the shorter one."""
    if d["kind"] != "length" or d.get("longer") != "new":
        return {}
    k = d["k"]
    return {name: [k] for name in names if k in watch_row[name]["ticks"]}


def short(s, n=150):
    return s if len(s) <= n else s[:n - 3] + "..."
