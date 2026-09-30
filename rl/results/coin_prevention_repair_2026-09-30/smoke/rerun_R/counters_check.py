"""F5's check of the coin repair's exact counters against the coin smoke (Oct 1, rules switch): the 40 scratch games
(kog3 both sides, fire_heatmor v meowth_carefree, seeds 20,950,000,000 + i) on the engine without the repairs (main's, 4690810)
and on R, with both instrument_scan.py scripts applied on R. The cloud's counters could not tell changed games from unchanged
ones ("coin_defender_attack fired in all 40") and read 0 in four changed games (16, 23, 29, 32) where the repair changed the
OFFERED choice and the bot picked another (Sonnet's S3 traced them to ticks 88, 27, 14 and 17). The new counters must
reproduce those ticks, and every changed game must have a changed-mechanic exact counter at or before its first difference.

Inputs, all in this folder: trace_old_4690810.jsonl.gz and trace_R.jsonl.gz (vs_trace.rs, in ../../../victory_star_repair_2026-09-30/smoke/rerun_R/),
watch_R.jsonl (legality_scan on R with the instrumented counters). ../games_legacy_instr.jsonl is the cloud's scan of the old engine.
"Changed-mechanic" exact counters: coin_cut_recorded (B a) and coin_queued_offered (B b and Chase Order). coin_full_prevention and
the off-gate counters are reported alongside: they say what the table runs, not that a game changed.
Usage: python3 counters_check.py"""
import gzip, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent
CHANGED_MECHANIC = ("coin_cut_recorded", "coin_queued_offered")
OTHER = ("coin_full_prevention", "offgate_helper_choice", "offgate_discard_then_damage")
S3_TICKS = {16: 88, 23: 27, 29: 14, 32: 17}          # first_diff_output.txt of the S3 rerun (Sonnet, Sept 30)


def load_trace(name):
    games, done = {}, {}
    for r in map(json.loads, gzip.open(HERE / name, "rt")):
        if r.get("done"):
            done[r["i"]] = r
        else:
            games.setdefault(r["i"], []).append(r)
    return games, done


old, old_done = load_trace("trace_old_4690810.jsonl.gz")
new, new_done = load_trace("trace_R.jsonl.gz")
watch = {r["i"]: r for r in map(json.loads, open(HERE / "watch_R.jsonl"))}
cloud_old = {r["i"]: r for r in map(json.loads, open(SMOKE / "games_legacy_instr.jsonl"))}
deals = sorted(old_done)

print("checks on the tools:")
print(f"  old engine replays the cloud's d21511a scan (same move fingerprint): "
      f"{sum(old_done[i]['moves'] == cloud_old[i]['moves'] for i in deals)} of {len(deals)}")
print(f"  R's trace equals R's watch scan (the counters change no play): "
      f"{sum(new_done[i]['moves'] == watch[i]['moves'] for i in deals)} of {len(deals)}")
changed = [i for i in deals if old_done[i]["moves"] != new_done[i]["moves"]]
print(f"\ngames the repairs change (old engine v R): {len(changed)} of {len(deals)}: {changed}")
print("  the cloud's 12 (old v its repaired engine): [2, 9, 12, 16, 19, 23, 28, 29, 30, 32, 33, 35]; same set: "
      f"{changed == [2, 9, 12, 16, 19, 23, 28, 29, 30, 32, 33, 35]}")

first_tick = lambda c: c["first"]
explained, open_games, first_diffs = [], [], {}
for i in changed:
    a, b = old[i], new[i]
    k = next((t for t in range(min(len(a), len(b)))
              if (a[t]["chosen"], a[t]["offered"], a[t]["board"]) != (b[t]["chosen"], b[t]["offered"], b[t]["board"])),
             min(len(a), len(b)))
    first_diffs[i] = k
    w = watch[i]
    fired = {n: first_tick(w[n]) for n in CHANGED_MECHANIC if w[n]["n"]}
    earliest = min(fired.values()) if fired else None
    ok = earliest is not None and earliest <= k
    (explained if ok else open_games).append(i)
    other = {n: (w[n]["n"], first_tick(w[n])) for n in OTHER if w[n]["n"]}
    x, y = a[k], b[k]
    # At the first difference: the same board and the same offered moves with a different choice means the engines differ only
    # in what the bot's lookahead saw; a different board or different offered moves would be a difference on the board.
    kind = ("same board, same offered moves, different choice (lookahead)" if (x["board"], x["offered"]) == (y["board"], y["offered"])
            else "the board or the offered moves differ")
    print(f"i = {i:2d}: first difference at tick {k:3d} ({kind}); changed-mechanic counters {fired or 'none'}; other exact {other or 'none'}; "
          f"superset coin_defender_attack {w['coin_defender_attack']}, coin_queued_attack_damage (chosen) {w['coin_queued_attack_damage']}  "
          f"=> {'explained on the board' if ok else 'NOT explained on the board'}")

print(f"\nexplained on the board: {len(explained)} {explained}")
print(f"not explained on the board: {len(open_games)} {open_games}")
print("S3's four games, first differing tick v coin_queued_offered first tick:")
for i, tick in S3_TICKS.items():
    print(f"  i = {i}: S3 traced the first difference to tick {tick}; here {first_diffs.get(i)}; coin_queued_offered first = "
          f"{watch[i]['coin_queued_offered']['first']}  ({'match' if watch[i]['coin_queued_offered']['first'] == tick == first_diffs.get(i) else 'DIFFERENT'})")
unchanged = [i for i in deals if i not in changed]
print("\nunchanged games (the counters are reach, not change):")
for n in CHANGED_MECHANIC + OTHER:
    games = [i for i in unchanged if watch[i][n]["n"]]
    print(f"  {n}: fired in {len(games)} unchanged games {games}; in {sum(1 for i in changed if watch[i][n]['n'])} of the {len(changed)} changed")
print("totals over the 40 games: " + ", ".join(f"{n} {sum(watch[i][n]['n'] for i in deals)}" for n in CHANGED_MECHANIC + OTHER)
      + f"; superset coin_defender_attack {sum(watch[i]['coin_defender_attack'] for i in deals)}, "
        f"coin_queued_attack_damage {sum(watch[i]['coin_queued_attack_damage'] for i in deals)}")
