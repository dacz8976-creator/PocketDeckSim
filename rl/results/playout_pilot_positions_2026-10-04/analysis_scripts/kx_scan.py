import json, re, sys, collections, os

POS = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_decisions_2026-10-02/positions_kx.json'
KX = '/home/dacz8976/pgd/runs_kx3_trace'
KM = '/home/dacz8976/pgd/runs_km3'

positions = {p['id']: p for p in json.load(open(POS))}

def read_out(path):
    plans = {}
    summ = None
    if not os.path.exists(path):
        return summ, plans
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
        except Exception:
            continue
        if j.get('kind') == 'position':
            summ = j.get('summary')
        elif j.get('kind') == 'free':
            plans[j['seed']] = (j['plan'], j.get('cut'))
    return summ, plans

def read_trace(path):
    # returns {seed: [(step, trace), ...]}
    out = collections.defaultdict(list)
    seed = None; step = None
    if not os.path.exists(path):
        return out
    for line in open(path):
        m = re.match(r'PGSTEP (\S+) seed (\d+) free (\d+)', line)
        if m:
            seed = int(m.group(2)); step = int(m.group(3)); continue
        if line.startswith('KX_TRACE '):
            t = json.loads(line[len('KX_TRACE '):])
            out[seed].append((step, t))
    return out

def short(mv):
    mv = mv.replace('Play { trainer_card: ', 'Play ').replace(' }', '')
    mv = re.sub(r'Attack\(Attack \{ energy_required: \[[^\]]*\], title: "([^"]+)".*', r'Attack \1', mv)
    return mv

def main(prefixes, detail_ids=None):
    for pid, p in positions.items():
        if not any(pid.startswith(x) for x in prefixes):
            continue
        if detail_ids and pid not in detail_ids:
            continue
        _, kxp = read_out(f'{KX}/out_{pid}.jsonl')
        if not kxp:
            continue
        _, kmp = read_out(f'{KM}/out_{pid}.jsonl')
        tr = read_trace(f'{KX}/err_{pid}.txt')
        kmfirst = collections.Counter(v[0][0] if v[0] else '-' for v in kmp.values())
        kxfirst = collections.Counter(v[0][0] if v[0] else '-' for v in kxp.values())
        his = p.get('his_plan', [])
        print('=' * 100)
        print(pid, '| maker', p.get('decision_maker'), '| exact', p.get('exact_list'), '| approx', p.get('approximate'), '| ms', p.get('milestones'), '| pts', p.get('points'))
        print('  HIS :', his)
        print('  KM3 first (12):', dict(kmfirst))
        for s in sorted(kxp):
            print(f'  KX s{s}:', kxp[s][0], '|', kxp[s][1])
        anychange = False
        for s in sorted(tr):
            for step, t in tr[s]:
                flag = 'CHANGED' if t['changed'] else 'kept'
                if t['changed']:
                    anychange = True
                cands = sorted(t['candidates'], key=lambda c: -c['score'])
                cs = '; '.join(f"{short(c['move'])} {c['score']:.3f} (d{c['diff']:+.3f} se{c['se']:.3f})" for c in cands)
                print(f'    s{s} step{step} {flag} km={short(t["km_move"])} -> {short(t["chosen"])} rounds={t["rounds"]} | {cs}')
                print(f'        reason: {t["reason"]}')

if __name__ == '__main__':
    pref = sys.argv[1].split(',') if len(sys.argv) > 1 else ['B-']
    ids = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    main(pref, ids)
