from pathlib import Path
from PIL import Image
p=Path(__file__).parent
for f in (p/'evidence').rglob('*.jpg'):
    try:
        with Image.open(f) as im: im.verify()
    except Exception as e: print('INVALID', f, str(e))
# Crop only, no interpolation: opponent discard orientation aid.
with Image.open(p/'evidence/native/t0183.00.jpg') as im:
    im.crop((0,450,210,800)).rotate(180).save(p/'evidence/native/183_opponent_discard_rotated.png')
