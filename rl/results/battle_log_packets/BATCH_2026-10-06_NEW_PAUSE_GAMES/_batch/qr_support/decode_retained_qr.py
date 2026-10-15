"""Read retained images only; reuse PDL image reader and pinned payload codec."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'deps'))
import cv2
import zxingcpp

PDL = Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab')
CODEC = PDL / 'third_party/s216/tcgp-deck-qr-102d75e/src/payload.js'
READER = PDL / 'lib/decode_qr.py'
CATALOG = PDL / 's216_card_catalog_v1.json'
NODE = Path(r'C:\Users\dacz8\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def decode_payload(payload):
    script = """const fs=require('node:fs');
    (async()=>{const m=await import('data:text/javascript;base64,'+fs.readFileSync(process.argv[1]).toString('base64'));
    const d=m.decodePayload(process.argv[2]);
    let roundtrip=null,roundtrip_limit=null;
    try {roundtrip=m.encodePayload(d,{allowUnselectableEnergy:true})===process.argv[2]} catch(e){roundtrip_limit=e.message}
    process.stdout.write(JSON.stringify({...d,energy:d.energyTypes.map(v=>({value:v,name:m.ENERGY_NAMES.get(v)||null,selectable:m.SELECTABLE_ENERGY.has(v)})),roundtrip,roundtrip_limit}));
    })().catch(e=>{console.error(e.message);process.exit(1)});"""
    result = subprocess.run([str(NODE), '-e', script, str(CODEC), payload], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('image', type=Path)
    ap.add_argument('--source-video', required=True, help='Original source basename, supplied by lead')
    ap.add_argument('--seconds', required=True, type=float, help='Source-local retained frame time')
    ap.add_argument('--source-sha256', help='Lead-verified original media hash; never inferred')
    ap.add_argument('--crop', nargs=4, type=int, metavar=('X1','Y1','X2','Y2'))
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    if args.out.exists():
        ap.error('Output exists; choose a new receipt path')
    img = cv2.imread(str(args.image))
    if img is None:
        ap.error('Image cannot be read')
    h, w = img.shape[:2]
    scan = img
    if args.crop:
        x1,y1,x2,y2 = args.crop
        if not (0 <= x1 < x2 <= w and 0 <= y1 < y2 <= h):
            ap.error('Crop outside native image')
        scan = img[y1:y2,x1:x2]
    found = list(dict.fromkeys(r.text for r in zxingcpp.read_barcodes(scan)))
    method = 'zxingcpp_native_image' if not args.crop else 'zxingcpp_native_crop'
    if not found:
        saved_argv = sys.argv
        try:
            sys.argv = [str(READER)]
            reader = runpy.run_path(str(READER))
        finally:
            sys.argv = saved_argv
        payload = reader['read_qr'](str(args.image))
        found = [payload] if payload else []
        method = 'existing_PDL_phone_crop_and_dotted_QR_variants'
    if len(found) != 1:
        ap.error(f'Expected exactly one QR payload, found {len(found)}. Retain a clearer native QR crop; no guessed identities.')
    payload = found[0]
    decoded = decode_payload(payload)
    if len(decoded['trainerIds']) + len(decoded['pokemonIds']) != 20:
        ap.error('Decoded payload does not contain exactly 20 card slots')
    aliases = json.loads(CATALOG.read_text(encoding='utf-8'))['aliases']
    by_entity = {}
    for alias in aliases:
        kind, num = alias['entity_key'].split(':')
        by_entity.setdefault((kind, int(num)), []).append(alias)
    cards = []
    for kind, ids in [('trainer', decoded['trainerIds']), ('pokemon', decoded['pokemonIds'])]:
        for num, count in Counter(ids).items():
            matches = by_entity.get((kind,num), [])
            names = sorted(set(a['raw_name'] for a in matches))
            functional = sorted(set(a['functional_id'] for a in matches))
            cards.append({'entity_kind':kind,'entity_id':num,'count':count,
                'name':names[0] if len(names)==1 else None,
                'name_candidates':names,'functional_ids':functional,
                'printing_aliases':sorted(set(a['printing_id'] for a in matches)),
                'resolution':'resolved_semantic_entity' if len(names)==1 and len(functional)==1 else 'unresolved',
                'printing_limit':'QR does not specify artwork, rarity or exact printing'})
    receipt = {'schema':'pause_batch_retained_qr_v1','decoded_at_utc':datetime.now(timezone.utc).isoformat(),
        'source_video':args.source_video,'source_seconds':args.seconds,'source_sha256':args.source_sha256,
        'retained_image':str(args.image.resolve()),'retained_image_sha256':digest(args.image),
        'native_dimensions':[w,h],'scan_crop_xyxy':args.crop,'read_method':method,
        'payload':payload,'payload_ascii_sha256':hashlib.sha256(payload.encode('ascii')).hexdigest(),
        'decoded':decoded,'card_slot_count':20,'cards':cards,
        'all_entities_resolved':all(c['resolution']=='resolved_semantic_entity' for c in cards),
        'dependencies':{'codec':str(CODEC),'codec_sha256':digest(CODEC),'reader':str(READER),'reader_sha256':digest(READER),
            'catalog':str(CATALOG),'catalog_sha256':digest(CATALOG),'catalog_provenance':'pinned community-derived catalog, not an official complete card export',
            'opencv':cv2.__version__},
        'limits':['QR is a filmed deck source, not a substitute for the required dated Pause Games log snapshot.',
            'A deck QR does not establish hidden draws, the opening hand, or that this deck was used throughout a battle.']}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.out),'card_slots':20,'all_entities_resolved':receipt['all_entities_resolved'],'energy':decoded['energy'],'roundtrip':decoded['roundtrip']}))

if __name__ == '__main__':
    main()
