#!/usr/bin/env python3
"""battle_logs_import_packets.py: copy the TEXT outputs of Codex's packets (ledgers, reviews, deck files, receipts, scripts, MEDIA_LOCATIONS.json) from Battle Logs into the repository, so that
GitHub is their backup before Recording_QA is moved out of OneDrive (tools/battle_logs_cleanup.py --move-to).

  python3 tools/battle_logs_import_packets.py              copy what is new or changed into rl/results/battle_log_packets/ and write its MANIFEST.json (prints a report)
  python3 tools/battle_logs_import_packets.py --dry-run    the report only: nothing is written
  python3 tools/battle_logs_import_packets.py --check      is the copy in the repository current? (exit 1 if not; writes nothing)
  python3 tools/battle_logs_import_packets.py --check --ref origin/main    ...and is it COMMITTED at that ref, byte for byte? (what --move-to asks)

The source is only ever read. Images (jpg, png, ...), videos and every binary are never copied; what is copied is chosen by extension (json, jsonl, txt, md, csv, tsv, log, html, py, ps1, sh,
and the backups named like x.json.before_completion), and not from the vendored dependency folders (deps, qr_dependencies, __pycache__, *.dist-info). Layout under the destination:
  <BATCH>/<game packet>/...     a game packet of a BATCH_* folder
  <BATCH>/_batch/...            a file or a non-packet folder directly in a BATCH_* folder
  _not_in_a_batch/<folder>/...  a folder of Recording_QA that is not a BATCH_*
  _recording_qa_root/...        a file at the top of Recording_QA
  _battle_logs_root/...         a file at the top of Battle Logs (MEDIA_LOCATIONS.json, the review notes; they do not move with Recording_QA, they are copied as a backup)
MANIFEST.json lists every copied file (source path under Battle Logs, SHA-256, size). A re-run copies only files that are new or whose SHA-256 changed; a file whose source has gone stays in the
copy and is listed under source_missing (the copy is a backup: it is never pruned). The run refuses, before writing anything, when the copy would exceed --max-total-mb (default 200) and
says what is large; a single file above --max-file-mb (default 50) or a path too long for a Windows checkout is skipped and reported. Standard library only."""
import argparse, collections, hashlib, json, os, re, subprocess, sys

DEST = 'rl/results/battle_log_packets'
EXTS = ('.json', '.jsonl', '.txt', '.md', '.csv', '.tsv', '.log', '.html', '.py', '.ps1', '.sh')
BACKUP = re.compile(r'\.(json|jsonl|txt|md|csv|py|ps1|sh)\.(before_\w+|initial|bak|orig)$', re.I)
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tif', '.tiff', '.heic', '.ico')
VIDEO_EXT = ('.mp4', '.mov', '.mkv', '.avi', '.m4v', '.webm')
EXCLUDED_DIRS = {'__pycache__', 'site-packages', 'node_modules', '.git', 'deps', 'qr_dependencies', 'zxingcpp', 'cv2'}
EXCLUDED_SUFFIX = ('.dist-info', '.egg-info')
GAME_PACKET = re.compile(r'^\d{8}_\d{6,9}_iOS')
WINDOWS_PREFIX = len(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim') + 1      # the Windows checkout the repo lives in; a path over 260 characters breaks tools there
MAX_PATH = 255
REPARSE = 0x400
SCHEMA = 'battle-log-packets/manifest-v1'


class ToolError(SystemExit):
    def __init__(self, msg):
        super().__init__(f'refused: {msg}')


def wanted(name):
    low = name.lower()
    if low.endswith(IMAGE_EXT + VIDEO_EXT):
        return False
    return low.endswith(EXTS) or bool(BACKUP.search(low))


def excluded_dir(name):
    return name in EXCLUDED_DIRS or name.endswith(EXCLUDED_SUFFIX)


def to_local(p):
    m = re.match(r'^([A-Za-z]):[\\/]*(.*)$', p)
    if m and os.name != 'nt':
        return '/mnt/' + m.group(1).lower() + '/' + m.group(2).replace('\\', '/')
    return p


def find_source(given=None):
    cands = [given] if given else [os.environ.get('BATTLE_LOGS'), r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs', r'C:\Users\dacz8\BattleLogs']
    for c in cands:
        if c and os.path.isdir(to_local(c)):
            return os.path.abspath(to_local(c))
    raise ToolError('the Battle Logs folder was not found; give --source (tried ' + ', '.join(str(c) for c in cands if c) + ')')


def dest_rel(source_rel):
    """where a file of Battle Logs goes under the destination (source_rel: path under Battle Logs, with '/')"""
    parts = source_rel.split('/')
    if len(parts) == 1:
        return '_battle_logs_root/' + parts[0]
    if parts[0] != 'Recording_QA':
        raise ValueError(f'not under Battle Logs/Recording_QA: {source_rel}')
    rest = parts[1:]
    if len(rest) == 1:
        return '_recording_qa_root/' + rest[0]
    if not rest[0].startswith('BATCH_'):
        return '_not_in_a_batch/' + '/'.join(rest)
    batch, tail = rest[0], rest[1:]
    if len(tail) == 1:
        return f'{batch}/_batch/{tail[0]}'
    if GAME_PACKET.match(tail[0]):
        return f'{batch}/' + '/'.join(tail)
    return f'{batch}/_batch/' + '/'.join(tail)


def blob_sha1(data):
    """git's object id of a file's bytes"""
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


class Scan:
    def __init__(self):
        self.files = []                      # (source_rel, abs path, size)
        self.skipped = collections.Counter()  # reason -> count
        self.skipped_bytes = collections.Counter()
        self.skipped_examples = collections.defaultdict(list)

    def skip(self, why, size=0, example=None):
        self.skipped[why] += 1
        self.skipped_bytes[why] += size
        if example and len(self.skipped_examples[why]) < 5:
            self.skipped_examples[why].append(example)


def scan_source(source, include_root=True, only_qa=False):
    """every file under Battle Logs/Recording_QA (and, unless only_qa, the files at the top of Battle Logs) that is wanted; links and reparse points are not followed"""
    sc = Scan()
    qa = os.path.join(source, 'Recording_QA')
    tops = [] if only_qa or not include_root else [source]
    for top in tops:
        for e in sorted(os.scandir(top), key=lambda e: e.name):
            if e.is_file(follow_symlinks=False):
                if wanted(e.name):
                    sc.files.append((e.name, e.path, e.stat(follow_symlinks=False).st_size))
                else:
                    sc.skip('top of Battle Logs: ' + (os.path.splitext(e.name)[1].lower() or 'no extension'), e.stat(follow_symlinks=False).st_size)
    stack = [qa]
    while stack:
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            sc.skip('folder not readable', example=d)
            continue
        with it:
            for e in sorted(it, key=lambda e: e.name):
                try:
                    if e.is_symlink():
                        sc.skip('link', example=e.path)
                    elif e.is_dir(follow_symlinks=False):
                        if getattr(e.stat(follow_symlinks=False), 'st_file_attributes', 0) & REPARSE:
                            sc.skip('reparse point', example=e.path)
                        elif excluded_dir(e.name):
                            sc.skip('vendored or cache folder (' + e.name + ')', example=e.path)
                        else:
                            stack.append(e.path)
                    else:
                        st = e.stat(follow_symlinks=False)
                        rel = os.path.relpath(e.path, source).replace(os.sep, '/')
                        low = e.name.lower()
                        if getattr(st, 'st_file_attributes', 0) & REPARSE:
                            sc.skip('reparse point', example=rel)
                        elif low.endswith(IMAGE_EXT):
                            sc.skip('image', st.st_size)
                        elif low.endswith(VIDEO_EXT):
                            sc.skip('video', st.st_size)
                        elif wanted(e.name):
                            sc.files.append((rel, e.path, st.st_size))
                        else:
                            sc.skip('not a text output: ' + (os.path.splitext(low)[1] or 'no extension'), st.st_size)
                except OSError:
                    sc.skip('unreadable', example=e.path)
    return sc


def mb(n):
    return f'{n / 1048576:,.1f} MB'


def load_manifest(dest):
    p = os.path.join(dest, 'MANIFEST.json')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            m = json.load(f)
        if m.get('schema') != SCHEMA:
            raise ToolError(f'{p} is not a {SCHEMA}')
        return m
    return {'schema': SCHEMA, 'files': {}}


def large_report(items, p):
    by_batch = collections.Counter()
    by_ext = collections.Counter()
    for rel, _, size in items:
        d = dest_rel(rel)
        by_batch[d.split('/')[0]] += size
        by_ext[os.path.splitext(rel)[1].lower() or '(none)'] += size
    p('largest folders under the destination:')
    for k, v in by_batch.most_common(8):
        p(f'  {mb(v):>12}  {k}')
    p('by extension:')
    for k, v in by_ext.most_common(6):
        p(f'  {mb(v):>12}  {k}')
    p('largest files:')
    for rel, _, size in sorted(items, key=lambda x: -x[2])[:10]:
        p(f'  {mb(size):>12}  {rel}')


def run(source, repo, dest_dir=DEST, dry=False, max_total_mb=200, max_file_mb=50, out=None):
    """-> dict of counts. Writes nothing when dry or when it refuses."""
    out = out or sys.stdout
    p = lambda *a: print(*a, file=out)
    source, repo = os.path.abspath(source), os.path.abspath(repo)
    dest = os.path.join(repo, dest_dir)
    for a, b in ((dest, source), (source, dest)):
        try:
            if os.path.commonpath([a, b]) == b:
                raise ToolError('the destination and the source are inside one another')
        except ValueError:
            pass
    if not os.path.isdir(os.path.join(source, 'Recording_QA')):
        raise ToolError(f'{source} has no Recording_QA folder')
    sc = scan_source(source)
    manifest = load_manifest(dest)
    files = {}
    too_long, too_big = [], []
    for rel, ap, size in sc.files:
        d = dest_rel(rel)
        if WINDOWS_PREFIX + len(dest_dir) + 1 + len(d) > MAX_PATH:
            too_long.append(rel)
        elif size > max_file_mb * 1048576:
            too_big.append((rel, size))
        else:
            files[d] = (rel, ap, size)
    present = {d: e for d, e in manifest['files'].items() if d not in files}          # copied before, source gone (or now skipped): stays
    total = sum(s for _, _, s in files.values()) + sum(e['size'] for e in present.values())
    p(f'source: {source}')
    p(f'destination: {dest}')
    p(f'selected {len(files):,} text files, {mb(sum(s for _, _, s in files.values()))}; already in the copy with the source gone: {len(present):,} ({mb(sum(e["size"] for e in present.values()))})')
    for why, n in sorted(sc.skipped.items(), key=lambda x: -x[1]):
        p(f'  not copied: {n:>6,} x {why}' + (f' ({mb(sc.skipped_bytes[why])})' if sc.skipped_bytes[why] else ''))
    for rel in too_long[:5]:
        p(f'  skipped, path too long for a Windows checkout: {rel}')
    for rel, size in too_big:
        p(f'  skipped, larger than {max_file_mb} MB: {rel} ({mb(size)})')
    if total > max_total_mb * 1048576:
        p(f'REFUSED: the copy would be {mb(total)}, above the limit of {max_total_mb} MB. Nothing was written.')
        large_report([(r, a, s) for r, a, s in files.values()], p)
        raise ToolError(f'the copy would be {mb(total)}, above {max_total_mb} MB (see the list of what is large above)')
    new = changed = same = 0
    todo = []
    for d in sorted(files):
        rel, ap, size = files[d]
        with open(ap, 'rb') as f:
            data = f.read()
        sha = hashlib.sha256(data).hexdigest()
        old = manifest['files'].get(d)
        target = os.path.join(dest, d.replace('/', os.sep))
        on_disk_ok = False
        if old and old['sha256'] == sha and os.path.isfile(target):
            with open(target, 'rb') as f:
                on_disk_ok = hashlib.sha256(f.read()).hexdigest() == sha
        if on_disk_ok:
            same += 1
        else:
            if old:
                changed += 1
            else:
                new += 1
            todo.append((d, target, data))
        files[d] = (rel, ap, len(data), sha)      # the size of the bytes that were read and copied (a live file can grow between the scan and the read)
    missing = sorted(present)
    p(f'new {new:,}, changed {changed:,}, unchanged {same:,}; source gone but kept {len(missing):,}')
    if dry:
        p('dry run: nothing written')
        return {'new': new, 'changed': changed, 'same': same, 'missing': len(missing), 'files': len(files), 'bytes': total}
    for d, target, data in todo:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        tmp = target + '.part'
        with open(tmp, 'wb') as f:
            f.write(data)
        os.replace(tmp, target)
    entries = {d: {'source': v[0], 'sha256': v[3], 'size': v[2]} for d, v in files.items()}
    for d, e in present.items():
        entries[d] = dict(e, source_missing=True)
    new_manifest = {'schema': SCHEMA, 'source_root': 'Battle Logs (C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs)',
                    'selection': {'extensions': list(EXTS) + ['x.<ext>.before_*|initial|bak|orig'], 'excluded_folders': sorted(EXCLUDED_DIRS) + ['*' + s for s in EXCLUDED_SUFFIX], 'never': 'images, videos, binaries'},
                    'files': dict(sorted(entries.items()))}
    text = json.dumps(new_manifest, ensure_ascii=False, indent=1, sort_keys=False) + '\n'
    mp = os.path.join(dest, 'MANIFEST.json')
    os.makedirs(dest, exist_ok=True)
    old_text = None
    if os.path.exists(mp):
        with open(mp, encoding='utf-8') as f:
            old_text = f.read()
    if old_text != text:
        with open(mp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    ga = os.path.join(dest, '.gitattributes')
    if not os.path.exists(ga):
        with open(ga, 'w', encoding='utf-8', newline='\n') as f:
            f.write('# the copied packets are byte-for-byte: no end-of-line conversion on any machine\n* -text\n')
    p(f'wrote {len(todo):,} files' + (', MANIFEST.json updated' if old_text != text else ', MANIFEST.json unchanged'))
    return {'new': new, 'changed': changed, 'same': same, 'missing': len(missing), 'files': len(files), 'bytes': total}


# ---------------------------------------------------------------------------------------------------------------- is the copy current?
def committed_blobs(repo, ref, dest_dir=DEST):
    """{path under the destination: git blob id} of the files committed at ref (a git ref), or None when git cannot read the ref"""
    try:
        r = subprocess.run(['git', '-C', repo, 'ls-tree', '-r', '-z', ref, '--', dest_dir + '/'], capture_output=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    out = {}
    for line in r.stdout.decode('utf-8').split('\0'):
        if line:
            meta, path = line.split('\t', 1)
            out[path[len(dest_dir) + 1:]] = meta.split()[2]
    return out


def working_blobs(repo, dest_dir=DEST):
    out = {}
    base = os.path.join(repo, dest_dir)
    for root, _, files in os.walk(base):
        for f in files:
            fp = os.path.join(root, f)
            with open(fp, 'rb') as fh:
                out[os.path.relpath(fp, base).replace(os.sep, '/')] = blob_sha1(fh.read())
    return out


def import_problems(source, repo, ref='origin/main', no_git=False, dest_dir=DEST, max_file_mb=50):
    """what is NOT yet safely copied: every wanted file of Recording_QA must be in the destination, byte for byte (by git's blob id), committed at `ref`
    (or, with no_git, present in the working tree). -> list of problem lines; empty means the copy is current."""
    blobs = working_blobs(repo, dest_dir) if no_git else committed_blobs(repo, ref, dest_dir)
    if blobs is None:
        return [f'git cannot read {ref} in {repo}']
    sc = scan_source(os.path.abspath(source), only_qa=True)
    missing, changed, skipped_big = [], [], 0
    for rel, ap, size in sc.files:
        d = dest_rel(rel)
        if size > max_file_mb * 1048576 or WINDOWS_PREFIX + len(dest_dir) + 1 + len(d) > MAX_PATH:
            skipped_big += 1
            continue
        if d not in blobs:
            missing.append(rel)
            continue
        with open(ap, 'rb') as f:
            if blob_sha1(f.read()) != blobs[d]:
                changed.append(rel)
    where = 'in the working tree' if no_git else f'at {ref}'
    out = []
    if missing:
        out.append(f'{len(missing):,} text files of Recording_QA are not {where} (e.g. {", ".join(missing[:3])})')
    if changed:
        out.append(f'{len(changed):,} text files of Recording_QA differ from the copy {where} (e.g. {", ".join(changed[:3])})')
    if 'MANIFEST.json' not in blobs:
        out.append(f'MANIFEST.json is not {where}')
    return out


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--source', help='the Battle Logs folder (default C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs, or $BATTLE_LOGS)')
    ap.add_argument('--repo', default=os.path.abspath(os.path.join(here, '..')), help='the repository checkout (default: the one this script is in)')
    ap.add_argument('--dry-run', action='store_true', help='report only; write nothing')
    ap.add_argument('--check', action='store_true', help='is the copy current? exit 1 if not; with --ref: committed at that ref, byte for byte')
    ap.add_argument('--ref', help='with --check: the git ref the copy must be committed at (default: the working tree)')
    ap.add_argument('--max-total-mb', type=int, default=200)
    ap.add_argument('--max-file-mb', type=int, default=50)
    a = ap.parse_args(argv)
    source = find_source(a.source)
    if a.check:
        probs = import_problems(source, a.repo, a.ref or 'origin/main', no_git=not a.ref, max_file_mb=a.max_file_mb)
        for line in probs:
            print('NOT CURRENT: ' + line)
        print('the copy is current' + (f' and committed at {a.ref}' if a.ref else ' in the working tree (not checked against git)') if not probs else '')
        return 1 if probs else 0
    run(source, a.repo, dry=a.dry_run, max_total_mb=a.max_total_mb, max_file_mb=a.max_file_mb)
    return 0


if __name__ == '__main__':
    sys.exit(main())
