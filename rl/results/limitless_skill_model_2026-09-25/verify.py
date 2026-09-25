#!/usr/bin/env python3
"""Independent development-only checks; never recomputes the one-shot reproduction."""
import collections,csv,gzip,json,pathlib,sys
import numpy as np
import statsmodels.api as sm
from analyze import HERE,PANEL,PAIRS,PI,Model,readraw

def main():
    checks=[]
    events=json.loads((HERE/'events.json').read_text());sp=json.loads((HERE/'split.json').read_text());dev=set(sp['development_event_ids']);hold=set(sp['holdout_event_ids']);assert not dev&hold
    rows=list(csv.DictReader((HERE/'development_matches.csv').open()));assert {r['event_id'] for r in rows}<=dev
    for r in rows:
        if r['winner'] in ('0','-1'):r['winner']=int(r['winner'])
    ratingrows=list(csv.DictReader((HERE/'development_player_skills.csv').open()));assert {r['event_id'] for r in ratingrows}<=dev
    skill={(r['event_id'],r['player']):float(r['skill']) for r in ratingrows}
    de=[e for e in events if e['id'] in dev]
    records={e['id']:{p['player']:p['record'] for p in readraw(e['id'],'standings')} for e in de}
    for r in ratingrows:
        other=[p[r['player']] for eid,p in records.items() if eid!=r['event_id'] and r['player'] in p]
        w=sum(p['wins'] for p in other);n=sum(sum(p[k] for k in ('wins','losses','ties')) for p in other)
        assert w==int(r['other_events_W']) and n==int(r['other_events_N'])
        assert abs(np.log((w+5)/(n-w+5))-float(r['skill']))<1e-12
    checks.append({'check':'all leave-one-event-out skill records independently summed from development standings only','passed':True,'records':len(ratingrows)})
    fitrows=[r for r in rows if r['archetype1'] in PANEL and r['archetype2'] in PANEL and r['result_status'] in ('decisive','tie')]
    X=np.zeros((len(fitrows),29));y=[]
    for i,r in enumerate(fitrows):
        a,b=r['archetype1'],r['archetype2']
        if a!=b:X[i,PI[tuple(sorted((a,b)))]]=1 if a<b else -1
        X[i,-1]=skill[r['event_id'],r['player1']]-skill[r['event_id'],r['player2']]
        y.append(.5 if r['result_status']=='tie' else float(r['winner']==r['player1']))
    independent=sm.GLM(y,X,family=sm.families.Binomial()).fit(maxiter=200,tol=1e-12)
    summary=json.loads((HERE/'model_summary.json').read_text());cells=list(csv.DictReader((HERE/'model_cells.csv').open()))
    beta_error=abs(independent.params[-1]-summary['beta']);score_error=max(abs(100/(1+np.exp(-independent.params[i]))-float(c['equal_skill_pct'])) for i,c in enumerate(cells))
    assert beta_error<1e-4 and score_error<1e-3
    checks.append({'check':'independent statsmodels GLM on original player1 orientation agrees with canonical-pair SciPy fit','passed':True,'beta_absolute_error':beta_error,'maximum_cell_percentage_point_error':score_error})
    model=Model(rows,de);counts=np.ones(len(de));counts[0]=3;counts[1]=0
    delta,s,n=model.ratings(counts)
    for ei in [0,1,len(de)-1]:
        for player in model.players[::max(1,len(model.players)//50)]:
            pi=model.plidx[player];w0=n0=0
            for ej,e in enumerate(de):
                if ej==ei:continue
                rec=records[e['id']].get(player)
                if rec:w0+=counts[ej]*rec['wins'];n0+=counts[ej]*sum(rec[k] for k in ('wins','losses','ties'))
            assert abs(s[ei,pi]-np.log((w0+5)/(n0-w0+5)))<1e-12 and n[ei,pi]==n0
    checks.append({'check':'bootstrap removes every copy of current source event, including triplicated and absent events','passed':True})
    assert all(c['equal_skill_pct']==c['both_p75_pct'] for c in cells)
    checks.append({'check':'both-at-p75 equals equal skill exactly, as specified by skill-difference model','passed':True})
    sources=json.loads((HERE/'decklist_sources.json').read_text());nfiles=0
    for h,entry in sources['selections'].items():
        assert entry['status']=='saved';rep=entry['representative'];assert rep['event_id'] in dev
        pl=next(p for p in readraw(rep['event_id'],'standings') if p['player']==rep['player']);source=collections.Counter()
        for section in pl['decklist'].values():
            if isinstance(section,list):
                for c in section:
                    if isinstance(c,dict) and all(k in c for k in ('count','set','number')):source[c['set'],str(c['number']).zfill(3)]+=c['count']
        saved=collections.Counter()
        for line in (HERE/entry['file']).read_text().splitlines():
            count,setid,num=line.split();assert len(num)==3;saved[setid,num]+=int(count)
        assert source==saved and sum(saved.values())==20;nfiles+=1
    assert nfiles==6
    checks.append({'check':'six 20-card files exactly match their development API decklists, including set and card number','passed':True})
    early=json.loads((HERE/'early_late_split.json').read_text());left=set(early['event_ids']['early']);right=set(early['event_ids']['late']);assert not left&right and left|right==dev
    assert all((e['date'][:10]<=early['median_event_start_utc'])==(e['id'] in left) for e in de)
    checks.append({'check':'early/late calendar-date partition covers development only without overlap','passed':True})
    for fn in ['held_archetype_records.csv','early_late_cells.csv','early_late_decks.csv','model_cells.csv','deck_verdicts.csv']:
        assert all(r['scope']=='development only' for r in csv.DictReader((HERE/fn).open()))
    checks.append({'check':'all estimate outputs explicitly labeled development only','passed':True})
    (HERE/'validation.json').write_text(json.dumps({'all_passed':True,'checks':checks},indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
