#!/bin/bash
V=/home/dacz8976/video_trial/g3
for i in $(seq 1 200); do
  grep -q 'ch_h2 done' $V/trial_chunks.log 2>/dev/null && break
  tmux has-session -t '=vchunk_h2' 2>/dev/null || break
  sleep 30
done
grep 'ch_h2' $V/trial_chunks.log | grep -v ' seg_'
echo "parts with content: $(grep -L 'PLACEHOLDER' $V/ch_h2/out_segments/PART_*.md | wc -l) of $(ls $V/ch_h2/out_segments/PART_*.md | wc -l)"
python3 - $V/ch_h2/costs.jsonl <<'EOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
seg = [r for r in rows if r['job'].startswith('seg_')]
print('pieces', len(seg), 'cost', round(sum(r.get('cost_usd') or 0 for r in seg), 3))
for r in rows:
    if not r['job'].startswith('seg_'): print(r)
EOF
for j in merge check compare; do
  f=$(ls $V/ch_h2/out_*/job_$j.json 2>/dev/null | head -1)
  [ -n "$f" ] && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print('--', sys.argv[2], (d.get('result') or '')[:700])" "$f" "$j"
done
