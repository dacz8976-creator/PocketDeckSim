#!/usr/bin/env python3
"""Rules switch 2 (rl/results/engine_switch_rules2_2026-10/): the checks sitting2.sh makes beside switch_check.py and
sitting1_check.py (PLAN.md steps 8b, 8 and 9's named rows, and 8c's hand-off; sitting1.sh's step 7c may also use `touched`
and `stepsum` for deck 10 v t-weezing). A copy of the Oct 1 switch's sitting2_check.py
(rl/results/engine_switch_rules_2026-10/), adapted by ADAPTATION_SPEC.md (Oct 9) items C2-1 to C2-12:
  - the counters come from counters.tsv here (--counters; default: $SWITCH2_COUNTERS, else the counters.tsv beside this
    file): 42 names in roles. This file holds only the 12 verdict groups (MECHANICS), and checks them against the file;
  - the rows and seeds are switch 2's (8b's new rows 40-46 and step 8's Will rows 60-62 on 23,300,000,000; the cloud's 8b
    rows 32-37 and Oct 1's carriers on 23,100,000,000);
  - a changed game gets a category and is never a finding by itself: Oct 1's "a changed game with every repair counter 0"
    finding is dropped (ADAPTATION_SPEC 1.12 and A7; PLAN.md section 6, the stop rule and the mechanic check: a changed game in a named row is
    judged by the mechanic check in 8c);
  - the hand-off names switch 2's engines, tools (tools_8c.tsv), rule and revert switches.
Standard library only. From sitting1_check.py (its own folder; sitting2.sh runs private copies side by side) it imports
only helpers whose code ADAPTATION_SPEC keeps unchanged: Malformed, as_exact, as_int, check_by_mechanic, short. It reads
counters.tsv itself; when sitting1_check.py read the same file at import, its role names (REACH2, OFFGATE2, ...,
ROUND2_QUEUED) must agree with this reading.

The counter model (counters.tsv: name, script, shape, role, mechanic, revert_switch, after comment lines; one comment line
"# ROUND2_QUEUED<tab>attack|attack|..." names the later coin round's attacks):
  reach2     round 2's exact counters (PLAN.md section 6, change 1, with section 0 (c)'s attack_return_weakness): only these explain a
             changed game on the board. coin_queued_by_attack counts for reach only on ROUND2_QUEUED's keys; its other keys
             (the first round's sites, which build the same choice on both engines) are round-1 evidence.
  offgate2   round 2's off-gate counters: a rewritten line ran and gave the old answer.
  superset2  trap_territory_two_in_play: never reach (PLAN.md section 6, change 1).
  r1_exact, r1_heads, r1_offgate, r1_superset   round 1's (both engines have round 1: never reach for this switch).
  Shapes: exact {n, first, ticks} (sitting1_check.as_exact), keyed {key: [strictly ascending ticks]} (fired when a list is
  not empty), int, int_or_null. A counter that is missing or malformed in a watch game is a malformed input.
A changed game's category (from its watch row): reach (a reach2 counter fired) / offgate_only (no reach2, an offgate2
fired: CONDITION 3) / other_only (only round-1 or superset counters fired, or round-1 keys of coin_queued_by_attack) / none
(no counter at all).

  pairs --set 8b2|will --repo R --out PAIRS.tsv [--seeds-out SEEDS.txt] [--seed-base B]
      Writes one of switch 2's new pairs files, in legality_scan's --pairs format with Oct 1's columns (pairing block
      held_key held_file opponent panel_file seed_first seed_last sub_block_end; paths relative to the repository, as
      --root R reads them). 8b2: pairings 40-46 (deck 12 v t-weezing and v t-lucario, deck 10 and brew-04 v t-weezing,
      water_round2 v meowth_carefree, houndoom_victini and deck 10 v c-magnezone_ex_magnezone); will: 60-62 (deck 10,
      brew-01 and brew-04 v t-weezing). seed_first = B (default 23,300,000,000) + 10,000 x pairing; seed_last covers the
      most deals the step plays there (40 in 8b, km3's 500 in step 8). --seeds-out: each row's seeds per bot and every
      deck file with its git blob id. Prints a one-line summary. Exit 0, or 2 when a deck file is missing.
  seedrec --repo R --out FILE --rows "LABEL|PAIRS|PAIRINGS|BOT=N,BOT=N" [...] [--reuse REUSE.tsv]
      Sitting 2's seed record (seeds_8_2.txt): for each --rows spec, the pairs file's rows of those pairings, each with its
      seed block (seed_first - 10,000 x pairing) and its seeds per bot; every deck file with its git blob id; the reused
      games (reuse.tsv) with their sha256, read now (each must be reuse.tsv's). No timestamps. Exit 0, or 2.
  model --counters C [--tightened tightened_rule.py]
      Reads counters.tsv as the model above and prints a one-line summary. Exit 2 when it is malformed, when MECHANICS does
      not group its reach2 counters exactly, or when sitting1_check.py reads it otherwise; with --tightened, exit 1 unless
      that file's ROUND2_QUEUED (read with ast, never run) is counters.tsv's.
  touched --old F [F ...] --new F --watch F --expect N --label L --step 7c|8b|8|9 --bot B --repo R --out-handoff F
          [--counters C] [--pairings P]
      One bot's scan set: the old side (a file the official legality_scan played, Oct 1's reused games, or a km3
      reference; several files make one side, keyed by (pairing, i): a deal in two is a duplicate), the new legality_scan
      and the watch build on the same deals. --pairings (a comma list, ranges allowed) keeps those pairings on all three
      sides. Each side must hold exactly N games, once each, the same deals, and each deal must be the same deal on all
      three (pairing, i, seed, first_seat, bots, decks and deck files, as far as the old side records them). Every watch
      game must carry every counter of the model in its shape, and must equal the new game on every field the new file
      records. A game is CHANGED when the new game differs from the old one on any field the old side records ("moves"
      differing is reported apart); its category comes from its watch row. Prints the set's lines (per pairing: games,
      identical, changed, by category; each fired counter by role: games, ticks, changed games; each off-gate counter in
      identical games; the categories; the changed games with no reach2 counter; the CONDITION 3 count) and writes the
      changed games to --out-handoff (HEADER's columns, header first). Exit 0 pass; 1 a finding (a count, a duplicate,
      other deals, a deal that is not the same deal, a field the old side records that the new file never writes, a
      malformed counter, watch not equal to new); 2 a malformed or missing input. A changed game is never a finding here:
      8c judges it.
  stepsum --step 7c|8b|8|9 --watch F [F ...] --rows F [F ...] [--counters C] [--pairings P]
      A step's lines over both bots, from the watch scans (--pairings keeps those pairings) and the hand-off rows: one
      reach verdict per mechanic ("reached in N games (M ticks)" or "UNREACHED (rests on its tests)", a report), the
      uncounted parts, each off-gate counter in identical games (a report: PLAN.md step 7b requires the off-gates only on
      the table, step 7b), the categories, the CONDITION 3 count. Its last line starts "SUMMARY: " and holds the phrase
      "changed <N> of <M> deals (<K> with no reach2 counter)" exactly once (the STEP line carries it; the gate and the pin
      read it). Exit 0, or 2 on a malformed input.
  handoff --tsv OUT --md OUT --candidate C --env switch2.env [--main M] [--tools tools_8c.tsv] [--counters C]
          [--rows F ...] [--files F ...]
      Rebuilds handoff_8c.tsv (one header, then every --rows file's rows in the order given) and handoff_8c.md (what 8c
      needs: totals per step and bot by category, the changed games per reach2 counter, the engines, the tools (each at
      the commit tools_8c.tsv names, with its blob), the pairs files and seed blocks, the --files with their sha256, the
      rule, the revert switches). No timestamps, so a rebuild of the same inputs is the same bytes.
  trace-gate FILE [--extra-rows F ...]
      Step 8c's gate before step 8 (Oct 1's, plus --extra-rows). FILE (trace_load.txt; read as utf-8-sig) holds exactly
      one line "TRACE LOAD <n> <free text naming the cloud commit>" (the text must hold a commit id, 7-40 hex characters)
      and, when the load is above 50, a line starting "DUSTIN " (his words). Other lines (CLOUD8B, CLOUD8B_OLD, read by
      sitting2.sh) are left alone. --extra-rows: hand-off row files (HEADER) of changed games the cloud's load does not
      cover (sitting2.sh passes the laptop's own 8b rows 40-46: the cloud played 32-37 only); each of their rows with no
      reach2 counter (category not reach) is added to n, since nothing has placed it yet, unless FILE has the line
      "COVERS 32-37,40-46" (the cloud's n covers the laptop's rows too). Prints the reading on its first
      line, then the marked lines "LOAD <n>" and "COMMIT <id>" once each when parsed (sitting2.sh reads exactly those, and
      checks the commit with git cat-file -e). Exit 0 when step 8 may run, 3 when it waits (missing, unparseable, an
      unreadable --extra-rows file, or a load above 50 with no DUSTIN line).
  cloud8b --new F --cloud F --bot km3|k3 --label L [--expect 240] [--pairings 32-37]
      The cloud's 8b rows v this run's rows for one bot (F: this run's file, kept to --pairings). The cloud's rows are
      first filtered to bot_a = the bot, those pairings, i < 40 (a file of both bots, or of more deals, is fine); they must
      then be exactly this run's deals, once each, else "not compared (owed)" with the reason. They are compared on the
      fields both files record, a_file and b_file left out (each checkout's own paths): exit 0 equal; 1 a matched deal
      differs (a halt); 3 not compared (owed: unreadable, other deals, or the cloud's rows lack a core field).
"""
import argparse, ast, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import sitting1_check as S1  # noqa: E402
    from sitting1_check import Malformed, as_exact, as_int, check_by_mechanic, short  # noqa: E402
except Exception as e:  # noqa: BLE001 (an import fault is a missing input, never read as a result)
    print(f"{(sys.argv[1:2] or ['sitting2_check'])[0]}: malformed or missing input: sitting1_check.py beside this file "
          f"cannot be imported ({e!r})")
    sys.exit(3 if sys.argv[1:2] in (["trace-gate"], ["cloud8b"]) else 2)

REL = "rl/results/engine_switch_rules2_2026-10"
OLDREL = "rl/results/engine_switch_rules_2026-10"   # Oct 1's switch: read in place, never written
BASE_OLD = 23_100_000_000
BASE_NEW = 23_300_000_000
PANEL_DIR = "decks/screen/opponents"
T_WEEZING, T_LUCARIO = f"{PANEL_DIR}/t-weezing.txt", f"{PANEL_DIR}/t-lucario.txt"
DECK10 = "decks/dustin/10-xatu-oricorio-tr-weezing.txt"
DECK12 = "decks/dustin/12-ariados-whimsicott-ogerpon.txt"
BREW01 = "decks/brews/brew-01-arceus-crobat-xatu.txt"
BREW04 = "decks/brews/brew-04-xatu-slowking.txt"
WATER = f"{REL}/scratch_8b2/water_round2.txt"   # P's rl/results/coin_prevention_round2_2026-10-01/smoke/water_round2.txt
MEOWTH = f"{OLDREL}/scratch_8b/meowth_carefree.txt"
HOUNDOOM = f"{OLDREL}/carriers/alternates/houndoom_victini.txt"
MAGNEZONE = "rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt"
# (pairing, held list, opponent name, opponent list); opponent names as Oct 1 ("t-" removed for the panel)
ROWS_8B2 = ((40, DECK12, "weezing", T_WEEZING), (41, DECK12, "lucario", T_LUCARIO), (42, DECK10, "weezing", T_WEEZING),
            (43, BREW04, "weezing", T_WEEZING), (44, WATER, "meowth_carefree", MEOWTH),
            (45, HOUNDOOM, "magnezone", MAGNEZONE), (46, DECK10, "magnezone", MAGNEZONE))
ROWS_WILL = ((60, DECK10, "weezing", T_WEEZING), (61, BREW01, "weezing", T_WEEZING), (62, BREW04, "weezing", T_WEEZING))
SETS = {"8b2": ("rules2_8b", ROWS_8B2, "8b", "8b's new rows (PLAN.md step 8b: the cloud's 5 other smoke pairings and the 2 "
                "block-coin rows)"),
        "will": ("rules2_will", ROWS_WILL, "8", "step 8's Will rows (PLAN.md step 8)")}
DEALS = {"8b": {"km3": 40, "k3": 40}, "8": {"km3": 500, "k3": 250}, "9": {"km3": 500}, "7c": {"km3": 60}}
PAIRINGS_8B_CLOUD = "32-37"
PATH_FIELDS = {"a_file", "b_file"}   # the cloud's paths may differ by design (its own checkout's lists)
CLOUD_CORE = ("pairing", "i", "seed", "first_seat", "bot_a", "bot_b", "moves", "decisions", "winner_seat", "points")
IDENT = ("pairing", "i", "seed", "first_seat", "bot_a", "bot_b", "a", "b", "a_file", "b_file")   # what makes it the same deal
PAIRS_HEAD = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last",
              "sub_block_end"]
# Each step's rows: the pairs file and the seed block a tracer needs (handoff_8c.md).
PAIRS_BY_STEP = (
    ("7c", "0-23 (the hand-off holds deck 10 v t-weezing, pairing 7)", f"{REL}/pairs_7c2.tsv", BASE_NEW),
    ("8b", "32-37 (the cloud's rows; 32-35 Oct 1's scratch rows)", f"{REL}/pairs_8b_cloud.tsv", BASE_OLD),
    ("8b", "40-46", f"{REL}/pairs_8b2.tsv", BASE_NEW),
    ("8", "0-31 (Oct 1's carriers)", f"{OLDREL}/pairs_8.tsv", BASE_OLD),
    ("8", "60-62 (the Will rows)", f"{REL}/pairs_will.tsv", BASE_NEW),
    ("9", "32-39 and 80-87 (B2e's named rows)", "rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv", 21_106_000_000),
)
MISSING = object()

# ---- The counter model (counters.tsv).
QUEUED = "coin_queued_by_attack"
QUEUED_R1 = "coin_queued_by_attack (round-1 keys)"   # the first round's sites: round-1 evidence, never reach
HELPER, BY_MECHANIC = "offgate_helper_choice", "offgate_helper_by_mechanic"
MODEL_HEAD = ["name", "script", "shape", "role", "mechanic", "revert_switch"]
ROLES = ("reach2", "offgate2", "superset2", "r1_exact", "r1_heads", "r1_offgate", "r1_superset")
ROLE_TEXT = {"reach2": "round 2's exact counters, the only reach; coin_queued_by_attack on ROUND2_QUEUED's keys",
             "offgate2": "round 2's off-gate counters: the rewritten lines ran and gave the old answer; never reach",
             "superset2": "round 2's superset; never reach",
             "r1_exact": "round 1's exact counters; both engines have round 1, so never reach here",
             "r1_heads": "round 1's Victory Star heads count; never reach",
             "r1_offgate": "round 1's off-gate counters, and coin_queued_by_attack's round-1 keys; never reach",
             "r1_superset": "round 1's supersets; never reach"}
SHAPES = ("exact", "keyed", "int", "int_or_null")
S1_NAMES = (("REACH2", "reach2"), ("OFFGATE2", "offgate2"), ("SUPERSET2", "superset2"), ("R1_EXACT", "r1_exact"),
            ("R1_HEADS", "r1_heads"), ("R1_OFFGATE", "r1_offgate"), ("R1_SUPERSET", "r1_superset"))
# The 12 reach verdicts (ADAPTATION_SPEC C2-3): label, what it is, its reach2 counters. Checked against counters.tsv.
MECHANICS = (
    ("sites", "the seven coin sites' queued coin choice (coin_queued_by_attack, ROUND2_QUEUED's attacks)", (QUEUED,)),
    ("plain-hit coin", "an attack's plain queued hit flips a coin Ability",
     ("coin_plain_damage_by_attack", "coin_plain_damage_chosen")),
    ("own-side coin", "a coin Ability flips for its own side's attack", ("coin_own_side_split",)),
    ("own-side Guts", "Guts flips for its own side's attack", ("guts_own_side_split",)),
    ("Perish Body", "Perish Body flips for a plain queued hit", ("perish_plain_hit_offered", "perish_plain_hit_chosen")),
    ("Will Confused", "Will on a Confused attacker's own first coin", ("will_confused_attack",)),
    ("Will block coin", "Will on a block coin", ("will_block_coin_attack",)),
    ("Victory Star block coin", "Victory Star after a block coin's heads",
     ("vs_block_coin_built", "vs_block_coin_choice_offered")),
    ("Trap Territory", "each Ariados adds 1 to the Retreat Cost",
     ("trap_territory_offer_changed", "trap_territory_outcome_changed")),
    ("Luxury Coin", "Luxury Coin not offered on the opponent's Stadium", ("luxury_coin_opp_stadium",)),
    ("Fossil lock", "a Fossil can't be played under an Item lock", ("fossil_item_lock",)),
    ("return Weakness", "an attack's return damage takes Weakness (P2)", ("attack_return_weakness",)),
)
UNCOUNTED = ("uncounted parts (no counter; a report, not a stop): P3's seven Fossil-as-Item places, Bounded Field x2, P1's "
             "caveat text and the Victini caveat text; no replayed list reaches them (PLAN.md section 3 and section 9, question 2a; "
             "RELEASE_PACKAGE.md, \"Recorded\")")
CATEGORIES = ("reach", "offgate_only", "other_only", "none")
COND3 = ("CONDITION 3 (the Oct 1 ruling, carried by Dustin's yes to question 1, PLAN.md section 6's precedents and section 9, question 1: a changed game "
         "where only round 2's off-gate counters fired)")
RULING = "each needs a trace meeting both halves in 8c; a pin-gate item, never a stop here"
HEADER = ("step", "bot", "pairing", "i", "seed", "held_file", "held_blob", "panel_file", "panel_blob", "old_moves",
          "new_moves", "moves_differ", "differing_fields", "old_winner", "new_winner", "old_points", "new_points",
          "category", "reach2_counters", "offgate2_counters", "round1_counters", "superset_counters", "revert_switches")


class Model:
    """counters.tsv: c {name: row}, roles {role: names in file order}, rq (ROUND2_QUEUED), final (no TO FINALIZE mark)."""

    def __init__(self, path):
        self.path = path
        with open(path, encoding="utf-8-sig") as f:
            lines = [ln.rstrip("\r\n") for ln in f]
        self.final = not (lines and lines[0].startswith("# TO FINALIZE"))
        self.c, self.rq, head = {}, None, None
        for ln in lines:
            if not ln.strip():
                continue
            if ln.startswith("#"):
                m = re.match(r"#\s*ROUND2_QUEUED\s+(\S.*)$", ln)
                if m:
                    if self.rq is not None:
                        raise Malformed(f"{short(path)}: two ROUND2_QUEUED lines")
                    self.rq = frozenset(x.strip() for x in m.group(1).split("|") if x.strip())
                continue
            cells = [x.strip() for x in ln.split("\t")]
            if head is None:
                if cells != MODEL_HEAD:
                    raise Malformed(f"{short(path)}: the header is {cells}, not {MODEL_HEAD}")
                head = cells
                continue
            if len(cells) != len(head):
                raise Malformed(f"{short(path)}: a row with {len(cells)} fields, not {len(head)}: {ln!r}")
            r = dict(zip(head, cells))
            if r["shape"] not in SHAPES or r["role"] not in ROLES or not re.fullmatch(r"[a-z0-9_]+", r["name"]):
                raise Malformed(f"{short(path)}: the row {ln!r} has an unknown name, shape or role")
            if r["name"] in self.c:
                raise Malformed(f"{short(path)}: {r['name']} is named twice")
            self.c[r["name"]] = r
        if not self.c:
            raise Malformed(f"{short(path)}: no counters")
        if not self.rq:
            raise Malformed(f"{short(path)}: no '# ROUND2_QUEUED<tab>a|b|...' line")
        self.roles = {ro: tuple(n for n, r in self.c.items() if r["role"] == ro) for ro in ROLES}
        grouped = [n for _, _, ns in MECHANICS for n in ns]
        if sorted(grouped) != sorted(self.roles["reach2"]):
            raise Malformed(f"{short(path)}: the reach2 counters ({', '.join(self.roles['reach2'])}) are not the ones "
                            f"sitting2_check.py's 12 verdict groups name ({', '.join(grouped)}): update MECHANICS first")
        if self.c.get(QUEUED, {}).get("shape") != "keyed" or self.c[QUEUED]["role"] != "reach2":
            raise Malformed(f"{short(path)}: {QUEUED} is not a keyed reach2 counter")
        if BY_MECHANIC in self.c and HELPER not in self.c:
            raise Malformed(f"{short(path)}: {BY_MECHANIC} without {HELPER}")
        # sitting1_check.py reads counters.tsv at import (ADAPTATION_SPEC C1-2, C1-9): when it read this same file, the two
        # readings must agree (it tolerates an unreadable file at import, so a file it could not read is not compared).
        s1_table = getattr(S1, "TABLE", None)
        s1_path = s1_table.get("path") if isinstance(s1_table, dict) else None
        if (s1_path and not getattr(S1, "COUNTERS_ERROR", None)
                and os.path.realpath(s1_path) == os.path.realpath(path)):
            for nm, ro in S1_NAMES:
                v = getattr(S1, nm, None)
                if v is not None and set(v) != set(self.roles[ro]):
                    raise Malformed(f"sitting1_check.py's {nm} ({', '.join(sorted(v))}) is not counters.tsv's {ro} "
                                    f"({', '.join(self.roles[ro])})")
            v = getattr(S1, "ROUND2_QUEUED", None)
            if v is not None and set(v) != set(self.rq):
                raise Malformed(f"sitting1_check.py's ROUND2_QUEUED is not counters.tsv's: {sorted(set(v) ^ set(self.rq))}")


def default_counters():
    return os.environ.get("SWITCH2_COUNTERS") or os.path.join(HERE, "counters.tsv")


def keyed(g, name):
    """A keyed counter: {key: [strictly ascending int ticks]}."""
    v = g.get(name, MISSING)
    where = f"game {(g.get('pairing'), g.get('i'))}: {name}"
    if not isinstance(v, dict):
        raise Malformed(f"{where} is {v!r}, not {{key: [ticks]}}")
    for k, t in v.items():
        if (not isinstance(k, str) or not isinstance(t, list)
                or not all(isinstance(x, int) and not isinstance(x, bool) for x in t)
                or any(p >= q for p, q in zip(t, t[1:]))):
            raise Malformed(f"{where}: {k!r}: {t!r} is not a list of strictly ascending ticks")
    return v


def vals_of(m, g):
    """Every counter of the model in game g, shape-checked: exact -> its ticks, keyed -> {key: ticks}, int, int or None."""
    out = {}
    for name, c in m.c.items():
        if name not in g:
            raise Malformed(f"game {(g.get('pairing'), g.get('i'))}: no {name} (not the watch build's output?)")
        sh = c["shape"]
        if sh == "exact":
            as_exact(g, name)
            out[name] = list(g[name]["ticks"])
        elif sh == "keyed":
            out[name] = keyed(g, name)
        elif sh == "int":
            out[name] = as_int(g, name)
        else:
            v = g[name]
            if v is not None and (not isinstance(v, int) or isinstance(v, bool)):
                raise Malformed(f"game {(g.get('pairing'), g.get('i'))}: {name} is {v!r}, not null or a tick")
            out[name] = v
    if BY_MECHANIC in m.c:
        check_by_mechanic(g)
    return out


def part_of(m, name, v, part="all"):
    """The counter's value as counted: for coin_queued_by_attack, part 'r2' keeps ROUND2_QUEUED's keys and 'r1' the
    others; a keyed counter loses its empty lists."""
    if m.c[name]["shape"] != "keyed":
        return v
    if name == QUEUED and part == "r2":
        return {k: t for k, t in v.items() if k in m.rq and t}
    if name == QUEUED and part == "r1":
        return {k: t for k, t in v.items() if k not in m.rq and t}
    return {k: t for k, t in v.items() if t}


def ticks(m, name, v, part="all"):
    """How often it fired: exact, its ticks; keyed, the ticks of its keys (see part_of); int, its value; int_or_null, 1
    when set."""
    sh = m.c[name]["shape"]
    if sh == "exact":
        return len(v)
    if sh == "keyed":
        return sum(len(t) for t in part_of(m, name, v, part).values())
    if sh == "int":
        return v
    return 0 if v is None else 1


def fired_all(m, vals):
    """{counter: ticks} for every counter that fired; coin_queued_by_attack's round-2 keys under its name, its round-1
    keys under QUEUED_R1."""
    out = {}
    for name in m.c:
        t = ticks(m, name, vals[name], "r2" if name == QUEUED else "all")
        if t:
            out[name] = t
    t = ticks(m, QUEUED, vals[QUEUED], "r1")
    if t:
        out[QUEUED_R1] = t
    return out


def classify(m, vals):
    """category, reach2, offgate2, round1, superset: the fired counters of each kind with every tick."""
    r2 = {n: part_of(m, n, vals[n], "r2") for n in m.roles["reach2"] if ticks(m, n, vals[n], "r2")}
    og = {n: part_of(m, n, vals[n]) for n in m.roles["offgate2"] if ticks(m, n, vals[n])}
    r1 = {n: part_of(m, n, vals[n]) for ro in ("r1_exact", "r1_heads", "r1_offgate") for n in m.roles[ro]
          if ticks(m, n, vals[n])}
    if ticks(m, QUEUED, vals[QUEUED], "r1"):
        r1[QUEUED_R1] = part_of(m, QUEUED, vals[QUEUED], "r1")
    sp = {n: vals[n] for ro in ("superset2", "r1_superset") for n in m.roles[ro] if ticks(m, n, vals[n])}
    cat = "reach" if r2 else "offgate_only" if og else "other_only" if (r1 or sp) else "none"
    return cat, r2, og, r1, sp


def cond3_line(n, first=None):
    if not n:
        return f"{COND3}: 0 games"
    return (f"{COND3}: {n} games (changed, an off-gate counter fired, no reach2 counter"
            + (f"; the first {first}" if first is not None else "") + f"); {RULING}")


def parse_pairings(spec):
    """'32-39,80,81' -> {32, ..., 39, 80, 81}."""
    out = set()
    for part in (x.strip() for x in str(spec).split(",")):
        if not part:
            continue
        mm = re.fullmatch(r"(\d+)-(\d+)", part)
        if mm and int(mm.group(1)) <= int(mm.group(2)):
            out |= set(range(int(mm.group(1)), int(mm.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
        else:
            raise ValueError(f"pairings {spec!r}: {part!r} is not a pairing or a range")
    if not out:
        raise ValueError(f"pairings {spec!r}: none")
    return out


def blob_id(path):
    """git's blob id of the file's bytes (git hash-object --no-filters; the repository's .gitattributes say * -text)."""
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def cj(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True)


def key_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def tsv_rows(path):
    """A --pairs file's rows as dicts (read as legality_scan reads it: BOM dropped, fields trimmed)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    if not lines:
        raise Malformed(f"{short(path)} is empty")
    header = [h.strip() for h in lines[0].split("\t")]
    return [dict(zip(header, (x.strip() for x in ln.split("\t")))) for ln in lines[1:]]


def data_rows(path):
    """A data file's rows (ADAPTATION_SPEC 1.2: '#' comment lines, then a header row, then tab-separated rows)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip() and not ln.startswith("#")]
    if not lines:
        raise Malformed(f"{short(path)} has no header")
    header = [h.strip() for h in lines[0].split("\t")]
    rows = []
    for ln in lines[1:]:
        cells = [x.strip() for x in ln.split("\t")]
        if len(cells) != len(header):
            raise Malformed(f"{short(path)}: a row with {len(cells)} fields, not {len(header)}: {ln!r}")
        rows.append(dict(zip(header, cells)))
    return rows


def read_env(path):
    """switch2.env: KEY=VALUE lines read with a regex, never sourced."""
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for n, ln in enumerate(f, 1):
            ln = ln.rstrip("\r\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            mm = re.fullmatch(r"([A-Z0-9_]+)=([^ ]*)", ln)
            if not mm:
                raise Malformed(f"{short(path)} line {n} is not KEY=VALUE")
            out[mm.group(1)] = mm.group(2)
    return out


# ---- pairs, seedrec, model.
def pairs(a):
    block, rows, st, what = SETS[a.set]
    deals = max(DEALS[st].values())
    files = sorted({x for _, h, _, o in rows for x in (h, o)})
    missing = [f for f in files if not os.path.isfile(os.path.join(a.repo, f))]
    if missing:
        raise Malformed(f"deck files missing: {', '.join(missing)}")
    lines = ["\t".join(PAIRS_HEAD)]
    for p, held, opp, pf in rows:
        s = a.seed_base + 10_000 * p
        lines.append("\t".join(str(x) for x in (p, block, key_of(held), held, opp, pf, s, s + deals - 1, s + 9_999)))
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    first, last = rows[0][0], rows[-1][0]
    if a.seeds_out:
        sl = [f"Rules switch 2, {what}: seeds {a.seed_base:,} + pairing x 10,000 + i (sitting2.sh, step 8-seeds), recorded "
              "and committed before any game. Same bot in both seats; the held list in seat 0 on even i.",
              f"Pairings ({os.path.basename(a.out)}; held list v opponent; seed ranges by bot):"]
        for p, held, opp, pf in rows:
            s = a.seed_base + 10_000 * p
            rng = "; ".join(f"{b} i < {n}: {s:,} - {s + n - 1:,}" for b, n in DEALS[st].items())
            sl.append(f"  {p} (step {st}): {held} v {pf}: {rng}")
        sl.append("Deck files (repository path, git blob id of the bytes on disk):")
        sl += [f"  {f} {blob_id(os.path.join(a.repo, f))}" for f in files]
        with open(a.seeds_out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(sl) + "\n")
    print(f"pairs {a.set}: {os.path.basename(a.out)}: pairings {first}-{last} ({len(rows)} rows: {what}); seeds "
          f"{a.seed_base + 10_000 * first:,} - {a.seed_base + 10_000 * last + deals - 1:,} ({a.seed_base:,} + pairing x "
          f"10,000 + i; " + ", ".join(f"{b} i < {n}" for b, n in DEALS[st].items()) + f"); {len(files)} deck files")
    return 0


def seedrec(a):
    sl = ["Rules switch 2, sitting 2's seeds (sitting2.sh, step 8-seeds), recorded and committed before any 8b or 8 game. "
          "seed = block + pairing x 10,000 + i, the same bot in both seats, the held list in seat 0 on even i (legality_scan "
          "--pairs; START_HERE's seed table: 23,100,000,000 for Oct 1's carriers and the cloud's 8b rows 32-37, "
          "23,300,000,000 for switch 2's new rows).",
          "Rows by step (pairs file; held list v opponent; the row's block; seed ranges by bot):"]
    files, n_rows = set(), 0
    for spec in a.rows:
        parts = spec.split("|")
        if len(parts) != 4:
            raise Malformed(f"--rows {spec!r} is not LABEL|PAIRS|PAIRINGS|BOT=N,...")
        label, path, pl, deals = parts
        want = parse_pairings(pl)
        dl = []
        for x in deals.split(","):
            b, _, n = x.partition("=")
            if not n.isdigit():
                raise Malformed(f"--rows {spec!r}: {x!r} is not BOT=N")
            dl.append((b, int(n)))
        rows = [r for r in tsv_rows(path) if int(r["pairing"]) in want]
        got = sorted(int(r["pairing"]) for r in rows)
        if got != sorted(want):
            raise Malformed(f"{short(path)} holds pairings {got} of {sorted(want)}, not each once")
        sl.append(f"{label} ({short(path)}, pairings {pl}):")
        for r in sorted(rows, key=lambda r: int(r["pairing"])):
            p, s0 = int(r["pairing"]), int(r["seed_first"])
            rng = "; ".join(f"{b} i < {n}: {s0:,} - {s0 + n - 1:,}" for b, n in dl)
            sl.append(f"  {p}: {r['held_file']} v {r['panel_file']} (block {s0 - 10_000 * p:,}): {rng}")
            files |= {r["held_file"], r["panel_file"]}
            n_rows += 1
    sl.append("Deck files (repository path, git blob id of the bytes on disk):")
    sl += [f"  {f} {blob_id(os.path.join(a.repo, f))}" for f in sorted(files)]
    n_reuse = 0
    if a.reuse:
        sl.append("Reused games, the old side of step 8's carriers and 8b's rows 32-35 (Oct 1's recorded new-engine games, "
                  "reuse.tsv; path, sha256 read now, games, bot, pairings, deals):")
        for r in data_rows(a.reuse):
            h = hashlib.sha256(open(os.path.join(a.repo, r["path"]), "rb").read()).hexdigest()
            if h != r["sha256"]:
                raise Malformed(f"{r['path']} has sha256 {h[:16]}.., not reuse.tsv's {r['sha256'][:16]}..")
            sl.append(f"  {r['path']} {h} {r['games']} games, {r['bot']}, pairings {r['pairings']}, i < {r['deals']}")
            n_reuse += 1
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sl) + "\n")
    print(f"seedrec: {os.path.basename(a.out)}: {n_rows} rows in {len(a.rows)} sets, {len(files)} deck files, "
          f"{n_reuse} reused files")
    return 0


def round2_queued_of(path):
    """tightened_rule.py's ROUND2_QUEUED, read with ast (never run)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "ROUND2_QUEUED" for t in node.targets):
            v = node.value
            if (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                    and v.func.id in ("frozenset", "set", "tuple", "list") and len(v.args) == 1 and not v.keywords):
                v = v.args[0]
            return set(ast.literal_eval(v))
    raise Malformed(f"{short(path)} has no ROUND2_QUEUED assignment")


def model_cmd(a):
    m = Model(a.counters)
    sw = sorted({r["revert_switch"] for r in m.c.values()} - {"-", ""})
    line = (f"counters.tsv: {len(m.c)} counters (" + ", ".join(f"{ro} {len(m.roles[ro])}" for ro in ROLES)
            + f"); ROUND2_QUEUED: {len(m.rq)} attacks; the {len(MECHANICS)} verdict groups cover the "
            f"{len(m.roles['reach2'])} reach2 counters; revert switches named: {', '.join(sw) or 'none'}"
            + ("" if m.final else "; NOTE the file is marked TO FINALIZE"))
    if a.tightened:
        rq = round2_queued_of(a.tightened)
        if rq != set(m.rq):
            print(line + f"; the classifier's ROUND2_QUEUED differs ({short(a.tightened)}): only there "
                  f"{sorted(rq - m.rq)}, only in counters.tsv {sorted(m.rq - rq)}")
            return 1
        line += "; the classifier's ROUND2_QUEUED is the same"
    print(line)
    return 0


# ---- touched, stepsum.
def read_set(path, want=None):
    """{(pairing, i): game}, the deals seen twice, and the number of games (only the pairings in want, when given)."""
    out, dup, n = {}, [], 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            if want is not None and g["pairing"] not in want:
                continue
            k = (g["pairing"], g["i"])
            if k in out:
                dup.append(k)
            out[k] = g
            n += 1
    return out, dup, n


def touched(a):
    m = Model(a.counters)
    want = parse_pairings(a.pairings) if a.pairings else None
    issues = []
    old, odup, on = {}, [], 0
    for path in a.old:
        g, dup, n = read_set(path, want)
        odup += dup
        on += n
        for k, v in g.items():
            if k in old:
                odup.append(k)
            old[k] = v
    new, ndup, nn = read_set(a.new, want)
    watch, wdup, wn = read_set(a.watch, want)
    for nm, games, dup, n in (("old", old, odup, on), ("new", new, ndup, nn), ("watch", watch, wdup, wn)):
        if dup:
            issues.append(f"the {nm} side holds {len(dup)} deals twice (first {dup[0]})")
        if n != a.expect or len(games) != a.expect:
            issues.append(f"the {nm} side holds {n} games ({len(games)} deals), expected {a.expect}")
    if not set(old) == set(new) == set(watch):
        issues.append("the three sides do not hold the same deals (old-only "
                      f"{len(set(old) - set(new) - set(watch))}, new-only {len(set(new) - set(old))}, "
                      f"watch-only {len(set(watch) - set(old))})")
    fields = sorted(set().union(*(g.keys() for g in old.values()))) if old else []
    nfields = sorted(set().union(*(g.keys() for g in new.values()))) if new else []
    lacking = sorted(set(fields) - set(nfields))
    if lacking:   # a field the new program never writes would make every game "changed": a fault, not a result
        issues.append(f"the new file records no {', '.join(lacking)}, which the old side records")
    keys = sorted(set(old) & set(new) & set(watch))
    stat = {}                                   # counter: [games where it fired, ticks, changed games where it fired]
    og_ident = {c: 0 for c in m.roles["offgate2"]}
    per, cats, out_rows = {}, dict.fromkeys(CATEGORIES, 0), []
    bad_shape, not_same, watch_bad, c3 = [], [], [], []
    blobs = {}

    def blob(p):
        if p not in blobs:
            q = os.path.join(a.repo, p) if p else ""
            blobs[p] = blob_id(q) if p and os.path.isfile(q) else "missing"
        return blobs[p]

    changed_n = moves_n = ident_n = 0
    for k in keys:
        o, n_, w = old[k], new[k], watch[k]
        try:
            vals = vals_of(m, w)
        except Malformed as e:
            bad_shape.append(str(e))
            continue
        nd = [f for f in IDENT if f in o and (n_.get(f, MISSING) != o[f] or w.get(f, MISSING) != o[f])]
        if nd:
            not_same.append((k, nd))
            continue
        wb = [f for f in nfields if w.get(f, MISSING) != n_.get(f, MISSING)]
        if wb:
            watch_bad.append((k, wb))
        d_new = [f for f in fields if n_.get(f, MISSING) != o.get(f, MISSING)]
        changed = bool(d_new)
        mv = n_.get("moves") != o.get("moves")
        row = per.setdefault(k[0], {"a": n_.get("a"), "b": n_.get("b"), "games": 0, "identical": 0, "changed": 0,
                                    "moves": 0, **dict.fromkeys(CATEGORIES, 0)})
        row["games"] += 1
        row["changed" if changed else "identical"] += 1
        row["moves"] += mv
        for nm, t in fired_all(m, vals).items():
            s = stat.setdefault(nm, [0, 0, 0])
            s[0] += 1
            s[1] += t
            s[2] += changed
        if not changed:
            ident_n += 1
            for c in og_ident:
                og_ident[c] += bool(ticks(m, c, vals[c]))
            continue
        changed_n += 1
        moves_n += mv
        cat, r2, og, r1, sp = classify(m, vals)
        cats[cat] += 1
        row[cat] += 1
        if cat == "offgate_only":
            c3.append(k)
        sw = sorted({m.c[n]["revert_switch"] for n in r2} - {"-", ""})
        out_rows.append((a.step, a.bot, k[0], k[1], n_.get("seed"), n_.get("a_file") or "", blob(n_.get("a_file")),
                         n_.get("b_file") or "", blob(n_.get("b_file")), o.get("moves"), n_.get("moves"),
                         "yes" if mv else "no", ",".join(d_new), o.get("winner_seat"), n_.get("winner_seat"),
                         cj(o.get("points")), cj(n_.get("points")), cat, cj(r2), cj(og), cj(r1), cj(sp), ",".join(sw)))
    with open(a.out_handoff, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in out_rows:
            f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    lab = a.label
    no_reach = changed_n - cats["reach"]
    lines = [f"{lab}: {', '.join(short(p) for p in a.old)} / {short(a.new)} / {short(a.watch)}"
             + (f" (pairings {a.pairings} only)" if want is not None else "")
             + f": {len(keys)} deals on all three sides (expected {a.expect} each); {ident_n} identical to the old game on "
             f"every field the old side records ({len(fields)} fields: {', '.join(fields)}), {changed_n} changed "
             f"({moves_n} with different moves)"]
    for p in sorted(per):
        r = per[p]
        lines.append(f"  pairing {p} {r['a']} v {r['b']}: {r['games']} games, {r['identical']} identical, "
                     f"{r['changed']} changed ({r['moves']} with different moves; "
                     + ", ".join(f"{c} {r[c]}" for c in CATEGORIES) + ")")
    for ro in ROLES:
        names = list(m.roles[ro]) + ([QUEUED_R1] if ro == "r1_offgate" else [])
        fired = [n for n in names if n in stat]
        lines.append(f"  {ro} ({ROLE_TEXT[ro]}): "
                     + ("; ".join(f"{n} in {stat[n][0]} games ({stat[n][1]} ticks; {stat[n][2]} of them changed)"
                                  for n in fired) or "none fired")
                     + (f"; {len(names) - len(fired)} others 0 in every game" if len(names) > len(fired) else ""))
    lines.append("  off-gate counters in identical games (the rewritten lines ran and gave the old answer; a report): "
                 + "; ".join(f"{c} in {og_ident[c]} of {ident_n}" for c in og_ident))
    lines.append("  changed games by category: " + ", ".join(f"{c} {cats[c]}" for c in CATEGORIES)
                 + f"; with no reach2 counter: {no_reach} of {changed_n} (8c places every changed game's first difference, "
                 f"these included; no category stops the runner). Rows: {short(a.out_handoff)}")
    lines.append("  " + cond3_line(len(c3), c3[0] if c3 else None))
    if not_same:
        k, d = not_same[0]
        issues.append(f"{len(not_same)} deals are not the same deal on the three sides (the first {k} on {', '.join(d)}): "
                      "a pairs file, seed or bot fault, not a game result")
    if watch_bad:
        k, d = watch_bad[0]
        issues.append(f"{len(watch_bad)} watch games differ from the new game (the first {k} on {', '.join(d)})")
    if bad_shape:
        issues.append(f"{len(bad_shape)} watch games with a malformed counter, the first: {bad_shape[0]}")
    ok = not issues
    lines.append(f"{lab}: {'PASS' if ok else 'does not pass'}: {len(keys)} deals; {changed_n} changed ({no_reach} with no "
                 f"reach2 counter; " + ", ".join(f"{c} {cats[c]}" for c in CATEGORIES) + f"); CONDITION 3: {len(c3)} games"
                 + ("" if ok else "; " + "; ".join(issues)))
    print("\n".join(lines))
    return 0 if ok else 1


def read_rows(paths):
    rows = []
    for path in paths or []:
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
        if not lines or tuple(lines[0].split("\t")) != HEADER:
            raise Malformed(f"{short(path)} does not start with the hand-off header")
        for ln in lines[1:]:
            r = ln.split("\t")
            if len(r) != len(HEADER):
                raise Malformed(f"{short(path)}: a row with {len(r)} fields, not {len(HEADER)}")
            rows.append(dict(zip(HEADER, r)))
    return rows


def stepsum(a):
    m = Model(a.counters)
    want = parse_pairings(a.pairings) if a.pairings else None
    rows = read_rows(a.rows)
    changed_keys = {(r["bot"], int(r["pairing"]), int(r["i"])) for r in rows}
    mech = {lab: [0, 0] for lab, _, _ in MECHANICS}
    og = {c: [0, 0] for c in m.roles["offgate2"]}   # identical games where it fired, identical games
    deals = 0
    for path in a.watch:
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                w = json.loads(ln)
                if want is not None and w["pairing"] not in want:
                    continue
                deals += 1
                vals = vals_of(m, w)
                for lab, _, names in MECHANICS:
                    t = sum(ticks(m, n, vals[n], "r2") for n in names)
                    if t:
                        mech[lab][0] += 1
                        mech[lab][1] += t
                if (w.get("bot_a"), w["pairing"], w["i"]) not in changed_keys:
                    for c in og:
                        og[c][1] += 1
                        og[c][0] += bool(ticks(m, c, vals[c]))
    cats = dict.fromkeys(CATEGORIES, 0)
    for r in rows:
        if r["category"] not in cats:
            raise Malformed(f"a hand-off row's category is {r['category']!r}")
        cats[r["category"]] += 1
    changed = len(rows)
    no_reach = changed - cats["reach"]
    c3 = [r for r in rows if r["category"] == "offgate_only"]
    lines = []
    for lab, what, names in MECHANICS:
        v = mech[lab]
        lines.append(f"{a.step} (all bots): reach verdict {lab} ({what}; {', '.join(names)}): "
                     + (f"reached in {v[0]} games ({v[1]} ticks)" if v[0] else "UNREACHED (rests on its tests)"))
    lines.append(f"{a.step}: {UNCOUNTED}")
    lines.append(f"{a.step}: off-gate counters in identical games (a report; PLAN.md step 7b requires the off-gates only on "
                 "the table, step 7b): " + "; ".join(f"{c} in {x[0]} of {x[1]}" for c, x in og.items()))
    lines.append(f"{a.step}: changed games: {changed} of {deals} deals, {no_reach} with no reach2 counter; by category: "
                 + ", ".join(f"{c} {cats[c]}" for c in CATEGORIES) + " (8c places every changed game's first difference; "
                 "no category stops the runner)")
    first = f"({c3[0]['pairing']}, {c3[0]['i']}) {c3[0]['bot']}" if c3 else None
    lines.append(f"{a.step}: {cond3_line(len(c3), first)}")
    reached = [f"{lab} {v[0]} games ({v[1]} ticks)" for lab, v in mech.items() if v[0]]
    unreached = [lab for lab, v in mech.items() if not v[0]]
    summ = ["reached: " + (", ".join(reached) or "none"),
            "unreached (they rest on their tests): " + (", ".join(unreached) or "none"),
            f"changed {changed} of {deals} deals ({no_reach} with no reach2 counter)",
            "by category " + ", ".join(f"{c} {cats[c]}" for c in CATEGORIES),
            f"CONDITION 3: {len(c3)} games"]
    lines.append("SUMMARY: " + "; ".join(summ))
    print("\n".join(lines))
    return 0


# ---- The hand-off for 8c.
ENGINES = """- **old**: the official engine, {old_name} (`{official7}`; engine/ tree {official_tree7}), the pinned programs
  `{old_dir}/` (legality_scan sha256 {old_scan}). Where the old side is reused (step 8's carriers, pairings 0-31, and
  8b's pairings 32-35): Oct 1's recorded new-engine games (`{oldrel}/5a18d31_8_new_*.jsonl`, `5a18d31_8b_new_*.jsonl`;
  `reuse.tsv`), played by that same program on the same seeds (PLAN.md section 3, the real cost). Step 9's old side: km3's B2e reference
  (`km_tables_2026-09-30/1f6319e_b2e_km3.jsonl`), which the first switch's step 9 found equal to this engine's games.
- **new**: the candidate {c} (main {main7} + P {p7}; engine/ = P's tree {ptree7}), built by sitting 1:
  `programs.sha256` (the plain legality_scan) and `watch.sha256` (the watch build: the Victory Star script and the coin
  script at P, so the counters of `counters.tsv`)."""
TOOLS_TEXT = """- **Pass each row's own bot** (its `bot` column: km3 or k3). The tracer and the probes default to kog3: a trace
  or probe under the default bot is another game.
- **Each row's deal:** its pairs file and seed block (the table below); seed = block + pairing x 10,000 + i; even i puts
  the held list in seat 0; the same bot in both seats.
- **Check each trace's move fingerprint** against the row's old_moves (the old engine's trace) and new_moves (the
  candidate's) before reading anything else from it: a trace that does not reproduce its game explains nothing.
- **Rows with moves_differ = no** (the games differ only in points, winner or another field, with the same moves): look at
  their state hashes and final boards; a prefix game is judged like any other board difference (PLAN.md section 6, change 2)."""
RULE = """PLAN.md section 6, the mechanic check: the last plan's mechanic check, with three changes.
1. **The reach counters** are round 2's exact counters (`counters.tsv`, role reach2: {n_reach} counters, section 0 (c)'s
   `attack_return_weakness` included); `coin_queued_by_attack` counts only ROUND2_QUEUED's attacks
   ({rq}). The supersets (`trap_territory_two_in_play`, `coin_defender_attack`, `vs_confused_attack`) and round 1's counters
   never count. A changed game is ON THE BOARD only when such a counter fired at or before the first differing tick k, in
   k's turn or at the cause tick; a firing after k, or in an earlier turn other than the cause tick, explains nothing.
2. **A prefix game** (one game longer or shorter than the other) is judged like any other board difference (precondition
   b): an exact counter at the extra tick, or nothing.
3. **IN LOOKAHEAD** (the same state and offered moves, a different choice) needs both halves: the code gate, and coin_probe
   v2 finding the gate's condition inside the bots' search at k; and the revert check: turning that gate off (its switch set
   below, alone: one name, or the names joined by "+" set together, as the seven sites need G1 off too; and
   `DECKGYM_ROUND2_OFF` for every gate together) must bring back the old engine's choice and scores. A game meeting the
   first two but failing the revert check is a stop.
Anything else is UNEXPLAINED: a stop, and it comes to Dustin first. A trace that needs a judgment call doesn't stop the
replays, but the pin waits for Dustin's word on it (PLAN.md section 6). Precedents (game 28, the 8 of `8c_DECISION.md`)
were that switch's own exceptions: a similar game this time is a new judgment call (PLAN.md section 6, precedents).
The categories above are the runner's sorting, not verdicts: reach (a reach2 counter fired somewhere in the game; 8c still
places it against k), offgate_only ({cond3}), other_only, none. None of them stopped the runner; 8c decides every row."""


def handoff(a):
    env = read_env(a.env)
    m = Model(a.counters)
    rows = read_rows(a.rows)
    with open(a.tsv, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(r[h] for h in HEADER) + "\n")
    order = {"7c": 0, "8b": 1, "8": 2, "9": 3}
    tot, mech = {}, {}
    for r in rows:
        t = tot.setdefault((r["step"], r["bot"]), {"changed": 0, "moves": 0, **dict.fromkeys(CATEGORIES, 0)})
        t["changed"] += 1
        t["moves"] += r["moves_differ"] == "yes"
        t[r["category"]] = t.get(r["category"], 0) + 1
        for c in json.loads(r["reach2_counters"] or "{}"):
            mech.setdefault((r["step"], r["bot"]), {}).setdefault(c, 0)
            mech[(r["step"], r["bot"])][c] += 1
    srt = sorted(tot, key=lambda sb: (order.get(sb[0], 9), sb[1] != "km3", sb))
    c7 = a.candidate[:7]
    c3 = sum(t["offgate_only"] for t in tot.values())
    md = ["# The hand-off for step 8c: the changed games of rules switch 2 (steps 7c, 8b, 8 and 9's named rows)",
          "",
          "Rebuilt by sitting2.sh (`sitting2_check.py handoff`) at every checkpoint from the per-scan-set rows "
          "(`handoff_<set>_<bot>.tsv`); every changed game is a row of `handoff_8c.tsv`. Nothing here is a verdict: 8c "
          "decides each row by the rule below (PLAN.md step 8c: (a) coin_probe v2, (b) the classifier, (e) the revert "
          "check, then hand traces for whatever the rule can't settle).",
          "",
          f"**{cond3_line(c3)}.**" if c3 else f"{cond3_line(0)}.",
          "",
          "## Totals",
          "",
          "Every changed game needs its first difference placed (tick k, its turn, the cause tick), not only the rows with "
          "no reach2 counter.",
          "",
          "| step | bot | changed games | with different moves | reach | offgate_only (CONDITION 3) | other_only | none |",
          "|---|---|---:|---:|---:|---:|---:|---:|"]
    for sb in srt:
        t = tot[sb]
        md.append(f"| {sb[0]} | {sb[1]} | {t['changed']} | {t['moves']} | " + " | ".join(str(t[c]) for c in CATEGORIES)
                  + " |")
    if not tot:
        md.append("| - | - | 0 | 0 | 0 | 0 | 0 | 0 |")
    r2 = list(m.roles["reach2"])
    md += ["", "Changed games in which each reach2 counter fired (anywhere in the game; 8c places it against the first "
           "difference):", "", "| step | bot | " + " | ".join(r2) + " |", "|---|---|" + "---:|" * len(r2)]
    for sb in srt:
        md.append(f"| {sb[0]} | {sb[1]} | " + " | ".join(str(mech.get(sb, {}).get(c, 0)) for c in r2) + " |")
    md += ["", "## The engines", "",
           ENGINES.format(old_name=env.get("OLD_RELEASE_NAME", "?"), official7=env.get("OFFICIAL", "?")[:7],
                          official_tree7=env.get("OFFICIAL_TREE", "?")[:7], old_dir=env.get("OLD_DIR", "?"),
                          old_scan=env.get("OLD_LEGALITY_SCAN_SHA256", "?"), oldrel=OLDREL, c=a.candidate,
                          main7=(a.main or "?")[:7], p7=env.get("P", "?")[:7], ptree7=env.get("P_TREE", "?")[:7]),
           "", "## The tools (`tools_8c.tsv`, each at its own commit, blob-checked by sitting2.sh at its start)", ""]
    if a.tools:
        md += ["| role | commit:path | blob |", "|---|---|---|"]
        md += [f"| {r.get('role', '?')} | `{r.get('commit', '?')[:8]}:{r.get('path', '?')}` | `{r.get('blob', '?')}` |"
               for r in data_rows(a.tools)]
    else:
        md.append("(no tools file given)")
    md += ["", TOOLS_TEXT, "", "## The pairs files and seed blocks", "", "| step | pairings | pairs file | seed block |",
           "|---|---|---|---:|"]
    md += [f"| {st} | {pl} | `{pf}` | {base:,} |" for st, pl, pf, base in PAIRS_BY_STEP]
    md += ["", "## The revert switches (counters.tsv; P's `engine/src/actions/apply_action_helpers.rs`)", "",
           "Each gate is on by default (the new rule); its environment variable (`=1` or `true`) turns it off for the whole "
           "process, and off is the official engine at that gate. A switch set joined by \"+\" is set together: the seven "
           "sites' old damage needs G1 (`DECKGYM_NO_PLAIN_HIT_COIN`) off too (the G2 comment). `DECKGYM_ROUND2_OFF` turns "
           "every gate off together. Never set one in a recorded run: sitting2.sh refuses to start while any `DECKGYM_*` "
           "variable is set.", "",
           "| mechanic | reach2 counters | switch |", "|---|---|---|"]
    by_mech = {}
    for n in r2:
        by_mech.setdefault((m.c[n]["mechanic"], m.c[n]["revert_switch"]), []).append(n)
    md += [f"| {mm} | {', '.join(ns)} | `{sw}` |" for (mm, sw), ns in by_mech.items()]
    md += ["", "## The files", "",
           "The rows: `handoff_8c.tsv` (columns: " + ", ".join(HEADER) + "). reach2_counters, offgate2_counters, "
           "round1_counters and superset_counters are compact JSON with every firing tick of each counter that fired "
           f"(keyed counters as {{key: [ticks]}}; `{QUEUED_R1}` holds the first round's sites); revert_switches names the "
           "switches of the fired reach2 counters' gates. The games and references (sha256):", ""]
    for p in a.files or []:
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        n = sum(1 for ln in open(p, encoding="utf-8") if ln.strip())
        md.append(f"- `{short(p)}`: {n} games, sha256 {h}")
    md += ["", "## The rule", "",
           RULE.format(n_reach=len(r2), rq=", ".join(sorted(m.rq)), cond3=COND3), ""]
    with open(a.md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))
    print(f"handoff: {len(rows)} changed games from {len(a.rows or [])} row files; "
          + "; ".join(f"{st} {bot}: {t['changed']} changed, {t['changed'] - t['reach']} with no reach2 counter"
                      for (st, bot), t in ((sb, tot[sb]) for sb in srt)) + f"; {cond3_line(c3)}")
    return 0


def trace_gate(a):
    marks = []   # the marked lines the shell reads: "LOAD <n>" and "COMMIT <id>", each once, after the reading

    def wait(why):
        print("\n".join([f"trace load: step 8 waits: {why}"] + marks))
        return 3
    if not os.path.isfile(a.file):
        return wait(f"{os.path.basename(a.file)} is not here")
    try:
        with open(a.file, encoding="utf-8-sig") as f:
            lines = [ln.rstrip("\r\n") for ln in f]
    except (OSError, UnicodeDecodeError) as e:
        return wait(f"{os.path.basename(a.file)} cannot be read ({e!r})")
    tl = [ln for ln in lines if ln.startswith("TRACE LOAD")]
    if len(tl) != 1:
        return wait(f"{len(tl)} lines start with 'TRACE LOAD', not 1")
    m = re.fullmatch(r"TRACE LOAD (\d+) (.*\S.*)", tl[0])
    if not m:
        return wait(f"the line {tl[0]!r} is not 'TRACE LOAD <n> <free text naming the cloud commit>'")
    n, text = int(m.group(1)), m.group(2).strip()
    marks.append(f"LOAD {n}")
    cm = re.search(r"(?<![0-9a-fA-F])([0-9a-f]{7,40})(?![0-9a-fA-F])", text)
    if not cm:
        return wait(f"its free text names no commit (7-40 hex characters): {text!r}")
    marks.append(f"COMMIT {cm.group(1)}")
    # The laptop's own changed games the cloud's load does not cover (its 8b rows 40-46): those with no reach2 counter
    # are counted as hand traces still owed (the safety of "TRACE LOAD n <= ~50" rests on every 8b row being covered)
    # (a line "COVERS 32-37,40-46" says the cloud's n already covers the laptop's rows 40-46 too: then nothing is added)
    covers = any(ln.strip() == "COVERS 32-37,40-46" for ln in lines)
    try:
        extra = 0 if covers else sum(1 for r in read_rows(a.extra_rows) if r["category"] != "reach")
    except (OSError, ValueError, Malformed) as e:
        return wait(f"the laptop's own 8b hand-off rows cannot be read ({e!r})")
    load = n + extra
    xt = ("; it covers the laptop's own 8b rows 40-46 too (COVERS line)" if covers and a.extra_rows else
          f" + {extra} of the laptop's own 8b rows 40-46 with no reach2 counter (not in the cloud's load) = {load}"
          if a.extra_rows else "")
    dustin = [ln for ln in lines if ln.startswith("DUSTIN ") and ln[7:].strip()]
    if load > 50 and not dustin:
        return wait(f"the trace load is {n}{xt} (more than about 50 hand traces), and no DUSTIN line gives his word")
    print("\n".join([f"trace load: {n} ({text}){xt}" + (f"; Dustin: {dustin[0][7:].strip()}" if dustin else "")
                     + "; step 8 may run"] + marks))
    return 0


def cloud8b(a):
    """The cloud's 8b rows v this run's rows for one bot. Exit 0 equal; 1 a matched deal differs (a halt); 3 not compared
    (owed), with the reason."""
    def owed(why):
        print(f"{a.label}: not compared (owed): {why}")
        return 3
    pl = parse_pairings(a.pairings)
    new, ndup, nn = read_set(a.new, pl)
    if ndup or nn != a.expect or len(new) != a.expect:
        return owed(f"this run's file holds {nn} games of pairings {a.pairings} ({len(new)} deals, {len(ndup)} twice), "
                    f"not {a.expect}")
    want = set(new)
    cloud, other = {}, 0
    try:
        with open(a.cloud, encoding="utf-8-sig") as f:
            for ln in f:
                if not ln.strip():
                    continue
                g = json.loads(ln)
                if not isinstance(g, dict) or "pairing" not in g or "i" not in g:
                    return owed("a row with no pairing or i")
                if g.get("bot_a") != a.bot or g["pairing"] not in pl or not (0 <= g["i"] < DEALS["8b"][a.bot]):
                    other += 1
                    continue
                k = (g["pairing"], g["i"])
                if k in cloud:
                    return owed(f"the cloud's rows hold deal {k} twice for {a.bot}")
                cloud[k] = g
    except (OSError, ValueError, TypeError) as e:
        return owed(f"the cloud's file cannot be read ({e!r})")
    if set(cloud) != want:
        return owed(f"after the filter (bot_a {a.bot}, pairings {a.pairings}, i < 40) the cloud's rows hold {len(cloud)} "
                    f"deals, {len(want - set(cloud))} of this run's missing and {len(set(cloud) - want)} others "
                    f"({other} rows of other bots or deals left out)")
    nf = set().union(*(g.keys() for g in new.values()))
    cf = set().union(*(g.keys() for g in cloud.values()))
    fields = sorted((nf & cf) - PATH_FIELDS)
    lacking = sorted(nf - cf - PATH_FIELDS)
    if not set(CLOUD_CORE) <= set(fields):
        return owed(f"the cloud's rows lack {', '.join(sorted(set(CLOUD_CORE) - set(fields)))}")
    bad = [(k, [f for f in fields if new[k].get(f, MISSING) != cloud[k].get(f, MISSING)]) for k in sorted(want)]
    bad = [(k, d) for k, d in bad if d]
    head = (f"{a.label}: {len(want) - len(bad)} of {len(want)} deals equal on the {len(fields)} fields both record "
            f"({', '.join(fields)}; a_file and b_file left out"
            + (f"; the cloud's rows lack {', '.join(lacking)}" if lacking else "")
            + (f"; {len(cf - nf)} fields only the cloud records, left out" if cf - nf else "")
            + f"; {other} cloud rows of other bots or deals left out)")
    if bad:
        print(head + f"; DIFFERS: {len(bad)} deals, first {bad[0][0]} on {', '.join(bad[0][1])}")
        return 1
    print(head)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs"); p.add_argument("--set", choices=tuple(SETS), required=True)
    p.add_argument("--repo", required=True); p.add_argument("--out", required=True); p.add_argument("--seeds-out")
    p.add_argument("--seed-base", type=int, default=BASE_NEW)
    r = sub.add_parser("seedrec"); r.add_argument("--repo", required=True); r.add_argument("--out", required=True)
    r.add_argument("--rows", nargs="+", required=True); r.add_argument("--reuse")
    mo = sub.add_parser("model"); mo.add_argument("--counters", default=default_counters()); mo.add_argument("--tightened")
    t = sub.add_parser("touched")
    t.add_argument("--old", nargs="+", required=True)
    for x in ("--new", "--watch", "--label", "--bot", "--repo", "--out-handoff"):
        t.add_argument(x, required=True)
    t.add_argument("--expect", type=int, required=True); t.add_argument("--step", choices=("7c", "8b", "8", "9"), required=True)
    t.add_argument("--counters", default=default_counters()); t.add_argument("--pairings")
    h = sub.add_parser("handoff"); h.add_argument("--tsv", required=True); h.add_argument("--md", required=True)
    h.add_argument("--candidate", required=True); h.add_argument("--env", required=True); h.add_argument("--main")
    h.add_argument("--tools"); h.add_argument("--counters", default=default_counters())
    h.add_argument("--rows", nargs="*"); h.add_argument("--files", nargs="*")
    g = sub.add_parser("trace-gate"); g.add_argument("file"); g.add_argument("--extra-rows", nargs="*", default=[])
    s = sub.add_parser("stepsum"); s.add_argument("--step", choices=("7c", "8b", "8", "9"), required=True)
    s.add_argument("--watch", nargs="+", required=True); s.add_argument("--rows", nargs="+", required=True)
    s.add_argument("--counters", default=default_counters()); s.add_argument("--pairings")
    c = sub.add_parser("cloud8b")
    for x in ("--new", "--cloud", "--label"):
        c.add_argument(x, required=True)
    c.add_argument("--bot", choices=("km3", "k3"), required=True); c.add_argument("--expect", type=int, default=240)
    c.add_argument("--pairings", default=PAIRINGS_8B_CLOUD)
    a = ap.parse_args()
    fn = {"pairs": pairs, "seedrec": seedrec, "model": model_cmd, "touched": touched, "handoff": handoff,
          "trace-gate": trace_gate, "stepsum": stepsum, "cloud8b": cloud8b}[a.cmd]
    try:
        rc = fn(a)
    except (OSError, ValueError, KeyError, TypeError, Malformed) as e:
        print(f"{a.cmd}: malformed or missing input: {e!r}")
        sys.exit(3 if a.cmd in ("trace-gate", "cloud8b") else 2)
    sys.exit(rc)


if __name__ == "__main__":
    main()
