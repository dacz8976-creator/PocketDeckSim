#!/bin/bash
# mk_kf.sh F_COMMIT: the committed engine ref for the slow report's re-pin on the FINAL candidate: the frozen kx3 (cd20a97a's
# six engine files) merged off-tree with F_COMMIT (git merge-tree + commit-tree). Local branch only (pushed after the gate).
# The branch laptop/kx3-on-engine-candidate-2026-10-20 was made earlier today on d9d2e704 and never pushed: it is moved.
# Prints K=<sha> on its last line.
set -eu
cd /home/dacz8976/pincand
F=$(git rev-parse "$1^{commit}")
KX=cd20a97a2e76897fae9883389cee4bf7ce5b3d97
BR=laptop/kx3-on-engine-candidate-2026-10-20
if git ls-remote --exit-code origin "refs/heads/$BR" >/dev/null 2>&1; then echo "$BR is on origin already: refusing to move it"; exit 1; fi
TREE=$(git merge-tree --write-tree $F $KX)
echo "merge-tree: $TREE (merge base $(git merge-base $F $KX))"
[ "$(git rev-parse $TREE:engine/src/players)" = "$(git rev-parse d513e37b:engine/src/players)" ] || { echo "players != d513e37b"; exit 1; }
[ "$(git rev-parse $TREE:rl/strength)" = "$(git rev-parse $F:rl/strength)" ] || { echo "rl/strength differs from F"; exit 1; }
n=$(git diff --name-only $F $TREE -- engine | wc -l); [ $n = 6 ] || { git diff --name-status $F $TREE -- engine; echo "want the 6 kx3 files, got $n"; exit 1; }
for f in $(git diff --name-only $F $TREE -- engine); do
  [ "$(git rev-parse $TREE:$f)" = "$(git rev-parse $KX:$f)" ] || { echo "$f is not cd20a97a's"; exit 1; }
done
git diff --name-status $F $TREE -- engine
K=$(git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree $TREE -p $KX -p $F -F - <<EOF
kx3 on the final engine candidate (slow-report re-pin): the frozen kx3 (claude/playout-pilot d513e37b, via laptop/kx3-on-rules2 cd20a97a) merged with ${F:0:8}

Made off-tree with git merge-tree, no conflict (merge base $(git merge-base $F $KX | cut -c1-8)). engine/src/players is d513e37b's byte for
byte; engine/ is ${F:0:8}'s (tree $(git rev-parse $F:engine | cut -c1-12)) plus kx3's 6 files (tree $(git rev-parse $TREE:engine | cut -c1-12)).
rl/strength is ${F:0:8}'s. For rl/strength/build.sh (harness bf9c5d68).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)
git branch -f $BR $K
echo "engine tree $(git rev-parse $K:engine)"
echo "K=$K"
