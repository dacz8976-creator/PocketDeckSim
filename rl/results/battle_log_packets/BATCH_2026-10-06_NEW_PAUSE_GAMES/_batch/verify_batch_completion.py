"""Verify all requested review dispositions and preserved media receipts without hydrating videos."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from batch_packet_scope import game_packets

B = Path(__file__).resolve().parent
ROOT = B.parent.parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_frozen_input(path, expected, label):
    """Cross-game Pause inputs also retain only the three authorized lead edits."""
    if path.name == 'PAUSE_GAME.json':
        backup = path.with_name('PAUSE_GAME.before_lead_acceptance.json')
        if backup.exists():
            assert digest(backup) == expected, label+' accepted Pause input'
            before = read(backup)
            current = dict(read(path))
            for key in ('lead_checked', 'battle_review_status', 'lead_acceptance'):
                if key in before:
                    current[key] = before[key]
                else:
                    current.pop(key, None)
            assert current == before, label+' unsupported post-acceptance change'
            return
    assert digest(path) == expected, label

def verify_game(p, name, source):
    lead=read(p/'LEAD_ACCEPTANCE.json')
    registration=read(p/'REGISTRATION_RESULT.json')
    game = read(p/'PAUSE_GAME.json')
    assert lead['accepted'] is True and registration['exit_code'] == 0, name
    assert game['lead_checked'] is True and game['battle_review_status'] == 'full_battle_review_complete', name
    assert game['capture_status'] in ('complete', 'complete_with_recording_limits'), name
    receipt_path = Path(lead['independent_acceptance'])
    independent = read(receipt_path)
    accepted = independent.get('accepted') is True or ('accepted' not in independent and independent.get('status') in ('accepted', 'accepted_with_recording_limits'))
    assert accepted and not any(independent.get(k) for k in ('required_repairs', 'required_repairs_remaining', 'remaining_repairs')), name
    assert source['sha256'] == lead['source_sha256'] == independent['source_sha256'], name
    for file, expected in independent.get('checked_input_sha256', {}).items():
        verify_frozen_input(p/file, expected, name+' '+file)
    ledger = read(p/'TURN_LEDGER.json')['turns']
    assert len(ledger) == lead['turn_rows'], name
    for file,expected in independent.get('supplemental_checked_input_sha256',{}).items():
        verify_frozen_input(p/file, expected, name+' supplemental '+file)
    return {'packet':str(p),'game_id':game.get('game_id'),'turn_rows':len(ledger),'accepted_input_hashes_verified':True}

selected = read(B/'OWNER_CONTEXT.json')['selected_sources']
assert len(selected) == 17 and len(set(selected)) == 17
index = list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
events = [read(p) for p in (ROOT/'Review_Log/events').glob('*.json')]
media = read(ROOT/'MEDIA_LOCATIONS.json')['moved']
rows = []
for name in selected:
    p = B/Path(name).stem
    source = read(p/'SOURCE.json')
    lead = read(p/'LEAD_ACCEPTANCE.json')
    registration = read(p/'REGISTRATION_RESULT.json')
    units=game_packets(p)
    game_rows=[verify_game(unit,name+' game'+str(number),source) for number,unit in enumerate(units,1)]
    if len(units)>1:
        assert lead.get('all_source_games_accepted') is True and lead['source_game_count']==len(units), name
        assert lead['source_total_turn_rows']==sum(r['turn_rows'] for r in game_rows), name
    moves = list(p.glob('MOVE_RECEIPT.*.json'))
    assert len(moves) == 1, name
    move = read(moves[0])
    assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256'], name
    archived = ROOT/'Reviewed'/name
    assert archived.is_file() and archived.stat().st_size == move['bytes'], name
    assert not (ROOT/name).exists(), name+' duplicate intake path'
    matches = [r for r in index if r['Video'] == name]
    assert len(matches) == 1 and matches[0]['Status'] == 'Reviewed' and matches[0]['Location'].replace('\\', '/') == 'Reviewed/'+name, name
    history = sorted((e for e in events if e.get('video_basename') == name), key=lambda e:e['logged_at_utc'])
    assert history and history[-1]['status'] == 'full_battle_review_complete' and history[-1]['video_sha256'] == source['sha256'], name
    locations = [m for m in media if m['filename'] == name]
    assert len(locations) == 1 and Path(locations[0]['current_path']).resolve() == archived.resolve() and locations[0]['sha256'] == source['sha256'], name
    rows.append({'source_video':name, 'source_sha256':source['sha256'], 'turn_rows':sum(r['turn_rows'] for r in game_rows), 'game_count':len(units), 'game_packets':game_rows, 'registration_verified':True, 'archive_receipt_verified':True, 'accepted_input_hashes_verified':True, 'video_contents_read':False})

queue = read(B/'PREPARED_GAME_QUEUE.json')
assert not queue['review_pending_sources']
expected_game_count=sum(len(game_packets(B/Path(name).stem)) for name in selected)
assert len(queue['accepted_game_entries']) + len(queue['excluded_computer_sources']) == expected_game_count
identities=[(r['source_video'],r.get('game_number_in_source',1)) for r in queue['accepted_game_entries']+queue['excluded_computer_sources']]
assert len(set(identities))==expected_game_count
assert {r['source_video'] for r in queue['accepted_game_entries']+queue['excluded_computer_sources']} == set(selected)
report = {'verified_utc':datetime.now(timezone.utc).isoformat(), 'all_requested_local_reviews_complete':True, 'source_count':len(rows), 'game_count':expected_game_count, 'human_game_entries_prepared':len(queue['accepted_game_entries']), 'computer_sources_excluded':len(queue['excluded_computer_sources']), 'scope':'Accepted input hashes, lead and independent dispositions, CLI registration, archive byte identity receipts, file sizes, unique index and media map. No video contents read; live saves and actual storage eviction are separate.', 'sources':rows}
(B/'BATCH_COMPLETION_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'sources'}))
