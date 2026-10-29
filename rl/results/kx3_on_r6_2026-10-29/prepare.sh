#!/bin/bash
# DRAFT (Oct 29; not run; coordinator-076 changes applied). prepare.sh [BASE]: the R6 kx3 replay check's branch and folder, before its
# lane (runbook step 13). Run it in WSL after the R6 night job (night_r6.sh) has ended, on the coordinator's word:
#   bash /home/dacz8976/relplan/kxr6_prepare.sh [BASE]   (a CR-stripped copy of this file: see NOTES.md)
# BASE: origin/main once main has moved to the adopted engine (runbook step 12; the default). Fallback: S (affe56e8), which the
# coordinator allows if there is no review 45 min after sending. Either must carry S's engine/ tree: the script records
# `git rev-parse BASE:engine` next to `git rev-parse affe56e8:engine` and refuses if they differ.
# It:
#   1. checks the night job's results: strength_K, sc_km3 and sc_kx3 done; both self-check lines equal to the pin texts; the build
#      record (program, its sha256, engine ref K, engine tree K:engine, harness c4f7da21, jobs 2). It checks that K is on origin.
#   2. checks the base: S's engine/ tree; the harness and prereg sources as at S; the 14 deck files with the development run's sha256;
#      the development run as at S; no check folder yet.
#   3. reuses the worktree /home/dacz8976/r5_w (coordinator-076). It must be clean (no change, no untracked file); its branch and commit
#      are recorded, then `git switch -c laptop/kx3-replay-r6-2026-10-29 BASE` there. No new checkout, no sparse checkout, no config
#      change. Nothing here or in the lane removes or force-cleans the worktree.
#   4. puts the drafts in place, fills the placeholders from kx_r4/strength.build.json and r6night/sc_*.out, runs
#      make_replay_configs.py (light Python), checks the configs and the scripts' syntax.
#   5. commits the folder; Guardrail A (public repo): no path of a commit to be pushed may contain exam, judge or transcript
#      (case-insensitive; "examples" is fine). Pushes the branch (origin must then have the commit). Installs the lane's copy in
#      ~/pincand_work/kxr6/.
#   6. prints what the coordinator must review and the command that arms the lane. It never starts the lane.
set -eu
S=affe56e88985e2997a66beb85efaca0c487617bd
K=e3ddc0149bb9d35fda1becbb17ab5f71d9461609
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
BASE_ARG=${1:-${KXR_BASE:-origin/main}}
SRC=${KXR_SRC:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/relplan/r6/kxr}
REPO=/home/dacz8976/pincand
W=/home/dacz8976/pincand_work; NJ=$W/r6night; L=$W/kxr6
WT=${KXR_WT:-/home/dacz8976/r5_w}
BR=laptop/kx3-replay-r6-2026-10-29
D=rl/results/kx3_on_r6_2026-10-29
DEV=rl/results/strength_2026-10-03_kx3_dev
P=/home/dacz8976/kx_r4/strength
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
export PYTHONDONTWRITEBYTECODE=1
die() { echo "STOP: $*"; exit 1; }
say() { echo "== $*"; }
# Guardrail A (coordinator-076, public repository): every commit that a push would send (not on any origin ref) is checked; a path
# with exam / judge / transcript (any case; "examples" allowed) refuses the push. Paths from `git show --name-only` (the --stat list
# without its abbreviation).
guard_a() {
  local c hits
  for c in $(git -C "$1" rev-list HEAD --not --remotes=origin); do
    hits=$(git -C "$1" show --name-only --format= $c | grep -iP 'exam(?!ples)|judge|transcript' || true)
    [ -z "$hits" ] || { echo "Guardrail A: commit ${c:0:8} touches: $(echo "$hits" | head -n 5 | tr '\n' ' ')"; return 1; }
  done
  echo "Guardrail A: $(git -C "$1" rev-list HEAD --not --remotes=origin | wc -l) commit(s) to push, no exam/judge/transcript path"
}

say "1. the night job, the program and K"
[ -e $NJ/night.end ] && [ ! -e $W/pgids/night_r6.pgid ] || die "the R6 night job has not ended ($NJ/night.end)"
for m in strength_K sc_km3 sc_kx3; do [ -e $NJ/$m.done ] && [ ! -e $NJ/$m.FAILED ] || die "night job: $m not done"; done
[ "$(cat $NJ/sc_km3.out)" = "$SC_KM3" ] || die "sc_km3.out is not the pin text: a STOP for the coordinator and Dustin"
[ "$(cat $NJ/sc_kx3.out)" = "$SC_KX3" ] || die "sc_kx3.out is not the pin text: a STOP for the coordinator and Dustin"
echo "night markers: $(cd $NJ && ls *.done *.FAILED 2>/dev/null | tr '\n' ' ')"
echo "lane S verdict: $(cat $NJ/lane_S.verdict 2>/dev/null || echo none)"
PSHA=$(sha256sum $P | cut -d' ' -f1)
ETREE_K=$(git -C $REPO rev-parse $K:engine)
VALS=$(python3 -I - $P "$PSHA" $K "$ETREE_K" $HARN <<'EOF'
import hashlib, json, sys
p, psha, k, t, h = sys.argv[1:]
raw = open(p + '.build.json', 'rb').read()
r = json.loads(raw)
want = dict(program=p, program_sha256=psha, engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2', schema=1)
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
if bad:
    sys.exit('build record: %r' % bad)
print(r['engine_tree_archived'], r['built_at'], hashlib.sha256(raw).hexdigest())
EOF
) || die "the build record does not fit (above)"
read -r ETREE BUILT_AT BREC_SHA <<< "$VALS"
SECS=$(cut -d' ' -f2 $NJ/sc_kx3.rc 2>/dev/null || echo "?")
echo "program $P sha256 $PSHA; engine tree $ETREE; built $BUILT_AT; build record sha256 $BREC_SHA; kx3 self-check ${SECS} s"
$G -C $REPO fetch -q origin
KON=$(git -C $REPO branch -r --contains $K | tr -d ' ' | tr '\n' ' ')
[ -n "$KON" ] || die "K ${K:0:8} is on no origin branch (coordinator-076: K is pushed with the record branch before this step)"
echo "K ${K:0:8} on origin, in: $KON"

say "2. the base"
BASE=$(git -C $REPO rev-parse "$BASE_ARG^{commit}")
BASE_ENGINE=$(git -C $REPO rev-parse $BASE:engine); S_ENGINE=$(git -C $REPO rev-parse $S:engine)
echo "base $BASE_ARG = $BASE; $BASE_ARG:engine $BASE_ENGINE; affe56e8:engine $S_ENGINE"
[ "$BASE_ENGINE" = "$S_ENGINE" ] || die "the base's engine/ is not S's: has main moved to the adopted engine (step 12)? Fallback, on the coordinator's 45-minute rule: pass $S"
if [ "$BASE" = "$S" ]; then BASE_LABEL="S itself, laptop/r6-release-2026-10-29, the fallback base"; else BASE_LABEL="${KXR_BASE_LABEL:-$BASE_ARG after the engine adoption}"; fi
for f in rl/strength/src rl/strength/Cargo.toml rl/strength/strength_prereg.py rl/strength/split_collect.py rl/strength/decks.json \
         rl/strength/groups.json rl/strength/heldout.json rl/strength/intended_lines.json $DEV; do
  [ "$(git -C $REPO rev-parse $BASE:$f)" = "$(git -C $REPO rev-parse $S:$f)" ] || die "$f differs between the base and S"
done
git -C $REPO cat-file -e $BASE:$D 2>/dev/null && die "$D already exists on the base"
python3 -I - $REPO $BASE $DEV <<'EOF' || die "a deck file differs from the development run's"
import hashlib, json, subprocess, sys
repo, base, dev = sys.argv[1:]
g = lambda *a: subprocess.run(['git', '-C', repo, *a], capture_output=True, check=True).stdout
m = json.loads(g('show', f'{base}:{dev}/manifest.json'))
bad = [x['path'] for x in m['decks'] + m['opponents'] if hashlib.sha256(g('show', f"{base}:{x['path']}")).hexdigest() != x['sha256']]
print('deck files equal to the development run\'s:', len(m['decks']) + len(m['opponents']) - len(bad), 'of', len(m['decks']) + len(m['opponents']), bad)
sys.exit(1 if bad else 0)
EOF
[ "$BASE" = "$S" ] && echo "NOTE: fallback base S. slowpin_main.py later diffs merge-base(main, check)..check, so main must contain S before the re-pin (runbook step 15)."
git -C $REPO show-ref --verify -q refs/heads/$BR && die "branch $BR exists locally"
git -C $REPO ls-remote --exit-code origin refs/heads/$BR >/dev/null 2>&1 && die "branch $BR exists on origin"
[ -e $L ] && die "$L exists (the lane's state folder must start empty)"
g=$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); echo "C: free ${g} GiB"
[ "$g" -ge 15 ] || die "C: below 15 GiB"

say "3. the worktree $WT (reused; never removed or force-cleaned)"
[ -d $WT ] || die "no worktree $WT"
[ "$(cd $WT && realpath "$(git rev-parse --git-common-dir)")" = "$(realpath $REPO/.git)" ] || die "$WT is not a worktree of $REPO"
[ -z "$(git -C $WT status --porcelain --untracked-files=all)" ] || die "$WT is not clean (git status --porcelain --untracked-files=all): nothing is switched"
mkdir -p $L
WT_BEFORE="$(git -C $WT rev-parse --abbrev-ref HEAD) $(git -C $WT rev-parse HEAD)"
echo "$WT before the switch: $WT_BEFORE (recorded in $L/WT_BEFORE)"
echo "$(date -u +%FT%TZ) $WT $WT_BEFORE" > $L/WT_BEFORE
git -C $WT switch -q -c $BR $BASE
cd $WT
[ "$(git rev-parse HEAD)" = "$BASE" ] && [ "$(git rev-parse --abbrev-ref HEAD)" = "$BR" ] && [ -z "$(git status --porcelain --untracked-files=all)" ] \
  || die "the worktree is not clean on $BR at the base after the switch"
for f in rl/strength/strength_prereg.py rl/strength/split_collect.py rl/strength/decks.json $DEV/games.jsonl $DEV/manifest.json $DEV/config.json \
         decks/screen/opponents/t-altaria.txt decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt; do [ -s $f ] || die "missing $f in the worktree"; done

say "4. the folder"
mkdir -p $D
for f in SPEC.md rows.json REACH.json make_replay_configs.py compare_dev.py lane_kxr_r6.sh prepare.sh; do tr -d '\r' < $SRC/$f > $D/$f; done
[ "$(git hash-object $D/compare_dev.py)" = "$(git rev-parse $S:rl/results/kx3_on_engine_2026-10-21/compare_dev.py)" ] || die "compare_dev.py is not Oct 21's"
python3 -I - $D "$PSHA" "$ETREE" "$BUILT_AT" "$BREC_SHA" "$(cat $NJ/sc_km3.out)" "$(cat $NJ/sc_kx3.out)" "$SECS" "$BASE" "$BASE_LABEL" "$BASE_ENGINE" <<'EOF'
import sys
d, psha, etree, built, brec, km3, kx3, secs, base, label, bengine = sys.argv[1:]
vals = {'PROGRAM_SHA': psha, 'ENGINE_TREE': etree, 'BUILT_AT': built, 'BUILD_RECORD_SHA': brec, 'SC_KM3_MEASURED': km3,
        'SC_KX3_MEASURED': kx3, 'SC_KX3_SECS': secs, 'BASE_COMMIT': base, 'BASE_LABEL': label, 'BASE_ENGINE': bengine}
for f in ('SPEC.md', 'make_replay_configs.py', 'lane_kxr_r6.sh'):
    p = f'{d}/{f}'
    t = open(p, encoding='utf-8').read()
    for k, v in vals.items():
        t = t.replace('@@' + k + '@@', v)
    open(p, 'w', encoding='utf-8', newline='\n').write(t)
    print('filled', p)
EOF
AT='@'; left=$(grep -n "${AT}${AT}" $D/SPEC.md $D/make_replay_configs.py $D/lane_kxr_r6.sh || true)
[ -z "$left" ] || die "placeholders left: $left"
out=$(python3 -I $D/make_replay_configs.py)
echo "$out"
echo "$out" | grep -qx "seeds: all 404 keys get the development run's seed" || die "make_replay_configs.py: not 404 seeded keys"
python3 -I - $D "$PSHA" <<'EOF' || die "configs"
import json, sys
d, psha = sys.argv[1:]
for s, want in {'a': (3, 8, 2, 24400000000), 'b': (3, 8, 2, 24440000000), 'c': (1, 1, 5, 24420070000)}.items():
    c = json.load(open(f'{d}/configs/config_replay_{s}.json'))
    got = (len(c['decks']), len(c['opponents']), c['deals'], c['seed_base'])
    print(s, c['name'], got, c['program'], c['program_sha256'][:12], c['stage'])
    assert got == want and c['program_sha256'] == psha and c['program'] == '/home/dacz8976/kx_r4/strength' and c['stage'] == 'dev', s
EOF
bash -n $D/lane_kxr_r6.sh || die "lane_kxr_r6.sh: syntax"
for f in make_replay_configs.py compare_dev.py; do python3 -I -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' $D/$f || die "$f: syntax"; done
python3 -I -c 'import json, sys; [json.load(open(p)) for p in sys.argv[1:]]' $D/rows.json $D/REACH.json || die "json"

say "5. commit, Guardrail A, push"
$G add $D
other=$(git diff --cached --name-only | grep -v "^$D/" || true); [ -z "$other" ] || die "staged outside $D: $other"
$G commit -q -m "The slow report's R6 re-pin check: spec, rows, reach, configs and scripts (before any game)

Program /home/dacz8976/kx_r4/strength ${PSHA:0:12} (K ${K:0:8}: S ${S:0:8} + kx3's six files); self-checks equal to the pin's.
No row named (SPEC.md section 3): any changed game is a stop.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
guard_a $WT || die "Guardrail A: not pushed (the commit stays local on $BR)"
git push -q origin $BR
[ "$(git ls-remote origin refs/heads/$BR | cut -f1)" = "$(git rev-parse HEAD)" ] || die "origin does not have $(git rev-parse --short HEAD)"
cp $D/lane_kxr_r6.sh $L/lane_kxr_r6.sh
cmp -s $L/lane_kxr_r6.sh $D/lane_kxr_r6.sh || die "the lane's copy"

say "6. for the coordinator's review (nothing has been started)"
echo "commit $(git rev-parse HEAD) on $BR in $WT (base $BASE: $BASE_LABEL; engine/ $BASE_ENGINE = affe56e8's), pushed"
echo "$WT was on: $WT_BEFORE (to go back after the check: git -C $WT switch <that branch>; never a forced clean)"
git show --stat --format='%H %s' HEAD | cat
echo "-- SPEC.md section 1 as filled:"; sed -n '/^## 1\./,/^## 2\./p' $D/SPEC.md
echo "-- review: SPEC.md sections 3 and 4 (no named row; the stop rule), REACH.json (changes R1-R10, incidental X1-X2, gaps),"
echo "   configs/*.json (program, sha256, engine text, seeds), lane_kxr_r6.sh (guards; KXR_UNTIL_EPOCH unset = no cutoff;"
echo "   KXR_REQUIRE_LANE_S=1; Guardrail A and a checked push before any game), make_replay_configs.py v Oct 21's:"
git show $S:rl/results/kx3_on_engine_2026-10-21/make_replay_configs.py > /home/dacz8976/relplan/kxr6_mrc_oct21.py
diff -u /home/dacz8976/relplan/kxr6_mrc_oct21.py $D/make_replay_configs.py || true
echo "-- to arm the lane after the review:"
echo "   tmux new-session -d -s kxr6 \"setsid -w bash $L/lane_kxr_r6.sh\""
echo "   (optional cutoff: tmux new-session -d -s kxr6 \"env KXR_UNTIL_EPOCH=<epoch s> setsid -w bash $L/lane_kxr_r6.sh\")"
echo "   pause: kill -STOP -- -\$(cat $W/pgids/lane_kxr_r6.pgid)   resume: kill -CONT -- -\$(cat $W/pgids/lane_kxr_r6.pgid)"
echo "   log: $L/lane_kxr_r6.log"
