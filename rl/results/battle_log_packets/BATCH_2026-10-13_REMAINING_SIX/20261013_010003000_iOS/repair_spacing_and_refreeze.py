import json,re,hashlib
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
text=(p/'REVIEW.md').read_text(encoding='utf-8')
text=re.sub(r'\b(Healed|healed|from|to|heads|Heads|conceded|Victory|final|Darkness|Colorless|total|Whip|Hit|Blast|Slam|Dratini|Dragonair|Drampa|Glimmet|Glimmora|Regigigas|draws|Draws|points|damage)(?=\d)',r'\1 ',text)
(p/'REVIEW.md').write_text(text,encoding='utf-8')
freeze=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
freeze['review_components']['REVIEW.md']=hashlib.sha256((p/'REVIEW.md').read_bytes()).hexdigest()
receipt=json.loads((p/'REPAIR_RECEIPT.json').read_text(encoding='utf-8'))
receipt['new_components']=freeze['review_components']
(p/'REPAIR_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
freeze['supplement_hashes']['REPAIR_RECEIPT.json']=hashlib.sha256((p/'REPAIR_RECEIPT.json').read_bytes()).hexdigest()
freeze['frozen_utc']=datetime.now(timezone.utc).isoformat()
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prose spacing normalized; eight current component hashes frozen.')
