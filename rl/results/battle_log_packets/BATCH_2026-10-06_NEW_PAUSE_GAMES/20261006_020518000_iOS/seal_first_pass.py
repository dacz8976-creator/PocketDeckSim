import json,subprocess,sys,hashlib,datetime
from pathlib import Path
from PIL import Image
P=Path(__file__).parent
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
L=read('TURN_LEDGER.json');E=read('TURN_EVIDENCE.json');proto=E['frames'][0]
for n in [14,16]:
    a=L['turns'][n-1]['plays_in_order'][-1];a['prompt_text']='Please choose a Pokémon to switch in'
    if n==14:a['evidence_ids']=['f0478_00','f0480_00','f0482_00'];a['timestamp_seconds']=478
if 'f0478_00' not in {f['evidence_id'] for f in E['frames']}:
    name='t0478.00.jpg'
    with Image.open(P/'turn_evidence'/name) as im:
        for suffix,bounds in [('bottom',(0,2025,1170,2532)),('top',(0,0,1170,700))]:im.crop(bounds).save(P/'turn_evidence'/f't0478.00_{suffix}.png')
    E['frames'].append({'evidence_id':'f0478_00','role':'mandatory_promotion_prompt','turn_number':14,'who_played':'owner mandatory choice during opponent turn',
     'source_video':proto['source_video'],'source_sha256':proto['source_sha256'],'requested_source_seconds':478,'actual_frame_seconds_if_measured':None,
     'full_frame_path':'turn_evidence/'+name,'native_dimensions':{'width':1170,'height':2532},
     'bottom_crop':{'path':'turn_evidence/t0478.00_bottom.png','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
     'top_crop':{'path':'turn_evidence/t0478.00_top.png','pixel_bounds_x0_y0_x1_y1':[0,0,1170,700]},
     'selected_for_start_hand':False,'before_first_play':False,'unzoomed':True,
     'observation':'Exact prompt: Please choose a Pokémon to switch in; owner Sandslash and Sandshrew highlighted on Bench.',
     'suitability_or_limit':'Owner Active is empty pending choice; opponent first point is already awarded.'})
L['turns'][13]['turn_evidence_ids']=sorted(set(L['turns'][13]['turn_evidence_ids']+['f0478_00']))
E['frames'].sort(key=lambda f:f['requested_source_seconds']);save('TURN_LEDGER.json',L);save('TURN_EVIDENCE.json',E)
run=subprocess.run([sys.executable,str(P.parent/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8')
receipt=json.loads(run.stdout);assert run.returncode==0 and receipt['structural_pass'],receipt
receipt['checked_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['packet_hashes']={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','CONSISTENCY_CHECK.json']}
receipt['native_frame_manifest_count']=len(E['frames']);receipt['worker_state']='stable_first_pass_pending_independent_acceptance'
save('STRUCTURAL_CHECK.json',receipt)
save('FIRST_PASS_SUBMISSION.json',{'source_video':proto['source_video'],'source_sha256':proto['source_sha256'],
 'status':'stable_full_first_pass_submitted_for_independent_acceptance','source_coverage_seconds':[0,616.08966],'games':1,'turns':17,
 'owner_result':'Victory3-2 versusAdgbag','local_match_date':'2026-10-05','structural_receipt':'STRUCTURAL_CHECK.json','consistency_receipt':'CONSISTENCY_CHECK.json',
 'limits':'Absent matching live deck list; hidden opponent identities; discard piles never opened; QR artwork printing not encoded; requested seek times rather than measuredPTS.',
 'worker_prohibited_actions_performed':False,'note':'Do not rerun build_packet.py or first-pass finalizers after lead edits.'})
print(json.dumps(receipt,ensure_ascii=False,indent=2))
