#!/usr/bin/env python3
"""Runtime validation of the rebuilt baseline printer (pg_pos with pgd_patch.py), on synthetic fixtures only. Skipped when the executables are not built.

  cd rl/ai_judge && python3 -B -m unittest discover -s tests          (PG_POS_BIN and JUDGE_PLANS_BIN name the executables)

The same checks, with their evidence written to JSON, are `python3 validate_baseline.py --out validation/baseline_printer_validation.json`.
"""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import judge  # noqa: E402
import validate_baseline as vb  # noqa: E402

HAVE = os.path.exists(vb.DEFAULT_NEW) and os.path.exists(judge.PLANS_BIN)


@unittest.skipUnless(HAVE, 'pg_pos (target-preserving build) or judge_plans is not built')
class BaselinePrinter(unittest.TestCase):
    def test_two_tool_targets_and_a_random_evolution_target_survive_every_step(self):
        ev = vb.validate(vb.DEFAULT_NEW, None)  # raises AssertionError with the labels seen when any check fails
        for pid in ('MINI-BLOWER', 'MINI-QGE', 'MINI-RETREAT'):
            self.assertEqual(len(ev['checks'][pid]['legal_target_labels']), 2)
            self.assertEqual(ev['checks'][pid]['ambiguous'], 0)

    def test_a_retreat_payment_keeps_its_energy_in_the_bots_move_list(self):
        legal, choice = vb.last_legal(vb.run_pg_pos(vb.DEFAULT_NEW, 'MINI-RETREAT', seeds=(1,), positions=vb.RET_POS))
        payments = sorted(l for l in legal if l.startswith('ChooseRetreatEnergy'))
        self.assertEqual(payments, ['ChooseRetreatEnergy#{"energies":["Fire"],"to_in_play_idx":1}', 'ChooseRetreatEnergy#{"energies":["Water"],"to_in_play_idx":1}'])
        self.assertIn(choice, payments)

    def test_the_old_executable_is_the_defect_this_fixes(self):
        old = vb.DEFAULT_OLD
        if not os.path.exists(old):
            self.skipTest('the old stage A executable is not on this machine')
        rows = vb.run_pg_pos(old, 'MINI-BLOWER', seeds=(1,))
        legal, choice = vb.last_legal(rows)
        self.assertEqual(sorted(set(l for l in legal if l.startswith('DiscardToolFromPokemon'))), ['DiscardToolFromPokemon'])  # two targets, one bare name
        legal, choice = vb.last_legal(vb.run_pg_pos(old, 'MINI-RETREAT', seeds=(1,), positions=vb.RET_POS))
        self.assertEqual(sorted(l for l in legal if l.startswith('RetreatPay')), ['RetreatPay:1', 'RetreatPay:1'])  # two payments, one label


if __name__ == '__main__':
    unittest.main()
