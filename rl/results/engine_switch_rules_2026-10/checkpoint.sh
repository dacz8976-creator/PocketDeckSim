#!/usr/bin/env bash
# The checkpoint commits of sitting1.sh (sourced; it runs nothing by itself). As pin.sh makes the pin commit: the commit
# is built in a PRIVATE index (git read-tree of main, git add of exactly the named paths, git write-tree, git
# commit-tree), so nothing another session staged or edited elsewhere comes along, and main moves to it with git
# update-ref only if main is still where the commit was built (else it is built again on the new main, three tries).
# The shared index is never used to stage or commit. Its one change is pin.sh's own step (pin.sh line 487): the entries
# of exactly the committed paths are set to the new commit's (git reset <commit> -- <paths>), so that no other session's
# commit records them as deleted or reverted and GitHub Desktop shows them unchanged. Nothing else in it is touched.
# That reset and the update-ref are one unit: ckpt_commit runs in a subshell that ignores stop signals, and those two git
# calls run in a process group of their own (setsid), so a stop sent to the run's group (quiet.sh stop, a second TERM)
# cannot fall between them; when main kept moving, the entries are set back to main's, so nothing stays staged.
# The push sends main only as a fast-forward of origin/main (after a fetch), and only when every commit it would send is
# this switch's (CKPT_OURS); the runner never pulls, merges or forces.
#
#   CKPT_OURS (environment): a file of commit ids, one a line: the commits a push may carry. ckpt_commit adds each commit
#       it makes; sitting1.sh adds the ones its start allowed. Unset: no such check (not used by sitting1.sh).
#   ckpt_commit REPO REL WORK MSGFILE PATH...
#       PATHs relative to REPO, each a file under REL/ (no *.part, no .sitting1.* working file). WORK is a private
#       folder for the index. Prints "commit <sha> <files changed>" or "unchanged <main sha>". Returns 1 with the reason
#       on stderr when it cannot commit: the shared index has staged changes in these paths, the working copy is not on
#       main, the commit would touch any other path or delete or retype one, or main kept moving.
#   ckpt_push REPO [SECONDS]
#       Prints "pushed <sha>" or "up to date <sha>". On stderr "not pushed: <why>" and returns 1 when offline (the fetch
#       or the push failed or timed out: try again later), 2 when origin/main has commits main lacks (a person pulls),
#       3 when main carries commits that are not in CKPT_OURS, still there after one more fetch a minute later (another
#       session's unpushed work: not this run's to push). SECONDS limits the fetch (default 300); the push gets three
#       times it.
# Every git call closes fd 9 (sitting1.sh's lock), so no git process holds the run's lock.

CKPT_ID=(-c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com)

ckpt_git_retry() {  # repo git-args...: in a process group of its own (a stop sent to the run's group cannot interrupt
  local repo=$1 i err rc; shift  # it), retried for up to 30 s while another git process holds a lock file
  err=$(mktemp) || return 1
  for i in 1 2 3 4 5 6 7 8 9 10; do
    rc=0; setsid -w git -C "$repo" "$@" 2> "$err" 9>&- || rc=$?
    if [ $rc -eq 0 ]; then rm -f -- "$err"; return 0; fi
    grep -q "\.lock': File exists" "$err" || break
    sleep 3
  done
  cat -- "$err" >&2; rm -f -- "$err"; return "$rc"
}

ckpt_commit() (  # a subshell: the caller's traps and variables are untouched
  trap '' HUP INT TERM   # a stop waits for this to finish; the caller's trap runs when it returns
  local repo=$1 rel=$2 work=$3 msg=$4; shift 4
  local -a paths=("$@")
  local p parent tree ns extra gone x try staged xi="$work/ckpt.index" reset_done=0
  [ ${#paths[@]} -gt 0 ] || { echo "no paths to commit" >&2; return 1; }
  [ -s "$msg" ] || { echo "no commit message ($msg)" >&2; return 1; }
  for p in "${paths[@]}"; do
    case $p in "$rel"/*) ;; *) echo "$p is outside $rel/" >&2; return 1;; esac
    case ${p##*/} in *.part|.sitting1.*|.sitting2.*) echo "$p is a working file, never committed" >&2; return 1;; esac
    [ -f "$repo/$p" ] || { echo "$p is missing" >&2; return 1; }
  done
  staged=$(git -C "$repo" diff --cached --name-only -- "${paths[@]}" 9>&-) || { echo "git diff --cached failed" >&2; return 1; }
  [ -z "$staged" ] || { echo "the shared index has staged changes in these paths (another session?): $(head -n 5 <<< "$staged" | tr '\n' ' ')" >&2; return 1; }
  [ "$(git -C "$repo" symbolic-ref -q HEAD 9>&- || true)" = refs/heads/main ] || { echo "the working copy is not on main" >&2; return 1; }
  for try in 1 2 3; do
    parent=$(git -C "$repo" rev-parse -q --verify refs/heads/main 9>&-) || { echo "no main" >&2; break; }
    rm -f -- "$xi"
    GIT_INDEX_FILE="$xi" git -C "$repo" read-tree "$parent" 9>&- || { echo "git read-tree (private index)" >&2; break; }
    GIT_INDEX_FILE="$xi" git -C "$repo" add -- "${paths[@]}" 9>&- || { echo "git add (private index)" >&2; break; }
    tree=$(GIT_INDEX_FILE="$xi" git -C "$repo" write-tree 9>&-) || { echo "git write-tree (private index)" >&2; break; }
    ns=$(git -C "$repo" diff-tree -r --no-renames --name-status "$parent" "$tree" 9>&-) || { echo "git diff-tree" >&2; break; }
    if [ -z "$ns" ]; then
      rm -f -- "$xi"
      [ $reset_done -eq 0 ] || ckpt_git_retry "$repo" reset -q "$parent" -- "${paths[@]}" 2> /dev/null || true
      echo "unchanged $parent"; return 0
    fi
    extra=$(cut -f2- <<< "$ns" | grep -vxF -f <(printf '%s\n' "${paths[@]}") || true)
    [ -z "$extra" ] || { echo "the commit would also change: $(tr '\n' ' ' <<< "$extra")" >&2; break; }
    gone=$(awk -F'\t' '$1 != "A" && $1 != "M"' <<< "$ns")
    [ -z "$gone" ] || { echo "the commit would delete or retype: $(tr '\n' ';' <<< "$gone")" >&2; break; }
    x=$(git -C "$repo" "${CKPT_ID[@]}" commit-tree "$tree" -p "$parent" -F "$msg" 9>&-) || { echo "git commit-tree" >&2; break; }
    [[ $x =~ ^[0-9a-f]{40}$ ]] || { echo "git commit-tree printed no commit" >&2; break; }
    reset_done=1
    ckpt_git_retry "$repo" reset -q "$x" -- "${paths[@]}" || { echo "setting the committed paths' entries in the shared index failed" >&2; break; }
    if ckpt_git_retry "$repo" update-ref -m "sitting1.sh checkpoint" refs/heads/main "$x" "$parent"; then
      [ -z "${CKPT_OURS:-}" ] || printf '%s\n' "$x" >> "$CKPT_OURS" || echo "(could not add $x to $CKPT_OURS)" >&2
      rm -f -- "$xi"; echo "commit $x $(grep -c . <<< "$ns")"; return 0
    fi
    # main moved since read-tree (another session committed): build the commit again on the new main
    [ "$try" != 3 ] || echo "main kept moving during three tries; nothing committed" >&2
  done
  # Nothing committed. If the shared index's entries were set to a commit main never reached, set them back to main's
  # (best effort), so nothing stays staged there.
  if [ $reset_done -eq 1 ] && parent=$(git -C "$repo" rev-parse -q --verify refs/heads/main 9>&-); then
    ckpt_git_retry "$repo" reset -q "$parent" -- "${paths[@]}" 2> /dev/null \
      || echo "(the committed paths may still be staged in the shared index: git reset -q -- $rel unstages them)" >&2
  fi
  rm -f -- "$xi"
  return 1
)

ckpt_push() {  # repo [seconds]: the fetch's limit (default 300; the push gets three times it)
  local repo=$1 lim=${2:-300} m o c u foreign try wait
  for try in 1 2; do
    m=$(git -C "$repo" rev-parse -q --verify refs/heads/main 9>&-) || { echo "not pushed: no main" >&2; return 1; }
    GIT_TERMINAL_PROMPT=0 timeout -k 30 "$lim" git -C "$repo" fetch -q --no-auto-maintenance origin 9>&- \
      || { echo "not pushed: git fetch origin failed or timed out (offline?)" >&2; return 1; }
    o=$(git -C "$repo" rev-parse -q --verify refs/remotes/origin/main 9>&-) || { echo "not pushed: no origin/main" >&2; return 1; }
    if [ "$o" = "$m" ]; then echo "up to date $m"; return 0; fi
    git -C "$repo" merge-base --is-ancestor "$o" "$m" 9>&- \
      || { echo "not pushed: origin/main ${o:0:7} has commits main ${m:0:7} lacks (the runner never pulls, merges or forces)" >&2; return 2; }
    foreign=""
    if [ -n "${CKPT_OURS:-}" ]; then
      u=$(git -C "$repo" rev-list "$o..$m" 9>&-) || { echo "not pushed: git rev-list origin/main..main failed" >&2; return 1; }
      for c in $u; do grep -qxF "$c" "$CKPT_OURS" 2> /dev/null || foreign+="${c:0:7} "; done
    fi
    [ -n "$foreign" ] || break
    if [ "$try" = 2 ]; then
      echo "not pushed: main carries commits this run did not make, still not on origin a minute later: $foreign(another session's unpushed work, not this run's to push)" >&2
      return 3
    fi
    wait=60; [ "$lim" -ge 60 ] || wait=$lim
    sleep "$wait"   # the other session may be about to push its own commit
  done
  GIT_TERMINAL_PROMPT=0 timeout -k 30 $((lim * 3)) git -C "$repo" push -q origin "$m:refs/heads/main" 9>&- \
    || { echo "not pushed: git push origin failed or timed out (main ${m:0:7}; origin/main ${o:0:7})" >&2; return 1; }
  echo "pushed $m"
}
