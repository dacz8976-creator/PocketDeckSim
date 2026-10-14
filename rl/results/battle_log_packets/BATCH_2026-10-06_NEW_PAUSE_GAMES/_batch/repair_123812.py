"""Apply the four frozen independent findings once, retaining original inputs."""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261005_123812000_iOS'
check = json.loads((P / 'independent_sol/CHECK_RESULT.json').read_text(encoding='utf-8'))
assert check['accepted'] is False
assert {r['id'] for r in check['required_repairs']} == {'R1', 'R2', 'R3', 'R4'}
backup = P / 'original_before_R1_R4'
assert not backup.exists() and not (P / 'LEAD_ACCEPTANCE.json').exists()
for name, digest in check['checked_input_sha256'].items():
    assert hashlib.sha256((P / name).read_bytes()).hexdigest() == digest, name
backup.mkdir()
for name in check['checked_input_sha256']:
    shutil.copy2(P / name, backup / Path(name).name)

def read(name):
    return json.loads((P / name).read_text(encoding='utf-8-sig'))

def save(name, value):
    (P / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

summary, game, uncertainties = read('SUMMARY.json'), read('PAUSE_GAME.json'), read('UNCERTAINTIES.json')
summary['queue'] = 'Deluxe Pack: Mega Emblem Event'
summary['queue_evidence_ids'] = ['f-0004.00', 'f-0005.00']
game['classification'].update(specific_queue=summary['queue'], queue_evidence_ids=summary['queue_evidence_ids'], limit='Visible event title established; unstated ranked status and concession reason remain unknown.')
u7 = next(u for u in uncertainties['uncertainties'] if u['id'] == 'U7')
u7.update(topic='Concession reason and unstated ranked status', observation='Concede filmed; reason not stated. Deluxe Pack: Mega Emblem Event is visible at4-5.', resolution='Human event loss by concession; no concession reason or ranked inference.')

ledger, evidence = read('TURN_LEDGER.json'), read('TURN_EVIDENCE.json')
for index, seconds in [(0, 45), (2, 110)]:
    draw = ledger['turns'][index]['draws_and_searches'][0]
    draw.update(timestamp_seconds=seconds, evidence_ids=[f'f-{seconds:07.2f}'])
    draw['cards_in_reveal_order'][0].update(timestamp_seconds=seconds, evidence_ids=draw['evidence_ids'])

for index, draw_index, window, refs in [(1, 1, [83, 85], ['f-0083.00', 'f-0085.00', 'f-0086.00']), (3, 2, [172, 174], ['f-0172.00', 'f-0174.00', 'f-0175.00'])]:
    draw = ledger['turns'][index]['draws_and_searches'][draw_index]
    draw.update(timestamp_seconds=None, displayed_draw_result_window_seconds=window, evidence_ids=refs, limit_reason='Two concealed cards established by fan expansion. Individual draw times and identities are not resolved by these samples.')
    for card in draw['cards_in_reveal_order']:
        card.update(timestamp_seconds=None, displayed_draw_result_window_seconds=window, evidence_ids=refs, basis='Opaque draw slot in the two-card result; fan expansion establishes combined count only.', limit_reason='Individual hidden reveal timing and identity unknown; ordinal does not establish an observed separate reveal.')

lead = ledger['turns'][1]['draws_and_searches'][3]
lead.update(timestamp_seconds=106, evidence_ids=['f-0105.00', 'f-0106.00'], displayed_draw_result_window_seconds=[105, 106])
lead['cards_in_reveal_order'][0].update(timestamp_seconds=106, evidence_ids=lead['evidence_ids'], basis='Fan3 at105 and fan4 at106 support one hidden search return by106.', limit_reason='Opponent identity remains concealed; exact animation instant within105-106 unknown.')
needle = ledger['turns'][0]['automatic_events_in_order'][0]
needle.update(timestamp_seconds=64, impact_animation_seconds=61, resolved_hp_seconds=64, event='Deceptive Needle impact animation61; resolved Ralts60 to50 by64', evidence_ids=['f-0060.50', 'f-0061.00', 'f-0064.00'])

discard = evidence['discard_snapshots'][0]
assert discard['snapshot_id'] == 'discard-94'
discard['cards_in_view'] = ["Professor's Research"]
discard['limit_reason'] = 'Native94 shows Research on top; Poke Ball top appears later at95. Only the top preview is established, not full pile contents.'

for index, window in [(0, [52, 53]), (8, [317, 317.5])]:
    turn = ledger['turns'][index]
    turn['timing'].update(first_voluntary_move_seconds=window[1], first_voluntary_move_interval_seconds=window)
    turn['plays_in_order'][0].update(timestamp_seconds=window[1], input_time_interval_seconds=window, input_timestamp_basis='Last retained pre-consumption frame and first retained consumed-card frame bound the play; not measured touch telemetry.')
candidate = next(f for f in evidence['frames'] if f['evidence_id'] == 'f-0317.00')
candidate.update(before_first_play=True, unzoomed=False, observation='Pre-consumption Poke Ball zoom inspection with intact four-card hand, not a consumed play.', suitability_or_limit='Intact card count, but zoom inspection makes this unsuitable for the selected unzoomed starting hand. Consumption is visible317.5; selected316 remains unchanged.')

for name, value in [('SUMMARY.json', summary), ('PAUSE_GAME.json', game), ('UNCERTAINTIES.json', uncertainties), ('TURN_LEDGER.json', ledger), ('TURN_EVIDENCE.json', evidence)]:
    save(name, value)
review = (P / 'REVIEW.md').read_text(encoding='utf-8')
for old, new in [
    ('The clip does not establish why the owner conceded or which human queue was selected.', 'The filmed deck selection establishes Deluxe Pack: Mega Emblem Event at4-5. The clip does not establish why the owner conceded or any unstated ranked status.'),
    ('Deceptive Needle at44.', 'Deceptive Needle face visible at45.'),
    ('Needle deals10 to Ralts60→50 by61.', 'Needle impact animates at61 while Ralts still displays60; resolved HP50 is visible by64.'),
    ('two hidden draws85–86', 'two hidden draw results bounded83–85 by fan3 to5; individual times unresolved'),
    ('alternate-art Darkrai109.', 'alternate-art Darkrai face visible110.'),
    ('Research171 draws two hidden cards173/175.', 'Research171 produces two hidden cards bounded172–174 by fan2 to4;175 is a settled result, not proof of a separate second draw.')]:
    assert old in review, old
    review = review.replace(old, new)
review += '\nRoot applied frozen independent findings R1-R4. Original submissions and original rejection remain retained. The input intervals52-53 and317-317.5 distinguish intact inspection from consumption; discard94 is Research, not the later Ball. Independent repair recheck remains required.\n'
(P / 'REVIEW.md').write_text(review, encoding='utf-8')
coverage = (P / 'COVERAGE.md').read_text(encoding='utf-8')
coverage += '\nR1-R4 source corrections: event title visible4-5; named draw faces45/110; hidden Research results bounded83-85 and172-174 without individual reveal times; Needle61 impact versus64 resolved HP; Research discard top94; consuming play windows52-53 and317-317.5, with317 pre-consumption zoom inspection. All original native evidence remains retained.\n'
(P / 'COVERAGE.md').write_text(coverage, encoding='utf-8')
save('INDEPENDENT_CORRECTIONS.json', {'applied_utc':datetime.now(timezone.utc).isoformat(), 'applied_by':'/root', 'repair_ids':['R1','R2','R3','R4'], 'original_inputs':str(backup), 'initial_rejection':'independent_sol/CHECK_RESULT.json', 'native_evidence_reused':True, 'required_independent_recheck':True, 'changes':{'R1':'Visible event queue corrected; unstated ranked status remains unknown.', 'R2':'Named face times and Lead fan expansion corrected; hidden draw results bounded; impact separated from HP resolution.', 'R3':'Retained discard94 now accurately records Research; full pile remains unestablished.', 'R4':'Consuming input windows explicit;317 intact zoom inspection qualified separately.'}})
result = subprocess.run([sys.executable, str(B / 'validate_packet.py'), str(P)], capture_output=True, text=True, encoding='utf-8', check=True)
(P / 'ROOT_REPAIR_STRUCTURE_CHECK.json').write_text(result.stdout, encoding='utf-8')
assert json.loads(result.stdout)['structural_pass'] is True
print('Applied frozen123812 R1-R4; structural pass; independent recheck required')
