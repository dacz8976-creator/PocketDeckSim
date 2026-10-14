#!/usr/bin/env python3
"""Tests for tools/battle_logs_cleanup.py, on made-up folder trees (nothing here touches the real Battle Logs).

  cd tools && python3 -B -m unittest -v test_battle_logs_cleanup"""
import contextlib, io, json, os, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battle_logs_cleanup as bl  # noqa: E402

AUDIT = bl.AUDIT_LIST


def write(path, data=b'x'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode())


class Tree:
    """a made-up Battle Logs folder: Battle Logs/Recording_QA/BATCH_*/<game packets>, plus things that must never be touched"""

    def __init__(self, test):
        self.root = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.root, True)
        self.logs = os.path.join(self.root, 'Battle Logs')
        self.qa = os.path.join(self.logs, 'Recording_QA')
        os.makedirs(self.qa)

    def game(self, batch, name, text=True, frames=3):
        gp = os.path.join(self.qa, batch, name)
        os.makedirs(gp, exist_ok=True)
        if text:
            for t in bl.TEXT_REQUIRED:
                write(os.path.join(gp, t), '{"ok": 1}' if t.endswith('.json') else '# review')
        write(os.path.join(gp, 'SOURCE.json'), '{}')
        write(os.path.join(gp, 'notes.txt'), 'notes')
        write(os.path.join(gp, 'extract_seek.py'), 'print(1)')
        for i in range(frames):
            write(os.path.join(gp, 'turn_evidence', f't{i:04d}.jpg'), b'j' * 100)
        write(os.path.join(gp, 'comparison.JPG'), b'J' * 50)
        write(os.path.join(gp, 'independent_sol', 'deep', 'f0.png'), b'p' * 70)
        write(os.path.join(gp, 'overview', 'o.jpeg'), b'e' * 30)
        return gp

    def extras(self, batch):
        write(os.path.join(self.qa, batch, 'qr_support', 'q.png'), b'q' * 10)         # a sub-folder that is not a game packet
        write(os.path.join(self.qa, batch, 'LIVE_SAVE_SUMMARY.png'), b's' * 10)        # an image at the batch level
        write(os.path.join(self.qa, batch, 'README.md'), '# batch')
        write(os.path.join(self.qa, batch, 'DOWNLOAD_SUCCESS.json'), '{}')

    def outside(self):
        write(os.path.join(self.logs, 'Reviewed', 'game.MP4'), b'v' * 1000)
        write(os.path.join(self.logs, 'Reviewed', 'frame.jpg'), b'f' * 20)
        write(os.path.join(self.logs, '20261014_160506000_iOS.MP4'), b'v' * 1000)
        write(os.path.join(self.logs, 'MEDIA_LOCATIONS.json'), '{}')
        write(os.path.join(self.qa, '20260926_old_sol', 'f.png'), b'o' * 5)            # a non-BATCH folder inside Recording_QA
        write(os.path.join(self.qa, 'compression_check.png'), b'c' * 5)                # an image at the top of Recording_QA

    def files(self):
        out = {}
        for root, _, fs in os.walk(self.root):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, self.root)] = os.path.getsize(p)
        return out


def index(folders, games=None, pending=None, confirmed='laptop 2026-10-14', found=True):
    """a RepoIndex: `folders` are 'BATCH/game' names that are in the repo; `games` the audited ones (default: all of them)"""
    meta = {f: (f'kw-{f.split("/")[1][2:].replace("_iOS", "")}', 'rl/results/pause_games_x/games_meta.json', 5) for f in folders}
    keys = {v[0]: {'folder': f, 'tier': 'A'} for f, v in meta.items()} if games is None else games
    audit = {'confirmed': confirmed, 'games': keys, 'pending': pending or {}}
    return bl.RepoIndex(meta, audit if found else {}, found)


def decide_for(tree, idx):
    return bl.decide(bl.scan_qa(tree.qa), idx)


class DecisionRule(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.game('BATCH_A', '20261001_000000002_iOS')

    def one(self, idx):
        return decide_for(self.t, idx)[0]

    def both(self):
        return ['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS']

    def test_a_batch_whose_every_game_is_in_the_repo_audited_and_has_its_text_is_marked_delete(self):
        d = self.one(index(self.both()))
        self.assertTrue(d.delete, d.why)
        self.assertEqual(d.frames, 2 * 6)
        self.assertIn('all 2 game packets', d.why)

    def test_a_game_not_in_a_committed_games_meta_stays_and_makes_the_batch_partial(self):
        d = self.one(index(self.both()[:1]))
        self.assertFalse(d.delete)
        self.assertEqual(d.verdict, 'PARTIAL')
        bad = [g for g in d.games if not g.ok]
        self.assertEqual([g.game.name for g in bad], ['20261001_000000002_iOS'])
        self.assertIn('not in the repo', bad[0].reasons[0])
        self.assertIn('1 of 2 game packets held back', d.why)
        self.assertEqual((d.frames, d.kept_frames), (6, 6))

    def test_a_batch_where_no_game_passes_is_keep(self):
        d = self.one(index([]))
        self.assertEqual((d.verdict, d.frames, d.kept_frames), ('keep', 0, 12))

    def test_a_game_in_the_repo_but_not_in_the_audit_list_is_not_deleted(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}
        d = self.one(index(self.both(), games=keys))
        self.assertFalse(d.delete)
        self.assertIn('not audited', ' '.join(d.games[1].reasons))

    def test_a_game_the_list_only_proposes_is_not_deleted_and_the_reason_is_shown(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}
        d = self.one(index(self.both(), games=keys, pending={'kw-261001_000000002': {'why': 'no panel compared it'}}))
        self.assertFalse(d.delete)
        self.assertIn('pending', ' '.join(d.games[1].reasons))
        self.assertIn('no panel compared it', ' '.join(d.games[1].reasons))

    def test_an_audit_entry_that_names_another_folder_does_not_count(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}, 'kw-261001_000000002': {'folder': 'BATCH_Z/20261001_000000002_iOS'}}
        d = self.one(index(self.both(), games=keys))
        self.assertFalse(d.delete)
        self.assertIn('not here', ' '.join(d.games[1].reasons))

    def test_with_no_audit_list_committed_nothing_is_deleted(self):
        d = self.one(index(self.both(), found=False))
        self.assertFalse(d.delete)
        self.assertIn('not committed', ' '.join(d.games[0].reasons))

    def test_a_game_missing_one_of_its_text_outputs_is_kept(self):
        os.remove(os.path.join(self.t.qa, 'BATCH_A', '20261001_000000002_iOS', 'TURN_LEDGER.json'))
        d = self.one(index(self.both()))
        self.assertFalse(d.delete)
        self.assertIn('TURN_LEDGER.json missing', ' '.join(d.games[1].reasons))

    def test_an_empty_text_output_counts_as_missing(self):
        write(os.path.join(self.t.qa, 'BATCH_A', '20261001_000000001_iOS', 'REVIEW.md'), b'')
        d = self.one(index(self.both()))
        self.assertFalse(d.delete)
        self.assertIn('REVIEW.md missing or empty', ' '.join(d.games[0].reasons))

    def test_a_batch_with_no_game_packets_is_kept(self):
        write(os.path.join(self.t.qa, 'BATCH_EMPTY', 'README.md'), 'x')
        d = [x for x in decide_for(self.t, index(self.both())) if x.batch.name == 'BATCH_EMPTY'][0]
        self.assertFalse(d.delete)
        self.assertIn('no game packets', d.why)

    def test_sub_folders_that_are_not_game_packets_and_batch_level_images_do_not_decide_and_are_counted(self):
        self.t.extras('BATCH_A')
        d = self.one(index(self.both()))
        self.assertTrue(d.delete)
        self.assertEqual((d.batch.support_frames, d.batch.root_frames), (1, 1))
        self.assertEqual(len(d.games), 2)

    def test_only_directories_named_like_game_packets_are_games(self):
        for name in ('__pycache__', 'STALLED_INTAKE_LOCK_17244', 'LIVE_UPDATE_20261013', 'qr_support'):
            os.makedirs(os.path.join(self.t.qa, 'BATCH_A', name))
        self.assertEqual(len(self.one(index(self.both())).games), 2)


class IndexFromTheRepo(unittest.TestCase):
    def repo(self, committed=True):
        self.repo_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo_dir, True)
        base = os.path.join(self.repo_dir, 'rl', 'results', 'pause_games_new_2026-10-12')
        write(os.path.join(base, 'games_meta.json'), json.dumps({
            'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'has_ledger': True},
            'kw-261001_000000002': {'folder': 'BATCH_A/20261001_000000002_iOS', 'has_ledger': True}}))
        write(os.path.join(base, 'positions_all.json'), json.dumps([{'game': 'kw-261001_000000001', 'id': 'p1'}]))      # no position for the second game
        write(os.path.join(self.repo_dir, AUDIT), json.dumps({'confirmed': 'laptop', 'games': {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}}))

    def test_a_game_counts_only_when_its_positions_are_in_the_positions_file_next_to_the_meta(self):
        self.repo()
        idx = bl.build_index(bl.RepoView(self.repo_dir, no_git=True))
        self.assertEqual(sorted(idx.folders), ['BATCH_A/20261001_000000001_iOS'])
        self.assertEqual(idx.folders['BATCH_A/20261001_000000001_iOS'][0], 'kw-261001_000000001')
        self.assertTrue(idx.audit_path_found)

    def test_only_pause_games_result_folders_are_read(self):
        self.repo()
        other = os.path.join(self.repo_dir, 'rl', 'results', 'something_else')
        write(os.path.join(other, 'games_meta.json'), json.dumps({'kw-x': {'folder': 'BATCH_B/g'}}))
        write(os.path.join(other, 'positions_all.json'), json.dumps([{'game': 'kw-x'}]))
        self.assertNotIn('BATCH_B/g', bl.build_index(bl.RepoView(self.repo_dir, no_git=True)).folders)

    @unittest.skipUnless(shutil.which('git'), 'git not installed')
    def test_with_git_a_file_that_is_only_in_the_working_tree_is_not_in_the_repo(self):
        self.repo()
        g = lambda *a: subprocess.run(['git', '-C', self.repo_dir, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True)
        g('init', '-q', '-b', 'main')
        g('add', 'rl/results/pause_games_new_2026-10-12')
        g('commit', '-q', '-m', 'games, but not the audit list')
        # the audit list is in the working tree and not committed
        idx = bl.build_index(bl.RepoView(self.repo_dir, ref='main'))
        self.assertFalse(idx.audit_path_found)
        self.assertIn('BATCH_A/20261001_000000001_iOS', idx.folders)
        g('add', AUDIT)
        g('commit', '-q', '-m', 'audit list')
        self.assertTrue(bl.build_index(bl.RepoView(self.repo_dir, ref='main')).audit_path_found)

    @unittest.skipUnless(shutil.which('git'), 'git not installed')
    def test_a_ref_git_cannot_read_is_refused(self):
        self.repo()
        subprocess.run(['git', '-C', self.repo_dir, 'init', '-q'], check=True)
        with self.assertRaises(SystemExit) as cm:
            bl.RepoView(self.repo_dir, ref='origin/main')
        self.assertIn('refused', str(cm.exception))


class DeleteScope(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.g1 = self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.g2 = self.t.game('BATCH_A', '20261001_000000002_iOS')
        self.k = self.t.game('BATCH_KEEP', '20261001_000000003_iOS')
        self.t.extras('BATCH_A')
        self.t.extras('BATCH_KEEP')
        self.t.outside()
        self.idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'])
        self.before = self.t.files()

    def apply(self, **kw):
        decisions = decide_for(self.t, self.idx)
        out = io.StringIO()
        return bl.apply_deletions(decisions, self.t.qa, kw.pop('index', self.idx), confirm=kw.pop('confirm', lambda *a: True), out=out, **kw), out.getvalue()

    def removed(self):
        after = self.t.files()
        return sorted(set(self.before) - set(after))

    def test_every_frame_of_the_delete_batchs_game_packets_goes_at_any_depth_and_in_any_case(self):
        (deleted, failed, freed, log), _ = self.apply()
        gone = self.removed()
        frames = [p for p in self.before if p.lower().endswith(bl.FRAME_EXT) and ('BATCH_A' + os.sep + '2026') in p]
        self.assertEqual(sorted(gone), sorted(frames))
        self.assertEqual(deleted, len(frames))
        self.assertEqual((failed, freed), (0, sum(self.before[p] for p in frames)))
        self.assertTrue(any(p.endswith('comparison.JPG') for p in gone) and any(p.endswith('f0.png') for p in gone) and any(p.endswith('o.jpeg') for p in gone))

    def test_nothing_but_frames_is_ever_removed_not_json_txt_md_py_or_the_video(self):
        self.apply()
        for p in self.removed():
            self.assertTrue(p.lower().endswith(bl.FRAME_EXT), p)
        after = self.t.files()
        for p in self.before:
            if not p.lower().endswith(bl.FRAME_EXT):
                self.assertIn(p, after, p)
        self.assertTrue(all(p in after for p in self.before if p.endswith('.MP4')))

    def test_a_batch_marked_keep_loses_nothing(self):
        self.apply()
        self.assertFalse([p for p in self.removed() if 'BATCH_KEEP' in p])

    def test_images_in_non_game_sub_folders_and_at_the_batch_level_of_a_delete_batch_stay(self):
        self.t.extras('BATCH_A')
        self.apply()
        after = self.t.files()
        self.assertIn(os.path.join('Battle Logs', 'Recording_QA', 'BATCH_A', 'qr_support', 'q.png'), after)
        self.assertIn(os.path.join('Battle Logs', 'Recording_QA', 'BATCH_A', 'LIVE_SAVE_SUMMARY.png'), after)

    def test_nothing_outside_the_batch_folders_is_touched(self):
        self.apply()
        after = self.t.files()
        for p in self.before:
            if os.sep + 'BATCH_A' + os.sep not in p:
                self.assertIn(p, after, p)

    def test_empty_folders_are_left_in_place(self):
        self.apply()
        self.assertTrue(os.path.isdir(os.path.join(self.g1, 'turn_evidence')))

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_a_link_to_a_folder_outside_is_not_followed_and_its_frames_are_not_deleted(self):
        outside = os.path.join(self.t.root, 'elsewhere')
        write(os.path.join(outside, 'precious.png'), b'p')
        os.symlink(outside, os.path.join(self.g1, 'linked_frames'))
        write(os.path.join(self.t.root, 'target.jpg'), b't')
        os.symlink(os.path.join(self.t.root, 'target.jpg'), os.path.join(self.g1, 'link.jpg'))
        self.apply()
        self.assertTrue(os.path.exists(os.path.join(outside, 'precious.png')))
        self.assertTrue(os.path.exists(os.path.join(self.t.root, 'target.jpg')))

    def test_the_plan_refuses_a_path_that_is_not_a_frame_inside_a_game_packet_of_a_delete_batch(self):
        decisions = decide_for(self.t, self.idx)
        d = [x for x in decisions if x.delete][0]
        victim = os.path.join(self.t.logs, 'Reviewed', 'frame.jpg')
        d.games[0].game.frames.append((victim, 20))
        with self.assertRaises(SystemExit) as cm:
            bl.deletion_plan(decisions, self.t.qa)
        self.assertIn('not a frame file inside a game packet', str(cm.exception))
        d.games[0].game.frames.pop()
        d.games[0].game.frames.append((os.path.join(self.g1, 'notes.txt'), 5))
        with self.assertRaises(SystemExit):
            bl.deletion_plan(decisions, self.t.qa)
        d.games[0].game.frames.pop()
        d.games[0].game.frames.append((os.path.join(self.t.qa, 'BATCH_A', 'qr_support', 'q.png'), 10))
        with self.assertRaises(SystemExit):
            bl.deletion_plan(decisions, self.t.qa)
        self.assertTrue(os.path.exists(victim))

    def test_without_a_confirmation_in_the_audit_list_nothing_is_deleted(self):
        for confirmed in (None, '', '  '):
            with self.assertRaises(SystemExit) as cm:
                self.apply(index=index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'], confirmed=confirmed))
            self.assertIn('confirmed', str(cm.exception))
        self.assertEqual(self.removed(), [])

    def test_a_no_to_the_question_deletes_nothing(self):
        with self.assertRaises(SystemExit):
            self.apply(confirm=lambda *a: False)
        self.assertEqual(self.removed(), [])

    def test_the_question_names_what_will_be_deleted(self):
        seen = []
        self.apply(confirm=lambda n, size, batches: seen.append((n, size, batches)) or True)
        self.assertEqual(seen[0][2], ['BATCH_A'])
        self.assertEqual(seen[0][0], 2 * 6)

    def test_only_limits_the_deletion_and_a_batch_not_marked_delete_cannot_be_named(self):
        self.t.game('BATCH_B', '20261001_000000004_iOS')
        self.idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS', 'BATCH_B/20261001_000000004_iOS'])
        self.before = self.t.files()
        self.apply(only={'BATCH_B'})
        self.assertTrue(all('BATCH_B' in p for p in self.removed()))
        with self.assertRaises(SystemExit) as cm:
            self.apply(only={'BATCH_KEEP'})
        self.assertIn('nothing to delete', str(cm.exception))

    def test_in_a_partial_batch_only_the_packets_that_pass_lose_their_frames(self):
        self.idx = index(['BATCH_A/20261001_000000001_iOS'])        # the second game is not in the repo
        (deleted, _, _, _), _ = self.apply()
        gone = self.removed()
        self.assertTrue(gone and all('20261001_000000001_iOS' in p for p in gone))
        self.assertTrue(all(p.lower().endswith(bl.FRAME_EXT) for p in gone))
        self.assertEqual(deleted, 6)
        self.assertTrue(os.path.exists(os.path.join(self.g2, 'turn_evidence', 't0000.jpg')))

    def test_whole_batches_only_leaves_a_partial_batch_alone_and_takes_a_whole_one(self):
        self.t.game('BATCH_B', '20261001_000000004_iOS')
        self.idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_B/20261001_000000004_iOS'])      # BATCH_A is partial, BATCH_B whole
        self.before = self.t.files()
        self.apply(whole_batches_only=True)
        self.assertTrue(self.removed() and all('BATCH_B' in p for p in self.removed()))
        with self.assertRaises(SystemExit):
            self.apply(whole_batches_only=True, only={'BATCH_A'})

    def test_the_log_lists_every_removed_file_and_ends_with_a_clean_integrity_line(self):
        (_, _, _, log), out = self.apply()
        with open(log, encoding='utf-8') as f:
            lines = [json.loads(l) for l in f]
        self.assertEqual(sum(1 for l in lines if 'removed' in l), len(self.removed()))
        self.assertTrue(lines[-1]['done'])
        self.assertEqual((lines[-1]['non_frame_files_missing_after'], lines[-1]['non_frame_files_changed']), ([], []))
        self.assertIn('integrity check', out)
        self.assertTrue(os.path.basename(log).startswith('CLEANUP_LOG_'))

    def test_the_integrity_check_catches_a_text_file_that_disappears_during_the_run(self):
        real = os.remove
        state = {'n': 0}

        def evil(p):
            real(p)
            state['n'] += 1
            if state['n'] == 1:
                real(os.path.join(self.g1, 'notes.txt'))
        with mock.patch.object(bl.os, 'remove', evil):
            with self.assertRaises(SystemExit) as cm:
                self.apply()
        self.assertIn('INTEGRITY CHECK FAILED', str(cm.exception))

    def test_nothing_to_delete_is_said_and_not_confirmed(self):
        idx = index([])
        decisions = decide_for(self.t, idx)
        out = io.StringIO()
        res = bl.apply_deletions(decisions, self.t.qa, idx, confirm=lambda *a: self.fail('asked'), out=out)
        self.assertEqual(res[0], 0)
        self.assertIn('nothing to delete', out.getvalue())


class MovingTheFolder(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.outside()
        self.target = os.path.join(self.t.root, 'BattleLogs')

    def move(self, **kw):
        out = io.StringIO()
        return bl.move_folder(self.t.logs, kw.pop('target', self.target), out=out, **kw), out.getvalue()

    def test_the_whole_folder_is_renamed_and_the_new_path_is_printed(self):
        before = self.t.files()
        new, out = self.move(confirm=lambda: True)
        self.assertEqual(new, os.path.join(self.target, 'Recording_QA'))
        self.assertIn('Codex should now use', out)
        self.assertFalse(os.path.exists(self.t.logs))
        moved = {os.path.relpath(os.path.join(r, f), self.target): os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(self.target) for f in fs}
        self.assertEqual(moved, {os.path.relpath(p, 'Battle Logs'): s for p, s in before.items()})

    def test_a_target_that_exists_is_refused_even_when_empty(self):
        os.makedirs(self.target)
        with self.assertRaises(SystemExit) as cm:
            self.move(confirm=lambda: True)
        self.assertIn('already exists', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.logs))

    def test_a_target_inside_the_folder_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self.move(target=os.path.join(self.t.logs, 'inner'), confirm=lambda: True)
        self.assertIn('inside', str(cm.exception))

    def test_a_target_whose_parent_is_missing_is_refused(self):
        with self.assertRaises(SystemExit):
            self.move(target=os.path.join(self.t.root, 'nope', 'BattleLogs'), confirm=lambda: True)

    def test_the_dry_run_moves_nothing_and_does_not_ask(self):
        new, out = self.move(dry=True, confirm=lambda: self.fail('asked'))
        self.assertIsNone(new)
        self.assertIn('dry run', out)
        self.assertTrue(os.path.isdir(self.t.logs))
        self.assertFalse(os.path.exists(self.target))

    def test_a_no_moves_nothing(self):
        with self.assertRaises(SystemExit):
            self.move(confirm=lambda: False)
        self.assertTrue(os.path.isdir(self.t.logs))

    def test_a_rename_that_fails_leaves_everything_where_it_was(self):
        with mock.patch.object(bl.os, 'rename', side_effect=PermissionError('in use')):
            with self.assertRaises(SystemExit) as cm:
                self.move(confirm=lambda: True)
        self.assertIn('nothing was changed', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.logs))

    def test_files_that_name_the_old_path_are_listed_not_edited(self):
        write(os.path.join(self.t.logs, 'MEDIA_LOCATIONS.json'), json.dumps({'a': r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\x.MP4'}))
        _, out = self.move(dry=True)
        self.assertIn('MEDIA_LOCATIONS.json', out)
        with open(os.path.join(self.t.logs, 'MEDIA_LOCATIONS.json')) as f:
            self.assertIn('OneDrive', f.read())


class PathsAndCommandLine(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'posix side')
    def test_windows_paths_become_mnt_paths_in_wsl_and_back(self):
        self.assertEqual(bl.to_local(r'C:\Users\dacz8\BattleLogs'), '/mnt/c/Users/dacz8/BattleLogs')
        self.assertEqual(bl.to_local('D:/x/y'), '/mnt/d/x/y')
        self.assertEqual(bl.to_windows('/mnt/c/Users/dacz8/BattleLogs/Recording_QA'), r'C:\Users\dacz8\BattleLogs\Recording_QA')
        self.assertEqual(bl.to_windows('/tmp/x'), '/tmp/x')

    def make(self):
        t = Tree(self)
        t.game('BATCH_A', '20261001_000000001_iOS')
        t.game('BATCH_B', '20261001_000000002_iOS')
        repo = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, repo, True)
        base = os.path.join(repo, 'rl', 'results', 'pause_games_new_2026-10-12')
        write(os.path.join(base, 'games_meta.json'), json.dumps({'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}))
        write(os.path.join(base, 'positions_all.json'), json.dumps([{'game': 'kw-261001_000000001'}]))
        write(os.path.join(repo, AUDIT), json.dumps({'confirmed': None, 'games': {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}}))
        return t, repo

    def run_main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = bl.main(argv)
        return code, out.getvalue()

    def test_the_default_is_a_dry_run_that_changes_nothing_and_says_why(self):
        t, repo = self.make()
        before = t.files()
        code, out = self.run_main(['--qa-root', t.qa, '--repo', repo, '--no-git'])
        self.assertEqual(code, 0)
        self.assertEqual(t.files(), before)
        self.assertIn('BATCH_A', out)
        self.assertRegex(out, r'BATCH_A\s+DELETE')
        self.assertRegex(out, r'BATCH_B\s+keep')
        self.assertIn('not in the repo', out)
        self.assertIn('confirmed: NO', out)

    def test_apply_with_an_unconfirmed_audit_list_refuses_even_with_yes(self):
        t, repo = self.make()
        before = t.files()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', t.qa, '--repo', repo, '--no-git', '--apply', '--yes'])
        self.assertEqual(t.files(), before)

    def test_apply_without_a_terminal_or_yes_refuses(self):
        t, repo = self.make()
        write(os.path.join(repo, AUDIT), json.dumps({'confirmed': 'laptop', 'games': {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}}))
        before = t.files()
        with mock.patch.object(sys, 'stdin', io.StringIO('')), self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', t.qa, '--repo', repo, '--no-git', '--apply'])
        self.assertIn('no terminal', str(cm.exception))
        self.assertEqual(t.files(), before)

    def test_apply_and_move_cannot_be_combined_and_dry_run_wins_over_apply(self):
        t, repo = self.make()
        with self.assertRaises(SystemExit):
            bl.main(['--qa-root', t.qa, '--repo', repo, '--no-git', '--apply', '--move-to', os.path.join(t.root, 'x')])
        write(os.path.join(repo, AUDIT), json.dumps({'confirmed': 'laptop', 'games': {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}}))
        before = t.files()
        self.run_main(['--qa-root', t.qa, '--repo', repo, '--no-git', '--apply', '--yes', '--dry-run'])
        self.assertEqual(t.files(), before)

    def test_apply_with_yes_and_a_confirmed_list_deletes_only_the_delete_batch_frames(self):
        t, repo = self.make()
        write(os.path.join(repo, AUDIT), json.dumps({'confirmed': 'laptop', 'games': {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS'}}}))
        before = t.files()
        code, out = self.run_main(['--qa-root', t.qa, '--repo', repo, '--no-git', '--apply', '--yes'])
        after = t.files()
        gone = sorted(set(before) - set(after))
        self.assertTrue(gone and all('BATCH_A' in p and p.lower().endswith(bl.FRAME_EXT) for p in gone))
        self.assertIn('integrity check', out)
        self.assertTrue([p for p in after if os.path.basename(p).startswith('CLEANUP_LOG_')])

    def test_a_qa_root_that_is_not_there_is_refused(self):
        with self.assertRaises(SystemExit):
            bl.find_qa_root(os.path.join(tempfile.gettempdir(), 'no_such_battle_logs_folder'))


if __name__ == '__main__':
    unittest.main()
