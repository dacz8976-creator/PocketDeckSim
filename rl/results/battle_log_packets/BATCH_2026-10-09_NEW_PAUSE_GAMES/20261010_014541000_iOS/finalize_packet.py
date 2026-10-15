import json,re
from pathlib import Path
p=Path(__file__).parent
def load(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,x):(p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=load('DECK_USED.json')
d['later_QR_candidate_source']='../20261010_015452000_iOS/QR_DECODE.json'
d['later_QR_candidate_conflicts']=[{'card':'Elegant Cape','basis':'Owner draws Elegant Cape from Research on turn7, retains it in hand, and attaches it to Koffing on turn11. Root reports later015452QR20 excludes Elegant Cape.','evidence_ids':['f_0264.00','f_0268.00','f_0439.00'],'status':'Visible earlier-game card conflicts with later QR candidate'}]
d['conflicts_with_filmed_cards']='Later015452QR candidate lacks Elegant Cape, which is visibly drawn and played in this earlier game. Exact earlier20 remains unverified.'
save('DECK_USED.json',d)
u=load('UNCERTAINTIES.json')
u['recording_limits'][0]['evidence']+=' Later015452QR candidate excludes visibly drawn/played Elegant Cape, per root candidate comparison.'
save('UNCERTAINTIES.json',u)
m=load('VIEWED_EVIDENCE_MANIFEST.json')
m['viewed_image_paths']+=['turn_evidence/energy_check.jpg','turn_evidence/t0473.30.jpg','turn_evidence/t0180.00.jpg','turn_evidence/t0315.00.jpg','turn_evidence/t0339.00.jpg']
m['viewed_image_paths']=list(dict.fromkeys(m['viewed_image_paths']))
save('VIEWED_EVIDENCE_MANIFEST.json',m)
for name in ['REVIEW.md','COVERAGE.md']:
    s=(p/name).read_text(encoding='utf-8')
    # Readability corrections only; preserve filenames and hashes.
    s=re.sub(r'\b(turn|Turn|turns|Turn\s|Stage|native|Native|position|points|seconds|duration)(\d)',r'\1 \2',s)
    s=re.sub(r'(\d)(seconds|second|turns|turn|cards|card|damage|points|point|decks|deck|frames|frame|HP|HP\b|Water|HPdoes)',r'\1 \2',s)
    s=s.replace('Poison10andBurn20','Poison 10 and Burn 20').replace('by20','by 20').replace('by40','by 40').replace('all12recorded','all 12 recorded').replace('all12turns','all 12 turns').replace('Sol, high','Sol, high').replace('December','December')
    if name=='REVIEW.md':s+='\nLater-candidate version conflict: the subsequent 015452 QR deck omits Elegant Cape, which is visibly drawn and played here. This game must remain an earlier unverified variant and must not inherit that later exact list.\n'
    (p/name).write_text(s,encoding='utf-8')
e=load('TURN_EVIDENCE.json'); ids={f['evidence_id'] for f in e['frames']}
l=load('TURN_LEDGER.json')
assert len(l['turns'])==12
assert [x['turn_number'] for x in l['turns']]==list(range(1,13))
missing=[]
def check(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ['evidence_ids','turn_evidence_ids'] and isinstance(v,list):
                missing.extend(z for z in v if z not in ids)
            else:check(v)
    elif isinstance(x,list):
        for v in x:check(v)
check(l)
assert not missing,missing
for f in e['frames']:
    assert (p/f['full_frame_path']).exists()
    assert (p/f['bottom_crop']['path']).exists()
    assert (p/f['top_crop']['path']).exists()
save('PACKET_VALIDATION.json',{'status':'passed','turn_rows':12,'native_frames':len(e['frames']),'all_ledger_evidence_ids_resolve':True,'all_native_frames_and_crops_exist':True,'independent_acceptance':'pending_lead','exact_game_deck20':'unverified_with_later_QR_Elegant_Cape_conflict'})
print('Validated12turn rows and all native paths/evidence IDs')
