"""Bind a distinct independent source check to the four latest guide files."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from validate_packet import BATCH,local,read,sha

NAMES=['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md']
def accept(packet,check_ref,manifest_ref):
 source=read(packet/'SOURCE.json')
 manifest_path=local(packet,manifest_ref);manifest=read(manifest_path)
 check_path=local(packet,check_ref);check=read(check_path)
 assert check['accepted'] is True and check['guide_update_checked'] is True
 assert check['source_video']==source['video_basename'] and check['source_sha256']==source['sha256']
 assert check['checked_submission_manifest_sha256']==sha(manifest_path)
 assert check['checked_submission_files']==manifest['files']
 assert not check['remaining_coverage_gaps'] and not check['unverified_material_claims']
 for n,s in manifest['files'].items():assert sha(local(packet,n))==s,n
 assert set(NAMES).issubset(manifest['files'])
 supplement=read(packet/'GUIDE_UPDATE_SUPPLEMENT.json')
 author=supplement.get('reviewer',read(packet/'ASSIGNMENT.json')['reviewer'])
 assert author!=check['reviewer'],'Supplement checker must be distinct from author'
 accepted={n:sha(packet/n) for n in NAMES}
 receipt={'accepted':True,'accepted_utc':datetime.now(timezone.utc).isoformat(),'accepted_by':'/root','source_video':source['video_basename'],'source_sha256':source['sha256'],'guide_update_checked':True,'independent_reviewer':check['reviewer'],'independent_model':check['model'],'independent_check':check_ref,'independent_check_sha256':sha(check_path),'checked_submission_manifest':manifest_ref,'checked_submission_manifest_sha256':sha(manifest_path),'accepted_files':accepted,'remaining_coverage_gaps':[],'unverified_material_claims':[],'limits':check.get('recording_limits',check.get('limits',[])),'guide_source_receipt':'../GUIDE_UPDATE_RECEIPT.json','scope':'Only these eight current same-card computer comparison games; older packets untouched','actual_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX','external_game_entry_requested':False}
 out=packet/'GUIDE_UPDATE_ACCEPTANCE.json'
 if out.exists():
  previous=read(out)
  assert previous['accepted_files']==accepted and previous['independent_check_sha256']==receipt['independent_check_sha256']
  return previous
 out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return receipt
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('packet');parser.add_argument('check');parser.add_argument('--manifest',default='GUIDE_UPDATE_SUBMISSION.json');args=parser.parse_args()
 p=Path(args.packet).resolve();assert p.parent==BATCH
 result=accept(p,args.check,args.manifest);print(json.dumps({'accepted':True,'source_video':result['source_video'],'guide_files':len(result['accepted_files'])}))
