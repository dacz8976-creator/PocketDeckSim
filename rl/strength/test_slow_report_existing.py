#!/usr/bin/env python3
"""Tests for slow_report_existing.py: the slow-report page built from games that were ALREADY played (the demonstration for deck 03, Wailord).

  cd rl/strength && python3 -B -m unittest -v test_slow_report_existing

Written before the code. The sources are synthetic development-run and gate-3 run directories in temporary folders (a registered manifest, its sha256, games.jsonl
with deck logs); the only real files read are the committed pin and the registry beside the script. Nothing is played and no source is changed.

What is pinned (the coordinator's and Astra's reporting rule, Oct 7):
  * the page says in bold, first, that it is existing development evidence and not a fresh test, and that it is not the km3 floor check and has no pass or fail line;
  * the question comes first, then the size, written "N kx3 games + N cheap km3 baseline games", and each range says which games it refers to;
  * a wide interval is never dismissed: the page says what it can and cannot answer;
  * question 2 (the Tool tie-break, gate 3) counts decisions changed and results changed separately, from the games, and refuses a pairing whose build check fails;
  * the sources must be registered runs (manifest.sha256 matches), the kx3 development run must be the pinned build, the gate-3 run a different, named build;
  * the page states the full design, so a deck without exactly deals x seats x lists kx3 games and as many baseline games in BOTH runs is refused, and the pairing is
    void unless every gate-3 baseline game replays the development run and every gate-3 kx3 game starts from the development run's own deal (WholeDesign).
"""
import contextlib, hashlib, io, json, math, os, re, shutil, statistics, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402
import slow_report_existing as ex  # noqa: E402

PANEL = ['t-altaria', 't-blaziken', 't-hydreigon', 't-lucario', 't-sceptile', 't-suicune', 't-vespiquen', 't-weezing']
DECK = '03-wailord-indeedee-wall'
OTHER = '09-mega-manectric-heliolisk'
PIN = json.loads(open(os.path.join(HERE, 'slow_report_pin.json'), encoding='utf-8').read())
SC = {'deck': 1.0, 'tie': 0.5, 'opp': 0.0}


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def wilson95(scores):
    n, k = len(scores), sum(scores)
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def pc(x):
    return f'{100 * x:.1f}%'


def game(deck, opp, deal, seat, arm, winner, *, log=None, points=(3, 1), turns=9, wall=100.0):
    log = [{'t': 1, 'o': 1, 'a': 'Attack:Ram', 'n': 2, 'act': 'X', 'b': 1, 'p': [0, 0]}] if log is None else log
    return dict(key=f'{deck}|{opp}|{deal}|{seat}|{arm}', deck=deck, opp=opp, deal=deal, seat=seat, arm=arm, seed=24_400_000_000 + PANEL.index(opp) * 10_000 + deal,
                pilot_deck='kx3' if arm == 'X' else 'km3', pilot_opp='km3', first='deck' if seat == 0 else 'opp', winner=winner, points=list(points), turns=turns, plies=40,
                wall_s=wall if arm == 'X' else 1.0, moves_deck=dict(n=len(log), total_s=0.02, ms=[10.0] * len(log)), moves_opp=dict(n=1, total_s=0.01, ms=[10.0]),
                started_at='2026-10-03T12:00:00Z', log=[dict(r, ms=12.5) for r in log])


def win_x(o, d, s):
    return 'deck' if (o + 2 * d + s) % 3 == 0 else ('tie' if (o + d + s) % 7 == 0 else 'opp')


def win_ref(o, d, s):
    return 'deck' if (o + d + 2 * s) % 4 == 0 else 'opp'


def make_run(root, name, *, pilot, stage='dev', program='/home/dacz8976/kx/strength', program_sha=None, decks=(DECK, OTHER), deals=5, tools_changes=None, base=None):
    """A registered run directory. tools_changes: for a gate-3 style run, a set of (opp, deal, seat) whose X game differs from `base` games (a dict key -> record)."""
    d = os.path.join(root, name)
    man = dict(name=name, stage=stage, pilot=pilot, reference='km3', created_at='2026-10-03T11:00:00Z', threads=2, deals=deals, seats=[0, 1], seed_base=24_400_000_000,
               pair_stride=10_000, planned_games=len(decks) * 8 * deals * 4, decks=[dict(name=n, path=f'decks/dustin/{n}.txt', sha256='c' * 64) for n in decks],
               opponents=[dict(name=n, path=f'decks/screen/opponents/{n}.txt', sha256='d' * 64) for n in PANEL], program=program, program_sha256=program_sha or PIN['program_sha256'],
               selfcheck={}, engine='claude/playout-pilot d513e37b engine tree 31dbd2e6e8ec', repo_commit='abc123', repo_root='/repo')
    write(os.path.join(d, 'manifest.json'), json.dumps(man, indent=1))
    write(os.path.join(d, 'manifest.sha256'), sha(os.path.join(d, 'manifest.json')) + '  manifest.json\n')
    games = []
    for dn in decks:
        for oi, opp in enumerate(PANEL):
            for deal in range(deals):
                for seat in (0, 1):
                    for arm in ('ref', 'X'):
                        k = f'{dn}|{opp}|{deal}|{seat}|{arm}'
                        if base is not None and arm == 'ref':
                            g = dict(base[k])
                        elif base is not None and arm == 'X':
                            g = dict(base[k])
                            if (dn, opp, deal, seat) in (tools_changes or set()):
                                g['log'] = g['log'] + [dict(t=2, o=2, a='Retreat', n=3, act='X', b=1, p=[0, 0], ms=7.0)]
                                g['moves_deck'] = dict(g['moves_deck'], n=g['moves_deck']['n'] + 1)
                        else:
                            w = (win_x if arm == 'X' else win_ref)(oi, deal, seat)
                            g = game(dn, opp, deal, seat, arm, w, wall=770.0 if dn == DECK else 100.0)
                        games.append(g)
    write(os.path.join(d, 'games.jsonl'), ''.join(json.dumps(g) + '\n' for g in games))
    write(os.path.join(d, 'errors.jsonl'), '')
    write(os.path.join(d, 'run_log.jsonl'), json.dumps(dict(event='start', at='2026-10-03T12:00:00Z', threads=2, pilot=pilot)) + '\n'
          + json.dumps(dict(event='stop', at='2026-10-04T12:00:00Z', played=len(games), elapsed_s=86400.0)) + '\n')
    return d, {g['key']: g for g in games}


class Sources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.dev, self.dev_games = make_run(self.tmp, 'strength_dev', pilot='kx3')
        self.changes = {(DECK, PANEL[o], d, s) for o, d, s in [(0, 0, 0), (0, 1, 1), (0, 2, 0), (0, 3, 1), (1, 0, 0), (1, 4, 1), (2, 1, 0), (2, 2, 1), (4, 0, 0), (4, 3, 1),
                                                                 (5, 0, 1), (5, 2, 0), (6, 1, 1), (6, 4, 0), (7, 2, 1)]}  # 15 pairs whose logged decisions differ
        self.tool, _ = make_run(self.tmp, 'strength_tool', pilot='kx3_r16_c12_z2_real_t0_poolmeta_tools', program='/home/dacz8976/kx/strength_tools', program_sha='cf73b2a4e858' + '0' * 52,
                                decks=(DECK,), base=self.dev_games, tools_changes=self.changes)
        self.out = os.path.join(self.tmp, 'out')

    def go(self, *extra, dev=None, tool=None, deck=DECK):
        err, out = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ex.main(['--deck', deck, '--dev', dev or self.dev, '--tool', tool or self.tool, '--out', self.out, '--pin', os.path.join(HERE, 'slow_report_pin.json'), *extra])
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def page(self):
        code, out, err = self.go()
        self.assertEqual(code, 0, err + out)
        return read(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md'))

    def xs(self, games, key=lambda g: True):
        return [SC[g['winner']] for g in games.values() if g['deck'] == DECK and g['arm'] == 'X' and key(g)]


class Label(Sources):
    def test_the_first_lines_say_existing_evidence_not_a_fresh_test_and_name_both_pilots(self):
        text = self.page()
        head = '\n'.join(text.splitlines()[:10])
        self.assertTrue(text.startswith(f'# Slow report from existing games: {DECK}'))
        self.assertIn('**Existing development evidence, not a fresh test.**', head)
        self.assertIn(f'**kx3 (d513e37b) on {DECK} v km3 on the public panel**', head)
        self.assertIn('Nothing was played for this page', head)
        self.assertIn('not the km3 floor check', head)
        self.assertIn('no pass or fail line', head)

    def test_every_line_printed_names_both_pilots_and_says_what_it_is(self):
        code, out, err = self.go()
        self.assertEqual(code, 0, err)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines)
        for l in lines:
            self.assertTrue(l.startswith(f'[kx3 (d513e37b) on {DECK} v km3 on the public panel; existing development evidence, not a fresh test]'), l)

    def test_nothing_in_the_sources_is_changed(self):
        before = {os.path.join(dp, f): sha(os.path.join(dp, f)) for r in (self.dev, self.tool) for dp, dn, fn in os.walk(r) for f in fn}
        self.page()
        after = {os.path.join(dp, f): sha(os.path.join(dp, f)) for r in (self.dev, self.tool) for dp, dn, fn in os.walk(r) for f in fn}
        self.assertEqual(before, after)

    def test_no_pass_fail_or_cutoff_words(self):
        text = re.sub(r'no pass or fail|not a ranking', '', self.page())
        for bad in (r'\bpass(es|ed)?\b', r'\bfail(s|ed|ure)?\b', r'\bverdict\b', r'\bcutoff', r'\bgood enough\b', r'\bclears?\b', r'borderline', r'\bthreshold\b'):
            self.assertIsNone(re.search(bad, text, re.I), bad)


class QuestionFirstThenSize(Sources):
    def test_each_question_comes_before_its_size_and_before_any_number(self):
        text = self.page()
        q1 = text.index('## Question 1:')
        q2 = text.index('## Question 2:')
        s1 = text.index('Size: 80 kx3 games + 80 cheap km3 baseline games')
        self.assertLess(q1, s1)
        self.assertLess(s1, q2)
        first_number = re.search(r'\d+\.\d%', text[q1:])
        self.assertGreater(first_number.start() + q1, s1, 'no result is quoted before the size')
        s2 = text.index('Size: 80 kx3 games with the Tool tie-break on')
        self.assertLess(q2, s2)
        self.assertGreater(text.index('+0.0', s2), s2)

    def test_the_questions_are_stated_in_plain_words(self):
        text = self.page()
        self.assertRegex(text, r'## Question 1: how does 03-wailord-indeedee-wall do with kx3, and is that better than with km3\?')
        self.assertRegex(text, r'## Question 2: does the Tool tie-break change what kx3 does with this deck\?')

    def test_sizes_are_written_as_n_kx3_games_plus_n_cheap_km3_baseline_games(self):
        text = self.page()
        self.assertIn('Size: 80 kx3 games + 80 cheap km3 baseline games (5 deals x 2 seats against each of the 8 public lists', text)
        self.assertIn('Size: 80 kx3 games with the Tool tie-break on + the 80 existing kx3 games with it off, paired by deal and seat (80 paired games; '
                      'and 80 cheap km3 baseline games, which the gate-3 build replays exactly)', text)
        self.assertIn('80 cheap km3 baseline games', text.split('## Question 2:')[1])

    def test_each_range_says_which_games_it_refers_to(self):
        text = self.page()
        self.assertIn('refers to the 80 kx3 games', text)
        self.assertIn('That range refers to the 80 paired games, each a deal and seat played by both pilots: 80 kx3 games + 80 cheap km3 baseline games.', text)
        self.assertIn('refers to the 80 paired games played with the Tool tie-break on and off', text)
        self.assertIn('each range refers to the 80 paired games.', text)
        self.assertNotIn('played both ways', text)
        self.assertRegex(text.split('## Against each public list')[1], r'refers to the 10 kx3 games|10 kx3 games each')


class QuestionOne(Sources):
    def test_the_score_and_its_range_are_the_dev_runs_kx3_games_for_this_deck_only(self):
        text = self.page()
        sc = self.xs(self.dev_games)
        p, lo, hi = wilson95(sc)
        self.assertEqual(len(sc), 80)
        self.assertIn(f'scored **{pc(p)}**', text)
        self.assertIn(f'probably between {pc(lo)} and {pc(hi)}', text)
        other = self.xs({k: g for k, g in self.dev_games.items()}, lambda g: False)
        self.assertEqual(other, [])

    def test_the_km3_baseline_score_is_the_dev_runs_ref_arm_for_this_deck(self):
        text = self.page()
        ref = [SC[g['winner']] for g in self.dev_games.values() if g['deck'] == DECK and g['arm'] == 'ref']
        self.assertEqual(len(ref), 80)
        self.assertIn(f'With km3, on the same deals, it scored {pc(sum(ref) / 80)} over the 80 cheap km3 baseline games.', text)

    def test_the_gain_is_the_paired_difference_with_a_t_interval(self):
        text = self.page()
        d = [SC[g['winner']] - SC[self.dev_games[k[: -len('X')] + 'ref']['winner']] for k, g in self.dev_games.items() if g['deck'] == DECK and g['arm'] == 'X']
        m, sd, n = statistics.mean(d), statistics.stdev(d), len(d)
        half = sr.t_crit(n - 1) * sd / math.sqrt(n)
        self.assertIn(f'{100 * m:+.1f} points** compared with km3 on the same deals, probably between {100 * (m - half):+.1f} and {100 * (m + half):+.1f} points (95% interval)', text)
        self.assertNotIn('give or take', text)
        self.assertNotIn('plus or minus', text)

    def test_the_gain_range_says_in_plain_words_whether_it_includes_no_gain(self):
        text = self.page()
        sec = text.split('## Question 1:')[1].split('## Question 2:')[0]
        d = [SC[g['winner']] - SC[self.dev_games[k[: -len('X')] + 'ref']['winner']] for k, g in self.dev_games.items() if g['deck'] == DECK and g['arm'] == 'X']
        m, sd, n = statistics.mean(d), statistics.stdev(d), len(d)
        half = sr.t_crit(n - 1) * sd / math.sqrt(n)
        lo, hi = m - half, m + half
        self.assertNotIn('That range runs', sec, 'the note does not repeat the numbers of the range before it')
        if lo <= 0 <= hi:
            self.assertIn('That range includes no gain at all', sec)
            self.assertIn(f'these {n} paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse', sec)
        else:
            self.assertIn('That range does not include no gain', sec)
            self.assertIn(f'on these {n} paired games kx3 did {"better" if lo > 0 else "worse"} than km3', sec)

    def test_the_width_of_the_gain_range_is_worked_out_from_the_two_ends_printed(self):
        """'(the gain's range is W points wide)': W is the difference of the two ends as printed (each rounded once), so the page never disagrees with itself by a rounding step. The
        width used to be twice the unrounded half, which printed 27.2 beside the ends +0.2 and +27.3 of this fixture."""
        text = self.page()
        a, b = re.search(r'probably between ([+-]\d+\.\d) and ([+-]\d+\.\d) points \(95% interval\)\. That range refers to the 80 paired games', text).groups()
        width = re.search(r"the gain's range is (\d+\.\d) points wide", text).group(1)
        self.assertEqual((a, b, width), ('+0.2', '+27.3', '27.1'))
        self.assertAlmostEqual(float(width), float(b) - float(a), places=6)

    def test_a_results_folder_is_named_from_rl_results_on_wherever_the_checkout_sits(self):
        self.assertEqual(ex.rel('/mnt/c/Users/x y/Pocket Deck Sim/PocketDeckSim/rl/results/strength_2026-10-03_kx3_dev'), 'rl/results/strength_2026-10-03_kx3_dev')
        self.assertEqual(ex.rel('/tmp/elsewhere/run'), '/tmp/elsewhere/run')

    def test_a_wide_interval_is_explained_not_dismissed(self):
        text = self.page()
        sec = text.split('## Question 1:')[1].split('## Question 2:')[0]
        self.assertIn('can tell', sec)
        self.assertIn('cannot tell', sec)
        for dismissive in ('within the noise', 'no real difference', 'not significant', 'meaningless', 'ignore'):
            self.assertNotIn(dismissive, text.lower(), dismissive)

    def test_per_list_rows_have_ten_games_and_wilson_ranges(self):
        text = self.page()
        for opp in PANEL:
            s = [SC[g['winner']] for g in self.dev_games.values() if g['deck'] == DECK and g['arm'] == 'X' and g['opp'] == opp]
            p, lo, hi = wilson95(s)
            row = [l for l in text.splitlines() if l.startswith(f'| {opp} ')]
            self.assertEqual(row, [f'| {opp} | 10 | {pc(p)} | {pc(lo)} to {pc(hi)} |'], opp)

    def test_the_time_the_games_took_is_stated_for_this_deck(self):
        text = self.page()
        self.assertIn('770 s a game', text)


class QuestionTwo(Sources):
    def test_decisions_changed_and_results_changed_are_counted_separately_from_the_games(self):
        text = self.page()
        sec = text.split('## Question 2:')[1]
        self.assertIn('15 of the 80 pairs had a logged decision that differed', sec)
        self.assertIn('0 of the 80 pairs had a different winner', sec)
        self.assertIn('0 of the 80 pairs ended with different points or a different number of turns', sec)

    def test_on_minus_off_is_zero_and_the_page_says_what_that_can_and_cannot_answer(self):
        text = self.page()
        sec = text.split('## Question 2:')[1]
        self.assertIn('+0.0 points', sec)
        self.assertIn('every one of the 80 on-minus-off differences was exactly 0', sec)
        self.assertIn('can tell', sec)
        self.assertIn('cannot tell', sec)
        # 0 results changed in 80 pairs: Wilson 95% upper bound on the share of deals whose result the rule changes
        p, lo, hi = wilson95([0.0] * 80)
        self.assertIn(f'probably no more than about {100 * hi:.1f} in 100', sec)
        self.assertNotIn('so a rule that', sec)

    def test_a_result_change_is_counted_and_the_difference_is_reported_with_its_interval(self):
        # flip the winner of three X games in the gate-3 run: three results changed
        rows = [json.loads(l) for l in read(os.path.join(self.tool, 'games.jsonl')).splitlines()]
        flipped = 0
        for r in rows:
            if r['arm'] == 'X' and r['deck'] == DECK and r['winner'] == 'opp' and flipped < 3:
                r['winner'] = 'deck'
                flipped += 1
        write(os.path.join(self.tool, 'games.jsonl'), ''.join(json.dumps(r) + '\n' for r in rows))
        # the run directory's manifest does not hold the games' hash, so the registration still matches
        text = self.page()
        sec = text.split('## Question 2:')[1]
        self.assertIn('3 of the 80 pairs had a different winner', sec)
        self.assertIn('+3.8 points', sec)  # 3 x 1 / 80
        self.assertNotIn('every one of the 80 on-minus-off differences was exactly 0', sec)

    def test_the_closing_sentence_says_what_gate_3_pooled_in_paired_games_kx3_games_and_decks(self):
        sec = self.page().split('## Question 2:')[1]
        self.assertIn('(gate 3 pooled 80 paired games, 80 kx3 games with the rule on against the same deals with it off, over 1 deck on its own page)', sec)
        self.assertNotIn('pooled 80 pairs', sec)

    def test_context_kx3_minus_km3_with_the_rule_on_and_off(self):
        text = self.page()
        sec = text.split('## Question 2:')[1]
        self.assertIn('kx3 minus km3 on the same deals: with the Tool tie-break on', sec)
        self.assertIn('off', sec)

    def test_the_build_check_is_repeated_and_a_failing_one_voids_the_pairing(self):
        rows = [json.loads(l) for l in read(os.path.join(self.tool, 'games.jsonl')).splitlines()]
        for r in rows:
            if r['arm'] == 'ref' and r['deck'] == DECK:
                r['turns'] += 1
                break
        write(os.path.join(self.tool, 'games.jsonl'), ''.join(json.dumps(r) + '\n' for r in rows))
        code, out, err = self.go()
        self.assertNotEqual(code, 0)
        self.assertIn('VOID', str(code) + err)
        self.assertFalse(os.path.exists(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md')))

    def test_the_build_check_result_is_on_the_page(self):
        text = self.page()
        self.assertIn('80 of the 80 km3 baseline games in the gate-3 run replay the development run exactly', text)

    def test_the_tool_build_is_named_as_a_candidate_and_not_the_pinned_build(self):
        text = self.page()
        sec = text.split('## Question 2:')[1]
        self.assertIn('cf73b2a4e858', sec)
        self.assertIn('not the pinned build', sec)


class Provenance(Sources):
    def test_the_sources_and_their_hashes_are_listed(self):
        text = self.page()
        sec = text.split('## Where these games come from')[1]
        for needle in ('strength_dev', 'strength_tool', sha(os.path.join(self.dev, 'games.jsonl'))[:12], sha(os.path.join(self.tool, 'games.jsonl'))[:12], '5a8f5c83a791',
                       "registered before the first of this deck's games", 'stage dev', 'only deck 03-wailord-indeedee-wall'):
            self.assertIn(needle, sec)

    def test_a_source_whose_manifest_changed_is_refused(self):
        man = json.loads(read(os.path.join(self.dev, 'manifest.json')))
        man['deals'] = 6
        write(os.path.join(self.dev, 'manifest.json'), json.dumps(man, indent=1))
        code, out, err = self.go()
        self.assertNotEqual(code, 0)
        self.assertIn('registered', str(code) + err)
        self.assertFalse(os.path.exists(self.out))

    def test_the_development_run_must_be_the_pinned_build(self):
        d, _ = make_run(self.tmp, 'strength_dev_other', pilot='kx3', program_sha='1' * 64)
        code, out, err = self.go(dev=d)
        self.assertNotEqual(code, 0)
        self.assertIn('pinned', str(code) + err)

    def test_the_development_run_must_be_a_development_run(self):
        d, _ = make_run(self.tmp, 'strength_not_dev', pilot='kx3', stage='heldout')
        code, out, err = self.go(dev=d)
        self.assertNotEqual(code, 0)
        self.assertIn('development run', str(code) + err)

    def test_the_gate_run_must_be_a_different_build_with_the_tool_rule(self):
        d, _ = make_run(self.tmp, 'strength_tool_not', pilot='kx3', decks=(DECK,), base=self.dev_games)
        code, out, err = self.go(tool=d)
        self.assertNotEqual(code, 0)
        self.assertIn('Tool tie-break', str(code) + err)

    def test_a_deck_that_is_not_in_a_source_is_refused(self):
        code, out, err = self.go(deck=OTHER)  # the gate run only has deck 03
        self.assertNotEqual(code, 0)
        self.assertIn(OTHER, str(code) + err)
        code, out, err = self.go(deck='99-nothing')
        self.assertNotEqual(code, 0)

    def test_a_gate_game_that_is_not_a_dev_deal_is_refused(self):
        rows = [json.loads(l) for l in read(os.path.join(self.tool, 'games.jsonl')).splitlines()]
        rows[0]['key'] = rows[0]['key'].replace('|0|0|', '|99|0|')
        write(os.path.join(self.tool, 'games.jsonl'), ''.join(json.dumps(r) + '\n' for r in rows))
        code, out, err = self.go()
        self.assertNotEqual(code, 0)
        self.assertIn('not a development-run deal', str(code) + err)


class WholeDesign(Sources):
    """The page states the full design (deals x seats x lists kx3 games and as many km3 baseline games, in both runs), so a deck that does not have it is refused, and the
    pairing is void unless gate 3 replays the development run: every baseline game exactly, every kx3 game from the development run's own deal. Nothing is written then."""
    HEAD = f'[kx3 (d513e37b) on {DECK} v km3 on the public panel; existing development evidence, not a fresh test] '

    def rows(self, d):
        return [json.loads(l) for l in read(os.path.join(d, 'games.jsonl')).splitlines()]

    def put_rows(self, d, rows):
        write(os.path.join(d, 'games.jsonl'), ''.join(json.dumps(r) + '\n' for r in rows))

    def edit(self, d, arm, n, change):
        """change(row) for the first n games of the deck's `arm` in run directory d; returns their keys."""
        rows = self.rows(d)
        done = [r for r in rows if r['deck'] == DECK and r['arm'] == arm][:n]
        for r in done:
            change(r)
        self.put_rows(d, rows)
        return [r['key'] for r in done]

    def drop_keys(self, d, keys):
        self.put_rows(d, [r for r in self.rows(d) if r['key'] not in keys])

    def refused(self, *fragments, void=False):
        code, out, err = self.go()
        self.assertTrue(str(code).startswith(self.HEAD + ('THE PAIRING IS VOID' if void else 'REFUSED')), code)
        for f in fragments:
            self.assertIn(f, str(code))
        self.assertTrue(str(code).endswith('Nothing was written.'), code)
        self.assertEqual(out, '', 'nothing is said as if a page had been written')
        self.assertFalse(os.path.exists(self.out), 'nothing was written')

    def test_a_deck_with_a_game_missing_from_the_development_run_is_refused_for_each_arm(self):
        for arm, who in (('X', 'kx3'), ('ref', 'baseline')):
            with self.subTest(arm=arm):
                self.setUp()
                keys = self.edit(self.dev, arm, 1, lambda r: None)
                self.drop_keys(self.dev, keys)
                self.drop_keys(self.tool, keys)  # (the same game gone from gate 3, which is built from the same deals)
                self.refused(f'REFUSED: the development run has 79 of the 80 {who} games planned for {DECK}, so a page that states the full design would not describe it.')

    def test_a_deck_with_a_game_missing_from_the_gate_3_run_alone_is_refused_for_each_arm(self):
        for arm, who in (('X', 'kx3'), ('ref', 'baseline')):
            with self.subTest(arm=arm):
                self.setUp()
                keys = self.edit(self.tool, arm, 1, lambda r: None)
                self.drop_keys(self.tool, keys)
                self.refused(f'REFUSED: the gate-3 run has 79 of the 80 {who} games planned for {DECK}, so a page that states the full design would not describe it.')

    def test_a_deck_with_more_games_than_the_design_is_refused_too(self):
        for arm, who in (('X', 'kx3'), ('ref', 'baseline')):
            with self.subTest(arm=arm):
                self.setUp()
                rows = self.rows(self.dev)
                extra = dict(next(r for r in rows if r['deck'] == DECK and r['arm'] == arm), deal=5)
                extra['key'] = f"{DECK}|{extra['opp']}|5|{extra['seat']}|{arm}"
                self.put_rows(self.dev, rows + [extra])
                self.refused(f'REFUSED: the development run has 81 of the 80 {who} games planned for {DECK}')

    def test_other_decks_in_the_runs_are_not_counted_against_this_one(self):
        rows = self.rows(self.dev)
        self.assertTrue(any(r['deck'] == OTHER for r in rows))
        self.assertEqual(sum(1 for r in rows if r['deck'] == DECK and r['arm'] == 'X'), 80)
        self.put_rows(self.dev, [r for r in rows if r['deck'] != OTHER or r['arm'] == 'ref'])  # the other deck is left incomplete
        self.assertEqual(self.go()[0], 0)

    def test_a_baseline_game_that_does_not_replay_voids_the_pairing_and_the_count_is_exact(self):
        def seed(r): r['seed'] += 1
        def first(r): r['first'] = 'opp' if r['first'] == 'deck' else 'deck'
        def winner(r): r['winner'] = 'deck' if r['winner'] != 'deck' else 'opp'
        def points(r): r['points'] = [r['points'][0] + 1, r['points'][1]]
        def plies(r): r['plies'] += 1
        def log(r): r['log'] = r['log'] + [dict(t=2, o=2, a='Retreat', n=3, act='X', b=1, p=[0, 0], ms=7.0)]
        for name, change in (('seed', seed), ('first player', first), ('winner', winner), ('points', points), ('plies', plies), ('a logged decision', log)):
            with self.subTest(change=name):
                self.setUp()
                self.edit(self.tool, 'ref', 1, change)
                self.refused(f'THE PAIRING IS VOID: 1 of the 80 km3 baseline games in the gate-3 run do not replay the development run, so the build does not reproduce '
                             'the development run and on-minus-off cannot be read against it.', void=True)
        self.setUp()
        keys = []
        for change in (seed, winner, log):  # three different games, three different ways
            rows = self.rows(self.tool)
            r = [r for r in rows if r['deck'] == DECK and r['arm'] == 'ref' and r['key'] not in keys][0]
            keys.append(r['key'])
            change(r)
            self.put_rows(self.tool, rows)
        self.refused('THE PAIRING IS VOID: 3 of the 80 km3 baseline games in the gate-3 run do not replay', void=True)

    def test_the_times_a_baseline_game_took_are_not_part_of_what_has_to_replay(self):
        def slower(r):
            r['wall_s'] = r['wall_s'] * 3 + 1
            r['log'] = [dict(d, ms=d['ms'] + 100.0) for d in r['log']]
            r['moves_deck'] = dict(r['moves_deck'], total_s=9.0, ms=[99.0] * len(r['moves_deck']['ms']))
        self.edit(self.tool, 'ref', 80, slower)
        code, out, err = self.go()
        self.assertEqual(code, 0, err)
        self.assertIn('80 of the 80 km3 baseline games in the gate-3 run replay the development run exactly', read(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md')))

    def test_a_kx3_game_that_does_not_start_from_its_development_deal_voids_the_pairing_and_the_count_is_exact(self):
        def seed(r): r['seed'] += 1
        def first(r): r['first'] = 'opp' if r['first'] == 'deck' else 'deck'
        message = ("THE PAIRING IS VOID: {n} of the 80 kx3 games in the gate-3 run did not start from the development run's deal (seed or first player differ), "
                   'so on-minus-off would compare different games.')
        for name, change in (('seed', seed), ('first player', first)):
            with self.subTest(change=name):
                self.setUp()
                self.edit(self.tool, 'X', 1, change)
                self.refused(message.format(n=1), void=True)
        self.setUp()
        rows = self.rows(self.tool)
        xs = [r for r in rows if r['deck'] == DECK and r['arm'] == 'X']
        seed(xs[0])
        first(xs[1])
        first(xs[2])
        self.put_rows(self.tool, rows)
        self.refused(message.format(n=3), void=True)

    def test_a_kx3_game_with_another_result_or_another_decision_is_not_void_that_is_what_the_rule_changes(self):
        def winner(r): r['winner'] = 'deck' if r['winner'] != 'deck' else 'opp'
        def log(r): r['log'] = r['log'] + [dict(t=2, o=2, a='Retreat', n=3, act='X', b=1, p=[0, 0], ms=7.0)]
        self.edit(self.tool, 'X', 5, winner)
        self.edit(self.tool, 'X', 5, log)
        code, out, err = self.go()
        self.assertEqual(code, 0, err)
        self.assertIn('- 5 of the 80 pairs had a different winner.', read(os.path.join(self.out, 'SLOW_REPORT_EXISTING.md')).splitlines())


class Wording(Sources):
    def test_the_deck_is_called_this_deck_and_the_panel_the_public_lists(self):
        text = self.page()
        self.assertNotIn('this list', text)
        self.assertIn('## Against each public list', text)

    def test_the_page_says_what_it_does_not_say(self):
        text = self.page()
        sec = text.split('## What this page does not say')[1]
        for needle in ('floor check', 'ranking', 'fresh', 'ladder', 'public lists'):
            self.assertIn(needle, sec)


if __name__ == '__main__':
    unittest.main()
