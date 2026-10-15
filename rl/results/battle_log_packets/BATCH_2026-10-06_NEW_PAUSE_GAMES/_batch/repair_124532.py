"""Apply frozen independent findings, with separately preserved Astra adjudication."""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261005_124532000_iOS'
check = json.loads((P / 'independent_sol/CHECK_RESULT.json').read_text(encoding='utf-8'))
assert check['accepted'] is False
assert {r['id'] for r in check['required_repairs']} == {'R1', 'R2', 'R3'}
assert (P / 'astra_timing/CHECK_RESULT.json').exists(), 'Await independent Astra receipt'
backup = P / 'original_before_R1_R3'
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

ledger, evidence = read('TURN_LEDGER.json'), read('TURN_EVIDENCE.json')
frames = {f['evidence_id']: f for f in evidence['frames']}
for ref, observation in {
    'f0053p20': 'Turn1 intact unzoomed four-card fan: Poison Barb, Lucky Ice Pop, Nidoking, Cyrus. No Turn5 Research or off-screen slot claim applies.',
    'f0089p20': "Turn3 intact unzoomed four-card fan: Lucky Ice Pop, Nidoking, Cyrus, Professor's Research, all readable before the Research preview or consuming play.",
    'f0269p70': 'Turn7 intact unzoomed six-card fan: Lucky Ice Pop, two separately retained Nidoking copies, Cyrus, Wally and newly drawn Nihilego. Nihilego is the rightmost card; no Turn5 Research or partial left-slot qualification applies.'
}.items():
    frames[ref]['observation'] = observation

for index, window, preview in [(0, [54, 55], 53.6), (2, [89.6, 90], 89.6)]:
    turn = ledger['turns'][index]
    turn['timing'].update(first_voluntary_move_seconds=window[1], first_voluntary_move_interval_seconds=window, first_card_preview_seconds=preview)
    play = turn['plays_in_order'][0]
    play.update(timestamp_seconds=window[1], selection_or_preview_timestamp_seconds=preview, input_or_selection_timestamp_seconds=None,
                input_time_interval_seconds=window,
                timing_limit='Requested native seek window bounds intact preview versus consumed card. Actual decoded PTS and exact touch telemetry are unmeasured; preview is separate from consumption.')
    if index == 0:
        play['card_reveal_timestamp_seconds'] = 55
    else:
        play['evidence_ids'] = list(dict.fromkeys(play['evidence_ids'] + ['f0090p20']))

frames['f0053p80'].update(before_first_play=True, unzoomed=False,
    observation='Poison Barb highlighted with translucent zoom preview; all four cards are still present. This is pre-consumption inspection, not a committed play.',
    suitability_or_limit='Intact four-card count but zoom inspection, so selected unzoomed53.2 remains preferred. Last intact54 and consumed55 bound the requested consuming transition; actual PTS unmeasured.')
frames['f0090p20'].update(before_first_play=False, unzoomed=True,
    observation='After Research consumption, only three cards remain: Lucky Ice Pop, Nidoking, Cyrus. No Research card or four-card highlighted fan is present.',
    suitability_or_limit='Post-consumption three-card hand; unsuitable starting hand. Independently adjudicated by Astra on this exact path, correcting the initial independent count claim. Actual decoded PTS unmeasured.')

draw = ledger['turns'][7]['draws_and_searches'][1]
refs = ['f0292p00', 'f0293p00', 'f0294p00', 'f0295p00']
draw.update(timestamp_seconds=None, displayed_draw_result_window_seconds=[292, 294], evidence_ids=refs,
    limit_reason='Research revealed292, concealed back entering293, all five backs present294 and unchanged295. The combined two-card result is observed; individual exact draw times and identities are not resolved.')
for card in draw['cards_in_reveal_order']:
    card.update(timestamp_seconds=None, displayed_draw_result_window_seconds=[292, 294], evidence_ids=refs,
        basis='Opaque slot in the combined two-card result; reveal ordinal is a schema position, not a separately observed hidden reveal.',
        limit_reason='Identity and individual animation time unknown.295 is settled result, not a second draw.')

old_limit = 'Scheduled +1/+3/+6 hand candidates are post-play in all four owner turns; denser native seeks recover intact preplay fans.'
new_limit = 'Candidates are individually qualified:53.8 is intact but zoomed before consumption;90.2 is a consumed three-card hand. Later offset candidates are post-play. Selected53.2/89.2/187.95/269.7 remain intact native preplay hands; exact decoded PTS unmeasured.'
def replace_text(value):
    if isinstance(value, str): return value.replace(old_limit, new_limit)
    if isinstance(value, list): return [replace_text(v) for v in value]
    if isinstance(value, dict): return {k:replace_text(v) for k,v in value.items()}
    return value
for name, obj in [('TURN_LEDGER.json', ledger), ('TURN_EVIDENCE.json', evidence), ('SUMMARY.json', read('SUMMARY.json')), ('PAUSE_GAME.json', read('PAUSE_GAME.json')), ('UNCERTAINTIES.json', read('UNCERTAINTIES.json'))]:
    save(name, replace_text(obj))

review = (P / 'REVIEW.md').read_text(encoding='utf-8')
for old, new in [
    ('Poison Barb 53.6 s:', 'Poison Barb consumed within requested54-55 s (53.6 is preview):'),
    ("Professor's Research 89.6 s:", "Professor's Research consumed within requested89.6-90 s (89.6 is preview):"),
    ('Scheduled +1/+3/+6 candidates are already after the immediate first play and are labeled unsuitable.', 'Candidates are qualified individually:53.8 retains four cards during zoom inspection;90.2 has three after Research consumption. Both are unsuitable for the selected unzoomed intact starting hand for different reasons. Later offsets are post-play.'),
    ('Scheduled +1/+3/+6 hand candidates are post-play in all four owner turns; denser native seeks recover intact preplay fans.', new_limit)
]:
    assert old in review, old
    review = review.replace(old, new)
review += '\nRoot applied frozen R1-R3 with the independent Astra timing adjudication. Initial Sol R2 incorrectly counted exact final_capture/t0090.20.jpg as four: it has three. The rejected original and separate adjudication remain preserved. Opponent Research292-294 establishes two hidden additions, with individual times null;295 is settled. Repair recheck is required.\n'
(P / 'REVIEW.md').write_text(review, encoding='utf-8')
coverage = (P / 'COVERAGE.md').read_text(encoding='utf-8')
coverage += '\nR1-R3 repaired using retained native evidence: per-turn selected hand descriptions; Tool preview distinct from54-55 consumption; Research preview89.6 distinct from consumed90/90.2; combined hidden Research292-294 with individual times unresolved. Separate Astra adjudication resolves the initial90.2 count error. Original source assets and initial rejection retained.\n'
(P / 'COVERAGE.md').write_text(coverage, encoding='utf-8')
save('INDEPENDENT_CORRECTIONS.json', {'applied_utc':datetime.now(timezone.utc).isoformat(), 'applied_by':'/root', 'repair_ids':['R1','R2','R3'], 'original_inputs':str(backup), 'initial_rejection':'independent_sol/CHECK_RESULT.json', 'adjudication':'astra_timing/CHECK_RESULT.json', 'native_evidence_reused':True, 'required_independent_recheck':True, 'changes':{'R1':'Three selected frames now describe their actual respective hands.', 'R2':'Consuming windows54-55 and89.6-90 separate from preview;53.8 pre-consumption zoom. Actual90.2 is post-consumption3, confirmed separately by Astra.', 'R3':'Hidden Research additions combined292-294, individual times null;295 settled.'}})
root = read('ROOT_VIEWED_EVIDENCE.json')
root['repair_views'] = [{'path':f['full_frame_path'], 'sha256':hashlib.sha256((P / f['full_frame_path']).read_bytes()).hexdigest(), 'observation':f.get('observation')} for f in [frames[r] for r in ['f0053p20','f0053p60','f0053p80','f0054p00','f0055p00','f0089p20','f0089p60','f0090p00','f0090p20','f0269p70','f0292p00','f0293p00','f0294p00','f0295p00']]]
root['repair_reviewed_utc'] = datetime.now(timezone.utc).isoformat()
save('ROOT_VIEWED_EVIDENCE.json', root)
result = subprocess.run([sys.executable, str(B / 'validate_packet.py'), str(P)], capture_output=True, text=True, encoding='utf-8', check=True)
(P / 'ROOT_REPAIR_STRUCTURE_CHECK.json').write_text(result.stdout, encoding='utf-8')
assert json.loads(result.stdout)['structural_pass'] is True
print('Applied124532 R1-R3 plus retained Astra adjudication; structural pass; independent recheck required')
