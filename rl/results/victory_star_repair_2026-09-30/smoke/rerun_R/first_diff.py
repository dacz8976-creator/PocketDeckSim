"""F6 of the rules switch (Oct 1): the 40 Victory Star smoke games (kog3 both sides, fire_victini v psychic_confuse, seeds
20,930,000,000 + i) on the engine without either repair (main's engine, 4690810) and on R (the rules candidate), with F5's
exact counters on R, and, for every game the repairs change, the first differing tick against "on the board".

Inputs, all in this folder unless named:
  trace_old_4690810.jsonl.gz   vs_trace.rs on the engine without the repairs (every tick of every game)
  trace_R.jsonl.gz             vs_trace.rs on R
  watch_R.jsonl                legality_scan on R with both instrument_scan.py scripts applied (F5's exact counters)
  ../games_legacy_instr.jsonl, ../games_fixed_plain.jsonl   the cloud's committed scans (265ce95's engine; 6415e39's engine)
A game is "explained on the board" when an exact counter first fired at or before its first differing tick: here
vs_confusion_first_built, whose "first" is a tick number in the same numbering as the traces. Anything else is printed in full
for a hand trace: who is Confused and who has a Victini at that tick, what each engine offered and chose.
Usage: python3 first_diff.py"""
import gzip, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SMOKE = HERE.parent


def load_trace(name):
    """Each game's tick rows in order, and its closing row (the move fingerprint)."""
    games, done = {}, {}
    for r in map(json.loads, gzip.open(HERE / name, "rt")):
        if r.get("done"):
            done[r["i"]] = r
        else:
            games.setdefault(r["i"], []).append(r)
    return games, done


def load_games(path):
    return {r["i"]: r for r in map(json.loads, open(path))}


old, old_done = load_trace("trace_old_4690810.jsonl.gz")
new, new_done = load_trace("trace_R.jsonl.gz")
watch = load_games(HERE / "watch_R.jsonl")
cloud_legacy = load_games(SMOKE / "games_legacy_instr.jsonl")
cloud_fixed = load_games(SMOKE / "games_fixed_plain.jsonl")
deals = sorted(old_done)

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

short = lambda s: s if len(s) <= 150 else s[:147] + "..."
explained, open_games = [], []
for i in changed:
    a, b = old[i], new[i]
    k = next((t for t in range(min(len(a), len(b)))
              if (a[t]["chosen"], a[t]["offered"], a[t]["board"]) != (b[t]["chosen"], b[t]["offered"], b[t]["board"])),
             min(len(a), len(b)))
    w = watch[i]
    built, choice = w["vs_confusion_first_built"], w["vs_confused_choice"]
    first_built = built["first"]
    on_board = first_built is not None and first_built <= k
    (explained if on_board else open_games).append(i)
    x, y = (a[k] if k < len(a) else None), (b[k] if k < len(b) else None)
    print(f"\ni = {i}: first difference at tick {k} (turn {x['turn'] if x else '-'}, mover seat {x['actor'] if x else '-'}); "
          f"old {len(a)} ticks, R {len(b)} ticks")
    print(f"  F5 exact, on R: vs_confusion_first_built n={built['n']} first={first_built}; "
          f"vs_confused_choice n={choice} first={w['vs_confused_choice_first']}; "
          f"superset vs_confused_attack n={w['vs_confused_attack']}")
    print(f"  => {'EXPLAINED ON THE BOARD (the Confusion-first branch was built at tick ' + str(first_built) + ', not after tick ' + str(k) + ')' if on_board else 'NOT explained on the board'}")
    if x and y:
        print(f"  same board before it: {x['board'] == y['board']}; same facts: {x['facts'] == y['facts']}; "
              f"same offered: {x['offered'] == y['offered']}; same chosen: {x['chosen'] == y['chosen']}")
        print(f"  facts at the tick (old): {x['facts']}")
        print(f"  board: {x['board']}")
        print(f"  old chose: {short(x['chosen'])}")
        print(f"  R   chose: {short(y['chosen'])}")
        if k > 0:
            print(f"  the tick before it (same on both): {short(a[k - 1]['chosen'])}")

print(f"\nexplained on the board: {len(explained)} {explained}")
print(f"not explained on the board: {len(open_games)} {open_games}")
print("unchanged games with a built branch on R (the branch was built and the game still equals the old engine's): "
      f"{[i for i in deals if i not in changed and watch[i]['vs_confusion_first_built']['n'] > 0]}")
print("fingerprints (old, R):", {i: (old_done[i]["moves"], new_done[i]["moves"]) for i in changed})
