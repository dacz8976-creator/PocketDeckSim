"""Reconcile accepted evening packets, archives, live receipts and local mirror."""
import argparse, csv, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--batch',choices=['BATCH_2026-10-14_EVENING_LADDER','BATCH_2026-10-14_LATE_LADDER_TWO','BATCH_2026-10-14_NEWER_LADDER_FOUR','BATCH_2026-10-14_NIGHT_LADDER_FOUR'],default='BATCH_2026-10-14_EVENING_LADDER')
p.add_argument('--allow-pending',action='store_true',help='Record a truthful checkpoint for sources still awaiting readable media or review')
a=p.parse_args()
BATCH=ROOT/'Recording_QA'/a.batch
BOSS=Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder')/BATCH.name
NAMES=['20261014_214436000_iOS.MP4','20261014_215114000_iOS.MP4','20261014_225451000_iOS.MP4','20261014_225802000_iOS.MP4']
if a.batch=='BATCH_2026-10-14_LATE_LADDER_TWO':NAMES=['20261014_230328000_iOS.MP4','20261014_231006000_iOS.MP4']
if a.batch=='BATCH_2026-10-14_NEWER_LADDER_FOUR':NAMES=['20261014_232438000_iOS.MP4','20261014_233402000_iOS.MP4','20261014_234511000_iOS.MP4','20261014_234728000_iOS.MP4']
if a.batch=='BATCH_2026-10-14_NIGHT_LADDER_FOUR':NAMES=['20261015_015320000_iOS.MP4','20261015_020931000_iOS.MP4','20261015_021533000_iOS.MP4','20261015_022206000_iOS.MP4']
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
    assert path.suffix.lower() not in ['.mp4','.mov','.mkv'],path
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
index=list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
baseline=load(BATCH/'UNRELATED_INDEX_BASELINE.json')
current={r['Video']:r for r in index}
assert all(current[r['Video']]==r for r in baseline),'Unrelated shared index change needs reconciliation'
locations=load(ROOT/'MEDIA_LOCATIONS.json')['moved']
rows=[]
unreviewed=[]
frozen_paths=set()
for name in NAMES:
    packet=BATCH/Path(name).stem
    if not (packet/'LEAD_ACCEPTANCE.json').exists():
        assert a.allow_pending, f'Review remains unfinished: {name}'
        unreviewed.append({'source':name,'review_complete':False,'availability':load(packet/'AVAILABILITY.json') if (packet/'AVAILABILITY.json').exists() else None,'cloud_metadata':metadata(ROOT/name) if (ROOT/name).exists() else None})
        continue
    source=load(packet/'SOURCE.json')
    acceptance=load(packet/'LEAD_ACCEPTANCE.json')
    checker=load(packet/'independent_sol/CHECK_RESULT.json')
    entry=load(packet/'LADDER_ENTRY.json')
    frozen=load(packet/'REVIEW_PACKET_HASHES.json')
    frozen_paths.update((packet/rel).resolve() for rel in frozen['files'])
    frozen_paths.add((packet/'REVIEW_PACKET_HASHES.json').resolve())
    if (packet/'SUPPLEMENT_HASHES.json').exists():
        supplement=load(packet/'SUPPLEMENT_HASHES.json')
        assert supplement['original_manifest_sha256']==sha(packet/'REVIEW_PACKET_HASHES.json')
        assert all(sha(packet/rel)==digest for rel,digest in supplement['files'].items())
        frozen_paths.update((packet/rel).resolve() for rel in supplement['files'])
        frozen_paths.add((packet/'SUPPLEMENT_HASHES.json').resolve())
    assert acceptance['accepted'] and checker['accepted']
    assert all(sha(packet/rel)==digest for rel,digest in frozen['files'].items())
    receipt=load(packet/('MOVE_RECEIPT.'+name+'.json'))
    assert receipt['identity_match'] and receipt['sha256_before']==receipt['sha256_after']==source['sha256']
    registration=load(packet/'REGISTRATION_RESULT.json')
    assert registration['exit_code']==0
    event=load(Path(registration['stdout'].strip()))
    assert event['status']=='full_battle_review_complete' and event['video_basename']==name
    assert event['video_sha256']==source['sha256'] and event['event_id']==receipt['review_event_id']
    archive=ROOT/'Reviewed'/name
    assert archive.exists() and archive.stat().st_size==source['bytes'] and not (ROOT/name).exists()
    assert current[name]['Status']=='Reviewed' and current[name]['Location'].replace('\\','/')=='Reviewed/'+name
    moved=next(m for m in locations if m['filename']==name)
    assert moved['sha256']==source['sha256'] and Path(moved['current_path']).resolve()==archive.resolve()
    storage=metadata(archive)
    external_path=packet/'EXTERNAL_SAVE_STATUS.json'
    external=load(external_path) if external_path.exists() else {}
    saved=external.get('saved') is True and external.get('fresh_reload_verified') is True
    if saved:assert external['source_filename']==name and external['source_sha256']==source['sha256']
    rows.append({'source':name,'source_sha256':source['sha256'],'review_complete':True,'independently_accepted':True,'registered':True,'archived':True,'current_path':str(archive),'result':entry['result'],'opponent':entry['opponent'],'section':entry['section'],'note_prefix':entry['note_prefix'],'external_saved':saved,'fresh_reload_verified':saved,'cloud_metadata':storage,'storage_complete':storage['in_sync'] and storage['online_only'] and storage['allocated_bytes']==0})
now=datetime.now(timezone.utc).isoformat()
pending=[r['source'] for r in rows if not r['external_saved']]
storage_pending=[r['source'] for r in rows if not r['storage_complete']]
blocker=load(BATCH/'BROWSER_BLOCKER.json') if (BATCH/'BROWSER_BLOCKER.json').exists() else {}
status={'checked_utc':now,'requested_games':len(NAMES),'reviewed_games':len(rows),'saved_games':len(rows)-len(pending),'review_and_archive_complete':not unreviewed,'review_and_ladder_logging_complete':not pending and not unreviewed,'remaining_reviews':unreviewed,'remaining_external_saves':pending,'external_blocker':blocker.get('latest_browser_response','Live access/save/readback remains pending; exact accepted entries retained in each LADDER_ENTRY.json') if pending else None,'storage_pending':storage_pending,'unrelated_index_rows_preserved':len(baseline),'source_rows':rows,'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1'}
save(BATCH/'BATCH_STATUS.json',status)
text=f'# October 14 ladder reviews\n\n{len(rows)} of {len(NAMES)} sources in this batch have complete source-bound reviews, separate independent checks, lead acceptance, immutable completion events, and verified archive moves into Reviewed. Older sources were not reopened.\n\n'
for r in rows:text+=f"- `{r['source']}`: {r['result']} versus {r['opponent']}; {r['note_prefix']}.\n"
if pending:text+='\nLive Ladder Log saving and reload verification remain pending. See BROWSER_BLOCKER.json and BATCH_STATUS.json for the recorded access limit. Each packet contains the exact source-bound ready entry in LADDER_ENTRY.json. Check all existing live entries by source filename before adding.\n'
elif rows:text+=f'\nAll {len(rows)} completed results are saved exactly once in the live Ladder Log and verified after reload. See LIVE_SAVE_VERIFICATION.json.\n'
if unreviewed:text+='\nReview remains pending for: '+', '.join(r['source'] for r in unreviewed)+'. See BATCH_STATUS.json and per-source availability receipts. No outcome is claimed for unreadable media.\n'
if storage_pending:text+='\nOneDrive cache release remains pending for: '+', '.join(storage_pending)+'. Sources remain preserved.\n'
elif rows:text+=f'\nAll {len(rows)} archived originals are in-sync and online-only with zero allocated disk bytes. Reports and retained evidence remain local.\n'
text+='\nThe frozen SOURCE.json keeps the original review-time path. MEDIA_LOCATIONS.json and MOVE_RECEIPT files resolve the current archive location. Hidden cards and source limitations remain explicit in each review. This batch does not use the Pause Games supplement.\n'
(BATCH/'README.md').write_text(text,encoding='utf-8')
BOSS.mkdir(parents=True,exist_ok=True)
copied=[]
for path in sorted(BATCH.rglob('*')):
    if not path.is_file() or path.name=='MIRROR_RECEIPT.json':continue
    assert path.suffix.lower() not in ['.mp4','.mov','.mkv'],path
    rel=path.relative_to(BATCH)
    dest=BOSS/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    digest=sha(path)
    if dest.exists() and sha(dest)!=digest:
        assert path.resolve() not in frozen_paths, f'Frozen mirror conflict: {dest}'
        backup=dest.with_name(dest.stem+'.before_'+datetime.now(timezone.utc).strftime('%H%M%S')+dest.suffix)
        shutil.copy2(dest,backup)
    if not dest.exists() or sha(dest)!=digest:shutil.copy2(path,dest)
    assert sha(dest)==digest
    copied.append({'path':rel.as_posix(),'bytes':path.stat().st_size,'sha256':digest})
mirror={'created_utc':now,'source':str(BATCH),'destination':str(BOSS),'file_count':len(copied),'all_hashes_verified':True,'videos_copied':0,'files':copied}
save(BATCH/'MIRROR_RECEIPT.json',mirror)
shutil.copy2(BATCH/'MIRROR_RECEIPT.json',BOSS/'MIRROR_RECEIPT.json')
assert sha(BATCH/'MIRROR_RECEIPT.json')==sha(BOSS/'MIRROR_RECEIPT.json')
print(json.dumps({'reviewed_archived':len(rows),'saved':len(rows)-len(pending),'review_pending':[r['source'] for r in unreviewed],'external_pending':pending,'storage_pending':storage_pending,'mirrored_files':len(copied)},ensure_ascii=False),flush=True)
