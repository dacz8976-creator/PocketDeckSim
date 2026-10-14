cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/V-R5"
sha256sum "rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs" | cut -c1-16
git rev-parse cd20a97a:engine
mkdir -p "$OUT/eng"
for f in engine/src/state/played_card.rs engine/src/state/mod.rs engine/src/state/energy.rs; do
  git show "cd20a97a:$f" > "$OUT/eng/$(basename $f)"
done
git ls-tree -r cd20a97a --name-only engine/src | grep -iE 'stadium|hooks|place|apply_trainer|apply_action' | head -30
git grep -n -E 'stadium_hp_bonus|refresh_hp_bonus' cd20a97a -- engine/src | cut -c1-220 | head -80
