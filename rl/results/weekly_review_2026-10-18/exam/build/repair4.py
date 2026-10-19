"""v1.5 (live laptop, Oct 19): Dustin's answers to the 5 pending points, with the coordinator's labelling decisions. No bot output used."""
import json, collections, os, shutil, sys
sys.path.insert(0, '/home/dacz8976/exam/repair')
from label_adapter import to_judge
F = '/home/dacz8976/exam/commit/exam_2026-10-19.json'
SNAP = '/home/dacz8976/exam/commit/exam_2026-10-19.v14_f71de2a9.json'
if not os.path.exists(SNAP):
    shutil.copy(F, SNAP)
d = json.load(open(SNAP))
assert d['format'] == 'pds-exam-v1.4', d['format']
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget')
def cut(line, stadium):
    mesa = 'Mesagoza' in json.dumps(stadium or '')
    for i, l in enumerate(line):
        if l == 'Play:Mesagoza':
            mesa = True
        if l.startswith(DRAW) or (l == 'UseStadium' and mesa):
            return line[:i + 1]
    return list(line)
def strategic(line):
    return [l for l in line if not (l.startswith(DRAW) or l in ('EndTurn', 'UseStadium') or l.startswith('Play:Quick-Grow'))]
def scope(line, seg):
    s = strategic(line)
    if all(l in seg for l in s):
        return 'full'
    return 'none' if not any(l in seg for l in s) else 'partial'
P = {p['id']: p for p in d['points']}
ANS = {
 'LAD-20261014_161324000_iOS-t5': "At this point I had lost 1 point to the opponent. Whimsicott ex getting knocked out, ends the game. Sacrificing spinarak is what I weighed as the better option since I needed one more turn to get the second energy to attack with whimsicott. Using the Xspeed and putting cottonee up could have been considered, but I was hoping to have two whimsicott ex to use and be able to retreat for free (with the x speed), if/when I needed to.",
 'LAD-20261014_225451000_iOS-t4': "The bench rotom ex had 1 energy, it needed two to attack, so pulling it up prevented it from being able to get the second energy onto it. And then the active Rotom is on the bench, where it can get energy in two turns, but that isn't scary. That was my thinking.",
 'LAD-20261016_031512000_iOS-t2': "Not attacking was a mistake. Benching pawniard is an option, but I've expressed my opinion on this before, ideally I have muk, regigas and two glimmora active, then after one dies I play pawniard so it doesn't take up a spot or get sniped before I can use it.",
 'LAD-20261016_031512000_iOS-t8': "Pawniard had one energy attached already, if when I'm able to evolve him to kingambit, I will be able to attach the necessary second energy to him then. I know I'm two turns from being able to use regigigas's attack, but there wasn't much benefit to attaching a second energy to pawniard either. I don't think any choices I made would have let me win that game with the cards I drew.",
 'LAD-20261014_215114000_iOS-t10': "The game was over. I was losing no matter what I did. Attaching energy to rattata would be the smart play normally, but it wasn't going to change anything",
}
SRC = 'Dustin, Oct 19 (relayed verbatim by the coordinator), with the coordinator\'s labelling decision'
log = []
for pid, words in ANS.items():
    p = P[pid]; a = p['answer']; st = p['position'].get('stadium')
    assert a['status'] == 'pending_dustin', pid
    pend = a.pop('pending_alternatives', [])
    a['dustin_answer'] = {'words': words, 'source': SRC}
    a['status'] = 'final'
    a['recorded_move_acceptable'] = True
    a.setdefault('rejected_alternatives', [])
    rej = lambda x, why: a['rejected_alternatives'].append({'line': x['line'], 'reason': x.get('reason', ''), 'rejected_because': why})
    if pid == 'LAD-20261014_161324000_iOS-t5':
        for x in pend:
            rej(x, "Dustin: Whimsicott ex knocked out ends the game (he was at 0-1, an ex gives 2 points), so retreating into it is not acceptable")
        his = a['his_move']; i = his.index('EndTurn')
        line = his[:i] + [to_judge('Play:X Speed'), to_judge('Retreat:2'), 'EndTurn']
        a['acceptable'].append({'line': line, 'first_segment': cut(line, st),
            'reason': "Dustin: X Speed and Cottonee Active as the sacrifice 'could have been considered'; he preferred keeping X Speed for a later free retreat with two Whimsicott ex"})
        log.append(f'{pid}: key his move; X Speed->Whimsicott rejected; X Speed->Cottonee added as acceptable')
    elif pid == 'LAD-20261014_225451000_iOS-t4':
        for x in pend:
            rej(x, "Dustin: Sabrina pulled up the benched Rotom ex with 1 Energy so it can't get its second; the unpowered one on the Bench isn't a threat")
        log.append(f'{pid}: key his move (Sabrina); keep-Sabrina line rejected')
    elif pid == 'LAD-20261016_031512000_iOS-t2':
        key = next(x for x in pend if not any(l.startswith('Place:Pawniard') for l in x['line']))
        a['key_line'] = key['line']; a['key_source'] = 'dustin'
        a['recorded_move_acceptable'] = False
        a['rejected_alternatives'].append({'line': a['his_move'], 'reason': 'his recorded move', 'rejected_because': "Dustin: 'Not attacking was a mistake.'"})
        for x in pend:
            if x is not key:
                rej(x, "Dustin's plan: Pawniard stays in hand until a Pokémon has been knocked out, so it doesn't take a Bench spot or get sniped")
        old = p['answer_kind']; p['answer_kind'] = 'attack now'; a['answer_kind_v14'] = old
        log.append(f'{pid}: key = Poké Ball, Darkness on Glimmet, Hang Down, Pawniard kept in hand; recorded line and bench-Pawniard rejected; answer_kind {old} -> attack now')
    elif pid == 'LAD-20261016_031512000_iOS-t8':
        for x in pend:
            x['reason'] = "Dustin: both are reasonable ('there wasn't much benefit to attaching a second energy to pawniard either')"
            a['acceptable'].append(x)
        log.append(f'{pid}: both lines acceptable')
    elif pid == 'LAD-20261014_215114000_iOS-t10':
        key = pend[0]
        a['key_line'] = key['line']; a['key_source'] = 'dustin'
        a['recorded_move_acceptable'] = False
        a['rejected_alternatives'].append({'line': a['his_move'], 'reason': 'his recorded move', 'rejected_because': "Dustin: attaching to Rattata 'would be the smart play normally'; the game was already decided"})
        p['decided_game'] = True
        log.append(f'{pid}: key = attach Water to the new Rattata; recorded line rejected as play quality; decided_game true')
    # key and segments
    keyl = a.get('key_line', a['his_move'])
    a['first_segment'] = cut(keyl, st)
    for x in a['acceptable']:
        x['first_segment'] = cut(x['line'], st)
    a.pop('ambiguous_resolved', None)
for p in d['points']:
    a = p['answer']; keyl = a.get('key_line', a['his_move'])
    p.setdefault('decided_game', False)
    by = {'key': scope(keyl, a['first_segment'])}
    for i, x in enumerate(a['acceptable']):
        by[f'alt{i}'] = scope(x['line'], x['first_segment'])
    a['segment_scope_by_line'] = by
    a['segment_scope_his'] = by['key']
    a['segment_scope'] = 'full' if all(v == 'full' for v in by.values()) else ('none' if by['key'] == 'none' else 'partial')
d['format'] = 'pds-exam-v1.5'
d['key_rule'] = ("The answer key is what a good player of his decks would do, using his judgment. It is his recorded move by default "
                 "(answer.his_move, which always stays the record); where he said otherwise, answer.key_line holds the key and "
                 "answer.recorded_move_acceptable is false (2 points: 031512 t2, 215114 t10). answer.first_segment is the key's first segment. "
                 "His words are in answer.dustin_answer. Lines he or the coordinator ruled out are in answer.rejected_alternatives and never count. "
                 "decided_game marks a point whose game was already lost; reports show those separately.")
d['scoring'] = d['scoring'].replace("Points with answer.status 'pending_dustin' are NOT scored until he answers; their pending alternatives never count.",
                                    "All 51 points are scored (Dustin answered the 5 pending points on Oct 19; see key_rule). Points with decided_game true are also reported separately.")
# coverage recount
dk = d['categories']['deck_kinds']; ak = d['categories']['answer_kinds']
cov = {f'{a} x {b}': 0 for a in dk for b in ak}
for p in d['points']:
    for k in p['deck_kinds']:
        cov[f"{k} x {p['answer_kind']}"] += 1
d['coverage'] = cov
json.dump(d, open(F, 'w'), indent=1, ensure_ascii=False)
print('\n'.join(log))
print('status', collections.Counter(p['answer']['status'] for p in d['points']))
print('answer kinds', collections.Counter(p['answer_kind'] for p in d['points']))
print('scope all 51', collections.Counter(p['answer']['segment_scope'] for p in d['points']))
print('full by deck', collections.Counter(p['deck'] for p in d['points'] if p['answer']['segment_scope'] == 'full'))
print('full by kind', collections.Counter(p['answer_kind'] for p in d['points'] if p['answer']['segment_scope'] == 'full'))
print('5 points scope', {pid: P[pid]['answer']['segment_scope'] for pid in ANS})
print('acceptable lines', sum(len(p['answer']['acceptable']) for p in d['points']), 'rejected', sum(len(p['answer'].get('rejected_alternatives', [])) for p in d['points']))
print('coverage', {k: v for k, v in cov.items() if v})
print('scoring pending clause replaced:', 'pending_dustin' not in d['scoring'])
