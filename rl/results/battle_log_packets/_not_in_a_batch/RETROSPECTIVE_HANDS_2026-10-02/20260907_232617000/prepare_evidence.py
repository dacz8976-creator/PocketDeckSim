from pathlib import Path
from PIL import Image,ImageDraw
import json,time
base=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs')
pkt=base/'Recording_QA/RETROSPECTIVE_HANDS_2026-10-02/20260907_232617000'
f=base/'Recording_QA/20260907_232617_v5_review/final_packet/frames'
e=pkt/'turn_evidence';e.mkdir(exist_ok=True)
times=[15,20,35,40,47,49,50,51,52,53,54,56,57,63,95,96,97,100,134,135,136,137,138,139,140,141,142,143,145,156,157,160,162,210,211,212,213,214,215,216,217,219,220,222,223,224,225,226,235,236,237,260,261,262,263,264,265,266,267,269,270,277,281,299,300,301,302,303,304,305,306,308,309.8,310.6,311.2,312,313,314,317,318,355,356,357,358,360,365,382,385,386,387,389,390,391,407,408,430,436,441.3]
meta=[]
for t in times:
 path=f/f'{t:07.3f}.jpg'
 if not path.exists():continue
 im=Image.open(path);w,h=im.size
 for label,b in [('bottom',(0,int(h*.8),w,h)),('top',(0,0,w,720))]:
  out=e/f'{t:07.3f}_{label}.png';im.crop(b).save(out)
 meta.append({'timestamp_requested':t,'path':str(path),'dimensions':[w,h]})
json.dump(meta,open(pkt/'REUSED_FRAME_METADATA.json','w'),indent=2)
def sheet(ts,label):
 imgs=[]
 for t in ts:
  path=e/f'{t:07.3f}_{label}.png'
  im=Image.open(path);imgs.append((t,im))
 w=1170;h=sum(i.height+30 for _,i in imgs);sh=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(sh);y=0
 for t,i in imgs:d.text((4,y),f'Source elapsed {t:.3f}s native {label} crop',fill='black');sh.paste(i,(0,y+30));y+=i.height+30
 out=pkt/f'locator_{label}_{ts[0]}.png';sh.save(out);print(out)
sheet([51,138,214], 'bottom')
sheet([265,360,313], 'bottom')
sheet([52,138,215], 'top')
sheet([265,360], 'top')
