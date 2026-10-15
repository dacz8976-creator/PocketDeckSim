"""Apply the owner's bounded wording corrections, preserving review history."""
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from refresh_accepted_packet import refresh_accepted_packet

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA' / 'BATCH_2026-09-30'
audit = batch / 'WORDING_CORRECTIONS_2026-09-30'
audit.mkdir(exist_ok=False)
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
intake = read(batch / 'INTAKE.json')
snapshot = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
(audit / 'INDEX_BEFORE.json').write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
specific = {
    '141742': [
        ('REVIEW.md', 'Budew does not attack and no item restriction from its Prickly Powder attack is established.', 'Budew does not attack. This visible Prickly Powder version removes the Defending Pokemon\'s Abilities until it leaves the Active Spot; no Ability lock is applied in this battle.'),
        ('REVIEW.md', 'No burn-damage, burn-coin, item-lock, Time Recall, Tool or Stadium behavior is tested here.', 'No burn-damage, burn-coin, Prickly Powder Ability-lock, Time Recall, Tool or Stadium behavior is tested here.'),
    ],
    '144608': [
        ('REVIEW.md', 'Vigilant Delivery', 'Villainous Delivery'),
        ('REVIEW.md', 'The visible targets have Fighting Weakness but each attack still deals 50: Bombirdier 70 -> 20 -> knockout; Alolan Grimer 80 -> 30 -> knockout; Gastly 60 -> 10 -> knockout.', 'Bombirdier is weak to Lightning, so its 70 -> 20 hit is plain 50 damage and does not test Fighting Weakness exclusion. Alolan Grimer and Gastly are Fighting-weak: their 80 -> 30 and 60 -> 10 hits still deal 50, directly testing Quick Straight\'s printed Weakness exclusion. Each target is subsequently knocked out by another Quick Straight.'),
    ],
    '153142': [('REVIEW.md', 'Corvisquire, 80 HP, Jaunt 30;', 'Corvisquire, 80 HP, Joust 30 for two Colorless; its printed effect discards all Pokemon Tools from the opponent\'s Active before doing damage;')],
    '155152': [
        ('REVIEW.md', 'Bubble 20 with a paralysis coin effect, Water + Colorless cost;', 'Bubble 20 with a paralysis coin effect, two Water cost [WW];'),
        ('ROOT_SPOT_CHECK.md', 'Ordinary Hearthflame Dance animation with printed 40 damage. Opponent Active shows 80 HP; Cyndaquil and Torchic are on its Bench. Articuno ex displays 140 HP. This animation frame is not used as a settled post-attack HP readout.', 'Owner turn 3 development before Rare Candy. Ogerpon is Active at 80 HP with one Fire, which does not meet Hearthflame Dance\'s two-Energy cost. Cyndaquil and Torchic are on its Bench; owner Articuno ex remains 140 HP. No Hearthflame Dance attack or attack-damage event is established by this frame.'),
    ],
    '160256': [('REVIEW.md', 'Bubble 20, Water plus Colorless cost,', 'Bubble 20, two Water cost [WW],')],
}
descriptions = {
    '141742': ['Prickly Powder is an Ability lock, not an Item restriction; Budew never attacked.'],
    '144608': ['Bombirdier is Lightning-weak; only the Fighting-weak Alolan Grimer and Gastly hits test Quick Straight ignoring Weakness.', 'Card lookup also confirms the untriggered Bombirdier Ability is named Villainous Delivery; its previously described effect was unchanged.'],
    '153142': ['Corvisquire attack is Joust 30 [CC], with the printed pre-damage Tool-discard effect.'],
    '155152': ['Bubble costs two Water [WW].', 'Root 52-second anchor is owner turn 3 development before Rare Candy, not an Ogerpon attack.'],
    '160256': ['Bubble costs two Water [WW].'],
}
protected_before = {}
for item in intake['sources']:
    packet = root / 'Recording_QA' / (Path(item['video']).stem + '_auto_sol')
    protected_before[item['video']] = {filename: digest(packet / filename) for filename in ['SOURCE.json', 'LEAD_ACCEPTANCE.json', f"MOVE_RECEIPT.{item['video']}.json"]}
    backup = audit / packet.name
    backup.mkdir()
    for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'ROOT_SPOT_CHECK.md']:
        path = packet / filename
        if path.is_file():
            (backup / filename).write_bytes(path.read_bytes())

# Save the exact local card-source lookup used to verify the requested text.
repo = Path(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim')
lookup = subprocess.run([sys.executable, str(repo / 'lib' / 'card.py'), 'B3 013', 'B3 115', 'B2 096', 'B2b 037', 'B3 146', 'P-B 003', 'Hitmonchan ex'], cwd=repo, check=True, capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
(audit / 'CARD_LOOKUPS.txt').write_text(lookup.stdout, encoding='utf-8')
source_reference = {'card_lookup': str(repo / 'lib' / 'card.py'), 'card_database': str(repo / 'lib' / 'deckgym-database.json'), 'database_sha256': digest(repo / 'lib' / 'deckgym-database.json'), 'git_head': subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip(), 'scope': 'Read-only exact card-text lookups and bounded saved-frame checks; no repeated full engine audit'}
(audit / 'SOURCE_REFERENCE.json').write_text(json.dumps(source_reference, indent=2) + '\n', encoding='utf-8')

entries = []
for item in intake['sources']:
    video = item['video']
    packet = root / 'Recording_QA' / (Path(video).stem + '_auto_sol')
    tag = video.split('_')[1][:6]
    for filename, before, after in specific.get(tag, []):
        path = packet / filename
        text = path.read_text(encoding='utf-8-sig')
        if text.count(before) != 1:
            raise RuntimeError(f'Expected one exact correction anchor: {packet.name}/{filename}: {before}')
        path.write_text(text.replace(before, after), encoding='utf-8')
    refreshed = refresh_accepted_packet(packet)
    changes = descriptions.get(tag, []).copy()
    changes.append('Current status refreshed from lead acceptance and the matching archive receipt. Historical worker-only actions remain explicitly separate.')
    addendum = [f'# Post-acceptance wording and status corrections: {video}', '', 'September 30, 2026. Owner supplied the cross-check from Claude session "Second brain from GitHub repos". The lead independently checked the cited card printings with the local card lookup and inspected the Corvisquire 53-second and Ogerpon 52-second frames. This is a targeted wording/status follow-up, not a repeated full review or full engine audit.', '', f"Source SHA-256: `{item['sha256']}`. The existing full Sol review remains accepted. Outcome, displayed score, source bytes and Ladder exclusion remain unchanged.", '', 'Corrections applied:', '']
    addendum += ['- ' + change for change in changes]
    addendum += ['', 'Display interpretation: the quoted results-screen Damage done can include overkill, so it is not net HP removed. The HUD shows up to three point circles; observed +2/+3 award events are recorded separately when they cross that display threshold.', '', f'Unmodified pre-correction packet files are preserved under `../BATCH_2026-09-30/WORDING_CORRECTIONS_2026-09-30/{packet.name}/`. Existing review events, source binding, lead acceptance and archive receipt are preserved.', '']
    (packet / 'POST_ACCEPTANCE_CORRECTIONS.md').write_text('\n'.join(addendum), encoding='utf-8')
    review = packet / 'REVIEW.md'
    review.write_text(review.read_text(encoding='utf-8-sig') + '\n\n## Post-acceptance wording and status check\n\nThe accepted review has received a targeted wording/status follow-up. See [the correction record](POST_ACCEPTANCE_CORRECTIONS.md) for exact changes, preserved history and result-display limits. Outcome, score, source identity and Ladder exclusion are unchanged.\n', encoding='utf-8')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    notes = 'Targeted post-acceptance wording/status correction requested by owner after Claude cross-check. Existing full Sol review and lead acceptance retained; no new full-review claim, no change to outcome, displayed points, source bytes or ladder exclusion. '
    notes += ' '.join(changes)
    command = [sys.executable, str(root / 'Review_Log' / 'review_log.py'), '--root', str(root), 'record', '--video', video, '--reviewer', 'root_20260930_post_acceptance_wording', '--status', 'full_battle_review_complete', '--scope', lead['scope'] + '; targeted post-acceptance wording/status addendum; full review remains accepted', '--correct', '--notes', notes]
    for filename in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json', 'POST_ACCEPTANCE_CORRECTIONS.md']:
        command += ['--evidence', str(packet / filename)]
    recorded = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
    event_path = Path(recorded.stdout.strip())
    event = read(event_path)
    assert event['video_sha256'] == item['sha256'] and event['video_bytes'] == item['bytes']
    summary_path = packet / 'SUMMARY.json'
    summary = read(summary_path)
    summary['current_review_event_id'] = event['event_id']
    summary['post_acceptance_corrections'] = 'POST_ACCEPTANCE_CORRECTIONS.md'
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    protected_after = {filename: digest(packet / filename) for filename in protected_before[video]}
    assert protected_before[video] == protected_after
    modified = []
    for old in (audit / packet.name).iterdir():
        now = packet / old.name
        if digest(old) != digest(now):
            modified.append({'file': old.name, 'before_sha256': digest(old), 'after_sha256': digest(now)})
    entries.append({'video': video, 'source_sha256': item['sha256'], 'changes': changes, 'modified_files': modified, 'follow_up_event_id': event['event_id'], 'supersedes_event_id': event['supersedes_event_id'], 'protected_source_acceptance_receipt_unchanged': True})
    print('Corrected and registered:', video, flush=True)

current = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
before_by_name = {r['Video']: r for r in snapshot}
after_by_name = {r['Video']: r for r in current}
assert before_by_name.keys() == after_by_name.keys()
names = {item['video'] for item in intake['sources']}
for name, prior in before_by_name.items():
    now = after_by_name[name]
    if name not in names:
        assert now == prior, f'Unrelated row changed: {name}'
    else:
        assert now['Status'] == prior['Status'] == 'Reviewed' and now['Location'] == prior['Location']
manifest = {'completed_at_utc': datetime.now(timezone.utc).isoformat(), 'passed': True, 'packets_refreshed': len(entries), 'content_corrected_packets': len(specific), 'outcomes_scores_ladder_source_unchanged': True, 'existing_events_preserved': True, 'videos': entries}
(audit / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
report = ['# September 30 post-acceptance review corrections', '', 'Applied the owner-supplied wording corrections, independently checked with exact local card printings and bounded saved-frame inspection. All 15 packet statuses now agree with their lead acceptances and archive receipts. Future acceptance refreshes those fields automatically.', '', 'Outcomes, displayed scores, source videos and Ladder exclusion are unchanged. Original packet text and prior immutable review events are preserved; new source-hashed correction events retain completed status.', '', '| Recording | Wording correction |', '|---|---|']
for entry in entries:
    tag = entry['video'].split('_')[1][:6]
    if tag in descriptions:
        report.append(f"| `{entry['video']}` | {' '.join(descriptions[tag])} |")
report += ['', 'Results counters can include overkill; point-circle displays stop at three. The reviews retain observed award events separately from the displayed final circles.', '', 'The external cross-check reported no engine contradictions. This follow-up verified the specific wording items; it did not repeat the entire engine audit or all 15 visual reviews.', '', 'Evidence and unmodified packet copies: `WORDING_CORRECTIONS_2026-09-30/`. Each affected review links its own `POST_ACCEPTANCE_CORRECTIONS.md`.', '']
(batch / 'POST_ACCEPTANCE_CORRECTIONS_2026-09-30.md').write_text('\n'.join(report), encoding='utf-8')
print(f'PASS: {len(entries)} status refreshes; five packets corrected; original outcomes/scores/sources/ladder unchanged', flush=True)
