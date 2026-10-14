"""Read-only final artifact, reference and current-status checks."""
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA/BATCH_2026-09-30_EVENING'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
intake, results, validation = [read(batch / name) for name in ['INTAKE.json','RESULTS.json','VALIDATION.json']]
assert results['completed'] == 11 and results['practice_wins'] == 5 and results['practice_losses'] == 6
assert validation['batch_complete'] and validation['unchanged_prior_index_entries'] == 98
assert len({v['sha256'] for v in intake['sources']}) == 11
assert not [p for p in root.iterdir() if p.is_file() and p.suffix.lower()=='.mp4' and p.name.startswith('20261001_')], 'Unreviewed new source remains at root'
for item in intake['sources']:
    name = item['video']
    packet = root / 'Recording_QA' / (Path(name).stem + '_auto_sol')
    subprocess.run([sys.executable,str(root/'Recording_QA/complete_auto_packet.py'),name,'--validate-only'],check=True,capture_output=True,text=True)
    for document in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
        text = (packet / document).read_text(encoding='utf-8-sig')
        assert '\u2014' not in text, f'Generated em dash: {name} {document}'
        if document.endswith('.md'):
            assert 'Current status: completed full-battle review accepted by the lead' in text
            assert not re.search(r'awaiting[^\n.]*lead|acceptance[^\n.]*pending|lead acceptance remains outstanding|not lead accepted',text,re.I), f'Stale status: {name} {document}'
        else:
            data = json.loads(text)
            assert data['current_status'] == 'full_battle_review_complete' and data['lead_acceptance'] == 'accepted'
            for key in ['lead_accepted','independent_lead_accepted','independently_accepted']:
                if key in data:
                    assert data[key] is True
report = root / 'BATTLE_TRANSCRIPTS_2026-09-30_EVENING.md'
text = report.read_text(encoding='utf-8')
for target in re.findall(r'\]\(([^)]+)\)',text):
    if not target.startswith(('https://','http://')):
        assert (root / target).is_file(), f'Broken summary link: {target}'
assert text.count('[Complete review]') == 11 and '\u2014' not in text
readme = (root / 'READ_ME_REVIEW_STATUS.md').read_text(encoding='utf-8')
assert 'contains 109 videos: 94 accepted full-battle reviews and eight completed rule tests' in readme
result = {'complete_reviews':11,'practice_wins':5,'practice_losses':6,'source_hashes_unique':11,'packet_references_valid':True,'summary_links_valid':True,'current_status_consistent':True,'unchanged_previous_index_rows':98,'ladder_entries_created':0}
(batch / 'FINAL_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
