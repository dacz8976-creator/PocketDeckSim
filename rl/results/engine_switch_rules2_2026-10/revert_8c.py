#!/usr/bin/env python3
"""Rules switch 2, step 8c: the revert-check driver (the laptop's spec, Oct 10; PLAN.md section 6, change 3).

A changed game is "in lookahead" only if the code gate holds, v2 finds the condition in the bots' search at the first differing tick,
AND the revert check reproduces the old choice and its scores. This script is that third part. It reads classify_8c.py's
lookahead.tsv (every game whose verdict is "LOOKAHEAD ONLY, both halves hold" or "NEEDS A JUDGMENT") and, per game, asks the pinned
score dump (score_dump_round2.rs, `revert_score_dump` in tools_8c.tsv) for the decision at the first differing tick k:

    official   the official engine's program (rl/engine-2026-10-02), no gate
    p          the candidate P's program, every gate at its default (on): must choose differently, or the difference did not replay
    gate_off   P with the game's own gate(s) off for that one decision (`--revert g1,g2`), the gates picked from the probe's findings
    all_off    P with every round-2 gate off (`--revert all`: the master switch, with_round2(false))

PASS = gate_off chooses the official engine's move AND its candidate list (the scores and the texts, as Oct 1's revert_check.py
compared them) equals the official one's AND all_off reproduces the official move and scores too. Anything else is FAIL, and any FAIL
is a stop that goes to Dustin through the laptop session. The gate comes from counters.tsv's revert_switch column through the
counter names of the probe's finding (queued/cut -> coin_queued_by_attack, a return ply -> attack_return_weakness, trapleaf and each
of round 2's seven kinds -> their counters), never from a hand-written name; a game with several findings gets the union of their
gates (reader one's N5, mixed frames); a finding, counter or switch this script does not know is a refusal, not a guess.

The gates are turned off IN the score dump (`--revert`, one decision, one thread), never through DECKGYM_* in the environment: a
variable would also change every replayed tick before k. No DECKGYM_* variable (or PDL_EQUIV_DEALS, GOLDFISH_TRACE, PG_DUMP) may be
set in the caller's environment; that is a refusal, as the sittings refuse. Nothing is exported; each program gets a copy of the
environment passed as env=.

Usage (all of it required; there are no defaults, so nothing is guessed):
  python3 revert_8c.py --lookahead lookahead.tsv --counters counters.tsv --handoff handoff_8c.tsv --root DIR_WITH_THE_DECKS
      --seed-base 23100000000 [--seed-base ...]
      --p-program PATH --p-cwd DIR --p-sha256 HEX64 --official-program PATH --official-cwd DIR --official-sha256 HEX64
      --out DIR [--jobs N]
Writes OUT/revert_8c.tsv (one row per lookahead game), OUT/revert_8c_summary.txt (the one line `revert R of L reproduced` for
8c_RESULT.txt), OUT/revert_8c.json (inputs and programs, with their sha256) and OUT/raw/ (the raw dump of every failed game).
Exit 0: R == L. Exit 1: a game failed (a stop). Exit 2: a refusal (nothing was run, or no program started)."""
import argparse, collections, concurrent.futures as cf, csv, hashlib, json, os, re, subprocess, sys
from pathlib import Path

# ---- the vocabulary (tightened_rule.py's; test_revert_8c.py compares these copies with that file when it is in this folder) ----
R2_KINDS = ("will", "vs", "trap", "own", "guts", "plain", "perish")
R2_COUNTER_KIND = {"will_confused_attack": "will", "will_block_coin_attack": "will", "vs_block_coin_built": "vs",
                   "vs_block_coin_choice_offered": "vs", "trap_territory_offer_changed": "trap", "trap_territory_outcome_changed": "trap",
                   "coin_own_side_split": "own", "guts_own_side_split": "guts", "coin_plain_damage_chosen": "plain",
                   "coin_plain_damage_by_attack": "plain", "perish_plain_hit_chosen": "perish", "perish_plain_hit_offered": "perish"}
BOTH_HALVES = "LOOKAHEAD ONLY, both halves hold"
JUDGMENT = "NEEDS A JUDGMENT"
PROBE_REQUIRED = ("queued", "cut", "free", "ret", "r2", "trapleaf")
PROBE_EXTRA = ("tick", "queued_attacks", "truncated", "retried")      # what classify_8c.py's lookahead.tsv adds to parse_probe's keys

# The gate each switch's environment variable names, as the score dump's --revert tokens (apply_action_helpers.rs: the round2_switch!
# lines and the P2 comment, read at P = c7a25df4 against score_dump_round2.rs's with_off). DECKGYM_ROUND2_OFF is not a per-counter
# switch: it is the all-off run, token "all".
ENV_TO_TOKEN = {
    "DECKGYM_FLAT_RETURN_DAMAGE": "p2", "DECKGYM_NO_PLAIN_HIT_COIN": "g1", "DECKGYM_PLAIN_QUEUED_SITES": "g2",
    "DECKGYM_NO_OWN_SIDE_COIN": "g3", "DECKGYM_WILL_SKIPS_GATE_COINS": "g4", "DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN": "g5",
    "DECKGYM_TRAP_TERRITORY_ONCE": "g6", "DECKGYM_NO_OWN_SIDE_GUTS": "g7", "DECKGYM_NO_PERISH_ON_QUEUED_HIT": "g8",
    "DECKGYM_LUXURY_COIN_ANY_STADIUM": "g9", "DECKGYM_FOSSIL_UNDER_ITEM_LOCK": "g10", "DECKGYM_FOSSIL_NOT_ITEM": "g11",
}
TOKEN_ORDER = ("p2",) + tuple(f"g{n}" for n in range(1, 12))
ALL_OFF = "all"
UNSET_IN_CALLER = ("PDL_EQUIV_DEALS", "GOLDFISH_TRACE", "PG_DUMP")     # with every DECKGYM_*: sitting2.sh's check, and the dump's own switch
COUNTERS_HEADER = ["name", "script", "shape", "role", "mechanic", "revert_switch"]
LOOKAHEAD_HEADER = ["step", "bot", "pairing", "i", "seed", "k", "turn", "verdict", "strict", "probe"]
TSV_HEADER = ["step", "bot", "pairing", "i", "k", "verdict", "kind", "gates", "tokens", "official_move", "p_move", "gate_off_move",
              "all_off_move", "replay_ok", "move_equal", "scores_equal", "all_off_equal", "process_ok", "result", "reason"]


class Refuse(Exception):
    """A refusal: the input is not what this script reads, or a gate would have to be guessed. Nothing is run."""


# ---- the caller's environment ----
def check_environment(environ):
    bad = sorted(k for k in environ if k.startswith("DECKGYM_") or k in UNSET_IN_CALLER)
    if bad:
        raise Refuse(f"the environment sets {', '.join(bad)}: unset it (the gates are turned off inside the score dump with --revert; "
                     f"a variable left set would change every replayed tick, and the sittings refuse to start with one)")


# ---- the data files ----
def read_tsv(path, header):
    """A tab-separated file as classify_8c.py reads one (csv, tab), comment lines (#) and empty lines skipped; the header is checked
    when one is given and every row must have the header's width."""
    try:
        with open(path, encoding="utf-8", newline="") as f:
            table = list(csv.reader((ln for ln in f if ln.strip() and not ln.startswith("#")), delimiter="\t"))
    except OSError as e:
        raise Refuse(f"{path}: {e}")
    if not table:
        raise Refuse(f"{path}: no header")
    got = table[0]
    if header is not None and got != header:
        raise Refuse(f"{path}: the header is {got}, not {header}")
    for cells in table[1:]:
        if len(cells) != len(got):
            raise Refuse(f"{path}: a row has {len(cells)} cells, the header {len(got)}: {cells[:3]}")
    return [dict(zip(got, cells)) for cells in table[1:]]


def read_counters(path):
    """{counter name: its revert_switch cell} from counters.tsv (comment lines skipped)."""
    out = {}
    for r in read_tsv(path, COUNTERS_HEADER):
        if r["name"] in out:
            raise Refuse(f"{path}: {r['name']} twice")
        out[r["name"]] = r["revert_switch"]
    return out


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blob_id(path):
    """The git blob id of a file (classify_8c.py's check of the hand-off's deck files)."""
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# ---- the probe's findings and their gates ----
def findings(probe):
    """The conditions the probe found, as labels in a fixed order: queued, cut, return, round 2's kinds, trapleaf. The probe's dict is
    read strictly: a missing field, an unknown round-2 kind or an unknown extra field is a refusal. Nothing found is a refusal too (a
    lookahead verdict needs a finding)."""
    if not isinstance(probe, dict):
        raise Refuse(f"the probe cell is not an object: {probe!r}")
    missing = [k for k in PROBE_REQUIRED if k not in probe]
    extra = [k for k in probe if k not in PROBE_REQUIRED + PROBE_EXTRA]
    if missing or extra:
        why = ([f"no {', '.join(missing)}"] if missing else []) + ([f"unknown field {', '.join(map(repr, extra))}"] if extra else [])
        raise Refuse(f"the probe cell has {'; '.join(why)}: {sorted(probe)}")
    r2 = probe["r2"]
    if not isinstance(r2, dict) or set(r2) != set(R2_KINDS):
        raise Refuse(f"the probe's round-2 kinds are {sorted(r2) if isinstance(r2, dict) else r2!r}, not {sorted(R2_KINDS)}")
    for name in ("queued", "cut", "ret", "trapleaf", *R2_KINDS):
        v = probe[name] if name in probe else r2[name]
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
            raise Refuse(f"the probe's {name} is {v!r}, not a ply or none")
    out = []
    if probe["queued"] is not None:
        out.append("queued")
    if probe["cut"] is not None:
        out.append("cut")
    if probe["ret"] is not None:
        out.append("return")
    out += [k for k in R2_KINDS if r2[k] is not None]
    if probe["trapleaf"] is not None:
        out.append("trapleaf")
    if not out:
        raise Refuse("the probe found nothing: a lookahead game has a finding, and no gate is guessed without one")
    return out


def counters_of(label):
    """The exact counters a finding is made of (tightened_rule.py's docstrings): QUEUED and CUT coin_queued_by_attack, RETURN
    attack_return_weakness, trapleaf the Trap Territory kind's counters, each other kind its own."""
    if label in ("queued", "cut"):
        return ["coin_queued_by_attack"]
    if label == "return":
        return ["attack_return_weakness"]
    kind = "trap" if label == "trapleaf" else label
    if kind not in R2_KINDS:
        raise Refuse(f"unknown finding {label!r}")
    return [n for n, k in R2_COUNTER_KIND.items() if k == kind]


def gates_for(labels, counters):
    """(environment variable names, score-dump tokens) of the union of the findings' gates, from counters.tsv's revert_switch column."""
    envs = set()
    for label in labels:
        cells = set()
        for name in counters_of(label):
            if name not in counters:
                raise Refuse(f"counters.tsv has no counter {name} (the finding {label})")
            cells.add(counters[name])
        if len(cells) != 1:
            raise Refuse(f"the finding {label}: its counters name different switches {sorted(cells)}")
        (cell,) = cells
        if cell in ("", "-"):
            raise Refuse(f"the finding {label}: counters.tsv names no revert switch for it")
        for env in cell.split("+"):
            if env not in ENV_TO_TOKEN:
                raise Refuse(f"the finding {label}: {env} is not a per-counter switch this script knows")
            envs.add(env)
    tokens = sorted((ENV_TO_TOKEN[e] for e in envs), key=TOKEN_ORDER.index)
    return sorted(envs, key=lambda e: TOKEN_ORDER.index(ENV_TO_TOKEN[e])), tokens


# ---- the score dump's output ----
def parse_dump(rc, stdout, stderr):
    """(Oct 1's revert_check.py.) The chosen move from the `deal i, tick t: chose X` line; the candidates (score, text) from the
    PGDUMP lines after the last `PGTICK ... asked about` line (PG_DUMP is set only for the decision asked about, so the replayed ticks
    print none). stderr first, then stdout: the candidates are found whichever stream the dump writes them to."""
    lines = (stderr + "\n" + stdout).splitlines()
    chosen = next((ln.split("chose ", 1)[1] for ln in lines if ln.startswith("deal ") and "chose " in ln), None)
    start = max((i for i, ln in enumerate(lines) if ln.startswith("PGTICK") and "asked about" in ln), default=0)
    cands = [(float(m[1]), m[2]) for ln in lines[start:] if (m := re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", ln))]
    return {"rc": rc, "chosen": chosen, "cands": cands, "ok": rc == 0 and chosen is not None and bool(cands), "stdout": stdout, "stderr": stderr}


def same_scores(x, y):
    """Oct 1's rule: the same number of candidates, each score within 1e-9 and each candidate text equal."""
    return len(x) == len(y) and all(abs(p[0] - q[0]) < 1e-9 and p[1] == q[1] for p, q in zip(x, y))


# ---- the programs ----
class Program:
    def __init__(self, label, path, cwd, sha256):
        self.label, self.path, self.cwd, self.sha256 = label, str(path), str(cwd), sha256

    def verify(self):
        if not re.fullmatch(r"[0-9a-f]{64}", self.sha256):
            raise Refuse(f"{self.label}: the sha256 given is not 64 lowercase hex digits")
        if not Path(self.path).is_file():
            raise Refuse(f"{self.label}: no program at {self.path}")
        if not Path(self.cwd).is_dir():
            raise Refuse(f"{self.label}: no working directory {self.cwd}")
        got = sha256_of(self.path)
        if got != self.sha256:
            raise Refuse(f"{self.label}: {self.path} is sha256 {got}, not the {self.sha256} given")


def run_program(program, args, env):
    p = subprocess.run([program.path, *args], cwd=program.cwd, env=env, capture_output=True, text=True, errors="replace")
    return p.returncode, p.stdout, p.stderr


# ---- the plan: every row read and every gate chosen before anything runs ----
def plan_games(lookahead_rows, counters, handoff_rows, root, seed_bases):
    handoff = {}
    for r in handoff_rows:
        handoff[(r["step"], r["bot"], int(r["pairing"]), int(r["i"]))] = r
    games, seen = [], set()
    for r in lookahead_rows:
        key = (r["step"], r["bot"], int(r["pairing"]), int(r["i"]))
        if key in seen:
            raise Refuse(f"{key} is twice in lookahead.tsv")
        seen.add(key)
        if r["verdict"] not in (BOTH_HALVES, JUDGMENT):
            raise Refuse(f"{key}: the verdict is {r['verdict']!r}: lookahead.tsv holds only {BOTH_HALVES!r} and {JUDGMENT!r}")
        h = handoff.get(key)
        if h is None:
            raise Refuse(f"{key} is not in the hand-off")
        if h["seed"] != r["seed"]:
            raise Refuse(f"{key}: seed {r['seed']} in lookahead.tsv, {h['seed']} in the hand-off")
        base = int(r["seed"]) - key[2] * 10_000 - key[3]
        if base not in seed_bases:
            raise Refuse(f"{key}: the seed {r['seed']} is seed base {base} (seed base + pairing * 10000 + i), not one of {sorted(seed_bases)}")
        try:
            probe = json.loads(r["probe"])
        except json.JSONDecodeError as e:
            raise Refuse(f"{key}: the probe cell is not JSON ({e})")
        k = int(r["k"])
        if isinstance(probe, dict) and "tick" in probe and probe["tick"] != k:
            raise Refuse(f"{key}: the probe was run at tick {probe['tick']}, the first differing tick is {k}")
        labels = findings(probe)
        envs, tokens = gates_for(labels, counters)
        paths = {}
        for side in ("held", "panel"):
            path = Path(root) / h[f"{side}_file"]
            if not path.is_file():
                raise Refuse(f"{key}: no deck file {path}")
            if blob_id(path) != h[f"{side}_blob"]:
                raise Refuse(f"{key}: {path} is not the hand-off's blob {h[side + '_blob']}")
            paths[side] = str(path)
        games.append({"key": key, "k": k, "verdict": r["verdict"], "labels": labels, "envs": envs, "tokens": tokens,
                      "seed_base": base, "held": paths["held"], "panel": paths["panel"]})
    games.sort(key=lambda g: (g["key"][1], g["key"][2], g["key"][3], g["key"][0]))
    return games


def dump_args(g):
    step, bot, pairing, i = g["key"]
    return ["--a", g["held"], "--b", g["panel"], "--seed-base", str(g["seed_base"]), "--pairing", str(pairing), "--bot", bot,
            "--deal", str(i), "--tick", str(g["k"])]


def check_game(g, programs, runner, env):
    """The four dumps of one game and the verdict."""
    args = dump_args(g)
    calls = {"official": (programs["official"], args), "p": (programs["p"], args),
             "gate_off": (programs["p"], args + ["--revert", ",".join(g["tokens"])]),
             "all_off": (programs["p"], args + ["--revert", ALL_OFF])}
    d = {name: parse_dump(*runner(prog, a, dict(env))) for name, (prog, a) in calls.items()}
    off = d["official"]
    t = {"process_ok": all(x["ok"] for x in d.values())}
    t["replay_ok"] = d["p"]["chosen"] != off["chosen"]
    t["move_equal"] = d["gate_off"]["chosen"] == off["chosen"]
    t["scores_equal"] = same_scores(off["cands"], d["gate_off"]["cands"])
    t["all_off_equal"] = d["all_off"]["chosen"] == off["chosen"] and same_scores(off["cands"], d["all_off"]["cands"])
    failed = [n for n, flag in (("process", t["process_ok"]), ("replay", t["replay_ok"]), ("move", t["move_equal"]),
                                ("scores", t["scores_equal"]), ("all_off", t["all_off_equal"])) if not flag]
    return {"game": g, "dumps": d, "tests": t, "result": "PASS" if not failed else "FAIL", "reason": ",".join(failed)}


# ---- outputs ----
def cell(x):
    return "" if x is None else str(x).replace("\t", " ").replace("\n", " ")


def yes(flag):
    return "yes" if flag else "NO"


def write_outputs(out, results, inputs, programs, argv):
    out = Path(out)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    with open(out / "revert_8c.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(TSV_HEADER) + "\n")
        for r in results:
            g, d, t = r["game"], r["dumps"], r["tests"]
            step, bot, pairing, i = g["key"]
            f.write("\t".join(cell(x) for x in [
                step, bot, pairing, i, g["k"], g["verdict"], "+".join(g["labels"]), ",".join(g["envs"]), ",".join(g["tokens"]),
                d["official"]["chosen"], d["p"]["chosen"], d["gate_off"]["chosen"], d["all_off"]["chosen"], yes(t["replay_ok"]),
                yes(t["move_equal"]), yes(t["scores_equal"]), yes(t["all_off_equal"]), yes(t["process_ok"]), r["result"], r["reason"]]) + "\n")
    for r in results:
        if r["result"] == "FAIL":
            step, bot, pairing, i = r["game"]["key"]
            with open(out / "raw" / f"{step}_{bot}_{pairing}_{i}.txt", "w", encoding="utf-8", newline="\n") as f:
                for name, x in r["dumps"].items():
                    f.write(f"##### {name}: rc {x['rc']}, chose {x['chosen']!r}, {len(x['cands'])} candidates\n##### stdout\n{x['stdout']}\n"
                            f"##### stderr\n{x['stderr']}\n")
    passed = sum(r["result"] == "PASS" for r in results)
    line = f"revert {passed} of {len(results)} reproduced"
    (out / "revert_8c_summary.txt").write_text(line + "\n", encoding="utf-8", newline="\n")
    info = {"summary": line, "games": len(results), "passed": passed,
            "failed": [list(r["game"]["key"]) + [r["reason"]] for r in results if r["result"] == "FAIL"],
            "by_kind": dict(collections.Counter("+".join(r["game"]["labels"]) for r in results)),
            "inputs": inputs, "programs": {p.label: {"path": p.path, "cwd": p.cwd, "sha256": p.sha256} for p in programs.values()},
            "driver_sha256": sha256_of(__file__), "argv": argv}
    (out / "revert_8c.json").write_text(json.dumps(info, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return line, passed


def run(argv, environ=None, runner=run_program, log=print):
    """The whole check; returns the exit code (0 all reproduced, 1 a game failed, 2 a refusal). `environ` is the caller's environment
    (os.environ), `runner(program, args, env)` returns (returncode, stdout, stderr)."""
    environ = os.environ if environ is None else environ
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for name in ("lookahead", "counters", "handoff", "root", "p-program", "p-cwd", "p-sha256", "official-program", "official-cwd",
                 "official-sha256", "out"):
        ap.add_argument("--" + name, required=True)
    ap.add_argument("--seed-base", required=True, action="append", type=int)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    try:
        check_environment(environ)
        programs = {"p": Program("p", a.p_program, a.p_cwd, a.p_sha256),
                    "official": Program("official", a.official_program, a.official_cwd, a.official_sha256)}
        for p in programs.values():
            p.verify()
        counters = read_counters(a.counters)
        lookahead = read_tsv(a.lookahead, LOOKAHEAD_HEADER)
        handoff = read_tsv(a.handoff, None)
        for need in ("step", "bot", "pairing", "i", "seed", "held_file", "panel_file", "held_blob", "panel_blob"):
            if handoff and need not in handoff[0]:
                raise Refuse(f"{a.handoff}: no {need} column")
        games = plan_games(lookahead, counters, handoff, a.root, set(a.seed_base))
    except Refuse as e:
        log(f"REFUSED: {e}", file=sys.stderr)
        return 2
    env = dict(environ)
    log(f"{len(games)} lookahead games; {', '.join(f'{k} {v}' for k, v in sorted(collections.Counter('+'.join(g['labels']) for g in games).items()))}")
    with cf.ThreadPoolExecutor(max(1, a.jobs)) as ex:
        results = list(ex.map(lambda g: check_game(g, programs, runner, env), games))
    inputs = {n: {"path": str(Path(getattr(a, n)).resolve()), "sha256": sha256_of(getattr(a, n))} for n in ("lookahead", "counters", "handoff")}
    inputs["root"] = str(Path(a.root).resolve())
    inputs["seed_bases"] = sorted(set(a.seed_base))
    line, passed = write_outputs(a.out, results, inputs, programs, argv)
    log(line)
    bad = [r for r in results if r["result"] == "FAIL"]
    for r in bad:
        log(f"  FAIL {r['game']['key']} ({'+'.join(r['game']['labels'])}; gates {','.join(r['game']['tokens'])}): {r['reason']}")
    if bad:
        log(f"STOP: {len(bad)} game(s) failed the revert check; this goes to Dustin through the laptop session (raw dumps in {a.out}/raw)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
