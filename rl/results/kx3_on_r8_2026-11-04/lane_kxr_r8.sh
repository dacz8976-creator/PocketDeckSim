#!/bin/bash
# The slow report's R8 re-pin check (rl/results/kx3_on_r8_2026-11-04/SPEC.md), the lane: R6's lane_kxr_r6.sh
# (rl/results/kx3_on_r6_2026-10-29/) adapted to R8 (plan 113 §7, coordinator-155). prepare.sh commits this file and installs a copy as
# ~/pincand_work/kxr8/lane_kxr_r8.sh; the lane refuses to run with a placeholder left or if its copy is not the committed file.
# Changes from R6's: the program is K8's (b5f15351); no night job to wait for (the switch's checks are in the R8 build record,
# r8_release/, and the lane checks their files); EVERY heavy step under nice 19 + ionice -c3 (coordinator-155: the registrations, the
# games and compare_dev.py); the lane waits while ~/credit_work/PAUSE exists (Dustin needs the laptop); Guardrail A also greps the added
# content (coordinator-154: the never-open exclusion array, from the last pushed tip), not only the paths.
# Pause for Dustin: touch ~/credit_work/PAUSE (the lane starts no new phase), or kill -STOP -- -$(cat ~/pincand_work/pgids/lane_kxr_r8.pgid)
# for an immediate hold; resume with rm / -CONT.
# Start (setsid under tmux, so a STOP of the group holds):
#   tmux new-session -d -s kxr8 "setsid -w bash /home/dacz8976/pincand_work/kxr8/lane_kxr_r8.sh"
#   0. guards: the switch's checks (K8's build record, both self-check texts), the program's sha256, K8 on origin, the worktree on BR,
#      clean, its HEAD on origin, the folder's files in place, no placeholder left, C: free.
#   1. reg: the three registrations (strength_prereg.py; each replays both self-checks on the program), in parallel; checked; committed;
#      Guardrail A; pushed and checked on origin: no game before that.
#   2. play: replay_b (threads 3) and replay_a (threads 2) in parallel, then replay_c (threads 2).
#   3. compare: compare_dev.py on all three -> COMPARE_DEV.txt (0 = no game changed, as rows.json names none).
#   4. record: COMPARE_DEV.txt and LANE_RECORD.txt into the folder; the games, the comparison and the record committed, Guardrail A, pushed.
# A STOP (SPEC.md section 4) goes to the coordinator and Dustin: the lane writes a "STOP" line in its log, $L/STOP.txt, and the first
# line of LANE_RECORD.txt. The session tells them.
set -u
W=/home/dacz8976/pincand_work
L=${KXR_STATE:-$W/kxr8}
WT=${KXR_WT:-/home/dacz8976/r5_w}
BR=${KXR_BRANCH:-laptop/kx3-replay-r8-2026-11-04}
D=rl/results/kx3_on_r8_2026-11-04
DEV=rl/results/strength_2026-10-03_kx3_dev
P=$W/RR_R8_48dec4f5/strength/K8/strength
PSHA=d4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d
KREF=b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0
SREF=543dad0007a345128ec95e9c2698699c8b5493ce
ETREE=f33d2c49baf432d4bd1e407b96a6c243471fa9b6
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
SW3=$W/RR_R8_543dad00/sw3; LNN=$W/RR_R8_48dec4f5/night
UNTIL=${KXR_UNTIL_EPOCH:-}
COMMIT_RESULTS=${KXR_COMMIT_RESULTS:-1}
REG_MIN=${KXR_REG_MIN:-140}
MIN_GIB=15
PAUSE=/home/dacz8976/credit_work/PAUSE
T=/home/dacz8976/relplan/tmp_kxr8
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
X=(':(exclude,icase)*judge*' ':(exclude,icase)*frozen*' ':(exclude,icase)*transcript*' ':(exclude,icase)*run3*' ':(exclude,icase)*weekly_review*' ':(exclude,icase)*battle_log_packets*' ':(exclude,icase)*answers*' ':(exclude,icase)*exam[!p]*' ':(exclude,icase)*exam')
LOG=$L/lane_kxr_r8.log
mkdir -p $L $W/pgids $T
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_kxr_r8.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
mark() { date -u +%FT%TZ > "$L/$1.done"; }
finish() { log "lane_kxr_r8 end: $1"; rm -rf "$T"; rm -f $W/pgids/lane_kxr_r8.pgid; date -u +%FT%TZ > $L/lane_kxr_r8.end; exit "${2:-0}"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$L/$1.FAILED"; log "$1 FAILED: $2"; finish "$1 failed" 1; }
write_record() {
  { if [ -e $L/STOP.txt ]; then echo "STOP (SPEC.md section 4; for the coordinator and Dustin): $(cat $L/STOP.txt)"; echo; fi
    echo "The lane's record (copied from $L on $(date -u +%FT%TZ))."; echo; echo "== lane_kxr_r8.log"; cat $LOG; echo
    for s in a b c; do
      echo "== reg_$s.rc $(cat $L/reg_$s.rc 2>/dev/null)  run_$s.rc $(cat $L/run_$s.rc 2>/dev/null)"
      echo "-- reg_$s.log (last 4 lines)"; tail -n 4 $L/reg_$s.log 2>/dev/null
      echo "-- run_$s.log (last 3 lines)"; tail -n 3 $L/run_$s.log 2>/dev/null; echo
    done
    echo "== the program"; sha256sum $P; echo "== its build record"; sha256sum $P.build.json
    echo "== compare_dev.py exit status: $(cat $L/compare.rc 2>/dev/null || echo 'not run')"; } > "$1/LANE_RECORD.txt"
}
stop() { echo "$(date -u +%FT%TZ) $2" > $L/STOP.txt; log "STOP (SPEC.md section 4; for the coordinator and Dustin, the session tells them): $2"; write_record $L; fail "$1" "STOP: $2"; }
open_() { [ -z "$UNTIL" ] || [ "$(date +%s)" -lt "$UNTIL" ]; }
mins_left() { echo $(( (UNTIL - $(date +%s)) / 60 )); }
free_gib() { echo $(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); }
pushed() { [ "$(git ls-remote origin "refs/heads/$BR" 2>/dev/null | cut -f1)" = "$(git rev-parse HEAD)" ]; }
wait_pause() { local said=0; while [ -e $PAUSE ]; do [ $said = 1 ] || { log "PAUSE present: waiting (Dustin needs the laptop)"; said=1; }; sleep 60; done; [ $said = 0 ] || log "PAUSE gone: going on"; }
# Guardrail A: every commit a push would send (not on any origin ref): its paths and message hold no exam / judge / transcript (any case;
# "examples" allowed), and its added content, never-open paths excluded by pathspec, holds no exam/judge/transcript path or secret.
guard_a() {
  local c hits base
  for c in $(git rev-list HEAD --not --remotes=origin); do
    hits=$( { git show --name-only --format='%B' $c; } | grep -iP 'private-exam|exam(?!ples)|judge|transcript' || true)
    [ -z "$hits" ] || { log "Guardrail A: commit ${c:0:8} names: $(echo "$hits" | head -n 5 | tr '\n' ' ')"; return 1; }
    hits=$(git show --format= --text $c -- . "${X[@]}" | grep -a '^+' | grep -a -iP 'private-exam|/exam/|exam_v[0-9]|exam-v[0-9]|transcripts?/|/judge/|judge_harness|sk-ant-|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20}|ghp_[A-Za-z0-9]{30,}|github_pat_|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key\s*=|VERTEX_API_KEY|GOOGLE_API_KEY|GEMINI_API_KEY' | head -n 5 || true)
    [ -z "$hits" ] || { log "Guardrail A: commit ${c:0:8} adds content that matches (not printed; see the commit)"; return 1; }
  done
}
push_checked() {
  guard_a || return 2
  local i; for i in 1 2 3; do git push -q origin "$BR" >> $LOG 2>&1 && pushed && return 0; log "push try $i failed"; sleep 60; done; return 1; }
k_on_origin() { git ls-remote origin "refs/heads/laptop/kx3-on-r8-2026-11-04" 2>/dev/null | cut -f1 | grep -qx $KREF; }
games() { python3 -I -c 'import sys; print(sum(1 for l in open(sys.argv[1]) if l.strip().endswith("}")))' "$1" 2>/dev/null || echo 0; }

export TMPDIR=$T PYTHONDONTWRITEBYTECODE=1
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
NICE="nice -n 19 ionice -c3"
rm -f $L/lane_kxr_r8.end
case "$UNTIL" in '') ;; *[!0-9]*) fail lane "KXR_UNTIL_EPOCH is not epoch seconds";; esac
log "lane_kxr_r8 armed (pgid $(cat $W/pgids/lane_kxr_r8.pgid)); cutoff: ${UNTIL:-none}"
said=0
while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do
  open_ || finish "cutoff reached while waiting for a cargo build to end"
  [ $said = 1 ] || { log "waiting: a cargo build is running"; said=1; }; sleep 60; done
wait_pause
open_ || finish "cutoff reached"
[ -e $L/record.done ] && finish "already done (record.done)"
[ -e $L/STOP.txt ] && finish "a STOP is recorded ($L/STOP.txt): the lane does not go on after a STOP" 1

# 0. guards
[ "$P" != /home/dacz8976/kx_r4/strength ] || fail lane "the program is the pinned one"
[ "$(cat $LNN/sc_km3.out)" = "$SC_KM3" ] || stop lane "Lane N's km3 self-check is not the pin text: $(cat $LNN/sc_km3.out)"
[ "$(cat $SW3/sc_kx3.out)" = "$SC_KX3" ] || stop lane "the switch's kx3 self-check is not the pin text: $(cat $SW3/sc_kx3.out)"
[ "$(sha256sum $P | cut -d' ' -f1)" = "$PSHA" ] || stop lane "the program's sha256 is not $PSHA"
chk=$(python3 -I - $P "$PSHA" $KREF "$ETREE" $HARN <<'EOF'
import json, sys
p, psha, k, t, h = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(program=p, program_sha256=psha, engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2', schema=1)
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
print('RECORD OK' if not bad else 'RECORD BAD %r' % bad)
EOF
)
[ "$chk" = "RECORD OK" ] || fail lane "build record: $chk"
cd $WT || fail lane "no worktree $WT"
[ "$(git rev-parse --abbrev-ref HEAD)" = "$BR" ] || fail lane "worktree not on $BR"
[ "$(git rev-parse HEAD:engine 2>/dev/null)" = "$(git rev-parse $SREF:engine)" ] || fail lane "the branch's engine/ is not S8's"
k_on_origin || fail lane "K8 ${KREF:0:8} is not on origin"
dirty=$(git status --porcelain --untracked-files=all | grep -v -E "^\?\? $D/replay_[abc]/" || true)
[ -z "$dirty" ] || fail lane "worktree not clean (nothing is cleaned by the lane): $(echo "$dirty" | head -n 3 | tr '\n' ' ')"
pushed || fail lane "HEAD $(git rev-parse --short HEAD) is not on origin/$BR (commit and push the spec first)"
for f in SPEC.md rows.json REACH.json make_replay_configs.py compare_dev.py lane_kxr_r8.sh configs/config_replay_a.json configs/config_replay_b.json configs/config_replay_c.json; do
  [ -s $D/$f ] || fail lane "missing $D/$f"; done
cmp -s "$0" $D/lane_kxr_r8.sh || fail lane "this script ($0) is not the committed $D/lane_kxr_r8.sh"
AT='@'
left=$(grep -l "${AT}${AT}" $D/SPEC.md $D/lane_kxr_r8.sh $D/configs/*.json $D/make_replay_configs.py || true)
[ -z "$left" ] || fail lane "a placeholder is left in: $left"
[ "$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1])))' $D/rows.json)" = "{}" ] || fail lane "rows.json is not {} (the spec names no row)"
cfg=$(python3 -I - $D $P "$PSHA" <<'EOF'
import json, sys
d, p, psha = sys.argv[1:]
want = {'a': (3, 8, 2, 24400000000), 'b': (3, 8, 2, 24440000000), 'c': (1, 1, 5, 24420070000)}
bad = []
for s, (nd, no, deals, sb) in want.items():
    c = json.load(open(f'{d}/configs/config_replay_{s}.json'))
    got = (len(c['decks']), len(c['opponents']), c['deals'], c['seed_base'])
    if got != (nd, no, deals, sb) or c['program'] != p or c['program_sha256'] != psha or c['pilot'] != 'kx3' or c['reference'] != 'km3' or c['stage'] != 'dev':
        bad.append((s, got, c['program'], c['program_sha256'][:12]))
print('CONFIGS OK' if not bad else 'CONFIGS BAD %r' % bad)
EOF
)
[ "$cfg" = "CONFIGS OK" ] || fail lane "configs: $cfg"
g=$(free_gib); log "C: free ${g} GiB"; [ "$g" -ge $MIN_GIB ] || fail lane "C: below $MIN_GIB GiB (${g})"
log "lane_kxr_r8 start: $(git rev-parse --short HEAD) on $BR in $WT; program $P ${PSHA:0:12}"

# 1. registrations
if [ ! -e $L/reg.done ]; then
  if [ -n "$UNTIL" ] && [ "$(mins_left)" -lt "$REG_MIN" ]; then finish "cutoff: $(mins_left) min left, the registrations need $REG_MIN"; fi
  git rev-parse HEAD > $L/SPEC_COMMIT
  for s in a b c; do
    [ -e $D/replay_$s/manifest.json ] && [ ! -e $D/replay_$s/manifest.sha256 ] && fail reg "replay_$s: an unfinished registration: move it aside by hand"
  done
  for s in a b c; do
    [ -e $D/replay_$s/manifest.sha256 ] && { log "reg $s: already registered"; continue; }
    ( env $SCRUB $NICE python3 rl/strength/strength_prereg.py --config $D/configs/config_replay_$s.json --out $D/replay_$s --repo . \
        > $L/reg_$s.log 2>&1; echo $? > $L/reg_$s.rc ) &
  done
  wait
  for s in a b c; do
    [ -e $D/replay_$s/manifest.sha256 ] || fail reg "replay_$s not registered (rc $(cat $L/reg_$s.rc 2>/dev/null); $L/reg_$s.log)"
    got=$(python3 -I - $D/replay_$s/manifest.json $DEV/manifest.json $P "$PSHA" "$(cat $L/SPEC_COMMIT)" "$SC_KM3" "$SC_KX3" $s <<'EOF'
import json, sys
mp, dp, p, psha, commit, km3, kx3, s = sys.argv[1:]
m, dev = json.load(open(mp)), json.load(open(dp))
devfiles = {x['name']: (x['path'], x['sha256']) for x in dev['decks'] + dev['opponents']}
stop, bad = [], []
if m['selfcheck'].get('km3') != km3 or m['selfcheck'].get('kx3') != kx3: stop.append(('self-check differs from the pin text', m['selfcheck']))
if m['program'] != p or m['program_sha256'] != psha: stop.append(('another program', m['program'], m['program_sha256']))
for x in m['decks'] + m['opponents']:
    if devfiles.get(x['name']) != (x['path'], x['sha256']): stop.append(('a file differs from the development run', x['name'], x['sha256'][:12]))
if set(m['selfcheck_source'].values()) != {'run by strength_prereg.py'}: bad.append(('selfcheck_source', m['selfcheck_source']))
if m['repo_commit'] != commit: bad.append(('repo_commit', m['repo_commit']))
if m['planned_games'] != {'a': 192, 'b': 192, 'c': 20}[s]: bad.append(('planned_games', m['planned_games']))
print('STOP %r' % stop if stop else 'BAD %r' % bad if bad else 'OK')
EOF
)
    case "$got" in OK) ;; STOP*) stop reg "replay_$s: ${got#STOP }";; *) fail reg "replay_$s: $got";; esac
  done
  $G add $D/replay_a $D/replay_b $D/replay_c
  other=$(git diff --cached --name-only | grep -v "^$D/" || true)
  [ -z "$other" ] || fail reg "staged files outside $D: $other"
  $G commit -q -m "The slow report's R8 re-pin check: the three registrations (before any game; self-checks equal the pin's)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || fail reg "commit failed"
  git rev-parse HEAD > $L/REG_COMMIT
  push_checked; rc=$?
  [ $rc = 2 ] && fail reg "Guardrail A refused the push: committed locally ($(git rev-parse --short HEAD)), no game played"
  [ $rc = 0 ] || fail reg "push of the registrations failed: committed locally ($(git rev-parse --short HEAD)), no game played"
  mark reg; log "reg done and pushed: $(git rev-parse --short HEAD)"
else
  [ "$(git rev-parse HEAD)" = "$(cat $L/REG_COMMIT)" ] || fail lane "HEAD is not the registrations' commit $(cut -c1-8 $L/REG_COMMIT)"
fi

# 2. play
run() {
  local extra=
  if [ -n "$UNTIL" ]; then local m=$(mins_left); [ "$m" -ge 1 ] || { echo 0 > $L/run_$1.rc; return; }; extra="--stop-after-min $m"; fi
  [ "$(sha256sum $P | cut -d' ' -f1)" = "$PSHA" ] || { echo 97 > $L/run_$1.rc; return; }
  env $SCRUB $NICE $P run --manifest $D/replay_$1/manifest.json --out $D/replay_$1 --threads $2 $extra > $L/run_$1.log 2>&1; echo $? > $L/run_$1.rc
}
if [ ! -e $L/play.done ]; then
  wait_pause
  log "play: b (threads 3) and a (threads 2), then c"
  run b 3 &
  pb=$!
  run a 2
  log "play a: rc $(cat $L/run_a.rc); $(games $D/replay_a/games.jsonl) of 192"
  wait_pause
  run c 2
  log "play c: rc $(cat $L/run_c.rc); $(games $D/replay_c/games.jsonl) of 20"
  wait $pb
  log "play b: rc $(cat $L/run_b.rc); $(games $D/replay_b/games.jsonl) of 192"
  for s in a b c; do
    case "$(cat $L/run_$s.rc)" in 0) ;; 97) stop play "replay_$s: the program's sha256 changed during the lane";;
      *) stop play "replay_$s: the program ended with rc $(cat $L/run_$s.rc) ($L/run_$s.log): games missing or unreadable";; esac
  done
  short=
  for s in a b c; do n=$(games $D/replay_$s/games.jsonl); w=$(case $s in c) echo 20;; *) echo 192;; esac); [ "$n" = "$w" ] || short="$short $s:$n/$w"; done
  if [ -n "$short" ]; then
    open_ && stop play "games missing with no cutoff reached:$short"
    finish "cutoff reached:$short (run the lane again to resume)"
  fi
  mark play
fi

# 3. compare (under nice too: coordinator-155)
$NICE python3 -I -B $D/compare_dev.py $D/replay_a $D/replay_b $D/replay_c > $L/COMPARE_DEV.txt 2>&1
echo $? > $L/compare.rc
log "compare: rc $(cat $L/compare.rc); $(tail -n 1 $L/COMPARE_DEV.txt)"
if [ "$(cat $L/compare.rc)" != 0 ]; then
  echo "$(date -u +%FT%TZ) compare_dev.py rc $(cat $L/compare.rc): $(tail -n 1 $L/COMPARE_DEV.txt) (COMPARE_DEV.txt)" > $L/STOP.txt
  log "STOP (SPEC.md section 4; for the coordinator and Dustin, the session tells them): $(cat $L/STOP.txt)"
fi
mark compare

# 4. record
if [ "$COMMIT_RESULTS" = 1 ] && [ ! -e $L/record.done ]; then
  cp $L/COMPARE_DEV.txt $D/COMPARE_DEV.txt
  write_record $D
  $G add $D/replay_a $D/replay_b $D/replay_c $D/COMPARE_DEV.txt $D/LANE_RECORD.txt
  other=$(git diff --cached --name-only | grep -v "^$D/" || true)
  [ -z "$other" ] || fail record "staged files outside $D: $other"
  verdict=$([ -e $L/STOP.txt ] && echo "STOP, for the coordinator and Dustin: see COMPARE_DEV.txt" || echo "no game changed")
  $G commit -q -m "The slow report's R8 re-pin check: the games and the comparison ($verdict)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || fail record "commit failed"
  push_checked; rc=$?
  case $rc in 0) log "record committed and pushed: $(git rev-parse --short HEAD)";;
    2) log "record committed locally ($(git rev-parse --short HEAD)); Guardrail A refused the push";;
    *) log "record committed locally ($(git rev-parse --short HEAD)); push failed: push it by hand";; esac
  mark record
else
  write_record $L
fi
[ -e $L/STOP.txt ] && finish "done with a STOP (compare rc $(cat $L/compare.rc)): for the coordinator and Dustin" 1
finish "done (compare rc $(cat $L/compare.rc))"
