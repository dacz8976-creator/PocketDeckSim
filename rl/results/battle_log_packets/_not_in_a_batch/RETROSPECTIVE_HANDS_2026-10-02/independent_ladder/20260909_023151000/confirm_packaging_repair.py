import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

B = Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\RETROSPECTIVE_HANDS_2026-10-02')
P = B / '20260909_023151000'
C = B / 'independent_ladder' / '20260909_023151000'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, data):
    (C/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

manifest = read(P/'SUBMISSION_AFTER_PACKAGING_REPAIR.json')
original = read(Path(manifest['original_submission']))
initial = C/'CHECK_RESULT.json'
initial_sha = sha(initial)
old_hashes = {Path(r['path']).name:r['sha256'] for r in original['submitted_files']}
rows = []
changed = []
for r in manifest['submitted_files']:
    path = Path(r['path'])
    actual = sha(path)
    rows.append({'path':str(path), 'expected_sha256':r['sha256'], 'actual_sha256':actual, 'matched':actual==r['sha256']})
    if old_hashes[path.name] != r['sha256']:
        changed.append(path.name)
assert len(rows)==26 and all(r['matched'] for r in rows)
assert set(changed)=={'HAND_SUPPLEMENT.json','SOURCE_REFERENCE.json'}

hand = read(P/'HAND_SUPPLEMENT.json')
source = read(P/'SOURCE_REFERENCE.json')
old_hand = read(P/'before_packaging_repair'/'HAND_SUPPLEMENT.json')
old_source = read(P/'before_packaging_repair'/'SOURCE_REFERENCE.json')
assert hand['target_rows']==hand['owner_turns']
assert hand['target_turn_numbers']==[1,3,5,7,9]
assert hand['capture_status']=='complete_with_recording_limits'
assert source['sha256']==source['source_sha256']==manifest['source_sha256']
source_without_alias = dict(source)
del source_without_alias['sha256']
assert source_without_alias==old_source
for i in (0,1,2,4):
    assert hand['owner_turns'][i]==old_hand['owner_turns'][i]
t7 = hand['owner_turns'][3]
assert t7['before_end_hand']['count']==1
assert t7['before_end_hand']['cards_left_to_right']==['Helioptile']
assert t7['before_end_hand']['evidence_ids']==['t0240.00']
assert 't0241.50' in t7['before_end_evidence_ids']
assert 't0241.50' in t7['before_end_candidate_limits']
for key, value in old_hand.items():
    if key!='owner_turns':
        assert hand[key]==value
for key, value in old_hand['owner_turns'][3].items():
    if key not in ('before_end_hand','before_end_evidence_ids'):
        assert t7[key]==value
for key in ('cards_left_to_right','count','status'):
    assert t7['before_end_hand'][key]==old_hand['owner_turns'][3]['before_end_hand'][key]

utc = datetime.now(timezone.utc).isoformat()
save('HASH_VALIDATION_AFTER_PACKAGING_REPAIR.json', {
    'completed_utc':utc, 'manifest':str(P/'SUBMISSION_AFTER_PACKAGING_REPAIR.json'),
    'manifest_sha256':sha(P/'SUBMISSION_AFTER_PACKAGING_REPAIR.json'),
    'effective_submitted_file_count':len(rows), 'all_effective_hashes_match':True,
    'changed_relative_to_original_freeze':changed, 'files':rows,
    'original_check_sha256':initial_sha, 'source_movie_read_or_hashed':False})
result = {
    'source':manifest['source'], 'source_sha256':manifest['source_sha256'],
    'checker':'Sol, different producer', 'completed_utc':utc,
    'status':'accepted_with_recording_limits', 'consequential_items':[], 'required_repairs':[],
    'effective_submission':str(P/'SUBMISSION_AFTER_PACKAGING_REPAIR.json'),
    'initial_check_preserved':str(initial), 'initial_check_sha256':initial_sha,
    'substantive_check':'Initial complete independent source-field check carries forward; only two packaging/phase files changed.',
    'hash_validation':{'submitted_files':26, 'all_effective_hashes_match':True, 'changed_files':changed},
    'resolved_repairs':[
        {'field':'HAND_SUPPLEMENT.target_rows/target_turn_numbers/capture_status', 'result':'Aliases present, target_rows deep-equals the five owner_turns, turns [1,3,5,7,9], complete_with_recording_limits.'},
        {'field':'SOURCE_REFERENCE.sha256', 'result':'Alias equals source_sha256 and frozen source SHA; other source fields unchanged.'},
        {'field':'HAND_SUPPLEMENT.owner_turns[3].before_end_hand', 'result':'Existing full native t0240.00 independently re-viewed: unzoomed single Helioptile before attack with Energy attachment resolving. Existing t0241.50 independently re-viewed: attack-selection overlay partly covers card; retained as qualified secondary.', 'primary_evidence_id':'t0240.00', 'secondary_evidence_id':'t0241.50', 'card_count':1, 'cards_left_to_right':['Helioptile']}
    ],
    'checks':['Other four owner rows unchanged.', 'T7 card identity/count/status unchanged; phase support clarified.', 'SOURCE_REFERENCE changed only by sha256 alias.', 'All other 24 effective submitted hashes identical to original freeze.', 'Initial source work, all nine turns, five hands, named draws/search limits, both boards/Zones, mode limits and inherited result remain accepted.'],
    'limits':['Requested/nominal seek times remain distinct from unmeasured actual PTS.', 'T2 concealed Ball result remains null; subsequent Entei bench does not establish search identity.', 'Sampled absence of Auto controls does not certify every instant. Any visible Auto option, including OFF, triggers owner computer-battle rule.', 'Hidden opponent identities, unopened discard contents and exact historical twenty-card deck remain qualified recording limits.'],
    'new_native_frames':0, 'source_movie_read_or_hashed':False, 'locator_decode_or_full_scan_repeated':False,
    'producer_files_modified_by_checker':False, 'outcome_changed':False
}
save('CHECK_RESULT_AFTER_PACKAGING_REPAIR.json', result)
(C/'CHECK_RESULT_AFTER_PACKAGING_REPAIR.md').write_text('''# Independent Sol confirmation after packaging repair

Accepted with recording limits. All 26 effective hashes in `SUBMISSION_AFTER_PACKAGING_REPAIR.json` match. Exactly two files changed from the original freeze: HAND_SUPPLEMENT.json and SOURCE_REFERENCE.json. The initial independent check and its substantive acceptance are preserved.

The five owner-hand aliases are complete and agree with owner_turns. The source SHA alias matches the frozen source identity. Turn 7 now uses the clean native view at requested 240 seconds as primary evidence for one Helioptile; the 241.5-second attack-selection overlay remains a secondary view with its occlusion stated. Both existing native frames were independently re-viewed. Card counts, identities, actions, boards and the inherited result did not change.

No required repairs or consequential issues remain. Requested times remain separate from unmeasured actual PTS. The concealed turn 2 Ball result, hidden cards, unopened discard contents, exact historical deck and sampled mode-control limits remain qualified. No movie read/hash, new capture, repeated locator decode, producer edit or shared registration was performed by this checker.
''', encoding='utf-8')
assert sha(initial)==initial_sha
print(json.dumps({'status':result['status'], 'all_26_effective_hashes_match':True, 'changed':changed, 'initial_check_preserved':True, 'result':str(C/'CHECK_RESULT_AFTER_PACKAGING_REPAIR.json')}))
