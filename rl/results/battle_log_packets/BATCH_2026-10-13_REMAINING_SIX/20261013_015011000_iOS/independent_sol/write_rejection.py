import json, hashlib, subprocess
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

p = Path(__file__).resolve().parent.parent
d = p / 'independent_sol'
frozen = json.loads((p / 'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8-sig'))
hashes = {n: hashlib.sha256((p/n).read_bytes()).hexdigest() for n in frozen['files']}
assert hashes == frozen['files'], 'Inputs changed since freeze'
for n,h in hashes.items():
    assert hashlib.sha256((d/'rejected_original_8'/n).read_bytes()).hexdigest() == h
e = json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8-sig'))
missing=[]
for frame in e['frames']:
    for k,v in frame.items():
        if isinstance(v,str) and v.endswith(('.jpg','.png')) and not (p/v).exists(): missing.append(v)
assert not missing
py = r'C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
validator = p.parent.parent/'BATCH_2026-10-11_NEW_PAUSE_GAMES'/'validate_packet.py'
out = subprocess.run([py,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8',check=True)
validation = json.loads(out.stdout)
(d/'STRUCTURAL_VALIDATION.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
result = {
    'accepted': False,
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'checker': '/root/check_remaining_015011',
    'review_model': 'gpt-6.1-sol',
    'reasoning_effort': 'high',
    'scope': 'Bounded independent source-bound check; reused native frames; no second whole-source pass or new decoding',
    'source_video': frozen['source_video'],
    'source_sha256': frozen['source_sha256'],
    'checked_input_sha256': hashes,
    'checked_input_file_count': len(hashes),
    'stable_against_frozen_hashes': True,
    'rejected_original_directory': 'independent_sol/rejected_original_8',
    'required_repairs': [
        {
            'id':'R1',
            'issue':'Copycat named arrival timestamps/evidence IDs point at subsequent reveals.',
            'source_findings': [
                '65.50 has no settled Research; 66.00 shows FIRST Professor Research zoom, with no prior Research in hand.',
                '66.50 shows two Research cards in transition; 67.00 shows SECOND Research zoom and one Research already in hand.',
                '68.00 shows Heavy Helmet zoom and two Research in hand.',
                '68.50 shows Lucky Ice Pop zoom with Helmet and both Research beneath it.',
                '69.50 is settled four-card hand, not the Pop reveal.'
            ],
            'requested_change':'Use observed reveal anchors Research 1 at66.00/n66_00; Research2 at67.00/n67_00; HeavyHelmet at68.00/n68_00; LuckyIcePop at68.50/n68_50. Update all prose/table, ledger draw group/card times and IDs, reveal labels and evidence references consistently. Keep timing qualified as sample anchors rather than exact onset.',
            'affected_files':['REVIEW.md','COVERAGE.md','TURN_LEDGER.json','TURN_EVIDENCE.json']
        },
        {
            'id':'R2',
            'issue':'168.50 is already an enlarged blurred error modal, not the claimed last unobstructed board/hand.',
            'source_findings':['167.50 has the clear five-card hand, both boards and unused Darkness; Waiting for opponent to return overlay remains at right without blocking the hand.','168.50 already shows error modal with blurred board and hand.169.00 shows the same modal over a clearer background.'],
            'requested_change':'Use retained167.50/n167_50 as final clear pre-terminal hand/board substitute. Change turn3 before-end timing, owner_hand_end, board_after, evidence role/selection and every clear168.50 claim to167.50. Label168.50 as already terminal/error evidence and retain169.00 as readable error corroboration. Do not infer new turn3 voluntary play.',
            'affected_files':['REVIEW.md','COVERAGE.md','UNCERTAINTIES.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
        }
    ],
    'source_findings': [
        'Opening27.50 preserves five faces: Copycat artwork on clipped left card, PokeBall, non-ex AlolanMuk, Pawniard, AlolanGrimer; later43.50 clearly names Copycat. Pawniard Active and Grimer right Bench.',
        'Ordinary independently selected owner first move43.50 clear hand Copycat/PokeBall/Muk/Ilima then45.00 PokeBall zoom and47.00 Regigigas search.47.00 literalSeal text restricts attacks only.',
        '71.50 ending hand contains Research,Research,Helmet,Pop;70.50 highlight is not attachment.71.80 turn2 transition corroborates End Turn.',
        'Opponent fan75.50 directly count5 with one currentFighting;81.50 directly count4, Tyrogue leftBench and oneFighting onFalinks. Next icon has no numeric future count.',
        '107.00 waiting-for-return, board unchanged;167.50 same board with owner fivecards and unusedDarkness. No damage or points gained.',
        '169.00 explicit opponent did not return error;182.30 Victory vs coke, wentfirst,3turns,0-0points,0damage. No concession claim.',
        'Exactly3 source-bound ledger rows cover owner/opponent/owner; primary coverage lists setup-through-result and prolonged wait. Bounded check does not repeat whole-source visual pass.',
        'Opened pile views absent per inspected primary coverage and retained ordinary/terminal boards; hidden opponent identities remain null and future Energy counts unknown.',
        'Deck20 slots and duplicate totals match own filmedQR receipt payload and supplied historical deck catalog; fresh_live_readback=false is honest. No fresh external claim is accepted.',
        'SOURCE_TIME corroborates Oct12Chicago; visible phone8:50 near47 and8:53 result. Filename UTC date preserved.'
    ],
    'reviewed_native_anchors_seconds':[27.5,43.5,45,47,65.5,66,66.5,67,68,68.5,70.5,71.5,71.8,75.5,81.5,107,167,167.5,168.5,169,182.3],
    'structural_validation': validation,
    'next_step':'Primary repairs two source-based evidence mismatches, refreezes eight files, then bounded independent correction recheck. Root alone handles acceptance/shared writes/external log/archive.'
}
(d/'CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'accepted':False,'required_repairs':['R1','R2'],'stable_eight':True,'validator':validation,'receipt':str(d/'CHECK_RESULT.json')},indent=2))
