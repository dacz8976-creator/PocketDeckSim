#!/usr/bin/env python3
"""battle_logs_cleanup.py: free OneDrive space by deleting the video FRAMES (jpg/png) of Codex's batch packets whose results are safely in the repo.

  python3 tools/battle_logs_cleanup.py                      dry run (the default): a verdict line per BATCH_* folder (DELETE / PARTIAL / keep), nothing is changed
  python3 tools/battle_logs_cleanup.py --apply              delete the frames of the game packets that pass (asks you to type DELETE; --yes skips that)
  python3 tools/battle_logs_cleanup.py --move-to C:\\Users\\dacz8\\BattleLogs\\Recording_QA     move ONLY Recording_QA out of OneDrive; the videos stay (separate; asks you to type MOVE)

The rule, the safety rails and the reasons are in tools/README_battle_logs_cleanup.md. In short: a game packet's frames may go when (1) its game is in a games_meta.json committed
on main under rl/results/pause_games_*/ with positions in the positions_all.json next to it, (2) the game is in the committed audit list rl/results/battle_logs_retention_2026-10-14/
audited_games.json (a person's decision that the positions passed their review) and that list has been confirmed, and (3) the packet's text outputs (TURN_LEDGER.json, REVIEW.md,
DECK_USED.json) are in the folder. The game packet is the unit; a batch is DELETE when every packet in it passes, PARTIAL when some do (--whole-batches-only leaves those alone).
Only .jpg/.jpeg/.png files inside game packets that pass are ever deleted: never json/txt/md or any other file, never a video, never anything outside Recording_QA. Standard
library only; works with Windows paths from PowerShell and with Windows or /mnt/c paths from WSL."""
import argparse, collections, dataclasses, datetime, json, os, re, stat, subprocess, sys

FRAME_EXT = ('.jpg', '.jpeg', '.png')
GAME_PACKET = re.compile(r'^\d{8}_\d{6,9}_iOS')                 # 20261013_030351000_iOS (and 20261002_205230000_iOS_auto_sol)
TEXT_REQUIRED = ('TURN_LEDGER.json', 'REVIEW.md', 'DECK_USED.json')   # a packet's text outputs: they must be there, non-empty, before its frames go
META_PATH = re.compile(r'^rl/results/pause_games_[^/]+/(?:.+/)?games_meta\.json$')
AUDIT_LIST = 'rl/results/battle_logs_retention_2026-10-14/audited_games.json'
QA_CANDIDATES = [r'C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA', r'C:\Users\dacz8\BattleLogs\Recording_QA']
REPARSE = 0x400      # FILE_ATTRIBUTE_REPARSE_POINT (a Windows junction or OneDrive placeholder that is a link): never followed


class ToolError(SystemExit):
    def __init__(self, msg):
        super().__init__(f'refused: {msg}')


# ---------------------------------------------------------------------------------------------------------------- paths
def to_local(p):
    """a Windows drive path in WSL becomes /mnt/c/...; a /mnt/c path on Windows becomes C:\\..."""
    m = re.match(r'^([A-Za-z]):[\\/]*(.*)$', p)
    if m and os.name != 'nt':
        return '/mnt/' + m.group(1).lower() + '/' + m.group(2).replace('\\', '/')
    m = re.match(r'^/mnt/([a-z])(?:/(.*))?$', p)
    if m and os.name == 'nt':
        return m.group(1).upper() + ':\\' + (m.group(2) or '').replace('/', '\\')
    return p


def to_windows(p):
    """the path to tell Codex: Windows style when it is a /mnt/<drive> path"""
    m = re.match(r'^/mnt/([a-z])(?:/(.*))?$', p)
    return m.group(1).upper() + ':\\' + (m.group(2) or '').replace('/', '\\') if m else p


def find_qa_root(given=None):
    cands = [given] if given else [os.environ.get('BATTLE_LOGS_QA')] + QA_CANDIDATES
    for c in cands:
        if c and os.path.isdir(to_local(c)):
            return os.path.abspath(to_local(c))
    raise ToolError('Recording_QA not found; give --qa-root (tried ' + ', '.join(str(c) for c in cands if c) + ')')


def is_link(path):
    try:
        st = os.lstat(path)
    except OSError:
        return True
    return os.path.islink(path) or bool(getattr(st, 'st_file_attributes', 0) & REPARSE)


# ---------------------------------------------------------------------------------------------------------------- what is committed
class RepoView:
    """the committed files the rule reads: those of a git ref (default origin/main), or, with no_git, the working tree (NOT a proof that anything is committed)"""

    def __init__(self, repo, ref='origin/main', no_git=False):
        self.repo, self.ref, self.no_git = os.path.abspath(repo), ref, no_git
        if not no_git:
            try:
                r = self._git('rev-parse', '--short=8', '--verify', ref + '^{commit}')
            except (OSError, subprocess.CalledProcessError) as e:
                raise ToolError(f'git cannot read {ref} in {self.repo} ({e}); run it from WSL, fetch main, or pass --no-git (then the working tree is read and nothing is proved committed)')
            self.commit = r.strip()

    def _git(self, *args):
        return subprocess.run(['git', '-C', self.repo, *args], capture_output=True, text=True, check=True).stdout

    def describe(self):
        return f'working tree of {self.repo} (NOT checked against git)' if self.no_git else f'{self.ref} ({self.commit})'

    def ls(self, prefix):
        if self.no_git:
            out = []
            base = os.path.join(self.repo, prefix)
            for root, _, files in os.walk(base):
                out += [os.path.relpath(os.path.join(root, f), self.repo).replace(os.sep, '/') for f in files]
            return out
        return [l for l in self._git('ls-tree', '-r', '--name-only', self.ref, '--', prefix).split('\n') if l]

    def read(self, path):
        if self.no_git:
            p = os.path.join(self.repo, path)
            if not os.path.exists(p):
                return None
            with open(p, 'rb') as f:
                return f.read()
        try:
            return subprocess.run(['git', '-C', self.repo, 'show', f'{self.ref}:{path}'], capture_output=True, check=True).stdout
        except subprocess.CalledProcessError:
            return None


@dataclasses.dataclass
class RepoIndex:
    folders: dict          # 'BATCH_x/gamedir' -> (game key, games_meta path, number of positions)
    audit: dict            # the audit list's JSON, or {}
    audit_path_found: bool


def build_index(view):
    """folder -> game key for every game of a committed games_meta.json whose sibling positions_all.json holds positions for it"""
    folders = {}
    for path in sorted(p for p in view.ls('rl/results') if META_PATH.match(p)):
        meta = json.loads(view.read(path))
        raw = view.read(path.rsplit('/', 1)[0] + '/positions_all.json')
        counts = collections.Counter(p.get('game') for p in json.loads(raw)) if raw else collections.Counter()
        for key, v in meta.items():
            f = (v.get('folder') or '').replace('\\', '/')
            if f and counts.get(key):
                old = folders.get(f)
                if old is None or counts[key] > old[2]:
                    folders[f] = (key, path, counts[key])
    raw = view.read(AUDIT_LIST)
    return RepoIndex(folders, json.loads(raw) if raw else {}, raw is not None)


# ---------------------------------------------------------------------------------------------------------------- what is on disk
@dataclasses.dataclass
class Game:
    name: str
    path: str
    frames: list           # [(path, size)] every .jpg/.jpeg/.png under the packet (links not followed)
    text: dict             # TEXT_REQUIRED name -> present and non-empty
    links_skipped: int = 0


@dataclasses.dataclass
class Batch:
    name: str
    path: str
    games: list
    support_frames: int = 0       # frames in a sub-folder that is not a game packet (qr_support, ...): never touched
    support_bytes: int = 0
    root_frames: int = 0          # image files directly in the batch folder (LIVE_SAVE_SUMMARY.png ...): never touched
    root_bytes: int = 0


def scan_frames(path):
    """-> ([(path, size)] of every .jpg/.jpeg/.png under path, links and reparse points not followed), number of things skipped. One stat per file (the folder is on a slow mount)."""
    frames, skipped = [], 0
    stack = [path]
    while stack:
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            skipped += 1
            continue
        with it:
            for e in it:
                try:
                    if e.is_symlink():
                        skipped += 1
                    elif e.is_dir(follow_symlinks=False):
                        if getattr(e.stat(follow_symlinks=False), 'st_file_attributes', 0) & REPARSE:
                            skipped += 1
                        else:
                            stack.append(e.path)
                    elif e.name.lower().endswith(FRAME_EXT):
                        st = e.stat(follow_symlinks=False)
                        if getattr(st, 'st_file_attributes', 0) & REPARSE:
                            skipped += 1
                        else:
                            frames.append((e.path, st.st_size))
                except OSError:
                    skipped += 1
    return frames, skipped


def scan_qa(qa_root):
    batches = []
    for name in sorted(os.listdir(qa_root)):
        bp = os.path.join(qa_root, name)
        if not name.startswith('BATCH_') or not os.path.isdir(bp) or is_link(bp):
            continue
        b = Batch(name, bp, [])
        for child in sorted(os.listdir(bp)):
            cp = os.path.join(bp, child)
            if is_link(cp):
                continue
            if os.path.isdir(cp) and GAME_PACKET.match(child):
                frames, skipped = scan_frames(cp)
                text = {t: os.path.isfile(os.path.join(cp, t)) and os.path.getsize(os.path.join(cp, t)) > 0 for t in TEXT_REQUIRED}
                b.games.append(Game(child, cp, frames, text, skipped))
            elif os.path.isdir(cp):
                frames, _ = scan_frames(cp)
                b.support_frames += len(frames)
                b.support_bytes += sum(s for _, s in frames)
            elif child.lower().endswith(FRAME_EXT):
                b.root_frames += 1
                b.root_bytes += os.path.getsize(cp)
        batches.append(b)
    return batches


# ---------------------------------------------------------------------------------------------------------------- the rule
@dataclasses.dataclass
class GameDecision:
    game: Game
    key: object
    reasons: list          # why it cannot go; empty = its frames may be deleted

    @property
    def ok(self):
        return not self.reasons


@dataclasses.dataclass
class BatchDecision:
    """the roll-up of its game packets' decisions: DELETE (every packet passes), PARTIAL (some do), keep (none do, or there are none)"""
    batch: Batch
    games: list
    why: str

    @property
    def ok_games(self):
        return [g for g in self.games if g.ok]

    @property
    def delete(self):
        """the whole batch is deletable: it has game packets and every one of them passes"""
        return bool(self.games) and len(self.ok_games) == len(self.games)

    @property
    def verdict(self):
        return 'DELETE' if self.delete else ('PARTIAL' if self.ok_games else 'keep')

    @property
    def frames(self):
        """frames in the game packets that pass: what --apply would remove from this batch"""
        return sum(len(g.game.frames) for g in self.ok_games)

    @property
    def bytes(self):
        return sum(s for g in self.ok_games for _, s in g.game.frames)

    @property
    def kept_frames(self):
        return sum(len(g.game.frames) for g in self.games if not g.ok)

    @property
    def kept_bytes(self):
        return sum(s for g in self.games if not g.ok for _, s in g.game.frames)


def decide_game(batch_name, game, index):
    folder = f'{batch_name}/{game.name}'
    reasons = []
    hit = index.folders.get(folder)
    key = hit[0] if hit else None
    if not hit:
        reasons.append('not in the repo: no committed games_meta.json (with positions) names this folder')
    if not index.audit_path_found:
        reasons.append('the audit list is not committed (' + AUDIT_LIST + ')')
    elif hit:
        entry = (index.audit.get('games') or {}).get(key)
        if entry is None:
            pending = (index.audit.get('pending') or {}).get(key)
            reasons.append('not audited: ' + ('proposed, pending a decision (' + str(pending.get('why', 'no reason given')) + ')' if pending else 'not in the audit list'))
        elif (entry.get('folder') or '').replace('\\', '/') != folder:
            reasons.append(f'the audit list says {key} is in {entry.get("folder")}, not here')
    for t, ok in game.text.items():
        if not ok:
            reasons.append(f'text output {t} missing or empty')
    return GameDecision(game, key, reasons)


def decide(batches, index):
    out = []
    for b in batches:
        gd = [decide_game(b.name, g, index) for g in b.games]
        bad = [g for g in gd if not g.ok]
        if not gd:
            why = 'no game packets in it'
        elif not bad:
            why = f'all {len(gd)} game packets are in the repo, audited, and have their text outputs'
        else:
            counts = collections.Counter(r.split(':')[0] for g in bad for r in g.reasons)
            why = f'{len(bad)} of {len(gd)} game packets held back (' + '; '.join(f'{n} x {k}' for k, n in counts.most_common()) + ')'
        out.append(BatchDecision(b, gd, why))
    return out


def audit_confirmed(index):
    c = index.audit.get('confirmed')
    return c if isinstance(c, str) and c.strip() else None


# ---------------------------------------------------------------------------------------------------------------- report
def mb(n):
    return f'{n / 1048576:,.0f} MB' if n < 1 << 30 else f'{n / (1 << 30):,.2f} GB'


def report(decisions, view, qa_root, index, verbose=False, out=None):
    out = out or sys.stdout
    p = lambda *a: print(*a, file=out)
    p(f'Recording_QA: {qa_root}')
    p(f'Committed state read from: {view.describe()}')
    p(f'Games with positions in the repo: {len(index.folders)}; audit list: ' + ('found' if index.audit_path_found else 'NOT found') + '; confirmed: ' + (audit_confirmed(index) or 'NO (--apply will refuse)'))
    p('')
    p(f'{"batch":46} {"verdict":8} {"games":>7} {"to delete":>10} {"size":>9}   {"stays":>6} {"size":>9}  why')
    for d in decisions:
        p(f'{d.batch.name[:46]:46} {d.verdict:8} {len(d.ok_games):3d}/{len(d.games):<3d} {d.frames:10d} {mb(d.bytes):>9}   {d.kept_frames:6d} {mb(d.kept_bytes):>9}  {d.why}')
        for g in d.games:
            if g.reasons and (verbose or len(d.games) - len(d.ok_games) <= 8):
                p(f'      stays {g.game.name}: ' + '; '.join(g.reasons))
        extras = []
        if d.batch.support_frames:
            extras.append(f'{d.batch.support_frames} frames ({mb(d.batch.support_bytes)}) in non-game sub-folders')
        if d.batch.root_frames:
            extras.append(f'{d.batch.root_frames} image files ({mb(d.batch.root_bytes)}) at the batch level')
        if extras:
            p('      never touched: ' + '; '.join(extras))
    whole = [d for d in decisions if d.delete]
    part = [d for d in decisions if d.verdict == 'PARTIAL']
    p('')
    p(f'TO DELETE by --apply: {sum(d.frames for d in decisions):,} frames, {mb(sum(d.bytes for d in decisions))}, from {len(whole) + len(part)} batches ({len(whole)} whole, {len(part)} partial);'
      f' with --whole-batches-only: {sum(d.frames for d in whole):,} frames, {mb(sum(d.bytes for d in whole))} from the {len(whole)} whole batches')
    p(f'STAYS: {sum(d.kept_frames for d in decisions):,} frames, {mb(sum(d.kept_bytes for d in decisions))} in game packets that do not pass (and the sub-folder and batch-level images above)')
    p('Only .jpg/.jpeg/.png files inside the game packets that pass are removed by --apply; json/txt/md, videos and everything outside Recording_QA never are.')
    p('--move-to PATH (a separate step) moves ONLY Recording_QA (the frames and the packets) to PATH; the videos and the rest of Battle Logs stay where they are, in OneDrive.')
    others = [n for n in os.listdir(qa_root) if not n.startswith('BATCH_') and os.path.isdir(os.path.join(qa_root, n))]
    if others:
        nf = sum(len(scan_frames(os.path.join(qa_root, n))[0]) for n in others)
        p(f'Outside BATCH_* (not in scope, never touched): {len(others)} folders in Recording_QA holding {nf:,} image files.')


# ---------------------------------------------------------------------------------------------------------------- apply
def text_inventory(game_paths):
    """{path: size} of every non-frame file under the game packets: what must still be there after the deletion"""
    inv = {}
    for gp in game_paths:
        for root, _, files in os.walk(gp, followlinks=False):
            for f in files:
                if not f.lower().endswith(FRAME_EXT):
                    fp = os.path.join(root, f)
                    try:
                        inv[fp] = os.path.getsize(fp)
                    except OSError:
                        inv[fp] = -1
    return inv


def selected(decisions, only=None, whole_batches_only=False):
    """[(batch decision, [game decisions])] whose frames --apply would delete: the passing packets of every batch (of the DELETE batches only with whole_batches_only), or of the named batches"""
    out = []
    for d in decisions:
        if (only and d.batch.name not in only) or (whole_batches_only and not d.delete) or not d.ok_games:
            continue
        out.append((d, d.ok_games))
    return out


def deletion_plan(decisions, qa_root, only=None, whole_batches_only=False):
    """-> [(path, size)] of the frames to delete; every one is checked here again to be a frame file inside a game packet that passes, inside qa_root, not a link"""
    plan = []
    qa_real = os.path.realpath(qa_root)
    for d, games in selected(decisions, only, whole_batches_only):
        for g in games:
            gp = os.path.abspath(g.game.path)
            gp_real = os.path.realpath(gp)           # once per packet: the packet really is Recording_QA/<batch>/<packet>
            if os.path.relpath(gp_real, qa_real).split(os.sep) != [d.batch.name, g.game.name]:
                raise ToolError(f'{g.game.path} is not Recording_QA/{d.batch.name}/{g.game.name} under {qa_root}')
            for fp, size in g.game.frames:
                ap = os.path.abspath(fp)
                try:
                    st = os.lstat(ap)
                    ok = (fp.lower().endswith(FRAME_EXT) and ap.startswith(gp + os.sep) and '..' not in os.path.relpath(ap, gp).split(os.sep)
                          and stat.S_ISREG(st.st_mode) and not getattr(st, 'st_file_attributes', 0) & REPARSE)
                except OSError:
                    ok = False
                if not ok:
                    raise ToolError(f'{fp} is not a frame file inside a game packet that passes, under {qa_root}')
                plan.append((fp, size))
    return plan


def apply_deletions(decisions, qa_root, index, only=None, confirm=None, log_dir=None, out=None, now=None, whole_batches_only=False):
    """delete the planned frames; `confirm` is called with (n, bytes, batches) and must return True. Returns (deleted, failed, bytes, log path)."""
    out = out or sys.stdout
    if not audit_confirmed(index):
        raise ToolError('the audit list has no "confirmed" entry (a person records there that the positions of its games passed review); edit and commit it first')
    if only:
        unknown = [o for o in only if o not in {d.batch.name for d, _ in selected(decisions, None, whole_batches_only)}]
        if unknown:
            raise ToolError('--only names batches with nothing to delete (not marked DELETE or PARTIAL, or PARTIAL with --whole-batches-only): ' + ', '.join(unknown))
    plan = deletion_plan(decisions, qa_root, only, whole_batches_only)
    batches = sorted({os.path.relpath(fp, qa_root).split(os.sep)[0] for fp, _ in plan})
    if not plan:
        print('nothing to delete', file=out)
        return 0, 0, 0, None
    if confirm is not None and not confirm(len(plan), sum(s for _, s in plan), batches):
        raise ToolError('not confirmed; nothing deleted')
    games = sorted({g.game.path for d, gs in selected(decisions, only, whole_batches_only) for g in gs})
    before = text_inventory(games)
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')
    log_path = os.path.join(log_dir or qa_root, f'CLEANUP_LOG_{stamp}.jsonl')
    deleted = failed = freed = 0
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(json.dumps({'start': stamp, 'qa_root': qa_root, 'batches': batches, 'frames_planned': len(plan), 'audit_confirmed': audit_confirmed(index)}) + '\n')
        for fp, size in plan:
            try:
                os.remove(fp)
                deleted += 1
                freed += size
                log.write(json.dumps({'removed': os.path.relpath(fp, qa_root).replace(os.sep, '/'), 'bytes': size}) + '\n')
            except OSError as e:
                failed += 1
                log.write(json.dumps({'failed': os.path.relpath(fp, qa_root).replace(os.sep, '/'), 'error': str(e)}) + '\n')
        after = text_inventory(games)
        gone = sorted(set(before) - set(after))
        changed = sorted(p for p in before if p in after and before[p] != after[p])
        log.write(json.dumps({'done': True, 'deleted': deleted, 'failed': failed, 'bytes_freed': freed, 'non_frame_files_missing_after': gone, 'non_frame_files_changed': changed}) + '\n')
    print(f'deleted {deleted:,} frames ({mb(freed)}); {failed} failed; log: {log_path}', file=out)
    if gone or changed:
        raise ToolError(f'INTEGRITY CHECK FAILED: {len(gone)} non-frame files missing and {len(changed)} changed after the deletion; see {log_path}')
    print(f'integrity check: all {len(before):,} non-frame files of those packets are still there, unchanged', file=out)
    return deleted, failed, freed, log_path


# ---------------------------------------------------------------------------------------------------------------- move
def move_recording_qa(source, target, repo=None, confirm=None, dry=False, out=None, import_check=None):
    """move ONLY Recording_QA (the frames and the packets) to `target`; the videos and everything else in Battle Logs stay where they are, in OneDrive.
    A rename on the same drive: instant, nothing copied, nothing half-moved. Returns the new path (None for a dry run)."""
    out = out or sys.stdout
    source, target = os.path.abspath(to_local(source)), os.path.abspath(to_local(target))
    p = lambda *a: print(*a, file=out)
    if not os.path.isdir(source):
        raise ToolError(f'{source} is not a folder')
    if os.path.basename(source).lower() != 'recording_qa':
        raise ToolError(f'{source} is not a folder named Recording_QA; this tool moves only Recording_QA (never the videos or the rest of Battle Logs)')
    if os.path.lexists(target):
        raise ToolError(f'{target} already exists; choose a path that does not exist')
    try:
        if os.path.commonpath([source, target]) == source:
            raise ToolError('the target is inside Recording_QA')
    except ValueError:
        pass      # different drives on Windows: the same-drive check below refuses
    parent = os.path.dirname(target)
    make_parent = not os.path.isdir(parent)
    if make_parent and not os.path.isdir(os.path.dirname(parent)):
        raise ToolError(f'neither the target\'s parent {parent} nor the folder above it exists')
    anchor = os.path.dirname(parent) if make_parent else parent
    if os.stat(source).st_dev != os.stat(anchor).st_dev:
        raise ToolError('the target is on another drive: a move there is a copy of everything and is not done by this tool; use a path on the same drive')
    logs = os.path.dirname(source)
    p(f'move ONLY Recording_QA (the frames and the packets): {to_windows(source)}  ->  {to_windows(target)}')
    p('  a rename on the same drive: instant, nothing is copied' + (f'; the folder {to_windows(parent)} is created first' if make_parent else ''))
    siblings = sorted(os.listdir(logs))
    videos = [f for f in siblings if f.lower().endswith(('.mp4', '.mov', '.mkv')) and os.path.isfile(os.path.join(logs, f))]
    folders = [f for f in siblings if os.path.isdir(os.path.join(logs, f)) and os.path.join(logs, f) != source]
    p(f'  STAYS where it is, in OneDrive: everything else in {to_windows(logs)}: {len(videos)} video file{"" if len(videos) == 1 else "s"} at its top, the folders {", ".join(folders) or "(none)"}, and its files. The videos are not moved.')
    p('  OneDrive will see Recording_QA leave and remove it from the cloud, INCLUDING the packets\' text outputs (ledgers, reviews, deck files): they exist nowhere else (the repo holds only the positions derived from them), so back them up first or pause OneDrive.')
    if any(part.lower().startswith('onedrive') for part in to_windows(target).replace('/', '\\').split('\\')):
        p('  WARNING: the target is still inside a OneDrive folder, so this would not take Recording_QA out of OneDrive.')
    for line in stale_references(source, repo):
        p('  ' + line)
    if import_check is not None:
        # the text outputs are the permanent part and exist nowhere else: GitHub must hold them, byte for byte, before they leave OneDrive's cloud
        problems = import_check()
        if problems:
            for line in problems:
                p('  IMPORT NOT CURRENT: ' + line)
            if not dry:
                raise ToolError('the text outputs of Recording_QA are not all committed in rl/results/battle_log_packets yet: run tools/battle_logs_import_packets.py, commit it and integrate it into main, '
                                'then try again (--no-import-check skips this check, at your own risk)')
            p('  (a real move would be refused until the import is current)')
        else:
            p('  import check: every text output of Recording_QA is committed, byte for byte, in rl/results/battle_log_packets')
    if dry:
        p('dry run: nothing moved')
        return None
    if confirm is not None and not confirm():
        raise ToolError('not confirmed; nothing moved')
    created = False
    try:
        if make_parent:
            os.mkdir(parent)
            created = True
        os.rename(source, target)
    except OSError as e:
        if created:
            try:
                os.rmdir(parent)
            except OSError:
                pass
        raise ToolError(f'Recording_QA could not be moved ({e}); nothing was changed (close what has files open in it: Codex, OneDrive sync, Explorer)')
    p('moved.')
    p(f'Codex should now use as its Recording_QA: {to_windows(target)}')
    p(f'This tool finds it with --qa-root "{to_windows(target)}" or the BATTLE_LOGS_QA variable. The videos and the other files are still in {to_windows(logs)}.')
    return target


def stale_references(source, repo):
    """what will need the new path and is only listed, never edited: scripts and text at the top of Recording_QA and of each batch that name the old Battle Logs path or reach a file that stays
    behind (MEDIA_LOCATIONS.json), and the repo's files that name the OneDrive path"""
    logs = os.path.dirname(source)
    needles = [to_windows(logs).lower(), logs.lower(), 'onedrive\\desktop\\battle logs', 'onedrive/desktop/battle logs', 'media_locations.json']
    lines, hits = [], []
    where = [source] + [os.path.join(source, d) for d in sorted(os.listdir(source)) if d.startswith('BATCH_') and os.path.isdir(os.path.join(source, d))]
    for d in where:
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and f.lower().endswith(('.json', '.md', '.txt', '.csv', '.py', '.ps1')) and os.path.getsize(fp) < 20_000_000:
                try:
                    with open(fp, encoding='utf-8', errors='replace') as fh:
                        txt = fh.read().lower().replace('\\\\', '\\')
                except OSError:
                    continue
                n = sum(txt.count(x) for x in needles)
                if n:
                    hits.append((os.path.relpath(fp, source).replace(os.sep, '/'), n))
    if hits:
        lines.append(f'{len(hits)} files in Recording_QA name the Battle Logs path or MEDIA_LOCATIONS.json (not edited; Codex\'s scripts need the new path): ' + ', '.join(f'{f} ({n}x)' for f, n in hits[:12]) + (' ...' if len(hits) > 12 else ''))
    lines.append('scripts that find files by a path relative to Recording_QA (for example ..\\Reviewed or ..\\MEDIA_LOCATIONS.json) cannot be found by this check and will break')
    if repo and os.path.isdir(repo):
        try:
            r = subprocess.run(['git', '-C', repo, 'grep', '-l', '-i', '-e', 'onedrive.desktop.battle logs'], capture_output=True, text=True)
            files = [l for l in r.stdout.split('\n') if l]
            if files:
                lines.append(f'{len(files)} files in the repo name the OneDrive path (they stay valid as history; a new run needs the new path): e.g. ' + ', '.join(files[:4]))
        except OSError:
            pass
    return lines


# ---------------------------------------------------------------------------------------------------------------- command line
def default_repo():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true', help='the default: report only')
    ap.add_argument('--apply', action='store_true', help='delete the frames of the batches marked delete')
    ap.add_argument('--move-to', metavar='PATH', help='move ONLY Recording_QA (the frames and the packets) to PATH, which becomes the new Recording_QA folder; the videos and the rest of Battle Logs stay in OneDrive; refuses if PATH exists')
    ap.add_argument('--yes', action='store_true', help='do not ask for the typed confirmation of --apply / --move-to')
    ap.add_argument('--no-import-check', action='store_true', help='with --move-to: do not require the text outputs to be committed at --ref (rl/results/battle_log_packets); at your own risk')
    ap.add_argument('--only', action='append', metavar='BATCH', help='with --apply: only this batch (repeatable); it must have something to delete')
    ap.add_argument('--whole-batches-only', action='store_true', help='with --apply: only the batches marked DELETE (every game packet passes), nothing from a PARTIAL batch')
    ap.add_argument('--qa-root', help=r'Recording_QA (default: C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA, or $BATTLE_LOGS_QA)')
    ap.add_argument('--repo', default=default_repo(), help='the repository checkout (default: the one this script is in)')
    ap.add_argument('--ref', default='origin/main', help='the git ref whose committed files count as "in the repo" (default origin/main)')
    ap.add_argument('--no-git', action='store_true', help='read the working tree instead of git (proves nothing about what is committed)')
    ap.add_argument('--verbose', '-v', action='store_true', help='list the reasons for every held-back game')
    a = ap.parse_args(argv)
    if a.apply and a.move_to:
        raise ToolError('--apply and --move-to are separate: run one, then the other')
    qa_root = find_qa_root(a.qa_root)

    def typed(word, what):
        def ask(*args):
            if a.yes:
                return True
            if not sys.stdin.isatty():
                raise ToolError('no terminal to type the confirmation in; pass --yes after reading the dry run')
            return input(f'{what}\nType {word} to go ahead: ').strip() == word
        return ask

    if a.move_to:
        check = None
        if not a.no_import_check:
            import battle_logs_import_packets as imp
            logs = os.path.dirname(qa_root)
            check = lambda: imp.import_problems(logs, a.repo, a.ref, a.no_git)
        move_recording_qa(qa_root, a.move_to, repo=a.repo, dry=a.dry_run, confirm=typed('MOVE', f'About to move ONLY Recording_QA ({qa_root}); the videos stay in OneDrive'), import_check=check)
        return 0
    view = RepoView(a.repo, a.ref, a.no_git)
    index = build_index(view)
    decisions = decide(scan_qa(qa_root), index)
    report(decisions, view, qa_root, index, a.verbose)
    if a.apply and not a.dry_run:
        def confirm(n, size, batches):
            return typed('DELETE', f'About to delete {n:,} frame files ({mb(size)}) from {len(batches)} batches: {", ".join(batches)}')()
        apply_deletions(decisions, qa_root, index, only=set(a.only) if a.only else None, confirm=confirm, whole_batches_only=a.whole_batches_only)
    elif a.only:
        raise ToolError('--only is for --apply')
    return 0


if __name__ == '__main__':
    sys.exit(main())
