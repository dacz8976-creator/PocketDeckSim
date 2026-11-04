#!/bin/bash
# mk_k8.sh LANE_COMMIT OUTDIR: K8 = kx3 on R8, for the Lane N kx3 smoke (coordinator-148 §2.4). A LOCAL branch
# laptop/kx3-on-r8-2026-11-04 made with a private index (no checkout, no worktree, no merge commit of a working tree); never
# pushed; main and R8's branch are never touched. Exit 0 = K8 made (OUTDIR/K8_COMMIT); exit 3 = players/mod.rs conflicts
# (the kx3 smoke stops, the rest of Lane N goes on; OUTDIR/mod_rs.conflict.txt); any other exit = stop the kx3 smoke, report.
# PROVENANCE: built on R6's mk_ks.sh (rl/results/dual_type_seam_2026-10-23/r6_release/tools/mk_ks.sh, sha256
# 0afaf393708f4bdb1a181bb6167c5fde9f1dcdf2f06c5f1108340dc5692f00bb, TOOLS.txt:8), which refuses R8 by itself: it exits when an
# overlay file changed on the base since 4d488449 (mk_ks.sh:18-20), and R8 changes engine/src/players/mod.rs. CHANGES:
#   1. kx3's files are those of e3ddc014 (= R6's K; its six engine blobs are d513e37b's, checked here: kx3's own decision code
#      byte-identical to d513e37b's), laid on the LANE commit instead of S.
#   2. players/mod.rs, the one file both sides change, is a 3-way merge (git merge-file; base affe56e8's, ours = the lane's,
#      theirs = e3ddc014's). Checked both ways: the merge minus R8's change is e3ddc014's file, and the merge minus kx3's change
#      is the lane's file. A conflict is exit 3, unless K8_UNION_OK=1 (to be set only on the coordinator's word): then the
#      union resolution is taken only if both sides are pure line additions and the result is exactly base + R8's added lines
#      + kx3's added lines (checked); its record says "union".
#   3. K8 v the lane = exactly the six kx3 paths; rl/strength is the lane's; the harness source hash is recorded (as build.sh
#      computes it: src/*.rs then Cargo.toml).
#   4. Branch laptop/kx3-on-r8-2026-11-04 (not -f: an existing branch is reused only if its tree is this K8's tree, else exit 5).
#   5. Parents: the lane commit and e3ddc014 (as mk_ks.sh: kx3's commit and the base).
set -eu
L=$(git -C /home/dacz8976/pincand rev-parse "${1:?usage: mk_k8.sh LANE_COMMIT OUTDIR}^{commit}")
OUTD=${2:?usage: mk_k8.sh LANE_COMMIT OUTDIR}
mkdir -p "$OUTD"
cd /home/dacz8976/pincand
KX=e3ddc0149bb9d35fda1becbb17ab5f71d9461609
D513=d513e37b
BASE=affe56e88985e2997a66beb85efaca0c487617bd
BR=laptop/kx3-on-r8-2026-11-04
M=engine/src/players/mod.rs
if git ls-remote --exit-code origin "refs/heads/$BR" >/dev/null 2>&1; then echo "$BR is on origin already: refusing"; exit 6; fi
FILES=$(git diff --name-only $BASE $KX -- engine)
echo "kx3's engine files (affe56e8 -> e3ddc014):"; git diff --name-status $BASE $KX -- engine
n=$(echo "$FILES" | wc -l); [ "$n" = 6 ] || { echo "want 6 files, got $n"; exit 4; }
same=0; for f in $FILES; do [ "$(git rev-parse -q --verify $D513:$f || echo none)" = "$(git rev-parse $KX:$f)" ] && same=$((same + 1)); done
echo "of the six, equal to d513e37b's blob: $same"; [ "$same" = 6 ] || { echo "kx3's files are not d513e37b's"; exit 4; }
for f in $FILES; do
  [ "$f" = "$M" ] && continue
  git rev-parse -q --verify "$L:$f" >/dev/null && { echo "$f exists on the lane commit: an overlay would replace it"; exit 4; }
done
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
git show $BASE:$M > $TMP/base.rs; git show $L:$M > $TMP/ours.rs; git show $KX:$M > $TMP/theirs.rs
MODE=plain
if ! git merge-file -p $TMP/ours.rs $TMP/base.rs $TMP/theirs.rs > $TMP/merged.rs; then
  cp $TMP/merged.rs "$OUTD/mod_rs.conflict.txt"
  echo "players/mod.rs: the 3-way merge conflicts ($(grep -c '^<<<<<<<' $TMP/merged.rs) hunk(s)); see $OUTD/mod_rs.conflict.txt"
  sed -n '/^<<<<<<</,/^>>>>>>>/p' $TMP/merged.rs
  [ "${K8_UNION_OK:-}" = 1 ] || { echo "conflict: the kx3 smoke stops (coordinator-148 §2.4); K8_UNION_OK=1 only on the coordinator's word"; exit 3; }
  git merge-file --union -p $TMP/ours.rs $TMP/base.rs $TMP/theirs.rs > $TMP/merged.rs || true
  MODE=union
  # name the hunk (coordinator-149): the enclosing enum/struct/fn and each side's first non-comment line
  C="$OUTD/mod_rs.conflict.txt"
  H_IN=$(awk '/^<<<<<<</{print last; exit} /^(pub )?(enum|struct|fn|impl) /{last=$0}' "$C" | sed 's/ *{.*//')
  H_OURS=$(sed -n '/^<<<<<<</,/^=======/p' "$C" | grep -v '^<<<<<<<\|^=======\|^ *///' | sed 's/^ *//' | head -n 1 | cut -c1-90)
  H_THEIRS=$(sed -n '/^=======/,/^>>>>>>>/p' "$C" | grep -v '^>>>>>>>\|^=======\|^ *///' | sed 's/^ *//' | head -n 1 | cut -c1-90)
  HUNKMSG="The union hunk (the only conflict): in '$H_IN', at the same place, the lane adds '$H_OURS' and kx3 adds
'$H_THEIRS' (each with its doc comment); the union keeps both, the lane's first."
fi
python3 -I - $TMP/base.rs $TMP/ours.rs $TMP/theirs.rs $TMP/merged.rs $MODE <<'EOF' || exit 4
import difflib, sys
base, ours, theirs, merged = (open(p).read().splitlines() for p in sys.argv[1:5])
mode = sys.argv[5]
def adds(a, b):
    """(added lines, removed lines) from a to b"""
    plus, minus = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op in ('replace', 'delete'):
            minus += a[i1:i2]
        if op in ('replace', 'insert'):
            plus += b[j1:j2]
    return plus, minus
r8p, r8m = adds(base, ours); kxp, kxm = adds(base, theirs)
mo_p, mo_m = adds(ours, merged); mt_p, mt_m = adds(theirs, merged)
print(f'mod.rs: R8 +{len(r8p)} -{len(r8m)}, kx3 +{len(kxp)} -{len(kxm)} (v affe56e8); merged v lane +{len(mo_p)} -{len(mo_m)}, merged v e3ddc014 +{len(mt_p)} -{len(mt_m)}; mode {mode}')
ok = sorted(mo_p) == sorted(kxp) and sorted(mo_m) == sorted(kxm) and sorted(mt_p) == sorted(r8p) and sorted(mt_m) == sorted(r8m)
if mode == 'union':
    ok = ok and not r8m and not kxm
print('mod.rs check: merged = lane + exactly kx3\'s change, = e3ddc014 + exactly R8\'s change:', 'OK' if ok else 'BAD')
sys.exit(0 if ok else 1)
EOF
export GIT_INDEX_FILE=$TMP/index
git read-tree $L
for f in $FILES; do
  if [ "$f" = "$M" ]; then
    b=$(git hash-object -w --no-filters $TMP/merged.rs); md=$(git ls-tree $L -- "$f" | cut -d' ' -f1); git update-index --add --cacheinfo "$md,$b,$f"
  else
    set -- $(git ls-tree $KX -- "$f"); git update-index --add --cacheinfo "$1,$3,$f"
  fi
done
TREE=$(git write-tree); unset GIT_INDEX_FILE
d=$(git diff --name-only $L $TREE | wc -l); [ "$d" = 6 ] || { echo "lane v K8 differs in $d files, want 6"; exit 4; }
for f in $FILES; do [ "$f" = "$M" ] || [ "$(git rev-parse $TREE:$f)" = "$(git rev-parse $KX:$f)" ] || { echo "$f is not e3ddc014's"; exit 4; }; done
[ "$(git rev-parse $TREE:rl/strength)" = "$(git rev-parse $L:rl/strength)" ] || { echo "rl/strength differs from the lane's"; exit 4; }
HARN=$( { git show $TREE:rl/strength/src/ext.rs; git show $TREE:rl/strength/src/main.rs; git show $TREE:rl/strength/Cargo.toml; } | sha256sum | cut -c1-64)
[ "$(git ls-tree --name-only $TREE rl/strength/src/ | tr '\n' ' ')" = "rl/strength/src/ext.rs rl/strength/src/main.rs " ] || { echo "rl/strength/src is not ext.rs + main.rs: the harness hash above is not build.sh's"; exit 4; }
if K=$(git rev-parse -q --verify "refs/heads/$BR"); then
  [ "$(git rev-parse $K^{tree})" = "$TREE" ] || { echo "$BR exists with another tree ($K): refusing to move it"; exit 5; }
  echo "$BR exists with this tree: reused"
else
  K=$(git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree $TREE -p $L -p $KX -F - <<EOF
kx3 on R8's engine (Lane N kx3 smoke): kx3's files laid onto ${L:0:8}

Built with a private index from the lane commit's tree plus kx3's files of e3ddc014 (laptop/kx3-on-r6-2026-10-29; its six
engine blobs are d513e37b's): five added files as they are, and engine/src/players/mod.rs by a 3-way merge ($MODE; base
affe56e8, ours = the lane's, theirs = e3ddc014's), checked to be the lane's file plus exactly kx3's change. K8 v the lane:
exactly those six paths. rl/strength is the lane's (harness ${HARN:0:8}). engine/ tree $(git rev-parse $TREE:engine | cut -c1-12).
${HUNKMSG:-The 3-way merge had no conflict.}
Local branch only, for the Lane N kx3 smoke (coordinator-148 §2.4); pushed only after Dustin's yes, with Guardrail A first.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)
  git branch $BR $K
fi
git diff --name-status $L $K | cat
{ echo "K8 $K"; echo "tree $TREE"; echo "engine_tree $(git rev-parse $K:engine)"; echo "lane $L"; echo "mod_rs_merge $MODE";
  echo "harness_source_sha256 $HARN"; echo "kx3_blobs_equal_d513e37b 6"; if [ $MODE = union ]; then echo "union_hunk in '$H_IN': lane '$H_OURS' + kx3 '$H_THEIRS'"; fi; } > "$OUTD/K8_RECORD.txt"
echo "$K" > "$OUTD/K8_COMMIT"
cat "$OUTD/K8_RECORD.txt"
echo "K8=$K"
