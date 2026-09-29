import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst")
from common import *
pairs, lim = load_limitless()
events = load_events(pairs, lim)
print("pairs", len(pairs), "events", len(events), "sum n_L", sum(sum(v) for v in lim.values()))
for name, (op, np_, on, nn) in readings().items():
    deals = load_reading(op, np_, pairs)
    O, N, L, nL, n = cell_stats(pairs, lim, deals)
    tO = S.tau(O, n, L, nL, pairs); tN = S.tau(N, n, L, nL, pairs)
    vals = {v for k in pairs for o, x in deals[k] for v in (o, x)}
    print(name, "dMSE %.1f" % dmse_point(pairs, O, N, L), "tau %s %.1f, %s %.1f" % (on, tO, nn, tN), "n range", min(n.values()), max(n.values()), "score values", sorted(vals))
