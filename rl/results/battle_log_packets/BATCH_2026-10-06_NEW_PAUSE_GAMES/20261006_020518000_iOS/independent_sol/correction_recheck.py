import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
p=Path(__file__).resolve().parent.parent;out=p/'independent_sol'
def read(f):return json.loads(f.read_text(encoding='utf-8'))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
old=read(out/'CHECK_RESULT_REJECTED_R1_R2.json');integrity=read(out/'INPUT_INTEGRITY.json')
backup={f:sha(p/'original_before_R1_R2'/f)==h for f,h in old['checked_input_sha256'].items()}
assert all(backup.values())
current={f:sha(p/f) for f in old['checked_input_sha256']}
changed=[f for f,h in current.items() if h!=old['checked_input_sha256'][f]]
assert set(changed)<= {'TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json'}
l=read(p/'TURN_LEDGER.json');e=read(p/'TURN_EVIDENCE.json');fm={f['evidence_id']:f for f in e['frames']}
for t in l['turns']:
    for action in t['plays_in_order']:
        assert 'Reference timestamp alone does not establish first input' in action['input_and_resolution_distinction']
        assert 'not an exact consuming input' in action['timestamp_role']
assert l['turns'][1]['plays_in_order'][0]['public_transition_interval_seconds']==[72,75]
assert l['turns'][11]['plays_in_order'][0]['public_transition_interval_seconds']==[376,378]
m=l['turns'][11]['plays_in_order'][1]
assert m['public_transition_interval_seconds']==[378,380]
assert m['public_presentation_observed_seconds']==380 and m['resolved_state_observed_seconds']==408.5
assert m['exact_consuming_input_seconds'] is None
for n,window,resolved in [(13,[435.5,440],440),(17,[570,571.5],573)]:
    t=l['turns'][n-1];a=t['plays_in_order'][0]
    assert t['timing']['first_voluntary_move_seconds'] is None
    assert t['timing']['first_voluntary_move_window_seconds']==window
    assert a['public_transition_interval_seconds']==window and a['resolved_state_observed_seconds']==resolved
    assert a['exact_consuming_input_seconds'] is None
for fid in ['f0095_50','f0097_50','f0199_50','f0488_50','f0491_50','f0576_50']:assert fm[fid]['unzoomed'] is True and fm[fid]['before_first_play'] is False
assert fm['f0161_50']['unzoomed'] is False and 'overlay' in l['turns'][4]['owner_hand_end']['basis']
assert 'discard is not yet established' in fm['f0100_50']['observation']
assert fm['f0435_50']['before_first_play'] is None and 'remains available' in fm['f0435_50']['observation']
assert 'not yet attached' in fm['f0438_50']['observation']
assert 'second Research draw' in fm['f0491_50']['observation']
unchanged_images=all(sha(p/f)==h for f,h in integrity['image_sha256'].items())
assert unchanged_images
qr=read(p/'qr_intake/QR_DECODE_0002.00.json');d=read(p/'DECK_USED.json')
assert d['filmed_qr']['payload_ascii_sha256']==qr['payload_ascii_sha256']
entries=read(p.parent/'NEW_DECK_ENTRIES.json')['decks']
entry=next(x for x in entries if x['id']=='filmed-qr-913d34a7e9b5')
assert entry['deck_code']==qr['payload'] and entry['source_sha256']==old['source_sha256']
assert sorted((x['entity_kind'],x['entity_id'],x['count']) for x in entry['cards_in_display_order'])==sorted((x['entity_kind'],x['entity_id'],x['count']) for x in d['filmed_qr']['counts_by_semantic_entity'])
supp={f:sha(Path(f) if Path(f).is_absolute() else p/f) for f in old['supplemental_checked_input_sha256']}
extra=read(out/'SUPPLEMENTAL_VIEWED_EVIDENCE.json')
supp.update({f:sha(p/f) for f in extra['supplemental_checked_input_sha256']})
supp['turn_evidence/t0440.00.jpg']=sha(p/'turn_evidence/t0440.00.jpg')
receipt=dict(old)
receipt.update({'checked_at_utc':datetime.now(timezone.utc).isoformat(),'result':'accepted','accepted':True,'checked_input_sha256':current,'supplemental_checked_input_sha256':supp,'remaining_repairs':[], 'correction_recheck':{
 'scope':'Only amended fields, retained native comparison and current hashes; no full review, builders, source-media reopening or extraction.',
 'frozen_backups_match_rejected_receipt':backup,
 'changed_canonical_files':changed,
 'all_876_retained_image_hashes_unchanged':unchanged_images,
 'R1':'Resolved: reference anchors no longer claim exact consuming inputs; Metal/May/owner attachments have supported bounds. May presentation380 and completed draw/return state408.5 are distinct.',
 'R2':'Resolved: zoom flags, coin/heal/selection descriptions and overlaid before-end hand basis agree with inspected native frames.',
 'newly_rechecked_native_full_frames':['turn_evidence/t0440.00.jpg','turn_evidence/t0380.00.jpg','turn_evidence/t0491.50.jpg'],
 'native_support':'440 shows Conkeldurr three Fighting plus one Colorless;380 May card presentation;491.5 Timburr second Research draw in changed five-card hand. Other repaired pixels were inspected in initial bounded audit and are unchanged.',
 'initial_rejection_preserved':'CHECK_RESULT_REJECTED_R1_R2.json',
 'structure_alone_used_for_acceptance':False}})
for name in ['CORRECTION_RECHECK.json','CHECK_RESULT.json']:(out/name).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'remaining_repairs':[],'changed_files':changed,'backup_matches':len(backup),'retained_images_unchanged':len(integrity['image_sha256']),'current_nine_hashes':current},indent=2))
