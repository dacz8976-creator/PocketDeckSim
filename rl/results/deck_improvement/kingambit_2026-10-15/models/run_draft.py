"""Run the consistency model (../consistency/sim2.py, unchanged) on the exact draft lists A, B, C and two side variants.
Same seed, policy 'eager', N deals per seat. usage: python3 -B run_draft.py N out.json"""
import sys, os, json, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'consistency'))
import sim2

P = sim2.PLAYED
B_CH = {'Rare Candy': 1, 'LIP': -2, 'Copycat': 1}
LISTS = [
    ('A played list', {}, P),
    ('B played -2 Ice Pop +1 Rare Candy +1 Copycat', B_CH, P),
    ('C = B -Ilima +Red', dict(B_CH, Ilima=-1, Red=1), P),
    ('Bplus = B -Ilima +Juliana', dict(B_CH, Ilima=-1, Juliana=1), P),
    ('Bjul = played -2 Ice Pop +1 Rare Candy +1 Juliana', {'Rare Candy': 1, 'LIP': -2, 'Juliana': 1}, P),
    ('Bsmall = played -1 Ice Pop +1 Rare Candy', {'Rare Candy': 1, 'LIP': -1}, P),
    ('File deck01', {}, sim2.CORE),
]
KEYS = ['PAW_1', 'PAW_2', 'KG_2', 'KG_3', 'KG_4', 'KG_5', 'BLADE_3', 'BLADE_4', 'BLADE_5', 'GLM_2', 'GLM_3', 'MUK_3',
        'ALL3_4', 'ALL3_5', 'MUKGIGAS_4', 'PAW_ACTIVE', 'KGdeck_3', 'RCdeck_3']

def main():
    n = int(sys.argv[1]); out = sys.argv[2]
    opp = sim2.opp_hand_pool()
    res = {}
    for name, ch, base in LISTS:
        dl = sim2.mk(ch, base)
        res[name] = {'list': dict(collections.Counter(dl))}
        for seat in ('first', 'second'):
            rng = random.Random(sim2.SEED)
            acc = collections.Counter(); why = collections.Counter()
            for _ in range(n):
                r = sim2.play_game(dl, seat, rng, opp, 'eager')
                for k, v in r.items():
                    if k == 'why4':
                        why[v] += 1
                    else:
                        acc[k] += v
            res[name][seat] = {k: round(100 * acc[k] / n, 1) for k in KEYS}
            res[name][seat + '_why4'] = {k: round(100 * v / n, 1) for k, v in why.most_common()}
        f, s = res[name]['first'], res[name]['second']
        both = {k: round((f[k] + s[k]) / 2, 1) for k in KEYS}
        res[name]['avg'] = both
        print(name, '|', ' '.join(f'{k}={both[k]}' for k in KEYS), '| BLADE first/second t3,t4:',
              f['BLADE_3'], s['BLADE_3'], f['BLADE_4'], s['BLADE_4'], flush=True)
    json.dump(res, open(out, 'w'), indent=1)

if __name__ == '__main__':
    main()
