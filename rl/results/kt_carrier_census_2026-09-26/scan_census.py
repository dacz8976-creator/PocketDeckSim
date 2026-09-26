#!/usr/bin/env python3
"""kt carrier census, scan phase (2026-09-26).

Reads the DEVELOPMENT-HALF standings only (split.json) and counts, for every
top-30 archetype, how many decklists carry each card in the kt card set
(cards.json in this folder).  Reports; decides nothing.

Holdout discipline: the holdout event ids are listed and their standings and
details files are never opened.  matches.csv is used only for development-half
rows (window top-30 by match count).

Outputs (all in this folder):
  census.csv           one row per archetype x card, plus an ANY row per archetype
  census_summary.json  counts, ranks, Dustin mapping, provenance notes
  carrier_entries.csv  every development list that carries at least one card

Run from the repo root with Windows python:
  python rl/results/kt_carrier_census_2026-09-26/scan_census.py
"""
import csv
import glob
import gzip
import io
import json
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LSM = os.path.join(ROOT, "rl", "results", "limitless_skill_model_2026-09-25")
RAW = os.path.join(LSM, "raw")
SPLIT = os.path.join(LSM, "split.json")
MATCHES = os.path.join(LSM, "matches.csv")
TOP30_FILE = os.path.join(ROOT, "decks", "classifier", "limitless_2026-09-10.json")
CARDS_FILE = os.path.join(HERE, "cards.json")
DB_FILE = os.path.join(ROOT, "lib", "deckgym-database.json")
DUSTIN_GLOBS = [os.path.join(ROOT, "decks", "dustin", "*.txt"),
                os.path.join(ROOT, "decks", "brews", "*.txt")]

# The card set named in the task, in the task's order.  Ferrothorn is listed
# twice on purpose: B1 167 (Guard Press, group 3) and A3a 052 (Steel Spikes,
# a counterattack ability).  They are separate entries in cards.json.
TASK_CARDS = ["Jasmine", "Cheren", "Blue", "Beast Wall", "Adaman", "Heavy Helmet",
              "Steel Apron", "Metal Core Barrier", "Mr. Mime", "Drifloon", "Bronzong",
              "Probopass ex", "Cloyster", "Stakataka", "Skarmory ex", "Avalugg", "Swirlix",
              "Ferrothorn", "Porygon", "Shuckle", "Wigglytuff", "Frigibax", "Golem", "Pupitar",
              "Carbink", "Registeel", "Archaludon", "Cosmoem", "Corviknight", "Gouging Fire",
              "Mega Steelix ex", "Aegislash", "Cornerstone Mask Ogerpon", "Protective Poncho",
              "Rocky Helmet", "Turtonator", "Togedemaru", "Alolan Sandslash", "Mega Sableye ex",
              "Chesnaught", "Poliwrath", "Druddigon", "Pawmot", "Ferrothorn", "Zangoose",
              "Iron Jugulis"]

# The six archetypes the task says are certainly Dustin's (B2e).
B2E_DUSTIN = ["Mega Manectric ex Heliolisk",
              "Team Rocket's Raticate ex Alolan Ninetales ex",
              "Hoopa ex Mega Absol ex",
              "Garchomp",
              "Whimsicott ex Ariados",
              "Mega Charizard Y ex Entei ex"]


def norm_id(set_code, number):
    """'P-A', '7' -> 'P-A 007' (the cards.json form)."""
    s = str(set_code).strip()
    n = str(number).strip()
    try:
        n = "%03d" % int(n)
    except ValueError:
        pass
    return "%s %s" % (s, n)


# ---------------------------------------------------------------- card set
def collect_card_entries(node, out):
    """Walk cards.json and collect every dict that has 'name' and 'ids'."""
    if isinstance(node, dict):
        if "name" in node and "ids" in node and isinstance(node["ids"], list):
            out.append(node)
        for v in node.values():
            collect_card_entries(v, out)
    elif isinstance(node, list):
        for v in node:
            collect_card_entries(v, out)


def load_card_set():
    with open(CARDS_FILE, encoding="utf-8") as f:
        cards_json = json.load(f)
    switch1_kinds = set(cards_json.get("switch1_relevant_kinds") or
                        ["trainer_turn_effect", "tool_reduction", "attack_self_reduction"])
    entries = []
    collect_card_entries(cards_json, entries)
    by_name = defaultdict(list)
    for e in entries:
        by_name[e["name"]].append(e)
    wanted = Counter(TASK_CARDS)
    cards = []  # list of dicts: label, name, ids, kind, group_note
    for name, want_n in wanted.items():
        found = by_name.get(name, [])
        if len(found) != want_n:
            raise SystemExit("cards.json has %d entries named %r, task lists it %d time(s)"
                             % (len(found), name, want_n))
        for e in found:
            label = name
            if want_n > 1:
                what = e.get("attack") or e.get("ability") or ""
                label = "%s (%s %s)" % (name, e["ids"][0], what)
            kind = e.get("kind", "")
            cards.append({"label": label, "name": name, "ids": list(e["ids"]),
                          "kind": kind, "subtype": e.get("subtype", ""),
                          "switch1": kind in switch1_kinds,
                          "attack_or_ability": e.get("attack") or e.get("ability") or ""})
    # keep the task order
    order = {}
    for i, n in enumerate(TASK_CARDS):
        order.setdefault(n, i)
    cards.sort(key=lambda c: (order[c["name"]], c["ids"][0]))
    id_to_labels = defaultdict(list)
    for c in cards:
        for cid in c["ids"]:
            id_to_labels[cid].append(c["label"])
    name_to_labels = defaultdict(list)
    for c in cards:
        name_to_labels[c["name"].casefold()].append(c["label"])
    return cards, id_to_labels, name_to_labels


# ---------------------------------------------------------------- Dustin mapping
def load_db_kinds():
    """id -> ('Pokemon'|'Trainer'..., name) from lib/deckgym-database.json,
    plus the set of every Pokemon card name (for splitting archetype names)."""
    with open(DB_FILE, encoding="utf-8") as f:
        db = json.load(f)
    kinds = {}
    pokemon_names = set()
    for entry in db:
        kind, v = next(iter(entry.items()))
        kinds[v["id"]] = (kind, v["name"])
        if kind == "Pokemon":
            pokemon_names.add(v["name"])
    return kinds, pokemon_names


LINE_RE = re.compile(r"^\s*(\d+)\s+(.+?)\s+([A-Z][A-Za-z0-9\-]*)\s+(\d{3})\s*$")


def species_word(name):
    """'Team Rocket's Weezing ex' -> 'weezing'; 'Alolan Ninetales ex' -> 'ninetales'."""
    words = [w for w in re.split(r"[\s:]+", name) if w]
    words = [w for w in words if w.lower() not in ("ex", "mega", "alolan", "galarian", "hisuian",
                                                    "paldean", "team", "rocket's", "teal", "mask",
                                                    "cornerstone", "wellspring", "hearthflame",
                                                    "sunny", "form", "type:")]
    return (words[-1] if words else name).lower()


def load_dustin_pokemon(db_kinds):
    """Return (list of (pokemon_name, file, is_main), files, {file: set(pokemon names)}).
    is_main: the file's name (e.g. 03-wailord-indeedee-wall.txt) names that species."""
    out = []
    by_file = defaultdict(set)
    files = []
    for g in DUSTIN_GLOBS:
        files.extend(sorted(glob.glob(g)))
    for path in files:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        slug = os.path.basename(path).lower()
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = LINE_RE.match(line)
                if not m:
                    continue
                cnt, name, set_code, num = m.groups()
                cid = "%s %s" % (set_code, num)
                kind, _ = db_kinds.get(cid, ("?", name))
                if kind != "Pokemon":
                    continue
                is_main = species_word(name) in slug
                out.append((name, rel, is_main))
                by_file[rel].add(name)
    return out, [os.path.relpath(p, ROOT).replace("\\", "/") for p in files], by_file


def word_in(name, text):
    return re.search(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text, re.I) is not None


def split_archetype_pokemon(name, pokemon_names):
    """Split a Limitless archetype name into Pokemon card names by greedy longest match
    against the deckgym database's Pokemon names (e.g. 'Butterfree Mega Sceptile ex' ->
    ['Butterfree', 'Mega Sceptile ex']).  Unmatched tokens are kept as single-word parts."""
    toks = name.split(" ")
    parts = []
    i = 0
    while i < len(toks):
        best = None
        for k in range(min(5, len(toks) - i), 0, -1):
            cand = " ".join(toks[i:i + k])
            if cand in pokemon_names:
                best = (k, cand)
                break
        if best is None:
            parts.append(toks[i]); i += 1
        else:
            parts.append(best[1]); i += best[0]
    return parts


B2E_POKEMON = None  # filled in main: Pokemon names that appear in the six B2e archetype names


def dustin_verdict(archetype, dustin_pokemon, by_file, pokemon_names):
    """Return (dustin, level, reason).
    level: 'b2e'                 one of the six B2e archetypes (certainly Dustin's)
           'all_in_one_file'     every Pokemon in the archetype name is a Pokemon card in ONE
                                 Dustin file (treated as Dustin's)
           'shares_pokemon'      at least one Pokemon in the archetype name is in some Dustin
                                 file or in a B2e archetype name (conservative: Dustin's)
           'none'                no shared Pokemon (not Dustin's)
    dustin = level != 'none'."""
    if archetype in B2E_DUSTIN:
        return True, "b2e", "one of the six B2e archetypes the task names as certainly Dustin's"
    parts = split_archetype_pokemon(archetype, pokemon_names)
    # all parts in one file?
    for rel, names in sorted(by_file.items()):
        if all(p in names for p in parts):
            return True, "all_in_one_file", ("every Pokemon in the archetype name (%s) is in %s"
                                             % (", ".join(parts), rel))
    hits = []
    seen = set()
    for pname, rel, is_main in dustin_pokemon:
        if pname in parts or word_in(pname, archetype):
            key = (pname, rel)
            if key in seen:
                continue
            seen.add(key)
            hits.append("%s in %s%s" % (pname, rel, " (named in the file name)" if is_main else ""))
    for p in parts:
        if p in B2E_POKEMON:
            hits.append("%s is in the B2e archetype %s" % (p, B2E_POKEMON[p]))
    if hits:
        return True, "shares_pokemon", ("conservative: shares a Pokemon with a Dustin file or a "
                                        "B2e archetype: " + "; ".join(hits))
    return False, "none", ("no Pokemon in the archetype name (%s) appears in any decks/dustin or "
                           "decks/brews file or B2e archetype" % ", ".join(parts))


# ---------------------------------------------------------------- window top-30
def window_top_by_dev_matches():
    csv.field_size_limit(10 ** 9)
    counts = Counter()
    ids_by_name = defaultdict(Counter)
    n_rows = 0
    n_dev_rows = 0
    with open(MATCHES, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n_rows += 1
            if row["split"] != "development":
                continue  # holdout rows are not used in the scan phase
            n_dev_rows += 1
            if row["result_status"] not in ("decisive", "tie"):
                continue
            for k in ("1", "2"):
                nm = row["deck%s_name" % k]
                if nm:
                    counts[nm] += 1
                    ids_by_name[nm][row["deck%s_id" % k]] += 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    rank = {nm: i + 1 for i, (nm, _) in enumerate(ranked)}
    return counts, rank, ranked, ids_by_name, n_rows, n_dev_rows


# ---------------------------------------------------------------- main scan
def main():
    with open(SPLIT, encoding="utf-8") as f:
        split = json.load(f)
    dev_ids = list(split["development_event_ids"])
    holdout_ids = list(split["holdout_event_ids"])
    assert not set(dev_ids) & set(holdout_ids)

    with open(TOP30_FILE, encoding="utf-8") as f:
        top30 = json.load(f)
    sept10 = [(row[0], row[1]) for row in top30["top"]]
    sept10_rank = {nm: i + 1 for i, (nm, _) in enumerate(sept10)}
    sept10_count = dict(sept10)

    cards, id_to_labels, name_to_labels = load_card_set()
    card_labels = [c["label"] for c in cards]

    db_kinds, pokemon_names = load_db_kinds()
    dustin_pokemon, dustin_files, dustin_by_file = load_dustin_pokemon(db_kinds)
    global B2E_POKEMON
    B2E_POKEMON = {}
    for b in B2E_DUSTIN:
        for p in split_archetype_pokemon(b, pokemon_names):
            B2E_POKEMON.setdefault(p, b)

    win_counts, win_rank, win_ranked, win_ids, n_rows, n_dev_rows = window_top_by_dev_matches()
    window_top30 = [nm for nm, _ in win_ranked[:30]]

    scan_set = list(OrderedDict.fromkeys([nm for nm, _ in sept10] + window_top30))

    # per-archetype accumulators
    A = {nm: {"n_entries": 0, "n_lists": 0, "events": set(), "events_any": set(),
              "deck_ids": Counter(), "n_lists_not20": 0,
              "card_lists": Counter(), "card_copies": Counter(),
              "name_only_lists": Counter(), "name_only_ids": defaultdict(Counter),
              "any_lists": 0, "any_switch1_lists": 0}
         for nm in scan_set}
    switch1_labels = {c["label"] for c in cards if c["switch1"]}
    carrier_rows = []
    events_scanned = []
    total_entries = 0
    total_with_decklist = 0
    n_missing_setnum = 0
    n_name_only_events = Counter()

    for eid in dev_ids:
        det_path = os.path.join(RAW, eid + "_details.json.gz")
        st_path = os.path.join(RAW, eid + "_standings.json.gz")
        with gzip.open(det_path, "rt", encoding="utf-8") as f:
            det = json.load(f)
        with gzip.open(st_path, "rt", encoding="utf-8") as f:
            standings = json.load(f)
        if isinstance(standings, dict):
            standings = standings.get("standings") or standings.get("data") or []
        ev = {"event_id": eid, "event_name": det.get("name"), "date": det.get("date"),
              "players": det.get("players"), "decklists_flag": det.get("decklists"),
              "n_standings": len(standings),
              "n_with_decklist": sum(1 for s in standings if s.get("decklist"))}
        events_scanned.append(ev)
        for s in standings:
            total_entries += 1
            dl = s.get("decklist")
            if dl:
                total_with_decklist += 1
            deck = s.get("deck") or {}
            dname = deck.get("name")
            if dname not in A:
                continue
            acc = A[dname]
            acc["n_entries"] += 1
            acc["events_any"].add(eid)
            acc["deck_ids"][deck.get("id")] += 1
            if not dl:
                continue
            acc["n_lists"] += 1
            acc["events"].add(eid)
            cards_in_list = []
            for section in ("pokemon", "trainer"):
                for c in dl.get(section) or []:
                    cards_in_list.append(c)
            ncards = sum(int(c.get("count") or 0) for c in cards_in_list)
            if ncards != 20:
                acc["n_lists_not20"] += 1
            carried = Counter()      # label -> copies (id match)
            carried_ids = defaultdict(set)
            name_only = Counter()    # label -> copies (same name, other printing)
            name_only_ids = defaultdict(set)
            for c in cards_in_list:
                cnt = int(c.get("count") or 0)
                cname = (c.get("name") or "").strip()
                if c.get("set") is None or c.get("number") is None:
                    n_missing_setnum += 1
                    # no id: fall back to the name (flagged in the summary)
                    for lab in name_to_labels.get(cname.casefold(), []):
                        carried[lab] += cnt
                        carried_ids[lab].add("name-only:" + cname)
                    continue
                cid = norm_id(c["set"], c["number"])
                labs = id_to_labels.get(cid)
                if labs:
                    for lab in labs:
                        carried[lab] += cnt
                        carried_ids[lab].add(cid)
                else:
                    for lab in name_to_labels.get(cname.casefold(), []):
                        name_only[lab] += cnt
                        name_only_ids[lab].add(cid)
            for lab, cnt in carried.items():
                acc["card_lists"][lab] += 1
                acc["card_copies"][lab] += cnt
            for lab in name_only:
                acc["name_only_lists"][lab] += 1
                n_name_only_events[lab] += 1
                for cid in name_only_ids[lab]:
                    acc["name_only_ids"][lab][cid] += 1
            if carried:
                acc["any_lists"] += 1
                if any(lab in switch1_labels for lab in carried):
                    acc["any_switch1_lists"] += 1
                carrier_rows.append({
                    "archetype": dname,
                    "deck_id": deck.get("id"),
                    "player": s.get("player"),
                    "player_name": s.get("name"),
                    "event_id": eid,
                    "event_name": det.get("name"),
                    "event_size": det.get("players"),
                    "date": det.get("date"),
                    "placing": s.get("placing"),
                    "record": "%s-%s-%s" % ((s.get("record") or {}).get("wins", ""),
                                             (s.get("record") or {}).get("losses", ""),
                                             (s.get("record") or {}).get("ties", "")),
                    "cards_carried": "; ".join("%s x%d [%s]" % (lab, carried[lab],
                                                                 ",".join(sorted(carried_ids[lab])))
                                               for lab in card_labels if lab in carried),
                    "carries_switch1_card": any(lab in switch1_labels for lab in carried),
                    "same_name_other_printing": "; ".join(
                        "%s x%d [%s]" % (lab, name_only[lab], ",".join(sorted(name_only_ids[lab])))
                        for lab in card_labels if lab in name_only),
                    "n_cards_in_list": ncards,
                    "url": "https://play.limitlesstcg.com/tournament/%s/player/%s/decklist"
                           % (eid, s.get("player")),
                })

    def placing_key(r):
        p = r["placing"]
        return (0, p) if isinstance(p, int) else (1, 10 ** 9)

    carrier_rows.sort(key=lambda r: (r["archetype"], placing_key(r), -(r["event_size"] or 0),
                                     r["date"] or "", r["player"] or ""))

    # ------------------------------------------------------------ census.csv
    census_path = os.path.join(HERE, "census.csv")
    fields = ["archetype", "in_sept10_top30", "rank_sept10", "sept10_players", "rank_window",
              "window_dev_matches", "dustin", "dustin_level", "dustin_reason",
              "n_entries", "n_lists_with_decklist", "n_events_with_decklist",
              "card", "card_ids", "card_kind", "switch1_relevant", "n_lists_carrying",
              "n_copies_total", "n_lists_same_name_other_printing", "same_name_other_printing_ids"]
    arch_summary = []
    with open(census_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for nm in scan_set:
            acc = A[nm]
            d_flag, d_level, reason = dustin_verdict(nm, dustin_pokemon, dustin_by_file, pokemon_names)
            base = {"archetype": nm, "in_sept10_top30": nm in sept10_rank,
                    "rank_sept10": sept10_rank.get(nm, ""), "sept10_players": sept10_count.get(nm, ""),
                    "rank_window": win_rank.get(nm, ""), "window_dev_matches": win_counts.get(nm, 0),
                    "dustin": d_flag, "dustin_level": d_level, "dustin_reason": reason,
                    "n_entries": acc["n_entries"], "n_lists_with_decklist": acc["n_lists"],
                    "n_events_with_decklist": len(acc["events"])}
            for c in cards:
                lab = c["label"]
                row = dict(base)
                row.update({"card": lab, "card_ids": " / ".join(c["ids"]), "card_kind": c["kind"],
                            "switch1_relevant": c["switch1"],
                            "n_lists_carrying": acc["card_lists"].get(lab, 0),
                            "n_copies_total": acc["card_copies"].get(lab, 0),
                            "n_lists_same_name_other_printing": acc["name_only_lists"].get(lab, 0),
                            "same_name_other_printing_ids": "; ".join(
                                "%s:%d" % (cid, n) for cid, n in
                                sorted(acc["name_only_ids"].get(lab, {}).items()))})
                w.writerow(row)
            for label, key in (("ANY (at least one card of the set)", "any_lists"),
                               ("ANY switch-1 card (groups 1-3)", "any_switch1_lists")):
                row = dict(base)
                row.update({"card": label, "card_ids": "", "card_kind": "", "switch1_relevant": "",
                            "n_lists_carrying": acc[key], "n_copies_total": "",
                            "n_lists_same_name_other_printing": "", "same_name_other_printing_ids": ""})
                w.writerow(row)
            carriers = [{"card": lab, "n_lists": acc["card_lists"][lab],
                         "n_copies": acc["card_copies"][lab],
                         "switch1_relevant": lab in switch1_labels}
                        for lab in card_labels if acc["card_lists"].get(lab, 0) > 0]
            name_only = [{"card": lab, "n_lists": acc["name_only_lists"][lab],
                          "ids": dict(acc["name_only_ids"][lab])}
                         for lab in card_labels if acc["name_only_lists"].get(lab, 0) > 0]
            arch_summary.append({
                "name": nm, "in_sept10_top30": nm in sept10_rank,
                "rank_sept10": sept10_rank.get(nm), "sept10_players": sept10_count.get(nm),
                "rank_window": win_rank.get(nm), "window_dev_matches": win_counts.get(nm, 0),
                "deck_ids_in_dev_standings": dict(acc["deck_ids"]),
                "dustin": d_flag, "dustin_level": d_level, "dustin_reason": reason,
                "n_entries": acc["n_entries"], "n_lists": acc["n_lists"],
                "n_events": len(acc["events"]), "n_events_any_entry": len(acc["events_any"]),
                "n_lists_not_20_cards": acc["n_lists_not20"],
                "carriers": carriers, "any_carrier_n": acc["any_lists"],
                "any_switch1_carrier_n": acc["any_switch1_lists"],
                "same_name_other_printing": name_only,
                "best_carrier_entries": [r for r in carrier_rows if r["archetype"] == nm][:10],
            })

    # ------------------------------------------------------------ carrier_entries.csv
    ce_path = os.path.join(HERE, "carrier_entries.csv")
    ce_fields = ["archetype", "deck_id", "player", "player_name", "event_id", "event_name",
                 "event_size", "date", "placing", "record", "cards_carried", "carries_switch1_card",
                 "same_name_other_printing", "n_cards_in_list", "url"]
    with open(ce_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ce_fields)
        w.writeheader()
        for r in carrier_rows:
            w.writerow(r)

    # ------------------------------------------------------------ summary json
    sept10_no_lists = [nm for nm, _ in sept10 if A[nm]["n_lists"] == 0]
    window_no_lists = [nm for nm in window_top30 if A[nm]["n_lists"] == 0]
    sept10_no_carrier = [nm for nm, _ in sept10 if A[nm]["any_lists"] == 0]
    with_carrier = [a for a in arch_summary if a["any_carrier_n"] > 0]
    with_switch1 = [a for a in arch_summary if a["any_switch1_carrier_n"] > 0]
    summary = {
        "title": "kt carrier census, scan phase",
        "date": "2026-09-26",
        "method": (
            "Development-half standings only (split.json development_event_ids, %d events); "
            "holdout standings and details never opened (%d ids listed). An entry counts for an "
            "archetype when its deck.name equals the Limitless archetype name (deck ids grouped by "
            "name are reported). A list 'carries' a card when a decklist line's SET+NUMBER "
            "(number zero-padded to 3) is one of the card's ids in cards.json; lines with the same "
            "name but another printing are counted separately as 'same_name_other_printing' and are "
            "NOT carriers. Window top 30 = development-half matches.csv rows with result_status "
            "decisive or tie, each side's deck name counted once per row (README rule for two-sided "
            "resolved pairings). Dustin's archetypes (dustin=true) at three levels: 'b2e' = one of "
            "the six B2e names; 'all_in_one_file' = every Pokemon in the archetype name (split by "
            "longest match against lib/deckgym-database.json Pokemon names) is a Pokemon card in one "
            "decks/dustin or decks/brews file; 'shares_pokemon' = at least one Pokemon in the "
            "archetype name is a Pokemon card in some Dustin file or is named in a B2e archetype "
            "(conservative, per the task rule: when in doubt, Dustin's). 'none' = not Dustin's. "
            "Cards are tagged switch1_relevant when cards.json's kind is one of "
            "switch1_relevant_kinds (groups 1-3); Protective Poncho, Rocky Helmet and the "
            "counterattack cards are group 4 (kt switches 2/3), not switch 1. Carrier entries are "
            "ordered by placing (unplaced last), then event size (largest first), then date."
            % (len(dev_ids), len(holdout_ids))),
        "dev_events_scanned": len(dev_ids),
        "holdout_events_skipped": len(holdout_ids),
        "holdout_event_ids_not_opened": holdout_ids,
        "matches_csv_rows_total": n_rows,
        "matches_csv_rows_development": n_dev_rows,
        "standings_entries_scanned": total_entries,
        "standings_entries_with_decklist": total_with_decklist,
        "decklist_lines_missing_set_or_number": n_missing_setnum,
        "card_set": [{"label": c["label"], "name": c["name"], "ids": c["ids"], "kind": c["kind"],
                      "switch1_relevant": c["switch1"],
                      "subtype": c["subtype"], "attack_or_ability": c["attack_or_ability"]}
                     for c in cards],
        "n_cards_in_set": len(cards),
        "n_switch1_cards_in_set": sum(1 for c in cards if c["switch1"]),
        "sept10_top30": [{"rank": i + 1, "name": nm, "players_sept10": n,
                          "rank_window": win_rank.get(nm), "window_dev_matches": win_counts.get(nm, 0)}
                         for i, (nm, n) in enumerate(sept10)],
        "window_top30_by_dev_matches": [{"rank": i + 1, "name": nm, "window_dev_matches": n,
                                         "rank_sept10": sept10_rank.get(nm),
                                         "deck_ids": dict(win_ids[nm])}
                                        for i, (nm, n) in enumerate(win_ranked[:30])],
        "window_top30_not_in_sept10": [nm for nm in window_top30 if nm not in sept10_rank],
        "sept10_not_in_window_top30": [nm for nm, _ in sept10 if nm not in window_top30],
        "sept10_top30_with_no_decklists": sept10_no_lists,
        "n_sept10_top30_with_no_decklists": len(sept10_no_lists),
        "window_top30_with_no_decklists": window_no_lists,
        "n_window_top30_with_no_decklists": len(window_no_lists),
        "sept10_top30_with_no_carrier": sept10_no_carrier,
        "archetypes_with_at_least_one_carrier": [a["name"] for a in with_carrier],
        "archetypes_with_a_switch1_carrier": [a["name"] for a in with_switch1],
        "non_dustin_archetypes_with_carrier": [
            {"name": a["name"], "any_carrier_n": a["any_carrier_n"],
             "any_switch1_carrier_n": a["any_switch1_carrier_n"], "n_lists": a["n_lists"],
             "carriers": a["carriers"]} for a in with_carrier if not a["dustin"]],
        "non_dustin_archetypes_with_switch1_carrier": [
            {"name": a["name"], "any_switch1_carrier_n": a["any_switch1_carrier_n"],
             "n_lists": a["n_lists"],
             "carriers": [c for c in a["carriers"] if c["switch1_relevant"]]}
            for a in with_switch1 if not a["dustin"]],
        "dustin_only_by_shares_pokemon_with_carrier": [
            {"name": a["name"], "any_carrier_n": a["any_carrier_n"],
             "any_switch1_carrier_n": a["any_switch1_carrier_n"], "reason": a["dustin_reason"],
             "carriers": a["carriers"]}
            for a in with_carrier if a["dustin_level"] == "shares_pokemon"],
        "dustin_files_scanned": dustin_files,
        "dustin_pokemon_by_file": {f: sorted(v) for f, v in sorted(dustin_by_file.items())},
        "dustin_pokemon_names": sorted({(p, f, m) for p, f, m in dustin_pokemon},
                                       key=lambda t: (t[1], t[0])),
        "events_scanned": events_scanned,
        "archetypes": arch_summary,
        "files": [census_path, ce_path, os.path.join(HERE, "census_summary.json"),
                  os.path.abspath(__file__)],
    }
    with open(os.path.join(HERE, "census_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)

    # ------------------------------------------------------------ console report
    print("dev events scanned: %d   holdout skipped: %d" % (len(dev_ids), len(holdout_ids)))
    print("standings entries: %d   with decklist: %d" % (total_entries, total_with_decklist))
    print("matches.csv rows: %d (development %d)" % (n_rows, n_dev_rows))
    print("lines missing set/number: %d" % n_missing_setnum)
    print("Sept-10 top-30 with no decklists: %d %s" % (len(sept10_no_lists), sept10_no_lists))
    print("window top-30 not in Sept-10: %s" % summary["window_top30_not_in_sept10"])
    print("Sept-10 not in window top-30: %s" % summary["sept10_not_in_window_top30"])
    print()
    print("%-46s %4s %4s %6s %6s %5s %5s %-16s %s" % ("archetype", "s10", "win", "lists", "events",
                                                    "any", "sw1", "dustin", "carriers (* = switch 1)"))
    for a in arch_summary:
        print("%-46s %4s %4s %6d %6d %5d %5d %-16s %s" % (
            a["name"][:46], a["rank_sept10"] or "-", a["rank_window"] or "-", a["n_lists"],
            a["n_events"], a["any_carrier_n"], a["any_switch1_carrier_n"], a["dustin_level"],
            ", ".join("%s%s:%d" % (c["card"], "*" if c["switch1_relevant"] else "", c["n_lists"])
                      for c in a["carriers"])))
    print()
    print("same-name-other-printing (not carriers):")
    for a in arch_summary:
        if a["same_name_other_printing"]:
            print("  %s: %s" % (a["name"], ", ".join("%s:%d %s" % (c["card"], c["n_lists"], c["ids"])
                                                    for c in a["same_name_other_printing"])))
    print()
    print("Dustin mapping:")
    for a in arch_summary:
        print("  %-46s %-16s %s" % (a["name"][:46], a["dustin_level"], a["dustin_reason"]))


if __name__ == "__main__":
    main()
