import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

packet = Path(__file__).resolve().parent.parent
manifest_path = packet / 'REVIEW_PACKET_HASHES.json'
manifest_bytes = manifest_path.read_bytes()
manifest = json.loads(manifest_bytes)
manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
expected_manifest_sha = '5dd3cab575981455daea579a44a33f0a0e9cbee3e0fbea2fd06fbf13b41885bb'
mismatches = []
for name, expected in manifest['files'].items():
    path = packet / name
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    if actual != expected:
        mismatches.append({'path': name, 'expected': expected, 'actual': actual})
times = [0,19,52,64,68,76,153,178,180,182,194,201,203,226,236,248,252,271,273,330,332,338,345,347,349,351,353,388,390,392,396,436,447]
result = {
    'accepted': not mismatches and manifest_sha == expected_manifest_sha,
    'reviewer': '/root/check_215114',
    'model': 'gpt-6.1-sol',
    'reasoning_effort': 'high',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'source_filename': '20261014_215114000_iOS.MP4',
    'source_sha256': 'b3170e7b962e7141ab0168cf4ca9aa2ce7e1241e6b750eee785eff51657c8a4a',
    'source_binding': 'Reused lead-verified original SOURCE.json binding; original was not rehashed or altered.',
    'frozen_manifest_sha256': manifest_sha,
    'expected_frozen_manifest_sha256': expected_manifest_sha,
    'frozen_files_match': not mismatches,
    'frozen_file_count': len(manifest['files']),
    'file_hash_mismatches': mismatches,
    'primary_unchanged': not mismatches and manifest_sha == expected_manifest_sha,
    'scope': 'Bounded independent semantic acceptance using retained native evidence, primary review and full phase coverage account. Not a repeated full visual pass.',
    'documents_read': ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'REVIEW_PACKET_HASHES.json', 'START_HERE_VIDEO_REVIEW.md', 'Review_Log/README.md'],
    'inspected_evidence': [{'path': f'evidence/t{t:07.2f}.jpg', 'source_seconds': t, 'view': 'native retained frame individually inspected'} for t in times],
    'ordinary_samples': [
        {'global_turn': 2, 'owner_turn': 1, 'times': [52,64,68,76], 'checks': 'Elegant Cape draw; Research and visible Rattata plus Research in hand; Soothing Shore played; end board has benched Rattata40, Vulpix60 with one Water, Deino60 to40, score0-0. Cape remains in hand. No Auto option visible.', 'consistent': True},
        {'global_turn': 8, 'owner_turn': 4, 'times': [226,236,248,252], 'checks': 'Initial Hydreigon10 without Energy; Ninetales180 with Cape gains third Water. Binding Snow80 inspected on card, first Hydreigon knockout awards one owner point, Absol70 with one Darkness promoted. Ninetales remains180, score1-2. Bench Hydreigon150 and Mega Absol170 retained.', 'consistent': True}
    ],
    'findings': [
        {'severity': 'none', 'fact': 'Deck13-A and visible Vulpix/Ninetales ex/Rattata/Raticate ex core confirmed at0. Both Ultra Ball Rank4 badges and opponent name 羊羽 confirmed at19. No Auto option observed in inspected board UI; exact queue menu remains unshown.'},
        {'severity': 'none', 'fact': 'First Ninetales attack accepted as ownerT3/global6: opponent turn5 banner at153, Rattata already knocked out and Vulpix promoted at178-180, Ninetales evolution194, named Binding Snow201 and80-damage203. Opponent already2 points; Ninetales180/Cape/twoWater, Hydreigon90 before damage. This differs from earlier Vulpix Gnaw20.'},
        {'severity': 'none', 'fact': 'Enhanced Blade native text271 has printed20 plus30 with Tool. Absol is Tool-equipped and Ninetales is130 at273 after180 earlier; bench Hydreigon120/threeDarkness. No Ninetales healing assigned to opponent ending.'},
        {'severity': 'none', 'fact': 'Owner turn10 ending: score2-2, promoted Hydreigon120/threeDarkness, Ninetales130 in healing animation330 then150 at332. Matches Soothing Shore20 recovery on owner ending.'},
        {'severity': 'none', 'fact': 'Deceptive Needle enlarged native text338 establishes end-of-owner-of-Tool turn10damage. Hyper Ray130 native345; Ninetales150 to20 at347, named Needle activation349 then10HP351. Hydreigon Energy present347 then gone351; Mega Absol has oneDarkness351. Score2-2. Separate130 and10 events, no Helmet inference.'},
        {'severity': 'none', 'fact': 'Owner turn12 banner353, end attack state388 has Hydreigon40/noEnergy and Ninetales10/threeWater plus Raticate120/oneWater. Soothing Shore named390,20healing392, Ninetales30 by396. No successful Raticate Energy theft is inferred.'},
        {'severity': 'none', 'fact': 'Explicit opponent concession436 with Ninetales30, Hydreigon80/noEnergy, benched Mega Absol170 and Bombirdier70. Victory447 versus 羊羽, wentsecond,13turns,points2-2,damage340. No third knockout point. The340 agrees with20+four80 attacks.'}
    ],
    'material_discrepancies': [],
    'limits': [
        'Independent semantic checking was bounded to listed retained evidence and two ordinary turn samples; no second complete frame pass was performed.',
        'Full first-pass setup-to-terminal coverage is documented by primary reviewer in COVERAGE.md and REVIEW.md, and checked for interval/turn/result consistency.',
        'Hidden cards, unshown complete deck lists, unknown card versions and intentions remain unknown. No external card/rules lookup was needed because consequential card text is readable in native evidence.',
        'The precise global6 turn banner was not separately viewed; turn number derives from observed preceding opponent turn5, promotion/evolution/attack sequence, second turn order and full coverage account.',
        'No primary edits, shared event/index/location changes, source moves, external game entries or Boss Folder writes occurred.'
    ]
}
dest = packet / 'independent_sol' / 'CHECK_RESULT.json'
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'accepted': result['accepted'], 'frozen_file_count': result['frozen_file_count'], 'mismatches': mismatches, 'manifest_sha256': manifest_sha, 'result_path': str(dest)}, ensure_ascii=False))
