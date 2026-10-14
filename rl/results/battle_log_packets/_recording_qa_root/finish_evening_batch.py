"""Publish final entry points from accepted packets and current metadata."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from free_reviewed_video_space import metadata
from evening_batch_status import main as reconcile
from refresh_accepted_packet import refresh_accepted_packet

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA/BATCH_2026-09-30_EVENING'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
intake = read(batch / 'INTAKE.json')
for item in intake['sources']:
    video = item['video']
    packet = root / 'Recording_QA' / (Path(video).stem + '_auto_sol')
    assert (packet / f'MOVE_RECEIPT.{video}.json').is_file(), f'Not archived: {video}'
    refresh_accepted_packet(packet)
reconcile()
results = read(batch / 'RESULTS.json')
assert results['completed'] == results['expected'] == 11
storage_entries = []
for item in intake['sources']:
    state = metadata(root / 'Reviewed' / item['video'])
    assert state['logical_bytes'] == item['bytes']
    storage_entries.append({'video':item['video'], **state})
online = sum(e['online_only'] for e in storage_entries)
allocated = sum(e['allocated_bytes'] for e in storage_entries)
storage = {'checked_at_utc':datetime.now(timezone.utc).isoformat(),'videos':11,'online_only':online,'still_local':11-online,'allocated_bytes':allocated,'logical_bytes':sum(e['logical_bytes'] for e in storage_entries),'files_deleted':0,'verification':'Metadata only; no archived original contents read','entries':storage_entries}
(batch / 'STORAGE_STATUS.json').write_text(json.dumps(storage,indent=2)+'\n',encoding='utf-8')
storage_text = f'{online} of 11 evening originals are confirmed online-only; {11-online} still retain local data ({allocated/1e9:.2f} GB). ' + ('OneDrive sync or space release remains pending for those files. Originals are retained.' if online < 11 else 'All filenames and logical sizes are unchanged. No original was deleted.')
report = root / 'BATTLE_TRANSCRIPTS_2026-09-30_EVENING.md'
text = report.read_text(encoding='utf-8')
text += '\n## Current original storage\n\n' + storage_text + '\n\nEvidence: [current storage metadata](Recording_QA/BATCH_2026-09-30_EVENING/STORAGE_STATUS.json). Written reviews and retained frames remain available locally.\n'
report.write_text(text,encoding='utf-8')
rows = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows) == 109 and sum(r['Status']=='Reviewed' for r in rows) == 102
entry = root / 'READ_ME_REVIEW_STATUS.md'
old = entry.read_text(encoding='utf-8-sig')
paragraph = f"Updated after the September 30 evening batch. All eleven additional Auto AI recordings are fully reviewed by separate fresh Sol workers, independently checked and accepted by the lead, then registered and archived with matching source hashes. Practice results: {results['practice_wins']} wins and {results['practice_losses']} losses. These games are excluded from Ladder Log. See the [evening review summary](BATTLE_TRANSCRIPTS_2026-09-30_EVENING.md) for full review links, useful observations and documented Auto-off intervals. {storage_text}\n\n"
if 'Updated after the September 30 evening batch.' in old:
    title, rest = old.split('\n\n',1)
    _, rest = rest.split('\n\n',1)
    old = title + '\n\n' + rest
old = old.replace('contains 98 videos: 83 accepted full-battle reviews and eight completed rule tests', 'contains 109 videos: 94 accepted full-battle reviews and eight completed rule tests')
old = old.replace('Updated 2026-09-30. All fifteen September 30 uploads', 'Earlier September 30 batch: all fifteen uploads')
title, rest = old.split('\n\n',1)
entry.write_text(title+'\n\n'+paragraph+rest,encoding='utf-8')
print(json.dumps({'completed':11,'wins':results['practice_wins'],'losses':results['practice_losses'],'index_entries':len(rows),'archived':102,'storage_online_only':online,'storage_pending':11-online}))
