from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from PIL import Image

p = Path(__file__).resolve().parent.parent
out = p / 'independent_sol'
sha = '7326d0f49952bda981acb67765fb118375963a485c52161e693cb7cf85be37fe'
video = '20261012_004435000_iOS.MP4'
files = ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
digest = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
frozen = {f: digest(p/f) for f in files}
docs = {f: json.loads((p/f).read_text(encoding='utf-8-sig')) for f in files if f.endswith('.json')}
source = json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
assert source['video_basename'] == video and source['sha256'] == sha
ledger = docs['TURN_LEDGER.json']['turns']
evidence = docs['TURN_EVIDENCE.json']['frames']
known = {f['evidence_id'] for f in evidence}
assert len(known) == len(evidence)
assert [r['turn_number'] for r in ledger] == list(range(1,11))
assert [r['opponent_hand_at_owner_turn_start']['count'] for r in ledger if r['who_played']=='owner'] == [4,2,3,3,5]
assert [r['owner_hand_end']['count'] for r in ledger if r['who_played']=='owner'] == [5,3,3,3,4]
assert [r['board_after']['turn_number_displayed'] for r in ledger[:3]] == [2,3,4]
for r in ledger:
    assert r['source_video'] == video
    assert [a['order'] for a in r['plays_in_order']] == list(range(1,len(r['plays_in_order'])+1))
    for key in ['owner_hand_start','owner_hand_end','owner_hand_before_end_action']:
        h = r[key]
        assert len(h['cards_left_to_right']) == h['count']
    for key in ['board_at_start','board_after']:
        for who in ['owner','opponent']:
            b = r[key][who]
            assert b['points'] == 0 and len(b['bench_in_position_order']) == 3
            for mon in [b['active']] + [x for x in b['bench_in_position_order'] if x]:
                assert mon['hp_now'] + mon['damage'] == mon['hp_max']
                assert sum(mon['attached_energy']['by_type'].values()) == mon['attached_energy']['total']
            assert set(b['energy_zone']) >= {'this_turn','next','evidence_ids'}
    if r['who_played']=='owner':
        candidates = [f for f in evidence if f['turn_number']==r['turn_number'] and f['offset_after_draw_seconds'] is not None]
        for offset in [1,3,6]:
            assert any(abs(f['offset_after_draw_seconds']-offset)<=.5 for f in candidates)
        assert any(f['selected_for_start_hand'] and f['before_first_play'] and f['unzoomed'] and f['bottom_crop'] and f['top_crop'] for f in candidates)
copycat = ledger[7]['draws_and_searches'][1]
assert copycat['hand_count_before'] == 0 and copycat['hand_count_after'] == 3
assert [c['name'] for c in copycat['cards_in_reveal_order']] == ["Professor's Research",'Kingdra ex','Small Balloon']
assert ledger[9]['board_after']['owner']['active']['hp_now'] == 10
assert ledger[9]['board_after']['opponent']['active']['hp_now'] == 30
assert ledger[9]['board_after']['opponent']['active']['attached_energy']['total'] == 4
assert ledger[9]['board_after']['opponent']['bench_in_position_order'][1]['attached_energy']['total'] == 2
assert not ledger[9]['board_after']['opponent']['active']['active_effects']
pg = docs['PAUSE_GAME.json']
assert pg['opening']['recorded_card_count'] == 5
assert pg['outcome']['concession_source_seconds'] == 451 and pg['outcome']['method']=='opponent_concession'
assert pg['capture_status']=='complete_with_recording_limits'
deck = docs['DECK_USED.json']
assert len(deck['cards_in_log_order']) == deck['total_card_slots'] == sum(x['count'] for x in deck['counts_by_name_and_variant']) == 20
qr = json.loads((out/'QR_DECODE.json').read_text())
live = json.loads((p.parent/'LIVE_DECK_SNAPSHOT_RESUME.json').read_text(encoding='utf-8-sig'))
assert qr['payload'] == live['decks'][0]['code']
norm = lambda s: s.replace('\u2019', "'")
assert {(norm(x['name']),x['variant'],x['count']) for x in deck['counts_by_name_and_variant']} == {(norm(x['name']),x['variant'],x['quantity']) for x in live['decks'][0]['counts_by_name_and_variant']}
for f in evidence:
    assert f['source_video']==video and f['source_sha256']==sha
    with Image.open(p/f['full_frame_path']) as im:
        assert im.size == (1170,2532)
    for key in ['bottom_crop','top_crop']:
        c=f[key]
        if c:
            b=c['pixel_bounds_x0_y0_x1_y1']
            with Image.open(p/c['path']) as im: assert im.size == (b[2]-b[0],b[3]-b[1])
            if key=='bottom_crop': assert b == [0,2025,1170,2532]
manifest = json.loads((p/'NATIVE_CROPS_MANIFEST.json').read_text())
assert len(manifest)==42
viewed = json.loads((out/'VIEWED_EVIDENCE.json').read_text())
additional = [44,134,186,304,449,451]
paths = {r['path'] for r in viewed['viewed_frames']}
for t in additional:
    rel = f'turn_evidence/t{t:07.2f}.jpg'
    if rel not in paths:
        viewed['viewed_frames'].append({'path':rel,'seconds':t,'viewed_as':'native','pixels':[1170,2532],'sha256':digest(p/rel)})
crop_names=['t0136.00_top.jpg','t0188.30_top.jpg','t0274.50_top.jpg','t0351.40_top.jpg','t0448.00_top.jpg','t0141.00_top.jpg','t0223.00_top.jpg','t0294.00_bottom.jpg']
for name in crop_names:
    rel='turn_evidence/'+name
    if rel not in paths:
        with Image.open(p/rel) as im: pixels=list(im.size)
        viewed['viewed_frames'].append({'path':rel,'viewed_as':'native_crop','pixels':pixels,'sha256':digest(p/rel)})
viewed['updated_utc']=datetime.now(timezone.utc).isoformat()
(out/'VIEWED_EVIDENCE.json').write_text(json.dumps(viewed,indent=2)+'\n',encoding='utf-8')
for r in viewed['viewed_frames']: assert digest(p/r['path'])==r['sha256']
assert frozen == {f:digest(p/f) for f in files}, 'Inputs changed during final check'
support=['SOURCE.json','QR_DECODE.json','NATIVE_CROPS_MANIFEST.json','independent_sol/REVIEW.md','independent_sol/QR_DECODE.json','independent_sol/VIEWED_EVIDENCE.json','../LIVE_DECK_SNAPSHOT_RESUME.json']
result={
 'accepted':True,'status':'accepted_with_recording_limits','source_video':video,'source_sha256':sha,
 'reviewer':'/root/verify_pause_004435','model':'gpt-6.1-sol','reasoning_effort':'high',
 'checked_at_utc':datetime.now(timezone.utc).isoformat(),
 'acceptance_scope':'Bounded independent source verification of completed full-battle and Pause Games packet; not a second full decode or simulator replay. Lead owns registration, archival and external log verification.',
 'required_repairs':[],
 'resolved_repairs':['Owner-start fans corrected to4/2/3/3/5 from native crops across prose, coverage, ledger and evidence.','First three after-board records changed to resolved boundaries with displayed turns2/3/4 and qualified generation phases.','Copycat draw count starts at0 after played card and shuffle; separate pre-Supporter count2 retained.','Native294 final-hand crop pair added;42pairs total.','Acting-opponent visible counts retained separately from hidden identities with before/afterdraw phases.'],
 'accepted_input_sha256':frozen,
 'checked_supporting_sha256':{f:digest(p/f) for f in support},
 'source_identity_checks':{'basis':'Frozen CLI SHA-256/size/duration/native-dimensions binding; no new source rehash or video seek by independent reviewer.','source_rehash_performed':False,'size_bytes':861227730,'duration_seconds':463.93,'native_dimensions':[1170,2532],'independent_QR_native_pixel_reread':True,'QR_payload_live_match':True},
 'outcome_verified':{'owner':'Dacz8976','opponent':'Chuaryzard','result':'win','method':'opponent_concession','concession':True,'concession_source_seconds':451,'victory_source_seconds':462,'final_points':{'owner':0,'opponent':0},'turn_count':10,'owner_result_damage':90},
 'capture_status':'complete_with_recording_limits','structural_validation':{'pass':True,'turn_rows':10,'native_frames':len(evidence),'crop_pairs':42,'issues':[]},
 'viewed_manifest':'VIEWED_EVIDENCE.json',
 'limits':['Hidden opponent identities and unopened discard piles are unavailable.','Mega Blaster mills3 cards; only final top Soothing Shore is visible and the other2 identities remain unknown.','Requested source seeks and action/draw timings are approximate; actual encoded frame PTS was not measured.','Queue subtype/ranked status remains unknown; no Auto control was observed.','Owner turn10 Research inspection/lift does not establish a completed play or2draws.','Match date2026-10-11 uses parent-verified source creation time and Chicago conversion; SOURCE.json remains frozen.','QR proves semantic entities and Water, not exact printing/artwork/rarity.']}
(out/'CHECK_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':True,'sealed_inputs':len(frozen),'native_frames':len(evidence),'crop_pairs':42,'required_repairs':[]}))
