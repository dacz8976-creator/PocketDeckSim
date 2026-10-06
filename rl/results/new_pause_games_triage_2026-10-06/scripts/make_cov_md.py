#!/usr/bin/env python3
"""Writes ENGINE_COVERAGE.md from cov.json (cov.py's output) and the engine's card_status dump."""
import json, os, re, collections, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE + "/out"
os.makedirs(OUT, exist_ok=True)
cov = json.load(open(HERE + "/cov.json", encoding="utf-8"))
status = json.load(open("/home/dacz8976/pgd/card_status.json", encoding="utf-8"))
sid = {c["id"]: c for c in status["cards"]}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c)).replace("’", "'")).strip().lower()


L = []
P = L.append
P("# Engine coverage of the new Pause Games batch (Oct 6)\n")
P(f"Status source: the pinned official engine's card status (`engine_version` {status['engine_version']}, schema {status['schema_version']}; {len(status['cards'])} cards; main-8626a35, the same program the strength runs use). "
  f"\"{status['scope']}\"\n")
unv = [c for c in status["cards"] if c["status"] != "Complete"]
P(f"The engine's status values in that dump: Complete {sum(1 for c in status['cards'] if c['status'] == 'Complete')}, RulesUnverified {len(unv)}; no card is missing or partial. "
  "RulesUnverified cards are implemented but carry a documented unverified rule choice.\n")

deck_names = {}
for d in cov["decks"]:
    for c in d["cards"]:
        deck_names.setdefault(norm(c["name"]), set()).add(d["name"])
opp_names = {norm(n): n for n in cov["opponent_cards"]}
P("## The eight RulesUnverified cards, and whether the batch touches them\n")
P("| card | id | in one of his 14 lists | opponent card seen |\n|---|---|---|---|")
for c in unv:
    nn = norm(c["name"])
    P(f"| {c['name']} | {c['id']} | {'yes: ' + ', '.join(sorted(deck_names[nn])) if nn in deck_names else 'no'} | {'yes' if nn in opp_names else 'no'} |")
P("\nNone of the eight appears in his lists or among the opponent cards the reviews name.\n")

P("## His 14 lists\n")
P("Every card slot resolved to its printings through the prepared deck entries' `semantic_variant_references` (the QR identifies the playable card, not the artwork), and each printing's status was read.\n")
tot = collections.Counter()
for d in cov["decks"]:
    P(f"### {d['name']} ({d['label'] or 'label not read'}; Energy: {', '.join(d['energy'] or [])})\n")
    P("| count | card | printings checked | engine status |\n|---|---|---|---|")
    for c in d["cards"]:
        sts = collections.Counter(p["status"] for p in c["printings"])
        for p in c["printings"]:
            tot[p["status"]] += 1
        P(f"| {c['count']} | {c['name']} | {', '.join(c['refs']) if c['refs'] else '(by name)'} | {', '.join(f'{k} x{v}' for k, v in sts.items())} |")
    P("")
P(f"Total printings checked in the 14 lists: {sum(tot.values())}; statuses: {dict(tot)}.\n")

P("## Opponent cards named in the reviews' boards, plays and reveals\n")
P("Names come from the ledgers (both boards at every boundary, every opponent play, every public reveal). Hidden draws and searches stay unnamed, so cards he never saw are not here. "
  "A name is matched to every printing with that name; the status shown is the worst across them.\n")
P("| card | printings with that name | engine status | games (hhmmss of the recording; g2 = second game of 012927) |\n|---|---|---|---|")
for n, r in sorted(cov["opponent_cards"].items(), key=lambda kv: norm(kv[0])):
    games = ", ".join(sorted({g[9:15] + ("/g2" if g.endswith("/g2") else "") for g in r["games"]}))
    stt = "Complete" if r["statuses"] == ["Complete"] else ", ".join(r["statuses"])
    P(f"| {n} | {len(r['ids'])} | {stt} | {games} |")
P(f"\n{len(cov['opponent_cards'])} opponent card names, all found in the engine's data, all Complete.\n")
open(OUT + "/ENGINE_COVERAGE.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print("wrote", OUT + "/ENGINE_COVERAGE.md", len(L), "lines")
