from PIL import Image
from pathlib import Path
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol/native')
im=Image.open(p/'t0130.00.jpg');print(im.size);im.crop((995,1590,1170,1940)).resize((525,1050)).save(p/'trainer_discard130.jpg',quality=95)
