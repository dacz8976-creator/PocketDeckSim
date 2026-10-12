#!/usr/bin/env python3
"""Triage step 1: engine coverage of every card in the 14 lists and every opponent card seen in the 18 ledgers.
Reads (never writes) the Battle Logs batch and the repo; writes cov.json / cov_summary.txt next to this script."""
import glob, json, os, re, sys, unicodedata, collections

HERE = os.path.dirname(os.path.abspath(__file__))
B = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES"
R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("♀", "").replace("♂", "")
    return re.sub(r"\s+", " ", s).strip().lower()


def base_name(n):
    n = re.sub(r"\s*\(.*$", "", n or "").strip()   # "Mewtwo ex (dark art)" -> "Mewtwo ex"; "Mega Lucario ex (red/blue ...)" -> "Mega Lucario ex"
    return n


ACTION_KINDS = {"attack", "ability", "retreat", "energy_attachment", "end_turn", "attack_effect", "promotion", "concede", "forced_promotion",
                "opponent_attack", "opponent_ability", "inspection", "prompt_response", "stadium_activation", "stadium_ability", "stadium_effect",
                "retreat_attempt", "mandatory_promotion_choice", "replacement_selection", "tool_attachment_resolved"}


def clean_names(raw):
    """A ledger name such as 'Garchomp [Mach Stealth / Land Crush, 150 HP]', 'Gourgeist / Soul Shot', 'Copperajah: Heavy Impact' or
    'Rare Candy + Mega Gardevoir ex' -> the card names in it."""
    if isinstance(raw, dict):
        raw = raw.get("name")
    if not raw or norm(str(raw)) in ("none", "empty", "null"):
        return []
    out = []
    for part in re.split(r"\s\+\s", str(raw)):
        part = re.split(r"\s*[\[:/]\s*", part)[0]
        part = base_name(part)
        if part:
            out.append(part)
    return out


db = json.load(open(f"{R}/lib/deckgym-database.json", encoding="utf-8"))
cards = {}
by_name = collections.defaultdict(list)
for c in db:
    kind, v = next(iter(c.items()))
    v = dict(v); v["_kind"] = kind
    cards[v["id"]] = v
    by_name[norm(v["name"])].append(v["id"])
status = {c["id"]: c for c in json.load(open("/home/dacz8976/pgd/card_status.json", encoding="utf-8"))["cards"]}
print("database cards", len(cards), "| status entries", len(status), "| ids without status", len(set(cards) - set(status)))


def st(i):
    s = status.get(i)
    return (s["status"], s.get("limitations") or []) if s else ("NO STATUS", [])


# ------------------------------------------------------------------------------------------------ the 14 lists
nd = json.load(open(B + "/NEW_DECK_ENTRIES.json", encoding="utf-8"))
decks = []
for d in nd["decks"]:
    decks.append({"key": d["id"], "name": d["deck_name"], "label": d.get("filmed_deck_label"), "source": d["source_video"], "energy": d.get("energy_configuration"),
                  "cards": d["cards_in_display_order"]})
ed = json.load(open(B + "/EDITED_DECK_ENTRY.json", encoding="utf-8"))
print("EDITED keys:", list(ed.keys()))
e0 = ed["decks"][0] if isinstance(ed["decks"], list) else ed["decks"]
print("edited deck keys:", list(e0.keys()))
edeck = {"key": "edited-water", "name": e0.get("deck_name") or "Snorlax ex / Team Rocket's Persian / Silvally (Water revision)", "label": "edit of New deck 6 (game 2)",
         "source": "20261006_012927000_iOS.MP4 (game 2)", "energy": e0.get("energy_configuration") or ["Water"], "cards": e0.get("cards_in_display_order") or []}
decks.append(edeck)

out = {"decks": [], "opponent_cards": {}, "problems": []}
for d in decks:
    rows = []
    for c in d["cards"]:
        refs = c.get("semantic_variant_references") or []
        nm = c["name"]
        ids = refs or by_name.get(norm(base_name(nm)), [])
        entry = {"name": nm, "count": c.get("count"), "refs": ids, "printings": []}
        for i in ids:
            s, lim = st(i)
            cc = cards.get(i)
            entry["printings"].append({"id": i, "db_name": cc["name"] if cc else None, "status": s, "limitations": lim})
            if cc and norm(cc["name"]) != norm(base_name(nm)):
                out["problems"].append(f"{d['name']}: {nm} -> {i} is named {cc['name']}")
        if not ids:
            out["problems"].append(f"{d['name']}: no printing found for {nm}")
        rows.append(entry)
    out["decks"].append({"key": d["key"], "name": d["name"], "label": d["label"], "source": d["source"], "energy": d["energy"], "cards": rows})

# ------------------------------------------------------------------------------------------------ opponent cards in the ledgers
opp = collections.defaultdict(lambda: {"games": collections.Counter(), "how": set()})
own_seen = collections.defaultdict(lambda: collections.Counter())
for d in sorted(glob.glob(B + "/2026*_iOS")):
    gid = os.path.basename(d)[:15]
    for sub, tag in ((d, gid), (d + "/game_02", gid + "/g2")):
        p = sub + "/TURN_LEDGER.json"
        if not os.path.exists(p):
            continue
        L = json.load(open(p, encoding="utf-8"))
        for t in L["turns"]:
            for bk in ("board_at_start", "board_after"):
                bd = t.get(bk) or {}
                for side, who in (("opponent", opp), ("owner", None)):
                    s = (bd.get(side) or {})
                    mons = [s.get("active")] + list(s.get("bench_in_position_order") or [])
                    for m in mons:
                        if isinstance(m, dict) and m.get("name"):
                            for n in clean_names(m["name"]):
                                if who is not None:
                                    who[n]["games"][tag] += 1; who[n]["how"].add("board")
                                else:
                                    own_seen[tag][n] += 1
                stv = bd.get("stadium")
                for stn in clean_names(stv):
                    opp[stn]["games"][tag] += 1; opp[stn]["how"].add("stadium in play")
            for pl in (t.get("plays_in_order") or []):
                if pl.get("kind") in ACTION_KINDS:
                    continue
                for n in clean_names(pl.get("card_name")):
                    if t["who_played"] == "opponent":
                        opp[n]["games"][tag] += 1; opp[n]["how"].add("played " + str(pl.get("kind")))
                    else:
                        own_seen[tag][n] += 1
            for ds in (t.get("draws_and_searches") or []):
                for rv in (ds.get("cards_in_reveal_order") or []):
                    if t["who_played"] == "opponent":
                        for n in clean_names(rv.get("name")):
                            opp[n]["games"][tag] += 1; opp[n]["how"].add("revealed")

rows = {}
for n, v in sorted(opp.items()):
    stad = n.startswith("[stadium] ")
    nn = n[10:] if stad else n
    ids = by_name.get(norm(nn), [])
    rows[n] = {"games": dict(v["games"]), "how": sorted(v["how"]), "ids": ids,
               "statuses": sorted({st(i)[0] for i in ids}) if ids else ["NOT IN DATABASE"],
               "not_complete": [{"id": i, "status": st(i)[0], "limitations": st(i)[1]} for i in ids if st(i)[0] != "Complete"]}
out["opponent_cards"] = rows
out["own_seen"] = {g: dict(c) for g, c in own_seen.items()}
json.dump(out, open(HERE + "/cov.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

lines = []
lines.append(f"problems: {len(out['problems'])}")
lines += ["  " + p for p in out["problems"]]
tot = collections.Counter()
for d in out["decks"]:
    for c in d["cards"]:
        for p in c["printings"]:
            tot[p["status"]] += 1
lines.append(f"deck printings by status: {dict(tot)}")
for d in out["decks"]:
    bad = [(c["name"], p["id"], p["status"]) for c in d["cards"] for p in c["printings"] if p["status"] != "Complete"]
    lines.append(f"- {d['name']} ({d['label']}): {sum(c['count'] or 0 for c in d['cards'])} cards, not Complete: {bad or 'none'}")
lines.append("opponent names with a status other than Complete (or not in the database):")
for n, r in rows.items():
    if r["statuses"] != ["Complete"]:
        lines.append(f"  {n}: {r['statuses']} ids {r['ids']} games {list(r['games'])}")
lines.append(f"opponent names seen: {len(rows)}")
open(HERE + "/cov_summary.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
