#!/bin/bash
set -euo pipefail
U=https://github.com/bcollazo/deckgym-core.git
cd /home/dacz8976/pincand
if ! git remote | grep -qx upstream; then
  git remote add upstream "$U"
fi
# fetch-only: pushing to upstream is disabled at the remote level
git remote set-url --push upstream "DISABLED--never-push-to-upstream"
git config remote.upstream.tagOpt --no-tags
nice -n 19 git fetch --quiet upstream main
echo "== remotes"; git remote -v
echo "== upstream/main"; git log -1 --format='%H %cI %s' upstream/main
echo "== push test (must fail)"; if git push --dry-run upstream HEAD:refs/heads/x 2>&1 | head -n 2; then :; fi

W=/home/dacz8976/upstream_watch
if [ ! -d "$W/.git" ]; then
  nice -n 19 git clone --quiet --no-tags "$U" "$W"
fi
cd "$W"
git remote set-url --push origin "DISABLED--never-push-to-upstream"
nice -n 19 git fetch --quiet origin
echo "== watch clone"; git log -1 --format='%H %cI %s' origin/main
echo "== last 12 commits touching database.json"; git log -12 --format='%h %cI %s' origin/main -- database.json
echo "== open PR refs for #429-ish? (issues are not refs; list recent branches)"; git ls-remote --heads origin | tail -n 15
