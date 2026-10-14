"""Copy accepted turn prose as provenance, without reconstructing new observations."""
import hashlib, json, re
from pathlib import Path

BATCH = Path(__file__).resolve().parent
games = json.loads((BATCH/'EVIDENCE_AVAILABILITY.json').read_text(encoding='utf-8'))
counts=[]
for game in games:
    review = Path(game['accepted_review'])
    text = review.read_text(encoding='utf-8-sig')
    rows=[]
    for number,line in enumerate(text.splitlines(),1):
        if line.startswith('|') and re.search(r'\b[Tt]urn\s+\d+',line):
            match = re.search(r'\b[Tt]urn\s+(\d+)',line)
            rows.append({'turn_number':int(match.group(1)),'accepted_source_line':number,'verbatim_accepted_row':line,'basis':'inherited_accepted_review_not_new_visual_observation'})
    for match in re.finditer(r'^###\s+Turn\s+(\d+)[^\n]*\n(.*?)(?=^### |^## |\Z)',text,re.M|re.S):
        if int(match.group(1)) not in [r['turn_number'] for r in rows]:
            rows.append({'turn_number':int(match.group(1)),'accepted_source_line':text[:match.start()].count('\n')+1,'verbatim_accepted_section':match.group(0).strip(),'basis':'inherited_accepted_review_not_new_visual_observation'})
    rows.sort(key=lambda r:r['turn_number'])
    folder=BATCH/game['source'].split('_iOS')[0]
    folder.mkdir(exist_ok=True)
    target=folder/'INHERITED_TURNS.json'
    if not target.exists():
        target.write_text(json.dumps({'source':game['source'],'accepted_review':str(review),'accepted_review_sha256':hashlib.sha256(review.read_bytes()).hexdigest(),'rows':rows,'limits':'Only explicitly turn-numbered accepted prose is copied. Zero rows means format unavailable, not zero game turns. This is reference scaffolding, not a completed capture ledger.'},indent=2,ensure_ascii=False),encoding='utf-8')
    counts.append({'source':game['source'],'inherited_rows':len(rows)})
print(json.dumps(counts))
