import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

P = Path(__file__).resolve().parent.parent
required = ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
read = lambda name: json.loads((P/name).read_text(encoding='utf-8-sig'))
S = read('SOURCE.json'); M = read('SUMMARY.json'); G = read('PAUSE_GAME.json'); D = read('DECK_USED.json'); T = read('TURN_LEDGER.json'); E = read('TURN_EVIDENCE.json')
assert S['sha256'] == 'dbf23091859cbe159afc724f32f517f75925ab214343474285306b035ee4146e'
assert [t['turn_number'] for t in T['turns']] == [1,2,3,4]
assert [c['name'] for c in G['opening']['cards_left_to_right']] == ['Horsea','Kingdra ex','Small Balloon','Soothing Shore','Copycat']
assert G['opening']['selected_active']['name'] == 'Horsea'
assert M['owner'] == 'Dacz8976' and M['opponent'] == '\u30e6\u30aa\u30ab'
assert M['outcome']['concession'] is False and M['outcome']['final_points'] == {'owner':1,'opponent':0}
assert M['classification'] == 'human' and M['turn_count'] == 4 and M['source_game_count'] == 1
t2, t4 = T['turns'][1], T['turns'][3]
assert t2['plays_in_order'][0]['card_name'] == 'Soothing Shore'
assert t2['owner_hand_end']['count'] == 3 and t4['owner_hand_end']['count'] == 2
assert t2['hand_at_start']['count'] == 5 and t4['hand_at_start']['count'] == 4
assert [c['name'] for c in t2['draws_and_searches'][1]['cards_in_reveal_order']] == ["Team Rocket's Koffing",'Rare Candy']
assert t4['draws_and_searches'][0]['cards_in_reveal_order'][0]['name'] == 'Sabrina'
assert t2['board_after']['turn_number_displayed'] == 3
assert t2['board_at_start']['owner']['energy_zone']['this_turn']['available'] is not True
assert t4['board_after']['owner']['active']['attached_energy']['by_type'] == {'Water':2}
assert t4['board_after']['opponent']['active'] is None
assert len(D['cards_in_log_order']) == 20 and sum(c['count'] for c in D['counts_by_name_and_variant']) == 20
L = read('../LIVE_DECK_SNAPSHOT.json')
live = next(d for d in L['decks'] if d['label'] == D['deck_name_in_log'])
assert D['captured_source_text'] == live['captured_source_text']
expected = [{'name':c['name'],'variant':c['variant']} for c in live['counts_by_name_and_variant'] for _ in range(c['quantity'])]
assert D['cards_in_log_order'] == expected
assert D['energy_configuration_from_log'] == 'Water'
assert any(f['evidence_id']=='t0106.40' and f['selected_for_start_hand'] for f in E['frames'])
for name in required:
    content = (P/name).read_text(encoding='utf-8-sig')
    assert not any(term in content for term in ['Pok\u00c3','Professor\u00e2','\ufffd']), name+' contains corrupted authored text'
hashes = {name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in required}
stamp = datetime.now(timezone.utc).isoformat()
result = {'accepted':True,'status':'accepted_with_recording_limits','source_video':S['video_basename'],'source_sha256':S['sha256'],'reviewer':'/root/verify_pause_004128','model':'gpt-6.1-sol','reasoning_effort':'high','checked_at_utc':stamp,'acceptance_scope':'Bounded independent verification of completed full-review packet using selected source evidence, not a second full decode or replay. Lead remains responsible for registration, archival and external logging.','required_repairs':[],'resolved_repairs':['Added dense native106.4 unzoomed preplay hand and crops for owner turn4.','Corrected turn2 ending boundary displayed turn number to3, retaining logical resolved turn2.','Qualified current Energy slot at selected53.2 frame before generation animation settled.','Normalized deck count field and rebuilt imported deck text/names from the correct UTF-8 live snapshot.'],'accepted_input_sha256':hashes,'checked_supporting_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['SOURCE.json','QR_DECODE.json','../LIVE_DECK_SNAPSHOT.json','independent_sol/VIEWED_EVIDENCE.json']},'source_identity_checks':{'independent_source_rehash_match':True,'size_bytes':245906067,'native_dimensions':[1170,2532],'independent_native_seeks':[27,121],'seek_jpeg_hash_matches':True},'outcome_verified':{'owner':'Dacz8976','opponent':'\u30e6\u30aa\u30ab','result':'win','method':'last opposing Pokemon knocked out','concession':False,'final_points':{'owner':1,'opponent':0},'victory_source_seconds':131,'turn_count':4},'capture_status':'complete_with_recording_limits','viewed_manifest':'VIEWED_EVIDENCE.json','limits':['Hidden opponent identities and unopened discard piles are unavailable.','Draw/turn timings are approximate requested seeks, not separately measured encoded PTS.','Queue rank/casual label remains unknown; no Auto option was observed.','Warning response is supported by prompt disappearance and immediate attack, without an on-screen tap marker.','Fresh QR pixel reread was unavailable because selected runtime lacks cv2. Retained image was visually inspected; payload binary decode,20 slots,Water,receipt image/source hashes and exact live payload/count equality were independently checked.','Match date2026-10-11 uses creation_time verified by lead and Chicago conversion corroborated by phone clock.']}
(P/'independent_sol/CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review = f'''# Independent bounded verification

Accepted with recording limits. Reviewer /root/verify_pause_004128, gpt-6.1-sol, high reasoning. Checked {stamp}. Source20261012_004128000_iOS.MP4, SHA-256 {S['sha256']}. This verifies the final full-review packet against selected native source evidence and retained action sequences. It is not a second full video replay.

The source rehash matches intake. Independent source seeks at27s and121s exactly match retained JPEG hashes. VIEWED_EVIDENCE.json lists30 visually inspected native/crop/action-sheet entries. All8 final inputs are sealed in CHECK_RESULT.json.

The five opening slots are Horsea, Kingdra ex, Small Balloon, Soothing Shore, Copycat; Horsea is selected Active. One match is shown, Dacz8976 versus ユオカ, with no observed Auto option. All4 turn rows and the source coverage/prose agree. Exact queue label remains unknown.

Ordinary owner turn2 starts with5 cards and first plays Soothing Shore. Professor's Research then reveals Team Rocket's Koffing before Rare Candy. Koffing is benched left, Water goes to Horsea, Small Balloon goes to Koffing, and Hook deals30 to Slowpoke90->60. Ending hand is Kingdra ex, Copycat, Rare Candy (3). Opponent Water attachment and Soothing Shore healing leave Slowpoke80/90 at owner turn4. Both boundary boards and zones reconcile after the documented label corrections.

The dense106.4 frame clearly shows owner turn4 starting hand Kingdra ex, Copycat, Rare Candy, Sabrina, before the first Rare Candy play. Evolution preserves Horsea's Water and a second Water is attached to Kingdra. Ending hand is Copycat,Sabrina (2). Opponent fan counts are4 and5 at owner turns2 and4. No discard pile is opened; public top/history is explicitly partial.

Stormy Prison90 is followed by Slowpoke0HP, the empty opponent board, point1-0, and the owner Victory screen131s. This supports a last-Pokemon knockout win with no concession. The117s warning continuation is an inference from disappearance and immediate attack, and is labeled accordingly.

The filmed receipt's payload exactly equals the dated live Kingdra ex / Team Rocket's Weezing ex code. Independent binary decode establishes11 Trainers,9 Pokemon,Water and complete payload consumption; semantic counts match the20-slot snapshot. Correct UTF-8 source text and exact log variants are preserved. QR does not establish artwork/rarity or hidden draws. This checker did not freshly decode QR pixels because cv2 is absent in the selected runtime.

Resolved repairs: dense preplay hand capture, displayed boundary turn3 after owner turn2, pre-generation Energy slot qualification, deck count-field normalization and UTF-8 deck source preservation. No required repairs remain. Hidden opponent faces, unopened discard piles, approximate timing, exact queue label and prompt tap remain recording limits. Lead completion, registration, source archival and external save verification are separate responsibilities.
'''
(P/'independent_sol/REVIEW.md').write_text(review,encoding='utf-8')
print(json.dumps({'accepted':True,'status':result['status'],'sealed_inputs':len(hashes),'required_repairs':[]},indent=2))
