#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
sed -i 's/\r$//' briefs/BRIEF_FIELD.md run_extra.sh
setsid tmux new-session -d -s vextra "bash /home/dacz8976/video_trial/run_extra.sh > /home/dacz8976/video_trial/extra.out 2>&1"
sleep 3; tmux ls | grep vextra
# then wait for it and print results
for i in $(seq 1 120); do grep -q 'extra done' extra.log 2>/dev/null && break; tmux has-session -t '=vextra' 2>/dev/null || break; sleep 30; done
cat extra.log; echo '--- costs'; cat extra_costs.jsonl
for g in g1 g2 g3; do echo "== field $g"; head -c 1500 $g/field/out_field/OPPONENT.json; echo; python3 -c "import json,sys; print((json.load(open(sys.argv[1])).get('result') or '')[:200])" $g/field/out_field/job.json; done
echo "== sonnet check g3"; python3 -c "import json,sys; print((json.load(open(sys.argv[1])).get('result') or '')[:1500])" g3/ch_s_sc/out_check/job.json
