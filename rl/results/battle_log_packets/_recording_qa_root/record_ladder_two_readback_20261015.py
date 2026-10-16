"""Verify exact accepted entries and preservation against a fresh live UI reload."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_LADDER_TWO'
NAMES = ['20261015_201201000_iOS.MP4', '20261015_201850000_iOS.MP4']

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def text_values(lines):
    return [re.sub(r'^\s*\d+ text ', '', line) for line in lines if re.match(r'^\s*\d+ text ', line)]

def totals(raw, label):
    values = text_values(raw.split('container decks')[0].splitlines())
    i = values.index(label)
    return dict(zip(['wins', 'losses', 'games'], map(int, values[i + 1:i + 4])))

before = (BATCH / 'LADDER_BEFORE_EXPANDED_AX.txt').read_text(encoding='utf-8')
path = BATCH / 'LADDER_RELOAD_AX.txt'
raw = path.read_text(encoding='utf-8')
assert 'Saved games loaded.' in before and 'Saved games loaded.' in raw
baseline = totals(before, 'All decks')
assert baseline == {'wins': 8, 'losses': 16, 'games': 24}
entries = [(BATCH / Path(name).stem, load(BATCH / Path(name).stem / 'LADDER_ENTRY.json')) for name in NAMES]
assert all(entry['section'] == 'd01' for _, entry in entries)
wins = sum(entry['result'] == 'win' for _, entry in entries)
losses = len(entries) - wins
expected = {key: baseline[key] + value for key, value in [('wins', wins), ('losses', losses), ('games', len(entries))]}
assert totals(raw, 'All decks') == expected
assert totals(raw, 'Muk / Glimmora / Kingambit / Regigigas') == {'wins': wins, 'losses': losses, 'games': len(entries)}
for label in ['Ariados / Whimsicott / Ogerpon', 'A. Ninetales / Raticate']:
    assert totals(raw, label) == totals(before, label)
prior = [value for value in text_values(before.splitlines()) if re.search(r'\d{8}_\d+_iOS\.MP4', value)]
assert len(prior) == 24 and all(raw.count(value) == 1 for value in prior)
now = datetime.now(timezone.utc).isoformat()
lines = raw.splitlines()
receipts = []
for packet, entry in entries:
    assert load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
    assert raw.count(entry['source_filename']) == 1
    matches = [i for i, line in enumerate(lines) if line.strip().endswith('text ' + entry['note'])]
    assert len(matches) == 1
    i = matches[0]
    start = max(j for j in range(i) if re.fullmatch(r'\s*\d+ row', lines[j]))
    end = next((j for j in range(i + 1, len(lines)) if re.fullmatch(r'\s*\d+ row', lines[j])), len(lines))
    values = text_values(lines[start:end])
    assert values[:3] == ['W' if entry['result'] == 'win' else 'L', entry['opponent_deck'], entry['note']]
    receipt = {'saved': True, 'fresh_reload_verified': True, 'checked_utc': now,
        'source_filename': entry['source_filename'], 'source_sha256': entry['source_sha256'],
        'artifact': entry['artifact'], 'source_occurrences_after_reload': 1, 'rendered_result': values[0],
        'rendered_opponent_deck': values[1], 'rendered_note': values[2], 'rendered_log_time': values[3],
        'raw_readback': str(path), 'readback_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'live_totals': expected}
    save(packet / 'EXTERNAL_SAVE_STATUS.json', receipt)
    save(packet / 'LADDER_READBACK.json', receipt)
    receipts.append(receipt)
save(BATCH / 'LIVE_SAVE_VERIFICATION.json', {'checked_utc': now, 'fresh_reload_verified': True,
    'all_exact_rows_verified': True, 'verified_entry_count': len(receipts), 'prior_source_notes_preserved_exactly_once': len(prior),
    'baseline_totals': baseline, 'verified_totals': expected, 'deck01_totals': {'wins': wins, 'losses': losses, 'games': len(entries)},
    'rows': receipts, 'proof_image': str(BATCH / 'LADDER_SAVED_PROOF.png')})
print(json.dumps({'verified_saved_entries': len(receipts), 'preserved_prior_entries': len(prior), **expected}))
