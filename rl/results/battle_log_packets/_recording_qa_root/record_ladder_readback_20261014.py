"""Record exact six-row live readback without touching source media."""
import argparse, hashlib, json, re, shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATE = ROOT / 'Recording_QA/BATCH_2026-10-14_LATE_LADDER_TWO'
EVENING = ROOT / 'Recording_QA/BATCH_2026-10-14_EVENING_LADDER'
NEWER = ROOT / 'Recording_QA/BATCH_2026-10-14_NEWER_LADDER_FOUR'
parser = argparse.ArgumentParser()
parser.add_argument('--newer-four', action='store_true')
args = parser.parse_args()
target = NEWER if args.newer_four else LATE
raw_path = target / 'LADDER_RELOAD_AX.txt'
raw = raw_path.read_text(encoding='utf-8')
assert 'Saved games loaded.' in raw
now = datetime.now(timezone.utc).isoformat()
names = ['20261014_214436000_iOS', '20261014_215114000_iOS', '20261014_225451000_iOS', '20261014_225802000_iOS', '20261014_230328000_iOS', '20261014_231006000_iOS']
if args.newer_four:
    names = ['20261014_232438000_iOS', '20261014_233402000_iOS', '20261014_234511000_iOS', '20261014_234728000_iOS']
packets = {stem: (NEWER if args.newer_four else EVENING if stem in names[:4] else LATE) / stem for stem in names}
entries = {stem: json.loads((packet / 'LADDER_ENTRY.json').read_text(encoding='utf-8-sig')) for stem, packet in packets.items()}
new_wins = sum(entry['result'] == 'win' for entry in entries.values())
new_losses = len(entries) - new_wins
baseline = {'wins': 5, 'losses': 11, 'games': 16} if args.newer_four else {'wins': 2, 'losses': 8, 'games': 10}
totals = {'wins': baseline['wins'] + new_wins, 'losses': baseline['losses'] + new_losses, 'games': baseline['games'] + len(entries)}
deck = {'wins': (3 if args.newer_four else 0) + new_wins, 'losses': (3 if args.newer_four else 0) + new_losses, 'games': (6 if args.newer_four else 0) + len(entries)}
assert all(entry['section'] == 'd13' for entry in entries.values()), 'Review deck routing before using these totals'
assert f"DECK 13 A. Ninetales / Raticate Water {deck['wins']}–{deck['losses']}" in raw
assert re.search(r'text All decks\s+\d+ cell\s+\d+ text ' + str(totals['wins']) + r'\s+\d+ cell\s+\d+ text ' + str(totals['losses']) + r'\s+\d+ cell\s+\d+ text ' + str(totals['games']), raw)
lines = raw.splitlines()
rows = []
baseline_notes = []
if args.newer_four:
    before_raw = (target / 'LADDER_BEFORE_AX.txt').read_text(encoding='utf-8')
    baseline_notes = [re.sub(r'^\s*\d+ text ', '', line) for line in before_raw.splitlines() if re.match(r'^\s*\d+ text .*20261014_\d+_iOS\.MP4', line)]
    assert len(baseline_notes) == 6
    assert all(raw.count(note) == 1 for note in baseline_notes), 'An existing source note changed or duplicated'
for stem in names:
    packet = packets[stem]
    entry = entries[stem]
    assert raw.count(entry['source_filename']) == 1, stem
    matches = [i for i, line in enumerate(lines) if line.strip().endswith('text ' + entry['note'])]
    assert len(matches) == 1, stem
    i = matches[0]
    start = max(j for j in range(i) if re.fullmatch(r'\s*\d+ row', lines[j]))
    end = next((j for j in range(i + 1, len(lines)) if re.fullmatch(r'\s*\d+ row', lines[j])), len(lines))
    values = [re.sub(r'^\s*\d+ text ', '', line) for line in lines[start:end] if re.match(r'^\s*\d+ text ', line)]
    assert values[0] == ('W' if entry['result'] == 'win' else 'L'), (stem, values)
    assert values[1] == entry['opponent_deck'] and values[2] == entry['note'], (stem, values)
    receipt = {'saved': True, 'fresh_reload_verified': True, 'checked_utc': now, 'source_filename': entry['source_filename'], 'source_sha256': entry['source_sha256'], 'artifact': entry['artifact'], 'source_occurrences_after_reload': 1, 'rendered_result': values[0], 'rendered_opponent_deck': values[1], 'rendered_note': values[2], 'rendered_log_time': values[3], 'raw_readback': str(raw_path), 'readback_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(), 'live_totals': totals, 'deck13_totals': deck}
    status = packet / 'EXTERNAL_SAVE_STATUS.json'
    if status.exists():
        backup = packet / 'EXTERNAL_SAVE_STATUS.before_live_recovery.json'
        if not backup.exists(): shutil.copy2(status, backup)
    status.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (packet / 'LADDER_READBACK.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows.append(receipt)
verification = {'checked_utc': now, 'artifact': rows[0]['artifact'], 'fresh_reload_verified': True, 'all_exact_rows_verified': True, 'verified_entry_count': len(rows), 'prior_source_notes_preserved_exactly_once': len(baseline_notes), 'baseline_totals': baseline, 'verified_totals': totals, 'deck13_totals': deck, 'rows': rows, 'proof_image': str(target / 'LADDER_SAVED_PROOF.png')}
for batch in [NEWER] if args.newer_four else [LATE, EVENING]:
    (batch / 'LIVE_SAVE_VERIFICATION.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'verified_saved_entries': len(rows), **totals}))
