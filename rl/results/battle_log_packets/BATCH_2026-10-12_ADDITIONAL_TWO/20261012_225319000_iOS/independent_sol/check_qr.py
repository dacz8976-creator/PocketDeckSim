import json, hashlib, sys
from pathlib import Path
from PIL import Image
p=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(p/'qr_runtime'))
import zxingcpp
f=p/'turn_evidence/t0000.00.jpg'
r=zxingcpp.read_barcodes(Image.open(f))
snapshot=json.loads((p.parent/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8-sig'))
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
out={'checker':'/root/check_later_225319','source_video':source['video_basename'],'source_sha256':source['sha256'],'frame_source_seconds':0,'frame':str(f),'frame_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'independently_decoded_payloads':[x.text for x in r],'live_snapshot_payload':snapshot['qr_payload'],'exact_payload_match':any(x.text==snapshot['qr_payload'] for x in r),'deck_snapshot_slots':len(snapshot['cards_in_log_order']),'deck_snapshot_count_sum':sum(x['count'] for x in snapshot['counts_by_name_and_variant']),'artwork_rarity':'unverified'}
(p/'independent_sol/QR_CHECK.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
