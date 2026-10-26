#!/bin/bash
# slowpin_run_tests.sh TAG [REPO_DIR] [MODULES...]: the nine rl/strength test modules, 4 at a time at nice 19; one output file per module under ~/slowpin_out/TAG/
TAG=$1; REPO=${2:-/home/dacz8976/slowpin}; shift 2 || true
MODS=${*:-"test_slow_report test_slow_report_registration test_slow_report_page test_slow_report_process test_slow_report_runloop test_slow_report_existing test_strength_prereg_use test_strength_report test_split_collect"}
OUT=/home/dacz8976/slowpin_out/$TAG
unset KX_RUNS_DIR   # the launcher sets it; the program-environment tests must not see it
mkdir -p $OUT
cd $REPO/rl/strength
run_mod() {
  m=$1
  s=$(date +%s)
  nice -n 19 python3 -B -m unittest $m > $OUT/$m.txt 2>&1
  rc=$?
  echo "$m rc=$rc secs=$(( $(date +%s) - s )) $(tail -3 $OUT/$m.txt | tr '\n' ' ' | cut -c1-160)"
}
export -f run_mod; export OUT
printf '%s\n' $MODS | xargs -P 4 -I{} bash -c 'run_mod {}' | tee $OUT/SUMMARY.txt
echo "done $TAG"