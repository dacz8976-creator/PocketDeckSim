"""One-shot guarded, bounded R1-R3 repair; never rerun over repaired files."""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

P = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
    return json.loads((P / name).read_text(encoding='utf-8-sig'))
def write(name, obj):
    (P / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

submission = read('SUBMISSION.json')
submission_sha = sha(P/'SUBMISSION.json')
assert submission_sha == 'bc4c16968e68b5df9e5c3bf04ff1b125dc00645b8a5fb2e189bdf3746c1d78fe'
assert not (P/'worker_submission').exists()
for name, expected in submission['files'].items():
    assert sha(P/name) == expected, name
frozen = ['SUBMISSION.json', 'independent_sol/CHECK_RESULT.json',
          'independent_sol/CHECK_RESULT.md', 'independent_sol/EXTRACTION_MANIFEST.json']
frozen_before = {name:sha(P/name) for name in frozen}
manifest = read('EXTRACTION_MANIFEST.json')
independent_manifest = read('independent_sol/EXTRACTION_MANIFEST.json')
assert len(independent_manifest) == 3
for frame in manifest + independent_manifest:
    assert sha(Path(frame['full_frame_path'])) == frame['full_frame_sha256']
    for crop in ('bottom_crop','top_crop'):
        assert sha(Path(frame[crop]['path'])) == frame[crop]['sha256']
        assert frame[crop]['parent_sha256'] == frame['full_frame_sha256']

# Assemble all changes before preserving or writing canonical outputs.
ledger = read('TURN_LEDGER.json')
evidence = read('TURN_EVIDENCE.json')
by_turn = {t['turn_number']:t for t in ledger['turns']}
old_effect = 'Binding Snow: cannot attach Energy from Energy Zone to Active during next opponent turn'
removed_paths = []
for turn in ledger['turns']:
    for phase in ('board_at_start','board_after'):
        side = turn[phase]['opponent']
        for location, card in [('active',side['active'])]+[(f'bench_in_position_order/{i}', c) for i,c in enumerate(side['bench_in_position_order'])]:
            if card and old_effect in card.get('active_effects',[]):
                card['active_effects'].remove(old_effect)
                removed_paths.append(f"turns/{turn['turn_number']}/{phase}/opponent/{location}/active_effects")
assert len(removed_paths) == 12, removed_paths

effect_text = "During your opponent's next turn, they can't take any Energy from their Energy Zone to attach to their Active Pokémon."
added_paths = []
for source_turn in (6,8,10,12,14,16):
    for turn_number,phase in [(source_turn,'board_after')]+([] if source_turn==16 else [(source_turn+1,'board_at_start')]):
        side = by_turn[turn_number][phase]['opponent']
        assert side['board_effects'] == []
        evidence_ids = by_turn[source_turn]['board_after']['evidence_ids'] + ['F0178.00']
        if source_turn == 14:
            evidence_ids += ['F0222.50','F0231.50','F0243.50']
        side['board_effects'].append({
            'effect':'Binding Snow', 'affected_player':'opponent',
            'scope':'player_restriction', 'restricted_source':'opponent Energy Zone',
            'restricted_destination':'whichever opponent Pokemon occupies the Active position during the affected turn',
            'restriction':'Cannot take Energy from the Energy Zone to attach to the Active Pokemon',
            'source_turn':source_turn, 'affected_turn':source_turn+1,
            'expires_at':{'turn_number':source_turn+1,'boundary':'end of next opponent turn'},
            'remaining_duration':'through the next opponent turn' if phase=='board_after' else 'through the current opponent turn',
            'source_card_text':effect_text,
            'evidence_ids':list(dict.fromkeys(evidence_ids)),
            'basis':'Native printed text at F0178.00 establishes opponent-player restriction and next-turn duration; source-turn attack establishes application. T15 post-retreat icon remains at F0222.50 and is absent after resolution at F0231.50 and before T16 attack at F0243.50.',
            'limit_reason':'Terminal T16 icon is visible at F0254.50; no subsequent opponent turn occurs in this recording, so its future expiry is the printed duration, not an observed event.' if source_turn==16 else None
        })
        added_paths.append(f'turns/{turn_number}/{phase}/opponent/board_effects')

# R2: Correct both capture suitability and the misleading action timestamp/anchor.
t6 = by_turn[6]
assert t6['timing']['first_voluntary_move_seconds'] == 96
t6['timing']['first_voluntary_move_seconds'] = 97.0
t6['timing']['first_voluntary_move_onset_bracket_seconds'] = {'after':96.505,'by':97.005,'basis':'Vulpix remains in hand at first frame and is moving into Bench 1 in second; input onset is not directly recorded.'}
play = t6['plays_in_order'][0]
assert play['card_name']=='Alolan Vulpix' and play['timestamp_seconds']==96 and play['evidence_ids']==['F0096.00']
play.update(timestamp_seconds=97.0, evidence_ids=['independent_sol:F0096.50','independent_sol:F0097.00','F0098.00'],
            basis='Independent native 96.505 s shows all four cards still in hand and Bench 1 empty; 97.005 s shows Vulpix moving into Bench 1; existing 98 s anchor shows subsequent attachment.',
            limit_reason='Visible action begins after 96.505 s and by 97.005 s; 97.0 is an approximate event time, not an exact measured input onset.')
t6['turn_evidence_ids'] += ['independent_sol:F0096.50','independent_sol:F0097.00']
frames = {f['evidence_id']:f for f in evidence['frames']}
assert frames['F0096.00']['before_first_play'] is False
frames['F0096.00'].update(before_first_play=True, unzoomed=True, hand_spread=True,
    observation='Cyrus, Copycat, Misty and Alolan Vulpix remain in hand; owner Bench 1 is empty.',
    suitability_or_limit='Usable scheduled draw-end +1 s preplay hand. The Energy-generation overlay does not obscure the four card names. Earlier F0095.30 remains the selected hand.')
frames['F0095.30']['suitability_or_limit'] = 'Selected extra early preplay hand at draw-end +0.30 s; scheduled +1 s F0096.00 is also usable and preplay.'
assert 'Auto plays before +1 on T6' in evidence['scheduled_capture_limits'][0]
evidence['scheduled_capture_limits'][0] = 'All eight owner turns have +1/+3/+6 candidates and before-attack views. T6 retains an additional selected +0.30 s hand; its scheduled +1 s frame is also preplay. Vulpix remains in hand at measured 96.505 s and is moving to the Bench at 97.005 s. Later candidates may be postplay.'

# R3: Keep Item-use time approximate; bind the named reveal to its actual frame.
t10 = by_turn[10]
search = t10['draws_and_searches'][1]
assert search['kind']=='search' and search['cards_in_reveal_order'][0]['name']=='Carvanha'
search['evidence_ids'] = ['independent_sol:F0152.50','F0154.00']
search['cards_in_reveal_order'][0].update(timestamp_seconds=152.502,
    evidence_ids=['independent_sol:F0152.50','F0154.00'],
    basis='Enlarged Carvanha reveal directly observed at measured source PTS 152.502 s; F0154.00 supports the resulting hand.',
    limit_reason='152.502 s is the selected reveal-frame time, not the exact start of the search animation.')
play = t10['plays_in_order'][0]
assert play['evidence_ids'] == ['F0152.00']
play['evidence_ids'] = ['F0152.00','independent_sol:F0152.50','F0154.00']
play['basis'] = 'F0152.00 shows the transaction before the reveal; independent_sol:F0152.50 directly reveals Carvanha at PTS 152.502 s; F0154.00 shows the resulting hand. Item-use time remains approximate.'
t10['turn_evidence_ids'] += ['independent_sol:F0152.50','F0154.00']

# Add immutable independent extraction records with canonical capture roles.
for f in independent_manifest:
    nf = copy.deepcopy(f)
    is_search = f['evidence_id']=='independent_sol:F0152.50'
    preplay = f['evidence_id']=='independent_sol:F0096.50'
    nf.update(role=['independent_search_reveal' if is_search else 'independent_first_play_boundary'],
        turn_number=10 if is_search else 6, who_played='owner (Auto)',
        draw_animation_end_seconds=148 if is_search else 95,
        offset_after_draw_seconds=None if is_search else round(f['actual_frame_seconds_if_measured']-95,3),
        selected_for_start_hand=False,before_first_play=preplay,unzoomed=not is_search,
        hand_spread=True if preplay else None,
        observation='Enlarged Carvanha search reveal' if is_search else ('All four preplay cards still in hand; owner Bench 1 empty' if preplay else 'Vulpix moving into owner Bench 1; remaining hand is Cyrus, Copycat, Misty'),
        suitability_or_limit='Bounded independent native anchor; immutable extraction metadata in independent_sol/EXTRACTION_MANIFEST.json.')
    assert nf['evidence_id'] not in frames
    evidence['frames'].append(nf)
evidence['immutable_extraction_manifests'] = {n:sha(P/n) for n in ['EXTRACTION_MANIFEST.json','independent_sol/EXTRACTION_MANIFEST.json']}

review = (P/'REVIEW.md').read_text(encoding='utf-8-sig')
review = replace_once(review,'T6 uses an extra +0.30 s preplay frame because Auto acts before +1.',
    'T6 retains an extra +0.30 s selected preplay frame; the scheduled +1 s F0096.00 is also a usable preplay hand. Independent 96.505 s still shows Vulpix in hand; 97.005 s shows its bench action in progress, so onset is bracketed rather than measured exactly.')
review = replace_once(review,'Research reveals Lapras then Vulpix; T10 Poké Ball finds Carvanha.',
    'Research reveals Lapras then Vulpix; T10 Poké Ball finds Carvanha, directly exposed at independent_sol:F0152.50 (measured PTS 152.502 s), with the resulting hand at F0154.00. F0152.00 precedes the reveal.')
review += '\n## Bounded independent corrections\n\nR1-R3 corrected by /root/astra_drafta_bounded_repairs, gpt-6-astra, high effort. Binding Snow is an opponent-player restriction on Energy Zone attachment to whichever Pokemon is Active during the next opponent turn. Native printed text at F0178.00 establishes that target and duration. The icon persists after the T15 retreat at F0222.50, while the now-benched Wailord receives Water; it is absent after T15 resolution at F0231.50 and before the next attack at F0243.50. Thus the T14 effect is absent in T15 board_after and T16 board_at_start. F0254.50 shows a newly applied terminal T16 icon, recorded separately without inventing a later turn. Original first-pass files and SUBMISSION.json are preserved in worker_submission; the effective manifest is SUBMISSION_AFTER_INDEPENDENT_REPAIR.json. This correction is a bounded clarification, not another complete visual pass.\n'
coverage = (P/'COVERAGE.md').read_text(encoding='utf-8-sig')
coverage += '\nBounded R1-R3 correction: reused native frames for printed Binding Snow wording, T15 post-retreat and end-turn expiry, T6 preplay/action boundary, and T10 Carvanha reveal. The T6 +1 s view is preplay; the selected +0.30 s view remains valid. Three independently extracted source-bound frames are now included in TURN_EVIDENCE.json and remain frozen in independent_sol/EXTRACTION_MANIFEST.json. The primary extraction manifest is unchanged. No additional source extraction or whole-battle re-review was performed.\n'
table = (P/'TURN_TABLE.md').read_text(encoding='utf-8-sig')
table = replace_once(table,'Alolan Vulpix (96s): Second Vulpix benched','Alolan Vulpix (about 97s; after 96.505, by 97.005): Second Vulpix benched')
table = replace_once(table,'F0095.30, F0096.00, F0098.00','F0095.30, F0096.00, independent_sol:F0096.50, independent_sol:F0097.00, F0098.00')
table = replace_once(table,'F0149.00, F0152.00, F0155.00','F0149.00, F0152.00, independent_sol:F0152.50 (reveal at 152.502s), F0154.00, F0155.00')

backup = P/'worker_submission'
backup.mkdir()
for name in list(submission['files'])+['SUBMISSION.json']:
    shutil.copy2(P/name,backup/name)
    assert sha(backup/name)==sha(P/name)
write('TURN_LEDGER.json',ledger)
write('TURN_EVIDENCE.json',evidence)
for name,body in [('REVIEW.md',review),('COVERAGE.md',coverage),('TURN_TABLE.md',table)]:
    (P/name).write_text(body,encoding='utf-8')

assert all(sha(P/name)==value for name,value in frozen_before.items())
assert sha(P/'EXTRACTION_MANIFEST.json')==submission['files']['EXTRACTION_MANIFEST.json']
assert all(sha(backup/name)==value for name,value in submission['files'].items())
assert sha(backup/'SUBMISSION.json')==submission_sha
for t in ledger['turns']:
    for phase in ('board_at_start','board_after'):
        side=t[phase]['opponent']
        for c in [side['active']]+side['bench_in_position_order']:
            assert not c or old_effect not in c.get('active_effects',[])
assert by_turn[15]['board_after']['opponent']['board_effects']==[]
assert by_turn[16]['board_at_start']['opponent']['board_effects']==[]
assert by_turn[16]['board_after']['opponent']['board_effects'][0]['source_turn']==16
all_ids={f['evidence_id'] for f in evidence['frames']}
def refs(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in ('evidence_ids','turn_evidence_ids'):
                assert all(e in all_ids for e in v),v
            refs(v)
    elif isinstance(obj,list):
        for v in obj:refs(v)
refs(ledger)
now=datetime.now(timezone.utc).isoformat()
changed={name:{'before_sha256':old,'after_sha256':sha(P/name)} for name,old in submission['files'].items() if sha(P/name)!=old}
receipt={
    'schema':'bounded-independent-repair/v1','source_video':submission['source_video'],'source_sha256':submission['source_sha256'],
    'reviewer':'/root/astra_drafta_bounded_repairs','model':'gpt-6-astra','reasoning_effort':'high',
    'attribution_basis':'Root confirmed successful spawn arguments: model gpt-6-astra, reasoning_effort high, fork_turns none.',
    'repaired_utc':now,'scope':'Only frozen independent R1-R3; no new full visual review; no movie move or external log',
    'original_submission':{'path':'SUBMISSION.json','sha256':submission_sha,'preserved_copy':'worker_submission/SUBMISSION.json'},
    'frozen_files_verified_unchanged':frozen_before,
    'preserved_firstpass_files':submission['files'], 'changed_files':changed,
    'source_card_text':effect_text,
    'confirmed_repairs':[
        {'id':'R1','finding':'Player-level current-Active attachment restriction, expires at next opponent turn end; terminal T16 freshly applied icon retained.', 'evidence_ids':['F0178.00','F0222.50','F0231.50','F0243.50','F0254.50'],'removed_per_pokemon_paths':removed_paths,'added_player_effect_paths':added_paths},
        {'id':'R2','finding':'Scheduled T6 +1 frame preplay; visible bench onset after96.505 and by97.005; earlier selected hand retained.','evidence_ids':['F0096.00','independent_sol:F0096.50','independent_sol:F0097.00']},
        {'id':'R3','finding':'Carvanha directly exposed at152.502; F0152.00 precedes reveal. No identity/count change.','evidence_ids':['F0152.00','independent_sol:F0152.50']}],
    'independently_inspected_image_ids':['F0178.00','F0222.50','F0231.50','F0243.50','F0254.50','F0096.00','independent_sol:F0096.50','independent_sol:F0097.00','F0152.00','independent_sol:F0152.50'],
    'source_evidence_bindings':[f for f in manifest+independent_manifest if f['evidence_id'] in ['F0178.00','F0222.50','F0231.50','F0243.50','F0254.50','F0096.00','independent_sol:F0096.50','independent_sol:F0097.00','F0152.00','independent_sol:F0152.50']],
    'guards_passed':['All13 original submitted hashes matched before mutation','All primary and independent frame/crop hashes verified','All13 original files plus SUBMISSION preserved byte-for-byte','Protected source/assignment/submission and both extraction manifests unchanged','Original independent checks unchanged','All ledger evidence IDs resolve','No per-Pokemon Binding Snow copies remain','Expired T14 restriction absent after T15 and before T16','Fresh T16 terminal restriction retained with unobserved-future limit'],
    'supplement_gaps_not_repaired':{'evolution_stack':'No explicit per-Pokemon evolution-stack field; witnessed evolutions exist in plays but not the new fresh-board supplement.','seen_card_inventory':'No SEEN_CARD_INVENTORY.json or readable companion in this packet at repair time.','decision_actor':'Owner rows identify owner (Auto), and SUMMARY has whole-game authorship, but no explicit per-turn actor record with native span/override provenance.','scope':'Newest evening guide and batch GUIDE_UPDATE_REQUIREMENTS read; broad supplement remains separate from these narrow repairs.'},
    'acceptance':'Requires independent repair recheck and root lead acceptance; this receipt is not self-acceptance.'
}
write('REPAIR_RECEIPT.json',receipt)
effective=copy.deepcopy(submission)
effective.update(reviewer='/root/astra_drafta_bounded_repairs',model='gpt-6-astra',reasoning_effort='high',
    submitted_utc=now,original_submission_manifest='SUBMISSION.json',original_submission_sha256=submission_sha,
    original_submission_preserved_directory='worker_submission',
    files={name:sha(P/name) for name in submission['files']},
    immutable_extraction_manifests={name:sha(P/name) for name in ['EXTRACTION_MANIFEST.json','independent_sol/EXTRACTION_MANIFEST.json']},
    additional_files={'REPAIR_RECEIPT.json':sha(P/'REPAIR_RECEIPT.json')},
    independent_acceptance='pending_repair_recheck',validation='Guarded R1-R3 repaired; original submission and checks preserved; IDs resolve; no new full visual pass or broad supplement claim.')
write('SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
print(json.dumps({'changed_files':list(changed),'new_frame_ids':[f['evidence_id'] for f in independent_manifest],
    'effective_manifest_sha256':sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json'), 'repair_receipt_sha256':sha(P/'REPAIR_RECEIPT.json')},indent=2))
