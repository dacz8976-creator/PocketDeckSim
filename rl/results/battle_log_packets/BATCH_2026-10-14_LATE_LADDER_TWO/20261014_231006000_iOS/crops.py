from PIL import Image
from pathlib import Path
p=Path(__file__).parent/'evidence'
for file,box,name in [('t0085.00.jpg',(870,805,1170,1080),'rainbow_cave'),('t0120.00.jpg',(410,960,800,1500),'ninetales_text'),('t0260.00.jpg',(0,1310,370,1790),'soothing_shore')]:
 im=Image.open(p/file);im.crop(box).save(p/(name+'.png'))
