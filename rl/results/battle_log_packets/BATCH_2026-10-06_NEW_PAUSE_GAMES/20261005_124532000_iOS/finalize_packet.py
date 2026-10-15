from pathlib import Path
import json,re
P=Path(__file__).parent
def read(n): return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x): (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger=read('TURN_LEDGER.json')
summary=read('SUMMARY.json')
summary['opponent_fan_counts_at_selected_owner_start']=[3,4,3,3]
summary['suggested_independent_checks'][3]['seconds']=[123,131,131.5,133,134,135,140,143,146,148,150,155,162,164,167,171,177,179,181,184]
summary['suggested_independent_checks'][3]['target']='Opponent turn 4: Rainbow cycle, May add two and return two concealed Pokemon, Ignition, item theft/search, Energy attachment, KO and Poison order'
summary['suggested_independent_checks'].append({'seconds':[224,225,227,227.5,228,229,231,236,241,248,251,265,269.7], 'target':'Opponent turn 6 normal draw, brief Poke Ball reveal and hidden search, bench Entei, heal/cure, attachment, KO and final three-back fan'})
save('SUMMARY.json',summary)
checks=read('WORKER_CHECKS.json')
checks['opponent_fan_counts_at_owner_starts']=[3,4,3,3]
checks['short_opponent_reveals_recovered']=['May 131.5 s','Poke Ball 227.5 s']
save('WORKER_CHECKS.json',checks)
for fn in ['REVIEW.md','COVERAGE.md']:
    s=(P/fn).read_text(encoding='utf-8')
    s=s.replace('3,4,4,4','3,4,3,3')
    # Keep source names, hashes and identity tokens intact; make narrative units readable.
    for word in ['turn','Turn','turns','cards','slots','points','point','damage','Fire','Darkness','Energy','HP','seconds','seconds','native','Bench','Active','Darkrai','Charmeleon','Entei','Nidoran','Nidoking','Nihilego','Cyrus','Research','Pulse','Needle','Peck','Aura','Poison','Darkness','Dark','More Poison']:
        s=re.sub(r'(?<![\w/])('+re.escape(word)+r')(\d)',r'\1 \2',s)
    s=re.sub(r'(\d)(HP| Fire| Darkness| damage)',r'\1 \2',s)
    for old,new in [('after8','after 8'),('score0 to3','score 0 to 3'),('deals200','deals 200'),('show70','show 70'),('No full','No full'),('plus20','plus 20'),('all8','all 8'),('All8','All 8'),('with2','with 2'),('then Needle192','then Needle 192'),('step1','step 1'),('draws1','draws 1'),('draws2','draws 2'),('adds1','adds 1'),('one point','one point'),('all four','all four'),('ninety','ninety')]: s=s.replace(old,new)
    s=s.replace('No Copycat is played.','The opponent plays May at 131.5 s on turn 4. Two concealed Pokemon are added, then two concealed Pokemon are returned to the deck by about 140 s. Their identities and private prompts are unavailable. Turn 6 includes a second Poke Ball, revealed at 227.5 s, which adds one concealed Basic Pokemon. No Copycat is played.')
    s=s.replace('a partly off-screen leftmost Lucky Ice Pop','an off-screen leftmost Lucky Ice Pop')
    if fn=='COVERAGE.md':s+='\nA final native reconciliation densely inspected 129-140.5 s, recovered the May reveal at 131.5 s, and resolved the brief Poke Ball reveal at 227.5 s. Owner-start opponent back counts are 3, 4, 3 and 3.\n'
    (P/fn).write_text(s,encoding='utf-8')
print('Final prose and bounded independent targets reconciled.')
