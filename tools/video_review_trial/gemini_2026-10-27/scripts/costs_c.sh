#!/bin/bash
cd /home/dacz8976/credit_work/tools || exit 1
for f in g1/costs.jsonl g2/arm_s/costs.jsonl g3/ch_s/costs.jsonl; do
  echo "== $f"
  git show "claude/video-review-trial-2026-10-26:tools/video_review_trial/results/$f" | python3 -c 'import sys,json
for l in sys.stdin:
    d=json.loads(l); print(d.get("job"), d.get("cost_usd"), round((d.get("ms") or 0)/60000,1), "min")'
done
