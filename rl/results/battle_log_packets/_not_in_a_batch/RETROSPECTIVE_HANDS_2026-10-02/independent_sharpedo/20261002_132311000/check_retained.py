import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageStat
ROOT=Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs')
B=ROOT/'Recording_QA/RETROSPECTIVE_HANDS_2026-10-02'
P=B/'20261002_132311000'
O=B/'independent_sharpedo/20261002_132311000'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sr=read(P/'SOURCE_REFERENCE.json'); source=read(Path(sr['frozen_source_reference']))
old=Path(sr['frozen_source_reference']).parent
local=read(P/'LOCAL_SOURCE_VERIFICATION.json')
move=read(old/'MOVE_RECEIPT.20261002_132311000_iOS.MP4.json')
ep=next((ROOT/'Review_Log/events').glob('*'+sr['latest_shared_completion_event']+'.json')); event=read(ep)
te=read(P/'TURN_EVIDENCE.json'); hand=read(P/'HAND_SUPPLEMENT.json')
checks=[]
for f in te['frames']:
    fp=Path(f['full_frame_path'])
    with Image.open(fp) as im:
        full=im.convert('RGB'); crops=[]
        for key in ('bottom_crop','top_crop'):
            spec=f[key]; bounds=spec['bounds']; expected=full.crop(bounds)
            with Image.open(spec['path']) as ci:
                actual=ci.convert('RGB'); mad=sum(ImageStat.Stat(ImageChops.difference(actual,expected)).mean)/3 if actual.size==expected.size else None
                crops.append({'type':key,'path':spec['path'],'bounds':bounds,'dimensions':list(actual.size),'dimension_match':actual.size==expected.size,'source_frame_matches':spec['source_frame']==str(fp),'mean_absolute_pixel_difference':mad})
        checks.append({'evidence_id':f['evidence_id'],'full_path':str(fp),'full_sha256':sha(fp),'full_dimensions':list(full.size),'native_match':full.size==(1170,2532),'source_binding_match':f['source_sha256']==source['sha256'] and f['source_video']==source['video_basename'],'crops':crops})
assert all(x['native_match'] and x['source_binding_match'] for x in checks)
assert all(c['dimension_match'] and c['source_frame_matches'] and c['mean_absolute_pixel_difference']==0 for x in checks for c in x['crops'])
hash_match=source['sha256']==local['sha256']==move['sha256_before']==move['sha256_after']==sr['source_identity']['sha256']==event['video_sha256']
assert hash_match
result={
 'reviewer':'sol_verify_wailord_021402','checked_utc':datetime.now(timezone.utc).isoformat(),'verdict':'accepted_with_recording_limits','scope':'Two targeted starting and ending hands, normal draw evidence, timing/crop/source checks for owner turns5 and11 only.',
 'source_checks':{'source_basename':source['video_basename'],'sha256':source['sha256'],'bytes':source['bytes'],'duration_seconds':source['duration_seconds'],'frozen_source_json':sr['frozen_source_reference'],'local_source_receipt':str(P/'LOCAL_SOURCE_VERIFICATION.json'),'local_verification_utc':local['verified_utc'],'archive_receipt':str(old/'MOVE_RECEIPT.20261002_132311000_iOS.MP4.json'),'shared_event_path':str(ep),'all_receipt_hashes_match':hash_match,'current_metadata_bytes':Path(sr['current_archive_path']).stat().st_size,'receipt_current_source_path_matches':local['actual_source_path']==sr['current_archive_path'],'independent_original_reads':0,'limit':'Independent checker validates frozen/worker receipt agreement and metadata; did not rehash original.'},
 'extraction_receipts':{'first':read(P/'EXTRACTION_RECEIPT_1.json'),'second':read(P/'EXTRACTION_RECEIPT_2.json'),'first_source_hash_matches':read(P/'EXTRACTION_RECEIPT_1.json')['source_sha256']==source['sha256'],'final20th_frame_limit':'Only first19 frames have timed extraction receipts;20th frame is documented without separately measured extraction duration.'},
 'visual_findings':[{'turn_number':5,'start_frame':163.7,'start_cards_left_to_right':['Lucky Ice Pop','Cyrus','Alolan Ninetales ex','Misty','Irida','Mega Sharpedo ex'],'start_count':6,'draw_identity':'Mega Sharpedo ex','draw_direct_reveal':163,'next_first_play_frame':164.1,'before_attack_frame':190,'before_attack_hand':['Cyrus','Alolan Ninetales ex','Misty','Irida'],'opponent_count':5,'draw_end_bracket':[163,163.7],'normal_draw_basis':'Direct enlarged reveal; fan append independently observed; no identity inferred from bookkeeping.'},{'turn_number':11,'start_frame':359,'start_cards_left_to_right':['Cyrus','Misty','Irida','Alolan Vulpix','Copycat','Elegant Cape'],'start_count':6,'draw_identity':'Elegant Cape','draw_direct_reveal':358,'next_first_play_frame':360,'before_attack_frame':378,'before_attack_hand':['Cyrus','Misty','Copycat'],'opponent_count':3,'draw_end_bracket':[358,359],'normal_draw_basis':'Direct enlarged reveal; fan append independently observed; no identity inferred from bookkeeping.'}],
 'scheduled_candidates':{'turn5':[165,167,170.1],'turn11':[360,362,365],'independently_confirmed_unsuitable_after_first_play':True},
 'image_checks':checks,'worker_file_hashes':{n:sha(P/n) for n in ['SOURCE_REFERENCE.json','HAND_SUPPLEMENT.json','TURN_EVIDENCE.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']},
 'required_repairs':[], 'limits':['Exact frame PTS unmeasured; timestamps are requested source-local seeks and qualified brackets.','Some carried card title suffixes overlap, with identity supported by prefix/distinctive illustration and linked wider native hand views. Exact printing not assigned.','Before-attack hands are latest retained clear views, not exact last frame.','Accepted actions, outcomes, boards, other hands, opening and discard reconstruction remain outside this bounded check.','Historical deck-version equivalence remains unverified.'],
 'metrics':{'visual_image_submissions':16,'full_images_metadata_provenance_checked':len(checks),'crops_checked':len(checks)*2,'new_extractions':0,'original_content_reads':0,'new_evidence_image_bytes':0,'wall_seconds':None,'token_usage':None,'dollar_usage':None,'unmeasured_reason':'Wall time and usage not instrumented.'}}
(O/'SOURCE_CHECKS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(O/'METRICS.json').write_text(json.dumps(result['metrics'],indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verdict':result['verdict'],'full_frames':len(checks),'crops':len(checks)*2,'pixel_exact_crops':True,'source_receipts_match':hash_match}))
