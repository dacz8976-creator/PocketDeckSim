import json, pathlib, hashlib, re, sys
from PIL import Image
import numpy as np
O=pathlib.Path(__file__).resolve().parent
P=O.parent.parent/'20260929_020916000'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def refs(x):
    if isinstance(x,dict):
        z=set()
        for k,v in x.items():
            if k=='evidence_ids': z.update(v)
            elif k!='turn_evidence_ids': z.update(refs(v))
        return z
    if isinstance(x,list): return set().union(*(refs(v) for v in x)) if x else set()
    return set()
E=read(P/'TURN_EVIDENCE.json'); M=read(P/'NATIVE_FILE_MANIFEST.json')
L=read(P/'TURN_LEDGER.json'); H=read(P/'HAND_SUPPLEMENT.json'); R=read(P/'REVIEW_SUPPLEMENT.json')
errors=[]; maes=[]; maxpts=0
for f in M['files']:
    x=pathlib.Path(f['path'])
    if sha(x)!=f['sha256'] or x.stat().st_size!=f['bytes']: errors.append('file hash/size '+str(x))
    if f['source_sha256']!=M['source_sha256']: errors.append('source SHA '+str(x))
for f in E['frames']:
    if 'decode_log' not in f: continue
    full=Image.open(f['full_frame_path']).convert('RGB')
    if full.size!=(1170,2532): errors.append('native dimensions '+f['evidence_id'])
    for k in ['top_crop','bottom_crop']:
        c=f[k]; b=c['pixel_bounds_x0_y0_x1_y1']; crop=Image.open(c['path']).convert('RGB')
        if crop.size!=(b[2]-b[0],b[3]-b[1]): errors.append('crop dimensions '+f['evidence_id'])
        delta=np.abs(np.asarray(full.crop(b),dtype=float)-np.asarray(crop,dtype=float))
        maes.append(float(delta.mean()))
    log=pathlib.Path(f['decode_log']).read_text(encoding='utf-8-sig')
    match=re.findall(r'\bn:\s*0\s+pts:\s*(-?\d+)\s+pts_time:([\d.-]+)',log)
    if not match or abs(float(match[0][1])-f['actual_frame_seconds_if_measured'])>0.0001: errors.append('PTS log '+f['evidence_id'])
    maxpts=max(maxpts,abs(f['requested_source_seconds']-f['actual_frame_seconds_if_measured']))
ids={f['evidence_id'] for f in E['frames']}; piles={d['snapshot_id'] for d in E['discard_snapshots']}
for row in L['turns']:
    missing=refs(row)-set(row['turn_evidence_ids'])
    if missing: errors.append('nested refs absent T'+str(row['turn_number'])+str(missing))
    if set(row['turn_evidence_ids'])-ids: errors.append('unresolved frame T'+str(row['turn_number']))
    if set(row['discard_snapshot_ids'])-piles: errors.append('unresolved pile T'+str(row['turn_number']))
for h in H['rows']:
    r=L['turns'][h['turn_number']-1]
    for hk,rk in [('untouched_post_draw_hand','owner_hand_start'),('before_end_hand','owner_hand_before_end'),('hand_after_end_automatic_events','owner_hand_end')]:
        if h[hk]!=r[rk]:errors.append('hand sync T'+str(h['turn_number'])+' '+hk)
if R['rows']!=L['turns']:errors.append('supplement/ledger rows differ')
out={'errors':errors,'native_file_entries_checked':len(M['files']),'frames_checked':len(E['frames']),'rows_checked':len(L['turns']),'owner_hand_rows_checked':len(H['rows']),'discard_ids_checked':len(piles),'jpeg_crop_alignment_mean_absolute_error_min':min(maes),'jpeg_crop_alignment_mean_absolute_error_max':max(maes),'crop_alignment_limit':'JPEG crops are recompressed; alignment comparison is approximate, not lossless equality','maximum_requested_vs_selected_pts_seconds':maxpts,'source_original_hash_reads':0,'source_decode_reads_for_this_validation':0,'encoding':'utf-8-sig'}
(O/(sys.argv[1] if len(sys.argv)>1 else 'BINDING_VALIDATION.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
