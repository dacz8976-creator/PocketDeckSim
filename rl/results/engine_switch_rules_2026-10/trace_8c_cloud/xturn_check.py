"""Step 8c (the cloud): the cross-turn variant of coin_probe (coin_probe_xturn, make_coin_probe_xturn.py) run as support
for the by-hand traces. It changes no verdict: the verdicts are trace_8c.py's, by the accepted rule and probes.
  1. every game trace_8c.py left UNEXPLAINED or NEEDS A JUDGMENT: the variant at the first differing tick k;
  2. a check of the variant against the accepted probe: on every 10th game (in results order) that trace_8c.py explained
     as LOOKAHEAD ONLY through coin_probe, the variant must find the gate too, at the same or a smaller ply (it searches a
     superset: it only adds the forced continuations the bots resolve without a ply);
  3. negative controls: the same deals and ticks controls_8c.py used for coin_probe (controls.txt), where it must find
     nothing.
Writes xturn.tsv and xturn_summary.txt here. Usage: python3 xturn_check.py <work dir>"""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path(sys.argv[1])
SEED_BASE = "23100000000"
pairs = {}
for l in open(W / "pairs_8.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = l.split("\t")
    pairs[int(c[0])] = (c[3], c[5])


def xprobe(bot, pairing, i, tick):
    held, opp = pairs[pairing]
    p = subprocess.run([str(W / "bin_probex_coin_probe_xturn"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
                        "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot, "--deal", str(i), "--tick", str(tick)],
                       cwd=W / "probex" / "engine", capture_output=True, text=True)
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", p.stdout, re.M)
    if p.returncode != 0 or not m:
        return {"error": p.stderr[-200:]}
    path = re.search(r"^    after \[(.*)\] offers", p.stdout, re.M)
    parse = lambda s: None if s == "none" else int(s)
    return {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true", "path": path[1][:300] if path else ""}


def inside(r):
    """The accepted classification's reading of a coin probe result: found, and not only at the leaf of a mixed frame."""
    if "error" in r:
        return None
    found = r["queued"] is not None or r["cut"] is not None
    leaf = found and r["queued"] == 3 and not r["free"] and (r["cut"] is None or r["cut"] > 3)
    return "inside" if found and not leaf else ("leaf only" if leaf else "not found")


games = []
for f in sorted((HERE / "rows").glob("*.jsonl")):
    games += [json.loads(l) for l in open(f, encoding="utf-8")]
games.sort(key=lambda g: (g["step"] != "8", g["pairing"], g["bot"] != "km3", g["i"]))
targets = [g for g in games if g["verdict"] in ("UNEXPLAINED", "NEEDS A JUDGMENT")]
coin_la = [g for g in games if g["verdict"] == "LOOKAHEAD ONLY, both halves hold"
           and (g["probe_coin"]["queued"] is not None or g["probe_coin"]["cut"] is not None)]
sample = coin_la[::10]
controls = []
ctl = HERE / "controls.txt"
if ctl.exists():
    for l in ctl.read_text(encoding="utf-8").splitlines():
        m = re.match(r"coin probe, (\w+), pairing (\d+), deal (\d+), tick (\d+)", l)
        if m:
            controls.append((m[1], int(m[2]), int(m[3]), int(m[4])))
jobs = ([("target", g["bot"], g["pairing"], g["i"], g["k"], g) for g in targets]
        + [("check", g["bot"], g["pairing"], g["i"], g["k"], g) for g in sample]
        + [("control", b, p, i, t, None) for b, p, i, t in controls])
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(lambda j: xprobe(j[1], j[2], j[3], j[4]), jobs))
out = ["\t".join(("role", "step", "bot", "pairing", "i", "tick", "trace_8c_verdict", "accepted_coin_probe", "xturn_probe",
                  "xturn_reading", "xturn_path"))]
lines, bad = [], []
for (role, bot, p, i, t, g), r in zip(jobs, results):
    acc = "" if g is None else json.dumps(g.get("probe_coin"), sort_keys=True)
    rd = inside(r)
    out.append("\t".join(str(x) for x in (role, g["step"] if g else "8", bot, p, i, t, g["verdict"] if g else "(unchanged deal)", acc,
                                           json.dumps({k: v for k, v in r.items() if k != "path"}, sort_keys=True), rd,
                                           r.get("path", ""))))
    if role == "check":
        c = g["probe_coin"]
        acc_ply = min(x for x in (c["queued"], c["cut"]) if x is not None)
        x_ply = min((x for x in (r.get("queued"), r.get("cut")) if x is not None), default=None)
        if rd != "inside" or x_ply is None or x_ply > acc_ply:
            bad.append(f"check {bot} {p} {i}: accepted {c}, variant {r}")
    if role == "control" and rd != "not found":
        bad.append(f"control {bot} {p} {i} tick {t}: variant {r}")
(HERE / "xturn.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
tg = [(g, r) for (role, *_, g), r in zip(jobs, results) if role == "target"]
s = [f"the cross-turn variant (not the accepted probe; no verdict changes):",
     f"  on the {len(tg)} games trace_8c.py left UNEXPLAINED or NEEDS A JUDGMENT: "
     + ", ".join(f"{k} {sum(1 for _, r in tg if inside(r) == k)}" for k in ("inside", "leaf only", "not found", None) if any(inside(r) == k for _, r in tg)),
     f"  agreement check on {len(sample)} of the {len(coin_la)} lookahead games coin_probe explains (every 10th): "
     f"{len(sample) - sum(1 for b in bad if b.startswith('check'))} found by the variant at the same or a smaller ply",
     f"  negative controls ({len(controls)}, controls.txt's coin-probe deals and ticks): "
     f"{len(controls) - sum(1 for b in bad if b.startswith('control'))} found nothing",
     f"  problems: {bad or 'none'}"]
for g, r in tg:
    s.append(f"  {g['step']} {g['bot']} pairing {g['pairing']} i {g['i']} (tick {g['k']}, {g['verdict']}): variant {inside(r)}: "
             f"{ {k: v for k, v in r.items() if k != 'path'} }; path [{r.get('path', '')[:220]}]")
(HERE / "xturn_summary.txt").write_text("\n".join(s) + "\n", encoding="utf-8")
print("\n".join(s))
