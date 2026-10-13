#!/usr/bin/env python3
"""position_cards.py: one text card per position for reading (board, his turn as the review wrote it, his plan, km3's plans over 12 seeds, km3's scores at its first step).
usage: position_cards.py POSITIONS.json KM3_SUMMARY.json RUNS_DIR POSITION_LIST.json QA_ROOT > position_cards.txt   (QA_ROOT = the Recording_QA folder)"""
import collections, glob, json, os, re, sys

pos_f, sum_f, runs, list_f, batch = sys.argv[1:6]
POS = {p['id']: p for p in json.load(open(pos_f, encoding='utf-8'))}
SUM = {s['id']: s for s in json.load(open(sum_f, encoding='utf-8'))}
LIST = {r['position_id']: r for r in json.load(open(list_f, encoding='utf-8'))}


def fix(s):
    """the reviews were saved with their UTF-8 read as cp1252 in places"""
    try:
        return s.encode('cp1252').decode('utf-8') if ('â' in s or 'Ã' in s) else s
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


BATCHES = ('BATCH_2026-10-12_NEW_LONG_VIDEOS', 'BATCH_2026-10-12_ADDITIONAL_TWO', 'BATCH_2026-10-13_NEWEST_TWO', 'BATCH_2026-10-13_REMAINING_SIX')


def review_rows(game_short):
    """{turn: (who, text)} from the game's REVIEW.md table (the packets use 3 to 5 columns: | turn | player (and interval) | [interval |] account |)"""
    d = [x for b in BATCHES for x in glob.glob(os.path.join(batch, b, '2026*_' + game_short.split('_', 1)[1] + '*'))]
    rows = {}
    if not d or not os.path.exists(os.path.join(d[0], 'REVIEW.md')):
        return rows
    for line in open(os.path.join(d[0], 'REVIEW.md'), encoding='utf-8').read().split('\n'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and cells[0].isdigit() and re.match(r'(owner|opponent)', cells[1], re.I):
            rows[int(cells[0])] = (cells[1].split(',')[0].lower(), fix(max(cells[2:], key=len)))
    return rows


def pk(b):
    s = f"{b['card']} {b['hp']}hp"
    if b.get('energy'):
        s += ' E:' + ''.join(e[0] for e in b['energy']) + f"({len(b['energy'])})"
    if b.get('tools'):
        s += ' T:' + ','.join(t.rsplit(' ', 2)[0] for t in b['tools'])
    if b.get('behind'):
        s += ' under:' + ','.join(x.rsplit(' ', 2)[0] for x in b['behind'])
    if b.get('effects'):
        s += ' fx:' + json.dumps(b['effects'])
    return s


def scores(err, pid, seed, step):
    """-> [(score, label)] of the first decision of one seed"""
    block, got, grab = [], [], False
    for line in open(err, encoding='utf-8', errors='replace'):
        if line.startswith('PGSTEP'):
            grab = line.strip() == f'PGSTEP {pid} seed {seed} free {step}'
            continue
        if grab and line.startswith('PGDUMP') and 'candidates=' not in line:
            m = re.match(r'PGDUMP\s+(-?[\d.]+)\s+(.*)$', line.rstrip('\n'))
            if m:
                got.append((float(m.group(1)), m.group(2)))
    return got


cache = {}
for pid, p in POS.items():
    s, L = SUM.get(pid, {}), LIST.get(pid, {})
    game = p['game'].replace('kw-', '')
    if game not in cache:
        cache[game] = review_rows(game)
    rows = cache[game]
    print('=' * 100)
    print(f"{pid}  game turn {p['turn_count']} (his turn {p['his_turn']})  points {p['points'][0]}-{p['points'][1]}  switch2: {L.get('switch2_flag')}  usable: {p['usable']}")
    print('ME   active:', pk(p['me']['board'][0]) if p['me']['board'] else '-')
    print('     bench :', '; '.join(pk(b) for b in p['me']['board'][1:]) or '-')
    print('     hand  :', ', '.join(h.rsplit(' ', 2)[0] for h in p['me']['hand']), '| discard:', ', '.join(h.rsplit(' ', 2)[0] for h in p['me']['discard']) or '-', '| zone now/next:', p['me']['energy_now'], p['me']['energy_next'])
    print('OPP  active:', pk(p['opp']['board'][0]) if p['opp']['board'] else '-')
    print('     bench :', '; '.join(pk(b) for b in p['opp']['board'][1:]) or '-', '| hand', p['opp']['hand_count'], '| discard:', ', '.join(h.rsplit(' ', 2)[0] for h in p['opp'].get('discard', [])) or '-', '| stadium:', (p['stadium'] or {}).get('card'))
    if p.get('turn_effects') or any(b.get('effects') for b in p['opp']['board']):
        print('     effects:', json.dumps(p.get('turn_effects')), [b.get('effects') for b in p['opp']['board']])
    who, row = rows.get(p['turn_count'], (None, None))
    print('HIS TURN (review):', (row or '-')[:900])
    print('HIS PLAN:', p['his_plan'], '(ended)' if p['his_plan_ended'] else '(not ended / cut)')
    if s:
        print(f"KM3 modal ({s['modal_n']}/{s['n']}):", s['modal'], '| agreement first', s['same_first'], 'plan', s['same_plan'], '|', s.get('cat'))
        others = [(pl, n) for pl, n in s['plans'] if pl != s['modal']]
        for pl, n in others[:3]:
            print(f'      other ({n}/12):', pl)
        err = os.path.join(runs, f'err_{pid}.txt')
        sc = scores(err, pid, 1, 0)
        if sc:
            ranked = sorted(sc, reverse=True)
            print('KM3 first-step scores (seed 1):', '; '.join(f'{lab} {v:.0f}' for v, lab in ranked[:6]))
            if s['his'] and s['his'][0] != s['modal'][0]:
                for i, (v, lab) in enumerate(ranked):
                    if lab == s['his'][0]:
                        print(f"      his first action {lab} is rank {i + 1} of {len(ranked)}, {ranked[0][0] - v:.0f} below the top")
    print('NOTES:', p['notes'][:300].replace('\n', ' '))
