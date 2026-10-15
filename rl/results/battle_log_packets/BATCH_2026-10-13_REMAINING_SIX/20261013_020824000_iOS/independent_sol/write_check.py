import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent
p = out.parent
freeze = json.loads((p / 'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
names = list(freeze['files'])
checked = {n: hashlib.sha256((p / n).read_bytes()).hexdigest() for n in names}
assert checked == freeze['files']
original = out / 'rejected_original'
original.mkdir(exist_ok=False)
for n in names + ['REVIEW_PACKET_HASHES.json']:
    shutil.copy2(p / n, original / n)
assert all(hashlib.sha256((original / n).read_bytes()).hexdigest() == h for n, h in checked.items())
validator = p.parents[1] / 'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r = subprocess.run([sys.executable, '-X', 'utf8', str(validator), str(p)], capture_output=True, text=True, encoding='utf-8', check=True)
structure = json.loads(r.stdout)
(out / 'STRUCTURE_CHECK.json').write_text(json.dumps(structure, indent=2) + '\n', encoding='utf-8')
checks = [
    {'topic': 'source identity', 'result': 'pass', 'observation': 'Current original hashed serially to SOURCE SHA-256; 998764820 bytes and mtime stable during hash. Source duration/metadata/timezone bindings agree with packet. All eight current file hashes match freeze.'},
    {'topic': 'opening', 'result': 'pass', 'seconds': [27.7], 'observation': 'Native bottom crop independently shows Heavy Helmet, non-ex Alolan Muk, Research, Glimmet, Kingambit in order, before Active placement. Glimmet selected Active separately.'},
    {'topic': 'ordinary owner first move and hand', 'result': 'repair timing qualification', 'seconds': [124.6, 125.3, 127.3, 144.2], 'observation': 'Six cards before play: Helmet, Muk, Kingambit, Ilima, Glimmora, Pawniard. 125.3 is Glimmora inspection/selection with card remaining in six-card hand, not committed evolution. 127.3 shows Glimmora on Active in evolution animation with five hand cards. Ending two cards are Kingambit and Ilima; board has Glimmora50, Muk110, Pawniard50 with Helmet, and Glimmora1 Darkness. Four hand removals reconcile 6 to2.'},
    {'topic': 'individual Research and searches', 'result': 'pass', 'seconds': [50.1, 51.1, 56.0, 217.5, 218.4, 224.5], 'observation': 'Research1 reveals Poke Ball then Glimmora; search finds Alolan Grimer. Research5 reveals Glimmet then Poke Ball; Regigigas visibly arrives from search. Each owner arrival has separate ledger entry.'},
    {'topic': 'independently selected ordinary opponent turn4', 'result': 'pass', 'seconds': [173.9, 178.9, 211.5], 'observation': 'Pre-evolution right Combee, subsequent right Vespiquen140, then Leaf Cape effective170 are consistent with action order. End board shows Glimmora10, poisoned Shuckle70, left Combee50, center Ogerpon130, right Vespiquen170 with1 Grass/Leaf Cape. Source frame211.5 displays transition to turn5; phase label should be read as boundary after turn4, without pretending displayed number remains4.'},
    {'topic': 'turn7 attachment and retreat', 'result': 'pass', 'seconds': [350.4, 352.3, 354.1], 'observation': 'Energy attachment animation targets Active Glimmet; settled Glimmet has1 Darkness; after retreat Regigigas Active150 with0, Glimmet Bench60 with0, Pawniard Bench retains1/Helmet. Paid1 Darkness is separately stated. Two-card ending hand agrees.'},
    {'topic': 'turn11 return/rebench/retreat/attachment', 'result': 'pass', 'seconds': [447.4, 457.8, 460.6, 462.5], 'observation': 'Ilima return removes damaged Regigigas and its Energy; Pawniard Active retains Helmet and1 until retreat; fresh Regigigas rebenched150 with0, then Active, and attachment animation targets Regigigas. Resulting Pawniard0, Regigigas1; hand Kingambit/Glimmora2 agrees with arithmetic.'},
    {'topic': 'turn13 final Energy target and HP', 'result': 'pass', 'seconds': [510.9], 'observation': 'Settled board independently confirms Regigigas50 with2 Darkness, Muk110 with0, Pawniard50 with0 and Helmet, opponent Active170 with2 Grass and Cape, left Vespiquen170 with1/Cape and Ogerpon130 with1. Next Energy TYPE remains explicitly distinct from unknown future count.'},
    {'topic': 'Glimmora KO effect', 'result': 'pass', 'seconds': [320.0], 'observation': 'Native frame shows Shattering Crystal text and tails face, supporting first opponent point rather than prevented point.'},
    {'topic': 'terminal', 'result': 'pass', 'seconds': [524.0, 527.0, 532.0, 540.4], 'observation': '140 damage on50HP Regigigas; Ogerpon discarded, Regigigas removed, Defeat then vs Subbles results. Went first,14 turns,0-3,60 damage are visible. Terminal retains unused opponent Grass, two Vespiquen170, owner Muk110/Pawniard50 Helmet.'},
    {'topic': 'deck and explicit limits', 'result': 'pass_with_external_pending', 'observation': 'Independent zxingcpp decoding of native4s QR exactly equals DECK_USED payload; 20 list slots and summed duplicate counts equal20, Darkness. Saved historical catalog SHA matches source_capture_sha256. Filmed semantic list/historical log provenance explicitly does not claim fresh live verification or exact artwork. Opponent hidden identities and unopened discards remain qualified.'},
]
result = {
    'accepted': False,
    'decision': 'rejected_pending_single_timing_qualification',
    'reviewer': '/root/check_remaining_020824',
    'model': 'inherited Sol',
    'effort': 'high',
    'checked_utc': datetime.now(timezone.utc).isoformat(),
    'source_video': freeze['source_video'],
    'source_sha256': freeze['source_sha256'],
    'checked_input_sha256': checked,
    'all_eight_stable': True,
    'source_hash_verified_current': True,
    'source_size_and_mtime_stable_during_hash': True,
    'scope': 'Bounded independent source acceptance: all eight actual files read/parsed, structural integrity separately checked, independently selected native opening, ordinary owner and opponent sequence, draws/searches, consequential state and terminal checks. No duplicate full visual pass or broad decoding.',
    'checks': checks,
    'required_repairs': [{
        'id': 'R1',
        'topic': 'turn3 inspection is not committed first play',
        'files': ['COVERAGE.md', 'TURN_LEDGER.json', 'TURN_EVIDENCE.json', 'REVIEW.md if needed for consistency'],
        'observation': 'Native125.3 shows selected Glimmora inspection overlay with six hand cards; native127.3 shows placed Glimmora/evolution animation and five cards. Coverage calls125.3 first evolution, ledger calls125.1 first voluntary move and evolution without identifying selection versus commit. Evidence scheduled_capture_limits says +1 turn3 already after first play, although this frame is inspection.',
        'repair': 'Qualify125.1/125.3 as inspection/selection and locate or bracket actual committed evolution using nearby retained source frames. Preserve actual preplay124.6 and final hand2. Adjust timing/evidence suitability wording consistently, refreeze eight files and request focused recheck. No new full pass is required.'
    }],
    'structural_validation': {'path': 'STRUCTURE_CHECK.json', 'structural_pass': structure['structural_pass'], 'turn_rows': structure['turn_rows'], 'semantic_acceptance_separate': True},
    'preserved_rejected_packet': 'rejected_original',
    'external_step_pending': True,
    'factual_outcome_verified': {'opponent': 'Subbles', 'result': 'loss', 'went_first': True, 'turns': 14, 'points': [0,3], 'damage_done': 60},
}
assert all(hashlib.sha256((p / n).read_bytes()).hexdigest() == h for n, h in checked.items())
(out / 'CHECK_RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Saved bounded rejection R1; all eight original files and freeze preserved; structural pass14 rows.')
