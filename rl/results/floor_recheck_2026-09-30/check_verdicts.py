"""Reads the pages run_check.sh wrote and checks them against PLAN.md; writes verdicts.txt. No game is played.
Needed: brew-06 and brew-06b 'fail' under km3 on both sides; the deck 14 control (k3) 'untrusted'; the plain
run_screen.py wins equal the floor's per opponent for brew-06 and brew-06b. Reported beside: brew-05b and deck 07
(anchors), and whether the k3 control repeats Sept 28's games.
Usage: python3 check_verdicts.py"""
import os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(D, "..", "floor_recheck_2026-09-28")
PAGES = {"brew-06": "brew-06-pyukumuku-silvally-payback", "brew-06b": "brew-06b-pyukumuku-silvally-scyther-grass",
         "control": os.path.join("control_k3", "14-comfey-raticate-hypno"),
         "brew-05b": "brew-05b-meowstic-hatterene-comfey", "deck-07": "07-skarmory-stall"}
ANCHORS = {"brew-05b": "584 (kog3, Sept 28); 597 (kp3, Sept 25)", "deck-07": "903 (kog3, Sept 28); 908 (kp3, Sept 25)"}


def page(folder, stem):
    text = open(os.path.join(folder, stem + ".md"), encoding="utf-8").read()
    m = re.search(r"\*\*Verdict: (.+?)\.\*\* (\d+) wins in (\d+) games", text)
    verdict = m[1].rsplit(": ", 1)[-1] if m[1].startswith("control reading") else m[1]
    pilots = re.search(r"Pilots: (\S+) on the deck, (\S+) on the panel", text).groups()
    engine = re.search(r"- Engine: (\S+)", text)[1]
    opp = {o: int(w) for o, w in re.findall(r"^- (t-[\w-]+): (\d+)/\d+ = ", text, flags=re.M)}
    return dict(verdict=verdict, full=m[1], wins=int(m[2]), n=int(m[3]), pilots=pilots, engine=engine, opp=opp)


def screen(path):
    out, cur = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"== (\S+): (\d+)/(\d+) ", line)
        if m:
            cur = out.setdefault(m[1], {"total": int(m[2]), "opp": {}})
            continue
        m = re.match(r"\s+(t-[\w-]+)\s+(\d+)-", line)
        if m and cur is not None:
            cur["opp"][m[1]] = int(m[2])
    return out


P = {k: page(D, v) for k, v in PAGES.items()}
S = screen(os.path.join(D, "run_screen.txt"))
L, ok = [], True


def need(cond, text):
    global ok
    ok &= bool(cond)
    L.append(("PASS " if cond else "NOT MET ") + text)


for k in ("brew-06", "brew-06b"):
    p = P[k]
    need(p["verdict"] == "fail" and p["pilots"] == ("km3", "km3") and p["n"] == 1920,
         f"{k}: '{p['full']}', {p['wins']} of {p['n']}, pilots {p['pilots'][0]}/{p['pilots'][1]} (needed: fail, km3 on both sides)")
    s = S.get(PAGES[k], {"total": None, "opp": {}})
    need(s["opp"] == p["opp"] and s["total"] == p["wins"],
         f"{k}: plain run_screen.py per opponent {s['opp'] or 'missing'} (total {s['total']}) v the floor's {p['opp']} (total {p['wins']})")
c = P["control"]
need(c["verdict"] == "untrusted" and c["pilots"] == ("k3", "k3"),
     f"control deck 14: '{c['full']}', {c['wins']} of {c['n']} (needed: untrusted, k3 on both sides)")
engines = {p["engine"] for p in P.values()}
need(engines == {"rl/engine-2026-09-30/deckgym"}, f"engine on every page: {sorted(engines)}")
L.append("")
for k in ("brew-05b", "deck-07"):
    p = P[k]
    L.append(f"reported: {k}: {p['full']}, {p['wins']} of {p['n']} ({100 * p['wins'] / p['n']:.1f}%); before: {ANCHORS[k]}")
try:
    old = page(OLD, PAGES["control"])
    same = old["wins"] == c["wins"] and old["opp"] == c["opp"]
    L.append(f"reported: the k3 control {'repeats' if same else 'DIFFERS FROM'} Sept 28's games ({c['wins']} v {old['wins']} wins; per opponent "
             f"{'equal' if old['opp'] == c['opp'] else str(c['opp']) + ' v ' + str(old['opp'])})")
except (OSError, TypeError, AttributeError) as e:
    L.append(f"reported: the Sept 28 control page could not be read ({e})")
L.insert(0, ("RECHECK PASSED: the floor stays usable under km3" if ok else
             "RECHECK NOT PASSED: the floor isn't used until Dustin has seen the pages") + "\n")
open(os.path.join(D, "verdicts.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("\n".join(L))
sys.exit(0 if ok else 1)
