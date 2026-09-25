#!/usr/bin/env python3
"""Brew consistency: how often a list does what it is built to do, from the list alone.

    python3 lib/brew_consistency.py decks/brews/brew-01-arceus-crobat-xatu.txt [--attackers "Xatu,Arceus ex"]
        [--combo "Crobat,Xatu"] [--combo-turn 3] [--trials 20000] [--json out.json]

Monte Carlo over shuffles of the list, with Pocket's opening rule (5 random cards; a hand with no Basic has
one card swapped for a Basic) and a simple solitaire policy: every turn draw 1, take the Energy Zone's
energy (not on turn 1 going first), play draw/search cards from DRAW_SEARCH, put Basics down, evolve
(from your second turn, never a Pokémon placed that turn; Rare Candy as printed), and give energy to the
main attacker's line. Nothing here needs the engine, so it works before a set is merged. What it can't
see (the opponent, points conceded, what the bot actually plays) comes from the engine goldfish runs
(engine/examples/goldfish.rs).

Metrics, going first and going second ("turn k" is your own k-th turn):
- one-Basic openings, and which Basic is then the lone starter;
- main attacker able to attack on turn 2 and turn 3 (in play, final stage, attack cost attached; moving
  it to the Active Spot is assumed free);
- a Stage 2 in play by turn 3;
- the named combo pieces all in play by turn N;
- stuck cards at the end of each turn: evolutions with nothing to evolve, Rare Candy with no use, and
  Supporters beyond the one a turn allows.
Also a structure check: attacks the deck's Energy can't pay for, and evolutions missing their middle stage.
"""
import argparse, io, json, os, random, re, sys
from collections import Counter
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
TYPE_LETTER = {"Grass": "G", "Fire": "R", "Water": "W", "Lightning": "L", "Psychic": "P", "Fighting": "F",
               "Darkness": "D", "Metal": "M", "Colorless": "C", "Dragon": "N"}

# Draw and search effects, by Trainer name. Kinds: draw (n cards), basic (n random Basics), named (n random
# cards from a name list), copycat (shuffle hand, draw the opponent's hand size), stage1_top (look at the top
# n, keep Stage 1s), tr_researcher (flip until tails, a random Team Rocket Pokémon per heads). Stadiums:
# once-a-turn searches or end-of-turn draws for the player who has them in play.
DRAW_SEARCH = {
    "Professor's Research": {"kind": "draw", "n": 2},
    "Poké Ball": {"kind": "basic", "n": 1},
    "Lisia": {"kind": "basic", "n": 2, "max_hp": 50},
    "Copycat": {"kind": "copycat"},
    "Gladion": {"kind": "named", "n": 1, "names": ["Type: Null", "Silvally"]},
    "Clemont": {"kind": "named", "n": 2, "names": ["Magneton", "Heliolisk", "Clemont's Backpack"]},
    "Sightseer": {"kind": "stage1_top", "n": 4},
    "Team Rocket's Researcher": {"kind": "tr_researcher"},
}
STADIUM_SEARCH = {
    "Mesagoza": {"kind": "coin_pokemon"},
    "Fragrant Forest": {"kind": "basic_type", "type": "Grass"},
    "Hiking Trail": {"kind": "draw_to", "n": 3},
    "Arcade": {"kind": "arcade"},
}
OPPONENT_HAND = 4  # assumed opponent hand size for Copycat


def load_db():
    for p in (os.environ.get("PDL_DB", ""), os.path.join(HERE, "deckgym-database.json")):
        if p and os.path.exists(p):
            out = {}
            for e in json.load(io.open(p, encoding="utf-8")):
                for kind, v in e.items():
                    if isinstance(v, dict) and "id" in v:
                        out[v["id"]] = dict(v, kind=kind)
            return out
    sys.exit("deckgym-database.json not found")


def parse_list(path, db):
    energy, cards = [], []
    for line in io.open(path, encoding="utf-8"):
        s = line.strip()
        if s.lower().startswith("energy:"):
            energy = [x.strip() for x in s.split(":", 1)[1].split(",") if x.strip()]
            continue
        if not s or not s[0].isdigit():
            continue
        m = re.search(r"([A-Z][A-Za-z0-9-]*)\s+(\d+)\s*$", s)
        count = int(s.split()[0])
        cid = None
        if m:
            for cand in (f"{m.group(1)} {int(m.group(2)):03d}", f"{m.group(1)} {m.group(2)}"):
                if cand in db:
                    cid = cand
                    break
        if cid is None:
            sys.exit(f"unresolved card line: {s}")
        cards += [db[cid]] * count
    return energy, cards


def is_basic(c):
    return c["kind"] == "Pokemon" and c.get("stage") == 0


def is_supporter(c):
    return c["kind"] != "Pokemon" and (c.get("trainer_card_type") or c.get("type")) == "Supporter"


def trainer_type(c):
    return c.get("trainer_card_type") or c.get("type")


def payable(attack, energy_types):
    letters = {TYPE_LETTER.get(t, t[:1]) for t in energy_types}
    return all(TYPE_LETTER.get(e, e[:1]) in letters or e == "Colorless" for e in attack.get("energy_required", []))


def structure_check(energy, cards):
    names = {c["name"] for c in cards}
    notes = []
    for c in sorted({c["id"]: c for c in cards if c["kind"] == "Pokemon"}.values(), key=lambda c: c["name"]):
        for a in c.get("attacks", []):
            if not payable(a, energy):
                cost = "".join(TYPE_LETTER.get(e, e[:1]) for e in a["energy_required"])
                notes.append(f"{c['name']}'s {a['title']} [{cost}] can't be paid with {'/'.join(energy)} Energy.")
        if c.get("stage", 0) >= 1 and c.get("evolves_from") and c["evolves_from"] not in names:
            if c.get("stage") == 2 and any(x["kind"] == "Trainer" and x["name"] == "Rare Candy" for x in cards):
                notes.append(f"{c['name']} (Stage 2) has no {c['evolves_from']} in the list: Rare Candy only.")
            else:
                notes.append(f"{c['name']} evolves from {c['evolves_from']}, which isn't in the list.")
    return notes


def lines_to(target_names, cards):
    """Every card name in the evolution lines that end in a target (for giving energy to the right Pokémon)."""
    by_name = {c["name"]: c for c in cards if c["kind"] == "Pokemon"}
    line = set(target_names)
    changed = True
    while changed:
        changed = False
        for n in list(line):
            prev = by_name.get(n, {}).get("evolves_from")
            if prev is None and n in STAGE1_FROM and n not in by_name:
                prev = STAGE1_FROM[n]  # a Stage 1 missing from the list (Rare Candy skips it)
            if prev and prev not in line:
                line.add(prev)
                changed = True
    return line


def default_attackers(energy, cards):
    best, names = -1, []
    for c in {c["id"]: c for c in cards if c["kind"] == "Pokemon"}.values():
        for a in c.get("attacks", []):
            if payable(a, energy):
                d = a.get("fixed_damage") or 0
                if d > best:
                    best, names = d, [c["name"]]
                elif d == best and c["name"] not in names:
                    names.append(c["name"])
    return names


class Solitaire:
    def __init__(self, energy, cards, attackers, rng):
        self.energy, self.cards, self.attackers, self.rng = energy, cards, set(attackers), rng
        self.line = lines_to(attackers, cards)
        self.by_name = {c["name"]: c for c in cards if c["kind"] == "Pokemon"}
        self.feeds = {n: lines_to([n], cards) - {n} for n in attackers}  # what evolves into each attacker

    def deal(self):
        deck = self.cards[:]
        self.rng.shuffle(deck)
        hand, deck = deck[:5], deck[5:]
        if not any(is_basic(c) for c in hand):
            bi = [i for i, c in enumerate(deck) if is_basic(c)]
            j = self.rng.choice(bi)
            k = self.rng.randrange(5)
            hand[k], deck[j] = deck[j], hand[k]
            self.rng.shuffle(deck)
        return hand, deck

    def attack_cost(self, card):
        costs = [len(a["energy_required"]) for a in card.get("attacks", []) if payable(a, self.energy) and (a.get("fixed_damage") or a.get("effect"))]
        return min(costs) if costs else None

    def play(self, first, turns=6, combo=(), combo_turn=3):
        rng = self.rng
        hand, deck = self.deal()
        opening_basics = [c["name"] for c in hand if is_basic(c)]
        # board entries: [card, energy, placed_turn, evolved_turn]
        basics = sorted([c for c in hand if is_basic(c)], key=lambda c: (c["name"] not in self.line, c["name"]))
        active = basics[0]
        hand.remove(active)
        board = [[active, 0, 0, -1]]
        for c in [c for c in hand if is_basic(c)][:3]:
            hand.remove(c)
            board.append([c, 0, 0, -1])
        stadium = None
        res = {"opening_basics": opening_basics, "ready": {}, "stage2_by": None, "combo_by": None, "stuck": [],
               "seen": []}
        seen = set(opening_basics) | {c["name"] for c in hand} | {s[0]["name"] for s in board}

        def draw(n=1):
            for _ in range(n):
                if deck and len(hand) < 10:
                    hand.append(deck.pop(0))
                    seen.add(hand[-1]["name"])

        def take(pred, n=1):
            got = 0
            for _ in range(n):
                idx = [i for i, c in enumerate(deck) if pred(c)]
                if not idx or len(hand) >= 10:
                    break
                hand.append(deck.pop(rng.choice(idx)))
                seen.add(hand[-1]["name"])
                got += 1
            rng.shuffle(deck)
            return got

        for k in range(1, turns + 1):
            draw()
            supporter_used = False
            stadium_used = False
            # Items and Supporters that find cards, then Basics, then evolutions, repeated until stable.
            for _ in range(4):
                for c in [c for c in hand if trainer_type(c) == "Item"]:
                    spec = DRAW_SEARCH.get(c["name"])
                    if spec and spec["kind"] == "basic" and any(is_basic(x) for x in deck):
                        hand.remove(c)
                        take(is_basic, spec["n"])
                if not supporter_used:
                    for c in sorted([c for c in hand if is_supporter(c) and c["name"] in DRAW_SEARCH],
                                    key=lambda c: c["name"] != "Professor's Research"):
                        spec = DRAW_SEARCH[c["name"]]
                        hand.remove(c)
                        supporter_used = True
                        if spec["kind"] == "draw":
                            draw(spec["n"])
                        elif spec["kind"] == "basic":
                            take(lambda x: is_basic(x) and (x.get("hp") or 0) <= spec.get("max_hp", 999), spec["n"])
                        elif spec["kind"] == "named":
                            take(lambda x: x["name"] in spec["names"], spec["n"])
                        elif spec["kind"] == "copycat":
                            deck.extend(hand)
                            hand.clear()
                            rng.shuffle(deck)
                            draw(OPPONENT_HAND)
                        elif spec["kind"] == "stage1_top":
                            top, rest = deck[:spec["n"]], deck[spec["n"]:]
                            keep = [x for x in top if x["kind"] == "Pokemon" and x.get("stage") == 1]
                            hand.extend(keep[: 10 - len(hand)])
                            seen.update(x["name"] for x in keep[: 10 - len(hand)])
                            deck[:] = rest + [x for x in top if x not in keep]
                            rng.shuffle(deck)
                        elif spec["kind"] == "tr_researcher":
                            while rng.random() < 0.5:
                                if not take(lambda x: x["kind"] == "Pokemon" and "Team Rocket" in x["name"]):
                                    break
                        break
                if stadium is None:
                    for c in hand:
                        if trainer_type(c) == "Stadium" and c["name"] in STADIUM_SEARCH:
                            hand.remove(c)
                            stadium = c["name"]
                            break
                if stadium and not stadium_used:
                    stadium_used = True
                    s = STADIUM_SEARCH[stadium]
                    if s["kind"] == "coin_pokemon" and rng.random() < 0.5:
                        take(lambda x: x["kind"] == "Pokemon")
                    elif s["kind"] == "basic_type":
                        take(lambda x: is_basic(x) and x.get("energy_type") == s["type"])
                    elif s["kind"] == "arcade" and rng.random() < 0.125:
                        draw(max(0, 7 - len(hand)))
                for c in [c for c in hand if is_basic(c)]:
                    if len(board) < 4:
                        hand.remove(c)
                        board.append([c, 0, k, -1])
                if k >= 2:
                    for slot in board:
                        if slot[2] == k or slot[3] == k:
                            continue
                        evo = next((c for c in hand if c["kind"] == "Pokemon" and c.get("evolves_from") == slot[0]["name"]), None)
                        if evo is None and slot[0].get("stage") == 0:
                            candy = next((c for c in hand if c["name"] == "Rare Candy"), None)
                            mids = {n for n, p in self.by_name.items() if p.get("evolves_from") == slot[0]["name"]}
                            top = next((c for c in hand if c["kind"] == "Pokemon" and c.get("stage") == 2
                                        and (c.get("evolves_from") in mids or self._two_below(c, slot[0]["name"]))), None)
                            if candy and top:
                                hand.remove(candy)
                                evo = top
                        if evo is not None:
                            hand.remove(evo)
                            slot[0], slot[3] = evo, k
            # Energy: from turn 1 going second, from turn 2 going first; to the attacker's line first.
            if not (first and k == 1):
                # To the Pokémon closest to attacking: fewest energy still missing for the cheapest main
                # attack it is or can become, then whatever is already on the attacker's line.
                # A Pokémon that still has to evolve counts two energy further away unless the card it
                # evolves into (or Rare Candy and that card) is already in hand.
                in_hand = {c["name"] for c in hand}
                def missing(s):
                    costs = []
                    for n in self.attackers:
                        if n not in self.by_name or self.attack_cost(self.by_name[n]) is None:
                            continue
                        if s[0]["name"] == n:
                            costs.append(self.attack_cost(self.by_name[n]))
                        elif s[0]["name"] in self.feeds[n]:
                            costs.append(self.attack_cost(self.by_name[n]) + (0 if n in in_hand else 2))
                    return (min(costs) - s[1]) if costs else None
                need = [(missing(s), s) for s in board]
                open_ = [(m, s) for m, s in need if m is not None and m > 0]
                if open_:
                    min(open_, key=lambda x: (x[0], x[1][0]["name"] not in self.attackers))[1][1] += 1
                else:
                    sorted(board, key=lambda s: (s[0]["name"] not in self.line, -s[1]))[0][1] += 1
            ready = any(s[0]["name"] in self.attackers and self.attack_cost(s[0]) is not None
                        and s[1] >= self.attack_cost(s[0]) for s in board)
            res["ready"][k] = ready
            if res["stage2_by"] is None and any(s[0].get("stage") == 2 for s in board):
                res["stage2_by"] = k
            in_play = {s[0]["name"] for s in board}
            if combo and res["combo_by"] is None and all(n in in_play for n in combo):
                res["combo_by"] = k
            stuck = 0
            for c in hand:
                if c["kind"] == "Pokemon" and c.get("stage", 0) >= 1:
                    base = c.get("evolves_from")
                    can = k >= 2 and any(s[0]["name"] == base and s[2] != k for s in board)
                    candy_ok = c.get("stage") == 2 and any(x["name"] == "Rare Candy" for x in hand) and k >= 2 and \
                        any(s[0].get("stage") == 0 and self._two_below(c, s[0]["name"]) and s[2] != k for s in board)
                    stuck += not (can or candy_ok)
                elif c["name"] == "Rare Candy":
                    stuck += not (k >= 2 and any(self._two_below(x, s[0]["name"]) for x in hand for s in board
                                                 if x["kind"] == "Pokemon" and x.get("stage") == 2 and s[2] != k))
                elif is_supporter(c) and supporter_used:
                    stuck += 1
            res["stuck"].append(stuck)
            res["seen"].append(set(seen))
            if stadium in ("Hiking Trail",):
                draw(max(0, STADIUM_SEARCH[stadium]["n"] - len(hand)))
        return res

    def _two_below(self, stage2, basic_name):
        mid = self.by_name.get(stage2.get("evolves_from"))
        if mid is not None:
            return mid.get("evolves_from") == basic_name
        # The Stage 1 isn't in the list: find it in the card database.
        return STAGE1_FROM.get(stage2.get("evolves_from")) == basic_name


STAGE1_FROM = {}


def run(path, attackers=None, combo=(), combo_turn=3, trials=20000, seed=22_100_000_000):
    db = load_db()
    for c in db.values():
        if c["kind"] == "Pokemon" and c.get("stage") == 1 and c.get("evolves_from"):
            STAGE1_FROM.setdefault(c["name"], c["evolves_from"])
    energy, cards = parse_list(path, db)
    attackers = attackers or default_attackers(energy, cards)
    out = {"list": os.path.basename(path), "energy": energy, "cards": len(cards), "attackers": attackers,
           "combo": list(combo), "combo_turn": combo_turn, "trials": trials, "seed": seed,
           "structure": structure_check(energy, cards)}
    copies = Counter(c["name"] for c in cards)
    names = sorted(copies)
    for first in (True, False):
        rng = random.Random(seed + (0 if first else 1))
        sim = Solitaire(energy, cards, attackers, rng)
        one_basic, lone = 0, Counter()
        ready = Counter()
        stage2 = combo_ok = 0
        stuck = Counter()
        seen = Counter()
        for _ in range(trials):
            r = sim.play(first, combo=combo, combo_turn=combo_turn)
            if len(r["opening_basics"]) == 1:
                one_basic += 1
                lone[r["opening_basics"][0]] += 1
            for k, v in r["ready"].items():
                ready[k] += v
            stage2 += r["stage2_by"] is not None and r["stage2_by"] <= 3
            combo_ok += r["combo_by"] is not None and r["combo_by"] <= combo_turn
            for k, s in enumerate(r["stuck"], 1):
                stuck[k] += s
            for k, names in enumerate(r["seen"][:4], 1):
                for n in names:
                    seen[(n, k)] += 1
        key = "first" if first else "second"
        out[key] = {
            "one_basic_opening": one_basic / trials,
            "lone_starter": {n: v / trials for n, v in lone.most_common()},
            "attacker_ready": {k: ready[k] / trials for k in sorted(ready)},
            "stage2_by_turn3": stage2 / trials if any(c.get("stage") == 2 for c in cards) else None,
            "combo_by_turn": combo_ok / trials if combo else None,
            "stuck_per_turn": {k: stuck[k] / trials for k in sorted(stuck)},
            # Chance each card has been in your hand by the end of your turn k (1-4): with this list's
            # draw and search cards played as above, and from draws alone (exact; 5 + k cards seen, the
            # opening-hand Basic rule ignored).
            "seen_by_turn": {n: {k: seen[(n, k)] / trials for k in range(1, 5)} for n in names},
            "seen_by_turn_draws_only": {n: {k: 1 - comb(len(cards) - c, 5 + k) / comb(len(cards), 5 + k)
                                            for k in range(1, 5)} for n, c in copies.items()},
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("--attackers", default="")
    ap.add_argument("--combo", default="")
    ap.add_argument("--combo-turn", type=int, default=3)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--json")
    a = ap.parse_args()
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]
    out = run(a.deck, split(a.attackers), tuple(split(a.combo)), a.combo_turn, a.trials)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
