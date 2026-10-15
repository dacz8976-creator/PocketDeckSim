"""Owner-authorized classification correction; preserves outcomes and original history."""
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
BATCH=Path(__file__).resolve().parent
ROOT=BATCH.parents[1]
p=argparse.ArgumentParser()
p.add_argument('source')
p.add_argument('--evidence',required=True)
a=p.parse_args()
inventory=json.loads((BATCH/'INVENTORY.json').read_text(encoding='utf-8-sig'))
if a.source not in {r['source'] for r in inventory['recordings']}:
    raise SystemExit('Outside selected review batch.')
evidence=Path(a.evidence).resolve()
if not evidence.is_relative_to(BATCH) or not evidence.is_file():
    raise SystemExit('Existing batch source classification evidence required.')
history=ROOT/'LADDER_HISTORY_PRE_2026-09-15.md'
computer=ROOT/'COMPUTER_BATTLE_HISTORY.md'
before=history.read_text(encoding='utf-8-sig')
lines=before.splitlines()
matches=[line for line in lines if line.startswith('|') and ('`'+a.source+'`') in line]
if len(matches)!=1:
    if computer.exists() and ('`'+a.source+'`') in computer.read_text(encoding='utf-8'):
        print(a.source+': already reclassified, skipped')
        raise SystemExit(0)
    raise SystemExit('Expected exactly one pre-season source row; inspect live season separately if absent.')
row=matches[0]
baseline=BATCH/'LADDER_HISTORY_PRE_2026-09-15.before_computer_reclassification.md'
if not baseline.exists():
    shutil.copy2(history,baseline)
remaining=[line for line in lines if line!=row]
results=[line for line in remaining if line.startswith('|') and '_iOS.MP4`' in line]
wins=sum('| Win ' in line for line in results)
losses=sum('| Loss ' in line for line in results)
for i,line in enumerate(remaining):
    if line.startswith('**Historical total:**'):
        remaining[i]=f'**Historical ladder total:** {len(results)} games, {wins} wins, {losses} losses. These results are not included in the live 2026-09-15 season.'
    elif line.startswith('**Historical ladder total:**'):
        remaining[i]=f'**Historical ladder total:** {len(results)} games, {wins} wins, {losses} losses. These results are not included in the live 2026-09-15 season.'
old_rule="Classification follows Dustin's rule: a recording without a clear Auto or specific-test label is treated as a ladder battle."
new_rule="Classification follows Dustin's clarified rule: any visible Auto option means a computer battle, even when Auto is off, and is excluded from ladder history. Other recordings retain their source-supported ladder classification unless a computer or specific-test label is established."
updated='\n'.join(remaining).replace(old_rule,new_rule)+'\n'
if '## Computer battles excluded from ladder' not in updated:
    updated+='\n## Computer battles excluded from ladder\n\nConfirmed computer battles retain their outcomes and review evidence in [COMPUTER_BATTLE_HISTORY.md](COMPUTER_BATTLE_HISTORY.md). The October 2 classification correction follows the owner\'s visible-Auto-option rule.\n'
history.write_text(updated,encoding='utf-8')
if computer.exists():
    computer_text=computer.read_text(encoding='utf-8')
else:
    computer_text='# Computer battle results\n\nThese selected recordings show an Auto option and are computer battles under Dustin\'s clarified rule, whether Auto is enabled or disabled. Their outcomes remain recorded here and are excluded from ladder totals. Auto control state and individual action authorship are separate facts.\n\n| Date | Source video in `Reviewed/` | Result | Player\'s visible deck core | Opponent | Outcome evidence | Classification evidence |\n| --- | --- | --- | --- | --- | --- | --- |\n'
cells=[cell.strip() for cell in row.split('|')[1:-1]]
cells[-1]=cells[-1].replace(' Auto state was not independently verified.','')
computer_text=computer_text.rstrip()+'\n| '+' | '.join(cells+[f'[Mode evidence](<{evidence}>)'])+' |\n'
computer.write_text(computer_text,encoding='utf-8')
receipt={'source':a.source,'changed_at_utc':datetime.now(timezone.utc).isoformat(),
 'authorization':'Direct owner clarification: any visible Auto option, even OFF, means computer opponent; exclude from ladder but still process.',
 'classification':'computer_battle','excluded_from_ladder':True,'original_outcome_row_preserved':row,
 'classification_evidence':str(evidence),'original_history_snapshot':str(baseline),
 'pre_history_sha256_before':hashlib.sha256(before.encode('utf-8')).hexdigest(),
 'pre_history_sha256_after':hashlib.sha256(history.read_bytes()).hexdigest(),
 'historical_ladder_total':{'games':len(results),'wins':wins,'losses':losses},
 'computer_history':str(computer),'live_season_totals_changed':False}
target=BATCH/a.source.split('_iOS')[0]/'CLASSIFICATION_RECEIPT.json'
target.write_text(json.dumps(receipt,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'source':a.source,'classification':'computer_battle','historical_ladder_total':receipt['historical_ladder_total'],'outcome_preserved':True,'live_season_totals_changed':False}))
