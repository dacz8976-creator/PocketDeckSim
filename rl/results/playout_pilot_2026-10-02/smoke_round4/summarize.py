"""The play-out pilot's round-4 smoke (Oct 4): kx3 (REALISTIC, the wide pool) on draft A against km3 on Dustin's deck 01,
which is in no pool, so the pilot must infer its list. The summary of a whole run, resumed or not, from its two files
(adapted from smoke/summarize.py; the inference lines are new).
Reads games.jsonl (one line per pilot game: seed, seat, both arms' results, decisions, changed, time) and trace.jsonl (one
line per decision that ran play-outs) next to this script, and writes summary.txt beside them:
- the pilot's score and km3's on the same deals, and the paired difference with its 95% interval, overall and by seat;
- the deals where the two arms' results differ;
- the decisions: asked, with play-outs, without (km's move kept with no play-out: setup after the opponent's, one move),
  changed from km3's move;
- the time: milliseconds per decision with play-outs (mean, median, p95, max), per decision of any kind (mean), seconds
  per pilot game (mean, median, max), by seat;
- the candidates per decision, the cap's drops, failed play-out rounds, the opponent lists the play-outs drew;
- the inference: the share of rounds whose opponent list was inferred ("inferred from N lists: <base>") or drawn whole
  from the pool ("<list> (1 of k consistent)"), the bases the inferred rounds used, by game turn;
- every changed decision with its evidence, and how close the kept decisions came to the threshold.
Usage: python3 summarize.py"""
import json, math, statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
games = [json.loads(l) for l in open(HERE / "games.jsonl", encoding="utf-8")]
traces = [json.loads(l) for l in open(HERE / "trace.jsonl", encoding="utf-8")]
out = []
say = out.append


def interval(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / max(1, n - 1))
    return m, 1.96 * sd / math.sqrt(n)


def pct(xs, p):
    xs = sorted(xs)
    return xs[round((len(xs) - 1) * p)]


say(f"games: {len(games)} (pilot kx3 v km3; the same deals km3 v km3), deals {len({g['seed'] for g in games})}")
for label, gs in [("all", games), ("pilot in seat 0", [g for g in games if g["pilot_seat"] == 0]),
                  ("pilot in seat 1", [g for g in games if g["pilot_seat"] == 1])]:
    if not gs:
        continue
    m, h = interval([g["pilot_score"] - g["km3_score"] for g in gs])
    say(f"  {label}: {len(gs)} games; pilot {sum(g['pilot_score'] for g in gs) / len(gs):.3f}, km3 on the same deals "
        f"{sum(g['km3_score'] for g in gs) / len(gs):.3f}; paired difference {m:+.3f} ± {h:.3f} (95%)")
moved = [g for g in games if g["pilot_score"] != g["km3_score"]]
say(f"deals whose result differs between the arms: {len(moved)}: " + "; ".join(
    f"seed {g['seed']} seat {g['pilot_seat']}: pilot {g['pilot_score']:g}, km3 {g['km3_score']:g} (changed {g['changed']})" for g in moved))
games_changed = [g for g in games if g["changed"]]
same_result = [g for g in games_changed if g["pilot_score"] == g["km3_score"]]
say(f"games with at least one changed decision: {len(games_changed)}; of these, same result as km3's game: {len(same_result)}")

decisions = sum(g["decisions"] for g in games)
changed = sum(g["changed"] for g in games)
say(f"\ndecisions asked of the pilot: {decisions}; with play-outs {len(traces)}; without {decisions - len(traces)} "
    f"(km's move kept with no play-out); changed from km3's move {changed} ({changed / max(1, len(traces)):.1%} of those with play-outs)")
ms = [t["decision"]["ms"] for t in traces]
say(f"ms per decision with play-outs: mean {sum(ms) / len(ms):.0f}, median {pct(ms, 0.5):.0f}, p95 {pct(ms, 0.95):.0f}, max {max(ms):.0f}")
say(f"ms per decision of any kind (from the games' means): {sum(g['ms_per_decision'] * g['decisions'] for g in games) / decisions:.0f}")
for label, gs in [("all", games), ("seat 0", [g for g in games if g["pilot_seat"] == 0]), ("seat 1", [g for g in games if g["pilot_seat"] == 1])]:
    secs = [g["seconds"] for g in gs]
    if secs:
        say(f"seconds per pilot game, {label}: mean {sum(secs) / len(secs):.1f}, median {pct(secs, 0.5):.1f}, max {max(secs):.1f}; "
            f"decisions per game {sum(g['decisions'] for g in gs) / len(gs):.1f}; turns per game {sum(g['turns'] for g in gs) / len(gs):.1f}")

ncand = [len(t["decision"]["candidates"]) for t in traces]
drops = [len(t["decision"]["dropped"]) for t in traces]
say(f"\ncandidates per decision with play-outs: mean {sum(ncand) / len(ncand):.1f}, median {pct(ncand, 0.5)}, max {max(ncand)}; "
    f"decisions at the cap (with drops) {sum(1 for d in drops if d)}, moves dropped {sum(drops)}")
say(f"play-out rounds: {sum(t['decision']['rounds'] for t in traces)}, failed (dropped) {sum(t['decision']['failed_rounds'] for t in traces)}")
lists = Counter()
for t in traces:
    lists.update(t["decision"]["lists"])
total = sum(lists.values())
inferred = sum(v for k, v in lists.items() if k.startswith("inferred from"))
say(f"opponent lists the rounds drew (the real list, Dustin's deck 01, is in no pool): {total} rounds; inferred {inferred} "
    f"({inferred / max(1, total):.1%}), drawn whole from the pool {total - inferred} ({(total - inferred) / max(1, total):.1%})")
bases = Counter()
for k, v in lists.items():
    if k.startswith("inferred from"):
        bases[k.split(": ", 1)[1]] += v
say("  bases of the inferred rounds: " + ", ".join(f"{k} {v / max(1, inferred):.1%}" for k, v in bases.most_common()))
whole = Counter()
for k, v in lists.items():
    if not k.startswith("inferred from"):
        whole[k.split(" (")[0]] += v
say("  lists drawn whole: " + (", ".join(f"{k} {v}" for k, v in whole.most_common()) or "none"))
labels = Counter(k.split(": ")[0] for k in lists if k.startswith("inferred from"))
say("  inference labels: " + ", ".join(f"'{k}'" for k in sorted(labels)))
by_turn = {}
for t in traces:
    d = t["decision"]
    n = sum(v for k, v in d["lists"].items() if k.startswith("inferred from"))
    a = by_turn.setdefault(min(d["turn"], 12), [0, 0])
    a[0] += n
    a[1] += sum(d["lists"].values())
say("  inferred share by game turn (12 = 12 or later): " + ", ".join(f"t{k} {v[0] / max(1, v[1]):.0%}" for k, v in sorted(by_turn.items())))

say("\nthe changed decisions (seed, seat, turn: km3's move -> the pilot's; the lead over km3's move ± its standard error):")
for t in traces:
    d = t["decision"]
    if d["chosen"] != d["km_move"]:
        best = next(c for c in d["candidates"] if c["move"] == d["chosen"])
        say(f"  {t['seed']} s{t['pilot_seat']} t{d['turn']}: {d['km_move']} -> {d['chosen']}: {best['diff']:+.3f} ± {best['se']:.3f} "
            f"({len(d['candidates'])} candidates, {d['rounds']} rounds)")
kept_leads = []
for t in traces:
    d = t["decision"]
    if d["chosen"] == d["km_move"] and len(d["candidates"]) > 1:
        lead = max((c for c in d["candidates"] if c["move"] != d["km_move"]), key=lambda c: c["diff"])
        if lead["diff"] > 0 and lead["se"] > 0:
            kept_leads.append(lead["diff"] / lead["se"])
say(f"kept decisions where a rival led km3's move: {len(kept_leads)}; the rival's lead in standard errors: median "
    f"{pct(kept_leads, 0.5):.2f}, share at 1.5 or more {sum(1 for x in kept_leads if x >= 1.5) / max(1, len(kept_leads)):.1%}"
    if kept_leads else "kept decisions where a rival led km3's move: 0")
(HERE / "summary.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
