"""Tests of check_lister_v2.py's logic with a stand-in for frozen-7's judge module (no lister binary, no engine).
usage: python3 test_check_lister_v2.py"""
import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_lister_v2 as C

MESA = {'card': 'Mesagoza B2a 093'}


def pos(pid, stadium=None, board=('Alolan Grimer A3 110',)):
    return {'id': pid, 'game': 'G', 'his_turn': 2, 'deck': 'd', 'turn_count': 3, 'points': [0, 0],
            'me': {'hand': [], 'discard': [], 'discard_energy': [], 'board': [{'card': c, 'hp': 70} for c in board], 'energy_now': 'Darkness',
                   'energy_next': 'Darkness', 'knockouts': 0},
            'opp': {'hand_count': 4, 'discard': [], 'discard_energy': [], 'board': [], 'knockouts': 0},
            'stadium': stadium, 'turn_effects': [], 'hand_source': 'review', 'decision_maker': 'Dustin', 'approximate': False,
            'opp_ambiguous': [], 'heldout': True, 'usable': True}


class StubJudge:
    """list_plans: the given plan lists. match_plans: a table from (point, tuple(labels)) to a plan number or an error text (each prefix of a
    line is asked separately, as frozen-7's replay would answer it). concrete_label: labels are already canonical here."""
    def __init__(self, plans, table):
        self.plans, self.table = plans, table

    def list_plans(self, ids, positions_path, decks_dir):
        return {i: self.plans[i] for i in ids}

    def match_plans(self, items, recs, positions_path, decks_dir):
        out = {}
        for pid, tag, labels in items:
            v = self.table.get((pid, tuple(labels)))
            out[tag] = (v, None) if isinstance(v, int) else (None, v or 'reaches no listed plan (capped list?)')
        return out

    @staticmethod
    def concrete_label(label):
        return label


def plans(*specs, capped=False):
    """specs: (end, last label) per plan."""
    return {'kind': 'plans', 'capped': capped,
            'plans': [{'n': i + 1, 'end': e, 'key': f'k{i + 1}', 'labels': ['…', last]} for i, (e, last) in enumerate(specs)]}


def prefixes(pid, line, numbers):
    """numbers[k-1] = what the first k steps reach (a plan number, an error text, or None)."""
    return {(pid, tuple(line[:k + 1])): n for k, n in enumerate(numbers) if n}


class CheckLister(unittest.TestCase):
    def run_check(self, positions, refs, J):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'positions.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(positions, f)
            return C.check(J, p, d, refs)

    def one(self, line, plan_specs, numbers, position=None):
        r = self.run_check([position or pos('A')], {'A': [{'id': 'key', 'labels': line}]}, StubJudge({'A': plans(*plan_specs)}, prefixes('A', line, numbers)))
        return r, r['rows'][0]

    def test_a_clean_chance_point_passes(self):
        """cut() stops at Poké Ball (2 steps); plan 1's last step is Poké Ball, reached first after 2 steps."""
        line = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'Place:Glimmet']
        r, row = self.one(line, [('chance', 'Play:Poké Ball'), ('end_turn', 'EndTurn')], [2, 1, 1])
        self.assertEqual((row['verdict'], row['lister_steps'], row['cut_steps'], row['cut_stop']), ('pass', 2, 2, 'chance'))

    def test_a_clean_end_of_turn_point_passes(self):
        line = ['Attach:1Darkness@0 zone', 'Attack:Slash']
        r, row = self.one(line, [('attack', 'Attack:Slash'), ('end_turn', 'EndTurn')], [2, 1])
        self.assertEqual(row['verdict'], 'pass')

    def test_a_forced_step_does_not_shorten_the_lister_segment(self):
        """Wallace with one target: the prefix ending at Play:Wallace already reaches plan 1 (replay takes the forced random evolution), but
        the lister's segment ends at plan 1's own last step, the ChooseRandomEvolutionTarget, as cut() does."""
        rand = 'ChooseRandomEvolutionTarget#{"in_play_idx":1}'
        line = ['Attach:1Water@0 zone', 'Play:Wallace', rand, 'EndTurn']
        r, row = self.one(line, [('chance', rand), ('end_turn', 'EndTurn')], [2, 1, 1, 1], pos('A', board=('Mega Sharpedo ex B4 035', 'Carvanha B4 034')))
        self.assertEqual((row['verdict'], row['lister_steps'], row['cut_steps']), ('pass', 3, 3))

    def test_the_lister_stopping_before_cut_is_resolved_by_r1(self):
        """Mesagoza in play: cut() stops at UseStadium (2 steps), but the plan the line reaches ends at the Attach (1 step)."""
        line = ['Attach:1Darkness@0 zone', 'UseStadium', 'Attack:Slash']
        r, row = self.one(line, [('chance', 'Attach:1Darkness@0 zone')], [1, 1, 1], pos('A', MESA))
        self.assertEqual((row['verdict'], [p['type'] for p in row['problems']], row['lister_segment']), ('resolved_by_R1', ['cut_differs'], line[:1]))
        self.assertEqual(r['points_resolved_by_R1'], ['A'])

    def test_the_lister_not_stopping_where_cut_does_is_resolved_by_r1(self):
        line = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'Attack:Slash']
        r, row = self.one(line, [('attack', 'Attack:Slash')], [None, None, 1])
        self.assertEqual((row['verdict'], row['lister_steps']), ('resolved_by_R1', 3))

    def test_an_opponent_choice_cut_does_not_know_is_resolved_by_r1(self):
        """A knockout's promotion (for example by an Ability's damage after an Attach): the lister's plan stops after the Attach."""
        line = ['Attach:1Darkness@0 zone', 'Play:Poké Ball', 'EndTurn']
        r, row = self.one(line, [('opponent_choice', 'Attach:1Darkness@0 zone'), ('chance', 'Play:Poké Ball')], [1, 1, 1])
        self.assertEqual((row['verdict'], row['lister_steps'], row['cut_steps']), ('resolved_by_R1', 1, 2))

    def test_sabrina_passes(self):
        line = ['Attach:1Darkness@0 zone', 'Play:Sabrina', 'EndTurn']
        r, row = self.one(line, [('opponent_choice', 'Play:Sabrina'), ('end_turn', 'EndTurn')], [2, 1, 1])
        self.assertEqual((row['verdict'], row['cut_stop']), ('pass', 'opponent_choice'))

    def test_an_uncertain_cut_is_recorded_not_a_crash(self):
        line = ['Promote:0@1', 'Ability@0', 'EndTurn']
        r, row = self.one(line, [('chance', 'Ability@0')], [None, 1, 1], pos('A', board=('Alolan Muk B2 097', 'Dustox B4 005')))
        self.assertEqual((row['verdict'], [p['type'] for p in row['problems']], row['cut_steps']), ('resolved_by_R1', ['uncertain_cut'], None))

    def test_no_plan_ambiguous_and_capped_need_a_drop(self):
        line = ['Attach:1Darkness@0 zone', 'EndTurn']
        r, row = self.one(line, [('end_turn', 'EndTurn')], [None, None])
        self.assertEqual((row['verdict'], row['problems'][0]['type']), ('drop', 'no_plan'))
        r, row = self.one(line, [('end_turn', 'EndTurn')], [None, 'ambiguous: the move list fits 2 different listed plans [1, 2]'])
        self.assertEqual((row['verdict'], row['problems'][0]['type']), ('drop', 'ambiguous'))
        J = StubJudge({'A': plans(('end_turn', 'EndTurn'), capped=True)}, prefixes('A', line, [1, 1]))
        r = self.run_check([pos('A')], {'A': [{'id': 'key', 'labels': line}]}, J)
        self.assertEqual((r['rows'][0]['verdict'], r['points_needing_drop']), ('drop', ['A']))

    def test_a_failing_alternative_is_removed_not_the_point(self):
        key = ['Attach:1Darkness@0 zone', 'EndTurn']
        alt = ['Retreat:1', 'EndTurn']
        J = StubJudge({'A': plans(('end_turn', 'EndTurn'))}, prefixes('A', key, [1, 1]))
        r = self.run_check([pos('A')], {'A': [{'id': 'recorded', 'labels': key}, {'id': 'alt0', 'labels': alt}]}, J)
        v = {row['ref']: row['verdict'] for row in r['rows']}
        self.assertEqual(v, {'recorded': 'pass', 'alt0': 'remove_alternative'})
        self.assertEqual((r['points_needing_drop'], r['points_with_alternatives_to_remove'], r['points_without_key_line']), ([], ['A'], []))

    def test_a_point_without_a_key_line_is_listed(self):
        line = ['Attach:1Darkness@0 zone', 'EndTurn']
        J = StubJudge({'A': plans(('end_turn', 'EndTurn'))}, prefixes('A', line, [1, 1]))
        r = self.run_check([pos('A')], {'A': [{'id': 'alt0', 'labels': line}]}, J)
        self.assertEqual(r['points_without_key_line'], ['A'])

    def test_drops_out_has_no_labels(self):
        line = ['Attach:1Darkness@0 zone', 'UseStadium', 'Attack:Slash']
        r, _ = self.one(line, [('chance', 'Attach:1Darkness@0 zone')], [1, 1, 1], pos('A', MESA))
        with tempfile.TemporaryDirectory() as d:
            C.write_drops(r, d)
            with open(os.path.join(d, 'A.txt'), encoding='utf-8') as f:
                text = f.read()
        self.assertIn('cut_differs', text)
        for l in line:
            self.assertNotIn(l, text)

    def test_bad_inputs_stop(self):
        J = StubJudge({'A': plans(('end_turn', 'EndTurn'))}, {})
        with self.assertRaises(SystemExit):  # a point without references
            self.run_check([pos('A'), pos('B')], {'A': [{'id': 'key', 'labels': ['EndTurn']}]}, J)
        with self.assertRaises(SystemExit):  # an empty reference list
            self.run_check([pos('A')], {'A': []}, J)
        with self.assertRaises(SystemExit):  # a reference without labels
            self.run_check([pos('A')], {'A': [{'id': 'key', 'labels': []}]}, J)
        with self.assertRaises(SystemExit):  # the same position twice
            self.run_check([pos('A'), pos('A')], {'A': [{'id': 'key', 'labels': ['EndTurn']}]}, J)
        with self.assertRaises(C.H.AnswerLeak):  # the lister must see the candidate view only
            self.run_check([dict(pos('A'), force=['EndTurn'])], {'A': [{'id': 'key', 'labels': ['EndTurn']}]}, J)


if __name__ == '__main__':
    unittest.main()
