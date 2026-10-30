import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
sys.path.insert(0, HERE)
import game_kit  # noqa: E402
import game_obs  # noqa: E402
import judge  # noqa: E402
import test_game_lister as TL  # noqa: E402


def card_id_seqs(pos):
    cid = judge._cid
    me, opp = pos['me'], pos['opp']
    seqs = {'me.hand': [cid(s) for s in me['hand']], 'me.discard': [cid(s) for s in me['discard']]}
    for name, side in (('me', me), ('opp', opp)):
        seqs[name + '.board'] = [[cid(b['card'])] + [cid(s) for s in b.get('behind', [])] + [cid(s) for s in b.get('tools', [])] for b in side['board']]
    seqs['opp.discard'] = [cid(s) for s in opp['discard']]
    seqs['stadium'] = cid(pos['stadium']['card']) if pos.get('stadium') else None
    return seqs


def datasets():
    out = []
    for label, f, decks, only in TL.pos_files():
        with open(f) as fh:
            plist = json.load(fh)
        by_id = {p['id']: p for p in plist}
        pos_out, recs = TL.exports(label, f, decks, only)
        kinds = TL.by_kind(TL.obs_run(recs, 'o_' + label))
        pos_rec = {}
        for l in pos_out.splitlines():
            d = json.loads(l)
            if d['kind'] == 'plans':
                pos_rec[d['id']] = d
        out.append((label, decks, by_id, [r['id'] for r in recs], kinds, pos_rec))
    return out


_DATA = []


def data():
    if not _DATA:
        _DATA.extend(datasets())
    return _DATA


class Obs(unittest.TestCase):
    def test_O1_card_ids(self):
        n = 0
        for label, decks, by_id, ids, kinds, _ in data():
            if label == '92':
                self.assertEqual(sorted(ids), sorted(TL.ids92()))
                self.assertEqual(len(ids), 92)
            for i in ids:
                orig = by_id[i]
                g = game_obs.pos_for_prompt(kinds['pos_like'][i]['pos'], i, orig['deck'])
                a, b = card_id_seqs(orig), card_id_seqs(g)
                for k in a:
                    if a[k] != b[k]:
                        self.fail('%s %s: %s | %s' % (label, i, TL.cut((k, a[k])), TL.cut((k, b[k]))))
                self.assertEqual(orig['turn_count'], g['turn_count'], i)
                self.assertEqual(json.dumps(orig['turn_effects']), json.dumps(g['turn_effects']), i)
                self.assertEqual(orig['me'].get('knockouts'), g['me']['knockouts'], i)
                n += 1
        print('O1 positions compared', n)

    def test_O2_prompt_identity(self):
        n = 0
        for label, decks, by_id, ids, kinds, pos_rec in data():
            if label == '92':
                self.assertEqual(sorted(ids), sorted(TL.ids92()))
                self.assertEqual(len(ids), 92)
            classes = {i: game_obs.declared_classes(by_id[i]) for i in ids}
            hits = [i for i in ids if classes[i]]
            if label == '92':
                print('CLASSES_92', len(hits))
                self.assertEqual(hits, [], 'declared class on the 92')
            else:
                print('CLASSES_FIXTURES', label, len(hits), hits[:5])
            for i in ids:
                if classes[i]:
                    continue
                orig = by_id[i]
                g = game_obs.pos_for_prompt(kinds['pos_like'][i]['pos'], i, orig['deck'])
                ra = judge.render_prompt(orig, pos_rec[i], 'shuffle-id', decks, 80, 'v1')
                rb = judge.render_prompt(g, kinds['plans'][i], 'shuffle-id', decks, 80, 'v1')
                for part, x, y in zip(('system', 'user', 'shown'), ra, rb):
                    if x != y:
                        if isinstance(x, str):
                            for lx, ly in zip(x.split('\n') + [''], y.split('\n') + ['']):
                                if lx != ly:
                                    self.fail('%s %s %s: %s | %s' % (label, i, part, TL.cut(lx), TL.cut(ly)))
                        self.fail('%s %s %s differs: %s | %s' % (label, i, part, TL.cut(x), TL.cut(y)))
                n += 1
        print('O2 prompts byte-identical', n)

    def test_O3_decks_and_ids(self):
        for f in list(game_kit.DECKS.values()) + list(game_kit.LISTS.values()):
            path = os.path.join(TL.REPO, f)
            d, k = game_obs.decks_dir_and_key(f)
            self.assertEqual(d, os.path.dirname(f))
            self.assertTrue(k and not k.endswith('.txt'))
            self.assertEqual(sum(game_obs.deck_counter(path).values()), 20, f)
        self.assertEqual(game_obs.decks_dir_and_key('decks/dustin/09-mega-manectric-heliolisk.txt'), ('decks/dustin', '09-mega-manectric-heliolisk'))
        inputs, meta, kinds = TL.seat1_inputs()
        n = 0
        for rec in inputs:
            rid = rec['id']
            pos = kinds['pos_like'][rid]['pos']
            deck = game_obs.deck_counter(os.path.join(TL.REPO, meta[rid]['deck_file']))
            ids = list(pos['me']['hand']) + list(pos['me']['discard'])
            for b in pos['me']['board']:
                ids.append(b['card'])
                ids += b.get('behind', []) + b.get('tools', [])
            for s in ids:
                self.assertIn(game_obs.pad_id(' '.join(s.split()[-2:])), deck, '%s %s' % (rid, s))
                n += 1
        print('O3 ids checked', n)

    def test_O4_seat1_pos_like(self):
        inputs, meta, kinds = TL.seat1_inputs()
        picked = [r for r in inputs if r['pdl_observation']['template']['turn_count'] >= 1]
        self.assertGreaterEqual(len(picked), 10)

        def cs(c):
            v = list(c.values())[0]
            return '%s %s' % (v['name'], v['id'])

        def board(side):
            return [{'card': cs(p['card']), 'behind': [cs(c) for c in p['cards_behind']], 'tools': [cs(c) for c in p['attached_tools']]}
                    for p in side if p is not None]

        def expected(obs):
            t = obs['template']
            a = obs['actor']
            tc = t['turn_count']
            te = []
            for e in t['turn_effects'].get(str(tc), []):
                te.append({'turn': tc, 'effect': relmap(json.loads(json.dumps(e)), a)})
            st = t['active_stadium']
            return {'turn_count': tc,
                    'stadium': None if st is None else {'card': cs(st), 'owner': 0 if t['active_stadium_owner'] == a else 1},
                    'turn_effects': te,
                    'me': {'hand': [cs(c) for c in t['hands'][a]], 'discard': [cs(c) for c in t['discard_piles'][a]],
                           'board': board(t['in_play_pokemon'][a]), 'knockouts': t['own_knockouts_this_game'][a]},
                    'opp': {'board': board(t['in_play_pokemon'][1 - a]), 'discard': [cs(c) for c in t['discard_piles'][1 - a]]}}

        def relmap(x, a):
            if isinstance(x, dict):
                return {k: ((0 if v == a else 1) if k in ('player', 'source_player', 'target_player') and isinstance(v, int) else relmap(v, a)) for k, v in x.items()}
            if isinstance(x, list):
                return [relmap(v, a) for v in x]
            return x

        for r in picked:
            got = game_obs.pos_for_prompt(kinds['pos_like'][r['id']]['pos'], r['id'], 'k')
            exp = expected(r['pdl_observation'])
            for k in ('turn_count', 'stadium', 'me', 'opp'):
                self.assertEqual(json.dumps(got[k], sort_keys=True), json.dumps(exp[k], sort_keys=True), '%s %s' % (r['id'], k))
            self.assertEqual(json.dumps(got['turn_effects']), json.dumps(exp['turn_effects']))
        # planted copies: a stadium, knockouts and turn effects (seat-1 actor)
        base = json.loads(json.dumps(picked[0]['pdl_observation']))
        a = base['actor']
        self.assertEqual(a, 1)
        t = base['template']
        tc = t['turn_count']
        trainer = next(c for c in (t['hands'][a] + t['discard_piles'][a]) if 'Trainer' in c)
        t['active_stadium'] = json.loads(json.dumps(trainer))
        t['active_stadium']['Trainer']['trainer_card_type'] = 'Stadium'
        t['active_stadium_owner'] = 1
        t['own_knockouts_this_game'] = [2, 3]
        rdft = {'ReducedDamageForTarget': {'amount': 30, 'only_from_ex': False, 'player': 1, 'scope': 'AllPokemon'}}
        rdt = {'ReducedDamageForType': {'amount': 20, 'energy_type': 'Lightning', 'player': 0}}
        t['turn_effects'] = {str(tc - 1): ['NoItemCards'], str(tc): [rdft, 'NoSupportCards', rdt], str(tc + 1): ['NoTrainerCards']}
        lines = TL.by_kind(TL.obs_run([{'id': 'planted', 'pdl_observation': base, 'legal_actions': None}], 'o4_planted'))
        self.assertNotIn('problem', lines)
        pos = game_obs.pos_for_prompt(lines['pos_like']['planted']['pos'], 'planted', 'k')
        exp = expected(base)
        self.assertEqual(exp['stadium']['owner'], 0)
        self.assertEqual(exp['me']['knockouts'], 3)
        self.assertEqual(len(exp['turn_effects']), 3)
        self.assertEqual(exp['turn_effects'][0]['effect']['ReducedDamageForTarget']['player'], 0)
        self.assertEqual(exp['turn_effects'][2]['effect']['ReducedDamageForType']['player'], 1)
        for k in ('turn_count', 'stadium', 'turn_effects', 'me', 'opp'):
            self.assertEqual(json.dumps(pos[k], sort_keys=(k != 'turn_effects')), json.dumps(exp[k], sort_keys=(k != 'turn_effects')), k)


if __name__ == '__main__':
    unittest.main()
