"""The counter tool's checks at km's build (the km registration, section 4.1, identity 8a; step 3).

rows: the tool's per-game rows (`--rows-out`, run with `--no-counts`) against the table files, deal by deal, on the move
fingerprint, both decks (names, and files where the reference has them), the seed and the seats; every expected deal
present. Only those fields are read: a row carrying counts is an error, so no count of a gating deal is ever loaded.
  python3 tool_check.py rows <label> <rows.jsonl> <deals> table=<table ref.jsonl> [new_decks.tsv=<new17 ref.jsonl>]

trace: on diagnostic games (not table deals), the tool's offered and played counts for Arena of Antiquity and Training
Area against a recount from its own move trace (`--trace-out`): per game and seat, a turn is offered when the card is
among the watched legal moves at some decision of that turn, and played when the chosen move plays it. Every game must
agree; at least one game must play each card; that game's trace lines for the card are printed, to count by hand.
  python3 tool_check.py trace <label> <rows.jsonl> <trace.tsv>

Appends one line per check to identity/identity_check.txt (and the printed lines to tool_check.txt); exits 1 on any
difference."""
import json, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARDS = ("Arena of Antiquity", "Training Area")
mode, label = sys.argv[1], sys.argv[2]
report = []


def finish(ok, line):
    line = f"{label}: {line}; {'PASS' if ok else 'FAIL'}"
    (HERE / "identity").mkdir(exist_ok=True)
    with open(HERE / "identity" / "identity_check.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")
    with open(HERE / "tool_check.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(report + [line]) + "\n\n")
    print("\n".join(report + [line]))
    sys.exit(0 if ok else 1)


if mode == "rows":
    rows_path, deals = sys.argv[3], int(sys.argv[4])
    refs = dict(a.split("=", 1) for a in sys.argv[5:])
    rows = [json.loads(l) for l in open(rows_path, encoding="utf-8")]
    if any("counts" in r or "xspeed" in r for r in rows):
        finish(False, "rows carry counts (run the tool with --no-counts)")
    cells = {(r["source"], r["pairing"], r["a"], r["b"]) for r in rows}
    want = {(s, p, a, b, i) for s, p, a, b in cells for i in range(deals)}
    ref = {}
    for source, path in refs.items():
        for l in open(path, encoding="utf-8"):
            g = json.loads(l)
            if g["i"] < deals and any(c[0] == source and c[1] == g["pairing"] for c in cells):
                ref[(source, g["pairing"], g["a"], g["b"], g["i"])] = g
    got = {(r["source"], r["pairing"], r["a"], r["b"], r["i"]): r for r in rows}
    bad, missing = [], sorted(want - set(ref)) + sorted(want - set(got))
    for k in sorted(want & set(ref) & set(got)):
        r, g = got[k], ref[k]
        seats = [r["a"], r["b"]] if r["first_seat"] == 0 else [r["b"], r["a"]]
        same = (r["moves"] == g["moves"] and r["seed"] == g["seed"] and r["first_seat"] == g["first_seat"]
                and r["seat_decks"] == seats and all(r[f] == g[f] for f in ("a_file", "b_file") if f in g))
        if not same:
            bad.append(k)
    report.extend(f"  differs: {k}" for k in bad[:20])
    report.extend(f"  missing: {k}" for k in missing[:20])
    ok = not bad and not missing and len(got) == len(want)
    finish(ok, f"{len(want) - len(bad) - len(missing)} of {len(want)} deals equal on the move fingerprint, both decks, "
               f"seed and seats ({len(cells)} cells, i < {deals}; rows {len(rows)}; differing {len(bad)}, missing "
               f"{len(missing)}); no count read")

if mode == "trace":
    rows_path, trace_path = sys.argv[3], sys.argv[4]
    offered, played, lines = defaultdict(set), defaultdict(set), defaultdict(list)
    for l in open(trace_path, encoding="utf-8"):
        source, pairing, i, seat, turn, names, chosen = l.rstrip("\n").split("\t")
        game = (source, int(pairing), int(i), int(seat))
        for card in CARDS:
            if card in names.split("|"):
                offered[game + (card,)].add(int(turn))
            if chosen.startswith("Play {") and f'name: "{card}"' in chosen:
                played[game + (card,)].add(int(turn))
            if card in names.split("|") or f'name: "{card}"' in chosen:
                lines[game[:3] + (card,)].append(f"    seat {seat} turn {turn}: offered [{names}]; chose {chosen[:90]}")
    rows = [json.loads(l) for l in open(rows_path, encoding="utf-8")]
    bad, shown, played_games = [], set(), defaultdict(int)
    for r in rows:
        for seat in (0, 1):
            counts = r["counts"][seat]["cards"]
            for card in CARDS:
                k = (r["source"], r["pairing"], r["i"], seat, card)
                tool = (counts.get(card, {}).get("offered", 0), counts.get(card, {}).get("played", 0))
                hand = (len(offered[k]), len(played[k]))
                if tool != hand:
                    bad.append((k, tool, hand))
                if hand[1] > 0:
                    played_games[card] += 1
                    if card not in shown:
                        shown.add(card)
                        report.append(f"  {card}, {r['source']} pairing {r['pairing']} i {r['i']} (seed {r['seed']}), "
                                      f"seat {seat}: the tool says offered {tool[0]}, played {tool[1]}; the trace's lines:")
                        report.extend(x for x in lines[k[:3] + (card,)] if x.startswith(f"    seat {seat} "))
    report.extend(f"  differs: {k}: tool {t}, trace {h}" for k, t, h in bad[:20])
    ok = not bad and all(played_games[c] > 0 for c in CARDS) and len(rows) > 0
    finish(ok, f"{len(rows)} traced games, {2 * len(rows)} seats: the tool's offered and played turns for "
               f"{' and '.join(CARDS)} equal the trace's recount in {2 * len(rows) * len(CARDS) - len(bad)} of "
               f"{2 * len(rows) * len(CARDS)} seat-cards (differing {len(bad)}); games where each is played: "
               + ", ".join(f"{c} {played_games[c]}" for c in CARDS))
sys.exit(f"unknown mode {mode}")
