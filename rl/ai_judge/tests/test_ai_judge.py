#!/usr/bin/env python3
"""Tests of the AI plan judge harness.

  cd rl/ai_judge && python3 -B -m unittest -v tests.test_ai_judge

The parser, prompt and cost tests need nothing built. The plan-list tests (count, dedupe, chance cut-off, no future leakage, cap) run the
judge_plans binary on the small positions in tests/fixtures and are skipped when it is not built (see README.md; JUDGE_PLANS_BIN points at it).
"""
import json, os, subprocess, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import judge  # noqa: E402

FIX = os.path.join(HERE, 'fixtures')
POS = os.path.join(FIX, 'mini_positions.json')
DECKS = os.path.join(FIX, 'decks')
DECK_ARGS = None
HAVE_BIN = os.path.exists(judge.PLANS_BIN)


def plans(ids, world_seed=1, extra=None):
    cmd = [judge.PLANS_BIN, '--positions', POS] + judge.deck_args(DECKS) + ['--world-seed', str(world_seed)] + (extra or [])
    for i in ids:
        cmd += ['--only', i]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-1500:]
    return {json.loads(l)['id']: json.loads(l) for l in r.stdout.splitlines()}, r.stdout


class Parser(unittest.TestCase):
    def test_plain_answer(self):
        r = judge.parse_choice('PLAN: 7\nREASON: Energy on Kingambit sets up next turn.', 12)
        self.assertEqual((r['ok'], r['plan'], r['reason']), (True, 7, 'Energy on Kingambit sets up next turn.'))

    def test_formatting_variants_are_accepted(self):
        for t in ['plan: 3\nreason: x', '**PLAN:** 3\n**REASON:** x', 'PLAN = Plan 3\nREASON - x', '  PLAN: #3  \nREASON: x']:
            self.assertEqual(judge.parse_choice(t, 5)['plan'], 3, t)

    def test_out_of_range_missing_and_ambiguous_are_refused(self):
        self.assertFalse(judge.parse_choice('PLAN: 0\nREASON: x', 5)['ok'])
        self.assertFalse(judge.parse_choice('PLAN: 6\nREASON: x', 5)['ok'])
        self.assertFalse(judge.parse_choice('I would play the attack.', 5)['ok'])
        r = judge.parse_choice('PLAN: 2\nREASON: x\nPLAN: 4', 5)
        self.assertFalse(r['ok'])
        self.assertIn('several', r['error'])

    def test_a_missing_reason_keeps_the_choice_and_says_so(self):
        r = judge.parse_choice('PLAN: 2', 5)
        self.assertTrue(r['ok'])
        self.assertIn('REASON', r['error'])

    def test_a_number_inside_the_reason_is_not_the_plan(self):
        r = judge.parse_choice('PLAN: 2\nREASON: plan 4 loses to a Rare Candy', 5)
        self.assertEqual(r['plan'], 2)


class PlanMatching(unittest.TestCase):
    REC = {'plans': [
        {'n': 1, 'labels': ['Attach:1Darkness@0 zone', 'Attack:Slash'], 'end': 'attack'},
        {'n': 2, 'labels': ['Attach:1Darkness@0 zone', 'Play:Poké Ball'], 'end': 'chance'},
        {'n': 3, 'labels': ['Attach:1Darkness@0 zone', 'EndTurn'], 'end': 'end_turn'},
        {'n': 4, 'labels': ['Play:Poké Ball'], 'end': 'chance'},
        {'n': 5, 'labels': ['Place:Glimmet@2', 'EndTurn'], 'end': 'end_turn'},
    ]}

    def test_a_bots_turn_is_cut_at_the_first_chance_step_and_after_an_attack(self):
        c = judge.canonical_plan(['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'Place:Pawniard@1', 'Attack:Slash', 'EndTurn'], self.REC)
        self.assertEqual(c, ['Attach:1Darkness@0 zone', 'Play:Poké Ball'])
        c = judge.canonical_plan(['Attach:1Darkness@0 zone', 'Attack:Slash', 'EndTurn'], self.REC)
        self.assertEqual(c, ['Attach:1Darkness@0 zone', 'Attack:Slash'])

    def test_number_for_picks_the_listed_plan_by_key(self):
        rec = {'plans': [{'n': 1, 'key': 'a'}, {'n': 2, 'key': 'b'}]}
        self.assertEqual(judge.number_for(rec, ['x', 'b']), 2)
        self.assertIsNone(judge.number_for(rec, ['x']))
        self.assertIsNone(judge.number_for(rec, 'no legal action labelled ...'))  # an error text instead of keys


class LivePath(unittest.TestCase):
    """judge_one with the API call replaced by a fake: no network."""
    def rec(self):
        mk = lambda n, labels, end: {'n': n, 'key': f'k{n}', 'labels': labels, 'steps': labels, 'n_steps': len(labels), 'end': end, 'final': {'kind': 'end_turn'},
                                    'result': {'board': ['Active: Regigigas 30/130 HP, Energy []'], 'hand': ['Kingambit'], 'points': [0, 0], 'deck_size': 9}}
        return {'KW-261013_010837000-t07': {'capped': False, 'total_found': 3,
                'start': TestFakeStart.START, 'plans': [mk(1, ['EndTurn'], 'end_turn'), mk(2, ['Retreat:1', 'EndTurn'], 'end_turn'), mk(3, ['Attach:1Darkness@0 zone', 'EndTurn'], 'end_turn')]}}

    def run_fake(self, order, reply, stop='end_turn'):
        from unittest import mock
        usage = {'input_tokens': 1000, 'output_tokens': 50}
        with mock.patch.object(judge, 'call_claude', return_value=(reply, usage, 1.5, judge.MODEL, {'stop_reason': stop, 'content_types': ['thinking', 'text']})):
            r, _, _ = judge.judge_one('KW-261013_010837000-t07', judge.load_positions(), self.rec(), order, True, judge.MODEL)
        return r

    def test_a_reversed_prompt_maps_the_chosen_number_back_to_the_listed_plan(self):
        r = self.run_fake('reverse', 'PLAN: 1\nREASON: attach')
        self.assertEqual((r['shown_number'], r['plan_number']), (1, 3))  # shown first = listed third
        self.assertEqual(r['plan'], ['Attach:1Darkness@0 zone', 'EndTurn'])
        self.assertEqual(r['order'], 'reverse')
        self.assertEqual(r['cost']['input_tokens'], 1000)
        self.assertGreater(r['cost']['usd'], 0)

    def test_reasoning_that_uses_up_the_output_cap_is_reported_not_guessed(self):
        r = self.run_fake('forward', '', stop='max_tokens')
        self.assertIsNone(r['plan_number'])
        self.assertIn('max_tokens', r['parse_error'])
        self.assertIsNotNone(r['cost'])  # the tokens were still spent and are recorded

    def test_an_answer_outside_the_list_is_refused(self):
        r = self.run_fake('forward', 'PLAN: 9\nREASON: x')
        self.assertIsNone(r['plan_number'])
        self.assertIn('not in 1..3', r['parse_error'])


class TestFakeStart:
    START = {'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
             'me': {'board': ['Active: Regigigas 30/130 HP, Energy []'], 'hand': ['Kingambit'], 'discard': [], 'discard_energy': [], 'deck_size': 9, 'unseen_deck': {'Glimmet': 1}},
             'opp': {'board': ['Active: Mega Kangaskhan ex 180/180 HP, Energy [Lightning]'], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}}


class Cost(unittest.TestCase):
    def test_cost_uses_the_response_usage_and_the_price_table(self):
        c = judge.cost_of('claude-sonnet-5-5', {'input_tokens': 10000, 'output_tokens': 100})
        self.assertAlmostEqual(c['usd'], 10000 * 3 / 1e6 + 100 * 15 / 1e6, places=6)
        self.assertEqual((c['input_tokens'], c['output_tokens']), (10000, 100))
        self.assertIn('assumed', c['price_note'])


class PromptWhitelist(unittest.TestCase):
    def fake_rec(self):
        return {'capped': False, 'total_found': 1,
                'start': {'turn_count': 7, 'points': [0, 0], 'energy_zone': ['Darkness', 'Darkness'], 'stadium': None, 'stadium_owner': None,
                          'me': {'board': ['Active: Regigigas 30/130 HP, Energy []'], 'hand': ['Kingambit', 'Rare Candy'], 'discard': ['Glimmet'], 'discard_energy': [],
                                 'deck_size': 9, 'unseen_deck': {'Poké Ball': 2, 'Glimmet': 1}},
                          'opp': {'board': ['Active: Mega Kangaskhan ex 180/180 HP, Energy [Lightning]'], 'hand_count': 5, 'deck_count': 12, 'discard': [], 'discard_energy': []}},
                'plans': [{'n': 1, 'labels': ['EndTurn'], 'steps': ['End the turn'], 'n_steps': 1, 'end': 'end_turn', 'final': {'kind': 'end_turn'},
                           'result': {'board': ['Active: Regigigas 30/130 HP, Energy []'], 'hand': ['Kingambit', 'Rare Candy'], 'points': [0, 0], 'deck_size': 9}}]}

    def test_the_prompt_never_carries_the_recorded_plan_or_hidden_fields(self):
        positions = judge.load_positions()
        pos = positions['KW-261013_010837000-t07']
        self.assertTrue(pos['his_plan'])
        system, user, shown = judge.render_prompt(pos, self.fake_rec())
        text = system + user
        for secret in ['his_plan', 'Evolve:Kingambit@1', 'hand_source', 'decision_maker', 'codex', 'filler', 'exact_list', 'approximate', 'Dustin']:
            self.assertNotIn(secret, text, secret)
        self.assertIn('PLAN: <one plan number>', text)
        self.assertEqual(list(shown), [1])

    def test_exact_card_text_is_included(self):
        positions = judge.load_positions()
        system, user, _ = judge.render_prompt(positions['KW-261013_010837000-t07'], self.fake_rec())
        self.assertIn('Overlord', user)  # Kingambit's attack, from lib/card.py

    def test_order_options_are_deterministic(self):
        ps = [{'n': i} for i in range(1, 7)]
        self.assertEqual([p['n'] for p in judge.order_plans(ps, 'reverse')], [6, 5, 4, 3, 2, 1])
        self.assertEqual(judge.order_plans(ps, 'shuffle:3'), judge.order_plans(ps, 'shuffle:3'))

    def test_dry_run_sends_nothing_and_records_no_choice(self):
        positions = judge.load_positions()
        rec = {'KW-261013_010837000-t07': self.fake_rec()}
        r, _, _ = judge.judge_one('KW-261013_010837000-t07', positions, rec, 'forward', live=False, model=judge.MODEL)
        self.assertTrue(r['dry_run'])
        self.assertIsNone(r['plan'])
        self.assertIsNone(r['cost'])
        self.assertGreater(r['prompt_tokens_estimate'], 100)


@unittest.skipUnless(HAVE_BIN, 'judge_plans is not built')
class PlanList(unittest.TestCase):
    def test_a_draw_ends_its_plan_and_nothing_follows_it(self):
        rec = plans(['MINI-DRAW'])[0]['MINI-DRAW']
        draws = [p for p in rec['plans'] if any(l == "Play:Professor's Research" for l in p['labels'])]
        self.assertTrue(draws)
        for p in draws:
            self.assertEqual(p['labels'][-1], "Play:Professor's Research", p['labels'])
            self.assertEqual(p['end'], 'chance')
            self.assertEqual(p['final']['kind'], 'your_deck')
        # no plan goes on past a chance step, and every plan ends in a legal way
        for p in rec['plans']:
            self.assertIn(p['end'], ('attack', 'chance', 'end_turn', 'opponent_choice'))
            self.assertEqual(sum(1 for l in p['labels'] if l == "Play:Professor's Research"), p['labels'].count("Play:Professor's Research"))

    def test_orders_of_the_same_moves_are_one_plan(self):
        rec = plans(['MINI-DRAW'])[0]['MINI-DRAW']
        ps = rec['plans']
        # the two plans "Energy then Heavy Helmet" and "Heavy Helmet then Energy" reach one visible state: only one may be listed
        self.assertEqual(len({(p['end'], tuple(p['result']['board']), tuple(p['result']['hand']), p['labels'][-1]) for p in ps}), len(ps))
        self.assertEqual(len({tuple(sorted(p['labels'])) for p in ps}), len(ps))
        both = [p for p in ps if any(l.startswith('Attach:') for l in p['labels']) and any(l.startswith('Tool:') for l in p['labels'])
                and p['end'] == 'end_turn' and not any(l.startswith('Retreat') for l in p['labels'])]
        # Energy to one of 2 Pokémon x Heavy Helmet on one of 2 Pokémon = 4 distinct states, each listed once (2 orders each would make 8)
        self.assertEqual(len(both), 4, [p['labels'] for p in both])

    def test_the_plan_list_is_complete_for_a_small_hand(self):
        rec = plans(['MINI-DRAW'])[0]['MINI-DRAW']
        self.assertFalse(rec['capped'])
        self.assertEqual(rec['n_plans'], rec['total_found'])
        # By hand: Energy {none, Pawniard, Glimmet} x Heavy Helmet {none, on either} x Retreat {no, yes} = 3 x 3 x 2 = 18 turn states, and the
        # states with an affordable attack or the draw add the rest: 12 attack plans, 18 draw plans (one per state before the draw), 18 end-turn plans.
        # (A retreating Pawniard leaves a Glimmet with Energy only when the Energy went to Glimmet, so only those states can still attack: Hang Down.)
        self.assertEqual(rec['n_plans'], 48)
        by_end = {}
        for p in rec['plans']:
            by_end[p['end']] = by_end.get(p['end'], 0) + 1
        self.assertEqual(by_end, {'attack': 12, 'chance': 18, 'end_turn': 18})

    def test_the_real_next_draw_and_the_world_never_change_the_output(self):
        strip = lambda out: '\n'.join(json.dumps({k: v for k, v in json.loads(l).items() if k != 'world_seed'}, sort_keys=True) for l in out.splitlines())  # the seed is echoed
        a = strip(plans(['MINI-DRAW', 'MINI-DRAW-TOP'], world_seed=1)[1])
        b = strip(plans(['MINI-DRAW', 'MINI-DRAW-TOP'], world_seed=2)[1])
        c = strip(plans(['MINI-DRAW', 'MINI-DRAW-TOP'], world_seed=99)[1])
        self.assertEqual(a, b)
        self.assertEqual(a, c)
        recs = plans(['MINI-DRAW', 'MINI-DRAW-TOP'])[0]
        # a position that FIXES the top of the deck (the actual next draw) lists exactly the same plans as one that does not
        self.assertEqual(recs['MINI-DRAW']['plans_hash'], recs['MINI-DRAW-TOP']['plans_hash'])
        # and the top cards are not named anywhere in the plans (they are not in hand or on the board)
        text = json.dumps(recs['MINI-DRAW-TOP']['plans'])
        self.assertNotIn('Kingambit', text)
        self.assertNotIn('Rare Candy', text)
        self.assertEqual(recs['MINI-DRAW']['start']['me']['unseen_deck'], recs['MINI-DRAW-TOP']['start']['me']['unseen_deck'])

    def test_a_coin_attack_is_described_by_its_chances(self):
        rec = plans(['MINI-COIN'])[0]['MINI-COIN']
        stomp = [p for p in rec['plans'] if p['labels'][-1] == 'Attack:Stomp']
        self.assertTrue(stomp)
        outs = stomp[0]['final']['outcomes']
        self.assertEqual(sorted(o['p'] for o in outs), [0.5, 0.5])
        self.assertNotEqual(outs[0]['lines'], outs[1]['lines'])

    def match(self, labels, pid='MINI-DRAW'):
        rec = plans([pid])[0][pid]
        keys = judge.replay([(pid, 't', labels)], POS, DECKS)['t']
        return judge.number_for(rec, keys), rec

    def test_a_move_list_in_another_order_or_with_other_slot_numbers_is_the_same_listed_plan(self):
        n1, rec = self.match(['Attach:1Darkness@1 zone', 'Retreat:1', 'Attack:Hang Down'])
        n2, _ = self.match(['Retreat:1', 'Attach:1Darkness@0 zone', 'Attack:Hang Down'])  # Energy after the swap goes to slot 0: the same Pokémon
        self.assertIsNotNone(n1)
        self.assertEqual(n1, n2)
        self.assertEqual(rec['plans'][n1 - 1]['end'], 'attack')
        a, _ = self.match(['Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Attach:1Darkness@1 zone'])
        b, _ = self.match(['Attach:1Darkness@1 zone', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0'])
        self.assertIsNotNone(a)
        self.assertEqual(a, b)

    def test_a_move_list_is_followed_only_to_its_first_chance_step_or_attack(self):
        n, rec = self.match(["Attach:1Darkness@0 zone", "Play:Professor's Research", 'Attack:Slash', 'EndTurn'])
        self.assertEqual(rec['plans'][n - 1]['end'], 'chance')
        self.assertEqual(rec['plans'][n - 1]['labels'], ['Attach:1Darkness@0 zone', "Play:Professor's Research"])
        m, rec = self.match(['Attach:1Darkness@0 zone', 'Attack:Slash', 'EndTurn'])
        self.assertEqual(rec['plans'][m - 1]['labels'], ['Attach:1Darkness@0 zone', 'Attack:Slash'])

    def test_a_list_without_a_closing_end_turn_gets_one(self):
        n, rec = self.match(['Attach:1Darkness@0 zone'])
        self.assertEqual(rec['plans'][n - 1]['labels'], ['Attach:1Darkness@0 zone', 'EndTurn'])

    def test_an_illegal_move_list_says_so(self):
        keys = judge.replay([('MINI-DRAW', 't', ['Play:Mesagoza'])], POS, DECKS)['t']
        self.assertIsInstance(keys, str)
        self.assertIn('no legal action', keys)

    def test_field_blower_targets_keep_their_own_identity(self):
        rec = plans(['MINI-BLOWER'])[0]['MINI-BLOWER']
        blow = [p for p in rec['plans'] if any(l.startswith('DiscardToolFromPokemon') for l in p['labels'])]
        labels = {l for p in blow for l in p['labels'] if l.startswith('DiscardToolFromPokemon')}
        self.assertEqual(len(labels), 2, labels)  # two different Pokémon -> two different labels, not one shared name
        self.assertEqual(len({p['key'] for p in blow}), len(blow))
        self.assertTrue(any('Active' in ' '.join(p['steps']) for p in blow) and any('Bench 1' in ' '.join(p['steps']) for p in blow))
        # replay tells them apart, with the full label and with the bare recorded name (which fits both)
        full = sorted(labels)
        k0 = judge.replay([('MINI-BLOWER', 'a', ['Play:Field Blower', full[0]]), ('MINI-BLOWER', 'b', ['Play:Field Blower', full[1]]),
                           ('MINI-BLOWER', 'c', ['Play:Field Blower', 'DiscardToolFromPokemon'])], POS, DECKS)
        self.assertNotEqual(k0['a'], k0['b'])
        self.assertEqual(len(k0['c']), 2)
        self.assertTrue(set(k0['a']) | set(k0['b']) == set(k0['c']))

    def test_every_generation_input_is_echoed_and_a_capped_list_is_refused(self):
        rec = plans(['MINI-DRAW'], extra=['--max-plans', '3'])[0]['MINI-DRAW']
        self.assertEqual(rec['world_seed'], 1)
        self.assertEqual(rec['limits']['max_plans'], 3)
        positions = judge.load_positions()
        positions['MINI-DRAW'] = json.load(open(POS))[0]
        with self.assertRaises(SystemExit) as cm:
            judge.judge_one('MINI-DRAW', positions, {'MINI-DRAW': rec}, 'forward', True, judge.MODEL)
        self.assertIn('capped', str(cm.exception))

    def test_the_cap_is_reported(self):
        rec = plans(['MINI-DRAW'], extra=['--max-plans', '3'])[0]['MINI-DRAW']
        self.assertTrue(rec['capped'])
        self.assertEqual(rec['n_plans'], 3)
        self.assertGreater(rec['total_found'], 3)

    def test_labels_use_the_pg_pos_vocabulary(self):
        rec = plans(['MINI-DRAW'])[0]['MINI-DRAW']
        labels = {l for p in rec['plans'] for l in p['labels']}
        self.assertIn('Attach:1Darkness@1 zone', labels)
        self.assertIn("Play:Professor's Research", labels)
        self.assertIn('EndTurn', labels)


if __name__ == '__main__':
    unittest.main()
