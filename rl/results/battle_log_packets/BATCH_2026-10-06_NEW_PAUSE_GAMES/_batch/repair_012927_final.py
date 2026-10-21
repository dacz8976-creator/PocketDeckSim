"""Reconcile the final independent findings once without changing game1 QR data."""
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B / '20261006_012927000_iOS'
C = P / 'game_02'
backup = P / 'original_before_final_independent'
assert not backup.exists() and not (P / 'LEAD_ACCEPTANCE.json').exists()
checks = [json.loads((q / 'independent_sol/CHECK_RESULT.json').read_text(encoding='utf-8')) for q in [P, C]]
assert all(c['accepted'] is False and len(c['required_repairs']) >= 3 for c in checks), 'Await final frozen rejection'
backup.mkdir()
for q, check in zip([P, C], checks):
    for name, digest in check['checked_input_sha256'].items():
        assert hashlib.sha256((q / name).read_bytes()).hexdigest() == digest, name
for q in [P, C]:
    dest = backup / ('parent' if q == P else 'game_02')
    dest.mkdir()
    for name in ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'PAUSE_GAME.json', 'DECK_USED.json', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json', 'HANDOFF.md', 'DECK_EDIT_LEDGER.json', 'CORRECTION_LEDGER.json']:
        if (q / name).exists(): shutil.copy2(q / name, dest / name)
for name in ['EDITED_DECK_ENTRY.json', 'EDITED_DECK_ENTRY.md', 'PAUSE_EDITED_DECK_IMPORT.json']:
    shutil.copy2(B / name, backup / name)
frozen13 = hashlib.sha256((B / 'NEW_DECK_ENTRIES.json').read_bytes()).hexdigest()

def read(q, name): return json.loads((q / name).read_text(encoding='utf-8-sig'))
def save(q, name, obj): (q / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def replace(value, old, new):
    if isinstance(value, str): return value.replace(old, new)
    if isinstance(value, list): return [replace(v, old, new) for v in value]
    if isinstance(value, dict): return {k:replace(v, old, new) for k,v in value.items()}
    return value

definition = read(B, 'EDITED_DECK_ENTRY.json')
entry = definition['decks'][0]
old_id = entry['id']
identity = {'cards':[(c['entity_kind'],c['entity_id'],c['count']) for c in entry['cards_in_display_order']], 'energy':['Water']}
digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
new_id = 'filmed-edit-' + digest[:12]
assert new_id != old_id
definition = replace(replace(definition, 'Darkness', 'Water'), old_id, new_id)
entry = definition['decks'][0]
entry['semantic_identity_sha256'] = digest
entry['energy_configuration'] = ['Water']
entry['native_final_views'].append({'source_seconds':596, 'path':str(P/'native/t0596.00.jpg'), 'image_sha256':hashlib.sha256((P/'native/t0596.00.jpg').read_bytes()).hexdigest(), 'observation':'Fully labeled Energy menu: Water selected, Darkness unselected; matches saved final Water droplet.'})
definition['source_correction_utc'] = datetime.now(timezone.utc).isoformat()
definition['supersedes_prepared_identity'] = old_id
save(B, 'EDITED_DECK_ENTRY.json', definition)
for name in ['EDITED_DECK_ENTRY.md', 'PAUSE_EDITED_DECK_IMPORT.json']:
    text = (B / name).read_text(encoding='utf-8').replace('Darkness','Water').replace(old_id,new_id)
    (B / name).write_text(text, encoding='utf-8')

edit = replace(read(P, 'DECK_EDIT_LEDGER.json'), old_id, new_id)
edit['final_energy_configuration'] = ['Water']
edit['energy_edits'][1]['observation'] = 'Energy dialog changes;594 warns selected type is not in deck;596 fully labeled menu shows Water alone selected and Darkness unselected. Exact intervening touch sequence remains unmeasured.'
edit['energy_edits'][2]['observation'] = 'Deck-box popup597 and deck pages599/600 retain the same Water droplet shown beside the labeled Water selection596. Water alone remains configured.'
edit['energy_edits'][3]['observation'] = 'Final New deck6 page20/20 Water only; continuous Save621 and event queue622 into game2.'
save(P, 'DECK_EDIT_LEDGER.json', edit)

# No Darkness Energy was attached during childgame; every child typed owner preview was Water.
for name in ['SUMMARY.json', 'UNCERTAINTIES.json', 'PAUSE_GAME.json', 'DECK_USED.json', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json']:
    save(C, name, replace(replace(read(C,name), 'Darkness', 'Water'), old_id, new_id))
ledger = read(C, 'TURN_LEDGER.json')
draw = ledger['turns'][0]['draws_and_searches'][2]
old_cards = copy.deepcopy(draw['cards_in_reveal_order'])
ordered = [old_cards[i] for i in [0,2,1,3]]
for position, card in enumerate(ordered, 1):
    seconds = 673 + position
    card.update(reveal_position=position, timestamp_seconds=seconds, evidence_ids=[f'f{seconds:04d}_00'], basis='Distinct named native Copycat reveal face observed in this source order.')
draw.update(cards_in_reveal_order=ordered, evidence_ids=['f0674_00','f0675_00','f0676_00','f0677_00'])
copycat = ledger['turns'][0]['plays_in_order'][2]
copycat.update(input_interval_seconds=[667,668], input_timing_limit='667 intact four-card selection;668 consumed Copycat and three remaining cards;670 old three return. Actual PTS and exact touch unmeasured.', card_reveal_timestamp_seconds=668, returned_hand_timestamp_seconds=670, evidence_ids=['f0667_00','f0668_00','f0670_00'])
row = ledger['turns'][1]
row['hand_at_start'].update(count=5, status='observed_concealed_faces', basis='Five distinct settled backs at692 after hidden normal draw.', evidence_ids=['f0692_00'], limit_reason='Count observed, identities concealed; individual normal draw animation time unresolved within690-692.')
row['opponent_hand_at_owner_turn_start'].update(count=5, supported_range=[5,5], evidence_ids=['f0692_00'], limit_reason='Five literal settled backs at opponent turn2 start; identities hidden.')
normal = row['draws_and_searches'][0]
normal.update(timestamp_seconds=None, displayed_draw_result_window_seconds=[690,692], evidence_ids=['f0690_00','f0692_00'], limit_reason='One hidden normal draw completed by692; exact arrival within690-692 unresolved.')
normal['cards_in_reveal_order'][0].update(timestamp_seconds=None, displayed_draw_result_window_seconds=[690,692], evidence_ids=['f0690_00','f0692_00'], basis='Completed fan expands4 to5; no individual face exposed.', limit_reason=normal['limit_reason'])
research = row['draws_and_searches'][1]
research.update(timestamp_seconds=None, displayed_draw_result_window_seconds=[696,698], evidence_ids=['f0696_00','f0698_00'], limit_reason='Four backs696 and six698 establish the combined two hidden additions, not individual reveal times.')
for card in research['cards_in_reveal_order']:
    card.update(timestamp_seconds=None, displayed_draw_result_window_seconds=[696,698], evidence_ids=research['evidence_ids'], basis='Opaque schema slot in combined two-card result; separately timed hidden reveals not established.', limit_reason='Individual identity and reveal time unknown.')
row['plays_in_order'][1].update(timestamp_seconds=700, card_reveal_timestamp_seconds=700, display_or_resolution_timestamp_seconds=700, coin_animation_timestamp_seconds=702, evidence_ids=['f0700_00','f0702_00','f0704_00'])
zone = row['board_at_start']['opponent']['energy_zone']
zone['this_turn'] = {'type':'Lightning','count':1,'available':True}
zone['generation_window_seconds'] = [690,692]
zone['basis'] = 'Large current Lightning and separate small next Lightning both visible692; generation occurred by692, not deferred to698.'
row['automatic_events_in_order'][0].update(evidence_ids=['f0690_00','f0692_00'], observed_window_seconds=[690,692])
save(C, 'TURN_LEDGER.json', ledger)
evidence = read(C, 'TURN_EVIDENCE.json')
observations = {'f0692_00':'Five settled opponent backs; current Lightning available and next Lightning separately visible.', 'f0694_00':'Four fan backs and one detached face-down played card; not a normal draw arrival.', 'f0696_00':'Four fan backs after Research consumption, before two hidden additions complete.', 'f0698_00':'Six fan backs establish combined two hidden Research additions by698; individual times unknown.', 'f0700_00':'Order Pad face-up card display.', 'f0702_00':'Order Pad coin animation; played-card face already observed700.'}
for frame in evidence['frames']:
    if frame['evidence_id'] in observations: frame['observation'] = observations[frame['evidence_id']]
save(C, 'TURN_EVIDENCE.json', evidence)
uncertainties = read(C, 'UNCERTAINTIES.json')
normal_limit = next(u for u in uncertainties['uncertainties'] if u['id']=='moving-opponent-normal-draw')
normal_limit.update(id='opponent-normal-draw-time', status='bounded_recording_limit', impact='692 has five literal settled backs and available current Lightning. Normal draw/generation time remains bounded690-692; hidden identity unknown.694 is a played-card back with four fan backs.')
uncertainties['resolved_corrections'].append('Final Water configuration, Copycat reveal order and consuming input, opponent literal five-back start/current Lightning692, combined hidden Research696-698 and Order Pad face700 resolved by independent native check.')
save(C, 'UNCERTAINTIES.json', uncertainties)

parent = read(P, 'TURN_LEDGER.json')
parent['turns'][1]['timing']['first_voluntary_move_interval_seconds'] = [55,56]
parent['turns'][1]['timing']['first_voluntary_move_seconds_basis'] = '55.3 is an approximate locator within retained intact55 and consumed56, not measured touch/PTS.'
parent['turns'][1]['plays_in_order'][0].update(input_interval_seconds=[55,56], input_timing_limit='First Ball intact55 and consumed56;58 remains face-up display timing. Actual decoded PTS/touch unmeasured.', evidence_ids=['f0055_00','f0056_00','f0058_00'])
save(P, 'TURN_LEDGER.json', parent)

for q in [P,C]:
    for name in ['REVIEW.md','COVERAGE.md','HANDOFF.md']:
        file = q/name
        if not file.exists(): continue
        text = file.read_text(encoding='utf-8')
        if q==C: text=text.replace('Darkness','Water')
        else:
            text=text.replace('Darkness-only Save','Water-only Save').replace('transient Water selection','selected Water configuration').replace('Energy transient Water595/596; final Darkness597/599/600/620.', 'Energy Water selected595/596; final Water597/599/600/620.')
        text=text.replace('Poké Ball, Lucky Ice Pop, Team Rocket’s Meowth and Cyrus', 'Poké Ball, Team Rocket’s Meowth, Lucky Ice Pop and Cyrus')
        text=text.replace('Copycat arrivals674/676/678/680', 'Copycat selected667/consumed668, old3 return670, arrivals Ball674/TRMeowth675/Pop676/Cyrus677')
        text=text.replace('Opponent normal draw is moving at 692/694; completed start count is not invented from that transition.', 'Opponent normal draw completes within690-692;692 shows five settled backs and current Lightning.694 is a detached played-card back with four remaining fan backs.')
        text=text.replace('moving normal draw692/694, Research696 with two hidden arrivals696/698, Order Pad702 tails704', 'normal draw bounded690-692 with five settled backs692/current Lightning, Research combined two hidden additions696-698 with individual times unresolved, Order Pad face700/coin702/tails704')
        text=text.replace(old_id,new_id)
        file.write_text(text,encoding='utf-8')
corrections=read(P,'CORRECTION_LEDGER.json')
corrections['corrections'].append({'field':'Final independent R1-R3 source reconciliation','initial_read':'Darkness-only finaledit;wrong Copycat order;moving opponent draw/current absent692;OrderPad face702.','resolved_read':'Water-only finaledit/new semanticidentity;Copycat Ball674/TRMeowth675/Pop676/Cyrus677,input667-668;opponent five backs/currentLightning692, hidden arrivals bounded, OrderPad face700. Parent firstBall consuming55-56 separate from58 display.','basis':'Frozen independent rejection plus direct root native views; initial submissions/prepared identity preserved in original_before_final_independent.','status':'resolved','corrected_utc':datetime.now(timezone.utc).isoformat()})
save(P,'CORRECTION_LEDGER.json',corrections)
for q in [P,C]:
    for name in ['SUMMARY.json','PAUSE_GAME.json','UNCERTAINTIES.json','DECK_USED.json']:
        save(q,name,replace(read(q,name),old_id,new_id))
save(P,'FINAL_INDEPENDENT_CORRECTIONS.json',{'applied_by':'/root','applied_utc':datetime.now(timezone.utc).isoformat(),'original_inputs':str(backup),'superseded_prepared_id':old_id,'corrected_prepared_id':new_id,'frozen13_unchanged_sha256':frozen13,'required_independent_recheck':True,'changes':['Waterfinalconfiguration and child next previews','Copycat exact native reveal order/inputwindow','Opponentturn2 fan/currentEnergy and combined hidden draws','OrderPad face700 versus coin702','ParentfirstBall window55-56 versus display58']})
for q in [P,C]:
    result=subprocess.run([sys.executable,str(B/'validate_packet.py'),str(q)],capture_output=True,text=True,encoding='utf-8',check=True)
    (q/'ROOT_FINAL_REPAIR_STRUCTURE_CHECK.json').write_text(result.stdout,encoding='utf-8')
    assert json.loads(result.stdout)['structural_pass'] is True
assert hashlib.sha256((B/'NEW_DECK_ENTRIES.json').read_bytes()).hexdigest()==frozen13
print('Repaired both012927 packets; new Water identity '+new_id+'; frozen13 unchanged; independent recheck required')
