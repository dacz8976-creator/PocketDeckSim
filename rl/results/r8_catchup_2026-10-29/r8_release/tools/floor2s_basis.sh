#!/bin/bash
# floor2s_basis.sh   (R8 record; coordinator-151 Q3, the command of coordinator-155 §1)
# Read-only. The floor's reference, ~/pincand_work/floor2S (R6's floor pages on S, Oct 29), checked against the sums R6 committed
# (rl/results/dual_type_seam_2026-10-23/r6_release/logs/floor_recheck_S/outputs.sha256, read from git at 543dad00).
set -u
S=543dad0007a345128ec95e9c2698699c8b5493ce; L=rl/results/dual_type_seam_2026-10-23/r6_release/logs/floor_recheck_S/outputs.sha256
cd /home/dacz8976/pincand_work/floor2S || exit 1
n=$(git -C /home/dacz8976/pincand show $S:$L | wc -l)
out=$(sha256sum -c <(git -C /home/dacz8976/pincand show $S:$L) 2>&1); rc=$?
echo "$out"
ok=$(echo "$out" | grep -c ': OK$')
other=$(find . -type f ! -path './_ref_stripped/*' | wc -l); ref=$(find ./_ref_stripped -type f | wc -l)
echo "sha256sum -c rc=$rc: $ok of $n OK; files in floor2S outside _ref_stripped: $other; in _ref_stripped: $ref"
if [ $rc = 0 ] && [ $ok = $n ] && [ $n = 92 ] && [ $other = 92 ] && [ $ref = 9 ]; then echo "RESULT: floor2S = 92 of 92 committed sums"; exit 0; fi
echo "RESULT: floor2S NOT as committed"; exit 1
