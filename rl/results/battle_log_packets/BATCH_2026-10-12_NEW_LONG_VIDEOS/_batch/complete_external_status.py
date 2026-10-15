"""Record fresh visible live readback without changing accepted review evidence."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil

batch = Path(__file__).resolve().parent
mirror = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\BATCH_2026-10-12_NEW_LONG_VIDEOS')
v = json.loads((batch / 'LIVE_SAVE_VERIFICATION.json').read_text(encoding='utf-8'))
assert v['external_saved'] and v['prior_39_games_unchanged'] and v['prior_25_decks_unchanged']
assert v['game_count'] == 43 and v['deck_count'] == 26
assert all(g['count'] == 1 for g in v['new_source_occurrences'])
assert not (batch / 'EXTERNAL_COMPLETION_RECEIPT.json').exists()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

files = [Path(__file__).name, 'LIVE_SAVE_VERIFICATION.json', 'LIVE_SAVE_SUMMARY.png', 'LIVE_DECK_SNAPSHOT.json']
changes = []
for name in ['README.md', 'BATCH_COMPLETION_CHECK.json', 'PAUSE_GAMES_BATCH_IMPORT.json']:
    p = batch / name
    history = p.stem + '.before_external_save' + p.suffix
    assert not (batch / history).exists()
    shutil.copy2(p, batch / history)
    previous_hash = sha(p)
    if name == 'README.md':
        text = p.read_text(encoding='utf-8')
        old = 'Pause Games import is prepared in PAUSE_GAMES_BATCH_IMPORT.json and has not been sent or saved online. The artifact lacks an Add Deck control, so importing this new deck needs a message to its existing Claude task and explicit owner authorization. These human event games do not enter the Ladder Log.'
        assert old in text
        text = text.replace(old, 'Pause Games import is saved and verified by a fresh public-page read. All four sources appear exactly once, with one new 20-card Darkness deck. Totals: 43 games, 25 wins, 18 losses and 15 opponent-concession wins. The prior 39 games and 25 deck lists are unchanged. See LIVE_SAVE_VERIFICATION.json and each game\'s appended DECK_LOG_SNAPSHOT.json. These human event games do not enter the Ladder Log.')
        p.write_text(text, encoding='utf-8')
    else:
        data = json.loads(p.read_text(encoding='utf-8-sig'))
        data.update(external_saved=True, external_verified_utc=v['verified_utc'], external_verification='LIVE_SAVE_VERIFICATION.json')
        data.pop('external_pending_reason', None)
        if name == 'BATCH_COMPLETION_CHECK.json':
            for g in data['accepted_sources']:
                g['external_saved'] = True
        else:
            data['sent'] = True
            for g in data['game_documents']:
                g['external_saved'] = True
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files.extend([name, history])
    changes.append({'path': name, 'previous_sha256': previous_hash, 'current_sha256': sha(p), 'preserved_previous': history})
for g in v['new_source_occurrences']:
    files.append(g['source_video'].removesuffix('.MP4') + '/DECK_LOG_SNAPSHOT.json')
copies = []
for name in files:
    dst = mirror / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(batch / name, dst)
    assert sha(batch / name) == sha(dst)
    copies.append({'path': name, 'sha256': sha(dst), 'bytes': dst.stat().st_size})
receipt = {
    'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'owner_authorization': 'Yes please finish. There are actually two more videos as well.',
    'external_saved': True, 'fresh_public_readback_verified': True,
    'four_games_unique': True, 'new_deck_20_slots_verified': True,
    'prior_games_and_decks_preserved': True, 'accepted_eight_file_packets_unchanged': True,
    'appended_deck_log_snapshots': 4, 'game_count': 43, 'deck_count': 26,
    'wins': 25, 'losses': 18, 'opponent_concession_wins': 15,
    'mirrored_all_added_and_updated_files': True, 'changes': changes, 'copies': copies,
}
out = batch / 'EXTERNAL_COMPLETION_RECEIPT.json'
out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
shutil.copy2(out, mirror / out.name)
assert sha(out) == sha(mirror / out.name)
print(json.dumps({k: v for k, v in receipt.items() if k not in ['changes', 'copies']}, indent=2))
