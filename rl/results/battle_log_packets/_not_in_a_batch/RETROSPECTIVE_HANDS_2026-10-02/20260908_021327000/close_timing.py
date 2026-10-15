import json,pathlib
P=pathlib.Path(__file__).resolve().parent
def load(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=='evidence_ids':v[k]=['f0406.00' if i=='f0407.00' else i for i in x]
            else:ref(x)
    elif isinstance(v,list):
        for x in v:ref(x)
h=load('HAND_SUPPLEMENT.json');l=load('TURN_LEDGER.json');e=load('TURN_EVIDENCE.json')
for r in h['rows']:
    r['candidate_limits']='Later or post-play candidates do not replace the selected untouched hand.'
    if r['turn_number']==12:r['candidate_limits']='About+3 candidate407s is after concession; retained for timing context only. +6 is after game end. Selected untouched hand404s and before-end warning hand406s are retained.'
ref(h['rows'][-1]['before_end_hand']);ref(l['turns'][-1]['owner_hand_end']);l['turns'][-1]['timing']['before_end_action_seconds']=406
for f in e['frames']:
    if f['evidence_id']=='f0407.00':f.update(role='draw_offset_candidate_after_concession',observation='Hand remains visible after opponent concession; cannot serve as before-end view.',suitability_or_limit='About+3 candidate retained; battle has ended.')
    if f['evidence_id']=='f0406.00':f.update(role='owner_before_end_hand_and_warning',observation='Before concession: Energy end-turn warning. All3 owner hand cards remain visible beneath popup.',suitability_or_limit='Warning overlays board, but owner hand remains readable.')
save('HAND_SUPPLEMENT.json',h);save('TURN_LEDGER.json',l);save('TURN_EVIDENCE.json',e)
text=(P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8').replace('f0404.00, f0407.00, f0408.00; TURN_LEDGER turn12','f0404.00, f0406.00, f0408.00; TURN_LEDGER turn12')
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
print('Turn12 before-end hand now cites the actual pre-concession406 warning view. Hand identities unchanged.')
