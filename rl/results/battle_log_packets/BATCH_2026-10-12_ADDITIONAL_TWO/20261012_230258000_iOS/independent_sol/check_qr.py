from pathlib import Path
import sys,json,hashlib
from PIL import Image
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent.parent/'20261012_225319000_iOS'/'qr_runtime'))
import zxingcpp
f=p.parent/'turn_evidence'/'t0001.50.jpg'
decoded=[x.text for x in zxingcpp.read_barcodes(Image.open(f))]
s=json.loads((p.parent/'SOURCE.json').read_text())
d=json.loads((p.parent.parent/'LIVE_DECK_SNAPSHOT.json').read_text())
o={'checker':'/root/check_later_230258','source_video':s['video_basename'],'source_sha256':s['sha256'],'frame_source_seconds':1.5,'frame':str(f),'frame_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'independently_decoded_payloads':decoded,'live_snapshot_payload':d['qr_payload'],'exact_payload_match':d['qr_payload'] in decoded,'deck_snapshot_slots':len(d['cards_in_log_order']),'deck_snapshot_count_sum':sum(x['count'] for x in d['counts_by_name_and_variant']),'artwork_rarity':'unverified'}
(p/'QR_CHECK.json').write_text(json.dumps(o,indent=2)+'\n')
print(json.dumps(o))
