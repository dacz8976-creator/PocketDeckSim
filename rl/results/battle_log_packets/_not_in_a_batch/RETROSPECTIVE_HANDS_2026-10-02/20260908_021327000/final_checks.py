import json,pathlib,re
P=pathlib.Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=load('TURN_LEDGER.json'); old=P.parents[1]/'20260908_021327_v7_review'/'final_packet'/'REVIEW.md'
oldtext=old.read_text(encoding='utf-8-sig'); sections={int(m.group(1)):m.group(0).rstrip() for m in re.finditer(r'^### Turn (\d+)\b.*?(?=^### |^## |\Z)',oldtext,re.M|re.S)}
for r in l['turns']:
    r['inherited_accepted_turn']['verbatim_accepted_section']=sections[r['turn_number']]
    for d in r['draws_and_searches']:
        if d['kind'] in ['normal_draw','opponent_normal_draw']:d['caused_by']=None
        if d['kind']=='search_researcher':d['caused_by']="Team Rocket's Researcher"
inherited=load('INHERITED_TURNS.json')
for r in inherited['rows']:r['verbatim_accepted_section']=sections[r['turn_number']]
save('INHERITED_TURNS.json',inherited)
p=l['turns'][11]['plays_in_order'][0]
p.update(card_name="Team Rocket's Raticate ex",target='owner Active',result='Inspect Active attack menu; no attack resolves before concession',basis='direct_native_observation',limit_reason=None)
c={'id':'C9','turn':12,'inherited_claim':sections[12],'observation':'Cyrus is the normal draw at404. Native405 shows the owner inspecting active Raticate attack menu, then406 Energy end-turn warning. No Cyrus effect resolves; whether a separate very brief inspection occurred between samples is not established.','evidence_ids':['f0404.00','f0405.00','f0406.00']}
l['conflicts']=[x for x in l['conflicts'] if x['id']!='C9']+[c];l['turns'][11]['supplement_conflicts']=[x for x in l['turns'][11]['supplement_conflicts'] if x['id']!='C9']+[c]
save('TURN_LEDGER.json',l)
u=load('UNCERTAINTIES.json');u['consequential_conflicts']=[x for x in u['consequential_conflicts'] if x['id']!='C9']+[c];save('UNCERTAINTIES.json',u)
a=load('ASTRA_QUESTIONS.json');a['status']='pending_bounded_independent_reconciliation'
for q in a['questions']:
    q['question']='Confirm the fresh bounded observation against the quoted accepted section. Assess only supplement fields and preserve the old packet.'
    q.setdefault('inherited_claim_summary',q['inherited_claim']);q['inherited_claim']=sections[q['turn']]
    q['inherited_claim_basis']=str(old)+':'+str(l['turns'][q['turn']-1]['inherited_accepted_turn']['accepted_source_line'])
save('ASTRA_QUESTIONS.json',a)
text=(P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8')
text=text.replace('1. Cyrus → opponent Bench: no switching effect resolves; all Bench undamaged','1. Active Raticate ex → attack menu: inspected; no attack resolves')
if 'Fresh turn12 capture' not in text:text+='\nFresh turn12 capture shows Cyrus as the normal draw and Active Raticate attack-menu inspection at405s. The accepted Cyrus-inspection account remains quoted separately (C9); no Cyrus effect is asserted by the supplement.\n'
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
e=load('TURN_EVIDENCE.json'); ids={x['evidence_id'] for x in e['frames']};missing=[]
def walk(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=='evidence_ids' and x is not None:missing.extend(i for i in x if i.startswith('f') and i not in ids)
            else:walk(x)
    elif isinstance(v,list):
        for x in v:walk(x)
for f in P.glob('*.json'):walk(load(f.name))
assert not missing,missing
assert len(e['frames'])==len(ids)==108
assert len(l['turns'])==12
assert all(r['inherited_accepted_turn']['verbatim_accepted_section']==sections[r['turn_number']] for r in l['turns'])
assert all(pathlib.Path(x['full_frame_path']).exists() for x in e['frames'])
print('Validated108 native IDs/paths,12 rows,exact accepted section copies, and all cited evidence IDs. Old packet unchanged.')
