#!/usr/bin/env python3
"""Tests for tools/battle_logs_import_packets.py, on made-up Battle Logs trees (nothing here reads the real Battle Logs).

  cd tools && python3 -B -m unittest -v test_battle_logs_import_packets"""
import contextlib, hashlib, io, json, os, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battle_logs_import_packets as imp  # noqa: E402


def write(path, data=b'x'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode())


class World:
    """a made-up Battle Logs folder and a made-up repository checkout"""

    def __init__(self, test):
        self.root = tempfile.mkdtemp()
        test.addCleanup(shutil.rmtree, self.root, True)
        self.bl = os.path.join(self.root, 'Battle Logs')
        self.qa = os.path.join(self.bl, 'Recording_QA')
        self.repo = os.path.join(self.root, 'repo')
        os.makedirs(self.repo)
        self.dest = os.path.join(self.repo, imp.DEST)
        p = lambda rel, data='{"a": 1}': write(os.path.join(self.bl, *rel.split('/')), data)
        self.p = p
        g = 'Recording_QA/BATCH_A/20261001_000000001_iOS/'
        p(g + 'TURN_LEDGER.json', '{"turns": []}')
        p(g + 'REVIEW.md', '# review')
        p(g + 'DECK_USED.json')
        p(g + 'notes.txt', 'n')
        p(g + 'extract_seek.py', 'print(1)')
        p(g + 'sub/deep/UNCERTAINTIES.json')
        p(g + 'README.md.before_completion', 'old')
        p('Recording_QA/BATCH_A/README.md', '# batch')
        p('Recording_QA/BATCH_A/DOWNLOAD_SUCCESS.json')
        p('Recording_QA/BATCH_A/qr_support/notes.txt', 'support')
        p('Recording_QA/20260908_old_review/REVIEW.md', '# old')
        p('Recording_QA/accept.py', 'x = 1')
        p('MEDIA_LOCATIONS.json', '{"m": 1}')
        p('NOTES.md', '# n')
        # things that must never be copied
        for rel in ('turn_evidence/t0000.jpg', 'o.PNG', 'x.json.png'):
            p(g + rel, b'IMG')
        p(g + 'video.MP4', b'VID')
        p('big_video.mov', b'VID')
        p('Recording_QA/BATCH_A/qr_support/deps/cv2/cv2.pyd', b'BIN')
        p('Recording_QA/BATCH_A/qr_support/deps/cv2/data.json', '{"vendored": 1}')
        p('Recording_QA/BATCH_A/qr_support/deps/zxing.dist-info/METADATA.txt', 'meta')
        p(g + 'independent_sol/qr_dependencies/zxingcpp/info.txt', 'dep')
        p(g + '__pycache__/x.pyc', b'PYC')
        p(g + 'archive.zip', b'ZIP')
        p(g + 'sound.wav', b'WAV')

    def source_snapshot(self):
        out = {}
        for root, _, files in os.walk(self.bl):
            for f in files:
                fp = os.path.join(root, f)
                st = os.stat(fp)
                with open(fp, 'rb') as fh:
                    out[os.path.relpath(fp, self.root)] = (st.st_size, st.st_mtime_ns, hashlib.sha256(fh.read()).hexdigest())
        return out

    def run(self, **kw):
        out = io.StringIO()
        res = imp.run(self.bl, self.repo, out=out, **kw)
        return res, out.getvalue()

    def copied(self):
        out = {}
        for root, _, files in os.walk(self.dest):
            for f in files:
                fp = os.path.join(root, f)
                with open(fp, 'rb') as fh:
                    out[os.path.relpath(fp, self.dest).replace(os.sep, '/')] = fh.read()
        return out

    def read_bytes(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def manifest(self):
        with open(os.path.join(self.dest, 'MANIFEST.json'), encoding='utf-8') as f:
            return json.load(f)


class Selection(unittest.TestCase):
    def setUp(self):
        self.w = World(self)

    def test_text_outputs_are_copied_in_the_layout_and_nothing_else(self):
        self.w.run()
        got = sorted(k for k in self.w.copied() if k not in ('MANIFEST.json', '.gitattributes'))
        self.assertEqual(got, sorted([
            'BATCH_A/20261001_000000001_iOS/TURN_LEDGER.json', 'BATCH_A/20261001_000000001_iOS/REVIEW.md', 'BATCH_A/20261001_000000001_iOS/DECK_USED.json',
            'BATCH_A/20261001_000000001_iOS/notes.txt', 'BATCH_A/20261001_000000001_iOS/extract_seek.py', 'BATCH_A/20261001_000000001_iOS/sub/deep/UNCERTAINTIES.json',
            'BATCH_A/20261001_000000001_iOS/README.md.before_completion',
            'BATCH_A/_batch/README.md', 'BATCH_A/_batch/DOWNLOAD_SUCCESS.json', 'BATCH_A/_batch/qr_support/notes.txt',
            '_not_in_a_batch/20260908_old_review/REVIEW.md', '_recording_qa_root/accept.py', '_battle_logs_root/MEDIA_LOCATIONS.json', '_battle_logs_root/NOTES.md']))

    def test_images_videos_binaries_and_vendored_folders_are_never_copied(self):
        self.w.run()
        for k in self.w.copied():
            low = k.lower()
            self.assertFalse(low.endswith(('.jpg', '.png', '.mp4', '.mov', '.pyd', '.pyc', '.zip', '.wav')), k)
            self.assertNotIn('deps', k.split('/'))
            self.assertNotIn('qr_dependencies', k.split('/'))
            self.assertNotIn('__pycache__', k.split('/'))
            self.assertFalse(any(part.endswith('.dist-info') for part in k.split('/')), k)

    def test_the_report_says_what_was_not_copied_and_why(self):
        _, out = self.w.run()
        self.assertIn('x image', out)
        self.assertIn('x video', out)
        self.assertIn('x vendored or cache folder', out)
        self.assertIn('x not a text output: .zip', out)

    def test_file_contents_are_copied_byte_for_byte_including_line_endings(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/crlf.txt', b'a\r\nb\r\n')
        self.w.run()
        self.assertEqual(self.w.copied()['BATCH_A/20261001_000000001_iOS/crlf.txt'], b'a\r\nb\r\n')

    def test_a_gitattributes_file_keeps_git_from_converting_line_endings(self):
        self.w.run()
        self.assertIn(b'* -text', self.w.read_bytes(os.path.join(self.w.dest, '.gitattributes')))

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_links_are_not_followed(self):
        outside = os.path.join(self.w.root, 'elsewhere')
        write(os.path.join(outside, 'secret.json'), '{}')
        os.symlink(outside, os.path.join(self.w.qa, 'BATCH_A', 'linked'))
        os.symlink(os.path.join(outside, 'secret.json'), os.path.join(self.w.qa, 'BATCH_A', 'link.json'))
        _, out = self.w.run()
        self.assertFalse([k for k in self.w.copied() if 'secret' in k or 'linked' in k or 'link.json' in k])
        self.assertIn('x link', out)


class Manifest(unittest.TestCase):
    def setUp(self):
        self.w = World(self)

    def test_every_copied_file_has_its_source_path_sha256_and_size(self):
        self.w.run()
        m = self.w.manifest()
        self.assertEqual(m['schema'], imp.SCHEMA)
        e = m['files']['BATCH_A/20261001_000000001_iOS/TURN_LEDGER.json']
        self.assertEqual(e['source'], 'Recording_QA/BATCH_A/20261001_000000001_iOS/TURN_LEDGER.json')
        self.assertEqual(e['sha256'], hashlib.sha256(b'{"turns": []}').hexdigest())
        self.assertEqual(e['size'], len(b'{"turns": []}'))
        self.assertEqual(m['files']['_battle_logs_root/MEDIA_LOCATIONS.json']['source'], 'MEDIA_LOCATIONS.json')
        self.assertEqual(set(m['files']), {k for k in self.w.copied() if k not in ('MANIFEST.json', '.gitattributes')})

    def test_the_size_is_that_of_the_bytes_copied_even_when_a_live_file_grew_after_the_scan(self):
        real = imp.scan_source

        def stale(*a, **kw):
            sc = real(*a, **kw)
            sc.files = [(r, p, s - 3 if r.endswith('TURN_LEDGER.json') else s) for r, p, s in sc.files]      # the size the scan saw, before the file grew
            return sc
        imp.scan_source = stale
        self.addCleanup(setattr, imp, 'scan_source', real)
        self.w.run()
        for k, e in self.w.manifest()['files'].items():
            self.assertEqual(e['size'], len(self.w.copied()[k]), k)

    def test_the_copy_matches_the_manifest(self):
        self.w.run()
        for k, e in self.w.manifest()['files'].items():
            self.assertEqual(hashlib.sha256(self.w.copied()[k]).hexdigest(), e['sha256'], k)


class Idempotence(unittest.TestCase):
    def setUp(self):
        self.w = World(self)
        self.first, _ = self.w.run()

    def test_a_second_run_changes_nothing_and_rewrites_nothing(self):
        before = {k: os.stat(os.path.join(self.w.dest, *k.split('/'))).st_mtime_ns for k in self.w.copied()}
        mtext = self.w.read_bytes(os.path.join(self.w.dest, 'MANIFEST.json'))
        res, out = self.w.run()
        self.assertEqual((res['new'], res['changed'], res['missing']), (0, 0, 0))
        self.assertEqual(res['same'], self.first['new'])
        self.assertEqual({k: os.stat(os.path.join(self.w.dest, *k.split('/'))).st_mtime_ns for k in self.w.copied()}, before)
        self.assertEqual(self.w.read_bytes(os.path.join(self.w.dest, 'MANIFEST.json')), mtext)
        self.assertIn('MANIFEST.json unchanged', out)

    def test_a_changed_source_file_is_copied_again_and_a_new_one_is_added_and_nothing_else_is(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/REVIEW.md', '# review, corrected')
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/NEW.json', '{"new": 1}')
        res, _ = self.w.run()
        self.assertEqual((res['new'], res['changed']), (1, 1))
        self.assertEqual(self.w.copied()['BATCH_A/20261001_000000001_iOS/REVIEW.md'], b'# review, corrected')
        self.assertIn('BATCH_A/20261001_000000001_iOS/NEW.json', self.w.manifest()['files'])

    def test_a_file_whose_source_has_gone_stays_in_the_copy_and_is_marked(self):
        os.remove(os.path.join(self.w.qa, 'BATCH_A', '20261001_000000001_iOS', 'notes.txt'))
        res, out = self.w.run()
        self.assertEqual(res['missing'], 1)
        k = 'BATCH_A/20261001_000000001_iOS/notes.txt'
        self.assertIn(k, self.w.copied())
        self.assertTrue(self.w.manifest()['files'][k]['source_missing'])
        self.assertIn('source gone but kept 1', out)

    def test_a_copy_damaged_in_the_repo_is_repaired_from_the_source(self):
        k = os.path.join(self.w.dest, 'BATCH_A', '20261001_000000001_iOS', 'REVIEW.md')
        write(k, 'tampered')
        res, _ = self.w.run()
        self.assertEqual(res['changed'], 1)
        self.assertEqual(self.w.read_bytes(k), b'# review')

    def test_the_dry_run_writes_nothing(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/NEW.json', '{"new": 1}')
        before = self.w.copied()
        res, out = self.w.run(dry=True)
        self.assertEqual(res['new'], 1)
        self.assertEqual(self.w.copied(), before)
        self.assertIn('dry run', out)


class SourceIsOnlyRead(unittest.TestCase):
    def test_the_source_tree_is_identical_after_a_run(self):
        w = World(self)
        before = w.source_snapshot()
        w.run()
        w.run()
        self.assertEqual(w.source_snapshot(), before)

    def test_a_destination_inside_the_source_or_the_other_way_round_is_refused(self):
        w = World(self)
        with self.assertRaises(SystemExit):
            imp.run(w.bl, w.bl, out=io.StringIO())
        with self.assertRaises(SystemExit):
            imp.run(w.bl, w.qa, out=io.StringIO())

    def test_a_folder_without_recording_qa_is_refused(self):
        w = World(self)
        other = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, other, True)
        with self.assertRaises(SystemExit) as cm:
            imp.run(other, w.repo, out=io.StringIO())
        self.assertIn('no Recording_QA', str(cm.exception))


class SizeGuard(unittest.TestCase):
    def setUp(self):
        self.w = World(self)
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/big_ledger.json', b'z' * 700_000)
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/bigger.json', b'z' * 900_000)

    def test_above_the_total_limit_it_refuses_before_writing_anything_and_says_what_is_large(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            imp.run(self.w.bl, self.w.repo, max_total_mb=1, out=out)
        self.assertIn('above 1 MB', str(cm.exception))
        text = out.getvalue()
        self.assertIn('REFUSED', text)
        self.assertIn('largest files', text)
        self.assertIn('bigger.json', text)
        self.assertIn('BATCH_A', text)
        self.assertFalse(os.path.exists(self.w.dest))

    def test_the_limit_counts_what_is_already_in_the_copy_with_its_source_gone(self):
        self.w.run()
        os.remove(os.path.join(self.w.qa, 'BATCH_A', '20261001_000000001_iOS', 'bigger.json'))
        with self.assertRaises(SystemExit):
            imp.run(self.w.bl, self.w.repo, max_total_mb=1, out=io.StringIO())

    def test_a_single_file_above_the_file_limit_is_skipped_and_reported_not_fatal(self):
        res, out = self.w.run(max_file_mb=0)
        self.assertEqual(res['files'], 0)
        self.assertIn('larger than 0 MB', out)

    def test_a_path_too_long_for_a_windows_checkout_is_skipped_and_reported(self):
        deep = os.path.join(*['d' * 40] * 5)
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/' + deep.replace(os.sep, '/') + '/x.json')
        _, out = self.w.run()
        self.assertIn('path too long', out)
        self.assertFalse([k for k in self.w.copied() if 'ddddd' in k])


class IsTheCopyCurrent(unittest.TestCase):
    def setUp(self):
        self.w = World(self)
        self.w.run()

    def problems(self, **kw):
        return imp.import_problems(self.w.bl, self.w.repo, **kw)

    def test_after_an_import_the_working_tree_copy_is_current(self):
        self.assertEqual(self.problems(no_git=True), [])

    def test_a_new_source_file_is_reported_as_not_copied(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/NEW.json', '{"n": 1}')
        probs = self.problems(no_git=True)
        self.assertTrue(probs and 'not in the working tree' in probs[0] and 'NEW.json' in probs[0])

    def test_a_changed_source_file_is_reported_as_differing(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/REVIEW.md', '# review, corrected')
        probs = self.problems(no_git=True)
        self.assertTrue(probs and 'differ from the copy' in probs[0])

    def test_a_file_that_is_only_at_the_top_of_battle_logs_is_not_required(self):
        self.w.p('NEW_NOTES.md', '# stays in OneDrive')
        self.assertEqual(self.problems(no_git=True), [])

    @unittest.skipUnless(shutil.which('git'), 'git not installed')
    def test_with_git_the_copy_must_be_committed_at_the_ref_byte_for_byte(self):
        g = lambda *a: subprocess.run(['git', '-C', self.w.repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True)
        g('init', '-q', '-b', 'main')
        probs = imp.import_problems(self.w.bl, self.w.repo, ref='main')
        self.assertTrue(probs, 'nothing is committed yet (git cannot even read main)')
        g('add', imp.DEST)
        g('commit', '-q', '-m', 'packets')
        self.assertEqual(imp.import_problems(self.w.bl, self.w.repo, ref='main'), [])
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/REVIEW.md', '# changed after the commit')
        probs = imp.import_problems(self.w.bl, self.w.repo, ref='main')
        self.assertTrue(probs and 'differ from the copy at main' in probs[0])

    @unittest.skipUnless(shutil.which('git'), 'git not installed')
    def test_a_copy_that_is_in_the_working_tree_but_not_committed_does_not_count_at_a_ref(self):
        g = lambda *a: subprocess.run(['git', '-C', self.w.repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True)
        g('init', '-q', '-b', 'main')
        write(os.path.join(self.w.repo, 'README'), 'x')
        g('add', 'README')
        g('commit', '-q', '-m', 'first')
        probs = imp.import_problems(self.w.bl, self.w.repo, ref='main')
        self.assertTrue(probs and 'not at main' in probs[0])

    def test_a_text_output_the_import_would_skip_is_a_problem_not_a_pass(self):
        # it is in no copy, so it cannot be shown to be committed (the size and path limits are the import's)
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/huge_ledger.json', b'z' * 2_000_000)
        probs = self.problems(no_git=True, max_file_mb=1)
        self.assertTrue([p for p in probs if 'larger than 1 MB' in p and 'huge_ledger.json' in p], probs)
        deep = '/'.join(['d' * 40] * 5)
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/' + deep + '/x.json')
        probs = self.problems(no_git=True)
        self.assertTrue([p for p in probs if 'path too long' in p or 'too long for a Windows checkout' in p], probs)

    @unittest.skipIf(os.name == 'nt', 'symlinks need privileges on Windows')
    def test_a_link_the_scan_could_not_follow_means_a_text_output_behind_it_cannot_be_shown_to_be_committed(self):
        elsewhere = os.path.join(self.w.root, 'elsewhere')
        write(os.path.join(elsewhere, 'REVIEW.md'), '# only here')
        os.symlink(elsewhere, os.path.join(self.w.qa, 'BATCH_A', '20261001_000000001_iOS', 'linked'))
        probs = self.problems(no_git=True)
        self.assertTrue([p for p in probs if '1 x link' in p and 'could not be examined' in p], probs)

    def test_a_folder_the_scan_cannot_read_is_a_problem(self):
        real = os.scandir

        def scandir(path):
            if os.fspath(path).endswith(os.path.join('20261001_000000001_iOS', 'sub')):
                raise PermissionError(13, 'denied')
            return real(path)
        with mock.patch.object(imp.os, 'scandir', scandir):
            probs = self.problems(no_git=True)
        self.assertTrue([p for p in probs if 'folder not readable' in p and 'could not be examined' in p], probs)

    def test_a_recording_qa_with_no_text_outputs_at_all_is_a_problem_not_a_pass(self):
        bl2 = os.path.join(self.w.root, 'Empty Battle Logs')
        os.makedirs(os.path.join(bl2, 'Recording_QA'))
        probs = imp.import_problems(bl2, self.w.repo, no_git=True)
        self.assertTrue([p for p in probs if 'no text outputs at all' in p], probs)

    def test_a_second_check_with_the_same_cache_hashes_only_what_changed(self):
        cache = {}
        self.assertEqual(self.problems(no_git=True, cache=cache), [])
        self.assertTrue(cache)
        counted = []
        real, copy = imp.blob_sha1, imp.working_blobs(self.w.repo)           # (the hashing of the copy in the working tree is not what is counted)
        with mock.patch.object(imp, 'working_blobs', lambda *a, **k: copy), mock.patch.object(imp, 'blob_sha1', lambda data: counted.append(1) or real(data)):
            self.assertEqual(self.problems(no_git=True, cache=cache), [])
            self.assertEqual(counted, [], 'nothing changed: nothing hashed again')
            path = os.path.join(self.w.qa, 'BATCH_A', '20261001_000000001_iOS', 'REVIEW.md')
            self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/REVIEW.md', '# review, corrected')
            os.utime(path, ns=(2_000_000_000_000_000_000, 2_000_000_000_000_000_000))
            probs = self.problems(no_git=True, cache=cache)
        self.assertEqual(len(counted), 1, 'only the changed file was read again')
        self.assertTrue(probs and 'differ from the copy' in probs[0])

    def test_files_that_leave_with_the_folder_but_are_not_copied_are_reported_in_info(self):
        info = {}
        self.assertEqual(self.problems(no_git=True, info=info), [])
        text = ' | '.join(info['uncopied'])
        self.assertIn('.zip', text)
        self.assertIn('.wav', text)
        self.assertIn('vendored or cache folder', text)
        self.assertNotIn('video', text)
        self.assertNotIn('image', text)

    def test_the_source_is_the_first_default_that_has_a_recording_qa_in_it(self):
        no_qa = os.path.join(self.w.root, 'No QA Here')
        os.makedirs(no_qa)
        with mock.patch.dict(os.environ, {'BATTLE_LOGS': no_qa}):
            try:
                found = imp.find_source()
            except SystemExit:
                found = None
        self.assertNotEqual(found, no_qa, 'a Battle Logs folder without Recording_QA (the one left after --move-to) is not the source')
        with mock.patch.dict(os.environ, {'BATTLE_LOGS': self.w.bl}):
            self.assertEqual(imp.find_source(), os.path.abspath(self.w.bl))

    @unittest.skipUnless(shutil.which('git'), 'git not installed')
    def test_origin_main_means_the_remote_tracking_ref_not_a_local_branch_of_that_name(self):
        g = lambda *a: subprocess.run(['git', '-C', self.w.repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a], check=True, capture_output=True, text=True)
        g('init', '-q', '-b', 'main')
        write(os.path.join(self.w.repo, 'README'), 'x')
        g('add', 'README')
        g('commit', '-q', '-m', 'first')
        g('branch', 'origin/main')                                   # a local branch that shadows the short name, at a commit without the packets
        g('add', imp.DEST)
        g('commit', '-q', '-m', 'packets')
        g('update-ref', 'refs/remotes/origin/main', 'HEAD')
        self.assertEqual(imp.import_problems(self.w.bl, self.w.repo, ref='origin/main'), [])

    def test_check_from_the_command_line_notes_what_leaves_without_a_copy(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = imp.main(['--source', self.w.bl, '--repo', self.w.repo, '--check'])
        self.assertEqual(code, 0)
        self.assertIn('NOTE: these files of Recording_QA are not text outputs and are not copied into git', out.getvalue())
        self.assertIn('.zip', out.getvalue())

    def test_check_from_the_command_line_exits_1_when_not_current(self):
        self.w.p('Recording_QA/BATCH_A/20261001_000000001_iOS/NEW.json', '{"n": 1}')
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = imp.main(['--source', self.w.bl, '--repo', self.w.repo, '--check'])
        self.assertEqual(code, 1)
        self.assertIn('NOT CURRENT', out.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(imp.main(['--source', self.w.bl, '--repo', self.w.repo]), 0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(imp.main(['--source', self.w.bl, '--repo', self.w.repo, '--check']), 0)


class Layout(unittest.TestCase):
    def test_dest_rel_for_every_kind_of_place(self):
        d = imp.dest_rel
        self.assertEqual(d('Recording_QA/BATCH_X/20261013_030351000_iOS/TURN_LEDGER.json'), 'BATCH_X/20261013_030351000_iOS/TURN_LEDGER.json')
        self.assertEqual(d('Recording_QA/BATCH_X/20261002_205230000_iOS_auto_sol/a/b.json'), 'BATCH_X/20261002_205230000_iOS_auto_sol/a/b.json')
        self.assertEqual(d('Recording_QA/BATCH_X/README.md'), 'BATCH_X/_batch/README.md')
        self.assertEqual(d('Recording_QA/BATCH_X/qr_support/n.txt'), 'BATCH_X/_batch/qr_support/n.txt')
        self.assertEqual(d('Recording_QA/20260908_review/x/y.json'), '_not_in_a_batch/20260908_review/x/y.json')
        self.assertEqual(d('Recording_QA/accept.py'), '_recording_qa_root/accept.py')
        self.assertEqual(d('MEDIA_LOCATIONS.json'), '_battle_logs_root/MEDIA_LOCATIONS.json')

    def test_blob_sha1_is_gits_object_id(self):
        self.assertEqual(imp.blob_sha1(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')       # `printf 'hello\n' | git hash-object --stdin`


if __name__ == '__main__':
    unittest.main()
