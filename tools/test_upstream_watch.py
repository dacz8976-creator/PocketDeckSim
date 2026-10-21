#!/usr/bin/env python3
"""Tests of tools/upstream_watch.py on a made-up upstream (a temporary git repository with merged pull requests); nothing touches the network.

  cd tools && python3 -B -m unittest -v test_upstream_watch
"""
import io, json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import upstream_watch as W  # noqa: E402


def git(d, *a):
    return subprocess.run(['git', '-C', d, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', *a], check=True, capture_output=True, text=True).stdout


def write(d, rel, text):
    p = os.path.join(d, *rel.split('/'))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def card(i, name, kind='Pokemon'):
    return {kind: {'id': i, 'name': name}}


def merge(d, branch, number, user, title, files):
    git(d, 'checkout', '-q', '-b', branch, 'main')
    for rel, text in files.items():
        write(d, rel, text)
    git(d, 'add', '-A')
    git(d, 'commit', '-q', '-m', f'work on {branch}')
    git(d, 'checkout', '-q', 'main')
    git(d, 'merge', '--no-ff', '-q', branch, '-m', f'Merge pull request #{number} from {user}/{branch}', '-m', title)


class Watch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.up = os.path.join(self.tmp.name, 'upstream')
        self.ours = os.path.join(self.tmp.name, 'ours')
        os.makedirs(self.up)
        git(self.up, 'init', '-q', '-b', 'main')
        git(self.up, 'remote', 'add', 'origin', self.up)
        write(self.up, 'src/hooks/core.rs', 'fn a() {}\n')
        write(self.up, 'src/players/bot.rs', 'fn bot() {}\n')
        write(self.up, 'src/database.rs', '// generated\n')
        write(self.up, 'README.md', 'x\n')
        write(self.up, 'database.json', json.dumps([card('A1 001', 'Bulbasaur'), card('A1 002', 'Rare Candy', 'Trainer')]))
        git(self.up, 'add', '-A')
        git(self.up, 'commit', '-q', '-m', 'start')
        self.start = git(self.up, 'rev-parse', 'HEAD').strip()
        write(self.ours, 'decks/dustin/01-test.txt', 'Energy: Darkness\n1 Kingambit B3a 043\n2 Rare Candy A3 144\n1 Misty A1 220\n')
        write(self.ours, 'decks/screen/opponents/t-x.txt', 'Energy: Fire\n2 Charizard ex A1 036\n')
        self.names = W.deck_card_names(self.ours)

    def rows(self):
        git(self.up, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        return W.report(self.up, self.start, git(self.up, 'rev-parse', 'HEAD').strip(), self.names)

    def test_deck_names_come_from_all_the_deck_folders(self):
        self.assertEqual(sorted(self.names), ['Charizard ex', 'Kingambit', 'Misty', 'Rare Candy'])
        self.assertEqual(self.names['Kingambit'], {'01-test'})

    def test_a_bot_change_is_skip_and_a_rules_fix_that_names_a_card_we_play_is_look(self):
        merge(self.up, 'bots', 8, 'bob', 'Faster search for the bots', {'src/players/bot.rs': 'fn bot() { 1 }\n'})
        merge(self.up, 'fix-king', 7, 'alice', 'Fix Overlord\'s Blade damage', {'src/hooks/core.rs': 'fn a() { /* Kingambit */ }\n', 'tests/king.rs': '// CardId::B3a043Kingambit\n'})
        rows = self.rows()
        self.assertEqual([(r['number'], r['hint'], r['who']) for r in rows], [(8, 'skip', 'bob'), (7, 'LOOK', 'alice')])
        self.assertEqual(rows[1]['hits'], ['Kingambit'])
        self.assertEqual(rows[1]['title'], "Fix Overlord's Blade damage")
        self.assertEqual(rows[0]['kinds'], {'tooling': 1})

    def test_an_engine_change_that_names_none_of_our_cards_is_only_maybe_unless_the_title_says_fix(self):
        merge(self.up, 'refactor', 9, 'carol', 'Rename a helper', {'src/hooks/core.rs': 'fn b() {}\n'})
        merge(self.up, 'panic', 10, 'carol', 'Consume stale choices instead of panicking', {'src/hooks/core.rs': 'fn c() {}\n'})
        self.assertEqual([r['hint'] for r in self.rows()], ['maybe', 'LOOK'])

    def test_new_cards_in_the_data_are_look_and_a_reprint_of_a_card_we_play_is_named(self):
        write(self.up, 'database.json', json.dumps([card('A1 001', 'Bulbasaur'), card('A1 002', 'Rare Candy', 'Trainer'), card('B9 001', 'Rare Candy', 'Trainer'), card('B9 002', 'Newmon ex')]))
        write(self.up, 'src/database.rs', '// generated, bigger\n')
        git(self.up, 'add', '-A')
        git(self.up, 'commit', '-q', '-m', 'B9')
        (r,) = self.rows()
        self.assertEqual((r['hint'], r['new_cards'], r['changed_cards'], r['reprints'], r['number']), ('LOOK', 2, 0, ['Rare Candy'], None))
        self.assertEqual(r['kinds'], {'data': 1, 'generated': 1})

    def test_generated_files_are_not_searched_for_card_names(self):
        write(self.up, 'src/database.rs', '// Kingambit Charizard\n')
        git(self.up, 'add', '-A')
        git(self.up, 'commit', '-q', '-m', 'regenerate')
        (r,) = self.rows()
        self.assertEqual((r['hint'], r['hits']), ('skip', []))

    def test_nothing_new_gives_no_rows_and_the_printout_says_so(self):
        out = io.StringIO()
        W.print_rows(self.rows(), self.names, self.start, self.start, out)
        self.assertIn('0 change(s)', out.getvalue())

    def test_the_printout_has_one_line_per_change_and_names_the_cards_too_short_to_match(self):
        merge(self.up, 'fix-king', 7, 'alice', 'Fix Kingambit', {'src/hooks/core.rs': 'Kingambit\n'})
        out = io.StringIO()
        W.print_rows(self.rows(), self.names, self.start, git(self.up, 'rev-parse', 'HEAD').strip(), out)
        text = out.getvalue()
        self.assertRegex(text, r'LOOK  \| #7 \d{4}-\d\d-\d\d alice: Fix Kingambit \| 1/0/0/0 \| - \| Kingambit')
        self.assertIn('names under 6 letters are not matched', text)
        self.assertIn('Misty', text)

    def test_mark_records_the_tip_and_the_next_report_starts_there(self):
        merge(self.up, 'fix-king', 7, 'alice', 'Fix Kingambit', {'src/hooks/core.rs': 'Kingambit\n'})
        clone = os.path.join(self.tmp.name, 'clone')
        subprocess.run(['git', 'clone', '-q', self.up, clone], check=True)
        W.main(['--clone', clone, '--no-fetch', '--since', self.start, '--repo', self.ours, '--mark'])
        tip = git(clone, 'rev-parse', 'origin/main').strip()
        self.assertEqual(W.read_state(self.ours), tip)
        merge(self.up, 'later', 11, 'dave', 'Another bot thing', {'src/players/bot.rs': 'fn z() {}\n'})
        git(clone, 'fetch', '-q', 'origin', 'main')
        out = io.StringIO()
        old = sys.stdout
        sys.stdout = out
        try:
            W.main(['--clone', clone, '--no-fetch', '--repo', self.ours])
        finally:
            sys.stdout = old
        self.assertIn('#11', out.getvalue())
        self.assertNotIn('#7', out.getvalue())

    def test_a_missing_state_file_or_clone_is_a_clear_refusal(self):
        with self.assertRaises(SystemExit) as c:
            W.read_state(self.ours)
        self.assertIn('LAST_CHECKED.txt is missing', str(c.exception))
        with self.assertRaises(SystemExit) as c:
            W.main(['--clone', os.path.join(self.tmp.name, 'nope'), '--no-fetch', '--since', 'abc1234', '--repo', self.ours])
        self.assertIn('is not a clone', str(c.exception))


if __name__ == '__main__':
    unittest.main()
