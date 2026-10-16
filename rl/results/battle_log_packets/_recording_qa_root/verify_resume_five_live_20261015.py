"""Check exact accepted rows against one fresh live Ladder Log reload."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/RESUME_2026-10-15_FIVE'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def texts(lines):
    return [re.sub(r'^\s*\d+ text ', '', line) for line in lines if re.match(r'^\s*\d+ text ', line)]

def totals(raw, label):
    values = texts(raw.split('container decks')[0].splitlines())
    i = values.index(label)
    return dict(zip(['wins', 'losses', 'games'], map(int, values[i + 1:i + 4])))

parser = argparse.ArgumentParser()
parser.add_argument('videos', nargs='+')
parser.add_argument('--tag', required=True)
args = parser.parse_args()
context = load(BATCH / 'OWNER_CONTEXT.json')
assert set(args.videos).issubset(context['selected_sources']) and len(set(args.videos)) == len(args.videos)
before = (BATCH / 'LADDER_BEFORE_EXPANDED_AX.txt').read_text(encoding='utf-8')
raw_path = BATCH / ('LADDER_RELOAD.' + args.tag + '.txt')
raw = raw_path.read_text(encoding='utf-8')
assert 'Saved games loaded.' in before and 'Saved games loaded.' in raw
baseline = totals(before, 'All decks')
assert baseline == {'wins': 12, 'losses': 17, 'games': 29}
entries = []
for name in args.videos:
    packet = Path(context['packets'][name])
    entry = load(packet / 'LADDER_ENTRY.json')
    assert load(packet / 'LEAD_ACCEPTANCE.json')['accepted']
    assert load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
    assert entry['source_filename'] == name and entry['section'] == 'd01'
    entries.append((packet, entry))
wins = sum(e['result'] == 'win' for _, e in entries)
losses = len(entries) - wins
changes = {'wins': wins, 'losses': losses, 'games': len(entries)}
expected = {k: baseline[k] + changes[k] for k in baseline}
assert totals(raw, 'All decks') == expected
deck_baseline = totals(before, 'Muk / Glimmora / Kingambit / Regigigas')
deck_expected = {k: deck_baseline[k] + changes[k] for k in changes}
assert totals(raw, 'Muk / Glimmora / Kingambit / Regigigas') == deck_expected
for label in ['Ariados / Whimsicott / Ogerpon', 'A. Ninetales / Raticate']:
    assert totals(raw, label) == totals(before, label)
prior = [v for v in texts(before.splitlines()) if re.search(r'\d{8}_\d+_iOS\.MP4', v)]
assert len(prior) == 29 and all(raw.count(v) == 1 for v in prior)
lines = raw.splitlines()
receipts = []
for packet, entry in entries:
    assert raw.count(entry['source_filename']) == 1
    matches = [i for i, line in enumerate(lines) if line.strip().endswith('text ' + entry['note'])]
    assert len(matches) == 1
    i = matches[0]
    start = max(j for j in range(i) if re.fullmatch(r'\s*\d+ row', lines[j]))
    end = next((j for j in range(i + 1, len(lines)) if re.fullmatch(r'\s*\d+ row', lines[j])), len(lines))
    values = texts(lines[start:end])
    assert values[:3] == ['W' if entry['result'] == 'win' else 'L', entry['opponent_deck'], entry['note']]
    receipt = {'saved': True, 'fresh_reload_verified': True, 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'source_filename': entry['source_filename'], 'source_sha256': entry['source_sha256'], 'artifact': entry['artifact'],
        'source_occurrences_after_reload': 1, 'rendered_result': values[0], 'rendered_opponent_deck': values[1],
        'rendered_note': values[2], 'rendered_log_time': values[3], 'raw_readback': str(raw_path),
        'readback_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(), 'live_totals': expected}
    for name in ['EXTERNAL_SAVE_STATUS.json', 'LADDER_READBACK.json']:
        target = packet / name
        if target.exists():
            old = load(target)
            assert old['saved'] and old['source_sha256'] == receipt['source_sha256']
            save(packet / (target.stem + '.' + args.tag + '.json'), receipt)
        else:
            save(target, receipt)
    receipts.append(receipt)
save(BATCH / ('LIVE_SAVE_VERIFICATION.' + args.tag + '.json'), {'checked_utc': datetime.now(timezone.utc).isoformat(),
    'fresh_reload_verified': True, 'all_exact_rows_verified': True, 'verified_entry_count': len(entries),
    'prior_source_notes_preserved_exactly_once': len(prior), 'baseline_totals': baseline,
    'verified_totals': expected, 'deck01_totals': deck_expected, 'rows': receipts,
    'proof_image': str(BATCH / ('LADDER_SAVED_PROOF.' + args.tag + '.png'))})
print(json.dumps({'verified_new_entries': len(entries), 'preserved_prior_entries': len(prior), **expected}))
