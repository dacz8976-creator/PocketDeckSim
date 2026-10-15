import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent.parent
native = [1, 7, 19, 27, 36, 53.2, 55, 63, 67, 88, 92, 103.5, 104.5, 105, 105.5, 106, 106.4, 107, 107.5, 115, 118.5, 128, 131]
paths = [f'turn_evidence/t{sec:07.2f}.jpg' for sec in native]
paths += ['turn_evidence/t0053.00_top.jpg', 'turn_evidence/t0105.00_top.jpg']
paths += [f'turn_evidence/actions_{i}.jpg' for i in range(5)]
rows = []
for name in paths:
    path = P/name
    with Image.open(path) as im: size = list(im.size)
    rows.append({'path':name, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'dimensions':size, 'inspection':'visual'})
manifest = {'reviewer':'/root/verify_pause_004128', 'review_model':'gpt-6.1-sol', 'reasoning_effort':'high', 'checked_at_utc':datetime.now(timezone.utc).isoformat(), 'source_video':'20261012_004128000_iOS.MP4', 'source_sha256':'dbf23091859cbe159afc724f32f517f75925ab214343474285306b035ee4146e', 'scope':'Bounded independent check of opening, ordinary first decision, draw order, turn-boundary states and terminal sequence using retained source evidence, plus two independent native seeks. This is not a second full video replay.', 'viewed_evidence':rows, 'new_native_extractions':2, 'independent_seek_seconds':[27,121], 'independent_seek_exact_jpeg_matches':True, 'limits':['Requested seek seconds are not exact measured video frame PTS.', 'Fresh QR pixel decoding was unavailable in selected runtime because cv2 is absent; retained QR was visually inspected and payload bytes, source binding, semantic slot counts and exact live code equality independently checked.', 'Hidden opponent identities and unshown discard dialogs remain unavailable.']}
(P/'independent_sol/VIEWED_EVIDENCE.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Retained {len(rows)} bounded visual evidence entries')
