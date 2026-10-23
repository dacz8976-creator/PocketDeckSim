#!/usr/bin/env python3
"""make_sources_snapshot.py's guards (PREREG_RUN3 addendum 3, D3): the real inputs pass, and each failure the Oct 21 verification
(wf_5a33f406-b62) proved on copies now stops the run. Reads the evidence read only; every mutated input is a copy under a temp folder.
  test_snapshot_guards.py EVIDENCE_ROOT QA_EXACT_DIR INDEX_CSV DECKS_JSON RULINGS_JSON"""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV, QA, INDEX, DECKS, RULINGS = (sys.argv.pop(1) for _ in range(5)) if len(sys.argv) >= 6 else (None,) * 5
BATCHES = ['DRIVE_INBOX_2026-10-20', 'DRIVE_LADDER_2026-10-19', 'DRIVE_LADDER_REMAINING_2026-10-19', 'DRIVE_INBOX_2026-10-21',
           'DRIVE_LADDER_2026-10-21_EVENING', 'DRIVE_LADDER_2026-10-23']
FROZEN_DB = '/tmp/frozen_db_70652fff.json'
# the two linked battles of DRIVE_INBOX_2026-10-21 (addendum 4's case record)
GAME01 = ('1Pe3YcccL4MVTmDWeyHnG7Uz5ZXTl5DEN', '11nTG081XdYLHpPHN9UFE6rFnq7ujo27e')
GAME06 = ('1oPEdAUQDKkSl3G4-3TgMpkOJtlaSq9eJ', '1RlG7rzxAZoBwA8OJv2khC3QNRXTob8V6')
# DRIVE_LADDER_2026-10-23's battle (battle_key + chronological_sources; the continuation links the opening's QR_ID.json by path)
BATTLE23 = ('1J23vw2SNQNk8OoacLpGX8IT01_12HEb-', '1-JWdPEk8S84x_vHmazpGcS4NthzEQhw1')
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
        battles = {p['drive_id']: p for p in w['packets'] if p.get('clips')}
        self.assertEqual(set(battles), {GAME01[0], GAME06[0], BATTLE23[0]})
        for opening, cont in (GAME01, GAME06, BATTLE23):
            b = battles[opening]
            self.assertEqual([c['drive_id'] for c in b['clips']], [opening, cont])
            self.assertEqual(b['start_utc'], b['clips'][0]['start_utc'])
            self.assertEqual(b['status'], 'in')
        self.assertIn('partial_review_note', battles[GAME06[0]])
        self.assertNotIn('partial_review_note', battles[GAME01[0]])
        self.assertFalse({GAME01[1], GAME06[1], BATTLE23[1]} & {p['drive_id'] for p in w['packets']}, 'a continuation is never a game of its own')

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

    def copy_packet(self, batch_name, drive, files=None):
        """A text-only copy of one packet into a new batch folder under tmp; returns (batch dir, packet name)."""
        src_batch = os.path.join(EV, 'DRIVE_INBOX_2026-10-21')
        name = next(n for n in os.listdir(src_batch) if n.startswith(drive))
        b = os.path.join(self.tmp, batch_name)
        for f in files or TEXT + ['RELATED_SOURCES.json']:
            if os.path.exists(os.path.join(src_batch, name, f)):
                os.makedirs(os.path.dirname(os.path.join(b, name, f)), exist_ok=True)
                shutil.copyfile(os.path.join(src_batch, name, f), os.path.join(b, name, f))
        return b, name

    def decks_variant(self, mutate):
        with open(DECKS, encoding='utf-8') as f:
            d = json.load(f)
        mutate(d['decks'])
        p = os.path.join(os.path.dirname(DECKS), f'DECKS_variant_{len(os.listdir(self.tmp))}.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f)
        self.addCleanup(os.remove, p)
        return p

    def test_7_a_battle_missing_a_clip_stops(self):
        # the opening clip of game01 without the batch that holds its continuation
        b, _ = self.copy_packet('BATCH_OPENING_ONLY', GAME01[0])
        self.stops('not exactly its listed clips', evidence=[os.path.join(EV, x) for x in BATCHES[:3]] + [b])

    def test_8_decks_must_tie_the_continuations(self):
        def drop(decks):
            for v in decks.values():
                for g in v['games']:
                    if g.get('drive_id') == GAME01[0]:
                        g['continuations'] = []
        self.stops('ties continuations', decks=self.decks_variant(drop))

    def test_9_a_partial_game_without_a_recorded_opening_is_excluded(self):
        def drop(decks):
            for v in decks.values():
                v['games'] = [g for g in v['games'] if g.get('drive_id') != GAME06[0]]
        r, w = self.run_snap(decks=self.decks_variant(drop))
        self.assertEqual(r.returncode, 0, r.stderr)
        g6 = next(p for p in w['packets'] if p['drive_id'] == GAME06[0])
        self.assertEqual(g6['status'], 'excluded')
        self.assertIn('starts mid-game', g6['reason'])

    @unittest.skipUnless(os.path.exists(FROZEN_DB), 'no frozen database copy')
    def test_10_a_continuation_with_another_code_stops(self):
        b, name = self.copy_packet('QR_ONLY', GAME01[0], ['QR_ID.json'])
        _, cname = self.copy_packet('QR_ONLY', GAME01[1], ['QR_ID.json'])
        p = os.path.join(b, cname, 'QR_ID.json')
        with open(p, encoding='utf-8-sig') as f:
            q = json.load(f)
        q['linked_payload'] = q['linked_payload'][:-6] + 'AAAAAA'
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(q, f)
        r = subprocess.run([sys.executable, '-B', os.path.join(HERE, 'make_v2_decks.py'), '--evidence', b, '--frozen-db', FROZEN_DB,
                            '--out', os.path.join(self.tmp, 'decks_bad')], capture_output=True, text=True, cwd='/home/dacz8976/pincand')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("is not its opening clip's code", r.stdout + r.stderr)

    def batch21_variant(self, label, mutate):
        """A text-only copy of the whole DRIVE_INBOX_2026-10-21 batch, changed by mutate(copy_dir); evidence = the other batches + it."""
        src_batch = os.path.join(EV, 'DRIVE_INBOX_2026-10-21')
        b = os.path.join(self.tmp, label, 'DRIVE_INBOX_2026-10-21')
        for name in os.listdir(src_batch):
            p = os.path.join(src_batch, name)
            if not os.path.isdir(p) or '_ScreenRecording' not in name:
                continue
            extra_files = [f for f in os.listdir(p) if f.startswith('LINKED_') and f.endswith('QR_ID.json')]
            for f in TEXT + ['RELATED_SOURCES.json'] + extra_files:
                if os.path.exists(os.path.join(p, f)):
                    os.makedirs(os.path.dirname(os.path.join(b, name, f)), exist_ok=True)
                    shutil.copyfile(os.path.join(p, f), os.path.join(b, name, f))
        mutate(b)
        return [os.path.join(EV, x) for x in BATCHES if x != 'DRIVE_INBOX_2026-10-21'] + [b]

    def test_12_a_battle_without_its_related_sources_stops(self):
        # game06 with RELATED_SOURCES.json gone from both clips (its battle id then lives only in SOURCE.json's recording_relationships)
        def drop(b):
            for n in os.listdir(b):
                if n.startswith(GAME06):
                    os.remove(os.path.join(b, n, 'RELATED_SOURCES.json'))
        ev = self.batch21_variant('NO_RELATED', drop)
        r, _ = self.run_snap(evidence=ev)
        self.assertNotEqual(r.returncode, 0, r.stdout[-400:])
        self.assertIn('battle', r.stdout + r.stderr)

    def test_13_a_stray_packet_naming_a_battle_stops(self):
        # the standalone 21-09-16 game given game01's RELATED_SOURCES.json
        def stray(b):
            g1 = next(n for n in os.listdir(b) if n.startswith(GAME01[0]))
            alone = next(n for n in os.listdir(b) if n.startswith('1NnyRGgRuCTy'))
            shutil.copyfile(os.path.join(b, g1, 'RELATED_SOURCES.json'), os.path.join(b, alone, 'RELATED_SOURCES.json'))
        ev = self.batch21_variant('STRAY', stray)
        self.stops('not exactly its listed clips', evidence=ev)

    def test_11_the_output_must_be_fresh(self):
        d = os.path.join(self.tmp, 'used_out')
        os.makedirs(d)
        with open(os.path.join(d, 'old.txt'), 'w') as f:
            f.write('x')
        self.stops('fresh place only', out_dir=d)


if __name__ == '__main__':
    if not RULINGS:
        sys.exit(__doc__)
    unittest.main()
