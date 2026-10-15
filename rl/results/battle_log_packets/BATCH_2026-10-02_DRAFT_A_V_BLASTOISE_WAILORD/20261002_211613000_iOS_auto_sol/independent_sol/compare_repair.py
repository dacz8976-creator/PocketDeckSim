import json, hashlib, difflib
from pathlib import Path
p=Path(__file__).resolve().parent.parent
def read(f): return json.loads(f.read_text(encoding='utf-8-sig'))
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
old=read(p/'worker_submission/SUBMISSION.json')
new=read(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')
assert sha(p/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')=='023e53edd194e05a78dc2fcb98f5959e31dac7fbcbde2a363231b531c8e85cfc'
assert sha(p/'worker_submission/SUBMISSION.json')=='f517ef25c730bae74c7b80c8fae098b354a5633983351a45d11d44edcda0344c'
assert all(sha(p/'worker_submission'/f)==h for f,h in old['files'].items())
assert all(sha(p/f)==h for f,h in new['files'].items())
assert len(new['files'])==20
changed=[f for f,h in old['files'].items() if new['files'][f]!=h]
assert set(changed)=={'TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','TURN_TABLE.md'}
print('Hashes pass. Changed files: '+str(changed))
def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(a.keys()|b.keys()):
            if k not in a: print(path+'/'+k,'ADDED',json.dumps(b[k],ensure_ascii=False))
            elif k not in b: print(path+'/'+k,'REMOVED',json.dumps(a[k],ensure_ascii=False))
            else: diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        for i,(x,y) in enumerate(zip(a,b)): diff(x,y,path+'/'+str(i))
    elif a!=b: print(path,repr(a),'->',repr(b))
for f in changed:
    print('\nFILE '+f)
    if f.endswith('.json'): diff(read(p/'worker_submission'/f),read(p/f))
    else:
        print(''.join(difflib.unified_diff((p/'worker_submission'/f).read_text(encoding='utf-8-sig').splitlines(True),(p/f).read_text(encoding='utf-8-sig').splitlines(True))))
