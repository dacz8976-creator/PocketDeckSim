#!/bin/bash
# replays_v_laneN.sh   (R8 record; coordinator-155 Q1)
# Read-only. The 18 replays the official build's lane ran on 543dad00 (unplanned: lane_r8.sh:206-207 gate them on goldfish_R.done,
# never on replays_R.done) against Lane N's 18 on 48dec4f5 (the basis under Q2 (A); the same engine tree, the same five programs).
#   1. games/summary.tsv: every r row equal after dropping the seconds column and normalising the RR_R8_<commit> folder name.
#   2. games/r: the same file names; each file byte-equal, or equal after normalising that folder name (and the worktree path),
#      or (only for *_cli_*.txt) equal after also dropping the one "Ran N simulations in ..." timing line. Anything else fails.
#   3. every *.jsonl (the games) and *_coverage.json byte-equal (12: 11 games files and goldfish's coverage).
set -u
A=${R_DIR:-/home/dacz8976/pincand_work/RR_R8_543dad00}/games; B=${N_DIR:-/home/dacz8976/pincand_work/RR_R8_48dec4f5}/games
norm() { sed -E 's#RR_R8_[0-9a-f]{8}#RR_R8_X#g' "$1"; }
ok=1
na=$(grep -cP '^r\t' $A/summary.tsv); nb=$(grep -cP '^r\t' $B/summary.tsv)
sa() { grep -P '^r\t' $1 | awk -F'\t' 'BEGIN{OFS="\t"}{$4="";print}' | sed -E 's#RR_R8_[0-9a-f]{8}#RR_R8_X#g' | sort; }
if [ $na = 18 ] && [ $nb = 18 ] && diff <(sa $A/summary.tsv) <(sa $B/summary.tsv) > /dev/null; then echo "summary.tsv: 18 r rows each, equal row for row (seconds and the RR folder name aside)"
else ok=0; echo "summary.tsv: NOT equal ($na v $nb rows)"; diff <(sa $A/summary.tsv) <(sa $B/summary.tsv) | head -n 10 | cut -c1-240; fi
fa=$(cd $A/r && find . -type f | sort); fb=$(cd $B/r && find . -type f | sort)
[ "$fa" = "$fb" ] && echo "games/r: the same $(echo "$fa" | wc -l) file names" || { ok=0; echo "games/r: the file names differ"; diff <(echo "$fa") <(echo "$fb") | head; }
nb_=0; nn=0; nt=0; bad=0; ng=0
for f in $fa; do
  case $f in *.jsonl|*_coverage.json) ng=$((ng+1)); cmp -s $A/r/$f $B/r/$f || { bad=$((bad+1)); echo "GAMES/COVERAGE DIFFER: $f"; }; continue;; esac
  if cmp -s $A/r/$f $B/r/$f; then nb_=$((nb_+1))
  elif diff -q <(norm $A/r/$f) <(norm $B/r/$f) > /dev/null; then nn=$((nn+1))
  elif [[ $f == *_cli_*.txt ]] && diff -q <(norm $A/r/$f | grep -v '^Ran [0-9]* simulations in ') <(norm $B/r/$f | grep -v '^Ran [0-9]* simulations in ') > /dev/null; then nt=$((nt+1))
  else bad=$((bad+1)); echo "OTHER DIFF: $f"; diff <(norm $A/r/$f) <(norm $B/r/$f) | head -n 4 | cut -c1-200; fi
done
echo "games/r: $ng games/coverage files byte-equal: $([ $bad = 0 ] && echo yes || echo NO); other files: $nb_ byte-equal, $nn equal after normalising the RR folder name, $nt equal after also dropping the cli timing line; $bad other"
[ $bad = 0 ] && [ $ng = 12 ] || ok=0
if [ $ok = 1 ]; then echo "RESULT: the official build's 18 replays equal Lane N's"; exit 0; fi
echo "RESULT: NOT equal"; exit 1
