import json,re,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for name in names:
 f=p/name
 text=f.read_text(encoding='utf-8')
 text=text.replace('all three names are visibly established by 141','all three names are visibly established by the post-resolution hand at 145').replace('three-card names are observed by141','three-card names are observed by 145')
 if name.endswith('.md'):
  text=re.sub(r'\b([A-Za-z]{3,})(\d{1,3})(?![\dA-Za-z])',r'\1 \2',text)
  text=re.sub(r'(?<![A-Za-z0-9])(\d+(?:\.\d+)?)(points|point|damage|seconds|second|turns|turn|cards|cards|Energy|Fighting|Metal|HP|per)(?![A-Za-z])',r'\1 \2',text)
  text=text.replace('allfive','all five').replace('one0-','one 0-').replace('entire0-','entire 0-').replace('all0-','all 0-').replace('with2','with 2').replace('to1','to 1').replace('and480','and 480').replace('the20','the 20').replace('the90','the 90').replace('the190','the 190').replace('the40','the 40').replace('from200','from 200').replace('to230','to 230').replace('each return20','each return 20').replace('adds20per','adds 20 per').replace('adds50when','adds 50 when').replace('adds30for','adds 30 for').replace('draws/searches','draws and searches').replace('rightBench','right Bench').replace('26-deck','26-deck')
  text=text.replace('October 12,2026','October 12, 2026').replace('with five total Bench Pokémon','with five total Bench Pokémon')
 f.write_text(text,encoding='utf-8')
# Add an explicit arithmetic audit separate from direct fan counts.
ld=json.loads((p/'TURN_LEDGER.json').read_text())
audit={1:'4 after Active placement +1 normal Dragonair -1 Poké Ball +1 Dratini -1 bench Dratini -1 Research +2 Research draws -1 Helmet =4.',3:'4 carried +1 Axew -1 bench Axew -1 Dragonair -1 Copycat -2 shuffled Haxorus +3 Copycat -1 Poké Ball +1 searched Axew -1 bench Dratini =2.',5:'2 carried +1 Lucky Ice Pop -1 played Ice Pop =2. Energy attachment removes no hand card.',7:'2 carried +1 Rare Candy -1 Rare Candy -1 Haxorus evolution =1 Axew.',9:'1 carried +1 Rainbow Cave -1 bench Axew -1 Stadium =0.',11:'0 carried +1 Dragonair -1 evolution =0.'}
for t in ld['turns']:
 if t['who_played']=='owner':t['owner_hand_end']['count_reconciliation']=audit[t['turn_number']]
(p/'TURN_LEDGER.json').write_text(json.dumps(ld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Spacing, Copycat named-hand anchor and hand arithmetic finalized; hashes not yet frozen.')
ed=json.loads((p/'TURN_EVIDENCE.json').read_text())
existing={f['requested_source_seconds']:f for f in ed['frames']}
for ts,n in [(50,1),(54,1),(174,4)]:
 if ts not in existing:
  z=json.loads(json.dumps(existing[52]));stem=f't{ts:07.2f}';z.update(evidence_id='N'+f'{ts:07.2f}',requested_source_seconds=ts,turn_number=n,who_played='owner' if n==1 else 'opponent',full_frame_path='turn_evidence/'+stem+'.jpg')
  z['bottom_crop']['path']='turn_evidence/'+stem+'_bottom.jpg';z['top_crop']['path']='turn_evidence/'+stem+'_top.jpg';ed['frames'].append(z)
for z in ed['frames']:
 if z['requested_source_seconds'] in [49.5,129.5,132.5,218,220,223,313.5,315.5,395.5,397.5,481]:z['unzoomed']=False
ed['frames'].sort(key=lambda z:z['requested_source_seconds'])
(p/'TURN_EVIDENCE.json').write_text(json.dumps(ed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
