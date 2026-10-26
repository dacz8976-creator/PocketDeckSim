#!/bin/bash
# wait for games 2 and 3 (both arms), then print logs, costs and each job's closing reply
V=/home/dacz8976/video_trial
for i in $(seq 1 300); do
  d2=$(grep -c 'game done' $V/g2/trial.log 2>/dev/null); d3=$(grep -c 'game done' $V/g3/trial.log 2>/dev/null)
  [ "${d2:-0}" -ge 1 ] && [ "${d3:-0}" -ge 1 ] && break
  tmux has-session -t '=vtrial2' 2>/dev/null || tmux has-session -t '=vtrial3' 2>/dev/null || break
  sleep 30
done
for g in g2 g3; do
  echo "################ $g"; cat $V/$g/trial.log
  for a in arm_s arm_t; do
    echo "== $g $a costs"; cat $V/$g/$a/costs.jsonl 2>/dev/null
    for d in $V/$g/$a/out_*; do
      echo "-- $(basename $d)"; [ -s $d/job.err ] && tail -n 2 $d/job.err
      python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print((d.get('result') or '')[:700])" $d/job.json 2>/dev/null
    done
  done
done
