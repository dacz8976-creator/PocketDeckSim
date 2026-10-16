import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

p = Path(__file__).resolve().parent.parent
mfile = p / 'REVIEW_PACKET_HASHES.json'
raw = mfile.read_bytes()
m = json.loads(raw)
bad = [f for f, h in m['files'].items() if not (p/f).is_file() or hashlib.sha256((p/f).read_bytes()).hexdigest() != h]
s = json.loads((p/'SOURCE.json').read_text())
source = Path(s['source_path_at_review'])
stat = source.stat()
native_times = [5,13,76,150,203,205,228,237,245,265,364,365,371,379]
sheets = [4,5,9,10,12,13,15,16,17,23,24]
inspected = [{'path':f'native/t{t:07.2f}.jpg','source_seconds':t,'kind':'retained_native_source_frame'} for t in native_times]
inspected += [{'path':f'orientation/dense_sheet_{n:03d}.jpg','source_seconds':list(range((n-1)*16+1,min(n*16,380),2)),'kind':'retained_contact_sheet'} for n in sheets]
inspected += [{'path':f'independent_sol/native/t{t:07.2f}.jpg','source_seconds':t,'kind':'new_independent_native_source_frame'} for t in [186,186.5,273]]
r = {
 'accepted': not bad and stat.st_size == s['bytes'],
 'verdict':'accepted',
 'source_filename':s['video_basename'],
 'source_sha256':s['sha256'],
 'frozen_manifest_sha256':hashlib.sha256(raw).hexdigest(),
 'frozen_files_match':not bad,
 'frozen_file_count_checked':len(m['files']),
 'frozen_file_mismatches':bad,
 'primary_unchanged':not bad,
 'reviewer':'/root/check_214436',
 'model':'gpt-6.1-sol',
 'reasoning_effort':'high',
 'checked_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Bounded independent semantic acceptance of frozen complete primary review. Not a second full pass.',
 'workflow_read':['START_HERE_VIDEO_REVIEW.md','Review_Log/README.md'],
 'packet_read':['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','REVIEW_PACKET_HASHES.json'],
 'source_identity':{'binding':'Previously verified source SHA-256 reused; no repetitive source rehash.','path':str(source),'bytes':stat.st_size,'mtime_ns':stat.st_mtime_ns,'source_stat_matches_bound_bytes':stat.st_size==s['bytes'],'duration_seconds_from_bound_source':s['duration_seconds']},
 'inspected_evidence':inspected,
 'ordinary_turn_samples':[
  {'owner_turn':1,'global_turn':2,'source_interval_seconds':[57,80],'evidence':['orientation/dense_sheet_004.jpg','orientation/dense_sheet_005.jpg','native/t0076.00.jpg'],'observations':'Soothing Shore draw; Poke Ball reveals second Vulpix; bench placement; first Water attached to Benched Vulpix; Stadium played; Active has no Water and no attack. No contradiction with primary.'},
  {'owner_turn':2,'global_turn':4,'source_interval_seconds':[131,154],'evidence':['orientation/dense_sheet_009.jpg','orientation/dense_sheet_010.jpg','native/t0150.00.jpg'],'observations':'Research played and Cyrus/Elegant Cape drawn; first Active Water; evolution retains 30 damage (120 remaining); Cape raises remaining HP to150; only one Active Water; turn ends without attack. No contradiction with primary.'}
 ],
 'findings':[
  {'severity':'verified','claim':'Ranked human eligibility, label and opponent','evidence':['native/t0005.00.jpg','native/t0013.00.jpg'],'detail':'Season B4b SP / Ultra Ball Rank4 /700; Deck13-A; N.N Lv60. Ranked matchmaking visible. No Auto option appears in inspected evidence; primary whole-coverage account reports none.'},
  {'severity':'verified','claim':'Second order; first main attack ownT3/global6 with opponent0','evidence':['independent_sol/native/t0186.00.jpg','native/t0203.00.jpg','native/t0205.00.jpg','orientation/dense_sheet_013.jpg','native/t0379.00.jpg'],'detail':'Native new frame186 shows current turn6. Result says went second. Ordinary first two owner turns have no attack. First Binding Snow selected203, executed205 for80; preattack opponent score0. Prefix accepted: 2nd | Alolan Ninetales ex T3 | opp 0 pts.'},
  {'severity':'verified','claim':'Asleep and two Darkrai Bad Dreams knockout','evidence':['native/t0228.00.jpg','native/t0237.00.jpg','native/t0245.00.jpg','native/t0265.00.jpg','orientation/dense_sheet_015.jpg','orientation/dense_sheet_016.jpg','orientation/dense_sheet_017.jpg','independent_sol/native/t0273.00.jpg'],'detail':'Hypnoblast takes120 to80; separate triggers take80 to60 to40. Tails241 leaves Active Asleep. Following owner turn has no attack; triggers take40 to20 to0. Independent273 shows +2 and opponent2.'},
  {'severity':'verified','claim':'Terminal Mega Altaria ex130 and loss','evidence':['orientation/dense_sheet_023.jpg','native/t0364.00.jpg','native/t0365.00.jpg','native/t0371.00.jpg','native/t0379.00.jpg','orientation/dense_sheet_024.jpg'],'detail':'Already energized Mega Altaria comes from Bench after Espeon retreat. Three opposing Bench Pokemon; visible Mega Harmony text40+30 each;130 damage against70 HP. +2 award then Defeat. Result11 turns, owner1/opponent3 displayed,160 damage. Both +2 awards preserved; displayed3 is not a claim of total point awards being3.'},
  {'severity':'verified','claim':'Coverage and state reconciliation','detail':'Read complete timeline/checklist and checked ordinary samples plus consequential sequence. Single setup-to-terminal match, all11 turns accounted for, HP/points and two80 attacks reconcile with terminal160 damage. No material missing phase or source-supported contradiction found.'}
 ],
 'material_discrepancies':[],
 'limitations':[
  'This is bounded independent acceptance, not a repeated full visual pass. Primary full-coverage review remains the end-to-end account.',
  'Exact20-card lists, unrevealed opponent draws/search identities and owner intent remain unknown.',
  'No Auto option seen is a negative observation; ranked queue positively supports ladder classification. Broader no-Auto statement uses primary full coverage plus independent inspected evidence.',
  'Source hash/duration were already bound and verified by lead; independent check verified frozen packet hashes and current source size and extracted only three missing consequential frames.',
  'No external log, shared event/index, source move, or Boss Folder mirror performed.'
 ],
 'required_corrections':[]
}
assert r['accepted'], bad
(Path(__file__).parent/'CHECK_RESULT.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':r['accepted'],'files_checked':len(m['files']),'manifest_sha256':r['frozen_manifest_sha256'],'output':str(Path(__file__).parent/'CHECK_RESULT.json')}))
