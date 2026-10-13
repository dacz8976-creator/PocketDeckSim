V=/home/dacz8976/pgd_vr/all
R='/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
ls -la "$V" | head -40
echo ---
head -3 "$V/KW261006_020518000.txt"
echo ---
cmp "$V/positions_all.json" "$R/positions_all.json" && echo SAME_POSITIONS
for f in "$V"/KW*.txt; do
  b=$(basename "$f")
  cmp -s "$f" "$R/decks/$b" && echo "same $b" || echo "DIFF $b"
done
