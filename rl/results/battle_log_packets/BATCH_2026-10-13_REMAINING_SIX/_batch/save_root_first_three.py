import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
now = datetime.now(timezone.utc).isoformat()
def save(p, d): p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def frame(p, name, observed):
    return {'path': 'turn_evidence/' + name, 'sha256': hashlib.sha256((p / 'turn_evidence' / name).read_bytes()).hexdigest(), 'observed': observed}

p = B / '20261013_010003000_iOS'
r = json.loads((p / 'ROOT_SOURCE_CHECKS.json').read_text(encoding='utf-8-sig'))
for n, o in [
 ('t0286.00.jpg', 'Root directly saw fifth Alolan Grimer added to hand after PokeBall search; corrected actual arrival286. Earlier284 was unresolved search.'),
 ('t0449.25.jpg', 'Root directly saw Darkness orb travelling toward Bench Muk; earlier449 Zone selected and Muk onlyColorless. Hand five cards unchanged.'),
 ('t0449.50.jpg', 'Root directly saw continuing attachment orb on Bench Muk; already viewed453 final board has Darkness1+Colorless1,total2 and consumed Zone. This supports repaired numbered regular attachment, not merely tool inspection.'),
]:
    if not any(c['path'] == 'turn_evidence/' + n for c in r['checks']): r['checks'].append(frame(p, n, o))
r['updated_utc'] = now
save(p / 'ROOT_SOURCE_CHECKS.json', r)

p = B / '20261013_010837000_iOS'
assert not (p / 'ROOT_SOURCE_CHECKS.json').exists()
observations = [
 ('t0032.00.jpg', 'Five opening faces before Active: Glimmora, Pawniard, Alolan Muk non-ex, Research, Copycat; owner first.'),
 ('t0201.00_bottom.jpg', 'Genuine ordinary preplay hand Kingambit/Glimmet/Muk3; original action order must be checked against selected Muk202.'),
 ('t0202.00.jpg', 'Muk selected over right Bench Grimer while Glimmet remains in hand. Contradicts original firstplayGlimmet claim; evolution precedes Glimmet.'),
 ('t0210.00_bottom.jpg', 'Ending hand Kingambit1; start3 minusMuk evolution minusGlimmet bench reconciles1.'),
 ('t0060.00.jpg', 'Literal Seal of Antiquity prevents Regigigas ATTACK without namedRegis onBench. It does not prevent attachment.'),
 ('t0068.00.jpg', 'Settled hand Glimmora/Muk/Copycat3, noResearch zoom. Primary supplied anchor message called thisResearch; checker checking actual ledger naming.'),
 ('t0069.00.jpg', 'RareCandy reveal after Research; this is notResearch arrival.'),
 ('t0144.00.jpg', 'Copycat first reveal PokeBall, initiallyemptyhand.'),
 ('t0145.00.jpg', 'Copycat nextKingambit, PokeBallalreadyinhand.'),
 ('t0146.00.jpg', 'Copycat nextGlimmet, PokeBall/Kingambit alreadyinhand; order3supported.'),
 ('t0152.00.jpg', 'PokeBall searched AlolanGrimer arrives; Kingambit/Glimmet inhand. Nohiddenextra card.'),
 ('t0428.00.jpg', 'Raticateex Active120 withDarkness1+Metal2; opponentBench Mega180 Lightning1/Fighting1,Pichu10,Rattata40. OwnerKingambit140 Dark2+Helmet,Muk110,handGlimmora1.'),
 ('t0538.00.jpg', 'Ilima normalarrival during Turn15 and waitingbanner, Glimmoraalreadyinhand, bothscores2 beforeaward. Opponent remains disconnected.'),
 ('t0550.00.jpg', 'Timeout +3points animation; owner cappedthree litpoints, opponent2. NoKO or concession shown.'),
 ('t0553.00.jpg', 'Victory terminal, Kingambit displayed. OutcomeWinbyreturntimeout.'),
]
source = json.loads((p / 'SOURCE.json').read_text(encoding='utf-8-sig'))
save(p / 'ROOT_SOURCE_CHECKS.json', {'lead':'/root','source_sha256':source['sha256'],'updated_utc':now,'full_second_pass':False,'checks':[frame(p,n,o) for n,o in observations],'pending_primary_repairs':['Turn5 Muk evolution precedes Glimmet bench; align numbered plays and hand anchors','Research arrival anchor names and timestamps require bounded checker confirmation']})
print('Saved direct root source observations')
