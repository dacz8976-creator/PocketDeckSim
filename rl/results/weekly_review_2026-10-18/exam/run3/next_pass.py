#!/usr/bin/env python3
"""The judge's passes for exam run 3 (PREREG_RUN3 addendum 8, K20; the coordinator's decision of Oct 25, before any run 3 row).

  next_pass.py --ids ALL_IDS --out NEXT_SEND --results F... --pass SEND_FILE STDOUT [--pass SEND_FILE STDOUT ...]

After the passes so far (each: the ids it was asked to send, and frozen-7 budget_judge.py's stdout/stderr), writes the ids the next pass sends
and prints one JSON line of counts.
- A task is NOT SENT in a pass only when budget_judge's own record says so: a line `NOT SENT <id> repeat ...` for it in that pass and no
  `TASK FAILED <id> ...` line (budget_judge prints NOT SENT only when its spend gate refused the task before any HTTP request).
- Anything else in a pass's send list counts as SENT (an issued call): a TASK FAILED line (an API error, a timeout, a connection reset, a
  refusal inside judge_one), a row, or no line at all (ambiguous: it may have left the machine).
- A decision with a row is never asked again. A decision without a row is sent again only if it has been SENT fewer than 2 times: never
  issued (only NOT SENT so far) -> eligible; issued once without a row -> its single resend (run 2's A4); issued twice -> never again.
Ids are read whitespace-separated from every file."""
import argparse, collections, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument('--ids', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--results', nargs='*', default=[]); ap.add_argument('--pass', dest='passes', nargs=2, action='append', default=[])
a = ap.parse_args()
ids = open(a.ids).read().split()
have = set()
for f in a.results:
    try:
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    have.add(json.loads(line)['position'])
    except FileNotFoundError:
        pass
sends = collections.Counter()
last = {}
for send_file, stdout in a.passes:
    send = open(send_file).read().split()
    try:
        txt = open(stdout, errors='replace').read()
    except FileNotFoundError:
        txt = ''
    not_sent = set(re.findall(r'^NOT SENT (\S+) repeat ', txt, re.M))
    failed = collections.Counter(re.findall(r'^TASK FAILED (\S+) repeat ', txt, re.M))
    issued = [i for i in send if not (i in not_sent and failed[i] == 0)]
    for i in issued:
        sends[i] += 1
    last = {'asked': len(send), 'sent': len(issued), 'not_sent': len([i for i in send if i in not_sent and failed[i] == 0]),
            'failed': sum(1 for i in send if failed[i]), 'without_row_after': sum(1 for i in send if i not in have)}
missing = [i for i in ids if i not in have]
nxt = [i for i in missing if sends[i] < 2]
open(a.out, 'w').write('\n'.join(nxt) + ('\n' if nxt else ''))
print(json.dumps({'last_pass': last, 'missing': len(missing), 'never_issued': sum(1 for i in missing if sends[i] == 0),
                  'issued_once': sum(1 for i in missing if sends[i] == 1), 'issued_twice': sum(1 for i in missing if sends[i] >= 2),
                  'next': len(nxt)}))
