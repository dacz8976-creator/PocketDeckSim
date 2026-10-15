"""Verify preserved historical outcomes and source-specific computer exclusions."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
inventory = json.loads((B / 'INVENTORY.json').read_text(encoding='utf-8-sig'))
errors = []

def table(path):
    rows = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.startswith('|') or '_iOS.MP4`' not in line:
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        source = cells[1].strip('`')
        if source in rows:
            errors.append(source + ': duplicate historical row')
        rows[source] = {'line': line, 'cells': cells}
    return rows

baseline_path = B / 'LADDER_HISTORY_PRE_2026-09-15.before_computer_reclassification.md'
ladder_path = ROOT / 'LADDER_HISTORY_PRE_2026-09-15.md'
computer_path = ROOT / 'COMPUTER_BATTLE_HISTORY.md'
baseline = table(baseline_path)
ladder = table(ladder_path)
computer = table(computer_path)
opponent_receipt = json.loads((B / 'HISTORY_OPPONENT_CORRECTION.json').read_text(encoding='utf-8-sig'))
checked = []
for game in inventory['recordings']:
    source = game['source']
    packet = B / source.split('_iOS')[0]
    lead_path = packet / 'LEAD_ACCEPTANCE.json'
    lead = json.loads(lead_path.read_text(encoding='utf-8-sig')) if lead_path.is_file() else {}
    if lead.get('shared_registration') != 'complete':
        errors.append(source + ': review is not yet accepted and registered')
    if int(source[:8]) >= 20260915:
        continue
    old = baseline.get(source)
    destinations = [name for name, rows in [('ladder', ladder), ('computer', computer)] if source in rows]
    if old is None or len(destinations) != 1:
        errors.append(source + ': expected one preserved pre-season result')
        continue
    destination = destinations[0]
    current = (ladder if destination == 'ladder' else computer)[source]
    if old['cells'][:4] != current['cells'][:4]:
        errors.append(source + ': date, source, result or visible deck core changed')
    if old['cells'][4] != current['cells'][4]:
        if opponent_receipt.get('source') != source or opponent_receipt.get('old_row') != old['line'] or opponent_receipt.get('new_row') != current['line']:
            errors.append(source + ': unsupported opponent correction')
    classification_path = packet / 'CLASSIFICATION_RECEIPT.json'
    classification = json.loads(classification_path.read_text(encoding='utf-8-sig')) if classification_path.is_file() else {}
    is_computer = classification.get('classification') == 'computer_battle' and classification.get('excluded_from_ladder') is True
    if is_computer != (destination == 'computer'):
        errors.append(source + ': history destination conflicts with accepted computer classification')
    checked.append({'source': source, 'destination': destination, 'result_preserved': old['cells'][2] == current['cells'][2],
                    'classification_receipt': str(classification_path) if is_computer else None})

def totals(rows):
    return {'games': len(rows), 'wins': sum(row['cells'][2].startswith('Win ') for row in rows.values()),
            'losses': sum(row['cells'][2].startswith('Loss ') for row in rows.values())}

ladder_totals = totals(ladder)
computer_totals = totals(computer)
expected_line = f"**Historical ladder total:** {ladder_totals['games']} games, {ladder_totals['wins']} wins, {ladder_totals['losses']} losses."
if expected_line not in ladder_path.read_text(encoding='utf-8-sig'):
    errors.append('Historical ladder total line does not match unique table results')
receipt = {'schema': 'retrospective-history-verification-v1', 'checked_utc': datetime.now(timezone.utc).isoformat(),
           'movie_content_reads': 0, 'pre_season_selected_results_checked': len(checked),
           'historical_ladder_total': ladder_totals, 'computer_history_total': computer_totals,
           'classification_rule': 'Any visible Auto option, including off, means computer; outcomes are retained outside ladder.',
           'files': [{'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                     for path in [baseline_path, ladder_path, computer_path, B / 'HISTORY_OPPONENT_CORRECTION.json']],
           'selected_results': checked, 'errors': errors, 'passed': not errors}
(B / 'HISTORY_VERIFICATION.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({key: receipt[key] for key in ['pre_season_selected_results_checked', 'historical_ladder_total', 'computer_history_total', 'passed', 'errors']}))
raise SystemExit(0 if receipt['passed'] else 1)
