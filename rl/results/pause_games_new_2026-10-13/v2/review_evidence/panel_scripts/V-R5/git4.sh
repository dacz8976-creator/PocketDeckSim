cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
git show cd20a97a:engine/src/actions/apply_action_helpers.rs | sed -n '1160,1185p;1250,1265p'
echo "=== who calls apply_common_action_suffix"
git grep -n 'apply_common_action_suffix\|apply_common_action_prefix' cd20a97a -- engine/src | cut -c1-200
echo "=== check_state_dump.py"
sed -n '1,80p' "rl/results/pause_games_new_2026-10-13/v2/scripts/check_state_dump.py"
echo "=== deck file"
cat "rl/results/pause_games_new_2026-10-13/v2/decks/KW261013_030351000.txt"
