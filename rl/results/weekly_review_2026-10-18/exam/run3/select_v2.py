#!/usr/bin/env python3
"""Exam v2's usable set, mechanically (PREREG_RUN3 section 2; addendum 5, G3): a turn is a candidate point ONLY where BOTH codings call it
usable, the usability job (inv_out_p<k>/inventory.json) and the blind second coding (selcode_out_p<k>/coding.json).

  select_v2.py EXAM_V2_DIR OUT_DIR [--parts 3]

- "Calls it usable", per coding (symmetric, conservative): board_known, hand_known, move_known and real_choice are all "yes" (section 2's
  definition) AND the coding's own `usable` verdict is true. A coding whose verdict and fields disagree on a turn calls it not usable;
  those turns are counted per coding.
- The turn list is selcode_in_p<k>/turns.json (made from the first coding by make_turns.py). Every listed turn must be coded exactly once
  by each coding; a turn either coding lacks is not a point, and is reported.
- Writes OUT_DIR/agreement.json (every turn: both codings' four fields, verdicts and reasons, copied, never read here),
  OUT_DIR/selection.json (the candidates: point id, game, global turn, clip, part, the game's folder) and OUT_DIR/SELECTION.md (counts).
  Prints counts only. Refuses to overwrite.
"""
import argparse, collections, json, os, sys

FIELDS = ('board_known', 'hand_known', 'move_known', 'real_choice')


def one(d, keys, what):
    found = [k for k in keys if k in d]
    if not found:
        sys.exit(f'{what}: none of {keys}: stop')
    if len({json.dumps(d[k]) for k in found}) > 1:
        sys.exit(f'{what}: two different values under {found}: stop')
    return d[found[0]]


def yes(v):
    return isinstance(v, str) and v.strip().lower() == 'yes'


def verdict(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str) and v.strip().lower() in ('yes', 'true'):
        return True
    if v is None or (isinstance(v, str) and v.strip().lower() in ('no', 'false')):
        return False
    sys.exit(f'a usable verdict {v!r} is neither true nor false: stop')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('exam_v2')
    ap.add_argument('out')
    ap.add_argument('--parts', type=int, default=3)
    a = ap.parse_args()
    if os.path.exists(a.out):
        sys.exit(f'{a.out} exists already: stop')
    agreement, cands, table, notes = {}, [], {}, []
    for k in range(1, a.parts + 1):
        turns = json.load(open(f'{a.exam_v2}/selcode_in_p{k}/turns.json', encoding='utf-8'))['turns']
        listed = {t['point_id']: t for t in turns}
        if len(listed) != len(turns):
            sys.exit(f'part {k}: a repeated point id in turns.json: stop')
        window = {g['game']: g for g in json.load(open(f'{a.exam_v2}/inv_in_p{k}/window.json', encoding='utf-8'))['games']}
        inv = json.load(open(f'{a.exam_v2}/inv_out_p{k}/inventory.json', encoding='utf-8'))
        games = inv if isinstance(inv, list) else inv['games']
        first = {}
        for g in games:
            for t in one(g, ('turns', 'his_turns'), 'an inventory game'):
                pid = one(t, ('point_id', 'id'), 'an inventory turn')
                if pid in first:
                    sys.exit(f'part {k}: {pid} twice in the inventory: stop')
                first[pid] = t
        second = json.load(open(f'{a.exam_v2}/selcode_out_p{k}/coding.json', encoding='utf-8'))
        if second.get('format') != 'pds-exam-v2-selcode':
            sys.exit(f'part {k}: coding.json format {second.get("format")!r}: stop')
        second = second['turns']
        for name, coded in (('first coding', first), ('second coding', second)):
            extra = sorted(set(coded) - set(listed))
            if extra:
                notes.append(f'part {k}: the {name} codes {len(extra)} turn(s) not in turns.json (not points): {extra}')
        c = collections.Counter()
        for pid, t in listed.items():
            row = {'part': k, 'game': t['game'], 'global_turn': t['global_turn'], 'clip': t['clip']}
            calls = {}
            for name, coded, why_key in (('first', first, 'reason'), ('second', second, 'why_not')):
                x = coded.get(pid)
                if x is None:
                    calls[name] = False
                    row[name] = None
                    c[f'{name}_missing'] += 1
                    continue
                fields_yes = all(yes(x.get(f)) for f in FIELDS)
                v = verdict(x.get('usable'))
                if fields_yes != v:
                    c[f'{name}_verdict_differs_from_fields'] += 1
                calls[name] = fields_yes and v
                row[name] = {**{f: x.get(f) for f in FIELDS}, 'usable': x.get('usable'), 'why_not': x.get(why_key)}
            row['first_usable'], row['second_usable'] = calls['first'], calls['second']
            row['candidate'] = calls['first'] and calls['second']
            c[{(True, True): 'both_usable', (True, False): 'first_only', (False, True): 'second_only',
               (False, False): 'neither'}[(calls['first'], calls['second'])]] += 1
            agreement[pid] = row
            if row['candidate']:
                cands.append({'point_id': pid, 'game': t['game'], 'global_turn': t['global_turn'], 'clip': t['clip'], 'part': k,
                              'folder': f"{a.exam_v2}/inv_in_p{k}/sources/{t['game']}", 'deck': window[t['game']]['deck'],
                              'clips_in_game': window[t['game']]['clips']})
        c['turns'] = len(listed)
        table[f'p{k}'] = dict(c)
    total = collections.Counter()
    for v in table.values():
        total.update(v)
    table['all'] = dict(total)
    cands.sort(key=lambda x: (x['game'], x['global_turn']))
    os.makedirs(a.out)
    with open(f'{a.out}/agreement.json', 'w', encoding='utf-8') as f:
        json.dump({'what': 'both codings of every turn, copied (select_v2.py); the rule: PREREG_RUN3 addendum 5, G3', 'turns': agreement},
                  f, indent=1, ensure_ascii=False)
    by_deck = collections.Counter(x['deck'] for x in cands)
    by_game = collections.Counter(x['game'] for x in cands)
    with open(f'{a.out}/selection.json', 'w', encoding='utf-8') as f:
        json.dump({'what': 'exam v2 candidates: every turn both codings call usable (select_v2.py; PREREG_RUN3 addendum 5, G3)',
                   'rule': 'a coding calls a turn usable when its four fields are all "yes" and its own usable verdict is true',
                   'table': table, 'notes': notes, 'candidates': cands}, f, indent=1, ensure_ascii=False)
    keys = ['turns', 'both_usable', 'first_only', 'second_only', 'neither', 'first_missing', 'second_missing',
            'first_verdict_differs_from_fields', 'second_verdict_differs_from_fields']
    md = ['# Exam v2: the usable set (select_v2.py)', '', 'A turn is a candidate ONLY where both codings call it usable (addendum 5, G3).', '',
          '| part | ' + ' | '.join(keys) + ' |', '|---' * (len(keys) + 1) + '|']
    for p, v in table.items():
        md.append(f'| {p} | ' + ' | '.join(str(v.get(x, 0)) for x in keys) + ' |')
    md += ['', f'Candidates: {len(cands)} from {len(by_game)} games.', '',
           'By deck: ' + ', '.join(f'{d} {n}' for d, n in sorted(by_deck.items(), key=lambda z: -z[1])), '']
    md += [f'- {n}' for n in notes]
    with open(f'{a.out}/SELECTION.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    print('\n'.join(md[4:]))


if __name__ == '__main__':
    main()
