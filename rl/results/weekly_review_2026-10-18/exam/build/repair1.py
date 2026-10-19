"""Checkpoint-1 repairs (Astra 20261019T0415Z): input/record corrections only. No bot output used."""
import json, copy, re
SRC = '/home/dacz8976/exam/commit/exam_2026-10-19.v11_43265934.json'
OUT = '/home/dacz8976/exam/commit/exam_2026-10-19.json'
d = json.load(open(SRC))
CHANCE = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer',
          'Play:Lucky Ice Pop', 'UseStadium', 'ChooseRandomEvolutionTarget')
def is_chance(l, stadium_is_mesagoza=True):
    return any(l.startswith(c) for c in CHANCE)
def cut(line):
    for i, l in enumerate(line):
        if is_chance(l):
            return line[:i + 1]
    return list(line)
log = []
SAFE = "opponent's list unknown; opponent hand size, discard and Energy are estimates from the video review"
for p in d['points']:
    pos, a = p['position'], p['answer']
    pid = p['id']
    p['fresh'] = True
    # (1) candidate-facing text: no build notes (some named later draws or coin results)
    a['build_notes'] = {'approximate_reason': pos.get('approximate_reason', ''), 'notes': pos.get('notes', '')}
    pos['approximate_reason'] = SAFE
    pos['notes'] = ''
    # (6) first-player first turn: no Energy in the zone
    if pid == 'LAD-20261016_024253000_iOS-t1':
        pos['me']['energy_now'] = None
        log.append(f'{pid}: energy_now set to none (going first, turn 1 has no Energy); Attach must leave legal_root')
    # (7) Mesagoza: playing it is deterministic, its flip (UseStadium) is the chance step; the flip found Glimmet
    if pid == 'LAD-20261016_020517000_iOS-t2':
        hm = a['his_move']; i = hm.index('Play:Mesagoza'); hm.insert(i + 1, 'UseStadium')
        log.append(f'{pid}: his_move now {hm} (the review: Mesagoza heads found Glimmet)')
    # (8) concrete random-evolution target (from the review)
    tgt = {'LAD-20261014_153908000_iOS-t6': 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}',   # benched Spinarak
           'LAD-20261014_164328000_iOS-t4': 'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Grass}'}   # Active Cottonee
    if pid in tgt:
        a['his_move'] = [tgt[pid] if l == 'ChooseRandomEvolutionTarget' else l for l in a['his_move']]
        log.append(f'{pid}: target {tgt[pid]}')
    # (4) pending Dustin: alternatives do NOT count until he answers; the point is held out of scoring
    pend = [x for x in a['acceptable'] if 'pending' in x.get('reason', '').lower()]
    if a.get('ambiguous'):
        a['status'] = 'pending_dustin'
        a['pending_alternatives'] = pend
        a['acceptable'] = [x for x in a['acceptable'] if x not in pend]
    else:
        a['status'] = 'final'
    # first segments, recomputed with one rule for every line
    a['first_segment'] = cut(a['his_move'])
    for x in a['acceptable'] + a.get('pending_alternatives', []):
        x['first_segment'] = cut(x['line'])
    # (3) draw-first variants, settled now
    seg = a['first_segment']
    if len(seg) > 1 and is_chance(seg[-1]) and not seg[0].startswith('ChooseRandom') and not seg[0].startswith('Play:Quick-Grow') and seg[-1] != 'UseStadium':
        ch = seg[-1]
        if ch.startswith('Play:Copycat'):
            a['draw_first'] = {'accepted': False, 'reason': 'Copycat shuffles the hand away, so the cards he played first would be lost; his order is the plan'}
        else:
            rest = [l for l in a['his_move'] if l != ch or a['his_move'].index(l) != a['his_move'].index(ch)]
            alt = [ch] + [l for i, l in enumerate(a['his_move']) if i != a['his_move'].index(ch)]
            a['draw_first'] = {'accepted': True, 'reason': f'{ch.split(":",1)[1]} first only adds information; the actions he took before it stay available after it'}
            a['acceptable'].append({'line': alt, 'reason': 'draw-first order of his own line (settled before any candidate output)', 'first_segment': [ch]})
        log.append(f"{pid}: draw-first {'accepted' if a['draw_first']['accepted'] else 'not accepted'} ({ch})")
    # (2) honest scope: does the scored first segment contain his turn's strategic actions?
    strat = [l for l in a['his_move'] if not is_chance(l) and l not in ('EndTurn',) and not l.startswith('Play:Quick-Grow')]
    inseg = [l for l in strat if l in seg]
    a['segment_scope'] = 'full' if len(inseg) == len(strat) else ('none' if not inseg else 'partial')
    a['strategic_actions_after_segment'] = [l for l in strat if l not in seg]
d['format'] = 'pds-exam-v1.2'
json.dump(d, open(OUT, 'w'), indent=1, ensure_ascii=False)
import collections
print('\n'.join(log))
print('scope', collections.Counter(p['answer']['segment_scope'] for p in d['points']))
print('scope by kind', collections.Counter((p['answer_kind'], p['answer']['segment_scope']) for p in d['points']))
print('status', collections.Counter(p['answer']['status'] for p in d['points']))
print('pending alts', sum(len(p['answer'].get('pending_alternatives', [])) for p in d['points']), 'acceptable now', sum(len(p['answer']['acceptable']) for p in d['points']))
