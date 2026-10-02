"""Round-2 readiness, job 1 (the cloud, Oct 2): the affected-deck inventory of the round-2 package, against current main.

The package is everything claude/coin-prevention-round2 adds to the official engine (main-8626a35): the later coin round's seven
sites, the card-text job and its follow-up. For each repaired mechanic it says, from the card text (engine/database.json; the
printings are listed in the output), which lists hold a card it needs, and then which pairings are EXPECTED to change: a pairing
is expected to change when the mechanic can act in its games, by the trigger written beside each mechanic below (one side uses
it, the other side supplies what it acts on, or the side's own list does). "Can act" is not "will act": a game changes only if the
cards meet in play; and a pairing not listed cannot change through that mechanic.

The lists: every .txt under decks/ (git ls-files, drafts_2026-10-01 included), the B2e lists, and the carriers and scratch lists of
the rules switch's steps 8 and 8b. The pairings:
  table     the 28 cells of the 8 research lists (decks/research/), and the 17 new cells (scoreboard v3: rayquaza and
            altaria_greninja, decks/gauntlet_2026-09-26/g-*.txt, against the 8 and each other);
  B2e       rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv (96);
  screen    any list against each of the 8 panel lists (decks/screen/opponents/t-*.txt), as run_screen.py plays them; the floor
            (decks/screen/floor.py) plays the same 8 pairings per list, so one answer covers both; the lists with floor pages
            on record are marked;
  carriers  rl/results/engine_switch_rules_2026-10/pairs_8.tsv (36: step 8's 32 and 8b's 4) and pairs_7c.tsv.
Usage: python3 inventory.py   (from anywhere in the repository; writes inventory_output.txt here)"""
import json, re, subprocess
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=HERE).stdout.strip())
DB = [next(iter(e.items())) for e in json.load(open(ROOT / "engine" / "database.json", encoding="utf-8"))]
RS = ROOT / "rl/results/engine_switch_rules_2026-10"


def texts(kind, d):
    """(label, text, is_attack, energy) for a card's Ability, attacks or Trainer text."""
    if kind != "Pokemon":
        return [("Trainer", d.get("effect") or "", False, None)]
    out = [("Ability " + d["ability"]["title"], d["ability"]["effect"], False, None)] if d.get("ability") else []
    return out + [("attack " + a["title"], a.get("effect") or "", True, a.get("energy_required")) for a in d.get("attacks", [])]


def ids_where(pred):
    """Printings whose card has a text matching pred(kind, d, label, text, is_attack)."""
    return {d["id"] for kind, d in DB for (lab, t, att, _) in texts(kind, d) if pred(kind, d, lab, t, att)}


def name_of(i):
    return next(d["name"] for _, d in DB if d["id"] == i)


# The card sets, from the text.
COIN = ids_where(lambda k, d, l, t, a: l.startswith("Ability") and t.startswith("If any damage is done to this Pokémon by attacks, flip a coin"))
SITES = {  # the later coin round's seven sites (the round's README, "Reach per card")
    "Wild Swing": {"A4 045", "A4 215"}, "Wellspring Dance": {"B2 048"}, "Tornado Shot": {"B3 051"},
    "Double Splash": {"B1a 019"}, "Triple Bombardment": {"B1a 020", "B1a 078", "B1a 084"},
    "second punch": {"B2 127", "B2 189", "B2 202", "B4 231"}, "Mischievous Ring": {"B4 077"}, "Litter": {"A4a 018"}}
WILL = {"A4 156", "A4 196"}
VICTINI = {"B3 025", "P-B 049"}
BLOCK = ids_where(lambda k, d, l, t, a: a and "your opponent flips a coin. If tails, that attack doesn't happen" in t)
CONFUSE_OPP = ids_where(lambda k, d, l, t, a: re.search(r"[Oo]pponent's Active Pokémon is now Confused|Both Active Pokémon are now Confused|"
                                                     r"make your opponent's Active Pokémon Confused|Choose either Poisoned or Confused", t)
                        or ("Confused" in t and "chosen at random" in t and "opponent's Active" in t))
CONFUSE_SELF = ids_where(lambda k, d, l, t, a: re.search(r"[Tt]his Pokémon is now Confused|Both Active Pokémon are now Confused|"
                                                      r"your Active Pokémon is now also Confused", t))
COIN_ATTACK = ids_where(lambda k, d, l, t, a: a and re.search(r"\b[Ff]lip\b", t))
FIRE_COIN_ATTACK = {d["id"] for kind, d in DB if kind == "Pokemon" and d.get("energy_type") == "Fire"
                    and any(a and re.search(r"\b[Ff]lip\b", t) for (_, t, a, _) in texts(kind, d))}
OWN_CHOICE = ids_where(lambda k, d, l, t, a: a and re.search(r"damage to 1 of your Benched Pokémon", t))
OWN_SIDE = ids_where(lambda k, d, l, t, a: a and re.search(r"damage to (1|each) of your (Benched )?Pokémon|"
                                                       r"all Benched Pokémon \(both yours", t))
COPY_ANYTHING = {"A1 205", "A1 247"}
COPY_A_FRIEND = {"B1a 055", "B3b 099", "P-B 012"}
CHASE_ORDER = {"B4 011", "B4 180", "B4 194"}
WILD_SWING = SITES["Wild Swing"]
ARIADOS = {"B1a 006", "B1a 070"}
GHOLDENGO = {"B4a 051", "B4a 109"}
COIN_STADIUM = {"B2a 093", "B4a 072"}
FOSSIL = {d["id"] for kind, d in DB if kind != "Pokemon" and d.get("trainer_card_type") == "Fossil"}
ITEM_LOCK = ids_where(lambda k, d, l, t, a: a and "can't play any Item cards" in t)
GUTS = ids_where(lambda k, d, l, t, a: l.startswith("Ability") and "would be Knocked Out by damage from an attack, flip a coin" in t)
PERISH = ids_where(lambda k, d, l, t, a: l.startswith("Ability") and "the Attacking Pokémon is Knocked Out" in t)


def has(deck, ids, n=1):
    return sum(c for i, c in deck.items() if i in ids) >= n


# Each mechanic: (name, where it was repaired, trigger(user, other) -> bool, the cards it reads). A one-sided trigger (the user's
# own list is enough) is listed in ONE_SIDED: any pairing of a user list can change.
MECHANICS = [(f"coin round 2: {site}", "later coin round (Oct 1)",
              (lambda ids: lambda u, o: has(u, ids) and has(o, COIN))(ids), f"the attacker {sorted(ids)} v a coin Ability")
             for site, ids in SITES.items()] + [
    ("Will with a Confused attacker (and Victory Star)", "card text, item 1",
     lambda u, o: has(u, WILL) and has(u, COIN_ATTACK) and (has(o, CONFUSE_OPP) or has(u, CONFUSE_SELF)),
     "Will, a coin attack, and a Confusion source (the opponent's, or the list's own self-Confusion)"),
    ("Victory Star with a block coin", "card text, A1",
     lambda u, o: has(u, VICTINI) and has(u, FIRE_COIN_ATTACK) and has(o, BLOCK), "Victini and a [R] coin attacker v a block-coin attack"),
    ("Will with a block coin", "card text, A2", lambda u, o: has(u, WILL) and has(o, BLOCK), "Will v a block-coin attack"),
    ("coin Abilities on your own Pokemon", "card text, A4", lambda u, o: has(u, OWN_SIDE) and has(u, COIN),
     "an own-side damage attack and a coin Ability in the same list"),
    ("the opponent's Active in an own-Bench choice", "card text, A4", lambda u, o: has(u, OWN_CHOICE) and has(o, COIN),
     "an own-Bench choice attack (Raging Thunder, Flash Impact) v a coin Ability"),
    ("a copied discard attack", "card text, A5",
     lambda u, o: has(o, COIN) and ((has(u, COPY_ANYTHING) and has(o, CHASE_ORDER | WILD_SWING))
                                    or (has(u, COPY_A_FRIEND) and has(u, WILD_SWING))),
     "Ditto (Copy Anything v Chase Order or Wild Swing; Copy a Friend with its own Wild Swing) v a coin Ability"),
    ("Trap Territory, two Ariados", "card text, item 4", lambda u, o: has(u, ARIADOS, 2), "two or more Ariados in the list"),
    ("Luxury Coin on the opponent's Stadium", "follow-up", lambda u, o: has(u, GHOLDENGO) and has(o, COIN_STADIUM),
     "Gholdengo v Mesagoza or Arcade"),
    ("a Fossil under an Item lock", "follow-up", lambda u, o: has(u, FOSSIL) and has(o, ITEM_LOCK), "a Fossil v an Item-lock attack"),
    ("Guts on your own Pokemon (E1)", "follow-up", lambda u, o: has(u, GUTS) and has(u, OWN_SIDE),
     "a Guts Pokemon and an own-side damage attack in the same list"),
    ("Perish Body on a plain queued hit (E2)", "follow-up", lambda u, o: has(o, PERISH),
     "any list v Galarian Cursola (the attacker side is not narrowed)"),
]


def read_list(path):
    deck = Counter()
    for line in (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\d+)\s+(?:.*\s)?([A-Za-z0-9-]+ \d+)\s*$", line)
        if m:
            deck[m[2]] += int(m[1])
    return deck


ONE_SIDED = {"coin Abilities on your own Pokemon", "Trap Territory, two Ariados", "Guts on your own Pokemon (E1)"}
# A deck list is a .txt with exactly 20 cards (coverage outputs and check pages under decks/ are not lists).
lists = [f for f in subprocess.run(["git", "ls-files", "decks"], capture_output=True, text=True, cwd=ROOT).stdout.split()
         if f.endswith(".txt") and sum(read_list(f).values()) == 20]
pair_files = {"b2e": "rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv",
              "carriers 8/8b": "rl/results/engine_switch_rules_2026-10/pairs_8.tsv",
              "carriers 7c": "rl/results/engine_switch_rules_2026-10/pairs_7c.tsv"}
tsv_pairs = {}
for key, f in pair_files.items():
    rows = (ROOT / f).read_text(encoding="utf-8").splitlines()
    head = rows[0].split("\t")
    tsv_pairs[key] = [(r["held_file"], r["panel_file"]) for r in (dict(zip(head, l.split("\t"))) for l in rows[1:])]
extra = sorted({p for ps in tsv_pairs.values() for pair in ps for p in pair} - set(lists))
decks = {p: read_list(p) for p in lists + extra}
PANEL = sorted(p for p in lists if p.startswith("decks/screen/opponents/"))
RESEARCH = sorted(p for p in lists if p.startswith("decks/research/"))
NEW17_LISTS = {"rayquaza": "decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt",
               "altaria_greninja": "decks/gauntlet_2026-09-26/g-mega_altaria_greninja.txt"}
table = list(combinations(RESEARCH, 2))
new17 = [(NEW17_LISTS[n], r) for n in NEW17_LISTS for r in RESEARCH] + [tuple(NEW17_LISTS.values())]
floor_on_record = {f.name.replace("_games.jsonl", "") for d in (ROOT / "rl/results").glob("floor*") for f in d.glob("*_games.jsonl")}


def why(a, b):
    """The mechanics that can act in the pairing a v b, as 'name (user side)'."""
    out = []
    for name, _, trig, _ in MECHANICS:
        for user, other, side in ((a, b, "first list"), (b, a, "second list")):
            if trig(decks[user], decks[other]):
                out.append(f"{name} ({side})")
    return out


L = []
say = L.append
n_txt = len([f for f in subprocess.run(["git", "ls-files", "decks"], capture_output=True, text=True, cwd=ROOT).stdout.split() if f.endswith(".txt")])
say(f"main: {len(lists)} deck lists under decks/ (of its {n_txt} .txt files; the rest are coverage and check pages), and "
    f"{len(extra)} lists outside it named by the pairing files.")
say("\n== the card sets, from the card text")
for label, ids in (("coin Abilities", COIN), ("block-coin attacks", BLOCK), ("Confusion of the opponent's Active", CONFUSE_OPP),
                   ("self-Confusion", CONFUSE_SELF), ("own-side damage attacks", OWN_SIDE), ("own-Bench choice attacks", OWN_CHOICE),
                   ("Item-lock attacks", ITEM_LOCK), ("Fossils", FOSSIL), ("Guts", GUTS), ("Perish Body", PERISH)):
    names = sorted({name_of(i) for i in ids})
    say(f"{label} ({len(ids)} printings): {', '.join(names)}")

say("\n== which lists hold the cards each mechanic reads (every list, the pairing files' included)")
for name, where, trig, cards in MECHANICS:
    holders = []
    for p, deck in sorted(decks.items()):
        sides = []
        if any(trig(deck, decks[q]) for q in decks):
            sides.append("uses it" if name in ONE_SIDED else "can use it against some list")
        if name not in ONE_SIDED and any(trig(decks[q], deck) for q in decks):
            sides.append("supplies what it acts on")
        if sides:
            holders.append(f"{p} ({'; '.join(sides)})")
    say(f"\n{name} [{where}; {cards}]: {len(holders)} lists")
    for h in holders:
        say(f"  {h}")

say("\n== the pairings EXPECTED to change")
total = 0
for label, ps in (("table, 28 cells", table), ("new-17 cells", new17), ("B2e, 96", tsv_pairs["b2e"]),
                  ("carriers, steps 8 and 8b (pairs_8.tsv, 36)", tsv_pairs["carriers 8/8b"]),
                  ("Dustin's decks v the panel, step 7c (pairs_7c.tsv)", tsv_pairs["carriers 7c"])):
    hit = [(a, b, why(a, b)) for a, b in ps if why(a, b)]
    total += len(hit)
    say(f"\n{label}: {len(hit)} of {len(ps)}")
    for a, b, w in hit:
        say(f"  {Path(a).stem} v {Path(b).stem}: {', '.join(w)}")
say("\nscreen and floor (each list v the 8 panel lists; * = floor pages on record):")
n_screen = 0
for p in sorted(lists):
    if p in PANEL:
        continue
    hit = [(Path(o).stem, why(p, o)) for o in PANEL if why(p, o)]
    if hit:
        n_screen += len(hit)
        star = "*" if Path(p).stem in floor_on_record else ""
        say(f"  {p}{star}: {len(hit)} of 8: " + "; ".join(f"v {o}: {', '.join(w)}" for o, w in hit))
say(f"  screen pairings expected to change: {n_screen} (over {len([p for p in lists if p not in PANEL])} lists x 8)")
say(f"\ntotal named pairings expected to change (table, new-17, B2e, carriers, 7c): {total}")
(HERE / "inventory_output.txt").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L))
