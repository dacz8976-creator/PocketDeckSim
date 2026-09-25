#!/usr/bin/env python3
"""Diagnostic only. All estimates are development-only; all-event use is explicitly isolated.
Run: python analyze.py [--bootstrap 2000]. Does not contact the network or touch source files.
"""
import argparse,ast,collections,csv,datetime,gzip,hashlib,itertools,json,math,pathlib,statistics
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from bs4 import BeautifulSoup
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[2];RAW=HERE/'raw'
PANEL=['altaria','blaziken','hydreigon','lucario','sceptile','suicune','vespiquen','weezing']
HELD=['manectric_heliolisk','raticate_ninetales','hoopa_absol','garchomp','whimsicott_ariados','charizardy_entei']
# The exact subtype labels in the Sept 8 roster used by the Sept 23 simulator check.
# No broad name/prefix classification, no merging different Pokémon printings or reversed labels.
MAPPING={
 'altaria':['mega-altaria-ex-b1-espeon-b3a'],
 'blaziken':['mega-blaziken-ex-b1'],
 'hydreigon':['hydreigon-mega-absol-ex-b1'],
 'lucario':['mega-lucario-ex-b3-lucario-a2'],
 'sceptile':['butterfree-b3b-mega-sceptile-ex-b3'],
 'suicune':['suicune-ex-a4a-baxcalibur-b2a'],
 'vespiquen':['vespiquen-ex-b4-shuckle-ex-a4'],
 'weezing':['team-rockets-weezing-ex-b4a-hoopa-ex-b4'],
 'manectric_heliolisk':['mega-manectric-ex-b2b-heliolisk-b4'],
 'raticate_ninetales':['team-rockets-raticate-ex-b4a-alolan-ninetales-ex-b2'],
 'hoopa_absol':['hoopa-ex-b4-mega-absol-ex-b1'],
 'garchomp':['garchomp-b4a'],
 'whimsicott_ariados':['whimsicott-ex-b1-ariados-b1a'],
 'charizardy_entei':['mega-charizard-y-ex-b1a-entei-ex-a4a']}
REV={v:k for k,vs in MAPPING.items() for v in vs};PAIRS=list(itertools.combinations(PANEL,2));PI={p:i for i,p in enumerate(PAIRS)}
BOOT_SEED=26_092_500_002

def dump(name,data): (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def csvout(name,rows,fields=None):
    rows=list(rows);fields=fields or list(rows[0])
    with (HERE/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def readraw(eid,kind):return json.loads(gzip.decompress((RAW/f'{eid}_{kind}.json.gz').read_bytes()))
def references():
    p=ROOT/'rl/results/deep_search_table/deep_table.py';data=p.read_text();d={}
    for n in ast.parse(data).body:
        if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('K3','LIMITLESS'):d[n.targets[0].id]=ast.literal_eval(n.value)
    dump('reference_inputs.json',{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(data.encode()).hexdigest(),'cells':[{'a':a,'b':b,'LIMITLESS':d['LIMITLESS'][a,b],'K3':d['K3'][a,b]} for a,b in PAIRS]})
    return d['LIMITLESS'],d['K3']

def serialize_matches(events,filename="matches.csv"):
    """Mechanical archival join only. Never calculate holdout-only statistics."""
    rows=[];seen=set()
    for e in events:
        eid=e['id'];det=readraw(eid,'details');sts=readraw(eid,'standings');ps=readraw(eid,'pairings')
        assert det['format'] in (None,'STANDARD')
        players={r['player']:r for r in sts};assert len(players)==len(sts)
        phases={p['phase']:p for p in det['phases']}
        for i,p in enumerate(ps):
            p1=p.get('player1','');p2=p.get('player2','');winner=p.get('winner')
            key=(eid,p.get('phase'),p.get('round'),p.get('table'),p.get('match'),p1,p2)
            assert key not in seen,('duplicate match identity',key);seen.add(key)
            if not p1 or not p2:status='bye_or_automatic_loss'
            elif winner==0:status='tie'
            elif winner==-1:status='double_loss'
            elif winner in (p1,p2):status='decisive'
            else:status='unresolved'
            row={'event_id':eid,'date':e['date'],'event_name':e['name'],'split':e['split'],'phase':p.get('phase'),'phase_type':phases.get(p.get('phase'),{}).get('type',''),'round':p.get('round'),'mode':phases.get(p.get('phase'),{}).get('mode',''),'table':p.get('table',''),'bracket_match':p.get('match',''),'source_row':i,'player1':p1,'player2':p2,'winner':winner,'result_status':status}
            for seat,pid in [(1,p1),(2,p2)]:
                pl=players.get(pid,{}) or {};deck=pl.get('deck') or {};rec=pl.get('record') or {}
                row.update({f'player{seat}_name':pl.get('name',''),f'deck{seat}_id':deck.get('id',''),f'deck{seat}_name':deck.get('name',''),f'archetype{seat}':REV.get(deck.get('id'),''),f'player{seat}_final_wins':rec.get('wins',''),f'player{seat}_final_losses':rec.get('losses',''),f'player{seat}_final_ties':rec.get('ties',''),f'player{seat}_placing':pl.get('placing','')})
            rows.append(row)
    csvout(filename,rows)
    return rows

def pair_records(rows,names=PANEL):
    out={tuple(p):[0,0,0] for p in itertools.combinations(sorted(names),2)}
    for r in rows:
        a,b=r['archetype1'],r['archetype2']
        if a not in names or b not in names or a==b or r['result_status'] not in ('tie','decisive'):continue
        key=tuple(sorted((a,b)));idx=2 if r['result_status']=='tie' else (0 if (r['winner']==r['player1'])==(a==key[0]) else 1)
        out[key][idx]+=1
    return out

def pct(wlt):
    w,l,t=wlt;n=w+l+t;return 100*(w+.5*t)/n if n else None

def averages(cell_values):
    result={}
    for d in PANEL:
        vals=[v if a==d else 100-v for (a,b),v in cell_values.items() if d in (a,b) and v is not None]
        result[d]=sum(vals)/7 if len(vals)==7 else None
    return result

def integrity(rows,baseline):
    """Authorized all-events integrity checks ONLY. No held-out subset outputs."""
    protocol=json.loads((HERE/'integrity_protocol.json').read_text())
    once=HERE/'reproduction_once.json'
    if once.exists():
        previous=json.loads(once.read_text())
        if previous.get('status')!='complete':raise RuntimeError('One-shot reproduction was started already; inspect the recorded failure before any action.')
        print('Reproduction already complete; reusing saved integrity outputs without recalculation.',flush=True)
        return
    stamp={'status':'started','started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':hashlib.sha256((HERE/'integrity_protocol.json').read_bytes()).hexdigest(),'analyze_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    with once.open('x') as f:json.dump(stamp,f,indent=2)
    allowed=set(protocol['event_inclusion_rule']['event_ids'])
    historical=[r for r in rows if r['event_id'] in allowed]
    cells=pair_records(historical);out=[]
    for p in PAIRS:
        got=tuple(cells[p]);old=baseline[p]
        po=(old[0]+.5*old[2])/sum(old);margin=1.96*math.sqrt(po*(1-po)/sum(old));pg=(got[0]+.5*got[2])/sum(got) if sum(got) else float('nan')
        noise_pass=bool(max(0,po-margin)<=pg<=min(1,po+margin))
        out.append({'scope':'all events, integrity check','a':p[0],'b':p[1],'pairings_W':got[0],'pairings_L':got[1],'pairings_T':got[2],'pairings_n':sum(got),'Sept23_W':old[0],'Sept23_L':old[1],'Sept23_T':old[2],'delta_W':got[0]-old[0],'delta_L':got[1]-old[1],'delta_T':got[2]-old[2],'matches_reference':got==old,'within_fixed_binomial_noise':noise_pass})
    csvout('integrity_reproduction.csv',out)
    checks=[]
    for a,b in [('sceptile','vespiquen'),('altaria','sceptile')]:
        for source,opponent in [(a,b),(b,a)]:
            sid=MAPPING[source][0];oid=MAPPING[opponent][0]
            f=RAW/f'{sid}_matchups.html.gz';soup=BeautifulSoup(gzip.decompress(f.read_bytes()),'html.parser');page_n=None
            for tr in soup.select('tr[data-matches]'):
                link=tr.find('a',href=lambda h:h and h.split('?')[0]==f'/decks/{oid}/matchups')
                if link:page_n=int(tr['data-matches']);break
            relevant=[r for r in rows if {r['archetype1'],r['archetype2']}=={a,b} and r['result_status'] in ('tie','decisive')]
            all_two_sided=[r for r in rows if {r['archetype1'],r['archetype2']}=={a,b} and r['player1'] and r['player2']]
            checks.append({'scope':'all events, integrity check','source_deck':source,'opponent':opponent,'source_id':sid,'opponent_id':oid,'page_n':page_n,'pairings_WLT_n':len(relevant),'pairings_two_sided_n':len(all_two_sided),'difference_WLT_minus_page':len(relevant)-page_n if page_n is not None else None,'page_url':json.loads((RAW/f'{sid}_matchups.meta.json').read_text())['url']})
    csvout('integrity_page_counts.csv',checks)
    total=sum(r['result_status'] in ('tie','decisive') and bool(r['player1']) and bool(r['player2']) and bool(r['deck1_id']) and bool(r['deck2_id']) for r in historical)
    tol=protocol['tolerance'];target=tol['legacy_total_matches'];total_pass=abs(total-target)<=tol['total_absolute_tolerance'];cells_pass=all(r['within_fixed_binomial_noise'] for r in out)
    stamp.update({'status':'complete','completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'all events, integrity check','event_count':len(allowed),'legacy_event_count':111,'event_count_difference':len(allowed)-111,'total_matches':total,'legacy_total_matches':target,'total_difference':total-target,'total_pass':total_pass,'cells_with_exact_WLT':sum(r['matches_reference'] for r in out),'cells_within_fixed_binomial_noise':sum(r['within_fixed_binomial_noise'] for r in out),'exact_match':total==target and all(r['matches_reference'] for r in out),'approximate_tolerance_pass':total_pass and cells_pass,'label':'approximate, event-count difference +'+str(len(allowed)-111)+'; exact differing membership unknown because the old 111 event ids were not saved'})
    dump('reproduction_once.json',stamp)
    return out,checks

def early_late(dev,events):
    dates=sorted(e['date'][:10] for e in events);med=dates[len(dates)//2]
    buckets={'early':{e['id'] for e in events if e['date'][:10]<=med},'late':{e['id'] for e in events if e['date'][:10]>med}}
    cellrows=[];deckrows=[]
    for half,eids in buckets.items():
        sub=[r for r in dev if r['event_id'] in eids];cells=pair_records(sub)
        for (a,b),v in cells.items():cellrows.append({'scope':'development only','half':half,'a':a,'b':b,'W':v[0],'L':v[1],'T':v[2],'n':sum(v),'score_pct':pct(v)})
        av=averages({k:pct(v) for k,v in cells.items()})
        for d in PANEL:deckrows.append({'scope':'development only','half':half,'deck':d,'average_7_pct':av[d],'covered_opponents':sum(d in p and sum(v)>0 for p,v in cells.items()),'n':sum(sum(v) for p,v in cells.items() if d in p)})
    csvout('early_late_cells.csv',cellrows);csvout('early_late_decks.csv',deckrows)
    dump('early_late_split.json',{'scope':'development only','median_event_start_utc':med,'rule':'early event UTC calendar date <= median calendar date, late > median date; all phases follow their event','event_ids':{k:sorted(v) for k,v in buckets.items()}})
    return med,cellrows,deckrows

def held_archetypes(dev,events):
    out=[]
    for h in HELD:
        pooled=[0,0,0]
        for d in PANEL:
            wlt=[0,0,0]
            for r in dev:
                a,b=r['archetype1'],r['archetype2']
                if {a,b}!={h,d} or r['result_status'] not in ('tie','decisive'):continue
                idx=2 if r['result_status']=='tie' else (0 if (r['winner']==r['player1'])==(a==h) else 1);wlt[idx]+=1
            pooled=[a+b for a,b in zip(pooled,wlt)]
            out.append({'scope':'development only','archetype':h,'opponent':d,'W':wlt[0],'L':wlt[1],'T':wlt[2],'n':sum(wlt)})
        out.append({'scope':'development only','archetype':h,'opponent':'whole_panel_pooled','W':pooled[0],'L':pooled[1],'T':pooled[2],'n':sum(pooled)})
    csvout('held_archetype_records.csv',out)
    # Most common exact list among top-eight finishers, using development standings only.
    candidates=collections.defaultdict(lambda:collections.defaultdict(list));invalid=[];deckdir=HERE/'decklists';deckdir.mkdir(exist_ok=True)
    for e in events:
        assert e['split']=='development'
        for pl in readraw(e['id'],'standings'):
            h=REV.get((pl.get('deck') or {}).get('id'))
            if h not in HELD or pl.get('placing') is None or pl['placing']>8 or pl['placing']<1:continue
            dl=pl.get('decklist') or {};cards=[]
            for section,values in dl.items():
                if isinstance(values,list):
                    for c in values:
                        if isinstance(c,dict) and all(k in c for k in ('count','set','number')):cards.append((c['set'],str(c['number']).zfill(3),int(c['count']),c.get('name','')))
            combined=collections.Counter()
            for s,n,c,na in cards:combined[s,n]+=c
            signature=tuple(sorted((s,n,c) for (s,n),c in combined.items()))
            if sum(c for s,n,c in signature)!=20:
                invalid.append({'event_id':e['id'],'player':pl['player'],'archetype':h,'card_count':sum(c for s,n,c in signature)});continue
            candidates[h][signature].append({'event_id':e['id'],'date':e['date'],'event_name':e['name'],'players':e['players'],'player':pl['player'],'placing':pl['placing'],'deck_id':(pl.get('deck') or {}).get('id'),'decklist_url':f'https://play.limitlesstcg.com/tournament/{e["id"]}/player/{pl["player"]}/decklist','raw_source':f'raw/{e["id"]}_standings.json.gz','card_names':[{'set':s,'number':n,'count':c,'name':na} for s,n,c,na in cards]})
    selections={}
    def best(entries):return min(entries,key=lambda x:(x['placing'],-x['players'],x['date'],x['player']))
    for h in HELD:
        if not candidates[h]:selections[h]={'status':'unavailable: no valid top-eight development list'};continue
        sig,entries=min(candidates[h].items(),key=lambda kv:(-len(kv[1]),best(kv[1])['placing'],-best(kv[1])['players'],best(kv[1])['date'],best(kv[1])['player'],kv[0]))
        text=''.join(f'{c} {s} {n}\n' for s,n,c in sig);file=deckdir/f'{h}.txt';file.write_text(text)
        selections[h]={'status':'saved','file':str(file.relative_to(HERE)),'sha256':hashlib.sha256(text.encode()).hexdigest(),'frequency_among_top8':len(entries),'eligible_top8_entries':sum(len(x) for x in candidates[h].values()),'distinct_exact_lists':len(candidates[h]),'representative':best(entries),'matching_entries':[{k:v for k,v in x.items() if k!='card_names'} for x in entries]}
    dump('decklist_sources.json',{'scope':'development only','selection_rule':'Most frequent exact 20-card multiset among final placing 1-8; ties by best placing, largest event, earliest date, player id, card multiset. Card identifiers copied directly from each API decklist; zero-padded number only. No normalization of alternate art or card names.','selections':selections,'invalid_or_missing_top8_lists':invalid})
    return out,selections

class Model:
    def __init__(self,dev,events):
        self.events=events;self.eids=[e['id'] for e in events];self.ei={e:i for i,e in enumerate(self.eids)}
        # Only development standings enter ratings, including records against nonpanel decks.
        players=sorted({p['player'] for e in events for p in readraw(e['id'],'standings')});self.players=players;self.plidx={p:i for i,p in enumerate(players)}
        self.W=np.zeros((len(events),len(players)));self.N=self.W.copy();self.present=np.zeros(self.W.shape,dtype=bool)
        for e in events:
            assert e['split']=='development'
            for p in readraw(e['id'],'standings'):
                i,j=self.ei[e['id']],self.plidx[p['player']];rec=p['record'];self.W[i,j]=rec['wins'];self.N[i,j]=sum(rec[k] for k in ['wins','losses','ties']);self.present[i,j]=True
        self.rows=[r for r in dev if r['archetype1'] in PANEL and r['archetype2'] in PANEL and r['result_status'] in ('decisive','tie')]
        self.E=np.array([self.ei[r['event_id']] for r in self.rows]);self.P1=np.array([self.plidx[r['player1']] for r in self.rows]);self.P2=np.array([self.plidx[r['player2']] for r in self.rows])
        self.J=np.array([PI.get(tuple(sorted((r['archetype1'],r['archetype2']))),-1) for r in self.rows]);self.nonmirror=self.J>=0
        self.SIGN=np.array([1 if r['archetype1']<=r['archetype2'] else -1 for r in self.rows])
        self.Y=np.array([.5 if r['result_status']=='tie' else float(r['winner']==r['player1']) for r in self.rows]);self.Y=np.where(self.SIGN==1,self.Y,1-self.Y)
    def ratings(self,counts):
        totalw=counts@self.W;totaln=counts@self.N
        # Exclude ALL resampled copies of this source event, not just one copy.
        w=totalw[None,:]-counts[:,None]*self.W;n=totaln[None,:]-counts[:,None]*self.N
        s=np.log((w+5)/(n-w+5))
        delta=(s[self.E,self.P1]-s[self.E,self.P2])*self.SIGN
        return delta,s,n
    def fit(self,counts,start=None):
        delta,s,n=self.ratings(counts);weights=counts[self.E];j=self.J;mask=self.nonmirror
        present=np.bincount(j[mask],weights=weights[mask],minlength=28)>0
        def fg(theta):
            eta=theta[-1]*delta;eta[mask]+=theta[j[mask]]
            p=expit(eta);res=weights*(p-self.Y)
            g=np.r_[np.bincount(j[mask],weights=res[mask],minlength=28),res@delta]
            f=np.sum(weights*(np.logaddexp(0,eta)-self.Y*eta))
            return f,g
        if start is None:start=np.zeros(29)
        fit=minimize(fg,start,jac=True,method='L-BFGS-B',options={'maxiter':1000,'gtol':1e-7,'ftol':1e-12,'maxls':50})
        score=100*expit(fit.x[:28]);score[~present]=np.nan
        gradient=float(np.max(np.abs(fg(fit.x)[1])))
        ok=bool(fit.success or gradient<1e-4)
        return fit.x,score,ok,gradient

def fit_model(dev,events,k3,boots):
    model=Model(dev,events);counts=np.ones(len(events));theta,score,ok,grad=model.fit(counts)
    if not ok:raise RuntimeError(f'Main model failed: gradient {grad}')
    delta,skills,priorn=model.ratings(counts)
    ratingrows=[]
    for e,i in model.ei.items():
        for p,j in model.plidx.items():
            if model.present[i,j]:ratingrows.append({'scope':'development only','event_id':e,'player':p,'other_events_W':int(model.W[:,j].sum()-model.W[i,j]),'other_events_N':int(priorn[i,j]),'skill':float(skills[i,j])})
    csvout('development_player_skills.csv',ratingrows)
    samples=[];fail=[];rng=np.random.default_rng(BOOT_SEED)
    for b in range(boots):
        counts=rng.multinomial(len(events),np.ones(len(events))/len(events));th,sc,success,gradient=model.fit(counts,theta)
        if success:samples.append(np.r_[sc,th[-1]])
        else:fail.append({'replicate':b,'max_gradient':gradient})
        if (b+1)%100==0:print(f'Bootstrap {b+1}/{boots}, failed {len(fail)}',flush=True)
    arr=np.asarray(samples);assert len(samples)>=.95*boots,'Too many failed event bootstrap fits'
    np.savez_compressed(HERE/'bootstrap_samples.npz',cell_score_pct=arr[:,:28],beta=arr[:,-1],seed=BOOT_SEED)
    beta_ci=np.quantile(arr[:,-1],[.025,.975]).tolist();q75=float(np.quantile([r['skill'] for r in ratingrows],.75))
    maincells={p:float(score[i]) for i,p in enumerate(PAIRS)};rawcells=pair_records(dev);rawpct={p:pct(v) for p,v in rawcells.items()}
    cells=[]
    for i,(a,b) in enumerate(PAIRS):
        vals=arr[:,i];vals=vals[np.isfinite(vals)];ci=np.quantile(vals,[.025,.975]).tolist() if len(vals) else [None,None]
        w,l,t=rawcells[a,b]
        cells.append({'scope':'development only','a':a,'b':b,'W':w,'L':l,'T':t,'n':w+l+t,'raw_score_pct':rawpct[a,b],'equal_skill_pct':maincells[a,b],'ci_low_pct':ci[0],'ci_high_pct':ci[1],'both_p75_pct':maincells[a,b],'K3_pct':k3[a,b],'valid_bootstraps':len(vals)})
    csvout('model_cells.csv',cells)
    rawavg=averages(rawpct);simavg=averages(k3);eqavg=averages(maincells);decks=[]
    for d in PANEL:
        ids=[i for i,p in enumerate(PAIRS) if d in p]
        signed=np.array([arr[:,i] if PAIRS[i][0]==d else 100-arr[:,i] for i in ids]).T
        deckdist=np.mean(signed,axis=1);valid=deckdist[np.isfinite(deckdist)];lo,hi=np.quantile(valid,[.025,.975]);half=max(eqavg[d]-lo,hi-eqavg[d])
        rawgap=rawavg[d]-simavg[d];adjgap=eqavg[d]-simavg[d]
        if half>8 or len(valid)<.95*boots:verdict='undetermined';reason='interval exceeds ±8 points or incomplete bootstrap coverage'
        elif abs(adjgap)<.5*abs(rawgap):verdict='Population';reason='absolute development gap shrank by more than half'
        elif adjgap*rawgap>0:verdict='bot/engine';reason='at least half the development gap remains on the same side'
        else:verdict='undetermined';reason='gap changed sign without shrinking by more than half'
        worst=max([p for p in PAIRS if d in p],key=lambda p:abs(rawpct[p]-k3[p]));opp=worst[1] if worst[0]==d else worst[0]
        def avg6(values):return sum(v if a==d else 100-v for (a,b),v in values.items() if d in (a,b) and (a,b)!=worst)/6
        sim6=avg6(k3);raw6=avg6(rawpct);eq6=avg6(maincells)
        decks.append({'scope':'development only','deck':d,'n_nonmirror':sum(sum(v) for p,v in rawcells.items() if d in p),'K3_average_pct':simavg[d],'raw_average_pct':rawavg[d],'equal_skill_average_pct':eqavg[d],'ci_low_pct':float(lo),'ci_high_pct':float(hi),'both_p75_average_pct':eqavg[d],'raw_minus_sim_pp':rawgap,'equal_minus_sim_pp':adjgap,'gap_shrink_fraction':1-abs(adjgap)/abs(rawgap) if rawgap else None,'verdict':verdict,'reason':reason,'removed_opponent':opp,'K3_6opponent_pct':sim6,'raw_6opponent_pct':raw6,'equal_6opponent_pct':eq6,'raw_6opponent_gap_pp':raw6-sim6,'equal_6opponent_gap_pp':eq6-sim6,'valid_bootstraps':len(valid)})
    csvout('deck_verdicts.csv',decks)
    summary={'scope':'development only','beta':float(theta[-1]),'beta_ci95':beta_ci,'bootstrap_replicates_requested':boots,'bootstrap_successful':len(samples),'bootstrap_failed':fail,'bootstrap_seed':BOOT_SEED,'bootstrap_method':'Resample whole development events with replacement; recompute all skills each draw; remove every copy of current source event before rating; unpenalized logistic fit each draw; percentile 2.5/97.5 intervals.','skill_p75_player_event_weighted':q75,'number_development_events':len(events),'panel_model_matches':len(model.rows),'panel_model_mirrors':int(np.sum(~model.nonmirror)),'panel_model_ties':int(np.sum(model.Y==.5)),'main_fit_max_gradient':grad,'players':len(model.players),'rating_rows':len(ratingrows),'rating_rows_no_other_games':sum(r['other_events_N']==0 for r in ratingrows),'skill_formula':'logit((other-event wins + 5)/(other-event wins + losses + ties + 10)); final standings records, including byes/administrative outcomes as recorded. Development events only.','outcome_formula':'win=1, loss=0, tie=0.5; fractional-binomial logit models expected match score, not a separate probability of a decisive win. Double losses/unresolved/byes excluded from fit.','pair_effect':'28 independent unordered-pair effects, sign reversed for opposite seats. Mirrors have effect 0 and inform beta. No global seat effect; player1 is pairing order, not game first turn.','p75_identity':'Both players at the SAME pooled 75th percentile gives s1-s2=0 exactly. Equal-skill and both-p75 values and intervals are identical by construction.','verdict_rule':'Compare development raw seven-opponent score gap with equal-skill gap, both minus fixed K3. Undetermined if either CI endpoint is >8 percentage points from estimate or <95% bootstrap coverage; otherwise Population if absolute gap shrinks >50%; bot/engine if >=50% remains same direction; otherwise undetermined. Point-estimate diagnostic labels, not causal attribution.','largest_cell_rule':'For each deck remove opponent with largest absolute development raw-vs-K3 cell gap; use the same six remaining opponents for K3, raw, adjusted. No refit.'}
    dump('model_summary.json',summary)
    return summary,cells,decks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bootstrap',type=int,default=2000);ap.add_argument('--development-only',action='store_true');ap.add_argument('--integrity-only',action='store_true');a=ap.parse_args()
    events=json.loads((HERE/'events.json').read_text());split=json.loads((HERE/'split.json').read_text());assert not set(split['holdout_event_ids'])&set(split['development_event_ids'])
    assert len(events)==len(split['holdout_event_ids'])+len(split['development_event_ids'])
    baseline,k3=references();dump('deck_mapping.json',{'panel':PANEL,'held_archetypes':HELD,'deck_ids':MAPPING,'rule':'Exact API deck ID equality; subtypes from the Sept 8 study README behind the Sept 23 table. No broad substring matching. Garchomp is B4a, not A2 or Garchomp ex; Heliolisk is B4, not B1a.'})
    rows=serialize_matches([e for e in events if e['split']=='development'],'development_matches.csv') if a.development_only else serialize_matches(events)
    if not a.development_only:integrity(rows,baseline)
    if a.integrity_only:return
    dev_events=[e for e in events if e['split']=='development'];dev=[r for r in rows if r['event_id'] in set(split['development_event_ids'])]
    assert all(r['split']=='development' for r in dev)
    del rows # Full-event material must not enter any subsequent estimate.
    med,earlycells,earlydecks=early_late(dev,dev_events);held,lists=held_archetypes(dev,dev_events)
    summary,cells,decks=fit_model(dev,dev_events,k3,a.bootstrap)
    devqa={'scope':'development only','status_counts':dict(collections.Counter(r['result_status'] for r in dev)),'mode_counts':dict(collections.Counter(r['mode'] for r in dev)),'events_without_decklists':[e['id'] for e in dev_events if not readraw(e['id'],'details').get('decklists')],'unmapped_deck_ids':sorted({r[f'deck{s}_id'] for r in dev for s in (1,2) if r[f'deck{s}_id'] not in REV}),'no_new_holdout_estimates':'Only mechanical matches.csv archival join and two explicitly labeled integrity reports read all-event outcomes. All models and list choices assert development membership.'}
    dump('development_data_quality.json',devqa)
    print(json.dumps({'beta':summary['beta'],'ci':summary['beta_ci95'],'decks':decks},indent=2))
if __name__=='__main__':main()
