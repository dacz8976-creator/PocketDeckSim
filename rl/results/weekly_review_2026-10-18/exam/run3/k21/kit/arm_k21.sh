#!/bin/bash
# Arms K21 (coordinator, Oct 26: "Arm for tonight's window as registered"): copies the kit and run 3's live folder from the pinned kit commit into
# ~/k21_run, then a tmux session (setsid) that starts run_k21.sh at 02:00Z on each registered night: 2026-10-27, -28, -30, -31 UTC (Mon, Tue,
# Thu, Fri nights CT). Never 2026-10-29 UTC (Wednesday night, Dual Fusion). A stop (k21_run/STOPPED) or the end (k21_run/DONE) ends the loop.
# Disarm: touch ~/k21_run/DISARM (checked before each night), or tmux kill-session -t k21 while it waits.
#   bash arm_k21.sh <kit commit>
set -euo pipefail
KIT_COMMIT=$1
K=/home/dacz8976/k21_run
REPO=/home/dacz8976/exam_034_w
EXAM_BRANCH=sonnet/exam-2026-10-19
RUN3=rl/results/weekly_review_2026-10-18/exam/run3
[ -e "$K/launch" ] && { echo "$K/launch exists: K21 already launched once; not re-arming over it"; exit 1; }
git -C "$REPO" fetch -q origin "$EXAM_BRANCH"
git -C "$REPO" merge-base --is-ancestor "$KIT_COMMIT" FETCH_HEAD || { echo "$KIT_COMMIT is not on $EXAM_BRANCH"; exit 1; }
rm -rf "$K/kit" "$K/live"
mkdir -p "$K/kit" "$K/live"
for f in run_k21.sh build_k21.sh gates_k21.py kx3_rows.py compare_k21.py arm_k21.sh watch_k21.sh; do
  git -C "$REPO" show "$KIT_COMMIT:$RUN3/k21/kit/$f" > "$K/kit/$f"
done
git -C "$REPO" archive "$KIT_COMMIT" "$RUN3/live-20261026T020013Z" | tar -x -C "$K/live" --strip-components=6
[ -s "$K/live/report_primary.json" ] && [ -d "$K/live/in/decks" ] || { echo "run 3's live folder did not extract"; exit 1; }
echo "$KIT_COMMIT" > "$K/KIT_COMMIT"
cat > "$K/nights.sh" <<EOF
#!/bin/bash
L=$K/launcher.log
say() { echo "\$(date -u +%FT%TZ) \$*" >> "\$L"; }
say "armed: kit $KIT_COMMIT; nights 2026-10-27 2026-10-28 2026-10-30 2026-10-31 at 02:00Z (never 2026-10-29)"
for D in 2026-10-27 2026-10-28 2026-10-30 2026-10-31; do
  T=\$(date -u -d "\$D 02:00:00" +%s); NOW=\$(date -u +%s)
  [ \$NOW -ge \$((T + 10 * 3600 + 50 * 60)) ] && { say "\$D: that night is over"; continue; }
  [ \$NOW -lt \$T ] && { say "waiting for \$D 02:00Z"; sleep \$((T - NOW)); }
  [ -e $K/DISARM ] && { say "disarmed (k21_run/DISARM): not starting \$D"; exit 0; }
  [ -e $K/STOPPED ] && { say "a stop holds: not starting \$D"; exit 0; }
  [ -e $K/DONE ] && { say "K21 done: nothing more"; exit 0; }
  say "\$D: starting run_k21.sh"
  ( cd $K && bash $K/kit/run_k21.sh ) >> $K/run_k21.stdout 2>&1
  say "\$D: run_k21.sh exit \$?; status \$(cat $K/STATUS_\$D 2>/dev/null)"
done
say "the registered nights are over"
EOF
tmux kill-session -t k21 2>/dev/null || true
tmux new-session -d -s k21 "setsid -w bash $K/nights.sh"
sleep 2
tmux has-session -t k21 && echo "armed: tmux k21; kit $KIT_COMMIT; $(tail -n 2 "$K/launcher.log" | tr '\n' ' ')"
