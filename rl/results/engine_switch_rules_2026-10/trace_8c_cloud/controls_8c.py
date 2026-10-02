"""Step 8c (the cloud): negative controls for the two probes, as R's coin_lookahead.py and first_diff.py make them, at
step 8's own carriers. In UNCHANGED deals (not in handoff_8c.tsv) the probe runs at the first tick from 8 on with two or
more offered moves where its repair's gate is absent from the board, and must find nothing:
  coin_probe: no coin-flip damage Ability Pokemon (Meowth, Togekiss, Bastiodon, Hisuian Goodra) in play on either side;
  vs_probe:   the houndoom_victini carrier's pairings (24-31), no Confused Pokemon in play (the trace's facts).
Two deals per carrier and bot for the coin probe (the first three carriers hold the coin Abilities), two per bot for
vs_probe. Usage: python3 controls_8c.py <work dir>  (build_8c.sh's; writes controls.txt here)"""
import gzip, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path(sys.argv[1])
SEED_BASE = "23100000000"
COIN_NAMES = ("Meowth", "Togekiss", "Bastiodon", "Hisuian Goodra")
lines = open(W / "handoff_8c.tsv", encoding="utf-8").read().splitlines()
head = lines[0].split("\t")
changed = {(r["bot"], int(r["pairing"]), int(r["i"])) for r in (dict(zip(head, l.split("\t"))) for l in lines[1:])}
pairs = {}
for l in open(W / "pairs_8.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = l.split("\t")
    pairs[int(c[0])] = (c[3], c[5])


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return p.stdout


def trace_rows(bot, pairing, i):
    held, opp = pairs[pairing]
    out = run([str(W / "bin_old_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base",
               SEED_BASE, "--pairing", str(pairing), "--bot", bot, "--deals", str(i)], W / "old" / "engine")
    return [json.loads(l) for l in out.splitlines() if '"done"' not in l]


def probe(kind, bot, pairing, i, tick):
    held, opp = pairs[pairing]
    exe, cwd = (("bin_new_vs_probe", "new") if kind == "vs" else ("bin_probe_coin_probe", "probe"))
    out = run([str(W / exe), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base", SEED_BASE,
               "--pairing", str(pairing), "--bot", bot, "--deal", str(i), "--tick", str(tick)], W / cwd / "engine")
    return [l for l in out.splitlines() if l.startswith("RESULT")][0]


report, found = [], 0
plan = [("coin", carrier, bot) for carrier in range(3) for bot in ("km3", "k3")] + [("vs", 3, bot) for bot in ("km3", "k3")]
for kind, carrier, bot in plan:
    done = 0
    for pairing in range(carrier * 8, carrier * 8 + 8):
        for i in range(0, 40):
            if done == 2 or (bot, pairing, i) in changed:
                continue
            rows = trace_rows(bot, pairing, i)
            ok = lambda r: (not any(n in json.dumps(r["board"]) for n in COIN_NAMES)) if kind == "coin" \
                else not any(r["facts"]["confused"])
            tick = next((t for t, r in enumerate(rows) if t >= 8 and r["n"] > 1 and ok(r)), None)
            if tick is None:
                continue
            res = probe(kind, bot, pairing, i, tick)
            nothing = res in ("RESULT built=none",) or (kind == "coin" and "queued=none cut=none" in res)
            found += 0 if nothing else 1
            report.append(f"{kind} probe, {bot}, pairing {pairing}, deal {i}, tick {rows[tick]['tick']} (turn {rows[tick]['turn']}), "
                          f"an unchanged deal: {res}  ({'nothing found' if nothing else 'FOUND SOMETHING'})")
            done += 1
            break
        if done == 2:
            break
report.append(f"{len(report)} controls, {found} found something")
(HERE / "controls.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
sys.exit(1 if found else 0)
