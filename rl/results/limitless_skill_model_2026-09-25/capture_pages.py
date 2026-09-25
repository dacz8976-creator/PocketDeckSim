#!/usr/bin/env python3
"""Cache source pages; only deck labels and requested integrity counts are analyzed."""
import datetime,gzip,json,pathlib,re,time,requests
from bs4 import BeautifulSoup
HERE=pathlib.Path(__file__).resolve().parent;RAW=HERE/'raw'
def capture(url,key):
    p=RAW/(key+'.html.gz')
    if p.exists():return gzip.decompress(p.read_bytes())
    r=requests.get(url,timeout=90)
    with gzip.open(p,'wb') as f:f.write(r.content)
    (RAW/(key+'.meta.json')).write_text(json.dumps({'url':r.url,'status':r.status_code,'headers':dict(r.headers),'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    rate=r.headers.get('RateLimit','');rem=re.search(r'\br=(\d+)',rate);reset=re.search(r'\bt=(\d+)',rate)
    if r.status_code==429 or (rem and int(rem[1])==0):
        time.sleep(max(float(r.headers.get('Retry-After','1')),int(reset[1])+1 if reset else 300))
        if r.status_code!=200:raise RuntimeError(f'{r.status_code}, cached {url}')
    r.raise_for_status();time.sleep(1);return r.content
if __name__=='__main__':
    # The live pages pool holdout events: expose only the four requested integrity counts.
    ids={'altaria':'mega-altaria-ex-b1-espeon-b3a','sceptile':'butterfree-b3b-mega-sceptile-ex-b3','vespiquen':'vespiquen-ex-b4-shuckle-ex-a4'}
    allowed={'altaria':['sceptile'],'sceptile':['altaria','vespiquen'],'vespiquen':['sceptile']}
    for source,sid in ids.items():
        soup=BeautifulSoup(capture(f'https://play.limitlesstcg.com/decks/{sid}/matchups?game=POCKET&format=standard&set=B4a',sid+'_matchups'),'html.parser')
        for opponent in allowed[source]:
            oid=ids[opponent]
            for row in soup.select('tr[data-matches]'):
                link=row.find('a',href=lambda h:h and h.split('?')[0]==f'/decks/{oid}/matchups')
                if link:print(source,'vs',opponent,'count',int(row['data-matches']));break
