"""Carrier lists for the rules switch (PLAN.md step 3, main 0a68b0a): one development list per carrier archetype from the
committed Limitless archive, by decklist_sources.json's rule, copied from limitless_skill_model_2026-09-25/analyze.py
(the "Most common exact list among top-eight finishers" block): development events only; entries with final placing
1-8; the decklist's cards as an exact multiset of (set, zero-padded number) that must total 20; the most frequent
multiset wins, ties by best placing, largest event, earliest date, player id, then the multiset. The only change is
the key: the Limitless deck id itself, not the archive's archetype mapping (these archetypes are not in it).
Where the rule finds no list, the same rule without the placing filter ("any placing", a final placing of None
sorting last) is reported beside it as an alternate. It is not the rule.
The archive's decklists carry no Energy line. Each file gets one, chosen from the attack costs of its Pokemon (ENERGY
below, as the B2e lists added theirs); the card lines are the source's exactly (cards_sha256 is theirs alone).
Usage: python3 select_carriers.py   (writes <key>.txt or alternates/<key>.txt, and selection.json)"""
import collections, gzip, hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[3] / "rl" / "results" / "limitless_skill_model_2026-09-25"
CARRIERS = {  # key -> (Limitless deck ids, what the plan wants it for)
    "garchomp_meowth": (["garchomp-b4a-meowth-b2"], "Meowth (Carefree Steps)"),
    "togekiss_meowth": (["togekiss-a4-meowth-b2"], "Togekiss A4 080 (Celestial Blessing) and Meowth"),
    "hisuian_goodra": (None, "Hisuian Goodra (Securely Sheltered: the (a) finite cut)"),  # the most-played id, below
    "houndoom_victini": (["mega-houndoom-ex-p-b-victini-b3"], "Victini (Victory Star): repair A"),
}
ENERGY = {  # key -> (Energy line, why)
    "garchomp_meowth": ("Water, Fighting", "Garchomp B4a 054 [WFC] Land Crush and Gabite B4a 053 [WF]; as Dustin's deck 08"),
    "togekiss_meowth": ("Psychic", "Togekiss A4 080 [PCC], Togetic A2 064 [P], Comfey A3 080 [PC]"),
    "hisuian_goodra": ("Water, Metal", "Hisuian Goodra B3b 050 [WMC] Heavy Impact, the attacker"),
    "houndoom_victini": ("Fire", "Mega Houndoom ex P-B 080 [RRC], Houndour A2a 011 [R], Victini B3 025 [RC]"),
}

events = json.loads((ARCHIVE / "events.json").read_text())
split = json.loads((ARCHIVE / "split.json").read_text())
dev = [e for e in events if e["split"] == "development"]
assert {e["id"] for e in dev} == set(split["development_event_ids"])
standings = {e["id"]: json.loads(gzip.decompress((ARCHIVE / "raw" / f"{e['id']}_standings.json.gz").read_bytes()))
             for e in dev}

# The most-played Hisuian Goodra deck id in the development events (every entry, any placing).
goodra = collections.Counter((pl.get("deck") or {}).get("id") for e in dev for pl in standings[e["id"]]
                             if "hisuian-goodra" in ((pl.get("deck") or {}).get("id") or ""))
top = max(goodra.values())
CARRIERS["hisuian_goodra"] = (sorted(k for k, v in goodra.items() if v == top), CARRIERS["hisuian_goodra"][1])


def entries(deck_ids, top8):
    """{multiset: [entry]} for the deck ids, as analyze.py builds its candidates."""
    out, invalid = collections.defaultdict(list), []
    for e in dev:
        for pl in standings[e["id"]]:
            if (pl.get("deck") or {}).get("id") not in deck_ids:
                continue
            if top8 and (pl.get("placing") is None or pl["placing"] > 8 or pl["placing"] < 1):
                continue
            cards = [(c["set"], str(c["number"]).zfill(3), int(c["count"]), c.get("name", ""))
                     for section, values in (pl.get("decklist") or {}).items() if isinstance(values, list)
                     for c in values if isinstance(c, dict) and all(k in c for k in ("count", "set", "number"))]
            combined = collections.Counter()
            for s, n, c, _ in cards:
                combined[s, n] += c
            sig = tuple(sorted((s, n, c) for (s, n), c in combined.items()))
            if sum(c for _, _, c in sig) != 20:
                invalid.append({"event_id": e["id"], "player": pl["player"], "cards": sum(c for _, _, c in sig)})
                continue
            rec = pl.get("record") or {}
            out[sig].append({"event_id": e["id"], "date": e["date"], "event_name": e["name"], "players": e["players"],
                             "player": pl["player"], "player_name": pl.get("name"), "country": pl.get("country"),
                             "placing": pl.get("placing"), "record": f"{rec.get('wins')}-{rec.get('losses')}-{rec.get('ties')}",
                             "drop": pl.get("drop"), "deck_id": pl["deck"]["id"], "deck_name": pl["deck"].get("name"),
                             "decklist_url": f"https://play.limitlesstcg.com/tournament/{e['id']}/player/{pl['player']}/decklist",
                             "raw_source": f"rl/results/limitless_skill_model_2026-09-25/raw/{e['id']}_standings.json.gz",
                             "card_names": [{"set": s, "number": n, "count": c, "name": na} for s, n, c, na in cards]})
    return out, invalid


def best(es):
    return min(es, key=lambda x: (x["placing"] if x["placing"] is not None else 10**9, -x["players"], x["date"], x["player"]))


def pick(cands):
    return min(cands.items(), key=lambda kv: (-len(kv[1]), (best(kv[1])["placing"] or 10**9), -best(kv[1])["players"],
                                              best(kv[1])["date"], best(kv[1])["player"], kv[0]))


selection = {"rule": "decklist_sources.json's: most frequent exact 20-card multiset among final placing 1-8 in the "
                     "development events; ties by best placing, largest event, earliest date, player id, multiset. "
                     "Keyed here by the Limitless deck id.",
             "alternate_rule": "The same without the placing filter (any final placing; None sorts last). Not the rule.",
             "hisuian_goodra_ids_by_development_entries": dict(goodra.most_common()), "carriers": {}}
for key, (ids, purpose) in CARRIERS.items():
    rec = {"deck_ids": ids, "purpose": purpose}
    all_entries, _ = entries(ids, top8=False)
    rec["development_entries_any_placing"] = sum(len(v) for v in all_entries.values())
    rec["development_placings"] = sorted((x["placing"] for v in all_entries.values() for x in v), key=lambda p: (p is None, p))
    for mode, top8 in (("rule", True), ("alternate", False)):
        cands, invalid = entries(ids, top8)
        if not cands:
            rec[mode] = {"status": "no list: no " + ("top-8 " if top8 else "") + "development entry with a valid 20-card list"}
            continue
        sig, es = pick(cands)
        path = HERE / (f"{key}.txt" if mode == "rule" else f"alternates/{key}.txt")
        path.parent.mkdir(exist_ok=True)
        text = "".join(f"{c} {s} {n}\n" for s, n, c in sig)
        path.write_text(f"Energy: {ENERGY[key][0]}\n" + text)
        rec[mode] = {"status": "saved", "file": str(path.relative_to(HERE)), "cards_sha256": hashlib.sha256(text.encode()).hexdigest(),
                     "energy_line": ENERGY[key][0], "energy_line_from": ENERGY[key][1],
                     "frequency": len(es), "eligible_entries": sum(len(v) for v in cands.values()),
                     "distinct_exact_lists": len(cands), "invalid_lists": invalid, "representative": best(es),
                     "matching_entries": [{k: v for k, v in x.items() if k != "card_names"} for x in es]}
        if mode == "rule":
            break                       # the alternate is only for carriers the rule can't supply
    selection["carriers"][key] = rec
(HERE / "selection.json").write_text(json.dumps(selection, indent=1, ensure_ascii=False) + "\n")
for key, rec in selection["carriers"].items():
    got = rec.get("rule", {}).get("status") == "saved"
    r = rec["rule"]["representative"] if got else rec.get("alternate", {}).get("representative")
    print(f"{key}: ids {rec['deck_ids']}, development entries {rec['development_entries_any_placing']} "
          f"(placings {rec['development_placings']}); rule: {rec['rule']['status'][:60]}"
          + (f"; alternate: {r['player']} {r['placing']} of {r['players']} {r['date'][:10]}" if not got and r else
             f"; {r['player']} {r['placing']} of {r['players']} {r['date'][:10]}" if r else ""))
