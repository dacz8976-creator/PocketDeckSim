#!/bin/bash
N=/home/dacz8976/pincand_work/RR_R8_543dad00/sw3
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
while [ ! -e $N/sc_kx3.rc ] || [ ! -e $N/floor.rc ]; do sleep 60; done
line=$(tail -n 1 $N/sc_kx3.full); echo "$line" > $N/sc_kx3.out
echo "sc_kx3 rc/secs $(cat $N/sc_kx3.rc): $line"
[ "$line" = "$SC_KX3" ] && echo "SC_KX3 EQUAL" || { echo "SC_KX3 STOP: differs from the pin"; tail -n 5 $N/sc_kx3.err; }
echo "floor rc/secs $(cat $N/floor.rc)"; tail -n 3 $N/floor.log; cut -c1-200 /home/dacz8976/pincand_work/floor2R8/summary.tsv
cp /home/dacz8976/relplan/r8/sw/floorR8_recompare.sh $N/
bash $N/floorR8_recompare.sh > $N/floorR8_recompare.txt 2>&1; echo "recompare exit $?"
cut -c1-400 $N/floorR8_recompare.txt
