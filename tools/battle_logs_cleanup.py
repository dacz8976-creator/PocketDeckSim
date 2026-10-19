#!/usr/bin/env python3
"""battle_logs_cleanup.py: free OneDrive space by deleting the video FRAMES (jpg/png) of Codex's batch packets whose results are safely in the repo.

  wsl python3 tools/battle_logs_cleanup.py                      dry run (the default): a verdict line per BATCH_* folder (DELETE / PARTIAL / keep), nothing is changed
  wsl python3 tools/battle_logs_cleanup.py --apply              delete the frames of the game packets that pass (asks you to type DELETE and 8 digits of the accepted hash; --yes skips that)
  wsl python3 tools/battle_logs_cleanup.py --move-to C:/Users/dacz8/BattleLogs/Recording_QA     move ONLY Recording_QA out of OneDrive; the videos stay (asks you to type MOVE)

Run it through wsl (it needs git, which Windows has not on its PATH) and give Windows paths with FORWARD slashes (C:/Users/...) or as /mnt/c/...: backslashes typed after `wsl` are eaten.
The rule, the safety rails and the reasons are in tools/README_battle_logs_cleanup.md. In short: a game packet's frames may go when (1) its game is in a games_meta.json committed
on origin/main under rl/results/pause_games_*/ with positions in the positions_all.json next to it, (2) the game is in the committed audit list rl/results/battle_logs_retention_2026-10-14/
audited_games.json under that same games_meta and position count, and the list carries an acceptance (who, when, and a hash of the games it accepted) that still matches, (3) the packet's text outputs
(TURN_LEDGER.json, REVIEW.md, DECK_USED.json) are in the folder and (4) its source video is in Battle Logs (--videos PATH if it is not where the tool looks). A packet that records more than one game
(RELATED_GAME_PACKETS.json, SUMMARY.json source_game_count, a game_02/ folder) keeps the media of ALL its games in its root, so it is held back WHOLE unless every game in it passes on its own under its own
folder. The game packet is the unit; a batch is DELETE when every packet in it passes, PARTIAL when some do (--whole-batches-only leaves those alone). --apply (and the import check of --move-to) reads only the
committed state of origin/main, which must be what origin has now (no --no-git, no other --ref without --allow-ref-other-than-origin-main, no going on when origin cannot be asked without --allow-offline).
Only .jpg/.jpeg/.png files inside game packets that pass are ever deleted, each only after its whole folder chain below Recording_QA has been looked at again (no link or junction) and, where the
file system allows, through a handle on its folder: never json/txt/md or any other file, never a video, never anything outside Recording_QA. Standard library only."""
import argparse, collections, dataclasses, datetime, hashlib, json, os, posixpath, re, shlex, signal, stat, subprocess, sys

FRAME_EXT = ('.jpg', '.jpeg', '.png')
GAME_PACKET = re.compile(r'^\d{8}_\d{6,9}_iOS')                 # 20261013_030351000_iOS (and 20261002_205230000_iOS_auto_sol)
TEXT_REQUIRED = ('TURN_LEDGER.json', 'REVIEW.md', 'DECK_USED.json')   # a packet's text outputs: they must be there, non-empty, before its frames go
META_PATH = re.compile(r'^rl/results/pause_games_[^/]+/(?:.+/)?games_meta\.json$')
AUDIT_LIST = 'rl/results/battle_logs_retention_2026-10-14/audited_games.json'
QA_CANDIDATES = ['C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA', 'C:/Users/dacz8/BattleLogs/Recording_QA']
NESTED_NAME = re.compile(r'(^|_)game_?\d+$', re.I)                      # game_02, game2, ..._game_02: a second game recorded in the same video
BACKUP_NAME = re.compile(r'^(?:original_|submitted_)?before_|_before_|^independent_sol|^rejected_', re.I)    # a folder that keeps an earlier state of a game: part of that game, not another game
SURROGATE_TAGS = (0xA000000C, 0xA0000003)                            # IO_REPARSE_TAG_SYMLINK, IO_REPARSE_TAG_MOUNT_POINT: links and junctions (OneDrive's own reparse points are not)
# words that say a name is not a person's acceptance, anywhere in it ("awaiting Dustin", "laptop (unconfirmed)", "<who>"), whole words only (Noah and Una are names)
NEGATION = re.compile(r"[<>{}\[\]]|\b(?:no|none|nobody|pending|false|tbd|tbc|tba|todo|not|never|wait|waiting|awaiting|hold|unconfirmed|unknown|unnamed|placeholder|n/?a|who|name|withdrawn|withdraw|revoked|revoke|"
                      r"cancel+ed|cancel|rejected|reject|declined|draft|test|example|replace|change|ask|asks|needs?|review|confirm|confirms|to confirm|approve)\b|^\s*-|[^\x00-\x7f]", re.I)
ACCEPTOR = re.compile(r'^\s*Dustin\b')                               # the retention decision is Dustin's: the name in "by" must be his (the laptop session may write it down for him: "Dustin via the laptop")
ACCEPTANCE_KEYS = {'by', 'date', 'games_sha256'}                     # nothing else may sit in "confirmed": an annotated acceptance ("withdrawn": true) is not one
EARLIEST_ACCEPTANCE = datetime.date(2026, 10, 14)                    # the audit list was proposed that day: an earlier date cannot be an acceptance of it
BATTLE_LOGS_DEFAULT = 'C:/Users/dacz8/OneDrive/Desktop/Battle Logs'  # where the videos are (at its top and in Reviewed\)
LOCATION_FILE = 'BATTLE_LOGS_LOCATION.json'                         # --move-to writes it into the moved Recording_QA: where the videos stayed
MEDIA_LOCATIONS = 'MEDIA_LOCATIONS.json'                            # in Battle Logs: Codex's record of where each video is, with the Drive archive entries
CACHE_DEFAULT = 'C:/Users/dacz8/BattleLogsData/Cache/raw'          # <root>/<sha256>/<original file name>: downloads of archived videos
DRIVE_CHECK_ENV = 'BATTLE_LOGS_DRIVE_CHECK'
DRIVE_CHECK_TIMEOUT = 30                                            # seconds: a check that is slower than this is "not confirmed"
SHA_RE = re.compile(r'^[0-9a-f]{64}$')
DEFAULT_REF = 'origin/main'
RELATED_KEYS = {'game_packets', 'games', 'packets', 'related_games', 'related_game_packets', 'related', 'game_folders', 'folders'}      # where RELATED_GAME_PACKETS.json lists the games, in the layouts seen or likely
NATIVE_FS = {'ext2', 'ext3', 'ext4', 'xfs', 'btrfs', 'tmpfs', 'overlay', 'f2fs', 'zfs', 'jfs'}         # file systems on which a directory handle stays on the folder it opened (not 9p: the mounted Windows drive)


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
    if given:
        local = to_local(given)
        if os.path.isdir(local):
            return os.path.abspath(local)
        raise ToolError(f'Recording_QA not found at {given}')
    found = [os.path.abspath(to_local(c)) for c in QA_CANDIDATES if os.path.isdir(to_local(c))]
    if len(found) > 1:
        raise ToolError('more than one Recording_QA exists (' + '; '.join(found) + '): give --qa-root to say which one this run is about')
    if found:
        return found[0]
    raise ToolError('Recording_QA not found; give --qa-root (tried ' + ', '.join(QA_CANDIDATES) + ')')


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
                # 'origin/main' means the remote-tracking ref, never a local branch or tag of that name
                self.commit_full = self._git('rev-parse', '--verify', ('refs/remotes/origin/main' if ref == DEFAULT_REF else ref) + '^{commit}').strip()
                self.commit = self.commit_full[:8]
                self.date = self._git('show', '-s', '--format=%cI', self.commit_full).strip()
            except (OSError, subprocess.CalledProcessError) as e:
                raise ToolError(f'git cannot read {ref} in {self.repo} ({e}); run it through wsl from a checkout, and fetch main first')

    def _git(self, *args):
        # --no-replace-objects: a local `git replace` must not be able to change what "committed on origin/main" says
        return subprocess.run(['git', '--no-replace-objects', '-C', self.repo, *args], capture_output=True, text=True, check=True).stdout

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
            return subprocess.run(['git', '--no-replace-objects', '-C', self.repo, 'show', f'{self.commit_full}:{path}'], capture_output=True, check=True).stdout
        except subprocess.CalledProcessError:
            return None

    def remote_main(self):
        """-> (the sha origin has for refs/heads/main right now, None), or (None, why) when origin cannot say (no network, no such remote, a timeout, several answers); never a password prompt"""
        try:
            r = subprocess.run(['git', '-C', self.repo, 'ls-remote', 'origin', 'refs/heads/main'], capture_output=True, text=True, timeout=30,
                               env=dict(os.environ, GIT_TERMINAL_PROMPT='0'))
        except (OSError, subprocess.TimeoutExpired) as e:
            return None, type(e).__name__
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        if r.returncode != 0 or len(lines) != 1 or lines[0].split()[1:] != ['refs/heads/main']:
            return None, (r.stderr.strip().splitlines() or [f'git ls-remote answered {len(lines)} lines'])[-1][:120]
        return lines[0].split()[0], None

    def push_url_differs(self):
        """does origin push somewhere else than it fetches from? Then what was fetched may be a stale mirror of what is on the real origin"""
        try:
            fetch = self._git('remote', 'get-url', 'origin').strip()
            push = self._git('remote', 'get-url', '--push', 'origin').strip()
        except (OSError, subprocess.CalledProcessError):
            return False
        return fetch != push


def check_fresh(view, allow_offline=False, out=None):
    """origin/main here must be what origin has now, or an acceptance withdrawn since the last fetch would still count. Refuses when it differs, and when origin cannot be asked unless allow_offline
    (then it only warns). Only for the committed state of origin/main (not --no-git, not another ref)."""
    out = out or sys.stdout
    if view.no_git or view.ref != DEFAULT_REF:
        return
    if view.push_url_differs():
        raise ToolError('origin is fetched from one place and pushed to another (remote.origin.pushurl): what this checkout fetched may be a stale mirror of the real origin, so "current" cannot be shown. Make the two URLs one')
    sha, why = view.remote_main()
    if sha is None:
        if not allow_offline:
            raise ToolError(f'origin cannot be asked ({why}), so it is not known whether the committed state is current (an acceptance may have been withdrawn since the last fetch). '
                            'Connect and run `git fetch origin`, or pass --allow-offline to go on with the origin/main this checkout has')
        print(f'WARNING: origin could not be asked ({why}); going on with the origin/main this checkout has ({view.commit}), as --allow-offline says', file=out)
    elif sha != view.commit_full:
        raise ToolError(f'origin/main in this checkout is {view.commit}, but origin has {sha[:8]}: run `git fetch origin` in the checkout (and push the audit list if it is only committed here), then run this again')


@dataclasses.dataclass
class RepoIndex:
    folders: dict          # 'BATCH_x/gamedir' -> (game key, games_meta path, number of positions, sha256 of those positions)
    audit: dict            # the audit list's JSON, or {}
    audit_path_found: bool
    conflicts: dict = dataclasses.field(default_factory=dict)       # 'BATCH_x/gamedir' -> the game keys that several games_meta files claim for it


def _loads(view, path, what):
    raw = view.read(path)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError as e:
        raise ToolError(f'{what} {path} is not valid JSON ({e}); nothing can be decided until it is fixed')


def validate_audit(audit):
    """the audit list must have the shape the rule reads; a malformed one is a refusal with a reason, not a traceback"""
    if not isinstance(audit, dict):
        raise ToolError(f'the audit list {AUDIT_LIST} must be a JSON object')
    for part in ('games', 'pending'):
        v = audit.get(part, {})
        if not isinstance(v, dict) or not all(isinstance(e, dict) for e in v.values()):
            raise ToolError(f'the audit list {AUDIT_LIST} is malformed: "{part}" must be an object whose entries are objects')
    return audit


def positions_digest(positions):
    """a sha256 of the positions of one game (as they are in positions_all.json): the audit list binds the content that was reviewed, not only how many positions there were"""
    return hashlib.sha256(json.dumps(positions, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def build_index(view):
    """folder -> the claim of a committed games_meta.json whose sibling positions_all.json holds positions for the game. A folder can be claimed by several files for the same game (the v1 and the
    corrected v2 positions of the same games): the claim the audit list reviewed (its games_meta, position count and digest) is the one used, else the one in the file the audit entry names, else the
    one with most positions (the earlier file on a tie)."""
    claims, keys = collections.defaultdict(list), collections.defaultdict(set)
    for path in sorted(p for p in view.ls('rl/results') if META_PATH.match(p)):
        meta = _loads(view, path, 'the games_meta file')
        pos = _loads(view, path.rsplit('/', 1)[0] + '/positions_all.json', 'the positions file next to')
        if not isinstance(meta, dict) or not all(isinstance(v, dict) for v in meta.values()) or not isinstance(pos or [], list) or not all(isinstance(p, dict) for p in (pos or [])):
            raise ToolError(f'{path} or the positions_all.json next to it has an unexpected shape (games_meta: {{key: {{folder, ...}}}}, positions: [{{game, ...}}]); nothing can be decided until it is fixed')
        by_game = collections.defaultdict(list)
        for p in (pos or []):
            by_game[p.get('game')].append(p)
        for key, v in meta.items():
            f = (v.get('folder') or '').replace('\\', '/')
            if f and by_game.get(key):
                keys[f].add(key)
                claims[f].append((key, path, len(by_game[key]), positions_digest(by_game[key])))
    raw = _loads(view, AUDIT_LIST, 'the audit list')
    audit = validate_audit(raw) if raw is not None else {}
    entries = collections.defaultdict(list)
    for key, e in (audit.get('games') or {}).items():
        entries[(e.get('folder') or '').replace('\\', '/')].append((key, e))
    folders = {}
    for f, cl in claims.items():
        pick = next((c for key, e in entries.get(f, []) for c in cl if c == (key, e.get('games_meta'), e.get('positions'), e.get('positions_sha256'))), None)
        pick = pick or next((c for key, e in entries.get(f, []) for c in cl if c[1] == e.get('games_meta')), None)
        folders[f] = pick or max(cl, key=lambda c: c[2])
    return RepoIndex(folders, audit, raw is not None, {f: sorted(k) for f, k in keys.items() if len(k) > 1})


def games_hash(games):
    """a hash of what an acceptance covers: each audited game with the folder, the games_meta file, the number of positions and the digest of the positions that were reviewed"""
    canon = {k: [(e.get('folder') or '').replace('\\', '/'), e.get('games_meta'), e.get('positions'), e.get('positions_sha256')] for k, e in sorted((games or {}).items())}
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
    if set(c) != ACCEPTANCE_KEYS:
        return None, f'"confirmed" must hold exactly by, date and games_sha256 (an acceptance that carries anything else, such as {sorted(set(c) - ACCEPTANCE_KEYS) or sorted(ACCEPTANCE_KEYS - set(c))}, is taken to be withdrawn or unfinished; withdraw one by setting "confirmed" to null)'
    by, date, h = c.get('by'), c.get('date'), c.get('games_sha256')
    if not isinstance(by, str) or len(by.strip()) < 2 or not ACCEPTOR.match(by) or NEGATION.search(by):
        return None, '"confirmed.by" must be Dustin\'s name, as in "Dustin" or "Dustin via the laptop" (no placeholder or not-yet wording such as "<who>", "awaiting", "unconfirmed", "withdrawn"; ASCII only)'
    try:
        when = datetime.date.fromisoformat(str(date))
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(date)):
            raise ValueError
    except ValueError:
        return None, '"confirmed.date" must be a date as YYYY-MM-DD'
    if when < EARLIEST_ACCEPTANCE or when > datetime.datetime.now(datetime.timezone.utc).date() + datetime.timedelta(days=1):
        return None, f'"confirmed.date" {date} cannot be the day this list was accepted (not before {EARLIEST_ACCEPTANCE}, not in the future)'
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
    nested: dict = dataclasses.field(default_factory=dict)       # relative folder of a second game inside the packet -> [(path, size)]: deleted only if every game the packet holds passes
    links_skipped: int = 0
    unreadable: int = 0
    video: object = None   # None = not checked, else (ok, reason)
    notes: list = dataclasses.field(default_factory=list)       # why the files that say how many games it holds cannot be relied on: a reason to hold it back
    declared: int = 1      # how many games the packet says it records (RELATED_GAME_PACKETS.json, SUMMARY.json source_game_count, the folders found)
    nested_text: dict = dataclasses.field(default_factory=dict)  # second-game folder (not a backup) -> TEXT_REQUIRED name -> present and non-empty: a second game needs its own text outputs too


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


def _count(v):
    """a game count written as a number or as a numeric string; None otherwise"""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.strip().isdigit():
        return int(v.strip())
    return None


def _entry_path(g):
    return (g.get('path') or g.get('packet') or g.get('folder') or g.get('dir') or '.').replace('\\', '/').strip('/') or '.'


def _related_entries(rel):
    """the per-game entries of a RELATED_GAME_PACKETS.json, in the layouts Codex wrote or may write: a list at the top, or game_packets / games / packets (...) as a list of {path | packet} or as a
    dict keyed by path; a bare string is a path"""
    if isinstance(rel, list):
        items = list(rel)
    elif isinstance(rel, dict):
        items = []
        for key, v in rel.items():
            if isinstance(v, list):
                if key in RELATED_KEYS and all(isinstance(x, (dict, str)) for x in v):
                    items += v
                elif v and all(isinstance(x, dict) and x.keys() & {'path', 'packet', 'folder', 'dir'} for x in v):          # (an unknown key that holds a list of paths)
                    items += v
            elif isinstance(v, dict) and key in RELATED_KEYS and v and all(isinstance(x, dict) for x in v.values()):
                items += [dict(x, path=k) for k, x in v.items()]
    else:
        items = []
    return [g if isinstance(g, dict) else {'path': g} for g in items if isinstance(g, (dict, str))]


def declared_games(packet, n_found):
    """how many games a packet says it records: the largest of 1 + the RELATED_GAME_PACKETS.json entries that are not the root, its entries, its game_count, SUMMARY.json's source_game_count /
    game_count / games_in_source / match_count / games (a number or a list), 2 when `other_games_found` is true, and 1 + the second-game folders found. Codex's own file says that for such a
    packet the root keeps the media for ALL its games"""
    rel = _json(os.path.join(packet, 'RELATED_GAME_PACKETS.json'))
    summ = _json(os.path.join(packet, 'SUMMARY.json'))
    entries = _related_entries(rel)
    counts = [1, 1 + n_found, len(entries), 1 + sum(1 for e in entries if _entry_path(e) != '.')]
    if isinstance(rel, dict):
        counts.append(_count(rel.get('game_count')) or 1)
        if rel.get('other_games_found') is True:
            counts.append(2)
    if isinstance(summ, dict):
        for k in ('source_game_count', 'game_count', 'games_in_source', 'match_count'):
            counts.append(_count(summ.get(k)) or 1)
        g = summ.get('games')
        counts.append(len(g) if isinstance(g, list) else (_count(g) or 1))
    return max(counts)


def marker_notes(packet):
    """why the files that say how many games the packet holds cannot be relied on (present but unreadable, or a RELATED file that does not say): the packet is held back, not guessed about"""
    notes = []
    for name in ('RELATED_GAME_PACKETS.json', 'SUMMARY.json'):
        fp = os.path.join(packet, name)
        if not os.path.exists(fp):
            continue
        data = _json(fp)
        if data is None or not isinstance(data, (dict, list)):
            notes.append(f'{name} cannot be read (it is not valid JSON), so it is not known whether the packet holds one game')
        elif name.startswith('RELATED') and declared_games(packet, 0) <= 1:
            entries = _related_entries(data)
            explicit = (isinstance(data, dict) and (_count(data.get('game_count')) == 1 or data.get('other_games_found') is False)) or (entries and all(_entry_path(e) == '.' for e in entries))
            if not explicit:
                notes.append(f'{name} does not say how many games the packet holds (no game_count of 1, no other_games_found: false, no listed root entry)')
    return notes


def nested_game_dirs(packet):
    """folders inside a game packet that hold a SECOND game of the same recording: those Codex's RELATED_GAME_PACKETS.json lists with a path other than '.', those named game_NN, and those with
    their own TURN_LEDGER.json and a SUMMARY.json whose game_id differs from the packet's. A backup copy of the same game (original_before_*, ...) has the same game_id and is not one. Folders are
    told apart by their name as the file system folds it (the case-insensitive Windows drive), and the spelling on the disk wins over the one in RELATED."""
    found = {}
    rel = _json(os.path.join(packet, 'RELATED_GAME_PACKETS.json'))
    for g in _related_entries(rel):
        p = posixpath.normpath(_entry_path(g))
        if p not in ('', '.') and not p.startswith('..') and os.path.isdir(os.path.join(packet, *p.split('/'))):      # (a listed path that is not there is a declared game with no folder: declared_games counts it)
            found.setdefault(fold(os.path.join(packet, *p.split('/'))), os.path.abspath(os.path.join(packet, *p.split('/'))))
    own = (_json(os.path.join(packet, 'SUMMARY.json')) or {}).get('game_id') if isinstance(_json(os.path.join(packet, 'SUMMARY.json')), dict) else None
    for root, dirs, files in os.walk(packet, followlinks=False):
        if os.path.abspath(root) == os.path.abspath(packet):
            continue
        if NESTED_NAME.search(os.path.basename(root)):
            found[fold(root)] = os.path.abspath(root)           # (the spelling os.walk reports is the one on the disk)
        elif 'TURN_LEDGER.json' in files and own:
            summ = _json(os.path.join(root, 'SUMMARY.json'))
            gid = summ.get('game_id') if isinstance(summ, dict) else None
            if gid and gid != own:
                found[fold(root)] = os.path.abspath(root)
    # a nested folder inside another nested folder belongs to the outer one
    paths = list(found.values())
    return sorted(f for f in paths if not any(f != o and fold(f).startswith(fold(o) + os.sep) for o in paths))


def scan_packet(name, cp):
    nested = nested_game_dirs(cp)
    frames, links, bad = scan_frames(cp, skip_dirs=nested)
    nf = {}
    for n in nested:
        nfr, l2, b2 = scan_frames(n)
        nf[os.path.relpath(n, cp).replace(os.sep, '/')] = nfr
        links += l2
        bad += b2
    nt = {rel: text_status(os.path.join(cp, *rel.split('/'))) for rel in nf if not _in_backup(rel)}
    return Game(name, cp, frames, text_status(cp), nf, links, bad, declared=declared_games(cp, len(nt)), nested_text=nt, notes=marker_notes(cp))


def text_status(folder):
    """{TEXT_REQUIRED name: present and non-empty} in one folder"""
    out = {}
    for t in TEXT_REQUIRED:
        fp = os.path.join(folder, t)
        try:
            out[t] = os.path.isfile(fp) and os.path.getsize(fp) > 0
        except OSError:
            out[t] = False
    return out


def _in_backup(rel):
    """is this folder (relative to its packet) inside a folder that keeps an earlier state of a game (original_before_*, independent_sol, ...)?"""
    return any(BACKUP_NAME.search(part) for part in rel.split('/'))


def video_index(logs_root):
    """{lower-case file name: [(size, path), ...]} of the video files at the top of Battle Logs and in Battle Logs/Reviewed: every copy, none hides another"""
    out = {}
    for d in (logs_root, os.path.join(logs_root, 'Reviewed')):
        try:
            for e in os.scandir(d):
                if e.is_file() and e.name.lower().endswith(('.mp4', '.mov', '.mkv', '.m4v')):
                    out.setdefault(e.name.lower(), []).append((e.stat().st_size, e.path))
        except OSError:
            pass
    return out


def video_dirs(qa_root, explicit=None):
    """the Battle Logs folders to look for videos in (each holds videos at its top and in Reviewed\\): --videos if given, else the one recorded when Recording_QA was moved, the folder
    Recording_QA sits in, and the default OneDrive Battle Logs. -> ([(path, where it came from)], [warnings]); only folders that exist are listed, a recorded one that is not there or
    unusable is a warning"""
    cands, warns = [], []
    if explicit:
        cands.append((explicit, '--videos'))
    else:
        loc = os.path.join(qa_root, LOCATION_FILE)
        rec = _json(loc)
        if rec is None and os.path.exists(loc):
            warns.append(f'{LOCATION_FILE} cannot be read (it is not valid JSON); ignored')
        if rec is not None:
            rl = rec.get('battle_logs') if isinstance(rec, dict) else None
            if not isinstance(rl, str) or not re.match(r'^(?:[A-Za-z]:[\\/]|/)', rl):
                warns.append(f'{LOCATION_FILE} is unusable (it needs {{"battle_logs": an absolute path}}); ignored')
            else:
                cands.append((rl, LOCATION_FILE))
        cands += [(os.path.dirname(qa_root), 'the folder Recording_QA is in'), (BATTLE_LOGS_DEFAULT, 'the default OneDrive Battle Logs')]
    out, seen = [], set()
    for c, why in cands:
        local = os.path.abspath(to_local(str(c)))
        if os.path.isdir(local):
            if fold(local) not in seen:
                seen.add(fold(local))
                out.append((local, why))
        elif why == LOCATION_FILE:
            warns.append(f'{LOCATION_FILE} names {c}, which is not a folder here; ignored')
    return out, warns


def video_index_all(dirs):
    """{lower-case file name: [(size, path), ...]} over several Battle Logs folders"""
    out = {}
    for d, _ in dirs:
        for k, v in video_index(d).items():
            out.setdefault(k, []).extend(v)
    return out


class Archive:
    """where a video can be besides the Battle Logs folders: Codex's MEDIA_LOCATIONS.json (records with the file name, bytes, sha256 and, for an archived one, google_drive_archive.file_id), the
    local cache of downloads (<cache_root>/<sha256>/<file name>) and a live Drive check. A copy counts only as the rule in check_video says; a Drive record alone never does."""

    def __init__(self, records=None, cache_root=None, drive_cmd=None, timeout=DRIVE_CHECK_TIMEOUT, warnings=()):
        self.records = records or {}        # lower-case file name -> [record dict]
        self.cache_root, self.drive_cmd, self.timeout = cache_root, drive_cmd, timeout
        self.warnings = list(warnings)
        self._sha = {}                      # (path, size, mtime_ns) -> sha256: kept for this run only
        self._live = {}                     # file id -> (ok, why): only for the scan, never for the check right before a deletion

    @classmethod
    def load(cls, files, cache_root=None, drive_cmd=None, timeout=DRIVE_CHECK_TIMEOUT):
        records, warns = {}, []
        for f in files:
            if not os.path.exists(f):
                continue
            data = _json(f)
            if not isinstance(data, dict):
                warns.append(f'{f} cannot be read as a JSON object; its records are ignored')
                continue
            for lst in data.values():
                for r in (lst if isinstance(lst, list) else []):
                    if isinstance(r, dict) and isinstance(r.get('filename'), str) and r['filename']:
                        records.setdefault(r['filename'].lower(), []).append(r)
        return cls(records, cache_root, drive_cmd, timeout, warns)

    def has_records(self, name):
        return bool(self.records.get(name.lower()))

    # --- the cache
    def _sha_of(self, path, st):
        key = (path, st.st_size, st.st_mtime_ns)
        if key not in self._sha:
            self._sha[key] = sha256_of(path)
        return self._sha[key]

    def cache_check(self, name, want, src_sha=None):
        """-> (ok, why): a file <cache_root>/<sha256>/<name> whose size is `want` and whose own SHA-256 (computed now) is the sha256 the record (or SOURCE.json) gives"""
        if not self.cache_root:
            return False, 'no cache folder configured'
        shas = {r['sha256'].lower() for r in self.records.get(name.lower(), []) if isinstance(r.get('sha256'), str) and SHA_RE.match(r['sha256'].lower())
                and (r.get('bytes') in (None, want))}
        if src_sha is not None:
            if not (isinstance(src_sha, str) and SHA_RE.match(src_sha.lower())):
                return False, 'SOURCE.json records a sha256 that is not 64 hex digits'
            shas = {src_sha.lower()} & shas if shas else {src_sha.lower()}
        if not shas:
            return False, 'no record gives a sha256 (with this size) for it'
        if os.path.basename(name) != name or name in ('.', '..'):
            return False, 'the video name is not a plain file name'
        why = []
        for sha in sorted(shas):
            d = os.path.join(self.cache_root, sha)
            fp = os.path.join(d, name)
            if not os.path.isfile(fp):
                why.append(f'{sha[:12]}.../{name} is not in the cache')
                continue
            if is_link(d) or is_link(fp):
                why.append(f'{sha[:12]}.../{name} in the cache is a link, not a file')
                continue
            try:
                st = os.stat(fp)
                if st.st_size != want:
                    why.append(f'cache copy {sha[:12]}.../{name} has {st.st_size} bytes, SOURCE.json says {want}')
                    continue
                got = self._sha_of(fp, st)
            except OSError as e:
                why.append(f'cache copy {sha[:12]}.../{name} cannot be read ({type(e).__name__})')
                continue
            if got != sha:
                why.append(f'cache copy {sha[:12]}.../{name} has SHA-256 {got[:12]}..., the record says {sha[:12]}...')
                continue
            return True, ''
        return False, '; '.join(why)

    # --- Drive
    def drive_check(self, name, want, fresh=False):
        """-> (ok, why): some Drive record of `name` whose live check (the external command, run now) says the file exists, is not in Trash and has `want` bytes"""
        recs = [r for r in self.records.get(name.lower(), []) if isinstance(r.get('google_drive_archive'), dict) and isinstance(r['google_drive_archive'].get('file_id'), str)
                and r['google_drive_archive']['file_id'].strip()]
        if not recs:
            return False, 'no Drive record'
        if not self.drive_cmd:
            return False, 'it has a Drive record, but no live Drive check is configured (--drive-check-cmd or BATTLE_LOGS_DRIVE_CHECK), and a record alone never counts'
        why = []
        for r in recs:
            a = r['google_drive_archive']
            fid = a['file_id'].strip()
            if r.get('bytes') not in (None, want):
                why.append(f'the Drive record says {r.get("bytes")} bytes, SOURCE.json says {want}')
                continue
            if not fresh and fid in self._live:
                res = self._live[fid]
            else:
                res = self._live_check(fid, want, a.get('provider_checksums') if isinstance(a.get('provider_checksums'), dict) else {}, r.get('sha256'))
                if not fresh:
                    self._live[fid] = res
            if res[0]:
                return True, ''
            why.append(res[1])
        return False, '; '.join(why)

    def _live_check(self, fid, want, sums, rec_sha):
        try:
            if any(c in fid for c in '\x00\r\n') or fid.startswith('-'):
                return False, f'Drive file id {fid!r} is not usable'
            argv = [t.replace('{id}', fid) for t in shlex.split(self.drive_cmd, posix=os.name != 'nt')]
            if not any('{id}' in t for t in shlex.split(self.drive_cmd, posix=os.name != 'nt')):
                argv.append(fid)
            r = subprocess.run(argv, capture_output=True, text=True, timeout=self.timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return False, f'the Drive check for {fid} took more than {self.timeout} s'
        except (OSError, ValueError) as e:
            return False, f'the Drive check could not be run ({type(e).__name__})'
        if r.returncode != 0:
            return False, f'the Drive check for {fid} failed (exit {r.returncode})'
        try:
            j = json.loads(r.stdout)
        except ValueError:
            return False, f'the Drive check for {fid} did not print JSON'
        if not isinstance(j, dict) or j.get('id') != fid:
            return False, f'the Drive check for {fid} answered for another file or in an unexpected shape'
        if j.get('exists') is not True:
            return False, f'Drive says file {fid} does not exist'
        if j.get('trashed') is not False:
            return False, f'Drive says file {fid} is in Trash (or does not say it is not)'
        size = j.get('size')
        size = int(size) if isinstance(size, str) and size.isdigit() else size
        if isinstance(size, bool) or size != want:
            return False, f'Drive says file {fid} has {j.get("size")!r} bytes, SOURCE.json says {want}'
        for key, mine in (('md5', sums.get('md5')), ('sha256', sums.get('sha256') or rec_sha)):
            if key in j and isinstance(mine, str) and mine and str(j[key]).lower() != mine.lower():
                return False, f'Drive says file {fid} has {key} {str(j[key])[:12]}..., the record says {mine[:12]}...'
        return True, ''


def check_video(game, videos, where='', fresh=False, archive=None):
    """-> (ok, reason): the packet's SOURCE.json names a video, with its size, and the video still exists: (a) some copy of it in Battle Logs has exactly that size, or (b) the download cache has
    it under its sha256 (from MEDIA_LOCATIONS.json or SOURCE.json), at that size and with that SHA-256, or (c) it is archived in Google Drive and a live check, now, says it is there, not in Trash,
    with that size. Frames can be cut again from any of these. `fresh` asks the file systems and Drive again (the check just before a packet's frames are deleted)"""
    src = _json(os.path.join(game.path, 'SOURCE.json'))
    src = src if isinstance(src, dict) else {}
    name = src.get('video_basename')
    if not isinstance(name, str) or not name:
        return False, 'source video not recorded (SOURCE.json has no video_basename)'
    want = src.get('bytes')
    if isinstance(want, bool) or not isinstance(want, int) or want <= 0:
        return False, f'SOURCE.json does not record a usable size for source video {name} (bytes: {want!r}), so a copy cannot be told from a truncated one'
    copies = videos.get(name.lower()) or []
    if fresh:
        now = []
        for size, path in copies:
            try:
                now.append((os.stat(path).st_size, path))
            except OSError:
                pass
        copies = now
    if want in {s for s, _ in copies}:
        return True, ''
    if copies:
        local = f'source video {name} has {", ".join(str(s) for s, _ in copies)} bytes, SOURCE.json says {want}'
    else:
        local = f'source video {name} not found in Battle Logs' + (f' (looked in {where}; --videos PATH names the folder)' if where else '')
    if archive is None or not archive.has_records(name):
        return False, local
    sha = src.get('sha256')
    ok, cwhy = archive.cache_check(name, want, sha)
    if ok:
        return True, ''
    ok, dwhy = archive.drive_check(name, want, fresh)
    if ok:
        return True, ''
    return False, f'{local}; archived: not in the cache ({cwhy}); Drive: {dwhy}'


def scan_qa(qa_root, videos=None, where='', archive=None):
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
                    g.video = check_video(g, videos, where, archive=archive)
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
    adopted: frozenset = frozenset()     # the second-game folders of a packet that passes because every game in it passes: their frames go with the packet's

    @property
    def ok(self):
        return not self.reasons

    @property
    def delete_frames(self):
        """the frames --apply may remove for this packet: its own, and those of the second games that passed on their own"""
        return list(self.game.frames) + [f for rel in sorted(self.adopted) for f in self.game.nested.get(rel, [])]

    @property
    def stay_frames(self):
        """the frames of this packet that stay: all of them when it is held back, else those of folders that keep an earlier state of a game"""
        if not self.ok:
            return list(self.game.frames) + [f for fr in self.game.nested.values() for f in fr]
        return [f for rel, fr in self.game.nested.items() if rel not in self.adopted for f in fr]


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
        return sum(len(g.delete_frames) for g in self.ok_games)

    @property
    def bytes(self):
        return sum(s for g in self.ok_games for _, s in g.delete_frames)

    @property
    def kept_frames(self):
        """frames that stay: those of packets that do not pass (second games inside them included), and of folders that keep an earlier state of a game"""
        return sum(len(g.stay_frames) for g in self.games)

    @property
    def kept_bytes(self):
        return sum(s for g in self.games for _, s in g.stay_frames)


def entry_reasons(folder, index):
    """-> (why this folder's game cannot go by the repo and the audit list, the repo's entry): [] when the game is in a committed games_meta.json with positions and is audited as it is now"""
    reasons = []
    hit = index.folders.get(folder)
    key = hit[0] if hit else None
    if not hit:
        reasons.append('not in the repo: no committed games_meta.json (with positions) names this folder')
    if folder in index.conflicts:
        reasons.append(f'several games_meta files name this folder for different games ({", ".join(index.conflicts[folder])}): the repo does not say which game it holds')
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
        elif entry.get('positions_sha256') != hit[3]:
            reasons.append('not audited as it is now: the positions in the repo are not the ones the audit list reviewed (their sha256 differs, or the entry has none)')
    return reasons, hit


def decide_game(batch_name, game, index):
    folder = f'{batch_name}/{game.name}'
    reasons, hit = entry_reasons(folder, index)
    key = hit[0] if hit else None
    for t, ok in game.text.items():
        if not ok:
            reasons.append(f'text output {t} missing or empty')
    if game.video is not None and not game.video[0]:
        reasons.append(game.video[1])
    if game.unreadable:
        reasons.append(f'{game.unreadable} entries in the packet could not be read')
    reasons += game.notes
    # a packet that records more than one game keeps the media of ALL its games in its root (Codex's RELATED_GAME_PACKETS.json: root_is_only_shared_writer_and_media_mover), so its frames
    # go only when every game in it passes on its own: each second game must be in the repo and audited under its own folder (BATCH/packet/game_02)
    second = sorted(r for r in game.nested if not _in_backup(r))
    if game.declared > 1 or second:
        why = []
        if game.declared - 1 > len(second):
            why.append(f'it records {game.declared} games but only {len(second)} second-game folder{"" if len(second) == 1 else "s"} could be found')
        for rel in second:
            r, _ = entry_reasons(f'{folder}/{rel}', index)
            if r:
                why.append(f'{rel} ({len(game.nested[rel])} frames) is not audited: {r[0]}')
            lost = [t for t, ok in game.nested_text.get(rel, {}).items() if not ok]
            if lost:
                why.append(f'{rel} has no text output {", ".join(lost)} (missing or empty)')
        if why:
            reasons.append(f'holds {game.declared} games; ' + '; '.join(why) + ' -- the packet root keeps the media of all its games, so none of its frames go')
    adopted = frozenset(second) if not reasons else frozenset()
    return GameDecision(game, key, reasons, folder, hit[1] if hit else None, hit[2] if hit else 0, adopted)


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


def report(decisions, view, qa_root, index, verbose=False, out=None, videos_from=None, warnings=(), asked_origin=False, archive=None):
    out = out or sys.stdout
    p = lambda *a: print(*a, file=out)
    p(f'Recording_QA: {qa_root}')
    if videos_from is not None:
        p('Source videos looked for in: ' + ('; '.join(f'{d} ({why})' for d, why in videos_from) or 'NOWHERE (no Battle Logs folder found: give --videos PATH)'))
    if archive is not None:
        p(f'Archived videos: cache {archive.cache_root or "(none)"} (a copy counts only with the recorded SHA-256 and size); MEDIA_LOCATIONS records for {len(archive.records)} files; Drive live check: '
          + (f'{archive.drive_cmd}' if archive.drive_cmd else 'NOT configured, so a video that is only in Drive is never confirmed and its packets stay (--drive-check-cmd, or BATTLE_LOGS_DRIVE_CHECK)'))
    for w in warnings:
        p('WARNING: ' + w)
    p(f'Committed state read from: {view.describe()}' + ('' if asked_origin or view.no_git else ' -- origin was NOT asked whether this is current (--apply asks)'))
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
            if g.ok:
                for rel, fr in g.game.nested.items():
                    if rel not in g.adopted:
                        p(f'      stays {g.game.name}/{rel}: a folder that keeps an earlier state of a game: {len(fr)} frames, {mb(sum(s for _, s in fr))}')
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
def sha256_of(path, check=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
            if check:
                check()
    return h.hexdigest()


def text_inventory(game_paths, check=None):
    """{path: sha256} of every non-frame file under the game packets: what must still be there, unchanged, after the deletion. `check` is called between files and between chunks (a signal
    that arrived is acted on there)"""
    inv = {}
    for gp in game_paths:
        for root, _, files in os.walk(gp, followlinks=False):
            for f in files:
                if not f.lower().endswith(FRAME_EXT):
                    fp = os.path.join(root, f)
                    try:
                        inv[fp] = sha256_of(fp, check)
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
            nested = [os.path.abspath(os.path.join(gp, *r.split('/'))) for r in g.game.nested if r not in g.adopted]       # a second game that did not pass on its own is never touched
            frames = []
            for fp, size in g.delete_frames:
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
    """SIGHUP/SIGTERM/SIGINT while frames are being deleted do not interrupt a file in the middle of 'removed, counted, logged': the handler only sets a flag, and the loop calls check() between
    files, which raises Interrupted, so the log is closed with an 'interrupted' line that agrees with what is gone (SIGKILL cannot be caught; the line-buffered log still has every line written).
    A signal that was set to be ignored (nohup ignores SIGHUP) stays ignored."""

    def __init__(self, enable=True):
        self.enable = enable and hasattr(signal, 'SIGTERM')
        self.old = {}
        self.pending = None

    def __enter__(self):
        if self.enable:
            def handler(signum, frame):
                self.pending = signal.Signals(signum).name
            for s in (getattr(signal, 'SIGHUP', None), signal.SIGTERM, signal.SIGINT):
                if s is not None:
                    try:
                        if signal.getsignal(s) == signal.SIG_IGN:
                            continue
                        self.old[s] = signal.signal(s, handler)
                    except ValueError:      # not the main thread
                        pass
        return self

    def check(self):
        if self.pending:
            raise Interrupted(self.pending)

    def __exit__(self, *a):
        for s, h in self.old.items():
            signal.signal(s, h)


# (os.remove and os.unlink are one call, but only os.unlink is listed in supports_dir_fd)
DIR_FD_OK = (os.name != 'nt' and os.unlink in os.supports_dir_fd and os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd and hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY'))


def fs_type(path):
    """the type of the file system that holds `path` (the longest matching mount point in /proc/mounts), or None when it cannot be told"""
    try:
        real, best, kind = os.path.realpath(path), '', None
        with open('/proc/mounts', encoding='utf-8', errors='replace') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3:
                    mp = parts[1].replace('\\040', ' ')
                    if (real == mp or real.startswith(mp.rstrip('/') + '/')) and len(mp) >= len(best):
                        best, kind = mp, parts[2]
        return kind
    except OSError:
        return None


def use_dir_handles(qa_real):
    """directory handles only where they stay on the folder they opened: native Linux file systems. On the mounted Windows drive (9p) a handle is resolved by name and a folder swapped for a
    junction is followed (shown by the second review), so there every file is checked on its path instead"""
    return DIR_FD_OK and fs_type(qa_real) in NATIVE_FS


class NotSafe(OSError):
    """a frame (or one of its folders) is not what the plan saw: a link, a folder swapped for a link, not a regular file"""


class PacketDirs:
    """a game packet's frames removed one at a time, each after its whole folder chain below Recording_QA is looked at again, uncached: every component a real folder, none a link or a junction.
    Where the file system keeps a directory handle on the folder it opened (native Linux), the file is removed relative to the folder's handle (O_NOFOLLOW, one handle per folder at a time) and
    the handle is compared with the folder at its path; elsewhere (the mounted Windows drive, native Windows Python) the file is removed by its path right after the check."""

    def __init__(self, qa_real, parts, packet_abs, qa_id=None):
        # `parts` are the packet's names below Recording_QA as the plan saw them (batch, packet), never re-derived from a path that may have been swapped for a link since
        self.qa_real, self.parts, self.packet_abs, self.qa_id = qa_real, tuple(parts), packet_abs, qa_id
        self.fds = {}
        self.use_fds = use_dir_handles(qa_real)
        self._chain(self.parts)
        if self.use_fds:
            try:
                self.fds[()] = os.open(qa_real, os.O_RDONLY | os.O_DIRECTORY)
                self._open(self.parts)
            except OSError:
                self.close()
                raise NotSafe(f'{"/".join(parts)} is not a real folder inside Recording_QA any more')

    def _chain(self, parts):
        """Recording_QA is the folder that was checked, and every folder below it down to `parts` is a real folder (lstat, nothing cached)"""
        try:
            st = os.lstat(self.qa_real)
            if self.qa_id and self.qa_id[1] and (st.st_dev, st.st_ino) != self.qa_id:
                raise NotSafe('Recording_QA is not the folder that was checked before the question any more')
            path = self.qa_real
            for part in parts:
                path = os.path.join(path, part)
                st = os.lstat(path)
                if not stat.S_ISDIR(st.st_mode) or is_name_surrogate(st):
                    raise NotSafe(f'{os.path.relpath(path, self.qa_real)} is not a real folder inside Recording_QA any more (a link or a junction took its place)')
        except NotSafe:
            raise
        except OSError as e:
            raise NotSafe(f'a folder of the packet is not there any more ({e})')

    def _open(self, parts):
        if parts not in self.fds:
            parent = self._open(parts[:-1])
            self.fds[parts] = os.open(parts[-1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        return self.fds[parts]

    def _release(self, keep):
        """close the handles of the folders the next file is not in (a packet can have more folders than the process may keep open)"""
        for key in [k for k in self.fds if k and keep[:len(k)] != k]:
            try:
                os.close(self.fds.pop(key))
            except OSError:
                self.fds.pop(key, None)

    def remove(self, fp):
        """remove one frame file, given its path inside the packet; raises NotSafe when it is not a regular file in a real folder of the packet"""
        name, folder = os.path.basename(fp), os.path.dirname(fp)
        rel = os.path.relpath(folder, self.packet_abs).split(os.sep)
        if rel[0] == os.pardir:
            raise NotSafe(f'{fp} is not inside its packet')
        where = self.parts + tuple(r for r in rel if r != '.')
        self._chain(where)
        if self.use_fds:
            try:
                self._release(where)
                fd = self._open(where)
                here, there = os.fstat(fd), os.lstat(os.path.join(self.qa_real, *where))
                if (here.st_dev, here.st_ino) != (there.st_dev, there.st_ino):
                    raise NotSafe(f'{fp}: its folder is not where it was when it was opened (it was moved)')
                st = os.stat(name, dir_fd=fd, follow_symlinks=False)
            except NotSafe:
                raise
            except OSError as e:
                raise NotSafe(f'{fp}: its folder is not a real folder of the packet any more ({e})')
            if not stat.S_ISREG(st.st_mode) or is_name_surrogate(st):
                raise NotSafe(f'{fp} is not a regular file at the moment of deletion')
            os.remove(name, dir_fd=fd)
        else:
            path = os.path.join(self.qa_real, *where, name)
            st = os.lstat(path)
            if not stat.S_ISREG(st.st_mode) or is_name_surrogate(st):
                raise NotSafe(f'{fp} is not a regular file at the moment of deletion')
            os.remove(path)

    def close(self):
        for fd in self.fds.values():
            try:
                os.close(fd)
            except OSError:
                pass
        self.fds = {}


class ApplyResult(tuple):
    """(deleted, failed, bytes freed, log path); .skipped is the number of packets that were left alone because a required text output or the packet folder changed during the run"""
    skipped = 0


def apply_deletions(decisions, qa_root, index, view=None, only=None, confirm=None, log_dir=None, out=None, now=None, whole_batches_only=False, progress_every=1000, handle_signals=True,
                    video_check=None):
    """delete the planned frames; `confirm` is called with (n, bytes, batches) and must return True; `video_check(game)` -> (ok, reason) is asked again just before each packet's first removal.
    Returns (deleted, failed, bytes freed, log path) with .skipped."""
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
        return ApplyResult((0, 0, 0, None))
    qa_real = os.path.realpath(qa_root)                 # resolved once, before the question, with the identity of the folder it names: a Recording_QA swapped for a link meanwhile is not followed
    qa_st = os.stat(qa_real)
    qa_id = (qa_st.st_dev, qa_st.st_ino)
    games = sorted({g.game.path for g, _ in plan})
    print(f'reading the {len(games)} packets\' text outputs for the integrity check ...', file=out)
    before = text_inventory(games)           # taken now, before the question, with a hash of each file
    if confirm is not None and not confirm(nplanned, sum(s for _, fr in plan for _, s in fr), batches):
        raise ToolError('not confirmed; nothing deleted')
    stamp = (now or datetime.datetime.now(datetime.timezone.utc)).strftime('%Y%m%dT%H%M%SZ')
    log_path = os.path.join(log_dir or qa_root, f'CLEANUP_LOG_{stamp}.jsonl')
    deleted = failed = freed = skipped_packets = 0
    phase = 'deleting'
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
            with _Signals(handle_signals) as sig:
                for g, frames in plan:
                    sig.check()
                    packet_abs = os.path.abspath(g.game.path)
                    missing = [t for t, ok in text_status(g.game.path).items() if not ok]
                    missing += [f'{rel}/{t}' for rel in sorted(g.adopted) for t, ok in text_status(os.path.join(g.game.path, *rel.split('/'))).items() if not ok]       # a second game's too
                    if missing:
                        skipped_packets += 1
                        put({'skipped_packet': g.folder, 'reason': 'text outputs missing or empty just before deletion: ' + ', '.join(missing)}, sync=True)
                        print(f'SKIPPED {g.folder}: {", ".join(missing)} missing or empty just before deletion', file=out)
                        continue
                    if video_check is not None:
                        vok, vwhy = video_check(g.game)
                        if not vok:
                            skipped_packets += 1
                            put({'skipped_packet': g.folder, 'reason': 'source video, checked again just before deletion: ' + vwhy}, sync=True)
                            print(f'SKIPPED {g.folder}: {vwhy} (checked again just before deletion)', file=out)
                            continue
                    try:
                        dirs = PacketDirs(qa_real, os.path.relpath(packet_abs, os.path.abspath(qa_root)).split(os.sep), packet_abs, qa_id)
                    except NotSafe as e:
                        skipped_packets += 1
                        put({'skipped_packet': g.folder, 'reason': str(e)}, sync=True)
                        print(f'SKIPPED {g.folder}: {e}', file=out)
                        continue
                    try:
                        for fp, size in frames:
                            rel = os.path.relpath(fp, qa_root).replace(os.sep, '/')
                            try:
                                dirs.remove(os.path.abspath(fp))
                            except NotSafe as e:
                                failed += 1
                                put({'failed': rel, 'error': f'{e}; left alone'})
                                sig.check()
                                continue
                            except OSError as e:
                                failed += 1
                                put({'failed': rel, 'error': str(e)})
                                sig.check()
                                continue
                            deleted += 1
                            freed += size
                            put({'removed': rel, 'bytes': size})
                            if progress_every and deleted % progress_every == 0:
                                log.flush()
                                os.fsync(log.fileno())
                                print(f'  removed {deleted:,} of {nplanned:,} ...', file=out)
                            sig.check()
                    finally:
                        dirs.close()
                phase = 'checking'
                after = text_inventory(games, check=sig.check)          # (a signal during this pass is acted on too)
                gone = sorted(set(before) - set(after))
                changed = sorted(p for p in before if p in after and before[p] != after[p])
                put({'done': True, 'deleted': deleted, 'failed': failed, 'skipped_packets': skipped_packets, 'bytes_freed': freed,
                     'non_frame_files_missing_after': gone, 'non_frame_files_changed': changed}, sync=True)
        except (Interrupted, KeyboardInterrupt) as e:
            put({'interrupted': str(e) or 'KeyboardInterrupt', 'during': phase, 'deleted': deleted, 'failed': failed, 'bytes_freed': freed}, sync=True)
            if phase == 'checking':
                print(f'interrupted ({e or "Ctrl-C"}) during the integrity check: all {deleted:,} deletions are in the log {log_path}; the check was not finished.', file=out)
                raise ToolError(f'interrupted during the integrity check after {deleted} deletions; the deletions are all logged, the check was not finished; to check, compare the text outputs with a copy', code=130)
            print(f'interrupted ({e or "Ctrl-C"}): {deleted:,} frames deleted, integrity check not run; the log is {log_path}. Run --apply again to finish.', file=out)
            raise ToolError(f'interrupted after {deleted} deletions; integrity check not run; run --apply again to finish', code=130)
    print(f'deleted {deleted:,} frames ({mb(freed)}); {failed} failed; {skipped_packets} packets skipped; log: {log_path}', file=out)
    if gone or changed:
        raise ToolError(f'INTEGRITY CHECK FAILED: {len(gone)} non-frame files missing and {len(changed)} changed since the inventory taken before the question (this tool deletes only frame files, so something else touched them, or the tool is wrong); see {log_path}')
    print(f'integrity check: all {len(before):,} non-frame files of those packets are still there, with the same SHA-256', file=out)
    if failed or skipped_packets:
        print(f'INCOMPLETE: {failed} frames could not be deleted and {skipped_packets} packets were skipped (see the log); close OneDrive/Codex/Explorer if they hold files open, '
              'and look at why a packet was skipped (a required text output or the folder changed during the run), then run --apply again.', file=out)
    res = ApplyResult((deleted, failed, freed, log_path))
    res.skipped = skipped_packets
    return res


# ---------------------------------------------------------------------------------------------------------------- move
def is_drive_root(p):
    return bool(re.fullmatch(r'/mnt/[a-z]/?', p)) or bool(re.fullmatch(r'[A-Za-z]:[\\/]?', p)) or p in ('/', '')


def quoted(path):
    """a path for pasting after `wsl`: in double quotes when it has a space"""
    return f'"{path}"' if ' ' in path else path


def move_recording_qa(source, target, repo=None, confirm=None, dry=False, out=None, import_check=None, import_label='committed, byte for byte, in rl/results/battle_log_packets',
                      import_where=None, videos_dir=None, allow_onedrive_target=False, import_info=None):
    """move ONLY Recording_QA (the frames and the packets) to `target`; the videos and everything else in Battle Logs stay where they are, in OneDrive.
    A rename on the same drive: instant, nothing copied, nothing half-moved. The import check runs before the question and AGAIN after the answer (a file Codex wrote meanwhile moves away
    uncommitted otherwise). Returns the new path (None for a dry run)."""
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
    if is_link(source):
        raise ToolError(f'{source} is a link (a symlink or junction), not the folder itself: renaming it would move the link and leave the data in OneDrive. Give the real folder')
    if os.path.basename(target).lower() != 'recording_qa':
        raise ToolError(f'the target {target} does not end in Recording_QA: the moved folder keeps its name (a path whose backslashes were lost on the way through `wsl` merges the last folder into the one before it)')
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
    if make_parent:
        grand, new = os.path.dirname(parent), os.path.basename(parent)
        glued = [s for s in os.listdir(grand) if len(s) >= 3 and s.lower() != new.lower() and new.lower().startswith(s.lower()) and os.path.isdir(os.path.join(grand, s))]
        if glued:
            raise ToolError(f'the folder that would be created, {parent}, is the name of an existing folder ({glued[0]}) with more letters stuck on: that is what a path with a lost backslash looks like '
                            f'(C:/Users/dacz8\\BattleLogs arriving as C:/Users/dacz8BattleLogs). Create the folder yourself first if it is meant')
    anchor = os.path.dirname(parent) if make_parent else parent
    if os.stat(source).st_dev != os.stat(anchor).st_dev:
        raise ToolError('the target is on another drive: a move there is a copy of everything and is not done by this tool; use a path on the same drive')
    in_onedrive = any(part.lower().startswith('onedrive') for part in to_windows(target).replace('/', '\\').split('\\'))
    if in_onedrive and not allow_onedrive_target:
        raise ToolError('the target is inside a OneDrive folder, so this would not take Recording_QA out of OneDrive (--allow-target-in-onedrive says it is meant)')
    logs = os.path.dirname(source)
    p(f'move ONLY Recording_QA (the frames and the packets): {to_windows(source)}  ->  {to_windows(target)}')
    p('  a rename on the same drive: instant, nothing is copied' + (f'; the folder {to_windows(parent)} is created first' if make_parent else ''))
    if in_onedrive:
        p('  WARNING: the target is still inside a OneDrive folder (--allow-target-in-onedrive): OneDrive keeps syncing it')
    siblings = sorted(os.listdir(logs))
    videos = [f for f in siblings if f.lower().endswith(('.mp4', '.mov', '.mkv')) and os.path.isfile(os.path.join(logs, f))]
    folders = [f for f in siblings if os.path.isdir(os.path.join(logs, f)) and fold(os.path.join(logs, f)) != fold(source)]
    p(f'  STAYS where it is, in OneDrive: everything else in {to_windows(logs)}: {len(videos)} video file{"" if len(videos) == 1 else "s"} at its top, the folders {", ".join(folders) or "(none)"}, and its files. The videos are not moved.')
    p('  OneDrive will see Recording_QA leave and remove it from the cloud, INCLUDING the packets\' text outputs (ledgers, reviews, deck files): they exist nowhere else (the repo holds only the positions derived from them), so back them up first or pause OneDrive.')
    for line in stale_references(source, repo):
        p('  ' + line)
    if import_check is not None:
        # the text outputs are the permanent part and exist nowhere else: GitHub must hold them, byte for byte, before they leave OneDrive's cloud
        if import_where:
            p('  ' + import_where)
        problems = import_check()
        if import_info and import_info.get('uncopied'):
            p('  WARNING: these files of Recording_QA are neither text outputs nor images/videos, are not copied into git, and leave OneDrive\'s cloud with the folder: ' + '; '.join(import_info['uncopied']))
        if problems:
            for line in problems:
                p('  IMPORT NOT CURRENT: ' + line)
            if not dry:
                raise ToolError('the text outputs of Recording_QA are not all committed in rl/results/battle_log_packets yet: run `wsl python3 tools/battle_logs_import_packets.py` (it finds the Battle Logs folder itself), '
                                'commit it, push it and integrate it into main, `git fetch origin`, then try again (--no-import-check skips this check, at your own risk)')
            p('  (a real move would be refused until the import is current)')
        else:
            p(f'  import check: every text output of Recording_QA is {import_label}')
    if dry:
        p('dry run: nothing moved')
        return None
    if confirm is not None and not confirm(to_windows(target)):
        raise ToolError('not confirmed; nothing moved')
    if import_check is not None:
        # asked again after the answer: Codex keeps writing, and the person may have taken minutes to type
        again = import_check()
        if again:
            raise ToolError('the text outputs of Recording_QA changed while the question was open, and are not all committed any more: ' + '; '.join(again[:3]) + '. Nothing was moved; run the import again')
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
    # where the videos are: --videos, else where an earlier move recorded them, else the folder Recording_QA was in
    prev = _json(os.path.join(target, LOCATION_FILE))
    prev = prev.get('battle_logs') if isinstance(prev, dict) else None
    where_videos = to_forward(to_local(videos_dir)) if videos_dir else (prev if isinstance(prev, str) and os.path.isdir(to_local(prev)) else to_forward(logs))
    try:
        with open(os.path.join(target, LOCATION_FILE), 'w', encoding='utf-8') as f:
            json.dump({'battle_logs': where_videos, 'note': 'where the videos stayed when Recording_QA was moved out of Battle Logs (battle_logs_cleanup.py --move-to); the tool looks for the source videos here',
                       'moved_from': to_forward(source), 'moved_to': to_forward(target), 'moved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}, f, indent=1)
            f.write('\n')
        p(f'  (wrote {LOCATION_FILE} in the moved folder: the tool reads it to find the videos)')
    except OSError as e:
        p(f'  WARNING: {LOCATION_FILE} could not be written ({e}); give --videos {quoted(where_videos)} to the tool')
    p(f'This tool finds it with --qa-root {quoted(to_forward(target))}. The videos and the other files are still in {to_windows(logs)} (--videos {quoted(to_forward(logs))} names that folder).')
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
    ap.add_argument('--audit-hash', action='store_true', help='print the games_sha256 an acceptance in the audit list must carry for the games listed now (with the ref and commit it was computed from), and exit')
    ap.add_argument('--videos', metavar='PATH', help='the Battle Logs folder that holds the source videos (at its top and in Reviewed/); default: the one recorded in the moved Recording_QA by --move-to, the folder '
                    'Recording_QA is in, and C:/Users/dacz8/OneDrive/Desktop/Battle Logs')
    ap.add_argument('--cache-root', default=CACHE_DEFAULT, metavar='PATH', help='the folder of downloaded archived videos, <PATH>/<sha256>/<file name> (default ' + CACHE_DEFAULT + '); a cache copy counts only with the recorded size and SHA-256')
    ap.add_argument('--media-locations', metavar='FILE', help='Codex\'s MEDIA_LOCATIONS.json (default: the one in each Battle Logs folder the tool looks in)')
    ap.add_argument('--drive-check-cmd', metavar='CMD', default=os.environ.get(DRIVE_CHECK_ENV), help='external command that asks Drive live about one archived file; "{id}" in it is replaced by the Drive file ID (else the ID is appended). '
                    'It must print JSON with id, exists, trashed and size (optionally md5/sha256). A Drive-only video counts as present only when it says exists:true, trashed:false and the size SOURCE.json records; no command, an error, a timeout or anything else = not confirmed (default: env ' + DRIVE_CHECK_ENV + ')')
    ap.add_argument('--allow-target-in-onedrive', action='store_true', help='with --move-to: accept a target that is itself inside a OneDrive folder (the move would not take Recording_QA out of OneDrive)')
    ap.add_argument('--allow-offline', action='store_true', help='with --apply / --move-to: go on when origin cannot be asked whether origin/main is current (otherwise refused: an acceptance may have been withdrawn since the last fetch)')
    ap.add_argument('--verbose', '-v', action='store_true', help='list the reasons for every held-back game')
    a = ap.parse_args(argv)
    a.repo = to_local(a.repo)
    if a.apply and a.move_to:
        raise ToolError('--apply and --move-to are separate: run one, then the other')
    # what --apply deletes on, and what a real --move-to trusts for the backup of the text outputs, is the committed state of origin/main and nothing else
    if (a.apply or (a.move_to and not a.no_import_check)) and not a.dry_run:
        what = '--apply' if a.apply else '--move-to (its import check)'
        if a.no_git:
            raise ToolError(f'{what} reads only the committed state of origin/main; --no-git reads whatever is in the working tree, which is not a backup of anything. Run it through wsl, which has git')
        if a.ref != DEFAULT_REF and not a.allow_ref_other_than_origin_main:
            raise ToolError(f'{what} reads only the committed state of {DEFAULT_REF}, not {a.ref}; --allow-ref-other-than-origin-main overrides this, at your own risk')
    if a.audit_hash:
        view = RepoView(a.repo, a.ref, a.no_git)
        index = build_index(view)
        if not index.audit_path_found:
            raise ToolError(f'the audit list {AUDIT_LIST} is not committed at {view.describe()}, so there is no hash to give')
        games = index.audit.get('games') or {}
        print(f'{games_hash(games)}  (games_sha256 of the {len(games)} games listed in {AUDIT_LIST} at {view.describe()}; origin was NOT asked whether that commit is current: `git fetch origin` first)')
        return 0
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
        check, label, mview, where, info = None, 'committed, byte for byte, in rl/results/battle_log_packets', None, None, {}
        if not a.no_import_check:
            import battle_logs_import_packets as imp
            logs = os.path.dirname(qa_root)
            mview = RepoView(a.repo, a.ref, a.no_git)
            if not a.dry_run:
                check_fresh(mview, a.allow_offline)         # the backup must be what origin has now, not a local commit that was never pushed
            if a.no_git:
                label = 'present in the working tree of the checkout (NOT checked against git: a real move would be refused)'
            where = f'committed state read from {mview.describe()}' + ('; origin was NOT asked whether that is current (a real move asks); `git fetch origin` first for an up-to-date answer' if a.dry_run else '')
            cache = {}          # {path: ((size, mtime), blob id)}: the repeat check after the typed answer re-hashes only what changed
            check = lambda: imp.import_problems(logs, a.repo, mview.commit_full or a.ref, a.no_git, cache=cache, info=info)

        def ask_move(target):
            if not typed('MOVE', f'About to move ONLY Recording_QA ({qa_root})\n  to {target}\nThe videos stay in OneDrive.')():
                return False
            if mview is not None:
                check_fresh(mview, a.allow_offline)         # asked again after the question
            return True
        move_recording_qa(qa_root, a.move_to, repo=a.repo, dry=a.dry_run, confirm=ask_move, import_check=check, import_label=label, import_where=where,
                          videos_dir=a.videos, allow_onedrive_target=a.allow_target_in_onedrive, import_info=info)
        return 0
    view = RepoView(a.repo, a.ref, a.no_git)
    index = build_index(view)
    explicit = to_local(a.videos) if a.videos else None
    if explicit and not os.path.isdir(explicit):
        raise ToolError(f'--videos {a.videos!r} is not a folder')
    vdirs, vwarn = video_dirs(qa_root, explicit)
    videos, where = video_index_all(vdirs), '; '.join(d for d, _ in vdirs) or 'no Battle Logs folder found'
    if a.media_locations:
        ml = [to_local(a.media_locations)]
        if not os.path.isfile(ml[0]):
            raise ToolError(f'--media-locations {a.media_locations!r} is not a file')
    else:
        ml = [os.path.join(d, MEDIA_LOCATIONS) for d, _ in vdirs]
    archive = Archive.load(ml, os.path.abspath(to_local(a.cache_root)) if a.cache_root else None, a.drive_check_cmd)
    vwarn = list(vwarn) + archive.warnings
    decisions = filter_batches(decide(scan_qa(qa_root, videos, where, archive), index), set(a.only) if a.only else None)
    report(decisions, view, qa_root, index, a.verbose, videos_from=vdirs, warnings=vwarn, asked_origin=bool(a.apply and not a.dry_run), archive=archive)
    if a.apply and not a.dry_run:
        check_fresh(view, a.allow_offline)

        def confirm(n, size, batches):
            acc, _ = acceptance(index)          # (apply_deletions has already refused without a valid one)
            word = f'DELETE {acc["games_sha256"][:8]}'
            if not typed(word, f'About to delete {n:,} frame files ({mb(size)}) from {len(batches)} batches: {", ".join(batches)}\n'
                               f'Accepted by {acc["by"]} on {acc["date"]} (games_sha256 {acc["games_sha256"][:8]}...), committed state: {view.describe()}')():
                return False
            check_fresh(view, a.allow_offline)              # asked again after the question: an acceptance withdrawn while it was open still counts
            return True
        res = apply_deletions(decisions, qa_root, index, view=view, only=set(a.only) if a.only else None, confirm=confirm, whole_batches_only=a.whole_batches_only,
                              video_check=lambda game: check_video(game, videos, where, fresh=True, archive=archive))
        return 1 if res[1] or res.skipped else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
