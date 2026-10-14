#!/usr/bin/env python3
"""check_review_fixes.py [positions_all.json] [decks_dir]: the changed positions against the laptop's list (REVIEW_POSITIONS_laptop.md, Oct 14): one line per finding, PASS or FAIL.

Reads the regenerated positions (default: ../positions_all.json) and checks, for each blocker and major of the review and for the frame-only facts it recorded, the value the review says the
position must have. It does not re-read the ledgers: it is the list of what the review asked for, as a check that can be run again after any regeneration. Exit status 1 when a line fails.
Not checked here (open, see V3_CHANGES.md): the Starting Plains HP in pg_pos.rs, the typed harness label of the Energy choice, 030351's phantom Fighting on the second Igglybuff, the minor findings."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
pos_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'positions_all.json')
decks_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', 'decks')
with open(pos_path, encoding='utf-8') as f:
    POS = {p['id'].replace('KW-26', '', 1): p for p in json.load(f)}       # '1013_015011000-t01' style keys


def at(game, turn):
    return POS[f'{game}-t{turn:02d}']


def games(prefix):
    return sorted(k for k in POS if k.startswith(prefix))


def names(cards):
    return [c.rsplit(' ', 2)[0] for c in cards]


def board_cards(p, side):
    return [b['card'] for b in p[side]['board']]


RESULTS = []


def check(label, ok, detail=''):
    RESULTS.append((label, bool(ok), detail))


# ---- blockers
for t, want_me, want_opp in ((1, ['Pawniard', 'Alolan Grimer'], ['Falinks']), (3, ['Pawniard', 'Regigigas', 'Alolan Grimer'], ['Falinks', 'Tyrogue'])):
    p = at('1013_015011000', t)
    check(f'B1 015011 t{t:02d}: the Bench of both sides is on the board', names(board_cards(p, 'me')) == want_me and names(board_cards(p, 'opp')) == want_opp, f"me {board_cards(p, 'me')} opp {board_cards(p, 'opp')}")
for k in games('1013_030351000-t'):
    p = POS[k]
    darkrai = [c for c in board_cards(p, 'opp') if c.startswith('Darkrai')]
    check(f'B2 {k}: every Darkrai of the opponent is B2b 040 (Bad Dreams)', all(c == 'Darkrai B2b 040' for c in darkrai), str(darkrai))
dratini_any = [(k, c) for k in games('1013_022530000-t') for side in ('me',) for b in POS[k][side]['board'] for c in [b['card']] + b.get('behind', []) + POS[k][side]['hand'] + POS[k][side]['discard'] if c.startswith('Dratini')]
check('B3 022530: no Dratini A3b 051 anywhere in the six positions, and his Dratini is B4 116', dratini_any and all(c == 'Dratini B4 116' for _, c in dratini_any), str(sorted({c for _, c in dratini_any})))
deck_file = os.path.join(decks_dir, 'KW261013_022530000.txt')
if os.path.exists(deck_file):
    with open(deck_file, encoding='utf-8') as f:
        deck_text = f.read()
    check('B3 022530: the deck file holds 2 Dratini B4 116 and no A3b 051', '2 Dratini B4 116' in deck_text and 'A3b 051' not in deck_text, deck_text.replace('\n', ' | ')[:200])

# ---- majors
for k in games('1012_010706000-t'):
    check(f'M1 {k}: the opponent next Energy is Psychic', POS[k]['opp']['energy_next'] == 'Psychic', POS[k]['opp']['energy_next'])
for k in games('1013_010003000-t'):
    check(f'M1 {k}: the opponent next Energy is Water or Lightning, not his deck\'s Darkness', POS[k]['opp']['energy_next'] in ('Water', 'Lightning'), POS[k]['opp']['energy_next'])
check('M1 203719 t17: the opponent next Energy is Lightning', at('1012_203719000', 17)['opp']['energy_next'] == 'Lightning', at('1012_203719000', 17)['opp']['energy_next'])
for game, t, i_prom, promoted in (('1012_203719000', 7, 'Promote:0@2', 'Glimmora'), ('1012_210823000', 8, 'Promote:0@1', 'Glimmora'), ('1013_020824000', 11, 'Promote:0@1', 'Pawniard')):
    plan = at(game, t)['his_plan']
    j = plan.index('Play:Ilima') if 'Play:Ilima' in plan else -1
    check(f'M2 {game} t{t:02d}: Play:Ilima is followed by {i_prom} ({promoted})', j >= 0 and plan[j + 1:j + 2] == [i_prom], str(plan))
plan = at('1012_210823000', 8)['his_plan']
check('M2 210823 t08: the Energy goes to the promoted Glimmora (slot 0), not the new Glimmet', 'Attach:1Darkness@0 zone' in plan and 'Attach:1Darkness@1 zone' not in plan, str(plan))
plan = at('1013_020824000', 11)['his_plan']
check('M2 020824 t11: Promote:0@1 then Retreat:1 (not Retreat:3)', plan.index('Promote:0@1') < plan.index('Retreat:1') and 'Retreat:3' not in plan, str(plan))
for game, t in (('1012_210041000', 8), ('1012_210823000', 2), ('1012_210823000', 4)):
    check(f'M3 {game} t{t:02d}: the Mesagoza use is a UseStadium step', 'UseStadium' in at(game, t)['his_plan'], str(at(game, t)['his_plan']))
for game, t in (('1012_010706000', 9), ('1012_230258000', 11), ('1013_010003000', 9)):
    plan = at(game, t)['his_plan']
    check(f'M4 {game} t{t:02d}: Giga Turbo is followed by its Energy target (fx)', 'Attack:Giga Turbo' in plan and plan[plan.index('Attack:Giga Turbo') + 1:][:1] and plan[plan.index('Attack:Giga Turbo') + 1].startswith('Attach:1Colorless@') and plan[plan.index('Attack:Giga Turbo') + 1].endswith(' fx'), str(plan))
for k in games('1012_210823000-t'):
    p = POS[k]
    check(f'M5 {k}: the opponent has no Alolan Meowth; the left Bench Meowth is B2 124', not any('Alolan Meowth' in c for c in board_cards(p, 'opp')) and 'Meowth B2 124' in board_cards(p, 'opp'), str(board_cards(p, 'opp')))
for t, want in ((5, 6), (7, 7), (9, 6)):
    check(f'M6 015659 t{t:02d}: the opponent hand is {want}', at('1013_015659000', t)['opp']['hand_count'] == want, str(at('1013_015659000', t)['opp']['hand_count']))
check('M6 015659: no Rare Candy in the opponent discard in any position', not any('Rare Candy' in ' '.join(POS[k]['opp']['discard']) for k in games('1013_015659000-t')), '')
plan = at('1013_022530000', 9)['his_plan']
check("M7 022530 t09: Dragon's Blessing's choice (Fighting, onto the Active) follows the Ability", 'Ability' in plan and plan[plan.index('Ability') + 1:][:1] == ['AttachTypedFromDiscard:Fighting@0'], str(plan))
check('M8 010706 t15: the Poké Ball that found nothing is not his first move', at('1012_010706000', 15)['his_plan'][:1] != ['Play:Poké Ball'], str(at('1012_010706000', 15)['his_plan']))
for k in games('1013_022530000-t'):
    tools = [x for b in POS[k]['opp']['board'] for x in b.get('tools', [])]
    turn = int(k.rsplit('-t', 1)[1])
    check(f'M9 {k}: the opponent cape is Elegant Cape B3b 065, never Giant Cape', not any(x.startswith('Giant Cape') for x in tools) and (turn < 3 or 'Elegant Cape B3b 065' in tools), str(tools))

# ---- the frame-only facts the review recorded
for game, turns in (('1012_010706000', {3: 6, 5: 7, 7: 8}), ('1012_203719000', {7: 4, 9: 3, 11: 4, 13: 4}), ('1012_225319000', {8: 4})):
    for t, want in turns.items():
        check(f'F {game} t{t:02d}: the opponent hand is {want} (the frames)', at(game, t)['opp']['hand_count'] == want, str(at(game, t)['opp']['hand_count']))

width = max(len(l) for l, _, _ in RESULTS)
fails = [r for r in RESULTS if not r[1]]
for label, ok, detail in RESULTS:
    print(('PASS  ' if ok else 'FAIL  ') + label + ('' if ok else f'   <- {detail}'))
print(f'\n{len(RESULTS) - len(fails)} of {len(RESULTS)} checks pass')
sys.exit(1 if fails else 0)
