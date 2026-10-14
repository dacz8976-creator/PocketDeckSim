exec(open(__file__.replace('inspect_diff.py','audit_repairs.py'),encoding='utf-8').read().split('for game in')[0])
def diff(a,z,k=''):
 if type(a)!=type(z): print(k,str(a)[:190],'->',str(z)[:190]); return
 if isinstance(a,dict):
  for key in a.keys()|z.keys():
   if key not in a or key not in z: print(k+'/'+key,'added/removed',str(z.get(key))[:190])
   else: diff(a[key],z[key],k+'/'+key)
 elif isinstance(a,list):
  if len(a)!=len(z): print(k,'length',len(a),'->',len(z))
  for i,(v,w) in enumerate(zip(a,z)): diff(v,w,k+'/'+str(i))
 elif a!=z: print(k,str(a)[:190],'->',str(z)[:190])
for game in ['20261002_205230000_iOS_auto_sol','20261002_210612000_iOS_auto_sol']:
 p=B/game; print(game)
 for n in ['TURN_LEDGER.json','TURN_EVIDENCE.json']: diff(read(p/'worker_submission'/n),read(p/n),n)
 r=read(p/'REPAIR_RECEIPT.json'); print('protected',r.get('frozen_files_verified_unchanged'))
