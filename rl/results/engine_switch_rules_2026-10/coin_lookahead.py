"""Step 8c of the rules switch, repair B's half, automated: for each game a repair changes, is the change explained?

For every changed game (two engines' per-tick traces, vs_trace.rs, and F5's watch scan on R) it finds the first differing tick, then
- ON THE BOARD: an exact counter of repair B (coin_queued_offered, coin_cut_recorded) first fires at or before that tick; or
- LOOKAHEAD ONLY, both halves: the first difference has the same board and the same offered moves with a different choice, and
  coin_probe.rs, run on R at that tick, finds repair B's condition inside the bot's search depth (a queued coin-path choice
  offered, or a finite heads cut recorded, within kog3's 3 plies); the other half is the code gate, read in the code
  (apply_attack_action.rs: coin_damage_prevention 264, queued_attack_damage_choice 281, discard_then_damage_choice 311,
  apply_defender_damage_prevention_if_needed 229, attack_outcome.rs: split_with_damage_prevention 621); or
- NEEDS A JUDGMENT: the condition is found only at the leaf of the search (offered at ply 3, never applied); or
- UNEXPLAINED: anything else (a board or offered-move difference with no counter, or no condition in the search). That stops the switch.
The probe also runs on the games explained on the board: there the condition must be on the table at the tick (0 moves), which is
the golden check against Sonnet's S3 (games 16, 23, 29, 32 at ticks 88, 27, 14, 17, traced by hand on Sept 30).

  python3 coin_lookahead.py --dir SMOKE_RERUN_DIR --a A.txt --b B.txt --seed-base N --probe PATH/coin_probe [--bot kog3] [--pairing 0]
SMOKE_RERUN_DIR holds trace_old_*.jsonl.gz, trace_R.jsonl.gz and watch_R.jsonl (coin_prevention_repair_2026-09-30/smoke/rerun_R/)."""
import argparse, glob, gzip, json, re, subprocess, sys
from pathlib import Path

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
CHANGED_MECHANIC = ("coin_cut_recorded", "coin_queued_offered")
SEARCH_PLIES = 3


def load_trace(path):
    games, done = {}, {}
    for r in map(json.loads, gzip.open(path, "rt")):
        if r.get("done"):
            done[r["i"]] = r
        else:
            games.setdefault(r["i"], []).append(r)
    return games, done


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


verdicts, golden = {}, {}
for i in changed:
    x, y = old[i], new[i]
    k = next((t for t in range(min(len(x), len(y)))
              if (x[t]["chosen"], x[t]["offered"], x[t]["board"]) != (y[t]["chosen"], y[t]["offered"], y[t]["board"])), min(len(x), len(y)))
    if k >= min(len(x), len(y)):                      # one game is a prefix of the other: no tick to probe
        verdicts[i] = "UNEXPLAINED"
        print(f"i = {i:2d}: the games agree on every tick of the shorter one ({k}) and differ only in length => UNEXPLAINED")
        golden[i] = (k, None)
        continue
    same_view = (x[k]["board"], x[k]["offered"]) == (y[k]["board"], y[k]["offered"])
    fired = {n: watch[i][n]["first"] for n in CHANGED_MECHANIC if watch[i][n]["n"]}
    earliest = min(fired.values()) if fired else None
    queued, cut, free, out = probe(i, k)
    if earliest is not None and earliest <= k:
        verdict = "ON THE BOARD"
    elif same_view and (queued is not None or cut is not None):
        # A queued choice offered at ply 3 is the tree's last node: priced only if its frame is pure (every choice queued), which
        # the bots resolve without spending a ply (expectiminimax_player.rs:659-673); a mixed frame there is never applied.
        leaf_only = queued == SEARCH_PLIES and not free and (cut is None or cut > SEARCH_PLIES)
        if leaf_only:
            verdict = "NEEDS A JUDGMENT (the choice is offered only at the leaf, ply 3, in a mixed frame)"
        else:
            verdict = "LOOKAHEAD ONLY, both halves hold"
    else:
        verdict = "UNEXPLAINED"
    verdicts[i] = verdict
    print(f"i = {i:2d}: first difference at tick {k:3d} ({'same board and offered moves, different choice' if same_view else 'the board or the offered moves differ'}); "
          f"counters {fired or 'none'}; probe: queued choice after {queued} move(s){' (a pure frame, resolved without a ply)' if free else ''}, "
          f"finite cut at ply {cut} => {verdict}")
    golden[i] = (k, queued)

print("\nS3's four games (the probe must find the queued coin-path choice on the table, after 0 moves, at the first differing tick):")
bad = 0
for pair in a.s3.split(","):
    i, tick = map(int, pair.split(":"))
    k, queued = golden[i]
    ok = (k == tick and queued == 0)
    bad += not ok
    print(f"  i = {i}: S3 traced tick {tick}; first difference here {k}; probe: queued after {queued} move(s)  ({'match' if ok else 'DIFFERENT'})")

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
print("\nverdicts:", json.dumps(tally))
print("games by verdict:", json.dumps({v: [i for i in verdicts if verdicts[i] == v] for v in tally}))
unexplained = [i for i, v in verdicts.items() if v == "UNEXPLAINED"]
judgment = [i for i, v in verdicts.items() if v.startswith("NEEDS A JUDGMENT")]
print(f"unexplained: {unexplained or 'none'}; needing a judgment: {judgment or 'none'}; golden and control mismatches: {bad}")
sys.exit(1 if unexplained or bad else 0)
