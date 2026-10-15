#!/usr/bin/env python3
"""read_ladder.py: read his ladder games against the saved predictions. Read only.

Ladder validation (rl/results/ladder_validation/SPEC.md, details in DETAILS.md). For every predictions file
(<deck>@<id>.json and its addenda <deck>@<id>+<tag>.json, written by make_predictions.py) it:
  - finds the file's registration: its first readable commit on main (committer's clock), or the file's own
    written_at if later, or the time this clone's reflog shows the commit reaching main if later still; checks the
    file is byte-identical to that commit (else INTEGRITY) and that the code is the code that wrote it (else CODE
    CHANGED); a predictions file deleted from main is still read from its first commit, and flagged;
  - ties each logged game to a deck version: 'confirmed' from the agents' committed version notes, else 'assumed'
    from the Ladder Log section and the deck file on main when the game was played (several deck files in one
    section: the file's log_label in the note decides, else the game is ambiguous and not read);
  - takes the play time from the iOS video name in the note (20261014_142546000_iOS = 14:25:46 UTC) or from a video
    name an agent added to the version notes. No video name: 'time unknown'; video after the log time: 'time
    doubtful'; both are feedback. A game is a test only if it started at least 10 minutes after registration, was
    not in the Ladder Log when the file was written, and its video is newer than the newest video then;
  - matches the opponent with the file's saved rule v1 and scores matched games with its calibrated forecasts;
  - prints, per version: the matched games (wins v expected wins, the chance in words, with the concession
    allowance), the off-panel record, the level check labelled with its assumption, the record on card-checked
    games, what the version notes changed, the game list; then the running tally of matched test games.

  python3 read_ladder.py --export EXPORT [--predictions DIR] [--versions FILE] [--repo PATH] [--main-ref main]
                         [--previous READING] [--as-if-committed now|TIME] [--no-git] [--out FILE]
  EXPORT: the Ladder Log export: what ArtifactData 'list' returns for collection 'logs' (records {"id", "data":
          {"games": [...]}}, one per line or in a JSON list), a folder of per-section JSON files (what 'list' with
          out_dir writes, the folder or its logs/ subfolder; not searched deeper), or one per-section file.
  DIR: default <repo>/rl/results/ladder_validation/predictions.
  FILE (--versions): the agents' version notes, default <DIR>/../versions.json; with git, main's committed copy is
          used and checked append-only: {"games": {"<section>/<game id>": {"version": "<card-list id>",
          "status": "confirmed", "evidence": "<packet path>", "cards": "checked" | "mismatch: <card>",
          "video": "<iOS video name>"}}}. Every note needs an evidence path.
  READING (--previous): an earlier reading written with --out (default: the newest file in <DIR>/../readings/);
          the reader lists every game whose opponent, result, note or time changed in the Ladder Log since.
  --as-if-committed: a dry run that treats every predictions file as first committed at that time. Not a counting
          reading.
It never writes anywhere except the optional --out file (a new file; never overwritten).

Self-test (on a Ladder Log export holding the Oct 14 snapshot; writes only to temporary folders):
  python3 read_ladder.py --selftest --export EXPORT [--repo PATH] [--no-git]
Standard library only; imports make_predictions.py from its own folder.
"""
import argparse
import collections
import contextlib
import copy
import datetime
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_predictions as mp  # noqa: E402

UTC = datetime.timezone.utc
VIDEO_RE = re.compile(r"(?<![0-9A-Za-z])(20\d{2})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})(\d{3})_iOS(?![A-Za-z0-9])")
SEAT_RE = re.compile(r"^\s*(1st|2nd)\b", re.I)
WENT_RE = re.compile(r"\bwent (first|second)\b", re.I)
CONCEDE_RE = re.compile(r"conced|concession|surrender|forfeit|resign|gave up|\bquit\b", re.I)
OPP_NAME_RES = [re.compile(r"\bopponent\s*:\s*.*?(?=\.\s|\s·|\s\||$)", re.I),      # "Opponent: plz_concede."
                re.compile(r"(?:^|\|)\s*vs\.?\s[^|]*", re.I)]                      # "| vs N.N |"
LABEL_RE = re.compile(r"\bdeck\s*(\d+)\s*-?\s*([a-z])(?![a-z0-9])", re.I)
NAME_RE = re.compile(r"^(?P<deck>.+)@(?P<id>[0-9a-f]{12})(?:\+(?P<tag>[A-Za-z0-9._-]+))?\.json$")
GAMES_MARK = "GAMES USED (json, for the next reading's comparison):"
PANEL_SHARE = 0.25          # about 1 game in 4 in the log was against a panel list (16 of 66 by Oct 14)
MS_MIN = 1_735_689_600_000  # 2025-01-01: an earlier ts is not a real log time
KNOWN_MATCH_RULES = {mp.MATCH_RULE["version"]}
KNOWN_READING_RULES = {mp.READING_RULE_VERSION}


# ---------------------------------------------------------------- small helpers
def iso(dt):
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def from_ms(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, UTC)


def parse_iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def plus_minutes(s, m):
    return iso(parse_iso(s) + datetime.timedelta(minutes=m))


def video_start(text):
    """(start time UTC, video name) from an iOS video name in the text, or None."""
    m = VIDEO_RE.search(text or "")
    if not m:
        return None
    try:
        d = datetime.datetime(*[int(m.group(i)) for i in range(1, 7)], tzinfo=UTC)
    except ValueError:
        return None
    return iso(d), m.group(0)


def chance_words(p):
    """A probability in plain words."""
    if p is None:
        return "n/a"
    if p >= 0.95:
        return "almost always"
    if p >= 0.5:
        return "about %d times in 10" % round(10 * p)
    if p >= 0.1:
        return "about 1 time in %d" % int(1 / p + 0.5)
    if p <= 0:
        return "never, under this forecast"
    n = 1 / p
    step = 10 if n < 100 else (100 if n < 1000 else 1000)
    return "about 1 time in {:,}".format(max(step, int(n / step + 0.5) * step))


def rec(rows):
    w = sum(1 for r in rows if r["win"])
    return "%d-%d" % (w, len(rows) - w)


def label_keys(text):
    return {"deck%s%s" % (a, b.lower()) for a, b in LABEL_RE.findall(text or "")}


def alnum(text):
    return re.sub(r"[^0-9a-z]", "", (text or "").lower())


# ---------------------------------------------------------------- the Ladder Log export
def _read_json(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def load_export(path, with_info=False):
    """{section id: [games]} from an ArtifactData 'list' result, a folder of per-section files, or one such file."""
    if not os.path.exists(path):
        raise SystemExit("Ladder Log export not found: %s" % path)
    docs, h = {}, hashlib.sha256()

    def add(doc_id, obj, where):
        if isinstance(obj, dict) and isinstance(obj.get("data"), dict) and "games" not in obj:
            doc_id, obj = obj.get("id") or doc_id, obj["data"]
        if isinstance(obj, dict) and isinstance(obj.get("games"), list) and doc_id:
            if doc_id in docs:
                raise SystemExit("section %s appears twice in the export (%s): refusing" % (doc_id, where))
            docs[doc_id] = list(obj["games"])

    if os.path.isdir(path):
        folder = path
        if not any(f.endswith(".json") for f in os.listdir(path)) and os.path.isdir(os.path.join(path, "logs")):
            folder = os.path.join(path, "logs")        # what 'list' with out_dir writes: <out_dir>/logs/<id>.json
        for f in sorted(os.listdir(folder)):
            p = os.path.join(folder, f)
            if f.endswith(".json") and os.path.isfile(p):
                with open(p, "rb") as fh:
                    b = fh.read()
                h.update(f.encode("utf-8") + b"\0" + b + b"\0")
                try:
                    add(f[:-5], json.loads(b.decode("utf-8-sig")), f)
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    raise SystemExit("cannot read %s: %s" % (p, e))
    else:
        with open(path, "rb") as fh:
            b = fh.read()
        h.update(b)
        text = b.decode("utf-8-sig")
        if re.search(r"^\s*\"?next_cursor\"?\s*[:=]", text, re.M):
            raise SystemExit("the export holds a next_cursor: it is the first page only. List again with a larger "
                             "limit (or follow the cursor) and save every page")
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            obj = None
        if obj is None:
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("{"):
                    try:
                        it = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    add(it.get("id"), it, "line")
        elif isinstance(obj, list):
            for it in obj:
                add(it.get("id") if isinstance(it, dict) else None, it, "list item")
        elif isinstance(obj, dict):
            items = next((obj[k] for k in ("documents", "docs", "items", "results") if isinstance(obj.get(k), list)), None)
            if items is not None:
                for it in items:
                    add(it.get("id") if isinstance(it, dict) else None, it, "list item")
            elif "games" in obj:
                add(os.path.splitext(os.path.basename(path))[0], obj, "file")   # one per-section file: the name is the id
            elif "data" in obj:
                add(obj.get("id") or os.path.splitext(os.path.basename(path))[0], obj, "file")
            else:
                for k, v in obj.items():
                    add(k, v, "key")
    n = sum(len(v) for v in docs.values())
    if not n:
        raise SystemExit("no games read from the export %s: refusing (wrong file or format?)" % path)
    info = {"sha256": h.hexdigest(), "sections": len(docs), "games": n}
    return (docs, info) if with_info else docs


def game_facts(doc_id, g, vnote=None):
    """Facts of one logged game, or (None, reason) when the entry is malformed."""
    if not isinstance(g, dict):
        return None, "not an object"
    gid = g.get("id")
    if not isinstance(gid, str) or not gid.strip():
        return None, "no game id"
    ts = g.get("ts")
    if isinstance(ts, bool) or not isinstance(ts, (int, float)) or not math.isfinite(ts):
        return None, "log time is not a number"
    now_ms = datetime.datetime.now(UTC).timestamp() * 1000
    if ts < 1e11:
        return None, "log time looks like seconds, not milliseconds"
    if not (MS_MIN <= ts <= now_ms + 2 * 86400000):
        return None, "log time out of range"
    note = g.get("note")
    note = note if isinstance(note, str) else ("" if note is None else str(note))
    opp = g.get("opp")
    opp = opp if isinstance(opp, str) else ("" if opp is None else str(opp))
    result = str(g.get("result") or "").strip().upper()
    logged = iso(from_ms(ts))
    v = video_start(note)
    src = "video"
    if v is None and vnote and vnote.get("video"):
        v = video_start(vnote["video"])
        src = "video (version notes)"
    if v is None:
        played, time_from = None, "time unknown"
    elif v[0] > logged:
        played, time_from = None, "time doubtful"
    else:
        played, time_from = v[0], src
    s = SEAT_RE.search(note)
    w = WENT_RE.search(note)
    seat = s.group(1).lower() if s else ({"first": "1st", "second": "2nd"}[w.group(1).lower()] if w else "unknown")
    stripped = note
    for r in OPP_NAME_RES:
        stripped = r.sub(" ", stripped)
    return {"doc": doc_id, "id": gid, "key": "%s/%s" % (doc_id, gid), "opp": opp, "result": result,
            "win": result == "W", "counted": result in ("W", "L"), "logged": logged, "ts": ts,
            "video": v[1] if v else None, "video_start": v[0] if v else None, "played": played, "time_from": time_from,
            "seat": seat, "concession": bool(CONCEDE_RE.search(stripped)), "labels": label_keys(note),
            "note_alnum": alnum(note), "note_sha256": mp.sha256_bytes(note.encode("utf-8"))}, None


# ---------------------------------------------------------------- version notes
def parse_notes(obj):
    """{key: note} from the version notes JSON; notes without an evidence path, or with a bad version or video,
    are ignored and reported."""
    games = (obj or {}).get("games", obj or {}) if isinstance(obj, dict) else {}
    notes, problems = {}, []
    for k, v in sorted(games.items()):
        if not isinstance(v, dict):
            problems.append("version note %s is not an object: ignored" % k)
            continue
        if not str(v.get("evidence") or "").strip():
            problems.append("version note %s cites no evidence path: ignored" % k)
            continue
        n = dict(v)
        if n.get("version") is not None:
            n["version"] = str(n["version"]).lower()[:12]
            if not re.fullmatch(r"[0-9a-f]{12}", n["version"]):
                problems.append("version note %s: %r is not a card-list id: ignored" % (k, v.get("version")))
                continue
        if n.get("video") and not video_start(str(n["video"])):
            problems.append("version note %s: %r is not an iOS video name: ignored" % (k, n["video"]))
            continue
        notes[k] = n
    return notes, problems


def load_versions(path, git, repo, main_ref):
    """(notes, problems, where) from the version notes file; with git, main's committed copy, checked append-only."""
    if not path:
        return {}, [], "no version notes"
    problems = []
    rel = None
    if git is not None and repo:
        rp = os.path.relpath(os.path.abspath(path), repo).replace(os.sep, "/")
        rel = None if rp.startswith("..") else rp
    if rel is not None:
        hist = list(reversed(git.history(rel, ref=main_ref, first_parent=True)))
        if hist:
            older = None
            for h, d, blob in hist:
                if set(blob) == {"0"}:
                    problems.append("INTEGRITY: the version notes were deleted from %s at %s" % (main_ref, h[:12]))
                    continue
                try:
                    cur = json.loads(git.blob_bytes(blob).decode("utf-8-sig")).get("games", {})
                except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                    problems.append("INTEGRITY: the version notes at %s are unreadable" % h[:12])
                    continue
                if older is not None:
                    for k, v in older.items():
                        if cur.get(k) != v:
                            problems.append("INTEGRITY: version note %s was changed or removed at %s (notes are append-only)" % (k, h[:12]))
                older = cur
            tip = git.show_bytes(main_ref, rel)
            if tip is None:
                return {}, problems, "version notes deleted from %s" % main_ref
            work = open(path, "rb").read() if os.path.exists(path) else None
            if work is not None and work != tip:
                problems.append("the working copy of %s differs from %s's: %s's committed copy is used" % (rel, main_ref, main_ref))
            notes, p2 = parse_notes(json.loads(tip.decode("utf-8-sig")))
            return notes, problems + p2, "%s on %s" % (rel, main_ref)
    if not os.path.exists(path):
        return {}, [], "no version notes"
    notes, p2 = parse_notes(_read_json(path))
    return notes, p2 + (["the version notes are not committed on %s: a counting reading uses committed notes only" % main_ref]
                        if git is not None else []), path


# ---------------------------------------------------------------- predictions files and git
def _parse_doc(data):
    try:
        doc = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError) as e:
        return None, "cannot read: %s" % e
    if not isinstance(doc, dict) or doc.get("schema") != mp.SCHEMA:
        return None, "schema %r, not %r" % (doc.get("schema") if isinstance(doc, dict) else None, mp.SCHEMA)
    return doc, None


def load_predictions(folder, git, repo, main_ref, overrides=None):
    names, rel_folder = set(), None
    if os.path.isdir(folder):
        names |= {f for f in os.listdir(folder) if NAME_RE.match(f)}
    if git is not None and overrides is None and repo:
        rp = os.path.relpath(os.path.abspath(folder), repo).replace(os.sep, "/")
        if not rp.startswith(".."):
            rel_folder = rp
            out = git.run("log", main_ref, "--first-parent", "--diff-merges=first-parent", "--diff-filter=A",
                          "--name-only", "--format=", "--", rel_folder)
            names |= {os.path.basename(p) for p in out.splitlines()
                      if p.strip() and os.path.dirname(p) == rel_folder and NAME_RE.match(os.path.basename(p))}
    files = []
    current_code = mp.code_sha256()
    for f in sorted(names):
        m = NAME_RE.match(f)
        path = os.path.join(folder, f)
        working = open(path, "rb").read() if os.path.exists(path) else None
        F = {"name": f, "path": path, "id": m.group("id"), "tag": m.group("tag"), "problems": []}
        used = working
        if overrides is not None:
            F["reg"] = dict(overrides.get(f) or {"on_main": False, "why": "no registration given"})
        elif git is None:
            F["reg"] = {"on_main": False, "why": "git not used: no commit time, so every game is feedback"}
        elif rel_folder is None:
            F["reg"] = {"on_main": False, "why": "the predictions folder is not in the repository: no commit time, every game is feedback"}
        else:
            rel = rel_folder + "/" + f
            hist = list(reversed(git.history(rel, ref=main_ref, first_parent=True)))
            first, bad = None, []
            for h, d, blob in hist:
                if set(blob) == {"0"}:
                    continue
                data = git.blob_bytes(blob)
                doc, why = _parse_doc(data)
                if doc is None:
                    bad.append(h)
                    continue
                first = (h, d, data)
                break
            if first is None:
                F["reg"] = {"on_main": False, "why": ("not committed on %s yet: every game is feedback" % main_ref) if not hist
                            else "no readable commit on %s: every game is feedback" % main_ref}
            else:
                h, d, data = first
                tip = git.show_bytes(main_ref, rel)
                used = data
                arrived, how = git.reflog_arrival(main_ref, h)
                F["reg"] = {"on_main": True, "commit": h, "commit_time": d, "reached_main": arrived, "reflog": how,
                            "working_identical": working == data, "main_tip_identical": tip == data,
                            "deleted_on_main": tip is None, "missing_here": working is None}
                if bad:
                    F["problems"].append("INTEGRITY: the first commit%s of %s on %s (%s) could not be read; it counts from %s"
                                         % ("s" if len(bad) > 1 else "", f, main_ref, ", ".join(x[:12] for x in bad), h[:12]))
        reg = F["reg"]
        doc, why = _parse_doc(used) if used is not None else (None, "missing")
        if doc is None:
            F["skip"] = why
            files.append(F)
            continue
        F["doc"] = doc
        F["used_sha256"] = mp.sha256_bytes(used)
        if reg.get("on_main"):
            t = reg.get("time") or reg.get("commit_time")
            wa = doc.get("written_at")
            if wa and wa > t:
                F["problems"].append("the commit time %s is before the file's own written_at %s (a clock off, or a "
                                     "backdated commit?): %s is used" % (t, wa, wa))
                t = wa
            ra = reg.get("reached_main")
            if ra and ra > t:
                if parse_iso(ra) - parse_iso(t) > datetime.timedelta(minutes=mp.TEST_MARGIN_MINUTES):
                    F["problems"].append("reached %s at %s by this clone's reflog, after its commit time %s (merged or "
                                         "fast-forwarded from another branch?): %s is used" % (main_ref, ra, t, ra))
                t = ra
            reg["time"] = t
            if reg.get("deleted_on_main"):
                F["problems"].append("INTEGRITY: %s was deleted from %s after its first commit; this reading uses that first commit" % (f, main_ref))
            elif not reg.get("main_tip_identical", True):
                F["problems"].append("INTEGRITY: %s was changed on %s after its first commit; this reading uses the first commit" % (f, main_ref))
            if reg.get("missing_here"):
                F["problems"].append("INTEGRITY: %s is missing from the predictions folder; read from its first commit" % f)
            elif not reg.get("working_identical", True):
                F["problems"].append("INTEGRITY: the working copy of %s differs from its first commit on %s (%s); this "
                                     "reading uses that first-committed version" % (f, main_ref, (reg.get("commit") or "")[:12]))
        rec_code = (doc.get("written_by") or {}).get("code_sha256") or {}
        changed = ["%s (%s -> %s)" % (k, str(rec_code.get(k))[:12], str(current_code.get(k))[:12])
                   for k in ("make_predictions.py", "read_ladder.py") if rec_code.get(k) != current_code.get(k)]
        if changed:
            F["problems"].append("CODE CHANGED since this file was written: %s. The reading below uses today's code; "
                                 "compare the two with git diff before trusting it" % "; ".join(changed))
        if doc["deck"].get("version_id") != F["id"]:
            F["skip"] = "the file name says version %s, the file says %s" % (F["id"], doc["deck"].get("version_id"))
        elif doc.get("matching_rule", {}).get("version") not in KNOWN_MATCH_RULES:
            F["skip"] = "matching rule %r: this reader knows %s" % (doc.get("matching_rule", {}).get("version"), sorted(KNOWN_MATCH_RULES))
        elif doc.get("reading_rule_version") not in KNOWN_READING_RULES:
            F["skip"] = "reading rule %r: this reader knows %s" % (doc.get("reading_rule_version"), sorted(KNOWN_READING_RULES))
        files.append(F)
    return files


def group_files(files):
    """{(deck name, version id): {"base": F, "addenda": [F]}}; addenda whose base is missing are skipped."""
    groups = collections.OrderedDict()
    for F in files:
        if "skip" in F or F["tag"]:
            continue
        groups[(F["doc"]["deck"]["name"], F["id"])] = {"base": F, "addenda": []}
    for F in files:
        if "skip" in F or not F["tag"]:
            continue
        key = (F["doc"]["deck"]["name"], F["id"])
        to = (F["doc"].get("addendum_to") or {})
        if key not in groups:
            F["skip"] = "its base file %s@%s.json is missing or unreadable" % key
            continue
        base = groups[key]["base"]
        if to.get("file") != base["name"]:
            F["skip"] = "it names %r as its base, not %s" % (to.get("file"), base["name"])
            continue
        if to.get("sha256") != base["used_sha256"]:
            F["problems"].append("INTEGRITY: written against a base file with sha256 %s, but the base file read here is %s"
                                 % (str(to.get("sha256"))[:12], base["used_sha256"][:12]))
        base_keys = {(b.get("role"), (b.get("engine") or {}).get("key")) for b in base["doc"]["bots"]}
        F["restated"] = [b["id"] for b in F["doc"]["bots"] if (b.get("role"), (b.get("engine") or {}).get("key")) in base_keys]
        if F["restated"]:
            F["problems"].append("restates %s of the base file: the running tally keeps the earliest registered forecast"
                                 % ", ".join(F["restated"]))
        groups[key]["addenda"].append(F)
    return groups


def deck_timeline(git, repo, rel, main_ref):
    """The deck file's card-list id over time on main (git), or the working file's id (no git)."""
    if git is not None:
        tl = []
        for h, d, blob in git.history(rel, ref=main_ref, first_parent=True):
            cid = None if set(blob) == {"0"} else (mp.card_list_sha256_or_none(git.blob_bytes(blob)) or "unreadable")
            tl.append((d, cid[:12] if cid and cid != "unreadable" else (cid or "absent")))
        return {"how": "git", "timeline": sorted(tl)}
    p = os.path.join(repo, rel) if repo else None
    if p and os.path.exists(p):
        with open(p, "rb") as fh:
            cid = mp.card_list_sha256_or_none(fh.read())
        return {"how": "working file", "id": cid[:12] if cid else "unreadable"}
    return {"how": "none"}


def deck_id_at(tl, when):
    if tl["how"] == "git":
        cur = "absent"
        for d, cid in tl["timeline"]:
            if when and d <= when:
                cur = cid
        return cur
    if tl["how"] == "working file":
        return tl["id"]
    return "absent"


# ---------------------------------------------------------------- ties and classes
def tie_games(facts, groups, notes, timelines, use_notes=True):
    """{game key: (group key, tie, evidence, cards)} and {reason: count} for games not read."""
    files_by_section = collections.defaultdict(lambda: collections.defaultdict(list))
    labels = collections.defaultdict(set)
    for gk, G in groups.items():
        d = G["base"]["doc"]["deck"]
        for s in d.get("log_docs") or []:
            files_by_section[s][d["file"]].append(gk)
        if d.get("log_label"):
            labels[d["file"]] |= label_keys(d["log_label"]) or {alnum(d["log_label"])}
    tied, not_read = {}, collections.Counter()
    for g in facts:
        note = (notes.get(g["key"]) or notes.get(g["id"])) if use_notes else None
        cards = (note or {}).get("cards")
        if note and note.get("version"):
            gks = [k for k in groups if k[1] == note["version"]]
            if len(gks) != 1:
                not_read["a version note names %s, which has no predictions file" % note["version"]] += 1
                continue
            tie = (gks[0], "confirmed" if note.get("status", "confirmed") == "confirmed" else "assumed", note.get("evidence") or "")
        else:
            files = files_by_section.get(g["doc"])
            if not files:
                not_read["no predictions file for section %s" % g["doc"]] += 1
                continue
            when = g["played"] or g["logged"]
            present = {}
            for rel in files:
                cid = deck_id_at(timelines[rel], when)
                if cid != "absent":
                    present[rel] = cid
            if not present:
                not_read["the deck file was not on main when played (section %s)" % g["doc"]] += 1
                continue
            if len(present) > 1:
                pick = [rel for rel in present if labels.get(rel) and
                        (labels[rel] & g["labels"] or any(k in g["note_alnum"] for k in labels[rel] if not k.startswith("deck")))]
                if len(pick) != 1:
                    not_read["ambiguous: %d deck files share section %s and the note names none of them" % (len(present), g["doc"])] += 1
                    continue
                rel = pick[0]
            else:
                rel = next(iter(present))
                if g["labels"] and labels.get(rel) and not (labels[rel] & g["labels"]) and \
                        all(k.startswith("deck") for k in labels[rel]):
                    not_read["the note names another deck (%s)" % ", ".join(sorted(g["labels"]))] += 1
                    continue
            cid = present[rel]
            gks = [k for k in files[rel] if k[1] == cid]
            if not gks:
                not_read["played with a card list that has no predictions file (%s)" % cid] += 1
                continue
            tie = (gks[0], "assumed", "")
        if cards and str(cards).lower().startswith("mismatch"):
            not_read["an agent found a card mismatch"] += 1
            continue
        tied[g["key"]] = tie + (str(cards) if cards else None,)
    return tied, not_read


def classify(g, F):
    """'test' or 'feedback' (with the reason) of one game for one predictions file."""
    reg, doc = F["reg"], F["doc"]
    if not reg.get("on_main"):
        return "feedback", "no registration"
    if g["time_from"] in ("time unknown", "time doubtful"):
        return "feedback", g["time_from"]
    if g["played"] < plus_minutes(reg["time"], mp.TEST_MARGIN_MINUTES):
        return "feedback", "played before the file reached main (+%d min)" % mp.TEST_MARGIN_MINUTES
    at = doc.get("ladder_log_at_writing") or {}
    if g["key"] in set(at.get("game_keys") or []):
        return "feedback", "already logged when the file was written"
    if at.get("newest_video_start") and g["played"] <= at["newest_video_start"]:
        return "feedback", "not newer than the newest video when the file was written"
    return "test", ""


# ---------------------------------------------------------------- checks
def matched_check(rows, fc):
    ps = [fc[r["match"]["list"]] for r in rows]
    O = sum(1 for r in rows if r["win"])
    E = sum(ps)
    d = mp.poisson_binomial(ps)
    if abs(O - E) < 1e-9:
        return O, E, None, "right on the forecast"
    if O < E:
        return O, E, sum(d[:O + 1]), "doing this badly or worse"
    return O, E, sum(d[O:]), "doing this well or better"


def level_check(W, n, bot):
    pm = mp.predictive_pmf(n, bot["x"], bot["n"])
    lo, hi = mp.band_from_pmf(pm)
    low, high = sum(pm[:W + 1]), sum(pm[W:])
    below_rate = W * bot["n"] <= bot["x"] * n
    return {"range": [lo, hi], "where": "inside" if lo <= W <= hi else ("below" if W < lo else "above"),
            "p_two_sided": min(1.0, 2 * min(low, high)), "p_one_sided": low if below_rate else high,
            "one_sided_words": "this low or lower" if below_rate else "this high or higher"}


def summarise_class(rows, bots, fcs):
    """rows: games of one class (test or feedback) for one predictions file."""
    counted = [r for r in rows if r["counted"]]
    matched = [r for r in counted if r["match"]["status"] == "panel"]
    inferred = [r for r in counted if r["match"]["status"] == "inferred"]
    off = [r for r in counted if r["match"]["status"] in ("readout", "ruled out", "unmatched")]
    checked = [r for r in counted if (r.get("cards") or "").lower().startswith("checked")]
    out = {"n": len(counted), "wins": sum(1 for r in counted if r["win"]), "record": rec(counted),
           "concession_wins": sum(1 for r in counted if r["win"] and r["concession"]),
           "concession_losses": sum(1 for r in counted if not r["win"] and r["concession"]),
           "off_panel_concession_wins": sum(1 for r in off if r["win"] and r["concession"]),
           "not_counted": len(rows) - len(counted),
           "cards_checked": {"n": len(checked), "record": rec(checked)},
           "matched": {"n": len(matched), "record": rec(matched),
                       "exact": {"n": sum(1 for r in matched if r["match"]["fit"] == "exact"),
                                 "record": rec([r for r in matched if r["match"]["fit"] == "exact"])},
                       "variant": {"n": sum(1 for r in matched if r["match"]["fit"] == "variant"),
                                   "record": rec([r for r in matched if r["match"]["fit"] == "variant"])},
                       "per_bot": {}},
           "inferred": {"n": len(inferred), "record": rec(inferred)},
           "off_panel": {"n": len(off), "record": rec(off), "parts": {}},
           "level": {}}
    for r in off:
        key = r["match"]["list"] if r["match"]["status"] == "readout" else r["match"]["status"]
        out["off_panel"]["parts"].setdefault(key, []).append(r)
    out["off_panel"]["parts"] = {k: {"n": len(v), "record": rec(v)} for k, v in out["off_panel"]["parts"].items()}
    a = PANEL_SHARE * out["off_panel_concession_wins"]
    for b in bots:
        fc = fcs[b["id"]]["per_list"]
        if matched:
            O, E, p, words = matched_check(matched, fc)
            pb = {"wins": O, "expected": E, "p_one_sided": p, "direction": words}
            ex = [r for r in matched if r["match"]["fit"] == "exact"]
            if ex and len(ex) < len(matched):
                O2, E2, p2, w2 = matched_check(ex, fc)
                pb["exact_only"] = {"wins": O2, "expected": E2, "p_one_sided": p2, "direction": w2}
            out["matched"]["per_bot"][b["id"]] = pb
        if a:
            pb = out["matched"]["per_bot"].setdefault(b["id"], {"wins": 0, "expected": 0.0, "p_one_sided": None,
                                                                 "direction": "no matched games"})
            pb["allowance"] = {"wins": pb["wins"] + a, "expected": pb["expected"] + a * fcs[b["id"]]["level"]}
        if counted:
            out["level"][b["id"]] = level_check(out["wins"], len(counted), b)
    return out


# ---------------------------------------------------------------- printing
def engine_note(b):
    key = (b.get("engine") or {}).get("key")
    cur_now = key in mp.CURRENT_ENGINE["harness_engine_trees"] + mp.CURRENT_ENGINE["floor_engines"]
    return "engine %s, %s" % (mp.engine_short(key), "the current engine now" if cur_now else "NOT the current engine now")


def print_class(P, title, sub, bots, fcs):
    s = summarise_class(sub, bots, fcs)
    extra = []
    if s["concession_wins"]:
        extra.append("%d win%s by the opponent's concession, counted in full" % (s["concession_wins"], "" if s["concession_wins"] == 1 else "s"))
    if s["concession_losses"]:
        extra.append("%d loss%s by his concession" % (s["concession_losses"], "" if s["concession_losses"] == 1 else "es"))
    if s["not_counted"]:
        extra.append("%d with a result other than W/L, not counted" % s["not_counted"])
    P("   -- %s: %d, record %s%s" % (title, s["n"], s["record"], (" (" + "; ".join(extra) + ")") if extra else ""))
    m = s["matched"]
    P("     1. Matched games (opponent on a panel list): %d, record %s (exact %d: %s; variant %d: %s)" % (
        m["n"], m["record"], m["exact"]["n"], m["exact"]["record"], m["variant"]["n"], m["variant"]["record"]))
    if not bots:
        P("          no bot on the engine pinned when this file was written: nothing to compare")
    for b in bots:
        pb = m["per_bot"].get(b["id"])
        if not pb or not m["n"]:
            continue
        P("          %-48s %d wins v %.1f expected; %s%s" % (
            b["label"] + ":", pb["wins"], pb["expected"], pb["direction"],
            "" if pb["p_one_sided"] is None else " happens %s (one-sided, p = %.3f)" % (chance_words(pb["p_one_sided"]), pb["p_one_sided"])))
        if "exact_only" in pb:
            e = pb["exact_only"]
            P("            exact matches only: %d wins v %.1f expected" % (e["wins"], e["expected"]))
    k = s["off_panel_concession_wins"]
    if k:
        P("        %d off-panel win%s came by the opponent's concession. An early concession can hide the attacker, so the "
          "matched games miss some wins and this check leans against the bot. With 1 in 4 of them counted as panel wins: %s."
          % (k, "" if k == 1 else "s", "; ".join("%s %.1f v %.1f" % (b["label"], m["per_bot"][b["id"]]["allowance"]["wins"],
                                                                     m["per_bot"][b["id"]]["allowance"]["expected"])
                                                 for b in bots if "allowance" in m["per_bot"].get(b["id"], {}))))
    if s["inferred"]["n"]:
        P("        Guessed lists (inferred, not scored): %d, record %s" % (s["inferred"]["n"], s["inferred"]["record"]))
    parts = s["off_panel"]["parts"]
    P("     2. Off-panel games, no prediction: %d, record %s%s" % (
        s["off_panel"]["n"], s["off_panel"]["record"],
        (" (" + "; ".join("%s %d: %s" % (("readout list " + kk) if kk.startswith(("h-", "l-", "g-")) else kk, v["n"], v["record"])
                          for kk, v in sorted(parts.items())) + ")") if parts else ""))
    P("     3. Level check, ASSUMING off-panel opponents are like the panel on average: %d win%s in %d game%s"
      % (s["wins"], "" if s["wins"] == 1 else "s", s["n"], "" if s["n"] == 1 else "s"))
    inside, below, above = [], [], []
    for b in bots:
        lv = s["level"].get(b["id"])
        if not lv:
            continue
        {"inside": inside, "below": below, "above": above}[lv["where"]].append(b["label"])
        P("          %-48s range %d-%d wins; %d is %s. A record this far from %.1f%% happens %s (two-sided p = %.3f; %s: p = %.3f, one-sided)" % (
            b["label"] + " (%.1f%%):" % b["number_pct"], lv["range"][0], lv["range"][1], s["wins"], lv["where"],
            b["number_pct"], chance_words(lv["p_two_sided"]), lv["p_two_sided"], lv["one_sided_words"], lv["p_one_sided"]))
    bits = []
    if below:
        bits.append("below the range of " + " and ".join(below))
    if above:
        bits.append("above the range of " + " and ".join(above))
    if inside:
        bits.append("inside the range of " + " and ".join(inside))
    if bits:
        P("        In short: %s is %s. (The frozen kx3's number is the optimistic end.)" % (s["record"], "; ".join(bits)))
    P("     Cards checked by an agent: %d of %d games%s." % (
        s["cards_checked"]["n"], s["n"], (", record %s on those" % s["cards_checked"]["record"]) if s["cards_checked"]["n"] else " (no check yet)"))
    return s


def print_bots(P, doc, bots, older):
    if bots:
        P("   bots compared (on the engine pinned when written: %s; km3 plays the panel in every run):" % bots[0]["engine"].get("label"))
    else:
        P("   bots compared: none (no bot in this file is on the engine pinned when it was written)")
    for b in bots:
        P("     %-48s %5.1f%% over %d games (%s)%s" % (b["label"], b["number_pct"], b["n"], engine_note(b),
                                                 "  knows the 8 lists: the optimistic end" if b.get("knows_the_panel_lists") else ""))
    if bots:
        kx = sum(b["n"] for b in bots if b.get("knows_the_panel_lists"))
        P("     kx3 games: {:,} of {:,} bot games compared.".format(kx, sum(b["n"] for b in bots)))
    if older:
        P("   kept for the record, out of the comparison (older engine): " +
          "; ".join("%s %.1f%% over %d" % (b["label"], b["number_pct"], b["n"]) for b in older))
    sc = doc.get("sources_check") or {}
    if sc.get("checked") and sc.get("floor_pages_not_given"):
        P("   floor pages with this deck's name not in the file (another version?): " + ", ".join(sc["floor_pages_not_given"]))
    if sc and not sc.get("checked"):
        P("   the writer's source check was not done (no git when written)")


def reg_line(F, main_ref):
    reg = F["reg"]
    if reg.get("on_main"):
        extra = ""
        if reg.get("commit_time"):
            extra = "; commit %s at %s (committer's clock)" % ((reg.get("commit") or "")[:12], reg["commit_time"])
            extra += "; reflog: %s" % (("reached %s at %s" % (main_ref, reg["reached_main"])) if reg.get("reached_main") else reg.get("reflog"))
        else:
            extra = "; %s" % (reg.get("commit") or "")
        ident = "yes" if reg.get("working_identical", True) and reg.get("main_tip_identical", True) else "NO"
        return "%s: registered on %s at %s%s; byte-identical to that commit: %s" % (F["name"], main_ref, reg["time"], extra, ident)
    return "%s: %s" % (F["name"], reg.get("why"))


# ---------------------------------------------------------------- the reading
def read(export, predictions, notes_in=None, git=None, repo=None, main_ref="main", registrations=None,
         previous=None, counting=True, banner=None):
    """Returns (lines, result, games_used). Reads only."""
    docs, info = load_export(export, with_info=True)
    if isinstance(notes_in, tuple):
        notes, note_problems, notes_where = notes_in
    else:
        notes, note_problems = parse_notes(notes_in or {})
        notes_where = "given" if notes_in else "no version notes"
    files = load_predictions(predictions, git, repo, main_ref, overrides=registrations)
    groups = group_files(files)
    facts, facts0, malformed, seen = [], [], collections.Counter(), set()
    for d, gs in sorted(docs.items()):
        for g in gs:
            gid = g.get("id") if isinstance(g, dict) else None
            vnote = notes.get("%s/%s" % (d, gid)) or notes.get(gid) if gid else None
            f, why = game_facts(d, g, vnote)
            if f is None:
                malformed["malformed entry (%s)" % why] += 1
                continue
            if f["key"] in seen:
                malformed["the same game id twice in section %s" % d] += 1
                continue
            seen.add(f["key"])
            facts.append(f)
            facts0.append(game_facts(d, g, None)[0])
    pooled_w = sum(1 for g in facts if g["win"])
    pooled_n = sum(1 for g in facts if g["counted"])
    timelines = {}
    for G in groups.values():
        rel = G["base"]["doc"]["deck"]["file"]
        if rel not in timelines:
            timelines[rel] = deck_timeline(git, repo, rel, main_ref)
    tied, not_read = tie_games(facts, groups, notes, timelines, use_notes=True)
    tied0, _ = tie_games(facts0, groups, {}, timelines, use_notes=False)
    not_read.update(malformed)
    fact = {g["key"]: g for g in facts}
    fact0 = {g["key"]: g for g in facts0}

    L = []
    P = L.append
    P("LADDER READING (read_ladder.py, read only), read at %s. Times are UTC; commit times are the committing machine's clock."
      % iso(datetime.datetime.now(UTC)))
    if banner:
        P(banner)
    if not counting:
        P("NOT A COUNTING READING (%s)." % ("a dry run" if registrations is not None else "read against %s, not main" % main_ref))
    total = sum(len(v) for v in docs.values())
    P("Export: %d games logged in %d sections (sha256 %s). Predictions files: %d usable in %d version%s%s."
      % (total, len(docs), info["sha256"][:12], sum(1 for F in files if "skip" not in F), len(groups), "" if len(groups) == 1 else "s",
         "" if all("skip" not in F for F in files) else "; skipped: " + "; ".join("%s (%s)" % (F["name"], F["skip"]) for F in files if "skip" in F)))
    P("Read: %d of %d logged games are tied to a predictions file; not read: %d%s."
      % (len(tied), total, total - len(tied),
         (" (" + "; ".join("%s: %d" % (k, v) for k, v in sorted(not_read.items())) + ")") if not_read else ""))
    P("Version notes: %s, %d note%s%s." % (notes_where, len(notes), "" if len(notes) == 1 else "s",
                                         ("; " + "; ".join(note_problems)) if note_problems else ""))
    if groups:
        P("The panel: " + next(iter(groups.values()))["base"]["doc"].get("who_plays_the_panel", mp.WHO_PLAYS_THE_PANEL))
    result = {"groups": {}, "tied": tied, "not_read": dict(not_read), "games_logged": total, "games_read": len(tied),
              "pooled": [pooled_w, pooled_n], "facts": fact}
    tally_cand = collections.defaultdict(dict)    # game key -> {(role, engine): (reg time, file, p, label)}
    for gk, G in groups.items():
        F0 = G["base"]
        doc = F0["doc"]
        rows = []
        for key, t in tied.items():
            if t[0] != gk:
                continue
            r = dict(fact[key])
            r["tie"], r["tie_note"], r["cards"] = t[1], t[2], t[3]
            r["match"] = mp.match_opponent(r["opp"], rule=doc["matching_rule"])
            r["class"], r["why"] = classify(r, F0)
            r["add_classes"] = {A["tag"]: classify(r, A)[0] for A in G["addenda"]}
            rows.append(r)
        rows.sort(key=lambda r: (r["played"] or r["logged"], r["key"]))
        logged_here = sum(1 for g in facts if g["doc"] in (doc["deck"].get("log_docs") or []))
        res = {"reg": F0["reg"], "rows": rows, "classes": {}, "addenda": {}}
        P("")
        P("== %s, version %s (card list); Ladder Log section %s%s" % (
            doc["deck"]["name"], gk[1], ", ".join(doc["deck"].get("log_docs") or []),
            ("; notes name it '%s'" % doc["deck"]["log_label"]) if doc["deck"].get("log_label") else ""))
        P("   " + reg_line(F0, main_ref))
        for pr in F0["problems"]:
            P("   " + pr)
        tests = [r for r in rows if r["class"] == "test"]
        n_test = sum(1 for r in tests if r["counted"])
        if n_test >= mp.VERDICT_TEST_GAMES:
            P("   Reading: the VERDICT for this version if no earlier reading had %d test games (%d test games)." % (mp.VERDICT_TEST_GAMES, n_test))
        else:
            P("   Reading: interim (%d test game%s; the verdict is the first reading with %d test games, or the reading at "
              "season end or retirement if that comes first)." % (n_test, "" if n_test == 1 else "s", mp.VERDICT_TEST_GAMES))
        P("   games: %d logged in this section; %d read with this version (test %d, feedback %d; tied %d assumed, %d confirmed); %d not read"
          % (logged_here, len(rows), len(tests), len(rows) - len(tests), sum(1 for r in rows if r["tie"] == "assumed"),
             sum(1 for r in rows if r["tie"] == "confirmed"), max(0, logged_here - sum(1 for r in rows if r["doc"] in doc["deck"]["log_docs"]))))
        fcs = doc["forecast"]["per_bot"]
        bots = [b for b in doc["bots"] if b.get("in_bot_comparison") and b["id"] in fcs]
        older = [b for b in doc["bots"] if not b.get("in_bot_comparison")]
        print_bots(P, doc, bots, older)
        for cls, title in (("test", "TEST games (played at least %d min after the file reached main)" % mp.TEST_MARGIN_MINUTES),
                           ("feedback", "FEEDBACK games (played before that, time unknown, or seen when the file was written)")):
            sub = [r for r in rows if r["class"] == cls]
            if not sub:
                P("   -- %s: none yet." % title)
                continue
            res["classes"][cls] = print_class(P, title, sub, bots, fcs)
            if cls == "test":
                for r in sub:
                    if r["counted"] and r["match"]["status"] == "panel":
                        for b in bots:
                            k = (b.get("role") or b["id"], (b.get("engine") or {}).get("key"))
                            c = (F0["reg"]["time"], F0["name"], fcs[b["id"]]["per_list"][r["match"]["list"]], b["label"])
                            if k not in tally_cand[r["key"]] or c[:2] < tally_cand[r["key"]][k][:2]:
                                tally_cand[r["key"]][k] = c
        for A in G["addenda"]:
            adoc = A["doc"]
            afcs = adoc["forecast"]["per_bot"]
            abots = [b for b in adoc["bots"] if b.get("in_bot_comparison") and b["id"] in afcs]
            aolder = [b for b in adoc["bots"] if not b.get("in_bot_comparison")]
            P("   ++ addendum '%s'" % A["tag"])
            P("      " + reg_line(A, main_ref))
            for pr in A["problems"]:
                P("      " + pr)
            print_bots(P, adoc, abots, aolder)
            sub = [r for r in rows if r["add_classes"].get(A["tag"]) == "test"]
            ares = {"reg": A["reg"], "test": None, "n_test": len(sub)}
            if sub:
                ares["test"] = print_class(P, "TEST games for this addendum's bots", sub, abots, afcs)
                for r in sub:
                    if r["counted"] and r["match"]["status"] == "panel":
                        for b in abots:
                            k = (b.get("role") or b["id"], (b.get("engine") or {}).get("key"))
                            c = (A["reg"]["time"], A["name"], afcs[b["id"]]["per_list"][r["match"]["list"]], b["label"])
                            if k not in tally_cand[r["key"]] or c[:2] < tally_cand[r["key"]][k][:2]:
                                tally_cand[r["key"]][k] = c
            else:
                P("   -- TEST games for this addendum's bots: none yet.")
            res["addenda"][A["tag"]] = ares
        # what the version notes changed
        changes = []
        for key in sorted(set(tied) | set(tied0)):
            a, b0 = tied.get(key), tied0.get(key)
            mine, mine0 = bool(a and a[0] == gk), bool(b0 and b0[0] == gk)
            if not (mine or mine0):
                continue
            g = fact.get(key) or fact0.get(key)
            if mine and not mine0:
                changes.append("%s (%s) added by a note" % (key, g["result"]))
            elif mine0 and not mine:
                changes.append("%s (%s) removed by a note" % (key, g["result"]))
            elif fact[key]["time_from"] != fact0[key]["time_from"]:
                changes.append("%s (%s): video added by a note (%s)" % (key, g["result"], fact[key]["video"]))
        rows0 = [dict(fact0[k], match=mp.match_opponent(fact0[k]["opp"], rule=doc["matching_rule"]))
                 for k, t in tied0.items() if t[0] == gk]
        for r in rows0:
            r["class"] = classify(r, F0)[0]
        if changes:
            t0 = [r for r in rows0 if r["class"] == "test" and r["counted"]]
            f0 = [r for r in rows0 if r["class"] == "feedback" and r["counted"]]
            P("   Without the version notes: test %s (%d), feedback %s (%d). The notes changed: %s." % (
                rec(t0), len(t0), rec(f0), len(f0), "; ".join(changes)))
        else:
            P("   No version note changes this version's games.")
        res["without_notes"] = {"test": rec([r for r in rows0 if r["class"] == "test" and r["counted"]]),
                                "feedback": rec([r for r in rows0 if r["class"] == "feedback" and r["counted"]]),
                                "changes": changes}
        P("   game list (game, played, time from, seat, result, rule v1, tie, cards, class | opponent):")
        for r in rows:
            mm = r["match"]
            why = "early" if r["why"].startswith("played before") else ("seen" if r["why"].startswith(("already", "not newer")) else "")
            cls = r["class"] + ("(%s)" % why if why else "") + "".join(" +%s:%s" % (t, c) for t, c in sorted(r["add_classes"].items()))
            P("     %-20s %-20s %-21s %-7s %s%-4s %-26s %-9s %-7s %-9s %-9s %-8s | %s" % (
                r["key"], r["played"] or ("(logged %s)" % r["logged"]), r["time_from"], r["seat"], r["result"],
                " (c)" if (r["concession"] and r["counted"]) else "", mm["list"] or "-", mm["status"], mm["fit"] or "-",
                r["tie"], (r["cards"] or "-")[:9], cls, r["opp"][:60]))
        P("     (c) = a concession; a win by the opponent's concession is a full win. feedback(early) = played less than "
          "%d min after the file reached main; feedback(seen) = in the log, or older than the newest video, when the file "
          "was written." % mp.TEST_MARGIN_MINUTES)
        result["groups"]["%s@%s" % gk] = res

    # the running tally
    P("")
    P("== Running tally: matched TEST games; one forecast per game and per bot and engine (the earliest registered)")
    by_key = collections.defaultdict(list)
    for key, cands in tally_cand.items():
        for k, c in cands.items():
            by_key[k].append((key, c))
    if not by_key:
        P("   no test games on a panel list yet.")
        result["tally"] = None
    else:
        rate = pooled_w / pooled_n if pooled_n else 0.5
        tally = {}
        for k in sorted(by_key, key=lambda k: (k[0], str(k[1]))):
            rows = by_key[k]
            O = sum(1 for key, c in rows if fact[key]["win"])
            E = sum(c[2] for key, c in rows)
            br = sum((c[2] - (1 if fact[key]["win"] else 0)) ** 2 for key, c in rows) / len(rows)
            coin = sum((0.5 - (1 if fact[key]["win"] else 0)) ** 2 for key, c in rows) / len(rows)
            base = sum((rate - (1 if fact[key]["win"] else 0)) ** 2 for key, c in rows) / len(rows)
            lab = rows[0][1][3]
            tally["%s@%s" % (k[0], mp.engine_short(k[1]))] = {"n": len(rows), "wins": O, "expected": E, "wins_minus_expected": O - E,
                                                             "brier": br, "coin": coin, "pooled": base, "games": sorted(key for key, c in rows)}
            P("     %-48s %d game%s, %d wins v %.1f expected (wins minus expected %+.1f); Brier %.3f, a coin flip %.3f, his pooled rate %.3f"
              % ("%s [engine %s]:" % (lab, mp.engine_short(k[1])), len(rows), "" if len(rows) == 1 else "s", O, E, O - E, br, coin, base))
        sets = {k: set(v["games"]) for k, v in tally.items()}
        common = set.intersection(*sets.values()) if sets else set()
        if any(len(s) != len(common) for s in sets.values()):
            P("     Bots are compared only on the %d game%s they all have; the lines above have different games." % (len(common), "" if len(common) == 1 else "s"))
        P("   His pooled ladder rate: %d of %d = %.0f%%. Brier score: lower is closer. The frozen kx3 is the optimistic end, so its "
          "wins minus expected should run negative and its Brier score worse." % (pooled_w, pooled_n, 100 * rate))
        P("   This tally says nothing about screening or ranking decks: it only says how close each bot's matchup forecasts came on these games.")
        result["tally"] = tally

    # changes in the Ladder Log since the previous reading
    games_used = {"read_at": iso(datetime.datetime.now(UTC)), "export_sha256": info["sha256"],
                  "games": {g["key"]: {"ts": g["ts"], "opp": g["opp"], "result": g["result"], "note_sha256": g["note_sha256"]}
                            for g in facts}}
    if previous is not None:
        prev = previous.get("games", {})
        diffs = []
        for key, old in sorted(prev.items()):
            new = games_used["games"].get(key)
            if new is None:
                diffs.append("%s removed (was %s v %s)" % (key, old.get("result"), old.get("opp")))
                continue
            what = [f for f in ("opp", "result", "ts", "note_sha256") if old.get(f) != new.get(f)]
            if what:
                diffs.append("%s changed: %s" % (key, ", ".join(
                    ("%s %r -> %r" % (f, old.get(f), new.get(f))) if f in ("opp", "result") else ("note edited" if f == "note_sha256" else "log time")
                    for f in what)))
        P("")
        P("== Ladder Log changes since the previous reading (%s): %s" % (previous.get("_from", "?"), "none" if not diffs else "%d" % len(diffs)))
        for dline in diffs:
            P("   " + dline)
        result["changes_since_previous"] = diffs
    return L, result, games_used


def read_previous(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    i = text.rfind(GAMES_MARK)
    if i < 0:
        raise SystemExit("%s is not a reading written with --out (no games block)" % path)
    obj = json.loads(text[i + len(GAMES_MARK):].strip().splitlines()[0])
    obj["_from"] = os.path.basename(path)
    return obj


# ---------------------------------------------------------------- command line
def parser():
    ap = argparse.ArgumentParser(description="Read his ladder games against the saved predictions (read only).")
    ap.add_argument("--export", help="Ladder Log export: ArtifactData 'list' JSON, a folder of per-section JSON, or one section file")
    ap.add_argument("--predictions", help="predictions folder (default <repo>/rl/results/ladder_validation/predictions)")
    ap.add_argument("--versions", help="the agents' version notes (default <predictions>/../versions.json when it exists)")
    ap.add_argument("--previous", help="an earlier reading written with --out (default: the newest in <predictions>/../readings/)")
    ap.add_argument("--repo", help="repository root (default: found from the current folder, then from this script)")
    ap.add_argument("--main-ref", default="main")
    ap.add_argument("--as-if-committed", help="dry run: treat every predictions file as first committed at this time ('now' or ISO with Z)")
    ap.add_argument("--no-git", action="store_true", help="no commit times: every game is feedback")
    ap.add_argument("--out", help="also write the reading to this new file (never overwritten)")
    ap.add_argument("--selftest", action="store_true")
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    repo = args.repo or mp.find_repo(os.getcwd()) or mp.find_repo(HERE)
    repo = os.path.abspath(repo) if repo else None
    if args.selftest:
        if not args.export:
            raise SystemExit("--selftest needs --export (a Ladder Log export holding the Oct 14 snapshot's 66 games)")
        if not repo:
            raise SystemExit("--selftest needs --repo (the PocketDeckSim repository, for deck 12's real files)")
        return selftest(repo, args.export, use_git=not args.no_git)
    if not args.export:
        raise SystemExit("--export is required")
    if not os.path.exists(args.export):
        raise SystemExit("Ladder Log export not found: %s" % args.export)
    if args.out:
        d = os.path.dirname(os.path.abspath(args.out))
        if not os.path.isdir(d):
            raise SystemExit("--out: the folder %s does not exist" % d)
        if os.path.lexists(args.out):
            print("REFUSED: %s exists; nothing was read or written." % args.out, file=sys.stderr)
            return 3
    pred = args.predictions or (os.path.join(repo, mp.DEFAULT_OUT) if repo else None)
    if not pred or not os.path.isdir(pred):
        raise SystemExit("predictions folder not found: pass --predictions")
    git = None
    if not args.no_git:
        if not repo:
            raise SystemExit("repository not found: pass --repo, or --no-git (every game is then feedback)")
        git = mp.Git(repo)
        if not git.ok:
            raise SystemExit("git not found (or %s is not a git repository); pass --no-git to read without commit times "
                             "(every game is then feedback)" % repo)
        if not git.verify_ref(args.main_ref):
            raise SystemExit("no branch %r in %s; pass --main-ref (e.g. origin/main)" % (args.main_ref, repo))
    regs, banner = None, None
    if args.as_if_committed:
        t = iso(datetime.datetime.now(UTC)) if args.as_if_committed == "now" else mp.utc_strict(args.as_if_committed, "--as-if-committed")
        regs = {f: {"on_main": True, "commit": "(not committed: dry run)", "time": t}
                for f in os.listdir(pred) if NAME_RE.match(f)}
        banner = "DRY RUN: every predictions file in %s is treated as first committed on main at %s." % (pred, t)
    vpath = args.versions or os.path.join(os.path.dirname(os.path.abspath(pred)), "versions.json")
    notes_in = load_versions(vpath if (args.versions or os.path.exists(vpath) or git is not None) else None, git, repo, args.main_ref)
    prev_path = args.previous
    if not prev_path:
        rd = os.path.join(os.path.dirname(os.path.abspath(pred)), "readings")
        cands = sorted(f for f in os.listdir(rd) if f.endswith(".txt")) if os.path.isdir(rd) else []
        prev_path = os.path.join(rd, cands[-1]) if cands else None
    previous = read_previous(prev_path) if prev_path else None
    counting = regs is None and args.main_ref in ("main", "origin/main") and git is not None
    lines, _, games_used = read(args.export, pred, notes_in, git, repo, args.main_ref, registrations=regs,
                                previous=previous, counting=counting, banner=banner)
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if args.out:
        try:
            with open(args.out, "x", encoding="utf-8", newline="\n") as fh:
                fh.write(text + "\n" + GAMES_MARK + "\n" + json.dumps(games_used, ensure_ascii=False, sort_keys=True) + "\n")
        except FileExistsError:
            print("REFUSED: %s exists; the reading was not written there." % args.out, file=sys.stderr)
            return 3
    return 0


# ---------------------------------------------------------------- self-test
# Rule v1 on the Oct 14 snapshot's 66 games (feedback only: all were played before any predictions file existed).
RULE_V1_66 = """
brew-01 dryde5b2 L t-vespiquen panel exact
brew-01 puegkh26 W - ruled_out -
brew-01 op2nw4iq L - unmatched -
brew-01 pzgxofc5 L - unmatched -
brew-03a 5j3gatiy L t-vespiquen panel exact
brew-03a i0b7q0aw L t-suicune panel exact
brew-03a fjrp6698 W - unmatched -
brew-03a j7ygejzg L - unmatched -
brew-04 dt62hbj1 W l-sharpedo readout exact
brew-05 265qsbyq L - unmatched -
brew-05 sxmmfqbf W - unmatched -
brew-05 inj3tqmf W g-dragonair_mega_rayquaza readout variant
brew-05 g4plkw2m W - unmatched -
brew-05 c3eehz66 L t-lucario panel variant
brew-05 q29m429j L - unmatched -
brew-05c k4koxjza L - unmatched -
brew-05c cgt39800 W - unmatched -
brew-05c sgyuq7p8 L - unmatched -
brew-06 b06l1 L t-lucario panel variant
brew-06 b06l2 L t-lucario panel variant
brew-06 b06l3 L - unmatched -
brew-06b tpc15fb7 L - unmatched -
brew-06b ys8h59kt L t-blaziken panel exact
brew-06b bj01ko8c L t-blaziken panel exact
brew-08 wu76b104 W - unmatched -
brew-08 izt3v99l W - unmatched -
brew-08 oxvly9rd L - unmatched -
brew-08 6vpilygm W g-dragonair_mega_rayquaza readout variant
brew-08 xy1ivenh W - unmatched -
brew-08 6v6uz8f4 L - unmatched -
brew-08 vxshsx64 W - unmatched -
brew-08 oubs7din W - unmatched -
brew-08 b1onjy8e L t-lucario panel variant
brew-08 66bj8pko W - unmatched -
brew-09 k9rp6pmw W - unmatched -
c-hydreigon-galarian-obstagoon-video-visib k95ae5i5 W - unmatched -
c-hydreigon-galarian-obstagoon-video-visib n85t8ocx L h-charizardy_entei readout exact
c-hydreigon-galarian-obstagoon-video-visib 5u42iufb L - unmatched -
c-hydreigon-galarian-obstagoon-video-visib ile7odgu W - unmatched -
c-hydreigon-galarian-obstagoon-video-visib gx13ee2a W - unmatched -
c-hydreigon-galarian-obstagoon-video-visib ztoknodg W - unmatched -
c-hydreigon-galarian-obstagoon-video-visib l6uu55cr L g-dragonair_mega_rayquaza readout variant
c-hydreigon-galarian-obstagoon-video-visib efkegujq L - unmatched -
c-mega-sharpedo-ex-gyarados-video-visible- lb8dqt2y L - unmatched -
c-skarmory-ex-chandelure 6tycxfqa W t-hydreigon panel exact
c-skarmory-ex-indeedee-ex-genesect-video-v bva14dpt W - unmatched -
c-skarmory-ex-indeedee-ex-genesect-video-v 69ex1k6d W - unmatched -
c-type-null-silvally-video-visible-core oefujszt W - unmatched -
d02 ks7cq6me L h-charizardy_entei readout exact
d02 1hwx3rpd L - unmatched -
d02 4a0xzylt W - unmatched -
d02 kzwhyst4 L - unmatched -
d07 zsy3l5cr W t-hydreigon panel variant
d07 k7mqsc2z W t-altaria panel exact
d07 y9vhwux3 W t-hydreigon panel variant
d07 pukrqofc L t-lucario panel exact
d12 htcgfxoj W l-sharpedo readout exact
d12 mk7rxbwl L - unmatched -
d12 pe0sas7w L - unmatched -
d12 4p1dhyul L - unmatched -
d12 zvste53r L - unmatched -
d12 cje2afoa W - unmatched -
d12 x737u7z9 L - unmatched -
d12 le8qdtg1 L - unmatched -
d12 y78azdr4 L t-blaziken panel exact
d12 ceratxro L t-suicune panel exact
"""
SEASON_START = "2026-10-14T06:00:00Z"
WRITTEN_AT = "2026-10-14T23:20:00Z"   # the fixture file's written_at
P_TIME = "2026-10-14T23:30:00Z"       # the synthetic first commit of deck 12's predictions file on main
WS_TIME = "2026-10-15T00:30:00Z"      # a whitespace-only edit of the deck file on main
NEWEST_AT_WRITING = "2026-10-15T00:50:00Z"   # fixture: the newest video at writing (a clock problem: after P_TIME)
ADD_COMMIT_TIME = "2026-10-15T01:30:00Z"     # the m32 addendum's commit, on a side branch
A_TIME = "2026-10-15T03:15:00Z"              # ... fast-forwarded into main (git) / registered (no git)
R2_TIME = "2026-10-15T03:50:00Z"             # an addendum that restates kx3_slow (a fixture the writer would refuse)
CARD_BRANCH_TIME = "2026-10-15T04:00:00Z"    # a real card change, committed on a branch (git only) ...
B12_TIME = "2026-10-15T04:45:00Z"            # a second deck file sharing section d12, with its predictions file (git only)
CHANGE_TIME = "2026-10-15T05:00:00Z"         # ... merged into main with --no-ff (git only)
DEL_TIME = "2026-10-15T07:00:00Z"            # the m32 addendum deleted from main (git only)
SYNTH = [  # (id, ts, note, opp, result): later d12 games
    ("syn-margin", "2026-10-14T23:55:00Z", "2nd | 20261014_233500000_iOS.MP4 | Defeat.", "Mega Lucario ex / Riolu", "L"),
    ("syn-newest", "2026-10-15T00:55:00Z", "1st | 20261015_004500000_iOS.MP4 | Victory.", "Combee / Vespiquen ex", "W"),
    ("syn-seen", "2026-10-15T01:05:00Z", "1st | 20261015_010000000_iOS.MP4 | Defeat.", "Weezing ex / Hoopa ex", "L"),
    ("syn-test", "2026-10-15T02:10:00Z", "1st | 20261015_020000000_iOS.MP4 | Victory 3-1.", "Mega-Blaziken ex / Torchic", "W"),
    ("syn-conc", "2026-10-15T02:30:00Z", "2nd | vs plz_concede | 20261015_022000000_iOS.MP4 | Win 0–0 by opponent concession at 01:10.", "Magikarp", "W"),
    ("syn-mismatch", "2026-10-15T02:45:00Z", "1st | 20261015_024000000_iOS.MP4 | Victory.", "Hydreigon / Bombirdier", "W"),
    ("syn-checked", "2026-10-15T02:55:00Z", "2nd | 20261015_025000000_iOS.MP4 | Defeat.", "Mega Lucario ex / Lucario", "L"),
    ("syn-novideo", "2026-10-15T03:00:00Z", "", "Tapu Koko ex / Oricorio", "L"),
    ("syn-agentvideo", "2026-10-15T03:20:00Z", "2nd | Defeat 1-3.", "Suicune ex / Baxcalibur", "L"),
    ("syn-doubtful", "2026-10-15T03:40:00Z", "1st | 20261015_040000000_iOS.MP4 | Defeat.", "Mega Sceptile ex / Butterfree", "L"),
    ("syn-confirmed", "2026-10-15T06:00:00Z", "2nd | 20261015_054000000_iOS.MP4 | Victory 3-2.", "M Altaria ex / Espeon", "W"),
]
SYNTH_GIT_ONLY = [
    ("syn-before-merge", "2026-10-15T04:40:00Z", "1st | 20261015_043000000_iOS.MP4 | Defeat.", "Hydreigon / Mega Absol ex", "L"),
    ("syn-label-b", "2026-10-15T04:57:00Z", "1st | Deck 12-B | 20261015_045600000_iOS.MP4 | Victory.", "Mega Blaziken ex", "W"),
    ("syn-ambiguous", "2026-10-15T04:59:00Z", "2nd | 20261015_045800000_iOS.MP4 | Defeat.", "Tapu Koko ex", "L"),
    ("syn-after-change", "2026-10-15T06:10:00Z", "1st | Deck 12-A | 20261015_053000000_iOS.MP4 | Victory 3-0.", "Mega Altaria ex / Espeon", "W"),
]
MALFORMED = [{"id": "syn-bad-ts", "ts": "1792033200000", "note": "", "opp": "x", "result": "W"},
             {"id": "syn-test", "ts": 1792030200000, "note": "duplicate id", "opp": "x", "result": "W"},
             "not a game"]
VERSION_NOTES = {"games": {
    "d12/4p1dhyul": {"version": "5c3b7d688afa", "status": "confirmed", "evidence": "self-test fixture: deck-share QR frame"},
    "d12/syn-confirmed": {"version": "5c3b7d688afa", "status": "confirmed", "evidence": "self-test fixture: his side's cards in the packet"},
    "d12/syn-agentvideo": {"video": "20261015_031000000_iOS.MP4", "evidence": "self-test fixture: Battle Logs listing"},
    "d12/syn-mismatch": {"cards": "mismatch: Leaf Cape (fixture)", "evidence": "self-test fixture: packet"},
    "d12/syn-checked": {"cards": "checked", "evidence": "self-test fixture: packet"},
    "d12/syn-novideo": {"version": "5c3b7d688afa"},     # no evidence: ignored
}}


def _ms(s):
    return int(datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def _tmp_git(root, *args, when=None):
    env = dict(os.environ)
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = "@%d +0000" % (_ms(when) // 1000)
    r = subprocess.run(["git", "-C", root, "-c", "user.name=read_ladder self-test", "-c", "user.email=selftest@invalid",
                        "-c", "init.defaultBranch=main", "-c", "core.logAllRefUpdates=true"] + list(args), capture_output=True, env=env)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (args[0], r.stderr.decode("utf-8", "replace").strip()[:200]))


def _listing(root):
    out = []
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            p = os.path.join(d, f)
            st = os.stat(p)
            out.append((os.path.relpath(p, root), st.st_size, st.st_mtime_ns))
    return sorted(out)


def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def selftest(repo, export, use_git=True):
    fails = []

    def check(cond, what):
        print(("  ok    " if cond else "  FAIL  ") + what)
        if not cond:
            fails.append(what)

    print("read_ladder self-test on the export %s (deck 12's predictions built from %s)" % (export, repo))
    docs = load_export(export)
    games = {g.get("id"): (d, g) for d, gs in docs.items() for g in gs}
    # 1. rule v1 over the snapshot's 66 games (all feedback)
    table = [ln.split() for ln in RULE_V1_66.strip().splitlines()]
    bad = []
    for doc_id, gid, res, lst, status, fit in table:
        if gid not in games:
            bad.append("%s missing" % gid)
            continue
        d, g = games[gid]
        m = mp.match_opponent(g.get("opp"))
        got = (d, g.get("result"), m["list"] or "-", m["status"].replace(" ", "_"), m["fit"] or "-")
        if got != (doc_id, res, lst, status, fit):
            bad.append("%s: %s" % (gid, got))
    check(len(table) == 66 and not bad, "rule v1 on the snapshot's 66 games equals the frozen table%s" % (": " + "; ".join(bad[:5]) if bad else ""))
    snap = [games[t[1]] for t in table if t[1] in games]
    for label, sel in (("last season", lambda g: g["ts"] < _ms(SEASON_START)), ("this season", lambda g: g["ts"] >= _ms(SEASON_START))):
        rows = [(d, g, mp.match_opponent(g["opp"])) for d, g in snap if sel(g)]
        cnt = {}
        for d, g, m in rows:
            k = m["status"] + ("/" + m["fit"] if m["fit"] else "")
            w, l = cnt.get(k, (0, 0))
            cnt[k] = (w + (g["result"] == "W"), l + (g["result"] != "W"))
        print("        %s: %d games; %s" % (label, len(rows), "; ".join("%s %d (%d-%d)" % (k, w + l, w, l) for k, (w, l) in sorted(cnt.items()))))
    lastp = sum(1 for d, g in snap if g["ts"] < _ms(SEASON_START) and mp.match_opponent(g["opp"])["status"] == "panel")
    thisp = sum(1 for d, g in snap if g["ts"] >= _ms(SEASON_START) and mp.match_opponent(g["opp"])["status"] == "panel")
    check((lastp, thisp) == (14, 2), "panel games: %d of 56 last season, %d of 10 this season (16 of 66)" % (lastp, thisp))
    # 2. facts from the notes: video start, seat, concessions
    f = game_facts("d12", games["htcgfxoj"][1])[0]
    check((f["played"], f["time_from"], f["seat"]) == ("2026-10-14T14:25:46Z", "video", "1st"),
          "htcgfxoj: played %s from the video name (logged %s), seat %s" % (f["played"], f["logged"], f["seat"]))
    f2 = game_facts("d12", games["mk7rxbwl"][1])[0]
    check(f2["seat"] == "2nd" and f2["played"] == "2026-10-14T14:31:11Z", "mk7rxbwl: seat 2nd, played 14:31:11Z")
    tids = {t[1] for t in table}
    conc = [gid for gid, (d, g) in games.items() if gid in tids and game_facts(d, g)[0]["concession"] and g["result"] == "W"]
    check(len(conc) == 12 and sum(1 for x in conc if games[x][0] == "brew-08") == 6,
          "wins by the opponent's concession in the snapshot: %d (brew 08: %d of its 7 wins)" % (len(conc), sum(1 for x in conc if games[x][0] == "brew-08")))
    ef = games["efkegujq"][1]
    check("concede" in ef["note"] and not game_facts("c-x", ef)[0]["concession"]
          and game_facts("c-x", dict(ef, note=ef["note"] + " Opponent concedes at 09:40."))[0]["concession"],
          "the opponent's name 'plz_concede' in the note is not a concession; 'opponent concedes' is")
    for txt in ("Victory by forfeit", "opponent resigned", "they gave up", "Opponent quit before finishing game"):
        check(game_facts("x", {"id": "a", "ts": _ms("2026-10-15T00:00:00Z"), "note": txt, "opp": "", "result": "W"})[0]["concession"],
              "'%s' reads as a concession" % txt)
    ft = game_facts("x", {"id": "a", "ts": _ms("2026-10-15T00:00:00Z"), "note": "Screen_Recording_20261014_190000_Pokemon.mp4",
                          "opp": "", "result": "W"})[0]
    check(ft["time_from"] == "time unknown", "a non-iOS recording name gives no play time ('time unknown')")
    for g, why in (({"id": "a", "ts": 1792033200, "note": "", "opp": "", "result": "W"}, "seconds"),
                   ({"id": "a", "ts": "1792033200000", "note": "", "opp": "", "result": "W"}, "not a number"),
                   ({"id": "a", "ts": float("nan"), "note": "", "opp": "", "result": "W"}, "not a number"),
                   ({"id": "a", "ts": 1792033200000 * 1000, "note": "", "opp": "", "result": "W"}, "out of range"),
                   ({"ts": 1792033200000, "note": "", "opp": "", "result": "W"}, "no game id"),
                   ("a string", "not an object")):
        r, w = game_facts("x", g)
        check(r is None and why in w, "a malformed entry is not read (%s)" % w)
    r, w = game_facts("x", {"id": "a", "ts": 1792033200000, "note": 5, "opp": 7, "result": 1})
    check(r is not None and r["opp"] == "7" and not r["counted"], "numbers in note, opp or result do not crash the reading")
    # export formats
    tmpx = tempfile.mkdtemp(prefix="read_ladder_export_")
    try:
        px = os.path.join(tmpx, "list_output.txt")
        with open(px, "w", encoding="utf-8") as fh:
            fh.write('%d documents from collection "logs":\n=== BEGIN ARTIFACT DB 92158b93 — data ===\n' % len(docs))
            for d, gs in sorted(docs.items()):
                fh.write(json.dumps({"id": d, "data": {"games": gs, "updated": 0}, "version": 1}, ensure_ascii=False) + "\n")
            fh.write("=== END ARTIFACT DB 92158b93 ===\n")
        check(load_export(px) == docs, "the inline 'list' output reads the same as the folder export (%d sections)" % len(docs))
        pa = os.path.join(tmpx, "array_bom.json")
        _write(pa, b"\xef\xbb\xbf" + json.dumps([{"id": d, "data": {"games": gs}} for d, gs in sorted(docs.items())], indent=2).encode("utf-8"))
        check(load_export(pa) == docs, "a pretty-printed JSON list with a byte-order mark reads the same")
        pd = os.path.join(tmpx, "d12.json")
        _write(pd, b"\xef\xbb\xbf" + json.dumps({"games": docs["d12"]}).encode("utf-8"))
        check(load_export(pd) == {"d12": docs["d12"]}, "one per-section file reads under its file name")
        nest = os.path.join(tmpx, "out_dir")
        for d, gs in docs.items():
            _write(os.path.join(nest, "logs", d + ".json"), json.dumps({"games": gs}))
            _write(os.path.join(nest, "logs", "old", "logs", d + ".json"), json.dumps({"games": gs}))
        check(load_export(nest) == docs, "an out_dir folder reads its logs/ files only (an older copy deeper down is not counted twice)")
        pc = os.path.join(tmpx, "page1.txt")
        _write(pc, open(px, encoding="utf-8").read() + "next_cursor: abc\n")
        for p, why in ((pc, "first page"), (os.path.join(tmpx, "empty.json"), "no games")):
            if not os.path.exists(p):
                _write(p, "[]")
            try:
                load_export(p)
                check(False, "an unusable export is refused (%s)" % why)
            except SystemExit as e:
                check(why in str(e), "an unusable export is refused (%s)" % why)
    finally:
        shutil.rmtree(tmpx, ignore_errors=True)

    # 3. readings on a temporary repository holding deck 12's predictions files
    base_args = mp.d12_argv(repo, "/nonexistent", sources=("slow", "exam5", "m64", "floor", "floor_sep30"),
                            extra=["--no-git", "--export", export, "--log-label", "Deck 12-A"])
    doc = mp.build(mp.parser().parse_args(base_args), repo, mp.Git(repo, enabled=False))
    vid = doc["deck"]["version_id"]
    check(vid == mp.DECK12_ID and doc["ladder_log_at_writing"]["games_logged"] == 66
          and "d12/htcgfxoj" in doc["ladder_log_at_writing"]["game_keys"]
          and doc["ladder_log_at_writing"]["newest_video_start"] == "2026-10-14T16:43:28Z",
          "deck 12's predictions file: version %s; the 66 logged games and the newest video (16:43:28) saved at writing" % vid)
    doc["written_at"] = WRITTEN_AT
    doc["ladder_log_at_writing"]["newest_video_start"] = NEWEST_AT_WRITING
    doc["ladder_log_at_writing"]["game_keys"].append("d12/syn-seen")
    add_args = ["--repo", repo, "--deck", mp.DECK12, "--log-doc", "d12", "--exam", mp.D12_SOURCES["m32"], "--no-git",
                "--addendum", "m32", "--out-dir", "/nonexistent"]
    tmp = tempfile.mkdtemp(prefix="read_ladder_selftest_")
    try:
        root = os.path.join(tmp, "repo")
        deck_path = os.path.join(root, mp.DECK12)
        pred_dir = os.path.join(root, mp.DEFAULT_OUT)
        pred_name = "%s@%s.json" % (doc["deck"]["name"], vid)
        add_name = "%s@%s+m32.json" % (doc["deck"]["name"], vid)
        r2_name = "%s@%s+restated.json" % (doc["deck"]["name"], vid)
        with open(os.path.join(repo, mp.DECK12), "rb") as fh:
            deck_bytes = fh.read()
        text = deck_bytes.decode("utf-8")
        ws_text = "# deck 12 (whitespace and a comment only)\r\n" + "\r\n".join("  " + l + "   " for l in text.splitlines()) + "\r\n\r\n"
        changed_text = text.replace("1 Lisia B1 226", "1 Sabrina A1 225")
        b_text = text.replace("1 Copycat B1 225", "1 Cyrus A2 150")
        check(mp.card_list_sha256(ws_text)[:12] == vid and mp.card_list_sha256(changed_text)[:12] != vid
              and len({vid, mp.card_list_sha256(changed_text)[:12], mp.card_list_sha256(b_text)[:12]}) == 3,
              "the whitespace-only deck edit keeps version %s; the card changes do not" % vid)

        def make_addendum(base_path):
            a = mp.parser().parse_args(add_args + ["--base", base_path])
            d = mp.build(a, repo, mp.Git(repo, enabled=False))
            d["written_at"] = "2026-10-15T01:20:00Z"     # a fixture time, before its commit, so the test does not depend on today's clock
            return d
        restated = copy.deepcopy(doc)
        restated["bots"] = [copy.deepcopy(b) for b in doc["bots"] if b["id"] == "kx3_slow"]
        restated["forecast"]["per_bot"] = {"kx3_slow": {k: (v if k != "per_list" else {kk: vv / 2 for kk, vv in v.items()})
                                                        for k, v in doc["forecast"]["per_bot"]["kx3_slow"].items()}}
        restated["duplicates"] = []
        b_doc = copy.deepcopy(doc)
        b_cl = mp.card_list_sha256(b_text)
        b_doc["deck"].update(name="12-b-fake", file="decks/dustin/12-b-fake.txt", version_id=b_cl[:12], card_list_sha256=b_cl,
                             log_label="Deck 12-B")
        b_name = "12-b-fake@%s.json" % b_cl[:12]

        git_mode = False
        if use_git:
            try:
                os.makedirs(root)
                _tmp_git(root, "init", "-q")
                _write(deck_path, deck_bytes)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "deck 12", when="2026-09-24T19:56:16Z")
                mp.write_new(os.path.join(pred_dir, pred_name), doc)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "predictions", when=P_TIME)
                _write(deck_path, ws_text)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "whitespace", when=WS_TIME)
                _tmp_git(root, "checkout", "-q", "-b", "side")
                adoc = make_addendum(os.path.join(pred_dir, pred_name))
                mp.write_new(os.path.join(pred_dir, add_name), adoc)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "m32 addendum on a branch", when=ADD_COMMIT_TIME)
                _tmp_git(root, "checkout", "-q", "main")
                _tmp_git(root, "merge", "-q", "--ff-only", "side", when=A_TIME)
                restated["addendum_to"] = {"file": pred_name, "sha256": mp.sha256_file(os.path.join(pred_dir, pred_name))}
                mp.write_new(os.path.join(pred_dir, r2_name), restated)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "restated", when=R2_TIME)
                _tmp_git(root, "checkout", "-q", "-b", "cards")
                _write(deck_path, changed_text)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "a card change on a branch", when=CARD_BRANCH_TIME)
                _tmp_git(root, "checkout", "-q", "main")
                _write(os.path.join(root, "decks/dustin/12-b-fake.txt"), b_text)
                mp.write_new(os.path.join(pred_dir, b_name), b_doc)
                _tmp_git(root, "add", "-A")
                _tmp_git(root, "commit", "-q", "-m", "deck 12-B", when=B12_TIME)
                _tmp_git(root, "merge", "-q", "--no-ff", "-m", "merge the card change", "cards", when=CHANGE_TIME)
                _write(deck_path, ws_text)   # the working copy is back on the version's card list
                git_mode = True
            except Exception as e:  # e.g. no git: fall back to the no-git reading
                print("  skip  temporary git repository (%s): reading without git" % e)
                shutil.rmtree(root, ignore_errors=True)
        if not git_mode:
            _write(deck_path, ws_text)
            mp.write_new(os.path.join(pred_dir, pred_name), doc)
            mp.write_new(os.path.join(pred_dir, add_name), make_addendum(os.path.join(pred_dir, pred_name)))
            restated["addendum_to"] = {"file": pred_name, "sha256": mp.sha256_file(os.path.join(pred_dir, pred_name))}
            mp.write_new(os.path.join(pred_dir, r2_name), restated)
        # the export: the snapshot plus later d12 games and three malformed entries
        exp = os.path.join(tmp, "export", "logs")
        os.makedirs(exp)
        for d, gs in docs.items():
            extra = (SYNTH + (SYNTH_GIT_ONLY if git_mode else [])) if d == "d12" else []
            data = {"games": gs + [{"id": i, "ts": _ms(ts), "note": n, "opp": o, "result": r} for i, ts, n, o, r in extra]
                    + (MALFORMED if d == "d12" else [])}
            with open(os.path.join(exp, d + ".json"), "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False)
        regs = None if git_mode else {
            pred_name: {"on_main": True, "commit": "(no git)", "time": P_TIME},
            add_name: {"on_main": True, "commit": "(no git)", "time": A_TIME},
            r2_name: {"on_main": True, "commit": "(no git)", "time": R2_TIME}}
        git = mp.Git(root) if git_mode else None
        before = _listing(tmp)
        lines, res, used = read(os.path.join(tmp, "export"), pred_dir, VERSION_NOTES, git, root, "main", registrations=regs)
        check(_listing(tmp) == before, "the reader wrote nothing")
        print("  ---- the reading (git: %s) ----" % ("temporary repository" if git_mode else "not used"))
        for ln in lines:
            print("  | " + ln)
        print("  ----")
        R = res["groups"].get("%s@%s" % (doc["deck"]["name"], vid))
        check(R is not None, "the reading has deck 12's version")
        if R is None:
            raise RuntimeError("no reading")
        reg = R["reg"]
        check(reg.get("on_main") and reg.get("time") == P_TIME, "the file's registration is %s" % reg.get("time"))
        rows = {r["id"]: r for r in R["rows"]}
        d12 = [t[1] for t in table if t[0] == "d12"]
        check(all(rows.get(g, {}).get("class") == "feedback" for g in d12), "deck 12's 10 logged games are all feedback")
        check(all(rows[g]["time_from"] == "video" for g in d12), "all 10 have a video start time")
        check(rows["4p1dhyul"]["tie"] == "confirmed" and sum(1 for g in d12 if rows[g]["tie"] == "assumed") == 9,
              "ties: 9 assumed, 1 confirmed (from the version notes)")
        fb10 = summarise_class([rows[g] for g in d12], [b for b in doc["bots"] if b["in_bot_comparison"]], doc["forecast"]["per_bot"])
        check(fb10["record"] == "2-8" and fb10["matched"]["n"] == 2 and fb10["matched"]["record"] == "0-2"
              and fb10["matched"]["exact"]["n"] == 2 and fb10["off_panel"]["record"] == "2-6"
              and fb10["off_panel"]["parts"].get("l-sharpedo", {}).get("record") == "1-0"
              and fb10["off_panel"]["parts"].get("unmatched", {}).get("record") == "1-6",
              "the 10 games: 2-8; matched 0-2 (2 exact); off-panel 2-6 (Sharpedo readout 1-0, unmatched 1-6)")
        kx = fb10["matched"]["per_bot"]["kx3_slow"]
        check(abs(kx["expected"] - 1.037) < 0.01 and abs(kx["p_one_sided"] - 0.222) < 0.002,
              "the 10 games, matched, frozen kx3: 0 wins v %.2f expected, chance %.3f (%s)" % (kx["expected"], kx["p_one_sided"], chance_words(kx["p_one_sided"])))
        lv = fb10["level"]
        check(lv["kx3_slow"]["range"] == [3, 9] and lv["kx3_slow"]["where"] == "below"
              and abs(lv["kx3_slow"]["p_two_sided"] - 0.024) < 0.001 and abs(lv["kx3_slow"]["p_one_sided"] - 0.012) < 0.001,
              "the 10 games, level, frozen kx3: range 3-9, 2 is below, p = %.3f two-sided (%s), %.3f one-sided"
              % (lv["kx3_slow"]["p_two_sided"], chance_words(lv["kx3_slow"]["p_two_sided"]), lv["kx3_slow"]["p_one_sided"]))
        check(lv["km3_slow_same_deals"]["range"] == [1, 7] and lv["km3_slow_same_deals"]["where"] == "inside"
              and lv["km3_floor"]["range"] == [1, 6] and lv["km3_floor"]["where"] == "inside"
              and abs(lv["km3_slow_same_deals"]["p_two_sided"] - 0.5748) < 0.001 and abs(lv["km3_floor"]["p_two_sided"] - 0.6113) < 0.001,
              "the 10 games, level: inside km3's ranges (1-7 same deals, p %.4f; 1-6 floor, p %.4f)"
              % (lv["km3_slow_same_deals"]["p_two_sided"], lv["km3_floor"]["p_two_sided"]))
        check(set(lv) == {"kx3_slow", "km3_slow_same_deals", "km3_floor"}, "only bots on the engine pinned at writing are compared")
        # the time rules
        expect_cls = {"syn-margin": ("feedback", "+10 min"), "syn-newest": ("feedback", "newest video"),
                      "syn-seen": ("feedback", "already logged"), "syn-novideo": ("feedback", "time unknown"),
                      "syn-doubtful": ("feedback", "time doubtful"), "syn-test": ("test", ""), "syn-conc": ("test", ""),
                      "syn-checked": ("test", ""), "syn-agentvideo": ("test", ""), "syn-confirmed": ("test", "")}
        for gid, (cls, why) in expect_cls.items():
            r = rows.get(gid, {})
            check(r.get("class") == cls and why in r.get("why", ""), "%s: %s%s" % (gid, r.get("class"), (" (%s)" % r.get("why")) if r.get("why") else ""))
        check(rows["syn-agentvideo"]["time_from"] == "video (version notes)" and rows["syn-novideo"]["tie"] == "assumed",
              "a video name an agent added to the notes gives the play time; a note with no evidence is ignored")
        check("syn-mismatch" not in rows and res["not_read"].get("an agent found a card mismatch") == 1,
              "a game with an agent's card mismatch is not read")
        check(rows["syn-test"]["match"]["list"] == "t-blaziken" and rows["syn-test"]["match"]["fit"] == "exact"
              and rows["syn-test"]["tie"] == "assumed", "'Mega-Blaziken ex' matched exact, tied (assumed) across the whitespace-only edit")
        check(rows["syn-conc"]["concession"] and rows["syn-conc"]["win"] and rows["syn-conc"]["match"]["status"] == "unmatched",
              "a concession win (opponent named 'plz_concede'): a full win, unmatched")
        check(rows["syn-confirmed"]["tie"] == "confirmed" and rows["syn-confirmed"]["match"]["list"] == "t-altaria",
              "a version-note game is 'confirmed'; 'M Altaria ex' matched t-altaria")
        t = R["classes"].get("test", {})
        want_t = ("3-3", "2-3", 5) if git_mode else ("3-2", "2-2", 4)
        check(t.get("record") == want_t[0] and t.get("concession_wins") == 1 and t["matched"]["record"] == want_t[1]
              and t["matched"]["n"] == want_t[2] and t["off_panel"]["record"] == "1-0" and t["off_panel_concession_wins"] == 1
              and t["cards_checked"] == {"n": 1, "record": "0-1"},
              "test games: %s (1 concession win in full); matched %s; off-panel 1-0; cards checked on 1 (0-1)" % (want_t[0], want_t[1]))
        al = t["matched"]["per_bot"]["kx3_slow"]["allowance"]
        check(abs(al["wins"] - (int(want_t[1][0]) + 0.25)) < 1e-9 and abs(al["expected"] - (t["matched"]["per_bot"]["kx3_slow"]["expected"] + 0.25 * 0.6125)) < 1e-6,
              "the concession allowance: 1 in 4 of the 1 off-panel concession win counted as a panel win")
        fbk = R["classes"]["feedback"]
        check(fbk["record"] == "3-12" and fbk["n"] == 15, "feedback games: %s over %d (the 10 logged ones and 5 synthetic)" % (fbk["record"], fbk["n"]))
        wn = R["without_notes"]
        check(any("syn-agentvideo" in c and "video added" in c for c in wn["changes"]) and any("syn-mismatch" in c and "removed" in c for c in wn["changes"]),
              "the reading lists what the version notes changed: %s" % "; ".join(wn["changes"]))
        A = R["addenda"].get("m32")
        check(A is not None and A["reg"]["time"] == A_TIME and A["n_test"] == (2 if git_mode else 1),
              "the m32 addendum is read under its base file from %s: %s test games for its bot" % (A and A["reg"]["time"], A and A["n_test"]))
        if git_mode:
            check(A["reg"].get("commit_time") == ADD_COMMIT_TIME and A["reg"].get("reached_main") == A_TIME
                  and any("fast-forwarded" in ln for ln in lines),
                  "a fast-forwarded addendum counts from when the reflog shows it reaching main (%s), not its commit (%s)" % (A_TIME, ADD_COMMIT_TIME))
            check(rows["syn-test"]["add_classes"]["m32"] == "feedback", "a game between the addendum's commit and its arrival on main is feedback for it")
            check(rows["syn-before-merge"]["class"] == "test" and rows["syn-before-merge"]["tie"] == "assumed",
                  "a game played after a branch's card change but before its --no-ff merge is still this version")
            rb = res["groups"].get("12-b-fake@%s" % b_cl[:12], {}).get("rows", [])
            check([r["id"] for r in rb] == ["syn-label-b"] and rb[0]["class"] == "test",
                  "two deck files share section d12: the game whose note names 'Deck 12-B' is read with that file")
            nr = res["not_read"]
            check(any(k.startswith("ambiguous") for k in nr) and "syn-ambiguous" not in rows and "syn-after-change" not in rows
                  and any("no predictions file (%s)" % mp.card_list_sha256(changed_text)[:12] in k for k in nr),
                  "a game naming no deck is ambiguous; a 'Deck 12-A' game after the card change has no predictions file (%s)" % sorted(nr)[:3])
        tal = res["tally"]
        kx_t = tal and tal.get("kx3_slow@4ebb30a9")
        fc = doc["forecast"]["per_bot"]["kx3_slow"]["per_list"]
        want_E = fc["t-blaziken"] + fc["t-suicune"] + fc["t-lucario"] + fc["t-altaria"] + (fc["t-hydreigon"] if git_mode else 0)
        if git_mode:
            want_E += fc["t-blaziken"]    # 12-B's forecasts are deck 12's (a fixture copy)
        check(kx_t and kx_t["n"] == (6 if git_mode else 4) and abs(kx_t["expected"] - want_E) < 1e-6
              and abs(kx_t["coin"] - 0.25) < 1e-9 and "m32_exam@69a5a441" not in tal,
              "running tally: frozen kx3 on %s matched test games, E %.3f from the earliest registered file (the restating "
              "addendum is not used); m32 (older engine) not in it" % (kx_t and kx_t["n"], kx_t and kx_t["expected"]))
        check(any("restates kx3_slow" in ln for ln in lines), "an addendum that restates a base bot is flagged")
        n_syn = len(SYNTH) + (len(SYNTH_GIT_ONLY) if git_mode else 0)
        check(res["games_logged"] == 66 + n_syn + len(MALFORMED) and res["not_read"].get("malformed entry (log time is not a number)") == 1
              and res["not_read"].get("malformed entry (not an object)") == 1 and res["not_read"].get("the same game id twice in section d12") == 1,
              "malformed entries (a ts as text, a non-object, a duplicate id) are counted as not read, not crashed on")
        # integrity and deletions (git)
        if git_mode:
            with open(os.path.join(pred_dir, pred_name), "ab") as fh:
                fh.write(b" ")
            lines2, res2, _ = read(os.path.join(tmp, "export"), pred_dir, VERSION_NOTES, mp.Git(root), root, "main")
            R2 = res2["groups"]["%s@%s" % (doc["deck"]["name"], vid)]
            check(any(ln.strip().startswith("INTEGRITY: the working copy") for ln in lines2) and not R2["reg"]["working_identical"]
                  and R2["classes"]["feedback"]["record"] == "3-12",
                  "a predictions file edited after its commit is flagged; the reading uses the committed version")
            _tmp_git(root, "rm", "-q", os.path.join(mp.DEFAULT_OUT, add_name))
            _tmp_git(root, "commit", "-q", "-m", "remove the m32 addendum", when=DEL_TIME)
            lines3, res3, _ = read(os.path.join(tmp, "export"), pred_dir, VERSION_NOTES, mp.Git(root), root, "main")
            R3 = res3["groups"]["%s@%s" % (doc["deck"]["name"], vid)]
            check("m32" in R3["addenda"] and any("deleted from main" in ln for ln in lines3),
                  "a predictions file deleted from main is still read from its first commit, and flagged")
        else:
            print("  skip  integrity, deletion, fast-forward, merge and shared-section cases (no git)")
        # CODE CHANGED: a file whose recorded code differs
        cc = copy.deepcopy(doc)
        cc["written_by"]["code_sha256"]["read_ladder.py"] = "0" * 64
        ccdir = os.path.join(tmp, "code_changed")
        mp.write_new(os.path.join(ccdir, pred_name), cc)
        lines4, _, _ = read(os.path.join(tmp, "export"), ccdir, None, None, None, "main",
                            registrations={pred_name: {"on_main": True, "commit": "(no git)", "time": P_TIME}})
        check(any("CODE CHANGED" in ln and "read_ladder.py" in ln for ln in lines4), "a file written by other code is flagged CODE CHANGED")
        wa = copy.deepcopy(doc)
        wa["written_at"] = "2026-10-15T01:00:00Z"
        wadir = os.path.join(tmp, "written_at")
        mp.write_new(os.path.join(wadir, pred_name), wa)
        lines5, res5, _ = read(os.path.join(tmp, "export"), wadir, None, None, None, "main",
                               registrations={pred_name: {"on_main": True, "commit": "(no git)", "time": P_TIME}})
        check(res5["groups"]["%s@%s" % (doc["deck"]["name"], vid)]["reg"]["time"] == "2026-10-15T01:00:00Z"
              and any("before the file's own written_at" in ln for ln in lines5),
              "a commit time earlier than the file's written_at is flagged and the later time is used")
        # --out, and the comparison with the previous reading
        outp = os.path.join(tmp, "reading.txt")
        a = ["--export", os.path.join(tmp, "export"), "--predictions", pred_dir, "--repo", root, "--out", outp] + ([] if git_mode else ["--no-git"])
        with contextlib.redirect_stdout(io.StringIO()):
            rc = main(a)
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc2 = main(a)
        print("  (expected refusal, as printed: %s)" % err.getvalue().strip().replace(tmp, "<tmp>"))
        check(rc == 0 and os.path.exists(outp) and rc2 == 3, "--out writes a new file and never overwrites it")
        prev = read_previous(outp)
        d12p = os.path.join(tmp, "export", "logs", "d12.json")
        dd = json.load(open(d12p, encoding="utf-8"))
        for g in dd["games"]:
            if isinstance(g, dict) and g.get("id") == "syn-test":
                g["opp"] = "Mega-Blaziken ex / Torchic?"
            if isinstance(g, dict) and g.get("id") == "ceratxro":
                g["result"] = "W"
        json.dump(dd, open(d12p, "w", encoding="utf-8"), ensure_ascii=False)
        lines6, res6, _ = read(os.path.join(tmp, "export"), pred_dir, VERSION_NOTES, git, root, "main", registrations=regs, previous=prev)
        ch = res6.get("changes_since_previous", [])
        check(len(ch) == 2 and any("syn-test" in c and "opp" in c for c in ch) and any("ceratxro" in c and "result" in c for c in ch),
              "a later reading lists Ladder Log edits since the previous one: %s" % "; ".join(ch))
        check(res6["groups"]["%s@%s" % (doc["deck"]["name"], vid)]["classes"]["test"]["inferred"]["n"] == 1,
              "adding a guess word moves a game to 'inferred', and the edit is listed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELF-TEST %s (%d failed)" % ("PASSED" if not fails else "FAILED", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
