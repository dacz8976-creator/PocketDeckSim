#!/bin/bash
# The slow report's R6 re-pin check (rl/results/kx3_on_r6_2026-10-29/SPEC.md), the lane: Oct 21's lane_kxr.sh adapted
# (rl/results/kx3_on_engine_2026-10-21/lane_kxr.sh; coordinator-076 changes applied). prepare.sh fills the placeholders (PSHA, ETREE),
# commits this file and installs a copy as ~/pincand_work/kxr6/lane_kxr_r6.sh; the lane refuses to run with a placeholder left or if
# its copy is not the committed file.
# It starts when the R6 night job (night_r6.sh) has ended. No time window by default: Dustin released the laptop for all of Oct 29
# (via the coordinator). KXR_UNTIL_EPOCH (epoch seconds; unset by default) is an optional cutoff: no phase and no new game starts after
# it, and running the lane again resumes. nice 19, ionice -c3; the programs' environment scrubbed of KX_*, PDL_*, DECKGYM_*, JEV_*,
# PG_*; TMPDIR on disk; C: >= 15 GiB free before the run starts. The worktree is /home/dacz8976/r5_w (reused, on BR); the lane never
# removes, resets or force-cleans it.
# Pause for Dustin: kill -STOP -- -$(cat ~/pincand_work/pgids/lane_kxr_r6.pgid); resume with -CONT.
# Start (setsid under tmux, so a STOP of the group holds):
#   tmux new-session -d -s kxr6 "setsid -w bash /home/dacz8976/pincand_work/kxr6/lane_kxr_r6.sh"
#   0. guards: the night job ended, its strength build (the build record) and both self-checks passed; the program's sha256; K on
#      origin; the worktree on BR, clean, its HEAD on origin; the folder's files in place, no placeholder left; C: free.
#   1. reg: the three registrations (strength_prereg.py; each replays both self-checks on the program), in parallel. Each manifest:
#      self-checks equal to the pin texts and run by strength_prereg.py, the program and its sha256, the 14 files' sha256 equal to the
#      development run's, the planned size, the repository commit. Then commit them, Guardrail A, push, and check that origin has the
#      commit: no game before that.
#   2. play: replay_b (threads 3) and replay_a (threads 2) in parallel, then replay_c (threads 2); every game played.
#   3. compare: compare_dev.py on all three -> COMPARE_DEV.txt (exit status recorded; 0 = no game changed, as rows.json names none).
#   4. record (KXR_COMMIT_RESULTS=1, the default): COMPARE_DEV.txt and LANE_RECORD.txt into the folder; the games, the comparison and
#      the record committed, Guardrail A, pushed. The reading (READING.md) is not the lane's: it is written after, by the session.
# A STOP (SPEC.md section 4: a changed game, a differing self-check or file, a missing or unreadable game, another program) goes to the
# coordinator and Dustin (coordinator-076). The lane only writes it clearly: a "STOP" line in its log, $L/STOP.txt, and the first line
# of LANE_RECORD.txt (in the folder and committed when the games were played; in $L otherwise). The session tells them.
set -u
W=/home/dacz8976/pincand_work
L=${KXR_STATE:-$W/kxr6}                       # the lane's state (markers, logs); never Oct 21's $W/kxr
NJ=$W/r6night                                 # the R6 night job's state
WT=${KXR_WT:-/home/dacz8976/r5_w}             # reused worktree (coordinator-076), switched to BR by prepare.sh
BR=${KXR_BRANCH:-laptop/kx3-replay-r6-2026-10-29}
D=rl/results/kx3_on_r6_2026-10-29
DEV=rl/results/strength_2026-10-03_kx3_dev
P=/home/dacz8976/kx_r4/strength
PSHA=23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378
KREF=e3ddc0149bb9d35fda1becbb17ab5f71d9461609
SREF=affe56e88985e2997a66beb85efaca0c487617bd
ETREE=cd970db60aa5df7e9db9d7479e88f87190dab2c3
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
UNTIL=${KXR_UNTIL_EPOCH:-}                    # unset: no cutoff
REQ_S=${KXR_REQUIRE_LANE_S:-1}                # 1: the night's lane on S must have passed (r6night/lane_S.done)
COMMIT_RESULTS=${KXR_COMMIT_RESULTS:-1}
REG_MIN=${KXR_REG_MIN:-140}                   # with a cutoff: minutes the registrations need (2 h 08 min on Oct 21-22)
MIN_GIB=15
T=/home/dacz8976/relplan/tmp_kxr6             # TMPDIR on disk (WSL /tmp is RAM); removed at the end (never the worktree)
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
LOG=$L/lane_kxr_r6.log
mkdir -p $L $W/pgids $T
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_kxr_r6.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
mark() { date -u +%FT%TZ > "$L/$1.done"; }
finish() { log "lane_kxr_r6 end: $1"; rm -rf "$T"; rm -f $W/pgids/lane_kxr_r6.pgid; date -u +%FT%TZ > $L/lane_kxr_r6.end; exit "${2:-0}"; }
fail() { echo "$(date -u +%FT%TZ) $2" > "$L/$1.FAILED"; log "$1 FAILED: $2"; finish "$1 failed" 1; }
write_record() {  # LANE_RECORD.txt into $1; its first line says STOP when $L/STOP.txt exists
  { if [ -e $L/STOP.txt ]; then echo "STOP (SPEC.md section 4; for the coordinator and Dustin): $(cat $L/STOP.txt)"; echo; fi
    echo "The lane's record (copied from $L on $(date -u +%FT%TZ))."; echo; echo "== lane_kxr_r6.log"; cat $LOG; echo
    for s in a b c; do
      echo "== reg_$s.rc $(cat $L/reg_$s.rc 2>/dev/null)  run_$s.rc $(cat $L/run_$s.rc 2>/dev/null)"
      echo "-- reg_$s.log (last 4 lines)"; tail -n 4 $L/reg_$s.log 2>/dev/null
      echo "-- run_$s.log (last 3 lines)"; tail -n 3 $L/run_$s.log 2>/dev/null; echo
    done
    echo "== the program"; sha256sum $P; echo "== its build record"; sha256sum $P.build.json
    echo "== compare_dev.py exit status: $(cat $L/compare.rc 2>/dev/null || echo 'not run')"; } > "$1/LANE_RECORD.txt"
}
stop() {  # a STOP of SPEC.md section 4 before the comparison: written into the log, STOP.txt and $L/LANE_RECORD.txt; then the lane ends
  echo "$(date -u +%FT%TZ) $2" > $L/STOP.txt
  log "STOP (SPEC.md section 4; for the coordinator and Dustin, the session tells them): $2"
  write_record $L
  fail "$1" "STOP: $2"
}
open_() { [ -z "$UNTIL" ] || [ "$(date +%s)" -lt "$UNTIL" ]; }
mins_left() { echo $(( (UNTIL - $(date +%s)) / 60 )); }
free_gib() { echo $(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); }
pushed() { [ "$(git ls-remote origin "refs/heads/$BR" 2>/dev/null | cut -f1)" = "$(git rev-parse HEAD)" ]; }
# Guardrail A (coordinator-076, public repository): every commit a push would send (not on any origin ref); a path with exam / judge /
# transcript (any case; "examples" allowed) refuses the push. Paths from `git show --name-only` (the --stat list, unabbreviated).
guard_a() {
  local c hits
  for c in $(git rev-list HEAD --not --remotes=origin); do
    hits=$(git show --name-only --format= $c | grep -iP 'exam(?!ples)|judge|transcript' || true)
    [ -z "$hits" ] || { log "Guardrail A: commit ${c:0:8} touches: $(echo "$hits" | head -n 5 | tr '\n' ' ')"; return 1; }
  done
}
push_checked() {  # Guardrail A, then push (up to 3 tries); origin must then have HEAD
  guard_a || return 2
  local i; for i in 1 2 3; do git push -q origin "$BR" >> $LOG 2>&1 && pushed && return 0; log "push try $i failed"; sleep 60; done; return 1; }
k_on_origin() { git ls-remote origin 2>/dev/null | cut -f1 | grep -qx $KREF && return 0
                git fetch -q origin 2>/dev/null; [ -n "$(git branch -r --contains $KREF 2>/dev/null)" ]; }
games() { python3 -I -c 'import sys; print(sum(1 for l in open(sys.argv[1]) if l.strip().endswith("}")))' "$1" 2>/dev/null || echo 0; }

export TMPDIR=$T PYTHONDONTWRITEBYTECODE=1   # no __pycache__ in the worktree (it must stay clean for a resume)
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)'); do unset "$v"; done
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
NICE="nice -n 19 ionice -c3"
rm -f $L/lane_kxr_r6.end
case "$UNTIL" in '') ;; *[!0-9]*) fail lane "KXR_UNTIL_EPOCH is not epoch seconds";; esac
log "lane_kxr_r6 armed (pgid $(cat $W/pgids/lane_kxr_r6.pgid)); cutoff: ${UNTIL:-none}"

# 0. the night job first: it must have ended (night.end written, its pgid file removed), and no cargo/rustc may still run
said=0
while [ ! -e $NJ/night.end ] || [ -e $W/pgids/night_r6.pgid ] || pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; do
  open_ || finish "cutoff reached while waiting for the night job"
  [ $said = 1 ] || { log "waiting for the R6 night job to end ($NJ/night.end)"; said=1; }
  sleep 60
done
log "night job ended: $(cat $NJ/night.end)"
open_ || finish "cutoff reached"
[ -e $L/record.done ] && finish "already done (record.done)"
[ -e $L/STOP.txt ] && finish "a STOP is recorded ($L/STOP.txt): the lane does not go on after a STOP" 1

# 0. guards
[ "$P" != /home/dacz8976/kx_r3/strength ] || fail lane "the program is the pinned one"
for m in strength_K sc_km3 sc_kx3; do [ -e $NJ/$m.done ] && [ ! -e $NJ/$m.FAILED ] || fail lane "night job: $m not done"; done
[ "$(cat $NJ/sc_km3.out)" = "$SC_KM3" ] || stop lane "the night job's km3 self-check is not the pin text: $(cat $NJ/sc_km3.out)"
[ "$(cat $NJ/sc_kx3.out)" = "$SC_KX3" ] || stop lane "the night job's kx3 self-check is not the pin text: $(cat $NJ/sc_kx3.out)"
if [ "$REQ_S" = 1 ]; then [ -e $NJ/lane_S.done ] || fail lane "night job: lane_S not PASS ($(cat $NJ/lane_S.verdict 2>/dev/null)); set KXR_REQUIRE_LANE_S=0 only on the coordinator's word"; fi
log "night markers: $(cd $NJ && ls *.done *.FAILED 2>/dev/null | tr '\n' ' ')"
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
[ "$(git rev-parse HEAD:engine 2>/dev/null)" = "$(git rev-parse $SREF:engine)" ] || fail lane "the branch's engine/ is not S's"
k_on_origin || fail lane "K ${KREF:0:8} is not on origin (coordinator-076: pushed with the record branch first)"
dirty=$(git status --porcelain --untracked-files=all | grep -v -E "^\?\? $D/replay_[abc]/" || true)   # a resumed run's untracked games are allowed
[ -z "$dirty" ] || fail lane "worktree not clean (nothing is cleaned by the lane): $(echo "$dirty" | head -n 3 | tr '\n' ' ')"
pushed || fail lane "HEAD $(git rev-parse --short HEAD) is not on origin/$BR (commit and push the spec first)"
for f in SPEC.md rows.json REACH.json make_replay_configs.py compare_dev.py lane_kxr_r6.sh configs/config_replay_a.json configs/config_replay_b.json configs/config_replay_c.json; do
  [ -s $D/$f ] || fail lane "missing $D/$f"; done
cmp -s "$0" $D/lane_kxr_r6.sh || fail lane "this script ($0) is not the committed $D/lane_kxr_r6.sh"
AT='@'   # the placeholder mark is two of these; spelled this way so that this line does not match itself
left=$(grep -l "${AT}${AT}" $D/SPEC.md $D/lane_kxr_r6.sh $D/configs/*.json $D/make_replay_configs.py || true)
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
log "lane_kxr_r6 start: $(git rev-parse --short HEAD) on $BR in $WT; program $P ${PSHA:0:12}"

# 1. registrations
if [ ! -e $L/reg.done ]; then
  if [ -n "$UNTIL" ] && [ "$(mins_left)" -lt "$REG_MIN" ]; then finish "cutoff: $(mins_left) min left, the registrations need $REG_MIN"; fi
  git rev-parse HEAD > $L/SPEC_COMMIT
  for s in a b c; do   # before anything starts: an unfinished registration (manifest.json without manifest.sha256) is not resumed
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
  $G commit -q -m "The slow report's R6 re-pin check: the three registrations (before any game; self-checks equal the pin's)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || fail reg "commit failed"
  git rev-parse HEAD > $L/REG_COMMIT
  push_checked; rc=$?
  [ $rc = 2 ] && fail reg "Guardrail A refused the push: committed locally ($(git rev-parse --short HEAD)), no game played"
  [ $rc = 0 ] || fail reg "push of the registrations failed: committed locally ($(git rev-parse --short HEAD)), no game played"
  mark reg; log "reg done and pushed: $(git rev-parse --short HEAD)"
else
  [ "$(git rev-parse HEAD)" = "$(cat $L/REG_COMMIT)" ] || fail lane "HEAD is not the registrations' commit $(cut -c1-8 $L/REG_COMMIT)"
fi

# 2. play (with a cutoff, each run gets --stop-after-min: it starts no new game after it, and a rerun of the lane resumes)
run() {
  local extra=
  if [ -n "$UNTIL" ]; then local m=$(mins_left); [ "$m" -ge 1 ] || { echo 0 > $L/run_$1.rc; return; }; extra="--stop-after-min $m"; fi
  [ "$(sha256sum $P | cut -d' ' -f1)" = "$PSHA" ] || { echo 97 > $L/run_$1.rc; return; }
  env $SCRUB $NICE $P run --manifest $D/replay_$1/manifest.json --out $D/replay_$1 --threads $2 $extra > $L/run_$1.log 2>&1; echo $? > $L/run_$1.rc
}
if [ ! -e $L/play.done ]; then
  log "play: b (threads 3) and a (threads 2), then c"
  run b 3 &
  pb=$!
  run a 2
  log "play a: rc $(cat $L/run_a.rc); $(games $D/replay_a/games.jsonl) of 192"
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

# 3. compare
python3 -I -B $D/compare_dev.py $D/replay_a $D/replay_b $D/replay_c > $L/COMPARE_DEV.txt 2>&1
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
  $G commit -q -m "The slow report's R6 re-pin check: the games and the comparison ($verdict)

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
