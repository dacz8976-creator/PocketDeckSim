#!/usr/bin/env python3
"""Tests of the AI plan judge harness.

  cd rl/ai_judge && python3 -B -m unittest -v tests.test_ai_judge

The parser, prompt and cost tests need nothing built. The plan-list tests (count, dedupe, chance cut-off, no future leakage, cap) run the
judge_plans binary on the small positions in tests/fixtures and are skipped when it is not built (see README.md; JUDGE_PLANS_BIN points at it).
"""
import json, os, subprocess, sys, tempfile, unittest

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

    def test_a_missing_reason_keeps_the_choice_and_says_so_as_a_warning_not_an_error(self):
        r = judge.parse_choice('PLAN: 2', 5)
        self.assertTrue(r['ok'])
        self.assertIsNone(r['error'])  # a record never carries an error together with a plan number
        self.assertIn('REASON', r['warning'])
        self.assertIsNone(judge.parse_choice('PLAN: 2\nREASON: x', 5)['warning'])

    def test_a_plan_line_that_names_several_plans_is_refused(self):
        for t in ['PLAN: 4 or 7\nREASON: x', 'PLAN: 4, 7\nREASON: x', 'PLAN: 4 / 7\nREASON: x', 'PLAN: 4 and 7\nREASON: x', 'plan: 4 | 7\nreason: x', 'PLAN: 4 then plan 7\nREASON: x']:
            r = judge.parse_choice(t, 9)
            self.assertFalse(r['ok'], t)
            self.assertIn('several plans', r['error'])
        for t in ['PLAN: 7.\nREASON: x', 'PLAN: 7 (the attack)\nREASON: x', '**PLAN: 7**\nREASON: x', 'PLAN: 7 (energy on 2)\nREASON: x']:
            self.assertEqual(judge.parse_choice(t, 9)['plan'], 7, t)

    def test_parsing_a_flood_of_blank_lines_is_fast(self):
        import time
        t0 = time.time()
        self.assertEqual(judge.parse_choice('\n' * 200000 + 'PLAN: 3\nREASON: x', 5)['plan'], 3)
        self.assertFalse(judge.parse_choice(' ' * 100000 + '\nPLAN: 3', 2)['ok'])
        self.assertEqual(judge.parse_choice('PLAN: 3' + ' ' * 100000, 5)['plan'], 3)  # trailing blanks are stripped before any matching
        self.assertLess(time.time() - t0, 5)

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


class ConcreteActionFormat(unittest.TestCase):
    """Pure Python, no binaries: the canonical concrete action label is Name#<compact JSON, keys sorted>."""
    def test_legacy_brace_labels_convert_losslessly(self):
        self.assertEqual(judge.concrete_label('DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0}'),
                         'DiscardToolFromPokemon#{"in_play_idx":2,"player":1,"tool_idx":0}')
        self.assertEqual(judge.concrete_label('ChooseRandomEvolutionTarget{in_play_idx:3}'), 'ChooseRandomEvolutionTarget#{"in_play_idx":3}')
        self.assertEqual(judge.concrete_label('X{flag:true,name:"a b"}'), 'X#{"flag":true,"name":"a b"}')

    def test_canonical_and_short_labels_pass_unchanged(self):
        for l in ['Attach:1Darkness@2 zone', 'EndTurn', 'DiscardToolFromPokemon', 'DiscardToolFromPokemon#{"in_play_idx":1,"player":1,"tool_idx":0}']:
            self.assertEqual(judge.concrete_label(l), l)

    def test_json_key_order_and_spacing_never_matter(self):
        a = judge.concrete_label('DiscardToolFromPokemon#{"tool_idx": 0, "player": 1, "in_play_idx": 2}')
        b = judge.concrete_label('DiscardToolFromPokemon#{"in_play_idx":2,"player":1,"tool_idx":0}')
        c = judge.concrete_label('DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0}')  # the legacy spelling of the same action
        self.assertEqual(a, b)
        self.assertEqual(b, c)
        self.assertEqual(b, 'DiscardToolFromPokemon#{"in_play_idx":2,"player":1,"tool_idx":0}')
        # raw UTF-8, as serde_json prints it
        self.assertEqual(judge.concrete_label('X#{"name": "Poké Ball"}'), 'X#{"name":"Poké Ball"}')
        with self.assertRaises(ValueError):
            judge.concrete_label('DiscardToolFromPokemon#{"tool_idx": 0,')  # not JSON: never guessed at

    def test_an_argument_is_never_dropped_to_the_bare_name(self):
        self.assertNotEqual(judge.concrete_label('ChooseRandomEvolutionTarget#{"in_play_idx":0}'), judge.concrete_label('ChooseRandomEvolutionTarget#{"in_play_idx":1}'))
        self.assertNotEqual(judge.concrete_label('ChooseRandomEvolutionTarget#{"in_play_idx":0}'), 'ChooseRandomEvolutionTarget')

    def test_a_legacy_label_that_cannot_be_read_without_loss_is_rejected(self):
        for l in ['Y{card:Some(Pawniard)}', 'Y{a:[1,2]}', 'Y{oops}']:
            with self.assertRaises(ValueError, msg=l):
                judge.concrete_label(l)

    def test_two_targets_are_never_resolved_to_the_first(self):
        rec = {'plans': [{'n': 1, 'key': 'a'}, {'n': 2, 'key': 'b'}]}
        with self.assertRaises(judge.AmbiguousPlan):
            judge.number_for(rec, ['a', 'b'])  # a bare name that fits both targets
        self.assertEqual(judge.number_for(rec, ['b', 'b']), 2)  # the same plan twice is not ambiguous

    def test_the_baseline_printer_patch_prints_all_arguments(self):
        src = open(os.path.join(HERE, '..', '..', 'results', 'pause_games_decisions_2026-10-02', 'harness', 'pgd_patch.py'), encoding='utf-8').read()
        self.assertIn('format!("{}#{}", name, m.values().next().unwrap())', src)
        rs = open(os.path.join(HERE, '..', 'plans', 'src', 'main.rs'), encoding='utf-8').read()
        self.assertIn('format!("{}#{}", name, m.values().next().unwrap())', rs)  # the same rule in both printers


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

    def test_the_lister_itself_reads_labels_whatever_their_json_key_order(self):
        # straight to the binary, bypassing judge.concrete_label: spaces and reversed key order must reach the same plan
        rec = plans(['MINI-BLOWER'])[0]['MINI-BLOWER']
        full = sorted({l for p in rec['plans'] for l in p['labels'] if l.startswith('DiscardToolFromPokemon#')})
        name, js = full[0].split('#', 1)
        obj = json.loads(js)
        scrambled = name + '#' + json.dumps(dict(reversed(list(obj.items()))), separators=(', ', ': '))
        self.assertNotEqual(scrambled, full[0])
        with tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps({'id': 'MINI-BLOWER', 'tag': 'plain', 'labels': ['Play:Field Blower', full[0]]}) + '\n')
            f.write(json.dumps({'id': 'MINI-BLOWER', 'tag': 'scrambled', 'labels': ['Play:Field Blower', scrambled]}) + '\n')
            path = f.name
        try:
            cmd = [judge.PLANS_BIN, '--positions', POS] + judge.deck_args(DECKS) + ['--replay', path]
            out = {json.loads(l)['tag']: json.loads(l) for l in subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.splitlines()}
        finally:
            os.unlink(path)
        self.assertTrue(out['plain']['ok'] and out['scrambled']['ok'], out)
        self.assertEqual(out['plain']['keys'], out['scrambled']['keys'])

    def test_a_random_evolution_target_keeps_its_own_identity(self):
        rec = plans(['MINI-QGE'])[0]['MINI-QGE']
        targets = {l for p in rec['plans'] for l in p['labels'] if l.startswith('ChooseRandomEvolutionTarget')}
        self.assertEqual(len(targets), 2, targets)  # two Bulbasaur: two different labels, each with its slot
        self.assertTrue(all('in_play_idx' in t for t in targets))
        chosen = [p for p in rec['plans'] if p['labels'][-1] in targets and p['labels'][:-1] == ['Play:Quick-Grow Extract']]
        self.assertEqual(len(chosen), 2)
        self.assertTrue(all(p['end'] == 'chance' for p in chosen))  # the evolution drawn from the deck is a chance event: the plan stops at the choice
        full = sorted(targets)
        keys = judge.replay([('MINI-QGE', 'a', ['Play:Quick-Grow Extract', full[0]]), ('MINI-QGE', 'b', ['Play:Quick-Grow Extract', full[1]]),
                             ('MINI-QGE', 'bare', ['Play:Quick-Grow Extract', 'ChooseRandomEvolutionTarget'])], POS, DECKS)
        self.assertNotEqual(keys['a'], keys['b'])
        self.assertEqual(len(keys['bare']), 2)
        with self.assertRaises(judge.AmbiguousPlan):
            judge.number_for(rec, keys['bare'])  # a bare name is never resolved to the first target
        self.assertNotEqual(judge.number_for(rec, keys['a']), judge.number_for(rec, keys['b']))

    def test_playing_a_stadium_is_never_chance_and_using_mesagoza_always_is(self):
        rec = plans(['MINI-STADIUM'])[0]['MINI-STADIUM']
        play = [p for p in rec['plans'] if 'Play:Mesagoza' in p['labels']]
        self.assertTrue(play)
        for p in play:
            if p['labels'][-1] == 'Play:Mesagoza':
                self.assertNotEqual(p['end'], 'chance', p['labels'])  # playing the Stadium ends no plan by itself
        used = [p for p in rec['plans'] if 'UseStadium' in p['labels']]
        self.assertTrue(used)
        for p in used:
            self.assertEqual(p['labels'][-1], 'UseStadium')  # nothing follows the flip
            self.assertEqual(p['end'], 'chance')
            self.assertEqual(p['final']['kind'], 'coin_or_random')
            self.assertEqual(p['final']['branch_chances'][-1], 0.5)  # tails: nothing happens, 50%
        self.assertTrue(any(p['labels'][-1] == 'Play:Mesagoza' and p['end'] == 'end_turn' or p['end'] == 'attack' for p in play))

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


RET_POS = os.path.join(FIX, 'retreat_positions.json')
OLD_POS = judge.DEFAULT_POSITIONS  # the 92 old positions (stage A); present in the repository


@unittest.skipUnless(os.path.exists(judge.PLANS_BIN), 'judge_plans is not built')
class RetreatPaymentLabels(unittest.TestCase):
    """Oct 19 review finding: ChooseRetreatEnergy had the short label RetreatPay:<slot>, which dropped WHICH Energy was paid, so 1,142 of the 5,728 plans of the 92 old
    positions could not be named by their own labels. It now takes the Name#JSON fallback."""

    @classmethod
    def setUpClass(cls):
        cls.rec = judge.list_plans(['MINI-RETREAT'], RET_POS, DECKS)['MINI-RETREAT']

    def test_two_payments_are_two_labels_with_their_energy_and_a_readable_step(self):
        labels = {l for p in self.rec['plans'] for l in p['labels'] if l.startswith('ChooseRetreatEnergy')}
        self.assertEqual(labels, {'ChooseRetreatEnergy#{"energies":["Fire"],"to_in_play_idx":1}', 'ChooseRetreatEnergy#{"energies":["Water"],"to_in_play_idx":1}'})
        self.assertFalse(any('RetreatPay' in l for p in self.rec['plans'] for l in p['labels']))
        steps = {s for p in self.rec['plans'] for s in p['steps'] if 'retreat cost' in s}
        self.assertEqual(len(steps), 2, steps)
        self.assertTrue(all(s.startswith('Pay the retreat cost of Ponyta (Active) (switching with Vulpix (Bench 1)) by discarding ') for s in steps), steps)
        self.assertEqual(sorted(s.rsplit(' by discarding ', 1)[1] for s in steps), ['Fire Energy', 'Water Energy'])

    def test_every_plan_is_named_by_its_own_labels(self):
        check = judge.label_roundtrip({'MINI-RETREAT': self.rec}, RET_POS, DECKS)['MINI-RETREAT']
        self.assertEqual((check['ambiguous'], check['unfollowable'], check['unique']), (0, 0, self.rec['n_plans']))

    def test_a_reference_must_name_the_payment_and_a_bare_name_is_ambiguous(self):
        retreat = [p for p in self.rec['plans'] if p['end'] == 'end_turn' and p['labels'][0] == 'Retreat:1' and 'Water' in ''.join(p['labels'])]
        self.assertEqual(len(retreat), 1, [p['labels'] for p in self.rec['plans']])
        recs = {'MINI-RETREAT': self.rec}
        item = lambda tag, labels: ('MINI-RETREAT', tag, labels)
        out = judge.match_plans([item('full', retreat[0]['labels']), item('bare', ['Retreat:1', 'ChooseRetreatEnergy', 'EndTurn']),
                                 item('none', ['Retreat:1']),
                                 item('flipped', ['Retreat:1', 'ChooseRetreatEnergy#{"to_in_play_idx":1,"energies":["Water"]}', 'EndTurn'])], recs, RET_POS, DECKS)
        self.assertEqual(out['full'][0], retreat[0]['n'])
        self.assertEqual(out['flipped'][0], retreat[0]['n'])  # key order in a requested label never matters
        self.assertIsNone(out['bare'][0])
        self.assertTrue(out['bare'][1].startswith('ambiguous'), out['bare'])  # the bare name fits both payments: never resolved to the first
        self.assertIsNone(out['none'][0])
        self.assertIn('ChooseRetreatEnergy', out['none'][1])  # a retreat whose payment is not named cannot be followed: it says which payments were legal


@unittest.skipUnless(os.path.exists(judge.PLANS_BIN) and os.path.exists(OLD_POS), 'judge_plans or the old positions are not available')
class ReplayOnOldPositions(unittest.TestCase):
    def test_the_order_of_energies_in_a_requested_label_does_not_matter(self):
        pid = 'KW-261013_022530000-t09'
        rec = judge.list_plans([pid], OLD_POS)[pid]
        two = [(p, l) for p in rec['plans'] for l in p['labels'] if l.startswith('ChooseRetreatEnergy#') and len(json.loads(l.split('#', 1)[1])['energies']) >= 2]
        if not two:
            self.skipTest('no two-Energy payment in this list')
        p, label = two[0]
        body = json.loads(label.split('#', 1)[1])
        body['energies'] = list(reversed(body['energies']))
        flipped = [('ChooseRetreatEnergy#' + json.dumps(body)) if l == label else l for l in p['labels']]
        self.assertNotEqual(flipped, p['labels'])
        out = judge.match_plans([(pid, 'x', flipped)], {pid: rec}, OLD_POS)
        self.assertEqual(out['x'], (p['n'], None))

    def test_a_dead_alternative_does_not_take_a_followable_move_list_down(self):
        # the recorded plan of KW-261013_020824000-t03 places a Pawniard WITHOUT a slot and later attaches a Tool to slot 2: the slots where that later move is not legal
        # used to abort the whole list ("unresolved"); they are now pruned and the list resolves
        pid = 'KW-261013_020824000-t03'
        positions = judge.load_positions(OLD_POS)
        rec = judge.list_plans([pid], OLD_POS)[pid]
        out = judge.match_plans([(pid, 'h', positions[pid]['his_plan'])], {pid: rec}, OLD_POS)
        self.assertIsNotNone(out['h'][0], out)

    def test_every_listed_plan_of_the_old_positions_is_named_by_its_own_labels(self):
        ids = judge.resolve_ids(type('A', (), {'ids': None, 'id': None, 'set': 'stageA'}), judge.load_positions(OLD_POS))
        check = judge.label_roundtrip(judge.list_plans(ids, OLD_POS), OLD_POS)
        bad = {pid: v for pid, v in check.items() if v['ambiguous'] or v['unfollowable']}
        self.assertEqual(bad, {})
        self.assertEqual(sum(v['n_plans'] for v in check.values()), sum(v['unique'] for v in check.values()))


if __name__ == '__main__':
    unittest.main()
