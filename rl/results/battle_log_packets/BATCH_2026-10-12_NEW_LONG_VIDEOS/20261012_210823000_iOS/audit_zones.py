from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent
times=[38,50,54.5,85.5,87,114,117,160,166,200,206.5,220.5,224,287,292,314,316,352,355.5,388,426,429,432]
out=p/'energy_zone_audit';out.mkdir(exist_ok=True)
for i in range(0,len(times),8):
 s=Image.new('RGB',(1080,1640),'white');d=ImageDraw.Draw(s)
 for k,t in enumerate(times[i:i+8]):
  x=k%2*540;y=k//2*410;d.text((x+8,y+6),f'{t}s: opponent left / owner right',fill='black')
  with Image.open(p/'turn_evidence'/f't{t:07.2f}.jpg') as im:
   a=im.crop((80,240,350,620));b=im.crop((900,2015,1170,2395));a.save(out/f't{t:07.2f}_opponent.png');b.save(out/f't{t:07.2f}_owner.png');s.paste(a,(x,y+30));s.paste(b,(x+270,y+30))
 s.save(out/f'contact_{i//8+1}.png')
