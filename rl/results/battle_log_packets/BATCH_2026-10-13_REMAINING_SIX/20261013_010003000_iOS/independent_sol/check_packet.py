import json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

p = Path(__file__).resolve().parent.parent
out = Path(__file__).resolve().parent
def read(name):
    return json.loads((p / name).read_text(encoding='utf-8-sig'))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
freeze = read('REVIEW_PACKET_HASHES.json')
hashes = {n: digest(p / n) for n in freeze['review_components']}
assert hashes == freeze['review_components'], 'Primary changed after freeze'
rejected = out / 'rejected_inputs'
rejected.mkdir(exist_ok=True)
for n in hashes:
    dest = rejected / n
    if dest.exists():
        assert digest(dest) == hashes[n], 'Do not overwrite rejected history'
    else:
        shutil.copy2(p / n, dest)
shutil.copy2(p / 'REVIEW_PACKET_HASHES.json', rejected / 'REVIEW_PACKET_HASHES.json')
ledger = read('TURN_LEDGER.json')
evidence = read('TURN_EVIDENCE.json')
frames = {f['evidence_id']: f for f in evidence['frames']}
assert len(ledger['turns']) == 11
assert [t['turn_number'] for t in ledger['turns']] == list(range(1, 12))
missing = []
def references(v):
    if isinstance(v, dict):
        for k, val in v.items():
            if k.endswith('evidence_ids') and isinstance(val, list):
                missing.extend(x for x in val if x not in frames)
            references(val)
    elif isinstance(v, list):
        for val in v:
            references(val)
references(ledger)
assert not missing, missing
selected = [27, 112, 114, 134, 212.6, 216, 284, 286, 61, 62, 387.5, 388.5, 358, 369, 380, 398, 448, 449, 450, 451, 452, 453, 472]
selected_files = []
for s in selected:
    path = p / 'turn_evidence' / f't{s:07.2f}.jpg'
    assert Image.open(path).size == (1170, 2532)
    selected_files.append({'source_seconds': s, 'path': str(path.relative_to(p)), 'sha256': digest(path), 'native_dimensions': [1170, 2532]})
required = [
    {'id': 'T7_SEARCH_ARRIVAL_REFERENCE', 'files': ['TURN_LEDGER.json'], 'problem': 'T7 Alolan Grimer search timestamp 285 cites f0284_00, whose retained native frame has no Alolan Grimer arrival. Native286 shows the fifth card Alolan Grimer. Native285 does not exist.', 'repair': 'Bind individual card and search-group timestamp/evidence to inspected arrival286/f0286_00, or retain and inspect a genuine earlier arrival frame. Do not use the pre-arrival284 frame as named arrival evidence.'},
    {'id': 'T11_MISSING_ENERGY_ATTACHMENT', 'files': ['REVIEW.md', 'TURN_LEDGER.json'], 'problem': 'After Lucky Ice Pop heads, native449 shows Energy targeting. Native451-453 has Bench Alolan Muk with Darkness plus Colorless, total2, whereas T11 contains only IcePop action and its final board has Colorless1.', 'repair': 'Inspect bounded449-450 transition, add the Darkness attachment to Bench Alolan Muk as numbered action2 afterIcePop and before Regigigas menu inspection, and correct final mixedEnergy total2 (Darkness1/Colorless1). Retain source-bound evidence and reconcile ownerZone consumption. No additional attack resolves.'}
]
findings = [
    {'topic': 'setup', 'finding': 'Native27 shows Regigigas, Mesagoza, Rare Candy, Glimmet, Glimmora left to right, owner going first. Five original slots supported.'},
    {'topic': 'ordinary independent turn3', 'finding': 'Native112 is unzoomed five-card preplay hand: Rare Candy, Glimmora, Lucky Ice Pop, Alolan Muk, Heavy Helmet. Native114 evolution leaves four. Native134 shows HP90 and four-card hand including returnedIcePop. Evolution/heal/heads return arithmetic supports ending4.'},
    {'topic': 'search turn5', 'finding': 'Native212.6 unzoomed preplay hand has PokeBall fifth. Native216 clearly reveals foundGlimmet. Search remains distinct from normal draw.'},
    {'topic': 'Research arrivals', 'finding': 'Native61/62 supports Lucky Ice Pop then Alolan Muk arrivals. Native387.5/388.5 supports Ilima then Kingambit arrivals.'},
    {'topic': 'turn8 scoring', 'finding': 'Native358 reads Shattering Crystal heads and deniedpoints text. Native369 ownerfirstpoint. Score/prose records0 opponentpoints after GlimmoraKO and poisonDrampaKO.'},
    {'topic': 'Basic abilities', 'finding': 'Native380 Alolan Muk text says Basic Pokemon in play have no Abilities; Stage1 Dragonair remains unaffected. Native398 shows Regigigas KO of Drampa and Colorless supplied to Bench Muk. Regigigas printed Seal restricts attacking, not attaching.'},
    {'topic': 'final hand and result', 'finding': 'Native448IcePopheads and449five-card hand. Native450 is Regigigas menu inspection. Native451-453 explicitly says Your opponent conceded. Native472 says vs.gimt Victory, wentfirst,11turns,2-0points,190damage. No final attack resolves.'},
    {'topic': 'coverage/classification', 'finding': 'Eight components report full source0-479.441667 and11 consecutive rows. Selected native gameplay has namedopponent and dualclocks with noAuto option, consistent with humanclassification. This is bounded independent acceptance, not a second fullvideopass.'},
    {'topic': 'capture limits', 'finding': 'Sixownerturns have draw-relative candidates,+1/+3/+6andbeforeend; earlyplay alternatives preserved forT5/T7. Nativecrop coordinates retained. Opponentfan counts explicit; hiddenidentities and unopeneddiscards are explicitlimits. NextEnergy numericcounts staynull. Native449finalEnergy target and451mixedEnergy require correction above.'},
    {'topic': 'deck provenance', 'finding': 'DECK_USED has20historicalcards, duplicatecounts total20, filmedexactQR20, DarknessEnergy. Historicalreceipt and QRpayload match their supplements. fresh_live_readback=false retained. Externalaccess limit does not implyfreshsave or preventlocalacceptance aftermaterialrepairs.'}
]
result = {
    'schema': 'battle-logs/bounded-independent-acceptance-v1',
    'reviewer': '/root/check_remaining_010003', 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'source_video': freeze['source_video'], 'source_sha256': freeze['source_sha256'],
    'source_identity_basis': 'Frozen source binding supplied by root and existing verified CLI intake; no redundant source rehash or entire-video pass',
    'accepted': False, 'checked_input_sha256': hashes, 'primary_freeze_match': True,
    'required_repairs': required, 'native_findings': findings, 'selected_native_evidence': selected_files,
    'packet_reference_inventory_passed': True,
    'structural_validation_is_separate': True,
    'fresh_live_readback': False,
    'rejected_input_preservation': str(rejected),
    'scope': 'All eight stable primary components, independently selected ordinary turn plus consequential draws/boards and terminal sequence; no shared writes, moves, browser access, lead acceptance, or subagents'
}
(out / 'CHECK_RESULT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps({'accepted':False, 'repairs':[r['id'] for r in required], 'freeze_match':True, 'turn_rows':len(ledger['turns']), 'selected_native_frames':len(selected_files)}, indent=2))
for t in ledger['turns']:
    b = t['board_after']
    print(t['turn_number'], t['who_played'], b['owner']['active']['name'], b['owner']['active']['hp_now'], b['opponent']['active']['name'], b['opponent']['active']['hp_now'], b['owner']['points'], b['opponent']['points'])
