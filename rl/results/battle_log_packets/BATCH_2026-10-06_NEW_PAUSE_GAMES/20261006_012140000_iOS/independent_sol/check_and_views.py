import json, hashlib
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageDraw

p = Path(__file__).resolve().parent.parent
out = Path(__file__).resolve().parent
required = ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
supplemental = ['QUALIFIED_DECK_CANDIDATE.json','RECORDING_METADATA.json','SUBMISSION_RECEIPT.json','STRUCTURAL_VALIDATION.json','../LIVE_DECK_SNAPSHOT.json','../NEW_DECK_ENTRIES.json','../20261005_183108000_iOS/QR_DECODE.json']
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
e = json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
submission = json.loads((p/'SUBMISSION_RECEIPT.json').read_text(encoding='utf-8'))
receipt={'checked_input_sha256':{n:sha(p/n) for n in required},'supplemental_checked_input_sha256':{n:sha(p/n) for n in supplemental if (p/n).is_file()},'submission_hash_mismatches':[],'crop_checks':[]}
for n,h in receipt['checked_input_sha256'].items():
    if submission['file_manifest'][n]['sha256'] != h: receipt['submission_hash_mismatches'].append(n)
for f in e['frames']:
    full=Image.open(p/f['full_frame_path']).convert('RGB')
    row={'id':f['evidence_id'],'native_size':list(full.size),'crops':{}}
    for k in ['bottom_crop','top_crop']:
        c=f[k]; b=c['pixel_bounds_x0_y0_x1_y1']; actual=Image.open(p/c['path']).convert('RGB'); expected=full.crop(b)
        mae=sum(ImageStat.Stat(ImageChops.difference(actual,expected)).mean)/3
        row['crops'][k]={'size':list(actual.size),'expected_size':list(expected.size),'mean_absolute_pixel_error':mae,'dimensions_match':actual.size==expected.size,'sha256':sha(p/c['path'])}
    receipt['crop_checks'].append(row)
(out/'INTEGRITY_CHECK.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def montage(name,times,kind='full',bounds=None,scale=None):
    ims=[]
    for t in times:
        suffix=f't{t:07.2f}'
        path=p/'turn_evidence'/(suffix+'.jpg') if kind=='full' else p/'turn_evidence'/'crops'/(suffix+'_'+kind+'.jpg')
        im=Image.open(path).convert('RGB')
        if bounds: im=im.crop(bounds)
        if scale: im=im.resize((scale,round(im.height*scale/im.width)))
        header=Image.new('RGB',(im.width,30),'white');ImageDraw.Draw(header).text((10,8),f'{t:.2f}s {kind}',fill='black')
        panel=Image.new('RGB',(im.width,im.height+30),'white');panel.paste(header);panel.paste(im,(0,30));ims.append(panel)
    dest=Image.new('RGB',(max(x.width for x in ims),sum(x.height for x in ims)),'white'); y=0
    for im in ims:dest.paste(im,(0,y));y+=im.height
    dest.save(out/(name+'.png'))

montage('T2_hand_candidates',[60.5,62.5,65.5,84],'bottom')
montage('T4_hand_candidates',[108.5,110.5,113.5,114],'bottom')
montage('T6_hand_candidates',[149,151,154,168],'bottom')
montage('opponent_ordinary_top',[90,92,94,96,98,100,101,103,104],'top')
montage('T2_draw_reveals',[59,64,75,76],'full',(250,500,950,1550))
montage('T6_pop_coin',[150,151,153,157.5,158],'full',None,390)
montage('T6_wally_energy',[162,163,164,165,166,167,168],'full',None,390)
montage('KO_phases',[173,173.5,174,174.5,175,178,182],'full',None,390)
montage('terminal',[0,18,20,203,204,214.8],'full',None,390)
print(json.dumps({'hash_mismatches':receipt['submission_hash_mismatches'],'frames':len(receipt['crop_checks']),'max_crop_mae':max(v['mean_absolute_pixel_error'] for r in receipt['crop_checks'] for v in r['crops'].values()),'outputs':str(out)},ensure_ascii=False))
