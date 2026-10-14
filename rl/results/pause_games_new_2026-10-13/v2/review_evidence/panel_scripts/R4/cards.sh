cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
for c in "A3b 051" "B4 116" "A1 183" "B2b 051" "B4 117" "A1 186" "B1 180" "B2 124" "A3 108" "A3a 037" "B2 094" "P-B 006" "A2b 055" "B2b 049" "B4 114" "B2a 075" "P-B 044" "B2b 050" "B2b 047" "B2b 001" "B2a 077" "B3b 064" "A2 147" "B4 154" "B2a 093" "B4 155" "B3a 045" "B3a 043" "B3 134" "B2 097" "A3 110" "A1a 056" "B2b 054" "B2b 056" "A2 148" "B2 145" "A3 149" "B1 219"; do
  echo "=================== $c"
  python3 lib/card.py "$c"
done
