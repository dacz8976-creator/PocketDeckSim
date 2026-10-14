"""Repair only authored QR-name copies after frozen independent rejection G1."""
import hashlib,json,shutil
from pathlib import Path
P=Path(__file__).resolve().parent/'20261004_213625000_iOS'
backup=P/'submitted_before_independent_corrections';backup.mkdir(exist_ok=True)
path=P/'DECK_USED.json'
if not (backup/path.name).exists():shutil.copy2(path,backup/path.name)
doc=json.loads(path.read_text(encoding='utf-8'));changed=[]
def normalize(value,trail=''):
    if isinstance(value,str) and any(bad in value for bad in ('PokÃ©','Professorâ€')):
        corrected=value.encode('cp1252').decode('utf-8');changed.append(trail);return corrected
    if isinstance(value,list):return [normalize(x,trail+f'[{i}]') for i,x in enumerate(value)]
    if isinstance(value,dict):return {k:normalize(v,trail+'.'+k) for k,v in value.items()}
    return value
doc=normalize(doc)
assert len(changed)==8,(len(changed),changed)
path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'INDEPENDENT_CORRECTIONS.json').write_text(json.dumps({'repair_id':'G1','rejected_report':'independent_sol/CHECK_RESULT.json','prior_submission':'submitted_before_independent_corrections/DECK_USED.json','changed_paths':changed,'scope':'Only eight authored copied card names normalized. Original QR receipt/catalog, all entity IDs/counts and source evidence unchanged.','current_sha256':{'DECK_USED.json':hashlib.sha256(path.read_bytes()).hexdigest()}},indent=2)+'\n',encoding='utf-8')
print('Normalized eight independently identified authored name fields.')
