#!/usr/bin/env python3
"""Gauntlet proposal (Sept 26, 2026): Limitless usage, Energy-type coverage, list variation,
coverage levels and their cost.

Reads only the DEVELOPMENT half of the Cowork Limitless pull
(rl/results/limitless_skill_model_2026-09-25/split.json, 63 events). The 63 holdout standings and
details files are never opened: paths are built only from development ids, and the script
asserts that no holdout id is ever passed to the file opener. matches.csv is read for rows whose
split column is "development" only (to count Limitless matches per pairing). No engine, no games,
no builds, no web.

Run with WSL python3 (standard library only):
  python3 "rl/results/gauntlet_proposal_2026-09-26/gauntlet.py"
Writes gauntlet.json next to itself and prints a text summary (the README's numbers).

Definitions (also in gauntlet.json -> "method"):
  archetype      the exact Limitless deck.name of a standings entry.
  list           a development standings entry with a decklist (4,722 of 4,884 entries).
  top-8 finish   a list whose placing is an integer <= 8.
  card identity  set + zero-padded number, then merged with every printing whose database entry
                 is identical apart from id, rarity and pack (alternate arts, promos with the same
                 text). Exact-list equality uses these merged identities.
  Energy         the lists' own "energy" field when the archetype has any list that states it: an
                 archetype uses a type when at least half of its stating lists include it. When
                 none of its lists states it, the non-Colorless attack costs of the Pokemon named in
                 the archetype name (most common printing in its lists); if those are all
                 Colorless, the card's own type.
  core card      in at least 90% of the archetype's lists; its core count is the largest k that at
                 least 90% of lists run k or more copies of.
  flex slots     20 minus the core cards' core counts.
"""
import csv
import gzip
import io
import json
import math
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
DB_FILE = os.path.join(ROOT, "lib", "deckgym-database.json")
SEPT10 = os.path.join(ROOT, "decks", "classifier", "limitless_2026-09-10.json")
DECK_MAPPING = os.path.join(LSM, "deck_mapping.json")
LADDER_CSV = os.path.join(ROOT, "decks", "screen", "panel_ladder_2026-09-26", "ladder_mapping.csv")
OUT_JSON = os.path.join(HERE, "gauntlet.json")

TYPES = ["Grass", "Fire", "Water", "Lightning", "Psychic", "Fighting", "Darkness", "Metal"]
GAMES_PER_PAIRING = 500          # both seats, 250 each
CORE_SHARE = 0.90
MODAL_REP_SHARE = 0.10           # modal exact list is "representative" at >= 10% of lists (and >= 3 lists)
RARE_CHOICE = 0.10               # a card count shared by < 10% of lists makes a test list "unusual"
COMMON_EXACT = 0.02              # an exact list in >= 2% of lists is a "common variant"
FLEX_SHOW = 0.05                 # flex alternatives shown when run by >= 5% of lists
LIMITLESS_CELL_MIN = 30          # a pairing is checkable against Limitless with >= 30 dev matches
CURVE_TARGETS = [0.50, 0.60, 0.70, 0.80]

# The current test decks: (key, file, group, deck_mapping key or explicit Limitless deck id)
TEST_DECKS = [
    ("altaria", "decks/screen/opponents/t-altaria.txt", "table", "altaria"),
    ("blaziken", "decks/screen/opponents/t-blaziken.txt", "table", "blaziken"),
    ("hydreigon", "decks/screen/opponents/t-hydreigon.txt", "table", "hydreigon"),
    ("lucario", "decks/screen/opponents/t-lucario.txt", "table", "lucario"),
    ("sceptile", "decks/screen/opponents/t-sceptile.txt", "table", "sceptile"),
    ("suicune", "decks/screen/opponents/t-suicune.txt", "table", "suicune"),
    ("vespiquen", "decks/screen/opponents/t-vespiquen.txt", "table", "vespiquen"),
    ("weezing", "decks/screen/opponents/t-weezing.txt", "table", "weezing"),
    ("h-manectric", "rl/results/b2e_card_check_2026-09-26/decks/h-manectric.txt", "held-out", "manectric_heliolisk"),
    ("h-raticate", "rl/results/b2e_card_check_2026-09-26/decks/h-raticate.txt", "held-out", "raticate_ninetales"),
    ("h-hoopa_absol", "rl/results/b2e_card_check_2026-09-26/decks/h-hoopa_absol.txt", "held-out", "hoopa_absol"),
    ("h-garchomp", "rl/results/b2e_card_check_2026-09-26/decks/h-garchomp.txt", "held-out", "garchomp"),
    ("h-whimsicott", "rl/results/b2e_card_check_2026-09-26/decks/h-whimsicott.txt", "held-out", "whimsicott_ariados"),
    ("h-charizardy_entei", "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt", "held-out", "charizardy_entei"),
    ("l-charizardy", "decks/screen/panel_ladder_2026-09-26/l-charizardy.txt", "ladder", "id:mega-charizard-y-ex-b1a-entei-ex-a4a"),
    ("l-sharpedo", "decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt", "ladder", "id:mega-sharpedo-ex-b4-gyarados-a4"),
]
# Other Limitless-archetype list files in the repo (not Dustin's: decks/dustin and decks/brews are
# his and are never counted as test lists). Labelled by nearest development list, below.
OTHER_REPO_LISTS = [
    "decks/variants-2026-09-23/altaria_jlng_pmpt44_2026-08-29.txt",
    "decks/variants-2026-09-23/altaria_lanora_blockdragon_2026-09-10.txt",
    "decks/variants-2026-09-23/vespiquen_kovacs469_pokebounty_2026-09-14.txt",
    "decks/variants-2026-09-23/vespiquen_twidleurstixx_breakfastclub_2026-09-02.txt",
    "rl/results/kt_carrier_census_2026-09-26/decks/c-mega_lucario_ex_lucario.txt",
    "rl/results/kt_carrier_census_2026-09-26/decks/c-mega_altaria_ex_igglybuff.txt",
    "rl/results/kt_carrier_census_2026-09-26/decks/c-jumpluff_ex_team_rocket_s_electrode.txt",
    "rl/results/kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt",
    "rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/charizardy_entei.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/garchomp.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/hoopa_absol.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/manectric_heliolisk.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/raticate_ninetales.txt",
    "rl/results/limitless_skill_model_2026-09-25/decklists/whimsicott_ariados.txt",
]
RESEARCH_COPIES = {k: "decks/research/%s.txt" % k for k in
                   ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune",
                    "vespiquen", "weezing"]}


# ------------------------------------------------------------------ helpers
def pct(x, digits=1):
    return round(100.0 * x, digits)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def norm_num(n):
    n = str(n).strip()
    try:
        return "%03d" % int(n)
    except ValueError:
        return n


def load_db():
    with open(DB_FILE, encoding="utf-8") as f:
        db = json.load(f)
    by_id = {}
    groups = defaultdict(list)
    for e in db:
        kind, v = next(iter(e.items()))
        sig = json.dumps({k: v[k] for k in sorted(v) if k not in ("id", "rarity", "booster_pack")},
                         sort_keys=True, ensure_ascii=False)
        by_id[v["id"]] = (kind, v)
        groups[(kind, sig)].append(v["id"])
    canon = {}
    for ids in groups.values():
        c = sorted(ids)[0]
        for i in ids:
            canon[i] = c
    pokemon_names = {v["name"] for k, v in by_id.values() if k == "Pokemon"}
    return by_id, canon, pokemon_names


def split_archetype_pokemon(name, pokemon_names):
    """Greedy longest match of the archetype name against database Pokemon names
    (the kt carrier census's rule)."""
    toks = name.split(" ")
    parts, i = [], 0
    while i < len(toks):
        best = None
        for k in range(min(5, len(toks) - i), 0, -1):
            cand = " ".join(toks[i:i + k])
            if cand in pokemon_names:
                best = (k, cand)
                break
        if best is None:
            parts.append(toks[i])
            i += 1
        else:
            parts.append(best[1])
            i += best[0]
    return parts


LINE_RE = re.compile(r"^\s*(\d+)\s+(?:(.+?)\s+)?([A-Za-z][A-Za-z0-9\-]*)\s+(\d{3})\s*$")


def parse_deck_file(rel):
    path = os.path.join(ROOT, rel)
    cards = []
    energy = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.lower().startswith("energy:"):
                energy = tuple(t.strip() for t in s.split(":", 1)[1].split(",") if t.strip())
                continue
            m = LINE_RE.match(s)
            if not m:
                raise SystemExit("unparsed line in %s: %r" % (rel, s))
            cnt, _name, set_code, num = m.groups()
            cards.append(("%s %s" % (set_code, num), int(cnt)))
    return cards, energy


# ------------------------------------------------------------------ main
def main():
    with open(SPLIT, encoding="utf-8") as f:
        split = json.load(f)
    dev_ids = list(split["development_event_ids"])
    holdout_ids = set(split["holdout_event_ids"])
    assert len(dev_ids) == 63 and len(holdout_ids) == 63 and not holdout_ids & set(dev_ids)

    by_id, canon, pokemon_names = load_db()
    unknown_ids = Counter()

    def cid_of(raw_id):
        if raw_id not in by_id:
            unknown_ids[raw_id] += 1
        return canon.get(raw_id, raw_id)

    def kind_of(c, fallback=None):
        if c in by_id:
            return by_id[c][0]
        return fallback or "?"

    raw_id_use = defaultdict(Counter)   # canonical id -> raw ids seen in lists
    names_seen = {}

    def label(c):
        raw = raw_id_use[c].most_common(1)[0][0] if raw_id_use[c] else c
        nm = by_id[c][1]["name"] if c in by_id else names_seen.get(c, "?")
        return "%s %s" % (nm, raw)

    def card_name(c):
        return by_id[c][1]["name"] if c in by_id else names_seen.get(c, "?")

    # ---------------------------------------------------------------- read development lists
    def open_dev(eid, what):
        assert eid not in holdout_ids, "refusing to open a holdout file"
        return gzip.open(os.path.join(RAW, "%s_%s.json.gz" % (eid, what)), "rt", encoding="utf-8")

    records = []
    n_entries = 0
    n_no_list = 0
    events = []
    for eid in dev_ids:
        with open_dev(eid, "details") as f:
            det = json.load(f)
        with open_dev(eid, "standings") as f:
            st = json.load(f)
        events.append({"id": eid, "name": det.get("name"), "date": det.get("date"),
                       "players": det.get("players")})
        for s in st:
            n_entries += 1
            dl = s.get("decklist")
            if not dl:
                n_no_list += 1
                continue
            deck = s.get("deck") or {}
            cards = Counter()
            kinds = {}
            for section in ("pokemon", "trainer"):
                for c in dl.get(section) or []:
                    raw = "%s %s" % (str(c.get("set")).strip(), norm_num(c.get("number")))
                    k = cid_of(raw)
                    raw_id_use[k][raw] += int(c.get("count") or 0)
                    names_seen.setdefault(k, c.get("name"))
                    cards[k] += int(c.get("count") or 0)
                    kinds[k] = "Pokemon" if section == "pokemon" else "Trainer"
            energy = dl.get("energy")
            energy = tuple(t for t in TYPES if energy and t in energy) if energy else None
            placing = s.get("placing")
            records.append({
                "eid": eid, "arch": deck.get("name"), "deck_id": deck.get("id"),
                "placing": placing if isinstance(placing, int) else None,
                "players": det.get("players"), "energy": energy, "cards": cards,
                "kinds": kinds, "player": s.get("player"),
            })
    for r in records:
        r["key"] = tuple(sorted(r["cards"].items()))
        r["pkey"] = tuple(sorted((c, n) for c, n in r["cards"].items()
                                 if kind_of(c, r["kinds"][c]) == "Pokemon"))
        r["tkey"] = tuple(sorted((c, n) for c, n in r["cards"].items()
                                 if kind_of(c, r["kinds"][c]) != "Pokemon"))
        r["n"] = sum(r["cards"].values())
        r["top8"] = r["placing"] is not None and r["placing"] <= 8

    N = len(records)
    N_TOP8 = sum(r["top8"] for r in records)
    by_arch = defaultdict(list)
    for r in records:
        by_arch[r["arch"]].append(r)

    # ---------------------------------------------------------------- usage
    with open(SEPT10, encoding="utf-8") as f:
        s10 = json.load(f)
    sept10_rank = {row[0]: i + 1 for i, row in enumerate(s10["top"])}

    def energy_of(arch):
        L = by_arch[arch]
        stated = [r["energy"] for r in L if r["energy"]]
        combos = Counter(stated)
        out = {"n_lists": len(L), "n_stating": len(stated),
               "combinations": [{"types": list(k), "lists": v} for k, v in combos.most_common(5)]}
        if stated:
            share = {t: sum(1 for e in stated if t in e) / len(stated) for t in TYPES}
            types = [t for t in TYPES if share[t] >= 0.5]
            if not types:
                types = list(combos.most_common(1)[0][0])
            out.update({"types": types, "source": "stated",
                        "type_share_of_stating_lists": {t: round(v, 4) for t, v in share.items() if v > 0}})
        else:
            out.update({"types": derived_types(arch), "source": "attackers"})
        out["attacker_types"] = derived_types(arch)
        return out

    def derived_types(arch):
        L = by_arch[arch]
        parts = split_archetype_pokemon(arch, pokemon_names)
        types = set()
        for p in parts:
            ids = Counter()
            for r in L:
                for c, n in r["cards"].items():
                    if c in by_id and by_id[c][0] == "Pokemon" and by_id[c][1]["name"] == p:
                        ids[c] += 1
            if not ids:
                continue
            v = by_id[ids.most_common(1)[0][0]][1]
            t = {e for a in v.get("attacks") or [] for e in a.get("energy_required") or []
                 if e in TYPES}
            if not t and v.get("energy_type") in TYPES:
                t = {v["energy_type"]}
            types |= t
        return [t for t in TYPES if t in types]

    arch_rows = []
    for arch, L in by_arch.items():
        t8 = sum(r["top8"] for r in L)
        arch_rows.append({"archetype": arch, "lists": len(L), "share": len(L) / N,
                          "top8": t8, "top8_share": t8 / N_TOP8 if N_TOP8 else 0,
                          "events": len({r["eid"] for r in L}),
                          "deck_ids": dict(Counter(r["deck_id"] for r in L)),
                          "sept10_rank": sept10_rank.get(arch)})
    arch_rows.sort(key=lambda a: (-a["lists"], -a["top8"], a["archetype"]))
    for i, a in enumerate(arch_rows):
        a["rank_lists"] = i + 1
    for i, a in enumerate(sorted(arch_rows, key=lambda a: (-a["top8"], -a["lists"], a["archetype"]))):
        a["rank_top8"] = i + 1
    arch_index = {a["archetype"]: a for a in arch_rows}
    for a in arch_rows:
        a["energy"] = energy_of(a["archetype"])

    # agreement check: stated Energy vs the named Pokemon's attack costs
    agree = {"checked": 0, "same": 0, "stated_includes_attackers": 0, "differs": []}
    for a in arch_rows:
        e = a["energy"]
        if e["source"] == "stated" and e["n_stating"] >= 5 and e["attacker_types"]:
            agree["checked"] += 1
            if e["types"] == e["attacker_types"]:
                agree["same"] += 1
            elif set(e["attacker_types"]) <= set(e["types"]):
                agree["stated_includes_attackers"] += 1
            else:
                agree["differs"].append({"archetype": a["archetype"], "lists": a["lists"],
                                         "stated": e["types"], "attackers": e["attacker_types"]})

    # ---------------------------------------------------------------- test decks
    with open(DECK_MAPPING, encoding="utf-8") as f:
        dmap = json.load(f)["deck_ids"]
    id_to_names = defaultdict(Counter)
    for r in records:
        id_to_names[r["deck_id"]][r["arch"]] += 1

    def to_counter(cards):
        c = Counter()
        for raw, n in cards:
            k = canon.get(raw, raw)
            c[k] += n
        return c

    tests = OrderedDict()
    for key, rel, group, mk in TEST_DECKS:
        cards, energy = parse_deck_file(rel)
        deck_id = mk[3:] if mk.startswith("id:") else dmap[mk][0]
        names = id_to_names.get(deck_id)
        assert names and len(names) == 1, (key, deck_id, names)
        arch = next(iter(names))
        cnt = to_counter(cards)
        tests[key] = {"key": key, "file": rel, "group": group, "deck_id": deck_id,
                      "archetype": arch, "energy_line": list(energy or ()), "cards": cnt,
                      "n_cards": sum(cnt.values())}
    research_check = {}
    for k, rel in RESEARCH_COPIES.items():
        cards, energy = parse_deck_file(rel)
        research_check[k] = (to_counter(cards) == tests[k]["cards"]
                             and list(energy or ()) == tests[k]["energy_line"])

    groups_order = ["table", "held-out", "ladder"]
    current_archs = OrderedDict()
    for t in tests.values():
        current_archs.setdefault(t["archetype"], []).append(t["key"])

    # ---------------------------------------------------------------- repo list files
    def overlap(a, b):
        return sum(min(n, b.get(c, 0)) for c, n in a.items())

    def nearest(cnt):
        best, labs = -1, Counter()
        exact = 0
        key = tuple(sorted(cnt.items()))
        for r in records:
            if r["key"] == key:
                exact += 1
            ov = overlap(cnt, r["cards"])
            if ov > best:
                best, labs = ov, Counter([r["arch"]])
            elif ov == best:
                labs[r["arch"]] += 1
        return labs.most_common(1)[0][0], best, exact, dict(labs)

    repo_lists = []
    for key, t in tests.items():
        lab, ov, ex, labs = nearest(t["cards"])
        repo_lists.append({"file": t["file"], "archetype_by_deck_id": t["archetype"],
                           "nearest_archetype": lab, "nearest_overlap": ov, "exact_dev_copies": ex,
                           "test_deck": True})
    for rel in OTHER_REPO_LISTS:
        cards, energy = parse_deck_file(rel)
        lab, ov, ex, labs = nearest(to_counter(cards))
        repo_lists.append({"file": rel, "nearest_archetype": lab, "nearest_overlap": ov,
                           "exact_dev_copies": ex, "test_deck": False,
                           "energy_line": list(energy or ())})
    archs_with_repo_list = defaultdict(list)
    for x in repo_lists:
        a = x.get("archetype_by_deck_id") or (x["nearest_archetype"] if x["nearest_overlap"] >= 17 else None)
        if a:
            archs_with_repo_list[a].append(x["file"])

    # ---------------------------------------------------------------- Energy coverage
    # An archetype "is of type T" when its Energy includes T; it is "single-type T" when T is its
    # only Energy. Coverage status per type:
    #   missing  no current test deck uses T;
    #   thin     exactly one archetype in the current set plays T as its only Energy, or only
    #            multi-Energy decks use it;
    #   covered  two or more archetypes play T as their only Energy.
    # Additions for a missing type: the most-used single-type archetype of that type (a deck that
    # runs on that Energy alone); if no archetype is single-type, the most-used that includes it.
    type_rank = {}
    type_rank_single = {}
    for t in TYPES:
        type_rank[t] = [a["archetype"] for a in arch_rows if t in a["energy"]["types"]]
        type_rank_single[t] = [a["archetype"] for a in arch_rows if a["energy"]["types"] == [t]]

    def brief(b):
        return {"archetype": b, "rank_lists": arch_index[b]["rank_lists"],
                "rank_top8": arch_index[b]["rank_top8"],
                "lists": arch_index[b]["lists"], "top8": arch_index[b]["top8"],
                "energy": arch_index[b]["energy"]["types"],
                "energy_combinations": arch_index[b]["energy"]["combinations"][:3],
                "in_current_set": b in current_archs}

    coverage = OrderedDict()
    for t in TYPES:
        decks_t = [k for k, d in tests.items() if t in d["energy_line"]]
        archs_t = list(OrderedDict.fromkeys(tests[k]["archetype"] for k in decks_t))
        single = [k for k in decks_t if len(tests[k]["energy_line"]) == 1]
        single_archs = list(OrderedDict.fromkeys(tests[k]["archetype"] for k in single))
        if not decks_t:
            status = "missing"
        elif len(single_archs) <= 1:
            status = "thin"
        else:
            status = "covered"
        coverage[t] = {
            "status": status, "test_decks": decks_t, "archetypes": archs_t,
            "single_type_decks": single, "single_type_archetypes": single_archs,
            "most_used_archetypes_of_type": [brief(b) for b in type_rank[t][:6]],
            "most_used_single_type_archetypes": [brief(b) for b in type_rank_single[t][:6]],
            "most_used_not_in_set": [brief(b) for b in type_rank[t] if b not in current_archs][:3],
            "n_archetypes_of_type": len(type_rank[t]),
            "lists_of_type": sum(arch_index[b]["lists"] for b in type_rank[t]),
            "lists_of_type_share": round(sum(arch_index[b]["lists"] for b in type_rank[t]) / N, 4),
            "n_single_type_archetypes": len(type_rank_single[t]),
            "lists_single_type": sum(arch_index[b]["lists"] for b in type_rank_single[t]),
        }
        if status == "missing":
            coverage[t]["all_archetypes_of_type"] = [brief(b) for b in type_rank[t]]
    additions = []
    for t in TYPES:
        if coverage[t]["status"] == "missing":
            cand = [b for b in type_rank_single[t] if b not in current_archs]
            rule = "most-used archetype with %s as its only Energy" % t
            if not cand:
                cand = [b for b in type_rank[t] if b not in current_archs]
                rule = "most-used archetype whose Energy includes %s (none is %s only)" % (t, t)
            if cand:
                runner = [b for b in type_rank[t] if b not in current_archs and b != cand[0]][:2]
                additions.append({"type": t, "archetype": cand[0], "rule": rule,
                                  "runners_up": [brief(b) for b in runner]})
    optional_thin = []
    for t in TYPES:
        if coverage[t]["status"] == "thin":
            cand = [b for b in type_rank[t] if b not in current_archs]
            cand_single = [b for b in type_rank_single[t] if b not in current_archs]
            optional_thin.append({"type": t,
                                  "most_used_not_in_set": brief(cand[0]) if cand else None,
                                  "most_used_single_type_not_in_set":
                                      brief(cand_single[0]) if cand_single else None})

    # ---------------------------------------------------------------- list variation
    def pokemon_evolution_ok(cnt):
        names = {card_name(c) for c in cnt}
        problems = []
        for c in cnt:
            if c in by_id and by_id[c][0] == "Pokemon":
                v = by_id[c][1]
                if v.get("stage") in (1, 2) and v.get("evolves_from") and v["evolves_from"] not in names:
                    if not (v.get("stage") == 2 and any(card_name(x) == "Rare Candy" for x in cnt)):
                        problems.append("%s without %s" % (v["name"], v["evolves_from"]))
        return problems

    def listing(cnt):
        rows = sorted(cnt.items(), key=lambda kv: (0 if kind_of(kv[0]) == "Pokemon" else 1, kv[0]))
        return ["%d %s" % (n, label(c)) for c, n in rows]

    def dist(a, b):
        return max(sum(a.values()), sum(b.values())) - overlap(a, b)

    def variation(arch, test_keys, extra_files=()):
        L = by_arch[arch]
        n = len(L)
        exact = Counter(r["key"] for r in L)
        top = exact.most_common()
        modal_key, modal_n = top[0]
        modal_ties = sum(1 for k, v in top if v == modal_n)
        modal = Counter(dict(modal_key))
        cum, k50 = 0, None
        for i, (k, v) in enumerate(top):
            cum += v
            if cum >= 0.5 * n:
                k50 = i + 1
                break
        dists = sorted(dist(r["cards"], modal) for r in L)
        med = dists[len(dists) // 2] if n % 2 else (dists[n // 2 - 1] + dists[n // 2]) / 2
        all_cards = set()
        for r in L:
            all_cards |= set(r["cards"])
        count_dist = {c: Counter(r["cards"].get(c, 0) for r in L) for c in all_cards}

        def share_at_least(c, k):
            return sum(v for m, v in count_dist[c].items() if m >= k) / n

        core = OrderedDict()
        for c in sorted(all_cards, key=lambda c: (0 if kind_of(c) == "Pokemon" else 1, c)):
            if share_at_least(c, 1) >= CORE_SHARE:
                k = 1
                while share_at_least(c, k + 1) >= CORE_SHARE:
                    k += 1
                core[c] = k
        core_slots = sum(core.values())
        flex_p, flex_t = [], []
        for r in L:
            fp = ft = 0
            for c, m in r["cards"].items():
                extra = m - core.get(c, 0)
                if extra > 0:
                    if kind_of(c, r["kinds"][c]) == "Pokemon":
                        fp += extra
                    else:
                        ft += extra
            flex_p.append(fp)
            flex_t.append(ft)
        alts = []
        for c in all_cards:
            kc = core.get(c, 0)
            rate = share_at_least(c, kc + 1)
            if rate < FLEX_SHOW or kc + 1 > 2 and rate == 0:
                continue
            runners = {m: v for m, v in count_dist[c].items() if m > kc}
            typical = max(runners.items(), key=lambda kv: (kv[1], -kv[0]))[0] if runners else kc + 1
            alts.append({"card": label(c), "kind": kind_of(c),
                         "what": ("copy %d of a core card" % (kc + 1)) if kc else "card",
                         "lists_share": round(rate, 4), "typical_count": typical})
        alts.sort(key=lambda a: -a["lists_share"])
        pk = Counter(r["pkey"] for r in L)
        pk_top = pk.most_common(3)
        tk = Counter(r["tkey"] for r in L)
        # representative lists
        rep_modal_ok = modal_n / n >= MODAL_REP_SHARE and modal_n >= 3
        build = Counter(core)
        cands = []
        for c in all_cards:
            kc = core.get(c, 0)
            for extra in (1, 2):
                if kc + extra > 2:
                    break
                cands.append((share_at_least(c, kc + extra), c, kc + extra))
        cands.sort(key=lambda x: (-x[0], x[1]))
        for rate, c, m in cands:
            if sum(build.values()) >= 20:
                break
            if build.get(c, 0) == m - 1 and sum(build.values()) + 1 <= 20:
                build[c] = m
        build_key = tuple(sorted(build.items()))
        build_real = exact.get(build_key, 0)
        # medoid: the real list closest on average to all lists
        distinct = [Counter(dict(k)) for k, _ in top]
        best_med, medoid = None, None
        for d in distinct:
            s = sum(dist(d, r["cards"]) for r in L)
            if best_med is None or s < best_med:
                best_med, medoid = s, d
        out = {
            "archetype": arch, "lists": n, "distinct_exact_lists": len(exact),
            "modal_share": round(modal_n / n, 4), "modal_lists": modal_n, "modal_ties": modal_ties,
            "top3_exact_shares": [round(v / n, 4) for _, v in top[:3]],
            "exact_lists_to_cover_half": k50,
            "median_cards_from_modal": med,
            "share_within_2_cards_of_modal": round(sum(1 for d in dists if d <= 2) / n, 4),
            "core": [{"card": label(c), "kind": kind_of(c), "core_count": k,
                      "lists_share_with_any": round(share_at_least(c, 1), 4)} for c, k in core.items()],
            "core_slots": core_slots, "flex_slots": 20 - core_slots,
            "mean_flex_copies_pokemon": round(sum(flex_p) / n, 2),
            "mean_flex_copies_trainer": round(sum(flex_t) / n, 2),
            "flex_alternatives": alts[:14],
            "pokemon_line": {"modal_share": round(pk_top[0][1] / n, 4), "distinct": len(pk),
                             "top3": [{"share": round(v / n, 4),
                                       "line": ["%d %s" % (m, label(c)) for c, m in k]} for k, v in pk_top]},
            "trainer_part": {"modal_share": round(tk.most_common(1)[0][1] / n, 4), "distinct": len(tk)},
            "modal_list": listing(modal),
            "modal_list_evolution_problems": pokemon_evolution_ok(modal),
            "representative": {
                "choice": "modal" if rep_modal_ok else "core_plus_flex",
                "why": ("the modal exact list is played by %d of %d lists (%.1f%%), at or above the "
                        "10%% bar, so a real, repeated list is used" % (modal_n, n, 100 * modal_n / n))
                if rep_modal_ok else
                ("the modal exact list is only %d of %d lists (%.1f%%), below the 10%% bar, so the "
                 "core plus the most common flex cards is used" % (modal_n, n, 100 * modal_n / n)),
                "core_plus_flex_list": listing(build),
                "core_plus_flex_cards": sum(build.values()),
                "core_plus_flex_real_copies": build_real,
                "core_plus_flex_cards_from_modal": dist(build, modal),
                "core_plus_flex_evolution_problems": pokemon_evolution_ok(build),
                "medoid_list": listing(medoid),
                "medoid_real_copies": exact.get(tuple(sorted(medoid.items())), 0),
                "medoid_cards_from_modal": dist(medoid, modal),
            },
            "energy": arch_index[arch]["energy"],
            "tests": [],
        }
        # the current test lists (and any other repo list of this archetype) against its lists
        items = [tests[k] for k in test_keys]
        for rel in extra_files:
            cards, energy = parse_deck_file(rel)
            items.append({"key": os.path.basename(rel), "file": rel, "cards": to_counter(cards),
                          "energy_line": list(energy or ())})
        for t in items:
            tkey = t["key"]
            cnt = t["cards"]
            key = tuple(sorted(cnt.items()))
            ex = exact.get(key, 0)
            consider = set(cnt) | {c for c in all_cards if share_at_least(c, 1) >= 0.5}
            choices = []
            for c in consider:
                m = cnt.get(c, 0)
                same = count_dist[c].get(m, 0) / n if c in count_dist else (1.0 if m == 0 else 0.0)
                choices.append({"card": label(c), "count_in_test_list": m,
                                "lists_share_same_count": round(same, 4)})
            choices.sort(key=lambda x: x["lists_share_same_count"])
            rare = [x for x in choices if x["lists_share_same_count"] < RARE_CHOICE]
            # A list taken from the development data always matches itself once, so an exact-list
            # share counts only with at least 3 copies.
            if key == modal_key:
                cls = "modal"
            elif (ex / n >= COMMON_EXACT and ex >= 3) or not rare:
                cls = "common variant"
            else:
                cls = "unusual"
            # single-card Trainer swaps for a sensitivity check: the most common Trainer
            # alternatives this list runs fewer copies of, each for the list's least common
            # non-core Trainer choice
            swaps_in = []
            for c in all_cards:
                if kind_of(c) == "Pokemon":
                    continue
                m = cnt.get(c, 0)
                if m >= 2:
                    continue
                rate = share_at_least(c, m + 1)
                if rate >= FLEX_SHOW:
                    swaps_in.append((rate, c, m + 1))
            swaps_in.sort(key=lambda x: (-x[0], x[1]))
            swaps_out = []
            for c, m in cnt.items():
                if kind_of(c) == "Pokemon" or m <= core.get(c, 0):
                    continue
                same = count_dist[c].get(m, 0) / n if c in count_dist else 0.0
                swaps_out.append((same, c, m))
            swaps_out.sort(key=lambda x: (x[0], x[1]))
            swaps = []
            used_out = set()
            for rate, c_in, m_in in swaps_in:
                outs = [x for x in swaps_out if x[1] != c_in and x[1] not in used_out]
                if not outs:
                    break
                same, c_out, m_out = outs[0]
                used_out.add(c_out)
                swaps.append({"in": "%s (copy %d)" % (label(c_in), m_in), "in_lists_share": round(rate, 4),
                              "out": "%s (copy %d)" % (label(c_out), m_out),
                              "out_same_count_share": round(same, 4)})
                if len(swaps) == 3:
                    break
            tp = tuple(sorted((c, m) for c, m in cnt.items() if kind_of(c) == "Pokemon"))
            diff_from_modal = {"test_only": ["%d %s" % (cnt[c] - modal.get(c, 0), label(c))
                                             for c in sorted(cnt) if cnt[c] > modal.get(c, 0)],
                               "modal_only": ["%d %s" % (modal[c] - cnt.get(c, 0), label(c))
                                              for c in sorted(modal) if modal[c] > cnt.get(c, 0)]}
            # twin: most common real list at least 2 cards away from the test list
            twin = None
            for k, v in top:
                d = Counter(dict(k))
                if dist(d, cnt) >= 2:
                    twin = {"lists": v, "share": round(v / n, 4), "cards_from_test": dist(d, cnt),
                            "is_modal": k == modal_key,
                            "adds": ["%d %s" % (d[c] - cnt.get(c, 0), label(c)) for c in sorted(d)
                                     if d[c] > cnt.get(c, 0)],
                            "removes": ["%d %s" % (cnt[c] - d.get(c, 0), label(c)) for c in sorted(cnt)
                                        if cnt[c] > d.get(c, 0)],
                            "list": listing(d)}
                    break
            out["tests"].append({
                "key": tkey, "file": t["file"], "energy_line": t["energy_line"],
                "exact_copies": ex, "exact_share": round(ex / n, 4),
                "is_modal": key == modal_key, "cards_from_modal": dist(cnt, modal),
                "class": cls, "rarest_choices": choices[:4], "rare_choices": rare,
                "pokemon_line_share": round(pk.get(tp, 0) / n, 4),
                "differs_from_modal": diff_from_modal, "twin": twin,
                "trainer_swaps_for_sensitivity": swaps,
            })
        return out

    gauntlet_archs = list(current_archs) + [a["archetype"] for a in additions]
    var = OrderedDict()
    for arch in gauntlet_archs:
        var[arch] = variation(arch, current_archs.get(arch, []))
    # growth candidates: usage top 18 archetypes not in the Energy gauntlet
    growth = [a["archetype"] for a in arch_rows[:18] if a["archetype"] not in gauntlet_archs]
    var_growth = OrderedDict()
    for arch in growth:
        files = [f for f in archs_with_repo_list.get(arch, []) if f not in {t["file"] for t in tests.values()}]
        var_growth[arch] = variation(arch, [], files)
    def copies_of(arch, listing_lines):
        """Every development list of this archetype equal to a listing produced by listing()."""
        out = []
        for r in by_arch[arch]:
            if sorted(listing(r["cards"])) == sorted(listing_lines):
                out.append({"player": r["player"], "event_id": r["eid"], "event_players": r["players"],
                            "date": next(e["date"] for e in events if e["id"] == r["eid"]),
                            "placing": r["placing"],
                            "url": "https://play.limitlesstcg.com/tournament/%s/player/%s/decklist"
                                   % (r["eid"], r["player"])})
        return out

    for a in additions:
        rep = var[a["archetype"]]["representative"]
        rep_list = rep["core_plus_flex_list"] if rep["choice"] == "core_plus_flex" else var[a["archetype"]]["modal_list"]
        a["representative_list"] = rep_list
        a["representative_list_copies"] = copies_of(a["archetype"], rep_list)
        a["top8_lists"] = [{"player": r["player"], "event_id": r["eid"], "event_players": r["players"],
                            "placing": r["placing"], "list": listing(r["cards"])}
                           for r in by_arch[a["archetype"]] if r["top8"]]
    for a in additions:
        a.update({"rank_lists": arch_index[a["archetype"]]["rank_lists"],
                  "rank_top8": arch_index[a["archetype"]]["rank_top8"],
                  "lists": arch_index[a["archetype"]]["lists"],
                  "top8": arch_index[a["archetype"]]["top8"],
                  "repo_lists": archs_with_repo_list.get(a["archetype"], []),
                  "representative": var[a["archetype"]]["representative"]["choice"]})

    # ---------------------------------------------------------------- coverage levels
    table_archs = [tests[k]["archetype"] for k in tests if tests[k]["group"] == "table"]
    held_archs = [tests[k]["archetype"] for k in tests if tests[k]["group"] == "held-out"]
    ladder_archs = [tests[k]["archetype"] for k in tests if tests[k]["group"] == "ladder"]
    add_archs = [a["archetype"] for a in additions]
    order = [a["archetype"] for a in arch_rows]
    curve = []
    cum = 0
    for i, a in enumerate(arch_rows):
        cum += a["lists"]
        curve.append(cum / N)
    curve_levels = OrderedDict()
    for tgt in CURVE_TARGETS:
        k = next(i + 1 for i, c in enumerate(curve) if c >= tgt)
        curve_levels["top%d_for_%d" % (k, int(tgt * 100))] = {"target": tgt, "k": k,
                                                              "archetypes": order[:k]}

    # Limitless development matches per unordered pairing (development rows only)
    pair_matches = Counter()
    csv.field_size_limit(10 ** 9)
    n_dev_rows = 0
    with open(MATCHES, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["split"] != "development":
                continue
            n_dev_rows += 1
            if row["result_status"] not in ("decisive", "tie"):
                continue
            a, b = row["deck1_name"], row["deck2_name"]
            if a and b and a != b:
                pair_matches[tuple(sorted((a, b)))] += 1

    # ladder games (Dustin's 33, mapped in panel_ladder_2026-09-26)
    with open(LADDER_CSV, encoding="utf-8", newline="") as f:
        ladder = list(csv.DictReader(f))
    panel_key_arch = {k: tests[k]["archetype"] for k in tests if tests[k]["group"] == "table"}

    def level_stats(name, archs):
        S = list(OrderedDict.fromkeys(archs))
        Sset = set(S)
        lists = sum(arch_index[a]["lists"] for a in S if a in arch_index)
        t8 = sum(arch_index[a]["top8"] for a in S if a in arch_index)
        core = list(OrderedDict.fromkeys(table_archs))
        non_core = [a for a in S if a not in core]
        pairs_core = [(core[i], core[j]) for i in range(len(core)) for j in range(i + 1, len(core))]
        pairs_core += [(a, c) for a in non_core for c in core]
        U = list(OrderedDict.fromkeys(core + S))
        pairs_rr = [(U[i], U[j]) for i in range(len(U)) for j in range(i + 1, len(U))]
        w = {a: arch_index[a]["lists"] for a in S}
        tot = sum(w.values())
        w = {a: v / tot for a, v in w.items()}
        sum_w2 = sum(v * v for v in w.values())
        K = len(S)
        se_equal = 100 * math.sqrt(0.25 / (GAMES_PER_PAIRING * K))
        se_weighted = 100 * math.sqrt(sum_w2 * 0.25 / GAMES_PER_PAIRING)
        wu = {a: arch_index[a]["lists"] for a in U}
        pv = [wu[a] * wu[b] for a, b in pairs_core]
        pv_tot = sum(pv)
        eff_pairs = (1 / sum((x / pv_tot) ** 2 for x in pv)) if pv_tot else 0
        lad_exact = sum(1 for g in ladder if g["mapped_archetype"] in Sset)
        in_family = [bool(g["mapped_archetype"] in Sset or
                          (g["panel_key"] and panel_key_arch.get(g["panel_key"]) in Sset))
                     for g in ladder]
        lad_family = sum(in_family)
        lad_missed = Counter(g["mapped_archetype"] for g, f in zip(ladder, in_family) if not f)
        return {
            "level": name, "archetypes": S, "k": K,
            "lists": lists, "lists_share": round(lists / N, 4),
            "top8": t8, "top8_share": round(t8 / N_TOP8, 4),
            "with_repo_list": [a for a in S if a in archs_with_repo_list],
            "without_repo_list": [a for a in S if a not in archs_with_repo_list],
            "pilot_reading_vs_core8": {"pairings": len(pairs_core),
                                       "games": len(pairs_core) * GAMES_PER_PAIRING,
                                       "pairings_with_%d_plus_dev_matches" % LIMITLESS_CELL_MIN:
                                           sum(1 for a, b in pairs_core
                                               if pair_matches[tuple(sorted((a, b)))] >= LIMITLESS_CELL_MIN),
                                       "usage_weighted_effective_pairings": round(eff_pairs, 1)},
            "pilot_reading_round_robin": {"decks": len(U), "pairings": len(pairs_rr),
                                          "games": len(pairs_rr) * GAMES_PER_PAIRING},
            "brew_reading": {"games": K * GAMES_PER_PAIRING,
                             "se_points_equal_weight": round(se_equal, 2),
                             "se_points_usage_weighted_same_games": round(se_weighted, 2),
                             "usage_weighted_effective_archetypes": round(1 / sum_w2, 1),
                             "share_proportional_allocation_same_total_min_games":
                                 int(round(min(w.values()) * K * GAMES_PER_PAIRING)),
                             "share_proportional_allocation_same_total_max_games":
                                 int(round(max(w.values()) * K * GAMES_PER_PAIRING)),
                             "weights": {a: round(v, 4) for a, v in w.items()}},
            "ladder_games_exact": lad_exact, "ladder_games_family": lad_family,
            "ladder_games_total": len(ladder),
            "ladder_opponents_not_covered_family": dict(lad_missed.most_common()),
        }

    levels = [
        level_stats("8 table decks", table_archs),
        level_stats("+ 6 held-out archetypes", table_archs + held_archs),
        level_stats("+ 2 ladder-panel lists", table_archs + held_archs + ladder_archs),
        level_stats("+ Energy-type additions", table_archs + held_archs + ladder_archs + add_archs),
        level_stats("+ the 2 biggest usage gaps", table_archs + held_archs + ladder_archs + add_archs
                    + growth[:2]),
        level_stats("+ all of usage top 18", table_archs + held_archs + ladder_archs + add_archs
                    + growth),
    ]
    for nm, lv in curve_levels.items():
        levels.append(level_stats("usage top %d (>= %d%% of lists)" % (lv["k"], int(lv["target"] * 100)),
                                  lv["archetypes"]))

    # ---------------------------------------------------------------- variation proposals
    G = list(gauntlet_archs)
    core8 = list(OrderedDict.fromkeys(table_archs))
    main_key = {a: (current_archs[a][0] if a in current_archs else None) for a in G}
    spread = []
    for a in G:
        v = var[a]
        t = next((x for x in v["tests"] if x["key"] == main_key[a]), None)
        spread.append({"archetype": a, "rank_lists": arch_index[a]["rank_lists"], "lists": v["lists"],
                       "modal_share": v["modal_share"], "median_cards_from_modal": v["median_cards_from_modal"],
                       "distinct_exact_lists": v["distinct_exact_lists"], "flex_slots": v["flex_slots"],
                       "main_list": t["file"] if t else None, "main_class": t["class"] if t else None})
    spread.sort(key=lambda x: (x["modal_share"], -x["lists"]))
    rr_pairs = len(G) * (len(G) - 1) // 2
    # Proposal A: a second ("twin") list for every gauntlet archetype whose modal list covers
    # under half of its lists; twins play the other archetypes' main lists in the large gauntlet only.
    setA = [x["archetype"] for x in spread if x["modal_share"] < 0.5]

    def opps_core(a):
        return len([c for c in core8 if c != a])

    propA = {
        "rule": "twin for every gauntlet archetype whose modal exact list is under 50% of its lists",
        "archetypes": setA,
        "twins_already_on_file": [a for a in setA if len(current_archs.get(a, [])) > 1],
        "gauntlet_round_robin": {"archetypes": len(G), "pairings": rr_pairs,
                                 "games": rr_pairs * GAMES_PER_PAIRING},
        "extra_vs_all_mains": {"pairings": len(setA) * (len(G) - 1),
                               "games": len(setA) * (len(G) - 1) * GAMES_PER_PAIRING},
        "extra_vs_core8_only": {"pairings": sum(opps_core(a) for a in setA),
                                "games": sum(opps_core(a) for a in setA) * GAMES_PER_PAIRING},
    }
    # Proposal B: a one-off sensitivity check on the most-used archetypes whose flex slots are
    # most spread out (modal list under 20% of lists, usage rank 15 or better): the twin plus up
    # to two single-card Trainer swaps, each played against the core 8 on the main list's seeds.
    setB = [x["archetype"] for x in spread if x["modal_share"] < 0.2 and x["rank_lists"] <= 15]
    rowsB = []
    for a in setB:
        t = next(x for x in var[a]["tests"] if x["key"] == main_key[a])
        variants = 1 + min(2, len(t["trainer_swaps_for_sensitivity"]))
        rowsB.append({"archetype": a, "main_list": t["file"], "variants": variants,
                      "opponents": opps_core(a),
                      "games": variants * opps_core(a) * GAMES_PER_PAIRING,
                      "twin": t["twin"], "swaps": t["trainer_swaps_for_sensitivity"][:2]})
    propA["recommended_subset"] = {
        "rule": "only the most-used spread-out archetypes: modal exact list under 20% of lists and "
                "usage rank <= 15 (the same set as proposal B)",
        "archetypes": setB,
        "twins_already_on_file": [a for a in setB if len(current_archs.get(a, [])) > 1],
        "extra_vs_all_mains": {"pairings": len(setB) * (len(G) - 1),
                               "games": len(setB) * (len(G) - 1) * GAMES_PER_PAIRING},
        "extra_vs_core8_only": {"pairings": sum(opps_core(a) for a in setB),
                                "games": sum(opps_core(a) for a in setB) * GAMES_PER_PAIRING},
    }
    propB = {"rule": "modal exact list under 20% of lists and usage rank <= 15; twin + up to 2 "
                     "single-card Trainer swaps, each vs the core 8 (7 for a core archetype)",
             "archetypes": rowsB,
             "games": sum(r["games"] for r in rowsB),
             "games_twin_only": sum(r["opponents"] * GAMES_PER_PAIRING for r in rowsB)}

    # ---------------------------------------------------------------- JSON
    usage_top = []
    for a in arch_rows[:40]:
        usage_top.append({k: a[k] for k in ("rank_lists", "archetype", "lists", "top8", "rank_top8",
                                             "events", "sept10_rank")}
                         | {"share": round(a["share"], 4), "top8_share": round(a["top8_share"], 4),
                            "energy": a["energy"]["types"], "energy_source": a["energy"]["source"],
                            "energy_stating_lists": a["energy"]["n_stating"],
                            "energy_combinations": a["energy"]["combinations"][:3],
                            "in_current_set": a["archetype"] in current_archs,
                            "repo_lists": archs_with_repo_list.get(a["archetype"], [])})
    out = {
        "title": "Gauntlet proposal: usage, Energy coverage, list variation (development half)",
        "date": "2026-09-26",
        "method": __doc__,
        "data": {"development_events": len(dev_ids), "holdout_events_not_opened": len(holdout_ids),
                 "standings_entries": n_entries, "entries_without_decklist": n_no_list,
                 "lists": N, "top8_finishes": N_TOP8,
                 "lists_not_20_cards": sum(1 for r in records if r["n"] != 20),
                 "lists_with_null_placing": sum(1 for r in records if r["placing"] is None),
                 "lists_stating_energy": sum(1 for r in records if r["energy"]),
                 "archetypes": len(arch_rows),
                 "matches_csv_development_rows": n_dev_rows,
                 "card_ids_not_in_database": dict(unknown_ids),
                 "smallest_event_players": min(e["players"] or 0 for e in events)},
        "energy_check_stated_vs_attackers": agree,
        "usage_top40": usage_top,
        "test_decks": [{"key": t["key"], "file": t["file"], "group": t["group"],
                        "archetype": t["archetype"], "deck_id": t["deck_id"],
                        "energy_line": t["energy_line"], "n_cards": t["n_cards"],
                        "archetype_energy": arch_index[t["archetype"]]["energy"]["types"],
                        "archetype_rank_lists": arch_index[t["archetype"]]["rank_lists"],
                        "archetype_lists": arch_index[t["archetype"]]["lists"],
                        "archetype_top8": arch_index[t["archetype"]]["top8"]}
                       for t in tests.values()],
        "research_copies_equal_t_files": research_check,
        "energy_coverage": coverage,
        "additions": additions,
        "optional_for_thin_types": optional_thin,
        "variation": var,
        "growth_candidates_usage_top18_not_in_gauntlet": growth,
        "variation_growth_candidates": var_growth,
        "variation_spread_ranking": spread,
        "proposal_A_twins": propA,
        "proposal_B_sensitivity": propB,
        "coverage_levels": levels,
        "cumulative_curve_top40": [{"rank": i + 1, "archetype": arch_rows[i]["archetype"],
                                    "cumulative_lists_share": round(curve[i], 4),
                                    "has_repo_list": arch_rows[i]["archetype"] in archs_with_repo_list}
                                   for i in range(40)],
        "repo_list_files": repo_lists,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    # ---------------------------------------------------------------- console summary
    d = out["data"]
    print("dev events %d, holdout not opened %d; entries %d, lists %d (no decklist %d); top-8 finishes %d"
          % (d["development_events"], d["holdout_events_not_opened"], d["standings_entries"], N,
             n_no_list, N_TOP8))
    print("lists not 20 cards: %d; null placing: %d; stating energy: %d; archetypes: %d; unknown ids: %s; smallest event %s"
          % (d["lists_not_20_cards"], d["lists_with_null_placing"], d["lists_stating_energy"],
             d["archetypes"], dict(unknown_ids), d["smallest_event_players"]))
    print("research copies equal t- files:", research_check)
    print("energy check:", agree["checked"], "checked,", agree["same"], "same,",
          agree["stated_includes_attackers"], "stated includes attackers;", "differs:",
          [(x["archetype"], x["lists"], x["stated"], x["attackers"]) for x in agree["differs"]])
    print()
    print("USAGE (development half)")
    for a in usage_top:
        print("%2d %-48s %4d %5.2f%%  t8 %3d (%5.2f%%, r%2d)  s10 %-4s %-22s %-8s stating %4d %s %s"
              % (a["rank_lists"], a["archetype"][:48], a["lists"], 100 * a["share"], a["top8"],
                 100 * a["top8_share"], a["rank_top8"], a["sept10_rank"] or "-",
                 "+".join(a["energy"]), a["energy_source"], a["energy_stating_lists"],
                 "CURRENT" if a["in_current_set"] else "",
                 ("repo:" + ",".join(os.path.basename(x) for x in a["repo_lists"])) if a["repo_lists"] else ""))
    print()
    print("TEST DECKS")
    for t in out["test_decks"]:
        print("  %-20s %-9s %-46s energy %-18s arch energy %-18s rank %d lists %d top8 %d"
              % (t["key"], t["group"], t["archetype"], "+".join(t["energy_line"]),
                 "+".join(t["archetype_energy"]), t["archetype_rank_lists"], t["archetype_lists"],
                 t["archetype_top8"]))
    print()
    print("ENERGY COVERAGE")
    for t, c in coverage.items():
        print("  %-9s %-8s decks %s" % (t, c["status"], c["test_decks"]))
        print("            %d archetypes of this type, %d lists; most used: %s" % (
            c["n_archetypes_of_type"], c["lists_of_type"],
            "; ".join("%s (r%d, %d lists, t8 %d, %s%s)" % (b["archetype"], b["rank_lists"], b["lists"],
                                                           b["top8"], "+".join(b["energy"]),
                                                           ", current" if b["in_current_set"] else "")
                      for b in c["most_used_archetypes_of_type"])))
        print("            single-type: %d archetypes, %d lists: %s" % (
            c["n_single_type_archetypes"], c["lists_single_type"],
            "; ".join("%s (r%d, %d, t8 %d%s)" % (b["archetype"], b["rank_lists"], b["lists"], b["top8"],
                                                  ", current" if b["in_current_set"] else "")
                      for b in c["most_used_single_type_archetypes"])))
        if "all_archetypes_of_type" in c:
            for b in c["all_archetypes_of_type"]:
                print("              %-46s r%-3d lists %2d t8 %d  %s  %s" % (
                    b["archetype"][:46], b["rank_lists"], b["lists"], b["top8"], "+".join(b["energy"]),
                    [(x["types"], x["lists"]) for x in b["energy_combinations"]]))
    print("ADDITIONS:", json.dumps(additions, ensure_ascii=False)[:3000])
    print("OPTIONAL (thin):", json.dumps(optional_thin, ensure_ascii=False))
    print()
    print("SPREAD:")
    for x in spread:
        print("  ", x)
    print("PROPOSAL A:", json.dumps(propA, ensure_ascii=False))
    print("PROPOSAL B:", json.dumps({k: v for k, v in propB.items() if k != "archetypes"}))
    for r in rowsB:
        print("   ", r["archetype"], r["variants"], r["opponents"], r["games"], "swaps:", r["swaps"])
    print()
    print("VARIATION (gauntlet, then growth candidates %s)" % growth)
    for arch, v in list(var.items()) + list(var_growth.items()):
        print("== %s: %d lists, %d distinct, modal %.1f%% (%d, ties %d), top3 %s, lists to cover half %s, median %s cards from modal, within 2: %.1f%%"
              % (arch, v["lists"], v["distinct_exact_lists"], 100 * v["modal_share"], v["modal_lists"],
                 v["modal_ties"], v["top3_exact_shares"], v["exact_lists_to_cover_half"],
                 v["median_cards_from_modal"], 100 * v["share_within_2_cards_of_modal"]))
        print("   core %d slots, flex %d; mean flex copies Pokemon %.2f Trainer %.2f"
              % (v["core_slots"], v["flex_slots"], v["mean_flex_copies_pokemon"], v["mean_flex_copies_trainer"]))
        print("   core:", "; ".join("%dx %s (%.0f%%)" % (c["core_count"], c["card"], 100 * c["lists_share_with_any"]) for c in v["core"]))
        print("   flex:", "; ".join("%s%s %.0f%%" % (a["card"], " (copy)" if a["what"] != "card" else "", 100 * a["lists_share"]) for a in v["flex_alternatives"]))
        print("   pokemon line: modal %.1f%%, %d distinct; top3 %s" % (
            100 * v["pokemon_line"]["modal_share"], v["pokemon_line"]["distinct"],
            [(x["share"], x["line"]) for x in v["pokemon_line"]["top3"]]))
        print("   trainer part: modal %.1f%%, %d distinct" % (100 * v["trainer_part"]["modal_share"], v["trainer_part"]["distinct"]))
        print("   modal list:", v["modal_list"], v["modal_list_evolution_problems"])
        rp = v["representative"]
        print("   representative:", rp["choice"], "| core+flex real copies", rp["core_plus_flex_real_copies"],
              "cards from modal", rp["core_plus_flex_cards_from_modal"], "problems", rp["core_plus_flex_evolution_problems"],
              "| medoid copies", rp["medoid_real_copies"], "from modal", rp["medoid_cards_from_modal"])
        if rp["choice"] != "modal":
            print("   core+flex list:", rp["core_plus_flex_list"])
        for t in v["tests"]:
            print("   TEST %s: class %s, exact %d (%.1f%%), %d cards from modal, pokemon line %.1f%%; rare %s"
                  % (t["key"], t["class"], t["exact_copies"], 100 * t["exact_share"], t["cards_from_modal"],
                     100 * t["pokemon_line_share"],
                     [(x["card"], x["count_in_test_list"], x["lists_share_same_count"]) for x in t["rare_choices"]]))
            print("        rarest:", [(x["card"], x["count_in_test_list"], x["lists_share_same_count"]) for x in t["rarest_choices"]])
            print("        vs modal: +", t["differs_from_modal"]["test_only"], " -", t["differs_from_modal"]["modal_only"])
            if t["twin"]:
                tw = t["twin"]
                print("        twin: %d lists (%.1f%%), %d cards away, modal=%s, adds %s removes %s"
                      % (tw["lists"], 100 * tw["share"], tw["cards_from_test"], tw["is_modal"], tw["adds"], tw["removes"]))
    print()
    print("COVERAGE LEVELS")
    for lv in levels:
        pr = lv["pilot_reading_vs_core8"]
        br = lv["brew_reading"]
        print("  %-36s k=%2d lists %5.1f%% top8 %5.1f%% | ladder exact %d/%d family %d | vs-core8 %d pairings %d games (%d checkable, eff %.1f) | RR %d decks %d games | brew %d games, SE eq %.2f wt %.2f eff %.1f, prop alloc min %d max %d"
              % (lv["level"], lv["k"], 100 * lv["lists_share"], 100 * lv["top8_share"],
                 lv["ladder_games_exact"], lv["ladder_games_total"], lv["ladder_games_family"],
                 pr["pairings"], pr["games"], pr["pairings_with_%d_plus_dev_matches" % LIMITLESS_CELL_MIN],
                 pr["usage_weighted_effective_pairings"],
                 lv["pilot_reading_round_robin"]["decks"], lv["pilot_reading_round_robin"]["games"],
                 br["games"], br["se_points_equal_weight"], br["se_points_usage_weighted_same_games"],
                 br["usage_weighted_effective_archetypes"],
                 br["share_proportional_allocation_same_total_min_games"],
                 br["share_proportional_allocation_same_total_max_games"]))
        print("      without repo list:", lv["without_repo_list"])
        print("      ladder not covered (family):", lv["ladder_opponents_not_covered_family"])
    print()
    print("CURVE")
    for x in out["cumulative_curve_top40"]:
        print("  %2d %-48s %5.1f%% %s" % (x["rank"], x["archetype"][:48], 100 * x["cumulative_lists_share"],
                                         "repo" if x["has_repo_list"] else ""))
    print()
    print("REPO LIST FILES")
    for x in repo_lists:
        print("  %-75s -> %-45s overlap %d exact %d %s" % (x["file"], x["nearest_archetype"], x["nearest_overlap"],
                                                         x["exact_dev_copies"],
                                                         ("(deck id: %s)" % x["archetype_by_deck_id"]) if x.get("archetype_by_deck_id") else ""))


if __name__ == "__main__":
    main()
