#!/usr/bin/env python3
"""Tests for normalize_ledger.py (the ledger copy the converter reads).

  cd rl/results/pause_games_new_2026-10-13/v2/scripts && python3 -B -m unittest -v test_normalize_ledger

Written for the laptop's review of the 92 positions (REVIEW_POSITIONS_laptop.md, Oct 14): the nested Bench of 015011, the deck of 022530 (a list of names and 'semantic entity N' strings that
left Dratini open), and the corrections the review settled from the frames. Made-up packets in a temporary folder; the last class checks the recorded corrections against the real ledgers when
the Recording_QA folder is on this machine."""
import copy, glob, importlib.util, io, json, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'pause_games_new_2026-10-12', 'harness'))
import deckspec as D  # noqa: E402

_spec = importlib.util.spec_from_file_location('normalize_ledger', os.path.join(HERE, 'normalize_ledger.py'))
N = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(N)

QA = os.environ.get('QA') or '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def pk(name, hp=60, **kw):
    d = {'name': name, 'variant': '', 'hp_now': hp, 'hp_max': hp, 'attached_energy': {'total': 0, 'by_type': {}}, 'tool': None, 'special_conditions': []}
    d.update(kw)
    return d


def packet(test, deck, turns, qr=None, snap=None, name='20269999_000000000_iOS'):
    root = tempfile.mkdtemp()
    test.addCleanup(shutil.rmtree, root, True)
    src = os.path.join(root, name)
    os.makedirs(src)
    write_json(os.path.join(src, 'DECK_USED.json'), deck)
    write_json(os.path.join(src, 'TURN_LEDGER.json'), {'turns': turns})
    if qr is not None:
        write_json(os.path.join(src, 'QR_DECODE.json'), qr)
    if snap is not None:
        write_json(os.path.join(src, 'DECK_LOG_SNAPSHOT.json'), snap)
    return src, os.path.join(root, 'out')


def read(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# a packet shaped like 20261013_022530000_iOS: 20 names, 'semantic entity N' strings, the QR and the snapshot beside it
DECK_022530 = {'schema': 'pause-games/turn-capture-v1', 'exact_list_status': 'filmed_QR_verified_live_log_snapshot_missing_initially', 'cards_in_log_order': None,
               'filmed_cards_in_QR_order': ['Dratini'] * 2 + ['Poké Ball'] * 18,
               'filmed_counts': [{'name': 'Dratini', 'variant': 'semantic entity 20770', 'count': 2}, {'name': 'Poké Ball', 'variant': 'semantic entity 30', 'count': 18}],
               'filmed_energy_configuration': ['Fighting']}
QR_022530 = {'cards': [{'entity_kind': 'pokemon', 'entity_id': 20770, 'count': 2, 'name': 'Dratini', 'printing_aliases': ['B4 116']},
                       {'entity_kind': 'trainer', 'entity_id': 30, 'count': 18, 'name': 'Poké Ball', 'printing_aliases': ['A2b 111', 'P-A 005']}],
             'decoded': {'energy': [{'name': 'Fighting', 'value': 6}]}}
SNAP_022530 = {'retrieved_utc': '2026-10-13T04:53:35Z', 'energy': 'Fighting', 'cards': [{'n': 2, 'name': 'Dratini', 'kind': 'Pokémon', 'id': 'B4 116'}, {'n': 18, 'name': 'Poké Ball', 'kind': 'Trainer', 'id': 'A2b 111'}]}


class NestedBench(unittest.TestCase):
    def test_inst_reads_a_nested_bench_and_skips_empty_slots(self):
        side = {'active': pk('Pawniard'), 'bench_in_position_order': [{'position': 1, 'pokemon': None}, {'position': 2, 'pokemon': pk('Regigigas', 150)}, {'position': 3, 'pokemon': pk('Alolan Grimer', 70)}]}
        self.assertEqual([p['name'] for p in N.inst(side)], ['Pawniard', 'Regigigas', 'Alolan Grimer'])

    def test_a_plain_bench_and_a_missing_side_are_read_as_before(self):
        self.assertEqual([p['name'] for p in N.inst({'active': pk('A'), 'bench_in_position_order': [pk('B'), {'name': 'none'}, {'empty': True, 'name': 'C'}]})], ['A', 'B'])
        self.assertEqual(N.inst(None), [])

    def test_a_knocked_out_pokemon_is_put_back_in_a_game_that_nests_its_bench(self):
        g = pk('Gurdurr', 90, instance_id='G', attached_energy={'total': 2, 'by_type': {'Fighting': 2}})
        t = pk('Timburr', 60, instance_id='T')
        row = {'turn_number': 2, 'who_played': 'owner', 'board_at_start': {'owner': {'active': g, 'bench_in_position_order': [{'position': 1, 'pokemon': None}, {'position': 2, 'pokemon': t}]}},
               'board_after': {'owner': {'active': t, 'bench_in_position_order': [{'position': 1, 'pokemon': None}, {'position': 2, 'pokemon': None}]}},
               'plays_in_order': [{'kind': 'end_turn'}, {'kind': 'promotion', 'target': 'T'}], 'automatic_events_in_order': ['Poison checkup knocks out Gurdurr.', 'Gurdurr and 2 Fighting Energy leave board.']}
        led = {'turns': [row]}
        log = []
        self.assertEqual(N.restore_checkup_knockouts(led, {}, log), 1)
        put_back = led['turns'][0]['board_after']['owner']['bench_in_position_order'][-1]
        self.assertEqual((put_back['name'], put_back['hp_now'], put_back['attached_energy']['by_type']), ('Gurdurr', 0, {'Fighting': 2}))
        self.assertTrue(log[0].startswith('   put back: turn 2 Gurdurr'))


class PlayText(unittest.TestCase):
    def test_a_play_with_only_details_gets_the_target_and_result_the_converter_reads(self):
        led = {'turns': [{'turn_number': 2, 'who_played': 'owner', 'plays_in_order': [
            {'kind': 'energy_attachment', 'details': 'Attach 1 Darkness from Energy Zone to Regigigas', 'energy': {'type': 'Darkness', 'number': 1, 'destination': 'Regigigas'}},
            {'kind': 'tool_attachment', 'details': 'Attach Heavy Helmet to Pawniard, not Glimmora'}]}]}
        changed, _ = N.normalize_plays(led)
        a, b = led['turns'][0]['plays_in_order']
        self.assertEqual((changed, a['target'], a['result'], a['energy']['count']), (2, 'Regigigas', 'Attach 1 Darkness from Energy Zone to Regigigas', 1))
        self.assertEqual(b['target'], 'Pawniard')

    def test_an_instance_arrow_is_read_as_the_pokemon_it_started_as(self):
        led = {'turns': [{'turn_number': 4, 'who_played': 'owner', 'plays_in_order': [
            {'kind': 'evolution', 'card_name': 'Dragonair', 'target': 'Dratini-1 → Dragonair-1'}, {'kind': 'ability', 'card_name': 'Dragonair', 'target': 'Dragonair-1'}]}]}
        N.normalize_plays(led)
        self.assertEqual([p['target'] for p in led['turns'][0]['plays_in_order']], ['Dratini-1', 'Dratini-1'])


class PacketDeck(unittest.TestCase):
    """the deck of 022530: a list of names and 'semantic entity N' strings left Dratini open (A3b 051 Beat or B4 116 Slam); the packet's own QR and snapshot say B4 116"""

    def test_a_list_that_leaves_an_entry_open_is_replaced_by_the_one_built_from_the_qr_and_the_snapshot(self):
        src, out = packet(self, DECK_022530, [], QR_022530, SNAP_022530)
        lines = N.normalize(src, out, corrections=[])
        self.assertTrue(lines[0].startswith('AGREE 20269999_000000000_iOS: QR 20 cards, snapshot 20 cards'))
        spec = D.read_deck(read(os.path.join(out, 'DECK_USED.json')), {})
        dratini = next(e for e in spec.entries if e.name == 'Dratini')
        self.assertEqual((dratini.ids, dratini.ambiguous), (['B4 116'], False))
        self.assertFalse(spec.version_unverified)

    def test_the_deck_as_the_file_stands_is_what_the_converter_would_have_read_without_the_fix(self):
        spec = D.read_deck(DECK_022530, {})
        dratini = next(e for e in spec.entries if e.name == 'Dratini')
        self.assertTrue(dratini.ambiguous, 'the premise: from the names alone Dratini is open')

    def test_a_list_that_names_every_printing_is_left_alone(self):
        deck = {'schema': 'x', 'exact_list_status': 'filmed_QR_exact20_verified',
                'filmed_qr_cards_in_order': [{'name': 'Dratini', 'entity_id': 20770, 'variant': 'B4 116'}] * 2 + [{'name': 'Poké Ball', 'entity_id': 30, 'variant': 'A2b 111'}] * 18}
        src, out = packet(self, deck, [], QR_022530, SNAP_022530)
        N.normalize(src, out, corrections=[])
        got = read(os.path.join(out, 'DECK_USED.json'))
        self.assertNotIn('filmed_qr_cards', got)
        self.assertEqual(got['filmed_qr_cards_in_order'], deck['filmed_qr_cards_in_order'])

    def test_open_entries_without_a_qr_and_snapshot_are_left_alone(self):
        src, out = packet(self, DECK_022530, [], None, None)
        N.normalize(src, out, corrections=[])
        self.assertNotIn('filmed_qr_cards', read(os.path.join(out, 'DECK_USED.json')))

    def test_a_packet_with_no_list_at_all_still_gets_one_from_its_qr_and_snapshot(self):
        src, out = packet(self, {'schema': 'x', 'exact_list_status': 'filmed_QR_exact_missing'}, [], QR_022530, SNAP_022530)
        N.normalize(src, out, corrections=[])
        self.assertEqual(read(os.path.join(out, 'DECK_USED.json'))['exact_list_status'], 'verified_filmed_QR_and_live_log_snapshot_agree')

    def test_a_qr_and_a_snapshot_that_disagree_keep_the_conflict_status(self):
        snap = copy.deepcopy(SNAP_022530)
        snap['cards'][0] = {'n': 2, 'name': 'Dratini', 'kind': 'Pokémon', 'id': 'A3b 051'}
        src, out = packet(self, DECK_022530, [], QR_022530, snap)
        lines = N.normalize(src, out, corrections=[])
        self.assertTrue(lines[0].startswith('DISAGREE'))
        self.assertEqual(read(os.path.join(out, 'DECK_USED.json'))['exact_list_status'], 'filmed_QR_and_log_snapshot_conflict')

    def test_a_log_list_printing_under_variant_as_shown_in_log_is_copied_to_variant(self):
        deck = {'exact_list_status': 'x', 'cards_in_log_order': [{'name': 'Dratini', 'variant': None, 'variant_as_shown_in_log': 'B4 116'}] * 20}
        src, out = packet(self, deck, [])
        N.normalize(src, out, corrections=[])
        self.assertEqual(read(os.path.join(out, 'DECK_USED.json'))['cards_in_log_order'][0]['variant'], 'B4 116')


def ledger_for_corrections():
    def row(n, who, hand=None, **kw):
        r = {'turn_number': n, 'who_played': who, 'plays_in_order': [], 'board_at_start': {'owner': {'active': pk('Timburr')}, 'opponent': {'active': pk('Stakataka', 110)}},
             'board_after': {'owner': {'active': pk('Timburr')}, 'opponent': {'active': pk('Stakataka', 110)}}}
        if hand is not None:
            r['opponent_hand_at_owner_turn_start'] = hand
        r.update(kw)
        return r
    meowth = pk('Alolan Meowth', 50, variant='50 HP, Nasty Plot; ability title unreadable', bench_position=1)
    caped = pk('Scyther', 70, tool='Giant Cape')
    rows = [row(1, 'owner', {'count': 4, 'supported_range': None}),
            row(2, 'opponent', plays_in_order=[{'order': 1, 'kind': 'card_play', 'card_name': 'Alolan Meowth', 'result': 'Bench left'}]),
            row(3, 'owner', {'count': 5, 'supported_range': None}),
            row(4, 'opponent', plays_in_order=[{'order': 2, 'kind': 'card_play', 'card_name': 'Rare Candy', 'target': 'Active Riolu', 'result': 'evolve Riolu directly'}]),
            row(5, 'owner', {'count': None, 'supported_range': [3, 4]})]
    rows[0]['board_at_start']['opponent']['bench_in_position_order'] = [{'position': 1, 'pokemon': meowth}, {'position': 2, 'pokemon': caped}]
    rows[2]['board_at_start']['opponent']['bench_in_position_order'] = [dict(meowth), dict(caped)]
    rows[2]['board_after']['opponent']['bench_in_position_order'] = [dict(meowth), dict(caped)]
    return {'turns': rows}


class Corrections(unittest.TestCase):
    def apply(self, ops):
        led = ledger_for_corrections()
        lines = N.apply_corrections(led, ops, 'GAME')
        return led, lines

    def test_a_renamed_pokemon_is_renamed_on_both_boards_nested_or_not_and_in_the_opponents_plays(self):
        led, lines = self.apply([{'id': 'm', 'op': 'rename_pokemon', 'side': 'opponent', 'name': 'Alolan Meowth', 'to': 'Meowth', 'variant': "50 HP, Carefree Steps / Feelin' Fine", 'note': 'n', 'evidence': 'e'}])
        names = [p['name'] for t in led['turns'] for key in ('board_at_start', 'board_after') for p in N.pokemon_slots(t[key]['opponent'])]
        self.assertNotIn('Alolan Meowth', names)
        self.assertEqual(led['turns'][0]['board_at_start']['opponent']['bench_in_position_order'][0]['pokemon']['variant'], "50 HP, Carefree Steps / Feelin' Fine")
        self.assertEqual(led['turns'][1]['plays_in_order'][0]['card_name'], 'Meowth')
        self.assertEqual(lines, ['GAME corrected from the frames: m (rename_pokemon, 4 changes)'], 'three board readings and one play')

    def test_a_renamed_pokemon_of_the_other_side_is_not_touched(self):
        led = ledger_for_corrections()
        led['turns'][0]['board_at_start']['owner']['active'] = pk('Alolan Meowth', 50)
        N.apply_corrections(led, [{'id': 'm', 'op': 'rename_pokemon', 'side': 'opponent', 'name': 'Alolan Meowth', 'to': 'Meowth'}], 'G')
        self.assertEqual(led['turns'][0]['board_at_start']['owner']['active']['name'], 'Alolan Meowth')

    def test_a_tool_is_renamed_only_in_the_turns_asked_for(self):
        led, _ = self.apply([{'id': 'c', 'op': 'rename_tool', 'side': 'opponent', 'name': 'Giant Cape', 'to': 'Elegant Cape', 'from_turn': 1, 'to_turn': 3}])
        tools = {t['turn_number']: [p.get('tool') for p in N.pokemon_slots(t['board_at_start']['opponent'])] for t in led['turns']}
        self.assertIn('Elegant Cape', tools[1])
        self.assertIn('Elegant Cape', tools[3])
        self.assertNotIn('Giant Cape', tools[3])

    def test_the_opponent_hand_is_set_and_the_old_reading_is_kept_beside_it(self):
        led, _ = self.apply([{'id': 'h', 'op': 'set_opponent_hand', 'counts': {'3': 6, '5': 4}, 'was': {'3': 5, '5': [3, 4]}}])
        h3 = led['turns'][2]['opponent_hand_at_owner_turn_start']
        self.assertEqual((h3['count'], h3['supported_range'], h3['ledger_said']), (6, None, 5))
        self.assertEqual(led['turns'][4]['opponent_hand_at_owner_turn_start']['ledger_said'], [3, 4])
        self.assertEqual(led['turns'][0]['opponent_hand_at_owner_turn_start']['count'], 4, 'a turn that is not in the correction is untouched')

    def test_a_correction_written_for_another_reading_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self.apply([{'id': 'h', 'op': 'set_opponent_hand', 'counts': {'3': 6}, 'was': {'3': 4}}])
        self.assertIn('the ledger says 5', str(cm.exception))

    def test_a_play_is_replaced_when_it_is_the_one_expected(self):
        led, _ = self.apply([{'id': 'rc', 'op': 'replace_play', 'turn': 4, 'order': 2, 'expect': {'card_name': 'Rare Candy'}, 'set': {'kind': 'evolution', 'card_name': 'Mega Lucario ex'}}])
        p = led['turns'][3]['plays_in_order'][0]
        self.assertEqual((p['kind'], p['card_name'], p['target']), ('evolution', 'Mega Lucario ex', 'Active Riolu'))
        self.assertEqual(p['replaced_by_correction'], {'kind': 'card_play', 'card_name': 'Rare Candy'})

    def test_a_play_that_is_not_the_one_expected_is_an_error(self):
        with self.assertRaises(SystemExit) as cm:
            self.apply([{'id': 'rc', 'op': 'replace_play', 'turn': 4, 'order': 2, 'expect': {'card_name': 'Poké Ball'}, 'set': {'kind': 'evolution'}}])
        self.assertIn('changed nothing', str(cm.exception))

    def test_a_correction_that_matches_nothing_is_an_error_and_so_is_an_unknown_op(self):
        for op in ({'id': 'x', 'op': 'rename_pokemon', 'side': 'opponent', 'name': 'Nobody', 'to': 'Somebody'}, {'id': 'y', 'op': 'rename_tool', 'name': 'Nothing', 'to': 'Else'}):
            with self.assertRaises(SystemExit) as cm:
                self.apply([op])
            self.assertIn('changed nothing', str(cm.exception))
        with self.assertRaises(SystemExit):
            self.apply([{'id': 'z', 'op': 'explode'}])

    def test_the_corrections_are_recorded_in_the_ledger_with_their_turns_notes_and_evidence(self):
        led, _ = self.apply([{'id': 'h', 'op': 'set_opponent_hand', 'counts': {'3': 6}, 'turns': [3], 'note': 'the hand is 6', 'evidence': 'frames t0114'}])
        self.assertEqual(led['corrections'], [{'id': 'h', 'op': 'set_opponent_hand', 'turns': [3], 'note': 'the hand is 6', 'evidence': 'frames t0114'}])

    def test_no_correction_leaves_the_ledger_without_the_key(self):
        led, lines = self.apply([])
        self.assertNotIn('corrections', led)
        self.assertEqual(lines, [])

    def test_the_source_ledger_file_is_not_edited(self):
        src, out = packet(self, {'schema': 'x'}, ledger_for_corrections()['turns'], QR_022530, SNAP_022530)
        with open(os.path.join(src, 'TURN_LEDGER.json'), 'rb') as f:
            before = f.read()
        N.normalize(src, out, corrections=[{'id': 'm', 'op': 'rename_pokemon', 'side': 'opponent', 'name': 'Alolan Meowth', 'to': 'Meowth'}])
        with open(os.path.join(src, 'TURN_LEDGER.json'), 'rb') as f:
            self.assertEqual(f.read(), before)
        self.assertEqual(read(os.path.join(out, 'TURN_LEDGER.json'))['corrections'][0]['id'], 'm')

    def test_the_default_corrections_are_the_ones_the_file_has_for_the_packet_name(self):
        path = os.path.join(tempfile.mkdtemp(), 'c.json')
        self.addCleanup(shutil.rmtree, os.path.dirname(path), True)
        write_json(path, {'_about': 'x', '20269999_000000000_iOS': [{'id': 'a', 'op': 'set_opponent_hand', 'counts': {'3': 6}}]})
        self.assertEqual(N.load_corrections('20269999_000000000_iOS', path)[0]['id'], 'a')
        self.assertEqual(N.load_corrections('20261111_000000000_iOS', path), [])
        self.assertEqual(N.load_corrections('x', os.path.join(os.path.dirname(path), 'missing.json')), [])


class CorrectionsFile(unittest.TestCase):
    def setUp(self):
        self.data = read(N.CORRECTIONS_FILE)

    def test_every_entry_has_an_id_an_op_a_note_and_the_evidence_it_rests_on(self):
        ids = []
        for game, ops in self.data.items():
            if game.startswith('_'):
                continue
            self.assertRegex(game, r'^2026\d{4}_\d{9}_iOS$')
            for c in ops:
                self.assertIn(c['op'], ('rename_pokemon', 'rename_tool', 'set_opponent_hand', 'replace_play'), c['id'])
                self.assertTrue(c.get('note') and c.get('evidence'), c['id'])
                self.assertIn('turns', c, c['id'])
                ids.append(c['id'])
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 7)

    def test_the_corrections_cover_the_three_misreadings_the_review_settled(self):
        ids = {c['id'] for ops in self.data.values() if isinstance(ops, list) for c in ops}
        self.assertTrue({'210823-meowth-left-bench', '015659-opponent-hands', '015659-no-rare-candy-turn-4', '022530-elegant-cape'} <= ids)


@unittest.skipUnless(glob.glob(os.path.join(QA, 'BATCH_*')), 'Recording_QA is not on this machine')
class AgainstTheRealLedgers(unittest.TestCase):
    """every recorded correction applies to the real ledger it was written for (the `was` readings and the `expect`ed plays are checked), and 022530's deck settles Dratini"""

    def packet_dir(self, game):
        found = glob.glob(os.path.join(QA, 'BATCH_*', game))
        return found[0] if found else None

    def test_every_correction_applies_to_its_ledger(self):
        data = read(N.CORRECTIONS_FILE)
        for game, ops in data.items():
            if game.startswith('_'):
                continue
            src = self.packet_dir(game)
            self.assertIsNotNone(src, game)
            out = tempfile.mkdtemp()
            self.addCleanup(shutil.rmtree, out, True)
            with open(os.devnull, 'w') as devnull:
                lines = N.normalize(src, out)
            self.assertEqual(sum(1 for l in lines if 'corrected from the frames' in l), len(ops), game)

    def test_the_deck_of_022530_has_dratini_b4_116(self):
        src = self.packet_dir('20261013_022530000_iOS')
        out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out, True)
        N.normalize(src, out)
        spec = D.read_deck(read(os.path.join(out, 'DECK_USED.json')), {})
        self.assertEqual([(e.ids, e.ambiguous) for e in spec.entries if e.name == 'Dratini'], [(['B4 116'], False)])


if __name__ == '__main__':
    unittest.main()
