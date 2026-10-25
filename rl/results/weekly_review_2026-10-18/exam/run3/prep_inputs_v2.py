#!/usr/bin/env python3
"""Inputs for exam run 3 (PREREG_RUN3), taken from the exam branch and the judge tag only (never from a working copy).

usage: prep_inputs_v2.py REPO FREEZE_COMMIT EXAM_TIP REF OUTDIR
- From the FREEZE commit (K19, 6e5fab0c): run3/frozen_2026-10-25/ (positions_v2.json, references_v2.json, eligibility_v2.json, ids_v2.txt,
  exam_v2_2026-10-25.json), each checked against FREEZE_MANIFEST.json and K19's sha256; the same files at EXAM_TIP must be byte-identical
  (nothing changed after the freeze); run3/decks/<deck>.txt for every deck the positions name.
- From EXAM_TIP: run3/strata/ (the chance-ending strata, fixed before any run 3 row).
Writes OUTDIR/positions.json, references.json, eligibility.json, ids.txt (verbatim), decks/*.txt, categories.json (deck, deck_kinds,
answer_kind, scope, primary; descriptive only), stratum_chance_run3.txt, stratum_chance_pooled.txt and inputs_manifest.json (every hash).
Stops on any mismatch."""
import hashlib, json, os, subprocess, sys

REPO, FREEZE, TIP, REF, OUT = sys.argv[1:6]
RUN3 = 'rl/results/weekly_review_2026-10-18/exam/run3'
FZ = f'{RUN3}/frozen_2026-10-25'
K19 = {'exam_v2_2026-10-25.json': 'f0627a2149f6ab4427d3be2e52f2bce707d5a2b3db16abef070fc632e6e14913',
       'references_v2.json': '650c21a76e5cb79326f1342eab2275890c2ebdd97d4aaa87a957dc4c485bbe4a',
       'eligibility_v2.json': 'b994a19f2c68f7a911660d5f1c9504cec8b0366118d1404150618f3b0b55ac97',
       'positions_v2.json': 'b75c02e129307b7bce70d0c7fed242b8c504bd0ea15c851ea59643110b80edaa',
       'ids_v2.txt': '1eb35725534b608e930ebb8bb91bfb69a2e0b71c727b5cfb6f149fc5bdeb9f78'}
MANIFEST_SHA = 'd54928f944b27a046a523038d6f1da4369cab0d6f8660d1aedf2463239f60e62'
LEAK_KEYS = {'force', 'his_plan', 'his_plan_ended', 'answer', 'answer_kind', 'kind', 'milestones', 'build_notes', '_draws', '_vpatch', 'notes',
             'approximate_reason', 'his_move', 'key_line', 'first_segment', 'acceptable', 'rejected_alternatives', 'pending_alternatives',
             'dustin_answer', 'lister_segments', 'segment_scope'}


def show(commit, path):
    return subprocess.run(['git', '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


os.makedirs(os.path.join(OUT, 'decks'), exist_ok=True)
man = {'freeze_commit': FREEZE, 'exam_tip': TIP, 'judge_ref': REF,
       'judge_ref_commit': subprocess.run(['git', '-C', REPO, 'rev-parse', REF], capture_output=True, text=True, check=True).stdout.strip(), 'files': {}}
mraw = show(FREEZE, f'{FZ}/FREEZE_MANIFEST.json')
if sha(mraw) != MANIFEST_SHA:
    sys.exit(f'FREEZE_MANIFEST.json: sha256 {sha(mraw)[:16]} is not K19\'s: stop')
fman = json.loads(mraw)
raw = {}
for f, want in K19.items():
    b = show(FREEZE, f'{FZ}/{f}')
    if sha(b) != want or fman.get(f) != want:
        sys.exit(f'{f}: sha256 {sha(b)[:16]} is not the frozen one ({want[:16]}): stop')
    if show(TIP, f'{FZ}/{f}') != b:
        sys.exit(f'{f}: changed after the freeze (at {TIP[:12]}): stop')
    raw[f] = b
    man['files'][f'frozen:{f}'] = want
exam = json.loads(raw['exam_v2_2026-10-25.json'])
pos = json.loads(raw['positions_v2.json'])
refs = json.loads(raw['references_v2.json'])
elig = json.loads(raw['eligibility_v2.json'])
ids = [l.strip() for l in raw['ids_v2.txt'].decode().splitlines() if l.strip()]
assert exam['format'] == 'pds-exam-v2', exam['format']
for q in pos:
    bad = LEAK_KEYS & set(q)
    if bad:
        sys.exit(f"{q.get('id')}: the candidate view carries answer-key fields {sorted(bad)}: stop")
pids = [q['id'] for q in pos]
if not (set(pids) == set(ids) == set(elig['primary_ids']) == set(refs) == {p['id'] for p in exam['points']}) or len(ids) != len(set(ids)):
    sys.exit('positions, ids, eligibility, references and the exam do not name the same points: stop')
if any(p['answer']['status'] != 'final' for p in exam['points']):
    sys.exit('a point is not final: stop')
open(os.path.join(OUT, 'positions.json'), 'wb').write(raw['positions_v2.json'])
open(os.path.join(OUT, 'references.json'), 'wb').write(raw['references_v2.json'])
open(os.path.join(OUT, 'eligibility.json'), 'wb').write(raw['eligibility_v2.json'])
open(os.path.join(OUT, 'ids.txt'), 'wb').write(raw['ids_v2.txt'])
for deck in sorted({q['deck'] for q in pos}):
    b = show(FREEZE, f'{RUN3}/decks/{deck}.txt')
    open(os.path.join(OUT, 'decks', f'{deck}.txt'), 'wb').write(b)
    man['files'][f'deck:{deck}'] = sha(b)
cats = {p['id']: {'deck': p['deck'], 'deck_kinds': (exam.get('deck_kinds') or {}).get(p['deck'], []), 'answer_kind': p['answer']['answer_kind'],
                  'scope': p['answer']['segment_scope'], 'primary': True} for p in exam['points']}
open(os.path.join(OUT, 'categories.json'), 'w').write(json.dumps(cats, ensure_ascii=False, indent=1))
for s in ('stratum_chance_run3.txt', 'stratum_chance_pooled.txt'):
    b = show(TIP, f'{RUN3}/strata/{s}')
    open(os.path.join(OUT, s), 'wb').write(b)
    man['files'][f'strata:{s}'] = sha(b)
s3 = [l.strip() for l in open(os.path.join(OUT, 'stratum_chance_run3.txt')) if l.strip()]
if not set(s3) <= set(ids):
    sys.exit('the run 3 stratum names points outside the exam: stop')
for f in ('positions.json', 'references.json', 'eligibility.json', 'ids.txt', 'categories.json'):
    man['files'][f'in:{f}'] = sha(open(os.path.join(OUT, f), 'rb').read())
json.dump(man, open(os.path.join(OUT, 'inputs_manifest.json'), 'w'), indent=1)
print(f"inputs ready: {len(pos)} positions, {len(set(elig['games'].values()))} games, {len(elig['full_scope_ids'])} full-scope, "
      f"{len(s3)} chance-ending; frozen files equal K19 and are unchanged at the tip; decks {len({q['deck'] for q in pos})}")
