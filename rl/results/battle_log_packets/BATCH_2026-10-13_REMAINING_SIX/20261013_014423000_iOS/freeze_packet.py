import json,hashlib,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
p=Path(__file__).resolve().parent
subprocess.run([sys.executable,'-X','utf8',str(p/'build_packet.py')],check=True)
for fn in ['REVIEW.md','COVERAGE.md']:
 t=(p/fn).read_text(encoding='utf-8')
 if fn=='REVIEW.md':
  start=t.index('Opponent Energy reconciliation:');end=t.index('\n\n',start)
  t=t[:start]+"Opponent Energy reconciliation: T2 active Dedenne 0 -> 1 Lightning, then automatic Zeraora Thunderclap Flash 0 -> 1 at the end of its first turn (125s). T4 active Dedenne 1 -> 2. T6 Electric Generator heads attaches to benched Dedenne 0 -> 1, followed by the ordinary attachment to Emolga 0 -> 1. T8 benched Dedenne 1 -> 2. T10 Emolga 1 -> 2, then active Dedenne pays 1 Lightning to retreat, leaving 1. Emolga becomes Active with 2 Lightning."+t[end:]
  start=t.index('Named arrivals,');end=t.index('\n\n',start)
  t=t[:start]+"Named arrivals, hand candidate suitability, both start and after boards, Energy Zones, conditions, score, hand counts and public action order are recorded per turn in TURN_LEDGER.json and TURN_EVIDENCE.json. Research's bright 57s transition is its play animation. Its individual arrivals are Lucky Ice Pop at 59s, followed by Regigigas at 60s; both are in hand at 61s. Copycat draws Glimmora at 185s, then Glimmet at 186s. Card inspections are separate from arrival and play records."+t[end:]
 # Plain prose spacing; source filenames, hashes, identifiers and link paths retain bytes.
 t=t.replace('Review date:2026','Review date: 2026').replace('Entire326.723s','Entire 326.723s').replace('one battle. Pending','one battle. Pending').replace('Chicago20:44:23','Chicago 20:44:23').replace('October12,2026','October 12, 2026').replace('after10 turns','after 10 turns').replace('lost0-3','lost 0-3').replace('exact20-card','exact 20-card').replace('at30s','at 30s').replace('at32s','at 32s').replace('Native0s','Native 0s').replace('Owner Energy reconciliation: no attachmentT1','Owner Energy reconciliation: no attachment in T1').replace('T3Pawniard0->1','T3 Pawniard 0 -> 1').replace('T5Glimmet0->1','T5 Glimmet 0 -> 1').replace('T7Pawniard1->2','T7 Pawniard 1 -> 2').replace('T9Glimmora1->2','T9 Glimmora 1 -> 2').replace('sees3 opponent','sees 3 opponent').replace('deals120','deals 120').replace('to100','to 100').replace('leaving50','leaving 50').replace('does30','does 30').replace('checkup10','checkup 10').replace('Dedenne80','Dedenne 80').replace('does90','does 90').replace('same3 Tools','same 3 Tools').replace('All10 structured','All 10 structured').replace('Turn1;','Turn 1;').replace('Turn2;','Turn 2;').replace('Turn3;','Turn 3;').replace('Turn4;','Turn 4;').replace('Turn5;','Turn 5;').replace('Turn6;','Turn 6;').replace('Turn7;','Turn 7;').replace('Turn8;','Turn 8;').replace('Turn9;','Turn 9;').replace('Turn10;','Turn 10;').replace('versusRedGarados','versus RedGarados').replace('confirms10','confirms 10').replace('owner0/opponent3','owner 0/opponent 3').replace('damage30','damage 30').replace('opponentDedenne','opponent Dedenne')
 (p/fn).write_text(t,encoding='utf-8')
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
for row in ledger['turns']:
 if row['who_played']=='opponent':
  row['hand_at_start']['count']={2:5,4:2,6:3,8:3,10:4}[row['turn_number']]
  row['hand_at_start']['basis']='Count supported by visible fan and prior public additions/removals; hidden identities remain null.'
  row['hand_at_start']['evidence_ids']=row['board_at_start']['evidence_ids']
 # Preserve action-evidence timing windows, rather than claim exact touch times.
 for a in row['plays_in_order']:
  a['timing_basis']='Nearby retained action or completed-transition frame. Exact touch onset is not measured.'
  if a['kind']=='energy_attachment':
   n=row['turn_number'];b,aft={3:(141,143),5:(191,193),7:(225,226),9:(264,266),2:(121,123),4:(150,154),6:(209,210),8:(243,246),10:(287,288)}[n]
   a['transition_window_seconds']=[b,aft];a['evidence_ids']=['N'+f'{b:07.2f}','N'+f'{aft:07.2f}']
(p/'TURN_LEDGER.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([sys.executable,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8')
(p/'STRUCTURAL_VALIDATION.json').write_text(r.stdout,encoding='utf-8');print(r.stdout)
if r.returncode:raise SystemExit(r.returncode)
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
receipt=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),source_video=src['video_basename'],source_sha256=src['sha256'],reviewer='/root/remaining_014423',files={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},status='submitted_for_independent_acceptance',correction_history='Primary draft corrected during native dense pass before first freeze: Research actual order, opponent generator/manual attachment order, late Energy targets. No rejected packet or acceptance exists yet.')
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print('FROZEN eight files; no further edits during separate acceptance.')
