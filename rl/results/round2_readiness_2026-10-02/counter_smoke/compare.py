"""Round-2 readiness, job 2 (Oct 2): the counters' smoke check (run_smoke.sh). games_round2_plain.jsonl and
games_round2_watch.jsonl hold the same games (pairs.tsv, 20 a pairing, km3 on both sides) played by the plain scan and by the
scan with both watch scripts. It prints whether the counters change any move, and, per pairing, where each round-2 counter
fired (games, ticks). The counter names are read from instrument_scan.py.
Usage: python3 compare.py   (writes compare_output.txt here)"""
import ast, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
script = (HERE.parents[1] / "coin_prevention_repair_2026-09-30" / "instrument_scan.py").read_text(encoding="utf-8")
names = lambda var: ast.literal_eval(re.search(rf"^{var} = (\[.*?\])", script, re.S | re.M)[1])
COUNTERS, KEYED = names("R2_COUNTERS"), names("R2_KEYED")
load = lambda v: {(r["pairing"], r["i"]): r for r in map(json.loads, open(HERE / f"games_{v}.jsonl", encoding="utf-8"))}
plain, watch = load("round2_plain"), load("round2_watch")
pairs = {int(l.split("\t")[0]): l.split("\t") for l in (HERE / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:]}

out = []
same = sum(plain[k]["moves"] == watch[k]["moves"] for k in plain)
out.append(f"plain v watch scan (the counters change no play): same moves in {same} of {len(plain)} games"
           + ("" if set(plain) == set(watch) else "; THE GAME SETS DIFFER"))
for p, row in sorted(pairs.items()):
    keys = sorted(k for k in watch if k[0] == p)
    out.append(f"\npairing {p}, {row[1]} v {row[3]} ({len(keys)} games):")
    for c in COUNTERS:
        n = [watch[k][c]["n"] for k in keys]
        if sum(n):
            out.append(f"  {c}: {sum(x > 0 for x in n)} games, {sum(n)} ticks")
    for c in KEYED:
        by = {}
        for k in keys:
            for key, ticks in watch[k][c].items():
                g, t = by.get(key, (0, 0))
                by[key] = (g + 1, t + len(ticks))
        for key, (g, t) in sorted(by.items()):
            out.append(f"  {c}[{key}]: {g} games, {t} ticks")
    silent = [c for c in COUNTERS if not any(watch[k][c]["n"] for k in keys)] + \
             [c for c in KEYED if not any(watch[k][c] for k in keys)]
    out.append(f"  silent: {', '.join(silent)}")
(HERE / "compare_output.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
