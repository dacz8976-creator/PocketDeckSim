"""Keep the primary draft while qualifying an unsupported terminal attachment."""
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
packet = root / 'Recording_QA' / '20261001_020413000_iOS_auto_sol'
originals = packet / 'before_lead_reconciliation'
originals.mkdir(exist_ok=True)
for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json']:
    saved = originals / filename
    if not saved.exists():
        shutil.copy2(packet / filename, saved)
review_path = packet / 'REVIEW.md'
review = review_path.read_text(encoding='utf-8-sig')
before = "A regular Psychic attachment is visible in this phase, and Fantasia Force's additional distribution animation occurs around the final attack; see the Energy-allocation uncertainty below for the final split."
after = "Psychic Energy movement occurs around the final attack, but a separate regular turn-17 attachment is not established by the inspected evidence. The settled pre-attack board has Mega Gardevoir five, Bramblin two and Mimikyu four; afterward it has six, four and four, a net increase of three consistent with Fantasia Force. No additional ordinary attachment or rules discrepancy is inferred."
assert before in review
review = review.replace(before, after)
review = review.replace("exact separation of the turn-17 regular attachment and three attack-generated allocations is left as a bounded uncertainty rather than an invented rule defect", "a separate turn-17 regular attachment is not established. The net increase from the settled pre-attack board is three, consistent with Fantasia Force, and does not establish a rule defect")
review = review.replace("the final distribution split between regular turn-17 Energy and attack-generated Energy remain unknown", "whether a separate regular turn-17 Energy attachment occurs remain unknown")
review_path.write_text(review, encoding='utf-8')
summary_path = packet / 'SUMMARY.json'
summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
summary['unresolved_facts'] = ["A separate regular turn-17 attachment is not established; settled net Energy gain is three consistent with Fantasia Force" if item == 'Exact terminal normal-versus-Fantasia Energy distribution split' else item for item in summary['unresolved_facts']]
summary['lead_reconciliation'] = 'LEAD_CLARIFICATION.md'
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
uncertainty_path = packet / 'UNCERTAINTIES.json'
uncertainty = json.loads(uncertainty_path.read_text(encoding='utf-8-sig'))
for item in uncertainty['uncertainties']:
    if item['id'] == 'terminal_energy_split':
        item['question'] = 'Does the terminal animation establish a separate regular turn-17 Psychic attachment?'
        item['finding'] = 'Not established. Settled pre-attack counts at 309/312s are Mega Gardevoir5, Bramblin2, Mimikyu4; final316s counts are6,4,4. The net increase is three, consistent with Fantasia Force. No additional ordinary attachment or rule defect is inferred.'
        item['impact'] = 'Limits attribution of a separate normal attachment; the settled counts, direct110 knockout, point award and Defeat result are established.'
uncertainty_path.write_text(json.dumps(uncertainty, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('Qualified terminal Energy wording; preserved primary packet under before_lead_reconciliation')
