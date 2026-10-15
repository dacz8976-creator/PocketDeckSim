"""Append root's bounded source observations without changing reviewer inputs."""
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
NAMES = ['20261013_022530000_iOS', '20261013_030351000_iOS']
now = datetime.now(timezone.utc).isoformat()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

checks = {
    NAMES[0]: {
        't0026.00.jpg': 'Opening before placement identifies Poke Ball, Research, Haxorus, Copycat and Druddigon.',
        't0056.00.jpg': 'Research first arrival reveals Rocky Helmet.',
        't0057.00.jpg': 'Research second arrival reveals Haxorus; Rocky Helmet is now in hand.',
        't0127.00.jpg': 'Ordinary owner Turn 3 genuine preplay hand: Haxorus, Copycat, Dragonair, Haxorus, Axew. Dratini is already benched.',
        't0127.50.jpg': 'Ordinary first move places Axew on left bench; four cards remain in hand.',
        't0145.00.jpg': 'Genuine unzoomed post-Copycat hand shows Haxorus, Poke Ball and Dratini in three slots. Confirms identities without assigning second/third arrival time or order.',
        't0158.00.jpg': 'Owner Turn 3 ending hand exactly Haxorus and Axew, count two. Matches five-card start, bench/evolution, Copycat replacement, Poke Ball play/search and Dratini bench arithmetic.',
        't0296.00.jpg': 'Turn 6 Rocky Helmet trigger banner is visible after Rough Skin sequence. This contradicts the draft claim that Helmet did not resolve.',
        't0297.00.jpg': 'Additional 20 damage overlay appears on Orthworm with displayed zero HP; Helmet sequence is retained separately from the preceding Rough Skin knockout.',
        't0498.00.jpg': 'Turn 11 attack preview shows Haxorus Frenzied Blade 170, one Fighting and two Metal; benched Axew two Fighting. Attack zoom obscures some lower board, so this alone is not a clean full ending-hand snapshot.',
        't0395.00.jpg': 'Turn 9 preplay hand Axew and Rainbow Cave. Haxorus has two Metal, current zone not visible in this frame.',
        't0396.00.jpg': 'Axew enters left bench first; Rainbow Cave remains in hand. Current and next zone icons show Fighting.',
        't0405.00.jpg': 'Rainbow Cave is in stadium slot; current zone transitioning empty, Haxorus still two Metal. No attached Axew Energy icon yet visible here.',
        't0416.00.jpg': 'Haxorus now one Fighting and two Metal; benched Axew one Fighting. Hand empty; next zone preview is Fighting, numerical future count unknown.',
        't0544.00.jpg': 'Explicit opponent-conceded banner; opponent Active name is Mega Scizor ex.',
        't0559.00.jpg': 'Victory terminal result: owner first, 12 turns, owner 2 points, opponent 1, damage 480.'
    },
    NAMES[1]: {
        't0031.00.jpg': 'Opening Rare Candy zoom partially obscures the hand; unsuitable alone as full-opening proof.',
        't0032.00.jpg': 'Preplacement opening five identifiable as Rare Candy, selected raised Dratini, Copycat, Rainbow Cave, Dragonair; Active still empty.',
        't0058.00.jpg': 'Copycat first visible arrival Rocky Helmet.',
        't0058.50.jpg': 'Next visible arrival Research; Rocky Helmet now in hand.',
        't0059.00.jpg': 'Research still zoomed; does not show next Poke Ball arrival.',
        't0059.50.jpg': 'Next visible arrival Poke Ball; Rocky Helmet and Research already in hand. Does not show Dragonair.',
        't0060.50.jpg': 'Fourth Copycat arrival Dragonair, with Helmet, Research and Poke Ball already in hand. Completes independently observed four-card reveal order.',
        't0077.00.jpg': 'End of owner Turn 1 hand Research plus Dragonair, count two. Axew benched and Rocky Helmet attached to Druddigon.',
        't0117.50.jpg': 'Ordinary owner Turn 3 preplay hand Research, Dragonair and drawn Dratini. Bench right empty.',
        't0118.50.jpg': 'Dratini draw/inspection zoom; remains in hand, right Bench empty. This alone does not prove placement.',
        't0119.00.jpg': 'Actual first voluntary Turn 3 play: Dratini moves onto right Bench; Research and Dragonair remain in hand. Confirms corrected placement anchor.',
        't0121.00.jpg': 'Owner Turn 3 first play Dratini now placed on right Bench, two-card hand Research and Dragonair.',
        't0568.00.jpg': 'Iris literal effect grants one additional point if an attack used by Haxorus knocks out the opponent Active. Score before attack is owner 0, opponent 2.',
        't0626.00.jpg': 'Defeat versus Hiro Japanese name: owner first, 16 turns, owner 2 points, opponent 3, damage 230.'
    }
}
for name in NAMES:
    packet = BATCH / name
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8'))
    path = packet / 'ROOT_SOURCE_CHECKS.json'
    receipt = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {
        'lead': '/root', 'source_sha256': source['sha256'], 'full_second_pass': False, 'checks': []}
    old = {r['path'] for r in receipt['checks']}
    for filename, observed in checks[name].items():
        frame = packet / 'turn_evidence' / filename
        relative = frame.relative_to(packet).as_posix()
        assert frame.exists(), frame
        if relative not in old:
            receipt['checks'].append({'path': relative, 'sha256': hashlib.sha256(frame.read_bytes()).hexdigest(), 'observed': observed})
    receipt['updated_utc'] = now
    save(path, receipt)
    time_path = packet / 'SOURCE_TIME.json'
    if not time_path.exists():
        result = subprocess.run(['C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe', '-v', 'error', '-show_entries', 'format_tags=creation_time:stream_tags=creation_time', '-of', 'json', str(ROOT / source['video_basename'])], capture_output=True, text=True, check=True)
        tags = json.loads(result.stdout)
        utc = tags['format']['tags']['creation_time']
        parsed = datetime.fromisoformat(utc.replace('Z', '+00:00'))
        # Chicago was on daylight saving time on the two source dates.
        local = parsed.astimezone(timezone(timedelta(hours=-5)))
        assert local.date().isoformat() == '2026-10-12'
        save(time_path, {'source_sha256': source['sha256'], 'probed_utc': now, 'probe_output': tags, 'creation_time_utc': utc, 'timezone': 'America/Chicago', 'utc_offset': '-05:00', 'creation_time_local': local.isoformat(), 'match_date_local': local.date().isoformat(), 'basis': 'Container and stream creation metadata, corroborated by visible phone clocks. Filename retains UTC date. Exact battle start is slightly later than recording start.'})

roles_path = BATCH / 'REVIEW_ROLES.json'
if not roles_path.exists():
    save(roles_path, {'updated_utc': now, 'lead': '/root', 'lead_role': 'Single shared writer, bounded direct source reconciliation, acceptance, registration, move, external verification and mirror.', 'sources': [
        {'source': NAMES[0] + '.MP4', 'registered_reviewer': '/root/pause_' + NAMES[0], 'actual_worker': '/root/newest_022530', 'independent_worker': '/root/check_newest_022530', 'model': 'gpt-6.1-sol', 'effort': 'high', 'current_status': 'full_review_and_independent_checks_in_progress'},
        {'source': NAMES[1] + '.MP4', 'registered_reviewer': '/root/pause_' + NAMES[1], 'actual_worker': '/root/newest_030351', 'independent_worker': 'pending_fresh_worker', 'model': 'gpt-6.1-sol', 'effort': 'high', 'current_status': 'full_review_in_progress'}]})
if not (BATCH / 'README.md').exists():
    (BATCH / 'README.md').write_text('# Newest two recordings\n\nBoth exact sources are now fully downloaded and hash-bound. Full review and independent checks are in progress. Only the two filenames in OWNER_CONTEXT.json are included.\n\nThe filmed QR establishes the same 20-card Haxorus / Dragonair / Druddigon list in both clips. It was absent from the fresh 26-deck Pause Games baseline. PREPARED_FILMED_DECK.json is a proposed import, not a saved live list.\n\nReview acceptance, external save, archival and final storage are not yet claimed. Original source filenames use UTC; SOURCE_TIME.json preserves the October 12 Chicago recording dates.\n', encoding='utf-8')
print('Saved bounded root checks, recording date supplements and current roles.')
