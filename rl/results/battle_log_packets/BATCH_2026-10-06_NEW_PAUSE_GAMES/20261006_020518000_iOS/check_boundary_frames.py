from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).parent
ts=[64,93,139,154,176,194,230,261,298,330,366,429,448,482,516,566,582]
for start in [0,9]:
    part=ts[start:start+9]; out=Image.new('RGB',(1755,3*390),'white');d=ImageDraw.Draw(out)
    for i,t in enumerate(part):
        with Image.open(P/'turn_evidence'/f't{t:07.2f}.jpg') as im:
            crop=im.crop((0,900,1170,1600));crop.thumbnail((585,350));x=i%3*585;y=i//3*390
            out.paste(crop,(x,y+30));d.text((x+10,y+5),f'concluded row {start+i+1} at {t}s',fill='black')
    out.save(P/f'boundary_labels_{start}.jpg')
for side,ts,bounds in [('owner',[59.5,94.5,158.3,197.5,264,332.8,433,485.6,570],(900,2020,1170,2340)),('opponent',[68,142,176,234,302,367,450,520],(0,240,350,520))]:
    out=Image.new('RGB',(1050,1050),'white');d=ImageDraw.Draw(out)
    for i,t in enumerate(ts):
        with Image.open(P/'turn_evidence'/f't{t:07.2f}.jpg') as im:
            crop=im.crop(bounds);x=i%3*350;y=i//3*350;out.paste(crop,(x,y+25));d.text((x+5,y+2),f'{side} at {t}s',fill='black')
    out.save(P/f'selected_energy_{side}.png')
ts=[64,93,139,154,176,194,230,261,298,330,366,429,448,482,516,566,579]
for side,bounds in [('owner',(900,2020,1170,2340)),('opponent',(0,240,350,520))]:
    out=Image.new('RGB',(2100,1050),'white');d=ImageDraw.Draw(out)
    for i,t in enumerate(ts):
        with Image.open(P/'turn_evidence'/f't{t:07.2f}.jpg') as im:
            crop=im.crop(bounds);x=i%6*350;y=i//6*350;out.paste(crop,(x,y+25));d.text((x+5,y+2),f'end row{i+1}: {side} {t}s',fill='black')
    out.save(P/f'ending_energy_{side}.png')
