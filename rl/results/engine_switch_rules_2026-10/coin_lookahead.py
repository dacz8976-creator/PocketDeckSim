"""Step 8c of the rules switch, repair B's half, automated and tightened by the laptop Opus's second read (Oct 1): for each game a
repair changes, is the change explained?

For every changed game (two engines' per-tick traces, vs_trace.rs, with a state hash per tick, and F5's watch scan on R, with every
tick of every exact counter) it finds the first differing tick and its cause (`tightened_rule.py`, this folder: read its docstring),
then
- ON THE BOARD: an exact counter of repair B (coin_cut_recorded, coin_queued_offered[_any]) fired in R's watch scan at a tick at or
  before the first differing tick and in the same turn as it (or at the cause tick, the move before it); or
- LOOKAHEAD ONLY, both halves: the first difference is the same state, the same offered moves (two or more), a different choice, no
  counter fired in that turn up to it, and coin_probe.rs, run on R at that tick, finds repair B's condition inside the bot's search
  depth (a queued coin-path choice offered, or a finite heads cut recorded, within kog3's 3 plies); the other half is the code gate,
  read in the code (apply_attack_action.rs: coin_damage_prevention 264, queued_attack_damage_choice 281, discard_then_damage_choice
  311, apply_defender_damage_prevention_if_needed 229, attack_outcome.rs: split_with_damage_prevention 621); or
- NEEDS A JUDGMENT: the condition is found only at the leaf of the search (offered at ply 3 in a mixed frame, never applied); or
- UNEXPLAINED: anything else (a board, offered-move or forced-move difference with no counter in that turn, or no condition in the
  search). That stops the switch.
The probe also runs on the games explained on the board, at the tick of the last counter that explains them: there the condition must
be on the table (a queued choice offered after 0 moves, or the cut recorded by the move chosen at ply 1), the golden check against
Sonnet's S3 (games 16, 23, 29, 32 at ticks 88, 27, 14, 17, traced by hand on Sept 30).

  python3 coin_lookahead.py --dir SMOKE_RERUN_DIR --a A.txt --b B.txt --seed-base N --probe PATH/coin_probe [--bot kog3] [--pairing 0]
SMOKE_RERUN_DIR holds trace_old_*.jsonl.gz, trace_R.jsonl.gz and watch_R.jsonl (coin_prevention_repair_2026-09-30/smoke/rerun_R/)."""
import argparse, glob, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tightened_rule import load_trace, first_difference, counter_hits  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--a", required=True)
ap.add_argument("--b", required=True)
ap.add_argument("--seed-base", required=True)
ap.add_argument("--probe", required=True)
ap.add_argument("--bot", default="kog3")
ap.add_argument("--pairing", default="0")
ap.add_argument("--s3", default="16:88,23:27,29:14,32:17", help="golden: deal:first differing tick pairs traced by hand")
a = ap.parse_args()
D = Path(a.dir)
CHANGED_MECHANIC = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
SEARCH_PLIES = 3

old, old_done = load_trace(glob.glob(str(D / "trace_old_*.jsonl.gz"))[0])
new, new_done = load_trace(D / "trace_R.jsonl.gz")
watch = {r["i"]: r for r in map(json.loads, open(D / "watch_R.jsonl"))}
changed = [i for i in sorted(old_done) if old_done[i]["moves"] != new_done[i]["moves"]]
print(f"{len(changed)} changed games of {len(old_done)}: {changed}")


def probe(deal, tick):
    p = subprocess.run([a.probe, "--a", a.a, "--b", a.b, "--seed-base", a.seed_base, "--pairing", a.pairing, "--bot", a.bot,
                        "--deal", str(deal), "--tick", str(tick)], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"coin_probe failed for deal {deal} tick {tick}: {p.stderr[-300:]}")
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", p.stdout, re.M)
    parse = lambda s: None if s == "none" else int(s)
    return parse(m[1]), parse(m[2]), m[3] == "true", p.stdout


verdicts, golden, kinds = {}, {}, {}
bad = 0
for i in changed:
    x, y = old[i], new[i]
    d = first_difference(x, y)
    kinds[i] = d["kind"]
    if d["kind"] == "length":                         # one game is a prefix of the other: no tick to probe
        verdicts[i] = "UNEXPLAINED"
        print(f"i = {i:2d}: {d['detail']} => UNEXPLAINED")
        golden[i] = (d["k"], None, None)
        continue
    k, cause = d["k"], d["cause"]
    strict = counter_hits(watch[i], CHANGED_MECHANIC, y, d)
    literal = counter_hits(watch[i], CHANGED_MECHANIC, y, d, literal=True)
    later = counter_hits(watch[i], CHANGED_MECHANIC, y, d, after=True)
    counters = f"counters at or before tick {k} in its turn, or at the cause tick: {strict or 'none'}" \
        + ("" if literal == strict else f" (without the cause-tick clause: {literal or 'none'})") \
        + (f"; same turn after tick {k}: {later}" if later else "")
    head = f"i = {i:2d}: first difference at tick {k:3d} (turn {x[k]['turn']}; {d['kind']}: {d['detail']}; cause tick {cause}); {counters}"
    if strict:
        gate = max(t for ticks in strict.values() for t in ticks)
        queued, cut, free, out = probe(i, gate)
        on_table = queued == 0 or cut == 1
        verdict = "ON THE BOARD"
        print(f"{head}; golden probe at tick {gate}: queued after {queued} move(s), cut at ply {cut} ({'on the table' if on_table else 'NOT ON THE TABLE'}) => {verdict}")
        golden[i] = (k, queued, cut)
        if not on_table:
            bad += 1
    elif d["kind"] == "lookahead":
        queued, cut, free, out = probe(i, k)
        if queued is not None or cut is not None:
            # A queued choice offered at ply 3 is the tree's last node: priced only if its frame is pure (every choice queued), which
            # the bots resolve without spending a ply (expectiminimax_player.rs:659-673); a mixed frame there is never applied.
            leaf_only = queued == SEARCH_PLIES and not free and (cut is None or cut > SEARCH_PLIES)
            verdict = ("NEEDS A JUDGMENT (the choice is offered only at the leaf, ply 3, in a mixed frame)" if leaf_only
                       else "LOOKAHEAD ONLY, both halves hold")
        else:
            verdict = "UNEXPLAINED"
        print(f"{head}; probe at tick {k}: queued choice after {queued} move(s){' (a pure frame, resolved without a ply)' if free else ''}, "
              f"finite cut at ply {cut} => {verdict}")
        golden[i] = (k, queued, cut)
    else:
        verdict = "UNEXPLAINED"
        print(f"{head} => {verdict}")
        golden[i] = (k, None, None)
    verdicts[i] = verdict

print("\nS3's four games (the first difference must be at S3's tick, with the queued coin-path choice on the table there):")
for pair in a.s3.split(","):
    i, tick = map(int, pair.split(":"))
    k, queued, cut = golden[i]
    ok = (k == tick and queued == 0 and verdicts[i] == "ON THE BOARD")
    bad += not ok
    print(f"  i = {i}: S3 traced tick {tick}; first difference here {k} ({kinds[i]}); probe: queued after {queued} move(s); verdict {verdicts[i]}  ({'match' if ok else 'DIFFERENT'})")

print("\nnegative control (unchanged games, a mid-game tick with no Meowth in play on either side: the probe must find nothing):")
controls = []
for i in sorted(set(old) - set(changed)):
    for t, r in enumerate(old[i][:60]):
        if t >= 8 and r["n"] > 1 and "Meowth" not in json.dumps(r["board"]):
            controls.append((i, t))
            break
    if len(controls) == 3:
        break
control_bad = 0
for i, t in controls:
    queued, cut, free, out = probe(i, t)
    ok = queued is None and cut is None
    control_bad += not ok
    print(f"  i = {i}, tick {t}: queued {queued}, cut {cut}  ({'nothing found, as it must be' if ok else 'FOUND SOMETHING'})")
bad += control_bad

tally = {}
for v in verdicts.values():
    tally[v] = tally.get(v, 0) + 1
print(f"\nkinds of first difference: { {k_: [i for i in kinds if kinds[i] == k_] for k_ in sorted(set(kinds.values()))} }")
print("verdicts:", json.dumps(tally))
print("games by verdict:", json.dumps({v: [i for i in verdicts if verdicts[i] == v] for v in tally}))
unexplained = [i for i, v in verdicts.items() if v == "UNEXPLAINED"]
judgment = [i for i, v in verdicts.items() if v.startswith("NEEDS A JUDGMENT")]
print(f"unexplained: {unexplained or 'none'}; needing a judgment: {judgment or 'none'}; golden and control mismatches: {bad}")
sys.exit(1 if unexplained or bad else 0)
