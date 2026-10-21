#!/usr/bin/env python3
"""make_sources_snapshot.py's guards (PREREG_RUN3 addendum 3, D3): the real inputs pass, and each failure the Oct 21 verification
(wf_5a33f406-b62) proved on copies now stops the run. Reads the evidence read only; every mutated input is a copy under a temp folder.
  test_snapshot_guards.py EVIDENCE_ROOT QA_EXACT_DIR INDEX_CSV DECKS_JSON RULINGS_JSON"""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV, QA, INDEX, DECKS, RULINGS = (sys.argv.pop(1) for _ in range(5)) if len(sys.argv) >= 6 else (None,) * 5
BATCHES = ['DRIVE_INBOX_2026-10-20', 'DRIVE_LADDER_2026-10-19', 'DRIVE_LADDER_REMAINING_2026-10-19']
EXACT = 'QR_EXACT_LISTS_2026-10-21'
TEXT = ['REVIEW.md', 'LEAD_ACCEPTANCE.json', 'LADDER_ENTRY.json', 'LADDER_SAVED.json', 'QR_ID.json', 'QR_DECODE.json', 'UNCERTAINTIES.json',
        'SOURCE.json', 'FINDINGS.json', 'COVERAGE.md', 'CANDIDATE_FREEZE.json', 'FIRST_PASS_FREEZE.json', 'REVIEW_METRICS.json',
        'NATIVE_EVIDENCE.json', 'READY.json', 'ROOT_TEXT_CORRECTION.json', 'independent/VERIFICATION.json']


class Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def run_snap(self, *, evidence=None, decks=DECKS, exact=None, summary=None, rulings=None, extra=None, no_exact=False, out_dir=None):
        out = tempfile.mkdtemp(dir=self.tmp)
        args = [sys.executable, '-B', os.path.join(HERE, 'make_sources_snapshot.py'), '--evidence', *(evidence or [os.path.join(EV, b) for b in BATCHES]),
                '--index', INDEX, '--decks', decks, '--out', out_dir or os.path.join(out, 'sources'), '--window-out', os.path.join(out, 'window.json')]
        if not no_exact:
            args += ['--exact-lists', exact or os.path.join(EV, EXACT), '--exact-summary', summary or QA]
        if rulings is not False and not no_exact:
            args += ['--rulings', rulings or RULINGS]
        if extra:
            args += ['--extra-decks', extra]
        r = subprocess.run(args, capture_output=True, text=True)
        w = None
        if os.path.exists(os.path.join(out, 'window.json')):
            with open(os.path.join(out, 'window.json')) as f:
                w = json.load(f)
        shutil.rmtree(out)
        return r, w

    def write(self, name, obj):
        p = os.path.join(self.tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f)
        return p

    def stops(self, why, **kw):
        r, _ = self.run_snap(**kw)
        self.assertNotEqual(r.returncode, 0, r.stdout[-500:])
        self.assertIn(why, r.stdout + r.stderr)

    def summary_copy(self, mutate):
        d = tempfile.mkdtemp(dir=self.tmp)
        for f in os.listdir(QA):
            if os.path.isfile(os.path.join(QA, f)) and f.endswith(('.json', '.md')):
                shutil.copyfile(os.path.join(QA, f), os.path.join(d, f))
        p = os.path.join(d, 'SUMMARY_DRIVE_VERIFICATION.json')
        with open(p, encoding='utf-8-sig') as f:
            s = json.load(f)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(mutate(s), f)
        return d

    def rulings_variant(self, mutate):
        with open(RULINGS, encoding='utf-8') as f:
            r = json.load(f)
        mutate(r)
        return self.write(f'rulings_{len(os.listdir(self.tmp))}.json', r)

    def test_0_real_inputs_pass(self):
        r, w = self.run_snap()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((w['counts']['in'], w['counts']['excluded']), (w['counts']['in_window'], 0))
        lim = [(p['drive_id'], p['deck_ruling']['limit']) for p in w['packets'] if p.get('deck_ruling', {}).get('limit')]
        self.assertEqual(lim, [('1wvU9NNdUNTX2vulAgVFC6y3ivM0bbV3T',
                                'decoded QR plus continuous footage of Cancel, the saved rename and selection; the saved list was not reopened')])
        self.assertEqual(sum(1 for p in w['packets'] if p.get('exact_list')), 7)

    def test_1_the_exact_lists_and_the_ruling_are_required(self):
        self.stops('required', no_exact=True)
        self.stops('required', rulings=False)
        self.stops('on one game', rulings=self.rulings_variant(
            lambda r: r['games']['19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'].update(limit='decoded QR plus continuous footage')))

    def test_2_a_missing_recording_folder_stops(self):
        d = os.path.join(self.tmp, 'exact_missing')
        shutil.copytree(os.path.join(EV, EXACT), d)
        shutil.rmtree(os.path.join(d, '19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'))
        self.stops('not exactly EXACT_DECKS.json', exact=d)

    def test_3_the_drive_copy_check_is_not_vacuous(self):
        self.stops('not exactly', summary=self.summary_copy(lambda s: []))
        self.stops('is not the copy Dustin linked', summary=self.summary_copy(lambda s: [dict(e, drive_id='OTHER') for e in s]))
        self.stops('is not the copy Dustin linked', summary=self.summary_copy(lambda s: [dict(e, verified=False) for e in s]))

    def test_4_the_ruling_must_cover_and_match(self):
        def typo(r):
            r['games']['1wvU9NNdUNTX2vulAgVFC6y3ivM0bbV3t'] = r['games'].pop('1wvU9NNdUNTX2vulAgVFC6y3ivM0bbV3T')
        self.stops('not exactly the exact-list recordings', rulings=self.rulings_variant(typo))
        self.stops("v Codex's", rulings=self.rulings_variant(lambda r: r['games']['19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'].update(codex_list='A')))
        self.stops("v Codex's", rulings=self.rulings_variant(lambda r: r['games']['19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'].update(exact=False)))
        self.stops('is not this packet', rulings=self.rulings_variant(
            lambda r: r['games']['19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'].update(recording='ScreenRecording_10-17-2026 10-13-06')))

    def test_5_one_game_counted_twice_stops(self):
        name = '1XH-pnOI64D12ud4tS8Rrbcu5XRxUtyIg_ScreenRecording_10-19-2026_22-41-23_1.mp4'
        src = os.path.join(EV, 'DRIVE_INBOX_2026-10-20', name)
        self.assertTrue(os.path.isdir(src), src)
        b = os.path.join(self.tmp, 'BATCH_DUP')
        for f in TEXT:
            if os.path.exists(os.path.join(src, f)):
                os.makedirs(os.path.dirname(os.path.join(b, name, f)), exist_ok=True)
                shutil.copyfile(os.path.join(src, f), os.path.join(b, name, f))
        self.stops('one game counted twice', evidence=[os.path.join(EV, x) for x in BATCHES] + [b])

    def test_6_extra_decks_are_checked(self):
        p21 = '1wvU9NNdUNTX2vulAgVFC6y3ivM0bbV3T_ScreenRecording_10-19-2026_21-57-12_1.mp4'
        self.stops('two lists for one game', extra=self.write('x1.json', {p21: 'v2deck_06ee642b71'}))
        self.stops('match no packet', extra=self.write('x2.json', {'no-such-recording': 'v2deck_06ee642b71'}))
        self.stops('no such deck file', extra=self.write('x3.json', {p21: 'v2deck_nonexistent'}))

    def test_7_a_clip_of_a_linked_battle_stops(self):
        # metadata only (SOURCE, LEAD_ACCEPTANCE, QR_ID) of the second clip of DRIVE_INBOX_2026-10-21's linked battle
        src_batch = os.path.join(EV, 'DRIVE_INBOX_2026-10-21')
        name = next(n for n in os.listdir(src_batch) if n.startswith('11nTG081XdYL'))
        b = os.path.join(self.tmp, 'BATCH_LINKED', name)
        os.makedirs(b)
        for f in ('SOURCE.json', 'LEAD_ACCEPTANCE.json', 'QR_ID.json'):
            shutil.copyfile(os.path.join(src_batch, name, f), os.path.join(b, f))
        self.stops('a clip of a linked battle', evidence=[os.path.join(EV, x) for x in BATCHES] + [os.path.dirname(b)])

    def test_8_the_output_must_be_fresh(self):
        d = os.path.join(self.tmp, 'used_out')
        os.makedirs(d)
        with open(os.path.join(d, 'old.txt'), 'w') as f:
            f.write('x')
        self.stops('fresh place only', out_dir=d)


if __name__ == '__main__':
    if not RULINGS:
        sys.exit(__doc__)
    unittest.main()
