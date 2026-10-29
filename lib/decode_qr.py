#!/usr/bin/env python3
"""Decode Pokémon TCG Pocket in-game deck QR codes (screenshots) into DeckGym card ids.

Format (verified on 15 decks, 2026-09-10): base64 -> [n_trainers][3-byte ids = 10,000,000 + id]
[n_pokemon][3-byte ids][n_energy][energy bytes]. Ids are the entity numbers in
s216_card_catalog_v1.json; the lowest-rarity printing is reported. Energy bytes: 1 Grass, 2 Fire,
3 Water, 4 Lightning, 5 Psychic, 6 Fighting, 7 Darkness, 8 Metal (verified); 9/10 unverified.
The QR is read from the crop [0.45h:0.77h, 0.17w:0.83w] of a phone screenshot; adjust if the
game UI moves.

Dual Fusion (C1) cards (release checklist R7): the catalog has none yet, so their entities come from
the PROVISIONAL overlay lib/c1_provisional_entities.json (read by lib/check_c1_overlay.py), only for
entities the catalog lacks: the catalog always wins. Such a card prints with "(provisional C1 entity)"
and its lowest C1 id. A new card the overlay does not cover (C1 118 Bewear ex, SP1, P-C) still prints
as UNKNOWN pokemon:N. If the catalog has any id the overlay lists, this tool refuses: compare with
lib/check_c1_overlay.py and drop the overlay. PDL_C1_OVERLAY=off skips the overlay.

deps: pip install opencv-python-headless numpy zxing-cpp   (decode() alone needs none of them)
usage: decode_qr.py <screenshot.png> [more ...]
"""
import glob, sys, base64, json, collections, os
_here=os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path: sys.path.insert(0,_here)
import check_c1_overlay as c1  # noqa: E402  (the provisional C1 overlay, release checklist R7)
_cat=next((p for p in (os.environ.get('PDL_CATALOG',''), os.path.join(_here,'s216_card_catalog_v1.json'),
                       os.path.join(_here,'..','s216_card_catalog_v1.json'), 's216_card_catalog_v1.json') if p and os.path.exists(p)), None)
if not _cat: raise SystemExit('s216_card_catalog_v1.json not found (set PDL_CATALOG or run from the project)')
cat=json.load(open(_cat, encoding='utf-8'))['aliases']
by=collections.defaultdict(list)
rank={'C':0,'U':1,'R':2,'RR':3,'AR':4,'SR':5,'SAR':6,'IM':7,'UR':8,'SSR':9}
for a in cat:
    kind,num=a['entity_key'].split(':'); by[(kind,int(num))].append(a)
# C1 entities the catalog lacks, from the provisional overlay (load() refuses any overlap: the catalog wins)
prov=collections.defaultdict(list)
for a in c1.load(cat)[0].values():
    prov[c1.split_key(a['entity_key'])].append(a)
def lookup(kind,num):
    """(card id, name, provisional) of a code's entity: the catalog's lowest-rarity printing, else the
    overlay's lowest C1 id; None if neither has it."""
    lst=by.get((kind,num))
    if lst:
        a=sorted(lst,key=lambda a:(rank.get(a['rarity'],5),a['deckgym_id']))[0]
        return a['deckgym_id'],a['raw_name'],False
    lst=prov.get((kind,num))
    if lst:
        a=min(lst,key=lambda a:int(a['deckgym_id'].split()[1]))
        return a['deckgym_id'],a['raw_name'],True
    return None
def name(kind,num):
    r=lookup(kind,num)
    if not r: return f"UNKNOWN {kind}:{num}"
    return f"{r[1]} {r[0]} {c1.NOTE}" if r[2] else f"{r[1]} {r[0]}"
ENERGY={1:'Grass?',2:'Fire',3:'Water',4:'Lightning',5:'Psychic',6:'Fighting',7:'Darkness',8:'Metal',9:'Dragon?',10:'Colorless?'}
def read_qr(path):
    import cv2, numpy as np, zxingcpp  # here, so decode() needs only the standard library
    img=cv2.imread(path); h,w=img.shape[:2]
    crop=img[int(h*0.45):int(h*0.77), int(w*0.17):int(w*0.83)]
    gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
    sat=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)[:,:,1]
    cands=[gray, 255-((sat>60).astype(np.uint8)*255)]
    for k in (5,7,9,11,13):
        ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))
        cands.append(255-cv2.dilate((sat>60).astype(np.uint8)*255,ker))
    for im in cands:
        im=cv2.copyMakeBorder(im,40,40,40,40,cv2.BORDER_CONSTANT,value=255)
        r=zxingcpp.read_barcodes(im)
        if r: return r[0].text
    return None
def read_code(code):
    """The code's (trainer entity numbers, Pokémon entity numbers, energy bytes), in the code's order."""
    b=base64.b64decode(code); i=0
    nt=b[i]; i+=1; tr=[]
    for _ in range(nt): tr.append(int.from_bytes(b[i:i+3],'big')-10_000_000); i+=3
    npk=b[i]; i+=1; pk=[]
    for _ in range(npk): pk.append(int.from_bytes(b[i:i+3],'big')); i+=3
    ne=b[i]; i+=1; en=list(b[i:i+ne]); i+=ne
    assert i==len(b)
    return tr,pk,en
def decode(code):
    tr,pk,en=read_code(code)
    return collections.Counter(name('pokemon',n) for n in pk), collections.Counter(name('trainer',n) for n in tr), en
if __name__=='__main__':
    for path in sys.argv[1:]:
        code=read_qr(path)
        if not code: print("==",os.path.basename(path),"DECODE FAILED"); continue
        pk,tr,en=decode(code)
        print(f"== {os.path.basename(path)}  {sum(pk.values())} Pokémon / {sum(tr.values())} Trainers  Energy: {', '.join(ENERGY.get(e,str(e)) for e in en)}  code={code}")
        for n,c in pk.items(): print(f"  {c} {n}")
        for n,c in tr.items(): print(f"  {c} {n}")
