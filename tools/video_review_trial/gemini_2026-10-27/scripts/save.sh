#!/bin/bash
# Save the Gemini video trial (scripts, briefs, Gemini outputs, scores, ledger) as one commit on a new branch, built with a
# private index (no worktree, no checkout), on top of the Oct 25-26 trial branch; push that branch only.
set -e
R=/home/dacz8976/credit_work/tools
SP=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/b816037a-8268-412e-9510-8518f9b17037/scratchpad
ST=/home/dacz8976/gv_stage
D=$ST/tools/video_review_trial/gemini_2026-10-27
B=claude/gemini-video-trial-2026-10-27
GH=https://github.com/dacz8976-creator/PocketDeckSim.git
rm -rf $ST; mkdir -p $D/scripts $D/briefs
cp $SP/gvideo/{gemini_video.py,encode.sh,split.sh,step_enc.sh,step_dry.sh,step_run.sh,step_g13.sh,step_med.sh,step_ref.sh,costs_c.sh,save.sh} $D/scripts/
cp $SP/gvideo/{REVIEW_VIDEO.md,FIELD_VIDEO.md} $SP/gscore/BRIEF_SCORE.md $D/briefs/
cp $SP/gvideo/README.md $D/
for g in g1 g2 g3; do
  for p in field review review_med; do
    case $p in review_med) n=review_default;; *) n=$p;; esac
    mkdir -p $D/$g/$n; cp /home/dacz8976/gemini_video/$g/out_$p/{response.txt,usage.json} $D/$g/$n/
  done
  mkdir -p $D/$g/score_high $D/$g/score_default
  cp $SP/gscore/$g/score/{SCORE.md,score.json} $D/$g/score_high/
  cp $SP/gscore/$g/med/score/{SCORE.md,score.json} $D/$g/score_default/
done
cp /home/dacz8976/gemini_video/ledger.json $D/
find $D -type f \( -name '*.sh' -o -name '*.py' -o -name '*.md' -o -name '*.json' -o -name '*.txt' \) -exec sed -i 's/\r$//' {} +
if grep -rlE --exclude=save.sh 'AIza[0-9A-Za-z_-]{20,}|AQ\.[0-9A-Za-z_-]{20,}|sk-ant-' $D; then echo "SECRET PATTERN FOUND: not committing"; exit 1; fi  # save.sh holds this pattern itself
echo "files: $(find $D -type f | wc -l), size: $(du -sh $D | cut -f1)"
cd $R
P=$(git rev-parse claude/video-review-trial-2026-10-26)
export GIT_INDEX_FILE=/home/dacz8976/gv_stage.idx
git read-tree $P
git --work-tree=$ST add tools/video_review_trial/gemini_2026-10-27
T=$(git write-tree)
printf '%s\n' "Gemini video trial (Oct 27): 3 ranked games read by Gemini 4 Argon on Vertex AI" "" \
  "Same 3 games as the Oct 25-26 Claude v Codex trial. Field pass (1 fps), full review at HIGH media" \
  "resolution and at the default resolution; each review scored against the checked Claude finals and" \
  "the frames. Total Gemini spend \$2.78 of a \$10 cap (Dustin's Google credits). Results in README.md." "" \
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > /home/dacz8976/gv_msg.txt
C=$(git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree $T -p $P -F /home/dacz8976/gv_msg.txt)
unset GIT_INDEX_FILE; rm -f /home/dacz8976/gv_stage.idx /home/dacz8976/gv_msg.txt
git update-ref refs/heads/$B $C
git show --stat --format='%h %s' $C | tail -3
git push -q $GH $C:refs/heads/$B
git ls-remote $GH refs/heads/$B
rm -rf $ST
