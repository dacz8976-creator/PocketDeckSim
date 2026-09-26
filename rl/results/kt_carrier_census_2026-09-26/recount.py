"""Independent recount of the kt carrier census (development half only).

Written from the data description alone, before reading scan_census.py or its
outputs.  Run from the repo root:

    python <scratch>/kt_census/recount.py

Reads:
  rl/results/limitless_skill_model_2026-09-25/split.json          (which events are development / holdout)
  rl/results/limitless_skill_model_2026-09-25/events.json         (name, date, players; development ids only used)
  rl/results/limitless_skill_model_2026-09-25/matches.csv         (development rows only: window top-30 and placing fallback)
  rl/results/limitless_skill_model_2026-09-25/raw/<dev id>_standings.json.gz   (NEVER a holdout id)
  decks/classifier/limitless_2026-09-10.json                      (Sept 10 top-30 names)
  rl/results/kt_carrier_census_2026-09-26/cards.json              (card ids for the census set)

Writes (scratch folder and the census results folder):
  recount_summary.json, recount_carrier_entries.csv
"""
import csv
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict

REPO = r"C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim"
SKILL = os.path.join(REPO, "rl", "results", "limitless_skill_model_2026-09-25")
CENSUS = os.path.join(REPO, "rl", "results", "kt_carrier_census_2026-09-26")
SCRATCH = os.path.dirname(os.path.abspath(__file__))

# The card set exactly as the task lists it (Ferrothorn appears twice: two printings).
TASK_CARDS = ["Jasmine", "Cheren", "Blue", "Beast Wall", "Adaman", "Heavy Helmet", "Steel Apron",
              "Metal Core Barrier", "Mr. Mime", "Drifloon", "Bronzong", "Probopass ex", "Cloyster",
              "Stakataka", "Skarmory ex", "Avalugg", "Swirlix", "Ferrothorn", "Porygon", "Shuckle",
              "Wigglytuff", "Frigibax", "Golem", "Pupitar", "Carbink", "Registeel", "Archaludon",
              "Cosmoem", "Corviknight", "Gouging Fire", "Mega Steelix ex", "Aegislash",
              "Cornerstone Mask Ogerpon", "Protective Poncho", "Rocky Helmet", "Turtonator",
              "Togedemaru", "Alolan Sandslash", "Mega Sableye ex", "Chesnaught", "Poliwrath",
              "Druddigon", "Pawmot", "Ferrothorn", "Zangoose", "Iron Jugulis"]

# The six archetypes the task says are certainly Dustin's (B2e held archetypes).
DUSTIN_CERTAIN = {
    "Mega Manectric ex Heliolisk": "B2e held archetype; decks/dustin/09-mega-manectric-heliolisk.txt",
    "Team Rocket's Raticate ex Alolan Ninetales ex": "B2e held archetype; decks/dustin/13-a-ninetales-raticate.txt",
    "Hoopa ex Mega Absol ex": "B2e held archetype; decks/dustin/04-absol-hoopa-darkrai.txt (and brew-07)",
    "Garchomp": "B2e held archetype; decks/dustin/08-garchomp-toolbox.txt",
    "Whimsicott ex Ariados": "B2e held archetype; decks/dustin/12-ariados-whimsicott-ogerpon.txt",
    "Mega Charizard Y ex Entei ex": "B2e held archetype (task says certainly his); brew-08 is Entei",
}
# Conservative mapping of the other files by main Pokemon (when in doubt, Dustin's).
DUSTIN_MAPPED = {
    "Mega Blaziken ex": "decks/dustin/06-mega-blaziken-tournament-list.txt is a Mega Blaziken ex deck (clear match)",
    "Mega Blaziken ex Greninja": "CONSERVATIVE: shares main Pokemon Mega Blaziken ex with decks/dustin/06 (no Greninja in his files)",
    "Team Rocket's Weezing ex Hoopa ex": "CONSERVATIVE: Hoopa ex is the main of decks/dustin/04 and brew-07; Team Rocket's Weezing ex is a 1-of in decks/dustin/10 and brew-04",
    "Hydreigon Mega Absol ex": "CONSERVATIVE: shares Mega Absol ex with the held archetype Hoopa ex Mega Absol ex (decks/dustin/04); no Hydreigon in his files",
    "Dedenne ex Indeedee ex": "CONSERVATIVE: Indeedee ex is a main of decks/dustin/05 (and in 03, 07); no Dedenne ex in his files",
    "Dragonair Mega Rayquaza ex": "CONSERVATIVE: Dragonair B4 117 is a named main of decks/dustin/11-archaludon-haxorus-dragonair.txt; no Mega Rayquaza ex in his files",
    "Mega Charizard X ex Mega Charizard Y ex": "CONSERVATIVE: shares Mega Charizard Y ex with the held archetype Mega Charizard Y ex Entei ex",
    "Mega Manectric ex Team Rocket's Electrode": "CONSERVATIVE: shares main Pokemon Mega Manectric ex with decks/dustin/09; no Team Rocket's Electrode in his files",
    # Window-only archetypes (not in the Sept 10 list). These four entries were added after the first
    # comparison with census_summary.json showed the map above only covered the Sept 10 names; the rule
    # is the same one applied above (any named main Pokemon in a Dustin file -> Dustin's).
    "Hoopa ex Mega Sableye ex": "decks/brews/brew-07-hoopa-darkrai-sableye.txt carries both Hoopa ex and Mega Sableye ex (clear match)",
    "Hoopa ex Greninja": "CONSERVATIVE: Hoopa ex is the main of decks/dustin/04 and brew-07; no Greninja in his files",
    "Zoroark ex Mega Absol ex": "CONSERVATIVE: shares Mega Absol ex with the held archetype Hoopa ex Mega Absol ex (decks/dustin/04); no Zoroark ex in his files",
    "Milotic ex Eevee ex": "CONSERVATIVE (thin): decks/dustin/15 carries Eevee B1 184, but the archetype names Eevee ex, a different card, and no Milotic ex is in his files; marked Dustin's only by the in-doubt rule; it carries none of the census cards, so the flag has no bearing on clause (d)",
}


def norm_name(s):
    if s is None:
        return None
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", s).strip()


def card_key(set_code, number):
    set_code = str(set_code).strip().upper()
    num = str(number).strip()
    try:
        return (set_code, int(num))
    except ValueError:
        return (set_code, num)


def parse_id(s):
    set_code, num = s.split()
    return card_key(set_code, num)


def build_card_set(cards_json):
    """name label -> {'names': set of printed names to match, 'ids': set of keys, 'group': str}"""
    g = cards_json["groups"]
    out = {}

    def add(label, name, ids, group):
        assert label not in out, label
        out[label] = {"name": name, "ids": {parse_id(i) for i in ids}, "id_strings": list(ids), "group": group}

    for e in g["group1_trainer_turn_effects"]:
        add(e["name"], e["name"], e["ids"], "group1_trainer_turn_effect")
    for e in g["group2_tool_reductions"]:
        add(e["name"], e["name"], e["ids"], "group2_tool_reduction")
    for e in g["group3_attack_self_reductions"]:
        add(e["name"], e["name"], e["ids"], "group3_attack_self_reduction")
    g4 = g["group4_considered"]
    for e in g4["tools_and_trainers"]:
        if e["name"] in ("Protective Poncho", "Rocky Helmet"):
            add(e["name"], e["name"], e["ids"], "group4_tool_switch2_or_3")
    for e in g4["counterattack_inputs"]["attacks"]:
        add(e["name"], e["name"], e["ids"], "group4_counterattack_attack")
    for e in g4["counterattack_inputs"]["abilities"]:
        label = e["name"]
        if label in out:  # Ferrothorn: second printing, an Ability, kept separate
            label = f"{e['name']} [{' / '.join(e['ids'])}]"
        add(label, e["name"], e["ids"], "group4_counterattack_ability")
    # check the task's list is fully covered
    names_in_set = Counter(v["name"] for v in out.values())
    task_counter = Counter(TASK_CARDS)
    for name, n in task_counter.items():
        assert names_in_set.get(name, 0) == n, (name, n, names_in_set.get(name))
    assert sum(names_in_set.values()) == len(TASK_CARDS), (sum(names_in_set.values()), len(TASK_CARDS))
    return out


def main():
    split = json.load(open(os.path.join(SKILL, "split.json"), encoding="utf-8"))
    dev_ids = list(split["development_event_ids"])
    holdout_ids = set(split["holdout_event_ids"])
    assert not (set(dev_ids) & holdout_ids)

    events_meta = {}
    for ev in json.load(open(os.path.join(SKILL, "events.json"), encoding="utf-8")):
        if ev["id"] in dev_ids:
            events_meta[ev["id"]] = {"name": ev["name"], "date": ev["date"][:10], "players": ev.get("players")}

    classifier = json.load(open(os.path.join(REPO, "decks", "classifier", "limitless_2026-09-10.json"), encoding="utf-8"))
    sept10 = [norm_name(row[0]) for row in classifier["top"]]
    sept10_rank = {n: i + 1 for i, n in enumerate(sept10)}
    sept10_counts = {norm_name(row[0]): row[1] for row in classifier["top"]}
    assert len(sept10) == 30

    cards_json = json.load(open(os.path.join(CENSUS, "cards.json"), encoding="utf-8"))
    card_set = build_card_set(cards_json)
    id_to_labels = defaultdict(list)
    for label, c in card_set.items():
        for k in c["ids"]:
            id_to_labels[k].append(label)
    name_to_labels = defaultdict(list)
    for label, c in card_set.items():
        name_to_labels[norm_name(c["name"])].append(label)

    # matches.csv: development rows only (holdout rows are never touched here)
    dev_match_deck_counts = Counter()
    dev_match_rows = 0
    holdout_rows_skipped = 0
    placing_fallback = {}
    with open(os.path.join(SKILL, "matches.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["split"] != "development":
                holdout_rows_skipped += 1
                continue
            assert r["event_id"] in dev_ids, r["event_id"]
            dev_match_rows += 1
            for side in ("1", "2"):
                dn = norm_name(r[f"deck{side}_name"])
                if dn:
                    dev_match_deck_counts[dn] += 1
                pl = r[f"player{side}_placing"]
                if pl:
                    placing_fallback[(r["event_id"], r[f"player{side}"])] = int(pl)
    window_top = dev_match_deck_counts.most_common()
    window_rank = {n: i + 1 for i, (n, _) in enumerate(window_top)}
    window_top30 = [n for n, _ in window_top[:30]]

    scan_set = set(sept10) | set(window_top30)

    # per-archetype accumulators
    arch = {n: {
        "name": n, "n_entries": 0, "n_lists": 0, "events_any": set(), "events_with_list": set(),
        "cards": Counter(), "copies": Counter(), "any_carrier_n": 0, "carriers": [],
        "name_only_matches": Counter(), "deck_ids": Counter(),
    } for n in scan_set}

    total_entries = 0
    total_with_decklist = 0
    events_scanned = 0
    unmatched_deck_names = Counter()
    for eid in dev_ids:
        assert eid not in holdout_ids
        path = os.path.join(SKILL, "raw", f"{eid}_standings.json.gz")
        with gzip.open(path, "rt", encoding="utf-8") as f:
            standings = json.load(f)
        events_scanned += 1
        meta = events_meta.get(eid, {})
        for e in standings:
            total_entries += 1
            dl = e.get("decklist")
            has_list = bool(dl) and bool(dl.get("pokemon") or dl.get("trainer"))
            if has_list:
                total_with_decklist += 1
            deck = e.get("deck") or {}
            dn = norm_name(deck.get("name"))
            if dn not in arch:
                if dn:
                    unmatched_deck_names[dn] += 1
                continue
            a = arch[dn]
            a["n_entries"] += 1
            a["events_any"].add(eid)
            a["deck_ids"][deck.get("id")] += 1
            if not has_list:
                continue
            a["n_lists"] += 1
            a["events_with_list"].add(eid)
            carried = {}
            for sec in ("pokemon", "trainer"):
                for item in dl.get(sec, []):
                    k = card_key(item.get("set"), item.get("number"))
                    iname = norm_name(item.get("name"))
                    labels = id_to_labels.get(k, [])
                    for label in labels:
                        carried[label] = carried.get(label, 0) + int(item.get("count") or 0)
                    if not labels and iname in name_to_labels:
                        # same printed name, a printing outside the census set (e.g. Cloyster A1 067)
                        a["name_only_matches"][f"{iname} {k[0]} {k[1]}"] += 1
            if carried:
                a["any_carrier_n"] += 1
                for label, n in carried.items():
                    a["cards"][label] += 1
                    a["copies"][label] += n
                placing = e.get("placing")
                if placing is None:
                    placing = placing_fallback.get((eid, e.get("player")))
                rec = e.get("record") or {}
                a["carriers"].append({
                    "player": e.get("player"), "display_name": e.get("name"), "event_id": eid,
                    "event_name": meta.get("name"), "event_size": meta.get("players") or len(standings),
                    "date": meta.get("date"), "placing": placing, "drop": e.get("drop"),
                    "record": f"{rec.get('wins')}-{rec.get('losses')}-{rec.get('ties')}",
                    "deck_id": deck.get("id"),
                    "cards_carried": [f"{label} x{n}" for label, n in sorted(carried.items())],
                    "url": f"https://play.limitlesstcg.com/tournament/{eid}/player/{e.get('player')}/decklist",
                })

    def sort_key(c):
        return (c["placing"] if c["placing"] is not None else 10 ** 6, -(c["event_size"] or 0), c["date"] or "", c["player"] or "")

    out_arch = []
    for n in sorted(arch, key=lambda x: (sept10_rank.get(x, 999), window_rank.get(x, 999))):
        a = arch[n]
        a["carriers"].sort(key=sort_key)
        if n in DUSTIN_CERTAIN:
            dustin, reason = True, DUSTIN_CERTAIN[n]
        elif n in DUSTIN_MAPPED:
            dustin, reason = True, DUSTIN_MAPPED[n]
        else:
            dustin, reason = False, "no main Pokemon of this archetype is a main Pokemon in decks/dustin/*.txt or decks/brews/*.txt"
        out_arch.append({
            "name": n,
            "rank_sept10": sept10_rank.get(n),
            "sept10_count": sept10_counts.get(n),
            "rank_window": window_rank.get(n),
            "window_dev_match_appearances": dev_match_deck_counts.get(n, 0),
            "in_sept10_top30": n in sept10_rank,
            "in_window_top30": n in window_top30,
            "dustin": dustin, "dustin_reason": reason,
            "n_entries": a["n_entries"], "n_lists": a["n_lists"],
            "n_events_any": len(a["events_any"]), "n_events": len(a["events_with_list"]),
            "deck_ids": dict(a["deck_ids"]),
            "carriers": [{"card": label, "n_lists": a["cards"][label], "copies_total": a["copies"][label]}
                         for label in sorted(a["cards"], key=lambda l: (-a["cards"][l], l))],
            "any_carrier_n": a["any_carrier_n"],
            "name_only_matches_other_printing": dict(a["name_only_matches"]),
            "carrier_entries": a["carriers"],
        })

    summary = {
        "title": "Independent recount of the kt carrier census (development half only)",
        "date": "2026-09-26",
        "method": {
            "events": "split.json development_event_ids; one standings.json.gz per event; holdout standings never opened",
            "matches_csv": "development rows only; holdout rows skipped (used for nothing)",
            "window_rank": "appearances of a deck name across development-half matches.csv rows (deck1_name + deck2_name, every row incl. byes/mirrors)",
            "list_rule": "entry counts as a list when decklist has a non-empty pokemon or trainer section",
            "card_match": "(set upper-cased, number as int) equality against cards.json ids; a same-name item with a printing outside the set is reported separately, not counted",
            "placing": "standings placing; when None (dropped) the matches.csv placing for that event+player is tried; still None means unplaced (sorted last)",
            "dustin_rule": "six B2e held archetypes certain; other files mapped by main Pokemon, conservative (in doubt -> Dustin's)",
        },
        "dev_events_scanned": events_scanned,
        "holdout_events_skipped": len(holdout_ids),
        "holdout_event_ids_never_read": sorted(holdout_ids),
        "dev_match_rows": dev_match_rows, "holdout_match_rows_skipped": holdout_rows_skipped,
        "standings_entries": total_entries, "entries_with_decklist": total_with_decklist,
        "card_set": {label: {"name": c["name"], "ids": c["id_strings"], "group": c["group"]} for label, c in card_set.items()},
        "sept10_top30": sept10,
        "window_top30": [{"rank": i + 1, "name": n, "dev_match_appearances": c, "rank_sept10": sept10_rank.get(n)}
                         for i, (n, c) in enumerate(window_top[:30])],
        "sept10_top30_missing_from_window_top30": [n for n in sept10 if n not in window_top30],
        "window_top30_missing_from_sept10": [n for n in window_top30 if n not in sept10_rank],
        "sept10_archetypes_with_no_decklists": [n for n in sept10 if arch[n]["n_lists"] == 0],
        "sept10_archetypes_with_no_entries": [n for n in sept10 if arch[n]["n_entries"] == 0],
        "unmatched_deck_names_top20": unmatched_deck_names.most_common(20),
        "archetypes": out_arch,
    }
    for target in (SCRATCH, CENSUS):
        with open(os.path.join(target, "recount_summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
        with open(os.path.join(target, "recount_carrier_entries.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["archetype", "rank_sept10", "rank_window", "dustin", "player", "display_name", "event_id",
                        "event_name", "event_size", "date", "placing", "drop", "record", "deck_id", "cards_carried", "url"])
            for a in out_arch:
                for c in a["carrier_entries"]:
                    w.writerow([a["name"], a["rank_sept10"], a["rank_window"], a["dustin"], c["player"], c["display_name"],
                                c["event_id"], c["event_name"], c["event_size"], c["date"], c["placing"], c["drop"],
                                c["record"], c["deck_id"], "; ".join(c["cards_carried"]), c["url"]])

    # console summary
    print(f"dev events scanned {events_scanned}; holdout skipped {len(holdout_ids)}; entries {total_entries}; with decklist {total_with_decklist}")
    print(f"dev match rows {dev_match_rows}; holdout rows skipped {holdout_rows_skipped}")
    print("card set labels:", len(card_set))
    print("\nWINDOW TOP 30 (dev-half match appearances) vs Sept 10 rank")
    for row in summary["window_top30"]:
        print(f"  {row['rank']:2d} {row['dev_match_appearances']:5d}  s10={str(row['rank_sept10']):>4}  {row['name']}")
    print("\nSept10 top30 missing from window top30:", summary["sept10_top30_missing_from_window_top30"])
    print("window top30 not in Sept10:", summary["window_top30_missing_from_sept10"])
    print("\nARCHETYPES (s10 rank, window rank, dustin, entries, lists, events(any/with list), any_carrier_n, cards)")
    for a in out_arch:
        cs = ", ".join(f"{c['card']}={c['n_lists']}" for c in a["carriers"])
        print(f"  s10={str(a['rank_sept10']):>4} w={str(a['rank_window']):>3} D={'Y' if a['dustin'] else 'n'} ent={a['n_entries']:4d} lists={a['n_lists']:4d} ev={a['n_events_any']}/{a['n_events']} any={a['any_carrier_n']:3d}  {a['name']}  [{cs}]")
        if a["name_only_matches_other_printing"]:
            print(f"        name-only (other printing): {a['name_only_matches_other_printing']}")
    print("\nSept10 archetypes with no decklists:", summary["sept10_archetypes_with_no_decklists"])
    print("Sept10 archetypes with no entries at all:", summary["sept10_archetypes_with_no_entries"])
    print("unmatched deck names (top 20):", unmatched_deck_names.most_common(20))


if __name__ == "__main__":
    main()
