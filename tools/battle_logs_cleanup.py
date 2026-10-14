#!/usr/bin/env python3
"""battle_logs_cleanup.py: free OneDrive space by deleting the video FRAMES (jpg/png) of Codex's batch packets whose results are safely in the repo.

  wsl python3 tools/battle_logs_cleanup.py                      dry run (the default): a verdict line per BATCH_* folder (DELETE / PARTIAL / keep), nothing is changed
  wsl python3 tools/battle_logs_cleanup.py --apply              delete the frames of the game packets that pass (asks you to type DELETE; --yes skips that)
  wsl python3 tools/battle_logs_cleanup.py --move-to C:/Users/dacz8/BattleLogs/Recording_QA     move ONLY Recording_QA out of OneDrive; the videos stay (asks you to type MOVE)

Run it through wsl (it needs git, which Windows has not on its PATH) and give Windows paths with FORWARD slashes (C:/Users/...) or as /mnt/c/...: backslashes typed after `wsl` are eaten.
The rule, the safety rails and the reasons are in tools/README_battle_logs_cleanup.md. In short: a game packet's frames may go when (1) its game is in a games_meta.json committed
on origin/main under rl/results/pause_games_*/ with positions in the positions_all.json next to it, (2) the game is in the committed audit list rl/results/battle_logs_retention_2026-10-14/
audited_games.json under that same games_meta and position count, and the list carries an acceptance (who, when, and a hash of the games it accepted) that still matches, (3) the packet's text outputs
(TURN_LEDGER.json, REVIEW.md, DECK_USED.json) are in the folder and (4) its source video is in Battle Logs. A second game recorded inside a packet (game_02/) is never part of the first game's decision: its
frames stay. The game packet is the unit; a batch is DELETE when every packet in it passes, PARTIAL when some do (--whole-batches-only leaves those alone). --apply reads only the committed state of
origin/main (no --no-git, no other --ref without --allow-ref-other-than-origin-main). Only .jpg/.jpeg/.png files inside game packets that pass are ever deleted: never json/txt/md or any other file, never a
video, never anything outside Recording_QA. Standard library only."""
import argparse, collections, dataclasses, datetime, hashlib, json, os, re, signal, stat, subprocess, sys

FRAME_EXT = ('.jpg', '.jpeg', '.png')
GAME_PACKET = re.compile(r'^\d{8}_\d{6,9}_iOS')                 # 20261013_030351000_iOS (and 20261002_205230000_iOS_auto_sol)
TEXT_REQUIRED = ('TURN_LEDGER.json', 'REVIEW.md', 'DECK_USED.json')   # a packet's text outputs: they must be there, non-empty, before its frames go
META_PATH = re.compile(r'^rl/results/pause_games_[^/]+/(?:.+/)?games_meta\.json$')
AUDIT_LIST = 'rl/results/battle_logs_retention_2026-10-14/audited_games.json'
QA_CANDIDATES = ['C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA', 'C:/Users/dacz8/BattleLogs/Recording_QA']
NESTED_NAME = re.compile(r'(^|_)game_\d{2,}$', re.I)                 # game_02, ..._game_02: a second game recorded in the same video
SURROGATE_TAGS = (0xA000000C, 0xA0000003)                            # IO_REPARSE_TAG_SYMLINK, IO_REPARSE_TAG_MOUNT_POINT: links and junctions (OneDrive's own reparse points are not)
NEGATION = re.compile(r'^\s*(no|none|n/?a|nobody|pending|false|tbd|todo|not\b|un|never|wait|hold|-)', re.I)
DEFAULT_REF = 'origin/main'


class ToolError(SystemExit):
    def __init__(self, msg, code=None):
        super().__init__(f'refused: {msg}' if code is None else msg)
        if code is not None:
            self.code = code


class Interrupted(Exception):
    """a SIGHUP/SIGTERM during the deletion loop"""


# ---------------------------------------------------------------------------------------------------------------- paths
def to_local(p):
    """a Windows drive path in WSL becomes /mnt/c/...; a /mnt/c path on Windows becomes C:\\...; 'C:Usersx' (backslashes lost on the way through wsl) is refused"""
    if re.match(r'^[A-Za-z]:(?![\\/])', p) and len(p) > 2:
        raise ToolError(f'{p!r} looks like a Windows path that lost its backslashes on the way through `wsl`; write it with forward slashes (C:/Users/...) or as /mnt/c/...')
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


def to_forward(p):
    """the same path for typing after `wsl`: C:/Users/... (forward slashes survive)"""
    w = to_windows(p)
    return w.replace('\\', '/') if re.match(r'^[A-Za-z]:\\', w) else w


def find_qa_root(given=None):
    cands = [given] if given else QA_CANDIDATES
    for c in cands:
        if c:
            local = to_local(c)
            if os.path.isdir(local):
                return os.path.abspath(local)
    raise ToolError('Recording_QA not found; give --qa-root (tried ' + ', '.join(str(c) for c in cands if c) + ')')


def fold(p):
    """a path for comparing: NTFS (also under /mnt/c) is case-insensitive"""
    return os.path.normcase(os.path.abspath(p)).casefold()


def is_name_surrogate(st):
    """a symlink or a junction (not OneDrive's own reparse points, which every file in a synced folder carries)"""
    return stat.S_ISLNK(st.st_mode) or getattr(st, 'st_reparse_tag', 0) in SURROGATE_TAGS


def is_link(path):
    try:
        return is_name_surrogate(os.lstat(path))
    except OSError:
        return True


# ---------------------------------------------------------------------------------------------------------------- what is committed
class RepoView:
    """the committed files the rule reads: those of a git ref (default origin/main), resolved ONCE to a commit, or, with no_git, the working tree (NOT a proof that anything is committed)"""

    def __init__(self, repo, ref=DEFAULT_REF, no_git=False):
        self.repo, self.ref, self.no_git = os.path.abspath(repo), ref, no_git
        self.commit = self.commit_full = self.date = None
        if not no_git:
            try:
                self.commit_full = self._git('rev-parse', '--verify', ref + '^{commit}').strip()
                self.commit = self.commit_full[:8]
                self.date = self._git('show', '-s', '--format=%cI', self.commit_full).strip()
            except (OSError, subprocess.CalledProcessError) as e:
                raise ToolError(f'git cannot read {ref} in {self.repo} ({e}); run it through wsl from a checkout, and fetch main first')

    def _git(self, *args):
        return subprocess.run(['git', '-C', self.repo, *args], capture_output=True, text=True, check=True).stdout

    def describe(self):
        return f'working tree of {self.repo} (NOT checked against git)' if self.no_git else f'{self.ref} ({self.commit}, committed {self.date})'

    def ls(self, prefix):
        if self.no_git:
            out = []
            base = os.path.join(self.repo, prefix)
            for root, _, files in os.walk(base):
                out += [os.path.relpath(os.path.join(root, f), self.repo).replace(os.sep, '/') for f in files]
            return out
        return [l for l in self._git('ls-tree', '-r', '--name-only', self.commit_full, '--', prefix).split('\n') if l]

    def read(self, path):
        if self.no_git:
            p = os.path.join(self.repo, path)
            if not os.path.exists(p):
                return None
            with open(p, 'rb') as f:
                return f.read()
        try:
            return subprocess.run(['git', '-C', self.repo, 'show', f'{self.commit_full}:{path}'], capture_output=True, check=True).stdout
        except subprocess.CalledProcessError:
            return None

    def remote_main(self):
        """the sha origin has for main right now, or None when origin cannot be reached"""
        try:
            r = subprocess.run(['git', '-C', self.repo, 'ls-remote', 'origin', 'main'], capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return r.stdout.split()[0]


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


def games_hash(games):
    """a hash of what an acceptance covers: each audited game with the folder, the games_meta file and the number of positions that were reviewed"""
    canon = {k: [(e.get('folder') or '').replace('\\', '/'), e.get('games_meta'), e.get('positions')] for k, e in sorted((games or {}).items())}
    return hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def acceptance(index):
    """-> (the acceptance dict, None) when the audit list carries a valid one that still matches its games, else (None, why not).
    A valid acceptance is {"by": who, "date": "YYYY-MM-DD", "games_sha256": the hash of `games`}; 'no', 'pending' or any other string is not one, and a later edit to `games` needs a new one."""
    c = index.audit.get('confirmed')
    if not index.audit_path_found:
        return None, 'the audit list is not committed (' + AUDIT_LIST + ')'
    if c in (None, '', False):
        return None, 'the audit list has no acceptance yet ("confirmed" is empty)'
    if not isinstance(c, dict):
        return None, '"confirmed" must be {"by": ..., "date": "YYYY-MM-DD", "games_sha256": ...}; a string such as "no", "pending" or a name is not an acceptance'
    by, date, h = c.get('by'), c.get('date'), c.get('games_sha256')
    if not isinstance(by, str) or len(by.strip()) < 2 or NEGATION.match(by):
        return None, '"confirmed.by" must name who accepted the list'
    try:
        datetime.date.fromisoformat(str(date))
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(date)):
            raise ValueError
    except ValueError:
        return None, '"confirmed.date" must be a date as YYYY-MM-DD'
    want = games_hash(index.audit.get('games'))
    if h != want:
        return None, f'the acceptance covers games_sha256 {str(h)[:12]}..., the list now hashes to {want[:12]}...: the games changed after it was given, so it needs a new acceptance (python3 tools/battle_logs_cleanup.py --audit-hash prints the hash)'
    return c, None


# ---------------------------------------------------------------------------------------------------------------- what is on disk
@dataclasses.dataclass
class Game:
    name: str
    path: str
    frames: list           # [(path, size)] the frames of THIS game: every .jpg/.jpeg/.png under the packet (links not followed) except those of a second game recorded inside it
    text: dict             # TEXT_REQUIRED name -> present and non-empty
    nested: dict = dataclasses.field(default_factory=dict)       # relative folder of a second game inside the packet -> [(path, size)]: never deleted
    links_skipped: int = 0
    unreadable: int = 0
    video: object = None   # None = not checked, else (ok, reason)


@dataclasses.dataclass
class Batch:
    name: str
    path: str
    games: list
    support_frames: int = 0       # frames in a sub-folder that is not a game packet (qr_support, ...): never touched
    support_bytes: int = 0
    root_frames: int = 0          # image files directly in the batch folder (LIVE_SAVE_SUMMARY.png ...): never touched
    root_bytes: int = 0
    skipped: int = 0              # links and entries that could not be read in the support folders


def _json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def scan_frames(path, skip_dirs=()):
    """-> ([(path, size)] of every .jpg/.jpeg/.png under path, links and junctions not followed, the folders in skip_dirs (absolute) not entered), links skipped, entries that could not be read.
    One stat per file (the folder is on a slow mount)."""
    frames, links, bad = [], 0, 0
    skip = {os.path.abspath(s) for s in skip_dirs}
    stack = [path]
    while stack:
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            bad += 1
            continue
        with it:
            for e in it:
                try:
                    if e.is_symlink():                                   # also how WSL shows a Windows junction
                        links += 1
                    elif e.is_dir(follow_symlinks=False):
                        if os.name == 'nt' and is_name_surrogate(e.stat(follow_symlinks=False)):      # a junction under native Windows Python
                            links += 1
                        elif os.path.abspath(e.path) not in skip:
                            stack.append(e.path)
                    elif e.name.lower().endswith(FRAME_EXT):
                        st = e.stat(follow_symlinks=False)
                        if is_name_surrogate(st):
                            links += 1
                        else:
                            frames.append((e.path, st.st_size))
                except OSError:
                    bad += 1
    return frames, links, bad


def nested_game_dirs(packet):
    """folders inside a game packet that hold a SECOND game of the same recording: those Codex's RELATED_GAME_PACKETS.json lists with a path other than '.', those named game_NN, and those with
    their own TURN_LEDGER.json and a SUMMARY.json whose game_id differs from the packet's. A backup copy of the same game (original_before_*, ...) has the same game_id and is not one."""
    found = set()
    rel = _json(os.path.join(packet, 'RELATED_GAME_PACKETS.json')) or {}
    for g in rel.get('game_packets') or []:
        p = (g.get('path') or '.').replace('\\', '/').strip('/')
        if p not in ('', '.'):
            found.add(os.path.abspath(os.path.join(packet, *p.split('/'))))
    own = (_json(os.path.join(packet, 'SUMMARY.json')) or {}).get('game_id')
    for root, dirs, files in os.walk(packet, followlinks=False):
        if os.path.abspath(root) == os.path.abspath(packet):
            continue
        if NESTED_NAME.search(os.path.basename(root)):
            found.add(os.path.abspath(root))
        elif 'TURN_LEDGER.json' in files and own:
            gid = (_json(os.path.join(root, 'SUMMARY.json')) or {}).get('game_id')
            if gid and gid != own:
                found.add(os.path.abspath(root))
    # a nested folder inside another nested folder belongs to the outer one
    return sorted(f for f in found if not any(f != o and f.startswith(o + os.sep) for o in found))


def scan_packet(name, cp):
    nested = nested_game_dirs(cp)
    frames, links, bad = scan_frames(cp, skip_dirs=nested)
    nf = {}
    for n in nested:
        nfr, l2, b2 = scan_frames(n)
        nf[os.path.relpath(n, cp).replace(os.sep, '/')] = nfr
        links += l2
        bad += b2
    text = {}
    for t in TEXT_REQUIRED:
        fp = os.path.join(cp, t)
        try:
            text[t] = os.path.isfile(fp) and os.path.getsize(fp) > 0
        except OSError:
            text[t] = False
    return Game(name, cp, frames, text, nf, links, bad)


def video_index(logs_root):
    """{lower-case file name: size} of the video files at the top of Battle Logs and in Battle Logs/Reviewed"""
    out = {}
    for d in (logs_root, os.path.join(logs_root, 'Reviewed')):
        try:
            for e in os.scandir(d):
                if e.is_file() and e.name.lower().endswith(('.mp4', '.mov', '.mkv', '.m4v')):
                    out[e.name.lower()] = e.stat().st_size
        except OSError:
            pass
    return out


def check_video(game, videos):
    """-> (ok, reason): the packet's SOURCE.json names a video that is in Battle Logs with the recorded size (frames can be cut again from it)"""
    src = _json(os.path.join(game.path, 'SOURCE.json')) or {}
    name = src.get('video_basename')
    if not name:
        return False, 'source video not recorded (SOURCE.json has no video_basename)'
    size = videos.get(str(name).lower())
    if size is None:
        return False, f'source video {name} not found in Battle Logs'
    if src.get('bytes') and int(src['bytes']) != size:
        return False, f'source video {name} has {size} bytes, SOURCE.json says {src["bytes"]}'
    return True, ''


def scan_qa(qa_root, videos=None):
    batches = []
    for name in sorted(os.listdir(qa_root)):
        bp = os.path.join(qa_root, name)
        if not name.startswith('BATCH_') or not os.path.isdir(bp) or is_link(bp):
            continue
        b = Batch(name, bp, [])
        for child in sorted(os.listdir(bp)):
            cp = os.path.join(bp, child)
            if is_link(cp):
                b.skipped += 1
                continue
            if os.path.isdir(cp) and GAME_PACKET.match(child):
                g = scan_packet(child, cp)
                if videos is not None:
                    g.video = check_video(g, videos)
                b.games.append(g)
            elif os.path.isdir(cp):
                frames, links, bad = scan_frames(cp)
                b.support_frames += len(frames)
                b.support_bytes += sum(s for _, s in frames)
                b.skipped += links + bad
            elif child.lower().endswith(FRAME_EXT):
                b.root_frames += 1
                try:
                    b.root_bytes += os.path.getsize(cp)
                except OSError:
                    b.skipped += 1
        batches.append(b)
    return batches


# ---------------------------------------------------------------------------------------------------------------- the rule
@dataclasses.dataclass
class GameDecision:
    game: Game
    key: object
    reasons: list          # why it cannot go; empty = its frames may be deleted
    folder: str = ''
    meta: object = None
    positions: int = 0

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
        """frames that stay: those of packets that do not pass, and of second games inside packets that do"""
        return sum(len(g.game.frames) for g in self.games if not g.ok) + sum(len(f) for g in self.games for f in g.game.nested.values())

    @property
    def kept_bytes(self):
        return sum(s for g in self.games if not g.ok for _, s in g.game.frames) + sum(s for g in self.games for f in g.game.nested.values() for _, s in f)


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
        elif entry.get('games_meta') != hit[1] or entry.get('positions') != hit[2]:
            reasons.append(f'not audited as it is now: the audit list reviewed {entry.get("positions")} positions in {entry.get("games_meta")}, the repo now has {hit[2]} in {hit[1]}')
    for t, ok in game.text.items():
        if not ok:
            reasons.append(f'text output {t} missing or empty')
    if game.video is not None and not game.video[0]:
        reasons.append(game.video[1])
    if game.unreadable:
        reasons.append(f'{game.unreadable} entries in the packet could not be read')
    return GameDecision(game, key, reasons, folder, hit[1] if hit else None, hit[2] if hit else 0)


def decide(batches, index):
    out = []
    for b in batches:
        gd = [decide_game(b.name, g, index) for g in b.games]
        bad = [g for g in gd if not g.ok]
        if not gd:
            why = 'no game packets in it'
        elif not bad:
            why = f'all {len(gd)} game packets are in the repo, audited, have their text outputs and their source video'
        else:
            counts = collections.Counter(r.split(':')[0].split(' (')[0] for g in bad for r in g.reasons)
            why = f'{len(bad)} of {len(gd)} game packets held back (' + '; '.join(f'{n} x {k}' for k, n in counts.most_common()) + ')'
        out.append(BatchDecision(b, gd, why))
    return out


def filter_batches(decisions, only):
    if not only:
        return decisions
    names = {d.batch.name for d in decisions}
    unknown = sorted(set(only) - names)
    if unknown:
        raise ToolError('--only names batches that do not exist: ' + ', '.join(unknown))
    return [d for d in decisions if d.batch.name in only]


# ---------------------------------------------------------------------------------------------------------------- report
def mb(n):
    return f'{n / 1048576:,.0f} MB' if n < 1 << 30 else f'{n / (1 << 30):,.2f} GB'


def report(decisions, view, qa_root, index, verbose=False, out=None):
    out = out or sys.stdout
    p = lambda *a: print(*a, file=out)
    p(f'Recording_QA: {qa_root}')
    p(f'Committed state read from: {view.describe()}')
    acc, why = acceptance(index)
    p(f'Games with positions in the repo: {len(index.folders)}; audit list: ' + ('found' if index.audit_path_found else 'NOT found') + '; acceptance: '
      + (f'{acc["by"]}, {acc["date"]}' if acc else f'NO ({why}) -- --apply will refuse'))
    p('')
    p(f'{"batch":46} {"verdict":8} {"games":>7} {"to delete":>10} {"size":>9}   {"stays":>6} {"size":>9}  why')
    for d in decisions:
        p(f'{d.batch.name[:46]:46} {d.verdict:8} {len(d.ok_games):3d}/{len(d.games):<3d} {d.frames:10d} {mb(d.bytes):>9}   {d.kept_frames:6d} {mb(d.kept_bytes):>9}  {d.why}')
        for g in d.games:
            if g.reasons and (verbose or len(d.games) - len(d.ok_games) <= 8):
                p(f'      stays {g.game.name}: ' + '; '.join(g.reasons))
            for rel, fr in g.game.nested.items():
                p(f'      stays {g.game.name}/{rel}: a second game recorded in the same packet, not part of this decision: {len(fr)} frames, {mb(sum(s for _, s in fr))}')
        extras = []
        if d.batch.support_frames:
            extras.append(f'{d.batch.support_frames} frames ({mb(d.batch.support_bytes)}) in non-game sub-folders')
        if d.batch.root_frames:
            extras.append(f'{d.batch.root_frames} image files ({mb(d.batch.root_bytes)}) at the batch level')
        skipped = d.batch.skipped + sum(g.game.links_skipped + g.game.unreadable for g in d.games)
        if skipped:
            extras.append(f'{skipped} links or unreadable entries NOT examined')
        if extras:
            p('      never touched: ' + '; '.join(extras))
    whole = [d for d in decisions if d.delete]
    part = [d for d in decisions if d.verdict == 'PARTIAL']
    p('')
    p(f'TO DELETE by --apply: {sum(d.frames for d in decisions):,} frames, {mb(sum(d.bytes for d in decisions))}, from {len(whole) + len(part)} batches ({len(whole)} whole, {len(part)} partial);'
      f' with --whole-batches-only: {sum(d.frames for d in whole):,} frames, {mb(sum(d.bytes for d in whole))} from the {len(whole)} whole batches')
    p(f'STAYS: {sum(d.kept_frames for d in decisions):,} frames, {mb(sum(d.kept_bytes for d in decisions))} in game packets that do not pass or in second games inside packets (and the sub-folder and batch-level images above)')
    p('Only .jpg/.jpeg/.png files inside the game packets that pass are removed by --apply; json/txt/md, videos and everything outside Recording_QA never are.')
    p('--move-to PATH (a separate step) moves ONLY Recording_QA (the frames and the packets) to PATH; the videos and the rest of Battle Logs stay where they are, in OneDrive.')
    others = [n for n in os.listdir(qa_root) if not n.startswith('BATCH_') and os.path.isdir(os.path.join(qa_root, n))]
    if others:
        nf = sum(len(scan_frames(os.path.join(qa_root, n))[0]) for n in others)
        p(f'Outside BATCH_* (not in scope, never touched): {len(others)} folders in Recording_QA holding {nf:,} image files.')


# ---------------------------------------------------------------------------------------------------------------- apply
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def text_inventory(game_paths):
    """{path: sha256} of every non-frame file under the game packets: what must still be there, unchanged, after the deletion"""
    inv = {}
    for gp in game_paths:
        for root, _, files in os.walk(gp, followlinks=False):
            for f in files:
                if not f.lower().endswith(FRAME_EXT):
                    fp = os.path.join(root, f)
                    try:
                        inv[fp] = sha256_of(fp)
                    except OSError:
                        inv[fp] = 'unreadable'
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
    """-> [(game decision, [(path, size)])] per passing packet; every frame is checked here to be a frame file inside that packet (not in a second game's folder), inside qa_root, not a link"""
    plan = []
    qa_real = os.path.realpath(qa_root)
    for d, games in selected(decisions, only, whole_batches_only):
        for g in games:
            gp = os.path.abspath(g.game.path)
            gp_real = os.path.realpath(gp)           # once per packet: the packet really is Recording_QA/<batch>/<packet>
            if os.path.relpath(gp_real, qa_real).split(os.sep) != [d.batch.name, g.game.name]:
                raise ToolError(f'{g.game.path} is not Recording_QA/{d.batch.name}/{g.game.name} under {qa_root}')
            nested = [os.path.abspath(os.path.join(gp, *r.split('/'))) for r in g.game.nested]
            frames = []
            for fp, size in g.game.frames:
                ap = os.path.abspath(fp)
                try:
                    st = os.lstat(ap)
                    ok = (fp.lower().endswith(FRAME_EXT) and ap.startswith(gp + os.sep) and '..' not in os.path.relpath(ap, gp).split(os.sep)
                          and not any(ap.startswith(n + os.sep) for n in nested) and stat.S_ISREG(st.st_mode) and not is_name_surrogate(st))
                except OSError:
                    ok = False
                if not ok:
                    raise ToolError(f'{fp} is not a frame file inside a game packet that passes, under {qa_root}')
                frames.append((fp, size))
            plan.append((g, frames))
    return plan


class _Signals:
    """turn SIGHUP/SIGTERM into an exception while frames are being deleted, so the log is closed and says what happened"""

    def __init__(self, enable=True):
        self.enable = enable and hasattr(signal, 'SIGTERM')
        self.old = {}

    def __enter__(self):
        if self.enable:
            def handler(signum, frame):
                raise Interrupted(signal.Signals(signum).name)
            for s in (getattr(signal, 'SIGHUP', None), signal.SIGTERM):
                if s is not None:
                    try:
                        self.old[s] = signal.signal(s, handler)
                    except ValueError:      # not the main thread
                        pass
        return self

    def __exit__(self, *a):
        for s, h in self.old.items():
            signal.signal(s, h)


def apply_deletions(decisions, qa_root, index, view=None, only=None, confirm=None, log_dir=None, out=None, now=None, whole_batches_only=False, progress_every=1000, handle_signals=True):
    """delete the planned frames; `confirm` is called with (n, bytes, batches) and must return True. Returns (deleted, failed, bytes freed, log path)."""
    out = out or sys.stdout
    acc, why = acceptance(index)
    if not acc:
        raise ToolError(why)
    if only:
        unknown = [o for o in only if o not in {d.batch.name for d, _ in selected(decisions, None, whole_batches_only)}]
        if unknown:
            raise ToolError('--only names batches with nothing to delete (not marked DELETE or PARTIAL, or PARTIAL with --whole-batches-only): ' + ', '.join(unknown))
    plan = deletion_plan(decisions, qa_root, only, whole_batches_only)
    nplanned = sum(len(f) for _, f in plan)
    batches = sorted({os.path.relpath(g.game.path, qa_root).split(os.sep)[0] for g, _ in plan})
    if not nplanned:
        print('nothing to delete', file=out)
        return 0, 0, 0, None
    games = sorted({g.game.path for g, _ in plan})
    print(f'reading the {len(games)} packets\' text outputs for the integrity check ...', file=out)
    before = text_inventory(games)           # taken now, before the question, with a hash of each file
    if confirm is not None and not confirm(nplanned, sum(s for _, fr in plan for _, s in fr), batches):
        raise ToolError('not confirmed; nothing deleted')
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')
    log_path = os.path.join(log_dir or qa_root, f'CLEANUP_LOG_{stamp}.jsonl')
    deleted = failed = freed = skipped_packets = 0
    state = 'done'
    realdirs = {}
    with open(log_path, 'w', encoding='utf-8', buffering=1, newline='\n') as log:
        def put(obj, sync=False):
            log.write(json.dumps(obj, ensure_ascii=False) + '\n')
            if sync:
                log.flush()
                os.fsync(log.fileno())
        put({'start': stamp, 'qa_root': qa_root, 'committed_state': view.describe() if view else None, 'commit': getattr(view, 'commit_full', None),
             'acceptance': acc, 'batches': batches, 'frames_planned': nplanned,
             'packets': [{'folder': g.folder, 'key': g.key, 'games_meta': g.meta, 'positions': g.positions, 'frames': len(f)} for g, f in plan]}, sync=True)
        try:
            with _Signals(handle_signals):
                for g, frames in plan:
                    packet_real = os.path.realpath(g.game.path)
                    missing = [t for t in TEXT_REQUIRED if not (os.path.isfile(os.path.join(g.game.path, t)) and os.path.getsize(os.path.join(g.game.path, t)) > 0)]
                    if missing:
                        skipped_packets += 1
                        put({'skipped_packet': g.folder, 'reason': 'text outputs missing just before deletion: ' + ', '.join(missing)}, sync=True)
                        print(f'SKIPPED {g.folder}: {", ".join(missing)} missing just before deletion', file=out)
                        continue
                    for fp, size in frames:
                        d = os.path.dirname(fp)
                        if d not in realdirs:
                            realdirs[d] = os.path.realpath(d)
                        try:
                            st = os.lstat(fp)
                            safe = (realdirs[d] == packet_real or realdirs[d].startswith(packet_real + os.sep)) and stat.S_ISREG(st.st_mode) and not is_name_surrogate(st)
                        except OSError:
                            safe = False
                        rel = os.path.relpath(fp, qa_root).replace(os.sep, '/')
                        if not safe:
                            failed += 1
                            put({'failed': rel, 'error': 'not a regular file inside its packet at the moment of deletion; left alone'})
                            continue
                        try:
                            os.remove(fp)
                        except OSError as e:
                            failed += 1
                            put({'failed': rel, 'error': str(e)})
                            continue
                        deleted += 1
                        freed += size
                        put({'removed': rel, 'bytes': size})
                        if progress_every and deleted % progress_every == 0:
                            log.flush()
                            os.fsync(log.fileno())
                            print(f'  removed {deleted:,} of {nplanned:,} ...', file=out)
        except (Interrupted, KeyboardInterrupt) as e:
            state = 'interrupted'
            put({'interrupted': str(e) or 'KeyboardInterrupt', 'deleted': deleted, 'failed': failed, 'bytes_freed': freed}, sync=True)
            print(f'interrupted ({e or "Ctrl-C"}): {deleted:,} frames deleted, integrity check not run; the log is {log_path}. Run --apply again to finish.', file=out)
            raise ToolError(f'interrupted after {deleted} deletions; integrity check not run; run --apply again to finish', code=130)
        after = text_inventory(games)
        gone = sorted(set(before) - set(after))
        changed = sorted(p for p in before if p in after and before[p] != after[p])
        put({'done': True, 'deleted': deleted, 'failed': failed, 'skipped_packets': skipped_packets, 'bytes_freed': freed,
             'non_frame_files_missing_after': gone, 'non_frame_files_changed': changed}, sync=True)
    print(f'deleted {deleted:,} frames ({mb(freed)}); {failed} failed; {skipped_packets} packets skipped; log: {log_path}', file=out)
    if gone or changed:
        raise ToolError(f'INTEGRITY CHECK FAILED: {len(gone)} non-frame files missing and {len(changed)} changed since the inventory taken before the question (this tool deletes only frame files, so something else touched them, or the tool is wrong); see {log_path}')
    print(f'integrity check: all {len(before):,} non-frame files of those packets are still there, with the same SHA-256', file=out)
    if failed or skipped_packets:
        print(f'INCOMPLETE: {failed} frames could not be deleted and {skipped_packets} packets were skipped; close OneDrive/Codex/Explorer if they hold files open, then run --apply again.', file=out)
    return deleted, failed, freed, log_path


# ---------------------------------------------------------------------------------------------------------------- move
def is_drive_root(p):
    return bool(re.fullmatch(r'/mnt/[a-z]/?', p)) or bool(re.fullmatch(r'[A-Za-z]:[\\/]?', p)) or p in ('/', '')


def move_recording_qa(source, target, repo=None, confirm=None, dry=False, out=None, import_check=None):
    """move ONLY Recording_QA (the frames and the packets) to `target`; the videos and everything else in Battle Logs stay where they are, in OneDrive.
    A rename on the same drive: instant, nothing copied, nothing half-moved. Returns the new path (None for a dry run)."""
    out = out or sys.stdout
    given_target = target
    source, target = os.path.abspath(to_local(source)), to_local(target)
    p = lambda *a: print(*a, file=out)
    if not os.path.isabs(target):
        raise ToolError(f'the target {given_target!r} is not an absolute path')
    target = os.path.abspath(target)
    if not os.path.isdir(source):
        raise ToolError(f'{source} is not a folder')
    if os.path.basename(source).lower() != 'recording_qa':
        raise ToolError(f'{source} is not a folder named Recording_QA; this tool moves only Recording_QA (never the videos or the rest of Battle Logs)')
    if os.path.lexists(target):
        raise ToolError(f'{target} already exists; choose a path that does not exist')
    if fold(target) == fold(source) or fold(target).startswith(fold(source) + os.sep):
        raise ToolError('the target is the same folder as Recording_QA or inside it')
    parent = os.path.dirname(target)
    if is_drive_root(parent):
        raise ToolError(f'the target {target} would sit directly in the root of a drive ({parent}); that is what a path with lost backslashes looks like. Choose a folder, for example C:/Users/dacz8/BattleLogs/Recording_QA')
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
    folders = [f for f in siblings if os.path.isdir(os.path.join(logs, f)) and fold(os.path.join(logs, f)) != fold(source)]
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
    if confirm is not None and not confirm(to_windows(target)):
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
    p(f'This tool finds it with --qa-root {to_forward(target)}. The videos and the other files are still in {to_windows(logs)}.')
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
    ap.add_argument('--dry-run', action='store_true', help='the default: report only (also with --apply: preview what it would do)')
    ap.add_argument('--apply', action='store_true', help='delete the frames of the game packets that pass')
    ap.add_argument('--move-to', metavar='PATH', help='move ONLY Recording_QA (the frames and the packets) to PATH, which becomes the new Recording_QA folder; the videos and the rest of Battle Logs stay in OneDrive; refuses if PATH exists. Write PATH with forward slashes (C:/Users/...) or as /mnt/c/...')
    ap.add_argument('--yes', action='store_true', help='do not ask for the typed confirmation of --apply / --move-to')
    ap.add_argument('--only', action='append', metavar='BATCH', help='only this batch (repeatable): the report shows just those, and --apply deletes just those; it must have something to delete')
    ap.add_argument('--whole-batches-only', action='store_true', help='with --apply: only the batches marked DELETE (every game packet passes), nothing from a PARTIAL batch')
    ap.add_argument('--no-import-check', action='store_true', help='with --move-to: do not require the text outputs to be committed at --ref (rl/results/battle_log_packets); at your own risk')
    ap.add_argument('--qa-root', help='Recording_QA (default: C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA)')
    ap.add_argument('--repo', default=default_repo(), help='the repository checkout (default: the one this script is in)')
    ap.add_argument('--ref', default=DEFAULT_REF, help='the git ref whose committed files count as "in the repo" (default origin/main; --apply accepts only origin/main)')
    ap.add_argument('--allow-ref-other-than-origin-main', action='store_true', help='with --apply: accept another --ref (for example a branch under review); at your own risk')
    ap.add_argument('--no-git', action='store_true', help='read the working tree instead of git (previews only: proves nothing about what is committed; --apply refuses it)')
    ap.add_argument('--audit-hash', action='store_true', help='print the games_sha256 an acceptance in the audit list must carry for the games listed now, and exit')
    ap.add_argument('--verbose', '-v', action='store_true', help='list the reasons for every held-back game')
    a = ap.parse_args(argv)
    if a.apply and a.move_to:
        raise ToolError('--apply and --move-to are separate: run one, then the other')
    if a.apply and not a.dry_run:
        if a.no_git:
            raise ToolError('--apply reads only the committed state of origin/main; --no-git reads whatever is in the working tree. Run it through wsl, which has git')
        if a.ref != DEFAULT_REF and not a.allow_ref_other_than_origin_main:
            raise ToolError(f'--apply reads only the committed state of {DEFAULT_REF}, not {a.ref}; --allow-ref-other-than-origin-main overrides this, at your own risk')
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

        def ask_move(target):
            return typed('MOVE', f'About to move ONLY Recording_QA ({qa_root})\n  to {target}\nThe videos stay in OneDrive.')()
        move_recording_qa(qa_root, a.move_to, repo=a.repo, dry=a.dry_run, confirm=ask_move, import_check=check)
        return 0
    view = RepoView(a.repo, a.ref, a.no_git)
    index = build_index(view)
    if a.audit_hash:
        print(games_hash(index.audit.get('games')))
        return 0
    logs = os.path.dirname(qa_root)
    decisions = filter_batches(decide(scan_qa(qa_root, video_index(logs)), index), set(a.only) if a.only else None)
    report(decisions, view, qa_root, index, a.verbose)
    if a.apply and not a.dry_run:
        remote = None if a.no_git else view.remote_main()
        if a.ref == DEFAULT_REF:
            if remote is None:
                print('WARNING: origin could not be reached, so it is not known whether the committed state is current. Fetch first if you can.')
            elif remote != view.commit_full:
                raise ToolError(f'origin/main here is {view.commit} but origin has {remote[:8]}: run `git fetch origin` in the checkout, then run this again')

        def confirm(n, size, batches):
            return typed('DELETE', f'About to delete {n:,} frame files ({mb(size)}) from {len(batches)} batches: {", ".join(batches)}\nCommitted state: {view.describe()}')()
        deleted, failed, freed, log = apply_deletions(decisions, qa_root, index, view=view, only=set(a.only) if a.only else None, confirm=confirm, whole_batches_only=a.whole_batches_only)
        return 1 if failed else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
