import json, hashlib, datetime
from pathlib import Path
P=Path(__file__).resolve().parent.parent; O=P/'independent_sol'
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
times=[33,58,65,66,62,71,77,118,148,149,154,211,215,216,282,298,300,328.1,331.1,384,393,395,407,458.1,468,498,509.5,522,114,169,188,489,530,554,565,116,160,229,336,406,467,521,79,162,235,302,346,410,471,414,550,35,28]
E=read('TURN_EVIDENCE.json'); bytime={f['requested_source_seconds']:f for f in E['frames']}
viewed=[]
for t in times:
    f=bytime.get(t)
    if f is None:
        path='turn_evidence/t'+format(t,'07.2f')+'.jpg'
        f={'evidence_id':None,'full_frame_path':path,'requested_source_seconds':t,'source_video':'20261010_013009000_iOS.MP4'}
    viewed.append({'evidence_id':f['evidence_id'],'path':'../'+f['full_frame_path'],'requested_source_seconds':t,'source_video':f['source_video'],'native_dimensions':[1170,2532],'retained_sha256':sha(P/f['full_frame_path']),'inspection':'Actual native full frame via view_image, directly inspected; source seek time is not measured PTS'})
(O/'VIEWED_EVIDENCE.json').write_text(json.dumps({'reviewer':'/root/check_013009','source_sha256':'80615dfc9c1e28f95434e3b4712f0540e6efc34392aef816419b6f82a0257329','actual_viewed_frame_count':len(viewed),'whole_battle_second_pass':False,'frames':viewed},ensure_ascii=False,indent=2),encoding='utf-8')
files=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
hashes={n:sha(P/n) for n in files}
L=read('TURN_LEDGER.json')
errors=[]
for t in L['turns']:
    for b in ['board_at_start','board_after']:
        pk=t[b]['owner']['active']
        if pk:
            for e in pk['active_effects']:
                if e['name']=='Pile-Driving Hammer cost increase':
                    if t['turn_number']>=16 or (t['turn_number']==15 and b=='board_after'):errors.append('Hammer persisted after T15')
                    if '16' in str(e.get('expiry')):errors.append('Hammer expiry wrong')
for n,display in [(1,2),(3,4),(13,14)]:
    if L['turns'][n-1]['board_after']['turn_number_displayed']!=display:errors.append('display turn repair '+str(n))
if 'absent' in read('SUMMARY.json')['games'][0]['deck_provenance']:errors.append('stale deck provenance')
if not any('fade' in x.lower() for x in read('PAUSE_GAME.json')['limits']):errors.append('missing T9 fade limit')
if hashes!={n:sha(P/n) for n in files}:errors.append('input mutation while hashing')
R={'reviewer':'/root/check_013009','model':'gpt-6.1-sol','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Bounded independent packet/evidence check, not second full battle visual pass','status':'accepted_with_recording_limits' if not errors else 'repairs_required','blocking_findings':errors,'source_sha256':'80615dfc9c1e28f95434e3b4712f0540e6efc34392aef816419b6f82a0257329','source_bytes':1046911287,'source_hash_independently_verified':True,'accepted_input_sha256':hashes if not errors else None,'input_hashes_at_check':hashes,'actual_native_frames_viewed':len(viewed),'structural_frame_count':len(E['frames']),'turn_rows':len(L['turns']),'exact_deck_slots':len(read('DECK_USED.json')['cards_in_log_order']),'support_files':['CHECK.md','VIEWED_EVIDENCE.json','STRUCTURAL_CHECK.json'],'external_log_independently_refetched':False,'main_packet_or_index_or_external_modified':False,'source_moved':False}
(O/'CHECK_RESULT.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(R,ensure_ascii=False,indent=2))
