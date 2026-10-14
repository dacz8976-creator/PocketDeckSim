#!/usr/bin/env python3
"""Tests for tools/battle_logs_cleanup.py, on made-up folder trees and throwaway git repos (nothing here touches the real Battle Logs).

  cd tools && python3 -B -m unittest -v test_battle_logs_cleanup"""
import contextlib, datetime, io, json, os, shutil, signal, subprocess, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battle_logs_cleanup as bl  # noqa: E402

AUDIT = bl.AUDIT_LIST
META = 'rl/results/pause_games_new_2026-10-12/games_meta.json'
VIDEO_BYTES = 1000
DIGEST = 'ab' * 32            # the sha256 of a game's reviewed positions, as the audit entries and the made-up index carry it
HAVE_GIT = bool(shutil.which('git'))


def write(path, data=b'x'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode())


def read(path):
    with open(path, 'rb') as f:
        return f.read()


class Tree:
    """a made-up Battle Logs folder: Battle Logs/Recording_QA/BATCH_*/<game packets> and their source videos, plus things that must never be touched"""

    def __init__(self, test):
        self.root = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.root, True)
        self.logs = os.path.join(self.root, 'Battle Logs')
        self.qa = os.path.join(self.logs, 'Recording_QA')
        os.makedirs(self.qa)

    def game(self, batch, name, text=True, frames=3, video='logs'):
        gp = os.path.join(self.qa, batch, name)
        os.makedirs(gp, exist_ok=True)
        if text:
            for t in bl.TEXT_REQUIRED:
                write(os.path.join(gp, t), '{"ok": 1}' if t.endswith('.json') else '# review')
        vname = name.split('_iOS')[0] + '_iOS.MP4'
        write(os.path.join(gp, 'SOURCE.json'), json.dumps({'video_basename': vname, 'bytes': VIDEO_BYTES}))
        if video == 'logs':
            write(os.path.join(self.logs, vname), b'v' * VIDEO_BYTES)
        elif video == 'reviewed':
            write(os.path.join(self.logs, 'Reviewed', vname), b'v' * VIDEO_BYTES)
        write(os.path.join(gp, 'notes.txt'), 'notes')
        write(os.path.join(gp, 'extract_seek.py'), 'print(1)')
        for i in range(frames):
            write(os.path.join(gp, 'turn_evidence', f't{i:04d}.jpg'), b'j' * 100)
        write(os.path.join(gp, 'comparison.JPG'), b'J' * 50)
        write(os.path.join(gp, 'independent_sol', 'deep', 'f0.png'), b'p' * 70)
        write(os.path.join(gp, 'overview', 'o.jpeg'), b'e' * 30)
        return gp

    def second_game(self, gp, how='related', frames=3):
        """a second game recorded in the same packet, in game_02/"""
        sub = os.path.join(gp, 'game_02')
        for t in bl.TEXT_REQUIRED:
            write(os.path.join(sub, t), '{"g": 2}' if t.endswith('.json') else '# review 2')
        write(os.path.join(sub, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_02'}))
        for i in range(frames):
            write(os.path.join(sub, 'crops', f'c{i}.png'), b'c' * 40)
        if how == 'related':
            write(os.path.join(gp, 'RELATED_GAME_PACKETS.json'), json.dumps({'game_count': 2, 'game_packets': [{'path': '.'}, {'path': 'game_02'}]}))
        return sub

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

    def videos(self):
        return bl.video_index(self.logs)

    def scan(self):
        return bl.scan_qa(self.qa, self.videos())

    def files(self):
        out = {}
        for root, _, fs in os.walk(self.root):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, self.root)] = os.path.getsize(p)
        return out

    def contents(self):
        out = {}
        for root, _, fs in os.walk(self.root):
            for f in fs:
                p = os.path.join(root, f)
                out[os.path.relpath(p, self.root)] = read(p)
        return out


def accept(games, by='laptop', date='2026-10-14'):
    return {'by': by, 'date': date, 'games_sha256': bl.games_hash(games)}


def index(folders, games=None, pending=None, accepted=True, found=True, meta=META, positions=5):
    """a RepoIndex: `folders` are 'BATCH/game' names that are in the repo; `games` the audited ones (default: all of them); `accepted`: True = a valid acceptance of `games`, or the value to put in 'confirmed'"""
    hits = {f: (f'kw-{f.split("/")[1][2:].replace("_iOS", "")}', meta, positions, DIGEST) for f in folders}
    if games is None:
        games = {v[0]: {'folder': f, 'games_meta': meta, 'positions': positions, 'positions_sha256': DIGEST} for f, v in hits.items()}
    audit = {'games': games, 'pending': pending or {}}
    if accepted is True:
        audit['confirmed'] = accept(games)
    else:
        audit['confirmed'] = accepted
    return bl.RepoIndex(hits, audit if found else {}, found)


def no_default(test):
    """the tool also looks for videos in C:/Users/dacz8/OneDrive/Desktop/Battle Logs: not in a test"""
    p = mock.patch.object(bl, 'BATTLE_LOGS_DEFAULT', os.path.join(tempfile.gettempdir(), 'no_such_default_battle_logs'))
    p.start()
    test.addCleanup(p.stop)


def decide_for(tree, idx):
    return bl.decide(tree.scan(), idx)


class DecisionRule(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.game('BATCH_A', '20261001_000000002_iOS')

    def one(self, idx):
        return decide_for(self.t, idx)[0]

    def both(self):
        return ['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS']

    def test_a_batch_whose_every_game_is_in_the_repo_audited_and_has_its_text_and_video_is_marked_delete(self):
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
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST}}
        d = self.one(index(self.both(), games=keys))
        self.assertFalse(d.delete)
        self.assertIn('not audited', ' '.join(d.games[1].reasons))

    def test_a_game_the_list_only_proposes_is_not_deleted_and_the_reason_is_shown(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST}}
        d = self.one(index(self.both(), games=keys, pending={'kw-261001_000000002': {'why': 'no panel compared it'}}))
        self.assertFalse(d.delete)
        self.assertIn('pending', ' '.join(d.games[1].reasons))
        self.assertIn('no panel compared it', ' '.join(d.games[1].reasons))

    def test_an_audit_entry_that_names_another_folder_does_not_count(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST},
                'kw-261001_000000002': {'folder': 'BATCH_Z/20261001_000000002_iOS', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST}}
        d = self.one(index(self.both(), games=keys))
        self.assertFalse(d.delete)
        self.assertIn('not here', ' '.join(d.games[1].reasons))

    def test_an_audit_entry_is_held_when_the_reviewed_positions_or_games_meta_are_no_longer_what_the_repo_has(self):
        # the review vouched for 5 positions in one games_meta; a later commit names the game in another file or with another number of positions
        for kw in ({'meta': 'rl/results/pause_games_new_2026-11-01/games_meta.json'}, {'positions': 6}, {'digest': 'cd' * 32}):
            idx = index(self.both())
            for f, (k, m, n, h) in list(idx.folders.items()):
                idx.folders[f] = (k, kw.get('meta', m), kw.get('positions', n), kw.get('digest', h))
            d = self.one(idx)
            self.assertFalse(d.delete, kw)
            self.assertIn('not audited as it is now', ' '.join(d.games[0].reasons))

    def test_a_game_with_no_positions_in_the_repo_is_not_deleted_even_if_the_list_names_it(self):
        keys = {'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST}}
        d = self.one(index(self.both()[1:], games=keys))
        self.assertEqual(d.verdict, 'keep')

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


class SourceVideo(unittest.TestCase):
    """the frames can be cut again from the video: a packet whose video is not in Battle Logs is held back"""

    def setUp(self):
        self.t = Tree(self)

    def verdict(self, **kw):
        self.t.game('BATCH_A', '20261001_000000001_iOS', **kw)
        d = decide_for(self.t, index(['BATCH_A/20261001_000000001_iOS']))[0]
        return d, ' '.join(d.games[0].reasons)

    def test_a_video_at_the_top_of_battle_logs_or_in_reviewed_passes(self):
        for where in ('logs', 'reviewed'):
            d, why = self.verdict(video=where)
            self.assertTrue(d.delete, (where, why))
            shutil.rmtree(self.t.root)
            self.t = Tree(self)

    def test_a_missing_video_holds_the_packet_back_and_says_which(self):
        d, why = self.verdict(video=None)
        self.assertFalse(d.delete)
        self.assertIn('source video 20261001_000000001_iOS.MP4 not found in Battle Logs', why)

    def test_a_video_with_another_size_than_the_packet_recorded_holds_it_back(self):
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        write(os.path.join(self.t.logs, '20261001_000000001_iOS.MP4'), b'v' * 7)
        d = decide_for(self.t, index(['BATCH_A/20261001_000000001_iOS']))[0]
        self.assertFalse(d.delete)
        self.assertIn('has 7 bytes', ' '.join(d.games[0].reasons))

    def test_a_packet_that_records_no_video_is_held_back(self):
        gp = self.t.game('BATCH_A', '20261001_000000001_iOS')
        write(os.path.join(gp, 'SOURCE.json'), '{}')
        d = decide_for(self.t, index(['BATCH_A/20261001_000000001_iOS']))[0]
        self.assertFalse(d.delete)
        self.assertIn('not recorded', ' '.join(d.games[0].reasons))


class SecondGameInsideAPacket(unittest.TestCase):
    """the laptop's blocker, twice: packet 012927 records two games, game 2 in game_02/ AND, as its own evidence files cite, in the packet root's shared native/ folder (Codex's
    RELATED_GAME_PACKETS.json: root_is_only_shared_writer_and_media_mover). A packet that records more than one game is held back WHOLE unless every game in it passes on its own."""
    FOLDER = 'BATCH_A/20261001_000000001_iOS'

    def setUp(self):
        self.t = Tree(self)
        self.gp = self.t.game('BATCH_A', '20261001_000000001_iOS')
        for name in ('t0622.00.jpg', 't0650.00.jpg'):
            write(os.path.join(self.gp, 'native', name), b'n' * 60)            # shared media of both games, in the root
        self.idx = index([self.FOLDER])

    def one(self):
        return decide_for(self.t, self.idx)[0]

    def why(self):
        return ' '.join(self.one().games[0].reasons)

    def related(self, **kw):
        write(os.path.join(self.gp, 'RELATED_GAME_PACKETS.json'), json.dumps(kw))

    def test_a_packet_that_lists_a_second_game_is_held_back_whole_including_its_shared_native_frames(self):
        self.t.second_game(self.gp, how='related', frames=3)
        d = self.one()
        self.assertFalse(d.delete)
        self.assertEqual((d.verdict, d.frames, d.bytes), ('keep', 0, 0))
        self.assertEqual(d.kept_frames, 8 + 3, 'the first game\'s 6 frames, the 2 native frames, the 3 of game_02: nothing goes')
        self.assertIn('holds 2 games', self.why())
        self.assertIn('game_02 (3 frames) is not audited', self.why())
        self.assertIn('so none of its frames go', self.why())
        self.assertEqual(list(d.games[0].game.nested), ['game_02'])

    def test_apply_deletes_nothing_from_such_a_packet_not_even_the_native_folder(self):
        self.t.second_game(self.gp, how='related', frames=3)
        before = self.t.contents()
        res = bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=lambda *a: True, out=io.StringIO())
        self.assertEqual(tuple(res)[:3], (0, 0, 0))
        self.assertEqual(self.t.contents(), before)

    def test_the_other_layout_of_the_related_file_is_read_too(self):
        # 20261010_021629000 writes games[{game_number, packet}] and game_count
        self.related(source_video='x.MP4', game_count=2, games=[{'game_number': 1, 'packet': '.'}, {'game_number': 2, 'packet': 'second_recording'}], other_games_found=True)
        write(os.path.join(self.gp, 'second_recording', 'crops', 'c.png'), b'c')
        d = self.one()
        self.assertFalse(d.delete)
        self.assertEqual(list(d.games[0].game.nested), ['second_recording'])
        self.assertIn('second_recording (1 frames) is not audited', self.why())

    def test_a_declared_second_game_with_no_folder_to_be_found_holds_the_packet(self):
        for label, kw in (('RELATED game_count', {'game_count': 2}), ('RELATED games entries', {'games': [{'packet': '.'}, {'packet': 'elsewhere'}]}), ('other_games_found', {'other_games_found': True})):
            self.related(**kw)
            self.assertIn('records 2 games but only 0 second-game folders could be found', self.why(), label)

    def test_the_root_summary_that_says_two_games_holds_the_packet(self):
        write(os.path.join(self.gp, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_01', 'source_game_count': 2}))
        self.assertIn('records 2 games', self.why())

    def test_a_packet_that_says_it_holds_one_game_passes_and_all_its_frames_go(self):
        self.related(game_count=1, games=[{'game_number': 1, 'packet': '.'}], other_games_found=False)
        write(os.path.join(self.gp, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_01', 'source_game_count': 1}))
        d = self.one()
        self.assertTrue(d.delete, self.why())
        self.assertEqual(d.frames, 8)

    def test_a_game_folder_with_no_declaration_at_all_is_found_by_its_name_and_holds_the_packet(self):
        self.t.second_game(self.gp, how='name')
        self.assertIn('holds 2 games', self.why())

    def test_a_game_folder_is_found_by_its_own_ledger_with_another_game_id(self):
        write(os.path.join(self.gp, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_01'}))
        sub = os.path.join(self.gp, 'second_recording')
        write(os.path.join(sub, 'TURN_LEDGER.json'), '{}')
        write(os.path.join(sub, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_02'}))
        write(os.path.join(sub, 'crops', 'c.png'), b'c')
        self.assertEqual(list(self.one().games[0].game.nested), ['second_recording'])
        self.assertIn('holds 2 games', self.why())

    def test_a_backup_copy_of_the_same_game_is_not_a_second_game_and_goes_with_the_packet(self):
        write(os.path.join(self.gp, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_01'}))
        bk = os.path.join(self.gp, 'original_before_final_independent')
        write(os.path.join(bk, 'TURN_LEDGER.json'), '{}')
        write(os.path.join(bk, 'SUMMARY.json'), json.dumps({'game_id': 'x_game_01'}))
        write(os.path.join(bk, 'crop.png'), b'c')
        d = self.one()
        self.assertTrue(d.delete, self.why())
        self.assertIn(os.path.join(bk, 'crop.png'), [p for p, _ in d.games[0].game.frames])

    def test_a_game_folder_inside_a_backup_folder_keeps_its_frames_and_does_not_hold_a_one_game_packet(self):
        # 012927 has original_before_final_independent/game_02 (0 frames there); in a packet that says it holds one game it must neither block it nor be deleted
        write(os.path.join(self.gp, 'original_before_final_independent', 'game_02', 'old.png'), b'o' * 9)
        d = self.one()
        self.assertTrue(d.delete, self.why())
        self.assertEqual(d.frames, 8)
        self.assertEqual(d.kept_frames, 1)
        self.assertEqual(list(d.games[0].game.nested), ['original_before_final_independent/game_02'])
        bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=lambda *a: True, out=io.StringIO())
        self.assertTrue(os.path.exists(os.path.join(self.gp, 'original_before_final_independent', 'game_02', 'old.png')))
        self.assertFalse(os.path.exists(os.path.join(self.gp, 'native', 't0622.00.jpg')))

    def audit_second_game(self, accepted=True, pending=False):
        key, folder = 'kw-261001_000000001_game_02', self.FOLDER + '/game_02'
        self.idx.folders[folder] = (key, META, 4, DIGEST)
        if not pending:
            self.idx.audit['games'][key] = {'folder': folder, 'games_meta': META, 'positions': 4, 'positions_sha256': DIGEST}
        else:
            self.idx.audit['pending'][key] = {'why': 'no panel yet'}
        self.idx.audit['confirmed'] = accept(self.idx.audit['games']) if accepted else None

    def test_the_packet_goes_when_the_second_game_is_in_the_repo_and_audited_under_its_own_folder(self):
        sub = self.t.second_game(self.gp, how='related', frames=3)
        self.audit_second_game()
        d = self.one()
        self.assertTrue(d.delete, self.why())
        self.assertEqual((d.frames, d.kept_frames), (8 + 3, 0))
        bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=lambda *a: True, out=io.StringIO())
        self.assertEqual(os.listdir(os.path.join(sub, 'crops')), [])
        self.assertEqual(os.listdir(os.path.join(self.gp, 'native')), [])

    def test_a_second_game_the_list_only_proposes_still_holds_the_packet(self):
        self.t.second_game(self.gp, how='related', frames=3)
        self.audit_second_game(pending=True)
        d = self.one()
        self.assertFalse(d.delete)
        self.assertIn('game_02 (3 frames) is not audited: not audited: proposed, pending a decision (no panel yet)', self.why())

    def test_the_plan_refuses_a_frame_of_a_second_game_that_did_not_pass(self):
        write(os.path.join(self.gp, 'original_before_final_independent', 'game_02', 'old.png'), b'o' * 9)
        decisions = decide_for(self.t, self.idx)
        decisions[0].games[0].game.frames.append((os.path.join(self.gp, 'original_before_final_independent', 'game_02', 'old.png'), 9))
        with self.assertRaises(SystemExit) as cm:
            bl.deletion_plan(decisions, self.t.qa)
        self.assertIn('not a frame file inside a game packet that passes', str(cm.exception))

    def test_the_dry_run_says_why_the_packet_is_held_and_which_folder_stays_in_a_packet_that_goes(self):
        self.t.second_game(self.gp, how='related', frames=3)
        out = io.StringIO()
        bl.report(decide_for(self.t, self.idx), bl.RepoView('.', no_git=True), self.t.qa, self.idx, out=out)
        self.assertIn('stays 20261001_000000001_iOS: holds 2 games; game_02 (3 frames) is not audited', out.getvalue())
        shutil.rmtree(os.path.join(self.gp, 'game_02'))
        os.remove(os.path.join(self.gp, 'RELATED_GAME_PACKETS.json'))
        write(os.path.join(self.gp, 'before_x', 'game_02', 'old.png'), b'o' * 9)
        out = io.StringIO()
        bl.report(decide_for(self.t, self.idx), bl.RepoView('.', no_git=True), self.t.qa, self.idx, out=out)
        self.assertIn('stays 20261001_000000001_iOS/before_x/game_02: a folder that keeps an earlier state of a game: 1 frames', out.getvalue())


class Acceptance(unittest.TestCase):
    GAMES = {'kw-1': {'folder': 'BATCH_A/g1', 'games_meta': META, 'positions': 5, 'positions_sha256': DIGEST}}

    def idx(self, confirmed, games=None):
        return bl.RepoIndex({}, {'confirmed': confirmed, 'games': games or self.GAMES}, True)

    def test_a_valid_acceptance_names_who_when_and_the_games_it_covers(self):
        acc, why = bl.acceptance(self.idx(accept(self.GAMES, by='Dustin via the laptop')))
        self.assertIsNone(why)
        self.assertEqual(acc['by'], 'Dustin via the laptop')

    def test_strings_that_say_no_or_not_yet_are_not_an_acceptance(self):
        for value in ('no', 'NO', 'pending', 'false', 'not yet - waiting for Dustin', 'unconfirmed', 'laptop, 2026-10-14', 'yes'):
            acc, why = bl.acceptance(self.idx(value))
            self.assertIsNone(acc, value)
            self.assertIn('must be {', why)

    def test_empty_and_json_booleans_are_not_an_acceptance(self):
        for value in (None, '', '  ', False, True, 0, [], {}):
            self.assertIsNone(bl.acceptance(self.idx(value))[0], repr(value))

    def test_a_structured_acceptance_with_a_negation_for_a_name_or_a_bad_date_is_refused(self):
        h = bl.games_hash(self.GAMES)
        for c in ({'by': 'no', 'date': '2026-10-14', 'games_sha256': h}, {'by': 'pending', 'date': '2026-10-14', 'games_sha256': h}, {'by': 'x', 'date': '2026-10-14', 'games_sha256': h},
                  {'by': 'laptop', 'date': 'soon', 'games_sha256': h}, {'by': 'laptop', 'date': '2026-13-45', 'games_sha256': h}, {'by': 'laptop', 'date': '2026-10-14'},
                  {'date': '2026-10-14', 'games_sha256': h}):
            self.assertIsNone(bl.acceptance(self.idx(c))[0], c)

    def test_placeholders_and_not_yet_wording_anywhere_in_the_name_are_refused_but_real_names_pass(self):
        # the laptop's second review: only the start of "by" was checked, so "awaiting Dustin" and the template's "<who>" passed
        h = bl.games_hash(self.GAMES)
        for by in ('<who>', '<a name>', 'awaiting Dustin', 'laptop (unconfirmed)', 'Dustin - NOT accepted yet', 'waiting for the laptop', 'TBD', 'n/a', 'name', 'who'):
            self.assertIsNone(bl.acceptance(self.idx({'by': by, 'date': '2026-10-14', 'games_sha256': h}))[0], by)
        for by in ('Dustin', 'laptop', 'Dustin via the laptop', 'Noah', 'Una', 'Dustin (laptop session)', 'Nora Holden'):
            self.assertIsNotNone(bl.acceptance(self.idx({'by': by, 'date': '2026-10-14', 'games_sha256': h}))[0], by)

    def test_a_date_before_the_list_existed_or_in_the_future_is_not_the_day_it_was_accepted(self):
        h = bl.games_hash(self.GAMES)
        for date in ('1970-01-01', '2026-10-13', '2099-12-31'):
            acc, why = bl.acceptance(self.idx({'by': 'Dustin', 'date': date, 'games_sha256': h}))
            self.assertIsNone(acc, date)
            self.assertIn('cannot be the day', why)
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        self.assertIsNotNone(bl.acceptance(self.idx({'by': 'Dustin', 'date': today, 'games_sha256': h}))[0])

    def test_the_acceptance_covers_the_digest_of_the_reviewed_positions_too(self):
        c = accept(self.GAMES)
        regenerated = {'kw-1': dict(self.GAMES['kw-1'], positions_sha256='cd' * 32)}
        acc, why = bl.acceptance(self.idx(c, games=regenerated))
        self.assertIsNone(acc)
        self.assertIn('needs a new acceptance', why)

    def test_an_acceptance_stops_covering_the_games_the_moment_the_list_changes(self):
        c = accept(self.GAMES)
        more = dict(self.GAMES, **{'kw-2': {'folder': 'BATCH_A/g2', 'games_meta': META, 'positions': 3, 'positions_sha256': DIGEST}})
        acc, why = bl.acceptance(self.idx(c, games=more))
        self.assertIsNone(acc)
        self.assertIn('needs a new acceptance', why)
        changed = {'kw-1': dict(self.GAMES['kw-1'], positions=6)}
        self.assertIsNone(bl.acceptance(self.idx(c, games=changed))[0])

    def test_editing_only_the_evidence_text_does_not_void_it(self):
        c = accept(self.GAMES)
        games = {'kw-1': dict(self.GAMES['kw-1'], evidence=['new note'], tier='A')}
        self.assertIsNotNone(bl.acceptance(self.idx(c, games=games))[0])

    def test_pending_entries_are_not_covered_so_moving_one_into_games_needs_a_new_acceptance(self):
        c = accept(self.GAMES)
        moved = dict(self.GAMES, **{'kw-9': {'folder': 'BATCH_B/g9', 'games_meta': META, 'positions': 2, 'positions_sha256': DIGEST}})
        self.assertIsNone(bl.acceptance(self.idx(c, games=moved))[0])

    def test_apply_refuses_without_a_valid_acceptance_and_deletes_nothing(self):
        t = Tree(self)
        t.game('BATCH_A', '20261001_000000001_iOS')
        before = t.contents()
        for bad in (None, 'no', 'pending', {'by': 'laptop', 'date': '2026-10-14', 'games_sha256': 'stale'}):
            idx = index(['BATCH_A/20261001_000000001_iOS'], accepted=bad)
            with self.assertRaises(SystemExit):
                bl.apply_deletions(decide_for(t, idx), t.qa, idx, confirm=lambda *a: True, out=io.StringIO())
        self.assertEqual(t.contents(), before)

    def test_the_report_says_who_accepted_or_why_it_is_not_accepted(self):
        t = Tree(self)
        t.game('BATCH_A', '20261001_000000001_iOS')
        for accepted, expect in ((True, 'acceptance: laptop, 2026-10-14'), ('no', 'acceptance: NO'), (None, 'acceptance: NO')):
            idx = index(['BATCH_A/20261001_000000001_iOS'], accepted=accepted)
            out = io.StringIO()
            bl.report(decide_for(t, idx), bl.RepoView('.', no_git=True), t.qa, idx, out=out)
            self.assertIn(expect, out.getvalue())


class IndexFromTheRepo(unittest.TestCase):
    def repo(self):
        self.repo_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.repo_dir, True)
        base = os.path.join(self.repo_dir, 'rl', 'results', 'pause_games_new_2026-10-12')
        write(os.path.join(base, 'games_meta.json'), json.dumps({
            'kw-261001_000000001': {'folder': 'BATCH_A/20261001_000000001_iOS', 'has_ledger': True},
            'kw-261001_000000002': {'folder': 'BATCH_A/20261001_000000002_iOS', 'has_ledger': True}}))
        write(os.path.join(base, 'positions_all.json'), json.dumps([{'game': 'kw-261001_000000001', 'id': 'p1'}]))      # no position for the second game
        write(os.path.join(self.repo_dir, AUDIT), json.dumps({'confirmed': None, 'games': {}}))

    def test_a_game_counts_only_when_its_positions_are_in_the_positions_file_next_to_the_meta(self):
        self.repo()
        idx = bl.build_index(bl.RepoView(self.repo_dir, no_git=True))
        self.assertEqual(sorted(idx.folders), ['BATCH_A/20261001_000000001_iOS'])
        self.assertEqual(idx.folders['BATCH_A/20261001_000000001_iOS'][:3], ('kw-261001_000000001', META, 1))
        self.assertEqual(idx.folders['BATCH_A/20261001_000000001_iOS'][3], bl.positions_digest([{'game': 'kw-261001_000000001', 'id': 'p1'}]))
        self.assertTrue(idx.audit_path_found)

    def test_only_pause_games_result_folders_are_read(self):
        self.repo()
        other = os.path.join(self.repo_dir, 'rl', 'results', 'something_else')
        write(os.path.join(other, 'games_meta.json'), json.dumps({'kw-x': {'folder': 'BATCH_B/g'}}))
        write(os.path.join(other, 'positions_all.json'), json.dumps([{'game': 'kw-x'}]))
        self.assertNotIn('BATCH_B/g', bl.build_index(bl.RepoView(self.repo_dir, no_git=True)).folders)

    @unittest.skipUnless(HAVE_GIT, 'git not installed')
    def test_with_git_a_file_that_is_only_in_the_working_tree_is_not_in_the_repo_and_the_commit_is_read_once(self):
        self.repo()
        g = lambda *a: subprocess.run(['git', '-C', self.repo_dir, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True).stdout
        g('init', '-q', '-b', 'main')
        g('add', 'rl/results/pause_games_new_2026-10-12')
        g('commit', '-q', '-m', 'games, but not the audit list')
        view = bl.RepoView(self.repo_dir, ref='main')
        first = view.commit_full
        idx = bl.build_index(view)
        self.assertFalse(idx.audit_path_found)
        self.assertIn('BATCH_A/20261001_000000001_iOS', idx.folders)
        self.assertIn(first[:8], view.describe())
        self.assertRegex(view.describe(), r'committed \d{4}-\d{2}-\d{2}T')
        g('add', AUDIT)
        g('commit', '-q', '-m', 'audit list')
        # the same view keeps reading the commit it resolved at the start, whatever main does afterwards
        self.assertFalse(bl.build_index(view).audit_path_found)
        self.assertTrue(bl.build_index(bl.RepoView(self.repo_dir, ref='main')).audit_path_found)

    @unittest.skipUnless(HAVE_GIT, 'git not installed')
    def test_a_ref_git_cannot_read_is_refused(self):
        self.repo()
        subprocess.run(['git', '-C', self.repo_dir, 'init', '-q'], check=True)
        with self.assertRaises(SystemExit) as cm:
            bl.RepoView(self.repo_dir, ref='origin/main')
        self.assertIn('refused', str(cm.exception))
        self.assertNotIn('--no-git', str(cm.exception))


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
        return sorted(p for p in set(self.before) - set(after))

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
        _, out = self.apply()
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

    def test_nothing_to_delete_is_said_and_not_confirmed(self):
        idx = index([])
        out = io.StringIO()
        res = bl.apply_deletions(decide_for(self.t, idx), self.t.qa, idx, confirm=lambda *a: self.fail('asked'), out=out)
        self.assertEqual(res[0], 0)
        self.assertIn('nothing to delete', out.getvalue())


class TheLog(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.game('BATCH_A', '20261001_000000002_iOS')
        self.idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'])

    def run_apply(self, **kw):
        out = io.StringIO()
        res = bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=lambda *a: True, out=out, **kw)
        return res, out.getvalue()

    def lines(self, log):
        with open(log, encoding='utf-8') as f:
            return [json.loads(l) for l in f]

    def test_the_log_lists_every_removed_file_and_ends_with_a_clean_integrity_line(self):
        (deleted, _, _, log), out = self.run_apply()
        lines = self.lines(log)
        self.assertEqual(sum(1 for l in lines if 'removed' in l), deleted)
        self.assertTrue(lines[-1]['done'])
        self.assertEqual((lines[-1]['non_frame_files_missing_after'], lines[-1]['non_frame_files_changed']), ([], []))
        self.assertIn('same SHA-256', out)
        self.assertTrue(os.path.basename(log).startswith('CLEANUP_LOG_'))

    def test_the_log_header_says_which_commit_authorised_it_and_names_each_packet_with_its_key_and_games_meta(self):
        view = mock.Mock(commit_full='abc123def456', describe=lambda: 'origin/main (abc123de, committed 2026-10-14T10:00:00-05:00)')
        (_, _, _, log), _ = self.run_apply(view=view)
        head = self.lines(log)[0]
        self.assertEqual(head['commit'], 'abc123def456')
        self.assertIn('committed 2026-10-14', head['committed_state'])
        self.assertEqual(head['acceptance']['by'], 'laptop')
        self.assertEqual({p['folder'] for p in head['packets']}, {'BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'})
        self.assertTrue(all(p['key'].startswith('kw-') and p['games_meta'] == META and p['positions'] == 5 for p in head['packets']))

    def test_the_log_is_written_line_by_line_while_the_deletion_runs(self):
        real, seen = os.remove, []

        def spy(p, **kw):
            if len(seen) == 3:      # at the fourth removal: what is in the file already?
                with open(glob_log(self.t.qa), encoding='utf-8') as f:
                    seen.append(f.read().count('"removed"'))
            else:
                seen.append(None)
            real(p, **kw)

        def glob_log(d):
            return os.path.join(d, [f for f in os.listdir(d) if f.startswith('CLEANUP_LOG_')][0])
        with mock.patch.object(bl.os, 'remove', spy):
            self.run_apply()
        self.assertEqual([s for s in seen if s is not None], [3], 'the three earlier removals were already in the log file')

    def test_progress_is_printed_every_n_files(self):
        (_, _, _, _), out = self.run_apply(progress_every=4)
        self.assertIn('removed 4 of 12', out)
        self.assertIn('removed 8 of 12', out)

    def test_a_sigterm_during_the_deletion_closes_the_log_with_an_interrupted_line_and_exits_130(self):
        real, state = os.remove, {'n': 0}

        def killer(p, **kw):
            state['n'] += 1
            if state['n'] == 3:
                os.kill(os.getpid(), signal.SIGTERM)
            real(p, **kw)
        before = signal.getsignal(signal.SIGTERM)
        with mock.patch.object(bl.os, 'remove', killer):
            with self.assertRaises(SystemExit) as cm:
                self.run_apply()
        self.assertEqual(cm.exception.code, 130)
        self.assertIs(signal.getsignal(signal.SIGTERM), before, 'the old handler is back')
        log = os.path.join(self.t.qa, [f for f in os.listdir(self.t.qa) if f.startswith('CLEANUP_LOG_')][0])
        lines = self.lines(log)
        # the signal arrives while the third file is being removed: that file is finished, counted and logged, then the run stops between files
        self.assertEqual(sum(1 for l in lines if 'removed' in l), 3)
        self.assertEqual(lines[-1]['interrupted'], 'SIGTERM')
        self.assertEqual(lines[-1]['deleted'], 3)
        self.assertNotIn('done', lines[-1])
        self.assertEqual(self.gone_frames(), 3)

    def gone_frames(self):
        return 12 - sum(1 for r, _, fs in os.walk(self.t.qa) for f in fs if f.lower().endswith(bl.FRAME_EXT))

    def test_the_last_file_removed_before_a_signal_is_always_in_the_log_and_the_count(self):
        # the laptop's residual: in about 1 of 2 interruptions the handler raised right after os.remove returned, before the count and the log line
        for sig in (signal.SIGTERM, signal.SIGHUP):
            for n in (1, 2, 5, 11):
                t = Tree(self)
                t.game('BATCH_A', '20261001_000000001_iOS')
                t.game('BATCH_A', '20261001_000000002_iOS')
                idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'])
                real, state = os.remove, {'n': 0}

                def killer(p, **kw):
                    real(p, **kw)
                    state['n'] += 1
                    if state['n'] == n:
                        os.kill(os.getpid(), sig)          # right after the file is gone
                with mock.patch.object(bl.os, 'remove', killer):
                    with self.assertRaises(SystemExit) as cm:
                        bl.apply_deletions(decide_for(t, idx), t.qa, idx, confirm=lambda *a: True, out=io.StringIO())
                self.assertEqual(cm.exception.code, 130)
                log = os.path.join(t.qa, [f for f in os.listdir(t.qa) if f.startswith('CLEANUP_LOG_')][0])
                lines = self.lines(log)
                gone = 12 - sum(1 for r, _, fs in os.walk(t.qa) for f in fs if f.lower().endswith(bl.FRAME_EXT))
                self.assertEqual((gone, sum(1 for l in lines if 'removed' in l), lines[-1]['deleted']), (n, n, n), (sig.name, n))

    def test_ctrl_c_is_logged_the_same_way(self):
        real, state = os.remove, {'n': 0}

        def ctrl_c(p, **kw):
            state['n'] += 1
            if state['n'] == 2:
                raise KeyboardInterrupt
            real(p, **kw)
        with mock.patch.object(bl.os, 'remove', ctrl_c):
            with self.assertRaises(SystemExit) as cm:
                self.run_apply()
        self.assertEqual(cm.exception.code, 130)
        log = os.path.join(self.t.qa, [f for f in os.listdir(self.t.qa) if f.startswith('CLEANUP_LOG_')][0])
        self.assertIn('interrupted', self.lines(log)[-1])

    def test_a_frame_that_cannot_be_deleted_is_counted_logged_and_makes_the_run_incomplete(self):
        real = os.remove

        def locked(p, **kw):
            if p.endswith('t0001.jpg'):
                raise PermissionError(13, 'locked by another process')
            real(p, **kw)
        with mock.patch.object(bl.os, 'remove', locked):
            (deleted, failed, _, log), out = self.run_apply()
        self.assertEqual(failed, 2)
        self.assertIn('INCOMPLETE: 2 frames could not be deleted', out)
        self.assertEqual(sum(1 for l in self.lines(log) if 'failed' in l and 'error' in l), 2)


class RacesBetweenThePlanAndTheDeletion(unittest.TestCase):
    def setUp(self):
        self.t = Tree(self)
        self.g1 = self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.g2 = self.t.game('BATCH_A', '20261001_000000002_iOS')
        self.idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_A/20261001_000000002_iOS'])

    def apply(self, confirm):
        out = io.StringIO()
        res = bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=confirm, out=out)
        return res, out.getvalue()

    def test_a_packet_whose_ledger_disappears_while_the_question_is_open_is_skipped_and_logged(self):
        def meanwhile(*a):
            os.remove(os.path.join(self.g1, 'TURN_LEDGER.json'))
            return True
        out = io.StringIO()
        with self.assertRaises(SystemExit) as cm:      # the vanished ledger is also seen by the integrity check, which says so loudly
            bl.apply_deletions(decide_for(self.t, self.idx), self.t.qa, self.idx, confirm=meanwhile, out=out)
        self.assertIn('SKIPPED BATCH_A/20261001_000000001_iOS', out.getvalue())
        self.assertIn('INTEGRITY CHECK FAILED', str(cm.exception))
        self.assertTrue(os.path.exists(os.path.join(self.g1, 'turn_evidence', 't0000.jpg')), 'its frames were kept')
        self.assertFalse(os.path.exists(os.path.join(self.g2, 'turn_evidence', 't0000.jpg')))
        log = os.path.join(self.t.qa, [f for f in os.listdir(self.t.qa) if f.startswith('CLEANUP_LOG_')][0])
        with open(log, encoding='utf-8') as f:
            self.assertIn('skipped_packet', f.read())

    def test_a_text_output_rewritten_with_the_same_size_during_the_run_is_caught_by_its_hash(self):
        def meanwhile(*a):
            return True
        real = os.remove
        state = {'n': 0}

        def rewrite(p, **kw):
            state['n'] += 1
            if state['n'] == 2:
                write(os.path.join(self.g2, 'notes.txt'), 'NOTES')          # same length as 'notes'
            real(p, **kw)
        with mock.patch.object(bl.os, 'remove', rewrite):
            with self.assertRaises(SystemExit) as cm:
                self.apply(meanwhile)
        self.assertIn('INTEGRITY CHECK FAILED', str(cm.exception))

    def test_the_inventory_is_taken_before_the_question_so_a_file_removed_while_it_is_open_is_noticed(self):
        def meanwhile(*a):
            os.remove(os.path.join(self.g2, 'notes.txt'))
            return True
        with self.assertRaises(SystemExit) as cm:
            self.apply(meanwhile)
        self.assertIn('INTEGRITY CHECK FAILED', str(cm.exception))

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_a_folder_swapped_for_a_link_while_the_question_is_open_does_not_send_the_deletion_outside(self):
        outside = os.path.join(self.t.root, 'elsewhere')
        for name in ('t0000.jpg', 't0001.jpg', 't0002.jpg'):
            write(os.path.join(outside, name), b'precious')

        def swap(*a):
            shutil.rmtree(os.path.join(self.g1, 'turn_evidence'))
            os.symlink(outside, os.path.join(self.g1, 'turn_evidence'))
            return True
        (deleted, failed, _, log), out = self.apply(swap)
        self.assertEqual(sorted(os.listdir(outside)), ['t0000.jpg', 't0001.jpg', 't0002.jpg'], 'nothing outside the packet was deleted')
        self.assertGreaterEqual(failed, 3)
        self.assertIn('INCOMPLETE', out)

    def outside_with_the_same_names(self):
        outside = os.path.join(self.t.root, 'elsewhere')
        for name in ('t0000.jpg', 't0001.jpg', 't0002.jpg'):
            write(os.path.join(outside, name), b'precious')
        return outside

    def swap_after_the_first_frame_of_turn_evidence(self, outside):
        """os.remove wrapper: once one frame of g1's turn_evidence is gone, the folder is replaced by a link to `outside`"""
        real, state = os.remove, {'done': False}

        def remove(p, **kw):
            real(p, **kw)
            if not state['done'] and os.path.basename(p).startswith('t000'):
                state['done'] = True
                shutil.rmtree(os.path.join(self.g1, 'turn_evidence'))
                os.symlink(outside, os.path.join(self.g1, 'turn_evidence'))
        return remove

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_a_folder_swapped_for_a_link_in_the_middle_of_the_run_does_not_send_the_next_deletions_outside(self):
        # the laptop's scope-n4 (b): realpath was cached per folder, so after one frame was gone the swapped folder was trusted
        for dir_fd_ok in (True, False):
            with self.subTest(dir_fd=dir_fd_ok):
                self.tearDownTree()
                outside = self.outside_with_the_same_names()
                with mock.patch.object(bl, 'DIR_FD_OK', dir_fd_ok), mock.patch.object(bl.os, 'remove', self.swap_after_the_first_frame_of_turn_evidence(outside)):
                    (deleted, failed, _, log), out = self.apply(lambda *a: True)
                self.assertEqual(sorted(os.listdir(outside)), ['t0000.jpg', 't0001.jpg', 't0002.jpg'], 'nothing outside the packet was deleted')
                self.assertGreaterEqual(failed, 1)

    def tearDownTree(self):
        shutil.rmtree(self.t.root, True)
        self.setUp()

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_a_packet_replaced_by_a_link_to_a_look_alike_packet_is_skipped_and_the_look_alikes_frames_stay(self):
        # scope-n4 (c): the packet was re-resolved through the link and the look-alike's frames were deleted (its text files were byte-identical, so the integrity check passed)
        for dir_fd_ok in (True, False):
            with self.subTest(dir_fd=dir_fd_ok):
                self.tearDownTree()
                look = os.path.join(self.t.root, 'lookalike')
                shutil.copytree(self.g2, look)

                def swap(*a):
                    shutil.move(self.g2, self.g2 + '_real')
                    os.symlink(look, self.g2)
                    return True
                with mock.patch.object(bl, 'DIR_FD_OK', dir_fd_ok):
                    res, out = self.apply(swap)
                self.assertEqual(res.skipped, 1)
                self.assertIn('SKIPPED BATCH_A/20261001_000000002_iOS', out)
                self.assertIn('INCOMPLETE', out)
                self.assertEqual(sorted(os.listdir(os.path.join(look, 'turn_evidence'))), ['t0000.jpg', 't0001.jpg', 't0002.jpg'], 'the look-alike keeps its frames')
                self.assertEqual(sorted(os.listdir(os.path.join(self.g2 + '_real', 'turn_evidence'))), ['t0000.jpg', 't0001.jpg', 't0002.jpg'], 'the real packet was left alone too')
                self.assertFalse(os.path.exists(os.path.join(self.g1, 'turn_evidence', 't0000.jpg')), 'the other packet was cleaned')

    def test_this_system_has_the_directory_handle_calls_the_tool_relies_on(self):
        # (it was found from a run where os.remove was wrongly believed unsupported and every test ran the slower fallback)
        if os.name != 'nt':
            self.assertTrue(bl.DIR_FD_OK)

    def test_the_fallback_without_directory_handles_deletes_the_same_frames(self):
        # native Windows Python has no dir_fd: every file re-resolves its folder, uncached
        before = self.t.files()
        with mock.patch.object(bl, 'DIR_FD_OK', False):
            (deleted, failed, _, _), out = self.apply(lambda *a: True)
        gone = set(before) - set(self.t.files())
        self.assertEqual((deleted, failed), (12, 0))
        self.assertTrue(all(p.lower().endswith(bl.FRAME_EXT) for p in gone if 'CLEANUP_LOG' not in p))

    def test_directory_handles_are_closed_after_each_packet(self):
        def open_fds():
            return len(os.listdir('/proc/self/fd')) if os.path.isdir('/proc/self/fd') else None
        n = open_fds()
        self.apply(lambda *a: True)
        if n is not None:
            self.assertEqual(open_fds(), n)


class MovingRecordingQA(unittest.TestCase):
    """--move-to moves ONLY Recording_QA: the videos and the rest of Battle Logs stay where they are (in OneDrive)"""

    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.outside()
        no_default(self)
        self.base = os.path.join(self.t.root, 'BattleLogs')              # does not exist yet: its parent, the temp root, does
        self.target = os.path.join(self.base, 'Recording_QA')

    def move(self, **kw):
        out = io.StringIO()
        return bl.move_recording_qa(kw.pop('source', self.t.qa), kw.pop('target', self.target), out=out, **kw), out.getvalue()

    def test_only_recording_qa_is_renamed_and_the_new_path_is_printed(self):
        before = self.t.files()
        new, out = self.move(confirm=lambda t: True)
        self.assertEqual(new, self.target)
        self.assertIn('Codex should now use as its Recording_QA', out)
        self.assertFalse(os.path.exists(self.t.qa))
        moved = {os.path.relpath(os.path.join(r, f), self.target): os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(self.target) for f in fs}
        self.assertIn(bl.LOCATION_FILE, moved)
        moved.pop(bl.LOCATION_FILE)                       # the one file the move adds: where the videos stayed
        want = {os.path.relpath(p, os.path.join('Battle Logs', 'Recording_QA')): s for p, s in before.items() if p.startswith(os.path.join('Battle Logs', 'Recording_QA') + os.sep)}
        self.assertEqual(moved, want)

    def test_the_videos_and_every_other_file_of_battle_logs_stay_where_they_are(self):
        before = self.t.files()
        self.move(confirm=lambda t: True)
        after = {os.path.relpath(os.path.join(r, f), self.t.root): os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(self.t.logs) for f in fs}
        stay = {p: s for p, s in before.items() if not p.startswith(os.path.join('Battle Logs', 'Recording_QA') + os.sep)}
        self.assertEqual(after, stay)
        self.assertTrue(any(p.endswith('.MP4') for p in after))

    def test_the_output_says_what_stays_and_what_leaves_onedrive(self):
        _, out = self.move(dry=True)
        self.assertIn('STAYS where it is, in OneDrive', out)
        self.assertIn('The videos are not moved', out)
        self.assertIn('video file', out)
        self.assertIn('Reviewed', out)
        self.assertIn('text outputs', out)

    def test_the_confirmation_is_asked_with_the_target(self):
        seen = []
        self.move(confirm=lambda target: seen.append(target) or True)
        self.assertEqual(seen, [bl.to_windows(self.target)])

    def test_a_folder_that_is_not_recording_qa_is_never_moved(self):
        with self.assertRaises(SystemExit) as cm:
            self.move(source=self.t.logs, confirm=lambda t: True)
        self.assertIn('not a folder named Recording_QA', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.logs) and not os.path.exists(self.base))

    def test_a_target_that_exists_is_refused_even_when_empty(self):
        os.makedirs(self.target)
        with self.assertRaises(SystemExit) as cm:
            self.move(confirm=lambda t: True)
        self.assertIn('already exists', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.qa))

    def test_a_target_inside_recording_qa_is_refused_whatever_the_case(self):
        for target in (os.path.join(self.t.qa, 'inner', 'Recording_QA'), os.path.join(self.t.qa.upper(), 'inner', 'Recording_QA'), os.path.join(self.t.qa.replace('Recording_QA', 'recording_qa'), 'inner', 'Recording_QA')):
            with self.assertRaises(SystemExit) as cm:
                self.move(target=target, confirm=lambda t: True)
            self.assertIn('inside', str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(self.t.qa, 'inner')))

    def test_a_relative_target_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self.move(target='BattleLogs/Recording_QA', confirm=lambda t: True)
        self.assertIn('not an absolute path', str(cm.exception))

    def test_a_target_directly_in_a_drive_root_is_refused(self):
        for target in ('/mnt/c/Recording_QA', '/Recording_QA'):
            with self.assertRaises(SystemExit) as cm:
                self.move(target=target, confirm=lambda t: True)
            self.assertIn('root of a drive', str(cm.exception))

    def test_a_target_that_does_not_end_in_recording_qa_is_refused_which_is_what_a_lost_separator_makes_of_it(self):
        # the laptop's platform-n3: C:/Users/dacz8/BattleLogs\\Recording_QA reaches the tool as C:/Users/dacz8/BattleLogsRecording_QA, and C:/Users/dacz8\\BattleLogs\\Recording_QA as C:/Users/dacz8BattleLogsRecording_QA
        for target in (os.path.join(self.t.root, 'BattleLogsRecording_QA'), os.path.join(self.t.root, 'Moved'), os.path.join(self.t.root, 'dacz8BattleLogsRecording_QA'), '/mnt/c/Usersdacz8BattleLogsRecording_QA'):
            with self.assertRaises(SystemExit) as cm:
                self.move(target=target, confirm=lambda t: True)
            self.assertIn('does not end in Recording_QA', str(cm.exception), target)
        self.assertTrue(os.path.isdir(self.t.qa))
        self.assertFalse(os.path.exists(os.path.join(self.t.root, 'BattleLogsRecording_QA')))

    def test_the_move_records_where_the_videos_stayed_in_the_moved_folder_and_the_hint_names_it(self):
        _, out = self.move(confirm=lambda t: True)
        rec = json.loads(read(os.path.join(self.target, bl.LOCATION_FILE)))
        self.assertEqual(os.path.abspath(bl.to_local(rec['battle_logs'])), os.path.abspath(self.t.logs))
        self.assertIn(bl.LOCATION_FILE, out)
        self.assertIn('--videos', out)

    def test_the_hint_quotes_a_path_with_a_space(self):
        self.assertEqual(bl.quoted('C:/Users/dacz8/Battle Logs'), '"C:/Users/dacz8/Battle Logs"')
        self.assertEqual(bl.quoted('C:/Users/dacz8/BattleLogs'), 'C:/Users/dacz8/BattleLogs')
        _, out = self.move(confirm=lambda t: True)
        self.assertIn('--videos "' + bl.to_forward(self.t.logs) + '"', out)       # (the made-up Battle Logs folder has a space)

    def test_the_dry_run_after_the_move_still_finds_the_videos_through_the_recorded_location(self):
        # the laptop's platform-n1: after the documented --move-to every packet was held back as "source video not found"
        self.t.game('BATCH_B', '20261001_000000002_iOS')
        idx = index(['BATCH_A/20261001_000000001_iOS', 'BATCH_B/20261001_000000002_iOS'])
        self.assertEqual([d.verdict for d in bl.decide(bl.scan_qa(self.t.qa, self.t.videos()), idx)], ['DELETE', 'DELETE'])
        self.move(confirm=lambda t: True)
        vdirs = bl.video_dirs(self.target)
        self.assertEqual(vdirs[0][1], bl.LOCATION_FILE)
        decisions = bl.decide(bl.scan_qa(self.target, bl.video_index_all(vdirs)), idx)
        self.assertEqual([d.verdict for d in decisions], ['DELETE', 'DELETE'], [g.reasons for d in decisions for g in d.games])
        # and without the recorded location the reason names where it looked and what to give
        os.remove(os.path.join(self.target, bl.LOCATION_FILE))
        again = bl.decide(bl.scan_qa(self.target, bl.video_index_all(bl.video_dirs(self.target)), 'somewhere'), idx)
        self.assertIn('not found in Battle Logs (looked in somewhere; --videos PATH names the folder)', ' '.join(again[0].games[0].reasons))
        # --videos names the folder
        viaflag = bl.decide(bl.scan_qa(self.target, bl.video_index_all(bl.video_dirs(self.target, self.t.logs))), idx)
        self.assertEqual([d.verdict for d in viaflag], ['DELETE', 'DELETE'])

    def test_a_dry_run_move_with_the_working_tree_check_says_the_import_is_not_checked_against_git(self):
        new, out = self.move(dry=True, import_check=lambda: [], import_label='present in the working tree of the checkout (NOT checked against git: a real move would be refused)')
        self.assertIsNone(new)
        self.assertIn('import check: every text output of Recording_QA is present in the working tree', out)
        self.assertIn('NOT checked against git', out)

    def test_a_target_two_levels_below_a_missing_folder_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self.move(target=os.path.join(self.t.root, 'nope', 'deeper', 'Recording_QA'), confirm=lambda t: True)
        self.assertIn('neither', str(cm.exception))
        self.assertFalse(os.path.exists(os.path.join(self.t.root, 'nope')))

    def test_one_missing_parent_folder_is_created_and_said(self):
        _, out = self.move(confirm=lambda t: True)
        self.assertTrue(os.path.isdir(self.base))
        self.assertIn('is created first', out)

    def test_an_existing_parent_is_not_announced_as_created(self):
        os.makedirs(self.base)
        _, out = self.move(confirm=lambda t: True)
        self.assertNotIn('is created first', out)
        self.assertTrue(os.path.isdir(self.target))

    def test_the_dry_run_moves_nothing_creates_nothing_and_does_not_ask(self):
        new, out = self.move(dry=True, confirm=lambda t: self.fail('asked'))
        self.assertIsNone(new)
        self.assertIn('dry run', out)
        self.assertTrue(os.path.isdir(self.t.qa))
        self.assertFalse(os.path.exists(self.base))

    def test_a_no_moves_nothing(self):
        with self.assertRaises(SystemExit):
            self.move(confirm=lambda t: False)
        self.assertTrue(os.path.isdir(self.t.qa))
        self.assertFalse(os.path.exists(self.base))

    def test_a_rename_that_fails_leaves_everything_where_it_was_and_removes_the_folder_it_made(self):
        with mock.patch.object(bl.os, 'rename', side_effect=PermissionError('in use')):
            with self.assertRaises(SystemExit) as cm:
                self.move(confirm=lambda t: True)
        self.assertIn('nothing was changed', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.qa))
        self.assertFalse(os.path.exists(self.base))

    def test_files_in_recording_qa_that_name_the_old_path_or_a_file_that_stays_are_listed_not_edited(self):
        script = os.path.join(self.t.qa, 'intake.py')
        write(script, r"BASE = r'C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs'" + "\\nopen('../MEDIA_LOCATIONS.json')")
        write(os.path.join(self.t.qa, 'BATCH_A', 'accept.py'), "x = 'media_locations.json'")
        _, out = self.move(dry=True)
        self.assertIn('intake.py', out)
        self.assertIn('BATCH_A/accept.py', out)
        self.assertIn('relative', out)
        self.assertIn('OneDrive', read(script).decode())

    def test_a_target_still_inside_onedrive_is_warned_about(self):
        os.makedirs(os.path.join(self.t.root, 'OneDrive'))
        _, out = self.move(target=os.path.join(self.t.root, 'OneDrive', 'Recording_QA'), dry=True)
        self.assertIn('still inside a OneDrive folder', out)

    def test_the_move_is_refused_while_the_text_outputs_are_not_all_committed(self):
        with self.assertRaises(SystemExit) as cm:
            self.move(confirm=lambda t: True, import_check=lambda: ['12 text files of Recording_QA are not at origin/main'])
        self.assertIn('not all committed', str(cm.exception))
        self.assertIn('battle_logs_import_packets', str(cm.exception))
        self.assertTrue(os.path.isdir(self.t.qa))
        self.assertFalse(os.path.exists(self.base))

    def test_the_move_goes_ahead_when_the_import_is_current_and_says_so(self):
        new, out = self.move(confirm=lambda t: True, import_check=lambda: [])
        self.assertEqual(new, self.target)
        self.assertIn('import check: every text output', out)

    def test_the_dry_run_shows_what_is_not_current_without_refusing(self):
        new, out = self.move(dry=True, import_check=lambda: ['3 text files differ'])
        self.assertIsNone(new)
        self.assertIn('IMPORT NOT CURRENT: 3 text files differ', out)
        self.assertIn('would be refused', out)


class Paths(unittest.TestCase):
    @unittest.skipIf(os.name == 'nt', 'posix side')
    def test_windows_paths_become_mnt_paths_in_wsl_and_back(self):
        self.assertEqual(bl.to_local('C:/Users/dacz8/BattleLogs'), '/mnt/c/Users/dacz8/BattleLogs')
        self.assertEqual(bl.to_local(r'C:\Users\dacz8\BattleLogs'), '/mnt/c/Users/dacz8/BattleLogs')
        self.assertEqual(bl.to_local('D:/x/y'), '/mnt/d/x/y')
        self.assertEqual(bl.to_windows('/mnt/c/Users/dacz8/BattleLogs/Recording_QA'), r'C:\Users\dacz8\BattleLogs\Recording_QA')
        self.assertEqual(bl.to_forward('/mnt/c/Users/dacz8/BattleLogs/Recording_QA'), 'C:/Users/dacz8/BattleLogs/Recording_QA')
        self.assertEqual(bl.to_windows('/tmp/x'), '/tmp/x')

    def test_a_windows_path_that_lost_its_backslashes_on_the_way_through_wsl_is_refused_not_guessed(self):
        # what the tool receives for C:\Users\dacz8\BattleLogs\Recording_QA typed after `wsl` in PowerShell
        for p in ('C:Usersdacz8BattleLogsRecording_QA', 'D:Foo'):
            with self.assertRaises(SystemExit) as cm:
                bl.to_local(p)
            self.assertIn('lost its backslashes', str(cm.exception))
        with self.assertRaises(SystemExit):
            bl.find_qa_root('C:Usersdacz8BattleLogsRecording_QA')

    def test_the_hints_use_forward_slashes_and_not_the_environment_variable(self):
        with open(os.path.join(HERE, 'battle_logs_cleanup.py'), encoding='utf-8') as f:
            src = f.read()
        self.assertNotIn('BATTLE_LOGS_QA', src)
        self.assertNotIn('--no-git" or', src)

    def test_fold_ignores_case_the_way_ntfs_does(self):
        self.assertEqual(bl.fold('/mnt/c/Users/X/Recording_QA'), bl.fold('/mnt/C/users/x/RECORDING_qa'))

    def test_a_qa_root_that_is_not_there_is_refused(self):
        with self.assertRaises(SystemExit):
            bl.find_qa_root(os.path.join(tempfile.gettempdir(), 'no_such_battle_logs_folder'))


class GitWorld:
    """a throwaway repo with committed games_meta/positions/audit list and an origin/main ref, as the tool reads them"""

    def __init__(self, test, folders, accepted=True, pending=None):
        self.repo = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.repo, True)
        self.folders = folders
        self.accepted = accepted
        self.pending = pending or {}
        self.write()
        self.g('init', '-q', '-b', 'main')
        self.commit('games and the audit list')

    def g(self, *a, cwd=None):
        return subprocess.run(['git', '-C', cwd or self.repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True).stdout

    def write(self):
        base = os.path.join(self.repo, os.path.dirname(META))
        meta, pos, games = {}, [], {}
        for f in self.folders:
            key = 'kw-' + f.split('/')[1][2:].replace('_iOS', '')
            meta[key] = {'folder': f}
            pos.append({'game': key})
            games[key] = {'folder': f, 'games_meta': META, 'positions': 1, 'positions_sha256': bl.positions_digest([{'game': key}])}
        write(os.path.join(base, 'games_meta.json'), json.dumps(meta))
        write(os.path.join(base, 'positions_all.json'), json.dumps(pos))
        audit = {'games': games, 'pending': self.pending, 'confirmed': accept(games) if self.accepted is True else self.accepted}
        write(os.path.join(self.repo, AUDIT), json.dumps(audit))

    def commit(self, msg):
        self.g('add', '-A')
        self.g('commit', '-q', '-m', msg)
        self.g('update-ref', 'refs/remotes/origin/main', 'HEAD')


@unittest.skipUnless(HAVE_GIT, 'git not installed')
class CommandLine(unittest.TestCase):
    FOLDERS = ['BATCH_A/20261001_000000001_iOS']

    def setUp(self):
        self.t = Tree(self)
        self.t.game('BATCH_A', '20261001_000000001_iOS')
        self.t.game('BATCH_B', '20261001_000000002_iOS')
        no_default(self)

    def run_main(self, world, *argv, offline=True):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = bl.main(['--qa-root', self.t.qa, '--repo', world.repo, *(['--allow-offline'] if offline else []), *argv])
        return code, out.getvalue()

    def main_raises(self, world, *argv, offline=True):
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', self.t.qa, '--repo', world.repo, *(['--allow-offline'] if offline else []), *argv])
        return str(cm.exception)

    def test_the_default_is_a_dry_run_that_changes_nothing_and_says_why(self):
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        code, out = self.run_main(w)
        self.assertEqual(code, 0)
        self.assertEqual(self.t.contents(), before)
        self.assertRegex(out, r'BATCH_A\s+DELETE')
        self.assertRegex(out, r'BATCH_B\s+keep')
        self.assertIn('not in the repo', out)
        self.assertIn('acceptance: laptop, 2026-10-14', out)
        self.assertIn('moves ONLY Recording_QA', out)
        self.assertIn('videos and the rest of Battle Logs stay', out)
        self.assertRegex(out, r'origin/main \([0-9a-f]{8}, committed \d{4}-')

    def test_apply_deletes_the_passing_games_frames_from_the_committed_state_and_writes_the_log(self):
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        code, out = self.run_main(w, '--apply', '--yes')
        after = self.t.contents()
        gone = sorted(set(before) - set(after))
        self.assertEqual(code, 0)
        self.assertTrue(gone and all('BATCH_A' in p and p.lower().endswith(bl.FRAME_EXT) for p in gone))
        self.assertIn('same SHA-256', out)
        self.assertTrue([p for p in after if os.path.basename(p).startswith('CLEANUP_LOG_')])
        self.assertIn('WARNING: origin could not be asked', out)

    def test_apply_refuses_no_git_even_with_yes_and_a_confirmation_only_in_the_working_tree(self):
        w = GitWorld(self, self.FOLDERS, accepted=None)                     # committed: not accepted
        w.accepted = True
        w.write()                                                           # accepted in the working tree only, never committed
        before = self.t.contents()
        self.assertIn('committed state of origin/main', self.main_raises(w, '--no-git', '--apply', '--yes'))
        self.assertEqual(self.t.contents(), before)
        self.main_raises(w, '--apply', '--yes')
        self.assertEqual(self.t.contents(), before)

    def test_apply_refuses_another_ref_unless_overridden_and_a_dry_run_may_read_any_ref(self):
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        self.assertIn('reads only the committed state of origin/main, not main', self.main_raises(w, '--ref', 'main', '--apply', '--yes'))
        self.assertEqual(self.t.contents(), before)
        code, out = self.run_main(w, '--ref', 'main', '--apply', '--yes', '--dry-run')
        self.assertEqual((code, self.t.contents()), (0, before))
        code, out = self.run_main(w, '--ref', 'main', '--apply', '--yes', '--allow-ref-other-than-origin-main')
        self.assertEqual(code, 0)
        self.assertNotEqual(self.t.contents(), before)

    def test_apply_refuses_a_confirmed_string_that_says_no_even_through_git(self):
        for value in ('no', 'pending', 'not yet - waiting for Dustin'):
            w = GitWorld(self, self.FOLDERS, accepted=value)
            before = self.t.contents()
            self.assertIn('not an acceptance', self.main_raises(w, '--apply', '--yes'))
            self.assertEqual(self.t.contents(), before)

    def test_apply_refuses_when_the_games_changed_after_the_acceptance(self):
        w = GitWorld(self, self.FOLDERS)
        w.folders = self.FOLDERS + ['BATCH_B/20261001_000000002_iOS']
        accepted_then = accept({'kw-261001_000000001': {'folder': self.FOLDERS[0], 'games_meta': META, 'positions': 1, 'positions_sha256': DIGEST}})
        w.accepted = accepted_then
        w.write()
        w.commit('a game added to the list without a new acceptance')
        before = self.t.contents()
        self.assertIn('needs a new acceptance', self.main_raises(w, '--apply', '--yes'))
        self.assertEqual(self.t.contents(), before)

    def test_apply_refuses_when_origin_has_a_newer_main_than_the_local_origin_main(self):
        w = GitWorld(self, self.FOLDERS)
        bare = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bare, True)
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', bare], check=True)
        w.g('remote', 'add', 'origin', bare)
        w.g('push', '-q', 'origin', 'main')
        w.g('fetch', '-q', 'origin')
        other = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, other, True)
        subprocess.run(['git', 'clone', '-q', bare, other], check=True, capture_output=True)
        write(os.path.join(other, 'revocation.txt'), 'the audit list was revoked')
        w.g('add', '-A', cwd=other)
        w.g('commit', '-q', '-m', 'revoke', cwd=other)
        w.g('push', '-q', 'origin', 'main', cwd=other)
        before = self.t.contents()
        self.assertIn('git fetch origin', self.main_raises(w, '--apply', '--yes'))
        self.assertEqual(self.t.contents(), before)
        w.g('fetch', '-q', 'origin')       # after fetching, the audit list is as committed and the run goes ahead
        code, out = self.run_main(w, '--apply', '--yes')
        self.assertEqual(code, 0)
        self.assertNotIn('could not be asked', out)

    def test_an_unreadable_apply_exits_non_zero_when_a_frame_could_not_be_deleted(self):
        w = GitWorld(self, self.FOLDERS)
        real = os.remove

        def locked(p, **kw):
            if p.endswith('t0001.jpg'):
                raise PermissionError(13, 'locked')
            real(p, **kw)
        with mock.patch.object(bl.os, 'remove', locked):
            code, out = self.run_main(w, '--apply', '--yes')
        self.assertEqual(code, 1)
        self.assertIn('INCOMPLETE', out)

    def test_only_previews_that_batch_with_a_dry_run_and_an_unknown_batch_is_an_error(self):
        w = GitWorld(self, self.FOLDERS + ['BATCH_B/20261001_000000002_iOS'])
        before = self.t.contents()
        code, out = self.run_main(w, '--apply', '--only', 'BATCH_A', '--dry-run')
        self.assertEqual((code, self.t.contents()), (0, before))
        self.assertIn('BATCH_A', out)
        self.assertNotIn('BATCH_B ', out)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', self.t.qa, '--repo', w.repo, '--only', 'BATCH_NOPE'])
        self.assertIn('do not exist', str(cm.exception))

    def test_audit_hash_prints_what_an_acceptance_must_carry(self):
        w = GitWorld(self, self.FOLDERS)
        code, out = self.run_main(w, '--audit-hash')
        want = bl.games_hash({'kw-261001_000000001': {'folder': self.FOLDERS[0], 'games_meta': META, 'positions': 1, 'positions_sha256': bl.positions_digest([{'game': 'kw-261001_000000001'}])}})
        self.assertEqual(out.split()[0], want)
        self.assertRegex(out, r'of the 1 games listed in .* at origin/main \([0-9a-f]{8}, committed ')

    def test_apply_and_move_cannot_be_combined(self):
        w = GitWorld(self, self.FOLDERS)
        with self.assertRaises(SystemExit):
            bl.main(['--qa-root', self.t.qa, '--repo', w.repo, '--apply', '--move-to', os.path.join(self.t.root, 'x', 'Recording_QA')])

    def test_apply_without_a_terminal_or_yes_refuses(self):
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        with mock.patch.object(sys, 'stdin', io.StringIO('')), self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', self.t.qa, '--repo', w.repo, '--allow-offline', '--apply'])
        self.assertIn('no terminal', str(cm.exception))
        self.assertEqual(self.t.contents(), before)

    def test_move_to_moves_only_recording_qa_after_a_yes_when_the_import_check_is_skipped(self):
        w = GitWorld(self, self.FOLDERS)
        write(os.path.join(self.t.logs, 'MEDIA_LOCATIONS.json'), '{}')
        target = os.path.join(self.t.root, 'Moved', 'Recording_QA')
        code, out = self.run_main(w, '--move-to', target, '--yes', '--no-import-check')
        self.assertEqual(code, 0)
        self.assertTrue(os.path.isdir(os.path.join(target, 'BATCH_A')))
        self.assertFalse(os.path.exists(self.t.qa))
        self.assertTrue(os.path.exists(os.path.join(self.t.logs, 'MEDIA_LOCATIONS.json')))
        self.assertIn('Codex should now use as its Recording_QA', out)

    def test_move_to_refuses_without_a_current_import_and_moves_nothing(self):
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        self.assertIn('not all committed', self.main_raises(w, '--move-to', os.path.join(self.t.root, 'Moved', 'Recording_QA'), '--yes'))
        self.assertEqual(self.t.contents(), before)

    def test_move_to_goes_ahead_once_the_import_is_committed(self):
        import battle_logs_import_packets as imp
        w = GitWorld(self, self.FOLDERS)
        with contextlib.redirect_stdout(io.StringIO()):
            imp.run(self.t.logs, w.repo)
        w.commit('the import')
        target = os.path.join(self.t.root, 'Moved', 'Recording_QA')
        code, out = self.run_main(w, '--move-to', target, '--yes')
        self.assertEqual(code, 0)
        self.assertIn('import check: every text output', out)
        self.assertTrue(os.path.isdir(os.path.join(target, 'BATCH_A')))

    # ---- the laptop's second review: freshness, the offline flag, the move's import check, the videos after a move
    def with_remote(self, w):
        """give the throwaway repo a bare origin that has its main; -> (bare path, a second clone to push from)"""
        bare = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, bare, True)
        subprocess.run(['git', 'init', '-q', '--bare', '-b', 'main', bare], check=True)
        w.g('remote', 'add', 'origin', bare)
        w.g('push', '-q', 'origin', 'main')
        w.g('fetch', '-q', 'origin')
        other = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, other, True)
        subprocess.run(['git', 'clone', '-q', bare, other], check=True, capture_output=True)
        return bare, other

    def push_revocation(self, w, other):
        write(os.path.join(other, 'revocation.txt'), 'the audit list was revoked')
        w.g('add', '-A', cwd=other)
        w.g('commit', '-q', '-m', 'revoke', cwd=other)
        w.g('push', '-q', 'origin', 'main', cwd=other)

    def test_apply_refuses_when_origin_cannot_be_asked_unless_it_is_told_to_go_on_offline(self):
        # gating-n1: a failing `git ls-remote` was only a warning, so a withdrawn acceptance still deleted
        w = GitWorld(self, self.FOLDERS)
        before = self.t.contents()
        msg = self.main_raises(w, '--apply', '--yes', offline=False)
        self.assertIn('origin cannot be asked', msg)
        self.assertIn('--allow-offline', msg)
        self.assertEqual(self.t.contents(), before)
        bare, other = self.with_remote(w)
        os.rename(bare, bare + '_gone')
        self.addCleanup(lambda: os.path.exists(bare + '_gone') and shutil.rmtree(bare + '_gone', True))
        self.assertIn('origin cannot be asked', self.main_raises(w, '--apply', '--yes', offline=False))
        self.assertEqual(self.t.contents(), before)
        code, out = self.run_main(w, '--apply', '--yes')                                  # told to go on: it warns and deletes
        self.assertEqual(code, 0)
        self.assertIn('WARNING: origin could not be asked', out)
        self.assertNotEqual(self.t.contents(), before)

    def test_the_question_to_origin_never_waits_for_a_password(self):
        w = GitWorld(self, self.FOLDERS)
        seen = {}
        real = subprocess.run

        def spy(cmd, *a, **kw):
            if 'ls-remote' in cmd:
                seen['env'], seen['cmd'] = kw.get('env'), cmd
            return real(cmd, *a, **kw)
        with mock.patch.object(bl.subprocess, 'run', spy):
            bl.RepoView(w.repo).remote_main()
        self.assertEqual(seen['env']['GIT_TERMINAL_PROMPT'], '0')
        self.assertEqual(seen['cmd'][-2:], ['origin', 'refs/heads/main'])

    def test_a_revocation_pushed_while_the_delete_question_is_open_is_seen_after_the_answer(self):
        w = GitWorld(self, self.FOLDERS)
        bare, other = self.with_remote(w)
        before = self.t.contents()

        def answer(prompt):
            self.push_revocation(w, other)                 # pushed while the question is open
            return 'DELETE'
        fake_stdin = mock.Mock()
        fake_stdin.isatty.return_value = True
        with mock.patch.object(sys, 'stdin', fake_stdin), mock.patch('builtins.input', answer):
            msg = self.main_raises(w, '--apply')
        self.assertIn('git fetch origin', msg)
        self.assertEqual(self.t.contents(), before, 'nothing was deleted')

    def test_origin_is_asked_for_refs_heads_main_only_so_a_branch_that_ends_in_main_cannot_stand_in_for_it(self):
        # gating-n2: `git ls-remote origin main` matched backup/main too and took the first line
        w = GitWorld(self, self.FOLDERS)
        bare, other = self.with_remote(w)
        stale = w.g('rev-parse', 'HEAD').strip()
        w.g('push', '-q', 'origin', 'HEAD:refs/heads/backup/main')                 # a snapshot branch at the accepted commit
        self.push_revocation(w, other)                                              # main moves on with a revocation; this clone has not fetched
        self.assertEqual(bl.RepoView(w.repo).remote_main()[0], w.g('ls-remote', 'origin', 'refs/heads/main').split()[0])
        self.assertNotEqual(bl.RepoView(w.repo).remote_main()[0], stale)
        before = self.t.contents()
        self.assertIn('git fetch origin', self.main_raises(w, '--apply', '--yes'))
        self.assertEqual(self.t.contents(), before)

    def test_a_local_branch_named_origin_main_does_not_stand_in_for_the_remote_tracking_ref(self):
        w = GitWorld(self, self.FOLDERS)
        first = w.g('rev-parse', 'HEAD').strip()
        write(os.path.join(w.repo, 'later.txt'), 'later')
        w.commit('a later commit (origin/main moves here)')
        w.g('branch', 'origin/main', first)                                         # a local branch with the remote-tracking ref's short name
        self.assertEqual(bl.RepoView(w.repo).commit_full, w.g('rev-parse', 'refs/remotes/origin/main').strip())
        self.assertNotEqual(bl.RepoView(w.repo).commit_full, first)

    def test_audit_hash_refuses_when_the_list_is_not_committed_at_the_ref_and_needs_no_recording_qa(self):
        # gating-n5: it printed the hash of an empty list (sha256 of "{}") and needed Recording_QA
        w = GitWorld(self, self.FOLDERS)
        w.g('rm', '-q', AUDIT)
        w.commit('the audit list removed')
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
            bl.main(['--qa-root', os.path.join(self.t.root, 'nowhere'), '--repo', w.repo, '--audit-hash'])
        self.assertIn('is not committed at', str(cm.exception))
        w2 = GitWorld(self, self.FOLDERS)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bl.main(['--qa-root', os.path.join(self.t.root, 'nowhere'), '--repo', w2.repo, '--audit-hash']), 0)
        self.assertRegex(out.getvalue(), r'^[0-9a-f]{64}  \(games_sha256 of the 1 games')

    def test_main_exits_1_when_a_packet_was_skipped_even_though_nothing_failed(self):
        # platform-4: apply_deletions printed INCOMPLETE but main() returned 0 because only failed deletions counted
        w = GitWorld(self, self.FOLDERS)
        ledger = os.path.join(self.t.qa, 'BATCH_A', '20261001_000000001_iOS', 'TURN_LEDGER.json')
        real = bl.check_fresh
        calls = []

        def vanish(*a, **kw):
            real(*a, **kw)
            calls.append(1)
            if len(calls) == 1:
                os.remove(ledger)                          # between the scan and the inventory
        with mock.patch.object(bl, 'check_fresh', vanish):
            code, out = self.run_main(w, '--apply', '--yes')
        self.assertEqual(code, 1)
        self.assertIn('SKIPPED BATCH_A/20261001_000000001_iOS', out)
        self.assertIn('INCOMPLETE: 0 frames could not be deleted and 1 packets were skipped', out)
        self.assertTrue(os.path.exists(os.path.join(self.t.qa, 'BATCH_A', '20261001_000000001_iOS', 'turn_evidence', 't0000.jpg')))

    def test_videos_names_the_folder_and_a_name_that_is_not_a_folder_is_refused(self):
        w = GitWorld(self, self.FOLDERS)
        elsewhere = os.path.join(self.t.root, 'elsewhere videos')
        os.makedirs(os.path.join(elsewhere, 'Reviewed'))
        shutil.move(os.path.join(self.t.logs, '20261001_000000001_iOS.MP4'), os.path.join(elsewhere, 'Reviewed', '20261001_000000001_iOS.MP4'))
        code, out = self.run_main(w)
        self.assertRegex(out, r'BATCH_A\s+keep')
        self.assertIn('--videos PATH names the folder', out)
        code, out = self.run_main(w, '--videos', elsewhere)
        self.assertRegex(out, r'BATCH_A\s+DELETE')
        self.assertIn('Source videos looked for in: ' + elsewhere + ' (--videos)', out)
        self.assertIn('is not a folder', self.main_raises(w, '--videos', os.path.join(self.t.root, 'nope')))

    def test_after_the_move_the_tool_still_finds_the_videos_and_the_next_round_can_run(self):
        # platform-n1 / scope-n2 through the command line
        w = GitWorld(self, self.FOLDERS)
        target = os.path.join(self.t.root, 'Moved', 'Recording_QA')
        code, out = self.run_main(w, '--move-to', target, '--yes', '--no-import-check')
        self.assertEqual(code, 0)
        self.assertIn(bl.LOCATION_FILE, out)
        moved_out = io.StringIO()
        with contextlib.redirect_stdout(moved_out):
            bl.main(['--qa-root', target, '--repo', w.repo, '--allow-offline'])
        self.assertRegex(moved_out.getvalue(), r'BATCH_A\s+DELETE')
        self.assertIn(bl.LOCATION_FILE, moved_out.getvalue())

    def test_move_to_refuses_no_git_and_another_ref_like_apply_does_and_a_dry_run_says_what_it_did_not_check(self):
        # platform-n2: the import check passed on an import that was only in the working tree, and the tool said "committed"
        import battle_logs_import_packets as imp
        w = GitWorld(self, self.FOLDERS)
        with contextlib.redirect_stdout(io.StringIO()):
            imp.run(self.t.logs, w.repo)                      # written into the working tree, never committed
        target = os.path.join(self.t.root, 'Moved', 'Recording_QA')
        before = self.t.contents()
        self.assertIn('--move-to (its import check) reads only the committed state of origin/main', self.main_raises(w, '--move-to', target, '--yes', '--no-git'))
        self.assertIn('not main', self.main_raises(w, '--move-to', target, '--yes', '--ref', 'main'))
        self.assertEqual(self.t.contents(), before)
        self.assertFalse(os.path.exists(os.path.join(self.t.root, 'Moved')))
        code, out = self.run_main(w, '--move-to', target, '--dry-run', '--no-git')
        self.assertEqual(code, 0)
        self.assertIn('present in the working tree of the checkout (NOT checked against git', out)
        self.assertNotIn('is committed, byte for byte', out)
        self.assertEqual(self.t.contents(), before)

    def test_move_to_refuses_when_origin_has_a_newer_main_than_this_checkout(self):
        import battle_logs_import_packets as imp
        w = GitWorld(self, self.FOLDERS)
        with contextlib.redirect_stdout(io.StringIO()):
            imp.run(self.t.logs, w.repo)
        w.commit('the import')
        bare, other = self.with_remote(w)
        w.g('push', '-q', 'origin', 'main')
        w.g('fetch', '-q', 'origin')
        self.push_revocation(w, other)
        before = self.t.contents()
        self.assertIn('git fetch origin', self.main_raises(w, '--move-to', os.path.join(self.t.root, 'Moved', 'Recording_QA'), '--yes'))
        self.assertEqual(self.t.contents(), before)

    def test_the_dry_run_counts_links_it_did_not_examine(self):
        if os.name == 'nt':
            self.skipTest('symlinks need privileges on Windows')
        w = GitWorld(self, self.FOLDERS)
        os.symlink(self.t.root, os.path.join(self.t.qa, 'BATCH_A', '20261001_000000001_iOS', 'a_link'))
        code, out = self.run_main(w)
        self.assertIn('links or unreadable entries NOT examined', out)


if __name__ == '__main__':
    unittest.main()
