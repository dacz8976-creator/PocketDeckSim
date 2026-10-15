from pathlib import Path
from PIL import Image,ImageDraw
import sys
p=Path(__file__).resolve().parent
kind=sys.argv[1]
times=[float(s) for s in sys.argv[2:]]
w=1170;h=507 if kind=='bottom' else 784
sheet=Image.new('RGB',(w*2,(h+30)*((len(times)+1)//2)),'white');d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 im=Image.open(p/'turn_evidence'/f't{t:07.2f}_{kind}.jpg');x=i%2*w;y=i//2*(h+30);sheet.paste(im,(x,y+30));d.text((x+5,y+5),str(t),fill='black')
out=p/f'montage_{kind}_{times[0]:07.2f}.jpg';sheet.save(out,quality=95);print(out)
