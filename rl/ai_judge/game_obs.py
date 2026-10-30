"""Observation -> the position fields judge.render_prompt reads; the deck check of the game bot."""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def decks_dir_and_key(deck_file):
    return os.path.dirname(deck_file), os.path.basename(deck_file)[:-4]


def pad_id(set_and_number):
    """'A1 5' -> 'A1 005': the engine pads card numbers to three digits (engine/src/deck.rs)."""
    parts = set_and_number.split()
    return f'{parts[-2]} {parts[-1]:0>3}'


def deck_counter(deck_file):
    c = Counter()
    with open(deck_file, encoding='utf-8') as f:
        for line in f:
            w = line.split()
            if len(w) >= 3 and w[0].isdigit():
                c[pad_id(' '.join(w[-2:]))] += int(w[0])
    return c


def pos_for_prompt(pos_like, pid, deck_key):
    tc = pos_like['turn_count']
    me, opp = pos_like['me'], pos_like['opp']
    out = {
        'id': pid,
        'deck': deck_key,
        'turn_count': tc,
        'his_turn': (tc + 1) // 2,
        'stadium': None if pos_like.get('stadium') is None else {'card': pos_like['stadium']['card'], 'owner': pos_like['stadium']['owner']},
        # key order: 'turn' then 'effect'; no fixture holds a non-empty list and the 92 hold none, so this order is the module's own choice
        'turn_effects': [{'turn': e['turn'], 'effect': e['effect']} for e in pos_like.get('turn_effects') or []],
        'me': {'hand': list(me['hand']), 'discard': list(me['discard']), 'board': [dict(b) for b in me['board']], 'knockouts': me['knockouts']},
        'opp': {'board': [dict(b) for b in opp['board']], 'discard': list(opp['discard'])},
    }
    return out


def declared_classes(pos):
    out = []
    if 'discard_n' in pos.get('opp', {}):
        out.append('opp.discard_n')
    if 'knockouts' not in pos.get('me', {}):
        out.append('me.knockouts_absent')
    tc = pos.get('turn_count')
    if 'his_turn' not in pos or pos.get('his_turn') != (tc + 1) // 2:
        out.append('his_turn')
    if 'turn_effects' not in pos:
        out.append('turn_effects_absent')
    return out
