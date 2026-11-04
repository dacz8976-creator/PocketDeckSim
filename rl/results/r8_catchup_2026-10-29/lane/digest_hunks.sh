#!/bin/bash
# digest_hunks.sh [LANE_COMMIT]: every hunk under engine/src/players/ and in engine/src/hooks/core.rs between affe56e8 (R6 S,
# main-affe56e) and the lane commit, with the commit(s) of R8 that made it, for coordinator-148 §2.1(c) ("every hunk under
# players/ and hooks/core.rs since affe56e8, each explained"). Read-only git; prints to stdout. The explanations are written
# afterwards from this list. Per hunk: file, hunk header, + / - line counts, and the commits: for added or changed lines,
# `git blame` of the new lines at the lane commit (commits after affe56e8 only); for a pure deletion, `git blame --reverse`
# of the old lines (the last commit that still had them) and the next commit on the path, which removed them.
set -eu
REPO=/home/dacz8976/r6v_scratch
L=$(git -C $REPO rev-parse "${1:-HEAD}^{commit}")
BASE=affe56e88985e2997a66beb85efaca0c487617bd
cd $REPO
echo "hunks under engine/src/players/ and engine/src/hooks/core.rs, ${BASE:0:8}..${L:0:8} (git diff -U0)"
git diff --stat $BASE $L -- engine/src/players engine/src/hooks/core.rs | cat
python3 -I - "$BASE" "$L" <<'EOF'
import re, subprocess, sys
base, lane = sys.argv[1], sys.argv[2]
diff = subprocess.run(['git', 'diff', '-U0', base, lane, '--', 'engine/src/players', 'engine/src/hooks/core.rs'],
                      capture_output=True, text=True, check=True).stdout
since = set(subprocess.run(['git', 'rev-list', f'{base}..{lane}'], capture_output=True, text=True, check=True).stdout.split())
subj = {}
def subject(c):
    if c not in subj:
        subj[c] = subprocess.run(['git', 'log', '-1', '--format=%h %s', c], capture_output=True, text=True).stdout.strip()[:110]
    return subj[c]
def blame(rev_args, path, start, count):
    out = subprocess.run(['git', 'blame', '--porcelain'] + rev_args + ['-L', f'{start},+{count}', '--', path], capture_output=True, text=True)
    return [l.split()[0] for l in out.stdout.splitlines() if re.match(r'^[0-9a-f]{40} \d+ \d+', l)]
path, n, rows = None, 0, []
for line in diff.splitlines():
    if line.startswith('+++ '):
        path = line[6:].strip() if line.startswith('+++ b/') else None
    m =re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)', line)
    if m and path:
        a, b, c, d = int(m[1]), int(m[2] if m[2] is not None else 1), int(m[3]), int(m[4] if m[4] is not None else 1)
        n += 1
        if d > 0:
            cs = [x for x in blame([lane], path, c, d) if x in since]
            how = 'blame of the new lines'
        else:
            last = blame(['--reverse', f'{base}..{lane}'], path, a, b)
            cs = []
            for x in dict.fromkeys(last):
                kids = subprocess.run(['git', 'rev-list', '--ancestry-path', '--reverse', f'{x}..{lane}', '--', path], capture_output=True, text=True).stdout.split()
                cs.append(kids[0] if kids else x)
            how = 'pure deletion: the commit after the last that had the lines'
        uniq = list(dict.fromkeys(cs))
        print(f'\n[{n}] {path} @@ -{a},{b} +{c},{d} @@{m[5]}   (+{d} -{b}; {how})')
        for x in uniq:
            print(f'      {subject(x)}')
        if not uniq:
            print('      (no commit after affe56e8 found: check by hand)')
print(f'\n{n} hunks')
EOF
