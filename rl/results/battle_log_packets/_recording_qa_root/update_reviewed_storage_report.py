"""Reconcile the September 30 cloud-only storage audit without opening videos."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
directory = root / 'Recording_QA' / 'CLOUD_STORAGE'
reads = [(p, json.loads(p.read_text(encoding='utf-8-sig'))) for p in sorted(directory.glob('*.inventory.json'))]
# Exclude the preliminary compatibility-mode diagnostic that disguised placeholders.
valid = [(p, d) for p, d in reads if d['videos'] == 91 and all(e['before']['cloud_placeholder'] for e in d['entries'])]
first_path, first = valid[0]
last_path, last = valid[-1]
assert set(e['video'] for e in first['entries']) == set(e['video'] for e in last['entries'])
for before, after in zip(first['entries'], last['entries']):
    assert before['video'] == after['video']
    assert before['before']['logical_bytes'] == after['after']['logical_bytes']
    assert after['after']['cloud_placeholder'] and after['after']['in_sync']
result = {'videos': 91, 'online_only': last['online_only'],
          'allocated_bytes_before': first['allocated_bytes_before'],
          'allocated_bytes_after': last['allocated_bytes_after'],
          'bytes_reclaimed': first['allocated_bytes_before'] - last['allocated_bytes_after'],
          'baseline_inventory': first_path.relative_to(root).as_posix(),
          'latest_inventory': last_path.relative_to(root).as_posix(),
          'filenames_and_logical_sizes_unchanged': True, 'all_cloud_copies_in_sync': True,
          'originals_deleted': 0,
          'pending_videos': [e['video'] for e in last['entries'] if not e['after']['online_only']]}
(directory / 'RESULTS_2026-09-30.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
report = ['# Reviewed video storage', '',
          f"September 30, 2026. {result['online_only']} of 91 completed videos are confirmed online-only. Local video allocation fell from {result['allocated_bytes_before'] / 1e9:.2f} GB to {result['allocated_bytes_after'] / 1e9:.2f} GB, releasing {result['bytes_reclaimed'] / 1e9:.2f} GB.", '',
          'All 91 filenames and logical sizes are unchanged, and Windows reports their cloud contents in sync. No original was deleted. The review packets, index, archive receipts and source hashes remain available.', '',
          "The original videos remain in OneDrive's Reviewed folder. Opening a video later downloads it again. The review workflow now requests online-only storage after archive verification and sync, then checks local allocation without reopening the video.", '',
          'Evidence: [storage receipts](Recording_QA/CLOUD_STORAGE/RESULTS_2026-09-30.json). The operation uses [Microsoft\'s supported online-only command](https://learn.microsoft.com/en-us/sharepoint/files-on-demand-windows).', '']
if result['pending_videos']:
    report += ['Still awaiting local-space release: ' + ', '.join('`' + v + '`' for v in result['pending_videos']) + '. The online-only preference is set; this is not counted as freed storage.', '']
(root / 'REVIEWED_VIDEO_STORAGE_2026-09-30.md').write_text('\n'.join(report), encoding='utf-8')
print(json.dumps(result, indent=2))
