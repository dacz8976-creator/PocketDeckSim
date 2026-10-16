"""Verify exact accepted night-batch rows against a fresh live UI reload."""
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
BATCH=ROOT/'Recording_QA/BATCH_2026-10-14_NIGHT_LADDER_FOUR'
p=argparse.ArgumentParser()
p.add_argument('sources',nargs='+')
a=p.parse_args()
allowed=json.loads((BATCH/'OWNER_CONTEXT.json').read_text(encoding='utf-8'))['selected_sources']
assert len(a.sources)==len(set(a.sources)) and set(a.sources).issubset(allowed)
before=(BATCH/'LADDER_BEFORE_AX.txt').read_text(encoding='utf-8')
raw_path=BATCH/'LADDER_RELOAD_AX.txt'
raw=raw_path.read_text(encoding='utf-8')
assert 'Saved games loaded.' in before and 'Saved games loaded.' in raw

def totals(text, label):
    summary=text.split('container decks')[0]
    values=[re.sub(r'^\s*\d+ text ', '', line) for line in summary.splitlines() if re.match(r'^\s*\d+ text ',line)]
    i=values.index(label)
    return dict(zip(['wins','losses','games'],map(int,values[i+1:i+4])))

baseline=totals(before,'All decks')
deck_before=totals(before,'A. Ninetales / Raticate')
assert baseline=={'wins':7,'losses':13,'games':20}, 'Reconcile changed live baseline'
entries=[]
for name in a.sources:
    packet=BATCH/Path(name).stem
    entry=json.loads((packet/'LADDER_ENTRY.json').read_text(encoding='utf-8'))
    assert json.loads((packet/'REGISTRATION_RESULT.json').read_text(encoding='utf-8'))['exit_code']==0
    assert entry['source_filename']==name and entry['section']=='d13', 'Review deck routing before using this batch verification'
    entries.append((packet,entry))
wins=sum(e['result']=='win' for _,e in entries)
losses=len(entries)-wins
expected={k:baseline[k]+v for k,v in [('wins',wins),('losses',losses),('games',len(entries))]}
deck_expected={k:deck_before[k]+v for k,v in [('wins',wins),('losses',losses),('games',len(entries))]}
assert totals(raw,'All decks')==expected
assert totals(raw,'A. Ninetales / Raticate')==deck_expected
prior_notes=[re.sub(r'^\s*\d+ text ', '', line) for line in before.splitlines() if re.match(r'^\s*\d+ text .*20261014_\d+_iOS\.MP4',line)]
assert len(prior_notes)==10 and all(raw.count(note)==1 for note in prior_notes)
now=datetime.now(timezone.utc).isoformat()
lines=raw.splitlines()
receipts=[]
for packet,entry in entries:
    assert raw.count(entry['source_filename'])==1
    matches=[i for i,line in enumerate(lines) if line.strip().endswith('text '+entry['note'])]
    assert len(matches)==1
    i=matches[0]
    start=max(j for j in range(i) if re.fullmatch(r'\s*\d+ row',lines[j]))
    end=next((j for j in range(i+1,len(lines)) if re.fullmatch(r'\s*\d+ row',lines[j])),len(lines))
    values=[re.sub(r'^\s*\d+ text ', '', line) for line in lines[start:end] if re.match(r'^\s*\d+ text ',line)]
    assert values[:3]==['W' if entry['result']=='win' else 'L',entry['opponent_deck'],entry['note']]
    receipt={'saved':True,'fresh_reload_verified':True,'checked_utc':now,'source_filename':entry['source_filename'],'source_sha256':entry['source_sha256'],'artifact':entry['artifact'],'source_occurrences_after_reload':1,'rendered_result':values[0],'rendered_opponent_deck':values[1],'rendered_note':values[2],'rendered_log_time':values[3],'raw_readback':str(raw_path),'readback_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'live_totals':expected,'deck13_totals':deck_expected}
    for filename in ['EXTERNAL_SAVE_STATUS.json','LADDER_READBACK.json']:
        (packet/filename).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    receipts.append(receipt)
verification={'checked_utc':now,'artifact':receipts[0]['artifact'],'fresh_reload_verified':True,'all_exact_rows_verified':True,'verified_entry_count':len(receipts),'prior_source_notes_preserved_exactly_once':len(prior_notes),'baseline_totals':baseline,'verified_totals':expected,'deck13_totals':deck_expected,'rows':receipts,'proof_image':str(BATCH/'LADDER_SAVED_PROOF.png')}
(BATCH/'LIVE_SAVE_VERIFICATION.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'verified_saved_entries':len(receipts),**expected}))
