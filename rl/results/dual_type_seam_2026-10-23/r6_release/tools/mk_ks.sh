#!/bin/bash
# mk_ks.sh S_COMMIT: the engine ref for the slow report's R6 re-pin. kx3's six engine files (d513e37b's, as pinned in 87a7f340 =
# laptop/kx3-on-engine-candidate-2026-10-20, kx3 on main-4d48844) laid onto S's tree, nothing else (runbook step 7, adapted:
# mk_kf.sh's "players == d513e37b" check cannot hold, since R6 changes five km3 player files on purpose; the check here is
# "K's tree = S's tree + exactly the six kx3 blobs"). Built with a private index, no checkout, no merge. Local branch only.
# Prints K=<sha> on its last line.
set -eu
cd /home/dacz8976/pincand
S=$(git rev-parse "$1^{commit}")
KX=87a7f3404263e1bfe76e8765ba8dd94695e19cfe
BASE=4d4884492aa85496acf9bafdae18b22739f56647
BR=laptop/kx3-on-r6-2026-10-29
if git ls-remote --exit-code origin "refs/heads/$BR" >/dev/null 2>&1; then echo "$BR is on origin already: refusing to move it"; exit 1; fi
FILES=$(git diff --name-only $BASE $KX -- engine)
echo "kx3's engine files (4d488449 -> 87a7f340):"; git diff --name-status $BASE $KX -- engine
n=$(echo "$FILES" | wc -l); [ "$n" = 6 ] || { echo "want 6 files, got $n"; exit 1; }
for f in $FILES; do
  # each must be absent or unchanged on S since 4d488449, so laying kx3's blob on S drops nothing of R6's
  a=$(git rev-parse -q --verify "$BASE:$f" || echo none); b=$(git rev-parse -q --verify "$S:$f" || echo none)
  [ "$a" = "$b" ] || { echo "$f changed on S since 4d488449 ($a -> $b): an overlay would drop it"; exit 1; }
done
IDX=$(mktemp); rm -f $IDX
export GIT_INDEX_FILE=$IDX
git read-tree $S
for f in $FILES; do
  set -- $(git ls-tree $KX -- "$f")   # mode type blob path
  git update-index --add --cacheinfo "$1,$3,$f"
done
TREE=$(git write-tree); unset GIT_INDEX_FILE; rm -f $IDX
d=$(git diff --name-only $S $TREE | wc -l); [ "$d" = 6 ] || { echo "S v K differs in $d files, want 6"; exit 1; }
for f in $FILES; do [ "$(git rev-parse $TREE:$f)" = "$(git rev-parse $KX:$f)" ] || { echo "$f is not 87a7f340's"; exit 1; }; done
same_d513=0; for f in $FILES; do [ "$(git rev-parse -q --verify d513e37b:$f || true)" = "$(git rev-parse $KX:$f)" ] && same_d513=$((same_d513+1)); done
echo "of the six, equal to d513e37b's blob: $same_d513"
[ "$(git rev-parse $TREE:rl/strength)" = "$(git rev-parse $S:rl/strength)" ] || { echo "rl/strength differs from S"; exit 1; }
K=$(git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree $TREE -p $KX -p $S -F - <<EOF
kx3 on R6's engine (slow-report re-pin): kx3's six engine files laid onto ${S:0:8}

Built with a private index from S's tree plus the six blobs that 87a7f340 (laptop/kx3-on-engine-candidate-2026-10-20,
kx3 on main-4d48844) adds or changes under engine/ against 4d488449; no merge. K's tree = S's tree + exactly those six
blobs ($same_d513 of them equal to d513e37b's). The km3 player files are S's (R6 changes five of them on purpose), so the
pilot is "kx3 (d513e37b's files, on main-${S:0:7})" (coordinator-072). engine/ tree $(git rev-parse $TREE:engine | cut -c1-12);
rl/strength is S's (harness c4f7da21, with the card-support refusal). For rl/strength/build.sh.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)
git branch -f $BR $K
git diff --name-status $S $K | cat
echo "engine tree $(git rev-parse $K:engine)"
echo "K=$K"
