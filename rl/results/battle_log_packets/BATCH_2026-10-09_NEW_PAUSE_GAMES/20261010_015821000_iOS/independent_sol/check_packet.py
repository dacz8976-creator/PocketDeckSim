from pathlib import Path
import json, hashlib, datetime
from collections import Counter
from PIL import Image
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES/20261010_015821000_iOS')
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
files=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
objs={f:json.loads((p/f).read_text(encoding='utf-8-sig')) for f in files if f.endswith('.json')}
e=objs['TURN_EVIDENCE.json']; l=objs['TURN_LEDGER.json']; d=objs['DECK_USED.json']
ids={f['evidence_id'] for f in e['frames']}; problems=[]
def walk(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='evidence_ids':
                for ref in v:
                    if ref not in ids: problems.append('unknown evidence '+ref)
            if k in ('source_sha256', 'sha256') and isinstance(v,str) and v!=src['sha256']: problems.append('source mismatch '+v)
            if k=='source_video' and v!=src['video_basename']: problems.append('filename mismatch '+str(v))
            walk(v)
    elif isinstance(x,list):
        for a in x: walk(a)
for o in objs.values(): walk(o)
assert [t['turn_number'] for t in l['turns']]==[1,2,3,4,5,6]
assert [t['who_played'] for t in l['turns']]==['owner','opponent']*3
for t in l['turns']:
    assert [a['order'] for a in t['plays_in_order']]==list(range(1,len(t['plays_in_order'])+1))
    for b in ('board_at_start','board_after'):
        for who in ('owner','opponent'):
            side=t[b][who]
            assert 'this_turn' in side['energy_zone'] and 'next' in side['energy_zone']
            for mon in [side['active']]+side['bench_in_position_order']:
                assert mon['damage']==mon['hp_max']-mon['hp_now']
                assert sum(mon['attached_energy']['by_type'].values())==mon['attached_energy']['total']
    if t['who_played']=='owner':
        offsets=[f['offset_after_draw_seconds'] for f in e['frames'] if f['turn_number']==t['turn_number'] and f['role']=='scheduled_draw_candidate']
        assert offsets==[1,3,6]
        assert any(f['role']=='before_end_action' and f['turn_number']==t['turn_number'] for f in e['frames'])
for f in e['frames']:
    assert Image.open(p/f['full_frame_path']).size==(1170,2532)
    for k in ('bottom_crop','top_crop'):
        crop=f[k]; bounds=crop['pixel_bounds_x0_y0_x1_y1']; expected=(bounds[2]-bounds[0],bounds[3]-bounds[1])
        assert Image.open(p/crop['path']).size==expected
qr=json.loads((p/'qr_intake/QR_DECODE_0001.00.json').read_text(encoding='utf-8-sig'))
live=json.loads((p.parent/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8-sig'))
match=[x for x in live['decks'] if x['code']==qr['payload']]
assert len(match)==1
slots=[{'name':name,'variant':var} for count,name,var in match[0]['rows'] for _ in range(int(count))]
assert slots==d['cards_in_log_order'] and len(slots)==20
assert sum(x['count'] for x in qr['cards'])==20
assert Counter(x['name'] for x in slots)==Counter({x['name']:x['count'] for x in qr['cards']})
try:
    import zxingcpp
    decoded=zxingcpp.read_barcodes(Image.open(p/'qr_intake/t0001.00.jpg'))
    assert any(x.text==qr['payload'] for x in decoded)
    qr_check='independent zxingcpp decode of retained native 1-second frame matches live saved payload'
except ImportError:
    qr_check='saved native decode payload independently reconciled with live snapshot and exact20; decoder unavailable for repeat decode'
assert not problems,problems
views=['t0026.50.jpg','t0042.50.jpg','t0093.30.jpg','t0094.00.jpg','t0139.00.jpg','t0162.00.jpg','t0047.00.jpg','t0048.00.jpg','t0148.00.jpg','t0196.00.jpg','t0197.00.jpg','t0200.00.jpg','t0204.00.jpg','t0003.00.jpg','t0084.00.jpg','t0220.00.jpg','t0226.00.jpg','t0236.00.jpg','t0242.00.jpg','t0253.00.jpg','crops/F0026_50_bottom.png','crops/F0093_30_top.png','crops/F0196_00_top.png','t0043.00.jpg','t0140.00.jpg','t0141.00.jpg','t0082.00.jpg','t0089.00.jpg','crops/F0042_50_top.png']
view_manifest=[]
for v in views:
    f=p/'turn_evidence'/v
    view_manifest.append({'path':str(f.relative_to(p)).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'native_dimensions':list(Image.open(f).size),'inspection':'Directly viewed via native view_image in this independent checker session'})
hashes={f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in files}
result={'schema':'bounded_independent_sol_acceptance_v1','reviewer':'/root/check_015821','model':'gpt-6.1-sol inherited','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_video':src['video_basename'],'source_sha256':src['sha256'],'source_bytes':src['bytes'],'source_identity_verification':'Independent PowerShell Get-FileHash SHA256 matched SOURCE.json; 462087569 bytes','accepted':True,'status':'accepted_with_recording_limits','blocking_findings':[],'blocking_repairs':[],'blockers':[],'accepted_input_sha256':hashes,'checked_input_sha256':hashes,'source_json_sha256':hashlib.sha256((p/'SOURCE.json').read_bytes()).hexdigest(),'scope':'Fresh bounded independent acceptance of completed end-to-end reviewer packet. Not a second full frame-by-frame review. Opening, ordinary first moves, consequential draws/searches, board/energy/fans and terminal result checked against native evidence; all 8 inputs structurally reconciled.','checks':{'opening':'Five original slots confirmed before Active; Koffing is Active in turn1 native board','first_actions':'T1 Research; T3 Horsea lifted in six-card fan93.3 then placement94; T5 Poké Ball missing from hand197 after full four-card hand196, Horsea reveal200 precedes Candy204','t3_hand':'139 is clear two-card hand before attachment/attack;140 and141 corroborate same two-card hand and one Water before Hook.148 names Hiking Trail Kingdra draw;162 has Candy/Shore/Kingdra, three cards after end effects. Pre-attack and resolved ending counts are distinct.','draws_searches':'Research Sabrina47 then Hiking Trail48; Hiking Trail Kingdra148; Poké Ball Horsea200; owner normal draws reconcile filmed start hands and ledger. No Copycat or guessed opponent identities.','opponent_fans':'Direct native top crops show4 at42.5,6 at93.3,5 at196; transaction inference remains separately labeled','board_energy':'Native ordinary opponent turn2 shows Water on Frigibax82, Suicune promotion84, no attached Energy on either at89. Native owner turns3 and5 reconcile Water counts, Balloon inheritance,140HP Weezing, caped160HP Suicune,90damage to70 and cannot-retreat effect226; opponent current/next Water visible at concession242. All12 start/end boards contain both sides and typed Energy Zones.','outcome':'242 Your opponent conceded;253 Victory vs よこっぴ, went first,6turns,1–0,120damage. Event mode visible3; no Auto observed in checked native states.','deck':qr_check,'structure':f'6 unique chronological turns; sequential actions; {len(e["frames"])} native1170x2532 frames and corresponding crop paths/dimensions validated; all evidence refs and source bindings resolve'},'recording_limits':['Hidden opponent cards stay hidden','No full discard-pile viewer shown; periodic requested snapshots explicitly unavailable','Estimated seek timestamps are not actual measured PTS','Artwork/rarity not established from semantic QR','Burn coin face and Tool name glare retained as limits'],'repairs_made':[],'viewed_evidence':view_manifest}
out=p/'independent_sol'; (out/'CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'INDEPENDENT_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='# Independent acceptance\n\nAccepted with recording limits. No blocking repairs.\n\nFresh bounded checker /root/check_015821 independently hashed the original source and checked all eight final packet inputs. The native opening, turn3 Horsea first move, turn5 Poké Ball before Rare Candy, Research reveals, Hiking Trail Kingdra draw, native opponent fans, ordinary paid retreat and Water states, resolved boards, concession and result screen support the packet.\n\nTurn3 139s is a two-card pre-attack hand, not the resolved ending hand. The 140/141s native views corroborate the same two cards with Water attached. Hiking Trail subsequently draws Kingdra ex;162s establishes the three-card resolved ending hand.\n\nThe source QR exactly matches the dated saved live20-card list. Hidden opponent identities, absent full discard views, approximate seek timestamps and unverified artwork/rarity remain explicit limits. This is bounded independent acceptance of an end-to-end review, not a claim of a second full source pass.\n\nCHECK_RESULT.json records the exact all-eight SHA256 freeze and29 actually viewed native references. Shared index, external log and source location were not changed.\n'
(out/'INDEPENDENT_CHECK.md').write_text(md,encoding='utf-8')
print(json.dumps({'accepted':True,'frames_validated':len(e['frames']),'viewed_refs':len(views),'qr_check':qr_check,'checked_input_sha256':hashes,'result':str(out/'CHECK_RESULT.json')},ensure_ascii=True,indent=2))

