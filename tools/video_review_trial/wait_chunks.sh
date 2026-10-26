#!/bin/bash
V=/home/dacz8976/video_trial/g3
for i in $(seq 1 300); do
  n=$(grep -c ' done$' $V/trial_chunks.log 2>/dev/null)
  [ "${n:-0}" -ge 2 ] && break
  tmux has-session -t '=vchunk_h' 2>/dev/null || tmux has-session -t '=vchunk_s' 2>/dev/null || break
  sleep 30
done
cat $V/trial_chunks.log | grep -v ' seg_' ; echo "(piece lines omitted)"
for a in ch_h ch_s; do
  echo "== $a"
  python3 - $V/$a/costs.jsonl <<'EOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
seg = [r for r in rows if r['job'].startswith('seg_')]
print('pieces', len(seg), 'cost', round(sum(r.get('cost_usd') or 0 for r in seg), 3), 'errors', sum(1 for r in seg if r.get('is_error')))
for r in rows:
    if not r['job'].startswith('seg_'): print(r)
EOF
  ls $V/$a/out_segments | grep -c PART_
  for j in merge check compare; do
    f=$(ls $V/$a/out_*/job_$j.json 2>/dev/null | head -1)
    [ -n "$f" ] && python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print('--', sys.argv[2], (d.get('result') or '')[:800])" "$f" "$j"
  done
done
