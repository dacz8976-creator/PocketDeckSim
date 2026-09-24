#!/usr/bin/env python3
"""Schema-based deck classifier for Pokémon TCG Pocket (DeckGym card ids).

Card layer : each card's attack/ability/trainer text -> mechanism FAMILIES (keyword rules), plus
             "implemented?" from the engine's effect->Mechanic maps (coverage only).
Deck layer : aggregate families over the 20 cards -> profile, structure metrics, labels,
             nearest neighbours (cosine on family vector), and a complement query
             ("what pairs with card X") for brewing.
Not a win-rate predictor. Rough by design.

usage: deck_classifier.py <database.json> <fork_src_dir> <decks.json> [more decks.json ...]
decks.json: {"deck name": {"energy": [...], "cards": {"B1 036": 2, ...}}, ...}
"""
import json, re, sys, math, collections, os

# ---------------------------------------------------------------- card layer
FAMILY_RULES = [  # (family, regex on lowercased effect text)
    ("STATUS_INFLICT", r"(opponent's active pokémon|defending pokémon|new active pokémon)[^.]*is now (poisoned|burned|asleep|paralyzed|confused)|make your opponent's active pokémon (poisoned|burned|asleep|paralyzed|confused)|both active pokémon are now|is chosen at random, and your opponent's active"),
    ("STATUS_AMP",    r"more damage from being poisoned|\+10 damage from being poisoned|if your opponent's active pokémon is (poisoned|burned|asleep|paralyzed|confused)|if the defending pokémon is (poisoned|asleep)"),
    ("STATUS_IMMUNE", r"can't be affected by (any )?special conditions|recovers from all special conditions|can't be asleep|can't be poisoned"),
    ("HEAL",          r"heal \d+ damage|heal all damage|recover"),
    ("DMG_REDUCE",    r"takes? -\d+ damage|prevent all damage|prevent all effects|less damage from attacks"),
    ("GUST",          r"switch in 1 of your opponent's benched|switch in 1 of your opponent's (damaged )?benched|your opponent switches|switch out your opponent's active"),
    ("SELF_SWITCH",   r"switch this pokémon with 1 of your benched|switch your active pokémon with|retreat cost is \d+ less|has no retreat cost|retreat cost of .* is 0|move this pokémon to your bench"),
    ("RETREAT_LOCK",  r"opponent's active pokémon'?s? retreat cost is \d+ more|opponent's active pokémon can't retreat|opponent's pokémon can't retreat"),
    ("BENCH_DMG",     r"damage to (1 of )?your opponent's benched|damage to each of your opponent's (benched )?pokémon|damage to each of your opponent's pokémon"),
    ("ENERGY_ACCEL",  r"attach (a|an|1|2) [^.]*energy from your energy zone|attach an energy from your discard|take a [^.]*energy from your energy zone and attach|move (a|an|all|1)[^.]*energy from"),
    ("ENERGY_DENIAL", r"discard (a|an|1|2|all) [^.]*energy from your opponent's|energy from your opponent's active pokémon to|opponent can't (take|attach) any energy|can't take any energy from their energy zone"),
    ("DRAW_SEARCH",   r"draw (a|\d+) card|put (a|1|2|all|random)[^.]*(from your deck|into your hand)|look at the top"),
    ("HAND_DISRUPT",  r"your opponent (shuffles|reveals|discards) (their|a random card from their|\d+ random cards? from their) hand|shuffles their hand into their deck"),
    ("POINT",         r"get (1|any) more point|can't get any points|1 more point"),
    ("ABILITY_LOCK",  r"have no abilities|has no ability|abilities are turned off"),
    ("HP_SET",        r"remaining hp is now 10|remaining hp is now"),
    ("DMG_SCALE",     r"more damage for each|does \d+ more damage for each|more damage for every"),
    ("COIN_GAMBLE",   r"flip (a|\d+) coins?|flip coins? until"),
    ("EVO_ACCEL",     r"evolve|evolution"),
    ("TOOL_SUPPORT",  r"pokémon tool|tool attached"),
    ("SELF_DMG",      r"does \d+ damage to itself"),
]
FAMILY_ORDER = [f for f, _ in FAMILY_RULES]

def families_from_text(text):
    t = (text or "").lower().replace("’", "'")
    return {f for f, rx in FAMILY_RULES if re.search(rx, t)}

def load_cards(db_path):
    db = json.load(open(db_path))
    cards = {}
    for e in db:
        kind, c = next(iter(e.items()))
        rec = {"id": c["id"], "name": c["name"], "kind": kind, "texts": []}
        if kind == "Pokemon":
            rec.update(energy_type=c["energy_type"], stage=c["stage"], hp=c["hp"], retreat=len(c["retreat_cost"]),
                       ex=" ex" in c["name"] or c["name"].endswith(" ex"), evolves_from=c.get("evolves_from"))
            rec["attacks"] = [{"cost": [x[0] for x in a["energy_required"]], "dmg": a.get("fixed_damage") or 0,
                               "effect": a.get("effect") or ""} for a in c["attacks"]]
            if c.get("ability"): rec["texts"].append(("ability", c["ability"]["effect"]))
            for a in c["attacks"]: rec["texts"].append(("attack", a.get("effect") or ""))
        else:
            rec.update(trainer_type=c.get("trainer_card_type") or kind)
            rec["texts"].append(("trainer", c.get("effect") or ""))
        rec["families"] = set()
        for _, tx in rec["texts"]: rec["families"] |= families_from_text(tx)
        if rec["kind"] == "Pokemon" and any(a["dmg"] >= 100 for a in rec["attacks"]): rec["families"].add("BIG_HIT")
        cards[rec["id"]] = rec
    return cards

def load_engine_coverage(src_dir):
    """effect text -> mechanic name from the fork's maps (implemented-ness signal only)."""
    cov = {}
    for fn, pat in [("actions/effect_mechanic_map.rs", r'"((?:[^"\\]|\\.)*)"\s*,\s*Mechanic::(\w+)'),
                    ("actions/effect_ability_mechanic_map.rs", r'map\.insert\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*AbilityMechanic::(\w+)')]:
        p = os.path.join(src_dir, fn)
        if os.path.exists(p):
            src = "\n".join(l for l in open(p, encoding="utf-8").read().splitlines() if not l.strip().startswith("//"))
            for txt, mech in re.findall(pat, src, re.S):
                cov[txt.replace('\\"', '"')] = mech
    return cov

# ---------------------------------------------------------------- deck layer
def deck_profile(deck, cards, cov):
    fam = collections.Counter(); unknown = []; unimpl = []
    pk = []; tr = []; typed_costs = collections.Counter(); ex_count = 0
    for cid, n in deck["cards"].items():
        c = cards.get(cid)
        if not c: unknown.append(cid); continue
        for f in c["families"]: fam[f] += n
        if c["kind"] == "Pokemon":
            pk.append((c, n)); ex_count += n if c["ex"] else 0
            for a in c["attacks"]:
                for e in a["cost"]:
                    if e not in ("C",): typed_costs[e] += 1
            for kind, tx in c["texts"]:
                if tx and kind in ("ability", "attack") and tx not in cov: unimpl.append(f"{c['name']} ({kind})")
        else:
            tr.append((c, n))
    n_pk = sum(n for _, n in pk); n_tr = sum(n for _, n in tr)
    basics = sum(n for c, n in pk if c["stage"] == 0)
    stage2 = sum(n for c, n in pk if c["stage"] == 2)
    candy = deck["cards"].get("A3 144", 0)
    # attacker metrics: best damage-per-energy among attacks
    best = (0, None); best_dpe = 0.0
    for c, n in pk:
        for a in c["attacks"]:
            if a["dmg"] > best[0]: best = (a["dmg"], c["name"])
            if a["cost"]: best_dpe = max(best_dpe, a["dmg"] / len(a["cost"]))
    energy = [e[0] for e in deck.get("energy", [])]
    typed_off = [e for e in typed_costs if e not in energy and e != "C"]
    denial = sum(fam[f] for f in ("STATUS_INFLICT", "RETREAT_LOCK", "ENERGY_DENIAL", "ABILITY_LOCK", "GUST", "HAND_DISRUPT", "POINT"))
    durab  = sum(fam[f] for f in ("HEAL", "DMG_REDUCE", "STATUS_IMMUNE"))
    snipe  = sum(fam[f] for f in ("BENCH_DMG", "GUST", "HP_SET"))
    speed  = fam["ENERGY_ACCEL"] + fam["DRAW_SEARCH"] + candy
    labels = []
    if durab >= 6 or (durab >= 4 and best_dpe <= 35): labels.append("WALL")
    if denial >= 5: labels.append("DENIAL/CONTROL")
    if fam["STATUS_INFLICT"] >= 3 or (fam["STATUS_INFLICT"] >= 2 and fam["STATUS_AMP"] >= 1): labels.append("STATUS-LOCK")
    if snipe >= 3: labels.append("SNIPE")
    if best[0] >= 80 and best_dpe >= 40 and basics >= n_pk * 0.5: labels.append("AGGRO")
    if fam["DMG_SCALE"] >= 2 and best[0] >= 100: labels.append("SCALING-HITTER")
    if fam["ENERGY_ACCEL"] >= 2: labels.append("RAMP")
    if sum(1 for _, n in pk if n == 1) >= 4: labels.append("TOOLBOX")
    if not labels: labels.append("MIDRANGE")
    risks = []
    if len(energy) > 1: risks.append(f"{len(energy)} energy types")
    if typed_off: risks.append(f"typed costs outside declared energy: {','.join(typed_off)}")
    if stage2 and not candy: risks.append("Stage 2 line without Rare Candy")
    if any(n == 1 and c["stage"] >= 1 for c, n in pk): risks.append("1-of evolution piece")
    if n_pk <= 5: risks.append("very thin Pokémon count")
    if ex_count >= 5: risks.append("ex-heavy (2-point KOs)")
    return {"fam": fam, "n_pk": n_pk, "n_tr": n_tr, "basics": basics, "stage2": stage2, "candy": candy,
            "ex": ex_count, "best": best, "best_dpe": round(best_dpe, 1), "denial": denial, "durab": durab,
            "snipe": snipe, "speed": speed, "labels": labels, "risks": risks, "unknown": unknown,
            "unimplemented": sorted(set(unimpl))}

GENERIC = {"DRAW_SEARCH", "COIN_GAMBLE", "EVO_ACCEL", "TOOL_SUPPORT", "SELF_DMG"}
IDENTITY = [f for f in FAMILY_ORDER + ["BIG_HIT"] if f not in GENERIC]
def vec(fam): return [fam.get(f, 0) for f in IDENTITY]
def cosine(a, b):
    na, nb = math.sqrt(sum(x*x for x in a)), math.sqrt(sum(x*x for x in b))
    return 0.0 if not na or not nb else sum(x*y for x, y in zip(a, b)) / (na * nb)

# ---------------------------------------------------------------- complement query
COMPLEMENTS = {  # family of the queried card -> (family that pairs with it, why)
    "STATUS_INFLICT": [("STATUS_AMP", "amplifies or cashes in the condition"), ("RETREAT_LOCK", "keeps the afflicted Pokémon in the Active Spot"), ("GUST", "drags the target you want afflicted into the Active Spot")],
    "STATUS_AMP":     [("STATUS_INFLICT", "supplies the condition it amplifies")],
    "STATUS_IMMUNE":  [("STATUS_INFLICT", "lets you run status pressure without eating the mirror")],
    "RETREAT_LOCK":   [("DMG_SCALE", "retreat-cost- and energy-scaled damage grows with the lock"), ("STATUS_INFLICT", "trapped Pokémon can't shed the condition")],
    "GUST":           [("BENCH_DMG", "soften the bench, then pull the damaged one up"), ("HP_SET", "pull the target you can finish")],
    "BENCH_DMG":      [("GUST", "finish what the spread damaged")],
    "ENERGY_DENIAL":  [("RETREAT_LOCK", "a stranded, energy-less Active can't leave"), ("DMG_REDUCE", "buy the turns denial needs")],
    "ENERGY_ACCEL":   [("BIG_HIT", "gets the expensive attack online early")],
    "DMG_REDUCE":     [("HEAL", "reduction plus healing is super-additive"), ("STATUS_INFLICT", "stall while the condition ticks")],
    "HEAL":           [("DMG_REDUCE", "reduction plus healing is super-additive")],
    "ABILITY_LOCK":   [("BIG_HIT", "the lock also frees your own drawback abilities (Regigigas)")],
    "HP_SET":         [("STATUS_INFLICT", "any tick finishes a 10-HP target at Checkup"), ("BENCH_DMG", "chip finishes it")],
    "POINT":          [("DMG_REDUCE", "point tricks want long games")],
    "DMG_SCALE":      [("RETREAT_LOCK", "if it scales with retreat cost"), ("ENERGY_ACCEL", "if it scales with energy")],
}

def complement_query(cid, cards, limit=12):
    c = cards[cid]; out = []
    for f in sorted(c["families"]):
        for g, why in COMPLEMENTS.get(f, []):
            hits = [x for x in cards.values() if g in x["families"] and x["name"] != c["name"]]
            # prefer base printings: dedupe by name
            seen = set(); uniq = []
            for x in sorted(hits, key=lambda x: (x["id"].split(" ")[0], x["id"])):
                if x["name"] in seen: continue
                seen.add(x["name"]); uniq.append(x)
            out.append((f, g, why, [f"{x['name']} {x['id']}" for x in uniq[:limit]], len(uniq)))
    return out

SET_ORDER = ["P-A","A1","A1a","A2","A2a","A2b","A3","A3a","A3b","A4","A4a","A4b","B1","B1a","B2","B2a","B2b","B3","B3a","B3b","B4","B4a"]
def set_rank(cid): 
    s = cid.split(" ")[0]; return SET_ORDER.index(s) if s in SET_ORDER else -1

def suggest_for_deck(deck, cards, per=5):
    """For each identity family the deck already has, list complement cards it could add:
    same energy type (or Colorless / Trainer), not already in the deck, newest sets first."""
    energy = set(deck.get("energy", [])); have = set(deck["cards"]); have_names = {cards[c]["name"] for c in have if c in cards}
    fam = collections.Counter()
    for cid, n in deck["cards"].items():
        if cid in cards:
            for f in cards[cid]["families"]: fam[f] += n
    out = []
    for f, _ in fam.most_common():
        if f in GENERIC: continue
        for g, why in COMPLEMENTS.get(f, []):
            if fam.get(g, 0) >= 2: continue  # already has that role
            pool = [x for x in cards.values() if g in x["families"] and x["name"] not in have_names
                    and (x["kind"] != "Pokemon" or x["energy_type"] in energy or x["energy_type"] == "Colorless")]
            seen = set(); uniq = []
            for x in sorted(pool, key=lambda x: (-set_rank(x["id"]), x["id"])):
                if x["name"] in seen: continue
                seen.add(x["name"]); uniq.append(x)
            if uniq: out.append((f, g, why, [f"{x['name']} {x['id']}" for x in uniq[:per]]))
    return out

# ---------------------------------------------------------------- main
def fmt_profile(name, deck, p):
    top = ", ".join(f"{f}×{n}" for f, n in p["fam"].most_common(6))
    s = [f"## {name}  [{', '.join(deck.get('energy', []))}]  → {' + '.join(p['labels'])}",
         f"   {p['n_pk']} Pokémon / {p['n_tr']} Trainers · basics {p['basics']} · stage-2 {p['stage2']} · candy {p['candy']} · ex {p['ex']} · best hit {p['best'][0]} ({p['best'][1]}) · best dmg/energy {p['best_dpe']}",
         f"   families: {top or '—'}",
         f"   denial {p['denial']} · durability {p['durab']} · snipe {p['snipe']} · setup {p['speed']}"]
    if p["risks"]: s.append(f"   risks: {'; '.join(p['risks'])}")
    if p["unimplemented"]: s.append(f"   not in engine maps: {', '.join(p['unimplemented'][:6])}")
    if p["unknown"]: s.append(f"   unknown ids: {p['unknown']}")
    return "\n".join(s)

if __name__ == "__main__":
    args=[a for a in sys.argv[1:] if not a.startswith("query=")]
    db_path, src_dir, *deck_files = args
    cards = load_cards(db_path); cov = load_engine_coverage(src_dir)
    decks = {}
    for f in deck_files: decks.update(json.load(open(f)))
    profiles = {n: deck_profile(d, cards, cov) for n, d in decks.items()}
    print(f"# cards loaded {len(cards)} · engine-mapped effect texts {len(cov)} · decks {len(decks)}\n")
    for n, d in decks.items():
        print(fmt_profile(n, d, profiles[n]))
        if not n.startswith("T-"):
            for f, g, why, hits in suggest_for_deck(d, cards)[:4]:
                print(f"   + {f}→{g} ({why}): {', '.join(hits)}")
        print()
    print("# nearest neighbours (cosine on family vector)")
    names = list(decks)
    for a in names:
        sims = sorted(((cosine(vec(profiles[a]['fam']), vec(profiles[b]['fam'])), b) for b in names if b != a), reverse=True)[:2]
        print(f"   {a:45s} ~ " + " | ".join(f"{b} ({s:.2f})" for s, b in sims))
    q = [a for a in sys.argv if a.startswith("query=")]
    for a in q:
        cid = a.split("=", 1)[1]
        print(f"\n# complements for {cards[cid]['name']} {cid}  (families: {', '.join(sorted(cards[cid]['families'])) or 'none'})")
        for f, g, why, hits, total in complement_query(cid, cards):
            print(f"   {f} → {g}: {why}  [{total} cards] e.g. {', '.join(hits[:10])}")
