#!/usr/bin/env python3
"""make_sources_snapshot.py's guards (PREREG_RUN3 addendum 3, D3): the real inputs pass, and each failure the Oct 21 verification
(wf_5a33f406-b62) proved on copies now stops the run. Reads the evidence read only; every mutated input is a copy under a temp folder.
  test_snapshot_guards.py EVIDENCE_ROOT QA_EXACT_DIR INDEX_CSV DECKS_JSON RULINGS_JSON"""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
EV, QA, INDEX, DECKS, RULINGS = (sys.argv.pop(1) for _ in range(5)) if len(sys.argv) >= 6 else (None,) * 5
# every ranked batch DECKS.json is built from (PREREG_RUN3 addendum 6): the snapshot stops on a DECKS.json game whose batch isn't passed
BATCHES = ['DRIVE_INBOX_2026-10-20', 'DRIVE_LADDER_2026-10-19', 'DRIVE_LADDER_REMAINING_2026-10-19', 'DRIVE_INBOX_2026-10-21',
           'DRIVE_LADDER_2026-10-21_EVENING', 'DRIVE_LADDER_2026-10-23', 'DRIVE_LADDER_2026-10-23_EVENING', 'DRIVE_LADDER_2026-10-24',
           'DRIVE_LADDER_2026-10-25']
FROZEN_DB = '/tmp/frozen_db_70652fff.json'
# the two linked battles of DRIVE_INBOX_2026-10-21 (addendum 4's case record)
GAME01 = ('1Pe3YcccL4MVTmDWeyHnG7Uz5ZXTl5DEN', '11nTG081XdYLHpPHN9UFE6rFnq7ujo27e')
GAME06 = ('1oPEdAUQDKkSl3G4-3TgMpkOJtlaSq9eJ', '1RlG7rzxAZoBwA8OJv2khC3QNRXTob8V6')
# DRIVE_LADDER_2026-10-23's battle (battle_key + chronological_sources; the continuation links the opening's QR_ID.json by path)
BATTLE23 = ('1J23vw2SNQNk8OoacLpGX8IT01_12HEb-', '1-JWdPEk8S84x_vHmazpGcS4NthzEQhw1')
EXACT = 'QR_EXACT_LISTS_2026-10-21'
# 21-57-12: the one weak source QR (battle_full20_proven false), ruled exact (coordinator-024); 10-05-09 (list C) has a ruling and no flag;
# 22-41-23 and 21-09-16 are filmed-code games without a ruling
P21 = '1wvU9NNdUNTX2vulAgVFC6y3ivM0bbV3T'
RULED = '19RzAoy_L_AnO4rKZy5CBTIpFzsbwdQg0'
UNRULED = '1XH-pnOI64D12ud4tS8Rrbcu5XRxUtyIg'
ALONE21 = '1NnyRGgRuCTyTGt5hzqSPIdbMrE1HDVgL'
MID_GAME = 'the opening is not recorded (no pre-game code in its first clip): a recording that starts mid-game'
# (F8b) the QR files the weak flags of 21-57-12 and 22-41-23 are found in (as weak_qr and a weak_qr ruling name them)
LAB21 = f'DRIVE_INBOX_2026-10-20/{P21}_ScreenRecording_10-19-2026_21-57-12_1.mp4/QR_ID.json'
LAB22 = f'DRIVE_INBOX_2026-10-20/{UNRULED}_ScreenRecording_10-19-2026_22-41-23_1.mp4/QR_ID.json'
COVERED = 'game ruling (addendum 3 D2; to be confirmed by the coordinator)'
ASK = "the coordinator rules: add an entry to RULINGS.json's weak_qr section (decision in or excluded): stop"
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
        # (F8) the one weak source QR is recorded on its game, which counts by its ruling
        self.assertEqual({p['drive_id']: p['weak_qr'] for p in w['packets'] if p.get('weak_qr')},
                         {P21: {LAB21: {'battle_full20_proven': False}}})
        self.assertIn('deck_ruling', next(p for p in w['packets'] if p['drive_id'] == P21))
        # (F8b) today's RULINGS.json has no weak_qr section: 21-57-12's game ruling covers its flag, and the record says so
        self.assertEqual({p['drive_id']: p['weak_qr_covered_by'] for p in w['packets'] if p.get('weak_qr_covered_by')}, {P21: COVERED})
        self.assertFalse([p['drive_id'] for p in w['packets'] if 'weak_qr_ruling' in p])
        print('test_0 window counts:', json.dumps(w['counts']), file=sys.stderr)

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
        # next to DECKS.json (its deck files resolve from there); a unique name, so one test can make several
        fd, p = tempfile.mkstemp(prefix='DECKS_variant_', suffix='.json', dir=os.path.dirname(DECKS))
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(d, f)
        self.addCleanup(os.remove, p)
        return p

    @staticmethod
    def game_in(decks, drive):
        return next(g for v in decks.values() for g in v['games'] if g.get('drive_id') == drive)

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
        # (F9) with no list at all, the reason stays the one for a recording that starts mid-game, word for word
        self.assertEqual(g6['reason'], MID_GAME)

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

    def weak_stops(self, drive, place, flag, **kw):
        """(F8) the run stops on game `drive`, naming the QR file `place` and its flag, and says how to proceed."""
        r, _ = self.run_snap(**kw)
        self.assertNotEqual(r.returncode, 0, r.stdout[-500:])
        out = r.stdout + r.stderr
        for why in (f'{drive}_ScreenRecording', f'{place}: {flag}', f'no ruling for {drive}', ASK):
            self.assertIn(why, out)

    def test_14_a_weak_source_qr_needs_a_ruling(self):
        # (F8) without the check these games would pass silently as "in": the flag is in DECKS.json only, in a source of a game that counts
        p22 = f'{UNRULED}_ScreenRecording_10-19-2026_22-41-23_1.mp4'

        def own(drive, weak):
            return lambda decks: self.game_in(decks, drive)['weak'].update(weak)

        def second(drive, weak, packet):
            # a second QR source of the same recording (as make_v2_decks.py lists it under also_from)
            return lambda decks: self.game_in(decks, drive).setdefault('also_from', []).append(
                {'packet': packet, 'batch': 'BATCH_SECOND_QR', 'qr_file': 'QR_DECODE.json', 'schema': None, 'weak': weak})
        # no ruling: the game's own source, then an also_from source (its own source stays clean)
        self.weak_stops(UNRULED, f'DRIVE_INBOX_2026-10-20/{p22}/QR_ID.json', 'battle_full20_proven = false',
                        decks=self.decks_variant(own(UNRULED, {'battle_full20_proven': False})))
        self.weak_stops(UNRULED, f'BATCH_SECOND_QR/{p22}/QR_DECODE.json', 'unsaved_changes_prompt = true',
                        decks=self.decks_variant(second(UNRULED, {'unsaved_changes_prompt': True}, p22)))
        # with a ruling the game counts as before, and the flag is written in its record
        r, w = self.run_snap(decks=self.decks_variant(own(RULED, {'unsaved_changes_prompt': 'Go Back Without Saving prompt'})))
        self.assertEqual(r.returncode, 0, r.stderr)
        g = next(p for p in w['packets'] if p['drive_id'] == RULED)
        self.assertEqual((g['status'], g['weak_qr']), ('in', {f'{EXACT}/{RULED}/QR_DECODE.json': {'unsaved_changes_prompt': 'Go Back Without Saving prompt'}}))
        self.assertEqual(g.get('weak_qr_covered_by'), COVERED)
        # 21-57-12's flag moved to its also_from source (Codex's addendum): read there too, and its ruling still covers it
        def moved(decks):
            g = self.game_in(decks, P21)
            g['also_from'][0]['weak'] = dict(g['weak'])
            g['weak'] = {}
        r, w = self.run_snap(decks=self.decks_variant(moved))
        self.assertEqual(r.returncode, 0, r.stderr)
        g = next(p for p in w['packets'] if p['drive_id'] == P21)
        self.assertEqual(g['status'], 'in')
        self.assertEqual(g['weak_qr'].get(f'{EXACT}/{P21}/QR_DECODE.json'), {'battle_full20_proven': False})

    def test_15_a_partial_game_by_the_repository_route_gets_its_true_reason(self):
        # (F9) game06 (partial) with no filmed code in DECKS.json but its list by --extra-decks: still excluded (addendum 4, E2; E7),
        # with the true reason; without the fix it read "the opening is not recorded ... starts mid-game"
        with open(DECKS, encoding='utf-8') as f:
            key6 = next(k for k, v in json.load(f)['decks'].items() for g in v['games'] if g.get('drive_id') == GAME06[0])

        def drop(decks):
            for v in decks.values():
                v['games'] = [g for g in v['games'] if g.get('drive_id') != GAME06[0]]
        r, w = self.run_snap(decks=self.decks_variant(drop), extra=self.write('x_game06.json', {GAME06[0]: key6}))
        self.assertEqual(r.returncode, 0, r.stderr)
        g6 = next(p for p in w['packets'] if p['drive_id'] == GAME06[0])
        self.assertEqual((g6['status'], g6['deck']), ('excluded', key6))
        self.assertIn('the list comes by the repository route (--extra-decks), so no own filmed code shows the opening', g6['reason'])
        self.assertNotIn('not recorded', g6['reason'])
        self.assertNotIn('mid-game', g6['reason'])

    # (F8) the flag in a packet's QR file that DECKS.json does not carry (make_v2_decks.py records one QR file per packet), in a file no
    # pin names, so only this check sees it; neither game has a ruling
    B21 = 'DRIVE_INBOX_2026-10-21'

    @staticmethod
    def qr_with_flag(drive, f, weak, base=None):
        """mutate(batch copy): write f in the packet of `drive` as its file `base` (default f itself) plus the weak flag."""
        def m(b):
            d = os.path.join(b, next(n for n in os.listdir(b) if n.startswith(drive)))
            with open(os.path.join(d, base or f), encoding='utf-8-sig') as fh:
                q = json.load(fh)
            q.update(weak)
            with open(os.path.join(d, f), 'w', encoding='utf-8') as fh:
                json.dump(q, fh)
        return m

    def test_16_a_weak_flag_in_a_second_qr_file_needs_a_ruling(self):
        # a second QR file (QR_DECODE.json, the same code as its QR_ID.json) in the standalone 21-09-16 game's packet
        alone = next(n for n in os.listdir(os.path.join(EV, self.B21)) if n.startswith(ALONE21))
        self.assertFalse(os.path.exists(os.path.join(EV, self.B21, alone, 'QR_DECODE.json')))
        self.weak_stops(ALONE21, f'{self.B21}/{alone}/QR_DECODE.json', 'unsaved_changes_prompt = true', evidence=self.batch21_variant(
            'WEAK_SECOND_FILE', self.qr_with_flag(ALONE21, 'QR_DECODE.json', {'unsaved_changes_prompt': True}, base='QR_ID.json')))

    def test_17_a_weak_flag_in_a_continuation_s_linked_qr_file_needs_a_ruling(self):
        # game06's clip 2 (22-26-30): its LINKED_CLIP07_QR_ID.json, which holds the opening's code; the stop names the battle's opening
        cont = next(n for n in os.listdir(os.path.join(EV, self.B21)) if n.startswith(GAME06[1]))
        self.weak_stops(GAME06[0], f'{self.B21}/{cont}/LINKED_CLIP07_QR_ID.json', 'battle_full20_proven = false', evidence=self.batch21_variant(
            'WEAK_LINKED', self.qr_with_flag(GAME06[1], 'LINKED_CLIP07_QR_ID.json', {'battle_full20_proven': False})))

    # (F8b) RULINGS.json's optional weak_qr section: {drive id: {decision: in | excluded, flags: {file: {flag: value}}, ruling: text}}.
    # Without it (before the fix) the section was not read: a weak game without a game ruling always stopped, with remedies that needed a
    # code change, and a game ruling covered any later flag
    def weak_rulings(self, entries):
        return self.rulings_variant(lambda r: r.setdefault('weak_qr', {}).update(entries))

    def weak_decks(self, drive, weak):
        return self.decks_variant(lambda decks: self.game_in(decks, drive)['weak'].update(weak))

    def test_18_a_weak_qr_ruling_in_lets_the_game_in(self):
        # 22-41-23 (no game ruling) with a weak own source: without the fix it stops for want of a ruling
        entry = {'decision': 'in', 'flags': {LAB22: {'battle_full20_proven': False}}, 'ruling': 'coordinator-test-in (mailbox id)'}
        r, w = self.run_snap(decks=self.weak_decks(UNRULED, {'battle_full20_proven': False}), rulings=self.weak_rulings({UNRULED: entry}))
        self.assertEqual(r.returncode, 0, r.stderr)
        g = next(p for p in w['packets'] if p['drive_id'] == UNRULED)
        self.assertEqual((g['status'], g['weak_qr'], g['weak_qr_ruling']), ('in', {LAB22: {'battle_full20_proven': False}}, entry))
        self.assertNotIn('weak_qr_covered_by', g)
        self.assertEqual((w['counts']['in'], w['counts']['excluded']), (w['counts']['in_window'], 0))
        # 21-57-12 (it has a game ruling too): its weak_qr entry decides in the game ruling's place, and is the one recorded
        entry21 = {'decision': 'in', 'flags': {LAB21: {'battle_full20_proven': False}}, 'ruling': 'coordinator-test-21'}
        r, w = self.run_snap(rulings=self.weak_rulings({P21: entry21}))
        self.assertEqual(r.returncode, 0, r.stderr)
        g = next(p for p in w['packets'] if p['drive_id'] == P21)
        self.assertEqual((g['status'], g['weak_qr_ruling']), ('in', entry21))
        self.assertNotIn('weak_qr_covered_by', g)
        self.assertIn('deck_ruling', g)

    def test_19_a_weak_qr_ruling_excluded_excludes_the_game(self):
        # without the fix the run stops on 22-41-23 instead of excluding it
        entry = {'decision': 'excluded', 'flags': {LAB22: {'battle_full20_proven': False}}, 'ruling': 'coordinator-test-out (mailbox id)'}
        r, w = self.run_snap(decks=self.weak_decks(UNRULED, {'battle_full20_proven': False}), rulings=self.weak_rulings({UNRULED: entry}))
        self.assertEqual(r.returncode, 0, r.stderr)
        g = next(p for p in w['packets'] if p['drive_id'] == UNRULED)
        self.assertEqual((g['status'], g['reason']), ('excluded', f'no exact deck list: weak source QR ({LAB22}: battle_full20_proven = false): '
                                                                  'excluded by ruling coordinator-test-out (mailbox id)'))
        self.assertEqual(g['weak_qr_ruling'], entry)
        self.assertEqual((w['counts']['in'], w['counts']['excluded']), (w['counts']['in_window'] - 1, 1))

    def test_20_a_flag_the_weak_qr_ruling_does_not_name_stops(self):
        # the ruling covers the flags it names only: another flag, another file, another value stop (without the fix: the old stop,
        # or for 21-57-12 a silent pass under its game ruling)
        both = {'battle_full20_proven': False, 'unsaved_changes_prompt': True}
        one = {'decision': 'in', 'flags': {LAB22: {'battle_full20_proven': False}}, 'ruling': 'coordinator-test'}
        self.stops(f'not covered: {LAB22}: unsaved_changes_prompt = true', decks=self.weak_decks(UNRULED, both),
                   rulings=self.weak_rulings({UNRULED: one}))
        other_file = dict(one, flags={LAB22.replace('/QR_ID.json', '/QR_DECODE.json'): {'battle_full20_proven': False}})
        self.stops(f'not covered: {LAB22}: battle_full20_proven = false', decks=self.weak_decks(UNRULED, {'battle_full20_proven': False}),
                   rulings=self.weak_rulings({UNRULED: other_file}))
        other_value = dict(one, flags={LAB22: {'unsaved_changes_prompt': True}})
        self.stops(f'not covered: {LAB22}: unsaved_changes_prompt = "Go Back Without Saving prompt"',
                   decks=self.weak_decks(UNRULED, {'unsaved_changes_prompt': 'Go Back Without Saving prompt'}),
                   rulings=self.weak_rulings({UNRULED: other_value}))
        # 21-57-12's game ruling does not cover a flag its weak_qr entry leaves out
        self.stops(f'not covered: {LAB21}: battle_full20_proven = false',
                   rulings=self.weak_rulings({P21: dict(one, flags={LAB21: {'unsaved_changes_prompt': True}})}))
        # an entry for a game on which no weak flag is found (10-05-09) is not for what the sources show
        self.stops('but no weak flag is found on this game',
                   rulings=self.weak_rulings({RULED: dict(one, flags={f'{EXACT}/{RULED}/QR_DECODE.json': {'battle_full20_proven': False}})}))

    def test_21_a_malformed_weak_qr_section_stops(self):
        # without the fix the section is not read and each of these runs passes
        ok = {'decision': 'in', 'flags': {LAB22: {'battle_full20_proven': False}}, 'ruling': 'coordinator-test'}
        for why, mutate in (
                ('weak_qr: is a list', lambda r: r.update(weak_qr=[ok])),
                ('holds exactly decision, flags and ruling', lambda r: r.update(weak_qr={UNRULED: dict(ok, note='x')})),
                ('holds exactly decision, flags and ruling', lambda r: r.update(weak_qr={UNRULED: {'decision': 'in', 'flags': ok['flags']}})),
                ('is not "in" or "excluded"', lambda r: r.update(weak_qr={UNRULED: dict(ok, decision='maybe')})),
                ('no ruling', lambda r: r.update(weak_qr={UNRULED: dict(ok, ruling='  ')})),
                ('flags is empty', lambda r: r.update(weak_qr={UNRULED: dict(ok, flags={})})),
                ('is not a set of weak flags', lambda r: r.update(weak_qr={UNRULED: dict(ok, flags={LAB22: {'battle_full20_proven': True}})})),
                ('is not a set of weak flags', lambda r: r.update(weak_qr={UNRULED: dict(ok, flags={LAB22: {'cancelled': True}})})),
                ('no game in the window has this drive id', lambda r: r.update(weak_qr={'no-such-drive-id': ok})),
                ("a later clip of a battle: key the entry by the battle's opening clip's drive id",
                 lambda r: r.update(weak_qr={GAME01[1]: ok}))):
            with self.subTest(why=why):
                self.stops(why, rulings=self.rulings_variant(mutate))

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
