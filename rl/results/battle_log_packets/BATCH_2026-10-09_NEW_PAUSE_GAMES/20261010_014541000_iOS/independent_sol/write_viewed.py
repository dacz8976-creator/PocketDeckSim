import json,hashlib
from pathlib import Path
from PIL import Image
p=Path(__file__).parent
packet=p.parent
native=[39,56,58,67,70,126.5,260,263,265,268,289,324,346,351,357,393,434,439,451,460,473.3,483,486,489,501,461,462,472,473,476,495,230,206.5,55]
new=[264,293,469,470,471,490,491,492,223,226]
rows=[]
for folder,times in [('turn_evidence',native),('independent_sol',new),('dense_seeks',[465,468,471])]:
    for t in times:
        path=packet/folder/f't{t:07.2f}.jpg'
        rows.append({'path':str(path.relative_to(packet)).replace('\\','/'),'source_video':'20261010_014541000_iOS.MP4','requested_source_seconds':t,'measured_frame_pts':None,'dimensions':list(Image.open(path).size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'viewed':True,'native':folder!='dense_seeks'})
path=packet/'dense_seeks/sheet_462.jpg'
rows.append({'path':'dense_seeks/sheet_462.jpg','source_video':'20261010_014541000_iOS.MP4','source_seconds_in_sheet':list(range(438,463,3)),'dimensions':list(Image.open(path).size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'viewed':True,'native':False,'role':'bounded action-order location sheet'})
result={'reviewer':'/root/check_014541','source_sha256':'f23cff1b9c79032374130dfdb2488b086b45d08ac5c6f734f6cc392a8a6330ae','scope':'Bounded independent acceptance, not a repeated full first pass','frames':rows,'new_native_extractions':len(new),'limitations':['Requested seeks, not measured PTS','Evidence viewing excludes failed missing-path attempts','Full-pass coverage is checked through existing account, coverage and first reviewer manifest']}
(p/'VIEWED_EVIDENCE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(rows))
