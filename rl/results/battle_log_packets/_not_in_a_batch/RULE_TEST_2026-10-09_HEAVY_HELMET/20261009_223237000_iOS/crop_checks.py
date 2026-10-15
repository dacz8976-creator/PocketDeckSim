from PIL import Image
from pathlib import Path
r=Path(__file__).parent
Image.open(r/'dense/sec_078.jpg').crop((200,1190,980,1680)).save(r/'wailmer_detail_native.jpg',quality=98)
Image.open(r/'dense/sec_274.jpg').crop((695,380,1040,695)).save(r/'opponent_bench_native.jpg',quality=98)
