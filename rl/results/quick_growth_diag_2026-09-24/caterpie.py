"""Diagnostic (Claude Code, seeds 20,000,000,000+): does Caterpie get stopped? Not for any ranking."""
import re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
REPO = str(__import__("pathlib").Path(__file__).resolve().parents[3])  # the repo root
ENG = f"{REPO}/engine/target/release/deckgym"
OPPS = ["vespiquen", "blaziken", "suicune", "altaria", "hydreigon", "weezing", "lucario"]
N = int(sys.argv[1]); OPP_BOT = sys.argv[2]
def job(args):
    oi, seat = args
    opp = OPPS[oi]; seed = 20_000_000_000 + oi * 100_000 + seat * 50_000
    decks = [f"{REPO}/decks/research/sceptile.txt", f"{REPO}/decks/research/{opp}.txt"]
    bots = ["k3", OPP_BOT]
    if seat == 1: decks.reverse(); bots.reverse()
    out = subprocess.run([ENG, "simulate", "--num", str(N), "--seed", str(seed), "--seed-stream", "--players", ",".join(bots),
                          *decks, "-vvv"], capture_output=True, text=True)
    t = out.stdout + out.stderr
    wins = int(re.search(rf"Player {seat} won: (\d+)", t)[1])
    draws = int(re.search(r"Draws: (\d+)", t)[1])
    return opp, wins + 0.5 * draws, t.count("chose ResolveEndTurnEvolution"), len(re.findall(r"Pokemon Caterpie\(\d+hp,\d+\) fainted", t))
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(job, [(oi, s) for oi in range(len(OPPS)) for s in (0, 1)]))
print(f"opponent bot {OPP_BOT}, Sceptile k3, {2*N} games per opponent")
print(f"{'opponent':10} {'Sceptile win%':>13} {'Quick Growth/game':>18} {'Caterpie KO/game':>17} {'stopped share':>14}")
for opp in OPPS:
    rows = [r for r in res if r[0] == opp]
    w = sum(r[1] for r in rows); qg = sum(r[2] for r in rows); ko = sum(r[3] for r in rows); g = 2 * N
    print(f"{opp:10} {100*w/g:13.1f} {qg/g:18.2f} {ko/g:17.2f} {ko/max(qg+ko,1):14.0%}")
