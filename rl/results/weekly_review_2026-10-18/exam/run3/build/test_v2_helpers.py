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

    def test_wallace_cuts_at_its_random_evolution(self):
        line = ['Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Water}', 'Attach:1Water@0 zone', 'EndTurn']
        b = pos(['Mega Sharpedo ex B4 035', 'Carvanha B4 034'])
        self.assertEqual(H.cut(line, b), line[:2])
        self.assertEqual(H.chance_steps(line, b), [0, 1])

    def test_fragrant_forest_and_lusamine(self):
        ff = pos(['Buzzwole ex A3a 043'], stadium={'card': 'Fragrant Forest B3 153'})
        self.assertEqual(H.cut(['UseStadium', 'Attach:1Grass@0 zone'], ff), ['UseStadium'])
        self.assertEqual(H.cut(['Play:Fragrant Forest', 'UseStadium', 'EndTurn'], pos(['Buzzwole ex A3a 043'])), ['Play:Fragrant Forest', 'UseStadium'])
        mixed = dict(pos(['Celesteela A3a 062']), me={'board': [{'card': 'Celesteela A3a 062', 'hp': 50}], 'discard_energy': ['Grass', 'Grass', 'Fighting']})
        same = dict(pos(['Celesteela A3a 062']), me={'board': [{'card': 'Celesteela A3a 062', 'hp': 50}], 'discard_energy': ['Grass', 'Grass', 'Grass']})
        two = dict(pos(['Celesteela A3a 062']), me={'board': [{'card': 'Celesteela A3a 062', 'hp': 50}], 'discard_energy': ['Grass', 'Fighting']})
        line = ['Play:Lusamine', 'AttachFromDiscard', 'EndTurn']
        self.assertEqual(H.cut(line, mixed), line[:2])
        self.assertEqual(H.cut(line, same), line)
        self.assertEqual(H.cut(line, two), line)

    def test_sabrina_ends_the_first_segment(self):
        """R1: after Sabrina the opponent chooses the new Active; frozen-7's lister ends the plan there, so cut() does too. A chance step
        before it still cuts first, and Sabrina is not a chance step."""
        b = pos(['Alolan Grimer A3 110'])
        line = ['Attach:1Darkness@0 zone', 'Play:Sabrina', 'Play:Poké Ball', 'EndTurn']
        self.assertEqual(H.cut(line, b), line[:2])
        self.assertEqual(H.cut(['Play:Poké Ball', 'Play:Sabrina', 'EndTurn'], b), ['Play:Poké Ball'])
        self.assertEqual(H.chance_steps(line, b), [2])

    def test_nothing_after_sabrina_needs_following(self):
        """R1: after Sabrina's stop the line is not scanned, so an unfollowed slot move after it raises nothing."""
        b = pos(['Alolan Muk B2 097', 'Dustox B4 005'])
        self.assertEqual(H.cut(['Play:Sabrina', 'Promote:0@1', 'Ability@0'], b), ['Play:Sabrina'])
        with self.assertRaises(H.Uncertain):  # without the stop, the same slot move is uncertain (as before)
            H.cut(['Promote:0@1', 'Ability@0'], b)

    def test_raticate_ability_is_a_chance_step(self):
        b = pos(["Team Rocket's Raticate ex B4a 059", 'Alolan Vulpix A2 019'])
        self.assertEqual(H.cut(['Ability@0', 'Attach:1Water@1 zone', 'EndTurn'], b), ['Ability@0'])
        self.assertEqual(H.chance_steps(['Ability@0', 'EndTurn'], b), [0])
        self.assertEqual(H.cut(["Evolve:Team Rocket's Raticate ex@1", 'Ability@1', 'EndTurn'], pos(['Alolan Vulpix A2 019', "Team Rocket's Rattata B4a 058"])),
                         ["Evolve:Team Rocket's Raticate ex@1", 'Ability@1'])

    def test_tool_stop_agrees_with_r1_segments(self):
        """validate_v2's check: v1.6's exact-stop rule, plus R1's earlier segment end (Sabrina, a chance Ability) before a later draw."""
        b = pos(['Alolan Grimer A3 110'])
        line = ['Attach:1Darkness@0 zone', 'Play:Sabrina', 'Play:Poké Ball', 'EndTurn']
        seg = H.cut(line, b)  # ends at Sabrina (2 steps); the tool stops at the Poké Ball's draw after 3
        self.assertTrue(H.tool_stop_agrees(line, seg, b, 3, True, False))
        self.assertFalse(H.tool_stop_agrees(line, seg, b, 3, True, True))   # something unmatched
        self.assertFalse(H.tool_stop_agrees(line, seg, b, 4, True, False))  # the stop is not a chance step of the line
        plain = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'EndTurn']
        self.assertTrue(H.tool_stop_agrees(plain, H.cut(plain, b), b, 2, True, False))   # v1.6's rule: the tool stops at the segment's end
        self.assertFalse(H.tool_stop_agrees(plain, H.cut(plain, b), b, 1, True, False))
        self.assertTrue(H.tool_stop_agrees(['Attach:1Darkness@0 zone', 'EndTurn'], ['Attach:1Darkness@0 zone', 'EndTurn'], b, 1, False, False))
        self.assertTrue(H.tool_stop_agrees(line, seg, b, 4, False, False))  # no chance stop: the whole line matched
        # a lister segment (R1) that ends at a knockout's promotion (an Attach) before the line's draw
        ko = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'EndTurn']
        self.assertFalse(H.tool_stop_agrees(ko, ko[:1], b, 2, True, False))
        self.assertTrue(H.tool_stop_agrees(ko, ko[:1], b, 2, True, False, from_lister=True))
        # a lister segment that runs past the tool's stop (a draw the lister does not count): only for a lister segment
        long = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'Place:Glimmet', 'EndTurn']
        self.assertTrue(H.tool_stop_agrees(long, long[:3], b, 2, True, False, from_lister=True))
        self.assertFalse(H.tool_stop_agrees(long, long[:3], b, 2, True, False))
        # a line cut() can't follow (an unfollowed slot before a chance Ability) never raises here: the stop is judged by its label
        d = pos(['Alolan Muk B2 097', 'Dustox B4 005'])
        unf = ['Promote:0@1', 'Ability@0', 'Play:Poké Ball', 'EndTurn']
        self.assertTrue(H.tool_stop_agrees(unf, unf[:2], d, 3, True, False, from_lister=True))

    def test_chance_steps_lists_all(self):
        line = ['Play:Quick-Grow Extract', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}', "Play:Professor's Research", 'EndTurn']
        self.assertEqual(H.chance_steps(line, pos(['Alolan Grimer A3 110'])), [0, 1, 2])

    def test_game_id(self):
        self.assertEqual(H.game_id('2026-10-19T22:12:18Z'), '20261019_221218000_SR')

    def built(self):
        me = {'hand': ['Poké Ball', 'Glimmet'], 'board': [H.B('Alolan Grimer A3 110', 70, 'D')], 'disc': ['Copycat'], 'dene': 'D'}
        opp = {'hand_count': 4, 'board': [H.B('Pikachu ex A1 096', 120)], 'zone': 'L'}
        return H.P('G', 5, 3, [0, 1], me, opp, ['Attach:1Darkness@0 zone', 'Play:Poké Ball'], 'v2deck_06ee642b71', 'prepare',
                   approx='the opponent\'s discard order is not shown in the review', notes='builder: from the review, turn 5',
                   draws={1: ['Glimmet']}, vpatch={'deck': ['Glimmet']})

    def test_candidate_view_strips_every_answer_field(self):
        """F5: the view a candidate gets has no answer field at any depth, exactly CANDIDATE_FIELDS, and the built position is unchanged."""
        b = self.built()
        v = H.candidate_view(b)
        self.assertEqual(set(v), set(H.CANDIDATE_FIELDS))
        self.assertFalse({k for _, k in H._key_paths(v)} & H.LEAK_KEYS)
        text = json.dumps(v, ensure_ascii=False)
        for s in b['force'] + [b['notes'], b['approximate_reason']]:
            self.assertNotIn(s, text)
        self.assertTrue(v['approximate'])  # the flag stays
        self.assertEqual(b['kind'], 'prepare')  # the build keeps its own fields (provenance), the view is a copy
        v['me']['hand'].append('X')
        self.assertNotIn('X', b['me']['hand'])

    def test_every_built_field_is_classified(self):
        """A field P() adds must be classified as a candidate field or an answer field, or candidate_view refuses the position."""
        b = self.built()
        self.assertEqual(set(b), set(H.CANDIDATE_FIELDS) | set(H.ANSWER_FIELDS))
        b['his_reason'] = 'new field'
        with self.assertRaises(H.AnswerLeak):
            H.candidate_view(b)

    def test_check_candidate_refuses_any_answer_material(self):
        """The check is not vacuous: an answer key at the top or nested, a field outside the list, his move's text, or the builder's text in
        any string field is refused."""
        b = self.built()
        good = H.candidate_view(b)
        cases = []
        for k in sorted(H.LEAK_KEYS):
            cases.append(dict(good, **{k: 'x'}))
        nested = json.loads(json.dumps(good)); nested['me']['board'][0]['kind'] = 'attack'; cases.append(nested)
        listed = json.loads(json.dumps(good)); listed['opp']['board'].append({'force': ['EndTurn']}); cases.append(listed)
        cases.append(dict(good, comment='fine'))
        cases.append(dict(good, opp_ambiguous=['Attach:1Darkness@0 zone']))
        cases.append(dict(good, stadium={'card': 'builder: from the review, turn 5'}))
        cases.append(dict(good, turn_effects=["the opponent's discard order is not shown in the review"]))
        for c in cases:
            with self.subTest(c=sorted(set(c) ^ set(good))):
                with self.assertRaises(H.AnswerLeak):
                    H.check_candidate(c, b)
        H.check_candidate(good, b)

    def test_the_check_reads_the_view_as_written(self):
        """A tuple holding an answer key, an answer-file field name, the builder's text with quotes inside a nested text, and a bare label as a
        whole text are refused; a bare label inside a longer text is not."""
        b = self.built()
        b['notes'] = 'builder: "Poké Ball" first'
        good = H.candidate_view(b)
        for c in (dict(good, turn_effects=({'force': ['EndTurn']},)),
                  dict(good, turn_effects=[{'first_segment': ['EndTurn']}]),
                  dict(good, stadium={'card': 'x', 'effects': ['see: builder: "Poké Ball" first']}),
                  dict(good, opp_ambiguous=['EndTurn'])):
            with self.assertRaises(H.AnswerLeak):
                H.check_candidate(c, dict(b, force=['EndTurn', 'Attach:1Darkness@0 zone']))
        H.check_candidate(dict(good, opp_ambiguous=['whether he could EndTurn early']), dict(b, force=['EndTurn']))

    def test_label_view_gives_his_move_and_no_builder_text(self):
        b = self.built()
        v = H.label_view(b)
        self.assertEqual(v['his_move'], b['force'])
        self.assertEqual(set(v), set(H.CANDIDATE_FIELDS) | {'his_move'})
        for k in ('notes', 'approximate_reason', 'kind', '_draws', '_vpatch'):
            self.assertNotIn(k, v)

    def test_certified_by_allows_only_his_words(self):
        """F4: a rejected or pending alternative is certified by Dustin or by the coordinator deciding from his words, never by an
        interpretation (v1.6's coordinator_interpretation)."""
        ok = {'P1': {'rejected_alternatives': [{'line': ['EndTurn'], 'certified_by': 'dustin'}],
                     'pending_alternatives': [{'line': ['EndTurn'], 'certified_by': 'coordinator_decision_from_his_words'}]}}
        H.check_certified_by(ok)
        for bad in ({'P1': {'rejected_alternatives': [{'line': ['EndTurn'], 'certified_by': 'coordinator_interpretation'}]}},
                    {'P1': {'rejected_alternatives': [{'line': ['EndTurn']}]}},
                    {'P1': {'pending_alternatives': [{'line': ['EndTurn'], 'certified_by': 'laptop'}]}}):
            with self.assertRaises(ValueError):
                H.check_certified_by(bad)

    @unittest.skipUnless(V16, 'v1.6 exam file not given')
    def test_v16_positions_pass_the_candidate_check(self):
        """On v1.6's real positions: the v2 view drops notes / approximate_reason, and no label of his move appears in any view."""
        with open(V16, encoding='utf-8') as f:
            d = json.load(f)
        for p in d['points']:
            built = dict(p['position'], id=p['id'], force=p['answer']['his_move'])
            v = H.candidate_view(built)
            self.assertNotIn('notes', v)
            self.assertNotIn('approximate_reason', v)
        print(f'\nv1.6 positions: {len(d["points"])} pass the candidate check', file=sys.stderr)

    @unittest.skipUnless(V16, 'v1.6 exam file not given')
    def test_v16_points_cut_the_same(self):
        with open(V16, encoding='utf-8') as f:
            d = json.load(f)
        same = differ = sabrina = raticate = 0
        for p in d['points']:
            a = p['answer']
            line = a.get('key_line') or a['his_move']
            new = H.cut(line, p['position'])
            if new == a['first_segment']:
                same += 1
            else:
                differ += 1
                # the expected differences (addendum 5, R1): v1.6's cut had no stop at an opponent's choice (Sabrina) or at Team Rocket's
                # Raticate ex's random Energy move; v2's ends there, inside v1.6's segment, where frozen-7's lister ends the plan
                inside = a['first_segment'][:len(new)] == new
                if inside and new[-1] == 'Play:Sabrina':
                    sabrina += 1
                elif inside and new[-1].startswith('Ability@') and any("Raticate" in b['card'] for b in p['position']['me']['board'] + [{'card': x} for x in line if x.startswith('Evolve:')]):
                    raticate += 1
        print(f'\nv1.6 points: {same} cut the same, {differ} differ ({sabrina} at Sabrina, {raticate} at Raticate ex, rule R1)', file=sys.stderr)
        self.assertEqual((differ, sabrina, raticate), (4, 1, 3))


if __name__ == '__main__':
    unittest.main()
