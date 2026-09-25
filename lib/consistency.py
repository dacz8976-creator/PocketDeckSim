#!/usr/bin/env python3
"""A1 consistency harness: how often a list does what it is built to do.

usage:
  python3 lib/consistency.py <deck.txt> [--main "<card name>[:<attack>]"] [--combo "<name>,<name>|<alt>"]
                             [--games N] [--goldfish N] [--seed S]
  python3 lib/consistency.py --batch decks/consistency_2026-09-25/lists.tsv [--games N] [--goldfish N]

Writes one plain-language page per list to decks/consistency_2026-09-25/<deck>.md and prints a
one-line summary. --batch also rewrites the table in decks/consistency_2026-09-25/ANCHORS.md.

What it measures, going first and going second separately:
  1. Opening hand: Basics in the 5-card hand under Pocket's swap-in rule (exact).
  2. Main attacker online: in play with the Energy for its main attack, by own turn 2, 3 and 4.
  3. Stage 2 in play by own turn 3, with and without Rare Candy (lists with a Stage 2).
  4. Combo pieces assembled by own turn 2..5 (Pokemon pieces in play, Trainer pieces in hand
     or already played).
  5. Goldfish against the engine: points conceded before the list's first attack that does
     damage, turn of that attack, dead cards in hand at the end of each turn.
  6. Coverage flag: the list's cards that hit known blind spots of the engine's bots.

Parts 2 to 4 come from a solitaire model written here (a sensible pilot playing the list's draw,
search, evolution and energy cards; no opponent), parts 5 from the engine program itself
(rl/addon-0.7.2/deckgym, the 'aa' attach-and-attack bot as opponent). Card text comes from
lib/deckgym-database.json through lib/card.py. Runs in WSL or Linux (the engine is a Linux file);
--goldfish 0 skips the engine and works anywhere with Python 3.8+.

Combo syntax: pieces separated by commas; alternatives inside a piece by '|'.
  --combo "Skarmory ex,Metal Core Barrier|Jasmine"  = Skarmory ex in play and either card in hand.
"""
import argparse
import collections
import glob
import io
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import card as cardlib  # noqa: E402  (lib/card.py: the project's card-text lookup)

DEFAULT_OUT = os.path.join(ROOT, 'decks', 'consistency_2026-09-25')
DEFAULT_ENGINE = os.path.join(ROOT, 'rl', 'addon-0.7.2', 'deckgym')
DEFAULT_OPP = os.path.join(ROOT, 'decks', 'research', 'weezing.txt')
SEED0 = 21_002_000_000          # the laptop's seed block for 2026-09-24/25
TURNS = 5                        # own turns simulated
BENCH = 3
HAND_LIMIT = 10
SYM = {'G': 'Grass', 'R': 'Fire', 'W': 'Water', 'L': 'Lightning', 'P': 'Psychic',
       'F': 'Fighting', 'D': 'Darkness', 'M': 'Metal', 'C': 'Colorless', 'N': 'Dragon'}
LETTER = {v: k for k, v in SYM.items()}


# ----------------------------------------------------------------------------------------------
# Cards and lists
# ----------------------------------------------------------------------------------------------

class Card:
    __slots__ = ('id', 'name', 'kind', 'stage', 'frm', 'hp', 'etype', 'attacks', 'ability',
                 'ttype', 'text', 'is_basic', 'ex', 'retreat')

    def __init__(self, kind, v):
        self.id = v['id']
        self.name = v['name']
        self.kind = 'P' if kind == 'Pokemon' else 'T'
        self.stage = v.get('stage') if self.kind == 'P' else None
        self.frm = v.get('evolves_from')
        self.hp = v.get('hp') or 0
        self.etype = v.get('energy_type')
        self.attacks = [dict(cost=list(a.get('energy_required') or []), title=a['title'],
                             dmg=a.get('fixed_damage') or 0, effect=a.get('effect') or '')
                        for a in (v.get('attacks') or [])]
        ab = v.get('ability')
        self.ability = (ab['title'], ab['effect']) if ab else None
        self.ttype = v.get('trainer_card_type')
        self.text = v.get('effect') or ''
        self.is_basic = self.kind == 'P' and self.stage == 0   # Fossils are Trainers: never Basic
        self.ex = self.name.endswith(' ex')
        self.retreat = len(v.get('retreat_cost') or [])


_DB = None


def db():
    global _DB
    if _DB is None:
        _DB = {'id': {}, 'name': {}}
        for kind, v in cardlib.load():
            c = Card(kind, v)
            _DB['id'][c.id] = c
            _DB['name'].setdefault(c.name, c)
    return _DB


def resolve(cid):
    d = db()['id']
    if cid in d:
        return d[cid]
    s, _, n = cid.rpartition(' ')
    padded = f'{s} {n:0>3}'
    return d.get(padded)


def read_deck(path):
    types, cards = [], []
    for ln in io.open(path, encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        if ln.lower().startswith('energy:'):
            types = [t.strip() for t in re.split(r'[,/]', ln.split(':', 1)[1]) if t.strip()]
            continue
        p = ln.split()
        n, cid = int(p[0]), ' '.join(p[-2:])
        c = resolve(cid)
        if c is None:
            sys.exit(f'{path}: unknown card id {cid!r} (line {ln!r})')
        cards += [c] * n
    if not types:
        sys.exit(f'{path}: no "Energy:" line')
    if len(cards) != 20:
        print(f'WARNING {path}: {len(cards)} cards, not 20', file=sys.stderr)
    return types, cards


def line_of(name):
    """[Basic, (Stage 1), name] following evolves_from in the card database."""
    out = [name]
    seen = 0
    while seen < 4:
        c = db()['name'].get(out[0])
        if not c or not c.frm:
            break
        out.insert(0, c.frm)
        seen += 1
    return out


def missing(cost, attached):
    """Energy still needed to pay `cost` with `attached` (colored first, then Colorless)."""
    left = collections.Counter(attached)
    miss = col = 0
    for sym in cost:
        if sym == 'Colorless':
            col += 1
        elif left[sym] > 0:
            left[sym] -= 1
        else:
            miss += 1
    return miss + max(0, col - sum(left.values()))


def payable(attack, types):
    return all(s == 'Colorless' or s in types for s in attack['cost'])


def est_damage(a):
    d = a['dmg']
    m = re.search(r'(\d+) more damage', a['effect'])
    if m:
        d += int(m.group(1)) * (1 if 'for each' in a['effect'] else 0.5)
    return d


def cost_str(cost):
    return ''.join(LETTER.get(s, s[:1]) for s in cost) or '0'


# ----------------------------------------------------------------------------------------------
# Draw / search / acceleration effects, read from card text
# ----------------------------------------------------------------------------------------------

def parse_filter(s):
    s = re.sub(r'\s+', ' ', s.strip())
    f = {'basic': False, 'hp_max': None, 'etype': None, 'names': None}
    m = re.match(r'(.*?) with (\d+) HP or less$', s)
    if m:
        f['hp_max'], s = int(m.group(2)), m.group(1)
    m = re.search(r'\[(\w)\]', s)
    if m:
        f['etype'] = SYM.get(m.group(1))
        s = re.sub(r'\s*\[\w\]\s*', ' ', s).strip()
    if s in ('Basic Pokémon',):
        f['basic'] = True
    elif s in ('Pokémon',):
        pass
    elif ' or ' in s or s in db()['name']:
        f['names'] = [x.strip() for x in s.split(' or ')]
    else:
        return None
    return f


def fmatch(f, c):
    if c.kind != 'P':
        return False
    if f['basic'] and not c.is_basic:
        return False
    if f['hp_max'] is not None and c.hp > f['hp_max']:
        return False
    if f['etype'] and c.etype != f['etype']:
        return False
    if f['names'] and c.name not in f['names']:
        return False
    return True


def num(w):
    return 1 if w in ('a', 'an') else int(w)


def classify(c):
    """Effects the solitaire model plays, and a note on what it ignores.

    Returns (effects, note). effects is a list of dicts with a 'kind' key; note says what the
    card does for the table ('modeled: ...' / 'ignored: ...').
    """
    effs = []
    if c.kind == 'T':
        t = c.text
        if re.match(r'Draw (\d+|a) cards?\.', t):
            n = num(re.match(r'Draw (\d+|a)', t).group(1))
            effs.append({'kind': 'draw', 'n': n})
        if 'Shuffle your hand into your deck. Draw a card for each card in your opponent' in t:
            effs.append({'kind': 'copycat'})
        m = re.search(r'Put (a|an|\d+) random (.+?) from your deck into your hand', t)
        if m and c.ttype != 'Stadium':
            f = parse_filter(m.group(2))
            if f:
                effs.append({'kind': 'search', 'n': num(m.group(1)), 'filter': f})
        if re.search(r'switch it with a random Pokémon (in|from) your deck', t):
            effs.append({'kind': 'communication'})
        if 'skipping the Stage 1' in t:
            effs.append({'kind': 'rare_candy'})
        m = re.search(r'Put a random \[(\w)\] Pokémon from your deck that evolves from that Pokémon '
                      r'onto that Pokémon to evolve it', t)
        if m:
            effs.append({'kind': 'evolve_from_deck', 'etype': SYM[m.group(1)]})
        m = re.search(r'Attach (a|an|\d+) \[(\w)\] Energy from your discard pile to your Active '
                      r'\[(\w)\] Pokémon', t)
        if m:
            effs.append({'kind': 'attach_from_discard', 'n': num(m.group(1)),
                         'etype': SYM[m.group(2)], 'target_type': SYM[m.group(3)]})
        m = re.search(r'[Tt]ake (a|an|\d+) \[(\w)\] Energy from your Energy Zone and attach it to '
                      r'(?:1 of )?your (Active|Benched)?', t)
        if m and c.ttype != 'Stadium':
            effs.append({'kind': 'accel_trainer', 'n': num(m.group(1)), 'etype': SYM[m.group(2)],
                         'coin': 'flip' in t.lower()})
        if 'may discard the Energy that has been generated in their Energy Zone' in t:
            effs.append({'kind': 'reroll_energy'})
        m = re.search(r'Once during each player\'s turn, that player may put a random (.+?) from '
                      r'their deck into their hand', t)
        if m:
            f = parse_filter(m.group(1))
            if f:
                effs.append({'kind': 'search_stadium', 'filter': f})
        m = re.search(r'At the end of each player\'s turn, that player draws cards until they have '
                      r'(\d+) cards', t)
        if m:
            effs.append({'kind': 'draw_to_eot', 'n': int(m.group(1))})
        m = re.search(r'flip (\d+) coins\. If all of them are heads, that player draws cards until '
                      r'they have (\d+) cards', t)
        if m:
            effs.append({'kind': 'arcade', 'coins': int(m.group(1)), 'to': int(m.group(2))})
        if effs:
            return effs, 'modeled: ' + ', '.join(describe_eff(e) for e in effs)
        if re.search(r'draw|from your deck|Energy', t):
            if 'Knocked Out' in t:
                return effs, 'ignored: needs a knockout (no opponent in the solitaire model)'
            if 'coin' in t:
                return effs, 'ignored: coin-flip effect'
            if 'opponent' in t and 'your deck' not in t and 'your hand' not in t:
                return effs, 'ignored: acts on the opponent'
            return effs, 'ignored: needs a board state the solitaire model does not track'
        return effs, 'ignored: not a draw, search, evolution or Energy effect'
    # Pokemon: abilities
    notes = []
    if c.ability:
        t = c.ability[1]
        act = 'if this Pokémon is in the Active Spot' in t
        m = re.search(r'Once during your turn,(?: if this Pokémon is in the Active Spot,)? you may '
                      r'draw (a|\d+) card', t)
        if m:
            effs.append({'kind': 'draw_ability', 'n': num(m.group(1)), 'active_only': act})
        m = re.search(r'At the end of your turn, if this Pokémon is in the Active Spot, draw (a|\d+) card', t)
        if m:
            effs.append({'kind': 'eot_draw', 'n': num(m.group(1)), 'active_only': True})
        m = re.search(r'[Tt]ake (a|an|\d+) \[(\w)\] Energy from your Energy Zone and attach (?:it|them) '
                      r'to (this Pokémon|the \[\w\] Pokémon in the Active Spot|your Active Pokémon)', t)
        if m:
            effs.append({'kind': 'accel_ability', 'n': num(m.group(1)), 'etype': SYM[m.group(2)],
                         'target': 'self' if m.group(3) == 'this Pokémon' else 'active',
                         'ends_turn': 'your turn ends' in t})
        if re.search(r'At the end of your opponent\'s turn, if this Pokémon is in the Active Spot, '
                     r'put a random card from your deck that evolves from this Pokémon', t):
            effs.append({'kind': 'quick_growth'})
        if 'can evolve during your first turn or the turn you play it' in t:
            effs.append({'kind': 'early_evolve', 'active_only': 'Active Spot' in t})
        m = re.search(r'Once during your turn, you may put a random (.+?) from your deck into your hand', t)
        if m:
            f = parse_filter(m.group(1))
            if f:
                effs.append({'kind': 'search_ability', 'filter': f})
        if effs:
            notes.append('ability modeled: ' + ', '.join(describe_eff(e) for e in effs))
        elif re.search(r'draw|from your deck|Energy Zone', t):
            notes.append(f'ability {c.ability[0]} ignored (condition not modeled)')
    for a in c.attacks:
        t = a['effect']
        if re.search(r'from your deck onto your Bench|Energy from your Energy Zone and attach|'
                     r'from your discard pile into your hand|from your deck into your hand', t):
            notes.append(f'attack {a["title"]} ignored (attacks are not modeled as setup)')
    return effs, '; '.join(notes)


def describe_eff(e):
    k = e['kind']
    if k == 'draw':
        return f'draw {e["n"]}'
    if k == 'copycat':
        return 'shuffle hand in, draw opponent-hand-size'
    if k in ('search', 'search_stadium', 'search_ability'):
        f = e['filter']
        what = ('Basic ' if f['basic'] else '') + (f'[{LETTER[f["etype"]]}] ' if f['etype'] else '') \
            + ('/'.join(f['names']) if f['names'] else 'Pokémon') \
            + (f' (HP<={f["hp_max"]})' if f['hp_max'] else '')
        n = e.get('n', 1)
        return f'search {n} random {what} to hand' + (' (once a turn)' if k != 'search' else '')
    if k == 'communication':
        return 'swap a Pokémon in hand for a random one in the deck'
    if k == 'rare_candy':
        return 'Basic straight to Stage 2 (not own turn 1, not a Basic played this turn)'
    if k == 'evolve_from_deck':
        return f'evolve a [{LETTER[e["etype"]]}] Pokémon from the deck'
    if k == 'attach_from_discard':
        return f'attach {e["n"]} [{LETTER[e["etype"]]}] from discard to the Active'
    if k == 'accel_trainer':
        return f'attach {e["n"]} [{LETTER[e["etype"]]}] from the Energy Zone' + (' (coin)' if e['coin'] else '')
    if k == 'reroll_energy':
        return 'discard the generated Energy for a new one (feeds discard-pile Energy)'
    if k == 'draw_to_eot':
        return f'end of turn: draw up to {e["n"]}'
    if k == 'arcade':
        return f'flip {e["coins"]}: all heads draw up to {e["to"]}'
    if k == 'draw_ability':
        return f'draw {e["n"]} once a turn' + (' (if Active)' if e['active_only'] else '')
    if k == 'eot_draw':
        return f'end of turn draw {e["n"]} (if Active)'
    if k == 'accel_ability':
        return (f'extra {e["n"]} [{LETTER[e["etype"]]}] to ' + ('itself' if e['target'] == 'self' else 'the Active')
                + (', ends the turn' if e['ends_turn'] else ''))
    if k == 'quick_growth':
        return 'evolves from the deck after the opponent\'s turn (if Active)'
    if k == 'early_evolve':
        return 'can evolve on its first turn (if Active)'
    return k


# ----------------------------------------------------------------------------------------------
# The plan: main attacker, combo, lines
# ----------------------------------------------------------------------------------------------

class Plan:
    def __init__(self, path, types, cards, main=None, combo=None, copycat_k=4):
        self.path, self.types, self.cards = path, types, cards
        self.copycat_k = copycat_k
        self.names = collections.Counter(c.name for c in cards)
        self.byname = {}
        for c in cards:
            self.byname.setdefault(c.name, c)
        self.effects, self.effect_notes = {}, {}
        for nm, c in self.byname.items():
            e, note = classify(c)
            self.effects[nm], self.effect_notes[nm] = e, note
        self.has_candy = any(e['kind'] == 'rare_candy' for es in self.effects.values() for e in es)
        self.stage2 = [nm for nm, c in self.byname.items() if c.kind == 'P' and c.stage == 2]
        # main attacker and its attack
        attack_title = None
        if main and ':' in main and main.split(':', 1)[0].strip() in self.byname:
            main, attack_title = [x.strip() for x in main.split(':', 1)]
        self.main = self.find_name(main) if main else self.infer_main()
        mc = self.byname[self.main]
        atks = [a for a in mc.attacks if attack_title is None or a['title'] == attack_title]
        if not atks:
            sys.exit(f'{self.main} has no attack {attack_title!r}')
        pay = [a for a in atks if payable(a, types)]
        self.main_payable = bool(pay)
        pool = pay or atks
        self.main_attack = max(pool, key=lambda a: (est_damage(a), -len(a['cost'])))
        self.main_cost = self.main_attack['cost']
        self.main_line = line_of(self.main)
        self.main_line_set = set(self.main_line)
        # combo pieces: list of alternatives lists
        if combo:
            self.combo = [[self.find_name(x) for x in piece.split('|')] for piece in combo.split(',')]
            self.combo_inferred = False
        else:
            self.combo = [[n] for n in self.infer_combo()]
            self.combo_inferred = True
        self.targets = [self.main] + [n for piece in self.combo for n in piece
                                      if self.byname[n].kind == 'P' and n != self.main]
        self.targets = list(dict.fromkeys(self.targets))
        self.lines = {t: line_of(t) for t in self.targets}
        self.line_names = set(n for t in self.targets for n in self.lines[t])

    def find_name(self, want):
        want = want.strip()
        for nm in self.byname:
            if nm.lower() == want.lower():
                return nm
        hits = [nm for nm in self.byname if want.lower() in nm.lower()]
        if len(hits) == 1:
            return hits[0]
        sys.exit(f'{self.path}: card {want!r} not in the list (have: {", ".join(self.byname)})')

    def infer_main(self):
        best, key = None, None
        for nm, c in self.byname.items():
            if c.kind != 'P':
                continue
            for a in c.attacks:
                if not payable(a, self.types) or est_damage(a) <= 0:
                    continue
                k = (est_damage(a) + (15 if c.ex else 0), -len(a['cost']))
                if key is None or k > key:
                    best, key = nm, k
        if best is None:
            sys.exit(f'{self.path}: no Pokémon with a payable damaging attack; pass --main')
        return best

    def infer_combo(self):
        pieces = [self.main]
        for nm, c in self.byname.items():
            if c.kind == 'P' and nm != self.main and (c.ex or (c.stage and c.ability)):
                pieces.append(nm)
        return pieces[:3]

    def combo_text(self):
        return ' + '.join(' or '.join(p) for p in self.combo)


# ----------------------------------------------------------------------------------------------
# Opening hand, exact
# ----------------------------------------------------------------------------------------------

def opening_exact(plan):
    cards = plan.cards
    N, H = len(cards), 5
    B = sum(c.is_basic for c in cards)
    raw = [comb(B, k) * comb(N - B, H - k) / comb(N, H) for k in range(0, min(B, H) + 1)]
    final = list(raw)
    final[1] += final[0]
    final[0] = 0.0
    only = {}
    for nm, n in plan.names.items():
        if plan.byname[nm].is_basic:
            only[nm] = n * comb(N - B, H - 1) / comb(N, H) + raw[0] * n / B
    # P(at least one copy of each name in the final opening hand)
    present = {}
    for nm, n in plan.names.items():
        c = plan.byname[nm]
        p_raw = 1 - comb(N - n, H) / comb(N, H)
        if c.is_basic:
            present[nm] = p_raw + raw[0] * n / B        # the swap-in brings a uniformly random Basic
        else:
            # hand with >=1 Basic: ordinary; zero-Basic hand: one random hand card goes back
            p = p_raw
            nb = N - B
            lose = 0.0
            for j in range(1, min(n, H) + 1):              # j copies among 5 non-Basic cards
                pj = comb(n, j) * comb(nb - n, H - j) / comb(N, H)   # joint with "no Basic"
                if j == 1:
                    lose += pj * (1 / H)
            present[nm] = p - lose
    return {'N': N, 'B': B, 'raw': raw, 'final': final, 'only': only, 'present': present}


# ----------------------------------------------------------------------------------------------
# Solitaire model
# ----------------------------------------------------------------------------------------------

class Slot:
    __slots__ = ('card', 'name', 'energy', 'placed', 'evolved', 'tool')

    def __init__(self, card, t):
        self.card, self.name, self.energy, self.placed, self.evolved, self.tool = card, card.name, [], t, -1, False


class Solo:
    def __init__(self, P, rng, first, candy=True, effects=True):
        self.P, self.rng, self.first, self.candy, self.fx = P, rng, first, candy, effects
        deck = list(P.cards)
        rng.shuffle(deck)
        if not any(c.is_basic for c in deck[:5]):                   # Pocket's swap-in (engine deck.rs)
            bidx = [i for i in range(5, len(deck)) if deck[i].is_basic]
            bi, hi = rng.choice(bidx), rng.randrange(5)
            deck[hi], deck[bi] = deck[bi], deck[hi]
            rest = deck[5:]
            rng.shuffle(rest)
            deck[5:] = rest
        self.hand, self.deck = deck[:5], deck[5:]
        self.opening_basics = sum(c.is_basic for c in self.hand)
        self.opening_names = set(c.name for c in self.hand)
        self.seen = set(self.opening_names)          # every card name drawn or fetched so far
        self.play = []
        self.used = set()
        self.discard_energy = collections.Counter()
        self.stadium = None
        self.t = 0
        self.setup()

    # -- helpers
    def effs(self, name, *kinds):
        return [e for e in self.P.effects.get(name, ()) if e['kind'] in kinds]

    def draw(self, n):
        for _ in range(n):
            if not self.deck or len(self.hand) >= HAND_LIMIT:
                return
            self.hand.append(self.deck.pop())
            self.seen.add(self.hand[-1].name)

    def fetch(self, c, to_hand=True):
        self.deck.remove(c)
        self.seen.add(c.name)
        if to_hand:
            self.hand.append(c)

    def inplay(self):
        return set(s.name for s in self.play)

    def needed(self):
        """Card names that would move the plan forward and are not yet in play."""
        need = set()
        have = self.inplay()
        for tgt in self.P.targets:
            if tgt in have:
                continue
            line = self.P.lines[tgt]
            top = max([i for i, nm in enumerate(line) if nm in have], default=-1)
            for nm in line[top + 1:]:
                need.add(nm)
            if len(line) == 3 and self.P.has_candy and self.candy and top < 1:
                need.add('Rare Candy')
        for piece in self.P.combo:
            if not self.piece_ok(piece):
                need.update(n for n in piece if self.P.byname[n].kind == 'T')
        return need

    def piece_ok(self, piece):
        have = self.inplay()
        hand = set(c.name for c in self.hand)
        for nm in piece:
            if self.P.byname[nm].kind == 'P':
                if nm in have:
                    return True
            elif nm in hand or nm in self.used or nm == self.stadium:
                return True
        return False

    def prio(self, name):
        if name in self.P.main_line_set:
            return 0
        if name in self.P.line_names:
            return 1
        return 2

    # -- setup
    def setup(self):
        basics = [c for c in self.hand if c.is_basic]

        def akey(c):
            wants = any(e.get('active_only') for e in self.P.effects.get(c.name, ())
                        if e['kind'] in ('eot_draw', 'draw_ability', 'quick_growth', 'early_evolve'))
            return (0 if wants else 1, 1 if c.name in self.P.main_line_set else 0, -c.hp)
        basics.sort(key=akey)
        act = basics[0]
        self.hand.remove(act)
        self.play.append(Slot(act, 0))
        rest = sorted([c for c in self.hand if c.is_basic], key=lambda c: self.prio(c.name))
        for c in rest[:BENCH]:
            self.hand.remove(c)
            self.play.append(Slot(c, 0))

    # -- one own turn
    def turn(self, t):
        self.t = t
        self.sup = self.stad_played = self.stad_used = False
        self.abil = set()
        if t >= 2:
            self.quick_growth()
        self.draw(1)
        self.energy_now = not (self.first and t == 1)
        guard = 0
        progress = True
        while progress and guard < 40:
            guard += 1
            progress = (self.play_stadium() or self.use_stadium() or self.play_items()
                        or self.place_basics() or self.evolve_all() or self.draw_abilities()
                        or self.attach_tools())
            if not progress:
                progress = self.play_supporter()
        self.energy_phase()
        m = self.metrics()
        self.end_phase(m)
        return m

    def quick_growth(self):
        a = self.play[0]
        if self.effs(a.name, 'quick_growth'):
            opts = [c for c in self.deck if c.kind == 'P' and c.frm == a.name]
            if opts:
                c = self.rng.choice(opts)
                self.fetch(c, to_hand=False)
                a.card, a.name, a.evolved = c, c.name, self.t

    def play_stadium(self):
        if self.stad_played:
            return False
        for c in self.hand:
            if c.ttype == 'Stadium' and c.name != self.stadium and (
                    self.P.effects.get(c.name) or any(c.name in p for p in self.P.combo)):
                if not self.fx and not self.effs(c.name, 'reroll_energy') and not any(c.name in p for p in self.P.combo):
                    continue
                self.hand.remove(c)
                self.stadium, self.stad_played = c.name, True
                self.used.add(c.name)
                return True
        return False

    def use_stadium(self):
        if self.stad_used or not self.stadium or not self.fx:
            return False
        for e in self.effs(self.stadium, 'search_stadium', 'arcade'):
            self.stad_used = True
            if e['kind'] == 'search_stadium':
                opts = [c for c in self.deck if fmatch(e['filter'], c)]
                if opts:
                    self.fetch(self.rng.choice(opts))
            else:
                if all(self.rng.random() < 0.5 for _ in range(e['coins'])):
                    self.draw(max(0, e['to'] - len(self.hand)))
            return True
        return False

    def play_items(self):
        for c in list(self.hand):
            if c.ttype != 'Item':
                continue
            for e in self.P.effects.get(c.name, ()):
                k = e['kind']
                if k == 'search' and self.fx:
                    opts = [x for x in self.deck if fmatch(e['filter'], x)]
                    if opts:
                        self.hand.remove(c)
                        self.used.add(c.name)
                        self.search(e, opts)
                        return True
                elif k == 'draw' and self.fx and self.deck:
                    self.hand.remove(c)
                    self.used.add(c.name)
                    self.draw(e['n'])
                    return True
                elif k == 'communication' and self.fx:
                    need = self.needed()
                    spare = [x for x in self.hand if x.kind == 'P' and x.name not in need]
                    want = [x for x in self.deck if x.kind == 'P' and x.name in need]
                    if spare and want:
                        self.hand.remove(c)
                        self.used.add(c.name)
                        give = spare[0]
                        self.hand.remove(give)
                        pool = [x for x in self.deck if x.kind == 'P']
                        got = self.rng.choice(pool)
                        self.fetch(got)
                        self.deck.append(give)
                        self.rng.shuffle(self.deck)
                        return True
                elif k == 'rare_candy' and self.candy and self.t >= 2:
                    for s in sorted(self.play, key=lambda s: self.prio(s.name)):
                        if not s.card.is_basic or s.placed >= self.t or s.evolved == self.t:
                            continue
                        opts = [x for x in self.hand if x.kind == 'P' and x.stage == 2
                                and line_of(x.name)[0] == s.name]
                        if opts:
                            opts.sort(key=lambda x: self.prio(x.name))
                            self.hand.remove(c)
                            self.used.add(c.name)
                            self.evolve(s, opts[0])
                            return True
                elif k == 'evolve_from_deck' and self.t >= 2:
                    for s in sorted(self.play, key=lambda s: self.prio(s.name)):
                        if s.card.etype != e['etype'] or s.placed >= self.t or s.evolved == self.t:
                            continue
                        opts = [x for x in self.deck if x.kind == 'P' and x.frm == s.name and x.etype == e['etype']]
                        if opts:
                            self.hand.remove(c)
                            self.used.add(c.name)
                            x = self.rng.choice(opts)
                            self.fetch(x, to_hand=False)
                            s.card, s.name, s.evolved = x, x.name, self.t
                            return True
        return False

    def search(self, e, opts):
        need = self.needed()
        for _ in range(e['n']):
            if not opts:
                break
            x = self.rng.choice(opts)          # the cards say "random": the pilot does not choose
            opts.remove(x)
            self.fetch(x)
        return need

    def place_basics(self):
        space = BENCH - (len(self.play) - 1)
        if space <= 0:
            return False
        need = self.needed()
        have = self.inplay()
        open_lines = sum(1 for tg in self.P.targets
                         if not any(n in have for n in self.P.lines[tg]))
        basics = sorted([c for c in self.hand if c.is_basic], key=lambda c: (c.name not in need, self.prio(c.name)))
        for c in basics:
            if c.name in need or space > open_lines:
                self.hand.remove(c)
                self.play.append(Slot(c, self.t))
                return True
        return False

    def can_evolve(self, s):
        if s.placed < self.t and s.evolved != self.t and self.t >= 2:
            return True
        return s is self.play[0] and any(e.get('active_only') is not None for e in self.effs(s.name, 'early_evolve'))

    def evolve(self, s, c):
        self.hand.remove(c)
        s.card, s.name, s.evolved = c, c.name, self.t

    def evolve_all(self):
        for s in sorted(self.play, key=lambda s: self.prio(s.name)):
            if not self.can_evolve(s):
                continue
            opts = [c for c in self.hand if c.kind == 'P' and c.frm == s.name]
            if opts:
                opts.sort(key=lambda c: self.prio(c.name))
                self.evolve(s, opts[0])
                return True
        return False

    def draw_abilities(self):
        if not self.fx:
            return False
        for i, s in enumerate(self.play):
            if (i, s.name) in self.abil:
                continue
            for e in self.effs(s.name, 'draw_ability', 'search_ability'):
                if e['kind'] == 'draw_ability' and e['active_only'] and i != 0:
                    continue
                self.abil.add((i, s.name))
                if e['kind'] == 'draw_ability':
                    self.draw(e['n'])
                else:
                    opts = [x for x in self.deck if fmatch(e['filter'], x)]
                    if opts:
                        self.fetch(self.rng.choice(opts))
                return True
        return False

    def attach_tools(self):
        for c in self.hand:
            if c.ttype == 'Tool' and any(c.name in p for p in self.P.combo):
                for s in self.play:
                    if not s.tool:
                        s.tool = True
                        self.hand.remove(c)
                        self.used.add(c.name)
                        return True
        return False

    def play_supporter(self):
        if self.sup or not self.fx:
            return False
        sups = [c for c in self.hand if c.ttype == 'Supporter' and self.P.effects.get(c.name)]
        if not sups:
            return False
        need = self.needed()
        hand_names = set(c.name for c in self.hand)
        best = None
        for c in sups:                                   # 1. a search that finds a needed card
            for e in self.effs(c.name, 'search'):
                if any(fmatch(e['filter'], x) and x.name in need and x.name not in hand_names for x in self.deck):
                    best = (c, e)
                    break
            if best:
                break
        if not best:                                     # 2. plain draw
            for c in sups:
                for e in self.effs(c.name, 'draw'):
                    if self.deck:
                        best = (c, e)
                        break
                if best:
                    break
        if not best:                                     # 3. Copycat, when it adds cards and loses nothing needed
            for c in sups:
                for e in self.effs(c.name, 'copycat'):
                    keep = [x for x in self.hand if x is not c]
                    if len(keep) < self.P.copycat_k and not any(x.name in need for x in keep):
                        best = (c, e)
                        break
                if best:
                    break
        if not best:                                     # 4. any search that finds anything
            for c in sups:
                for e in self.effs(c.name, 'search'):
                    if any(fmatch(e['filter'], x) for x in self.deck):
                        best = (c, e)
                        break
                if best:
                    break
        if not best:
            return False
        c, e = best
        self.hand.remove(c)
        self.used.add(c.name)
        self.sup = True
        if e['kind'] == 'search':
            self.search(e, [x for x in self.deck if fmatch(e['filter'], x)])
        elif e['kind'] == 'draw':
            self.draw(e['n'])
        elif e['kind'] == 'copycat':
            self.deck.extend(self.hand)
            self.hand = []
            self.rng.shuffle(self.deck)
            self.draw(self.P.copycat_k)
        return True

    # -- energy
    def role_cost(self, s):
        if s.name in self.P.main_line_set:
            return 0, self.P.main_cost
        for tg in self.P.targets[1:]:
            if s.name in self.P.lines[tg]:
                c = self.P.byname[tg]
                atks = [a for a in c.attacks if payable(a, self.P.types) and est_damage(a) > 0]
                if atks:
                    return 1, max(atks, key=est_damage)['cost']
        return None, None

    def energy_target(self, et):
        best, key = None, None
        for s in self.play:
            role, cost = self.role_cost(s)
            if cost is None:
                continue
            before = missing(cost, s.energy)
            if missing(cost, s.energy + [et]) >= before:
                continue
            k = (role, -(s.card.stage or 0), before)
            if key is None or k < key:
                best, key = s, k
        return best or self.play[0]

    def energy_phase(self):
        if not self.energy_now:
            return
        types = self.P.types
        et = self.rng.choice(types)
        if self.stadium and self.effs(self.stadium, 'reroll_energy') and not self.stad_used:
            patch = [c for c in self.hand for e in self.effs(c.name, 'attach_from_discard')]
            tgt = self.energy_target(et)
            useless = self.role_cost(tgt)[1] is None or missing(self.role_cost(tgt)[1], tgt.energy + [et]) >= \
                missing(self.role_cost(tgt)[1], tgt.energy)
            if patch or (len(types) > 1 and useless):
                self.stad_used = True
                self.discard_energy[et] += 1
                et = self.rng.choice(types)
        self.energy_target(et).energy.append(et)
        # Energy from the discard pile to the Active (Flame Patch)
        for c in list(self.hand):
            for e in self.effs(c.name, 'attach_from_discard'):
                a = self.play[0]
                if self.discard_energy[e['etype']] > 0 and a.card.etype == e['target_type'] and c in self.hand:
                    self.discard_energy[e['etype']] -= 1
                    a.energy.append(e['etype'])
                    self.hand.remove(c)
                    self.used.add(c.name)
        # Trainers that attach from the Energy Zone
        for c in list(self.hand):
            for e in self.effs(c.name, 'accel_trainer'):
                if c.ttype == 'Supporter' and self.sup:
                    continue
                if e['coin'] and self.rng.random() < 0.5:
                    self.hand.remove(c)
                    self.used.add(c.name)
                    if c.ttype == 'Supporter':
                        self.sup = True
                    continue
                if c in self.hand:
                    self.hand.remove(c)
                    self.used.add(c.name)
                    if c.ttype == 'Supporter':
                        self.sup = True
                    tgt = self.energy_target(e['etype'])
                    tgt.energy.extend([e['etype']] * e['n'])
        # Abilities that attach from the Energy Zone without ending the turn
        for i, s in enumerate(self.play):
            for e in self.effs(s.name, 'accel_ability'):
                if e['ends_turn'] or (i, s.name) in self.abil or e['etype'] not in types:
                    continue
                tgt = s if e['target'] == 'self' else self.play[0]
                if e['target'] == 'active' and tgt.card.etype != e['etype']:
                    continue
                self.abil.add((i, s.name))
                tgt.energy.extend([e['etype']] * e['n'])

    def metrics(self):
        main_slots = [s for s in self.play if s.name == self.P.main]
        return {
            'online': self.P.main_payable and any(missing(self.P.main_cost, s.energy) == 0 for s in main_slots),
            'main': bool(main_slots),
            'stage2': any(s.card.stage == 2 for s in self.play),
            'combo': all(self.piece_ok(p) for p in self.P.combo),
            'pieces': [self.piece_ok(p) for p in self.P.combo],
        }

    def end_phase(self, m):
        if self.energy_now and not m['online']:           # an Ability that ends the turn: only when not attacking
            for i, s in enumerate(self.play):
                for e in self.effs(s.name, 'accel_ability'):
                    if e['ends_turn'] and (i, s.name) not in self.abil and e['etype'] in self.P.types:
                        s.energy.extend([e['etype']] * e['n'])
                        self.abil.add((i, s.name))
                        break
                else:
                    continue
                break
        if self.fx:
            for e in self.effs(self.play[0].name, 'eot_draw'):
                self.draw(e['n'])
            if self.stadium:
                for e in self.effs(self.stadium, 'draw_to_eot'):
                    self.draw(max(0, e['n'] - len(self.hand)))


def solitaire(plan, n, seed):
    """Runs n deals per seat and variant. Returns nested counts."""
    variants = ['normal', 'nodraw']
    if plan.has_candy and plan.stage2:
        variants.append('nocandy')
    out = {}
    for first in (True, False):
        for var in variants:
            rng = random.Random(seed * 2 + (0 if first else 1))    # same deals across variants
            acc = {'online': [0] * (TURNS + 1), 'main': [0] * (TURNS + 1), 'stage2': [0] * (TURNS + 1),
                   'combo': [0] * (TURNS + 1), 'pieces': [[0] * (TURNS + 1) for _ in plan.combo],
                   'basics': collections.Counter(), 'seen': collections.Counter(), 'n': n}
            for _ in range(n):
                g = Solo(plan, rng, first, candy=(var != 'nocandy'), effects=(var != 'nodraw'))
                acc['basics'][g.opening_basics] += 1
                for t in range(1, TURNS + 1):
                    m = g.turn(t)
                    for k in ('online', 'main', 'stage2', 'combo'):
                        acc[k][t] += m[k]
                    for i, ok in enumerate(m['pieces']):
                        acc['pieces'][i][t] += ok
                    if t in (3, 5):
                        for nm in g.seen:
                            acc['seen'][(nm, t)] += 1
            out[(first, var)] = acc
    return out


def earliest(plan, first):
    """Fastest own turn the main attack can be paid with one Energy a turn and no acceleration."""
    stage = plan.byname[plan.main].stage or 0
    st = 1 if stage == 0 else (2 if stage == 1 or plan.has_candy else 3)
    need = len(plan.main_cost)
    en = need + 1 if first else max(1, need)
    if need == 0:
        en = 1
    return max(st, en)


# ----------------------------------------------------------------------------------------------
# Goldfish against the engine's simple bots
# ----------------------------------------------------------------------------------------------

def side_damage(state, side):
    tot = cnt = 0
    for s in state['in_play_pokemon'][side]:
        if s:
            cnt += 1
            tot += s.get('damage_counters') or 0
    return tot, cnt


def hand_card(c):
    kind, v = next(iter(c.items()))
    return kind, v


def parse_game(plies, res, pilot=0):
    opp = 1 - pilot
    starts = [p for p in plies if p['state']['turn_count'] == 1]
    if not starts:
        return None
    first = starts[0]['state']['current_player'] == pilot

    def own(tc):
        if tc < 1:
            return None
        mine = (tc % 2 == 1) == first
        return (tc + 1) // 2 if mine else None

    first_attack = first_real = conceded = None
    for i, p in enumerate(plies):
        s, a = p['state'], p['chosen_action']['action']
        if p['actor'] != pilot or s['turn_count'] < 1 or not (isinstance(a, dict) and 'Attack' in a):
            continue
        t = own(s['turn_count'])
        if t is None:
            continue
        if first_attack is None:
            first_attack = t
        tc = s['turn_count']
        j = i + 1
        while j < len(plies):
            pj = plies[j]
            if pj['state']['turn_count'] != tc or pj['chosen_action']['action'] == 'EndTurn':
                break
            j += 1
        if j >= len(plies):
            real = True                     # the game ended while this attack resolved
        else:
            after = plies[j]['state']
            db0, n0 = side_damage(s, opp)
            db1, n1 = side_damage(after, opp)
            real = after['points'][pilot] > s['points'][pilot] or db1 > db0 or n1 < n0
        if real:
            first_real, conceded = t, s['points'][opp]
            break
    fp = res.get('final_points') or plies[-1]['state']['points']
    outcome = res.get('outcome')
    win = isinstance(outcome, dict) and outcome.get('Win') == pilot
    tie = outcome == 'Tie' or (isinstance(outcome, dict) and 'Tie' in outcome)
    if first_real is None:
        conceded = fp[opp]
    # dead cards: at the pilot's last free decision of each own turn (EndTurn or Attack)
    last = {}
    for i, p in enumerate(plies):
        s, a = p['state'], p['chosen_action']['action']
        if (p['actor'] != pilot or s['turn_count'] < 1 or s['current_player'] != pilot
                or s.get('end_turn_pending') or p['chosen_action'].get('is_stack')):
            continue
        if a == 'EndTurn' or (isinstance(a, dict) and 'Attack' in a):
            t = own(s['turn_count'])
            if t:
                last[t] = i
    dead = {}
    for t, i in last.items():
        p = plies[i]
        blob = '\n'.join(json.dumps(x['action'], ensure_ascii=False) for x in p['playable_actions'])
        candy = '"Rare Candy"' in blob
        d = []
        for c in p['state']['hands'][pilot]:
            kind, v = hand_card(c)
            if f'"id": "{v["id"]}"' in blob:
                continue
            if candy and kind == 'Pokemon' and v.get('stage') == 2:
                continue
            if needs_opp_bench(v['name']):
                continue
            d.append(v['name'])
        dead[t] = (len(p['state']['hands'][pilot]), d)
    return {'first': first, 'first_attack': first_attack, 'first_real': first_real,
            'conceded': conceded, 'win': win, 'tie': tie, 'final': fp,
            'turns': res.get('final_turn'), 'dead': dead}


def goldfish(deck_path, opp_path, pilot, n, seed, engine):
    tmp = tempfile.mkdtemp(prefix='a1_goldfish_')
    try:
        data, resd = os.path.join(tmp, 'data'), os.path.join(tmp, 'res')
        cmd = [engine, 'simulate', deck_path, opp_path, '--players', f'{pilot},aa', '--num', str(n),
               '--seed', str(seed), '--seed-stream', '--data-output', data, '--results-output', resd]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f'engine failed ({r.returncode}): {r.stderr[-1500:]}')
        games = []
        for gid in sorted(os.listdir(data)):
            files = sorted(glob.glob(os.path.join(data, gid, 'ply_*.json')))
            plies = [json.load(io.open(f, encoding='utf-8')) for f in files]
            rp = os.path.join(resd, f'game_{gid}.json')
            res = json.load(io.open(rp, encoding='utf-8')) if os.path.exists(rp) else {}
            g = parse_game(plies, res)
            if g:
                g['seed'] = (res.get('randomness') or {}).get('game_seed')
                games.append(g)
        return games
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# -- scripted pilot: the solitaire policy playing the real engine through the add-on (RawEnv) --

DEFAULT_ADDON_PY = os.path.expanduser('~/.cache/pocket-deck-lab/rules4-addon-072/venv/bin/python')


def akind(a):
    return a if isinstance(a, str) else next(iter(a))


def card_name(c):
    return next(iter(c.values()))['name']


def all_names(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'name' and isinstance(v, str):
                out.add(v)
            else:
                all_names(v, out)
    elif isinstance(obj, list):
        for v in obj:
            all_names(v, out)
    return out


DEFENSIVE = re.compile(r'-\d+ damage from attacks|gets \+\d+ HP')
DEFENSIVE_ACTIVE = re.compile(r'-\d+ damage from attacks|Attacking Pokémon')   # only useful on the Active
OPP_BENCH = re.compile(r"opponent's Benched|Switch out your opponent's Active")


def needs_opp_bench(name):
    """Cards that are unplayable only because the aa opponent never benches (Cyrus, Sabrina...)."""
    c = db()['name'].get(name)
    return bool(c and c.kind == 'T' and OPP_BENCH.search(c.text))
HEAL = re.compile(r'^Heal \d+ damage')


class Pilot:
    """Plays one seat of a real engine game with the same priorities as the solitaire model."""

    def __init__(self, plan):
        self.P = plan

    def c(self, name):
        return self.P.byname.get(name) or db()['name'].get(name)

    def prio(self, name):
        if name in self.P.main_line_set:
            return 0
        if name in self.P.line_names:
            return 1
        return 2

    def needed(self, board, hand):
        have = set(s['name'] for s in board if s)
        need = set()
        for tgt in self.P.targets:
            if tgt in have:
                continue
            line = self.P.lines[tgt]
            top = max([i for i, nm in enumerate(line) if nm in have], default=-1)
            need.update(line[top + 1:])
            if len(line) == 3 and self.P.has_candy and top < 1:
                need.add('Rare Candy')
        for piece in self.P.combo:
            ok = any((nm in have) if self.P.byname[nm].kind == 'P' else (nm in hand) for nm in piece)
            if not ok:
                need.update(n for n in piece if self.P.byname[n].kind == 'T')
        return need

    def best_attack(self, name, energy):
        c = self.c(name)
        if not c:
            return None, 0
        atks = [a for a in c.attacks if payable(a, self.P.types) and est_damage(a) > 0
                and missing(a['cost'], energy) == 0]
        if not atks:
            return None, 0
        a = max(atks, key=est_damage)
        return a, est_damage(a)

    def role_cost(self, name):
        if name in self.P.main_line_set:
            return 0, self.P.main_cost
        for tg in self.P.targets[1:]:
            if name in self.P.lines[tg]:
                atks = [a for a in self.P.byname[tg].attacks if payable(a, self.P.types) and est_damage(a) > 0]
                if atks:
                    return 1, max(atks, key=est_damage)['cost']
        return None, None

    def promote_key(self, s):
        a, dmg = self.best_attack(s['name'], s['energy'])
        c = self.c(s['name'])
        return (0 if dmg > 0 else 1, -dmg, 0 if s['name'] not in self.P.main_line_set else 1, -(s['hp_left'] or 0),
                (c.stage or 0) if c else 0)

    def setup(self, v, acts, K):
        hand = v['me']['hand']
        if v['me']['board'][0] is None:
            opts = [(i, card_name(a['Place'][0])) for i, a in enumerate(acts) if K[i] == 'Place']

            def akey(nm):
                wants = any(e.get('active_only') for e in self.P.effects.get(nm, ())
                            if e['kind'] in ('eot_draw', 'draw_ability', 'quick_growth', 'early_evolve'))
                c = self.c(nm)
                return (0 if wants else 1, 1 if nm in self.P.main_line_set else 0, -(c.hp if c else 0))
            return min(opts, key=lambda x: akey(x[1]))[0]
        opts = [(i, card_name(a['Place'][0])) for i, a in enumerate(acts) if K[i] == 'Place']
        if opts:
            return min(opts, key=lambda x: self.prio(x[1]))[0]
        return K.index('EndTurn')

    def frame(self, v, acts, K):
        board = v['me']['board']
        if all(k in ('Promote', 'Activate') for k in K):
            mine = [(i, a[K[i]]['in_play_idx']) for i, a in enumerate(acts) if a[K[i]]['player'] == v['viewer']]
            if mine:
                return min(mine, key=lambda x: self.promote_key(board[x[1]]))[0]
        if all(k == 'Evolve' for k in K):
            return min(range(len(acts)), key=lambda i: self.prio(card_name(acts[i]['Evolve']['evolution'])))
        if all(k == 'AttachTool' for k in K):
            tool = next(iter(acts[0]['AttachTool']['tool_card'].values()))
            to_active = bool(DEFENSIVE_ACTIVE.search(tool.get('effect') or ''))

            def tkey(i):
                idx = acts[i]['AttachTool']['in_play_idx']
                s = board[idx]
                if to_active:
                    return (0 if idx == 0 else 1, idx)
                return (self.prio(s['name']) if s else 9, idx)
            return min(range(len(acts)), key=tkey)
        if all(k == 'CommunicatePokemon' for k in K):
            need = self.needed(board, v['me']['hand'])
            for i, a in enumerate(acts):
                if card_name(a['CommunicatePokemon']['hand_pokemon']) not in need:
                    return i
        if all(k == 'Heal' for k in K):
            return next((i for i, a in enumerate(acts) if a['Heal']['in_play_idx'] == 0), 0)
        return 0

    def decide(self, v, acts):
        K = [akind(a) for a in acts]
        if v['turn'] == 0:
            return self.setup(v, acts, K)
        if 'EndTurn' not in K:
            return self.frame(v, acts, K)
        me, them = v['me'], v['them']
        board, hand = me['board'], me['hand']
        need = self.needed(board, hand)
        have = set(s['name'] for s in board if s)
        # 1. Basics to the Bench
        space = sum(1 for s in board[1:] if s is None)
        open_lines = sum(1 for tg in self.P.targets if not any(n in have for n in self.P.lines[tg]))
        places = [(i, card_name(a['Place'][0])) for i, a in enumerate(acts) if K[i] == 'Place' and a['Place'][1] != 0]
        places.sort(key=lambda x: (x[1] not in need, self.prio(x[1])))
        for i, nm in places:
            if nm in need or space > open_lines:
                return i
        plays = [(i, a['Play']['trainer_card']) for i, a in enumerate(acts) if K[i] == 'Play']
        act = board[0]
        # 2. Items that draw, search, evolve or move Energy; heals when the Active is hurt
        for i, tc in plays:
            if tc['trainer_card_type'] != 'Item':
                continue
            kinds = set(e['kind'] for e in self.P.effects.get(tc['name'], ()))
            if kinds & {'search', 'draw', 'rare_candy', 'evolve_from_deck', 'communication', 'attach_from_discard'}:
                if 'communication' in kinds and not any(x in need for x in self.P.byname):
                    continue
                return i
            if HEAL.search(tc['effect'] or '') and act and act['hp_card'] and act['hp_left'] <= act['hp_card'] - 20:
                return i
        # 3. evolve, main line first
        evs = [(i, card_name(a['Evolve']['evolution'])) for i, a in enumerate(acts) if K[i] == 'Evolve']
        if evs:
            return min(evs, key=lambda x: self.prio(x[1]))[0]
        # 4. Stadiums and Tools that do something for this plan or add HP / cut damage
        for i, tc in plays:
            nm, t = tc['name'], tc['effect'] or ''
            piece = any(nm in p for p in self.P.combo)
            if tc['trainer_card_type'] == 'Stadium' and (self.P.effects.get(nm) or piece or DEFENSIVE.search(t)
                                                         or 'HP' in t):
                return i
            if tc['trainer_card_type'] == 'Tool' and (piece or DEFENSIVE.search(t) or 'Attacking Pokémon' in t):
                if DEFENSIVE_ACTIVE.search(t):
                    if act and not act['tools']:
                        return i
                elif any(s and not s['tools'] for s in board):
                    return i
        if 'UseStadium' in K:
            st = v.get('stadium')
            kinds = set(e['kind'] for e in self.P.effects.get(st, ())) if st else set()
            patch = any(self.P.effects.get(h) and any(e['kind'] == 'attach_from_discard' for e in self.P.effects[h])
                        for h in hand)
            if kinds & {'search_stadium', 'arcade'} or ('reroll_energy' in kinds and patch):
                return K.index('UseStadium')
        # 5. Abilities that draw, search or add Energy (not the ones that end the turn)
        for i, a in enumerate(acts):
            if K[i] != 'UseAbility':
                continue
            s = board[a['UseAbility']['in_play_idx']]
            for e in self.P.effects.get(s['name'], ()) if s else ():
                if e['kind'] in ('draw_ability', 'search_ability') or (e['kind'] == 'accel_ability' and not e['ends_turn']):
                    return i
        # 6. one Supporter: search for a missing piece, else draw, else Copycat on a small hand, else defence
        sups = [(i, tc) for i, tc in plays if tc['trainer_card_type'] == 'Supporter']
        pick = None
        for i, tc in sups:
            if pick is None and need and any(e['kind'] == 'search' for e in self.P.effects.get(tc['name'], ())):
                pick = i
        for i, tc in sups:
            if pick is None and any(e['kind'] == 'draw' for e in self.P.effects.get(tc['name'], ())):
                pick = i
        for i, tc in sups:
            if pick is None and any(e['kind'] == 'copycat' for e in self.P.effects.get(tc['name'], ())):
                keep = len(hand) - 1
                if keep <= 2 and len(them['hand']) > keep and not any(h in need for h in hand if h != tc['name']):
                    pick = i
        for i, tc in sups:
            t = tc['effect'] or ''
            named = [s['name'] for s in board if s and s['name'] in t]
            fits = act and (not named or act['name'] in t)      # e.g. Jasmine only helps Skarmory ex / Steelix
            if pick is None and fits and (DEFENSIVE.search(t) or (HEAL.search(t) and act['hp_left'] <= act['hp_card'] - 30)):
                pick = i
        if pick is not None:
            return pick
        # 7. the turn's Energy: main line first, then other combo attackers, else the Active.
        #    Exception: a Benched Pokémon can attack now, the Active cannot, and one Energy on the
        #    Active is all its retreat needs -> Energy on the Active, then retreat (step 8).
        att = [(i, a['Attach']) for i, a in enumerate(acts) if K[i] == 'Attach' and a['Attach'].get('is_turn_energy')]
        atks = [(i, a['Attack']) for i, a in enumerate(acts) if K[i] == 'Attack']
        best_now = max([est_damage(dict(dmg=a.get('fixed_damage') or 0, effect=a.get('effect') or ''))
                        for _, a in atks], default=0)
        ready_bench = [j for j, s in enumerate(board) if j and s and s['name'] in self.P.targets
                       and self.best_attack(s['name'], s['energy'])[1] > 0]
        if att and act and best_now <= 0 and ready_bench and 'Retreat' not in K:
            ac = self.c(act['name'])
            if ac and ac.retreat - len(act['energy']) == 1:
                for i, at in att:
                    if at['attachments'][0][2] == 0:
                        return i
        if best_now <= 0 and ready_bench and 'Retreat' not in K:
            for i, tc in plays:          # a Stadium or Item that lowers the Retreat Cost
                if 'Retreat Cost' in (tc['effect'] or '') and 'less' in (tc['effect'] or '') \
                        and tc['trainer_card_type'] in ('Item', 'Stadium'):
                    return i
        if att:
            best, key = None, None
            for i, at in att:
                n_, et, idx = at['attachments'][0]
                s = board[idx]
                role, cost = self.role_cost(s['name'])
                if cost is None:
                    continue
                before = missing(cost, s['energy'])
                if missing(cost, s['energy'] + [et]) >= before:
                    continue
                c = self.c(s['name'])
                k = (role, -((c.stage or 0) if c else 0), before)
                if key is None or k < key:
                    best, key = i, k
            if best is None:
                best = next((i for i, at in att if at['attachments'][0][2] == 0), att[0][0])
            return best
        # 8. retreat to a Benched Pokémon that can attack now, if the Active cannot
        if best_now <= 0:
            rets = []
            for i, a in enumerate(acts):
                if K[i] == 'Retreat':
                    s = board[a['Retreat']]
                    _, dmg = self.best_attack(s['name'], s['energy']) if s and s['name'] in self.P.targets else (None, 0)
                    if dmg > 0:
                        rets.append((i, -dmg, self.prio(s['name'])))
            if rets:
                return min(rets, key=lambda x: (x[2], x[1]))[0]
        # 9. attack: the most damage
        if atks:
            return max(atks, key=lambda x: est_damage(dict(dmg=x[1].get('fixed_damage') or 0,
                                                            effect=x[1].get('effect') or '')))[0]
        # 10. an Ability that ends the turn, when not attacking
        for i, a in enumerate(acts):
            if K[i] == 'UseAbility':
                s = board[a['UseAbility']['in_play_idx']]
                if s and any(e['kind'] == 'accel_ability' and e['ends_turn'] for e in self.P.effects.get(s['name'], ())):
                    return i
        return K.index('EndTurn')


def scripted_games(deck_path, opp_path, n, seed, main, combo, copycat_k):
    """Runs inside the add-on's Python. The pilot plays seat 0; the engine's aa bot plays seat 1."""
    import pdl_rl_env
    types, cards = read_deck(deck_path)
    plan = Plan(deck_path, types, cards, main, combo, copycat_k)
    pilot = Pilot(plan)
    vocab = sorted(set(pdl_rl_env.RawEnv.deck_card_ids(deck_path)) | set(pdl_rl_env.RawEnv.deck_card_ids(opp_path)))
    env = pdl_rl_env.RawEnv(vocab)
    env.set_recording(True)
    games = []
    for k in range(n):
        s = seed + k
        env.reset(deck_path, opp_path, s, [None, 'aa'])
        first = None
        rec = {'seed': s, 'first_real': None, 'first_attack': None, 'conceded': None,
               'main_attack': None, 'main_conceded': None, 'dead': {}, 'forced_turns': 0}
        pending = None          # (own turn, their active HP before my attack, their points, main?)
        hist_seen = 0
        forced_end = False
        last_hand = None
        last_turn = None
        while not env.done:
            v = json.loads(env.describe(0))
            acts = [json.loads(a) for a in env.legal_actions_json()]
            tc = v['turn']
            if first is None and tc >= 1:
                first = (tc % 2 == 1)
            own = ((tc + 1) // 2 if first else tc // 2) if tc >= 1 else 0
            i = pilot.decide(v, acts)
            a = acts[i]
            kd = akind(a)
            if tc >= 1 and kd in ('EndTurn', 'Attack') and 'EndTurn' in [akind(x) for x in acts]:
                live = set()
                for x in acts:
                    if akind(x) != 'EndTurn':
                        all_names(x, live)
                candy = 'Rare Candy' in live
                dead = [h for h in v['me']['hand'] if h not in live and not needs_opp_bench(h)
                        and not (candy and (pilot.c(h) and pilot.c(h).stage == 2))]
                rec['dead'].setdefault(own, (len(v['me']['hand']), dead))
            if kd == 'Attack' and tc >= 1:
                opp_act = v['them']['board'][0]
                is_main = v['me']['board'][0]['name'] == plan.main
                if rec['first_attack'] is None:
                    rec['first_attack'] = own
                if is_main and rec['main_attack'] is None:
                    rec['main_attack'], rec['main_conceded'] = own, v['them']['points']
                if rec['first_real'] is None:
                    pending = (own, opp_act['hp_left'] if opp_act else None, v['them']['points'])
            env.step(i)
            hist = env.history()
            new = hist[hist_seen:]
            hist_seen = len(hist)
            if pending is not None:
                real = None
                if env.done:
                    w, pts, _ = env.result()
                    real = w == 0 or pts[0] > 0
                else:
                    for (p, kind, mv, view) in new:
                        if p == 1 and view:
                            ov = json.loads(view)
                            a0 = ov['me']['board'][0]
                            real = a0 is None or pending[1] is None or a0['hp_left'] < pending[1]
                            break
                    if real is None:
                        nv = json.loads(env.describe(0))
                        a0 = nv['them']['board'][0]
                        real = a0 is None or pending[1] is None or a0['hp_left'] < pending[1]
                if real:
                    rec['first_real'], rec['conceded'] = pending[0], pending[2]
                pending = None
            # turns that ended with only EndTurn legal (auto-played): all of the hand was dead
            for (p, kind, mv, view) in new:
                if p == 0 and kind == 'forced' and mv == '"EndTurn"':
                    forced_end = True
                elif p == 1 and view and forced_end:
                    ov = json.loads(view)
                    ot = ov['turn'] - 1
                    if ot >= 1 and first is not None:
                        own_t = (ot + 1) // 2 if first else ot // 2
                        if own_t not in rec['dead']:
                            rec['dead'][own_t] = (len(ov['them']['hand']), ['(unseen)'] * len(ov['them']['hand']))
                            rec['forced_turns'] += 1
                    forced_end = False
        w, pts, turns = env.result()
        rec.update({'first': bool(first), 'win': w == 0, 'tie': w == -1, 'final': list(pts), 'turns': turns})
        if rec['first_real'] is None:
            rec['conceded'] = pts[1]
        if rec['main_attack'] is None:
            rec['main_conceded'] = pts[1]
        rec['dead'] = {str(k): v for k, v in rec['dead'].items()}
        games.append(rec)
    return games


def run_scripted(deck_path, opp_path, n, seed, main, combo, copycat_k, addon_py):
    if not os.path.exists(addon_py):
        raise RuntimeError(f'add-on Python not found at {addon_py}')
    args = json.dumps([deck_path, opp_path, n, seed, main, combo, copycat_k])
    r = subprocess.run([addon_py, os.path.abspath(__file__), '--worker', args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'scripted pilot failed: {r.stderr[-1500:]}')
    games = json.loads(r.stdout)
    for g in games:
        g['dead'] = {int(k): (v[0], v[1]) for k, v in g['dead'].items()}
    return games


def summarize_goldfish(games):
    out = {}
    for seat in (True, False):
        gs = [g for g in games if g['first'] == seat]
        if not gs:
            continue
        n = len(gs)
        fr = [g['first_real'] for g in gs]
        dead_counts, dead_names, checks = [], collections.Counter(), 0
        for g in gs:
            for t, (hs, d) in g['dead'].items():
                if t <= 4:
                    dead_counts.append(len(d))
                    checks += 1
                    for nm in set(d) - {'(unseen)'}:
                        dead_names[nm] += 1
        att = [x for x in fr if x is not None]
        if 'main_attack' in gs[0]:
            ma = [g['main_attack'] for g in gs]
            main_stats = {
                'main_by3': sum(1 for x in ma if x is not None and x <= 3) / n,
                'main_by4': sum(1 for x in ma if x is not None and x <= 4) / n,
                'main_never': sum(1 for x in ma if x is None) / n,
                'main_conceded': sum(g['main_conceded'] for g in gs) / n,
            }
        else:
            main_stats = {}
        out[seat] = {**main_stats,
            'n': n, 'wins': sum(g['win'] for g in gs), 'ties': sum(g['tie'] for g in gs),
            'by2': sum(1 for x in fr if x is not None and x <= 2) / n,
            'by3': sum(1 for x in fr if x is not None and x <= 3) / n,
            'by4': sum(1 for x in fr if x is not None and x <= 4) / n,
            'never': sum(1 for x in fr if x is None) / n,
            'median': (sorted(att)[len(att) // 2] if att else None),
            'conceded': sum(g['conceded'] for g in gs) / n,
            'conceded2': sum(1 for g in gs if g['conceded'] >= 2) / n,
            'dead': (sum(dead_counts) / len(dead_counts)) if dead_counts else 0.0,
            'dead_names': [(nm, c / checks) for nm, c in dead_names.most_common(5)] if checks else [],
        }
    return out


# ----------------------------------------------------------------------------------------------
# Coverage flag: cards that hit known blind spots of the engine's bots
# ----------------------------------------------------------------------------------------------

def rust_unescape(s):
    s = re.sub(r'\\u\{([0-9a-fA-F]+)\}', lambda m: chr(int(m.group(1), 16)), s)
    return s.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')


def brace_block(src, start):
    i = src.index('{', start)
    depth = 0
    for j in range(i, len(src)):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                return i, j + 1
    return i, len(src)


_EST = None


def estimator_info():
    """(effect text -> Mechanic, mechanics priced by k3, mechanics priced only by spread-aware tiers)."""
    global _EST
    if _EST is not None:
        return _EST
    mp = os.path.join(ROOT, 'engine', 'src', 'actions', 'effect_mechanic_map.rs')
    vf = os.path.join(ROOT, 'engine', 'src', 'players', 'value_functions.rs')
    if not (os.path.exists(mp) and os.path.exists(vf)):
        _EST = False
        return _EST
    src = io.open(mp, encoding='utf-8').read()
    entries = {}
    for m in re.finditer(r'map\.insert\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*Mechanic::(\w+)', src):
        entries[rust_unescape(m.group(1))] = m.group(2)
    v = io.open(vf, encoding='utf-8').read()
    a, b = brace_block(v, v.index('fn estimated_attack_damage_ex('))
    body = v[a:b]
    spread = set()
    k = body.find('if spread_aware {')
    if k >= 0:
        sa, sb = brace_block(body, k)
        spread = set(re.findall(r'Mechanic::(\w+)', body[sa:sb]))
        body = body[:sa] + body[sb:]
    main = set(re.findall(r'Mechanic::(\w+)', body))
    _EST = (entries, main, spread - main)
    return _EST


EXCHANGE_WORDS = re.compile(r'damage|HP|[Hh]eal|[Ss]witch|Active|[Rr]etreat|Confused|Poisoned|Asleep|'
                            r'Burned|Paralyzed|Energy|evolve|Tool|Stadium|Special Condition')
DAMAGE_CHANGE = re.compile(r'more damage|damage for each|remaining HP|does \d+ damage to|'
                           r'damage to 1 of your opponent|instead of|for each heads|damage to your opponent')


def coverage(plan):
    """Per card: which blind-spot rules it hits. Returns list of (name, [(code, text)])."""
    est = estimator_info()
    rows = []
    for nm, c in plan.byname.items():
        flags = []
        texts = []
        if c.kind == 'T':
            texts.append(('card', c.text))
        if c.ability:
            texts.append((f'Ability {c.ability[0]}', c.ability[1]))
        for a in c.attacks:
            if a['effect']:
                texts.append((f'attack {a["title"]}', a['effect']))
        # (a) observation.rs hidden_continuation_reason: text names the opponent and a hand or deck
        for where, t in texts:
            lo = t.lower()
            boiler_smog = where.startswith('Ability') and 'play this pokémon from your hand to evolve' in lo \
                and "opponent's hand" not in lo and "opponent's deck" not in lo
            # the text rule reads the text of a played card, an attack or a used (activated) Ability;
            # automatic Abilities never become a UseAbility move
            automatic = where.startswith('Ability') and not t.startswith('Once during your turn')
            if 'opponent' in lo and ('hand' in lo or 'deck' in lo) and not boiler_smog and not automatic:
                flags.append(('a', f'{where} names the opponent\'s hand or deck: blind k3 leaves it unpriced'))
            if where.startswith('Ability') and re.search(r'end of your opponent\'s turn.*from your deck.*evolve|'
                                                          r'start of your turn.*from your deck', lo):
                flags.append(('a', f'{where} searches this deck automatically: the opposing bot\'s end of turn is left unpriced'))
        # (b) value_functions.rs estimated_attack_damage_ex: effects outside the estimator use printed damage
        if est:
            entries, main, spread = est
            for a in c.attacks:
                e = a['effect']
                if not e:
                    continue
                mech = entries.get(e)
                if mech in main:
                    continue
                # self-damage ("also does 20 damage to itself") leaves the damage to the opponent as printed
                strong = bool(DAMAGE_CHANGE.search(re.sub(r'(also )?does \d+ damage to itself', '', e)))
                why = ('not in the engine\'s effect map' if mech is None else
                       f'mechanic {mech} is priced only by spread-aware tiers' if mech in spread else
                       f'mechanic {mech} has no damage estimator')
                if strong:
                    flags.append(('b', f'attack {a["title"]}: damage-changing effect, {why}; '
                                       f'the bots value it at printed {a["dmg"]}'))
                else:
                    flags.append(('b-', f'attack {a["title"]}: effect not in the damage estimate ({why}); '
                                        f'damage read as printed {a["dmg"]}'))
        # (c) expectiminimax_player.rs is_public_information_action: the reply search never plays
        #     anything from the hand (Trainers, Basics to the Bench, evolutions)
        if c.kind == 'T' and EXCHANGE_WORDS.search(c.text):
            flags.append(('c', 'played from hand and changes the next exchange: the opponent\'s reply search never sees it'))
        elif c.kind == 'P' and c.stage:
            flags.append(('c', 'evolves from hand: the opponent\'s reply search never sees the evolution'
                               + (' or its on-evolve Ability' if c.ability and 'to evolve' in c.ability[1] else '')))
        elif c.kind == 'P' and c.ability and not c.ability[1].startswith('Once during your turn'):
            flags.append(('c', 'a copy benched from hand changes the board (passive Ability): not seen by the reply search'))
        if flags:
            rows.append((nm, flags))
    return rows


# ----------------------------------------------------------------------------------------------
# Page
# ----------------------------------------------------------------------------------------------

def pct(x):
    return f'{100 * x:.0f}%'


def deck_label(path):
    base = os.path.splitext(os.path.basename(path))[0]
    parent = os.path.basename(os.path.dirname(os.path.abspath(path)))
    return f'research-{base}' if parent == 'research' else base


def build(path, main=None, combo=None, games=10000, gold=150, seed=SEED0, engine=DEFAULT_ENGINE,
          opp=DEFAULT_OPP, copycat_k=4, out_dir=DEFAULT_OUT, ladder=None, quiet=False,
          addon_py=DEFAULT_ADDON_PY):
    t0 = time.time()
    types, cards = read_deck(path)
    plan = Plan(path, types, cards, main, combo, copycat_k)
    label = deck_label(path)
    op = opening_exact(plan)
    sol = solitaire(plan, games, seed)
    gold_res = {}
    gold_err = []
    if gold > 0:
        # 'sp': the scripted pilot on the real engine (add-on); 'aa': the engine's own bot as pilot
        try:
            gs = run_scripted(os.path.abspath(path), os.path.abspath(opp), gold, seed, main, combo,
                              copycat_k, addon_py)
            gold_res['sp'] = (seed, summarize_goldfish(gs))
        except Exception as e:  # report, do not hide
            gold_err.append(f'scripted pilot: {e}')
        if not os.path.exists(engine):
            gold_err.append(f'engine not found at {engine}')
        else:
            try:
                s = seed + 5000
                gs = goldfish(os.path.abspath(path), os.path.abspath(opp), 'aa', gold, s, engine)
                gold_res['aa'] = (s, summarize_goldfish(gs))
            except Exception as e:
                gold_err.append(f'aa pilot: {e}')
    gold_err = '; '.join(gold_err) or None
    cov = coverage(plan)
    page, line, row = render(plan, label, op, sol, gold_res, gold_err, cov, games, gold, seed, opp,
                             ladder, time.time() - t0)
    os.makedirs(out_dir, exist_ok=True)
    with io.open(os.path.join(out_dir, f'{label}.md'), 'w', encoding='utf-8') as f:
        f.write(page)
    if not quiet:
        print(line)
    return line, row


def render(plan, label, op, sol, gold_res, gold_err, cov, games, gold, seed, opp, ladder, secs):
    P = plan
    L = []
    w = L.append
    mc = P.byname[P.main]
    main_desc = (f'{P.main} ({"Basic" if not mc.stage else f"Stage {mc.stage}"}), '
                 f'{P.main_attack["title"]} [{cost_str(P.main_cost)}] {P.main_attack["dmg"] or ""}').rstrip()
    g1, g2 = sol[(True, 'normal')], sol[(False, 'normal')]
    n = g1['n']

    def r(acc, k, t):
        return acc[k][t] / acc['n']

    one_basic = op['final'][1]
    # --- one-line summary
    gs = ''
    gavg = {}
    for pilot, (s0, s) in gold_res.items():
        allg = sum(v['n'] for v in s.values())
        keys = set.intersection(*[set(k for k, x in v.items() if isinstance(x, float)) for v in s.values()])
        gavg[pilot] = {k: sum(v[k] * v['n'] for v in s.values()) / allg for k in keys}
    if 'sp' in gavg:
        a = gavg['sp']
        gs = (f'; goldfish (scripted pilot v aa): damaging attack by own T3 {pct(a["by3"])} with '
              f'{a["conceded"]:.1f} pts conceded first, {P.main} attacks by T4 {pct(a["main_by4"])} with '
              f'{a["main_conceded"]:.1f} conceded first, {a["dead"]:.1f} dead cards/turn')
    nflag = sum(1 for _, fl in cov if any(c == 'a' for c, _ in fl))
    line = (f'{label}: one-Basic opening {pct(one_basic)}; {P.main} online by own T3 {pct(r(g1, "online", 3))} first / '
            f'{pct(r(g2, "online", 3))} second (T4 {pct(r(g1, "online", 4))}/{pct(r(g2, "online", 4))}); '
            f'combo by T4 {pct(r(g1, "combo", 4))}/{pct(r(g2, "combo", 4))}{gs}; '
            f'unpriced-text cards (a): {nflag}')
    row = {'label': label, 'ladder': ladder, 'one_basic': one_basic, 'main': P.main,
           'on3': (r(g1, 'online', 3), r(g2, 'online', 3)), 'on4': (r(g1, 'online', 4), r(g2, 'online', 4)),
           'on2': (r(g1, 'online', 2), r(g2, 'online', 2)),
           'combo4': (r(g1, 'combo', 4), r(g2, 'combo', 4)), 'combo': P.combo_text(),
           'stage2': ((r(g1, 'stage2', 3), r(g2, 'stage2', 3)) if P.stage2 else None),
           'gold': gavg, 'flags_a': nflag,
           'flags_b': sum(1 for _, fl in cov if any(c == 'b' for c, _ in fl))}

    w(f'# Consistency: {label}\n')
    w(f'`{os.path.relpath(P.path, ROOT) if os.path.isabs(P.path) else P.path}` · Energy: {", ".join(P.types)} · '
      f'main attacker: {main_desc} · combo: {P.combo_text()}'
      + (' (inferred from the list; pass --combo to name it)' if P.combo_inferred else '') + '\n')
    if ladder:
        w(f'Ladder record: {ladder}\n')
    w(f'**In one line:** {line}\n')
    w('Turns are the player\'s own turns (own turn 1 is your first turn whether you go first or second). '
      'Going first: no Energy on own turn 1, but you draw. Nobody evolves on their own turn 1. '
      f'Solitaire figures come from {n:,} deals per seat (about ±1 point); the opening table is exact.\n')

    # 1. opening
    w('## 1. Opening hand\n')
    w(f'{op["B"]} Basic Pokémon in {op["N"]} cards. The 5-card hand is dealt at random; only a hand with no Basic has '
      'one random card swapped for a random Basic, so extra Basics are not favoured. The opening is the same going '
      'first or second.\n')
    w('| Basics in the opening hand | 1 | 2 | 3 | 4 | 5 |')
    w('|---|---|---|---|---|---|')
    fin = op['final'] + [0.0] * 6
    mcb = sol[(True, 'normal')]['basics']
    w('| exact | ' + ' | '.join(pct(fin[k]) for k in range(1, 6)) + ' |')
    w('| solitaire check | ' + ' | '.join(pct(mcb[k] / n) for k in range(1, 6)) + ' |\n')
    w(f'**Exactly one Basic: {pct(one_basic)}** (of which {pct(op["raw"][0])} are swap-in hands that had none).\n')
    w('| Only Basic in the hand is… | chance | | Card in the opening hand | chance |')
    w('|---|---|---|---|---|')
    only = sorted(op['only'].items(), key=lambda kv: -kv[1])
    key_cards = [nm for nm in P.byname if nm in P.line_names or any(nm in p for p in P.combo)]
    pres = [(nm, op['present'][nm]) for nm in key_cards]
    for i in range(max(len(only), len(pres))):
        a = f'{only[i][0]} | {pct(only[i][1])}' if i < len(only) else ' | '
        b = f'{pres[i][0]} | {pct(pres[i][1])}' if i < len(pres) else ' | '
        w(f'| {a} | | {b} |')
    w('')

    # 2. main attacker
    w('## 2. Main attacker online\n')
    if not P.main_payable:
        w(f'**{P.main}\'s attack cost [{cost_str(P.main_cost)}] cannot be paid with this deck\'s Energy types.**\n')
    w(f'"Online" = {P.main} in play (Active or Bench) with the Energy for {P.main_attack["title"]} '
      f'[{cost_str(P.main_cost)}] attached, at the moment you would attack. Fastest possible without acceleration: '
      f'own turn {earliest(P, True)} going first, {earliest(P, False)} going second.\n')
    w('| | going first T2 | T3 | T4 | going second T2 | T3 | T4 |')
    w('|---|---|---|---|---|---|---|')
    w(f'| {P.main} online | ' + ' | '.join(pct(r(g1, 'online', t)) for t in (2, 3, 4)) + ' | '
      + ' | '.join(pct(r(g2, 'online', t)) for t in (2, 3, 4)) + ' |')
    w(f'| {P.main} in play (any Energy) | ' + ' | '.join(pct(r(g1, 'main', t)) for t in (2, 3, 4)) + ' | '
      + ' | '.join(pct(r(g2, 'main', t)) for t in (2, 3, 4)) + ' |')
    d1, d2 = sol[(True, 'nodraw')], sol[(False, 'nodraw')]
    w(f'| online, draw/search cards not played | ' + ' | '.join(pct(r(d1, 'online', t)) for t in (2, 3, 4)) + ' | '
      + ' | '.join(pct(r(d2, 'online', t)) for t in (2, 3, 4)) + ' |\n')
    w('Where "in play" is well above "online", Energy is the limit (one a turn); where both are low, '
      'finding the cards is the limit. The last row shows what the list\'s draw and search cards add.\n')

    # 3. stage 2
    w('## 3. Stage 2 in play\n')
    if not P.stage2:
        w('No Stage 2 in the list.\n')
    else:
        w(f'Stage 2 cards: {", ".join(P.stage2)}. Rare Candy in the list: {"yes" if P.has_candy else "no"}.\n')
        w('| | going first T3 | T4 | going second T3 | T4 |')
        w('|---|---|---|---|---|')
        w('| any Stage 2 in play (list as built) | ' + ' | '.join(pct(r(g1, 'stage2', t)) for t in (3, 4)) + ' | '
          + ' | '.join(pct(r(g2, 'stage2', t)) for t in (3, 4)) + ' |')
        if (True, 'nocandy') in sol:
            c1, c2 = sol[(True, 'nocandy')], sol[(False, 'nocandy')]
            w('| same deals, Rare Candy never played | ' + ' | '.join(pct(r(c1, 'stage2', t)) for t in (3, 4)) + ' | '
              + ' | '.join(pct(r(c2, 'stage2', t)) for t in (3, 4)) + ' |')
        w('')

    # 4. combo
    w('## 4. Combo assembled\n')
    w(f'Pieces: {P.combo_text()}. A Pokémon piece counts when it is in play; a Trainer piece when it is in hand '
      'or already played.\n')
    w('| by own turn | 2 | 3 | 4 | 5 |')
    w('|---|---|---|---|---|')
    w('| going first | ' + ' | '.join(pct(r(g1, 'combo', t)) for t in (2, 3, 4, 5)) + ' |')
    w('| going second | ' + ' | '.join(pct(r(g2, 'combo', t)) for t in (2, 3, 4, 5)) + ' |\n')
    if len(P.combo) > 1:
        w('Each piece on its own (going first / second):\n')
        w('| piece | by T3 | by T5 |')
        w('|---|---|---|')
        for i, piece in enumerate(P.combo):
            a1, a2 = g1['pieces'][i], g2['pieces'][i]
            w(f'| {" or ".join(piece)} | {pct(a1[3] / n)} / {pct(a2[3] / n)} | {pct(a1[5] / n)} / {pct(a2[5] / n)} |')
        w('')

    w('### Drawing each card\n')
    w('Each card, drawn or fetched at least once by own turn 3 / by own turn 5 (the opening hand counts; '
      'going first, the list\'s draw and search cards played; "no draw" = the same deals with them left in hand):\n')
    w('| card | copies | by T3 | by T5 | by T3, no draw | by T5, no draw |')
    w('|---|---|---|---|---|---|')
    s1, s0 = sol[(True, 'normal')]['seen'], sol[(True, 'nodraw')]['seen']
    for nm in P.byname:
        w(f'| {nm} | {P.names[nm]} | {pct(s1[(nm, 3)] / n)} | {pct(s1[(nm, 5)] / n)} | '
          f'{pct(s0[(nm, 3)] / n)} | {pct(s0[(nm, 5)] / n)} |')
    w('')

    # 5. goldfish
    w('## 5. Goldfish against the engine\n')
    if gold <= 0:
        w('Skipped (--goldfish 0).\n')
    elif gold_err and not gold_res:
        w(f'Not run: {gold_err}\n')
    if gold > 0 and gold_res:
        if gold_err:
            w(f'Partly run: {gold_err}\n')
        w(f'The real engine (rules4: {os.path.relpath(DEFAULT_ENGINE, ROOT)} and the pdl_rl_env 0.7.2 add-on built '
          f'from the same rules) plays this list against `{os.path.relpath(opp, ROOT)}` piloted by the engine\'s '
          '`aa` bot (attach-and-attack: it puts its Energy on the Active and attacks whenever it can, and nothing '
          'else). Because the engine lists End Turn first among the legal moves and `aa` takes the first move when '
          'it cannot attach or attack, `aa` never benches a Pokémon, not even at setup, and never plays a Trainer: '
          'the opponent is one Active Pokémon, and knocking it out wins. That makes it a fixed clock (here mostly '
          'Hoopa ex: 30 a turn from its first Energy, 100 from its third), not a real opponent.\n')
        w('Two pilots for this list. **sp** (scripted pilot, the main reading): the solitaire model\'s priorities '
          'playing the real engine through the add-on: benches Basics, plays the draw, search, Rare Candy and '
          'Energy cards, evolves, puts Energy on the main line, attaches defensive Tools, heals a hurt Active, '
          'retreats to a Pokémon that can attack, and attacks for the most damage. **aa** (the brief\'s pilot): '
          'the engine\'s own bot on this side too, so both sides have a single Pokémon and the game ends at the '
          'first knockout; its "points conceded" can never exceed what one knockout gives. `et` ends every turn '
          'at once and never attacks, so it is not used. '
          f'{gold} games per pilot; the coin decides who goes first.\n')
        w('"Damaging attack" = the list\'s first attack that damaged or knocked out the opposing Active (poison '
          'it applied counts). "Conceded" = the opponent\'s points at that moment (or at the end if it never came). '
          '"Main attacks" = the first attack by the main attacker. "Dead" = cards in hand at the end of the '
          'turn that the rules did not let you play then (own turns 1-4; a second Supporter after one was '
          'played counts as dead; cards that need an opposing Bench, such as Cyrus and Sabrina, are left out '
          'because this opponent never has one).\n')
        w('| pilot | seat | games | won | damaging attack by T2 | by T3 | by T4 | never | '
          'points conceded before it | conceded 2+ | main attacks by T3 | by T4 | never | conceded before main | '
          'dead cards / turn |')
        w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        for pilot, (s0, summ) in gold_res.items():
            for seat in (True, False):
                if seat not in summ:
                    continue
                v = summ[seat]
                ms = (f'{pct(v["main_by3"])} | {pct(v["main_by4"])} | {pct(v["main_never"])} | {v["main_conceded"]:.2f}'
                      if 'main_by3' in v else '- | - | - | -')
                w(f'| {pilot} | {"first" if seat else "second"} | {v["n"]} | {pct(v["wins"] / v["n"])} | '
                  f'{pct(v["by2"])} | {pct(v["by3"])} | {pct(v["by4"])} | {pct(v["never"])} | '
                  f'{v["conceded"]:.2f} | {pct(v["conceded2"])} | {ms} | {v["dead"]:.1f} |')
        w('')
        for pilot, (s0, summ) in gold_res.items():
            names = collections.Counter()
            tot = 0
            for seat, v in summ.items():
                for nm, fr in v['dead_names']:
                    names[nm] += fr * v['n']
                tot += v['n']
            if names:
                w(f'Most often dead at end of turn ({pilot}): ' + ', '.join(
                    f'{nm} {pct(c / tot)}' for nm, c in names.most_common(4)) + ' of turn-ends.\n')
        seeds = ', '.join(f'{p}: {s0:,} to {s0 + gold - 1:,}' for p, (s0, _) in gold_res.items())
        w(f'Engine game seeds (one per game): {seeds}. The won column is against a single Pokémon that never '
          'plays a Trainer and means little; read the tempo columns. The `aa` opponent also never plays a card, '
          'so its hand grows and Copycat draws more than it would on the ladder.\n')

    # 6. coverage
    w('## 6. Coverage flag\n')
    w('Cards that hit known blind spots of the engine\'s bots, so the simulator\'s numbers for this list '
      'are less trustworthy where these cards matter:\n'
      '- **(a)** text names the opponent\'s hand or deck: blind k3 leaves the move unpriced '
      '(engine/src/observation.rs `hidden_continuation_reason`).\n'
      '- **(b)** attack effect outside the damage estimator: the bots value the attack at printed damage '
      '(engine/src/players/value_functions.rs `estimated_attack_damage_ex`, fallback `_ => fixed`; effect texts '
      'read from engine/src/actions/effect_mechanic_map.rs). "b-" = the effect does not change damage (status, '
      'self-damage), so only its side effect is unvalued.\n'
      '- **(c)** played from hand: the opponent-reply search (the `o` tiers such as b3o3n4; k3 has no reply ply) '
      'only considers attacks, retreats, Abilities, draws and the turn\'s Energy '
      '(engine/src/players/expectiminimax_player.rs `is_public_information_action`).\n')
    if estimator_info() is False:
        w('Engine source not found beside this file: (b) not computed.\n')
    if cov:
        w('| card | flags |')
        w('|---|---|')
        for nm, fl in cov:
            w(f'| {nm} ×{P.names[nm]} | ' + '<br>'.join(f'**({c})** {t}' for c, t in fl) + ' |')
        w('')
    na = [nm for nm, fl in cov if any(c == 'a' for c, _ in fl)]
    nb = [nm for nm, fl in cov if any(c == 'b' for c, _ in fl)]
    verdict = []
    if na:
        verdict.append(f'k3 leaves {", ".join(na)} unpriced')
    if nb:
        verdict.append(f'the damage of {", ".join(nb)} is read as printed')
    w('**Reading:** ' + ('; '.join(verdict) + '. Bot numbers for this list are untrusted to that extent.'
                         if verdict else 'no (a) or (b) hits; only the reply-search limit (c) applies.') + '\n')

    # effect table
    w('## Draw, search and Energy effects in this list\n')
    w('What the solitaire model plays (card text from lib/card.py):\n')
    w('| card | text | model |')
    w('|---|---|---|')
    for nm, c in P.byname.items():
        note = P.effect_notes.get(nm) or ''
        if c.kind == 'P' and not note:
            continue
        text = c.text if c.kind == 'T' else (f'Ability {c.ability[0]}: {c.ability[1]}' if c.ability else '')
        if c.kind == 'P' and not c.ability:
            text = '; '.join(f'{a["title"]}: {a["effect"]}' for a in c.attacks if a['effect'])
        w(f'| {nm} ×{P.names[nm]} | {text} | {note} |')
    w('')
    w('## How the solitaire pilot plays\n')
    w('Setup: all Basics in hand go into play (Active: a Basic with an "if Active" draw Ability, else one '
      'outside the main line). Each own turn: draw; then repeat until nothing changes: play a Stadium that does '
      'something here, use it, play Items (Poké Ball and other searches take a random matching card, as printed; '
      'Rare Candy on the main line first), bench Basics the plan needs (others only while the Bench has room to '
      'spare), evolve (main line first), use draw Abilities, attach Tool pieces; when nothing else moves, one '
      'Supporter: a search that finds a missing piece, else a draw, else Copycat when the hand is small and holds '
      f'nothing needed (Copycat assumes the opponent holds {P.copycat_k} cards). Then the turn\'s Energy '
      '(random among the declared types) goes to the main line first, then other combo attackers, else the '
      'Active; Energy from the discard or from Abilities is added; then the check; an Ability that ends the '
      'turn is used only when the main attacker cannot attack. No opponent, no knockouts, no retreat, no '
      'attacks (attack effects that set up, such as Flock or Glittering Gift, are ignored), no coin-flip '
      'Supporters. Hand limit 10.\n')
    w(f'Generated by `lib/consistency.py` in {secs:.0f} s; solitaire seed {seed:,} (Python random, same deals '
      'across variants).\n')
    return '\n'.join(L), line, row


# ----------------------------------------------------------------------------------------------
# Batch: pages for a list of decks, plus the ANCHORS.md table
# ----------------------------------------------------------------------------------------------

def read_batch(path):
    rows = []
    for ln in io.open(path, encoding='utf-8'):
        if not ln.strip() or ln.startswith('#'):
            continue
        p = [x.strip() for x in ln.rstrip('\n').split('\t')]
        p += [''] * (6 - len(p))
        rows.append({'deck': p[0], 'main': p[1] or None, 'combo': p[2] or None,
                     'ladder': p[3] or None, 'screen': p[4] or None, 'role': p[5] or ''})
    return rows


def anchors_table(results):
    L = ['| List | Role | Ladder | k3 screen | 1-Basic open | Main online by T3 (1st / 2nd) | by T4 (1st / 2nd) | '
         'Combo by T4 (1st / 2nd) | sp: damaging attack by T3 | sp: pts conceded before it | '
         'sp: main attacks by T4 | sp: pts conceded before main | sp: dead cards/turn | aa: damaging attack by T3 | '
         '(a) cards |',
         '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for b, row in results:
        gd = row['gold']

        def g(p, k, f):
            return f(gd[p][k]) if gd.get(p) and k in gd[p] else '-'
        f2 = lambda x: f'{x:.2f}'   # noqa: E731
        L.append(f'| {row["label"]} (main {row["main"]}) | {b["role"]} | {b["ladder"] or "-"} | {b["screen"] or "-"} | '
                 f'{pct(row["one_basic"])} | {pct(row["on3"][0])} / {pct(row["on3"][1])} | '
                 f'{pct(row["on4"][0])} / {pct(row["on4"][1])} | {pct(row["combo4"][0])} / {pct(row["combo4"][1])} | '
                 f'{g("sp", "by3", pct)} | {g("sp", "conceded", f2)} | {g("sp", "main_by4", pct)} | '
                 f'{g("sp", "main_conceded", f2)} | {g("sp", "dead", lambda x: f"{x:.1f}")} | '
                 f'{g("aa", "by3", pct)} | {row["flags_a"]} |')
    return '\n'.join(L)


def write_anchors(out_dir, results, lines, args):
    path = os.path.join(out_dir, 'ANCHORS.md')
    table = anchors_table(results)
    auto = ('<!-- table:start (rewritten by lib/consistency.py --batch) -->\n'
            f'Run: {args.games:,} solitaire deals per seat, {args.goldfish} engine games per pilot per list, '
            f'seeds from {args.seed:,} (list i: solitaire and scripted-pilot seeds {args.seed:,} + 10,000·i, '
            f'aa-pilot seeds that +5,000), opponent `{os.path.relpath(args.opponent, ROOT)}` piloted by aa. '
            'sp = scripted pilot on the real engine; aa = the engine\'s attach-and-attack bot as pilot.\n\n'
            + table + '\n\nOne line per list:\n\n' + '\n'.join(f'- {x}' for x in lines) + '\n'
            '<!-- table:end -->')
    if os.path.exists(path):
        old = io.open(path, encoding='utf-8').read()
        if '<!-- table:start' in old and '<!-- table:end -->' in old:
            a = old.index('<!-- table:start')
            b = old.index('<!-- table:end -->') + len('<!-- table:end -->')
            new = old[:a] + auto + old[b:]
        else:
            new = old.rstrip() + '\n\n' + auto + '\n'
    else:
        new = '# Consistency harness: anchors\n\n' + auto + '\n'
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(new)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ['--worker']:            # internal: runs under the add-on's Python
        a = json.loads(argv[1])
        print(json.dumps(scripted_games(*a)))
        return
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split('\n', 1)[1])
    ap.add_argument('deck', nargs='?', help='deck file (named or ids-only format)')
    ap.add_argument('--main', help='main attacker name, optionally "Name:Attack title" (default: inferred)')
    ap.add_argument('--combo', help='combo pieces, comma-separated; alternatives with | (default: inferred)')
    ap.add_argument('--games', type=int, default=10000, help='solitaire deals per seat (default 10000)')
    ap.add_argument('--goldfish', type=int, default=150, help='engine games per pilot (aa and er); 0 skips (default 150)')
    ap.add_argument('--seed', type=int, default=SEED0, help=f'seed (default {SEED0:,})')
    ap.add_argument('--engine', default=DEFAULT_ENGINE, help='deckgym engine program (Linux)')
    ap.add_argument('--opponent', default=DEFAULT_OPP, help='goldfish opponent list, piloted by aa')
    ap.add_argument('--addon-python', default=DEFAULT_ADDON_PY,
                    help='Python with the pdl_rl_env add-on, for the scripted pilot (default: the rules4 add-on venv)')
    ap.add_argument('--copycat-hand', type=int, default=4, help='opponent hand size Copycat assumes (default 4)')
    ap.add_argument('--out', default=DEFAULT_OUT, help='output folder')
    ap.add_argument('--batch', help='TSV: deck, main, combo, ladder, k3 screen, role (one list per line)')
    ap.add_argument('--ladder', help='ladder record to print on the page')
    args = ap.parse_args(argv)
    args.opponent = os.path.abspath(args.opponent)
    if args.batch:
        rows = read_batch(args.batch)
        results, lines = [], []
        for i, b in enumerate(rows):
            s = args.seed + 10000 * i
            print(f'[{i + 1}/{len(rows)}] {b["deck"]}  seeds {s:,} (solitaire, sp) / {s + 5000:,} (aa)',
                  file=sys.stderr, flush=True)
            path = b['deck'] if os.path.isabs(b['deck']) else os.path.join(ROOT, b['deck'])
            line, row = build(path, b['main'], b['combo'], args.games, args.goldfish, s, args.engine,
                              args.opponent, args.copycat_hand, args.out, b['ladder'], addon_py=args.addon_python)
            results.append((b, row))
            lines.append(line)
        write_anchors(args.out, results, lines, args)
        return
    if not args.deck:
        ap.error('give a deck file or --batch')
    build(args.deck, args.main, args.combo, args.games, args.goldfish, args.seed, args.engine,
          args.opponent, args.copycat_hand, args.out, args.ladder, addon_py=args.addon_python)


if __name__ == '__main__':
    main()
