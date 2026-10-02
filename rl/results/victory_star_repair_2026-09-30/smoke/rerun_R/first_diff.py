"""F6 of the rules switch (Oct 1), tightened by the laptop Opus's second read: the 40 Victory Star smoke games (kog3 both sides,
fire_victini v psychic_confuse, seeds 20,930,000,000 + i) on the engine without either repair (main's engine, 4690810) and on R
(the rules candidate), with F5's exact counters on R, and, for every game the repairs change, the first differing tick and what
explains it. The rule is in `../../../engine_switch_rules_2026-10/tightened_rule.py` (read its docstring): a game is "on the
board" only if an exact counter fired at or before the first differing tick within that tick's turn, or at the cause tick (the move
before it; the coordinator's ruling of Oct 1 on "in the same turn as the first difference"); a difference that
is only in the bots' choice ("lookahead") needs the probe (`vs_probe.rs`, run on R at that tick) to find the gate inside kog3's
three plies; anything else is UNEXPLAINED, and that stops the switch.

Inputs, all in this folder unless named:
  trace_old_4690810.jsonl.gz   vs_trace.rs on the engine without the repairs (every tick of every game, a state hash per tick)
  trace_R.jsonl.gz             vs_trace.rs on R
  watch_R.jsonl                legality_scan on R with both instrument_scan.py scripts applied (F5's exact counters, every tick)
  ../games_legacy_instr.jsonl, ../games_fixed_plain.jsonl   the cloud's committed scans (265ce95's engine; 6415e39's engine)
  --probe PATH                 the vs_probe binary built on R (scratch copy of R's engine, `cargo build --release --features
                               test-utils --example vs_probe`); without it the lookahead games are left as "NEEDS THE PROBE"
The probe is also run, as a golden check, at the tick of the last vs_confusion_first_built before the cause in every game explained on
the board (the Confusion-first branch must be on the table there: built after 0 moves), and as a negative control at a mid-game tick
of three unchanged games (nothing may be found). Its full output goes to probe_output.txt.
Usage: python3 first_diff.py --probe /path/to/vs_probe"""
import argparse, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent
sys.path.insert(0, str(HERE.parents[2] / "engine_switch_rules_2026-10"))
from tightened_rule import load_trace, first_difference, counter_hits, short  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--probe", default=None, help="the vs_probe binary built on R")
args = ap.parse_args()
DECK_A, DECK_B, SEED_BASE, BOT = SMOKE / "fire_victini.txt", SMOKE / "psychic_confuse.txt", "20930000000", "kog3"
COUNTERS = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")


def load_games(path):
    import json
    return {r["i"]: r for r in map(json.loads, open(path))}


old, old_done = load_trace(HERE / "trace_old_4690810.jsonl.gz")
new, new_done = load_trace(HERE / "trace_R.jsonl.gz")
watch = load_games(HERE / "watch_R.jsonl")
cloud_legacy = load_games(SMOKE / "games_legacy_instr.jsonl")
cloud_fixed = load_games(SMOKE / "games_fixed_plain.jsonl")
deals = sorted(old_done)
probe_log = []


def run_probe(deal, tick):
    """The fewest moves before an attack that builds the Confusion-first branch at `tick` of `deal` (None: not found within 2 moves)."""
    p = subprocess.run([args.probe, "--a", str(DECK_A), "--b", str(DECK_B), "--seed-base", SEED_BASE, "--bot", BOT,
                        "--deal", str(deal), "--tick", str(tick)], capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"vs_probe failed for deal {deal} tick {tick}: {p.stderr[-300:]}")
    m = re.search(r"^RESULT built=(\S+)$", p.stdout, re.M)
    probe_log.append(f"=== deal {deal}, tick {tick}\n{p.stdout}")
    return (None if m[1] == "none" else int(m[1])), p.stdout


print("checks on the tools:")
print(f"  games traced: {len(deals)} on the old engine, {len(new_done)} on R")
print(f"  old engine replays the cloud's 265ce95 scan (same move fingerprint): "
      f"{sum(old_done[i]['moves'] == cloud_legacy[i]['moves'] for i in deals)} of {len(deals)}")
print(f"  R's trace equals R's watch scan (the counters change no play): "
      f"{sum(new_done[i]['moves'] == watch[i]['moves'] for i in deals)} of {len(deals)}")
print(f"  R v the cloud's repaired-engine scan (6415e39's engine, A only): "
      f"{sum(new_done[i]['moves'] == cloud_fixed[i]['moves'] for i in deals)} of {len(deals)} identical")

changed = [i for i in deals if old_done[i]["moves"] != new_done[i]["moves"]]
print(f"\ngames the repairs change (old engine v R): {len(changed)} of {len(deals)}: {changed}")
print(f"  of the cloud's 13 (old v 6415e39): {sum(cloud_legacy[i]['moves'] != cloud_fixed[i]['moves'] for i in deals)} changed")

verdicts, golden_bad, kinds = {}, 0, {}
for i in changed:
    a, b, w = old[i], new[i], watch[i]
    d = first_difference(a, b)
    kinds[i] = d["kind"]
    if d["kind"] == "length":
        verdicts[i] = "UNEXPLAINED"
        print(f"\ni = {i}: {d['detail']} => UNEXPLAINED")
        continue
    k, cause = d["k"], d["cause"]
    x, y = d["x"], d["y"]
    strict = counter_hits(w, COUNTERS, b, d)
    literal = counter_hits(w, COUNTERS, b, d, literal=True)
    later = counter_hits(w, COUNTERS, b, d, after=True)
    print(f"\ni = {i}: first difference at tick {k} (turn {x['turn']}, mover seat {x['actor']}): {d['kind']}, {d['detail']}; "
          f"cause tick {cause} (turn {b[cause]['turn']}); old {len(a)} ticks, R {len(b)} ticks")
    print(f"  exact counters on R at or before tick {k} in its turn, or at the cause tick: {strict or 'none'}"
          f"{'' if literal == strict else '; without the cause-tick clause: ' + str(literal or 'none')}"
          f"; same turn after tick {k} (never an explanation): {later or 'none'}")
    print(f"  all ticks on R: vs_confusion_first_built {w['vs_confusion_first_built']['ticks']}, "
          f"vs_confused_choice_offered {w['vs_confused_choice_offered']['ticks']}, vs_confused_choice_chosen "
          f"{w['vs_confused_choice_chosen']['ticks']}; superset vs_confused_attack n={w['vs_confused_attack']}")
    if strict:
        verdict = "ON THE BOARD"
        built_hits = [t for t in strict.get("vs_confusion_first_built", []) if t <= cause]
        if built_hits and args.probe:
            gate_tick = max(built_hits)
            built, _ = run_probe(i, gate_tick)
            ok = built == 0
            golden_bad += not ok
            print(f"  golden: the probe at tick {gate_tick} (the last built branch up to the cause) finds the branch built after "
                  f"{built} move(s) ({'match' if ok else 'DIFFERENT, it must be 0'})")
    elif d["kind"] == "lookahead":
        if not args.probe:
            verdict = "NEEDS THE PROBE"
        else:
            built, _ = run_probe(i, k)
            if built is not None:
                verdict = "LOOKAHEAD ONLY, both halves hold"
                print(f"  probe at tick {k}: the Confusion-first branch is built by an attack after {built} move(s) of the mover's own, "
                      f"inside kog3's three plies (attack = ply {built + 1})")
            else:
                verdict = "UNEXPLAINED"
                print(f"  probe at tick {k}: no Confusion-first gate state within 2 moves before an attack")
    else:
        verdict = "UNEXPLAINED"
    verdicts[i] = verdict
    print(f"  => {verdict}")
    if x and y:
        print(f"  same state: {x['state'] == y['state']}; same board summary: {x['board'] == y['board']}; same facts: {x['facts'] == y['facts']}; "
              f"same offered: {x['offered'] == y['offered']} (n {x['n']} / {y['n']}); same chosen: {x['chosen'] == y['chosen']}")
        print(f"  facts at the tick (old): {x['facts']}")
        print(f"  board: {x['board']}")
        print(f"  old chose: {short(x['chosen'])}")
        print(f"  R   chose: {short(y['chosen'])}")
        if k > 0:
            print(f"  the tick before it (same on both): {short(a[k - 1]['chosen'])}")

controls = []
for i in sorted(set(old) - set(changed)):
    for t, r in enumerate(old[i][:60]):
        if t >= 8 and r["n"] > 1:
            controls.append((i, t))
            break
    if len(controls) == 3:
        break
control_bad = 0
if args.probe:
    print("\nnegative control (unchanged games, a mid-game tick: the probe must find no gate):")
    for i, t in controls:
        built, _ = run_probe(i, t)
        ok = built is None
        control_bad += not ok
        print(f"  i = {i}, tick {t}: built after {built} move(s) ({'nothing found, as it must be' if ok else 'FOUND SOMETHING'})")
    (HERE / "probe_output.txt").write_text("".join(probe_log), encoding="utf-8")

tally = {}
for v in verdicts.values():
    tally[v] = tally.get(v, 0) + 1
print(f"\nkinds of first difference: { {k_: [i for i in kinds if kinds[i] == k_] for k_ in sorted(set(kinds.values()))} }")
print("verdicts:", tally)
for v in sorted(tally):
    print(f"  {v}: {[i for i in verdicts if verdicts[i] == v]}")
unexplained = [i for i, v in verdicts.items() if v == "UNEXPLAINED"]
print(f"unexplained: {unexplained or 'none'}; golden and control mismatches: {golden_bad + control_bad}")
print("unchanged games with a built branch on R (the branch was built and the game still equals the old engine's): "
      f"{[i for i in deals if i not in changed and watch[i]['vs_confusion_first_built']['n'] > 0]}")
print("fingerprints (old, R):", {i: (old_done[i]["moves"], new_done[i]["moves"]) for i in changed})
sys.exit(1 if unexplained or golden_bad or control_bad else 0)
