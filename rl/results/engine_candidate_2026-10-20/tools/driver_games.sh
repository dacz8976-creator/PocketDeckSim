#!/bin/bash
# Engine candidate, night driver 2: the self-check games. Waits for driver 1 (builds, suite, km3 self-checks), then:
# the old pin's sample (step 10 and the kd3 table, to show it still runs and reproduces), then the candidate's tier 1 and tier 2.
# Each replay is skipped when summary.tsv already has it (resumable). The keeper freezes this group 12:55Z-02:00Z.
set -u
W=/home/dacz8976/pincand_work
R=/home/dacz8976/pincand
LOG=$W/driver.log
mkdir -p $W/pgids $W/games
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/games.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
log "driver_games: waiting for driver 1 (selfcheck_km3.done)"
while [ ! -e $W/selfcheck_km3.done ]; do
  if ! tmux has-session -t "=pincand" 2>/dev/null && [ ! -e $W/selfcheck_km3.done ]; then log "driver 1 ended without finishing: driver_games stops"; exit 1; fi
  sleep 60
done
# the old side: an archive of main (engine tree 70652fff, the pinned programs' source) for the working folder, and the pinned
# programs themselves, checked against SHA256SUMS (never written into rl/engine-2026-10-12/)
if [ ! -e $W/O.done ]; then
  rm -rf $W/O && mkdir -p $W/O $W/programs/O
  git -C $R -c core.autocrlf=false archive origin/main engine decks | tar -x -C $W/O
  cp $R/rl/engine-2026-10-12/deckgym $R/rl/engine-2026-10-12/legality_scan $R/rl/engine-2026-10-12/goldfish $W/programs/O/
  chmod +x $W/programs/O/*
  ( cd $W/programs/O && sha256sum -c $R/rl/engine-2026-10-12/SHA256SUMS ) >> $LOG 2>&1 || { log "old programs do not match SHA256SUMS: stop"; exit 1; }
  date -u +%FT%TZ > $W/O.done
fi
run() {  # side name
  if grep -q -P "^$1\t$2\t" $W/games/summary.tsv 2>/dev/null; then return; fi
  python3 $W/replay.py "$1" "$2" >> $LOG 2>&1 || log "replay $1 $2: the tool failed (exit $?)"
}
CLI="08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish 08a9b3a_10_run_screen"
log "old sample: step 10 and the kd3 table"
for n in $CLI 08a9b3a_table_kd3_40; do run old $n; done
log "new tier 1"
for n in $CLI floor:14 floor:10 floor:06 floor:02 floor:08 floor:D_root floor:D_amended \
         08a9b3a_new17_k3 08a9b3a_new17_kp3 08a9b3a_dev_km3_new17 08a9b3a_cov_var_v-lucario_2_km3 \
         08a9b3a_table_k3 08a9b3a_table_kp3 08a9b3a_dev_km3_table; do run new $n; done
date -u +%FT%TZ > $W/tier1.done
log "new tier 2"
for n in 08a9b3a_table_kd3_40 08a9b3a_table_kpr3_40 08a9b3a_new17_kog3 08a9b3a_table_kog3 08a9b3a_table_kq3 \
         08a9b3a_cov_var_v-suicune_2_km3 08a9b3a_cov_var_v-weezing_2_km3 08a9b3a_cov_scizor_km3 08a9b3a_cov_var_l-charizardy_km3 \
         08a9b3a_dev_kta3_new17 08a9b3a_fresh_kta3_new17 08a9b3a_dev_kta3_table 08a9b3a_fresh_kta3_table 08a9b3a_cov_b2e_km3; do run new $n; done
date -u +%FT%TZ > $W/tier2.done
log "driver_games done"
