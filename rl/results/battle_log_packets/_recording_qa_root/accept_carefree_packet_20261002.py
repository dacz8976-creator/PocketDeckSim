"""Lead acceptance for available footage of the two-part owner rules test."""
import argparse,shutil
from datetime import datetime,timezone
from intake_carefree_snipes_20261002 import ROOT,BATCH,VIDEOS,read,save
from accept_shark_packet_20261002 import explicit_image_paths

def main():
    parser=argparse.ArgumentParser();parser.add_argument('video',choices=VIDEOS);parser.add_argument('--evidence',nargs='+',required=True);parser.add_argument('--notes',required=True);parser.add_argument('--astra',nargs='*',default=[]);args=parser.parse_args()
    p=ROOT/'Recording_QA'/(args.video.removesuffix('.MP4')+'_rule_sol')
    source=read(p/'SOURCE.json');assignment=read(p/'ASSIGNMENT.json');summary=read(p/'SUMMARY.json')
    assert source['video_basename']==assignment['video_basename']==summary['video_basename']==args.video
    assert source['sha256']==assignment['sha256'] and summary['complete_available_footage_review']
    assert not source['ladder_eligible'] and not source['pause_games_eligible']
    for ref in args.evidence:assert (p/ref).resolve().is_relative_to(p.resolve()) and (p/ref).is_file(),ref
    for ref in args.astra:assert (BATCH/ref).is_file(),ref
    history=p/'worker_submission';history.mkdir(exist_ok=True)
    for filename in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
        assert (p/filename).is_file()
        if not (history/filename).exists():shutil.copyfile(p/filename,history/filename)
    for filename in ['REVIEW.md','COVERAGE.md']:
        path=p/filename
        prose=path.read_text(encoding='utf-8-sig').replace(p.as_posix()+'/', '')
        prose=explicit_image_paths(prose,p)
        prose=prose.replace('First-pass draft awaiting lead acceptance.','The complete first pass has been independently accepted by the lead.')
        prose+='\n\n## Independent lead check\n\n'+args.notes+'\n'
        prose+='\nFirst-pass reviewer: '+source['reviewer']+'; '+source['review_model']+' high. Independent lead and targeted Astra checks: October 2, 2026.\n'
        for ref in args.astra:prose+='\n[Targeted Astra check](../'+BATCH.name+'/'+ref+').\n'
        assert '\u2014' not in prose
        path.write_text(prose,encoding='utf-8')
    summary.update({'lead_acceptance':'accepted','lead_notes':args.notes,'ladder_eligible':False,'pause_games_eligible':False,'review_group':BATCH.name,'astra_reports':args.astra});save(p/'SUMMARY.json',summary)
    uncertainties=read(p/'UNCERTAINTIES.json')
    if isinstance(uncertainties,list):uncertainties={'items':uncertainties,'raw_list_preserved':True}
    uncertainties.update({'lead_check_complete':True,'material_claims_reconciled':True,'astra_reports':args.astra});save(p/'UNCERTAINTIES.json',uncertainties)
    acceptance={'source_video':args.video,'source_sha256':source['sha256'],'accepted':True,'coverage_checked':True,'completion_status':'rule_test_review_complete','ladder_eligible':False,'pause_games_eligible':False,'remaining_coverage_gaps':[],'unverified_material_claims':[],'scope':f"Entire available {source['duration_seconds']}-second source as one part of the two-recording computer rules test. Recording interruption and hidden/missing battle actions remain explicit; rule-test completion does not assert uninterrupted full-battle footage.",'lead_evidence':args.evidence,'lead_notes':args.notes,'astra_reports':args.astra,'review_group':BATCH.name,'related_source':next(n for n in VIDEOS if n!=args.video),'review_model':source['review_model'],'reasoning_effort':source['reasoning_effort'],'checked_at':datetime.now(timezone.utc).isoformat()}
    assert not (p/'LEAD_ACCEPTANCE.json').exists()
    save(p/'LEAD_ACCEPTANCE.json',acceptance)
    (p/'LEAD_CLARIFICATION.md').write_text('# Independent lead check\n\n'+args.notes+'\n\nThe two files represent one owner-declared test battle. This completed test is excluded from Pause Games and Ladder Log. No simulator change, repair pinning or training occurred.\n',encoding='utf-8')
    print('Accepted available rules-test source '+args.video)

if __name__=='__main__':main()
