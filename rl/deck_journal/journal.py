#!/usr/bin/env python3
"""Deck version journal (rl/deck_journal/SPEC.md): one append-only record per deck of every version of its list,
what changed, why, and what each test, bot and ladder game said about it. Standard library only; cards only
through lib/card.py's database and the deck-code catalog; no engine binary.

  journal.py add-version --deck STEM --list-file F --origin TEXT --by WHO [--parent ID] [--file DECKFILE]
                         [--origin-source PATH] [--reason TEXT --reason-by WHO --reason-source PATH] [--title T]
  journal.py add-result  --deck STEM --kind played --packet DIR --by WHO [--binding TEXT --version ID]
  journal.py add-result  --deck STEM --kind bot --version ID --source PATH [--deck-path PATH] --by WHO
  journal.py add-result  --deck STEM --kind setup --run FOLDER --by WHO [--only ID,ID] [--corrects FOLDER@COMMIT]
  journal.py add-result  --deck STEM --kind ladder --version ID --export X --predictions DIR [--versions V] --by WHO
  journal.py add-result  --deck STEM --kind ladder-notes --version ID --export X --versions V --by WHO
  journal.py add-result  --deck STEM --kind note --version ID --text T --source PATH --by WHO
  journal.py view  --deck STEM        write journals/<stem>.md from the JSON (never edit the view by hand)
  journal.py check [--deck STEM]      validate every journal: ids, code_cards, append-only against main, view current

Writes happen only through add-version and add-result (or the functions below); each checks that the id is
recomputed from the list, the list passes lib/deck_check.py, the parent exists, the source path exists and is
committed, a bot result's list matches, and nothing earlier changed.
"""
import argparse
import base64
import collections
import copy
import datetime
import json
import os
import re
import subprocess
import sys
import unicodedata
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in (os.path.join(ROOT, "lib"), os.path.join(ROOT, "rl", "results", "ladder_validation")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import card  # noqa: E402  (lib/card.py: the card database)
import card_canon  # noqa: E402
import deck_check  # noqa: E402
import encode_qr  # noqa: E402  (lib/encode_qr.py: the deck-code catalog and byte layout)
import make_predictions as mp  # noqa: E402  (card_list_sha256, harness_bots, floor_bot, wilson, Git)
import read_ladder as rl  # noqa: E402  (load_versions, game_facts, read)

SCHEMA = "deck-journal v1"
JOURNALS = os.path.join(HERE, "journals")
ENERGY_NAMES = {1: "Grass", 2: "Fire", 3: "Water", 4: "Lightning", 5: "Psychic", 6: "Fighting", 7: "Darkness",
                8: "Metal", 9: "Dragon", 10: "Colorless"}
LINE = re.compile(r"^(\d+)\s+(.+?)\s+([A-Z][0-9A-Za-z\-]*\s\d{3})$")
BINDINGS = ("filmed deck code", "catalog, unconfirmed", "his note, unconfirmed")
REVIEWED_TESTERS = os.path.join(HERE, "reviewed_testers.json")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]


class Refused(Exception):
    pass


# ---------------------------------------------------------------- cards and lists
_NAMES = {}


def names():
    """{card id: name}, from lib/card.py's database (never from a packet)."""
    if not _NAMES:
        for _, v in card.load():
            _NAMES[v["id"]] = v["name"]
    return _NAMES


def _clean(text):
    return unicodedata.normalize("NFC", text).replace("’", "'").replace("‘", "'")


def parse_list(text):
    """(energy codes, [(count, id)]) of a deck-file text. Names must be the database's name for the id."""
    energy, pairs, seen = [], [], collections.OrderedDict()
    for raw in _clean(text).replace("﻿", "").splitlines():
        line = re.split(r"(?:^|\s)(?:#|//)", raw, maxsplit=1)[0].strip()
        if not line:
            continue
        if line.lower().startswith("energy:"):
            for e in line[7:].split(","):
                e = e.strip().lower()
                if e not in encode_qr.ENERGY:
                    raise Refused("unknown energy %r" % e)
                energy.append(encode_qr.ENERGY[e])
            continue
        m = LINE.match(line)
        if not m:
            raise Refused("cannot read deck line %r" % raw)
        n, name, cid = int(m[1]), m[2], m[3]
        if cid not in encode_qr.BYID or cid not in names():
            raise Refused("unknown card id %s (%s)" % (cid, name))
        if names()[cid] != name:
            raise Refused("%s is %r in the card database, not %r" % (cid, names()[cid], name))
        seen[cid] = seen.get(cid, 0) + n
    if not energy:
        raise Refused("no Energy line")
    return sorted(set(energy)), [(n, c) for c, n in seen.items()]


def list_lines(energy, pairs):
    """Deck-file lines built from (count, id) pairs, each name taken from the card database for its id."""
    out = ["Energy: " + ", ".join(ENERGY_NAMES[e] for e in sorted(set(energy)))]
    out += ["%d %s %s" % (n, names()[cid], cid) for n, cid in pairs]
    return out


def lines_of(text):
    return list_lines(*parse_list(text))


def list_id(lines):
    """First 12 hex digits of make_predictions.card_list_sha256: the id the predictions files use."""
    return mp.card_list_sha256("\n".join(lines))[:12]


def pairs_of(lines):
    return parse_list("\n".join(lines))[1]


def code_cards(energy, pairs):
    cards = []
    for n, cid in pairs:
        cards += [encode_qr.BYID[cid]["entity_key"]] * n
    return {"energy": sorted(set(energy)), "cards": sorted(cards)}


def decode_payload(payload):
    """The card entities and Energy a deck code holds (layout in lib/encode_qr.py)."""
    try:
        b = base64.b64decode(payload, validate=True)
        i = 0
        nt = b[i]
        i += 1
        cards = []
        for _ in range(nt):
            cards.append("trainer:%06d" % (int.from_bytes(b[i:i + 3], "big") - 10_000_000))
            i += 3
        npk = b[i]
        i += 1
        for _ in range(npk):
            cards.append("pokemon:%06d" % int.from_bytes(b[i:i + 3], "big"))
            i += 3
        ne = b[i]
        i += 1
        energy = list(b[i:i + ne])
        i += ne
    except (ValueError, IndexError) as e:
        raise Refused("cannot read the deck code: %s" % e)
    if i != len(b) or len(energy) != ne:
        raise Refused("the deck code has stray bytes")
    return {"energy": sorted(set(energy)), "cards": sorted(cards)}


def packet_payload(packet_dir):
    """The deck code filmed at the start of the video: key payload, or qr_payload (230258)."""
    p = os.path.join(packet_dir, "QR_DECODE.json")
    if not os.path.exists(p):
        raise Refused("%s has no QR_DECODE.json" % packet_dir)
    with open(p, encoding="utf-8-sig") as fh:
        d = json.load(fh)
    for k in ("payload", "qr_payload", "decoded_payload"):
        if isinstance(d.get(k), str) and d[k]:
            return d[k]
    raise Refused("%s holds no payload or qr_payload" % p)


def _entity_printings(pairs):
    out = collections.defaultdict(collections.Counter)
    for n, cid in pairs:
        out[encode_qr.BYID[cid]["entity_key"]][cid] += n
    return out


def _distance(a, b):
    ca, cb = collections.Counter(a["cards"]), collections.Counter(b["cards"])
    return sum(((ca - cb) + (cb - ca)).values()) + len(set(a["energy"]) ^ set(b["energy"]))


def diff_versions(parent_pairs, pairs):
    """(diff lines, printing_only lines): changes in the cards the game's deck code holds, and same-card printings."""
    pe, ne = _entity_printings(parent_pairs), _entity_printings(pairs)
    removed, added, printing = [], [], []
    for e in sorted(set(pe) | set(ne)):
        a, b = pe.get(e, collections.Counter()), ne.get(e, collections.Counter())
        na, nb = sum(a.values()), sum(b.values())
        common = a & b
        ra, rb = sorted((a - common).elements()), sorted((b - common).elements())
        k = min(len(ra), len(rb), na if nb >= na else nb)   # printing swaps of cards kept in the list
        for x, y in zip(ra[:k], rb[:k]):
            printing.append("%s %s -> %s" % (names()[x], x, y))
        ra, rb = ra[k:], rb[k:]
        for x in ra:
            removed.append("-1 %s %s" % (names()[x], x))
        for y in rb:
            added.append("+1 %s %s" % (names()[y], y))
    return removed + added, sorted(set(printing))


def energy_diff(a, b):
    return (["-Energy: " + ENERGY_NAMES[e] for e in sorted(set(a) - set(b))] +
            ["+Energy: " + ENERGY_NAMES[e] for e in sorted(set(b) - set(a))])


# ---------------------------------------------------------------- git
def _git(root, *args):
    r = subprocess.run(["git", "-c", "safe.directory=*", "-C", root] + list(args), capture_output=True)
    if r.returncode != 0:
        raise Refused("git %s: %s" % (" ".join(args[:2]), r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r.stdout.decode("utf-8", "replace")


def _git_bytes(root, *args):
    r = subprocess.run(["git", "-c", "safe.directory=*", "-C", root] + list(args), capture_output=True)
    if r.returncode != 0:
        raise Refused("git %s: %s" % (" ".join(args[:2]), r.stderr.decode("utf-8", "replace").strip()[:200]))
    return r.stdout


def committed(root, rel, main_ref=None):
    """The last commit touching the path; refuses a path that does not exist, is not tracked, has edits, or whose
    last commit is not an ancestor of main (main_ref, else origin/main, else main)."""
    if not os.path.exists(os.path.join(root, rel)):
        raise Refused("source path does not exist: %s" % rel)
    if not _git(root, "ls-files", "--", rel).strip():
        raise Refused("source path is not committed: %s" % rel)
    dirty = [x for x in _git(root, "status", "--porcelain", "--", rel).splitlines() if not x.startswith("??")]
    if dirty:
        raise Refused("source path has uncommitted changes: %s" % rel)
    commit = _git(root, "log", "-1", "--format=%H", "--", rel).strip()
    main_ref = main_ref or _main_ref(mp.Git(root))
    if main_ref and subprocess.run(["git", "-c", "safe.directory=*", "-C", root, "merge-base", "--is-ancestor", commit,
                                    main_ref], capture_output=True).returncode != 0:
        raise Refused("source path %s was last changed in %s, which is not on main (%s)" % (rel, commit[:8], main_ref))
    return commit


def head(root):
    try:
        return _git(root, "rev-parse", "HEAD").strip()
    except Refused:
        return "no-git"


def _main_ref(git):
    for r in ("origin/main", "main"):
        if git.verify_ref(r):
            return r
    return None


def now():
    return mp.now_utc()


# ---------------------------------------------------------------- the journal file
def new_doc(stem, title):
    return {"schema": SCHEMA, "deck": stem, "title": title, "versions": []}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def find(doc, vid):
    for v in doc["versions"]:
        if v["id"] == vid:
            return v
    raise Refused("no version %s in the journal of %s" % (vid, doc["deck"]))


def check_append_only(old, new, where):
    """Problems if `new` edits, reorders or deletes anything `old` holds (new versions and results may be added)."""
    problems = []
    nv = {v["id"]: v for v in new["versions"]}
    old_ids = [v["id"] for v in old["versions"]]
    if [v["id"] for v in new["versions"]][:len(old_ids)] != old_ids:
        problems.append("%s: an earlier version was removed or reordered" % where)
    for k in ("deck", "schema", "title"):
        if old.get(k) != new.get(k):
            problems.append("%s: %s changed" % (where, k))
    for v in old["versions"]:
        n = nv.get(v["id"])
        if n is None:
            continue
        for k in v:
            if k != "results" and n.get(k) != v[k]:
                problems.append("%s: version %s: %s was changed" % (where, v["id"], k))
        for k in n:
            if k not in v:
                problems.append("%s: version %s: a new key %s was added to an earlier version" % (where, v["id"], k))
        if n.get("results", [])[:len(v["results"])] != v["results"]:
            problems.append("%s: version %s: an earlier result was edited or deleted" % (where, v["id"]))
    return problems


def validate(doc):
    """Ids and code_cards recomputed from each list; parents exist; plays_same_as names an earlier version."""
    problems, seen = [], []
    for v in doc["versions"]:
        try:
            lines = lines_of("\n".join(v["list"]))
            energy, pairs = parse_list("\n".join(v["list"]))
        except Refused as e:
            problems.append("%s: %s" % (v.get("id"), e))
            continue
        if lines != v["list"]:
            problems.append("%s: its list is not in the tool's own form" % v["id"])
        if list_id(lines) != v["id"]:
            problems.append("%s: the id is not the card list's id" % v["id"])
        if code_cards(energy, pairs) != v["code_cards"]:
            problems.append("%s: code_cards differ from the list" % v["id"])
        if v["origin"] == "agent proposal" and v["parent"] is None:
            problems.append("%s: an agent proposal has no parent" % v["id"])
        if v["parent"] is not None and v["parent"] not in seen:
            problems.append("%s: parent %s is not an earlier version" % (v["id"], v["parent"]))
        if v["plays_same_as"] is not None and v["plays_same_as"] not in seen:
            problems.append("%s: plays_same_as %s is not an earlier version" % (v["id"], v["plays_same_as"]))
        seen.append(v["id"])
    return problems


def save(path, doc, root=ROOT, ref="origin/main"):
    """Write the journal after checking it against the copy on disk and origin/main's committed copy (ref=None skips
    the second check; only tests do that)."""
    problems = validate(doc)
    if os.path.exists(path):
        problems += check_append_only(load(path), doc, "the copy on disk")
    if ref:
        rel = os.path.relpath(os.path.abspath(path), root).replace(os.sep, "/")
        git = mp.Git(root)
        use = ref if git.ok and git.verify_ref(ref) else (_main_ref(git) if git.ok else None)
        blob = git.show_bytes(use, rel) if use else None
        if blob:
            problems += check_append_only(json.loads(blob.decode("utf-8")), doc, "%s's committed copy" % use)
    if problems:
        raise Refused("; ".join(problems))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def _reason(reason):
    text, by, source = reason
    return {"text": text, "by": by, "source": source}


# ---------------------------------------------------------------- versions
def _root_id(doc, vid):
    v = find(doc, vid)
    while v["plays_same_as"] is not None:
        v = find(doc, v["plays_same_as"])
    return v["id"]


def now_playing_id(doc):
    """The root id of the NOW PLAYING group (the one with the newest played game), or None."""
    groups = _groups(doc)
    i = _now_index(groups)
    return groups[i][0]["id"] if i is not None else None


def choose_parent(doc, candidates):
    """Among versions that are equally close, the NOW PLAYING one, else the newest (never the oldest)."""
    now = now_playing_id(doc)
    if now is not None:
        for c in candidates:
            if c["id"] == now:
                return c
    return candidates[-1]


def _closest(doc, cc):
    best = min(_distance(v["code_cards"], cc) for v in doc["versions"])
    return choose_parent(doc, [v for v in doc["versions"] if _distance(v["code_cards"], cc) == best])


def add_version(doc, root, *, list_text=None, energy=None, pairs=None, origin, reason, by, commit=None, parent=None,
                file=None, origin_source=None, at=None, check_committed=True, main_ref=None,
                origin_source_is_path=True):
    """Add a version. The id, list, code_cards, diff, printing_only and plays_same_as are computed here."""
    if origin == "agent proposal" and parent is None:
        raise Refused("an agent proposal needs --parent ID: the list it was built on")
    if list_text is not None:
        energy, pairs = parse_list(list_text)
    lines = list_lines(energy, pairs)
    vid = list_id(lines)
    if any(v["id"] == vid for v in doc["versions"]):
        raise Refused("version %s is already in the journal" % vid)
    bad = [m for s, m in deck_check.check(doc["deck"], [(n, names()[c], c) for n, c in pairs]) if s == "ERROR"]
    if bad:
        raise Refused("the list fails lib/deck_check.py: %s" % "; ".join(bad))
    cc = code_cards(energy, pairs)
    file_commit = None
    if file:
        if check_committed:
            file_commit = committed(root, file, main_ref)
        with open(os.path.join(root, file), encoding="utf-8") as fh:
            if mp.card_list_sha256(fh.read())[:12] != vid:       # the file's own text, no Energy-alias clean-up
                raise Refused("%s is not this list (id %s)" % (file, vid))
    if origin_source and check_committed and origin_source_is_path:
        committed(root, origin_source, main_ref)
    if parent is not None:
        par, basis = find(doc, parent), "stated"
    elif doc["versions"]:
        par = _closest(doc, cc)          # the fewest changes; a tie goes to NOW PLAYING, then the newest
        basis = "inferred (fewest cards changed)"
    else:
        par, basis = None, None
    diff, printing = ([], [])
    if par is not None:
        diff, printing = diff_versions(pairs_of(par["list"]), pairs)
        diff = energy_diff(par["code_cards"]["energy"], cc["energy"]) + diff
    same = next((v["id"] for v in doc["versions"] if v["code_cards"] == cc), None)
    entry = {"id": vid, "list": lines, "code_cards": cc, "parent": par["id"] if par else None, "parent_basis": basis,
             "diff": diff, "printing_only": printing, "plays_same_as": same, "origin": origin,
             "origin_source": origin_source, "file": file,
             "file_first_commit_date": _file_date(root, file) if file else None,
             "reason": _reason(reason),
             "added": {"at": at or now(), "by": by, "commit": commit or head(root)}, "results": []}
    doc["versions"].append(entry)
    return entry


def _file_date(root, rel):
    try:
        return _git(root, "log", "--follow", "--diff-filter=A", "--format=%cs", "--", rel).strip().splitlines()[-1]
    except (Refused, IndexError):
        return None


def match_versions(doc, cc):
    """Ids of every version whose code_cards equal these (card sets, never code strings), earliest first."""
    return [v["id"] for v in doc["versions"] if v["code_cards"] == cc]


def version_from_code(doc, root, cc, source, by, commit=None, at=None):
    """A new version for filmed code_cards no version has: inferred parent, reason 'not stated'. Its printings are
    the parent's for cards the parent has, else card_canon's base id."""
    par = _closest(doc, cc) if doc["versions"] else None
    have = _entity_printings(pairs_of(par["list"])) if par else {}
    canon = card_canon.Canon()
    by_entity = collections.defaultdict(list)
    for cid, a in encode_qr.BYID.items():
        by_entity[a["entity_key"]].append(cid)
    pairs = []
    for e, n in sorted(collections.Counter(cc["cards"]).items()):
        pool = collections.Counter(have.get(e, {}))
        for cid, k in sorted(pool.items()):
            take = min(k, n)
            if take:
                pairs.append((take, cid))
                n -= take
        if n:
            base = canon.base_id(sorted(by_entity[e])[0])
            pairs.append((n, base))
    merged = collections.OrderedDict()
    for n, cid in pairs:
        merged[cid] = merged.get(cid, 0) + n
    return add_version(doc, root, energy=cc["energy"], pairs=[(n, c) for c, n in merged.items()],
                       origin="his list (filmed deck code)", origin_source=source, reason=("not stated", by, "none"),
                       by=by, commit=commit, at=at)


# ---------------------------------------------------------------- results
def _result_key(r):
    return (r["kind"], r["source"], r["commit"], r.get("bot") or r.get("video") or r.get("basis") or r.get("section"))


def _append(doc, vid, r):
    v = find(doc, vid)
    key = _result_key(r)
    for x in v["results"]:
        if _result_key(x) == key:
            raise Refused("this result is already filed under %s (same source and commit): %s" % (vid, key[1]))
    v["results"].append(r)
    return r


def _corrected_keys(results, vid):
    """(kind, source, commit) of every result that a later result in this version corrects."""
    return {(c["kind"], c["source"], c["commit"]) for r in results for c in [r.get("corrects")]
            if c and c.get("version") == vid}


def live_results(version):
    """The version's results that no other result corrects (the earlier ones stay in the file)."""
    gone = _corrected_keys(version["results"], version["id"])
    return [r for r in version["results"] if (r["kind"], r["source"], r["commit"]) not in gone]


def _corrected_note(r):
    if not r.get("corrects"):
        return ""
    return " (corrected %s)" % _short_date(r["at"][:10])


def _short_date(iso):
    return "%s %d" % (MONTHS[int(iso[5:7]) - 1], int(iso[8:10]))


def _env(kind, source, commit, by, at=None):
    return {"kind": kind, "at": at or now(), "by": by, "source": source, "commit": commit}


def local_date_of_video(video):
    """The Chicago calendar date of a recording whose iOS file name is a UTC time (YYYYMMDD_HHMMSS...)."""
    m = re.match(r"(\d{4})(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d)", video or "")
    if not m:
        return None
    dt = datetime.datetime(*[int(x) for x in m.groups()], tzinfo=datetime.timezone.utc)
    return dt.astimezone(zoneinfo.ZoneInfo("America/Chicago")).date().isoformat()


PACKET_DATE_KEYS = ("local_match_date", "match_date_local", "match_date", "local_recording_start")


def packet_date(summary, video):
    """The packet's own local match date when it has one; otherwise the video name's UTC time in Chicago."""
    for k in PACKET_DATE_KEYS:
        v = summary.get(k)
        if isinstance(v, str) and re.match(r"\d{4}-\d\d-\d\d", v):
            return v[:10]
    return local_date_of_video(video)


def _outcome_word(v):
    if isinstance(v, dict):
        for k in ("owner_result", "owner", "result"):
            w = _outcome_word(v.get(k))
            if w:
                return w
        return None
    if not isinstance(v, str):
        return None
    s = v.strip().lower()
    if s in ("win", "loss", "draw"):
        return s
    if re.search(r"\b(defeat|loss|lost|lose)\b", s):
        return "loss"
    if re.search(r"\b(win|won|victory)\b", s):
        return "win"
    if re.search(r"\b(draw|tie|tied)\b", s):
        return "draw"
    return None


def played_outcome(summary):
    """(result, key, raw): SUMMARY.json's result, then outcome, then owner_result / method; the raw value is kept.
    The field is read as it stands: nothing is added (no 'conceded' unless the field says win/loss)."""
    for k in ("result", "outcome", "owner_result", "method"):
        w = _outcome_word(summary.get(k))
        if w:
            return w, k, summary.get(k)
    return None, None, None


def add_played(doc, root, packet_rel, by, commit_check=True, binding="filmed deck code", version=None, at=None,
               main_ref=None):
    """One game seen in a review packet, bound to a version by the filmed deck code (or by the weaker bindings)."""
    if binding not in BINDINGS:
        raise Refused("binding must be one of %s" % ", ".join(BINDINGS))
    pdir = os.path.join(root, packet_rel)
    source = packet_rel.rstrip("/") + "/QR_DECODE.json"
    commit = committed(root, source, main_ref) if commit_check else "unchecked"
    cc = decode_payload(packet_payload(pdir))
    if version is None:
        hits = match_versions(doc, cc)
        version = hits[0] if hits else version_from_code(doc, root, cc, source, by, at=at)["id"]
    elif binding == "filmed deck code":
        raise Refused("a version is named only with a weaker binding; the filmed code finds its own version")
    qr = {}
    with open(os.path.join(pdir, "QR_DECODE.json"), encoding="utf-8-sig") as fh:
        qr = json.load(fh)
    video = qr.get("source_video") or os.path.basename(packet_rel.rstrip("/")) + ".MP4"
    summary = {}
    try:
        with open(os.path.join(pdir, "SUMMARY.json"), encoding="utf-8-sig") as fh:
            summary = json.load(fh)
    except (OSError, ValueError):
        pass
    outcome, okey, raw = played_outcome(summary)
    r = _env("played", source, commit, by, at)
    r.update({"video": video, "packet": packet_rel.rstrip("/"), "binding": binding, "result": outcome,
              "result_key": okey, "result_raw": raw, "date": packet_date(summary, video),
              "note": "a game seen in a review packet; not a ladder game unless the Ladder Log has it"})
    return _append(doc, version, r)


def bot_deck_info(v, root, git, main_ref, deck_path=None):
    """The deck a bot result may be filed under: the version's own file, or --deck-path (a file committed on main
    whose raw card list has this version's id). The deck name harness_bots looks for is that file's stem."""
    path = deck_path or v.get("file")
    if not path:
        raise Refused("version %s has no deck file on main: a bot number can only be filed under a list a bot "
                      "could have played from a committed deck file (pass --deck-path PATH)" % v["id"])
    if deck_path:
        committed(root, deck_path, main_ref)
    with open(os.path.join(root, path), "rb") as fh:
        raw = fh.read()
    cl = mp.card_list_sha256(raw.decode("utf-8"))
    if cl[:12] != v["id"]:
        raise Refused("%s is not version %s (its card list is %s)" % (path, v["id"], cl[:12]))
    versions = git.file_versions(path)
    on_main = git.file_versions(path, ref=main_ref) if main_ref else versions
    if not any(x["card_list_sha256"] == cl for x in on_main or []):
        raise Refused("%s as it is now is not committed on %s" % (path, main_ref))
    return {"name": os.path.splitext(os.path.basename(path))[0], "file": path, "version_id": cl[:12],
            "card_list_sha256": cl, "file_sha256": mp.sha256_bytes(raw), "file_versions": versions,
            "deck_path": path}


def _arm_games(folder, arm):
    """Every game of this arm in the run's games.jsonl, whatever the deck (the N of 'n of N')."""
    p = os.path.join(folder, "games.jsonl")
    if not os.path.exists(p):
        return None
    return sum(1 for g in mp.load_jsonl(p) if g.get("arm") == arm)


def add_bot(doc, root, vid, source_rel, by, at=None, deck_path=None, main_ref=None):
    """Bot results from a slow report, exam, replay (folder) or floor (page), built by make_predictions' own
    functions; refused unless the run tested this version's file (or --deck-path's committed file with the same
    card list)."""
    v = find(doc, vid)
    git = mp.Git(root)
    main_ref = main_ref or _main_ref(git)
    deck = bot_deck_info(v, root, git, main_ref, deck_path)
    abs_ = os.path.join(root, source_rel)
    if os.path.isdir(abs_) and not os.path.exists(os.path.join(abs_, "manifest.json")):
        source_rel = source_rel.rstrip("/") + "/" + deck["name"] + ".md"      # a floor folder: this deck's page
        abs_ = os.path.join(root, source_rel)
    commit = committed(root, source_rel, main_ref)
    try:
        if os.path.isdir(abs_):
            bots = mp.harness_bots(abs_, source_rel.rstrip("/"), deck, git, main_ref)
        else:
            bots = [mp.floor_bot(abs_, source_rel, deck, git, main_ref, root)]
    except SystemExit as e:
        raise Refused(str(e))
    main_commit = _git(root, "rev-parse", main_ref).strip() if main_ref else None
    out = []
    for b in bots:
        r = _env("bot", source_rel.rstrip("/"), commit, by, at)
        n_run = _arm_games(abs_, b["arm"]) if os.path.isdir(abs_) else b["n"]
        r.update({"bot": b["id"], "label": b["label"], "run_kind": b["kind"], "arm": b["arm"], "pilot": b["pilot"],
                  "stage": b["source"].get("stage"), "run_name": os.path.basename(source_rel.rstrip("/")),
                  "games_in_run": n_run if n_run is not None else b["n"],
                  "knows_the_panel_lists": bool(b.get("knows_the_panel_lists")),
                  "engine": {"label": b["engine"]["label"], "key": b["engine"].get("key")},
                  "current_engine": bool(b["in_bot_comparison"]), "counts": b["counts"],
                  "n": b["n"], "wins": b["wins"], "ties": b["ties"], "losses": b["losses"],
                  "number_pct": b["number_pct"], "ci95_wilson": b["ci95_wilson"], "games_sha256": b["games_sha256"],
                  "tested": b["source"].get("tested_version") or b["source"].get("deck_check", {}).get("how"),
                  "deck_path": deck["deck_path"], "deck_file_sha256": deck["file_sha256"],
                  "card_list_sha256": deck["card_list_sha256"], "main_commit": main_commit,
                  "note": b.get("comparison_note")})
        out.append(_append(doc, vid, r))
    return out


# ---------------------------------------------------------------- setup tester runs
SETUP_SCHEMA = "setup-tester results v2"
NEEDS_RULING = {"P2": "R1", "P3": "R2"}       # the plan lines held unless run.rulings holds the ruling they need
PLAN_MEASURES = ("P2.any", "P2.both", "P2.g1", "P2.g2", "P3.pawn_lead", "P3.pawn_promo", "P3.grimer_muk", "P4.ko",
                 "P4.win", "P4.late1", "P4.late2p", "P4.never", "P4.nomoment", "P5.ko", "P5.win")
SEATS = ("first", "second", "pooled")
RUN_FIELDS = ("code_sha256", "tester_commit", "tree_clean", "plan_path", "plan_sha256", "rules_commit", "engine_note",
              "seed_base", "deal_rule", "deals_no_knockout", "deals_per_clock", "config", "setup_bench_trigger",
              "setup_bench_reserved", "copycat", "copycat_opp_hand", "undecided_rule", "rulings",
              "not_played_by_script", "acts_on_damage", "clocks")
CLOCK_FIELDS = ("label", "kind", "games", "horizon", "source", "source_sha256", "range_method", "strongest",
                "strongest_source", "strongest_flag", "zero_by_construction")
VERSION_FIELDS = ("label", "list", "list_id", "card_list_sha256", "diff", "path", "setup", "clock", "exact", "p1_exact",
                  "paired_vs_base")
COPYCAT_FIELDS = ("rule", "label", "value_table", "default_value", "fallback", "samples", "disagreement")


def _seat_n(total, seat):
    return total if seat == "pooled" else ((total + 1) // 2 if seat == "first" else total // 2)   # even deals first


def _check_range(rng, where):
    if not (isinstance(rng, list) and len(rng) == 2 and all(isinstance(x, (int, float)) for x in rng)
            and 0 <= rng[0] <= rng[1] <= 1):
        raise Refused("%s: range %r is not 0 <= lo <= hi <= 1" % (where, rng))


def _check_cell(cell, total, where, *, clock, mean=False):
    if not isinstance(cell, dict):
        raise Refused("%s: no figures" % where)
    keys = ("x_no", "x_yes", "n") if clock else ("x", "n")
    for k in keys:
        if not isinstance(cell.get(k), int) or isinstance(cell.get(k), bool):
            raise Refused("%s: %s is missing or not a whole number" % (where, k))
    seat = where.rsplit(".", 1)[1]
    if cell["n"] != _seat_n(total, seat):
        raise Refused("%s: n is %s, but %s deals went %s" % (where, cell["n"], total, seat))
    if clock:
        if not (0 <= cell["x_no"] <= cell["x_yes"] <= cell["n"]):
            raise Refused("%s: needs 0 <= x_no <= x_yes <= n, got %s, %s of %s"
                          % (where, cell["x_no"], cell["x_yes"], cell["n"]))
    elif not mean and not (0 <= cell["x"] <= cell["n"]):
        raise Refused("%s: needs 0 <= x <= n, got x %s of n %s" % (where, cell["x"], cell["n"]))
    elif mean and cell["x"] < 0:
        raise Refused("%s: a mean's total cannot be negative" % where)
    for k in ("wilson", "boot"):
        if k in cell:
            _check_range(cell[k], where)


def _plan_cell(cell, method):
    return {"x_no": cell["x_no"], "x_yes": cell["x_yes"], "n": cell["n"], "range": cell[method],
            "range_method": method}


def _flagged(d, lo, hi):
    return bool((lo > 0 or hi < 0) and abs(d) >= 0.01)


def _read_run(root, folder, main_ref):
    """(commit, results dict, {file: sha256}) of a run folder as the last commit on main left it."""
    folder = folder.rstrip("/")
    commit = _git(root, "log", "-1", "--format=%H", main_ref, "--", folder).strip()
    if not commit:
        raise Refused("not on main: no commit on %s touches %s" % (main_ref, folder))
    if _git(root, "status", "--porcelain", "--", folder).strip():
        raise Refused("%s has uncommitted or untracked files in the working copy" % folder)
    names_ = _git(root, "ls-tree", "-r", "--name-only", commit, "--", folder).splitlines()
    if folder + "/SUPERSEDED.md" in names_:
        raise Refused("%s holds SUPERSEDED.md at %s" % (folder, commit[:8]))
    blobs = {}
    for f in ("results.json", "RESULTS.md"):
        if folder + "/" + f not in names_:
            raise Refused("%s has no %s at %s" % (folder, f, commit[:8]))
        blobs[f] = _git_bytes(root, "show", "%s:%s/%s" % (commit, folder, f))
    try:
        res = json.loads(blobs["results.json"].decode("utf-8"))
    except ValueError as e:
        raise Refused("results.json is not JSON: %s" % e)
    return commit, res, {f: mp.sha256_bytes(b) for f, b in blobs.items()}


def _check_run(res, reviewed_path):
    """Everything about a results.json that must hold before any number is read; returns run, versions."""
    if not isinstance(res, dict) or res.get("schema") != SETUP_SCHEMA:
        raise Refused("schema is not exactly %r" % SETUP_SCHEMA)
    run, versions = res.get("run"), res.get("versions")
    if not isinstance(run, dict) or not isinstance(versions, dict) or not versions:
        raise Refused("results.json has no run or versions")
    for k in RUN_FIELDS:
        if k not in run:
            raise Refused("run.%s is missing" % k)
    for k in COPYCAT_FIELDS:
        if k not in run["copycat"]:
            raise Refused("run.copycat.%s is missing" % k)
    for c, ci in run["clocks"].items():
        for k in CLOCK_FIELDS:
            if k not in ci:
                raise Refused("run.clocks.%s.%s is missing" % (c, k))
    if "p1_lead" not in run["config"]:
        raise Refused("run.config.p1_lead is missing")
    with open(reviewed_path, encoding="utf-8") as fh:
        reviewed = json.load(fh)
    entry = reviewed.get(run["code_sha256"])
    if entry is None:
        raise Refused("the tester's code %s is not reviewed (not in reviewed_testers.json)" % run["code_sha256"][:12])
    if entry.get("tester_commit") != run["tester_commit"]:
        raise Refused("tester_commit %s differs from the reviewed one %s" % (run["tester_commit"], entry.get("tester_commit")))
    if run["tree_clean"] is not True:
        raise Refused("tree_clean is not true: the tester ran with uncommitted edits")
    if "base" not in versions:
        raise Refused("the run has no base version")
    seen = {}
    for name, v in versions.items():
        for k in VERSION_FIELDS:
            if k not in v:
                raise Refused("version %s: %s is missing" % (name, k))
        try:
            mine = list_id(lines_of("\n".join(v["list"])))
        except Refused as e:
            raise Refused("version %s: its list cannot be read: %s" % (name, e))
        csha = v["card_list_sha256"]
        if not (mine and v["list_id"] and isinstance(csha, str) and csha):
            raise Refused("version %s: an id is null" % name)
        if not (mine == v["list_id"] == csha[:12]):
            raise Refused("version %s: the ids disagree: the list gives %s, list_id %s, card_list_sha256 %s"
                          % (name, mine, v["list_id"], csha[:12]))
        if mine in seen:
            raise Refused("versions %s and %s share the id %s" % (seen[mine], name, mine))
        seen[mine] = name
        if "P1" not in v["setup"] or not all(s in v["setup"]["P1"] for s in SEATS):
            raise Refused("version %s has no setup.P1" % name)
        if not isinstance(v["p1_exact"], (int, float)):
            raise Refused("version %s has no p1_exact" % name)
        for m, cells in v["setup"].items():
            for s in SEATS:
                _check_cell(cells.get(s), run["deals_no_knockout"], "%s.setup.%s.%s" % (name, m, s), clock=False,
                            mean=(m == "G5.n5"))
        for c, ms in v["clock"].items():
            if c not in run["clocks"]:
                raise Refused("version %s has the clock %s, which run.clocks does not describe" % (name, c))
            for m in PLAN_MEASURES:
                if m not in ms:
                    raise Refused("version %s: clock %s has no %s" % (name, c, m))
            for m, cells in ms.items():
                for s in SEATS:
                    if m == "given_moment":
                        continue
                    _check_cell(cells.get(s), run["deals_per_clock"], "%s.%s.%s.%s" % (name, c, m, s), clock=True)
    return run, versions, seen


def _clock_blocks(v, run, kind_of):
    plan, desc = {}, {}
    for c, ms in v["clock"].items():
        method = "boot" if kind_of[c] == "recorded" else "wilson"
        plan[c], desc[c] = {}, {}
        for m, cells in ms.items():
            if m == "given_moment":
                continue
            out = {s: _plan_cell(cells[s], method) for s in SEATS}
            (plan if m in PLAN_MEASURES else desc)[c][m] = out
    return plan, desc


def _comparisons(name, versions, base_name):
    """Same-deal differences: direct against the base, inverted for the base itself, none between two others."""
    def build(w, sign):
        setup, clock = {}, {}
        for m, seats in w["paired_vs_base"].items():
            setup[m] = {s: ([d, lo, hi] if sign > 0 else [-d, -hi, -lo]) for s, (d, lo, hi) in seats.items()}
        for c, ms in w["clock"].items():
            for m, cells in ms.items():
                if m == "given_moment" or "diff" not in cells:
                    continue
                d, lo, hi = cells["diff"]["pooled"]
                d, lo, hi = (d, lo, hi) if sign > 0 else (-d, -hi, -lo)
                clock.setdefault(c, {})[m] = {"diff": [d, lo, hi], "flag": _flagged(d, lo, hi)}
        return setup, clock
    out = []
    if name != base_name:
        setup, clock = build(versions[name], +1)
        out.append({"against": versions[base_name]["list_id"], "against_name": base_name, "how": "direct",
                    "setup": setup, "clock": clock})
    else:
        for other, w in versions.items():
            if other != base_name:
                setup, clock = build(w, -1)
                out.append({"against": w["list_id"], "against_name": other, "how": "inverted",
                            "setup": setup, "clock": clock})
    return out


def _setup_result(doc, folder, commit, main_commit, files, run, versions, name, by, at, only, ids):
    v = versions[name]
    base = versions["base"]
    kinds = {c: ci["kind"] for c, ci in run["clocks"].items()}
    plan, desc_clock = _clock_blocks(v, run, kinds)
    rulings = run["rulings"]
    held = sorted(m for m, need in NEEDS_RULING.items() if need not in rulings)
    setup = v["setup"]
    r = _env("setup", folder, commit, by, at)
    r.update({
        "main_commit": main_commit, "files_sha256": files, "run_version": name, "run_label": v["label"],
        "run_base": {"name": "base", "id": base["list_id"]},
        "also_in_run": [{"name": n, "id": w["list_id"]} for n, w in versions.items() if w["list_id"] not in ids],
        "tester": {"code_sha256": run["code_sha256"], "tester_commit": run["tester_commit"],
                   "plan_path": run["plan_path"], "plan_sha256": run["plan_sha256"]},
        "engine": {"rules_commit": run["rules_commit"], "note": run["engine_note"]},
        "seeds": {"seed_base": run["seed_base"], "deal_rule": run["deal_rule"]},
        "deals": {"no_knockout": run["deals_no_knockout"], "per_clock": run["deals_per_clock"]},
        "config": {"pawniard_bench": run["config"]["pawniard_bench"],
                   "setup_bench": {"trigger": run["setup_bench_trigger"], "reserved": run["setup_bench_reserved"]},
                   "copycat": {"rule": run["copycat"]["rule"], "label": run["copycat"]["label"],
                               "value_table": run["copycat"]["value_table"],
                               "default_value": run["copycat"]["default_value"],
                               "fallback": run["copycat"]["fallback"], "samples": run["copycat"]["samples"],
                               "opp_hand": run["copycat_opp_hand"],
                               "disagreement": run["copycat"]["disagreement"].get(name)},
                   "all": run["config"]},
        "p1": {"pokemon": run["config"]["p1_lead"], "exact": v["p1_exact"], "simulated": setup["P1"]},
        "clocks": {c: {k: ci[k] for k in CLOCK_FIELDS} for c, ci in run["clocks"].items()},
        "plan_lines": {c: {m: plan[c][m] for m in PLAN_MEASURES} for c in plan},
        "held": held, "rulings": rulings, "undecided_rule": run["undecided_rule"],
        "descriptive": {
            "setup": {m: {s: {"x": cells[s]["x"], "n": cells[s]["n"], "wilson": cells[s]["wilson"]} for s in SEATS}
                      for m, cells in sorted(setup.items()) if m not in ("P1", "G5.n5")},
            "setup_mean": {"G5.n5": setup["G5.n5"]} if "G5.n5" in setup else {},
            "clock": desc_clock, "exact": v["exact"]},
        "comparisons": _comparisons(name, versions, "base"),
        "not_valued": {"not_played_by_script": run["not_played_by_script"], "acts_on_damage": run["acts_on_damage"]},
    })
    gm = {c: {m: {s: {"x": cells[s]["x"], "n": cells[s]["n"], "boot": cells[s].get("boot")} for s in SEATS}
              for m, cells in v["clock"][c]["given_moment"].items()} for c in v["clock"] if "given_moment" in v["clock"][c]}
    r["plan_given_moment"] = gm
    return r


def add_setup_run(doc, root, folder, by, *, only=None, corrects=None, main_ref=None, reviewed=None, at=None):
    """One `setup` result per version of a committed, reviewed setup-tester run, filed under each version's card-list
    id. The run is read from the last commit on main that touches its folder; nothing is written unless every check
    passes (a refusal leaves the journal as it was). A tester run never creates a version."""
    git = mp.Git(root)
    main_ref = main_ref or _main_ref(git)
    if not main_ref:
        raise Refused("no main branch to read the run from")
    folder = folder.rstrip("/")
    commit, res, files = _read_run(root, folder, main_ref)
    run, versions, by_id = _check_run(res, reviewed or REVIEWED_TESTERS)
    have = {v["id"] for v in doc["versions"]}
    want = [i for i in (only or by_id)]
    for i in want:
        if i not in by_id:
            raise Refused("--only names %s, which the run did not test" % i)
    missing = [i for i in want if i not in have]
    if missing:
        raise Refused("the journal has no version %s; add each first, a tester run never creates one:\n%s" % (
            ", ".join(missing), "\n".join(
                '  add-version --origin "agent proposal" --parent ID --reason ... (list of %s in the run: %s)'
                % (i, by_id[i]) for i in missing)))
    main_commit = _git(root, "rev-parse", main_ref).strip()
    cname = corrects.partition("@") if corrects else None
    if cname and (cname[0].rstrip("/") != folder or not cname[2]):
        raise Refused("--corrects must name %s@COMMIT" % folder)
    results = []
    for i in want:
        name = by_id[i]
        earlier = [x for x in find(doc, i)["results"] if x["kind"] == "setup" and x["source"] == folder
                   and x["run_version"] == name]
        if any(x["commit"] == commit for x in earlier):
            raise Refused("this run (%s at %s) is already filed under %s" % (folder, commit[:8], i))
        r = _setup_result(doc, folder, commit, main_commit, files, run, versions, name, by, at, want, set(want))
        if earlier:
            target = [x for x in earlier if cname and x["commit"].startswith(cname[2])]
            if not target:
                raise Refused("%s is already filed under %s at %s; filing it at another commit needs "
                              "--corrects %s@<that commit>" % (folder, i, earlier[-1]["commit"][:8], folder))
            r["corrects"] = {"kind": "setup", "source": folder, "commit": target[-1]["commit"], "version": i}
        elif cname:
            raise Refused("--corrects names %s, but nothing from it is filed under %s" % (corrects, i))
        results.append((i, r))
    for i, r in results:
        _append(doc, i, r)
    return [r for _, r in results]


def add_note(doc, root, vid, text, source, by, at=None, main_ref=None):
    commit = committed(root, source, main_ref)
    r = _env("note", source, commit, by, at)
    r["text"] = text
    r["basis"] = text[:40]
    return _append(doc, vid, r)


def _record(rows):
    w = sum(1 for g in rows if g["result"] == "W")
    return {"wins": w, "losses": len(rows) - w}


def _ladder(doc, vid, games, basis, source, commit, by, at):
    counted = [g for g in games if g["result"] in ("W", "L")]
    tests = [g for g in counted if g["class"] == "test"]
    feed = [g for g in counted if g["class"] == "feedback"]
    r = _env("ladder", source, commit, by, at)
    r.update({"basis": basis, "test": _record(tests), "feedback": _record(feed),
              "concession_wins": sum(1 for g in counted if g["result"] == "W" and g.get("concession")),
              "cards": dict(collections.Counter((g.get("cards") or "not checked").split(":")[0] for g in counted)),
              "games": games})
    return _append(doc, vid, r)


def ladder_from_notes(doc, vid, games_by_section, notes, source, by, commit, at=None):
    """A version with no predictions file: the games whose version notes name its id, each as feedback, with the
    Ladder Log result. No other tie logic. `notes` is the parsed versions.json object (or read_ladder's notes)."""
    parsed, _ = rl.parse_notes(notes) if "games" in notes or not all(isinstance(x, dict) for x in notes.values()) \
        else (notes, [])
    games = []
    for key, n in sorted(parsed.items()):
        if n.get("version") != vid or str(n.get("cards", "")).lower().startswith("mismatch"):
            continue
        doc_id, _, gid = key.partition("/")
        g = next((x for x in games_by_section.get(doc_id, []) if isinstance(x, dict) and x.get("id") == gid), None)
        if g is None:
            continue
        f, why = rl.game_facts(doc_id, g, n)
        if f is None:
            continue
        games.append({"game": key, "section": doc_id, "result": f["result"], "opponent": f["opp"], "class": "feedback",
                      "tie": "confirmed by a version note", "concession": f["concession"],
                      "cards": n.get("cards"), "evidence": n.get("evidence")})
    return _ladder(doc, vid, games, "version notes (no predictions file)", source, commit, by, at)


def ladder_from_reading(doc, vid, reading, source, by, commit, at=None):
    """A counting reading by read_ladder.py (its result object): this version's rows, test or feedback."""
    groups = [g for k, g in reading["groups"].items() if k.endswith("@" + vid)]
    if len(groups) != 1:
        raise Refused("the reading has no group for version %s" % vid)
    games = [{"game": r["key"], "section": r["doc"], "result": r["result"], "opponent": r["opp"], "class": r["class"],
              "tie": r["tie"], "concession": bool(r["concession"]), "cards": r["cards"]} for r in groups[0]["rows"]]
    return _ladder(doc, vid, games, "counting reading", source, commit, by, at)


# ---------------------------------------------------------------- the view
def _groups(doc):
    roots = collections.OrderedDict((v["id"], [v]) for v in doc["versions"] if v["plays_same_as"] is None)
    for v in doc["versions"]:
        if v["plays_same_as"] is not None:
            root = v["plays_same_as"]
            while root not in roots:
                root = find(doc, root)["plays_same_as"]
            roots[root].append(v)
    return list(roots.values())


def _vdate(r):
    """(month, day) of a played game: the stored local date, else the UTC video name in Chicago."""
    d = r.get("date") or local_date_of_video(r.get("video"))
    return (int(d[5:7]), int(d[8:10])) if d else None


def _span(dates):
    a, b = min(dates), max(dates)
    if a == b:
        return "%s %d" % (MONTHS[a[0] - 1], a[1])
    return ("%s %d-%d" % (MONTHS[a[0] - 1], a[1], b[1])) if a[0] == b[0] else \
           "%s %d-%s %d" % (MONTHS[a[0] - 1], a[1], MONTHS[b[0] - 1], b[1])


def _plain_diff(diff):
    """'1 Copycat out, 1 Lucky Ice Pop in; Alolan Grimer A3 110 in place of B2 096 (a different card)'."""
    outs, ins, energy = [], [], []
    for d in diff:
        if d[1:].startswith("Energy: "):
            energy.append("Energy %s %s" % (d[9:], "out" if d[0] == "-" else "in"))
            continue
        name, cid = re.match(r"^[-+]1 (.+?) (\S+ \d{3})$", d).groups()
        (outs if d[0] == "-" else ins).append((name, cid))
    swaps = []
    for name, old in list(outs):
        new_ = next((i for n, i in ins if n == name), None)
        if new_:
            swaps.append("%s %s in place of %s (a different card)" % (name, new_, old))
            outs.remove((name, old))
            ins.remove((name, new_))
    plain = ["%d %s out" % (c, n) for n, c in sorted(collections.Counter(n for n, _ in outs).items())]
    plain += ["%d %s in" % (c, n) for n, c in sorted(collections.Counter(n for n, _ in ins).items())]
    parts = [", ".join(plain + energy)] if plain or energy else []
    return "; ".join(parts + swaps)


def _pct(x):
    return "%.1f%%" % x


def _now_index(groups):
    """Index of the group with the newest played game (ties to the later group), or None."""
    dates = []
    for g in groups:
        ds = [x for x in (_vdate(r) for v in g for r in v["results"] if r["kind"] == "played") if x]
        dates.append(max(ds) if ds else None)
    return max((i for i, d in enumerate(dates) if d), key=lambda i: (dates[i], i), default=None)


def _vname(v):
    """How the view names a version in a 'Changed from' line."""
    m = re.match(r"(\d+)-", (v.get("file") or "").split("/")[-1])
    return "the deck-%s file" % m[1] if v["origin"] == "deck file on main" and m else v["id"]


# ---- setup numbers in plain words
SETUP_WORDS = {"P2.any": "at least one Glimmora attacks", "P2.both": "both Glimmora attack",
               "P2.g1": "the first Glimmora attacks", "P2.g2": "the second Glimmora attacks",
               "P4.late1": "not ready, ready 1 turn late", "P4.late2p": "not ready, ready 2 or more turns late",
               "P4.never": "the moment came and Kingambit was never ready", "P4.nomoment": "their strongest is never in reach",
               "P3.pawn_lead": "Pawniard forced to lead", "P3.pawn_promo": "a Pawniard-line Pokémon promoted, nothing else left",
               "P3.grimer_muk": "Alolan Grimer or Muk in front",
               "P4.ko": "Kingambit ready to knock out their strongest", "P4.win": "ready, and the knockout wins outright",
               "P5.ko": "ready then or later (before they reach 3 points), knocks out their strongest",
               "P5.win": "ready then or later, wins outright"}
CLOCK_ORDER = ("his", "fast", "medium", "slow")
PACE_NAMES = {"fast": "fast", "medium": "medium", "slow": "slow"}
FLAG_ORDER = ("P4.ko", "P4.win", "P5.ko", "P5.win", "P2.any", "P2.both", "P2.g1", "P2.g2", "P3.pawn_lead",
              "P3.pawn_promo", "P3.grimer_muk", "P4.late1", "P4.late2p", "P4.never", "P4.nomoment")


def _rng(cell):
    return "%.1f-%.1f" % (100 * cell["range"][0], 100 * cell["range"][1])


def _cell_text(cell, seat, zero, v2, marks):
    if zero is not None and seat in zero:
        return "zero by construction"
    s = "%s (%s)" % (_pct(100.0 * cell["x_no"] / cell["n"]), _rng(cell))
    if v2 and cell["x_yes"] != cell["x_no"]:
        s += " [%s as yes]" % _pct(100.0 * cell["x_yes"] / cell["n"])
        marks.append(1)
    return s


def _seats_text(r, clock, measure, marks):
    zero = r["clocks"][clock]["zero_by_construction"].get(measure)
    v2 = str(r.get("undecided_rule", "")).startswith("v2")
    cells = r["plan_lines"][clock][measure]
    return "going first %s, second %s" % tuple(_cell_text(cells[s], s, zero, v2, marks) for s in ("first", "second"))


def _hp_range(r, clock):
    hps = [x["hp"] for x in r["clocks"][clock]["strongest"]]
    return "%d-%d" % (min(hps), max(hps))


def _pace_name(r, clock):
    s = r["clocks"][clock]["strongest"][0]
    kind = {3: "Mega ex", 2: "ex"}.get(s["points"], "Pokémon")
    text = "%s, a %d-HP %s" % (PACE_NAMES[clock], s["hp"], kind)
    return text + (", knockouts on their turns 3/5/7" if clock == "slow" else "")


def _card_counts(diff):
    outs, ins = collections.Counter(), collections.Counter()
    for d in diff:
        if d[1:].startswith("Energy: "):
            continue
        name = re.match(r"^[-+]1 (.+?) \S+ \d{3}$", d)[1]
        (outs if d[0] == "-" else ins)[name] += 1
    return outs, ins


def _setup_lines(doc, group, ref, setup):
    r, vid = setup
    root = group[0]
    held = set(r["held"])
    v2 = str(r.get("undecided_rule", "")).startswith("v2")
    marks = []
    folder = r["source"].split("/")[-1]
    dis = r["config"]["copycat"].get("disagreement") or {}
    dtxt = ("; the fallback rule would play it differently in %s of its decisions"
            % _pct(100.0 * dis["disagree"] / dis["decisions"])) if dis.get("decisions") else ""
    L = ["  Setup odds (setup tester, run %s at %s%s; a script playing your plan, not a win rate; Copycat played by your "
         "valuation, approximated (value table in the run's RESULTS.md)%s)%s:"
         % (folder, r["commit"][:7], (", on " + vid) if vid != root["id"] else "", dtxt, _corrected_note(r))]
    p1 = "P1 Regigigas leads: %s (exact)." % _pct(100.0 * r["p1"]["exact"])
    his = "his"
    if "P2" not in held:
        p1 += " P2 a Glimmora gets its turn (it attacks at least once), your games' pace: %s." % "; ".join(
            "%s: %s" % (SETUP_WORDS[m], _seats_text(r, his, m, marks)) for m in ("P2.any", "P2.both"))
    L.append("    " + p1)
    if held:
        what = " and ".join({"P2": "P2 a Glimmora's turn", "P3": "P3 the plan broken in front"}[h] for h in sorted(held))
        L.append("    %s: held until a rule is settled (the run records no ruling on it)." % what)
    if "P3" not in held:
        L.append("    P3 the plan broken in front, by cause, your games' pace: %s." % "; ".join(
            "%s: %s" % (SETUP_WORDS[m], _seats_text(r, his, m, marks)) for m in ("P3.pawn_lead", "P3.pawn_promo", "P3.grimer_muk")))
    L.append("    P4-P5, your games' pace (their strongest as your opponents showed it: %s HP): Kingambit ready when the Blade "
             "can knock it out (P4): knocks out their strongest: %s; wins outright (a lower bound): %s; and ready then or later, "
             "before they reach 3 points (P5): knocks out their strongest: %s; wins outright: %s." % (
                 _hp_range(r, his), _seats_text(r, his, "P4.ko", marks), _seats_text(r, his, "P4.win", marks),
                 _seats_text(r, his, "P5.ko", marks), _seats_text(r, his, "P5.win", marks)))
    paces = "; ".join("%s: knocks out their strongest: %s, wins outright (a lower bound): %s" % (
        _pace_name(r, c), _seats_text(r, c, "P4.ko", marks), _seats_text(r, c, "P4.win", marks))
        for c in ("fast", "medium", "slow"))
    L.append("    P4, set paces (assumed opponents), %s; other clocks: in the run's RESULTS.md." % paces)
    if marks:
        L[-1] += " [x% as yes] counts the games whose recording stops early as yes; the main figure counts them as no."
    # against
    ref_id = ref["id"]
    comp = next((c for c in r["comparisons"] if c["against"] == ref_id), None)
    if comp is None:
        L.append("    Against what you play (%s), same deals: no same-deal comparison with %s in this run." % (ref_id, ref_id))
    else:
        flags = []
        for c in CLOCK_ORDER:
            ms = comp["clock"].get(c, {})
            for m in FLAG_ORDER:
                if m in ms and ms[m]["flag"]:
                    d, lo, hi = ms[m]["diff"]
                    flags.append("%s pace, %s: %+.1f points (%.1f to %.1f)" % (
                        c if c != "his" else "your games'", SETUP_WORDS.get(m, m), 100 * d, 100 * lo, 100 * hi))
        if flags:
            shown = "; ".join(flags[:3]) + (" and %d more in RESULTS.md" % (len(flags) - 3) if len(flags) > 3 else "")
        else:
            shown = "no plan line moved by 1 point or more with a range that excludes 0"
        L.append("    Against what you play (%s), same deals: %s." % (ref_id, shown))
    # not valued
    nv = r["not_valued"]
    outs, ins = _card_counts(_diff_between(ref, root))
    changed = ["%d %s out" % (n, c) for c, n in sorted(outs.items()) if c in nv["not_played_by_script"]]
    changed += ["%d %s in" % (n, c) for c, n in sorted(ins.items()) if c in nv["not_played_by_script"]]
    in_list = [c for c in nv["acts_on_damage"] if any(" %s " % c in " %s " % x for x in root["list"][1:])]
    if changed or in_list:
        s = "    Not valued here (the script never plays them; they count as blank cards): %s." % (
            ", ".join(changed) if changed else "no changed card")
        if in_list:
            s += " %s %s on damage; this tester counts knockouts, not damage." % (
                ", ".join(in_list), "acts" if len(in_list) == 1 else "act")
        L.append(s)
    k = r["descriptive"]["setup"]["K2.t3"]
    L.append("    Speed, descriptive only (speed is not this deck's goal; here Pawniard is benched at once): Kingambit in play "
             "by your turn 3: going first %s (%s), second %s (%s)." % (
                 _pct(100.0 * k["first"]["x"] / k["first"]["n"]), "%.1f-%.1f" % tuple(100 * x for x in k["first"]["wilson"]),
                 _pct(100.0 * k["second"]["x"] / k["second"]["n"]), "%.1f-%.1f" % tuple(100 * x for x in k["second"]["wilson"])))
    return L


def _diff_between(ref, v):
    return diff_versions(pairs_of(ref["list"]), pairs_of(v["list"]))[0] if ref["id"] != v["id"] else []


# ---- bots in plain words
def _bot_name(r):
    return r["bot"].split("_")[0].split("@")[0]


def _bot_lines(entries, prefix):
    """entries: [(version id, result)] of one version; prefix(vid) names the version in a merged block."""
    L = []
    cur = [(vid, r) for vid, r in entries if r["current_engine"]]
    old = [(vid, r) for vid, r in entries if not r["current_engine"]]
    for vid, r in cur:
        who = _bot_name(r)
        what = "%s (%s, %s, current engine): %s (95%% range %s-%s); %s games %d of %d" % (
            who, r.get("stage") or r["run_kind"], r.get("run_name") or r["source"].split("/")[-1], _pct(r["number_pct"]),
            r["ci95_wilson"][0], r["ci95_wilson"][1], who, r["n"], r.get("games_in_run", r["n"]))
        if r.get("knows_the_panel_lists"):
            what += "; %s knows the panel's lists, so its number is the optimistic end" % who
        if r["run_kind"] == "floor":
            what += "; counts wins only (a draw is not a win)"
        L.append(prefix(vid) + what + _corrected_note(r))
    by_vid = collections.OrderedDict()
    for vid, r in old:
        by_vid.setdefault(vid, []).append(r)
    for vid, rs in by_vid.items():
        sets = len({r["games_sha256"] for r in rs})
        lo, hi = min(r["number_pct"] for r in rs), max(r["number_pct"] for r in rs)
        L.append(prefix(vid) + "older engine, kept for the record and not compared: %d results on %d game sets, numbers "
                 "from %s to %s" % (len(rs), sets, _pct(lo), _pct(hi)))
        for r in rs:
            if r["run_kind"] == "floor":
                L.append(prefix(vid) + "%s floor, older engine: %s of %d games; counts wins only (a draw is not a win)"
                         % (_bot_name(r), _pct(r["number_pct"]), r["n"]))
    return L


def _block(doc, group, label):
    root = group[0]
    ids = [v["id"] for v in group]
    live = [(v["id"], r) for v in group for r in live_results(v)]
    results = [r for _, r in live]
    L = []
    played = [r for r in results if r["kind"] == "played"]
    head_ = "%s  %s" % (label, root["id"])
    if root["origin"] == "deck file on main":
        stem = root["file"].split("/")[-1]
        num = re.match(r"(\d+)-", stem)
        d = root.get("file_first_commit_date")
        mo = (MONTHS[int(d[5:7]) - 1] + " %d" % int(d[8:10])) if d else None
        head_ += "  the %s file%s" % ("deck-" + num[1] if num else stem, (" (%s)" % mo) if mo else "")
    if played:
        dates = [x for x in (_vdate(r) for r in played) if x]
        bind = sorted({r["binding"] for r in played})
        how = "from the deck code on video" if bind == ["filmed deck code"] else "binding: " + ", ".join(bind)
        head_ += "  (in %d of your games%s, %s)" % (len(played), ", " + _span(dates) if dates else "", how)
    L.append(head_)
    if len(group) > 1:
        L.append("  Also written with other printings of the same cards (plays the same): " + ", ".join(ids[1:]) + ".")
    now = now_playing_id(doc)
    ref = None
    if root["parent"] is None:
        L.append("  First version recorded.")
    else:
        par = find(doc, root["parent"])
        ref = find(doc, now) if root["origin"] == "agent proposal" and now and now != root["id"] else par
        d = _plain_diff(_diff_between(ref, root) if ref is not par else root["diff"])
        built = " (built on %s)" % par["id"] if ref is not par else ""
        L.append("  Changed from %s: %s%s." % (_vname(ref), d if d else "no card changes (printings only)", built))
    rz = root["reason"]
    L.append("  Why: %s." % rz["text"] if rz["text"] == "not stated" else
             "  Why: %s (%s)." % (rz["text"].rstrip("."), rz["by"]))
    setups = [(r, vid) for vid, r in live if r["kind"] == "setup"]
    if setups and ref is None:
        ref = root
    if setups:
        L += _setup_lines(doc, group, ref, setups[-1])
    else:
        L.append("  Setup odds: not computed yet.")
    merged = len(group) > 1
    prefix = (lambda vid: "(played on %s) " % vid) if merged else (lambda vid: "")
    items = _bot_lines([(vid, r) for vid, r in live if r["kind"] == "bot"], prefix)
    if not items:
        L.append("  Bots: none on this list yet.")
    for i, it in enumerate(items):
        L.append(("  Bots: " if i == 0 else "        ") + it + ".")
    lad = [r for r in results if r["kind"] == "ladder"]
    if lad:
        r = [x for x in lad if x["basis"] == "counting reading"][-1:] or lad[-1:]
        r = r[0]
        nt, nf = sum(r["test"].values()), sum(r["feedback"].values())
        L.append("  Your ladder games (%s): test %d-%d (%d games), feedback %d-%d (%d games); wins by concession "
                 "(full wins): %d." % (r["basis"], r["test"]["wins"], r["test"]["losses"], nt, r["feedback"]["wins"],
                                       r["feedback"]["losses"], nf, r["concession_wins"]))
    else:
        L.append("  Your ladder games: none logged.")
    for n in [r for r in results if r["kind"] == "note"][-2:]:
        L.append("  Note: %s%s" % (n["text"], _corrected_note(n)))
    return "\n".join(L)


def render(doc):
    """The plain-words view: newest version first; the same input always gives the same text."""
    groups = _groups(doc)
    now_i = _now_index(groups)
    out = ["%s: %d list%s recorded" % (doc["title"], len(groups), "" if len(groups) == 1 else "s")]
    for i in reversed(range(len(groups))):
        if now_i is not None:
            label = "NOW PLAYING" if i == now_i else ("OLDER" if i < now_i else "LISTED")
        else:
            label = "NEWEST" if i == len(groups) - 1 else "OLDER"
        out.append(_block(doc, groups[i], label))
    return "\n\n".join(out) + "\n"


# ---------------------------------------------------------------- command line
def _path(stem, jdir=None):
    return os.path.join(jdir or JOURNALS, stem + ".json")


def _doc_for(args, create):
    p = _path(args.deck, args.dir)
    if os.path.exists(p):
        return load(p), p
    if not create:
        raise Refused("no journal for %s" % args.deck)
    return new_doc(args.deck, args.title or args.deck), p


def _write_view(doc, p):
    with open(p[:-5] + ".md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(doc))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("add-version", "add-result", "view", "check"):
        s = sub.add_parser(name)
        s.add_argument("--deck", required=(name != "check"))
        s.add_argument("--dir", help="journals folder (default rl/deck_journal/journals)")
        s.add_argument("--by")
        s.add_argument("--title")
        s.add_argument("--version")
        if name == "add-version":
            s.add_argument("--list-file", required=True)
            s.add_argument("--origin", required=True)
            s.add_argument("--parent")
            s.add_argument("--file")
            s.add_argument("--origin-source")
            s.add_argument("--reason", default="not stated")
            s.add_argument("--reason-by")
            s.add_argument("--reason-source", default="none")
        if name == "add-result":
            s.add_argument("--kind", required=True,
                           choices=["played", "bot", "setup", "ladder", "ladder-notes", "note"])
            s.add_argument("--packet")
            s.add_argument("--binding", default="filmed deck code")
            s.add_argument("--source")
            s.add_argument("--run")
            s.add_argument("--only")
            s.add_argument("--corrects")
            s.add_argument("--deck-path")
            s.add_argument("--export")
            s.add_argument("--predictions")
            s.add_argument("--versions")
            s.add_argument("--text")
    a = ap.parse_args(argv)
    try:
        return _run(a)
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    except SystemExit as e:
        if isinstance(e.code, str):
            print("REFUSED: %s" % e.code, file=sys.stderr)
            return 2
        raise


def _run(a):
    if a.cmd == "check":
        bad = 0
        stems = [a.deck] if a.deck else sorted(f[:-5] for f in os.listdir(a.dir or JOURNALS) if f.endswith(".json"))
        for stem in stems:
            p = _path(stem, a.dir)
            doc = load(p)
            problems = validate(doc)
            git = mp.Git(ROOT)
            use = _main_ref(git) if git.ok else None
            blob = git.show_bytes(use, os.path.relpath(p, ROOT).replace(os.sep, "/")) if use else None
            if blob:
                problems += check_append_only(json.loads(blob.decode("utf-8")), doc, use + "'s copy")
            md = p[:-5] + ".md"
            if not os.path.exists(md) or open(md, encoding="utf-8").read() != render(doc):
                problems.append("the view is not current: run journal.py view")
            print("%s: %s" % (stem, "ok" if not problems else "; ".join(problems)))
            bad += bool(problems)
        return 1 if bad else 0
    if not a.by and a.cmd != "view":
        raise Refused("--by is required (who is writing)")
    doc, p = _doc_for(a, create=(a.cmd == "add-version"))
    if a.cmd == "view":
        _write_view(doc, p)
        print("wrote " + p[:-5] + ".md")
        return 0
    if a.cmd == "add-version":
        with open(a.list_file, encoding="utf-8") as fh:
            text = fh.read()
        e = add_version(doc, ROOT, list_text=text, origin=a.origin, file=a.file, origin_source=a.origin_source,
                        parent=a.parent, reason=(a.reason, a.reason_by or a.by, a.reason_source), by=a.by,
                        origin_source_is_path=not (a.origin_source and " " in a.origin_source))
        print("added version %s" % e["id"])
    else:
        _add_result(doc, a)
    save(p, doc, ROOT)
    _write_view(doc, p)
    return 0


def _add_result(doc, a):
    k = a.kind
    if k == "played":
        r = add_played(doc, ROOT, a.packet, a.by, binding=a.binding, version=a.version)
        print("filed a played game under %s" % [v["id"] for v in doc["versions"] if r in v["results"]][0])
    elif k == "bot":
        print("filed %d bot result(s)" % len(add_bot(doc, ROOT, a.version, a.source, a.by, deck_path=a.deck_path)))
    elif k == "setup":
        only = [x for x in a.only.split(",") if x] if a.only else None
        out = add_setup_run(doc, ROOT, a.run, a.by, only=only, corrects=a.corrects)
        print("filed %d setup result(s): %s" % (len(out), ", ".join(r["run_version"] for r in out)))
    elif k == "note":
        add_note(doc, ROOT, a.version, a.text, a.source, a.by)
        print("filed a note")
    else:
        docs = rl.load_export(a.export)
        git = mp.Git(ROOT)
        ref = _main_ref(git)
        notes = rl.load_versions(a.versions, git, ROOT, ref)[0] if a.versions else {}
        src = os.path.relpath(os.path.abspath(a.export), ROOT).replace(os.sep, "/")
        commit = committed(ROOT, src, ref)
        if k == "ladder-notes":
            add = ladder_from_notes(doc, a.version, docs, notes, src, a.by, commit)
        else:
            lines, result, _ = rl.read(a.export, a.predictions, (notes, [], a.versions or "no version notes"), git, ROOT,
                                       ref, counting=True)
            add = ladder_from_reading(doc, a.version, result, src, a.by, commit)
        print("filed a ladder result: test %s, feedback %s" % (add["test"], add["feedback"]))


if __name__ == "__main__":
    sys.exit(main())
