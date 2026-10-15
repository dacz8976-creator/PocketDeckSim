from pathlib import Path
import subprocess, sys, json, datetime
p=Path(__file__).parent
r=subprocess.run([sys.executable,str(p.parent/'validate_packet.py'),str(p)],capture_output=True,text=True,encoding='utf-8')
receipt=json.loads(r.stdout)
receipt.update(checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checker='batch validate_packet.py; worker hand/board reconciliation',source_json='SOURCE.json',worker='/root/pause_034953')
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
selected=[f for f in evidence['frames'] if f.get('selected_for_start_hand')]
checks=[]
for t in ledger['turns']:
    if t['who_played']=='owner':
        h=t['owner_hand_reconciliation']
        checks.append(h['start']+h['card_additions_after_start']-h['card_removals']==h['end'])
    for bkey in ('board_at_start','board_after'):
        for who in ('owner','opponent'):
            b=t[bkey][who]
            checks.append(len(b['bench_in_position_order'])==3)
            for pk in [b['active']]+b['bench_in_position_order']:
                if pk.get('name'):
                    checks.append(pk['hp_max']-pk['damage']==pk['hp_now'])
                    checks.append(sum(pk['attached_energy']['by_type'].values())==pk['attached_energy']['total'])
receipt['worker_consistency_checks']=dict(selected_owner_hands=len(selected),expected_owner_hands=8,all_selected_intact_flags=all(f['before_first_play'] and f['unzoomed'] and f['hand_spread'] for f in selected),hand_HP_energy_position_arithmetic_pass=all(checks),native_frames=len(evidence['frames']),owner_start_end_counts=[[t['turn_number'],t['owner_hand_reconciliation']['start'],t['owner_hand_reconciliation']['end']] for t in ledger['turns'] if t['who_played']=='owner'])
receipt['structural_pass']=receipt['structural_pass'] and len(selected)==8 and all(checks)
(p/'STRUCTURAL_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=True,indent=2))
raise SystemExit(0 if receipt['structural_pass'] else 1)
