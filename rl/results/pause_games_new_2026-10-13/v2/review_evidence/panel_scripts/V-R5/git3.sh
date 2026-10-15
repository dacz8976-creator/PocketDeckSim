cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
echo "=== from_state"
git grep -n -A25 'pub fn from_state' cd20a97a -- engine/src/game.rs | cut -c1-200
echo "=== energy.rs 90-120"
git show cd20a97a:engine/src/state/energy.rs | sed -n '85,120p'
echo "=== apply_action refresh contexts"
for L in 1298 1381 1402 1533 1722; do
  echo "--- line $L"
  git show cd20a97a:engine/src/actions/apply_action.rs | awk -v l=$L 'NR>=l-25 && NR<=l+2 && /fn |refresh_hp/ {print NR": "$0}'
done
echo "--- helpers"
for L in 1177 1259; do
  echo "--- line $L"
  git show cd20a97a:engine/src/actions/apply_action_helpers.rs | awk -v l=$L 'NR>=l-40 && NR<=l+2 && /fn |refresh_hp/ {print NR": "$0}'
done
echo "--- attack"
for L in 1937 6815; do
  echo "--- line $L"
  git show cd20a97a:engine/src/actions/apply_attack_action.rs | awk -v l=$L 'NR>=l-40 && NR<=l+2 && /fn |refresh_hp/ {print NR": "$0}'
done
echo "=== is_starting_plains_active"
git grep -n -A8 'fn is_starting_plains_active' cd20a97a -- engine/src | cut -c1-200
echo "=== end turn / turn start refresh?"
git grep -n -E 'fn end_turn|fn advance_turn|fn start_turn' cd20a97a -- engine/src | cut -c1-200 | head
