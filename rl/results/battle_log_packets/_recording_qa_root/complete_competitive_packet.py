"""Accept, register and archive one source-bound competitive review."""
import argparse
import json
import re
import shutil
import subprocess
import sys
from intake_competitive_20261002 import ROOT,BATCH,packet_for,read,save,DESTINATION
from start_competitive_packet import SELECTED

def validate(name):
    packet=packet_for(name)
    for filename in ['SOURCE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','LEAD_ACCEPTANCE.json']:
        assert (packet/filename).is_file(),filename
    source=read(packet/'SOURCE.json'); assignment=read(packet/'ASSIGNMENT.json')
    lead=read(packet/'LEAD_ACCEPTANCE.json'); summary=read(packet/'SUMMARY.json')
    assert source['video_basename']==assignment['video_basename']==lead['source_video']==name
    assert source['sha256']==assignment['source_sha256']==lead['source_sha256']
    assert lead['accepted'] and lead['coverage_checked']
    assert lead['completion_status']=='full_battle_review_complete'
    assert assignment['requested_log']==lead['requested_log']==DESTINATION
    assert not assignment['ranked_ladder_eligible'] and not lead['ranked_ladder_eligible']
    assert summary['complete_available_footage_review'] and summary['battle_complete']
    assert not lead['remaining_coverage_gaps'] and not lead['unverified_material_claims']
    for ref in lead['lead_evidence']:
        path=(packet/ref).resolve()
        assert path.is_relative_to(packet.resolve()) and path.is_file(),ref
    for filename in ['REVIEW.md','COVERAGE.md']:
        prose=(packet/filename).read_text(encoding='utf-8-sig')
        assert '\u2014' not in prose,filename
        refs=set(re.findall(r'`([^`\n]+\.(?:jpg|png))`',prose))
        refs.update(re.findall(r'(?<![A-Za-z0-9_])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.*?-]+\.(?:jpg|png))(?![A-Za-z0-9_])',prose))
        for ref in refs:
            matches=list(packet.glob(ref)) if '*' in ref or '?' in ref else [packet/ref]
            if not all(path.is_file() for path in matches) and '/' not in ref and '\\' not in ref:
                matches=list(packet.rglob(ref)); assert len(matches)==1,ref
            assert matches and all(path.is_file() and path.resolve().is_relative_to(packet.resolve()) for path in matches),ref
    return packet,source,assignment,lead

def refresh(packet,source,lead,receipt):
    status='full_battle_review_complete'
    assert receipt['identity_match'] and receipt['sha256_before']==receipt['sha256_after']==source['sha256']
    archived=ROOT/'Reviewed'/source['video_basename']
    assert archived.is_file() and archived.stat().st_size==source['bytes']==receipt['bytes']
    history=packet/'worker_submission'; history.mkdir(exist_ok=True)
    for filename in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
        if not (history/filename).exists():shutil.copyfile(packet/filename,history/filename)
    external=packet/'EXTERNAL_LOG_RECEIPT.json'
    external_saved=external.exists() and read(external).get('verified_after_reload') is True
    for filename in ['SUMMARY.json','UNCERTAINTIES.json']:
        path=packet/filename; data=read(path)
        data.setdefault('worker_status_at_submission',data.get('review_status',data.get('status','complete_first_pass')))
        data.update({'status':status,'review_status':status,'current_status':status,'lead_acceptance':'accepted','source_archived':True,'source_modified':False,'global_registration_complete':True,'ranked_ladder_eligible':False,'requested_log':DESTINATION,'external_log_saved':external_saved,'archive_receipt':f"MOVE_RECEIPT.{source['video_basename']}.json",'archive_completion_event_id':receipt['review_event_id']})
        save(path,data)
    stamp='**Current status: full battle independently accepted, registered and archived unchanged. Competitive result destination: Pause Games.**'
    for filename in ['REVIEW.md','COVERAGE.md']:
        path=packet/filename; prose=path.read_text(encoding='utf-8-sig')
        prose=prose.replace('This is a first-pass draft awaiting independent lead acceptance.','The complete first pass has been independently accepted by the lead; registration and unchanged archival are complete.')
        prose=prose.replace('pending independent lead acceptance','independently lead-accepted, registered and archived')
        if stamp not in prose:
            title,rest=prose.split('\n',1);prose=title+'\n\n'+stamp+'\n'+rest
        path.write_text(prose,encoding='utf-8')
    assert not list(packet.rglob('*.MP4'))
    subprocess.run(['attrib','+P','-U',str(packet/'*'),'/S','/D'],check=True,capture_output=True,text=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('video',choices=SELECTED);parser.add_argument('--validate-only',action='store_true');args=parser.parse_args()
    packet,source,assignment,lead=validate(args.video)
    if args.validate_only:
        print('Accepted packet references valid: '+args.video);return
    receipt_path=packet/f'MOVE_RECEIPT.{args.video}.json'
    if not receipt_path.exists():
        command=[sys.executable,str(ROOT/'Review_Log'/'review_log.py'),'--root',str(ROOT),'record','--video',args.video,'--reviewer',assignment['reviewer'],'--status','full_battle_review_complete','--scope',lead['scope'],'--notes','Complete fresh Sol high first pass, independently source-checked and accepted. Owner requests competitive result in Pause Games, '+DESTINATION+'. Exact mode label and hidden cards remain qualified; ranked Ladder Log excluded.']
        for filename in ['REVIEW.md','COVERAGE.md','LEAD_ACCEPTANCE.json']:
            command+=['--evidence',str(packet/filename)]
        subprocess.run(command,check=True)
        shell=shutil.which('pwsh');assert shell
        subprocess.run([shell,'-NoProfile','-File',str(ROOT/'Recording_QA'/'finalize_accepted_review.ps1'),'-Video',args.video,'-Packet',str(packet.relative_to(ROOT))],check=True)
    refresh(packet,source,lead,read(receipt_path))
    print('Review and archive complete: '+args.video,flush=True)

if __name__=='__main__':main()
