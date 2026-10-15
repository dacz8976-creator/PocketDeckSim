import hashlib
import json
from pathlib import Path

packet = Path(__file__).resolve().parent
expected = Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR/20261014_144627000_iOS').resolve()
assert packet == expected
keep_times = [0,23,28,38,48,62,67,72,76,82,94,100,106,117,132,141,144,148,152,155,164,166,168,175,178,188,194,200,212,216,218,220,224,239,252,263,278,294,310,313,316,320,325,340,350,355,363,370,376,386,390,397,404,412,418,424,430,437,441,445,447,452,456,467,468]
keep_names = {f't{t:07.2f}.jpg' for t in keep_times}
for frame in (packet/'native').glob('*.jpg'):
    assert frame.resolve().is_relative_to(expected)
    if frame.name not in keep_names:
        frame.unlink()
for frame in (packet/'overview').glob('*.jpg'):
    assert frame.resolve().is_relative_to(expected)
    if not frame.name.startswith('contact_'):
        frame.unlink()
for t in keep_times:
    assert (packet/'native'/f't{t:07.2f}.jpg').is_file(), t
summary = json.loads((packet/'SUMMARY.json').read_text(encoding='utf-8'))
summary['first_main_attacker_attack']['effect'] = 'First main attacker attack knocks out 90-HP Zeraora; owner reaches 1 point.'
(packet/'SUMMARY.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
primary = ['SOURCE.json','PROBE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']
files = [packet/f for f in primary] + sorted((packet/'native').glob('*.jpg')) + sorted((packet/'overview').glob('contact_*.jpg'))
mapping = {f.relative_to(packet).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
record = {'source_filename': summary['source_filename'], 'source_sha256': summary['source_sha256'], 'reviewer': summary['reviewer'], 'scope': 'Frozen primary first-pass packet; no independent or lead acceptance claimed', 'files': mapping}
(packet/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'frozen_files':len(mapping),'native_frames':len(keep_times),'all_hashes_verified': all(hashlib.sha256((packet/k).read_bytes()).hexdigest()==v for k,v in mapping.items())}))
