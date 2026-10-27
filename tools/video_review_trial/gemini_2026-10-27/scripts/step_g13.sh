#!/bin/bash
# g1 and g3: briefs (with free token probes), then the field pass and the review pass, one call at a time (one ledger)
cd /home/dacz8976/gemini_video || exit 1
bash step_dry2.sh g1 'ScreenRecording_10-24-2026 15-29-43_1.mp4' | tail -1
bash step_run2.sh g1 field | head -3
bash step_run2.sh g1 review | head -3
bash step_dry2.sh g3 'ScreenRecording_10-24-2026 13-24-53_1.mp4' | tail -1
bash step_run2.sh g3 field | head -3
bash step_run2.sh g3 review | head -3
echo "--- ledger"; python3 -c "import json; l=json.load(open('ledger.json')); print(round(l['accrued_usd'],4), [(c['out'].split('/')[-2]+'/'+c['out'].split('/')[-1], c['state'], c.get('usd')) for c in l['calls']])"
