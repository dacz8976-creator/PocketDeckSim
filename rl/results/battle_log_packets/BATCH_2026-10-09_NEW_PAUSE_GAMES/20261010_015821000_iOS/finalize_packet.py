import json,re
from pathlib import Path
p=Path(__file__).parent
def load(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,d):(p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=load('TURN_LEDGER.json');row=d['turns'][0]
row['timing']['end_after_resolution_seconds']=58
row['board_after']['evidence_ids']=['F0058_00'];row['board_after']['phase']='after End Turn; no automatic effects'
for side in ('owner','opponent'):
    row['board_after'][side]['evidence_ids']=['F0058_00']
    row['board_after'][side]['energy_zone']['evidence_ids']=['F0058_00']
    row['board_after'][side]['active']['evidence_ids']=['F0058_00']
# Make start6's evidence refer to its boundary, retaining the attack's source226 for the lock.
b=d['turns'][5]['board_at_start']
for side in ('owner','opponent'):
    b[side]['evidence_ids']=['F0231_00'];b[side]['energy_zone']['evidence_ids']=['F0231_00']
    for mon in [b[side]['active']]+b[side]['bench_in_position_order']:mon['evidence_ids']=['F0231_00']
save('TURN_LEDGER.json',d)
for filename in ('REVIEW.md','COVERAGE.md'):
    text=(p/filename).read_text(encoding='utf-8')
    # Only ordinary prose is reformatted; preserve source names, IDs, paths and the exact hash.
    protected=[]
    pattern=r'20261010_015821000_iOS\.MP4|8d64e896d3125e504b7186754cbf2c21c0b5fcbc61f65524f6de27a2effd2a38|SOURCE\.json|[A-Z_]+\.json|New deck13|Dacz8976|\[0,2025,1170,2532\]|\[0,0,1170,720\]'
    def hold(m):protected.append(m.group());return '\u0001'+chr(0xE000+len(protected)-1)+'\u0002'
    text=re.sub(pattern,hold,text)
    text=re.sub(r'(?<=[A-Za-z])(?=\d)',' ',text)
    text=re.sub(r'(?<=\d)(?=[A-Za-z])',' ',text)
    text=re.sub(r'(?<=\d)(?=HP|Energy|Water|cards|point|draw|reveals|plays|turns)', ' ',text)
    text=text.replace(' s','s') if False else text
    replacements={'turn public-action':'turn public action','250,253':'250, 253','26.5,26.8,27':'26.5, 26.8, 27','43/45/48':'43 /45 /48','94/96/99':'94 /96 /99','197/199/202':'197 /199 /202','each of 6 turns':'each of 6 turns','one actual row for each':'one actual row for each','plus Stormy':'plus Stormy','Waterandpaidretreat':'Water and paid retreat','normaldraw':'normal draw','first-player':'first player','initialdraw':'initial draw','beforeActive':'before Active','Research 2 reveals':'Research 2 reveals','namednormaldraw':'named normal draw','skip-stageevolution':'skip stage evolution','Candyevolution':'Candy evolution','Victoryanimationandresultcard':'Victory animation and result card','sourceending':'source ending','afterattack':'after attack','deckscreen':'deck screen','selectedevent':'selected event','all 7 plays':'all 7 plays','Stadiumdraw':'Stadium draw','checkupKO':'checkup KO','Tool,endability':'Tool, end ability','concession 242':'concession 242','native-event':'native event','sourcebound':'source bound'}
    for a,v in replacements.items():text=text.replace(a,v)
    for i,v in enumerate(protected):text=text.replace('\u0001'+chr(0xE000+i)+'\u0002',v)
    (p/filename).write_text(text,encoding='utf-8')
with (p/'REVIEW.md').open('a',encoding='utf-8') as f:
    f.write('\nTurn table rows correspond in order to rows1–6 in [TURN_LEDGER.json](TURN_LEDGER.json). Selected owner start frames are [42.5s](turn_evidence/t0042.50.jpg), [93.3s](turn_evidence/t0093.30.jpg) and [196s](turn_evidence/t0196.00.jpg). The original opening is [26.5s](turn_evidence/t0026.50.jpg), and the ending is [242s](turn_evidence/t0242.00.jpg) plus [253s](turn_evidence/t0253.00.jpg).\n')
print('Finalized boundary evidence and prose spacing')
