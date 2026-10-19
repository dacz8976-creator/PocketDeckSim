"""v1.6 (live laptop, Oct 19, before any bot run): exposure treatment, references file for the formal comparison, record fixes. No bot output used."""
import json, os, shutil, collections, re
C = '/home/dacz8976/exam/commit'
F = f'{C}/exam_2026-10-19.json'
SNAP = f'{C}/exam_2026-10-19.v151_100c52b6.json'
if not os.path.exists(SNAP):
    shutil.copy(F, SNAP)
d = json.load(open(SNAP))
assert d['format'] == 'pds-exam-v1.5.1', d['format']
EXCL_GAME = '20261015_210617000_iOS'
# (1) exposure treatment
d['primary_excluded_games'] = [EXCL_GAME]
d['primary_exclusion_reasons'] = {EXCL_GAME: (
    "2026-10-19: developer exposure. Sonnet (the judge harness's developer) read one answer-key example from this game in a review message "
    "not addressed to it. Decided by the coordinator on Astra's recommendation. This game's points keep their labels and stay in the file, "
    "but are reported separately as diagnostic/sensitivity only, never in the primary result.")}
excl_ids = [p['id'] for p in d['points'] if p['game'] == EXCL_GAME]
prim = [p for p in d['points'] if p['game'] != EXCL_GAME]
for p in d['points']:
    p['primary_eligible'] = p['game'] != EXCL_GAME
d['denominator_history'] = [
    {'version': 'v1.1-v1.3', 'points': 51, 'scored': 46, 'note': '5 points held pending Dustin'},
    {'version': 'v1.4', 'points': 51, 'scored': 46, 'full_scope_scored': 17, 'note': 'scope set by the shortest accepted segment'},
    {'version': 'v1.5/v1.5.1', 'points': 51, 'scored': 51, 'full_scope': 19, 'note': "Dustin's 5 answers applied"},
    {'version': 'v1.6', 'points': 51, 'primary_eligible': len(prim), 'excluded': excl_ids,
     'primary_full_scope': sum(1 for p in prim if p['answer']['segment_scope'] == 'full'),
     'note': f'game {EXCL_GAME} excluded from the primary result (developer exposure, Oct 19)'},
]
# (4) basis of each rejection
for p in d['points']:
    for r in p['answer'].get('rejected_alternatives', []):
        txt = r['rejected_because']
        if p['id'] == 'LAD-20261016_031512000_iOS-t2' and any(l.startswith('Place:Pawniard') for l in r['line']):
            r['certified_by'] = 'coordinator_interpretation'
            r['basis_note'] = ("The coordinator's stricter reading of his plan: Dustin called benching Pawniard 'an option' while describing his preference "
                               "to hold it until a Pokémon is knocked out. Not a human-certified mistake.")
        elif txt.startswith("Dustin: 'Not attacking") or "would have been the better move" in txt:
            r['certified_by'] = 'dustin'
        else:
            r['certified_by'] = 'coordinator_decision_from_his_words'
# (3) Quick-Grow wording in the operative text
d['scoring'] = d['scoring'].replace("a draw, search, coin or random pick, incl. UseStadium on Mesagoza",
    "a draw, search or coin, Quick-Grow Extract's evolution (the player picks a visible target; the evolution card is random) and UseStadium on Mesagoza")
d['format'] = 'pds-exam-v1.6'
json.dump(d, open(F, 'w'), indent=1, ensure_ascii=False)

# (2) references for the formal comparison (Sonnet's generic format) + meta
refs, meta_scope = {}, {}
for p in d['points']:
    a = p['answer']
    key = a.get('key_line')
    lst = [{'id': 'key', 'labels': key}] if key else [{'id': 'recorded', 'labels': a['his_move']}]
    if key:
        assert a['recorded_move_acceptable'] is False
    lst += [{'id': f'alt{i}', 'labels': x['line']} for i, x in enumerate(a['acceptable'])]
    rejected = [r['line'] for r in a.get('rejected_alternatives', [])]
    assert not any(x['labels'] in rejected for x in lst), p['id']
    refs[p['id']] = lst
    meta_scope[p['id']] = a['segment_scope']
json.dump(refs, open(f'{C}/references.json', 'w'), indent=1, ensure_ascii=False)
meta = {
    'format': 'pds-exam-references-v1',
    'exam': 'exam_2026-10-19.json (pds-exam-v1.6)',
    'contract': [
        "references.json is {position id: [{id, labels}]}, Sonnet's generic format (rl/ai_judge formal.py map_references).",
        "Each list is a whole accepted turn in canonical Name#JSON labels; the judge's replay follows it to its first chance step or its attack, so the compared unit is that first segment.",
        "The key is answer.key_line where present ('key'), otherwise his recorded move ('recorded'); a recorded move with recorded_move_acceptable false is never a key.",
        "Accepted alternatives are included ('alt<i>'); rejected alternatives are excluded; the 69 validation records are not answers and are not imported.",
        "Two metrics, reported separately: prefix agreement on the eligible points, and full-plan agreement on the eligible points whose scope is 'full'.",
        "Primary result: primary_eligible only. The excluded game is reported separately (diagnostic/sensitivity).",
    ],
    'primary_eligible': [p['id'] for p in prim],
    'primary_excluded': {pid: EXCL_GAME for pid in excl_ids},
    'scope': meta_scope,
    'primary_full_scope': [p['id'] for p in prim if p['answer']['segment_scope'] == 'full'],
    'game_of': {p['id']: p['game'] for p in d['points']},
    'counts': {
        'points': len(d['points']), 'primary_eligible': len(prim), 'excluded': len(excl_ids),
        'primary_scope': dict(collections.Counter(p['answer']['segment_scope'] for p in prim)),
        'primary_by_deck': dict(collections.Counter(p['deck'] for p in prim)),
        'primary_by_kind': dict(collections.Counter(p['answer_kind'] for p in prim)),
        'primary_games': len({p['game'] for p in prim}),
        'reference_lines': sum(len(v) for v in refs.values()),
    },
}
json.dump(meta, open(f'{C}/references_meta.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(meta['counts'], indent=1))
print('excluded ids', excl_ids)
print('rejection basis', collections.Counter(r['certified_by'] for p in d['points'] for r in p['answer'].get('rejected_alternatives', [])))
# v15 completeness check: every 'validated' post-chance variant matched ALL its remaining actions?
V = [json.loads(l) for l in open(f'{C}/build/vlines_v15.jsonl')]
inc = []
for r in V:
    m = re.match(r'(validated|partly)[^(]*\((\d+)/(\d+)', r['after_chance']) or re.search(r'after (\d+)/(\d+)', r['after_chance'])
    if m:
        a, b = (int(m.group(2)), int(m.group(3))) if m.lastindex == 3 else (int(m.group(1)), int(m.group(2)))
        if a != b:
            inc.append((r['pid'], r['tag'], r['after_chance']))
print('post-chance lines with fewer matched than remaining actions:', inc)
