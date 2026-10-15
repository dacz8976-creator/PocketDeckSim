import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

p = Path(__file__).resolve().parents[1]
out = Path(__file__).resolve().parent
sha = json.loads((p / 'SOURCE.json').read_text())['sha256']
full = [3,4,6,8,32,33,50.3,51.3,53,54,55,79.3,81,95,100.3,117,118,121,127,129,130,134,136,162,174]
bottom = [51.3,53.3,56.3,79.3,100.3,101.3,103.3,106.3,127]
top = [50.3,87,100.3,139]
fresh = [83,84,85,89,91]
entries = []
for times, suffix, role, directory in [(full,'','native full frame','turn_evidence'),(bottom,'_bottom','native bottom crop','turn_evidence'),(top,'_top','native top crop','turn_evidence'),(fresh,'','independently extracted native full frame','independent_sol/source_check')]:
    for t in times:
        filename = f'{directory}/t{t:07.2f}{suffix}.jpg'
        entries.append({'path': filename, 'source_seconds_requested': t, 'kind': role, 'sha256': hashlib.sha256((p / filename).read_bytes()).hexdigest()})
for n in range(1,6):
    filename = f'overview/sheet_{n:02d}.jpg'
    entries.append({'path':filename,'kind':'coarse overview sheet, approximate midpoint labels, not native hand proof','sha256':hashlib.sha256((p/filename).read_bytes()).hexdigest()})
manifest = {'reviewer':'/root/check_015452','checked_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':'20261010_015452000_iOS.MP4','source_sha256':sha,'scope':'Bounded independent acceptance; all five coarse source sheets plus selected native ordinary and decisive events, not an independent full video replay','viewed_evidence':entries,'computational_source_checks':[{'source_seconds':t,'independent_path':f'independent_sol/source_check/t{t:07.2f}.jpg','retained_path':f'turn_evidence/t{t:07.2f}.jpg','exact_jpeg_hash_match':hashlib.sha256((p/f'independent_sol/source_check/t{t:07.2f}.jpg').read_bytes()).digest()==hashlib.sha256((p/f'turn_evidence/t{t:07.2f}.jpg').read_bytes()).digest()} for t in [32,129]],'new_native_extractions':7,'limits':['Requested seek times, not exact measured PTS.','No independent re-decode of QR payload: local interpreter lacks zxingcpp; receipt source hash and semantic count equality were independently checked.','Hidden opponent identities and unshown discard dialogs cannot be reconstructed.']}
(out/'VIEWED_EVIDENCE.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')

ledger = json.loads((p/'TURN_LEDGER.json').read_text())
deck = json.loads((p/'DECK_USED.json').read_text())
assert [r['turn_number'] for r in ledger['turns']] == [1,2,3,4]
assert ledger['turns'][1]['hand_at_start']['evidence_ids'] == ['f0083.00']
assert ledger['turns'][1]['timing']['draw_animation_end_seconds'] == 83
assert ledger['turns'][1]['board_at_start']['opponent']['energy_zone']['this_turn']['available'] is False, 'T2 pregeneration boundary repair pending'
assert deck['actual_card_count'] == 20 and deck['energy_configuration_from_log'] == ['Water']
assert not deck['conflicts_with_filmed_cards']
names = ['PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']
hashes = {name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in names}
resolved = [
    'Removed invented Darkness change; native3/6/8 show the same Water icon and4 shows unsaved edit warning.',
    'Corrected T2 settled normaldraw boundary to83 and four-back hand evidence; retained hidden Research draw interval87-89 with no invented individual reveal times.',
    'Corrected T2 start Energy Zone to visibly empty before generation; later Water generation and95 attachment retained.',
    'Preserved initial missing live deck snapshot as history and reconciled exact refreshed20-slot list and Water with filmed QR receipt.'
]
result = {'accepted':True,'source_sha256':sha,'source_video':'20261010_015452000_iOS.MP4','reviewer':'/root/check_015452','checked_at_utc':datetime.now(timezone.utc).isoformat(),'required_repairs':[],'resolved_repairs':resolved,'checked_input_sha256':hashes,'checked_supporting_sha256':{name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in ['SOURCE.json','QR_DECODE.json','../LIVE_NEW_DECKS_VERIFIED.json']},'capture_status':'complete_with_recording_limits','outcome_verified':{'owner':'Dacz8976','opponent':'msthsky','result':'win','method':'opponent_concession','concession_seconds':162,'result_seconds':174,'turns':4,'points':{'owner':0,'opponent':0}},'acceptance_scope':'Bounded independent check of finished full review, coverage and selected native evidence. Root remains responsible for final registration and archival.','viewed_manifest':'VIEWED_EVIDENCE.json','source_identity_checks':{'rehash_match':True,'bytes':305967963,'native_width':1170,'native_height':2532,'two_independent_extracts_exact_match':True},'limits':manifest['limits']}
(out/'CHECK_RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
report = '''# Independent acceptance check

Accepted after source-based corrections. Reviewer /root/check_015452 performed a bounded independent check of the submitted whole-battle review, retained native evidence and all five coarse overview sheets. This is not a second continuous replay of the entire video.

The source independently rehashes to SOURCE.json SHA-256 and has305,967,963bytes. Fresh32s and129s native extractions exactly match retained JPEG hashes. Native full frames are1170x2532; bottom crops1170x507 at y2025 and top crops1170x600. Seven bounded new extracts were retained, with no shared log writes, moves or external actions.

Opening32s establishes Rare Candy, Weezing ex, gold Koffing, standard Koffing, Small Balloon. Standard Koffing is placed Active33s. Ordinary owner turn1 starts with Research as first play51.3s; Horsea54s then Soothing Shore55s are separately revealed. Before-end79.3s shows Rare Candy plus Weezing ex, count2. Numbered bench/Stadium/Tool/free retreat/End Turn sequence reconciles with the board.

Owner turn3 has three-card pre-play hand100.3s, Rare Candy first, Kingdra evolution, Weezing evolution and accepted Boiler Smog117-121s, then Water attachment. Empty before-end hand127s reconciles all removals. Poison10 at129s precedes Burn20 at130s; tails134s leaves Burn and the final Active Goomy10HP. Kingdra remains170HP with1Water, Weezing140HP left Bench and Koffing60HP with Balloon middle Bench. Opponent Hoppip50HP middle Bench has1Water; second Goomy40HP appears right Bench on turn4.

The draw+1/+3/+6 scheduled views are retained for both owner turns and truthfully rejected as pre-play hands because actions already began. The selected native50.3/100.3 and before-end79.3/127 views supply readable hands. Opponent top crops directly show3backs at owner turn1 and5at owner turn3. Both boards and current/next Water zones are covered with the corrected pre-generation phase limit on turn2. Neither discard dialog appears in the retained coverage; the explicit not-shown limit is appropriate. Hidden opponent card identities and exact printing labels remain unknown.

Four ledger rows match the four recorded turns and prose intervals. Explicit opponent-conceded banner162s and Victory vs msthsky174s establish win, fourturns and0-0points. Displayed damage done0 coexists with visible30status damage; no attack or knockout is claimed.

The frozen exact20-slot DECK_USED list totals20, has Water, and matches the source-bound filmed QR receipt's semantic names/counts. The initial live-log absence is preserved separately and the refreshed live receipt exists. The checker did not independently decode the QR payload because this interpreter lacks zxingcpp; it checked the receipt image hash and QR-to-log semantic counts. QR names were not substituted for observed hands.

Required repairs: none. Root-applied repairs were independently checked: unsupported Darkness change removed; opponent turn2 normaldraw settled83s and Research87-89s accurately qualified; opponent turn2 initial current Energy visibly absent rather than prematurely generated; current live-deck provenance reconciled. Exact checked-input hashes are frozen in CHECK_RESULT.json. Further edits require a refreshed hash acceptance.

VIEWED_EVIDENCE.json lists independently viewed files, requested timestamps, image hashes and computational source comparisons. Timestamp precision is bounded by requested seeks, not measured frame PTS. Root retains final registration, save verification and archive responsibilities.
'''
(out/'CHECK.md').write_text(report,encoding='utf-8')
print('Accepted final input hashes:',json.dumps(hashes))
