#!/usr/bin/env python3
"""Inputs for the exam's first scored run, taken from the exam commit and the judge tag only (never from a working copy).

usage: prep_inputs.py REPO EXAM_COMMIT REF OUTDIR
Writes OUTDIR/positions.json (the candidate view: each point's `position`, nothing else), OUTDIR/decks/*.txt (the three lists the positions name),
OUTDIR/references.json (verbatim from the exam commit), OUTDIR/eligibility.json (the harness's ai_judge_eligibility_v1, converted from
references_meta.json), OUTDIR/ids.txt (49 primary ids, then the 2 diagnostic ones) and OUTDIR/inputs_manifest.json (every hash).
Stops on any mismatch: the references' and meta's sha256 must be the ones Astra checked (12e0e997..., 6adca41e...)."""
import hashlib, json, os, subprocess, sys

REPO, EXAM, REF, OUT = sys.argv[1:5]
EXAM_DIR = 'rl/results/weekly_review_2026-10-18/exam'
ASTRA = {'references.json': '12e0e997', 'references_meta.json': '6adca41e'}
DECKS = {  # deck key in the positions -> path in the judge tag's tree (the exam build used these same lists)
    '12-ariados-whimsicott-ogerpon': 'decks/dustin/12-ariados-whimsicott-ogerpon.txt',
    '13-a-ninetales-raticate': 'decks/dustin/13-a-ninetales-raticate.txt',
    'kingambit_list_A': 'rl/results/pause_games_new_2026-10-13/v2/decks/KW261013_010837000.txt',
}
LEAK_KEYS = {'force', 'his_plan', 'his_plan_ended', 'answer', 'answer_kind', 'kind', 'milestones', 'build_notes'}


def show(commit, path):
    return subprocess.run(['git', '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout


def sha(b):
    return hashlib.sha256(b).hexdigest()


os.makedirs(os.path.join(OUT, 'decks'), exist_ok=True)
man = {'exam_commit': EXAM, 'judge_ref': REF, 'judge_ref_commit': subprocess.run(['git', '-C', REPO, 'rev-parse', REF], capture_output=True, text=True, check=True).stdout.strip(),
       'files': {}}
raw = {f: show(EXAM, f'{EXAM_DIR}/{f}') for f in ('exam_2026-10-19.json', 'references.json', 'references_meta.json')}
for f, b in raw.items():
    man['files'][f'exam:{f}'] = sha(b)
for f, pre in ASTRA.items():
    if not sha(raw[f]).startswith(pre):
        sys.exit(f'{f}: sha256 {sha(raw[f])[:16]} is not the one Astra checked ({pre}...): stop')
exam = json.loads(raw['exam_2026-10-19.json'])
meta = json.loads(raw['references_meta.json'])
refs = json.loads(raw['references.json'])
assert exam['format'] == 'pds-exam-v1.6', exam['format']
points = exam['points']
# the candidate view: the position only
pos = []
for p in points:
    q = dict(p['position'])
    q['id'] = p['id']
    bad = LEAK_KEYS & set(q)
    if bad:
        sys.exit(f"{p['id']}: the candidate view carries answer-key fields {sorted(bad)}: stop")
    pos.append(q)
open(os.path.join(OUT, 'positions.json'), 'w').write(json.dumps(pos, ensure_ascii=False))
open(os.path.join(OUT, 'references.json'), 'wb').write(raw['references.json'])
for key, path in DECKS.items():
    b = show(REF, path)
    open(os.path.join(OUT, 'decks', f'{key}.txt'), 'wb').write(b)
    man['files'][f'deck:{key}'] = sha(b)
used = {p['position']['deck'] for p in points}
assert used == set(DECKS), (used, set(DECKS))
# eligibility in the harness's format
primary = list(meta['primary_eligible'])
excluded = sorted(meta['primary_excluded'])
full = list(meta['primary_full_scope'])
assert len(primary) == 49 and len(excluded) == 2 and len(full) == 19, (len(primary), len(excluded), len(full))
assert set(full) <= set(primary) and not (set(primary) & set(excluded))
assert set(primary) | set(excluded) == {p['id'] for p in points} == set(refs)
reason = exam['primary_exclusion_reasons'][exam['primary_excluded_games'][0]]
elig = {'schema': 'ai_judge_eligibility_v1', 'primary_ids': primary, 'full_scope_ids': full,
        'games': {p['id']: p['game'] for p in points}, 'excluded_reasons': {pid: reason for pid in excluded}}
open(os.path.join(OUT, 'eligibility.json'), 'w').write(json.dumps(elig, ensure_ascii=False, indent=1))
open(os.path.join(OUT, 'ids.txt'), 'w').write('\n'.join(primary + excluded) + '\n')
# categories for the descriptive breakdown (not an input of the formal comparison)
cats = {p['id']: {'deck': p['deck'], 'deck_kinds': p['deck_kinds'], 'answer_kind': p['answer_kind'], 'scope': p['answer']['segment_scope'],
                  'primary': p['id'] in primary} for p in points}
open(os.path.join(OUT, 'categories.json'), 'w').write(json.dumps(cats, ensure_ascii=False, indent=1))
for f in ('positions.json', 'references.json', 'eligibility.json', 'ids.txt', 'categories.json'):
    man['files'][f'in:{f}'] = sha(open(os.path.join(OUT, f), 'rb').read())
json.dump(man, open(os.path.join(OUT, 'inputs_manifest.json'), 'w'), indent=1)
print(f"inputs ready: {len(pos)} positions ({len(primary)} primary, {len(excluded)} diagnostic), {len(full)} full-scope; references {sha(raw['references.json'])[:16]}, "
      f"meta {sha(raw['references_meta.json'])[:16]}, exam {sha(raw['exam_2026-10-19.json'])[:16]}")
