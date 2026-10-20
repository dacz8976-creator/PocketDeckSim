W=/home/dacz8976/pincand_work
for i in $(seq 1 110); do
  [ -e $W/more.done ] && break
  tmux has-session -t "=pinmore" 2>/dev/null || { echo "pinmore ended"; break; }
  sleep 30
done
date -u +%FT%TZ
grep -P '^(oldnew|new)\t(7c|dray|08a9b3a_8)' $W/games/summary.tsv | cut -f1-6 | cut -c1-200
[ -e $W/more.done ] || { echo "more not done"; exit 0; }
# U on every changed recorded run (new side), including the step 8 carrier row
cd /home/dacz8976/pincand
mkdir -p $W/pgids; echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/after.pgid
rm -f $W/games/u/verify.tsv
nice -n 19 python3 $W/u_verify.py
python3 $W/classify.py
cut -f1-4 $W/games/u/verify.tsv
for f in $W/games/oldnew/*.diff.tsv; do n=$(($(wc -l < $f) - 1)); echo "$(basename $f): $n"; [ $n -gt 0 ] && cat $f; done
date -u +%FT%TZ
