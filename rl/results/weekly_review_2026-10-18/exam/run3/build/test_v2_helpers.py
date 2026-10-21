"""Tests of exam v2's builder helpers (v2_helpers.py). usage: python3 test_v2_helpers.py [V16_EXAM_JSON]
With v1.6's exam file given, it also checks that v2's cut gives every v1.6 point's recorded first segment (counts only, nothing printed per point)."""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v2_helpers as H

V16 = sys.argv.pop(1) if len(sys.argv) > 1 else None


def pos(board, stadium=None, pid='T'):
    return {'id': pid, 'stadium': stadium, 'me': {'board': [{'card': c, 'hp': 50} for c in board]}}


class Helpers(unittest.TestCase):
    def test_deck_energy_from_decks_json(self):
        self.assertEqual(H.deck_energy('v2deck_9633a01781'), ['W', 'L', 'M'])
        self.assertEqual(H.deck_energy('v2deck_06ee642b71'), ['D'])

    def test_multi_type_zone_needs_what_the_game_showed(self):
        me = {'hand': [], 'board': []}
        opp = {'hand_count': 5, 'board': []}
        with self.assertRaises(ValueError):
            H.P('G', 3, 2, [0, 0], me, opp, [], 'v2deck_9633a01781', 'k')
        p = H.P('G', 3, 2, [0, 0], me, opp, [], 'v2deck_9633a01781', 'k', ez_now='L', ez_next='W')
        self.assertEqual((p['me']['energy_now'], p['me']['energy_next']), ('Lightning', 'Water'))
        with self.assertRaises(ValueError):
            H.P('G', 3, 2, [0, 0], me, opp, [], 'v2deck_9633a01781', 'k', ez_now='D', ez_next='W')

    def test_one_type_zone_keeps_v16s_rule(self):
        p = H.P('G', 3, 2, [0, 0], {'hand': [], 'board': []}, {'hand_count': 5, 'board': []}, [], 'v2deck_06ee642b71', 'k')
        self.assertEqual((p['me']['energy_now'], p['me']['energy_next']), ('Darkness', 'Darkness'))
        with self.assertRaises(ValueError):
            H.P('G', 3, 2, [0, 0], {'hand': [], 'board': []}, {'hand_count': 5, 'board': []}, [], 'v2deck_06ee642b71', 'k', ez_now='W')

    def test_v16_cuts(self):
        b = pos(['Alolan Grimer A3 110'])
        self.assertEqual(H.cut(['Play:Poké Ball', 'Place:Glimmet', 'Attach:1Darkness@0 zone'], b), ['Play:Poké Ball'])
        self.assertEqual(H.cut(['Attach:1Darkness@0 zone', 'Play:Mesagoza', 'UseStadium', 'Attack:Slash'], b), ['Attach:1Darkness@0 zone', 'Play:Mesagoza', 'UseStadium'])
        self.assertEqual(H.cut(['UseStadium', 'Attach:1Darkness@0 zone'], pos(['Alolan Grimer A3 110'], stadium={'card': 'Rainbow Cave'})),
                         ['UseStadium', 'Attach:1Darkness@0 zone'])
        self.assertEqual(H.cut(['Play:Quick-Grow Extract', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}', 'Attach:1Grass@1 zone'], b),
                         ['Play:Quick-Grow Extract', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}'])
        self.assertEqual(H.cut(['Attach:1Darkness@0 zone', 'EndTurn'], b), ['Attach:1Darkness@0 zone', 'EndTurn'])

    def test_dustox_ability_is_a_chance_step_by_slot(self):
        self.assertEqual(H.cut(['Attach:1Darkness@0 zone', 'Ability@0', 'Attack:Cutting Wind'], pos(['Dustox B4 005', 'Wurmple B4 001'])),
                         ['Attach:1Darkness@0 zone', 'Ability@0'])
        self.assertEqual(H.cut(['Evolve:Dustox@1', 'Ability@1', 'Attach:1Darkness@0 zone'], pos(['Alolan Muk B2 097', 'Cascoon B4 004'])),
                         ['Evolve:Dustox@1', 'Ability@1'])
        self.assertEqual(H.cut(['Retreat:1', 'Ability@1', 'EndTurn'], pos(['Dustox B4 005', 'Alolan Grimer A3 110'])), ['Retreat:1', 'Ability@1'])
        self.assertEqual(H.cut(['Place:Wurmple', 'Play:Rare Candy', 'Evolve:Dustox@2', 'Ability@2'], pos(['Alolan Muk B2 097', 'Alolan Grimer A3 110'])),
                         ['Place:Wurmple', 'Play:Rare Candy', 'Evolve:Dustox@2', 'Ability@2'])

    def test_other_abilities_are_not_chance(self):
        line = ['Ability@1', 'AttachTypedFromDiscard:Metal@0', 'Attach:1Water@0 zone', 'EndTurn']
        self.assertEqual(H.cut(line, pos(['Dragonite B4 118', 'Dragonair B4 117'])), line)

    def test_an_unfollowed_slot_move_is_uncertain(self):
        with self.assertRaises(H.Uncertain):
            H.cut(['Promote:0@1', 'Ability@0'], pos(['Alolan Muk B2 097', 'Dustox B4 005']))
        # without a chance-Ability Pokemon in play and the slots followed, an Ability is plain
        self.assertEqual(H.cut(['Ability@1', 'EndTurn'], pos(['Dragonite B4 118', 'Dragonair B4 117'])), ['Ability@1', 'EndTurn'])

    def test_chance_steps_lists_all(self):
        line = ['Play:Quick-Grow Extract', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}', "Play:Professor's Research", 'EndTurn']
        self.assertEqual(H.chance_steps(line, pos(['Alolan Grimer A3 110'])), [0, 1, 2])

    def test_game_id(self):
        self.assertEqual(H.game_id('2026-10-19T22:12:18Z'), '20261019_221218000_SR')

    @unittest.skipUnless(V16, 'v1.6 exam file not given')
    def test_v16_points_cut_the_same(self):
        with open(V16, encoding='utf-8') as f:
            d = json.load(f)
        same = differ = 0
        for p in d['points']:
            a = p['answer']
            line = a.get('key_line') or a['his_move']
            if H.cut(line, p['position']) == a['first_segment']:
                same += 1
            else:
                differ += 1
        print(f'\nv1.6 points: {same} cut the same, {differ} differ', file=sys.stderr)
        self.assertEqual(differ, 0)


if __name__ == '__main__':
    unittest.main()
