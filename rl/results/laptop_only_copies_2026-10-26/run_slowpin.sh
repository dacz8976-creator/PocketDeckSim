#!/bin/bash
# The slow report's re-pin draft on top of the adoption draft, its pin tests in a worktree, the PIN_TESTS.txt follow-up commit.
set -eu
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad
R=/home/dacz8976/pincand_work/release
BR=laptop/new-slow-pin-2026-10-20
CAND=rl/results/engine_candidate_2026-10-20
cd /home/dacz8976/pincand
A=$(git rev-parse laptop/engine-adoption-draft-2026-10-20)
[ "$A" = "$(git rev-parse origin/laptop/engine-adoption-draft-2026-10-20)" ] || { echo "adoption draft not pushed"; exit 1; }
cat > $R/vars_slowpin.json <<EOF
{"base": "$A", "K": "87a7f3404263e1bfe76e8765ba8dd94695e19cfe", "kbranch": "laptop/kx3-on-engine-candidate-2026-10-20",
 "program": "/home/dacz8976/kx_r3/strength", "cert_dir": "$R", "branch": "$BR",
 "f_commit": "4d4884492aa85496acf9bafdae18b22739f56647"}
EOF
python3 -I $S/hb/slowpin_final.py $R/vars_slowpin.json --dry-run
python3 -I $S/hb/slowpin_final.py $R/vars_slowpin.json ${1:-}
P=$(git rev-parse $BR)
echo "slow-pin draft $P"

# the pin tests, foreground, KX_RUNS_DIR unset
WT=/home/dacz8976/slowpin_final_w
[ -e $WT ] && git worktree remove --force $WT
git worktree add -q --detach $WT $P
unset KX_RUNS_DIR
TAG=final_$(date -u +%m%dT%H%M)
bash /home/dacz8976/slowpin_run_tests.sh $TAG $WT
OUT=/home/dacz8976/slowpin_out/$TAG
(cd $WT/rl/strength && s=$(date +%s) && nice -n 19 python3 -B -m unittest test_slow_report_paired > $OUT/test_slow_report_paired.txt 2>&1; \
  echo "test_slow_report_paired rc=$? secs=$(( $(date +%s) - s )) $(tail -3 $OUT/test_slow_report_paired.txt | tr '\n' ' ' | cut -c1-160)") | tee -a $OUT/SUMMARY.txt
echo "worktree status: $(git -C $WT status --porcelain | wc -l) changes"

# PIN_TESTS.txt, a follow-up commit on the slow-pin branch (private index; nothing checked out)
{ echo "The slow report's pin tests at $P ($BR), run $(date -u +%FT%TZ) in a detached worktree of that commit,"
  echo "with KX_RUNS_DIR unset, in a foreground shell (the signal tests need it), nice 19; /home/dacz8976/slowpin_run_tests.sh"
  echo "(the nine modules, 4 at a time) and test_slow_report_paired after them. Per module: rc, seconds, the last lines."
  echo
  sort $OUT/SUMMARY.txt; } > $R/PIN_TESTS.txt
cat $R/PIN_TESTS.txt
if grep -q -E 'rc=[1-9]' $OUT/SUMMARY.txt; then echo "A MODULE FAILED: no follow-up commit"; git worktree remove --force $WT; exit 1; fi
IDX=$(mktemp); rm -f $IDX
GIT_INDEX_FILE=$IDX git read-tree $P
GIT_INDEX_FILE=$IDX git update-index --add --cacheinfo 100644,$(git hash-object -w $R/PIN_TESTS.txt),$CAND/slow_pin/PIN_TESTS.txt
T=$(GIT_INDEX_FILE=$IDX git write-tree); rm -f $IDX
C=$(git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree $T -p $P -F - <<EOF
DRAFT, NOT ADOPTED: the slow report's new pin, its pin tests (PIN_TESTS.txt)

The nine rl/strength test modules and test_slow_report_paired, run at ${P:0:8} with KX_RUNS_DIR unset:
every module rc=0. Record: $CAND/slow_pin/PIN_TESTS.txt.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)
git update-ref refs/heads/$BR $C $P
git diff-tree -r --name-status $P $C
git push ${LEASE:+--force-with-lease=$BR:$LEASE} origin $BR 2>&1 | tail -n 3
git ls-remote origin $BR
git worktree remove --force $WT; git worktree prune
