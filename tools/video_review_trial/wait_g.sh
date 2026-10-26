#!/bin/bash
# wait for one trial game to finish, then print its log, costs and job errors
G=/home/dacz8976/video_trial/$1
for i in $(seq 1 280); do
  grep -q 'game done' "$G/trial.log" 2>/dev/null && break
  tmux has-session -t "=vtrial${1#g}" 2>/dev/null || break
  sleep 30
done
cat "$G/trial.log"; echo "--- costs"; cat "$G/costs.jsonl" 2>/dev/null
for d in out_review_haiku out_review_sonnet out_check out_compare; do
  echo "--- $d: $(ls "$G/$d" 2>/dev/null | tr '\n' ' ')"
  [ -s "$G/$d/job.err" ] && tail -n 3 "$G/$d/job.err"
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print((d.get('result') or '')[:900])" "$G/$d/job.json" 2>/dev/null
done
