"""Preserve completed work and exact unreadable-source limits without media reads."""
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / 'Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR'
DEST = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / B.name
names = json.loads((B/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

rows = list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
location_map = load(ROOT/'MEDIA_LOCATIONS.json')
live = load(B/'LIVE_SAVE_VERIFICATION.json')
assert live['verified_after_reload'] and live['previous_rows_preserved'] and live['first_note_verified']
assert live['source_row_counts'] == {names[0]:1, **{name:0 for name in names[1:]}}
result = {'checked_utc':datetime.now(timezone.utc).isoformat(), 'requested_games':4,
          'all_requested_work_complete':False, 'media_contents_read':False,
          'artifact':'https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1',
          'live_verified_current_season':{'wins':1,'losses':0,'games':1},
          'historical_season_unchanged':{'wins':27,'losses':29,'games':56}, 'sources':[]}
for name in names:
    packet=B/Path(name).stem
    archived=ROOT/'Reviewed'/name
    current=archived if archived.exists() else ROOT/name
    entry={'source':name,'current_path':str(current),'cloud_metadata':metadata(current),'source_contents_read':False}
    if (packet/'LEAD_ACCEPTANCE.json').exists():
        source=load(packet/'SOURCE.json')
        lead=load(packet/'LEAD_ACCEPTANCE.json')
        move=load(packet/('MOVE_RECEIPT.'+name+'.json'))
        readback=load(packet/'LADDER_READBACK.json')
        assert lead['accepted'] and move['identity_match'] and readback['verified_after_reload']
        assert move['sha256_before']==move['sha256_after']==lead['source_sha256']==source['sha256']
        matches=[r for r in rows if r['Video']==name]
        assert len(matches)==1 and matches[0]['Status']=='Reviewed' and matches[0]['Location']=='Reviewed/'+name
        mapped=[r for r in location_map['moved'] if r['filename']==name]
        assert len(mapped)==1 and mapped[0]['sha256']==source['sha256'] and Path(mapped[0]['current_path'])==archived
        assert len(readback['rows'])==1 and name in readback['rows'][0]
        entry.update(review_complete=True,independently_accepted=True,registered=True,archived=True,
                     external_saved=True,fresh_reload_verified=True,source_sha256=source['sha256'],
                     result='win',section='Deck 12',note_prefix='1st | Whimsicott ex T4 | opp 0 pts',
                     storage_complete=entry['cloud_metadata']['in_sync'] and entry['cloud_metadata']['online_only'] and entry['cloud_metadata']['allocated_bytes']==0)
        save(packet/'EXTERNAL_SAVE_STATUS.json', {'source_filename':name,'source_sha256':source['sha256'],
            'external_saved':True,'fresh_reload_verified':True,'artifact':result['artifact'],
            'readback':'LADDER_READBACK.json','checked_utc':result['checked_utc']})
    else:
        entry.update(review_complete=False,registered=False,archived=False,external_saved=False,
                     source_sha256=None,
                     remaining='Stable complete local read, SHA256/duration binding, full review, independent acceptance, logging/readback and archival',
                     blocker='OneDrive source contents are not readable. Second/third hydration timed out; second/fourth bounded 32-byte reads timed out. A filesystem filename/size is not actual source availability.')
    result['sources'].append(entry)
result['reviewed_games']=sum(e['review_complete'] for e in result['sources'])
result['saved_games']=sum(e['external_saved'] for e in result['sources'])
result['remaining_games']=4-result['saved_games']
save(B/'BATCH_STATUS.json',result)
text='''# October 14 new ladder games

One of four new games is completely reviewed, independently checked, registered, archived, saved in the existing Ladder Log and verified after reload.

20261014_142546000_iOS.MP4: Deck 12, win3-0 versus まいちゃん. Note begins `1st | Whimsicott ex T4 | opp 0 pts`. Match began09:25:46 CDT; source-local Victory04:59.8. Current-season totals1win,0losses,1game. Previous-season56games (27wins,29losses) preserved.

The other three sources remain in the main folder. Their filenames and logical sizes exist, but OneDrive has not supplied readable bytes. No identities, deck sections, turn/order facts or outcomes have been guessed for them, and no external entries were created. Continue from these packets after source availability recovers; do not repeat the accepted first review or add its game twice.

See BATCH_STATUS.json for exact source paths, cloud metadata, outstanding work and archive/readback reconciliation. REVIEW_ASSIGNMENT.md preserves the review and logging contract. The accepted packet's LEAD_CLARIFICATION.md corrects a nonmaterial primary timeline clock typo without altering its frozen source evidence. OneDrive Free up space was requested for the accepted archived original; metadata, not a media reread, determines whether release has completed.

Written reports, retained evidence and receipts are mirrored to Pocket Deck Lab/Boss Folder/BATCH_2026-10-14_NEW_LADDER_FOUR. MIRROR_RECEIPT.json verifies their hashes. No original video is copied to that mirror or deleted.
'''
(B/'README.md').write_text(text,encoding='utf-8')
DEST.mkdir(exist_ok=True)
files=[]
for src in sorted(B.rglob('*')):
    if not src.is_file() or '__pycache__' in src.parts or src.name=='MIRROR_RECEIPT.json':
        continue
    assert src.suffix.lower() not in ['.mp4','.mov','.mkv','.avi','.m4v']
    rel=src.relative_to(B)
    dst=DEST/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    source_hash=sha(src)
    if not dst.exists() or sha(dst)!=source_hash:
        shutil.copy2(src,dst)
    assert sha(dst)==source_hash
    files.append({'path':rel.as_posix(),'bytes':src.stat().st_size,'sha256':source_hash})
receipt={'created_utc':datetime.now(timezone.utc).isoformat(),'source':str(B),'destination':str(DEST),
         'videos_copied':0,'file_count':len(files),'files':files,'all_copy_hashes_match':True}
save(B/'MIRROR_RECEIPT.json',receipt)
shutil.copy2(B/'MIRROR_RECEIPT.json',DEST/'MIRROR_RECEIPT.json')
assert sha(B/'MIRROR_RECEIPT.json')==sha(DEST/'MIRROR_RECEIPT.json')
print(json.dumps({k:result[k] for k in ['all_requested_work_complete','reviewed_games','saved_games','remaining_games']}),flush=True)
print(json.dumps({'mirror_files':len(files),'archive_and_index_map_match':True,'all_copy_hashes_match':True,'media_contents_read':False}),flush=True)
