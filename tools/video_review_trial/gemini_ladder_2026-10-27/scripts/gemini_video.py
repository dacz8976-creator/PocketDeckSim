"""Gemini video trial (Oct 27): one game video + one brief -> one Vertex AI generateContent call, under a hard dollar cap.

usage: gemini_video.py --video V.mp4 --brief B.md --out DIR --fps F [--resolution LOW|MEDIUM|HIGH] [--ledger L] [--cap-usd 10] [--dry]

- The key is read like the frozen judge's providers.load_key: VERTEX_API_KEY from the environment, else the LAST `export VERTEX_API_KEY=` line of
  ~/.bashrc (parsed as text, never executed, never printed, never stored).
- Before any charged call, countTokens (free) gives the exact input size. The call is sent only if
  ledger accrued + this call's worst case <= cap, where worst case = input tokens x $4/M + maxOutputTokens x $20/M (the higher published price).
  The actual cost (at $2 / $10 per M through 2026-11-30, thinking billed as output) then replaces the worst case in the ledger.
  A failed call is charged its full worst case.
- Writes DIR/response.txt (the model's text), DIR/usage.json (tokens, seconds, cost, settings) and appends to the ledger.
"""
import argparse, base64, json, os, re, sys, time, urllib.request, urllib.error, datetime

PROJECT = 'project-45583ef0-ed57-426c-bde'  # as committed in run3/PREREG_RUN3.md (a project id, not a secret)
MODEL = 'gemini-4-argon'
BASE = f'https://aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/global/publishers/google/models/{MODEL}'
MAX_OUT = 32768  # the most a non-streaming direct HTTP call allows (frozen-7's setting)
RESERVE = (4.0, 20.0)
def price_today():
    return (2.0, 10.0) if datetime.date.today() <= datetime.date(2026, 11, 30) else (4.0, 20.0)

def load_key(var='VERTEX_API_KEY'):
    k = (os.environ.get(var) or '').strip()
    if not k:
        p = os.path.expanduser('~/.bashrc')
        for line in open(p, encoding='utf-8', errors='replace') if os.path.exists(p) else []:
            m = re.match(r'\s*export\s+' + re.escape(var) + r'=(.*)$', line.strip())
            if m:
                k = m.group(1).strip().strip('"').strip("'").rstrip('\r')
    if not re.fullmatch(r'[A-Za-z0-9._-]{20,}', k or ''):
        sys.exit(f'{var}: not set or not a plain key (value not shown)')
    return k

def post(url, key, body, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors='replace')
        return e.code, {'error_text': txt.replace(key, '<key>')[:4000]}

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--video', required=True); a.add_argument('--brief', required=True); a.add_argument('--out', required=True)
    a.add_argument('--fps', type=float, default=1.0); a.add_argument('--resolution', default=None, choices=[None, 'LOW', 'MEDIUM', 'HIGH'])
    a.add_argument('--thinking', default='HIGH'); a.add_argument('--ledger', default=os.path.expanduser('~/gemini_video/ledger.json'))
    a.add_argument('--cap-usd', type=float, default=10.0); a.add_argument('--dry', action='store_true')
    o = a.parse_args()
    os.makedirs(o.out, exist_ok=True)
    key = load_key()
    vid = open(o.video, 'rb').read()
    if len(vid) > 19 * 1024 * 1024:
        sys.exit(f'video is {len(vid)/1e6:.1f} MB; inline data must stay under about 20 MB: re-encode smaller')
    brief = open(o.brief, encoding='utf-8').read()
    part_v = {'inlineData': {'mimeType': 'video/mp4', 'data': base64.b64encode(vid).decode()}, 'videoMetadata': {'fps': o.fps}}
    contents = [{'role': 'user', 'parts': [part_v, {'text': brief}]}]
    gen = {'maxOutputTokens': MAX_OUT, 'thinkingConfig': {'thinkingLevel': o.thinking}}
    if o.resolution:
        gen['mediaResolution'] = 'MEDIA_RESOLUTION_' + o.resolution
    st, ct = post(BASE + ':countTokens', key, {'contents': contents}, 300)
    if st != 200 or 'totalTokens' not in ct:
        sys.exit(f'countTokens failed: HTTP {st} {json.dumps(ct)[:1500]}')
    tin = ct['totalTokens']
    worst = tin * RESERVE[0] / 1e6 + MAX_OUT * RESERVE[1] / 1e6
    led = json.load(open(o.ledger)) if os.path.exists(o.ledger) else {'cap_usd': o.cap_usd, 'accrued_usd': 0.0, 'calls': []}
    print(f'input tokens {tin} (countTokens; media resolution {o.resolution or "default"}, fps {o.fps}); worst case ${worst:.3f}; ledger ${led["accrued_usd"]:.3f} of ${o.cap_usd:.2f}')
    if o.dry:
        return
    if led['accrued_usd'] + worst > o.cap_usd:
        sys.exit('REFUSED: this call\'s worst case does not fit under the cap; nothing sent')
    led['accrued_usd'] += worst; led['calls'].append({'out': o.out, 'state': 'in_flight', 'reserved': worst})
    json.dump(led, open(o.ledger, 'w'), indent=1)
    t0 = time.time()
    st, r = post(BASE + ':generateContent', key, {'contents': contents, 'generationConfig': gen}, 1500)
    secs = round(time.time() - t0, 1)
    um = r.get('usageMetadata') or {}
    pin, pout = price_today()
    if st == 200 and um.get('promptTokenCount') is not None:
        out_tok = (um.get('candidatesTokenCount') or 0) + (um.get('thoughtsTokenCount') or 0)
        usd = um['promptTokenCount'] * pin / 1e6 + out_tok * pout / 1e6
    else:
        usd = worst  # failed call or no usage: charged in full
    led['accrued_usd'] += usd - worst
    led['calls'][-1].update({'state': 'ok' if st == 200 else f'http_{st}', 'usd': round(usd, 5), 'seconds': secs})
    json.dump(led, open(o.ledger, 'w'), indent=1)
    cand = (r.get('candidates') or [{}])[0]
    text = ''.join(p.get('text', '') for p in (cand.get('content') or {}).get('parts', []) if not p.get('thought'))
    open(os.path.join(o.out, 'response.txt'), 'w', encoding='utf-8').write(text)
    rec = {'http': st, 'seconds': secs, 'usd': round(usd, 5), 'usd_is_worst_case': not (st == 200 and um.get('promptTokenCount') is not None),
           'price_per_mtok': [pin, pout], 'usage': um, 'finish_reason': cand.get('finishReason'), 'count_tokens': tin,
           'settings': {'model': MODEL, 'fps': o.fps, 'media_resolution': o.resolution, 'thinking': o.thinking, 'max_output_tokens': MAX_OUT},
           'video': os.path.basename(o.video), 'video_mb': round(len(vid) / 1e6, 2), 'brief': os.path.basename(o.brief)}
    if st != 200:
        rec['error'] = r.get('error_text', json.dumps(r)[:2000])
    json.dump(rec, open(os.path.join(o.out, 'usage.json'), 'w'), indent=1)
    print(f'HTTP {st}, {secs} s, ${usd:.4f}, finish {cand.get("finishReason")}, answer {len(text)} chars; ledger now ${led["accrued_usd"]:.3f}')

if __name__ == '__main__':
    main()
