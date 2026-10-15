#!/usr/bin/env python3
"""Tests for the pause-game converter (cardlib.py, deckspec.py, ledger_to_positions.py).

  cd rl/results/pause_games_new_2026-10-12/harness && python3 -B -m unittest -v test_ledger_to_positions

Written from the laptop's review of the first version (REVIEW_POSITIONS_laptop.md): every blocker and major finding has a test here. Most tests use small made-up games
(a deck file and a ledger written to a temporary folder) with real cards from the engine's database; the last class checks the review's named examples against the real
ledgers and is skipped when the Recording_QA folder is not on this machine."""
import collections, contextlib, glob, io, json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cardlib as C  # noqa: E402
import deckspec as D  # noqa: E402
import ledger_to_positions as L  # noqa: E402

QA = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'


# ------------------------------------------------------------------------------------------------------------- builders for made-up games
def entry(name, entity, **kw):
    d = {'name': name, 'entity_id': entity}
    d.update(kw)
    return d


def deck_json(qr=None, log=None, energy=None, status='filmed_QR_exact20_verified', **extra):
    j = {'schema': 'pause-games/deck-snapshot-v1', 'exact_list_status': status}
    if qr is not None:
        j['filmed_qr_cards_in_order'] = qr
    if log is not None:
        j['cards_in_log_order'] = log
    if energy is not None:
        j['energy_configuration_from_log'] = energy
    j.update(extra)
    return j


def mon(name, hp_max, hp=None, variant='', energy=None, tool='none', pos=None, conds=(), stack=None, **kw):
    d = {'name': name, 'variant': variant, 'hp_now': hp if hp is not None else hp_max, 'hp_max': hp_max, 'attached_energy': {'total': sum((energy or {}).values()), 'by_type': dict(energy or {})},
         'tool': tool, 'special_conditions': list(conds)}
    if pos is not None:
        d['bench_position'] = pos
    if stack is not None:
        d['evolution_stack'] = {'cards_bottom_to_top': stack}
    d.update(kw)
    return d


def board(active, bench=(), points=0, zone=None):
    return {'active': active, 'bench_in_position_order': list(bench), 'points': points,
            'energy_zone': zone or {'this_turn': {'type': 'Fighting', 'count': 1, 'available': True}, 'next': {'type': 'Fighting', 'count': 1, 'available': False}}}


def hand(*names):
    return {'cards_left_to_right': [{'name': n} for n in names], 'count': len(names)}


def play(kind, card=None, target=None, result='', **kw):
    d = {'kind': kind, 'card_name': card, 'target': target, 'result': result}
    d.update(kw)
    return d


def owner_turn(n, hand_names, owner_board, opp_board, plays, after=None, stadium='none', opp_hand=4):
    return {'turn_number': n, 'who_played': 'owner', 'hand_at_start': hand(*hand_names), 'opponent_hand_at_owner_turn_start': {'count': opp_hand},
            'board_at_start': {'owner': owner_board, 'opponent': opp_board, 'stadium': stadium}, 'plays_in_order': plays, 'board_after': {'owner': after or owner_board}}


def opp_turn(n, plays, opp_board=None, owner_board=None):
    return {'turn_number': n, 'who_played': 'opponent', 'plays_in_order': plays,
            'board_at_start': {'owner': owner_board or board(None), 'opponent': opp_board or board(None)}, 'board_after': {'owner': owner_board or board(None)}}


class MadeUpGame:
    """a temporary Recording_QA game folder"""

    def __init__(self, test, deck, turns):
        self.dir = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.dir, True)
        self.path = os.path.join(self.dir, '20269999_000000000_iOS')
        os.makedirs(self.path)
        for name, data in (('DECK_USED.json', deck), ('TURN_LEDGER.json', {'turns': turns})):
            with open(os.path.join(self.path, name), 'w', encoding='utf-8') as f:
                json.dump(data, f)

    def convert(self, entities=None):
        with contextlib.redirect_stdout(io.StringIO()):
            return L.convert_game(self.path, entities or {})


def fighting_deck():
    """20 cards: two Conkeldurr that are two cards (Guts / Mega Punch, and Bedrock Breaker), two Sandslash likewise, entity-only and printing-list entries"""
    qr = ([entry('Timburr', 6750, variant='A3 094')] * 2 + [entry('Gurdurr', 6760, variant='A3 095')] + [entry('Conkeldurr', 6770, variant='A3 096')] + [entry('Conkeldurr', 20500, variant='B4 089')]
          + [entry('Wally', 1570, printing_aliases=['B4 153', 'B4 193'])] * 2 + [entry('Poké Ball', 30, variant=['A2b 111', 'P-A 005'])] * 2 + [entry('Rare Candy', 480)] * 2
          + [entry('Professor’s Research', 40, variant='A4b 373 / P-A 007')] * 2 + [entry('Copycat', 990)] + [entry('Sandshrew', 14430, variant='B2 077 / B2 170')] * 2
          + [entry('Sandslash', 14440, variant='B2 078'), entry('Sandslash', 1380, variant='A1 138')] + [entry('Lucky Ice Pop', 1060)] * 2)
    assert len(qr) == 20, len(qr)
    return deck_json(qr=qr, energy=[{'name': 'Fighting', 'value': 6}])


GLOBAL = {480: ['A3 144', 'A4b 314'], 1060: ['B2 145'], 990: ['B1 225', 'B1 270']}


# ------------------------------------------------------------------------------------------------------------- cards
class Cards(unittest.TestCase):
    def test_two_cards_with_one_name_are_two_functions(self):
        self.assertEqual(len(C.functions('Conkeldurr')), 2)
        self.assertNotEqual(C.SIG['A3 096'], C.SIG['B4 089'])
        self.assertIn('Guts', C.titles(C.BYID['A3 096']))
        self.assertIn('Bedrock Breaker', C.titles(C.BYID['B4 089']))

    def test_printings_of_one_function_are_one_function(self):
        self.assertEqual(C.SIG['A2b 111'], C.SIG['P-A 005'])
        self.assertEqual(len(C.functions('Poké Ball')), 1)

    def test_names_are_the_engines(self):
        self.assertEqual(C.nname('Professor’s Research'), "Professor's Research")
        self.assertEqual(C.nname('Poke Ball'), 'Poké Ball')
        self.assertEqual(C.nname('Nidoran male'), 'Nidoran♂')

    def test_text_points_to_the_function_whatever_the_id_it_names(self):
        # the reader swapped two ids: the attack titles still say which card it is
        text = 'B1 172 Bedrock Breaker 100'
        best, amb = C.best(['A3 096', 'B4 089'], text, 150)
        self.assertEqual(best, ['B4 089'])
        self.assertFalse(amb)


# ------------------------------------------------------------------------------------------------------------- deck lists
class DeckLists(unittest.TestCase):
    def test_entity_entries_take_their_printings_from_the_aliases_variant_lists_and_two_printing_variants(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        self.assertEqual(sum(e.count for e in s.entries), 20)
        by = {(e.name, e.entity): e for e in s.entries}
        self.assertEqual(by[('Poké Ball', 30)].ids[0], 'A2b 111')
        self.assertEqual(by[('Wally', 1570)].ids, ['B4 153', 'B4 193'])
        self.assertEqual(by[('Professor\'s Research', 40)].ids[0], 'A4b 373')
        self.assertEqual(by[('Sandshrew', 14430)].ids, ['B2 077', 'B2 170'])

    def test_an_entity_with_no_printing_in_the_file_borrows_them_from_another_game(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        rc = next(e for e in s.entries if e.name == 'Rare Candy')
        self.assertEqual(rc.ids[0], 'A3 144')
        self.assertEqual(rc.how, 'entity seen in another game')

    def test_two_conkeldurr_are_two_entries_not_one(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        ck = [e for e in s.entries if e.name == 'Conkeldurr']
        self.assertEqual(sorted(e.ids[0] for e in ck), ['A3 096', 'B4 089'])
        self.assertEqual([e.count for e in ck], [1, 1])

    def test_a_log_list_with_exact_printings_keeps_two_functions_of_one_name_apart(self):
        log = [{'name': 'Conkeldurr', 'variant': 'A3 096'}, {'name': 'Conkeldurr', 'variant': 'B4 089'}] + [{'name': 'Poké Ball', 'variant': 'A2b 111'}] * 18
        s = D.read_deck(deck_json(log=log, status='verified_live_list_and_filmed_qr_game_binding'), {})
        self.assertEqual(sorted(e.ids[0] for e in s.entries if e.name == 'Conkeldurr'), ['A3 096', 'B4 089'])

    def test_a_name_whose_printings_are_not_in_the_files_and_has_several_functions_is_ambiguous(self):
        s = D.read_deck(deck_json(qr=[entry('Meowth', 14900), entry('Meowth', 1960)] + [entry('Poké Ball', 30, variant='A2b 111')] * 18), {})
        meow = [e for e in s.entries if e.name == 'Meowth']
        self.assertTrue(all(e.ambiguous for e in meow))
        self.assertEqual(len(meow[0].cands), 2)

    def test_energy_is_read_from_a_list_of_names_and_values_from_strings_and_from_the_qr_first(self):
        base = [entry('Poké Ball', 30, variant='A2b 111')] * 20
        self.assertEqual(D.read_deck(deck_json(qr=base, energy=[{'name': 'Fighting', 'value': 6}]), {}).energy, ['Fighting'])
        self.assertEqual(D.read_deck(deck_json(qr=base, energy='Water'), {}).energy, ['Water'])
        self.assertEqual(D.read_deck(deck_json(qr=base, energy=['Grass', 'Darkness']), {}).energy, ['Grass', 'Darkness'])
        j = deck_json(qr=base, energy=['Water'])
        j['filmed_qr_energy'] = [{'name': 'Fire', 'value': 2}]
        self.assertEqual(D.read_deck(j, {}).energy, ['Fire'], 'the filmed QR says what the game had')

    def test_a_file_with_no_20_card_list_gives_no_deck(self):
        self.assertIsNone(D.read_deck(deck_json(qr=[entry('Poké Ball', 30)] * 5), {}))

    def test_the_qr_list_is_the_game_s_when_the_live_log_is_another_version(self):
        qr = [entry('Combusken', 11260, variant='B1 044')] * 2 + [entry('Poké Ball', 30, variant='A2b 111')] * 18
        log = [{'name': 'Rare Candy', 'variant': 'A3 144'}] * 2 + [{'name': 'Poké Ball', 'variant': 'A2b 111'}] * 18
        s = D.read_deck(deck_json(qr=qr, log=log, status='exact_live_log_20_slot_snapshot_saved_but_game_version_conflict'), {})
        self.assertEqual(s.source, 'qr')
        self.assertIn('Combusken', {e.name for e in s.entries})
        self.assertFalse(s.version_unverified)

    def test_a_deck_the_files_call_a_different_version_is_marked_unverified(self):
        s = D.read_deck(deck_json(log=[{'name': 'Poké Ball', 'variant': 'A2b 111'}] * 20, status='verified_live_list_game_version_unverified'), {})
        self.assertTrue(s.version_unverified)


# ------------------------------------------------------------------------------------------------------------- settling a deck and placing cards
def led_with(*pokemon):
    """a ledger that only shows his Pokemon (name, variant, hp_max) on his board"""
    turns = [{'turn_number': 2, 'who_played': 'owner', 'board_at_start': {'owner': board(mon(n, hp, variant=v)), 'opponent': board(None)}, 'board_after': {'owner': board(mon(n, hp, variant=v))}}
             for n, v, hp in pokemon]
    return {'turns': turns}


class Settling(unittest.TestCase):
    def test_two_meowth_entries_get_two_different_functions_by_what_the_ledger_shows(self):
        s = D.read_deck(deck_json(qr=[entry('Meowth', 14900), entry('Meowth', 1960)] + [entry('Poké Ball', 30, variant='A2b 111')] * 18), {})
        L.settle_deck(s, led_with(('Meowth', 'Carefree Steps / Feelin’ Fine, 50 HP', 50), ('Meowth', 'Pay Day, 60 HP', 60)))
        self.assertEqual(sorted(e.rid for e in s.entries if e.name == 'Meowth'), ['A1 196', 'B2 124'])

    def test_a_name_the_ledger_cannot_settle_is_flagged_not_silently_guessed(self):
        s = D.read_deck(deck_json(qr=[entry('Meowth', 14900), entry('Meowth', 1960)] + [entry('Poké Ball', 30, variant='A2b 111')] * 18), {})
        L.settle_deck(s, led_with())
        self.assertTrue(any(e.flag for e in s.entries if e.name == 'Meowth'))

    def test_a_pokemon_on_the_board_is_the_card_its_attacks_say_it_is(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        L.settle_deck(s, led_with())
        a = L.Alloc(s)
        self.assertEqual(a.take('Conkeldurr', text='Bedrock Breaker100; discard a Stadium', hp=150), 'B4 089')
        self.assertEqual(a.take('Conkeldurr', text='Guts / Mega Punch80', hp=150), 'A3 096')

    def test_a_card_in_hand_is_what_the_board_and_the_discard_leave(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        L.settle_deck(s, led_with())
        a = L.Alloc(s)
        a.take('Conkeldurr', text='Guts / Mega Punch80', hp=150)       # one is on the board
        self.assertEqual(a.take('Conkeldurr'), 'B4 089', 'the other is in his hand')
        self.assertEqual(a.flags, [])

    def test_a_hand_card_with_two_functions_left_and_no_evidence_is_flagged(self):
        s = D.read_deck(fighting_deck(), GLOBAL)
        L.settle_deck(s, led_with())
        a = L.Alloc(s)
        a.take('Conkeldurr')
        self.assertTrue(a.flags)


class Opponent(unittest.TestCase):
    def test_the_printing_is_chosen_by_attack_titles_anywhere_in_the_text_not_only_at_its_start(self):
        # a name with two functions of one HP that differ in their attacks
        found = None
        for name in C.BYNAME:
            by = collections.defaultdict(list)
            for c in C.BYNAME[name]:
                if C.is_pokemon(c):
                    by[c['hp']].append(c['id'])
            for hp, ids in by.items():
                fs = {C.SIG[i]: i for i in ids}
                if len(fs) > 1:
                    a, b = list(fs.values())[:2]
                    ta, tb = set(C.titles(C.BYID[a])), set(C.titles(C.BYID[b]))
                    if ta - tb and tb - ta:
                        found = (name, hp, a, b, sorted(tb - ta)[0])
                        break
            if found:
                break
        name, hp, a, b, title = found
        chosen, alts = L.opp_pick(name, hp, [f'shiny artwork; {title} 30'])
        self.assertEqual(chosen, b)
        self.assertEqual(alts, [])

    def test_an_opponent_card_the_ledger_cannot_settle_is_listed_as_ambiguous(self):
        found = next(n for n in C.BYNAME if len(C.functions(n)) > 1 and all(C.is_pokemon(C.BYID[f[0]]) for f in C.functions(n)) and len({C.BYID[f[0]]['hp'] for f in C.functions(n)}) == 1)
        hp = C.BYID[C.functions(found)[0][0]]['hp']
        chosen, alts = L.opp_pick(found, hp, ['no description'])
        self.assertTrue(alts)


# ------------------------------------------------------------------------------------------------------------- a made-up game through the converter
def fighting_game(test):
    own0 = board(mon('Timburr', 60, variant='A3 094 Corkscrew Punch', pos=None), [mon('Timburr', 60, variant='A3 094 Corkscrew Punch', pos=1)])
    opp0 = board(mon('Stakataka', 110, variant='Brass Rock 40', energy={'Metal': 2}), [])
    t2 = owner_turn(2, ['Wally', 'Gurdurr', 'Conkeldurr', 'Poké Ball', 'Copycat'], own0, opp0, [
        play('card_play_attempt', 'Wally', 'benched Timburr', 'Energy destination prompt shown'),
        play('prompt_response', 'Wally', 'Wally selection', 'Cancel; no Energy attached, card returned to hand', response='Cancel'),
        play('card_play', 'Poke Ball', 'owner hand', 'No effect: no target in deck'),
        play('card_play', 'Wally', 'owner Active Timburr', 'Attach one Colorless Energy to Stage2'),
        play('evolution', 'Gurdurr', 'owner Active', 'Evolve Active Timburr'),
        play('energy_attachment', None, 'owner Active', 'Attach Fighting from zone', energy={'type': 'Fighting', 'count': 1}),
        play('attack', 'Gurdurr', 'opponent Active', 'Strength40'),
        play('end_turn', None, None, '')], after=board(mon('Gurdurr', 90, variant='Strength40', energy={'Fighting': 1, 'Colorless': 1}), [mon('Timburr', 60, pos=1)]))
    p3 = opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Active Gurdurr', '40 damage. Stakataka gains next-owner-turn 20-damage reduction.')])
    own4 = board(mon('Gurdurr', 50, 90, variant='Strength40', energy={'Fighting': 1, 'Colorless': 1}), [mon('Timburr', 60, pos=1)])
    opp4 = board(mon('Stakataka', 110, variant='Brass Rock 40', energy={'Metal': 2}), [])
    t4 = owner_turn(4, ['Conkeldurr', 'Rare Candy'], own4, opp4, [
        play('evolution', 'Conkeldurr', 'owner Active Gurdurr', 'Evolve'),
        play('attack', 'Conkeldurr', 'opponent Active', 'Bedrock Breaker100; no Stadium in play'),
        play('end_turn', None, None, '')], after=own4)
    return MadeUpGame(test, fighting_deck(), [t2, p3, t4])


class ConvertedGame(unittest.TestCase):
    def setUp(self):
        self.game = fighting_game(self)
        self.pos, self.skipped, self.deck = self.game.convert(GLOBAL)

    def test_the_deck_keeps_both_conkeldurr_and_both_sandslash_and_the_game_s_energy(self):
        ids = {(c['name'], c['id']): c['count'] for c in self.deck['cards']}
        self.assertEqual(ids[('Conkeldurr', 'A3 096')], 1)
        self.assertEqual(ids[('Conkeldurr', 'B4 089')], 1)
        self.assertEqual(ids[('Sandslash', 'B2 078')], 1)
        self.assertEqual(ids[('Sandslash', 'A1 138')], 1)
        self.assertEqual(self.deck['energy'], ['Fighting'])
        self.assertEqual(sum(c['count'] for c in self.deck['cards']), 20)

    def test_the_conkeldurr_in_his_hand_is_the_one_whose_attack_he_used(self):
        t4 = next(p for p in self.pos if p['turn_count'] == 4)
        self.assertIn('Conkeldurr B4 089', t4['me']['hand'])
        self.assertIn('Attack:Bedrock Breaker', t4['his_plan'])

    def test_a_cancelled_wally_is_not_a_move_and_the_one_he_played_is_play_wally_then_its_energy_target(self):
        t2 = next(p for p in self.pos if p['turn_count'] == 2)
        self.assertEqual(t2['his_plan'][:2], ['Play:Wally', 'Attach:1Colorless@0 fx'])
        self.assertEqual(t2['his_plan'].count('Play:Wally'), 1)

    def test_a_poke_ball_that_found_nothing_is_not_in_his_plan(self):
        t2 = next(p for p in self.pos if p['turn_count'] == 2)
        self.assertNotIn('Play:Poké Ball', t2['his_plan'])

    def test_energy_is_his_decks_not_water(self):
        t2 = next(p for p in self.pos if p['turn_count'] == 2)
        self.assertEqual(t2['me']['energy_next'], 'Fighting')

    def test_an_effect_the_opponent_s_last_attack_left_is_carried_to_the_pokemon_it_is_on(self):
        t4 = next(p for p in self.pos if p['turn_count'] == 4)
        stak = t4['opp']['board'][0]
        self.assertEqual(stak.get('effects'), [{'effect': {'ReducedDamage': {'amount': 20}}, 'turns': 1}])

    def test_the_plan_of_a_turn_that_only_ended_is_marked_ended(self):
        game = MadeUpGame(self, fighting_deck(), [owner_turn(2, ['Gurdurr'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn', None, None, '')])])
        pos, _, _ = game.convert(GLOBAL)
        self.assertEqual(pos[0]['his_plan'], [])
        self.assertTrue(pos[0]['his_plan_ended'])

    def test_a_game_whose_deck_version_is_unverified_has_unusable_positions(self):
        deck = deck_json(log=[{'name': 'Timburr', 'variant': 'A3 094'}] * 20, status='verified_live_list_game_version_unverified', energy='Fighting')
        game = MadeUpGame(self, deck, [owner_turn(2, ['Timburr'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])])
        pos, _, _ = game.convert({})
        self.assertFalse(pos[0]['usable'])
        self.assertIn('not this game', pos[0]['usable_reason'])


class CarriedEffects(unittest.TestCase):
    """what the opponent's last attack leaves on the board for his turn (the review's Brass Rock, Mach Stealth and Pile-Driving Hammer)"""

    def game(self, attack_card_name, attacker, result, mine_after, mine_now, defender_name='Timburr'):
        own_before = board(mon(defender_name, 60), mine_after)
        opp_board = board(mon(attacker, 150, energy={'Fighting': 3}), [])
        t2 = owner_turn(2, ['Gurdurr'], own_before, opp_board, [play('end_turn')], after=own_before)
        p3 = opp_turn(3, [play('attack', attack_card_name, 'owner Active', result)], opp_board=opp_board)
        p3['board_after'] = {'owner': board(mon(defender_name, 60), mine_after), 'opponent': opp_board}
        t4 = owner_turn(4, ['Gurdurr'], board(mine_now[0], mine_now[1:]), opp_board, [play('end_turn')])
        return MadeUpGame(self, fighting_deck(), [t2, p3, t4])

    def test_mach_stealth_follows_a_knock_out_by_garchomp_even_when_the_ledger_names_only_the_attack(self):
        g = self.game('Land Crush', 'Garchomp', '120 damage, Timburr HP0, KO', [mon('Timburr', 60, pos=1)], [mon('Timburr', 60)])
        pos, _, _ = g.convert(GLOBAL)
        p4 = next(p for p in pos if p['turn_count'] == 4)
        self.assertEqual(p4['opp']['board'][0].get('effects'), [{'effect': 'PreventAllDamageAndEffects', 'turns': 1}])

    def test_mach_stealth_needs_a_knock_out(self):
        g = self.game('Land Crush', 'Garchomp', '120 damage, Timburr survives', [mon('Timburr', 60, pos=1)], [mon('Timburr', 60), mon('Timburr', 60, pos=1)])
        pos, _, _ = g.convert(GLOBAL)
        p4 = next(p for p in pos if p['turn_count'] == 4)
        self.assertNotIn('effects', p4['opp']['board'][0])

    def test_pile_driving_hammer_costs_his_defending_pokemon_more_if_it_is_still_there(self):
        g = self.game("Team Rocket's Tinkaton: Pile-Driving Hammer", "Team Rocket's Tinkaton", '80 damage', [mon('Timburr', 60, pos=1)], [mon('Timburr', 60), mon('Timburr', 60, pos=1)])
        pos, _, _ = g.convert(GLOBAL)
        p4 = next(p for p in pos if p['turn_count'] == 4)
        self.assertEqual(p4['me']['board'][0].get('effects'), [{'effect': {'IncreasedAttackCost': {'amount': 2}}, 'turns': 1}, {'effect': {'IncreasedRetreatCost': {'amount': 2}}, 'turns': 1}])

    def test_pile_driving_hammer_does_nothing_to_a_pokemon_that_was_knocked_out(self):
        g = self.game("Team Rocket's Tinkaton: Pile-Driving Hammer", "Team Rocket's Tinkaton", '80 damage, KO', [mon('Timburr', 60, pos=1)], [mon('Gurdurr', 90)])
        pos, _, _ = g.convert(GLOBAL)
        p4 = next(p for p in pos if p['turn_count'] == 4)
        self.assertNotIn('effects', p4['me']['board'][0])


class BetweenTurns(unittest.TestCase):
    """what he has used up by the next turn: Lucky Ice Pop (heads brings it back, tails discards it), his own Stadium replaced by his own, a Rare Candy, cards milled"""

    def three_turns(self, plays2, plays4, hand6=('Wally',), own=None, stadium6='none', opp_row=None):
        own = own or board(mon('Timburr', 60), [])
        opp = board(mon('Stakataka', 110), [])
        turns = [owner_turn(2, ['Lucky Ice Pop', 'Lucky Ice Pop', 'Wally'], own, opp, plays2, after=own),
                 opp_turn(3, [], opp_board=opp), owner_turn(4, ['Wally'], own, opp, plays4, after=own),
                 opp_row or opp_turn(5, [], opp_board=opp), owner_turn(6, list(hand6), own, opp, [play('end_turn')], stadium=stadium6)]
        return turns

    def convert(self, turns, deck=None):
        return MadeUpGame(self, deck or fighting_deck(), turns).convert(GLOBAL)[0]

    def test_a_lucky_ice_pop_that_came_back_on_heads_is_not_in_the_discard_and_one_on_tails_is(self):
        heads = [play('card_play', 'Lucky Ice Pop', 'owner Active', 'Heal 10 to 20; heads; returns Pop')]
        tails = [play('card_play', 'Lucky Ice Pop', 'owner Active', 'Heal 10 to 20; tails; discarded')]
        p6 = self.convert(self.three_turns(heads, tails))[-1]
        self.assertEqual(p6['me']['discard'].count('Lucky Ice Pop B2 145'), 1, 'only the tails one')
        p6 = self.convert(self.three_turns(heads, heads))[-1]
        self.assertNotIn('Lucky Ice Pop B2 145', p6['me']['discard'])

    def test_a_stadium_of_his_replaced_by_another_of_his_goes_to_his_discard(self):
        deck = deck_json(qr=[entry('Timburr', 6750, variant='A3 094')] * 2 + [entry('Arena of Antiquity', 1, variant='B3 154'), entry('Hiking Trail', 2, variant='B2b 069')] + [entry('Poké Ball', 30, variant='A2b 111')] * 16,
                         energy='Fighting')
        turns = self.three_turns([play('stadium', 'Arena of Antiquity', 'shared', 'Put into play')], [play('stadium', 'Hiking Trail', 'shared', 'Replace Arena of Antiquity')], stadium6='Hiking Trail')
        # the cards he plays must be in his hand in the made-up turns
        turns[0]['hand_at_start'] = hand('Arena of Antiquity', 'Poké Ball')
        turns[2]['hand_at_start'] = hand('Hiking Trail')
        turns[4]['hand_at_start'] = hand('Poké Ball')
        p6 = self.convert(turns, deck)[-1]
        self.assertIn('Arena of Antiquity B3 154', p6['me']['discard'])
        self.assertEqual(p6['stadium'], {'card': 'Hiking Trail B2b 069', 'owner': 0})

    def test_a_pokemon_a_rare_candy_evolved_has_no_stage_1_under_it(self):
        a = mon('Timburr', 60, instance_id='A')
        after = board(mon('Conkeldurr', 150, variant='Bedrock Breaker100', instance_id='A'), [])
        turns = [owner_turn(2, ['Wally', 'Rare Candy', 'Conkeldurr'], board(a, []), board(mon('Stakataka', 110), []),
                            [play('item', 'Rare Candy', 'A', 'Evolve Timburr directly to Conkeldurr')], after=after),
                 opp_turn(3, []), owner_turn(4, ['Wally'], after, board(mon('Stakataka', 110), []), [play('end_turn')], after=after)]
        pos = MadeUpGame(self, fighting_deck(), turns).convert(GLOBAL)[0]
        p4 = next(p for p in pos if p['turn_count'] == 4)
        self.assertEqual([x.rsplit(' ', 2)[0] for x in p4['me']['board'][0]['behind']], ['Timburr'])

    def test_a_hand_that_holds_every_copy_left_of_a_name_is_not_flagged_but_one_of_two_is(self):
        both = MadeUpGame(self, fighting_deck(), [owner_turn(2, ['Conkeldurr', 'Conkeldurr'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])]).convert(GLOBAL)[0][0]
        self.assertNotIn('not told by the ledger', both['notes'])
        self.assertEqual(sorted(both['me']['hand']), ['Conkeldurr A3 096', 'Conkeldurr B4 089'])
        one = MadeUpGame(self, fighting_deck(), [owner_turn(2, ['Conkeldurr'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])]).convert(GLOBAL)[0][0]
        self.assertIn('not told by the ledger', one['notes'])

    def test_cards_the_opponents_attack_milled_are_said_to_be_unknown(self):
        opp = board(mon('Stakataka', 110), [])
        row = opp_turn(5, [play('attack', 'Mega Gyarados ex', 'owner Active', 'Mega Blaster140:160→20, discard top3 owner deck')], opp_board=opp)
        p6 = self.convert(self.three_turns([play('end_turn')], [play('end_turn')], opp_row=row))[-1]
        self.assertIn('discarded the top 3 cards of his deck', p6['notes'])


class PlanSteps(unittest.TestCase):
    def two_weezing_game(self, plays, hand_names=('Team Rocket’s Weezing ex',)):
        deck = deck_json(qr=[entry('Team Rocket’s Koffing', 1, variant='B4a 042')] * 2 + [entry('Team Rocket’s Weezing ex', 2, variant='B4a 043')] * 2 + [entry('Poké Ball', 30, variant='A2b 111')] * 16,
                         energy='Darkness')
        own = board(mon('Team Rocket’s Koffing', 60, variant='Reverse Thrust 10; 60 HP'), [])
        opp = board(mon('Goomy', 50), [])
        return MadeUpGame(self, deck, [owner_turn(4, list(hand_names), own, opp, plays)])

    def test_boiler_smog_logged_as_a_prompt_answer_is_an_ability_step(self):
        g = self.two_weezing_game([play('card_play', 'Team Rocket’s Weezing ex', 'owner Active Koffing', 'Evolve'),
                                   play('prompt_response', None, 'opponent Active Goomy', 'Boiler Smog accepted; Goomy becomes Poisoned and Burned', prompt_text='Use the effect of Boiler Smog?', response='Yes'),
                                   play('end_turn')])
        pos, _, _ = g.convert({})
        self.assertEqual(pos[0]['his_plan'], ['Evolve:Team Rocket\'s Weezing ex@0', 'Ability'])

    def test_boiler_smog_as_the_response_of_the_evolution_row_is_one_ability_step(self):
        g = self.two_weezing_game([play('card_play', 'Team Rocket’s Weezing ex', 'owner Active Koffing', 'Evolve to 140 HP', response='Use Boiler Smog'), play('end_turn')])
        pos, _, _ = g.convert({})
        self.assertEqual(pos[0]['his_plan'], ['Evolve:Team Rocket\'s Weezing ex@0', 'Ability'])

    def test_a_declined_boiler_smog_is_not_a_step(self):
        g = self.two_weezing_game([play('card_play', 'Team Rocket’s Weezing ex', 'owner Active Koffing', 'Evolve'),
                                   play('prompt_response', None, 'Boiler Smog', 'Decline the effect', prompt_text='Use Boiler Smog?', response='Cancel'), play('end_turn')])
        pos, _, _ = g.convert({})
        self.assertEqual(pos[0]['his_plan'], ['Evolve:Team Rocket\'s Weezing ex@0'])


class Flags(unittest.TestCase):
    def test_no_name_stands_for_a_flag_the_printing_decides(self):
        import position_list as PL
        togekiss_flagged = PL.AFFECTED_IDS.get('A4 080')
        self.assertTrue(togekiss_flagged, 'Togekiss A4 080 (Celestial Blessing) is on the switch 2 list')
        # an ordinary Meowth is not: only the Carefree Steps card is
        self.assertIn('B2 124', PL.AFFECTED_IDS)
        self.assertNotIn('A1 196', PL.AFFECTED_IDS)


# ------------------------------------------------------------------------------------------------------------- what the three audits of the regenerated positions found
def real_deck(*groups, fill='Poké Ball', energy='Fighting'):
    """a 20-card QR deck from (name, printing id, count) groups, filled up with Poké Balls"""
    qr = []
    for i, (name, pid, n) in enumerate(groups):
        qr += [entry(name, 9000 + i, variant=pid)] * n
    qr += [entry(fill, 30, variant='A2b 111')] * (20 - len(qr))
    assert len(qr) == 20, len(qr)
    return deck_json(qr=qr, energy=energy)


class AuditFixes(unittest.TestCase):
    def convert(self, deck, turns):
        return MadeUpGame(self, deck, turns).convert({})[0]

    def at(self, pos, turn):
        return next(p for p in pos if p['turn_count'] == turn)

    # (a) a card of the hand: the ledger reads text on it
    def test_a_hand_card_is_the_function_its_variant_text_names_whatever_the_id_beside_it_says(self):
        deck = real_deck(('Aegislash', 'B1 172', 1), ('Aegislash', 'B2 120', 1), ('Doublade', 'B1 171', 1), ('Doublade', 'B2 119', 1), ('Honedge', 'B2 118', 2))
        t = owner_turn(2, ['Aegislash', 'Aegislash', 'Doublade'], board(mon('Honedge', 70), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        t['hand_at_start'] = {'count': 3, 'cards_left_to_right': [
            {'name': 'Aegislash', 'variant': 'B2 120; Cursed Metal / Slicing Blade 70, HP140'},       # the ledger's ids are swapped: the attack titles are not
            {'name': 'Aegislash', 'variant': 'B1 172; Superb Shield 80, HP140'},
            {'name': 'Doublade', 'variant': 'B1 171; Dual Blades40x, HP90'}]}
        p = self.convert(deck, [t])[0]
        self.assertEqual(p['me']['hand'], ['Aegislash B1 172', 'Aegislash B2 120', 'Doublade B2 119'])
        self.assertNotIn('not told by the ledger', p['notes'])

    # (b) Quick-Grow Extract evolves at once
    def test_the_attack_after_a_quick_grow_extract_is_the_evolved_pokemons(self):
        deck = real_deck(('Caterpie', 'B3b 001', 2), ('Metapod', 'B3b 002', 2), ('Quick-Grow Extract', 'B1a 067', 2))
        t = owner_turn(3, ['Quick-Grow Extract', 'Poké Ball'], board(mon('Caterpie', 40, variant='Hook 30; 40 HP'), []), board(mon('Stakataka', 110), []), [
            play('card_play', 'Quick-Grow Extract', 'Caterpie Active', 'Find and directly evolve into Metapod; preserve10damage,70/80HP'),
            play('attack', 'Metapod', 'Budew Active', 'Ram30 KO; owner point1')])
        p = self.convert(deck, [t])[0]
        self.assertEqual(p['his_plan'], ['Play:Quick-Grow Extract', 'Attack:Ram'])

    # (c) Turbo Shark's Energy goes where the prompt chose
    def test_turbo_sharks_energy_target_is_the_pokemon_the_prompt_selected_not_the_one_named_after(self):
        deck = real_deck(('Carvanha', 'B4 034', 2), ('Mega Sharpedo ex', 'B4 035', 2), ('Wailord', 'B1 057', 2), ('Suicune ex', 'A4a 020', 2), energy='Water')
        own = board(mon('Mega Sharpedo ex', 190, variant='Turbo Shark70, printed HP190'),
                    [mon('Wailord', 200, variant='Whale Pump 60+, printed HP200', pos=2), mon('Suicune ex', 140, variant='Legendary Pulse / Crystal Waltz, printed HP140', pos=3)])
        t = owner_turn(11, ['Carvanha'], own, board(mon('Stakataka', 110), []), [
            play('card_play', 'Carvanha', 'Bench1', 'Bench second Carvanha50.'),
            play('attack', 'Mega Sharpedo ex', 'Houndstone Active', 'Turbo Shark70:160→90; nested Energy destination prompt at472-475 selects Wailord Bench2, attach1 Water resolved at476. Carvanha remains at0 Energy.')])
        p = self.convert(deck, [t])[0]
        self.assertEqual(p['his_plan'], ['Place:Carvanha', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'])

    # (d) a Tool that left a Pokemon that is still there
    def test_a_tool_that_is_gone_from_a_pokemon_still_on_the_board_is_in_the_discard(self):
        deck = real_deck(('Honedge', 'B2 118', 2), ('Metal Core Barrier', 'B2 148', 2))
        before, after = board(mon('Honedge', 70), []), board(mon('Honedge', 70, tool='Metal Core Barrier'), [])
        turns = [owner_turn(2, ['Metal Core Barrier', 'Poké Ball'], before, board(mon('Stakataka', 110), []), [play('tool_attachment', 'Metal Core Barrier', 'owner Active Honedge', 'attached')], after=after),
                 opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Active', '60 damage')], owner_board=after),
                 owner_turn(4, ['Poké Ball'], board(mon('Honedge', 70, tool='none'), []), board(mon('Stakataka', 110), []), [play('end_turn')])]
        turns[1]['board_after'] = {'owner': board(mon('Honedge', 70, tool='Metal Core Barrier'), [])}
        turns[0]['board_after'] = {'owner': after}
        pos = self.convert(deck, turns)
        self.assertEqual(self.at(pos, 4)['me']['discard'], ['Metal Core Barrier B2 148'])
        # a Tool still attached is not discarded
        turns[2] = owner_turn(4, ['Poké Ball'], board(mon('Honedge', 70, tool='Metal Core Barrier'), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        self.assertEqual(self.at(self.convert(deck, turns), 4)['me']['discard'], [])

    # (e) which of two same-named Pokemon the opponent knocked out
    def test_the_knocked_out_honedge_is_the_one_whose_energy_is_not_on_the_board_any_more(self):
        deck = real_deck(('Honedge', 'B2 118', 2), ('Horsea', 'A4 041', 2))
        h1, h3 = mon('Honedge', 70, energy={'Metal': 2}, pos=1), mon('Honedge', 70, pos=3)
        turns = [owner_turn(2, ['Poké Ball'], board(mon('Horsea', 50), [h1, h3]), board(mon('Stakataka', 110), []), [play('end_turn')]),
                 opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Bench3', 'Bench3 removed')]),
                 owner_turn(4, ['Poké Ball'], board(mon('Horsea', 50), [mon('Honedge', 70, energy={'Metal': 2}, pos=1)]), board(mon('Stakataka', 110), []), [play('end_turn')])]
        pos = self.convert(deck, turns)
        p4 = self.at(pos, 4)
        self.assertEqual(p4['me']['discard_energy'], [])
        self.assertEqual(p4['me']['discard'], ['Honedge B2 118'])

    def test_energy_the_opponent_moved_off_a_pokemon_before_knocking_it_out_is_not_in_his_discard_and_a_blown_tool_is(self):
        deck = real_deck(('Horsea', 'A4 041', 2), ("Team Rocket's Koffing", 'B4a 042', 1), ('Small Balloon', 'B3b 064', 2))
        end = board(mon('Horsea', 50, energy={'Water': 1}), [mon("Team Rocket's Koffing", 60, tool='Small Balloon', pos=1), mon('Horsea', 50, pos=2)])
        turns = [owner_turn(2, ['Poké Ball'], end, board(mon('Stakataka', 110), []), [play('end_turn')]),
                 opp_turn(3, [play('ability', "Team Rocket's Raticate ex", 'opponent Active', 'Thieving Incisors moves one Water from Active Horsea to Raticate'),
                              play('card_play', 'Field Blower', 'owner Bench1', "Discards owner Koffing's Small Balloon"),
                              play('attack', "Team Rocket's Raticate ex", 'owner Active', 'Boost Dash70 knocks out Active Horsea50')]),
                 owner_turn(4, ['Poké Ball'], board(mon('Horsea', 50), [mon("Team Rocket's Koffing", 60, tool='none', pos=1)]), board(mon('Stakataka', 110), []), [play('end_turn')])]
        p4 = self.at(self.convert(deck, turns), 4)
        self.assertEqual(p4['me']['discard_energy'], [])
        self.assertEqual(sorted(p4['me']['discard']), ['Horsea A4 041', 'Small Balloon B3b 064'])

    # (f) the printing of a card under a Pokemon: what the ledger showed of that Pokemon earlier
    def test_a_stack_card_is_the_printing_the_ledger_showed_when_the_pokemon_was_still_that_stage(self):
        deck = real_deck(('Spritzee', 'B1 115', 1), ('Spritzee', 'B1a 035', 1), ('Aromatisse', 'B1 116', 1), ('Aromatisse', 'B1a 036', 1))
        t2 = owner_turn(2, ['Aromatisse', 'Poké Ball'], board(mon('Spritzee', 60, variant='Sweet Scent, 60 HP'), []), board(mon('Stakataka', 110), []), [
            play('card_play', 'Aromatisse', 'Spritzee Active', 'Evolves Spritzee into Aromatisse')], after=board(mon('Aromatisse', 100, variant='Perfume Blast 40, 100 HP'), []))
        t4 = owner_turn(4, ['Poké Ball'], board(mon('Aromatisse', 100, variant='Perfume Blast 40, 100 HP'), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        p4 = self.at(self.convert(deck, [t2, opp_turn(3, []), t4]), 4)
        self.assertEqual(p4['me']['board'][0]['card'], 'Aromatisse B1a 036')
        self.assertEqual(p4['me']['board'][0]['behind'], ['Spritzee B1a 035'])

    # (h) / (k) a Rare Candy whose target has no instance id
    def test_a_rare_candy_logged_by_the_name_it_evolved_into_leaves_no_stage_1_under_it(self):
        t2 = owner_turn(2, ['Rare Candy', 'Conkeldurr', 'Poké Ball'], board(mon('Timburr', 60, variant='Corkscrew Punch20'), [mon('Timburr', 60, pos=1)]), board(mon('Stakataka', 110), []), [
            play('item', 'Rare Candy', 'Timburr in owner Bench slot1', 'Evolve the left Timburr directly into Bedrock Conkeldurr150HP.')],
            after=board(mon('Timburr', 60), [mon('Conkeldurr', 150, variant='Bedrock Breaker100', pos=1)]))
        t4 = owner_turn(4, ['Poké Ball'], board(mon('Timburr', 60), [mon('Conkeldurr', 150, variant='Bedrock Breaker100', pos=1)]), board(mon('Stakataka', 110), []), [play('end_turn')])
        p4 = self.at(MadeUpGame(self, fighting_deck(), [t2, opp_turn(3, []), t4]).convert(GLOBAL)[0], 4)
        conk = next(b for b in p4['me']['board'] if b['card'].startswith('Conkeldurr'))
        self.assertEqual([x.rsplit(' ', 2)[0] for x in conk['behind']], ['Timburr'])
        self.assertNotIn('Gurdurr', ' '.join(p4['me']['hand'] + p4['me']['discard']))

    # (l) a knocked-out Rare Candy Pokemon takes no Stage 1 with it
    def test_the_knocked_out_rare_candy_pokemon_leaves_the_other_ones_stack_alone(self):
        a_before = mon('Timburr', 60, instance_id='A')
        b = mon('Conkeldurr', 150, variant='Bedrock Breaker100', instance_id='B', pos=1)
        a_after = mon('Conkeldurr', 150, variant='Guts / Mega Punch80', instance_id='A')
        t2 = owner_turn(2, ['Rare Candy', 'Conkeldurr', 'Wally'], board(a_before, [b]), board(mon('Stakataka', 110), []), [play('item', 'Rare Candy', 'A', 'Evolve Timburr directly to Conkeldurr')], after=board(a_after, [b]))
        p3 = opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Active', 'A knocked out')])
        t4 = owner_turn(4, ['Wally'], board(mon('Conkeldurr', 150, variant='Bedrock Breaker100', instance_id='B'), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        p4 = self.at(MadeUpGame(self, fighting_deck(), [t2, p3, t4]).convert(GLOBAL)[0], 4)
        self.assertEqual(sorted(x.rsplit(' ', 2)[0] for x in p4['me']['discard']), ['Conkeldurr', 'Rare Candy', 'Timburr'])      # no Gurdurr: the Rare Candy skipped it
        self.assertEqual([x.rsplit(' ', 2)[0] for x in p4['me']['board'][0]['behind']], ['Timburr', 'Gurdurr'])

    # (m) the Pokemon that retreated sits in the slot the other left
    def test_energy_attached_to_the_pokemon_that_just_retreated_goes_to_its_new_slot(self):
        a, b = mon('Timburr', 60, energy={'Fighting': 3}, instance_id='A'), mon('Timburr', 60, instance_id='B', pos=1)
        for target in ('A on bench1', 'Timburr on bench1'):
            ids_off = target.startswith('Timburr')
            if ids_off:
                a, b = mon('Timburr', 60, energy={'Fighting': 3}), mon('Timburr', 60, pos=1)
            t2 = owner_turn(2, ['Wally'], board(a, [b]), board(mon('Stakataka', 110), []), [
                play('retreat', 'Timburr', 'owner Active Timburr', 'A to bench1; B to Active; A pays1 Fighting' if not ids_off else 'retreat to bench1, the other Timburr to Active'),
                play('energy_attachment', None, target, 'Attach1 to the benched Timburr', energy={'type': 'Fighting', 'count': 1})])
            p = MadeUpGame(self, fighting_deck(), [t2]).convert(GLOBAL)[0][0]
            self.assertEqual(p['his_plan'][:2], ['Retreat:1', 'Attach:1Fighting@1 zone'], target)

    # (i) the Energy zone
    def test_the_energy_of_this_turn_and_of_the_next_come_from_the_zone_as_the_turn_ended_not_the_circle_that_had_not_loaded(self):
        def zone(this, nxt):
            return {'this_turn': {'type': this, 'count': 0 if this == 'none' else 1, 'available': this != 'none'}, 'next': {'type': nxt, 'count': 1, 'available': False}}
        own2 = board(mon('Timburr', 60), [], zone=zone('none', 'Darkness'))
        own4 = board(mon('Timburr', 60), [], zone=zone('none', 'Grass'))
        t2 = owner_turn(2, ['Wally'], own2, board(mon('Stakataka', 110), []), [play('energy_attachment', None, 'owner Active', 'One Darkness attached', energy={'type': 'Darkness', 'count': 1})],
                        after=board(mon('Timburr', 60), [], zone=zone('none', 'Grass')))
        t4 = owner_turn(4, ['Wally'], own4, board(mon('Stakataka', 110), []), [play('energy_attachment', None, 'owner Active', 'One Grass attached', energy={'type': 'Grass', 'count': 1})],
                        after=board(mon('Timburr', 60), [], zone=zone('none', 'Metal')))
        pos = MadeUpGame(self, fighting_deck(), [t2, opp_turn(3, []), t4]).convert(GLOBAL)[0]
        self.assertEqual((self.at(pos, 2)['me']['energy_now'], self.at(pos, 2)['me']['energy_next']), ('Darkness', 'Grass'))
        self.assertEqual((self.at(pos, 4)['me']['energy_now'], self.at(pos, 4)['me']['energy_next']), ('Grass', 'Metal'))

    # (j) the opponent's Stadium
    def test_using_the_opponents_stadium_is_a_stadium_step_not_an_ability(self):
        t = owner_turn(10, ['Wally'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [
            play('stadium_ability', 'Rainbow Cave', 'owner Energy Zone', 'Metal current Energy discarded and regenerated'), play('end_turn')],
            stadium={'name': 'Rainbow Cave', 'played_by': 'opponent'})
        p = MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]
        self.assertEqual(p['his_plan'], ['UseStadium'])
        self.assertEqual(p['stadium']['owner'], 1)

    # (g) No Abilities
    def test_prickly_powder_leaves_no_abilities_on_the_defending_pokemon_until_it_leaves_the_active_spot(self):
        t = owner_turn(3, ['Wally'], board(mon('Timburr', 60), []), board(mon('Budew', 30), []), [play('end_turn')])
        p1 = opp_turn(2, [play('attack', 'Budew: Prickly Powder', 'owner Active', 'Timburr loses all Abilities')], opp_board=board(mon('Budew', 30), []))
        p = MadeUpGame(self, fighting_deck(), [p1, t]).convert(GLOBAL)[0][0]
        self.assertEqual(p['me']['board'][0].get('effects'), [{'effect': 'NoAbilities', 'turns': 255}])

    # the panel's Chubby Cheer: a player-wide effect that reaches the opponent's NEXT turn
    def test_chubby_cheer_is_a_turn_effect_for_the_opponent_s_next_turn_and_other_lasting_effects_are_named(self):
        def with_attack(card_name):
            p1 = opp_turn(3, [play('attack', card_name, 'owner Active', '10 damage')], opp_board=board(mon('Happiny', 40), []))
            t = owner_turn(4, ['Wally'], board(mon('Timburr', 60), []), board(mon('Happiny', 40), []), [play('end_turn')])
            return MadeUpGame(self, fighting_deck(), [owner_turn(2, ['Wally'], board(mon('Timburr', 60), []), board(mon('Happiny', 40), []), [play('end_turn')]), p1, t]).convert(GLOBAL)[0][-1]
        p = with_attack('Happiny: Chubby Cheer')
        want = [{'turn': tk, 'effect': {'IncreasedDamageForPlayer': {'amount': 20, 'player': 1, 'energy_type': None}}} for tk in (4, 5)]
        self.assertEqual(p['turn_effects'], want)
        p = with_attack('Leafeon: Leafy Cyclone')
        self.assertEqual(p['turn_effects'], [])
        self.assertIn('is not carried into the position', p['notes'])

    def test_a_lucky_ice_pop_is_back_in_hand_on_heads_in_every_wording_the_ledgers_glue_it_in(self):
        for text, back in (('Heal110→130; Heads213 returns Pop to hand', True), ('Heals20 Mega40→60; coinHeads; same Item returned to hand.', True), ('Heal20:50→70. Heads at158; card returns to hand.', True),
                           ('Heals20 Mega60→80; coinTails; discarded.', False), ('Tails271 discards Pop', False), ('Heal 10; returns to hand', True), ('Heal 10; discarded', False), ('', False)):
            self.assertEqual(L.pop_returned(text), back, text)

    # (n) a search that found nothing, however the ledger hyphenates it
    def test_a_poke_ball_that_found_nothing_is_recognised_in_every_wording_the_ledgers_use(self):
        for text in ('No effect: no target in deck', 'No eligible Basic remains in deck: visible no-target message at268; card discarded', 'Unsuccessful search; nothing found'):
            self.assertTrue(L.NOTHING_FOUND.search(text), text)
        self.assertFalse(L.NOTHING_FOUND.search('Search finds Horsea'))

    # (p) the opponent's stack cards are guesses and are said to be
    def test_an_opponent_stack_card_that_could_be_two_functions_is_listed_as_ambiguous(self):
        opp = board(mon('Aromatisse', 100, variant='Perfume Blast 40, 100 HP'), [])
        t = owner_turn(2, ['Wally'], board(mon('Timburr', 60), []), opp, [play('end_turn')])
        p = MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]
        self.assertTrue(any(a['name'] == 'Spritzee' and a.get('under') == 'Aromatisse' for a in p['opp_ambiguous']), p['opp_ambiguous'])


# ------------------------------------------------------------------------------------------------------------- the opponent's discard and deck, the laptop's verify panel
def opp_row(n, plays, start, after, **extra):
    r = {'turn_number': n, 'who_played': 'opponent', 'plays_in_order': plays, 'board_at_start': {'owner': board(None), 'opponent': start}, 'board_after': {'owner': board(None), 'opponent': after}}
    r.update(extra)
    return r


class OpponentDiscard(unittest.TestCase):
    def three(self, opp_start, opp_after, opp_plays, own=None, **opp_extra):
        """his turn 2, the opponent's turn 3 (start -> after), his turn 4: the position at turn 4"""
        own = own or board(mon('Timburr', 60), [])
        t2 = owner_turn(2, ['Wally', 'Poké Ball'], own, opp_start, [play('end_turn')])
        t2['board_after']['opponent'] = opp_start
        t4 = owner_turn(4, ['Wally'], own, opp_after, [play('end_turn')])
        game = MadeUpGame(self, fighting_deck(), [t2, opp_row(3, opp_plays, opp_start, opp_after, **opp_extra), t4])
        return next(p for p in game.convert(GLOBAL)[0] if p['turn_count'] == 4)

    def test_a_pokemon_of_his_that_left_the_board_is_in_his_discard_with_its_stack_tool_and_energy(self):
        start = board(mon('Stakataka', 110, energy={'Metal': 2}), [mon('Seadra', 70, energy={'Water': 1}, tool='Small Balloon', pos=1)])
        after = board(mon('Stakataka', 110, energy={'Metal': 2}), [])
        p = self.three(start, after, [play('card_play', 'Professor’s Research', 'owner deck', 'draw 2'), play('item', 'Poké Ball', 'owner deck', 'found Horsea'), play('end_turn')])
        names = sorted(x.rsplit(' ', 2)[0] for x in p['opp']['discard'])
        self.assertEqual(names, ['Horsea', 'Poké Ball', 'Professor’s Research'.replace('’', "'"), 'Seadra', 'Small Balloon'])
        self.assertEqual(p['opp']['discard_energy'], ['Water'])
        self.assertNotIn('discard_n', p['opp'])
        self.assertNotIn('Stakataka', ' '.join(p['opp']['discard']))

    def test_cards_the_ledger_names_as_paid_to_attack_are_in_the_discard_and_unreadable_ones_are_counted_not_guessed(self):
        b = board(mon('Stakataka', 110, energy={'Metal': 2}), [])
        plays = [{'kind': 'attack', 'card_name': 'Gourgeist / Soul Shot', 'target': 'Active', 'result': 'Discards Chingling; damage 70',
                  'nested_events_in_order': [{'kind': 'attack_cost_discard', 'card_name': 'Chingling'}]},
                 {'kind': 'attack', 'card_name': 'Gourgeist / Soul Shot', 'target': 'Active', 'result': 'Hidden discard cost',
                  'nested_events_in_order': [{'kind': 'attack_cost_discard', 'card_name': None, 'limit_reason': 'Identity not readable'}]}]
        p = self.three(b, b, plays, automatic_events_in_order=[{'order': 1, 'event': 'Discard1 opponent hand card after attack selection. New top pile preview is Klefki.'}])
        self.assertEqual(sorted(x.rsplit(' ', 2)[0] for x in p['opp']['discard']), ['Chingling', 'Klefki'])
        self.assertEqual(p['opp']['discard_hidden'], 1)
        self.assertIn('lower bound', p['notes'])
        self.assertIn('hidden in the ledger', p['approximate_reason'])

    def test_a_lucky_ice_pop_that_came_back_and_a_cancelled_card_are_not_in_his_discard(self):
        b = board(mon('Stakataka', 110), [])
        p = self.three(b, b, [play('item', 'Lucky Ice Pop', 'Active', 'Heal 20; Heads at158; returns'), play('card_play_attempt', 'Poké Ball', 'owner deck', 'cancelled'), play('end_turn')])
        self.assertEqual(p['opp']['discard'], [])

    def test_his_stadium_replaced_by_another_goes_to_his_discard_and_an_energy_paid_to_retreat_too(self):
        b = board(mon('Stakataka', 110), [mon('Cubone', 60, pos=1)])
        t2 = owner_turn(2, ['Wally', 'Poké Ball'], board(mon('Timburr', 60), []), b, [play('end_turn')], stadium={'name': 'Hiking Trail', 'played_by': 'opponent'})
        t2['board_after']['opponent'] = b
        r3 = opp_row(3, [play('retreat', None, 'Stakataka', 'pays one Metal; Cubone promoted', energy={'retreat_payment_by_type': {'Metal': 1}})], b, b)
        r3['board_at_start']['stadium'] = {'name': 'Hiking Trail', 'played_by': 'opponent'}
        t4 = owner_turn(4, ['Wally'], board(mon('Timburr', 60), []), b, [play('end_turn')], stadium={'name': 'Arena of Antiquity', 'played_by': 'owner'})
        p = next(x for x in MadeUpGame(self, fighting_deck(), [t2, r3, t4]).convert(GLOBAL)[0] if x['turn_count'] == 4)
        self.assertEqual([x.rsplit(' ', 2)[0] for x in p['opp']['discard']], ['Hiking Trail'])
        self.assertEqual(p['opp']['discard_energy'], ['Metal'])

    def test_an_empty_deck_the_ledger_reports_is_a_deck_count_of_zero_for_the_side_it_names(self):
        b = board(mon('Stakataka', 110), [])
        p = self.three(b, b, [play('end_turn')], draws_and_searches=[{'kind': 'normal_draw_failed', 'limit_reason': 'Empty deck notice; no gained card'}])
        self.assertEqual(p['opp']['deck_count'], 0)
        self.assertNotIn('deck_count', p['me'])
        t4 = owner_turn(4, ['Wally'], board(mon('Timburr', 60), []), b, [play('end_turn')])
        t4['draws_and_searches'] = [{'kind': 'normal_draw_failed', 'limit_reason': 'Deck empty; normal draw yields zero cards.'}]
        t2 = owner_turn(2, ['Wally', 'Poké Ball'], board(mon('Timburr', 60), []), b, [play('end_turn')])
        pos = MadeUpGame(self, fighting_deck(), [t2, opp_row(3, [], b, b), t4]).convert(GLOBAL)[0]
        self.assertEqual(next(x for x in pos if x['turn_count'] == 4)['me']['deck_count'], 0)

    def test_the_opponent_s_rare_candy_leaves_no_stage_1_under_his_stage_2(self):
        start = board(mon('Dratini', 70), [])
        after = board(mon('Dragonite', 150), [])
        p = self.three(start, after, [play('item', 'Rare Candy', 'Dratini Active', 'Evolve Dratini directly into Dragonite'), play('end_turn')])
        drag = p['opp']['board'][0]
        self.assertEqual([x.rsplit(' ', 2)[0] for x in drag['behind']], ['Dratini'])
        self.assertIn('Rare Candy', ' '.join(p['opp']['discard']))

    def test_an_eevee_ex_that_became_a_glaceon_ex_is_an_evolution_not_a_knock_out(self):
        pairs, kos = L.match_boards([mon('Eevee ex', 90, pos=1)], [mon('Glaceon ex', 140, pos=1)])
        self.assertEqual(kos, [])
        self.assertEqual(len(pairs), 1)


class HandTextAndMill(unittest.TestCase):
    def test_a_hand_card_written_with_its_attack_after_the_name_is_that_function(self):
        deck = real_deck(('Aegislash', 'B1 172', 1), ('Aegislash', 'B2 120', 1), ('Honedge', 'B2 118', 2))
        t = owner_turn(2, ['Aegislash', 'Aegislash'], board(mon('Honedge', 70), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        t['hand_at_start'] = {'count': 2, 'cards_left_to_right': ['Aegislash (Cursed Metal / Slicing Blade)', 'Aegislash [B2 120 Superb Shield]']}
        p = MadeUpGame(self, deck, [t]).convert({})[0][0]
        self.assertEqual(p['me']['hand'], ['Aegislash B1 172', 'Aegislash B2 120'])
        self.assertNotIn('not told by the ledger', p['notes'])

    def test_a_card_the_opponent_s_attack_milled_and_the_ledger_shows_is_in_his_discard(self):
        b = board(mon('Stakataka', 110), [])
        t2 = owner_turn(2, ['Wally', 'Poké Ball'], board(mon('Timburr', 60), []), b, [play('end_turn')])
        t2['board_after']['opponent'] = b
        mill = {'kind': 'attack', 'card_name': 'Mega Gyarados ex', 'target': 'owner', 'result': 'Mega Blaster140; discard top3 owner deck',
                'nested_events_in_order': [{'kind': 'deck_mill', 'destination': 'Owner discard', 'count': 3, 'cards_in_reveal_order': [None, None, None], 'visible_final_discard_top': 'Copycat'}]}
        r3 = opp_row(3, [mill], b, b)
        t4 = owner_turn(4, ['Wally'], board(mon('Timburr', 60), []), b, [play('end_turn')])
        p = next(x for x in MadeUpGame(self, fighting_deck(), [t2, r3, t4]).convert(GLOBAL)[0] if x['turn_count'] == 4)
        self.assertIn('Copycat B1 225', p['me']['discard'])
        self.assertIn('the other 2 are not known', p['notes'])


# ------------------------------------------------------------------------------------------------------------- the review's named examples, against the real ledgers
@unittest.skipUnless(os.path.isdir(QA), 'the Recording_QA folder is not on this machine')
class ReviewExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dirs = sorted(glob.glob(QA + 'BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*'))
        cls.entities = D.global_entity_map(L.read_decks(cls.dirs).values())
        cls.cache = {}

    def game(self, short):
        if short not in self.cache:
            d = next(d for d in self.dirs if os.path.basename(d).replace('_iOS', '').endswith(short))
            with contextlib.redirect_stdout(io.StringIO()):
                self.cache[short] = L.convert_game(d, self.entities)
        return self.cache[short]

    def position(self, short, turn):
        return next(p for p in self.game(short)[0] if p['turn_count'] == turn)

    def deck(self, short):
        return {(c['name'], c['id']): c['count'] for c in self.game(short)[2]['cards']}

    def test_213625_the_caterpie_line_is_the_b3b_one_and_sunny_wind_is_payable(self):
        d = self.deck('20261004_213625000')
        self.assertIn(('Caterpie', 'B3b 001'), d)
        self.assertIn(('Butterfree', 'B3b 003'), d)
        p = self.position('20261004_213625000', 7)
        names = [b['card'] for b in p['me']['board']] + p['me']['hand']
        self.assertTrue(all(not n.startswith(('Butterfree A1', 'Caterpie A1')) for n in names))

    def test_012303_t11_the_winning_bedrock_breaker_is_the_b4_089_conkeldurr(self):
        p = self.position('20261010_012303000', 11)
        self.assertIn('Conkeldurr B4 089', p['me']['hand'])
        self.assertIn('Attack:Bedrock Breaker', p['his_plan'])

    def test_031138_012927_020518_carry_the_flagged_rules_switch_2_cards(self):
        self.assertIn(('Togekiss', 'A4 080'), self.deck('20261005_031138000'))
        self.assertIn(('Meowth', 'B2 124'), self.deck('20261006_012927000'))
        d = self.deck('20261006_020518000')
        self.assertIn(('Conkeldurr', 'A3 096'), d)
        self.assertIn(('Conkeldurr', 'B4 089'), d)

    def test_020518_is_a_fighting_deck(self):
        for p in self.game('20261006_020518000')[0]:
            self.assertNotEqual(p['me']['energy_next'], 'Water', p['id'])
            self.assertEqual(p['me']['energy_now'] in (None, 'Fighting'), True, p['id'])
        self.assertEqual(self.game('20261006_020518000')[2]['energy'], ['Fighting'])

    def test_every_deck_is_20_cards(self):
        for d in self.dirs:
            short = os.path.basename(d).replace('_iOS', '')
            try:
                deck = self.game(short)[2]
            except (ValueError, KeyError):
                continue
            self.assertEqual(sum(c['count'] for c in deck['cards']), 20, short)

    def test_003458_the_dragonair_is_the_b4_117_card_and_the_oricorio_game_names_its_printing(self):
        p = self.position('20261012_003458000', 5)
        drag = next(b for b in p['opp']['board'] if b['card'].startswith('Dragonair'))
        self.assertTrue(drag['card'].endswith('B4 117'), drag['card'])

    # ---- what the three audits found in the regenerated positions
    def test_audit_hand_cards_the_ledger_names_by_attack_title(self):
        for t in (2, 4, 6, 8):
            self.assertIn('Aegislash B2 120', self.position('20261005_032023000', t)['me']['hand'], t)
        self.assertIn('Doublade B2 119', self.position('20261005_034953000', 10)['me']['hand'])
        self.assertIn('Aegislash B1 172', self.position('20261005_034953000', 10)['me']['hand'])
        self.assertIn('Conkeldurr B4 089', self.position('20261010_013009000', 1)['me']['hand'])

    def test_audit_032023_the_knocked_out_honedge_took_no_energy_and_the_self_discarding_tool_is_in_the_discard(self):
        self.assertEqual(self.position('20261005_032023000', 10)['me']['discard_energy'], [])
        p12 = self.position('20261005_032023000', 12)
        self.assertEqual(p12['me']['discard_energy'], ['Metal'])
        self.assertEqual(p12['me']['discard'].count('Metal Core Barrier B2 148'), 1)
        p8 = self.position('20261005_032857000', 8)
        self.assertEqual(p8['me']['discard'].count('Metal Core Barrier B2 148'), 2)

    def test_audit_020258_the_moved_water_and_the_blown_away_balloon(self):
        for t in (4, 6, 8):
            p = self.position('20261010_020258000', t)
            self.assertEqual(p['me']['discard_energy'], [], t)
            self.assertIn('Small Balloon B3b 064', p['me']['discard'], t)
        self.assertNotIn('Play:Poké Ball', self.position('20261010_020258000', 6)['his_plan'])

    def test_audit_plan_steps_of_003547_021629_213625_012927(self):
        self.assertEqual(self.position('20261005_003547000', 11)['his_plan'][-2:], ['Attack:Turbo Shark', 'Attach:1Water@1 fx'])
        for t in (20, 22):
            self.assertEqual(self.position('20261010_021629000', t)['his_plan'][:2], ['Retreat:2', 'Attach:1Water@2 zone'], t)
        p = self.position('20261004_213625000', 3)
        self.assertEqual(p['his_plan'][-1], 'Attack:Ram')
        self.assertEqual(p['me']['board'][0].get('effects'), [{'effect': 'NoAbilities', 'turns': 255}])
        self.assertEqual(self.position('20261006_012927000', 10)['his_plan'][0], 'UseStadium')

    def test_audit_stacks_of_031138_012303_014541_021629(self):
        self.assertEqual(self.position('20261005_031138000', 6)['me']['board'][0]['behind'], ['Spritzee B1a 035'])
        for t in (5, 7):
            conk = self.position('20261010_012303000', t)['me']['board'][0]
            self.assertEqual([x.rsplit(' ', 2)[0] for x in conk['behind']], ['Timburr'], t)
        for t in (5, 7):
            self.assertEqual(self.position('20261010_014541000', t)['me']['board'][0]['behind'], ['Horsea A4 041'], t)
        p24 = self.position('20261010_021629000', 24)
        self.assertIn('Kingdra ex A4 043', p24['me']['discard'])
        self.assertNotIn('Seadra A1 071', p24['me']['discard'])
        self.assertEqual(p24['me']['board'][0]['behind'], ['Horsea A4 041', 'Seadra A1 071'])

    def test_audit_183108_the_opponent_possible_column_does_not_list_his_own_promoted_pokemon(self):
        rows = json.load(open(os.path.join(HERE, '..', 'position_list.json'), encoding='utf-8'))
        r = next(r for r in rows if r['position_id'] == 'KW-261005_183108000-t01')
        self.assertEqual(r['switch2_opponent_possible'], '')
        self.assertEqual(r['switch2_flag'], 'yes')      # Mega Sableye ex (Cursed Jewel) is in his own deck

    def test_audit_012927_the_energy_zone_is_read_as_the_turn_ended(self):
        got = [(self.position('20261006_012927000', t)['me']['energy_now'], self.position('20261006_012927000', t)['me']['energy_next']) for t in (4, 6, 8)]
        self.assertEqual(got, [('Darkness', 'Grass'), ('Grass', 'Metal'), ('Metal', 'Metal')])



# ------------------------------------------------------------------------------------------------------------- Oct 13: conditions and knock-outs
class ConditionsAndKnockouts(unittest.TestCase):
    """Fable via Sonnet's read of the Oct 13 games: pg_pos had no Special Condition and no knock-out count, so a sleeping Pokemon was
    played as awake and Kingambit's Overlord's Blade read 60. The converter now writes them into the position (pg_pos.rs reads them)."""

    def convert(self, deck, turns):
        return MadeUpGame(self, deck, turns).convert({})[0]

    def at(self, pos, turn):
        return next(p for p in pos if p['turn_count'] == turn)

    def test_his_sleeping_active_is_asleep_in_the_position(self):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60, conds=['Asleep']), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        p = self.convert(fighting_deck(), [t])[0]
        self.assertEqual(p['me']['board'][0].get('conditions'), ['Asleep'])
        self.assertNotIn('not represented', p['notes'])

    def test_the_opponents_poisoned_active_is_poisoned_and_other_wordings_are_read(self):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60, conds=['paralyzed']), []), board(mon('Stakataka', 110, conds=['Poison', 'Confusion']), []), [play('end_turn')])
        p = self.convert(fighting_deck(), [t])[0]
        self.assertEqual(p['me']['board'][0].get('conditions'), ['Paralyzed'])
        self.assertEqual(p['opp']['board'][0].get('conditions'), ['Poisoned', 'Confused'])

    def test_a_pokemon_with_no_condition_has_no_conditions_key(self):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        p = self.convert(fighting_deck(), [t])[0]
        self.assertNotIn('conditions', p['me']['board'][0])

    def test_a_condition_the_engine_does_not_have_stays_a_note(self):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60, conds=['Frozen']), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        p = self.convert(fighting_deck(), [t])[0]
        self.assertNotIn('conditions', p['me']['board'][0])
        self.assertIn('Frozen', p['notes'])

    def test_the_knockout_count_is_his_pokemon_knocked_out_so_far(self):
        deck = real_deck(('Honedge', 'B2 118', 2), ('Horsea', 'A4 041', 2))
        h1, h3 = mon('Honedge', 70, pos=1), mon('Honedge', 70, pos=3)
        turns = [owner_turn(2, ['Poké Ball'], board(mon('Horsea', 50), [h1, h3]), board(mon('Stakataka', 110), []), [play('end_turn')]),
                 opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Bench3', 'Bench3 removed')]),
                 owner_turn(4, ['Poké Ball'], board(mon('Horsea', 50), [mon('Honedge', 70, pos=1)]), board(mon('Stakataka', 110), []), [play('end_turn')]),
                 opp_turn(5, [play('attack', 'Stakataka: Brass Rock', 'owner Active', 'knocks out Active Horsea')]),
                 owner_turn(6, ['Poké Ball'], board(mon('Honedge', 70)), board(mon('Stakataka', 110), []), [play('end_turn')])]
        pos = self.convert(deck, turns)
        self.assertEqual([self.at(pos, t)['me'].get('knockouts') for t in (2, 4, 6)], [0, 1, 2])


# ------------------------------------------------------------------------------------------------------------- Oct 13: a checkup knock-out after his turn
def cards_shown(p):
    """how many cards of his deck a position shows: the board with what is under and on it, his hand and his discard"""
    n = len(p['me']['hand']) + len(p['me']['discard'])
    for pk in p['me']['board']:
        n += 1 + len(pk.get('behind', [])) + len(pk.get('tools', []))
    return n


class CheckupKnockouts(unittest.TestCase):
    """Fable's job after the v2 read of the Oct 13 games: a Pokemon of his that the checkup (Poison, Burn, Bad Dreams on a sleeping one) knocks out AFTER his turn ended. The ledger logs the
    knock-out and his promotion at the end of his own row and that row's `board_after` is already past it, so comparing the end of one of his rows with the start of the next (which finds
    what the opponent's turn knocked out) never saw it: the Pokemon, what was under it, its Tool and its Energy were missing from his discard, `me.knockouts` stayed 0 and the position
    showed too few cards (game 20261013_030351000: 4 cards short at turn 15, so turn 15 could not run)."""
    DECK = real_deck(('Timburr', 'A3 094', 2), ('Gurdurr', 'A3 095', 1), ('Conkeldurr', 'A3 096', 1), ('Rocky Helmet', 'A2 148', 1))
    OPP = board(mon('Stakataka', 110), [])

    def gurdurr(self, **kw):
        d = dict(hp=20, variant='Strength40', energy={'Fighting': 1}, tool='Rocky Helmet', conds=['Asleep'], instance_id='G', stack=['Timburr', 'Gurdurr'])
        d.update(kw)
        return mon('Gurdurr', 90, **d)

    def game(self, plays, auto, active=None, bench=None, after_active=None, after_bench=(), hand2=('Poké Ball',)):
        """row 2 is his turn that ends in a checkup knock-out of his Active, row 3 the opponent's, row 4 his next turn (a position is made at 2 and 4);
        `after_bench` is what row 2's `board_after` lists besides the new Active (the next turn starts without it)"""
        start = board(active or self.gurdurr(), bench if bench is not None else [mon('Timburr', 60, pos=1, instance_id='T')])
        new_active = after_active or mon('Timburr', 60, instance_id='T')
        row2 = owner_turn(2, list(hand2), start, self.OPP, plays, after=board(new_active, list(after_bench)))
        row2['automatic_events_in_order'] = auto
        row4 = owner_turn(4, ['Poké Ball'], board(new_active, []), self.OPP, [play('end_turn')])
        return MadeUpGame(self, self.DECK, [row2, opp_turn(3, []), row4]).convert({})[0]

    def p4(self, pos):
        return next(p for p in pos if p['turn_count'] == 4)

    KO_EVENTS = ['Bad Dreams knocks out 20-HP Gurdurr.', 'Gurdurr, Rocky Helmet and 2 Fighting are discarded; owner promotes Timburr.']

    def test_a_pokemon_the_checkup_knocked_out_after_he_ended_his_turn_reaches_his_discard_with_its_stack_tool_and_energy(self):
        plays = [play('energy_attachment', None, 'G', 'Attach Fighting from zone', energy={'type': 'Fighting', 'count': 1, 'destination': 'G'}),
                 play('end_turn'), play('promotion', None, 'T', 'Choose Timburr as replacement after Gurdurr KO')]
        p = self.p4(self.game(plays, self.KO_EVENTS))
        self.assertEqual(sorted(p['me']['discard']), ['Gurdurr A3 095', 'Rocky Helmet A2 148', 'Timburr A3 094'])
        self.assertEqual(sorted(p['me']['discard_energy']), ['Fighting', 'Fighting'], 'the Energy it had at the start and the one he attached this turn')
        self.assertEqual(p['me']['knockouts'], 1)
        self.assertIn('checkup', p['notes'])
        self.assertEqual(cards_shown(p), 5, 'the Timburr on the board, the Poké Ball in hand, and the three cards of the knocked-out Pokémon')

    def test_an_ability_the_knocked_out_pokemon_used_this_turn_does_not_make_it_an_evolved_one(self):
        # 030351: Dragonair used Dragon's Blessing (card_name Dragonair, target its own id) and was knocked out by Bad Dreams after the turn
        plays = [play('ability', 'Gurdurr', 'G', "Gurdurr's Ability"), play('end_turn'), play('promotion', None, 'T', '')]
        p = self.p4(self.game(plays, self.KO_EVENTS))
        self.assertEqual(sorted(p['me']['discard']), ['Gurdurr A3 095', 'Rocky Helmet A2 148', 'Timburr A3 094'])
        self.assertEqual(p['me']['knockouts'], 1)

    def test_the_same_when_his_turn_ended_with_an_attack_and_not_an_end_turn(self):
        plays = [play('attack', 'Gurdurr', 'opponent Active', 'Strength40'), play('promotion', None, 'T', 'Choose Timburr as replacement')]
        p = self.p4(self.game(plays, self.KO_EVENTS))
        self.assertEqual(sorted(p['me']['discard']), ['Gurdurr A3 095', 'Rocky Helmet A2 148', 'Timburr A3 094'])
        self.assertEqual(p['me']['knockouts'], 1)

    def test_the_count_in_the_ledgers_text_wins_when_it_differs_from_what_the_plays_add_up_to(self):
        events = ['Poison checkup knocks out Gurdurr.', 'Gurdurr and three Fighting Energy leave board.']
        p = self.p4(self.game([play('end_turn'), play('promotion', None, 'T', '')], events))
        self.assertEqual(p['me']['discard_energy'], ['Fighting'] * 3)
        self.assertIn("in the ledger's text (3)", p['notes'])

    def test_the_energy_the_text_gives_the_promoted_pokemon_is_not_the_knocked_out_ones(self):
        # 030351 turn 13: "Druddigon, Rocky Helmet and 3 Metal are discarded. Owner promotes second Haxorus 150 HP with 1 Fighting."
        events = ['Poison checkup knocks out Gurdurr.', 'Gurdurr, Rocky Helmet and 2 Fighting are discarded. Owner promotes Timburr 60 HP with 1 Fighting.']
        plays = [play('energy_attachment', None, 'G', 'Attach Fighting from zone', energy={'type': 'Fighting', 'count': 1, 'destination': 'G'}), play('end_turn'), play('promotion', None, 'T', '')]
        p = self.p4(self.game(plays, events))
        self.assertEqual(p['me']['discard_energy'], ['Fighting'] * 2)
        self.assertNotIn("in the ledger's text", p['notes'])

    def test_a_pokemon_that_left_the_board_without_a_knock_out_in_the_text_is_not_in_the_discard(self):
        # a bounce (Ilima-like): the Pokemon is gone at the end of his row and a promotion follows, but the ledger says it went back to his hand
        events = ['Gurdurr returns to hand; owner promotes Timburr.']
        p = self.p4(self.game([play('end_turn'), play('promotion', None, 'T', '')], events))
        self.assertEqual(p['me']['discard'], [])
        self.assertEqual(p['me']['knockouts'], 0)

    def test_a_pokemon_that_shuffled_itself_into_the_deck_is_not_in_the_discard_even_with_a_promotion_play_after_the_attack(self):
        # Accelgor's Deck and Cover (213625 turn 11, 214731 turn 6): the attacker and what is on it go back to the deck and another Pokemon is promoted
        plays = [play('attack', 'Gurdurr', 'opponent Active', 'Strength40; shuffles attacker and all attached cards into the deck'), play('promotion', None, 'T', 'promote Timburr')]
        events = ['Active Gurdurr and attached Pokemon stack return to deck; its 1 Fighting leave board', 'Select Timburr as replacement']
        p = self.p4(self.game(plays, events))
        self.assertEqual(p['me']['discard'], [])
        self.assertEqual(p['me']['knockouts'], 0)

    def test_a_pokemon_gone_with_no_promotion_after_his_turn_is_not_a_checkup_knock_out(self):
        p = self.p4(self.game([play('end_turn')], self.KO_EVENTS))
        self.assertEqual(p['me']['discard'], [])
        self.assertEqual(p['me']['knockouts'], 0)

    def test_the_knocked_out_one_is_told_from_a_pokemon_of_its_name_that_is_still_there_by_its_instance_id(self):
        a = mon('Timburr', 60, hp=10, conds=['Poisoned'], instance_id='A')
        b = mon('Timburr', 60, pos=1, instance_id='B')
        plays = [play('end_turn'), play('promotion', None, 'B', 'Choose Timburr as replacement')]
        pos = self.game(plays, ['Poison checkup knocks out Timburr.'], active=a, bench=[b], after_active=mon('Timburr', 60, instance_id='B'))
        p = self.p4(pos)
        self.assertEqual(p['me']['discard'], ['Timburr A3 094'])
        self.assertEqual(p['me']['knockouts'], 1)
        self.assertEqual(p['me']['board'][0]['card'].split(' ')[0], 'Timburr')

    def test_a_pokemon_of_the_same_name_that_evolved_this_turn_is_not_the_knocked_out_one(self):
        # the bench Timburr A evolves (the ledger gives the evolved one a new id) while the Active Timburr B is knocked out by the Poison
        b = mon('Timburr', 60, hp=10, conds=['Poisoned'], instance_id='B')
        a = mon('Timburr', 60, pos=1, instance_id='A')
        evolved = mon('Gurdurr', 90, variant='Strength40', instance_id='A2', stack=['Timburr', 'Gurdurr'])
        plays = [play('evolution', 'Gurdurr', 'A → A2', 'Evolve Timburr A'), play('end_turn'), play('promotion', None, 'A2', 'Choose Gurdurr as replacement')]
        pos = self.game(plays, ['Poison checkup knocks out Timburr.'], active=b, bench=[a], after_active=evolved, hand2=('Gurdurr',))
        p = self.p4(pos)
        self.assertEqual(p['me']['discard'], ['Timburr A3 094'], 'one Timburr, the one that was Active')
        self.assertEqual(p['me']['knockouts'], 1)

    def test_a_knock_out_the_opponents_attack_made_between_the_turns_is_still_found_and_not_counted_twice(self):
        # the existing between-turns path: the Pokemon is in the row's `board_after` and gone from the next start
        g = self.gurdurr(conds=[])
        row2 = owner_turn(2, ['Poké Ball'], board(g, [mon('Timburr', 60, pos=1, instance_id='T')]), self.OPP, [play('end_turn')])
        row4 = owner_turn(4, ['Poké Ball'], board(mon('Timburr', 60, instance_id='T'), []), self.OPP, [play('end_turn')])
        opp3 = opp_turn(3, [play('attack', 'Stakataka: Brass Rock', 'owner Active', 'knocks out Active Gurdurr')])
        p = self.p4(MadeUpGame(self, self.DECK, [row2, opp3, row4]).convert({})[0])
        self.assertEqual(sorted(p['me']['discard']), ['Gurdurr A3 095', 'Rocky Helmet A2 148', 'Timburr A3 094'])
        self.assertEqual(p['me']['knockouts'], 1)
        self.assertIn('between turns', p['notes'])

    def test_a_ledger_that_already_shows_the_knocked_out_pokemon_in_its_board_after_does_not_count_it_twice(self):
        # (the Oct 13 v2 read put it there by a copy of the ledger; the same rows must give the same positions)
        ko = self.gurdurr(hp=0)
        plays = [play('end_turn'), play('promotion', None, 'T', '')]
        pos = self.game(plays, self.KO_EVENTS, after_active=mon('Timburr', 60, instance_id='T'), after_bench=[ko])
        p = self.p4(pos)
        self.assertEqual(sorted(p['me']['discard']), ['Gurdurr A3 095', 'Rocky Helmet A2 148', 'Timburr A3 094'])
        self.assertEqual(p['me']['knockouts'], 1)


# ------------------------------------------------------------------------------------------------------------- Oct 14: the laptop's review of the 92 positions of the Oct 12-13 games
# (REVIEW_POSITIONS_laptop.md, main 373b41a6: three blockers and nine majors; every one has a test here)
HIDDEN_ZONE = {'this_turn': {'type': None, 'count': 0, 'available': False}, 'next': {'type': None, 'count': None, 'available': None}}


def zone_of(this=None, nxt=None):
    return {'this_turn': {'type': this, 'count': 1 if this else 0, 'available': bool(this)}, 'next': {'type': nxt, 'count': 1 if nxt else None, 'available': None}}


def nested(position, pokemon):
    """a Bench entry the way game 20261013_015011000 writes it: {position, pokemon: {...} or null}"""
    return {'position': position, 'pokemon': pokemon}


class NestedBench(unittest.TestCase):
    """blocker 1: 015011 nests every Bench entry as {position, pokemon}; the converter kept only entries with a `name`, so both Benches were empty (Grimer and Regigigas were dealt back into his deck)"""

    def convert(self, own, opp):
        t = owner_turn(2, ['Gurdurr'], own, opp, [play('end_turn')])
        return MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]

    def test_a_nested_bench_is_read_on_both_sides_and_empty_slots_are_skipped(self):
        own = board(mon('Timburr', 60), [nested(1, None), nested(2, mon('Timburr', 60, pos=2))])
        opp = board(mon('Stakataka', 110), [nested(1, mon('Stakataka', 110, pos=1)), nested(2, None), nested(3, None)])
        p = self.convert(own, opp)
        self.assertEqual([b['card'].split(' ')[0] for b in p['me']['board']], ['Timburr', 'Timburr'])
        self.assertEqual(len(p['opp']['board']), 2)

    def test_the_slot_of_a_nested_entry_is_the_outer_position_when_the_pokemon_does_not_carry_one(self):
        inner = mon('Timburr', 60)
        inner['bench_position'] = None
        own = board(mon('Timburr', 60), [nested(1, None), nested(2, inner), nested(3, mon('Timburr', 60, pos=3))])
        got = L.instances(own)
        self.assertEqual([L.bpos(x) for x in got], [None, 2, 3])

    def test_a_nested_bench_does_not_change_the_cards_the_deck_has_left(self):
        own = board(mon('Timburr', 60), [nested(2, mon('Timburr', 60, pos=2))])
        p = self.convert(own, board(mon('Stakataka', 110), []))
        shown = len(p['me']['hand']) + sum(1 + len(b.get('behind', [])) for b in p['me']['board'])
        self.assertEqual(shown, 3, 'two Timburr on the board, one Gurdurr in hand')

    def test_a_plain_bench_is_read_as_before(self):
        own = board(mon('Timburr', 60), [mon('Timburr', 60, pos=1)])
        self.assertEqual(len(L.instances(own)), 2)


class BoostedHP(unittest.TestCase):
    """blocker 2: 030351 under Starting Plains shows the opponent's Darkrai at 120 HP (printed 100 + 20); opp_pick kept only printings whose printed HP is 120, so Bad Dreams / Dark Slumber
    (B2b 040, 100 HP) lost to Shadow Cage (B1 154, 120 HP) and nothing was flagged. The HP a Stadium or a Tool adds comes from the card texts of the database."""

    def test_what_a_stadium_or_a_tool_adds_comes_from_the_card_text_and_the_card_it_is_on(self):
        darkrai, scizor, scyther = C.BYID['B2b 040'], C.BYID['B2b 047'], C.BYID['B2b 001']
        self.assertEqual(C.hp_boost(darkrai, stadium='Starting Plains'), 20)
        self.assertEqual(C.hp_boost(scizor, stadium='Starting Plains'), 0, 'a Stage 1')
        self.assertEqual(C.hp_boost(scizor, tool='Elegant Cape'), 30)
        self.assertEqual(C.hp_boost(scyther, tool='Elegant Cape'), 0, 'a Basic')
        self.assertEqual(C.hp_boost(scyther, tool='Giant Cape'), 20)
        self.assertEqual(C.hp_boost(scizor, tool='Elegant Cape', stadium='Starting Plains'), 30)
        self.assertEqual(C.hp_boost(darkrai), 0)
        self.assertEqual(C.hp_boost(darkrai, tool='Rocky Helmet', stadium='Rainbow Cave'), 0)

    def test_a_grass_pokemon_gets_a_leaf_cape_and_a_darkness_pokemon_does_not(self):
        grass = next(c for c in C.CARDS if C.is_pokemon(c) and c.get('energy_type') == 'Grass')
        self.assertEqual(C.hp_boost(grass, tool='Leaf Cape'), 30)
        self.assertEqual(C.hp_boost(C.BYID['B2b 040'], tool='Leaf Cape'), 0)

    def convert_opp(self, hp_max, variant, stadium):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Darkrai', hp_max, variant=variant), []), [play('end_turn')], stadium=stadium)
        return MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]

    def test_the_opponents_darkrai_under_starting_plains_is_the_100_hp_card_with_bad_dreams(self):
        p = self.convert_opp(120, 'Bad Dreams / Dark Slumber 40; printed 100 HP', 'Starting Plains')
        self.assertEqual(p['opp']['board'][0]['card'], 'Darkrai B2b 040')
        self.assertEqual(p['opp']['board'][0]['hp'], 120)

    def test_the_hp_alone_settles_it_when_the_ledger_names_no_attack(self):
        p = self.convert_opp(120, '', 'Starting Plains')
        self.assertEqual(p['opp']['board'][0]['card'], 'Darkrai B2b 040')

    def test_without_the_stadium_120_hp_is_the_card_printed_with_120(self):
        p = self.convert_opp(120, 'Shadow Cage', 'none')
        self.assertEqual(p['opp']['board'][0]['card'], 'Darkrai B1 154')

    def test_a_ledger_that_did_not_add_the_boost_is_still_read_by_its_printed_hp(self):
        p = self.convert_opp(100, 'Bad Dreams', 'Starting Plains')
        self.assertEqual(p['opp']['board'][0]['card'], 'Darkrai B2b 040')

    def test_a_tool_that_adds_hp_is_taken_off_before_the_printings_are_compared(self):
        # a Stage 1 Dragonair at 110 with an Elegant Cape (+30) is the 80-HP card, not one of the 90 / 100 ones
        chosen, alts = L.opp_pick('Dragonair', 110, [], tool='Elegant Cape')
        self.assertEqual(C.BYID[chosen]['hp'], 80)
        self.assertEqual(L.opp_pick('Dragonair', 80, [])[0] in [c['id'] for c in C.BYNAME['Dragonair'] if c['hp'] == 80], True)

    def test_his_own_darkrai_under_starting_plains_is_the_function_of_the_right_printed_hp(self):
        deck = real_deck(('Darkrai', 'B2b 040', 1), ('Darkrai', 'B1 154', 1))
        t = owner_turn(2, ['Poké Ball'], board(mon('Darkrai', 120, variant=''), []), board(mon('Stakataka', 110), []), [play('end_turn')], stadium='Starting Plains')
        p = MadeUpGame(self, deck, [t]).convert({})[0][0]
        self.assertEqual(p['me']['board'][0]['card'], 'Darkrai B2b 040')


class SemanticEntityStrings(unittest.TestCase):
    """blocker 3: 022530's DECK_USED.json writes each entry as {name, variant: 'semantic entity 20770', count}; deckspec read no entity from the string, so Dratini was settled on an HP tie
    (A3b 051 Beat instead of B4 116 Slam)"""

    def deck(self):
        return deck_json(qr=None, filmed_cards_in_QR_order=['Dratini'] * 2 + ['Poké Ball'] * 18,
                         filmed_counts=[{'name': 'Dratini', 'variant': 'semantic entity 20770', 'count': 2}, {'name': 'Poké Ball', 'variant': 'semantic entity 30', 'count': 18}], energy='Fighting')

    def test_the_entity_is_read_from_the_string(self):
        self.assertEqual(D.entry_entity({'name': 'Dratini', 'variant': 'semantic entity 20770'}), 20770)
        self.assertEqual(D.entry_entity({'name': 'Dratini', 'variant_as_shown_in_log': 'semantic entity 20770'}), 20770)
        self.assertEqual(D.entry_entity({'name': 'Dratini', 'entity_id': 5, 'variant': 'semantic entity 20770'}), 5, 'an entity id the file gives wins')
        self.assertIsNone(D.entry_entity({'name': 'Dratini', 'variant': 'B4 116'}))

    def test_a_printing_beside_the_entity_still_counts_as_a_printing(self):
        d = {'name': 'Dratini', 'variant': 'B4 116 semantic entity 20770'}
        self.assertEqual(D.entry_ids(d), ['B4 116'])
        self.assertEqual(D.entry_entity(d), 20770)

    def test_an_entity_another_game_gave_its_printing_settles_the_entry(self):
        s = D.read_deck(self.deck(), {20770: ['B4 116'], 30: ['A2b 111']})
        dratini = next(e for e in s.entries if e.name == 'Dratini')
        self.assertEqual((dratini.entity, dratini.ids, dratini.ambiguous), (20770, ['B4 116'], False))
        self.assertEqual(dratini.how, 'entity seen in another game')

    def test_the_global_entity_map_reads_entities_from_strings_too(self):
        m = D.global_entity_map([deck_json(qr=[{'name': 'Dratini', 'variant': 'semantic entity 20770 B4 116', 'count': 2}] + [entry('Poké Ball', 30, variant='A2b 111')] * 18)])
        self.assertEqual(m.get(20770), ['B4 116'])


class OpponentNextEnergy(unittest.TestCase):
    """major 1: when the opponent's zone is hidden at his turn start the position took HIS deck's Energy (18 positions: 010706 Psychic, 010003 Water / Lightning, 203719 t17 Lightning); the
    type is on the same row after his turn, or on his next row"""

    def energy_next(self, start, after, next_row):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=start), [play('end_turn')])
        t['board_after']['opponent'] = board(mon('Stakataka', 110), [], zone=after)
        rows = [t] + ([opp_turn(3, [], opp_board=board(mon('Stakataka', 110), [], zone=next_row))] if next_row is not None else [])
        p = MadeUpGame(self, fighting_deck(), rows).convert(GLOBAL)[0][0]
        return p['opp']['energy_next'], p['notes']

    def test_a_type_the_zone_shows_at_the_start_is_used(self):
        self.assertEqual(self.energy_next(zone_of(nxt='Water'), HIDDEN_ZONE, zone_of(this='Psychic'))[0], 'Water')

    def test_a_hidden_zone_takes_the_type_the_same_row_shows_after_his_turn(self):
        self.assertEqual(self.energy_next(HIDDEN_ZONE, zone_of(nxt='Lightning'), None)[0], 'Lightning')

    def test_a_zone_hidden_at_start_and_after_takes_the_type_of_his_next_turn(self):
        self.assertEqual(self.energy_next(HIDDEN_ZONE, HIDDEN_ZONE, zone_of(this='Psychic'))[0], 'Psychic')

    def test_the_energy_the_opponent_attached_from_his_zone_on_his_next_row_counts_too(self):
        nxt = opp_turn(3, [play('energy_attachment', None, 'opponent Active', 'attach from zone', energy={'type': 'Water', 'count': 1})], opp_board=board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE))
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE), [play('end_turn')])
        p = MadeUpGame(self, fighting_deck(), [t, nxt]).convert(GLOBAL)[0][0]
        self.assertEqual(p['opp']['energy_next'], 'Water')

    def test_the_last_turn_takes_the_only_type_his_zone_ever_showed_in_the_game(self):
        # 010706 turn 21: no later row, nothing on its own row, but his zone is Psychic every time it is shown
        t2 = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE), [play('end_turn')])
        o3 = opp_turn(3, [], opp_board=board(mon('Stakataka', 110), [], zone=zone_of(this='Psychic')))
        t4 = owner_turn(4, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE), [play('end_turn')])
        pos = {p['turn_count']: p for p in MadeUpGame(self, fighting_deck(), [t2, o3, t4]).convert(GLOBAL)[0]}
        self.assertEqual(pos[4]['opp']['energy_next'], 'Psychic')
        self.assertNotIn("opponent's next Energy", pos[4]['notes'])

    def test_two_types_in_his_zone_leave_the_last_turn_to_the_decks_energy(self):
        t2 = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE), [play('end_turn')])
        t2['board_after']['opponent'] = board(mon('Stakataka', 110), [], zone=zone_of(nxt='Water'))
        o3 = opp_turn(3, [], opp_board=board(mon('Stakataka', 110), [], zone=zone_of(this='Psychic')))
        t4 = owner_turn(4, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), [], zone=HIDDEN_ZONE), [play('end_turn')])
        pos = {p['turn_count']: p for p in MadeUpGame(self, fighting_deck(), [t2, o3, t4]).convert(GLOBAL)[0]}
        self.assertEqual(pos[4]['opp']['energy_next'], 'Fighting')
        self.assertIn("opponent's next Energy", pos[4]['notes'])

    def test_nothing_known_falls_back_to_his_decks_energy_and_says_so(self):
        got, notes = self.energy_next(HIDDEN_ZONE, HIDDEN_ZONE, None)
        self.assertEqual(got, 'Fighting')
        self.assertIn("opponent's next Energy", notes)

    def test_a_known_type_leaves_no_such_note(self):
        self.assertNotIn("opponent's next Energy", self.energy_next(HIDDEN_ZONE, zone_of(nxt='Water'), None)[1])


class StadiumActivationPlay(unittest.TestCase):
    """major 3: Mesagoza logged as `stadium_activation` mapped to `other` and was dropped (210041 t08, 210823 t02 and t04)"""

    def plan(self, kind, card='Mesagoza'):
        t = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play(kind, card, None, 'Activate search coin; tails, no card found'), play('end_turn')], stadium='Mesagoza')
        return MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]['his_plan']

    def test_a_stadium_activation_is_a_use_stadium_step(self):
        self.assertEqual(self.plan('stadium_activation'), ['UseStadium'])

    def test_the_other_spellings_still_are(self):
        for kind in ('stadium_ability', 'stadium_effect', 'ability'):
            self.assertEqual(self.plan(kind), ['UseStadium'], kind)

    def test_nk_maps_the_kind(self):
        self.assertEqual(L.nk('stadium_activation'), 'ability')
        self.assertEqual(L.nk('Stadium Activation'), 'ability')


class GigaTurboTarget(unittest.TestCase):
    """major 4: Giga Turbo attaches an Energy from the zone to a Benched Pokemon like Turbo Shark, but only Turbo Shark got the `fx` step (010706 t09, 230258 t11, 010003 t09)"""
    DECK = real_deck(('Regigigas', 'B3 134', 2), ('Alolan Grimer', 'A3 110', 2), ('Alolan Muk', 'B2 097', 2), energy='Colorless')

    def plan(self, bench, plays, hand=('Poké Ball',)):
        own = board(mon('Regigigas', 150, variant='Seal of Antiquity / Giga Turbo', energy={'Colorless': 3}), bench)
        t = owner_turn(9, list(hand), own, board(mon('Stakataka', 110), []), plays)
        return MadeUpGame(self, self.DECK, [t]).convert({})[0][0]['his_plan']

    def test_the_energy_goes_to_the_benched_pokemon_the_text_names(self):
        plan = self.plan([mon('Alolan Muk', 110, pos=1)], [play('attack', 'Giga Turbo', 'Mega Diancie ex', '100 damage: 130 -> 30; nested attach 1 Colorless from Energy Zone to Alolan Muk. Poison 30 -> 20.')])
        self.assertEqual(plan, ['Attack:Giga Turbo', 'Attach:1Colorless@1 fx'])

    def test_a_pokemon_that_evolved_this_turn_is_found_under_its_new_name(self):
        plan = self.plan([mon('Alolan Grimer', 70, pos=1)], [play('evolution', 'Alolan Muk', 'Alolan Grimer', 'Evolve'),
                                                              play('attack', 'Regigigas Giga Turbo', 'Starmie ex Active', '100 damage 130->30 HP; generate Colorless 1 and attach to Alolan Muk Bench 1 at 432.')],
                         hand=('Alolan Muk',))
        self.assertEqual(plan, ['Evolve:Alolan Muk@1', 'Attack:Giga Turbo', 'Attach:1Colorless@1 fx'])

    def test_a_target_the_text_does_not_name_cuts_the_plan_at_the_step(self):
        t = owner_turn(9, ['Poké Ball'], board(mon('Regigigas', 150, variant='Giga Turbo', energy={'Colorless': 3}), [mon('Alolan Muk', 110, pos=1), mon('Alolan Grimer', 70, pos=2)]), board(mon('Stakataka', 110), []),
                       [play('attack', 'Giga Turbo', 'Mega Diancie ex', '100 damage; one Colorless attached to a Benched Pokémon')])
        p = MadeUpGame(self, self.DECK, [t]).convert({})
        self.assertEqual(p[0][0]['his_plan'], ['Attack:Giga Turbo'])
        self.assertTrue(p[0][0]['unresolved'])


class IlimaPromotion(unittest.TestCase):
    """major 2: Ilima puts his damaged Active into his hand and he must promote another Pokemon; the plan had no Promote step and kept the returned Pokemon in its slot list, so every later
    slot was wrong (203719 t07, 210823 t08, 020824 t11)"""
    DECK = real_deck(('Regigigas', 'B3 134', 1), ('Pawniard', 'B3a 041', 2), ('Glimmet', 'B3a 044', 1), ('Ilima', 'A3 149', 1), energy='Darkness')

    def plan(self, plays, bench=None, active=None, hand=('Ilima', 'Poké Ball')):
        bench = bench if bench is not None else [mon('Pawniard', 50, pos=2), mon('Glimmet', 60, pos=3)]
        own = board(active or mon('Regigigas', 150, hp=80, variant='Seal of Antiquity / Giga Turbo', energy={'Darkness': 1}), bench)
        t = owner_turn(11, list(hand), own, board(mon('Stakataka', 110), []), plays)
        p = MadeUpGame(self, self.DECK, [t]).convert({})[0][0]
        return p['his_plan'], p

    def test_a_separate_promotion_row_gives_a_promote_step_and_the_slots_after_it_follow_the_engine(self):
        plan, _ = self.plan([play('card_play', 'Ilima', None, 'Return damaged Colorless Regigigas to hand; its 1 Darkness discarded'),
                             play('prompt_response', None, None, 'Choose Pawniard as replacement Active'),
                             play('card_play', 'Regigigas', None, 'Bench returned Regigigas center, fresh 150 HP'),
                             play('retreat', None, 'Regigigas', 'paid 1 Darkness; Pawniard retreats; Regigigas becomes Active', energy={'type': None, 'destination': 'Regigigas', 'retreat_payment_by_type': {'Darkness': 1}}),
                             play('energy_attachment', None, 'Regigigas', 'Attach 1 Darkness from Energy Zone to Regigigas', energy={'type': 'Darkness', 'count': 1, 'destination': 'Regigigas'}),
                             play('end_turn')])
        self.assertEqual(plan, ['Play:Ilima', 'Promote:0@1', 'Place:Regigigas', 'Retreat:1', 'Attach:1Darkness@0 zone'])

    def test_the_promoted_pokemon_named_in_the_ilima_row_is_enough(self):
        plan, _ = self.plan([play('card_play', 'Ilima', 'owner active Regigigas', 'Return 10 HP Regigigas to hand; discard its Darkness. Promote Glimmet.'),
                             play('card_play', 'Regigigas', 'owner bench middle', 'Rebench Regigigas at 150 HP.'),
                             play('energy_attachment', None, 'owner active Glimmet', 'Attach 1 Darkness.', energy={'type': 'Darkness', 'count': 1, 'destination': 'owner active Glimmet'}),
                             play('end_turn')])
        self.assertEqual(plan, ['Play:Ilima', 'Promote:0@2', 'Place:Regigigas', 'Attach:1Darkness@0 zone'])

    def test_a_promotion_the_ilima_row_words_as_promotes_full_art_is_read(self):
        plan, _ = self.plan([play('card_play', 'Ilima', None, 'Returns damaged 50/150 HP Regigigas to hand; no Energy attached; promotes full-art Glimmet'),
                             play('card_play', 'Pawniard', None, 'Places second Pawniard in left Bench slot'),
                             play('end_turn')], hand=('Ilima', 'Pawniard'))
        self.assertEqual(plan, ['Play:Ilima', 'Promote:0@2', 'Place:Pawniard'])

    def test_with_one_pokemon_on_the_bench_it_is_the_one_promoted(self):
        plan, _ = self.plan([play('card_play', 'Ilima', None, 'Return damaged Regigigas to hand'), play('end_turn')], bench=[mon('Pawniard', 50, pos=1)])
        self.assertEqual(plan, ['Play:Ilima', 'Promote:0@1'])

    def test_when_the_ledger_does_not_say_which_one_the_plan_stops_there_and_the_target_is_unresolved(self):
        plan, p = self.plan([play('card_play', 'Ilima', None, 'Return damaged Regigigas to hand'), play('card_play', 'Regigigas', None, 'Bench Regigigas'), play('end_turn')])
        self.assertEqual(plan, ['Play:Ilima'])
        self.assertTrue(p['unresolved'])

    def test_ilima_on_a_benched_pokemon_leaves_a_hole_that_the_next_pokemon_he_benches_fills(self):
        plan, _ = self.plan([play('card_play', 'Ilima', None, 'Return damaged benched Pawniard from the Bench to hand'),
                             play('card_play', 'Pawniard', None, 'Bench Pawniard again'),
                             play('energy_attachment', None, 'Pawniard', 'Attach 1 Darkness to Pawniard', energy={'type': 'Darkness', 'count': 1, 'destination': 'Pawniard'}),
                             play('end_turn')],
                            bench=[mon('Pawniard', 50, hp=20, pos=1), mon('Glimmet', 60, pos=2)])
        self.assertEqual(plan, ['Play:Ilima', 'Place:Pawniard', 'Attach:1Darkness@1 zone'])

    def test_a_turn_without_ilima_keeps_its_slots(self):
        plan, _ = self.plan([play('energy_attachment', None, 'Pawniard', 'Attach', energy={'type': 'Darkness', 'count': 1, 'destination': 'Pawniard'}), play('end_turn')])
        self.assertEqual(plan, ['Attach:1Darkness@1 zone'])

    def test_a_promotion_after_the_attack_is_not_a_step_of_his_turn(self):
        plan, _ = self.plan([play('attack', 'Regigigas', 'opponent Active', 'Raging Hammer'), play('promotion', None, 'Pawniard', 'Choose Pawniard after the knock-out')])
        self.assertEqual(plan, ['Attack:Giga Turbo'])


class DragonsBlessingChoice(unittest.TestCase):
    """major 7: Dragon's Blessing takes an Energy from the discard and the engine asks which type (one choice per distinct type); the plan had the Ability but not the choice (022530 t09)"""
    DECK = real_deck(('Axew', 'B2b 054', 2), ('Dratini', 'B4 116', 2), energy='Fighting')

    def plan(self, ability_play):
        t = owner_turn(9, ['Poké Ball'], board(mon('Axew', 70, variant='Sharp Fang'), [mon('Dratini', 60, pos=2)]), board(mon('Stakataka', 110), []), [ability_play, play('end_turn')])
        return MadeUpGame(self, self.DECK, [t]).convert(GLOBAL)[0][0]['his_plan']

    def test_the_type_he_chose_is_a_step_after_the_ability(self):
        plan = self.plan(play('ability', 'Dragon’s Blessing', 'Active Axew', 'Right Bench Dragonair recovers 1 Fighting from discard onto Axew.', energy={'type': 'Fighting', 'count': 1, 'destination': 'Active Axew'}))
        self.assertEqual(plan, ['Ability', 'AttachTypedFromDiscard:Fighting@0'])

    def test_the_target_slot_is_the_pokemon_the_energy_went_to(self):
        plan = self.plan(play('ability', 'Dragon’s Blessing', 'Dratini', 'Dragonair recovers 1 Metal from discard onto Dratini.', energy={'type': 'Metal', 'count': 1, 'destination': 'Dratini'}))
        self.assertEqual(plan, ['Ability', 'AttachTypedFromDiscard:Metal@1'])

    def test_an_ability_that_moves_no_energy_from_the_discard_is_just_an_ability(self):
        plan = self.plan(play('ability', 'Sharp Fang', 'Active Axew', 'does something else'))
        self.assertEqual(plan, ['Ability'])


class NoBasicFound(unittest.TestCase):
    """major 8: 'No Basic found' did not match the NOTHING_FOUND pattern, so a Poké Ball that found nothing stayed as his first move (010706 t15)"""

    def test_the_pattern_reads_no_basic_found(self):
        for text in ('No Basic found', 'no Basic Pokémon found', 'No basic pokemon found in deck', 'No effect: no target in deck'):
            self.assertTrue(L.NOTHING_FOUND.search(text), text)
        self.assertFalse(L.NOTHING_FOUND.search('Search finds Horsea'))
        self.assertFalse(L.NOTHING_FOUND.search('finds a Basic Pokémon: Basic Dratini'))

    def test_such_a_poke_ball_is_not_in_his_plan(self):
        t = owner_turn(15, ['Poké Ball', 'Wally'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('card_play', 'Poké Ball', None, 'No Basic found'), play('end_turn')])
        p = MadeUpGame(self, fighting_deck(), [t]).convert(GLOBAL)[0][0]
        self.assertEqual(p['his_plan'], [])
        self.assertIn('found nothing', p['notes'])


class RecordedCorrections(unittest.TestCase):
    """the frame-only corrections the review settled are applied to the ledger copy by normalize_ledger.py and recorded in it; the converter says so in the notes of the positions they cover"""

    def convert(self, corrections):
        t2 = owner_turn(2, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        t4 = owner_turn(4, ['Poké Ball'], board(mon('Timburr', 60), []), board(mon('Stakataka', 110), []), [play('end_turn')])
        game = MadeUpGame(self, fighting_deck(), [t2, opp_turn(3, []), t4])
        path = os.path.join(game.path, 'TURN_LEDGER.json')
        with open(path, encoding='utf-8') as f:
            led = json.load(f)
        led['corrections'] = corrections
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(led, f)
        return {p['turn_count']: p for p in game.convert(GLOBAL)[0]}

    def test_a_correction_is_a_note_in_the_positions_of_its_turns_only(self):
        pos = self.convert([{'id': 'x', 'turns': [4], 'note': 'the opponent hand at turn 4 is 6 (the frames), not 5'}])
        self.assertIn('the opponent hand at turn 4 is 6', pos[4]['notes'])
        self.assertNotIn('the opponent hand at turn 4', pos[2]['notes'])

    def test_a_correction_without_turns_covers_every_position_of_the_game(self):
        pos = self.convert([{'id': 'y', 'note': 'the left Bench Pokemon is a Meowth B2 124'}])
        self.assertTrue(all('the left Bench Pokemon is a Meowth' in p['notes'] for p in pos.values()))

    def test_a_ledger_without_corrections_has_none(self):
        pos = self.convert([])
        self.assertNotIn('corrected', pos[2]['notes'])


if __name__ == '__main__':
    unittest.main()
