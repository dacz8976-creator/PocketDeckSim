#!/bin/bash
# r8_push.sh v2 (coordinator-154 §3): Guardrail A's content grep takes the never-open exclusion array and starts at the
# last pushed tip (CBASE); names-only checks still cover BASE..TIP. Push to origin only (never upstream, never main).
#   r8_push2.sh scan|push TIP CBASE [BR] [BASE]
set -u
P=/home/dacz8976/pincand; W=/home/dacz8976/r6v_scratch
MODE=${1:-scan}; TIP=${2:-}; CBASE=${3:-}; BR=${4:-laptop/r8-catchup-2026-10-29}; BASE=${5:-ebc97535}
O=/home/dacz8976/relplan/r8/cc/push; mkdir -p $O; TAG=$(echo $BR | tr '/' '_')
X=(':(exclude,icase)*judge*' ':(exclude,icase)*frozen*' ':(exclude,icase)*transcript*' ':(exclude,icase)*run3*' ':(exclude,icase)*weekly_review*' ':(exclude,icase)*battle_log_packets*' ':(exclude,icase)*answers*' ':(exclude,icase)*exam[!p]*' ':(exclude,icase)*exam')
export GIT_TERMINAL_PROMPT=0 GIT_NO_LAZY_FETCH=1
die() { echo "PUSH STOP: $*"; exit 1; }
[ -n "$TIP" ] && [ -n "$CBASE" ] || die "give TIP and CBASE"
if [ $BR = laptop/r8-catchup-2026-10-29 ]; then
  [ "$(git -C $W rev-parse --abbrev-ref HEAD)" = $BR ] || die "worktree not on $BR"
  [ -z "$(git -C $W status --porcelain)" ] || die "worktree not clean"
fi
[ "$(git -C $P rev-parse refs/heads/$BR)" = "$(git -C $P rev-parse $TIP)" ] || die "the branch is not at $TIP"
TIP=$(git -C $P rev-parse $TIP); CBASE=$(git -C $P rev-parse $CBASE)
[ "$(git -C $P remote get-url --push upstream)" = DISABLED--never-push-to-upstream ] || die "upstream push is not disabled"
git -C $P merge-base --is-ancestor $BASE $TIP || die "$BASE is not an ancestor"
git -C $P merge-base --is-ancestor $CBASE $TIP || die "$CBASE is not an ancestor"
[ -n "$(git -C $P branch -r --contains $CBASE)" ] || die "$CBASE is not on origin"
{
echo "== branch $BR; names range $BASE..$TIP: $(git -C $P rev-list --count $BASE..$TIP) commits; content range ${CBASE:0:8}..${TIP:0:8}: $(git -C $P rev-list --count $CBASE..$TIP) commits; $(git -C $P diff --shortstat $CBASE $TIP)"
echo "== commits the push adds beyond origin's refs (local view): $(git -C $P rev-list $TIP --not --remotes=origin | wc -l)"
echo "== binary files in the content range"; git -C $P diff --numstat $CBASE $TIP -- . "${X[@]}" | awk '$1=="-"{print "BINARY", $3}'
echo "== paths in the content range (names)"; git -C $P diff --name-only $CBASE $TIP | sed 's#^#  #' | head -n 60
echo "== Guardrail A: messages and paths ($CBASE..TIP) (private-exam|exam(?!ples)|judge|transcript)"
{ git -C $P log --format='%H%n%B' $CBASE..$TIP; git -C $P diff --name-only $CBASE $TIP; } \
  | grep -a -inP 'private-exam|exam(?!ples)|judge|transcript' | head -n 40 || true
echo "== Guardrail A: added content ($CBASE..TIP, never-open paths excluded by pathspec)"
git -C $P diff $CBASE $TIP --text -- . "${X[@]}" | grep -a '^+' | grep -a -inP 'private-exam|/exam/|exam_v[0-9]|exam-v[0-9]|transcripts?/|/judge/|judge_harness|sk-ant-|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{20}|ghp_[A-Za-z0-9]{30,}|github_pat_|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key\s*=|VERTEX_API_KEY|GOOGLE_API_KEY|GEMINI_API_KEY' | head -n 40 || true
echo "== per-deal / private / never-open names in paths ($BASE..TIP)"
git -C $P diff --name-only $BASE $TIP | grep -a -i -E 'arch_splits|battle_log|battlelogs|battle[ _]logs|\.mov$|camera.roll|weekly_review|frozen|run3|judge|transcript|answers' || echo "(none)"
} > $O/scan_$TAG.txt 2>&1
cat $O/scan_$TAG.txt
PIN="TIP $TIP CBASE $CBASE SCAN $(sha256sum < $O/scan_$TAG.txt | cut -c1-64)"
if [ "$MODE" != push ]; then echo "$PIN" > $O/push_pin_$TAG.txt; echo "pinned: $PIN"; echo "SCAN ONLY (no push)"; exit 0; fi
[ "$(cat $O/push_pin_$TAG.txt 2>/dev/null)" = "$PIN" ] || die "the tip or the scan output differ from the pinned scan"
before=$(timeout 120 git -C $P ls-remote origin refs/heads/$BR | cut -f1); echo "origin before: ${before:-(no such branch)}"
[ -z "$before" ] || git -C $P merge-base --is-ancestor $before $TIP || die "origin's branch is not an ancestor of the tip"
timeout 600 git -C $P push --no-follow-tags origin "$TIP:refs/heads/$BR"; rc=$?
echo "push rc=$rc"
after=$(timeout 120 git -C $P ls-remote origin refs/heads/$BR | cut -f1); echo "origin after: $after"
[ $rc = 0 ] || die "push failed"
[ "$after" = $TIP ] || die "origin does not show the tip"
echo "origin main: $(timeout 120 git -C $P ls-remote origin refs/heads/main | cut -f1) (unchanged by this push)"
echo "PUSH DONE: $BR = $TIP"
