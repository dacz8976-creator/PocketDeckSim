"""Persist the lead's actual bounded visual checks; no full-review claim."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

packet = Path(__file__).resolve().parent / '20261012_230258000_iOS'
source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
checks = [
    (31.5, 'Opening shows going first and Mesagoza, Kingambit, Regigigas, Glimmet, Professor\'s Research.'),
    (48, 'T1 preplay hand has Mesagoza, Kingambit, Research and Lucky Ice Pop; Regigigas Active, Glimmet Bench; opponent Froakie Active.'),
    (52, 'First Research draw visibly reveals Poke Ball.'),
    (53, 'Second Research draw visibly reveals Heavy Helmet.'),
    (201, 'T5 Rare Candy draw is visible with an Energy generation overlay. Five owner hand cards; opponent has two benched Staryu and a Froakie behind active Froakie.'),
    (203, 'T5 Mesagoza activation begins; it precedes the later attachment and attack.'),
    (416, 'Copycat is inspected/played with only Ilima beside it; three opponent card backs are visible.'),
    (422, 'Copycat first visible reveal is Professor\'s Research.'),
    (423, 'Copycat second visible reveal is Ilima.'),
    (432, 'After Giga Turbo, active Starmie ex is at 30 HP and Regigigas at 90 HP; effect targets benched Alolan Muk.'),
    (495, 'Explicit no-cards-left/unable-to-draw notice; battle continues afterward.'),
    (544, 'Final promoted Alolan Muk shows one attached Colorless Energy, distinct from deck Darkness.'),
    (548, 'Starmie ex Hydro Splash visibly deals 90 damage to Alolan Muk, whose HP was 90 before attack.'),
    (564, 'Defeat vs Giorno, went first, 14 turns, owner 2 points/opponent 3 points, 160 damage.'),
]
rows = []
for timestamp, observation in checks:
    relative = f'turn_evidence/t{timestamp:07.2f}.jpg'
    path = packet / relative
    assert path.exists(), relative
    rows.append({'timestamp_seconds': timestamp, 'frame': relative,
                 'frame_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'observation': observation})
receipt = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'lead': '/root',
           'video': source['video_basename'], 'source_sha256': source['sha256'],
           'checks': rows, 'basis': 'Lead directly viewed the listed source-native derivatives.',
           'scope': 'Bounded lead checks supporting full primary and independent review; not a replacement for whole-source review.',
           'limits': ['Source-local approximate seeks; exact frame PTS is unverified.',
                      'Hidden cards and unopened discard contents remain unknown.']}
target = packet / 'ROOT_SOURCE_CHECKS.json'
assert not target.exists()
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('14 bounded lead frame checks recorded.')
