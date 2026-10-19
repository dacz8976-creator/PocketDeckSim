#!/usr/bin/env python3
"""Which Stadium uses does the plan lister treat as a chance event? (synthetic positions only)

  python3 stadium_use_audit.py [--out validation/stadium_use_audit.json]

For each Stadium with a once-per-turn use in the card pool, a synthetic position puts it in play (the opponent's, so the player's list is unaffected) and the plan
lister is asked for the player's plans. Playing a Stadium from the hand is never chance (tests/test_ai_judge.py); using one is chance when its effect has more
than one outcome, touches the player's own deck, or depends on hidden information. This is the lister's rule; the laptop's exam-side rule is "UseStadium is chance
only when the Stadium in play is Mesagoza", which agrees on Mesagoza and is looser for the others (see FROZEN.md).
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge  # noqa: E402

FIX = os.path.join(HERE, 'tests', 'fixtures')
STADIUMS = [('Mesagoza', 'B2a 093'), ('Fragrant Forest', 'B3 153'), ('Area Zero', 'B3a 074'), ('Kid\'s Room', 'B3b 069'), ('Arcade', 'B4a 072'), ('Rainbow Cave', 'B4 155')]


def positions():
    base = json.load(open(os.path.join(FIX, 'mini_positions.json'), encoding='utf-8'))
    stad = next(p for p in base if p['id'] == 'MINI-STADIUM')
    out = []
    for name, cid in STADIUMS:
        p = json.loads(json.dumps(stad))
        p['id'] = f'AUDIT-{name}'
        p['me']['hand'] = ['Glimmet B3a 044']  # a Basic in hand, for Area Zero
        p['stadium'] = {'card': f'{name} {cid}', 'owner': 1}
        p['opp']['hand_count'] = 4
        out.append(p)
    return out


def audit():
    import tempfile
    pos = positions()
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(pos, f)
        path = f.name
    try:
        recs = judge.list_plans([p['id'] for p in pos], path, os.path.join(FIX, 'decks'))
    finally:
        os.unlink(path)
    rows = {}
    for p in pos:
        name = p['id'][len('AUDIT-'):]
        plans = recs[p['id']]['plans']
        used = [x for x in plans if x['labels'][-1] == 'UseStadium']
        later = [x for x in plans if 'UseStadium' in x['labels'] and x['labels'][-1] != 'UseStadium']
        rows[name] = {'use_offered': bool(used or later), 'use_is_chance': bool(used) and all(x['end'] == 'chance' for x in used),
                      'final_kinds': sorted({x['final'].get('kind') for x in used}), 'plans_continuing_after_the_use': len(later)}
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    a = ap.parse_args()
    rows = audit()
    text = json.dumps(rows, indent=1)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, 'w').write(text + '\n')
    print(text)


if __name__ == '__main__':
    main()
