from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent/'cue_audit'
fs=sorted((P/'reduced').glob('*.jpg'))
for s in range(0,len(fs),36):
 w,h=Image.open(fs[s]).size;out=Image.new('RGB',(w*6,(h+25)*6),'white');d=ImageDraw.Draw(out)
 for i,f in enumerate(fs[s:s+36]):
  x=i%6*w;y=i//6*(h+25);d.text((x+4,y+3),f'{s+i+.5:.1f}s',fill='black');out.paste(Image.open(f),(x,y+25))
 out.save(P/f'grid_{s//36+1:02}.jpg',quality=92)
print(len(fs))
