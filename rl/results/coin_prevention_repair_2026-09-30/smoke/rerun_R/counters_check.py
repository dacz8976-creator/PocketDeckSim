"""F5's check of the coin repair's exact counters against the coin smoke (Oct 1, rules switch; tightened by the laptop Opus's second
read): the 40 scratch games (kog3 both sides, fire_heatmor v meowth_carefree, seeds 20,950,000,000 + i) on the engine without the
repairs (main's, 4690810) and on R, with both instrument_scan.py scripts applied on R. The cloud's counters could not tell changed
games from unchanged ones ("coin_defender_attack fired in all 40") and read 0 in four changed games (16, 23, 29, 32) where the repair
changed the OFFERED choice and the bot picked another (Sonnet's S3 traced them to ticks 88, 27, 14 and 17). The new counters must
reproduce those ticks, and a changed game is "on the board" by the tightened rule (`engine_switch_rules_2026-10/tightened_rule.py`):
a changed-mechanic exact counter fired at a tick at or before the first differing tick, in the same turn (or at the cause tick, the move
before it). The games that are not are the "lookahead" ones: `engine_switch_rules_2026-10/coin_lookahead.py` runs the probe on them.

Inputs, all in this folder: trace_old_4690810.jsonl.gz and trace_R.jsonl.gz (vs_trace.rs, in ../../../victory_star_repair_2026-09-30/smoke/rerun_R/,
with a state hash per tick), watch_R.jsonl (legality_scan on R with the instrumented counters; every exact counter has every tick).
../games_legacy_instr.jsonl is the cloud's scan of the old engine.
"Changed-mechanic" exact counters: coin_cut_recorded (B a), coin_queued_offered (B b and Chase Order) and its id-free twin
coin_queued_offered_any. coin_full_prevention and the off-gate counters are reported alongside: they say what the table runs, not that
a game changed.
Usage: python3 counters_check.py"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent
sys.path.insert(0, str(HERE.parents[2] / "engine_switch_rules_2026-10"))
from tightened_rule import load_trace, first_difference, counter_hits  # noqa: E402

CHANGED_MECHANIC = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
OTHER = ("coin_full_prevention", "offgate_helper_choice", "offgate_discard_then_damage")
S3_TICKS = {16: 88, 23: 27, 29: 14, 32: 17}          # first_diff_output.txt of the S3 rerun (Sonnet, Sept 30)

old, old_done = load_trace(HERE / "trace_old_4690810.jsonl.gz")
new, new_done = load_trace(HERE / "trace_R.jsonl.gz")
watch = {r["i"]: r for r in map(json.loads, open(HERE / "watch_R.jsonl"))}
cloud_old = {r["i"]: r for r in map(json.loads, open(SMOKE / "games_legacy_instr.jsonl"))}
deals = sorted(old_done)

print("checks on the tools:")
print(f"  old engine replays the cloud's d21511a scan (same move fingerprint): "
      f"{sum(old_done[i]['moves'] == cloud_old[i]['moves'] for i in deals)} of {len(deals)}")
print(f"  R's trace equals R's watch scan (the counters change no play): "
      f"{sum(new_done[i]['moves'] == watch[i]['moves'] for i in deals)} of {len(deals)}")
print(f"  the id-free coin_queued_offered_any equals the id-listed coin_queued_offered in every game (the smoke holds only Meowth): "
      f"{all(watch[i]['coin_queued_offered_any']['ticks'] == watch[i]['coin_queued_offered']['ticks'] for i in deals)}")
changed = [i for i in deals if old_done[i]["moves"] != new_done[i]["moves"]]
print(f"\ngames the repairs change (old engine v R): {len(changed)} of {len(deals)}: {changed}")
print("  the cloud's 12 (old v its repaired engine): [2, 9, 12, 16, 19, 23, 28, 29, 30, 32, 33, 35]; same set: "
      f"{changed == [2, 9, 12, 16, 19, 23, 28, 29, 30, 32, 33, 35]}")

explained, open_games, first_diffs = [], [], {}
for i in changed:
    a, b = old[i], new[i]
    w = watch[i]
    d = first_difference(a, b)
    k = d["k"]
    first_diffs[i] = k
    if d["kind"] == "length":
        open_games.append(i)
        print(f"i = {i:2d}: {d['detail']}  => NOT explained on the board")
        continue
    strict = counter_hits(w, CHANGED_MECHANIC, b, d)
    later = counter_hits(w, CHANGED_MECHANIC, b, d, after=True)
    ok = bool(strict)
    (explained if ok else open_games).append(i)
    other = {n: (w[n]["n"], w[n]["first"]) for n in OTHER if w[n]["n"]}
    print(f"i = {i:2d}: first difference at tick {k:3d}, turn {a[k]['turn']} ({d['kind']}: {d['detail']}); changed-mechanic counters at or before it in its "
          f"turn, or at the cause tick: {strict or 'none'}; same turn after it: {later or 'none'}; every tick of coin_queued_offered "
          f"{w['coin_queued_offered']['ticks']}; other exact {other or 'none'}; superset coin_defender_attack {w['coin_defender_attack']}, "
          f"coin_queued_attack_damage (chosen) {w['coin_queued_attack_damage']}  => "
          f"{'explained on the board' if ok else 'NOT explained on the board (lookahead: see coin_lookahead.py)'}")

print(f"\nexplained on the board: {len(explained)} {explained}")
print(f"not explained on the board: {len(open_games)} {open_games}   (the probe decides them: engine_switch_rules_2026-10/coin_lookahead.py)")
print("S3's four games, first differing tick v coin_queued_offered tick:")
for i, tick in S3_TICKS.items():
    ticks = watch[i]["coin_queued_offered"]["ticks"]
    print(f"  i = {i}: S3 traced the first difference to tick {tick}; here {first_diffs.get(i)}; coin_queued_offered ticks {ticks}  "
          f"({'match' if tick in ticks and tick == first_diffs.get(i) else 'DIFFERENT'})")
unchanged = [i for i in deals if i not in changed]
print("\nunchanged games (the counters are reach, not change):")
for n in CHANGED_MECHANIC + OTHER:
    games = [i for i in unchanged if watch[i][n]["n"]]
    print(f"  {n}: fired in {len(games)} unchanged games {games}; in {sum(1 for i in changed if watch[i][n]['n'])} of the {len(changed)} changed")
print("totals over the 40 games (ticks at which each fired): " + ", ".join(f"{n} {sum(watch[i][n]['n'] for i in deals)}" for n in CHANGED_MECHANIC + OTHER)
      + f"; superset coin_defender_attack {sum(watch[i]['coin_defender_attack'] for i in deals)}, "
        f"coin_queued_attack_damage {sum(watch[i]['coin_queued_attack_damage'] for i in deals)}")
by_mechanic = {}
for i in deals:
    for name, ticks in watch[i]["offgate_helper_by_mechanic"].items():
        by_mechanic[name] = by_mechanic.get(name, 0) + len(ticks)
print(f"offgate_helper_choice by the helper's mechanic (ticks over the 40 games): {by_mechanic}")
