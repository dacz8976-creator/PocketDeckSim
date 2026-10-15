import json, os, shutil, subprocess, sys, collections
REPO = '/home/dacz8976/pgfix'
PROG = '/home/dacz8976/kx_r2/strength'
W = '/home/dacz8976/paired_check'
shutil.rmtree(W, ignore_errors=True); os.makedirs(W)
reg = json.load(open(f'{REPO}/rl/strength/decks.json'))['decks']
opps = ['t-altaria', 't-suicune', 't-hydreigon', 't-weezing']
base_path = 'decks/dustin/13-a-ninetales-raticate.txt'
cape_path = 'decks/variants-2026-10-15/13-a-giant-cape.txt'
# negative control: the same swap but the Cape on the last line (Ilima's line removed): every card after Ilima's old place moves up by one
txt = open(f'{REPO}/{base_path}', encoding='utf-8').read()
moved = txt.replace('1 Ilima A3 149\n', '') .rstrip('\n') + '\n1 Giant Cape A2 147\n'
open(f'{W}/moved.txt', 'w', encoding='utf-8').write(moved)
variants = {'base': f'{REPO}/{base_path}', 'cape': f'{REPO}/{cape_path}', 'moved': f'{W}/moved.txt'}
def run(label):
    man = dict(name=label, repo_root=REPO, pilot='km3', reference='km3', stage='use', decks=[dict(name=label, path=variants[label], sha256='x')],
               opponents=[dict(name=o, path=reg[o], sha256='x') for o in opps], deals=10, seats=[0, 1], seed_base=24606700000, pair_stride=10000, threads=4,
               log_level='deck', ext_timeout_s=None, heldout_decks=[], heldout_locked=True)
    mp = f'{W}/{label}_manifest.json'; json.dump(man, open(mp, 'w'))
    out = f'{W}/{label}'; os.makedirs(out)
    r = subprocess.run([PROG, 'run', '--manifest', mp, '--out', out, '--threads', '4'], capture_output=True, text=True)
    print(label, r.returncode, r.stderr[-300:])
    rows = [json.loads(l) for l in open(f'{out}/games.jsonl')]
    return {(g['opp'], g['deal'], g['seat'], g['arm']): g for g in rows}
R = {k: run(k) for k in variants}
def strip(g): return ([{k: v for k, v in e.items() if k != 'ms'} for e in g['log']], g['winner'], g['points'], g['turns'])
for other in ('cape', 'moved'):
    keys = sorted(R['base'])
    same_first = sum(1 for k in keys if R['base'][k]['first'] == R[other][k]['first'])
    same_game = sum(1 for k in keys if strip(R['base'][k]) == strip(R[other][k]))
    # the length of the common prefix of the logged moves, as a share of the shorter log
    def prefix(a, b):
        n = 0
        for x, y in zip(a, b):
            if x != y: break
            n += 1
        return n
    first_move_same = sum(1 for k in keys if strip(R['base'][k])[0][:1] == strip(R[other][k])[0][:1])
    print(f'base v {other}: {len(keys)} twin games; who goes first the same in {same_first}; first logged move the same in {first_move_same}; the whole game identical in {same_game}')
    # games where the replaced card (Ilima / Giant Cape) never appears in either log: should be identical when the cards in place are aligned
    never = [k for k in keys if not any(e['a'] in ('Play:Ilima', 'Play:Giant Cape') for e in R['base'][k]['log'] + R[other][k]['log'])]
    print(f'   of the {len(never)} games where neither card was played, identical: {sum(1 for k in never if strip(R["base"][k]) == strip(R[other][k]))}')
