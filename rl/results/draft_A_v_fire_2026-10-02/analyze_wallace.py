#!/usr/bin/env python3
"""Draft A v the Fire list, the Wallace addendum: the per-game extraction and the results page. Registered in
ADDENDUM_WALLACE.md beside this file, before any game. Not a ranking, not a ladder forecast.

    python3 analyze_wallace.py extract --tmp DIR --seat 0|1 --seed SEED --num N --coverage FILE --out FILE [--smoke]
        One deckgym call of the Wallace version against the Fire list: analyze.py's own extraction and checks (the
        registered analyze.py, imported and unchanged), plus each Wallace the list played (ADDENDUM section 6.W).
    python3 analyze_wallace.py report [--dir DIR] [--main-dir DIR] [--allow-partial]
        Reads DIR/games/*.jsonl and DIR/coverage/wallace_coverage.json (the Wallace version) and MAIN-DIR/games/*.jsonl
        (draft A's and deck 13's recorded games, which must be the registered 2,000), and writes DIR/RESULTS.md.
        Refuses an incomplete or duplicated set of Wallace games unless --allow-partial (a test; the page says PARTIAL).
    python3 analyze_wallace.py --self-test

analyze.py is imported, never edited. Its extraction reads the list of a tag from its module-level LISTS and calls its
module-level game_extract; for the tag "wallace" this file adds the Wallace list to that table and wraps game_extract
to add the Wallace fields, in this process only. Every other definition is analyze.py's and the README's.
"""
import sys
sys.dont_write_bytecode = True      # no __pycache__ beside the registered files
import argparse, glob, json, os     # noqa: E402
from collections import Counter     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze as A                 # noqa: E402  the registered analyze.py (sha256 pinned by run_wallace.sh)
floor = A.floor

TAG = "wallace"
WALLACE_LIST = "decks/brews/drafts_2026-10-01/draft-A-wallace.txt"
OUT_DIR = os.path.join(HERE, "wallace")
WALLACE = "Wallace"
CHOOSE = "ChooseRandomEvolutionTarget"
LABEL = dict(A.LABEL, wallace="the Wallace version of draft A (1 Misty -> 1 Wallace)")
SHORT = {"wallace": "Wallace version", "draftA": "draft A", "deck13": "deck 13"}
EVOLVED, NOT_EVOLVED, NO_CHOICE, UNKNOWN = "evolved", "not evolved", "no target choice", "unknown"


# --- extraction (ADDENDUM section 6.W) -----------------------------------------------------------------------------------

def wallace_events(plies, seat, went_first):
    """Each Wallace the list in `seat` played: own turn, game turn, the target (name and spot), and what it became.
    The target is the spot chosen at the list's next decision (ChooseRandomEvolutionTarget). The result is read at the
    decision after that (any player's): the same Pokemon (same first card) under a new name = evolved into that name;
    under the same name = not evolved (the deck held nothing that evolves from it)."""
    out = []
    for k, p in enumerate(plies):
        if p["actor"] != seat:
            continue
        kind, v = floor.body(p["chosen_action"])
        if kind != "Play" or floor.card_fields(v["trainer_card"]).get("name") != WALLACE:
            continue
        t = p["state"]["turn_count"]
        ev = dict(own=A.own_turn(t, went_first), t=t, target=None, spot=None, became=None, result=None)
        nxt = plies[k + 1] if k + 1 < len(plies) else None
        if nxt is None or nxt["actor"] != seat or floor.body(nxt["chosen_action"])[0] != CHOOSE:
            ev["result"] = NO_CHOICE
            out.append(ev)
            continue
        idx = floor.body(nxt["chosen_action"])[1]["in_play_idx"]
        before = nxt["state"]["in_play_pokemon"][seat][idx]
        ev.update(target=A.slot_name(before), spot="Active" if idx == 0 else "Bench")
        later = plies[k + 2] if k + 2 < len(plies) else None
        after = later["state"]["in_play_pokemon"][seat][idx] if later else None
        if before is None or after is None or A.base_id(after) != A.base_id(before):
            ev["result"] = UNKNOWN
        elif A.slot_name(after) != A.slot_name(before):
            ev.update(result=EVOLVED, became=A.slot_name(after))
        else:
            ev["result"] = NOT_EVOLVED
        out.append(ev)
    return out


_GAME_EXTRACT = A.game_extract


def game_extract_wallace(result, plies, seat, flagged):
    """analyze.py's record of one game, plus its Wallace plays."""
    rec = _GAME_EXTRACT(result, plies, seat, flagged)
    rec["wallace"] = wallace_events(plies, seat, rec["went_first"])
    return rec


def extract(a):
    """analyze.py's extract, unchanged, for the tag "wallace": the same checks (result files, completion, seeds in the
    registered block unless --smoke, the lists in the seats, km3 on both sides, printed wins, one trace file per ply)."""
    A.LISTS = dict(A.LISTS, **{TAG: WALLACE_LIST})
    A.game_extract = game_extract_wallace
    a.tag = TAG
    A.extract(a)


# --- the page ------------------------------------------------------------------------------------------------------------

def load(d):
    recs = []
    for f in sorted(glob.glob(os.path.join(d, "games", "*.jsonl"))):
        recs += [json.loads(line) for line in open(f, encoding="utf-8") if line.strip()]
    return recs


def completeness(recs, tags):
    keys = Counter((r["tag"], r["seat"], r["seed"]) for r in recs)
    dup = sorted(k for k, c in keys.items() if c > 1)
    want = {(tag, s, A.SEED_BASE + A.PER_SEAT * s + i) for tag in tags for s in (0, 1) for i in range(A.PER_SEAT)}
    missing, extra = want - set(keys), set(keys) - want
    return (not dup and not missing and not extra), missing, extra, dup


def steps(r):
    """README section 6.5's steps (analyze.py's line_steps) plus ADDENDUM 6.W's: WP, W1, W2 and L1w."""
    s = A.line_steps(r)
    ws = r.get("wallace") or []
    w1 = any(e["own"] <= 1 and e["became"] == A.SHARPEDO for e in ws)
    w2 = any(e["own"] <= 2 and e["became"] == A.SHARPEDO for e in ws)
    s.update(WP=bool(ws), W1=w1, W2=w2, L1w=s["L1"] or w2)
    return s


def split(g):
    return [("all", g), ("went first", [r for r in g if r["went_first"] is True]),
            ("went second", [r for r in g if r["went_first"] is False])]


def share(c, n):
    return f"{c} = {A.pct(c / n)}" if n else "n/a"


def reading(lo, hi, other):
    if lo != lo:
        return "no reading (fewer than two paired deals)"
    if lo > 0:
        return (f"the Wallace version beat the Fire list more often than {other} did on the same deals, by more than "
                "the paired interval")
    if hi < 0:
        return (f"{other} beat the Fire list more often than the Wallace version did on the same deals, by more than "
                "the paired interval")
    return (f"no difference seen: the paired interval includes zero, so this test cannot tell the Wallace version from "
            f"{other} against the Fire list")


def t2_target(r):
    """Own turn 2's Turbo Shark: the arm's target, or why there was no arm (README 6.5; as analyze.py's page)."""
    s = [s_ for s_ in r["sharks"] if s_["own"] == 2]
    return (None if not s else f"armed: {s[0]['target']}" if s[0]["result"] == "armed"
            else f"not armed: {s[0]['result']}")


def report(a):
    d, md = os.path.abspath(a.dir), os.path.abspath(a.main_dir)
    main = load(md)
    ok, missing, extra, dup = completeness(main, ("draftA", "deck13"))
    if not ok:
        raise SystemExit(f"REFUSED: the recorded games in {md} are not the registered 2,000 ({len(missing)} missing, "
                         f"{len(extra)} outside, {len(dup)} duplicated)")
    recs = load(d)
    complete, missing, extra, dup = completeness(recs, (TAG,))
    if not complete and not a.allow_partial:
        raise SystemExit(f"REFUSED: {len(recs)} Wallace games; {len(missing)} registered deals missing, {len(extra)} "
                         f"outside the registered seeds or not the Wallace version, {len(dup)} duplicated. No page "
                         "(use --allow-partial only for a test).")
    by = {"draftA": [r for r in main if r["tag"] == "draftA"], "deck13": [r for r in main if r["tag"] == "deck13"],
          TAG: [r for r in recs if r["tag"] == TAG]}
    order = (TAG, "draftA", "deck13")
    idx = {tag: {(r["seat"], r["seed"]): r for r in by[tag]} for tag in order}
    st = {id(r): steps(r) for tag in order for r in by[tag]}
    w = by[TAG]
    L = ["# Draft A v the Fire list, the Wallace addendum: results", ""]
    if not complete:
        L += [f"**PARTIAL: {len(recs)} Wallace games, not the registered 1,000 ({len(missing)} registered deals missing, "
              f"{len(extra)} outside the registered seeds, {len(dup)} duplicated). A test page, not the result.**", ""]
    L += ["Written by `analyze_wallace.py report` from `wallace/games/*.jsonl`, `wallace/coverage/wallace_coverage.json` "
          "and the main test's recorded `games/*.jsonl` (draft A and deck 13, the same deals). Every definition is the "
          "README's (sections 6 and 7) or ADDENDUM_WALLACE.md's. **Not a ranking and not a ladder forecast**: one list "
          "against one saved opponent list, both sides played by the km3 bot.", ""]

    # the two paired differences and their readings (ADDENDUM section 7)
    pair = {}
    for other in ("draftA", "deck13"):
        deals = sorted(set(idx[TAG]) & set(idx[other]))
        diffs = [int(idx[TAG][k]["won"]) - int(idx[other][k]["won"]) for k in deals]
        pair[other] = (deals, diffs, A.paired(diffs))
    L.append("**Readings (ADDENDUM_WALLACE.md section 7):**")
    for other in ("draftA", "deck13"):
        deals, diffs, (m, lo, hi, sd) = pair[other]
        line = f"- Against {SHORT[other]}: {reading(lo, hi, SHORT[other])}."
        if lo == lo:
            line += (f" Paired difference, the Wallace version minus {SHORT[other]}: {100 * m:+.1f} points (95% interval "
                     f"{100 * lo:+.1f} to {100 * hi:+.1f}).")
            if abs(m) < 0.05:
                line += (" The point difference is under 5 points, the size START_HERE calls noise for two versions of "
                         "one shell (for scale only; the reading is the registered one).")
        L.append(line)
    if w:
        ww = sum(r["won"] for r in w)
        lw, hw = A.wilson(ww, len(w))
        side = "above" if lw > 0.5 else "below" if hw < 0.5 else "not distinguishable from"
        L += ["", f"Secondary, descriptive: the Wallace version's win rate against this list is {side} 50% "
              f"({A.pct(ww / len(w))}, {A.ci((lw, hw))})."]
        c = lambda tag, key: sum(st[id(r)][key] for r in by[tag])   # noqa: E731
        n = lambda tag: len(by[tag])                                  # noqa: E731
        L += ["", "Beside the readings (descriptive; the tables below):",
              f"- Wallace was played in {share(c(TAG, 'WP'), n(TAG))} of the Wallace version's games; a Wallace made "
              f"Mega Sharpedo ex by own turn 2 in {share(c(TAG, 'W2'), n(TAG))} (by own turn 1: {share(c(TAG, 'W1'), n(TAG))}).",
              f"- Mega Sharpedo ex in play by own turn 2, by an Evolve or Wallace (L1w): Wallace version "
              f"{share(c(TAG, 'L1w'), n(TAG))}; draft A {share(c('draftA', 'L1w'), n('draftA'))}.",
              f"- Turbo Shark as the attack of own turn 2 (L2): Wallace version {share(c(TAG, 'L2'), n(TAG))}; draft A "
              f"{share(c('draftA', 'L2'), n('draftA'))}. The plan's line: Wallace version {share(c(TAG, 'plan'), n(TAG))}; "
              f"draft A {share(c('draftA', 'plan'), n('draftA'))}."]

    # win rates
    L += ["", "## Win rates (draws are not wins)", "", "| list | games | wins | draws | win rate | 95% interval (Wilson) |",
          "|---|---|---|---|---|---|"]
    for tag in order:
        g = by[tag]
        wn, nn, dr = sum(r["won"] for r in g), len(g), sum(r["draw"] for r in g)
        L.append(f"| {LABEL[tag]} | {nn} | {wn} | {dr} | {A.pct(wn / nn) if nn else 'n/a'} | {A.ci(A.wilson(wn, nn))} |")
    L.append("")
    L.append("Draft A's and deck 13's rows are the main test's recorded games (its RESULTS.md), not new games.")

    # paired differences
    for other in ("draftA", "deck13"):
        deals, diffs, (m, lo, hi, sd) = pair[other]
        both = sum(1 for k in deals if idx[TAG][k]["won"] and idx[other][k]["won"])
        a_only, b_only = sum(1 for x in diffs if x == 1), sum(1 for x in diffs if x == -1)
        L += ["", f"## Paired difference: the Wallace version minus {SHORT[other]} (per deal: same seed, same seat)", "",
              f"- Deals played by both: {len(deals)}. Difference per deal = (the Wallace version won) - ({SHORT[other]} "
              "won), each 1 or 0.",
              (f"- Mean: {100 * m:+.2f} points; standard deviation of the per-deal differences {sd:.4f}; 95% interval "
               f"{100 * lo:+.2f} to {100 * hi:+.2f} points (mean +- 1.96 x sd / sqrt(n)).") if lo == lo else
              f"- Mean: {100 * m:+.2f} points; no interval (fewer than two deals)." if deals else "- No deals.",
              f"- Both won: {both}. The Wallace version won and {SHORT[other]} did not: {a_only}. {SHORT[other]} won and "
              f"the Wallace version did not: {b_only}. Neither won: {len(deals) - both - a_only - b_only}."]
        for s in (0, 1):
            ds = [int(idx[TAG][k]["won"]) - int(idx[other][k]["won"]) for k in deals if k[0] == s]
            if not ds:
                L.append(f"- Seat {s} only: no deals.")
                continue
            ms, ls, hs, _ = A.paired(ds)
            L.append(f"- Seat {s} only ({len(ds)} deals, descriptive): {100 * ms:+.1f} points" +
                     (f" ({100 * ls:+.1f} to {100 * hs:+.1f})" if ls == ls else "") + ".")
        differ = sum(1 for k in deals if idx[TAG][k]["went_first"] != idx[other][k]["went_first"])
        L.append(f"- Deals on which the two lists did not both go first or both go second: {differ} of {len(deals)}.")

    # went first / second, seat
    L += ["", "## Went first / went second, and seat", "",
          "| list | went first | went second | seat 0 | seat 1 |", "|---|---|---|---|---|"]
    for tag in order:
        cells = []
        for sel in (lambda r: r["went_first"] is True, lambda r: r["went_first"] is False,
                    lambda r: r["seat"] == 0, lambda r: r["seat"] == 1):
            h = [r for r in by[tag] if sel(r)]
            cells.append(A.rate(sum(r["won"] for r in h), len(h)))
        L.append(f"| {LABEL[tag]} | " + " | ".join(cells) + " |")
    L += ["", "Each cell: wins/games = win rate (95% Wilson interval)."]

    # Wallace's own counts
    L += ["", "## Wallace's own counts (ADDENDUM_WALLACE.md section 6.W)", ""]
    evs = [e for r in w for e in r.get("wallace") or []]
    groups = split(w)
    L += ["| | " + " | ".join(f"{lab} ({len(h)})" for lab, h in groups) + " |", "|---|---|---|---|"]
    for key, lab in (("WP", "games in which Wallace was played"),
                     ("W1", "W1: a Wallace on own turn 1 made Mega Sharpedo ex"),
                     ("W2", "W2: a Wallace on own turn 2 or earlier made Mega Sharpedo ex"),
                     ("L1", "L1 (README 6.5): an Evolve into Mega Sharpedo ex by own turn 2"),
                     ("L1w", "L1w: Mega Sharpedo ex by own turn 2, by an Evolve or Wallace (L1 or W2)")):
        L.append(f"| {lab} | " + " | ".join(share(sum(st[id(r)][key] for r in h), len(h)) for _, h in groups) + " |")
    da = split(by["draftA"])
    L.append("| draft A's L1 on the same deals (it has no Wallace, so its L1w = L1) | " +
             " | ".join(share(sum(st[id(r)]["L1"] for r in h), len(h)) for _, h in da) + " |")
    by_turn = Counter(A.col(e["own"]) for e in evs)
    tgt = Counter(f"{e['target']} ({e['spot']})" if e["target"] else "no target" for e in evs)
    res = Counter(e["result"] + (f" into {e['became']}" if e["became"] else "") for e in evs)
    multi = sum(1 for r in w if len(r.get("wallace") or []) > 1)
    L += ["", f"Wallaces played: {len(evs)} in {sum(1 for r in w if r.get('wallace'))} games ({multi} games with more "
          "than one). By own turn: " + ", ".join(f"turn {c}: {by_turn[c]}" for c in A.TURN_COLS) + ".",
          "By target (the Pokemon on the chosen spot): " + (", ".join(f"{k}: {c}" for k, c in tgt.most_common()) or "none")
          + ". By result: " + (", ".join(f"{k}: {c}" for k, c in res.most_common()) or "none") + ".",
          "A Wallace evolution is not an Evolve the list chose, so README 6.5's L1 and an arm's `evolved` do not count "
          "it; W1, W2 and L1w do."]
    wy = [r for r in w if st[id(r)]["W2"]]
    wn_ = [r for r in w if not st[id(r)]["W2"]]
    L.append(f"Win rate when a Wallace made Mega Sharpedo ex by own turn 2: {A.rate(sum(r['won'] for r in wy), len(wy))}; "
             f"otherwise: {A.rate(sum(r['won'] for r in wn_), len(wn_))}. Descriptive only, not cause and effect.")

    # Sharpedo's line, the Wallace version beside draft A
    L += ["", "## Sharpedo's line (README section 6.5): the Wallace version beside draft A, on the same deals", ""]
    cols = [(tag, lab, h) for tag in (TAG, "draftA") for lab, h in split(by[tag])]
    L += ["| step | " + " | ".join(f"{SHORT[tag]}, {lab} ({len(h)})" for tag, lab, h in cols) + " |",
          "|---|" + "---|" * len(cols)]
    for key, lab in (("L1", "Mega Sharpedo ex evolved by own turn 2 (an Evolve)"),
                     ("L1w", "Mega Sharpedo ex by own turn 2, by an Evolve or Wallace"),
                     ("L2", "Turbo Shark was the attack of own turn 2"),
                     ("L3", "that Turbo Shark armed a Benched Pokemon (any Water Pokemon)"),
                     ("L3v", "that Turbo Shark armed a Benched Alolan Vulpix"),
                     ("L4", "Alolan Ninetales ex evolved by own turn 3 (any Vulpix)"),
                     ("L4v", "that armed Alolan Vulpix evolved into Alolan Ninetales ex by own turn 3"),
                     ("L5", "own turn 3's attack was Binding Snow or Turbo Shark"),
                     ("line2", "the line through turn 2 (L2 and L3)"), ("line3", "the line through turn 3 (L2 to L5)"),
                     ("plan", "the plan's line (L2, L4v and L5)")):
        L.append(f"| {key}: {lab} | " + " | ".join(share(sum(st[id(r)][key] for r in h), len(h)) for _, _, h in cols) + " |")
    L.append("| games that reached own turn 2 / 3 | " + " | ".join(
        f"{sum(r['max_own_turn'] >= 2 for r in h)} / {sum(r['max_own_turn'] >= 3 for r in h)}" for _, _, h in cols) + " |")
    cnt = {(tag, lab): Counter(t2_target(r) for r in h) for tag, lab, h in cols}
    keys = sorted({k for c in cnt.values() for k in c if k},
                  key=lambda k: (not k.startswith("armed"), -sum(c[k] for c in cnt.values()), k))
    L += ["", "**Own turn 2's Turbo Shark, by where its Energy went** (games).", "",
          "| own turn 2 | " + " | ".join(f"{SHORT[tag]}, {lab} ({len(h)})" for tag, lab, h in cols) + " |",
          "|---|" + "---|" * len(cols)]
    for k in keys + [None]:
        L.append(f"| {k or 'no Turbo Shark on own turn 2'} | " + " | ".join(str(cnt[(tag, lab)][k]) for tag, lab, _ in cols) + " |")
    firsts = {}
    for tag, lab, h in cols:
        f_ = Counter()
        for r in h:
            ts = [s["own"] for s in r["sharks"]]
            f_["never" if not ts else (min(ts) if min(ts) <= 5 else "6+")] += 1
        firsts[(tag, lab)] = f_
    fc = [k for k in (1, 2, 3, 4, 5, "6+") if k != 1 or any(f_[1] for f_ in firsts.values())] + ["never"]
    L += ["", "**First Turbo Shark, by own turn** (games).", "",
          "| games | " + " | ".join(k if k == "never" else f"turn {k}" for k in fc) + " |", "|---|" + "---|" * len(fc)]
    for tag, lab, h in cols:
        L.append(f"| {SHORT[tag]}, {lab} ({len(h)}) | " + " | ".join(
            f"{firsts[(tag, lab)][k]}" + (f" ({A.pct(firsts[(tag, lab)][k] / len(h))})" if h else "") for k in fc) + " |")
    if w:
        yes = [r for r in w if st[id(r)]["line2"]]
        no = [r for r in w if not st[id(r)]["line2"]]
        L += ["", f"The Wallace version's win rate when the line through turn 2 happened: "
              f"{A.rate(sum(r['won'] for r in yes), len(yes))}; when it did not: {A.rate(sum(r['won'] for r in no), len(no))}. "
              "Descriptive only, not cause and effect."]
        sharks = [s for r in w for s in r["sharks"]]
        sres = Counter(s["result"] for s in sharks)
        arms = [e for r in w for e in r["arms"]]
        atg = Counter(e["target"] for e in arms)
        att = [e for e in arms if e["attacked"]]
        lost = [e for e in arms if not e["attacked"] and e["lost_track"]]
        left = [e for e in arms if not e["attacked"] and not e["lost_track"] and e["left_play"] is not None]
        how = Counter((e["attacked"][1], e["attacked"][2]) for e in att)
        L += ["", f"**The Wallace version's Turbo Sharks and the Bench-arming count.** Turbo Sharks: {len(sharks)} "
              f"({len(sharks) / len(w):.2f} a game; {sum(1 for r in w if r['sharks'])} games with at least one). Outcome "
              "of each: " + (", ".join(f"{k}: {c}" for k, c in sorted(sres.items())) or "none") + ".",
              f"Arms: {len(arms)} ({A.pct(len(arms) / len(sharks)) if sharks else 'n/a'} of Turbo Sharks). By target: " +
              (", ".join(f"{k}: {c}" for k, c in atg.most_common()) or "none") + ". The armed Pokemon later attacked "
              f"from the Active Spot in {len(att)} cases (first attack: " +
              (", ".join(f"{n_} {t_}: {c}" for (n_, t_), c in how.most_common()) or "none") +
              f"); left play first in {len(left)}; tracking lost in {len(lost)} (expected 0)."]

    # attacks by own turn
    L += ["", "## Attacks by own turn, attacker and attack (the Wallace version's own attacks)", ""]
    tab = {}
    for r in w:
        for ot, t, name, title in r["attacks"]:
            tab.setdefault((name, title), Counter())[A.col(ot)] += 1
    reach = Counter(c for r in w for c in A.TURN_COLS if r["max_own_turn"] >= (7 if c == "7+" else c))
    L += [f"{len(w)} games. Each cell: number of attacks (one at most per turn, so also games). Draft A's and deck 13's "
          "tables are in the main test's RESULTS.md.", "",
          "| attacker | attack | " + " | ".join(f"turn {c}" for c in A.TURN_COLS) + " | total |",
          "|---|---|" + "---|" * (len(A.TURN_COLS) + 1)]
    for (name, title), c in sorted(tab.items(), key=lambda x: -sum(x[1].values())):
        L.append(f"| {name} | {title} | " + " | ".join(str(c[k]) for k in A.TURN_COLS) + f" | {sum(c.values())} |")
    L.append("| games that reached this own turn | | " + " | ".join(str(reach[c]) for c in A.TURN_COLS) + " | |")

    # did the three attack at all
    L += ["", "## Did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all? (README section 6.7)", "",
          "| list | Pokemon | games in which it attacked at least once | its attacks, all games |", "|---|---|---|---|"]
    for tag in (TAG, "draftA"):
        g = by[tag]
        here = A.deck_names(WALLACE_LIST if tag == TAG else A.LISTS[tag])
        for name in A.THREE:
            if name not in here:
                L.append(f"| {LABEL[tag]} | {name} | not in the list | not in the list |")
                continue
            games, n_att = A.attacked_at_all(g, name)
            L.append(f"| {LABEL[tag]} | {name} | {games} of {len(g)}" + (f" ({A.pct(games / len(g))})" if g else "") +
                     f" | {n_att} |")

    # coverage flags
    L += ["", "## Coverage flags (official goldfish `--coverage`, read as floor.py reads them, pilot km3)", ""]
    cp = os.path.join(d, "coverage", "wallace_coverage.json")
    if not os.path.isfile(cp):
        L.append(f"- {LABEL[TAG]}: no coverage file ({os.path.relpath(cp, d)})")
    else:
        fl = floor.flagged_cards(json.load(open(cp, encoding="utf-8")), A.PILOT, floor.database())
        if not fl:
            L.append(f"- {LABEL[TAG]} (`{WALLACE_LIST}`): no flagged card.")
        else:
            L.append(f"- {LABEL[TAG]} (`{WALLACE_LIST}`): " + "; ".join(
                f"{n_} ({', '.join(sorted(c['ids']))}): {'; '.join(c['reasons'])}" for n_, c in sorted(fl.items())) + ".")
            if w:
                use = A.flagged_use(w, fl, WALLACE_LIST)
                L.append("  - In these games, as the floor counts them: " + "; ".join(
                    f"{n_} as {role}: used on {us} of {op} opportunities" + (f" ({A.pct(us / op)})" if op else "")
                    for n_, (op, us, role) in sorted(use.items())) + ".")
    L.append("- Draft A, deck 13 and the Fire list: the main test's RESULTS.md.")

    # checks
    lc = sum(1 for r in w if r.get("lifecycle_errors"))
    tm = sum(r["tracking_mismatches"] for r in w)
    two = sum(r["turns_with_two_attacks"] for r in w)
    smoke = sum(1 for r in w if r.get("smoke"))
    odd = sum(1 for e in evs if e["result"] in (NO_CHOICE, UNKNOWN))
    L += ["", "## For a second reader", "",
          f"- Wallace games read: {len(w)}; every game completed, its seed, lists and pilots checked against the "
          "registration, and the engine's printed wins checked against the result files, at extraction (analyze.py's "
          "checks; `wallace/run.log`). Recorded games read for the pairing: draft A "
          f"{len(by['draftA'])}, deck 13 {len(by['deck13'])} (the registered 2,000, checked).",
          f"- Wallace games with lifecycle errors: {lc}. Arm-tracking mismatches: {tm}. Own turns with two attacks: {two}. "
          f"Smoke records: {smoke}. Wallaces with no target choice or an unreadable result: {odd}. All five are "
          "expected to be 0.",
          "- Engine, programs and lists: sha256 in `wallace/provenance.txt` (written by run_wallace.sh before the first "
          "game).",
          "- Per-game records: `wallace/games/*.jsonl` (analyze.py's fields plus `wallace`: each Wallace played, "
          "[own turn, game turn, target, spot, result, became])."]
    out = os.path.join(d, "RESULTS.md")
    with open(out + ".part", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    os.replace(out + ".part", out)
    print(f"Written: {out}")


# --- self-test -----------------------------------------------------------------------------------------------------------

def _fake_game(choose=True, evolves=True):
    """A made-up game (not an engine game): the Wallace version in seat 0 goes second. On own turn 1 (game turn 2) it
    plays Wallace on its Active Carvanha, which becomes Mega Sharpedo ex (or, with evolves=False, stays Carvanha: no
    Mega Sharpedo ex left in the deck); Mega Sharpedo ex then uses Turbo Shark and arms the Benched Alolan Vulpix."""
    def mon(cid, name, stage=0):
        return {"Pokemon": {"id": cid, "name": name, "energy_type": "Water", "stage": stage}}
    carv, shark, vul = mon("B4 034", "Carvanha"), mon("B4 035", A.SHARPEDO, 1), mon("B2 028", A.VULPIX)
    wal = {"id": "B3b 068", "name": WALLACE, "trainer_card_type": "Supporter"}

    def slot(card, behind=()):
        return {"card": card, "cards_behind": list(behind)}

    def ply(t, cur, board, action, playable=None):
        return {"state": {"turn_count": t, "current_player": cur, "hands": [[], []], "points": [0, 0],
                          "in_play_pokemon": [board, [None] * 4]},
                "actor": cur, "chosen_action": {"action": action},
                "playable_actions": [{"action": x} for x in (playable or [action])]}
    b1 = [slot(carv), slot(vul), None, None]
    b2 = [slot(shark, [carv]), slot(vul), None, None] if evolves else b1
    arm = {"Attach": {"attachments": [[1, "Water", 1]], "is_turn_energy": False}}
    plies = [ply(1, 1, b1, "EndTurn"), ply(2, 0, b1, {"Play": {"trainer_card": wal}})]
    if choose:
        plies.append(ply(2, 0, b1, {CHOOSE: {"in_play_idx": 0, "energy_type": "Water"}}))
    plies.append(ply(2, 0, b2, {"Attach": {"attachments": [[1, "Water", 0]], "is_turn_energy": True}}))
    if evolves:
        plies += [ply(2, 0, b2, {"Attack": {"title": A.TURBO}}), ply(2, 0, b2, arm, [arm])]
    else:
        plies.append(ply(2, 0, b2, "EndTurn"))
    plies.append(ply(3, 1, b2, "EndTurn"))
    result = {"randomness": {"game_seed": 2}, "game_id": "fake-wallace", "outcome": {"Win": 0}, "final_points": [2, 0],
              "final_turn": 3, "plies": len(plies)}
    return game_extract_wallace(result, plies, 0, {})


def self_test():
    g = _fake_game()
    assert g["went_first"] is False and g["max_own_turn"] == 1 and g["tracking_mismatches"] == 0, g
    assert g["wallace"] == [dict(own=1, t=2, target="Carvanha", spot="Active", became=A.SHARPEDO, result=EVOLVED)], g
    assert g["sharks"][0]["own"] == 1 and g["sharks"][0]["result"] == "armed" and g["sharks"][0]["target"] == A.VULPIX
    s = steps(g)
    assert s["WP"] and s["W1"] and s["W2"] and s["L1w"] and not s["L1"] and not s["L2"], s
    g2 = _fake_game(evolves=False)
    assert g2["wallace"] == [dict(own=1, t=2, target="Carvanha", spot="Active", became=None, result=NOT_EVOLVED)], g2
    s = steps(g2)
    assert s["WP"] and not (s["W1"] or s["W2"] or s["L1w"]), s
    g3 = _fake_game(choose=False)
    assert [e["result"] for e in g3["wallace"]] == [NO_CHOICE], g3["wallace"]
    s = steps({"evolves": [], "attacks": [], "sharks": [], "arms": []})        # a record without Wallace (draft A's)
    assert not (s["WP"] or s["W2"] or s["L1w"]), s
    mine, draft = Counter(A.deck_ids(WALLACE_LIST)), Counter(A.deck_ids(A.LISTS["draftA"]))
    assert sum(mine.values()) == 20 and mine - draft == Counter({"B3b 068": 1}) and draft - mine == Counter({"A1 220": 1})
    assert WALLACE in A.deck_names(WALLACE_LIST) and set(A.THREE) <= A.deck_names(WALLACE_LIST)
    print("self-test (Wallace) passed: a made-up game's Wallace on own turn 1 (evolved, not evolved, no target choice); "
          "W1, W2, L1w beside L1 and L2; the list is draft A with one Misty (A1 220) replaced by one Wallace (B3b 068)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", nargs="?", choices=("extract", "report"))
    ap.add_argument("--tmp")
    ap.add_argument("--seat", type=int)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--num", type=int)
    ap.add_argument("--coverage")
    ap.add_argument("--out")
    ap.add_argument("--smoke", action="store_true", help="extract only: seeds outside the registered range (a test)")
    ap.add_argument("--dir", default=OUT_DIR)
    ap.add_argument("--main-dir", default=HERE)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    A.self_test()
    self_test()
    if a.self_test:
        return
    if a.mode == "extract":
        if None in (a.tmp, a.seat, a.seed, a.num, a.coverage, a.out):
            raise SystemExit("extract needs --tmp --seat --seed --num --coverage --out")
        extract(a)
    elif a.mode == "report":
        report(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
