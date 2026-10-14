import json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

p = Path(__file__).resolve().parent
batch = p.parent
source = json.loads((p/'SOURCE.json').read_text(encoding='utf-8'))
meta = json.loads((p/'RECORDING_METADATA.json').read_text(encoding='utf-8'))
live = json.loads((batch/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8'))
new = json.loads((batch/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8'))
candidate = next(d for d in new['decks'] if d['source_video'] == '20261004_213625000_iOS.MP4')
now = datetime.now(timezone.utc).isoformat()
video = source['video_basename']
sha = source['sha256']
game = p.name+'_game1'
bindings = [{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
base = {'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':bindings}
def save(name, value):
    (p/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def eid(t): return 'f'+f'{t:07.2f}'.replace('.','_')

labels = {
0:'Event lobby: Deluxe Pack: Mega Emblem Event, Wins 3, New deck 24.',
9:'Matched opponent profile: level 60, ゆうぜん.',
17:'Versus introduction: ゆうぜん against Dacz8976.',
22:'Opening deal animation; setup only.',
23:'All five owner opening cards before Active placement; five opponent card backs.',
24:'Original fourth opening slot Caterpie selected, card zoom; Active prompt.',
25:'Caterpie placed Active; four cards remain in owner hand.',
26:'Active Caterpie 40 HP; Bench setup prompt and four-card owner hand.',
27:'Second Caterpie placement on left Bench; three owner cards remain.',
28:'Bench Caterpie placement animation.',
29:'Bench Caterpie placement animation resolving.',
30:'Ready setup with Active and left Bench Caterpie, each 40 HP; Start Battle highlighted.',
44:'Waiting in setup: Active and left Bench Caterpie 40 HP; owner three-card hand; opponent five backs.',
44.5:'Setup board clearing animation; Caterpie cards return toward the hand.',
45:'Connection is unstable overlay; blurred setup board.',
45.5:'Connection is unstable overlay; no game turn established.',
46:'Opponent face-down Active placement during terminal transition; owner five-card hand restored.',
47:'Terminal transition white frame.',
48:'Victory animation beginning; Accelgor 80 HP shown.',
49:'Dacz8976 Victory animation with Accelgor; this card was not played.',
53:'Results header: Victory versus ゆうぜん.',
54:'Results: Victory versus ゆうぜん, turns played 0, damage done 0, Card of the Game None.',
55:'Final results: Victory versus ゆうぜん, went first, turns played 0, points 0-0, damage 0.'}
frames=[]
for t, observation in labels.items():
    name=f't{t:07.2f}'
    full=p/'turn_evidence'/f'{name}.jpg'
    with Image.open(full) as im:
        assert im.size==(1170,2532)
        im.crop((0,2025,1170,2532)).save(p/'turn_evidence'/f'{name}_bottom.png')
        im.crop((0,0,1170,620)).save(p/'turn_evidence'/f'{name}_top.png')
    frames.append({'evidence_id':eid(t),'role':'setup_or_terminal','turn_number':None,'who_played':None,
        'source_video':video,'source_sha256':sha,'draw_animation_end_seconds':None,
        'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':None,
        'full_frame_path':f'turn_evidence/{name}.jpg','native_dimensions':{'width':1170,'height':2532},
        'bottom_crop':{'path':f'turn_evidence/{name}_bottom.png','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
        'top_crop':{'path':f'turn_evidence/{name}_top.png','pixel_bounds_x0_y0_x1_y1':[0,0,1170,620]},
        'selected_for_start_hand':False,'before_first_play': t==23,'unzoomed':t in [23,26,30,44,46],
        'hand_spread':t in [23,26,30,44,46],'observation':observation,
        'suitability_or_limit':'Setup/result evidence, not a draw-timed turn frame. No game turn occurred.'})
limits = [
    'The game awarded Victory before a turn began. Results explicitly show 0 turns played and 0 damage. There are no owner/opponent game-turn rows or draw-relative captures to create.',
    'Connection instability is directly visible before Victory. Its exact server cause, and whether any player deliberately conceded, are not shown.',
    'Opponent Pokemon identities are never revealed. One face-down Active appears during the terminal transition.',
    'No opened discard piles or battle-log scroll are shown. No in-turn card play, search, normal draw, attachment or attack occurs.',
    'No deck QR or complete list is shown in this source. A same-label earlier source QR is a candidate only; no uninterrupted recording proves the list was unchanged across sources.',
    'Seek times are source-local requested positions. Exact decoded frame PTS has not been measured.'
]
opening_names=['Caterpie','Quick-Grow Extract','Butterfree','Caterpie','Lucky Ice Pop']
opening=[{'position':i+1,'name':n,'variant':{'Caterpie':'Quick Growth / Hook, 40 HP','Butterfree':'Sunny Wind, 130 HP'}.get(n),
          'basis':'visible opening card face','evidence_ids':[eid(23)],'limit_reason':None} for i,n in enumerate(opening_names)]
actions=[
    {'order':1,'kind':'setup_active_placement','card_name':'Caterpie','opening_position':4,'timestamp_seconds':24,'result':'Active, 40 HP','evidence_ids':[eid(24),eid(25)]},
    {'order':2,'kind':'setup_bench_placement','card_name':'Caterpie','opening_position':1,'timestamp_seconds':27,'result':'left Bench, 40 HP','evidence_ids':[eid(27),eid(30)]},
    {'order':3,'kind':'setup_ready','card_name':None,'timestamp_seconds':30,'result':'Start Battle highlighted; controls disappear by the 30.75 s overview; waiting for opponent','evidence_ids':[eid(30)]}
]
pokemon={'name':'Caterpie','variant':'Quick Growth / Hook','current_hp':40,'maximum_hp':40,'damage':0,
         'energy_count':0,'energy_by_type':[],'tool':'none','special_conditions':[],'active_effects':[]}
zone={'this_turn':None,'next':{'type':'Grass','basis':'visible Grass preview icon'},
      'limit_reason':'Setup Energy Zone previews do not display a generated current-turn Energy or this/next line text.'}
setup_board={'phase':'after owner placement / waiting for opponent','timestamp_seconds':44,'turn_number':None,
    'owner':{'active':pokemon,'bench_in_position_order':[dict(pokemon,position=1)],'empty_bench_positions':[2,3],
             'points':None,'energy_zone':zone},
    'opponent':{'active':None,'bench_in_position_order':[],'points':None,'energy_zone':zone,
                'limit_reason':'No opponent Pokemon has been placed visibly at this setup boundary. Points UI is not yet shown.'},
    'stadium':'none','evidence_ids':[eid(44)],'points_limit':'Results later confirm points 0-0.'}
save('PAUSE_GAME.json',dict(base,review_date=now,destination='https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
    deck_name='Butterfree / Accelgor (visible core; exact version uncertain)',
    opening={'source_video':video,'timestamp_seconds':23,'expected_card_slots':5,'recorded_card_count':5,
        'cards_left_to_right':opening,'selected_active':{'name':'Caterpie','opening_position':4,'source_video':video,
        'timestamp_seconds':24,'evidence_ids':[eid(24),eid(25)]},
        'redraw_or_replacement':{'observed':False,'basis':'Initial opening retained through setup; later board/hand restoration is a terminal connection transition, not an observed new opening deal.'},
        'before_active_placement':True,'status':'complete','evidence_ids':[eid(23)],'limit_reason':None},
    setup_actions_in_order=actions,setup_board_after_owner_ready=setup_board,
    setup_owner_hand_after_ready={'names_left_to_right':['Quick-Grow Extract','Butterfree','Lucky Ice Pop'],'count':3,'evidence_ids':[eid(30),eid(44)]},
    setup_opponent_hand={'count':5,'count_method':'Five distinct visible card backs at 23 s and 44 s','identities':None,
        'limit_reason':'Hidden card faces','evidence_ids':[eid(23),eid(44)]},
    packet_files={'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},
    capture_status='complete_with_recording_limits',battle_review_status='full_source_and_terminal_review_complete_pending_lead',
    outcome='win',limits=limits,lead_checked=False))
save('TURN_LEDGER.json',dict(base,turns=[],recorded_game_turn_count=0,
    empty_ledger_basis='Results at 54-55 s explicitly show Turns played 0. All observed owner actions belong to opening setup. No turn 0 or fabricated turn 1 is inserted.',
    setup_record='PAUSE_GAME.json',terminal={'outcome':'win','turns_played':0,'points':{'owner':0,'opponent':0},'damage_done':0,
        'evidence_ids':[eid(54),eid(55)]},limits=limits))
save('TURN_EVIDENCE.json',dict(base,default_capture_policy={'owner_turn_offsets_after_draw_seconds':[1,3,6],
    'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,
    'fixed_grid_is_turn_start_evidence':False},frames=frames,discard_snapshots=[
        {'snapshot_id':'discard-owner-unavailable','pile_owner':'owner','cards_in_view':None,'scroll_coverage':None,'full_pile_established':None,'limit_reason':'Discard pile was never opened; no turn or discard action occurred.'},
        {'snapshot_id':'discard-opponent-unavailable','pile_owner':'opponent','cards_in_view':None,'scroll_coverage':None,'full_pile_established':None,'limit_reason':'Discard pile was never opened; no turn or discard action occurred.'}],
    scheduled_capture_limits=['No normal game-turn draw occurred, so +1/+3/+6 and before-End-Turn captures are inapplicable. Native opening/setup/terminal frames and crops are retained.']))
save('DECK_CANDIDATE_EARLIER_QR.json',candidate)
save('DECK_USED.json',dict(base,deck_name_in_log=None,filmed_deck_label='New deck 24',
    visible_core=['Caterpie (Quick Growth)','Butterfree (Sunny Wind)','Quick-Grow Extract','Lucky Ice Pop','Accelgor (Deck and Cover; result animation only)'],
    source_url=live['source_url'],captured_at=live['retrieved_utc'],log_list_version=None,expected_card_count=20,
    cards_in_log_order=None,counts_by_name_and_variant=None,energy_configuration_from_log=None,
    observed_energy_preview=['Grass'],actual_card_count=None,capture_source_text_or_image='../LIVE_DECK_SNAPSHOT.json',
    game_version_binding_basis='New deck 24 label and visible core agree with earlier 213625 QR candidate. This source starts at an event lobby; intervening deck edits are unrecorded. Candidate is not a verified exact game list.',
    conflicts_with_filmed_cards='No filmed conflict with candidate; no current nine-list live snapshot fully matches the Grass core.',
    exact_list_status='unavailable_game_version_unverified',candidate_deck_reference='DECK_CANDIDATE_EARLIER_QR.json',
    candidate_20_card_slots_verified_in_earlier_source=True,candidate_exact_game_binding_verified=False,
    limits=[limits[4],'Earlier candidate is prepared as a new deck entry, external_saved false in frozen NEW_DECK_ENTRIES.json. It is not an exact live-log snapshot for this game.']))
relationships=[
 {'other_source':'20261004_213625000_iOS.MP4','relationship':'separate_previous_match',
  'basis':'Peer native frame at local 459 s explicitly shows Defeat versus Noytamon; this source begins new event matchmaking and introduces ゆうぜん.',
  'evidence_path':'../20261004_213625000_iOS/turn_evidence/t0459.00.png'},
 {'other_source':'20261004_214731000_iOS.MP4','relationship':'separate_later_match',
  'basis':'Peer native_01 contact sheet includes new five-card setup at local 24.5 s, going second, different opening and opponent red-R sleeves; subsequent ordinary board names CloutDemon. This source ends Victory versus ゆうぜん.',
  'evidence_path':'../20261004_214731000_iOS/native_01.jpg'}]
save('SUMMARY.json',{'game_id':game,'source_video':video,'source_sha256':sha,'reviewer':'/root/pause_214518',
    'review_model':'gpt-6.1-sol','reasoning_effort':'high','review_date':now,
    'scope':'Entire 55.216667-second source: event lobby, new matchmaking, opening setup, waiting/connection transition, Victory and final results.',
    'classification':'human_opponent','recording_type':'complete_setup_only_match_with_terminal_result',
    'mode':'Deluxe Pack: Mega Emblem Event','auto_control_observed':False,'auto_enabled':None,
    'auto_limit':'No Auto control or option appears; no menu is opened. Human event matchmaking/profile is visible.',
    'opponent':'ゆうぜん','opponent_level':60,'owner':'Dacz8976','match_date':meta['match_date_local'],
    'outcome':'win','points':[0,0],'turn_count':0,'damage_done':0,
    'source_continuity':'New match from event lobby through final Victory. No linked continuation needed. No visible recording cut.',
    'source_relationships':relationships,'capture_status':'complete_with_recording_limits',
    'worker_disposition':'ready_for_bounded_independent_check_and_lead_acceptance',
    'acceptance_status':'awaiting_independent_review','full_source_review_complete':True,
    'independent_check_candidates_seconds':[0,9,17,23,24,27,30,44,44.5,45.5,46,49,55],
    'important_findings':['Results explicitly show 0 turns, 0 damage and 0-0 points with Victory. No fabricated turn ledger rows.',
        'All five opening card names and chosen Active slot are visible.',
        'Connection instability precedes Victory; the exact termination cause is unknown.',
        'Exact 20-card game deck cannot be bound from this source; earlier QR candidate retained separately.'],
    'limits':limits})
save('UNCERTAINTIES.json',{'source_video':video,'source_sha256':sha,'reviewer':'/root/pause_214518',
    'unreviewed_intervals':[],'consequential_ambiguities_requiring_astra':[],
    'items':[{'id':'termination-cause','question':'Why was the setup match awarded Victory?','status':'unresolved_recording_limit',
        'observed':'Connection is unstable at 45-45.5 s; Victory at 48-49 s and final results at 55 s.','not_established':'Concession, opponent fault, network adjudication or server reason.',
        'evidence_ids':[eid(45.5),eid(49),eid(55)]},
        {'id':'exact-deck-version','status':'unresolved_recording_limit','question':'Did the earlier New deck 24 QR remain unchanged for this game?',
        'observed':'Lobby label and opening core agree.','not_established':'Exact 20-card list, intervening edits or direct same-source QR.',
        'evidence_ids':[eid(0),eid(23)]},
        {'id':'opponent-cards','status':'hidden_information','question':'Opponent Active and hand identities?',
        'observed':'Five card backs during setup; face-down Active in terminal transition.','not_established':'Any opponent card name.',
        'evidence_ids':[eid(23),eid(44),eid(46)]}]})

(p/'REVIEW.md').write_text('''# Complete source review: 20261004_214518000_iOS.MP4

Reviewer: /root/pause_214518, gpt-6.1-sol, high. Review date: 2026-10-06. Independent acceptance and all shared registration, external logging and archival remain the lead's responsibility.

Dacz8976 receives an explicit Victory against ゆうぜん (level 60) in Deluxe Pack: Mega Emblem Event. The match ends during setup, with 0 turns played, 0 damage and 0-0 points on the final results. The complete 55.216667-second supplied source contains a new matchmaking sequence and terminal result. It is a separate match, not a clipped ending or continuation of another recording.

Source binding: SOURCE.json, 77,196,172 bytes, SHA-256 55de49ce96ee9aa524c81f86245cf9af455700f6cd59d5146fe97e2f58b4cf0e, native 1170 x 2532. Embedded date companion establishes local match date October 4, 2026. SOURCE.json was preserved unchanged.

No Auto option appears in the inspected source. The visible event lobby, search for opponent and matched human profile support human-opponent classification. No Auto menu was opened. Owner setup choices are visible; no gameplay turn or automated choice occurs.

| Source-local time | Observed phase and actions | Evidence |
|---|---|---|
| 0-2 s | Event lobby shows Wins 3 and selected New deck 24. Battle matchmaking starts. | f0000_00, qr_intake/t0001.00.png; overview sheet 1 |
| 2-11 s | Searching, opponent found, level 60 profile ゆうぜん. | f0009_00; overview sheet 1 |
| 11-22 s | Loading, versus introduction against Dacz8976, board and deal animation. | f0017_00, f0022_00; overview sheets 1-2 |
| 22-24 s | Five-card opening: Caterpie, Quick-Grow Extract, Butterfree, Caterpie, Lucky Ice Pop, left to right. Going first. Original slot 4 Caterpie selected. | f0023_00, f0024_00; setup_dense sheet 1 |
| 24-26 s | Setup action 1: chosen Caterpie placed Active, 40/40 HP. Four cards remain. | f0025_00, f0026_00 |
| 26-30 s | Setup action 2: original slot 1 Caterpie placed on left Bench, 40/40 HP. Setup action 3: Start Battle highlighted near 30 s and controls disappear by the 30.75 s overview sample. Remaining hand is Quick-Grow Extract, Butterfree, Lucky Ice Pop. | f0027_00, f0030_00; setup_dense sheet 2 |
| 30-44.25 s | Waiting for opponent. Owner Active/left Bench Caterpie each remain 40 HP with no attachments, Tools or conditions. Other two Bench positions empty. Opponent has five backs and no visibly placed Pokemon. Both setup Energy previews are Grass; no generated current-turn Energy is displayed. No Stadium or turn number. | f0044_00; overview sheets 2-3; ending_dense sheet 1 |
| 44.25-46.5 s | Board clears and owner Caterpies return to the five-card hand. Connection is unstable overlay appears at 45-45.5 s. Opponent face-down Active appears by 46 s, with hidden identity; point circles show zero. No turn starts. | f0044_50, f0045_50, f0046_00; ending_dense sheet 1 |
| 46.5-50 s | Terminal transition and Dacz8976 Victory animation. Accelgor (80 HP, Deck and Cover) is shown as result art, not a played Pokemon. | f0048_00, f0049_00; ending_dense sheet 2 |
| 50-55.216667 s | Loading then final Victory vs. ゆうぜん. Results show Went first, Turns played 0, Card of the Game None, both points zero and Damage done 0. Source ends on those results. | f0054_00, f0055_00; ending_dense sheet 3 |

Opening setup is recorded separately in PAUSE_GAME.json. TURN_LEDGER.json intentionally contains zero rows, matching the actual zero-turn match. There is no invented turn 0 or turn 1. No normal turn draw, Research, search, ability, Trainer play, Energy attachment, retreat, attack, knockout, End Turn prompt or discard-pile inspection occurs. Draw-end +1/+3/+6 captures and before-End-Turn views therefore do not apply. The native opening/setup/result full frames and bottom/top crops are retained in turn_evidence and described in TURN_EVIDENCE.json.

The opponent fan has five distinct card backs before setup placement and at the waiting boundary. The identities are hidden. At the terminal transition the opponent places one face-down Active; it is not assigned a guessed species. Current/next Energy line values at game-turn boundaries do not exist because no turn begins; the visible Grass setup previews are recorded as previews.

Connection instability is observed immediately before Victory. The source does not say that the opponent conceded or disconnected, or which network/server condition caused the award. The result is verified, while the termination cause remains unknown. This zero-turn win supports no tactical quality assessment.

DECK_USED.json preserves the absent exact-game-list limit. New deck 24 and the visible Grass core agree with an earlier filmed QR from 20261004_213625000_iOS.MP4, but this source contains no QR or complete list and does not record the intervening interval. The earlier candidate 20-card list is retained in DECK_CANDIDATE_EARLIER_QR.json, not asserted as this game's verified version. The frozen nine live lists contain no matching Grass deck.

The neighboring clips are separate games on actual evidence. The 213625 packet's native 459 s frame shows Defeat versus Noytamon. This source starts fresh event matchmaking against ゆうぜん. The 214731 packet's native_01 sheet shows fresh setup at local 24.5 s, going second, a different opening and red-R opponent sleeves, then ordinary play naming CloutDemon. This source already ends Victory versus ゆうぜん. No split-source joining or duplicate result is warranted.

All phases of this supplied source have been visually reviewed using the source-wide 2-second overview, denser 0.5-second setup/terminal windows and native detail frames. Static waiting has been checked against matching boundary states. This is not a claim that every decoded frame was individually read. Exact requested seek times are retained; frame PTS was not measured. No source intervals remain unreviewed and no consequential ambiguity needs Astra to establish the outcome.
''',encoding='utf-8')
(p/'COVERAGE.md').write_text('''# Coverage and independent-check handoff

Whole source: 0-55.216667 seconds reviewed. One distinct setup-only human event match with explicit terminal Victory. No recording continuation is needed.

- Lobby/matchmaking/introduction, 0-22 s: covered by source-wide overview and native lobby/profile/VS/deal views.
- Full opening and setup choices, 22-30.75 s: covered by 0.5-second setup overview and native 23/24/25/26/27/30 s frames.
- Static waiting, 30.75-44.25 s: covered by source-wide overview, with matching native setup state at 44 s.
- Board restoration, connection overlay, hidden opponent placement, 44.25-46.5 s: covered by 0.5-second terminal overview and native 44.5/45/45.5/46 s frames.
- Victory/results through source end, 46.5-55.216667 s: covered by dense overview and native 48/49/53/54/55 s views.
- Zero game turns: explicit result evidence at 54-55 s. Zero ledger rows is intentional, not missing coverage.
- Opening five slots and chosen Active: captured and named. Native full frames plus bottom-fifth/top crops retained.
- Draw/search/turn-action and before-End-Turn supplement: inapplicable because no turn occurs.
- Discard views: none opened, no discard actions; recorded as unavailable.
- Exact deck: source lacks QR/full list; earlier same-label candidate kept separately, exact game version unverified.

Worker recommendation: eligible for independent acceptance as a fully reviewed terminal match, with recording limits. Lead must independently check before registration or external entry. No LEAD_ACCEPTANCE file was created by the worker.

Bounded check set: 23 s opening, 24-25 s fourth-slot Active choice, 27/30 s second Caterpie Bench and ready choice, 44 s waiting state, 44.5-46 s board restoration/connection transition, 49 s Victory, 55 s explicit zero-turn result. Also compare neighboring sources using SUMMARY.json relationships. No ordinary turn or draw/search order exists to sample.

No external log, review events/index, source moves, location map or source binding were changed by this worker.
''',encoding='utf-8')
print('Wrote setup-only terminal review packet with',len(frames),'native evidence frames and zero game turns.')
