#!/bin/bash
# prepare.sh [BASE]: the R8 kx3 replay check's branch and folder, before its lane (plan 113 §7.2-7.3; R6's prepare.sh adapted).
#   bash /home/dacz8976/relplan/r8/kr8/prepare.sh [BASE]   (a CR-stripped copy of this file)
# BASE: the R8 branch after the adoption commit (113 §7.2: main does not carry R8 until the end; the default is
# origin/laptop/r8-catchup-2026-10-29). It must carry S8's engine/ tree: the script refuses otherwise.
# It:
#   1. checks the switch's results: K8's build record (program, sha256, engine ref K8, engine tree K8:engine, harness c4f7da21, jobs 2);
#      both self-check texts equal to the pin's (km3 on strength_L in Lane N, kx3 on strength_K8 in the switch); K8 on origin.
#   2. checks the base: S8's engine/ tree; the harness and prereg files as R6's check used them (affe56e8); the 14 deck files with the
#      development run's sha256; compare_dev.py = Oct 21's; no check folder yet.
#   3. reuses the worktree /home/dacz8976/r5_w (as R6 did): it must be clean; its branch and commit are recorded, then
#      `git switch -c laptop/kx3-replay-r8-2026-11-04 BASE` there. Nothing here or in the lane removes or force-cleans it.
#   4. puts the files in place, fills the placeholders, runs make_replay_configs.py, checks the configs and the scripts' syntax.
#   5. commits the folder; Guardrail A (paths, message and added content with the never-open exclusion array); pushes; installs the
#      lane's copy in ~/pincand_work/kxr8/.
#   6. prints what the coordinator reviews and the command that arms the lane. It never starts the lane.
set -eu
S8=543dad0007a345128ec95e9c2698699c8b5493ce
R6E=affe56e88985e2997a66beb85efaca0c487617bd          # R6's release: the harness files must be as R6's check used them
K=b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
BASE_ARG=${1:-${KXR_BASE:-origin/laptop/r8-catchup-2026-10-29}}
SRC=${KXR_SRC:-/home/dacz8976/relplan/r8/kr8}
REPO=/home/dacz8976/pincand
W=/home/dacz8976/pincand_work; LNN=$W/RR_R8_48dec4f5/night; SW3=$W/RR_R8_543dad00/sw3; L=$W/kxr8
WT=${KXR_WT:-/home/dacz8976/r5_w}
BR=laptop/kx3-replay-r8-2026-11-04
D=rl/results/kx3_on_r8_2026-11-04
DEV=rl/results/strength_2026-10-03_kx3_dev
P=$W/RR_R8_48dec4f5/strength/K8/strength
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
X=(':(exclude,icase)*judge*' ':(exclude,icase)*frozen*' ':(exclude,icase)*transcript*' ':(exclude,icase)*run3*' ':(exclude,icase)*weekly_review*' ':(exclude,icase)*battle_log_packets*' ':(exclude,icase)*answers*' ':(exclude,icase)*exam[!p]*' ':(exclude,icase)*exam')
export PYTHONDONTWRITEBYTECODE=1
die() { echo "STOP: $*"; exit 1; }
say() { echo "== $*"; }
guard_a() {
  local c hits
  for c in $(git -C "$1" rev-list HEAD --not --remotes=origin); do
    hits=$(git -C "$1" show --name-only --format='%B' $c | grep -iP 'private-exam|exam(?!ples)|judge|transcript' || true)
    [ -z "$hits" ] || { echo "Guardrail A: commit ${c:0:8} names: $(echo "$hits" | head -n 5 | tr '\n' ' ')"; return 1; }
    hits=$(git -C "$1" show --format= --text $c -- . "${X[@]}" | grep -a '^+' | grep -a -iP 'private-exam|/exam/|exam_v[0-9]|exam-v[0-9]|transcripts?/|/judge/|judge_harness|sk-ant-|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20}|ghp_[A-Za-z0-9]{30,}|github_pat_|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key\s*=|VERTEX_API_KEY|GOOGLE_API_KEY|GEMINI_API_KEY' | head -n 5 || true)
    [ -z "$hits" ] || { echo "Guardrail A: commit ${c:0:8} adds content that matches (not printed; read the commit)"; return 1; }
  done
  echo "Guardrail A: $(git -C "$1" rev-list HEAD --not --remotes=origin | wc -l) commit(s) to push; paths, message and added content clean"
}
[ -e /home/dacz8976/credit_work/PAUSE ] && die "PAUSE present: Dustin needs the laptop"

say "1. the switch's results, the program and K8"
[ "$(cat $LNN/sc_km3.out)" = "$SC_KM3" ] || die "Lane N's sc_km3.out is not the pin text: a STOP for the coordinator and Dustin"
[ "$(cat $SW3/sc_kx3.out)" = "$SC_KX3" ] || die "the switch's sc_kx3.out is not the pin text: a STOP for the coordinator and Dustin"
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
SECS=$(cut -d' ' -f2 $SW3/sc_kx3.rc)
echo "program $P sha256 $PSHA; engine tree $ETREE; built $BUILT_AT; build record sha256 $BREC_SHA; kx3 self-check ${SECS} s"
$G -C $REPO fetch -q origin
[ "$(git -C $REPO ls-remote origin refs/heads/laptop/kx3-on-r8-2026-11-04 | cut -f1)" = $K ] || die "K8 ${K:0:8} is not on origin"
echo "K8 ${K:0:8} on origin (laptop/kx3-on-r8-2026-11-04)"

say "2. the base"
BASE=$(git -C $REPO rev-parse "$BASE_ARG^{commit}")
BASE_ENGINE=$(git -C $REPO rev-parse $BASE:engine); S_ENGINE=$(git -C $REPO rev-parse $S8:engine)
echo "base $BASE_ARG = $BASE; base:engine $BASE_ENGINE; 543dad00:engine $S_ENGINE"
[ "$BASE_ENGINE" = "$S_ENGINE" ] || die "the base's engine/ is not S8's"
git -C $REPO merge-base --is-ancestor $S8 $BASE || die "S8 is not an ancestor of the base"
BASE_LABEL="${KXR_BASE_LABEL:-the R8 branch after the adoption commit (113 §7.2: main does not carry R8 until the end)}"
for f in rl/strength/src rl/strength/Cargo.toml rl/strength/strength_prereg.py rl/strength/split_collect.py rl/strength/decks.json \
         rl/strength/groups.json rl/strength/heldout.json rl/strength/intended_lines.json $DEV; do
  [ "$(git -C $REPO rev-parse $BASE:$f)" = "$(git -C $REPO rev-parse $R6E:$f)" ] || die "$f differs between the base and R6's release (affe56e8)"
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
git -C $REPO show-ref --verify -q refs/heads/$BR && die "branch $BR exists locally"
git -C $REPO ls-remote --exit-code origin refs/heads/$BR >/dev/null 2>&1 && die "branch $BR exists on origin"
[ -e $L ] && die "$L exists (the lane's state folder must start empty)"
g=$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); echo "C: free ${g} GiB"
[ "$g" -ge 15 ] || die "C: below 15 GiB"

say "3. the worktree $WT (reused; never removed or force-cleaned)"
[ -d $WT ] || die "no worktree $WT"
[ "$(cd $WT && realpath "$(git rev-parse --git-common-dir)")" = "$(realpath $REPO/.git)" ] || die "$WT is not a worktree of $REPO"
[ -z "$(git -C $WT status --porcelain --untracked-files=all)" ] || die "$WT is not clean: nothing is switched"
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
for f in SPEC.md rows.json REACH.json make_replay_configs.py lane_kxr_r8.sh prepare.sh; do tr -d '\r' < $SRC/$f > $D/$f; done
git show $BASE:rl/results/kx3_on_engine_2026-10-21/compare_dev.py > $D/compare_dev.py
[ "$(git hash-object $D/compare_dev.py)" = "$(git rev-parse $BASE:rl/results/kx3_on_r6_2026-10-29/compare_dev.py)" ] || die "compare_dev.py is not Oct 21's and R6's"
python3 -I - $D "$PSHA" "$ETREE" "$BUILT_AT" "$BREC_SHA" "$(cat $LNN/sc_km3.out)" "$(cat $SW3/sc_kx3.out)" "$SECS" "$BASE" "$BASE_LABEL" "$BASE_ENGINE" <<'EOF'
import sys
d, psha, etree, built, brec, km3, kx3, secs, base, label, bengine = sys.argv[1:]
vals = {'PROGRAM_SHA': psha, 'ENGINE_TREE': etree, 'BUILT_AT': built, 'BUILD_RECORD_SHA': brec, 'SC_KM3_MEASURED': km3,
        'SC_KX3_MEASURED': kx3, 'SC_KX3_SECS': secs, 'BASE_COMMIT': base, 'BASE_LABEL': label, 'BASE_ENGINE': bengine}
for f in ('SPEC.md', 'make_replay_configs.py', 'lane_kxr_r8.sh'):
    p = f'{d}/{f}'
    t = open(p, encoding='utf-8').read()
    for k, v in vals.items():
        t = t.replace('@@' + k + '@@', v)
    open(p, 'w', encoding='utf-8', newline='\n').write(t)
    print('filled', p)
EOF
AT='@'; left=$(grep -n "${AT}${AT}" $D/SPEC.md $D/make_replay_configs.py $D/lane_kxr_r8.sh || true)
[ -z "$left" ] || die "placeholders left: $left"
out=$(python3 -I $D/make_replay_configs.py)
echo "$out"
echo "$out" | grep -qx "seeds: all 404 keys get the development run's seed" || die "make_replay_configs.py: not 404 seeded keys"
python3 -I - $D "$PSHA" $P <<'EOF' || die "configs"
import json, sys
d, psha, p = sys.argv[1:]
for s, want in {'a': (3, 8, 2, 24400000000), 'b': (3, 8, 2, 24440000000), 'c': (1, 1, 5, 24420070000)}.items():
    c = json.load(open(f'{d}/configs/config_replay_{s}.json'))
    got = (len(c['decks']), len(c['opponents']), c['deals'], c['seed_base'])
    print(s, c['name'], got, c['program'], c['program_sha256'][:12], c['stage'])
    assert got == want and c['program_sha256'] == psha and c['program'] == p and c['stage'] == 'dev', s
EOF
bash -n $D/lane_kxr_r8.sh || die "lane_kxr_r8.sh: syntax"
for f in make_replay_configs.py compare_dev.py; do python3 -I -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' $D/$f || die "$f: syntax"; done
python3 -I -c 'import json, sys; [json.load(open(p)) for p in sys.argv[1:]]' $D/rows.json $D/REACH.json || die "json"
[ "$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])))' $D/rows.json)" = "{}" ] || die "rows.json is not {}: a named row goes to the coordinator before the lane"

say "5. commit, Guardrail A, push"
$G add $D
other=$(git diff --cached --name-only | grep -v "^$D/" || true); [ -z "$other" ] || die "staged outside $D: $other"
$G commit -q -m "The slow report's R8 re-pin check: spec, rows, reach, configs and scripts (before any game)

Program $P ${PSHA:0:12} (K8 ${K:0:8}: kx3's six files on R8's engine); self-checks equal to the pin's.
No row named (SPEC.md section 3): any changed game is a stop.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
guard_a $WT || die "Guardrail A: not pushed (the commit stays local on $BR)"
git push -q origin $BR
[ "$(git ls-remote origin refs/heads/$BR | cut -f1)" = "$(git rev-parse HEAD)" ] || die "origin does not have $(git rev-parse --short HEAD)"
cp $D/lane_kxr_r8.sh $L/lane_kxr_r8.sh
cmp -s $L/lane_kxr_r8.sh $D/lane_kxr_r8.sh || die "the lane's copy"

say "6. for the coordinator's review (nothing has been started)"
echo "commit $(git rev-parse HEAD) on $BR in $WT (base $BASE: $BASE_LABEL; engine/ $BASE_ENGINE = S8's), pushed"
echo "$WT was on: $WT_BEFORE (to go back after the check: git -C $WT switch <that branch>; never a forced clean)"
git show --stat --format='%H %s' HEAD | cat
echo "-- to arm the lane after the review:"
echo "   tmux new-session -d -s kxr8 \"setsid -w bash $L/lane_kxr_r8.sh\""
echo "   pause: touch ~/credit_work/PAUSE (no new phase) or kill -STOP -- -\$(cat $W/pgids/lane_kxr_r8.pgid); resume: rm it / kill -CONT"
echo "   log: $L/lane_kxr_r8.log"
