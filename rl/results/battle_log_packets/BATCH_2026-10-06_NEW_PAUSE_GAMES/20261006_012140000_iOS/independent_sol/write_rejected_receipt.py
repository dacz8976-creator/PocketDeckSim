import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

out=Path(__file__).resolve().parent
p=out.parent
check=json.loads((out/'INTEGRITY_CHECK.json').read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
submission=json.loads((p/'SUBMISSION_RECEIPT.json').read_text(encoding='utf-8'))
supp=check['supplemental_checked_input_sha256'].copy()
c=json.loads((p/'QUALIFIED_DECK_CANDIDATE.json').read_text(encoding='utf-8'))['candidate']
qr=Path(c['QR_receipt']); q=json.loads(qr.read_text(encoding='utf-8'))
supp[str(qr)]=sha(qr)
supp[q['retained_image']]=sha(Path(q['retained_image']))
changed=[n for n,h in check['checked_input_sha256'].items() if sha(p/n)!=h]
manifest_mismatches=[n for n,v in submission['file_manifest'].items() if (p/n).is_file() and sha(p/n)!=v['sha256']]
affected=[{'turn_number':r['turn_number'],'field':k+'.turn_number_displayed','value_before':r[k]['turn_number_displayed'],'evidence_ids':r[k]['evidence_ids']} for r in ledger['turns'] for k in ['board_at_start','board_after'] if not(r['turn_number']==5 and k=='board_after')]
viewed=[0,20,23.5,25,38,50,51,56,59,60,60.5,61,62.5,64,65.5,75,76,84,89,90,91,92,94,96,98,99,100,101,102,103,104,106,107.5,108.5,110.5,113.5,114,123,126,145,147,149,150,151,153,154,157.5,158,160,162,163,164,165,166,167,168,173,173.5,174,174.5,175,178,182,186,202,203,204,214.8]
receipt={
 'schema':'battle-review/independent-sol-acceptance-v1',
 'reviewer':'/root/independent_012140',
 'review_model':'gpt-6.1-sol',
 'reasoning_effort':'high',
 'reviewed_utc':datetime.now(timezone.utc).isoformat(),
 'source_video':'20261006_012140000_iOS.MP4',
 'source_sha256':'2fbf36e1f6d45a8e7fc6b1d273b0dc64c106ce1df14ac0447617e413ad79cf4e',
 'duration_seconds':215.053333,
 'scope':'Fresh bounded independent checks of first-pass packet, all required captures and boundary claims, ordinary opening/first owner decision/opponent turn, consequential draws, T6, terminal. Separate from the whole-source first pass. No media redecoding or second full review claimed.',
 'accepted':False,
 'decision':'rejected_pending_surgical_repairs',
 'checked_input_sha256':check['checked_input_sha256'],
 'supplemental_checked_input_sha256':supp,
 'input_changed_during_review':changed,
 'submission_manifest_mismatches':manifest_mismatches,
 'native_frames':180,
 'crop_count':360,
 'crop_integrity':{'receipt':'INTEGRITY_CHECK.json','dimensions_match':all(v['dimensions_match'] for r in check['crop_checks'] for v in r['crops'].values()),'maximum_mean_absolute_pixel_error':max(v['mean_absolute_pixel_error'] for r in check['crop_checks'] for v in r['crops'].values()),'interpretation':'All declared crops correspond to their native full frames. Small pixel differences are JPEG re-encoding, maximum channel mean error below 0.8/255. Native size1170x2532; bottom[0,2025,1170,2532]; top[0,0,1170,620].'},
 'viewed_source_seconds':viewed,
 'evidence_checked_sha256':{f['full_frame_path']:sha(p/f['full_frame_path']) for f in evidence['frames'] if f['requested_source_seconds'] in viewed},
 'checks_passed':[
  'Opening23.5 has Scolipede/Poke Ball/Research/Whirlipede/Venipede, all five slots before placement. Venipede Active by25.',
  'Ordinary first owner decision59-66: Whirlipede normal draw59, five intact cards60, Ball selected60.5 and consumed by61, Mega Sableye ex reveal64, center bench placement by65.5. Input consumption is separate from reveal.',
  'Research reveal order75 Mega Sableye ex,76 Wally. EndingT2 hand84 has Scolipede/Whirlipede/Whirlipede/Wally count4.',
  'Full ordinary opponentT3 window90-104: hidden draw to4 backs92; waiting94/96; Alolan Diglett right bench98 and fan3; Metal attached Dialga100/101; no attack or HP change before owner turn4 banner104.',
  'Opponent Ball search50 remains facedown. Tinkatink revealed for later play51 does not establish searched identity.',
  'Cyrus normal draw106 and Lucky Ice Pop147 are named native reveals. T4 selected107.5/end114 counts5/4, T6 selected149/end168 counts5/3. Owner-start opponent fans3/3/4.',
  'All owner-turn scheduled+1/+3/+6 candidates retained, timing tied to59.5/107.5/148 draw-end anchors. Post-play/zoom candidates individually qualified; denser preplay selected60/107.5 and scheduled+1 selected149. Before-attack hand84/114/168 substitutes for End Turn. Actual native full/crop evidence inspected.',
  'Pop consumed149-150, card resolution reveal151; heal60 to80 by154; Heads157.5. Return timing needs repair below, final Item identity/count correct.',
  'T6 evolution at160 begins over Whirlipede80; completed Scolipede130/140 at162 retains10 damage. Wally consumed162-163, reveal164, generated Colorless at165 and attached166. Separate stillavailable Darkness attaches to right Mega167-168.',
  'KO sequence is separated correctly:173 still20HP,173.5 zero while Dialga occupiesActive,174 glow,174.5 cloud,175 first clear emptyActive/discardpreview,178 +2points,182 DiglettActive60HP with2Metal.',
  'Terminal203 waiting,204 explicit concession,214.8 finalVictory versus おせち; second,7turns,2-0,160damage. Lobby0 identifies Deluxe Pack: Mega Emblem Event; no battleAuto appears in inspected views.',
  'Both boards, current versus nextEnergy, benches, points, HP and conditional poison reconcile in selected source evidence. No Tool/Stadium play or attached Tool appears; representation needs repair below.',
  'Full discard piles not opened per complete first-pass coverage; partial previews correctly limited. No game-bound QR/full20 list in whole-source first pass. Frozen live snapshot lacks Scolipede; prior183108 QR candidate has20 slots and matching original payload, retained only as candidate with unrecorded edit/version uncertainty. Exact game list staysnull.'
 ],
 'repair_requests':[
  {'id':'R1_absence_representation','files':['TURN_LEDGER.json'],'finding':'Every boundary stadium is null despite an observed-absence basis; occupied Pokemon tool values are null despite no attached Tool observed. Null means unknown under template contract.','repair':'Set stadium to none on all14 boundaries and tool to none on occupied Pokemon, preserving explicit observed-absence basis. Empty positional slots remain explicitly empty rather than inventing a Pokemon.'},
  {'id':'R2_displayed_turn','files':['TURN_LEDGER.json'],'finding':'13 boundary records assert a displayed current-turn number after the banner disappeared. Only T5 board_after F014500 visibly readsCurrent turn6. T4 board_after F012300 also incorrectly claims turn5 displayed in phase text.','affected_fields':affected,'repair':'Set those13 turn_number_displayed values to null with absent/unreadable-banner reason; retain concluded row turn separately in phase or an inferred turn field. Remove unsupported displayed wording from T4 after phase. Preserve T5 after displayed6.'},
  {'id':'R3_item_return_time','files':['TURN_LEDGER.json','REVIEW.md'],'finding':'T6 play1 return event timestamp158/F015800 does not show returned Pop. At158 the owner holds only Scolipede/Whirlipede/Wally/Cyrus; healedWhirlipede80. At160 Pop is visibly back while Scolipede evolution is underway.','evidence_ids':['F015800','F016000'],'repair':'Record Item return bounded after158 and by160, with exact instant unknown; useF016000 as observed returned hand and F015800 as preceding bound. Add F016000 to play1 evidence and preserve sameItem, Heads and endingcount3. Change prose return at158 to this bound.'}
 ],
 'astra_required':False,
 'lead_acceptance_written':False,
 'canonical_files_edited':False,
 'registration_media_or_external_writes':False,
 'remaining':'Root repairs three precise findings, then independent hash-bound amendment recheck before acceptance. Structure alone did not establish acceptance.'
}
text=json.dumps(receipt,ensure_ascii=False,indent=2)+'\n'
(out/'INDEPENDENT_ACCEPTANCE.rejected.json').write_text(text,encoding='utf-8')
(out/'INDEPENDENT_ACCEPTANCE.json').write_text(text,encoding='utf-8')
print(json.dumps({'decision':receipt['decision'],'repairs':len(receipt['repair_requests']),'changed':changed,'manifest_mismatches':manifest_mismatches,'receipt':str(out/'INDEPENDENT_ACCEPTANCE.rejected.json')},ensure_ascii=False))
