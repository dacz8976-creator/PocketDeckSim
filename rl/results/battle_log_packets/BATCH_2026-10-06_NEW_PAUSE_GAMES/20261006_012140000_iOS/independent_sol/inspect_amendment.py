import json, hashlib, difflib
from pathlib import Path
p=Path(__file__).resolve().parent.parent
def read(n): return json.loads((p/n).read_text(encoding='utf-8-sig'))
def diff(a,b,path=''):
    if type(a)!=type(b):
        print(path,repr(a),'->',repr(b)); return
    if isinstance(a,dict):
        for k in a.keys()|b.keys():
            if k not in a: print(path+'/'+k,'ADDED',repr(b[k]))
            elif k not in b: print(path+'/'+k,'REMOVED',repr(a[k]))
            else: diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b): print(path,'LENGTH',len(a),len(b))
        for i,(v,w) in enumerate(zip(a,b)): diff(v,w,path+'/'+str(i))
    elif a!=b: print(path,repr(a),'->',repr(b))
diff(read('original_before_R1_R3/TURN_LEDGER.json'),read('TURN_LEDGER.json'))
print('REVIEW_DIFF')
print(''.join(difflib.unified_diff((p/'original_before_R1_R3/REVIEW.md').read_text(encoding='utf-8').splitlines(True),(p/'REVIEW.md').read_text(encoding='utf-8').splitlines(True))))
e=read('TURN_EVIDENCE.json')
print('NATIVE_REF')
print(json.dumps([f for f in e['frames'] if f['evidence_id'] in ['F015800','F016000']],ensure_ascii=False))
