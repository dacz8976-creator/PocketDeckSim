import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageStat

ROOT = Path(r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs')
B = ROOT/'Recording_QA/RETROSPECTIVE_HANDS_2026-10-02'
P = B/'20261002_021402000'
OUT = B/'independent_wailord/20261002_021402000'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sr = read(P/'SOURCE_REFERENCE.json')
old = Path(sr['frozen_source_json']).parent
source = read(old/'SOURCE.json')
move = read(old/'MOVE_RECEIPT.20261002_021402000_iOS.MP4.json')
evpath = next((ROOT/'Review_Log/events').glob('*'+sr['latest_shared_event']+'.json'))
event = read(evpath)
te = read(P/'TURN_EVIDENCE.json')
inh = read(P/'INHERITED_TURNS.json')
ledger = read(P/'TURN_LEDGER.json')
lines = (old/'REVIEW.md').read_text(encoding='utf-8-sig').splitlines()
checks = []
for frame in te['frames']:
    fp = Path(frame['full_frame_path'])
    with Image.open(fp) as im:
        full = im.convert('RGB')
        cr = []
        for label in ('bottom_crop','top_crop'):
            spec = frame[label]
            bounds = spec['pixel_bounds_x0_y0_x1_y1']
            expected = full.crop(bounds)
            with Image.open(spec['path']) as ci:
                crop = ci.convert('RGB')
                mad = sum(ImageStat.Stat(ImageChops.difference(expected,crop)).mean)/3 if crop.size == expected.size else None
                cr.append({'type':label,'path':spec['path'],'dimensions':list(crop.size),'bounds':bounds,'dimension_match':crop.size == expected.size,'mean_absolute_pixel_difference':round(mad,4) if mad is not None else None})
        checks.append({'evidence_id':frame['evidence_id'],'full_path':str(fp),'full_sha256':digest(fp),'full_dimensions':list(full.size),'native_match':full.size==(1170,2532),'source_binding_match':frame['source_sha256']==source['sha256'] and frame['source_video']==source['video_basename'],'crops':cr})
inherited = [{'turn':r['turn_number'],'line':r['accepted_source_line'],'verbatim_match':lines[r['accepted_source_line']-1] == r['verbatim_accepted_row']} for r in inh['rows']]
output = {
 'reviewer':'sol_verify_wailord_021402', 'checked_utc':datetime.now(timezone.utc).isoformat(),
 'status':'needs_repair', 'scope':'Opening and six owner hands, named draw/search evidence, crop/source provenance and inherited ledger boundaries only; no new board/outcome review.',
 'source_identity':{'basename':source['video_basename'],'sha256':source['sha256'],'bytes':source['bytes'],'duration_seconds':source['duration_seconds'],'frozen_source_json':str(old/'SOURCE.json'),'move_receipt':str(old/'MOVE_RECEIPT.20261002_021402000_iOS.MP4.json'),'move_before_after_hash_match':move['sha256_before']==move['sha256_after']==source['sha256'],'source_reference_hash_match':sr['sha256']==sr['current_verified_sha256']==source['sha256'],'shared_event_path':str(evpath),'shared_event_hash_match':event.get('video_sha256')==source['sha256'],'current_path':sr['current_source_path'],'current_metadata_bytes':Path(sr['current_source_path']).stat().st_size,'original_content_reads_by_independent_checker':0,'limit':'Frozen receipt identity and worker hash statement corroborated; checker did not reread or rehash original.'},
 'accepted_context':{'review_sha256_actual':digest(old/'REVIEW.md'),'review_sha256_matches_inherited':digest(old/'REVIEW.md')==inh['accepted_review_sha256'],'inherited_rows':inherited,'ledger_turn_numbers':[x['turn_number'] for x in ledger['turns']],'target_turn_numbers':[1,3,5,7,9,11],'owner13_limit_preserved':True},
 'image_checks':checks,
 'metrics':{'registered_full_images_metadata_checked':len(checks),'registered_crops_checked':sum(len(x['crops']) for x in checks),'visual_image_submissions':30,'new_extractions':0,'original_reads':0,'new_evidence_image_bytes':0,'wall_seconds':None,'token_usage':None,'dollar_usage':None,'unmeasured_reason':'Wall time and token/dollar usage not instrumented.'},
 'required_repair':[{'files':['HAND_SUPPLEMENT.json','TURN_LEDGER.json'],'turn_number':7,'field':'draws_and_searches research event limit_reason and first-card basis/reveal_order provenance','reason':'native137.00 shows Copycat enlarged as current reveal and Indeedee ex already appended in hand; it does not show an Indeedee reveal at137.','requested':'Replace Indeedee revealed first at137 with Indeedee already appended in fan at137; Copycat directly shown enlarged at137 and retained at139. Qualify Indeedee-then-Copycat ordering from append position/state rather than claim the first reveal at137.'}],
 'supported_findings':{'opening_cards':['Poké Ball','Pokémon Center Lady','Heavy Helmet','Wailmer','Irida'],'all_six_start_and_end_hands_match':True,'quick_turn5_preplay_supported_by100_8_then101_2':True,'copycat_five_cards_in_append_order':['Heavy Helmet','Indeedee ex','Soothing Shore','Lucky Ice Pop','Soothing Shore'],'copycat_duplicate_shores_direct_at252':True,'research_turn11_direct_reveal_order':['Cyrus','Poké Ball'],'opponent_fans':[3,5,[7,8],[7,8],5,4]},
 'limits':['Exact decoded PTS unmeasured; source-local requested seeks only.','Normal draw card identity direct in new append position; transaction identification follows adjacent hand continuity.','Copycat identities/direct append order verified; exact individual reveal onset remains unmeasured.','Opponent turns5/7 fan overlap retained as7-8 range.','Turn11 unsuccessful Poke Ball inherited accepted message and ending count, not independently rereviewed.','Boards, actions, outcome and owner13 inherited or outside target scope.']
}
(OUT/'SOURCE_CHECKS.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'native_frames':len(checks),'native_all_match':all(x['native_match'] for x in checks),'crop_dimensions_all_match':all(c['dimension_match'] for x in checks for c in x['crops']),'max_crop_pixel_MAD':max(c['mean_absolute_pixel_difference'] for x in checks for c in x['crops']),'review_hash_match':output['accepted_context']['review_sha256_matches_inherited'],'all_inherited_rows_match':all(x['verbatim_match'] for x in inherited),'event_hash_match':output['source_identity']['shared_event_hash_match']}))
