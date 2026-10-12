#!/usr/bin/env python3
"""Rules switch 2 (rl/results/engine_switch_rules2_2026-10/): the checks sitting1.sh makes beside switch_check.py (PLAN.md
steps 6, 7b and 7c), and the counter model sitting2_check.py imports. The copy of Oct 1's
../engine_switch_rules_2026-10/sitting1_check.py, adapted (ADAPTATION_SPEC.md C1-1 to C1-9): the counters are read from
counters.tsv instead of constants (round 2's package writes 42); the floor comparison gains three modes for switch 2's pages
(the coverage program line, deck 10's t-weezing row, Victini's caveat on draft D's pages); pairs7c2 writes step 7c's 24 new
rows. Standard library only. Each subcommand prints what it found and exits 0 when the check passes, 1 when it fails, 2 on a
malformed or missing input.

The counter model (counters.tsv in this folder; ADAPTATION_SPEC.md 1.11). One row per counter the watch build writes (both
instrument_scan.py scripts: Victory Star's, cd8fe70b, and the coin script at P), with these columns:
  name script shape role mechanic revert_switch
(revert_switch: "-", or the DECKGYM_* switch(es) that turn the counter's gate off, several joined by "+".)
A first line starting "# TO FINALIZE" marks the file not final: the runners refuse to start on it, but this module still reads
it, so a dry run works. A comment line "# ROUND2_QUEUED<TAB>a|b|..." names round 2's eight queued attacks.
  shapes: exact       {"n", "first", "ticks"}: every firing tick, ascending (as_exact);
          keyed       {key: [ascending ticks]}, fired when any list is non-empty (as_keyed);
          int         a count; int_or_null: a tick or null, fired when not null.
  roles:  reach2      round 2's exact counters: the rewritten rule acted on the board (coin_queued_by_attack counts as reach only
                      for the ROUND2_QUEUED attacks: reach_value; for step 7b's zero check every key counts);
          offgate2    round 2's off-gate counters: the rewritten lines ran and gave the old answer;
          superset2   trap_territory_two_in_play: never reach (PLAN.md section 6, change 1);
          r1_exact, r1_heads, r1_offgate, r1_superset: round 1's (Oct 1's) counters. Both engines have round 1, so for this
                      switch they are never reach.
  A counter missing from a game, or of another shape, is Malformed (exit 2: not the watch build's output).
The module reads counters.tsv once at import (the file named by the environment's SWITCH2_COUNTERS, else the one next to this
script; sitting1.sh and sitting2.sh run private copies side by side) into REACH2, OFFGATE2, SUPERSET2, R1_EXACT, R1_HEADS,
R1_OFFGATE, R1_SUPERSET, ROUND2_QUEUED and COUNTERS; an unreadable file leaves them empty and COUNTERS_ERROR set. The
subcommands below read the file named by --counters themselves.

  counters FILE [FILE ...] --counters counters.tsv --label L [--zero-role ROLE ...] [--zero NAME,... ...]
           [--require NAME,... [--in PAIRINGS]] [--report-rest] [--plain FILE ...]
      The watch build's per-game counters. Every game must carry every counter of counters.tsv in its shape (else exit 2).
      --zero-role / --zero: every counter of that role (any key of a keyed one) or so named must read 0 in every game.
      --require: each named counter must be above 0 in at least one game of the pairings named by --in (all games without
      it). --report-rest: every other counter is reported (games, ticks), with a NOTE when one of round 1's, or of round 2's
      exact counters, is above 0. --plain: the plain build's files of the same deals: the keys a watch game adds to the plain
      record must be exactly counters.tsv's names (else exit 2). One line per file, one line per pairing where a shown
      counter fired, one line per required counter, the others, then "<label>: PASS: ..." or "<label>: does not pass: ...".
  floor NEWDIR REFDIR NAME --label L [--allow-coverage-program] [--report-opponent NAME] [--allow-caveat KEY] [--expect-games N]
      A floor page replayed by floor.py's own call (floor_with.py) against the recorded page: NAME_games.jsonl holds the same
      games in the same order (keyed (opponent, seat, seed), once each; --expect-games, default the recorded count), each
      equal on every field of floor.py's per-game summary record (the union of both records' keys; not moves or decisions);
      NAME_coverage.json is byte-equal; NAME.md is equal line for line, the program in its "- Engine:" line aside. Modes:
        --allow-coverage-program  the "- Coverage from <program> (sha256 <hash>; ..." line's program and hash aside, both
                                  printed (the Sept 30 pages name rl/engine-2026-09-30/goldfish; floor.py now takes the
                                  manifest's, rl/engine-2026-10-02/goldfish); the coverage file itself is still compared;
        --report-opponent NAME    games against NAME may differ: counted and printed (a "REPORT-OPPONENT" line, with wins
                                  before and after, and "a new page in step 15" when any differs), never a failure; every
                                  other opponent's game must be equal; when NAME's games differ, the page may differ only in
                                  lines naming NAME and in its totals (the verdict, the flagged line, the worst-matchup list,
                                  the coverage-flag counts and the failure-mode rows); the coverage must still be byte-equal;
        --allow-caveat KEY        the coverage file may differ only in KEY's "limitations" list, and the page only in the
                                  engine cell of the table row whose card carries KEY (both printed in full).
  pairs7c --repo R --out FILE
      Oct 1's step 7c pairs file, unchanged (switch 2 replays ../engine_switch_rules_2026-10/pairs_7c.tsv in place; the dry
      run checks this still writes that file byte for byte).
  pairs7c2 --repo R --out FILE [--seeds-out FILE]
      Step 7c's new rows on rules switch 2's block (seed = 23,300,000,000 + pairing x 10,000 + i, i < 60): pairings 0-7 deck
      10 (10-xatu-oricorio-tr-weezing), 8-15 draft D's first list (this folder's floor_7c/d_first/ copy of the 9cc6667 blob),
      16-23 draft D as amended (today's list), each against the 8 lists of decks/screen/opponents in sorted order (so deck 10
      v t-weezing is pairing 7). pairs_7c.tsv's columns, block "rules2_7c". --seeds-out writes the seed record with every
      deck file's git blob id.
  script-names --counters counters.tsv --coin SCRIPT --patched legality_scan.rs
      counters.tsv against the watch build's scripts: every name is written by the patched legality_scan.rs (a "name" string
      in it), and the coin script's R2_COUNTERS + R2_KEYED (read with ast) are exactly counters.tsv's round-2 rows (reach2,
      offgate2, superset2), the keyed ones exactly R2_KEYED.
  attackers FLOOR.py
      floor.py's ATTACKERS keys (read with ast), one per line; nothing when it has no such table.
"""
import argparse, ast, glob, hashlib, json, os, re, sys

SHAPES = ("exact", "keyed", "int", "int_or_null")
ROLE_NAMES = ("reach2", "offgate2", "superset2", "r1_exact", "r1_heads", "r1_offgate", "r1_superset")
HEADER = ("name", "script", "shape", "role", "mechanic", "revert_switch")
MARKER = "# TO FINALIZE"
BY_MECHANIC = "offgate_helper_by_mechanic"   # {mechanic: [ticks]}; its union must equal offgate_helper_choice's ticks
OFFGATE_HELPER = "offgate_helper_choice"
QUEUED_KEYED = "coin_queued_by_attack"       # reach only for ROUND2_QUEUED's attacks
MISSING = object()

REL = "rl/results/engine_switch_rules2_2026-10"
DECKS_7C = ("decks/dustin/02-arceus-crobat.txt", "decks/dustin/06-mega-blaziken-tournament-list.txt",
            "decks/dustin/08-garchomp-toolbox.txt", "decks/dustin/14-comfey-raticate-hypno.txt")
BASE_7C, FIRST_7C, DEALS_7C = 23_100_000_000, 40, 60
BASE_7C2, DEALS_7C2, SUB = 23_300_000_000, 60, 10_000
HELD_7C2 = (("10-xatu-oricorio-tr-weezing", "decks/dustin/10-xatu-oricorio-tr-weezing.txt",
             "deck 10 (its row v t-weezing, pairing 7, is named: its changed games go to 8c)"),
            ("draft-D-first", f"{REL}/floor_7c/d_first/draft-D-entei-grimhound.txt",
             "draft D's first list (the 9cc6667 blob b15acdd1, copied byte for byte by sitting1.sh at 7c-seeds)"),
            ("draft-D-amended", "decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt",
             "draft D as amended at 9e139e6 (today's list)"))
PAIRS_HEAD = ("pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last", "sub_block_end")


class Malformed(Exception):
    pass


def short(path):
    return path.split("/rl/results/", 1)[1] if "/rl/results/" in path else path


def pairings(spec):
    out = set()
    for part in (x.strip() for x in spec.split(",") if x.strip()):
        if "-" in part:
            lo, hi = part.split("-", 1)
            out |= set(range(int(lo), int(hi) + 1))
        else:
            out.add(int(part))
    return out


def blob_id(path):
    """git's blob id of the file's bytes (git hash-object --no-filters; the repository's .gitattributes say * -text)."""
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# --- the counter model -----------------------------------------------------------------------------------------------------

def load_counters(path):
    """counters.tsv -> {"path", "final", "names": {name: (script, shape, role, mechanic, revert_switch)}, "order": (names in file
    order), "roles": {role: (names)}, "round2_queued": frozenset}. Raises Malformed on a malformed file."""
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\r\n") for ln in f]
    final = not (lines and lines[0].startswith(MARKER))
    names, order, queued, header = {}, [], None, None
    for k, ln in enumerate(lines, 1):
        if not ln.strip():
            continue
        if ln.startswith("#"):
            m = re.match(r"^# ROUND2_QUEUED\s+(\S.*)$", ln)
            if m:
                if queued is not None:
                    raise Malformed(f"{short(path)}:{k}: a second ROUND2_QUEUED line")
                queued = frozenset(x.strip() for x in m.group(1).split("|") if x.strip())
            continue
        cells = ln.split("\t")
        if header is None:
            header = tuple(cells)
            if header != HEADER:
                raise Malformed(f"{short(path)}:{k}: the header is {header}, not {HEADER}")
            continue
        if len(cells) != len(HEADER):
            raise Malformed(f"{short(path)}:{k}: {len(cells)} fields, not {len(HEADER)}")
        name, script, shape, role, mech, rev = cells
        if not re.fullmatch(r"[a-z0-9_]+", name):
            raise Malformed(f"{short(path)}:{k}: {name!r} is not a counter name")
        if script not in ("coin", "vs") or shape not in SHAPES or role not in ROLE_NAMES:
            raise Malformed(f"{short(path)}:{k}: {name}: script {script!r}, shape {shape!r} or role {role!r} unknown")
        # revert_switch: "-", one DECKGYM_* name, or several joined by "+" (a gate whose old answer needs them together: G2,
        # the seven sites, needs G1 off too, apply_action_helpers.rs's own comment)
        if not re.fullmatch(r"-|[a-z0-9_]+", mech) or not re.fullmatch(r"-|DECKGYM_[A-Z0-9_]+(\+DECKGYM_[A-Z0-9_]+)*", rev):
            raise Malformed(f"{short(path)}:{k}: {name}: mechanic {mech!r} or revert_switch {rev!r} malformed")
        if name in names:
            raise Malformed(f"{short(path)}:{k}: {name} is listed twice")
        names[name] = (script, shape, role, mech, rev)
        order.append(name)
    if header is None or not names:
        raise Malformed(f"{short(path)}: no header or no counter")
    if queued is None:
        raise Malformed(f"{short(path)}: no '# ROUND2_QUEUED' line")
    if QUEUED_KEYED in names and names[QUEUED_KEYED][1] != "keyed":
        raise Malformed(f"{short(path)}: {QUEUED_KEYED} is not keyed")
    roles = {r: tuple(n for n in order if names[n][2] == r) for r in ROLE_NAMES}
    return {"path": path, "final": final, "names": names, "order": tuple(order), "roles": roles, "round2_queued": queued}


def _default_counters_path():
    return os.environ.get("SWITCH2_COUNTERS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "counters.tsv")


try:
    TABLE = load_counters(_default_counters_path())
    COUNTERS_ERROR = None
except (OSError, ValueError, Malformed) as _e:
    TABLE = {"path": _default_counters_path(), "final": False, "names": {}, "order": (),
             "roles": {r: () for r in ROLE_NAMES}, "round2_queued": frozenset()}
    COUNTERS_ERROR = repr(_e)
COUNTERS = TABLE["names"]
REACH2, OFFGATE2, SUPERSET2 = (TABLE["roles"][r] for r in ("reach2", "offgate2", "superset2"))
R1_EXACT, R1_HEADS, R1_OFFGATE, R1_SUPERSET = (TABLE["roles"][r] for r in ("r1_exact", "r1_heads", "r1_offgate", "r1_superset"))
ROUND2_QUEUED = TABLE["round2_queued"]


def _where(g, name):
    return f"game {(g.get('pairing'), g.get('i'))}: {name}"


def as_exact(g, name):
    """An exact counter: {n, first, ticks}, every firing tick kept (n == len(ticks), first == ticks[0] or null, ticks strictly
    ascending ints). Returns (n, first)."""
    v = g.get(name)
    where = _where(g, name)
    if not (isinstance(v, dict) and set(v) == {"n", "first", "ticks"} and isinstance(v["n"], int)
            and (v["first"] is None or isinstance(v["first"], int)) and isinstance(v["ticks"], list)):
        raise Malformed(f"{where} is {v!r}, not {{n, first, ticks}}")
    t = v["ticks"]
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in t) or any(a >= b for a, b in zip(t, t[1:])):
        raise Malformed(f"{where} {v!r}: ticks are not strictly ascending ints")
    if v["n"] != len(t) or v["first"] != (t[0] if t else None):
        raise Malformed(f"{where} {v!r}: n, first and ticks disagree")
    return v["n"], v["first"]


def as_keyed(g, name, keys=None):
    """A keyed counter: {key: [strictly ascending int ticks]}. Returns the number of ticks (of the given keys only, if any)."""
    v = g.get(name)
    where = _where(g, name)
    if not isinstance(v, dict) or not all(isinstance(k, str) and isinstance(x, list) for k, x in v.items()):
        raise Malformed(f"{where} is {v!r}, not {{key: [ticks]}}")
    total = 0
    for k, t in v.items():
        if not all(isinstance(x, int) and not isinstance(x, bool) for x in t) or any(a >= b for a, b in zip(t, t[1:])):
            raise Malformed(f"{where}[{k!r}] {t!r}: ticks are not strictly ascending ints")
        if keys is None or k in keys:
            total += len(t)
    return total


def as_int(g, name):
    v = g.get(name)
    if not isinstance(v, int) or isinstance(v, bool):
        raise Malformed(f"{_where(g, name)} is {v!r}, not a count")
    return v


def as_int_or_null(g, name):
    """A tick or null. Returns 1 when set, 0 when null."""
    if name not in g:
        raise Malformed(f"{_where(g, name)} is missing")
    v = g[name]
    if v is None:
        return 0
    if not isinstance(v, int) or isinstance(v, bool):
        raise Malformed(f"{_where(g, name)} is {v!r}, not a tick or null")
    return 1


def value(g, name, table=None):
    """How much the counter fired in game g (exact: n; keyed: its ticks; int: the count; int_or_null: 1 if set), by its
    shape in counters.tsv. Malformed when the counter is missing or of another shape."""
    t = (table or TABLE)["names"]
    if name not in t:
        raise Malformed(f"{name} is not a counter of counters.tsv")
    if name not in g:
        raise Malformed(f"{_where(g, name)} is missing")
    shape = t[name][1]
    if shape == "exact":
        return as_exact(g, name)[0]
    if shape == "keyed":
        return as_keyed(g, name)
    if shape == "int":
        return as_int(g, name)
    return as_int_or_null(g, name)


def reach_value(g, name, table=None):
    """value() as reach reads it (ADAPTATION_SPEC.md 1.11): coin_queued_by_attack counts only ROUND2_QUEUED's attacks."""
    tb = table or TABLE
    if name == QUEUED_KEYED:
        return as_keyed(g, name, tb["round2_queued"])
    return value(g, name, tb)


def check_by_mechanic(g):
    """offgate_helper_by_mechanic is {mechanic: [ticks]}, and the union of its lists is offgate_helper_choice's ticks."""
    m = g.get(BY_MECHANIC)
    where = _where(g, BY_MECHANIC)
    if not isinstance(m, dict) or not all(isinstance(k, str) and isinstance(x, list) for k, x in m.items()):
        raise Malformed(f"{where} is {m!r}, not {{mechanic: [ticks]}}")
    as_exact(g, OFFGATE_HELPER)
    union = sorted({t for x in m.values() for t in x})
    if union != g[OFFGATE_HELPER]["ticks"]:
        raise Malformed(f"{where}: its ticks {union} are not {OFFGATE_HELPER}'s {g[OFFGATE_HELPER]['ticks']}")


# --- counters ---------------------------------------------------------------------------------------------------------------

def counters(a):
    tb = load_counters(a.counters)
    names, order = tb["names"], tb["order"]

    def names_of(specs, opt):
        out = []
        for spec in specs:
            for n in (x.strip() for x in spec.split(",") if x.strip()):
                if n not in names:
                    raise Malformed(f"{opt} {n}: not a counter of {short(a.counters)}")
                if n not in out:
                    out.append(n)
        return out

    zero = [n for n in order if names[n][2] in a.zero_role]
    for n in names_of(a.zero, "--zero"):
        if n not in zero:
            zero.append(n)
    req = names_of(a.require, "--require")
    if a.in_ and not req:
        raise Malformed("--in needs --require")
    scope = pairings(a.in_) if a.in_ else None
    named = [n for n in zero if names[n][2] not in a.zero_role]
    zdesc = (f"the {len(zero)} counters of "
             + "; ".join(([f"role {', '.join(a.zero_role)}"] if a.zero_role else []) + ([", ".join(named)] if named else [])))
    plain_keys = None
    if a.plain:
        plain_keys = set()
        for path in a.plain:
            with open(path, encoding="utf-8") as f:
                for ln in f:
                    if ln.strip():
                        plain_keys |= set(json.loads(ln))
    want_extra = set(order)
    lines, per_pair, fired = [], {}, {n: [0, 0] for n in order}
    req_games, scope_games, total, bad_total = {n: 0 for n in req}, 0, 0, 0
    for path in a.files:
        n_games, bad = 0, []
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                g = json.loads(ln)
                n_games += 1
                vals = {c: value(g, c, tb) for c in order}
                if BY_MECHANIC in names and OFFGATE_HELPER in names:
                    check_by_mechanic(g)
                if plain_keys is not None:
                    got = set(g) - plain_keys
                    if got != want_extra:
                        raise Malformed(f"game {(g.get('pairing'), g.get('i'))} of {short(path)}: the keys the watch build adds "
                                        f"to the plain record are not counters.tsv's: extra {sorted(got - want_extra)}, "
                                        f"missing {sorted(want_extra - got)}")
                nz = [c for c in zero if vals[c]]
                if nz:
                    bad.append(((g.get("pairing"), g.get("i")), nz))
                key = (g.get("pairing"), g.get("a"), g.get("b"))
                row = per_pair.setdefault(key, {"games": 0, "c": {}})
                row["games"] += 1
                for c in order:
                    if vals[c]:
                        fired[c][0] += 1
                        fired[c][1] += vals[c]
                        x = row["c"].setdefault(c, [0, 0])
                        x[0] += 1
                        x[1] += vals[c]
                if scope is None or g.get("pairing") in scope:
                    scope_games += 1
                    for c in req:
                        if vals[c]:
                            req_games[c] += 1
        total += n_games
        bad_total += len(bad)
        zt = ("no zero check" if not zero else
              (f"{zdesc} read 0 in all {n_games} games" if not bad else
               f"{zdesc} are NOT all 0: {len(bad)} games, first {bad[0][0]} ({', '.join(bad[0][1])})"))
        lines.append(f"{a.label}: {short(path)}: {n_games} games; {zt}"
                     + ("; every game adds exactly counters.tsv's names to the plain record" if plain_keys is not None else ""))
    shown = set(order) if a.report_rest else set(zero) | set(req)
    pos = {n: k for k, n in enumerate(order)}
    for (p, x, y), row in sorted(per_pair.items(),
                                 key=lambda kv: (kv[0][0] if isinstance(kv[0][0], int) else -1, str(kv[0][1]), str(kv[0][2]))):
        here = sorted((c for c in row["c"] if c in shown), key=pos.get)
        if here:
            lines.append(f"  pairing {p} {x} v {y}: {row['games']} games; "
                         + "; ".join(f"{c} in {row['c'][c][0]} games ({row['c'][c][1]} ticks)" for c in here))
    scope_txt = f"pairings {a.in_}" if scope is not None else "these games"
    for c in req:
        lines.append(f"  required {c} above 0 in {scope_txt}: "
                     + (f"yes, in {req_games[c]} of {scope_games} games" if req_games[c]
                        else f"no, in none of {scope_games} games (required)"))
    rest = [c for c in order if c not in zero and c not in req]
    up = [c for c in rest if fired[c][0]]
    if a.report_rest:
        lines.append("  others (reported, not checked): "
                     + ("; ".join(f"{c} above 0 in {fired[c][0]} games ({fired[c][1]} ticks)" for c in up) if up
                        else "none above 0") + f"; {len(rest) - len(up)} at 0 in every game")
        r1 = [c for c in up if names[c][2].startswith("r1_")]
        if r1:
            lines.append("  NOTE: round 1's counters above 0 here (both engines have round 1, so they are never reach for this "
                         f"switch; a report, not a stop): {', '.join(r1)}")
        r2 = [c for c in up if names[c][2] == "reach2"]
        if r2:
            lines.append(f"  NOTE: round 2's exact counters above 0 here (a report; their games are read in the identity line): "
                         f"{', '.join(r2)}")
    ok = bad_total == 0 and all(req_games[c] for c in req) and total > 0
    parts = []
    if zero:
        parts.append(f"{zdesc} 0 in every game: " + ("yes" if not bad_total else f"no ({bad_total} games)"))
    for c in req:
        parts.append(f"{c} above 0 in {scope_txt}: "
                     + (f"yes, in {req_games[c]} of {scope_games} games" if req_games[c]
                        else f"no, in none of {scope_games} games (required)"))
    if a.report_rest:
        parts.append("others above 0: " + (", ".join(f"{c} ({fired[c][0]} games)" for c in up) if up else "none"))
    if not total:
        parts.append("no games")
    lines.append(f"{a.label}: {'PASS' if ok else 'does not pass'}: " + "; ".join(parts) + f" ({total} games)")
    print("\n".join(lines))
    return ok


# --- floor ------------------------------------------------------------------------------------------------------------------

ENGINE_RE = re.compile(r"^- Engine: \S+ ")
COV_RE = re.compile(r"^- Coverage from (\S+) \(sha256 ([0-9a-f]{64});")
ROW_IDS_RE = re.compile(r"^\| [^|]*\(([^()|]*)\) \|")
TOTALS = ("**Verdict:", "Flagged cards", "| went first |", "| went second |", "Main attackers for these measures")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def cells(line):
    """A markdown table row's cells (the text between the bars, stripped)."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_caveat_row(line, key):
    m = ROW_IDS_RE.match(line)
    return bool(m) and key in [x.strip() for x in m.group(1).split(",")]


def compare_page(new, ref, a, opp_changed):
    """The page's (normalized) lines against the recorded page's: (differences that fail, differences the modes allow)."""
    fail, allowed = [], []
    if len(new) != len(ref):
        return [(0, f"{len(new)} lines", f"{len(ref)} lines")], allowed
    opp = a.report_opponent if opp_changed else None
    sec, worst = "", []
    for k, (x, y) in enumerate(zip(new, ref)):
        if y.startswith("## "):
            sec = y
        if opp and sec.startswith("## Worst matchups") and x.startswith("- ") and y.startswith("- "):
            worst.append(k)
            continue
        if x == y:
            continue
        if a.allow_caveat and is_caveat_row(x, a.allow_caveat) and is_caveat_row(y, a.allow_caveat):
            cx, cy = cells(x), cells(y)
            if len(cx) == len(cy) >= 3 and all(cx[j] == cy[j] for j in range(len(cx)) if j != 2):
                allowed.append(f"line {k + 1}, the row of {a.allow_caveat}, its engine cell only: recorded {cy[2]!r}; "
                               f"replayed {cx[2]!r}")
                continue
        if opp:
            if opp in x and opp in y:
                allowed.append(f"line {k + 1} names {opp}: recorded {y!r}; replayed {x!r}")
                continue
            if any(x.startswith(t) and y.startswith(t) for t in TOTALS):
                allowed.append(f"line {k + 1}, a total: recorded {y!r}; replayed {x!r}")
                continue
            if sec.startswith("## Coverage flag") and x.startswith("| ") and y.startswith("| "):
                cx, cy = cells(x), cells(y)
                if len(cx) == len(cy) == 6 and cx[:3] == cy[:3]:
                    allowed.append(f"line {k + 1}, {cx[0]}'s counts: recorded {cy[3:]}; replayed {cx[3:]}")
                    continue
        fail.append((k + 1, x, y))
    if worst:
        tag = f"- {opp}:"
        wn = sorted(new[k] for k in worst if not new[k].startswith(tag))
        wr = sorted(ref[k] for k in worst if not ref[k].startswith(tag))
        on = [new[k] for k in worst if new[k].startswith(tag)]
        orf = [ref[k] for k in worst if ref[k].startswith(tag)]
        if wn != wr or len(on) != 1 or len(orf) != 1:
            fail.append((worst[0] + 1, " / ".join(new[k] for k in worst), " / ".join(ref[k] for k in worst)))
        elif [new[k] for k in worst] != [ref[k] for k in worst]:
            allowed.append(f"the worst-matchup list: {opp}'s line recorded {orf[0]!r}, replayed {on[0]!r}; every other line "
                           f"equal (their order may move)")
    return fail, allowed


def floor(a):
    name, issues, extra = a.name, [], []
    new_g = os.path.join(a.newdir, f"{name}_games.jsonl")
    ref_g = os.path.join(a.refdir, f"{name}_games.jsonl")
    new, ref = read_jsonl(new_g), read_jsonl(ref_g)
    keyf = lambda g: (g.get("opponent"), g.get("seat"), g.get("seed"))  # noqa: E731
    for label, games in (("recorded", ref), ("replayed", new)):
        keys = [keyf(g) for g in games]
        if len(set(keys)) != len(keys):
            issues.append(f"the {label} page holds a game twice")
    expect = len(ref) if a.expect_games is None else a.expect_games
    if len(new) != expect or len(ref) != expect:
        issues.append(f"{len(new)} replayed games v {len(ref)} recorded (expected {expect} each)")
    fields = sorted(set().union(*(g.keys() for g in ref + new))) if ref or new else []
    opp = a.report_opponent
    bad, rep = [], []
    for k in range(min(len(new), len(ref))):
        if keyf(new[k]) != keyf(ref[k]):
            bad.append((k, ["the deal (opponent, seat, seed)"]))
            continue
        d = [f for f in fields if new[k].get(f, MISSING) != ref[k].get(f, MISSING)]
        if d:
            (rep if opp is not None and ref[k].get("opponent") == opp else bad).append((k, d))
    if bad:
        k, d = bad[0]
        issues.append(f"{len(bad)} games differ" + (f" (games against {opp} aside)" if opp else "")
                      + f"; the first, line {k + 1} {keyf(ref[k])}, on {', '.join(d)}")
    eq = min(len(new), len(ref)) - len(bad) - len(rep)
    if opp is not None:
        ro = [g for g in ref if g.get("opponent") == opp]
        no = [g for g in new if g.get("opponent") == opp]
        if not ro:
            issues.append(f"the recorded page holds no game against {opp} (--report-opponent)")
        extra.append(f"  REPORT-OPPONENT {opp}: {len(rep)} of {len(ro)} games differ (wins "
                     f"{sum(bool(g.get('won')) for g in ro)} -> {sum(bool(g.get('won')) for g in no)})"
                     + ("; a new page in step 15" if rep else "; every game equal"))
        if rep:
            k, d = rep[0]
            extra.append(f"  the first {opp} game that differs: line {k + 1} {keyf(ref[k])}, on {', '.join(d)}")
    same_bytes = open(new_g, "rb").read() == open(ref_g, "rb").read()
    cov_new = open(os.path.join(a.newdir, f"{name}_coverage.json"), "rb").read()
    cov_ref = open(os.path.join(a.refdir, f"{name}_coverage.json"), "rb").read()
    cov_desc = "byte-equal"
    if cov_new != cov_ref:
        cov_desc = "differs"
        if a.allow_caveat:
            key = a.allow_caveat
            cn, cr = json.loads(cov_new), json.loads(cov_ref)
            if (isinstance(cn, dict) and isinstance(cr, dict) and isinstance(cn.get(key), dict)
                    and isinstance(cr.get(key), dict)):
                ln_, lr_ = cn[key].get("limitations"), cr[key].get("limitations")
                cn[key]["limitations"] = cr[key]["limitations"] = None
                if cn == cr:
                    cov_desc = f"equal but for {key}'s limitations"
                    extra.append(f"  caveat {key}: the coverage's limitations, recorded {lr_!r}; replayed {ln_!r}")
        if cov_desc == "differs":
            issues.append("the coverage file differs from the recorded one"
                          + (f" (beyond {a.allow_caveat}'s limitations)" if a.allow_caveat else ""))
    raw_new = [ln.rstrip("\n") for ln in open(os.path.join(a.newdir, f"{name}.md"), encoding="utf-8")]
    raw_ref = [ln.rstrip("\n") for ln in open(os.path.join(a.refdir, f"{name}.md"), encoding="utf-8")]
    engine_lines = sum(bool(ENGINE_RE.match(ln)) for ln in raw_ref)
    if engine_lines != 1:
        issues.append(f"the recorded page has {engine_lines} '- Engine:' lines, not 1")
    if a.allow_coverage_program:
        cov_lines = {}
        for label, raw in (("recorded", raw_ref), ("replayed", raw_new)):
            found = [COV_RE.match(ln) for ln in raw if COV_RE.match(ln)]
            if len(found) != 1:
                issues.append(f"the {label} page has {len(found)} '- Coverage from' lines, not 1")
            else:
                cov_lines[label] = (found[0].group(1), found[0].group(2))
        if len(cov_lines) == 2:
            (pr, hr), (pn, hn) = cov_lines["recorded"], cov_lines["replayed"]
            extra.append(f"  coverage program: recorded {pr} (sha256 {hr[:16]}..), replayed {pn} (sha256 {hn[:16]}..)"
                         + (" (the same)" if (pr, hr) == (pn, hn) else
                            " (set aside in the page by --allow-coverage-program: the page names the goldfish floor.py "
                            "used; the coverage file itself is compared above)"))

    def norm(ln):
        ln = ENGINE_RE.sub("- Engine: <program> ", ln)
        if a.allow_coverage_program:
            m = COV_RE.match(ln)
            if m:
                ln = "- Coverage from <program> (sha256 <hash>;" + ln[m.end():]
        return ln

    md_new, md_ref = [norm(x) for x in raw_new], [norm(x) for x in raw_ref]
    fail, allowed = compare_page(md_new, md_ref, a, bool(rep))
    if fail:
        k, x, y = fail[0]
        issues.append(f"the page differs in {len(fail)} places: {len(md_new)} lines v {len(md_ref)}"
                      + (f", first at line {k}: {x!r} v {y!r}" if k else ""))
    for t in allowed:
        extra.append(f"  allowed: {t}")
    ok = not issues
    page_desc = (", equal but for the program path" + (" and the coverage program" if a.allow_coverage_program else "")
                 if not fail and not allowed else
                 (f", {len(allowed)} differences allowed by the modes (below)" if not fail else ""))
    print(f"{a.label}: {short(new_g)} v {short(ref_g)}: {eq} of {len(ref)} games equal on every field of the per-game "
          f"summary record ({len(fields)} fields: {', '.join(fields)}; no moves or decisions)"
          + (f", {len(rep)} games against {opp} reported" if opp is not None else "")
          + f"; the games file {'byte-equal' if same_bytes else 'not byte-equal'}; coverage {cov_desc}; page "
          f"{len(md_ref)} lines{page_desc}" + ("" if ok else "; DIFFERS: " + "; ".join(issues)))
    if extra:
        print("\n".join(extra))
    return ok


# --- the pairs files --------------------------------------------------------------------------------------------------------

def pairs7c(a):
    opps = sorted(glob.glob(os.path.join(a.repo, "decks", "screen", "opponents", "*.txt")))
    if len(opps) != 8:
        raise Malformed(f"decks/screen/opponents holds {len(opps)} lists, not 8")
    for d in DECKS_7C:
        if not os.path.isfile(os.path.join(a.repo, d)):
            raise Malformed(f"{d} is missing")
    rows, p = ["\t".join(PAIRS_HEAD)], FIRST_7C
    for d in DECKS_7C:
        key = os.path.splitext(os.path.basename(d))[0]
        for o in opps:
            oname = os.path.splitext(os.path.basename(o))[0]
            s = BASE_7C + 10_000 * p
            rows.append("\t".join(str(x) for x in (p, "rules7c", key, d, oname.removeprefix("t-"),
                                                   f"decks/screen/opponents/{oname}.txt", s, s + DEALS_7C - 1,
                                                   s + 9_999)))
            p += 1
    text = "\n".join(rows) + "\n"
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    last = p - 1
    print(f"pairs7c: {short(a.out)}: pairings {FIRST_7C}-{last} ({last - FIRST_7C + 1} rows: "
          f"{', '.join(os.path.splitext(os.path.basename(d))[0][:2] for d in DECKS_7C)} x the 8 panel lists), "
          f"i < {DEALS_7C}, seeds {BASE_7C + 10_000 * FIRST_7C:,} - {BASE_7C + 10_000 * last + DEALS_7C - 1:,} "
          f"(23,100,000,000 + pairing x 10,000 + i; step 8 uses pairings 0-31 and 8b 32-35, seeds up to "
          f"{BASE_7C + 10_000 * 35 + 499:,})")
    return True


def pairs7c2(a):
    opps = sorted(glob.glob(os.path.join(a.repo, "decks", "screen", "opponents", "*.txt")))
    names = [os.path.splitext(os.path.basename(o))[0] for o in opps]
    if len(opps) != 8 or not all(n.startswith("t-") for n in names):
        raise Malformed(f"decks/screen/opponents holds {names}, not the 8 t-* panel lists")
    if names[7] != "t-weezing":
        raise Malformed(f"the 8th sorted panel list is {names[7]}, not t-weezing (sitting1.sh names pairing 7 deck 10 v t-weezing)")
    for _, d, _ in HELD_7C2:
        if not os.path.isfile(os.path.join(a.repo, d)):
            raise Malformed(f"{d} is missing")
    rows, p, groups = ["\t".join(PAIRS_HEAD)], 0, []
    for key, d, what in HELD_7C2:
        first = p
        for oname in names:
            s = BASE_7C2 + SUB * p
            rows.append("\t".join(str(x) for x in (p, "rules2_7c", key, d, oname.removeprefix("t-"),
                                                   f"decks/screen/opponents/{oname}.txt", s, s + DEALS_7C2 - 1,
                                                   s + SUB - 1)))
            p += 1
        groups.append((first, p - 1, key, d, what))
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rows) + "\n")
    last = p - 1
    summary = (f"pairs7c2: {short(a.out)}: pairings 0-{last} ({last + 1} rows: deck 10, draft D's first list and draft D "
               f"amended x the 8 panel lists; deck 10 v t-weezing is pairing 7), i < {DEALS_7C2}, seeds {BASE_7C2:,} - "
               f"{BASE_7C2 + SUB * last + DEALS_7C2 - 1:,} (23,300,000,000 + pairing x 10,000 + i)")
    if a.seeds_out:
        files = sorted({d for _, d, _ in HELD_7C2} | {f"decks/screen/opponents/{n}.txt" for n in names})
        out = ["Rules switch 2's step 7c new rows (sitting1.sh, step 7c-seeds), recorded and committed before any 7c game.",
               f"Pairs file: {REL}/pairs_7c2.tsv ({last + 1} rows, sitting1_check.py pairs7c2; pairs_7c.tsv's columns, block "
               "rules2_7c).",
               "Block: 23,300,000,000 + pairing x 10,000 + i (rules switch 2's block, in START_HERE's seed table), i < 60, km3 "
               "in both seats; first_seat = i % 2:"]
        for first, end, key, d, what in groups:
            out.append(f"  pairings {first}-{end}: {key} ({d}): {what}; v the 8 panel lists in sorted order, seeds "
                       f"{BASE_7C2 + SUB * first:,} - {BASE_7C2 + SUB * end + DEALS_7C2 - 1:,}")
        out += ["Pairings 24-39, 47-59 and 63-99 of this block are unused here (40-46: step 8b's new rows; 60-62: step 8's Will "
                "rows; sitting2.sh).",
                "Oct 1's 32 rows (pairings 40-71 of 23,100,000,000, decks 02, 06, 08 and 14) are replayed from "
                "rl/results/engine_switch_rules_2026-10/pairs_7c.tsv in place (blob d747cf5f).",
                "The floor replays use floor.py's own seeds: 7,100 + 1,000 x opponent (seat 0) and + 500 (seat 1), as recorded.",
                "Deck files (repository path, git blob id of the bytes on disk):"]
        out += [f"  {d} {blob_id(os.path.join(a.repo, d))}" for d in files]
        with open(a.seeds_out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(out) + "\n")
    print(summary)
    return True


# --- the scripts ------------------------------------------------------------------------------------------------------------

def _assigned(tree, wanted):
    """{name: the literal value} of the module-level assignments to the wanted names (read with ast)."""
    found = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets, val = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, val = [node.target], node.value
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id in wanted:
                found[t.id] = ast.literal_eval(val)
    return found


def script_names(a):
    tb = load_counters(a.counters)
    order, names = tb["order"], tb["names"]
    src = open(a.patched, encoding="utf-8").read()
    missing = [n for n in order if f'"{n}"' not in src]
    lists = _assigned(ast.parse(open(a.coin, encoding="utf-8").read()), ("R2_COUNTERS", "R2_KEYED"))
    issues = []
    for k in ("R2_COUNTERS", "R2_KEYED"):
        v = lists.get(k)
        if not isinstance(v, (list, tuple)) or not all(isinstance(x, str) for x in v):
            issues.append(f"{short(a.coin)} has no list of names {k}")
            lists[k] = []
    r2 = list(lists["R2_COUNTERS"]) + list(lists["R2_KEYED"])
    want = [n for n in order if names[n][0] == "coin" and names[n][2] in ("reach2", "offgate2", "superset2")]
    if len(set(r2)) != len(r2):
        issues.append("the coin script names a round-2 counter twice")
    if set(r2) != set(want):
        issues.append(f"the coin script's R2_COUNTERS + R2_KEYED are not counters.tsv's round-2 rows: only in the script "
                      f"{sorted(set(r2) - set(want))}, only in counters.tsv {sorted(set(want) - set(r2))}")
    keyed = {n for n in want if names[n][1] == "keyed"}
    if set(lists["R2_KEYED"]) != keyed:
        issues.append(f"R2_KEYED {sorted(lists['R2_KEYED'])} is not counters.tsv's keyed round-2 rows {sorted(keyed)}")
    if missing:
        issues.append(f"the patched {os.path.basename(a.patched)} does not write {', '.join(missing)}")
    ok = not issues
    print(f"script-names: {short(a.patched)} with {short(a.coin)}: "
          + (f"all {len(order)} counters of {short(a.counters)} are written (a \"name\" string each); the coin script's "
             f"R2_COUNTERS + R2_KEYED ({len(r2)}) are exactly its {len(want)} round-2 rows, R2_KEYED its {len(keyed)} keyed ones"
             if ok else "DIFFERS: " + "; ".join(issues)))
    return ok


def attackers(a):
    found = _assigned(ast.parse(open(a.floorpy, encoding="utf-8").read()), ("ATTACKERS",))
    if "ATTACKERS" in found:
        v = found["ATTACKERS"]
        if not isinstance(v, dict) or not all(isinstance(k, str) for k in v):
            raise Malformed(f"{short(a.floorpy)}'s ATTACKERS is not a table keyed by deck path")
        if v:
            print("\n".join(sorted(v)))
    return True


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("counters"); c.add_argument("files", nargs="+"); c.add_argument("--label", required=True)
    c.add_argument("--counters", required=True)
    c.add_argument("--zero-role", action="append", default=[], choices=ROLE_NAMES)
    c.add_argument("--zero", action="append", default=[])
    c.add_argument("--require", action="append", default=[])
    c.add_argument("--in", dest="in_", metavar="PAIRINGS")
    c.add_argument("--report-rest", action="store_true")
    c.add_argument("--plain", action="append", default=[])
    f = sub.add_parser("floor"); f.add_argument("newdir"); f.add_argument("refdir"); f.add_argument("name")
    f.add_argument("--label", required=True)
    f.add_argument("--allow-coverage-program", action="store_true")
    f.add_argument("--report-opponent")
    f.add_argument("--allow-caveat")
    f.add_argument("--expect-games", type=int)
    p = sub.add_parser("pairs7c"); p.add_argument("--repo", required=True); p.add_argument("--out", required=True)
    q = sub.add_parser("pairs7c2"); q.add_argument("--repo", required=True); q.add_argument("--out", required=True)
    q.add_argument("--seeds-out")
    s = sub.add_parser("script-names"); s.add_argument("--counters", required=True); s.add_argument("--coin", required=True)
    s.add_argument("--patched", required=True)
    t = sub.add_parser("attackers"); t.add_argument("floorpy")
    a = ap.parse_args()
    fn = {"counters": counters, "floor": floor, "pairs7c": pairs7c, "pairs7c2": pairs7c2, "script-names": script_names,
          "attackers": attackers}[a.cmd]
    try:
        ok = fn(a)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, Malformed) as e:
        print(f"{a.cmd}: malformed or missing input: {e!r}")
        sys.exit(2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
