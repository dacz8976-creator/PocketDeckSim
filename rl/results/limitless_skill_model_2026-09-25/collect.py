#!/usr/bin/env python3
"""Freeze membership using event metadata only, then cache raw API data."""
import argparse,datetime,gzip,hashlib,json,pathlib,random,shutil
from fetch import HERE,RAW,fetch,get_json
SEED=26_092_500_001
START='2026-08-26';END='2026-09-24'

def main():
    events=get_json('https://play.limitlesstcg.com/api/tournaments?game=POCKET&limit=1000','tournaments_limit1000')
    assert min(x['date'][:10] for x in events)<START, 'Need further pagination'
    chosen=sorted([x for x in events if START<=x['date'][:10]<=END and x['format'] in (None,'STANDARD')],key=lambda x:x['id'])
    ids=[x['id'] for x in chosen];rng=random.Random(SEED);shuffled=ids.copy();rng.shuffle(shuffled)
    hold=set(shuffled[:len(ids)//2])
    manifest={'seed':SEED,'algorithm':'Python random.Random(seed).shuffle(sorted event ids); first floor(N/2) holdout','frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'start_date_utc':START,'end_date_utc':END,'timezone_note':'Run started Sept 24 America/Chicago, Sept 25 UTC. Include event start dates through Sept 24 UTC.','holdout_event_ids':sorted(hold),'development_event_ids':sorted(set(ids)-hold),'allowed_all_event_uses':['Sept 23 reproduction, all events, integrity check','page-vs-pairings counts, all events, integrity check'],'all_estimates':'development only, including skill records and decklist selection'}
    out=HERE/'split.json'
    if out.exists():
        old=json.loads(out.read_text());assert old['holdout_event_ids']==manifest['holdout_event_ids'] and old['development_event_ids']==manifest['development_event_ids'];manifest=old
    else:out.write_text(json.dumps(manifest,indent=2)+'\n')
    for e in chosen:e['split']='holdout' if e['id'] in hold else 'development'
    (HERE/'events.json').write_text(json.dumps(chosen,indent=2,ensure_ascii=False)+'\n')
    print(f'Frozen {len(chosen)} events: {len(hold)} holdout, {len(chosen)-len(hold)} development. No outcomes inspected.',flush=True)
    # Download development first; holdout bodies are only opened by explicitly scoped integrity/serialization code.
    for i,e in enumerate(sorted(chosen,key=lambda e:(e['split'],e['date'],e['id']))):
        print(f'Event {i+1}/{len(chosen)} {e["id"]} {e["split"]}',flush=True)
        for endpoint in ['details','standings','pairings']:
            key=f'{e["id"]}_{endpoint}'
            if endpoint=='details' and e['id']=='6aa84414f1243e65f980140f' and (RAW/'probe_details.json.gz').exists():
                shutil.copyfile(RAW/'probe_details.json.gz',RAW/f'{key}.json.gz');shutil.copyfile(RAW/'probe_details.meta.json',RAW/f'{key}.meta.json')
            fetch(f'https://play.limitlesstcg.com/api/tournaments/{e["id"]}/{endpoint}',key)
    print('COLLECTION COMPLETE',flush=True)
if __name__=='__main__':main()
