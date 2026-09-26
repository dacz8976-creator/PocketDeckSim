#!/usr/bin/env bash
# Read-only: what changed in engine/ between the identity commit (53638a7) and the table commit (e09fb46).
set -u
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
cd "$REPO" || { echo "cannot cd to repo"; exit 1; }
echo "=== 53638a7..14c7d9b engine/ (amendment 6) ==="
git diff --stat 53638a7 14c7d9b -- engine/ | cat
echo
echo "=== 14c7d9b..e09fb46 engine/ (tests only?) ==="
git diff --stat 14c7d9b e09fb46 -- engine/ | cat
echo
echo "=== non-test hunks in 14c7d9b (lines outside mod tests / kpr_feature_tests) ==="
git diff 53638a7 14c7d9b -- engine/src/players/value_functions.rs | grep -n -E '^@@' | head -20
echo
echo "=== 858b6fe (kp3 table build) .. 53638a7 engine/ stat: what else changed in the engine since kp3's table ==="
git diff --stat 858b6fe 53638a7 -- engine/ | tail -15
echo
echo "=== is kp3's table build 858b6fe an ancestor of e09fb46? ==="
git merge-base --is-ancestor 858b6fe e09fb46 && echo "yes 858b6fe is an ancestor of e09fb46" || echo "NO"
echo
echo "=== main-7fc6ccb (official engine) vs e09fb46 engine/ stat (tail) ==="
git diff --stat 7fc6ccb e09fb46 -- engine/ | tail -8
echo
echo "=== effect_ability_mechanic_map.rs: names near the attach mechanics ==="
git show e09fb46:engine/src/actions/effect_ability_mechanic_map.rs | grep -n -B8 -E 'AttachEnergyFromZoneToActiveTypedPokemon|AttachEnergyFromZoneToYourTypedPokemon|AttachEnergyFromZoneToSelf \{|AttachEnergyFromZoneToSelfAndDamage|AttachEnergyFromDiscardToSelfAndDamage|AttachEnergyFromDiscardToActiveTypedFromBench' | grep -E 'name|title|"|Attach' | head -60
