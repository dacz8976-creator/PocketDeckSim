"""Bound this explicitly requested four-source batch and claim reviews serially."""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OLDER_FOUR'
PROBE = Path('C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe')
SELECTED = ['20261002_011527000_iOS.MP4', '20261002_012229000_iOS.MP4',
            '20260926_211809000_iOS.MP4', '20260926_212155000_iOS.MP4']
OLD = ['Recording_QA/20261002_011527000_iOS_competitive_sol',
       'Recording_QA/20261002_012229000_iOS_competitive_sol',
       'Recording_QA/20260926_new_clips_sol_review/XaBy8_211809',
       'Recording_QA/20260926_new_clips_sol_review/StefaGo_212155']

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

BATCH.mkdir(exist_ok=True)
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
if not (BATCH / 'INDEX_BEFORE.json').exists():
    save(BATCH / 'INDEX_BEFORE.json', rows)
owner_context = {'requested_utc': datetime.now(timezone.utc).isoformat(),
      'owner_request': 'Can we finish processing the 4 older files now?', 'selected_sources': SELECTED,
      'scope': 'Exactly these four older sources. Continue the approved compact Sol/high workflow, use existing evidence, independent checks, lead registration and safe archival where the full battle is covered. No other backlog.',
      'routing': 'Any visible Auto control, even OFF, means computer and excludes both external human logs. Otherwise follow existing Ladder Log default; do not add an uncertain result.',
      'recording_gaps': 'Do not invent missing turns, link different opponents, or claim a cut recording as a whole completed battle.',
      'shared_writes': 'Root alone writes index/events, external entries, moves, media map and Boss mirror.'}
if not (BATCH / 'OWNER_CONTEXT.json').exists():
    save(BATCH / 'OWNER_CONTEXT.json', owner_context)
else:
    assert json.loads((BATCH / 'OWNER_CONTEXT.json').read_text(encoding='utf-8-sig'))['selected_sources'] == SELECTED
sources = []
for name, previous in zip(SELECTED, OLD):
    path = ROOT / name
    before = path.stat()
    assert path.is_file() and not (ROOT / 'Reviewed' / name).exists()
    p = BATCH / path.stem
    if (p / 'SOURCE.json').exists() and (p / 'ASSIGNMENT.json').exists():
        bound = json.loads((p / 'SOURCE.json').read_text(encoding='utf-8-sig'))
        assignment = json.loads((p / 'ASSIGNMENT.json').read_text(encoding='utf-8-sig'))
        assert before.st_size == bound['bytes']
        sources.append({'source': name, 'sha256': bound['sha256'], 'bytes': bound['bytes'],
                        'duration_seconds': bound['duration_seconds'], 'creation_utc': bound['source_creation_utc'],
                        'packet': str(p), 'previous_packet': previous, 'reviewer': assignment['reviewer']})
        continue
    prior = next((r for r in rows if r['Video'] == name), None)
    assert prior is None or prior['Status'] != 'Reviewed'
    p.mkdir(exist_ok=True)
    metadata = subprocess.run([str(PROBE), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    probe = json.loads(metadata.stdout)
    save(p / 'PROBE.json', probe)
    worker = '/root/older_' + name[9:15]
    registered = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'Review_Log/review_log.py'), 'record',
          '--video', name, '--reviewer', worker, '--status', 'in_progress',
          '--scope', 'Owner-requested continuation: review the entire available source and identify actual full-battle coverage, recording gaps, mode and outcome; reuse prior packet.',
          '--notes', 'New explicit owner request October 14. Prior source-specific partial/intake evidence is preserved.'], capture_output=True, text=True, encoding='utf-8')
    save(p / 'ASSIGNMENT_REGISTRATION.json', {'exit_code': registered.returncode, 'stdout': registered.stdout, 'stderr': registered.stderr})
    assert registered.returncode == 0, registered.stderr
    event = json.loads(Path(registered.stdout.strip()).read_text(encoding='utf-8-sig'))
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    identity = {'video_basename': name, 'sha256': event['video_sha256'], 'bytes': after.st_size,
         'duration_seconds': float(probe['format']['duration']), 'streams': probe['streams'],
         'source_path_at_review': str(path), 'bound_utc': event['logged_at_utc'], 'identity_provenance': event['identity_provenance'],
         'previous_packet': str(ROOT / previous), 'previous_packet_preserved': True, 'recording_relationships': [],
         'source_creation_utc': probe['format'].get('tags', {}).get('creation_time'),
         'old_filename_date_is_not_review_date': True}
    old_source = ROOT / previous / 'SOURCE.json'
    if old_source.exists():
        old = json.loads(old_source.read_text(encoding='utf-8-sig'))
        old_hash = old.get('sha256', old.get('source_sha256'))
        if old_hash:
            identity['previous_sha256'] = old_hash
            identity['previous_identity_matches'] = old_hash.lower() == identity['sha256'].lower()
            assert identity['previous_identity_matches'], name
    save(p / 'SOURCE.json', identity)
    assignment = {'reviewer': worker, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
                  'source': name, 'source_sha256': identity['sha256'], 'entire_available_source': True,
                  'previous_packet': str(ROOT / previous), 'external_write_authority': False,
                  'shared_write_authority': False, 'output_packet': str(p), 'assignment_event': event['event_id'],
                  'capture_protocol_scope': 'Ordinary full-source review. Pause Games supplement only if owner routing establishes a new human Pause Game; do not retrofit the old computer or ladder clips.'}
    save(p / 'ASSIGNMENT.json', assignment)
    sources.append({'source': name, 'sha256': identity['sha256'], 'bytes': after.st_size,
                    'duration_seconds': identity['duration_seconds'], 'creation_utc': identity['source_creation_utc'],
                    'packet': str(p), 'previous_packet': previous, 'reviewer': worker})
    print(json.dumps(sources[-1]), flush=True)
save(BATCH / 'SOURCE_INVENTORY.json', sources)
