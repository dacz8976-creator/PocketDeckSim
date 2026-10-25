#!/usr/bin/env python3
"""Exam v2's freeze (PREREG_RUN3 section 10 and addendum 5, G2 step 8): from the final assembly, write the frozen exam, its references, its
eligibility file and the candidate view, with each point's scope by v1.6's rule. Mechanical; no bot, no judge.

  freeze_v2.py EXAM_V2_DIR ASSEMBLY_DIR OUT_DIR

- The scope (v1.6's README, v1.4's scope rule, unchanged): a line's scope is "full" when its scored first segment holds all of the line's
  strategic actions, "none" when it holds none, else "partial". Strategic actions are every action except chance actions (v2_helpers.DRAW and
  every chance step chance_steps() finds: a chance Stadium's use, a chance Ability), EndTurn and UseStadium, as v1.6's strategic() was. A
  point is "full" only if EVERY accepted line (the key and each acceptable line) is full; "none" if the key line is none; else "partial".
  A line's scored segment is its lister segment where the assembly recorded one (R1), else cut().
- Eligibility (frozen-7's ai_judge_eligibility_v1): primary_ids = every final point (no developer exposure is recorded, so none is
  excluded); full_scope_ids = the primary points whose scope is "full"; games; excluded_reasons (empty).
- references.json must equal, point for point, the key line plus the acceptable lines of the frozen exam.
"""
import collections, datetime, hashlib, json, os, sys

E2, ASM, OUT = sys.argv[1:4]
sys.path.insert(0, os.path.join(E2, 'build'))
import v2_helpers as H  # noqa: E402

d = json.load(open(f'{ASM}/exam_v2_draft.json', encoding='utf-8'))
refs = json.load(open(f'{ASM}/references.json', encoding='utf-8'))
if d.get('format') != 'pds-exam-v2-draft':
    sys.exit(f"{d.get('format')}: not an exam v2 draft: stop")


def strategic_idx(line, pos):
    chance = set(H.chance_steps(line, pos))
    return [i for i, l in enumerate(line)
            if i not in chance and not l.startswith(H.DRAW) and l.split('#')[0] not in ('EndTurn', 'UseStadium')]


def line_scope(line, seg, pos):
    s = strategic_idx(line, pos)
    if list(line[:len(seg)]) != list(seg):
        raise SystemExit(f'segment {seg} is not a prefix of {line}: stop')
    inside = [i for i in s if i < len(seg)]
    return 'full' if len(inside) == len(s) else ('none' if not inside else 'partial')


points, scope_count, problems = [], collections.Counter(), []
for p in d['points']:
    a, pos = p['answer'], p['position']
    if a['status'] != 'final':
        problems.append(f"{p['id']}: status {a['status']}")
        continue
    ls = a.get('lister_segments') or {}
    key_tag = 'key' if a.get('key_line') else 'his'
    key = a['key_line'] if a.get('key_line') else a['his_move']
    by_line = {key_tag: line_scope(key, a['first_segment'], pos)}
    for i, x in enumerate(a['acceptable']):
        seg = ls.get(f'alt{i}') or H.cut(x['line'], pos)
        by_line[f'alt{i}'] = line_scope(x['line'], seg, pos)
    sc = 'full' if all(v == 'full' for v in by_line.values()) else ('none' if by_line[key_tag] == 'none' else 'partial')
    a['segment_scope'] = sc
    a['segment_scope_by_line'] = by_line
    scope_count[sc] += 1
    want = [{'id': key_tag, 'labels': key}] + [{'id': f'alt{i}', 'labels': x['line']} for i, x in enumerate(a['acceptable'])]
    if refs.get(p['id']) != want:
        problems.append(f"{p['id']}: references.json differs from the exam's key and acceptable lines")
    points.append(p)
if problems or set(refs) != {p['id'] for p in points}:
    sys.exit(f'stop: {problems[:10]} | references ids equal: {set(refs) == {p["id"] for p in points}}')
primary = [p['id'] for p in points]
full = [p['id'] for p in points if p['answer']['segment_scope'] == 'full']
games = {p['id']: p['game'] for p in points}
exam = {'format': 'pds-exam-v2', 'frozen': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'what': "exam v2 (run 3), FROZEN before any bot or judge output for it: the final assembly (labels, note 044's fixes, Part B's printing "
                "notes, Dustin's answers by K11's mapping, frozen-7's lister check, validate_v2), with each point's scope by v1.6's rule",
        'scoring': "As v1.6 (README 'Scoring'), with PREREG_RUN3 addendum 5's R1: a line's scored first segment ends where frozen-7's plan lister "
                   "ends the plan it reaches (its first chance event, or its first step after which the opponent must act), else the whole turn "
                   "(answer.first_segment for the key; answer.lister_segments where recorded). Two metrics, reported separately: prefix agreement "
                   "on the primary points; full-plan agreement on the primary points whose answer.segment_scope is 'full'. The key is "
                   "answer.key_line where present, else his recorded move; rejected alternatives never count; references.json holds the key "
                   "('key' or 'his') and every acceptable line ('alt<i>').",
        'primary_eligible': primary, 'primary_excluded': {}, 'full_scope_ids': full,
        'scope_counts': dict(scope_count), 'full_scope_caveat': d.get('full_scope_caveat'), 'deck_kinds': d.get('deck_kinds'),
        'g1_drops_build': d.get('g1_drops_build'), 'g1_drops_lister': d.get('g1_drops_lister'), 'record': d.get('record'), 'points': points}
elig = {'schema': 'ai_judge_eligibility_v1', 'primary_ids': primary, 'full_scope_ids': full, 'games': games, 'excluded_reasons': {}}
os.makedirs(OUT, exist_ok=False)
json.dump(exam, open(f'{OUT}/exam_v2_2026-10-25.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
open(f'{OUT}/references_v2.json', 'wb').write(open(f'{ASM}/references.json', 'rb').read())
open(f'{OUT}/positions_v2.json', 'wb').write(open(f'{ASM}/positions.json', 'rb').read())
json.dump(elig, open(f'{OUT}/eligibility_v2.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
open(f'{OUT}/ids_v2.txt', 'w').write('\n'.join(primary) + '\n')
sha = lambda f: hashlib.sha256(open(f, 'rb').read()).hexdigest()
man = {f: sha(f'{OUT}/{f}') for f in sorted(os.listdir(OUT))}
json.dump(man, open(f'{OUT}/FREEZE_MANIFEST.json', 'w'), indent=1)
print(f'frozen: {len(points)} points, {len(set(games.values()))} games; scope {dict(scope_count)}; full-scope {len(full)}')
for f, h in man.items():
    print(f'  {h}  {f}')
