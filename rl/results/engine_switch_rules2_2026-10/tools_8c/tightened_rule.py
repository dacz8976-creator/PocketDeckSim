"""tightened_rule for rules switch 2 (the cloud, Oct 9; switch-2 PLAN.md precondition (b), "the classifier's prefix fix"): v2 (below)
with the length case finished and round 2's counter names.
  - A "length" difference (one game a prefix of the other, or the two the same tick for tick) is a board difference: its k is the first
    tick only the longer game has (the common length) and its cause k - 1, the last tick both games have, whose move had a different
    effect (it ended one game and not the other, or decided a different result). So `counter_hits` explains it as it explains a "state"
    difference: an exact counter at the cause tick, or at or before k in k's turn. That covers the new game shorter (the case v2 left
    open: a +20 hit back that Knocks Out the last Pokemon ends the new game at the attack's tick, its last), longer (as v2's
    `extra_tick_hits`, which stays) and as long (only the last move's effect differs).
  - `counter_hits` reads k's turn from the rows that exist: the rows it is given (the new game's) when they reach k, else the longer
    game's row at k that `first_difference` returns (x for the old game, y for the new), else the last row given.
  - `round2_reach` gives round 2's exact counter names from instrument_scan.py's lists (R2_COUNTERS and R2_KEYED less the off-gate and
    superset ones), and `reach_row` flattens the keyed ones ({key: [ticks]}) into counter_hits' {"ticks"} form, leaving out of
    coin_queued_by_attack the first round's coin sites, which build the same choice on both engines (ROUND2_QUEUED: the later round's
    eight attacks). validate_v2.py kept round 1's names, right for the Oct 1 hand-off it checks.
  - Shared by the switch-2 copies of classify_8c.py and coin_lookahead.py (this folder; Oct 9, later): `board_hits` (counter_hits and
    extra_tick_hits together), `watch_from_counters` (a hand-off row's counters as a watch row), `parse_probe` (coin_probe v2's
    RESULT, RESULT_P2 and RESULT_R2 lines), `lookahead_verdict` (with round 2's kinds, and the strict reading of a queued choice that
    may be a first-round site), `golden_ok`, `nothing_found` (the probe's retry) and `control_clean` (the negative controls). Read
    their docstrings.
  Tests: test_tightened_rule.py (this folder).

v2's docstring follows.
tightened_rule v2 (the cloud, Oct 2; round-2 readiness, job 3). v1 is `../engine_switch_rules_2026-10/tightened_rule.py`,
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
import ast, gzip, json, re

# The later coin round's sites, by attack title (card text, lib/card.py): the keys of coin_queued_by_attack that the switch changes.
ROUND2_QUEUED = frozenset({"Wild Swing", "Wellspring Dance", "Tornado Shot", "Double Splash", "Triple Bombardment", "Mischievous Ring",
                           "Litter", "Double-Punching Family"})


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
        detail = (f"one game is a prefix of the other ({len(a)} and {len(b)} ticks)" if longer
                  else f"the two games are the same tick for tick ({m} ticks); only the last move's effect differs")
        return {"kind": "length", "detail": detail, "k": m, "cause": m - 1 if m else None, "longer": longer,
                "x": a[m] if len(a) > m else None, "y": b[m] if len(b) > m else None}
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
    turn = (rows[k] if k < len(rows) else d.get("x") or d.get("y") or rows[-1])["turn"]
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


def round2_reach(instrument_scan_text):
    """Round 2's exact counter names, in instrument_scan.py's order: R2_COUNTERS, then R2_KEYED, less the off-gate counters and the
    superset trap_territory_two_in_play (the gate held, whether or not anything reads it)."""
    names = lambda var: ast.literal_eval(re.search(rf"^{var} = (\[.*?\])", instrument_scan_text, re.S | re.M)[1])
    keep = lambda n: not n.startswith("offgate_") and n != "trap_territory_two_in_play"
    return tuple(n for n in names("R2_COUNTERS") if keep(n)) + tuple(n for n in names("R2_KEYED") if keep(n))


KEYED = ("coin_queued_by_attack", "coin_plain_damage_by_attack")


def reach_row(watch_row, keyed=KEYED):
    """The watch row with each keyed exact counter's ticks put together in counter_hits' {"ticks"} form (coin_queued_by_attack: the
    later round's attacks only); the other counters as they are."""
    out = dict(watch_row)
    for name in keyed:
        keep = (lambda key: key in ROUND2_QUEUED) if name == "coin_queued_by_attack" else (lambda key: True)
        out[name] = {"ticks": sorted({t for key, ticks in (watch_row.get(name) or {}).items() if keep(key) for t in ticks})}
    return out


def board_hits(watch_row, names, rows, d):
    """What explains a first difference `d` on the board, whatever its kind: counter_hits' ticks, and for a "length" difference whose
    longer game is the new one, extra_tick_hits' tick k as well."""
    out = {n: list(t) for n, t in counter_hits(watch_row, names, rows, d).items()}
    for n, ticks in extra_tick_hits(watch_row, names, d).items():
        out[n] = sorted(set(out.get(n, [])) | set(ticks))
    return out


def watch_from_counters(exact, names, keyed=KEYED):
    """A hand-off row's exact counters ({name: [ticks]}; a keyed one {name: {key: [ticks]}}, instrument_scan.py's form) as the watch
    row counter_hits reads, through reach_row. A keyed counter given as a plain list is refused: its first-round keys can't be left out."""
    row = {}
    for n in names:
        v = exact.get(n)
        if n in keyed:
            if isinstance(v, list):
                raise ValueError(f"{n}: a keyed counter given as a list of ticks, without its keys")
            row[n] = v or {}
        else:
            row[n] = {"ticks": list(v or [])}
    return reach_row(row, keyed=[n for n in keyed if n in names])


# coin_probe v2 (../round2_readiness_2026-10-02/coin_probe_v2.rs). Its round-2 kinds, in the RESULT_R2 line's order, and the exact
# counters each is made of (the probe's docstring: WILL ... PERISH); RETURN is attack_return_weakness, QUEUED coin_queued_by_attack.
R2_KINDS = ("will", "vs", "trap", "own", "guts", "plain", "perish")
R2_COUNTER_KIND = {"will_confused_attack": "will", "will_block_coin_attack": "will", "vs_block_coin_built": "vs",
                   "vs_block_coin_choice_offered": "vs", "trap_territory_offer_changed": "trap", "trap_territory_outcome_changed": "trap",
                   "coin_own_side_split": "own", "guts_own_side_split": "guts", "coin_plain_damage_chosen": "plain",
                   "coin_plain_damage_by_attack": "plain", "perish_plain_hit_chosen": "perish", "perish_plain_hit_offered": "perish"}
SEARCH_PLIES = 3
BOTH_HALVES = "LOOKAHEAD ONLY, both halves hold"
JUDGMENT = "NEEDS A JUDGMENT"


def parse_probe(out):
    """coin_probe v2's output: queued, cut, free (RESULT), ret (RESULT_P2), r2 {kind: ply} and trapleaf (RESULT_R2), the attacks named
    on the shortest QUEUED paths ("queued_attacks", when any) and "truncated" when the search stopped at its node limit. An output
    without the RESULT_R2 line (a probe built before precondition (a)) is refused, not read as nothing found."""
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", out, re.M)
    p2 = re.search(r"^RESULT_P2 ret=(\S+)$", out, re.M)
    r2 = re.search(r"^RESULT_R2 " + " ".join(f"{k}=(\\S+)" for k in R2_KINDS) + r" trapleaf=(\S+)$", out, re.M)
    if not (m and p2 and r2):
        raise ValueError("coin_probe v2's RESULT, RESULT_P2 and RESULT_R2 lines are not all there")
    num = lambda s: None if s == "none" else int(s)
    c = {"queued": num(m[1]), "cut": num(m[2]), "free": m[3] == "true", "ret": num(p2[1]),
         "r2": {k: num(r2[j + 1]) for j, k in enumerate(R2_KINDS)}, "trapleaf": num(r2[len(R2_KINDS) + 1])}
    block = re.search(r"^ *QUEUED: .*\n((?: {4}after .*\n?)+)", out, re.M)
    titles = sorted({_title(t, end) for line in (block[1].splitlines() if block else [])
                     for t, end in re.findall(r'title: "([^"]*?)("|\.\.\.)', line.split("] offers")[0])})
    if titles:
        c["queued_attacks"] = titles
    if "search stopped at" in out:
        c["truncated"] = True
    return c


def _title(t, end):
    """An attack title on a probe path. The probe cuts each action to 87 characters and "...", which can cut a title short (Mega
    Kangaskhan ex's "Double-Punching Family"): a cut title that begins one of ROUND2_QUEUED's attacks is read as that attack, any
    other is kept with its "..."."""
    if end == '"':
        return t
    return next((name for name in sorted(ROUND2_QUEUED) if t and name.startswith(t)), t + "...")


def nothing_found(c):
    """The probe found no condition at all (a negative control's requirement)."""
    return (c["queued"] is None and c["cut"] is None and c["ret"] is None and c["trapleaf"] is None
            and all(v is None for v in c["r2"].values()))


def control_clean(c):
    """A negative control's requirement (an unchanged game, a mid-game tick without Meowth): the probe finds nothing at all, no queued
    coin-path choice, cut or return ply and none of round 2's seven kinds or trapleaf (the laptop's spec for the revert-check driver,
    Oct 10, item 2). Before, round 2's kinds and trapleaf were not required to be absent (a Will in hand or two Ariados in play can
    be found in a game that didn't change); a control that finds one now fails, and is looked at."""
    return nothing_found(c)


def lookahead_verdict(c, round2_queued):
    """A "lookahead" first difference with no exact counter, read from the probe at its tick k: (the verdict, the verdict under the
    strict reading). BOTH_HALVES when the probe finds, inside the bots' 3 plies, a return ply (P2), a round-2 kind, or a queued
    coin-path choice or cut that is not only at the leaf of a mixed frame; JUDGMENT when what it finds is only at the leaf: a queued
    choice offered at ply 3 in a mixed frame, a round-2 kind only beyond the search (4: offered at a depth-3 leaf, never applied), or
    trapleaf (a leaf's value reads a Retreat Cost Trap Territory raised; no counter sees it); else UNEXPLAINED. The strict reading
    counts a queued choice or cut only when `round2_queued` (it is a later-round site: the path names one of ROUND2_QUEUED's attacks,
    or, when it names none, a list holds a later-round attacker), since both engines build the first round's."""
    inside_r2 = any(v is not None and v <= SEARCH_PLIES for v in c["r2"].values())
    beyond_r2 = any(v is not None and v > SEARCH_PLIES for v in c["r2"].values())
    coin = c["queued"] is not None or c["cut"] is not None
    leaf_only = coin and c["queued"] == SEARCH_PLIES and not c["free"] and (c["cut"] is None or c["cut"] > SEARCH_PLIES)
    if c["ret"] is not None or inside_r2:
        return BOTH_HALVES, BOTH_HALVES
    leaf = JUDGMENT if beyond_r2 or c["trapleaf"] is not None else None
    if coin and not leaf_only:
        return BOTH_HALVES, BOTH_HALVES if round2_queued else leaf or "UNEXPLAINED"
    if leaf_only:
        return JUDGMENT, JUDGMENT if round2_queued else leaf or "UNEXPLAINED"
    return (leaf, leaf) if leaf else ("UNEXPLAINED", "UNEXPLAINED")


def golden_ok(name, c, keys=()):
    """The golden check for an exact counter that explains a game on the board, from the probe run at the counter's last explaining
    tick: its condition must be on the table there (a round-2 kind or RETURN at ply 1; a queued choice after 0 moves or a cut at
    ply 1). None for a counter the probe has no condition for (luxury_coin_opp_stadium, fossil_item_lock), and for
    coin_queued_by_attack when the attacks it fired for at that tick (`keys`) are only Mega Kangaskhan ex's Double-Punching Family:
    the engine queues its second punch when any of the opponent's Pokemon has a coin Ability (any_coin_target), the probe's QUEUED
    only when a target has one."""
    if name in R2_COUNTER_KIND:
        return c["r2"][R2_COUNTER_KIND[name]] == 1
    if name == "attack_return_weakness":
        return c["ret"] == 1
    if name == "coin_queued_by_attack":
        if keys and set(keys) <= {"Double-Punching Family"}:
            return None
        return c["queued"] == 0 or c["cut"] == 1
    return None


def short(s, n=150):
    return s if len(s) <= n else s[:n - 3] + "..."
