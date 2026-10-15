import json,hashlib,re,subprocess
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
def save(n,x): (p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
# Correct the first-turn preview from its actual Lightning symbol, rather than the later Water preview.
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
ledger['turns'][0]['board_after']['opponent']['energy_zone']['next']['type']='Lightning'
save('TURN_LEDGER.json',ledger)
# Source-faithful prose with ordinary spaces.
for name in ['REVIEW.md','COVERAGE.md']:
 text=(p/name).read_text(encoding='utf-8')
 text=re.sub(r'\b(at|At|turn|Turn|row|October|Duration|Native|native|show|and|exact|deck)(?=\d)',r'\1 ',text)
 text=re.sub(r'(\d)(s|HP)\b',r'\1 \2',text)
 text=text.replace('October 13,2026','October 13, 2026').replace('October 12,2026,20:00','October 12, 2026, 20:00')
 if name=='REVIEW.md':text+='\nThe byte-identical historical log deck is retained in HISTORICAL_DECK_MATCH.json. Its saved retrieval was 2026-10-13T04:53:35.861Z and its expanded list has 20 slots. This is historical provenance, with fresh_live_readback=false; current live access remains blocked.\n'
 (p/name).write_text(text,encoding='utf-8')
py=r'C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
validator=p.parents[1]/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([py,'-Xutf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8')
(p/'STRUCTURAL_VALIDATION.json').write_text(r.stdout,encoding='utf-8')
assert r.returncode==0,r.stdout+r.stderr
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
save('REVIEW_PACKET_HASHES.json',dict(source_video=source['video_basename'],source_sha256=source['sha256'],frozen_utc=datetime.now(timezone.utc).isoformat(),review_components={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names},supplement_hashes={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in ['SOURCE.json','SOURCE_TIME.json','QR_DECODE.json','HISTORICAL_DECK_MATCH.json','STRUCTURAL_VALIDATION.json']},scope='Eight completed worker components, frozen for independent acceptance; supplements are separate',visual_acceptance=False))
print(r.stdout)
print('Frozen eight components. Stop edits while independent checker reviews.')
