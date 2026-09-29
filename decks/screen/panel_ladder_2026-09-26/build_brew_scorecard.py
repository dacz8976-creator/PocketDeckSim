#!/usr/bin/env python3
"""Rebuild brew_scorecard.md, the one-file scorecard of floor, predicted setup speed and ladder record.

Standard library only. Reads, and changes nothing but its output file:
  - the floor pages   rl/results/floor*/**/<slug>.md   (newest folder date wins per deck; control pages skipped)
  - the A1 harness    decks/consistency_2026-09-25/ANCHORS.md   (the dated prediction and the table)
  - an export of the Ladder Log's `logs` collection   <export>/logs/<doc>.json

Refresh (panel agent, Dustin Sept 29):
  1. Export the log, READ ONLY. ArtifactData: action "list", url https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1,
     collection "logs", query {"limit": 1000}, out_dir <export folder>. It writes <export folder>/logs/<doc>.json.
  2. python3 decks/screen/panel_ladder_2026-09-26/build_brew_scorecard.py --export <export folder>

Same inputs give the same file: nothing here reads the clock. Warnings go to stderr.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "brew_scorecard.md"
ANCHORS = REPO / "decks" / "consistency_2026-09-25" / "ANCHORS.md"
RESULTS = REPO / "rl" / "results"
LOG_URL = "https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1"

# One row per deck the scorecard follows. `key` is also the default Ladder Log doc id.
# slug = the floor page / ANCHORS name; logs = Ladder Log doc ids that hold this deck's games.
ROWS = {
    "brew-08": dict(name="Brew 08 Entei ex / Rainbow Cave + Flame Patch", slug="brew-08-entei-rainbow-cave", pred="08"),
    "brew-07": dict(name="Brew 07 Hoopa ex / Darkrai ex / Mega Sableye ex", slug="brew-07-hoopa-darkrai-sableye", pred="07"),
    "brew-09": dict(name="Brew 09 Mega Sableye ex / Galarian Obstagoon", slug="brew-09-sableye-obstagoon", pred="09"),
    "brew-10": dict(name="Brew 10 Mega Diancie ex / Giratina ex", slug="brew-10-diancie-giratina", pred="10"),
    "d07": dict(name="Deck 07 Skarmory stall", slug="07-skarmory-stall", logs=["d07"]),
    "brew-05b": dict(name="Brew 05b Meowstic / Hatterene / Comfey (log id brew-05)", slug="brew-05b-meowstic-hatterene-comfey", logs=["brew-05"]),
    "brew-01": dict(name="Brew 01 Arceus ex / Crobat / Xatu", slug="brew-01-arceus-crobat-xatu"),
    "brew-03a": dict(name="Brew 03a Arceus ex / Nihilego / Toxapex", slug="brew-03a-arceus-nihilego-toxapex"),
    "brew-06": dict(name="Brew 06 Payback (Pyukumuku / Silvally / TR Mewtwo)", slug="brew-06-pyukumuku-silvally-payback"),
    "brew-06b": dict(name="Brew 06b Payback, Grass (Pyukumuku / Silvally / TR Scyther)", slug="brew-06b-pyukumuku-silvally-scyther-grass"),
    "d02": dict(name="Deck 02 Arceus ex / Crobat", slug="02-arceus-crobat", logs=["d02"]),
    "brew-04": dict(name="Brew 04 Xatu / TR Slowking", slug="brew-04-xatu-slowking"),
    "brew-05c": dict(name="Brew 05c Meowstic / Hatterene (the Cape variant)", slug="brew-05c"),
    "brew-02": dict(name="Brew 02 Arceus ex / Tandemaus / Persian", slug="brew-02-arceus-tandemaus-persian"),
    "brew-03b": dict(name="Brew 03b Arceus ex / Crobat / Nihilego / Toxapex", slug="brew-03b-arceus-crobat-nihilego-toxapex"),
}

GROUPS = [
    ("A", "Prediction written before play (brews 07-10)", ["brew-08", "brew-07", "brew-09", "brew-10"]),
    ("B", "Anchors: played before the harness existed (its measure was set after their results)",
     ["d07", "brew-05b", "brew-01", "brew-03a", "brew-06", "brew-06b"]),
    ("C", "Played, no floor page, no prediction", ["d02", "brew-04", "brew-05c"]),
    ("D", "Floor page only: never played, no prediction", ["brew-02", "brew-03b"]),
]

# Names for Ladder Log docs that are not scorecard rows (the video-derived "c-" decks).
EXTRA_NAMES = {
    "c-entei-ex-video-visible-core": "Entei ex (video-visible core)",
    "c-hydreigon-galarian-obstagoon-video-visib": "Hydreigon / Galarian Obstagoon (video-visible core)",
    "c-mega-sharpedo-ex-gyarados-video-visible-": "Mega Sharpedo ex / Gyarados (video-visible core)",
    "c-skarmory-ex-chandelure": "Skarmory ex / Chandelure",
    "c-skarmory-ex-indeedee-ex-genesect-video-v": "Skarmory ex / Indeedee ex / Genesect (video-visible core)",
    "c-type-null-silvally-video-visible-core": "Type: Null / Silvally (video-visible core)",
}

# What the prediction's wording called each brew (checked against the parsed figures below).
PRED_WORDS = {"08": "fastest (named with 07)", "07": "fastest (named with 08)", "09": "third of four", "10": "slowest"}

HEADER = ("| Brew | Floor: kog3 vs the 8 panel decks, 1,920 games | Weakest matchups (each ±6) | "
          "Sim setup: main attacker's first attack by own turn 2 / 3 / 4, opp. points before it | "
          "A1 harness: points conceded before first 30+ attack | Ladder W-L | "
          "Three-item setup note (Dustin's ladder games) |")
SEP = "|---|---|---|---|---|---|---|"


def warn(msg):
    print("WARNING: " + msg, file=sys.stderr)


def read(p):
    return Path(p).read_text(encoding="utf-8")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def clean(s):
    return s.replace("|", "/").replace("\n", " ").strip()


def chicago():
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo("America/Chicago")
    except Exception:
        warn("no tz data for America/Chicago; using fixed UTC-5 (CDT, right for every date so far)")
        return timezone(timedelta(hours=-5))


# ---------------------------------------------------------------- floor pages

def find_floor_pages():
    """slug -> list of (folder date, mtime, path), newest last."""
    found = {}
    for p in RESULTS.glob("floor*/**/*.md"):
        if "control" in p.parent.name.lower():
            continue
        try:
            first = read(p).split("\n", 1)[0]
        except OSError:
            continue
        m = re.match(r"# Floor check: (\S+)", first)
        if not m:
            continue
        top = p.relative_to(RESULTS).parts[0]
        d = re.search(r"(\d{4}-\d{2}-\d{2})", top)
        found.setdefault(m.group(1), []).append((d.group(1) if d else "0000-00-00", p.stat().st_mtime, p))
    for v in found.values():
        v.sort(key=lambda t: (t[0], t[1]))
    return found


def section(text, heading_re):
    m = re.search(heading_re, text, re.M)
    if not m:
        return ""
    body = text[m.end():]
    nxt = re.search(r"^## ", body, re.M)
    return body[:nxt.start()] if nxt else body


def parse_floor(path):
    t = read(path)
    f = {"path": path}
    m = re.search(r"\*\*Verdict: (.+?)\.\*\*\s+(\d+) wins in (\d+) games \(([\d.]+)%\)", t)
    if not m:
        raise ValueError("no verdict line in %s" % path)
    v = m.group(1)
    f["verdict"] = {"clears the floor": "clears"}.get(v, v)
    f["wins"], f["games"], f["pct"] = int(m.group(2)), int(m.group(3)), m.group(4)

    f["lowuse"] = []
    m = re.search(r"^Flagged cards \([^)]*\): (.*?)\. A share under", t, re.M)
    if m and m.group(1).strip().lower() != "none":
        for part in m.group(1).split("; "):
            mm = re.match(r"(.+?): used on (\d+) of (\d+) opportunities \(([\d.]+)%\)", part)
            if mm and int(mm.group(3)) >= 20 and float(mm.group(4)) < 25:
                f["lowuse"].append((mm.group(1), mm.group(4), int(mm.group(3))))

    f["worst"] = []
    for line in section(t, r"^## Worst matchups.*$").splitlines():
        mm = re.match(r"- t-(\w+): \d+/\d+ = (\d+)%", line)
        if mm:
            f["worst"].append((mm.group(1).capitalize(), int(mm.group(2))))

    for key, label in (("first", "went first"), ("second", "went second")):
        row = next((l for l in t.splitlines() if l.startswith("| " + label + " ")), None)
        if not row:
            raise ValueError("no '%s' row in %s" % (label, path))
        c = cells(row)
        f[key] = {"games": int(c[1]), "did": [int(x) for x in re.findall(r"\d+", c[3])],
                  "pts": c[4], "never": c[5]}
    m = re.search(r"^Main attackers for these measures \((.*?)\): (.*?)\. Draws: \d+", t, re.M)
    f["main"] = m.group(2) if m else "?"
    f["guess"] = bool(m and "fallback" in m.group(1))
    m = re.search(r"Pilots: ([^.]*?)\.", t)
    f["pilots"] = m.group(1) if m else "?"

    f["page_items"] = []
    for line in section(t, r"^## Your first \w+ ladder games.*$").splitlines():
        if not line.startswith("|"):
            continue
        c = cells(line)
        if len(c) < 5 or c[0].lower() == "opponent" or re.fullmatch(r"[-: ]+", c[0]):
            continue
        went, att, pts = c[1].lower(), c[2].lower(), re.search(r"\d+", c[3])
        seat = 1 if ("1st" in went or "first" in went) else 2 if ("2nd" in went or "second" in went) else None
        tm = re.search(r"turn\s*(\d+)", att)
        f["page_items"].append({
            "who": re.sub(r"\s*\(.*$", "", c[0]).strip(), "seat": seat,
            "turn": int(tm.group(1)) if tm else None,
            "conceded": (not tm) and "never" in att and "conceded" in att,
            "pts": int(pts.group(0)) if pts else None,
            "inferred": "inferred" in went or "inferred" in att,
        })
    return f


# ---------------------------------------------------------------- A1 (ANCHORS.md)

def parse_anchors():
    t = read(ANCHORS)
    head = []
    for line in t.splitlines():
        if line.startswith(">"):
            head.append(line.lstrip("> ").rstrip())
        elif head:
            break
    quote = re.sub(r"\s+", " ", " ".join(head)).replace("**", "")
    pred = {"quote": quote}
    m = re.search(r"made before any of these brews was played on the ladder: (\d{4}-\d{2}-\d{2}), about "
                  r"(\d{1,2}:\d{2}) (\w+) \(commit (\w+)'s numbers\)", quote)
    pred["when"] = "%s, about %s %s" % (m.group(1), m.group(2), m.group(3)) if m else "date not found"
    pred["commit"] = m.group(4) if m else "?"
    pred["fig"] = {mm.group(1): float(mm.group(3)) for mm in
                   re.finditer(r"\b(0[7-9]|10) ([A-Za-z/ ]+?) \((\d\.\d\d)\)", quote)}
    m = re.search(r"With [^.]*?gross failure[^)]*\)\.", quote)
    pred["scoring"] = m.group(0) if m else ""
    order = sorted(pred["fig"], key=lambda k: pred["fig"][k])
    if order != ["08", "07", "09", "10"]:
        warn("prediction order parsed from ANCHORS.md is %s, not 08 07 09 10; check PRED_WORDS" % order)

    rows = {}
    body = t.split("<!-- table:start", 1)[-1].split("<!-- table:end", 1)[0]
    for line in body.splitlines():
        if not line.startswith("| ") or " (main " not in line:
            continue
        c = cells(line)
        if len(c) < 11:
            continue
        m = re.search(r"\*\*(\d+\.\d+)\*\* ± (\d+\.\d+)", c[10])
        if m:
            rows[c[0].split(" (main ")[0]] = {"head": m.group(1), "noise": m.group(2)}
    return pred, rows


# ---------------------------------------------------------------- Ladder Log export

def load_logs(export):
    d = Path(export) / "logs"
    if not d.is_dir():
        sys.exit("No logs folder at %s. Export the Ladder Log's `logs` collection there first "
                 "(see the top of this script)." % d)
    docs = {}
    for p in sorted(d.glob("*.json")):
        j = json.loads(read(p))
        docs[p.stem] = sorted(j.get("games", []), key=lambda g: g.get("ts", 0))
    return docs


ITEM_RE = re.compile(
    r"(?P<seat>\b1st\b|\b2nd\b|\bfirst\b|\bsecond\b)[^|\n]*\|[^|\n]*?"
    r"(?:\bT\s?(?P<t>\d+)\b|\bturn\s*(?P<t2>\d+)\b|(?P<nv>\bnever\b))[^|\n]*\|[^|\n]*?"
    r"\bopp\w*\s*(?P<p>\d+)", re.I)


def three_items(page_items, games):
    """Items from the floor page's ladder table, plus any game whose Note box carries
    'seat | attack turn | opp N pts'. Returns (items, games without items)."""
    items, used = [], set()
    for it in page_items:
        idx = next((i for i, g in enumerate(games)
                    if i not in used and it["who"] and it["who"] in g.get("note", "")), None)
        if idx is not None:
            used.add(idx)
        items.append(it)
    for i, g in enumerate(games):
        if i in used:
            continue
        m = ITEM_RE.search(g.get("note", ""))
        if not m:
            continue
        used.add(i)
        turn = m.group("t") or m.group("t2")
        items.append({"who": g.get("opp", ""), "seat": 1 if m.group("seat").lower() in ("1st", "first") else 2,
                      "turn": int(turn) if turn else None, "conceded": False, "pts": int(m.group("p")),
                      "inferred": False})
    return items, [g for i, g in enumerate(games) if i not in used]


def record(games):
    w = sum(1 for g in games if g.get("result") == "W")
    l = sum(1 for g in games if g.get("result") == "L")
    if w + l != len(games):
        warn("a game has a result other than W or L")
    conc = sum(1 for g in games if g.get("result") == "W" and re.search(r"concession", g.get("note", ""), re.I))
    return w, l, conc


def ladder_cell(games):
    if not games:
        return "no games"
    w, l, conc = record(games)
    s = "**%d-%d** (%d%%)" % (w, l, round(100 * w / (w + l))) if w + l else "0 games"
    if conc:
        s += "; %d of %d wins by concession" % (conc, w)
    return s


def summarize(items):
    """Numbers behind the three-item cell."""
    out = {"n": len(items), "seats": {}}
    for seat in (1, 2):
        its = [i for i in items if i["seat"] == seat]
        got = [i for i in its if not i["conceded"]]
        out["seats"][seat] = {
            "games": len(its), "got": len(got), "conceded": len(its) - len(got),
            "by": [sum(1 for i in got if i["turn"] is not None and i["turn"] <= t) for t in (2, 3, 4)],
        }
    pts = [i["pts"] for i in items if i["turn"] is not None and i["pts"] is not None]
    out["pts"] = pts
    out["mean"] = sum(pts) / len(pts) if pts else None
    out["inferred"] = sum(1 for i in items if i["inferred"])
    out["noseat"] = sum(1 for i in items if i["seat"] is None)
    return out


def items_cell(items, missing, ngames):
    if not ngames:
        return "-"
    noun = "game" if ngames == 1 else "games"
    if not items:
        return "none (0 of %d %s)" % (ngames, noun)
    s = summarize(items)
    parts = ["%d of %d %s." % (len(items), ngames, noun)]
    for seat, lbl in ((1, "1st"), (2, "2nd")):
        d = s["seats"][seat]
        if not d["games"]:
            continue
        t = "%s (%d %s): by T2 %d/%d, T3 %d/%d, T4 %d/%d." % (
            lbl, d["games"], "game" if d["games"] == 1 else "games",
            d["by"][0], d["got"], d["by"][1], d["got"], d["by"][2], d["got"])
        if d["conceded"]:
            t += " %d conceded before its first attack." % d["conceded"]
        parts.append(t)
    if s["pts"]:
        if len(set(s["pts"])) == 1:
            parts.append("Opp. points at that attack: %d in all %d." % (s["pts"][0], len(s["pts"])))
        else:
            parts.append("Opp. points at that attack: mean %.2f over %d (range %d-%d)." % (
                s["mean"], len(s["pts"]), min(s["pts"]), max(s["pts"])))
    if s["inferred"]:
        parts.append("%d %s inferred from context." % (s["inferred"], "game" if s["inferred"] == 1 else "games"))
    if missing:
        names = [clean(g.get("opp", "?"))[:60] for g in missing[:3]]
        parts.append("No items yet: %s%s." % ("; ".join(names), " +%d more" % (len(missing) - 3) if len(missing) > 3 else ""))
    return " ".join(parts)


# ---------------------------------------------------------------- cells

def floor_cell(f):
    if not f:
        return "no floor page"
    s = "**%s** %s (%.1f%%)" % (f["verdict"], format(f["wins"], ","), float(f["pct"]))
    if f["lowuse"]:
        s += "; low use: " + ", ".join(
            "%s %s%%" % (re.sub(r" as Trainer \(played\)$", " (Trainer)", n), p) for n, p, _ in f["lowuse"])
    return clean(s)


def worst_cell(f):
    return ", ".join("%s %d%%" % w for w in f["worst"][:3]) if f else "-"


def sim_cell(f):
    if not f:
        return "-"
    def one(lbl, r):
        return "%s %d / %d / %d%%, opp %s" % (lbl, r["did"][0], r["did"][1], r["did"][2], r["pts"])
    s = "%s; %s; never attacks %s / %s; main: %s%s" % (
        one("1st", f["first"]), one("2nd", f["second"]), f["first"]["never"], f["second"]["never"],
        f["main"], " (guess)" if f["guess"] else "")
    return clean(s)


def a1_cell(cfg, pred, a1):
    slug, num = cfg["slug"], cfg.get("pred")
    row = a1.get(slug)
    if num and num in pred["fig"]:
        rank = PRED_WORDS.get(num, "")
        noise = " ± %s" % row["noise"] if row else ""
        return "**Predicted** %s: %.2f%s pts, %s" % (pred["when"], pred["fig"][num], noise, rank)
    if row:
        return "%s ± %s pts (not a prediction: measure set after the result)" % (row["head"], row["noise"])
    return "-"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", required=True, help="folder holding logs/<doc>.json from the Ladder Log export")
    ap.add_argument("--out", default=str(OUT), help="output file (default: brew_scorecard.md beside this script)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the file")
    args = ap.parse_args()

    docs = load_logs(args.export)
    pred, a1 = parse_anchors()
    pages = find_floor_pages()
    floor = {}
    for slug, cands in pages.items():
        floor[slug] = parse_floor(cands[-1][2])

    tz = chicago()
    all_games = [g for gs in docs.values() for g in gs]
    tw, tl, tconc = record(all_games)
    latest = max((g.get("ts", 0) for g in all_games), default=0)
    latest_s = datetime.fromtimestamp(latest / 1000, tz).strftime("%Y-%m-%d %H:%M") if latest else "n/a"

    used_docs, info = set(), {}
    for key, cfg in ROWS.items():
        ids = cfg.get("logs", [key])
        games = sorted([g for i in ids for g in docs.get(i, [])], key=lambda g: g.get("ts", 0))
        used_docs.update(i for i in ids if i in docs)
        f = floor.get(cfg["slug"])
        items, missing = three_items(f["page_items"] if f else [], games)
        info[key] = dict(cfg=cfg, games=games, floor=f, items=items, missing=missing)

    def row_md(key):
        r = info[key]
        c = r["cfg"]
        return "| %s | %s | %s | %s | %s | %s | %s |" % (
            clean(c["name"]), floor_cell(r["floor"]), worst_cell(r["floor"]), sim_cell(r["floor"]),
            clean(a1_cell(c, pred, a1)), ladder_cell(r["games"]), clean(items_cell(r["items"], r["missing"], len(r["games"]))))

    L = []
    add = L.append
    add("<!-- Generated by build_brew_scorecard.py from the floor pages, ANCHORS.md and a Ladder Log export. "
        "Do not edit by hand: fix the source or the script and rebuild. -->")
    add("# Brew scorecard: floor, predicted setup speed and ladder record, side by side")
    add("")
    add("The ladder is the production test. Per brew, this puts the floor figure, the sim's setup speed and Dustin's "
        "ladder record with his three-item setup note in one row. The brew 08 row is first because a prediction about "
        "it was written (%s) before he played it." % pred["when"])
    add("")
    add("**Standing job of the panel agent (Dustin, Sept 29).** Keep this one file current whenever the Ladder Log "
        "changes. It is rewritten in place: no new folder or file per brew.")
    add("")
    add("## How to refresh it")
    add("")
    add("1. Export the Ladder Log's `logs` collection. Read only: never write to the log. Tool ArtifactData, "
        "action `list`, url `%s`, collection `logs`, query `{\"limit\": 1000}`, `out_dir` a scratch folder. "
        "It writes `<out_dir>/logs/<doc>.json`." % LOG_URL)
    add("2. From the repo root, in WSL: `python3 decks/screen/panel_ladder_2026-09-26/build_brew_scorecard.py "
        "--export <out_dir>`. It rewrites this file. It plays no games and reads no engine.")
    add("3. Run it again when a floor page is added or changed under `rl/results/floor*/`, or when `ANCHORS.md` "
        "changes. The newest floor page for a deck wins.")
    add("4. A Ladder Log doc the script does not know shows up in section E and prints a warning. Add it to `ROWS` in "
        "the script if it deserves a row of its own.")
    add("5. Do not commit from the panel agent's session unless asked; the parent session reviews and commits.")
    add("")
    add("**Log state at this build:** %d games in %d docs with games, record %d-%d (%d wins by concession); newest game filed "
        "%s Chicago time." % (len(all_games), sum(1 for g in docs.values() if g), tw, tl, tconc, latest_s))
    add("")
    add("Rows are grouped, not ranked. Nothing here ranks the brews, and clearing the floor is not a recommendation "
        "(the ranking hold stands).")

    # --- Group A
    add("")
    add("## A. %s" % GROUPS[0][1])
    add("")
    add("The prediction, made before any of these brews was played on the ladder (%s, commit %s's numbers): points "
        "conceded before the first attack of 30 or more damage, scripted pilot against the `aa` bot, mean of both "
        "seats. Fastest to slowest: %s. %s" % (
            pred["when"], pred["commit"],
            ", ".join("%s %.2f" % (k, pred["fig"][k]) for k in sorted(pred["fig"], key=lambda k: pred["fig"][k])),
            pred["scoring"]))
    add("")
    add(HEADER)
    add(SEP)
    for k in GROUPS[0][2]:
        add(row_md(k))
    add("")
    have = [k for k in GROUPS[0][2] if info[k]["items"]]
    if not have:
        add("**Prediction status:** no predicted brew has setup notes yet.")
    else:
        bits = []
        for k in have:
            s = summarize(info[k]["items"])
            bits.append("%s: opponent had a mean of %.2f points at the first main attack over %d games (predicted %.2f)"
                        % (info[k]["cfg"]["name"].split(" ")[1], s["mean"] if s["mean"] is not None else float("nan"),
                           len(s["pts"]), pred["fig"].get(info[k]["cfg"]["pred"], float("nan"))))
        if len(have) < 2:
            add("**Prediction status:** only brew %s has setup notes. The prediction is an order across brews, so it "
                "cannot be scored until at least one more of %s has games with the three items. %s." % (
                    info[have[0]]["cfg"]["pred"],
                    ", ".join(info[k]["cfg"]["pred"] for k in GROUPS[0][2] if k not in have), bits[0]))
        else:
            add("**Prediction status:** %d of the 4 predicted brews have setup notes. %s. Compare by hand with the "
                "predicted order." % (len(have), "; ".join(bits)))
    add("")
    add("The measure differs a little by column. The prediction and the sim column count opponent points before the "
        "first 30+ attack (A1) or first main attack (floor page); Dustin's note counts the opponent's points when he "
        "first attacks with the main attacker. For Entei ex the two are the same event: its only attack, Blazing "
        "Beatdown, does 60 or more.")

    # --- Groups B-D
    for gid, title, keys in GROUPS[1:]:
        add("")
        add("## %s. %s" % (gid, title))
        add("")
        add(HEADER)
        add(SEP)
        for k in keys:
            add(row_md(k))

    # --- Group E
    extras = [(d, gs) for d, gs in docs.items() if d not in used_docs and gs]
    add("")
    add("## E. Other decks in the Ladder Log (record only: no floor page, no prediction)")
    add("")
    if extras:
        add("| Log doc | Deck | Ladder W-L |")
        add("|---|---|---|")
        for d, gs in extras:
            if d not in EXTRA_NAMES:
                warn("Ladder Log doc '%s' is not in ROWS or EXTRA_NAMES" % d)
            add("| %s | %s | %s |" % (d, clean(EXTRA_NAMES.get(d, "(not in the script's table)")), ladder_cell(gs)))
    else:
        add("None.")
    covered = sum(len(r["games"]) for r in info.values()) + sum(len(gs) for _, gs in extras)
    add("")
    add("Games in sections A to E: %d; games in the log: %d." % (covered, len(all_games)))
    if covered != len(all_games):
        warn("sections A-E cover %d games but the log has %d" % (covered, len(all_games)))

    # --- Notes
    add("")
    add("## What each column is, and is not")
    add("")
    add("- **Floor.** `decks/screen/floor.py`: pilot kog3 on both sides, 240 games against each of the 8 panel decks, "
        "1,920 games in all. Bar: 349 or fewer wins fail, 350-418 are borderline, 419 or more clear. Each matchup is "
        "±6 points, the total ±1.8. It is the sim's win rate against the panel, not a ladder win rate. \"Low use\" "
        "means a flagged card the bot played on under 25% of at least 20 chances, so the sim may understate the deck.")
    add("- **Weakest matchups.** The three lowest of the 8, from the floor page.")
    add("- **Sim setup.** From the floor page's failure-modes table: the share of games in which the deck's main "
        "attacker had made its first attack by the deck's own turn 2, 3 and 4 (your first turn is 1), then the "
        "opponent's average points before that attack, for going first (1st) and second (2nd), and the share of "
        "games in which it never attacks. \"(guess)\" means the page had no A1 entry and floor.py took the Pokémon "
        "with the highest printed damage as the main attacker.")
    add("- **A1 harness.** `decks/consistency_2026-09-25/ANCHORS.md`: points conceded before the deck's first attack "
        "of 30+ damage, scripted pilot against `aa`, both seats averaged (± is simulation noise only). Only brews "
        "07-10 have a prediction dated before play. The six anchors' figures are shown for scale: the measure was "
        "picked after their ladder results were known.")
    add("- **Ladder W-L.** Counted from the Ladder Log export. A concession is a win (Dustin, Sept 28); the number of "
        "wins by concession is shown, not adjusted. These are 1 to 10 games: at 10 games a win rate is uncertain by "
        "about ±30 points, so it cannot be compared with the floor's percent.")
    add("- **Three-item note.** For each game: went first or second, the turn of the first attack with the main "
        "attacker, and the opponent's points then. First asked for on Sept 28 (brews 07 and 08), so earlier games "
        "have a result and free-text notes only. Items come from the floor page's ladder table when it has one "
        "(brew 08's nine video reviews), and from any Note box written as `2nd | Entei T2 | opp 0 pts`. \"By T2 x/y\" "
        "counts games that reached a first attack; games the opponent ended by concession first are left out of y.")
    add("- **Three different \"opponent points\".** A1: scripted pilot against a one-Pokémon goldfish. Floor page: "
        "kog3 against kog3 on the panel. Ladder: real opponents. Same idea, different opponents.")

    # --- Sources
    add("")
    add("## Sources")
    add("")
    add("| Row | Floor page used | Older pages, not used | Pilots |")
    add("|---|---|---|---|")
    for gid, _, keys in GROUPS:
        for k in keys:
            cfg = info[k]["cfg"]
            cands = pages.get(cfg["slug"])
            if not cands:
                continue
            rel = lambda p: p.relative_to(REPO).as_posix()
            add("| %s | `%s` | %s | %s |" % (
                clean(cfg["name"]), rel(cands[-1][2]),
                ", ".join("`%s`" % rel(c[2]) for c in cands[:-1]) or "-", clean(info[k]["floor"]["pilots"])))
    add("")
    add("Also read: `decks/consistency_2026-09-25/ANCHORS.md` (prediction and A1 table) and the Ladder Log export "
        "(`logs` collection of %s)." % LOG_URL)
    add("")

    text = "\n".join(L)
    if args.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)
    else:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("wrote %s (%d games, %d-%d)" % (args.out, len(all_games), tw, tl))


if __name__ == "__main__":
    main()
