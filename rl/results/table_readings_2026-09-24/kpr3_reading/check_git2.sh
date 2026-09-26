#!/usr/bin/env bash
# Second reader, read-only: where the "tests only" commits' engine lines sit in value_functions.rs.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
F=engine/src/players/value_functions.rs
echo "== first line of the test module at 53638a7 and e09fb46"
for c in 1981bb4 53638a7 14c7d9b e09fb46; do echo "$c: $(git show $c:$F | grep -n '#\[cfg(test)\]' | head -3 | tr '\n' ' ') lines $(git show $c:$F | wc -l)"; done
echo "== hunk headers 1981bb4..53638a7"
git diff -U0 1981bb4 53638a7 -- $F | grep '^@@'
echo "== hunk headers 14c7d9b..e09fb46 (e09fb46's parent chain from 14c7d9b; engine only)"
git diff -U0 14c7d9b e09fb46 -- $F | grep '^@@'
echo "== removed lines 14c7d9b..e09fb46"
git diff -U0 14c7d9b e09fb46 -- $F | grep '^-[^-]'
echo "== hunk headers 53638a7..14c7d9b (amendment 6's code)"
git diff -U0 53638a7 14c7d9b -- $F | grep '^@@'
git diff --numstat 53638a7 14c7d9b -- engine/
