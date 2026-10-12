import json, glob, os
Q='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
meta={}; allg=[]
for b in ('BATCH_2026-10-06_NEW_PAUSE_GAMES','BATCH_2026-10-09_NEW_PAUSE_GAMES','BATCH_2026-10-11_NEW_PAUSE_GAMES'):
    for d in sorted(glob.glob(Q+b+'/2026*')):
        n=os.path.basename(d)
        short='kw-'+n.replace('_iOS','')[2:]
        try: pg=json.load(open(d+'/PAUSE_GAME.json',encoding='utf-8'))
        except Exception: pg={}
        oc=pg.get('outcome') or {}
        oc=oc if isinstance(oc,dict) else {'result':str(oc)}
        res=oc.get('result') or oc.get('owner')
        meth=oc.get('method')
        opp=oc.get('opponent') if isinstance(oc.get('opponent'),str) else pg.get('opponent')
        pts=oc.get('points_at_concession') or ({'owner':oc.get('points_owner',oc.get('owner_points')),'opponent':oc.get('points_opponent',oc.get('opponent_points'))})
        t=f"{pg.get('deck_name','?')}; {res}{(' by '+meth) if meth else ''}{(' '+str(pts.get('owner'))+'-'+str(pts.get('opponent'))) if isinstance(pts,dict) and pts.get('owner') is not None else ''}; opponent {opp}"
        meta[short]={'title':t,'folder':b+'/'+n,'has_ledger':os.path.exists(d+'/TURN_LEDGER.json')}
json.dump(meta,open('/home/dacz8976/pgd_vr/all/games_meta.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(meta), sum(1 for v in meta.values() if v['has_ledger']))