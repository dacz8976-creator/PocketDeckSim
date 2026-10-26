#!/bin/bash
# Two cheap follow-up tests: (1) a Sonnet "field pass" (OPPONENT.json only, <=30 full frames) on g1-g3;
# (2) Sonnet as checker of g3's Sonnet-pieces review (Opus found 2 majors there).
export PATH="$HOME/.local/bin:$PATH"
eval "$(grep '^export ANTHROPIC_API_KEY=' ~/.bashrc | tail -1)"
V=/home/dacz8976/video_trial; B=$V/briefs; LOG=$V/extra.log
cost() { python3 -c "import json,sys; d=json.load(open(sys.argv[2])); print(json.dumps({'job': sys.argv[1], 'cost_usd': d.get('total_cost_usd'), 'ms': d.get('duration_ms'), 'turns': d.get('num_turns')}))" "$1" "$2" >> $V/extra_costs.jsonl 2>/dev/null; }
run() {  # dir, name, prompt file, out, model, cap
  echo "$(date -u +%FT%TZ) $2 start" >> $LOG
  ( cd "$1" && claude -p "$(cat "$3") Your output folder is $1/$4 ." --bare --restricted --strict-mcp-config \
      --add-dir "$1/$4" --permission-mode acceptEdits --model "$5" --max-budget-usd "$6" --output-format json > "$1/$4/job.json" 2> "$1/$4/job.err" )
  echo "$(date -u +%FT%TZ) $2 end rc=$?" >> $LOG
  cost "$2" "$1/$4/job.json"
}
field() {  # gN, recording name
  D=$V/$1/field; mkdir -p $D/out_field
  [ -d $D/frames ] || cp -al $V/$1/frames $D/frames
  echo 'PLACEHOLDER - replace me' > $D/out_field/OPPONENT.json
  SH=$(ls $D/frames/sheets | sed 's#^#`frames/sheets/#; s#$#`#' | paste -sd, -)
  python3 -c "import sys; t=open(sys.argv[1]).read().replace('<SHEETS>', sys.argv[2]).replace('<RECORDING>', sys.argv[3]); open(sys.argv[4],'w').write(t)" \
     $B/BRIEF_FIELD.md "$SH" "$2" $D/prompt.md
  run $D field_$1 $D/prompt.md out_field claude-sonnet-5-5 3
}
field g1 "ScreenRecording_10-24-2026 15-29-43_1.mp4" &
field g2 "ScreenRecording_10-24-2026 12-51-31_1.mp4" &
field g3 "ScreenRecording_10-24-2026 13-24-53_1.mp4" &
# Sonnet check of the g3 Sonnet-pieces review (same input Opus checked)
S=$V/g3/ch_s_sc; mkdir -p $S/out_check
[ -d $S/frames ] || cp -al $V/g3/frames $S/frames
[ -d $S/out_write ] || cp -r $V/g3/ch_s/out_write $S/out_write
rm -f $S/out_write/job_*.json $S/out_write/job_*.err
sed 's#<REVIEW_DIR>#out_write#g' $B/BRIEF_CHECK1.md > $S/prompt.md
run $S sonnet_check_g3 $S/prompt.md out_check claude-sonnet-5-5 6 &
wait
echo "$(date -u +%FT%TZ) extra done" >> $LOG
