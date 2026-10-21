#!/usr/bin/env python3
"""reach_scan.py - deck reach of the Oct 20 hit-back ruling (the hit back left by Cursed Jewel, Spike Armor,
Bristling Spikes, Needle Lariat, Shell Trap counts as ATTACK damage for every card on the Pokemon it hits).

Question: which recorded results could the port move? A game can change only if a hit-back holder's attack is used
(holder side) AND the Pokemon that then attacks into the holder carries one of the newly-applying receiving-side items
(Rocky Helmet, Heavy Helmet, damage cuts, prevention, on-damage / on-KO triggers). Holder-side items (Lucky Mittens,
open-question boosts) and the port traps (T1-T4 of the census) are reported too.

READ-ONLY. It reads the repository only through `git ls-tree`, `git cat-file --batch` and `git show` at one commit
(default c1670e81), plus `git show` of the kx3 branch for kx3's pool. No checkout, no build, no game.

Run (inside WSL):  python3 reach_scan.py [--commit c1670e81] [--out DIR]
Writes DIR/reach_report.txt (default: the folder this script sits in).
Item ids are the census agent's lists (Oct 20, hb/census); the script re-derives each group from database.rs by its
ability / attack / trainer name and prints any id the census did not list.
"""
import argparse, collections, json, os, re, subprocess, sys

REPO = "/home/dacz8976/pincand"
KX3_REFS = ["laptop/kx3-on-engine-candidate-2026-10-20", "origin/laptop/kx3-on-rules2"]

ap = argparse.ArgumentParser()
ap.add_argument("--commit", default="c1670e81")
ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
A = ap.parse_args()
C = A.commit
OUT = []


def p(*a):
    OUT.append(" ".join(str(x) for x in a))


def git(*args, binary=False):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


def cat_many(paths):
    """Read many blobs at commit C in one git cat-file --batch call."""
    if not paths:
        return {}
    inp = "".join(f"{C}:{x}\n" for x in paths).encode()
    r = subprocess.run(["git", "-C", REPO, "cat-file", "--batch"], input=inp, capture_output=True, check=True).stdout
    res, i = {}, 0
    for x in paths:
        nl = r.index(b"\n", i)
        hdr = r[i:nl].decode()
        i = nl + 1
        if hdr.endswith("missing"):
            res[x] = None
            continue
        size = int(hdr.split()[-1])
        res[x] = r[i:i + size].decode("utf-8", "replace")
        i += size + 1
    return res


# ---------------------------------------------------------------- card database (database.rs at C)
DB_TEXT = git("show", f"{C}:engine/src/database.rs")
STR = r'"((?:[^"\\]|\\.)*)"'
DB = {}
starts = [m.start() for m in re.finditer(r"map\.insert\(", DB_TEXT)]
for k, s in enumerate(starts):
    chunk = DB_TEXT[s:(starts[k + 1] if k + 1 < len(starts) else len(DB_TEXT))]
    idm, nm = re.search(r"\bid:\s*" + STR, chunk), re.search(r"\bname:\s*" + STR, chunk)
    if not idm:
        continue
    c = {"id": idm.group(1), "name": nm.group(1) if nm else "?", "line": DB_TEXT.count("\n", 0, s) + 1,
         "kind": "Pokemon" if "Card::Pokemon" in chunk else ("Trainer" if "Card::Trainer" in chunk else "?")}
    if c["kind"] == "Pokemon":
        ab = re.search(r"ability:\s*Some\(Ability\s*\{\s*title:\s*" + STR + r"\.to_string\(\),\s*effect:\s*" + STR, chunk, re.S)
        c["ability"] = ab.group(1) if ab else None
        c["ability_text"] = ab.group(2) if ab else None
        c["attacks"] = []
        for am in re.finditer(r"Attack\s*\{(.*?)\n\s*\}", chunk, re.S):
            t = re.search(r"title:\s*" + STR, am.group(1))
            if t:
                c["attacks"].append(t.group(1))
        st, rc, et = re.search(r"stage:\s*(\d+)", chunk), re.search(r"retreat_cost:\s*vec!\[(.*?)\]", chunk, re.S), \
            re.search(r"energy_type:\s*EnergyType::(\w+)", chunk)
        c["stage"] = int(st.group(1)) if st else None
        c["retreat"] = len(re.findall(r"EnergyType::\w+", rc.group(1))) if rc else None
        c["type"] = et.group(1) if et else None
    else:
        tt = re.search(r"trainer_card_type:\s*TrainerType::(\w+)", chunk)
        c["ttype"] = tt.group(1) if tt else None
    DB[c["id"]] = c
p(f"reach_scan.py at commit {C}: database.rs has {len(DB)} cards")


def nm(i):
    return f"{DB[i]['name']} {i}" if i in DB else f"?? {i}"


# ---------------------------------------------------------------- the census lists (verbatim ids)
def ids(s):
    out = []
    for t in s.split(","):
        t = t.strip()
        if t:
            out.append(t)
    return out


HOLDERS = {  # id: (attack, hit back)
    "A3 039": ("Spike Armor", 40), "A3b 048": ("Bristling Spikes", 30), "P-A 090": ("Bristling Spikes", 30),
    "B1 047": ("Shell Trap", 20), "B2 010": ("Needle Lariat", 80),
    "B3b 041": ("Cursed Jewel", 40), "B3b 081": ("Cursed Jewel", 40), "B3b 088": ("Cursed Jewel", 40)}

# (key, census row, label, kind of name, ids, verdict, condition)
# verdict: IN = brought in by the ruling; ALREADY = fires today already; NEVER = not by text (port trap);
#          UNCHANGED = not keyed on attacks; HOLDER_IN / HOLDER_OPEN = on the holder's side; FIX = bug fix, not ruling
RECV = [
    ("heavy_helmet", "a1", "Heavy Helmet", "trainer", ids("B1 219"), "IN", "rc3"),
    ("steel_apron", "a2", "Steel Apron", "trainer", ids("A4 153"), "IN", "metal"),
    ("metal_core_barrier", "a3", "Metal Core Barrier", "trainer", ids("B2 148, B2b 117"), "IN", "metal"),
    ("shell_armor", "a4", "Shell Armor -10", "ability", ids("A1 067, P-B 059"), "IN", None),
    ("hard_coat", "a4", "Hard Coat -20", "ability", ids("A1 182"), "IN", None),
    ("exoskeleton", "a4", "Exoskeleton -20", "ability", ids("A2 087, A4a 044"), "IN", None),
    ("fur_coat", "a4", "Fur Coat -20", "ability", ids("A3 109, B1 206, B1 207, B1 208, B1a 065, B2 141, B2b 064, B3 144, B3b 061, B4 142, B4a 064"), "IN", None),
    ("solid_shell", "a4", "Solid Shell -20", "ability", ids("A4 021, A4 186, A4 202, A4b 023"), "IN", None),
    ("armor", "a4", "Armor -30", "ability", ids("B2a 020, B2a 101, B2a 111, B3a 105"), "IN", None),
    ("thick_fat", "a5", "Thick Fat", "ability", ids("A2 032, A2 033, A2 160, A4 050"), "IN", "fire_water_holder"),
    ("def_whirlwind", "a5", "Defensive Whirlwind", "ability", ids("P-A 047"), "IN", "fighting_holder"),
    ("resilience_link", "a6", "Resilience Link -30", "ability", ids("A2a 026, A2a 055, P-A 044"), "IN", "arceus"),
    ("ice_face", "a7", "Ice Face -40", "ability", ids("B1 080, B1 236"), "IN", None),
    ("unown_guard", "a8", "Unown GUARD -10", "ability", ids("A4 084"), "IN", "other_unown"),
    ("coordinated_unit", "a9", "Coordinated Unit -20", "ability", ids("B2 092, B2 172, B4 215"), "IN", "two_falinks"),
    ("intimidating_fang", "a10", "Intimidating Fang -20 (arguable)", "ability", ids("A3a 015"), "IN", None),
    ("coin_cut", "a13", "Guarded Grill / Securely Sheltered (coin)", "ability", ids("A2 114, B3b 050"), "IN", None),
    ("safeguard", "b1", "Safeguard", "ability", ids("A3 066, A3 165, A4b 146, A4b 147, B1 303"), "IN", "ex_holder"),
    ("disguise", "b2", "Disguise", "ability", ids("B2 073, B2 186, B2 199, B4a 107"), "IN", None),
    ("stance", "b3", "Stance", "ability", ids("B4 044, B4 163"), "IN", None),
    ("coin_prevent", "b4", "Celestial Blessing / Carefree Steps (coin)", "ability", ids("A4 080, B2 124, B2 204"), "IN", None),
    ("poncho", "b5", "Protective Poncho", "trainer", ids("B2 147, B2 234"), "IN", "self_switch"),
    ("shell_shield", "b6", "Shell Shield (cannot happen in practice)", "ability", ids("B1a 018"), "IN", "never_practice"),
    ("rocky_helmet", "c1", "Rocky Helmet", "trainer", ids("A2 148, A4b 322, A4b 323"), "IN", None),
    ("counterattack_ab", "c2", "Counterattack / Rough Skin / Steel Spikes / Automated Combat (20 back)", "ability",
     ids("A1 061, B1 297, A2b 028, P-A 054, A4a 065, A1a 056, A3a 052, B3a 046"), "IN", None),
    ("poison_barb", "c3", "Poison Barb", "trainer", ids("A3 146"), "IN", None),
    ("poison_point", "c3", "Poison Point", "ability", ids("B1 160, B1 263, B1 281, B3 231"), "IN", None),
    ("bouncy_body", "c4", "Bouncy Body", "ability", ids("B1 069, B1 234, B3 210"), "IN", None),
    ("dark_pendant", "c5", "Dark Pendant", "trainer", ids("A4 154"), "IN", "dark"),
    ("guts", "c6", "Guts (coin)", "ability", ids("A3 096, B3b 058"), "IN", None),
    ("perish_body", "c7", "Perish Body (coin)", "ability", ids("A4a 035"), "IN", None),
    ("ko_damage", "c8", "Innards Out / Final Scream / Destiny Burst", "ability", ids("A3 054, A3 163, A4a 097, B2 103, B4a 020"), "IN", None),
    ("offload_pass", "c9", "Offload Pass", "ability", ids("A3 104, A3 187, A3 205, A4b 223, B1 324"), "IN", None),
    ("lucky_egg", "c10", "Lucky Egg", "trainer", ids("B3 148"), "IN", None),
    ("rescue_scarf", "c11", "Rescue Scarf", "trainer", ids("A4 155"), "IN", None),
    ("electrical_cord", "c12", "Electrical Cord (fires today already)", "trainer", ids("A3a 065, A4b 318, A4b 319"), "ALREADY", None),
    ("hala", "c13", "Hala (fires today, wrongly; NEVER by text)", "trainer", ids("B1 222, B1 267"), "FIX", None),
    ("ko_points_coin", "c15", "Fade into Darkness / Shattering Crystal (any KO)", "ability", ids("B1 105, B3a 045, B3a 078"), "UNCHANGED", None),
    ("reply_strongly", "c16", "Reply Strongly", "attack", ids("A4 086, A4 175"), "NEVER", None),
]
TRAPS_RECV = [  # on the receiver's side; must NOT move (port traps)
    ("t1_selfcut", "a11/T1", "attack self-cuts (Guard Press, Stiffen, Steel Wing, ...)", "attack", ids(
        "A1 126, A1a 045, A4 104, B1 119, B1 309, A2 117, A3 043, B1 167, B1a 093, B2 003, A2 073, A2 165, B3b 052, "
        "A2a 057, A2a 085, A2a 094, A4b 253, A3 086, A4b 182, A4b 183, A3a 053, P-A 080, A4 124, A4 194, A4 209, A4b 252, "
        "B1 075, B1 117, B1 175, B1 246, B1a 052, B1a 080, B1a 086, B3 232, B1a 056, B3 222, P-B 037, B2 093, B2 120, "
        "B3 116, B4a 056, B3a 054"), "NEVER", None),
    ("t1_hide", "b7/T1", "Hide / Dig / Fly family", "attack", ids(
        "A1 140, B1a 038, B3 211, A1a 024, A4 058, A2 042, A2 058, A2 163, B2 074, B4a 100, P-B 072, A2b 036, A2b 056, "
        "A2b 106, A3 069, A3b 042, A4 044, B2a 022, P-B 033, A4 131, A4 141, B2a 071, B3a 052, B4 139, B3 016, P-B 064, "
        "B4 128, B4 177, B4a 062, B4a 076, P-A 045"), "NEVER", None),
    ("t1_harden", "b8/T1", "Harden", "attack", ids("B1 004, B1 006"), "NEVER", None),
    ("t1_blocking", "b9/T1", "Blocking Shell", "attack", ids("B1 067"), "NEVER", None),
    ("t1_vuln", "d3/T1", "Clanging Scales / Close Combat / Pivot Throw (+damage taken)", "attack", ids("A3 127, B3 080, B4 080"), "NEVER", None),
    ("t1_next_turn_protect", "b10", "Illusive Trickery / Mach Stealth", "ability", ids("A4a 050, P-A 106, B4a 054"), "NEVER", None),
    ("t2_supporter_cut", "a12/T2", "Blue / Adaman / Jasmine / Cheren / Beast Wall", "trainer", ids(
        "A1a 067, A1a 081, A2a 075, A2a 090, A4 160, A4 200, B3 151, B3 192, A3a 063"), "NEVER", None),
    ("t3_growl", "T3", "Growl family (cut put on the holder)", "attack", ids(
        "A1 151, A1 239, A3 226, A4b 194, A4b 195, B3b 026, B4 049, P-A 030, P-B 082, A2a 030, A4 059, A4 078, A4 173, "
        "B3b 056, B4 134, B3 078, B3 168"), "NEVER", None),
    ("t3_supporter_boost", "T3", "Giovanni / Red (unscoped turn boosts)", "trainer_name", ["Giovanni", "Red"], "NEVER", None),
    ("t1_own_counterattack", "c14/T1", "the receiver's own new Counterattack (a holder attacking into a holder)", "attack",
     sorted(HOLDERS), "NEVER", None),
    ("hala_dup", None, None, None, [], None, None),
]
TRAPS_RECV = [t for t in TRAPS_RECV if t[1]]
HOLDER_SIDE = [
    ("lucky_mittens", "holder", "Lucky Mittens on the holder", "trainer", ids("B1 220"), "HOLDER_IN", None),
    ("cursed_metal", "holder", "Cursed Metal (Aegislash) +30 [P]/[M]", "ability", ids("B1 172, B1a 102"), "HOLDER_OPEN", "metal_holder"),
    ("unown_power", "holder", "Unown POWER +10", "ability", ids("A4 085"), "HOLDER_OPEN", None),
    ("training_area", "either", "Training Area +10 for Stage 1 (Stadium, both sides)", "trainer", ids("B2 153"), "HOLDER_OPEN", "stage1_holder"),
    ("t4_vengeance", "holder", "vengeance attacks (T4 false trigger on the holder's next turn)", "attack", ids(
        "A1a 047, A1a 074, A4b 224, A4b 225, B1a 064, A3 077, A4b 178, A4b 179, B2a 021, B2a 033, P-B 036, B2b 017, "
        "B2b 070, B3 061, B3 114, P-B 060, B3a 028, B4 142"), "NEVER", None),
    ("sophocles", "receiver", "Sophocles (names Togedemaru; T3)", "trainer_name", ["Sophocles"], "NEVER", "togedemaru_holder"),
]
SELF_SWITCH = set(ids("A3 068, A3 166, A4 018, A4 212, A4a 002, B1 072, B2a 006, B2a 023, B2b 001, B2b 087, B2b 038, "
                      "B2b 101, B3 098, B3 212, B3 120, B3 176, B4 096, B4a 042"))
RETREAT_CHANGERS = ["Peculiar Plaza", "Small Balloon", "Inflatable Boat", "Big Air Balloon"]

# trainer_name rows -> ids by name
for table in (TRAPS_RECV, HOLDER_SIDE):
    for k, row in enumerate(table):
        if row[3] == "trainer_name":
            names = row[4]
            got = sorted(i for i, c in DB.items() if c["kind"] == "Trainer" and c["name"] in names)
            table[k] = (row[0], row[1], row[2], "trainer", got, row[5], row[6])

ALL_GROUPS = RECV + TRAPS_RECV + HOLDER_SIDE
ID2GROUPS = collections.defaultdict(list)
for g in ALL_GROUPS:
    for i in g[4]:
        ID2GROUPS[i].append(g)

# ---------------------------------------------------------------- 0. completeness check of the census ids
p("\n== 0. Census id lists re-derived from database.rs (by ability / attack / trainer name) ==")


def keys_of(i, kind):
    c = DB.get(i)
    if not c:
        return set()
    if kind == "trainer":
        return {("t", c["name"])} if c["kind"] == "Trainer" else set()
    if kind == "ability":
        return {("ab", c["ability"])} if c.get("ability") else set()
    if kind == "attack":
        return {("at", t) for t in c.get("attacks") or []}
    return set()


bad = 0
for g in ALL_GROUPS:
    key, row, label, kind, gid = g[0], g[1], g[2], g[3], g[4]
    missing_db = [i for i in gid if i not in DB]
    if missing_db:
        p(f"  {label}: ids not in database.rs: {missing_db}")
        bad += 1
    # union of keys of the group's ids; then every db card with any of those keys
    ks = set()
    for i in gid:
        ks |= keys_of(i, kind)
    if kind == "attack":  # keep only attack titles shared by at least 1 id AND not generic (appear in the group)
        # restrict to the title(s) each id has in common with some other id of the group, else its own titles
        cnt = collections.Counter(t for i in gid for t in keys_of(i, kind))
        ks = {t for t in ks if cnt[t] >= 1}
    extra = sorted(i for i, c in DB.items() if i not in gid and keys_of(i, kind) & ks)
    if kind == "attack":
        # attack titles are generic (e.g. "Revenge"); report extras only as information
        if extra:
            p(f"  {label}: other cards with the same attack title(s) {sorted(t for _, t in ks)[:6]}...: "
              + ", ".join(nm(i) for i in extra[:40]) + (" ..." if len(extra) > 40 else ""))
    elif extra:
        bad += 1
        p(f"  {label}: NOT in the census list but same {kind} name: " + ", ".join(nm(i) for i in extra))
p(f"  ({bad} trainer/ability groups with ids outside the census list; attack-title extras are information only)")

# ---------------------------------------------------------------- 1. deck lists at C
LINE = re.compile(r"^\s*(\d+)\s*[xX]?\s+(?:(.+?)\s+)?((?:P-[AB])|(?:[AB]\d[a-z]?))\s*[- ]\s*(\d{1,3})\s*$")


def parse_list(text):
    cards, unresolved = collections.Counter(), []
    energy = None
    for raw in text.splitlines():
        s = raw.strip().lstrip("﻿")
        if s.lower().startswith("energy:"):
            energy = s.split(":", 1)[1].strip()
            continue
        m = LINE.match(s)
        if not m:
            continue
        cid = f"{m.group(3)} {int(m.group(4)):03d}"
        if cid not in DB:
            unresolved.append(s)
        cards[cid] += int(m.group(1))
    return cards, energy, unresolved


tree = git("ls-tree", "-r", "--name-only", C).splitlines()
txts = [x for x in tree if x.endswith(".txt")]
blobs = cat_many(txts)
DECKS = {}
for path in txts:
    t = blobs.get(path)
    if t is None:
        continue
    cards, energy, unres = parse_list(t)
    n = sum(cards.values())
    if len(cards) >= 3 and (energy is not None or 15 <= n <= 20):
        DECKS[path] = {"cards": cards, "energy": energy, "n": n, "unresolved": unres}
p(f"\n== 1. Deck lists: {len(DECKS)} committed .txt files at {C} parse as deck lists (>=3 card lines and an Energy line or 15-20 cards) ==")


def deck_profile(cards):
    """Holders, receiving items, traps and attributes of one list (a Counter of ids)."""
    prof = {"holders": [], "items": collections.defaultdict(list), "metal": [], "dark": [], "rc3": [], "self_switch": [],
            "arceus": [], "unown_other": [], "falinks": 0, "retreat_changers": [], "names": {}}
    for i, n in cards.items():
        c = DB.get(i)
        if not c:
            continue
        if i in HOLDERS:
            prof["holders"].append(i)
        for g in ID2GROUPS.get(i, []):
            prof["items"][g[0]].append(f"{n}x {nm(i)}")
        if c["kind"] == "Pokemon":
            if c.get("type") == "Metal":
                prof["metal"].append(nm(i))
            if c.get("type") == "Darkness":
                prof["dark"].append(nm(i))
            if (c.get("retreat") or 0) >= 3:
                prof["rc3"].append(f"{nm(i)} (Retreat {c['retreat']})")
            if i in SELF_SWITCH:
                prof["self_switch"].append(nm(i))
            if "Arceus" in c["name"]:
                prof["arceus"].append(nm(i))
            if c["name"] == "Unown" and i != "A4 084":
                prof["unown_other"].append(nm(i))
            if c["name"] == "Falinks":
                prof["falinks"] += n
        elif c["name"] in RETREAT_CHANGERS:
            prof["retreat_changers"].append(nm(i))
    return prof


GROUP = {g[0]: g for g in ALL_GROUPS}


def cond_ok(cond, holder, recv_prof):
    """Can this item meet a hit back from `holder` when carried by a Pokemon of the receiving list?"""
    h = DB[holder]
    if cond is None:
        return True, ""
    if cond == "rc3":
        if recv_prof["rc3"]:
            return True, "Retreat>=3 in list: " + ", ".join(sorted(set(recv_prof["rc3"])))
        return False, "no Pokemon with Retreat 3 or more in the list"
    if cond == "metal":
        return (True, "[M] Pokemon: " + ", ".join(sorted(set(recv_prof["metal"])))) if recv_prof["metal"] else (False, "no [M] Pokemon")
    if cond == "dark":
        return (True, "[D] Pokemon: " + ", ".join(sorted(set(recv_prof["dark"])))) if recv_prof["dark"] else (False, "no [D] Pokemon")
    if cond == "fire_water_holder":
        return (h["type"] in ("Fire", "Water")), f"holder is {h['type']}"
    if cond == "fighting_holder":
        return (h["type"] == "Fighting"), f"holder is {h['type']}"
    if cond == "ex_holder":
        return h["name"].endswith(" ex"), f"holder {'is' if h['name'].endswith(' ex') else 'is not'} an ex"
    if cond == "self_switch":
        return (True, "self-switch attackers: " + ", ".join(sorted(set(recv_prof["self_switch"])))) if recv_prof["self_switch"] \
            else (False, "no self-switch attacker in the list, so no Benched receiver")
    if cond == "arceus":
        return bool(recv_prof["arceus"]), ("Arceus: " + ", ".join(recv_prof["arceus"])) if recv_prof["arceus"] else "no Arceus"
    if cond == "other_unown":
        return bool(recv_prof["unown_other"]), "other Unown: " + ", ".join(recv_prof["unown_other"]) if recv_prof["unown_other"] else "no other Unown"
    if cond == "two_falinks":
        return recv_prof["falinks"] >= 2, f"{recv_prof['falinks']} Falinks"
    if cond == "never_practice":
        return False, "only attack is Waterfall; no Squirtle line has a self-switch attack"
    if cond == "metal_holder":
        return h["type"] in ("Metal", "Psychic"), f"holder is {h['type']}"
    if cond == "stage1_holder":
        return h.get("stage") == 1, f"holder stage {h.get('stage')}"
    if cond == "togedemaru_holder":
        return h["name"] == "Togedemaru", f"holder is {h['name']}"
    return True, ""


def pair_reach(hold_cards, recv_cards):
    """Items on recv's side that a hit back from hold's holders would meet. Returns (reached, blocked, traps, holder_side)."""
    hp, rp = deck_profile(hold_cards), deck_profile(recv_cards)
    reached, blocked, traps, hside = [], [], [], []
    for hdr in sorted(set(hp["holders"])):
        for g in RECV:
            if g[0] in rp["items"]:
                ok, why = cond_ok(g[6], hdr, rp)
                rec = (g[1], g[2], g[5], ", ".join(rp["items"][g[0]]), nm(hdr), why)
                (reached if ok else blocked).append(rec)
        for g in TRAPS_RECV:
            if g[0] in rp["items"]:
                traps.append((g[1], g[2], ", ".join(rp["items"][g[0]]), nm(hdr)))
        for g in HOLDER_SIDE:
            where = g[1]
            src = []
            if where in ("holder", "either") and g[0] in hp["items"]:
                src.append("holder list: " + ", ".join(hp["items"][g[0]]))
            if where in ("receiver", "either") and g[0] in rp["items"]:
                src.append("receiving list: " + ", ".join(rp["items"][g[0]]))
            if src:
                ok, why = cond_ok(g[6], hdr, rp)
                hside.append((g[2], g[5], "; ".join(src), nm(hdr), ("applies" if ok else "cannot: ") + (why if not ok else (why or ""))))
    return reached, blocked, traps, hside


def short(path):
    return path


# per-deck summary for every list
p("\nLists holding a hit-back holder:")
holder_decks = []
for path, d in sorted(DECKS.items()):
    pr = deck_profile(d["cards"])
    if pr["holders"]:
        holder_decks.append(path)
        p(f"  {path}: " + ", ".join(f"{d['cards'][h]}x {nm(h)} ({HOLDERS[h][0]}, hit back {HOLDERS[h][1]})" for h in pr["holders"]))
p(f"  -> {len(holder_decks)} lists")

# ---------------------------------------------------------------- 2. tables
p("\n== 2. Per-deck holders and receiving-side items (focus lists) ==")
PANEL = sorted(x for x in DECKS if x.startswith("decks/screen/opponents/"))
RESEARCH = sorted(x for x in DECKS if x.startswith("decks/research/"))
FOCUS = ["decks/brews/brew-06-pyukumuku-silvally-payback.txt", "decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt",
         "decks/dustin/14-comfey-raticate-hypno.txt", "decks/brews/brew-05b-meowstic-hatterene-comfey.txt",
         "decks/dustin/07-skarmory-stall.txt", "decks/dustin/12-ariados-whimsicott-ogerpon.txt",
         "decks/brews/brew-07-hoopa-darkrai-sableye.txt", "decks/brews/brew-09-sableye-obstagoon.txt",
         "rl/results/engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt",
         "decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt"] + PANEL + RESEARCH
FOCUS += sorted(x for x in DECKS if (x.startswith("decks/dustin/") or x.startswith("decks/brews/") or x.startswith("decks/variants-")
                                     or x.startswith("decks/computer/")) and x not in FOCUS)


def describe(path):
    d = DECKS[path]
    pr = deck_profile(d["cards"])
    hs = ", ".join(nm(h) for h in pr["holders"]) or "none"
    its = []
    for g in ALL_GROUPS:
        if g[0] in pr["items"]:
            its.append(f"[{g[1]} {g[5]}] {g[2]}: " + ", ".join(pr["items"][g[0]]))
    return hs, its, pr, d


for path in FOCUS:
    if path not in DECKS:
        p(f"  {path}: NOT FOUND at {C}")
        continue
    hs, its, pr, d = describe(path)
    extra = []
    if pr["rc3"]:
        extra.append("Retreat>=3: " + ", ".join(sorted(set(pr["rc3"]))))
    if pr["retreat_changers"]:
        extra.append("retreat changers: " + ", ".join(pr["retreat_changers"]))
    if pr["self_switch"]:
        extra.append("self-switch attackers: " + ", ".join(pr["self_switch"]))
    p(f"  {path} ({d['n']} cards; Energy {d['energy']}): holders: {hs}")
    for x in its:
        p(f"      item {x}")
    if not its:
        p("      no receiving-side, holder-side or trap item")
    for x in extra:
        p(f"      {x}")
    if d["unresolved"]:
        p(f"      UNRESOLVED lines: {d['unresolved']}")

# ---------------------------------------------------------------- 3. every list that holds a brought-in receiving item
p("\n== 3. Every committed list holding a BROUGHT-IN receiving item (could move only against a holder) ==")
by_item = collections.defaultdict(list)
for path, d in sorted(DECKS.items()):
    pr = deck_profile(d["cards"])
    for g in RECV:
        if g[0] in pr["items"] and g[5] in ("IN", "ALREADY", "FIX"):
            by_item[(g[1], g[2], g[5])].append(f"{path} [{', '.join(pr['items'][g[0]])}]")
for (row, label, verdict), lst in sorted(by_item.items()):
    p(f"  {row} {label} ({verdict}): {len(lst)} lists")
    for x in lst:
        p(f"      {x}")


# ---------------------------------------------------------------- 4. recorded tables
FROM_DISK = {}
WINREPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"


def resolve(path, base_dir=""):
    """Map a list path from a pairs file to a key of DECKS. Lists not committed at C are read (read-only) from the
    pincand working tree, then from the Windows checkout, and marked as such in FROM_DISK."""
    q = path.strip().replace("\\ ", " ")
    for pre in (REPO + "/", WINREPO + "/", "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/"):
        if q.startswith(pre):
            q = q[len(pre):]
    cands = [q, os.path.normpath(os.path.join(base_dir, q)), os.path.normpath(os.path.join("engine", q))]
    for c in cands:
        if c in DECKS:
            return c
    for c in cands:
        for root, tag in ((REPO, "pincand working tree (not committed)"), (WINREPO, "Windows checkout (not in pincand)")):
            fp = os.path.join(root, c)
            if os.path.isfile(fp):
                try:
                    t = open(fp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                cards, energy, unres = parse_list(t)
                if cards:
                    DECKS[c] = {"cards": cards, "energy": energy, "n": sum(cards.values()), "unresolved": unres}
                    FROM_DISK[c] = tag
                    return c
    return q


def check_pair(a, b):
    """Both directions. Returns list of text lines (empty = cannot reach)."""
    lines = []
    if a not in DECKS or b not in DECKS:
        return [f"    (list missing at {C} and on disk: {a if a not in DECKS else b})"], False
    reached_any = False
    for hold, recv in ((a, b), (b, a)):
        r, bl, tr, hs = pair_reach(DECKS[hold]["cards"], DECKS[recv]["cards"])
        if not (r or bl or tr or hs):
            if deck_profile(DECKS[hold]["cards"])["holders"]:
                lines.append(f"    holder side {hold}: the receiving list {recv} holds NO receiving-side item -> cannot reach")
            continue
        for x in r:
            reached_any = True
            lines.append(f"    REACH  holder {x[4]} ({hold}) <- {x[0]} {x[1]} [{x[2]}] on {recv}: {x[3]}; {x[5]}")
        for x in bl:
            lines.append(f"    blocked holder {x[4]} <- {x[0]} {x[1]}: {x[3]}; {x[5]}")
        for x in tr:
            lines.append(f"    trap-only (must NOT move) holder {x[3]} <- {x[0]} {x[1]}: {x[2]}")
        for x in hs:
            if x[1] == "HOLDER_IN" and "applies" in x[4]:
                reached_any = True
            lines.append(f"    holder-side {x[0]} [{x[1]}] ({x[3]}): {x[2]}; {x[4]}")
    return lines, reached_any


def mirror_note(a):
    if a in DECKS:
        r, bl, tr, hs = pair_reach(DECKS[a]["cards"], DECKS[a]["cards"])
        if r:
            return "  (same-list combo if it ever plays itself: " + "; ".join(f"{x[1]} on {x[4]}" for x in r) + ")"
    return ""


p("\n== 4. Recorded tables: does any pairing reach the change? ==")
# 4a. every committed pairs TSV with held_file / panel_file
tsvs = [x for x in tree if x.endswith(".tsv")]
tb = cat_many(tsvs)
pair_tables = {}
for path in tsvs:
    t = tb.get(path) or ""
    lines = t.splitlines()
    if not lines:
        continue
    hdr = lines[0].split("\t")
    if "held_file" in hdr and "panel_file" in hdr:
        hi, pi = hdr.index("held_file"), hdr.index("panel_file")
        rows, seen = [], {}
        base = os.path.dirname(path)
        for l in lines[1:]:
            f = l.split("\t")
            if len(f) > max(hi, pi):
                a, b = resolve(f[hi], base), resolve(f[pi], base)
                if (a, b) in seen:  # handoff files repeat a pairing once per game; keep one row per pair
                    seen[(a, b)].append(f[0])
                    continue
                seen[(a, b)] = [f[0]]
                rows.append((f[0], a, b))
        pair_tables[path] = [(",".join(sorted(set(seen[(a, b)]), key=lambda s: (len(s), s))[:12]) +
                              (",..." if len(set(seen[(a, b)])) > 12 else ""), a, b) for (_, a, b) in rows]
        pair_rows_total = sum(len(v) for v in seen.values())
        pair_tables[path + "\0n"] = pair_rows_total
# which TSVs the candidate pass (.cmd) and rules2 (.run) replayed
refd = collections.defaultdict(set)
cmdruns = [x for x in tree if (x.startswith("rl/results/engine_candidate_2026-10-20/") and x.endswith(".cmd"))
           or (x.startswith("rl/results/engine_switch_rules2_2026-10/") and x.endswith(".run"))]
cb = cat_many(cmdruns)
for path, t in cb.items():
    for m in re.finditer(r"--pairs\s+(\S+)", t or ""):
        q = m.group(1).replace("\\ ", " ")
        q = re.sub(r"^.*?/(rl/results/)", r"\1", q)
        pm = re.search(r"--pairings\s+(\S+)", t)
        refd[q].add((path, pm.group(1).replace("\\,", ",") if pm else "all"))
p(f"  {len([k for k in pair_tables if chr(0) not in k])} committed pairs files (held_file/panel_file); "
  f"{len(refd)} of them replayed by the candidate pass or rules switch 2")

table_hits = {}
missing_by_table = {}
for path in sorted(k for k in pair_tables if "\0" not in k):
    rows = pair_tables[path]
    hits, missing = [], set()
    for (pid, a, b) in rows:
        if a not in DECKS or b not in DECKS:
            missing |= {x for x in (a, b) if x not in DECKS}
            continue
        lines, reached = check_pair(a, b)
        if lines:
            hits.append((pid, a, b, lines, reached))
    table_hits[path] = hits
    missing_by_table[path] = missing
    tag = "REPLAYED by candidate/rules2" if path in refd else "older table"
    n_reach = sum(1 for h in hits if h[4])
    nrows = pair_tables[path + "\0n"]
    if hits or missing:
        p(f"\n  {path} [{tag}; {nrows} rows, {len(rows)} distinct pairings]: {n_reach} pairing(s) REACH")
        for pid, a, b, lines, reached in hits:
            p(f"   pairing {pid}: {a} v {b}{'  ** REACHES **' if reached else ''}")
            for l in lines:
                p(l)
        if missing:
            p(f"   lists not found at {C} nor on disk: {sorted(missing)}")
        if path in refd:
            for (who, prs) in sorted(refd[path]):
                p(f"     replayed by {who} (pairings {prs})")
no_hit = sorted(x for x in pair_tables if "\0" not in x and not table_hits[x] and not missing_by_table[x])
p(f"\n  pairs files with NO holder in any pairing ({len(no_hit)}): cannot reach the change")
for x in no_hit:
    p(f"    {x}{'  [REPLAYED]' if x in refd else ''}")
if FROM_DISK:
    p("\n  lists read from disk because they are not committed at " + C + ":")
    for k, v in sorted(FROM_DISK.items()):
        pr = deck_profile(DECKS[k]["cards"])
        p(f"    {k} ({v}): holders {[nm(h) for h in pr['holders']] or 'none'}; items {[GROUP[g][2] for g in pr['items']] or 'none'}")

# 4b. research table (legality_scan --decks decks/research: all 28 unordered pairs)
p("\n  research table (legality_scan --decks decks/research, 28 pairings: all pairs of the 8 lists)")
rr = []
for i in range(len(RESEARCH)):
    for j in range(i + 1, len(RESEARCH)):
        lines, reached = check_pair(RESEARCH[i], RESEARCH[j])
        if lines:
            rr.append((RESEARCH[i], RESEARCH[j], lines, reached))
if rr:
    for a, b, lines, reached in rr:
        p(f"   {a} v {b}{'  ** REACHES **' if reached else ''}")
        for l in lines:
            p(l)
else:
    p("    no holder in any research list -> cannot reach (k3, kp3, km3, kog3, kq3, kpr3, kd3, kta3 dev/fresh tables, CLI altaria v blaziken)")

# 4c. floor pages and run_screen: list v each of the 8 panel lists
p("\n  floor pages / run_screen (list v each of decks/screen/opponents/*.txt)")
floor_pages = sorted(set(x for x in tree if re.match(r"rl/results/(floor_|engine_switch_rules2_2026-10/floor_7c|engine_candidate_2026-10-20/games/new/floor_).*\.md$", x)))
floor_decks = collections.defaultdict(list)
for md in floor_pages:
    base = os.path.basename(md)[:-3]
    cands = [x for x in DECKS if os.path.basename(x) == base + ".txt" and (x.startswith("decks/") or "/d_first/" in x)]
    for c in cands:
        floor_decks[c].append(md)
floor_list = sorted(set(list(floor_decks) + FOCUS[:10]))
for dk in floor_list:
    if dk not in DECKS or dk in PANEL:
        continue
    out, any_r = [], False
    for o in PANEL:
        lines, reached = check_pair(dk, o)
        if lines:
            out.append((o, lines, reached))
            any_r |= reached
    pages = floor_decks.get(dk, [])
    p(f"   {dk}: {'REACHES' if any_r else 'cannot reach'}" + (f"; floor pages: {len(pages)}" if pages else "; no floor page found by name"))
    for pg in pages:
        p(f"      page {pg}")
    for o, lines, reached in out:
        p(f"      v {o}{'  ** REACHES **' if reached else ''}")
        for l in lines:
            p("  " + l)
    mn = mirror_note(dk)
    if mn:
        p("     " + mn)

# 4d. self-checks
p("\n  km3 / kx3 self-check: t-altaria v t-suicune")
lines, reached = check_pair("decks/screen/opponents/t-altaria.txt", "decks/screen/opponents/t-suicune.txt")
p("    " + ("REACHES" if reached else "cannot reach (no holder in either list)") if not lines else "\n".join(lines))

# 4e. kx3 pool
p("\n  kx3's pool (playout_pool.rs POOL, the lists kx3 may imagine for the opponent)")
for ref in KX3_REFS:
    try:
        src = git("show", f"{ref}:engine/src/players/playout_pool.rs")
    except subprocess.CalledProcessError:
        p(f"    {ref}: not found")
        continue
    ents = re.findall(r'\(\s*"([^"]+)",\s*"([^"]+)",\s*"([0-9a-f]{64})",\s*r#"(.*?)"#\s*\)', src, re.S)
    p(f"    {ref}: {len(ents)} pool lists")
    for (name, path, sha, body) in ents:
        cards, energy, unres = parse_list(body)
        pr = deck_profile(cards)
        same = (path in DECKS and DECKS[path]["cards"] == cards)
        its = [f"{GROUP[k][1]} {GROUP[k][2]}" for k in pr["items"]]
        p(f"      {name}: holders {[nm(h) for h in pr['holders']] or 'none'}; items {its or 'none'}; "
          f"{'same cards as ' + path if same else 'DIFFERS from ' + path + ' at ' + C}")
    p("      KX_EXTRA_LISTS (run-time extras) refuse decks/brews paths; the fixed computer deck:")
    for x in sorted(DECKS):
        if x.startswith("decks/computer/"):
            pr = deck_profile(DECKS[x]["cards"])
            p(f"        {x}: holders {[nm(h) for h in pr['holders']] or 'none'}; items {[GROUP[k][2] for k in pr['items']] or 'none'}")

# 4f. strength-harness runs (slow reports, kx3 dev/exam/replays, thinking time, m64): every committed config*.json
p("\n  strength-harness runs (rl/results/**/config*.json: deck_files / decks / deck_groups x opponents / opponent_groups)")
reg = json.loads(git("show", f"{C}:rl/strength/decks.json"))["decks"]
grp = json.loads(git("show", f"{C}:rl/strength/groups.json"))
cfgs = [x for x in tree if x.startswith("rl/results/") and re.search(r"/config[^/]*\.json$", x)]
cfb = cat_many(cfgs)
REACH_ALL = []
for path in sorted(cfgs):
    try:
        cfg = json.loads(cfb[path] or "{}")
    except Exception:
        continue
    names = list(cfg.get("decks") or [])
    for g in cfg.get("deck_groups") or []:
        names += grp.get(g, [])
    files = list(cfg.get("deck_files") or []) + [reg.get(n, n) for n in names]
    opp_names = list(cfg.get("opponents") or [])
    for g in cfg.get("opponent_groups") or []:
        opp_names += grp.get(g, [])
    opps = [reg.get(n, f"decks/screen/opponents/{n}.txt") for n in opp_names]
    if not files or not opps:
        p(f"   {path}: no deck/opponent lists in the config (skipped)")
        continue
    lines_out, any_r = [], False
    for dk in files:
        for o in opps:
            lines, reached = check_pair(dk, o)
            if reached:
                any_r = True
                REACH_ALL.append((path, dk, o))
                lines_out.append(f"      {dk} v {o}: " + " | ".join(l.strip() for l in lines if "REACH" in l))
    pilot = cfg.get("pilot")
    p(f"   {path} (pilot {pilot}, reference {cfg.get('reference')}; {len(files)} deck(s) x {len(opps)} opponents): "
      + ("REACHES" if any_r else "cannot reach"))
    for l in lines_out:
        p(l)

# ---------------------------------------------------------------- 5. positions (pause games): me/opp boards
p("\n== 5. Positions (pause games / position lists): a holder on one side and an item on the other ==")
CARD_RE = re.compile(r"((?:P-[AB])|(?:[AB]\d[a-z]?)) (\d{3})\b")


def ids_in(obj):
    out = collections.Counter()
    if isinstance(obj, str):
        for m in CARD_RE.finditer(obj):
            out[f"{m.group(1)} {m.group(2)}"] += 1
    elif isinstance(obj, dict):
        for v in obj.values():
            out.update(ids_in(v))
    elif isinstance(obj, list):
        for v in obj:
            out.update(ids_in(v))
    return out


jsons = [x for x in tree if x.endswith(".json") and ("position" in x.lower())]
jb = cat_many(jsons)
pos_files = 0
for path in sorted(jsons):
    t = jb.get(path)
    if not t or '"opp"' not in t or '"me"' not in t:
        continue
    try:
        data = json.loads(t)
    except Exception:
        continue
    plist = data if isinstance(data, list) else data.get("positions") if isinstance(data, dict) else None
    if not isinstance(plist, list):
        continue
    pos_files += 1
    folder = path.rsplit("/", 1)[0]
    hits = []
    for pos in plist:
        if not isinstance(pos, dict) or "me" not in pos or "opp" not in pos:
            continue
        deck = pos.get("deck")
        his = None
        for cand in (f"{folder}/decks/{deck}.txt", f"{folder.rsplit('/', 1)[0]}/decks/{deck}.txt"):
            if cand in DECKS:
                his = DECKS[cand]["cards"]
                break
        if his is None:
            cand = [x for x in DECKS if os.path.basename(x) == f"{deck}.txt"]
            his = DECKS[cand[0]]["cards"] if cand else collections.Counter()
        me = ids_in(pos["me"]) + his
        opp_vis = ids_in(pos["opp"])
        filled = not pos.get("exact_list", False)  # notes: the opponent's hidden cards are filled from the pilot's own list
        opp = opp_vis + (his if filled else collections.Counter())
        lines, reached = [], False
        for hold, recv, hn, rn in ((me, opp, "me", "opp"), (opp, me, "opp", "me")):
            r, bl, tr, hs = pair_reach(hold, recv)
            for x in r:
                reached = True
                lines.append(f"holder {x[4]} ({hn}) <- {x[1]} on {rn}: {x[3]}")
            for x in hs:
                if x[1] == "HOLDER_IN" and "applies" in x[4]:
                    reached = True
                    lines.append(f"holder-side {x[0]} ({hn})")
        if reached:
            hits.append((pos.get("id"), lines, filled))
    if hits:
        p(f"  {path}: {len(hits)} position(s) reach")
        for pid, lines, filled in hits:
            p(f"    {pid}{' (opp hidden cards filled from his list)' if filled else ''}: " + "; ".join(sorted(set(lines))))
p(f"  ({pos_files} position files scanned: committed .json files with 'position' in the path holding me/opp positions)")

# ---------------------------------------------------------------- 6. every committed file naming a holder list
p("\n== 6. Every committed file that names a holder list (by file name) or a holder game (by game id) ==")
keys = set()
for path in holder_decks:
    b = os.path.basename(path)[:-4]
    m = re.match(r"KW(\d{6}_\d{9})", b)
    keys.add(m.group(1).split("_")[1] if m else b)
pat = "|".join(re.escape(k) for k in sorted(keys))
try:
    hits = git("grep", "-l", "-E", pat, C, "--").splitlines()
except subprocess.CalledProcessError:
    hits = []
hits = [h.split(":", 1)[1] for h in hits]
groups = collections.defaultdict(list)
for h in hits:
    parts = h.split("/")
    g = "/".join(parts[:3]) if parts[0] == "rl" and len(parts) > 3 else "/".join(parts[:2]) if len(parts) > 2 else h
    groups[g].append(h)
p(f"  pattern: {pat}  ({len(hits)} files)")
for g in sorted(groups):
    fs = groups[g]
    if g.startswith("rl/results/battle_log_packets"):
        p(f"  {g}: {len(fs)} files (game evidence packets, not engine results)")
        continue
    p(f"  {g}: {len(fs)} files")
    for f in fs[:40]:
        p(f"      {f}")
    if len(fs) > 40:
        p(f"      ... {len(fs) - 40} more")

open(os.path.join(A.out, "reach_report.txt"), "w", encoding="utf-8").write("\n".join(OUT) + "\n")
print("\n".join(OUT))
