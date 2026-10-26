#!/bin/bash
cd /home/dacz8976/video_trial/g3/ch_h/out_segments || exit 1
ls
for k in 02 05 07; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1], d.get('num_turns'), d.get('total_cost_usd'), (d.get('result') or '')[:500])" job_seg_$k.json
done
