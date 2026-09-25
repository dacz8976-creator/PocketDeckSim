#!/usr/bin/env python3
"""Cache every HTTP response and obey Limitless RateLimit/Retry-After headers.
Only writes beneath this script's directory. Resume uses successful cached bodies.
"""
import argparse,datetime,gzip,hashlib,json,pathlib,re,time,email.utils,requests
HERE=pathlib.Path(__file__).resolve().parent
RAW=HERE/'raw'; RAW.mkdir(exist_ok=True)
STATE=RAW/'rate_state.json'

def fetch(url,key=None,kind='json'):
    key=key or hashlib.sha256(url.encode()).hexdigest()[:20]
    body=RAW/f'{key}.{kind}.gz'; meta=RAW/f'{key}.meta.json'
    if body.exists() and meta.exists() and json.loads(meta.read_text()).get('status')==200:
        return gzip.decompress(body.read_bytes())
    for attempt in range(6):
        state=json.loads(STATE.read_text()) if STATE.exists() else {}
        wait=state.get('next_request',0)-time.time()
        if wait>0:
            print(f'Rate-limit wait {wait:.1f}s',flush=True)
            time.sleep(wait)
        try:
            r=requests.get(url,timeout=90,headers={'User-Agent':'PocketDeckSim diagnostic research; cached sequential requests'})
        except requests.RequestException as e:
            with (RAW/'transport_errors.jsonl').open('a') as f:f.write(json.dumps({'url':url,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':str(e)})+'\n')
            time.sleep(min(60,2**attempt));continue
        suffix='' if attempt==0 and not body.exists() else f'.attempt{int(time.time())}'
        saved=RAW/f'{key}{suffix}.{kind}.gz'
        with gzip.open(saved,'wb') as f:f.write(r.content)
        info={'url':r.url,'requested_url':url,'status':r.status_code,'headers':dict(r.headers),'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(r.content).hexdigest(),'body':saved.name}
        (RAW/f'{key}{suffix}.meta.json').write_text(json.dumps(info,indent=2))
        rate=r.headers.get('RateLimit',''); rem=re.search(r'\br=(\d+)',rate); reset=re.search(r'\bt=(\d+)',rate)
        delay=0.2
        if rem and reset:
            remaining,seconds=int(rem[1]),int(reset[1]);delay=seconds+1 if remaining<=0 else .3
        elif r.headers.get('X-RateLimit-Remaining')=='0':
            value=float(r.headers.get('X-RateLimit-Reset','300'));delay=max(1,value-time.time()) if value>1e9 else value+1
        retry=r.headers.get('Retry-After')
        if retry:
            try:delay=max(delay,float(retry)+1)
            except ValueError:delay=max(delay,email.utils.parsedate_to_datetime(retry).timestamp()-time.time()+1)
        if r.status_code==429:delay=max(delay,60)
        STATE.write_text(json.dumps({'next_request':time.time()+delay,'rate':rate,'last_url':url}))
        print(f'{r.status_code} {key} {len(r.content)} bytes [{rate}]',flush=True)
        if r.status_code==200:
            if saved!=body:
                body.write_bytes(saved.read_bytes());meta.write_text(json.dumps(info,indent=2))
            return r.content
        if r.status_code not in (429,500,502,503,504):raise RuntimeError(f'{r.status_code}: {url}; cached {saved}')
    raise RuntimeError(f'Failed after retries: {url}')

def get_json(url,key):return json.loads(fetch(url,key))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('url');ap.add_argument('key');ap.add_argument('--kind',default='json');a=ap.parse_args()
    data=fetch(a.url,a.key,a.kind);print(data[:12000].decode(errors='replace'))
