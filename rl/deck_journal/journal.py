#!/usr/bin/env python3
"""Deck version journal (rl/deck_journal/SPEC.md): one append-only record per deck of every version of its list,
what changed, why, and what each test, bot and ladder game said about it. Standard library only; cards only
through lib/card.py's database and the deck-code catalog; no engine binary.

  journal.py add-version --deck STEM --list-file F --origin TEXT --by WHO [--parent ID] [--file DECKFILE]
                         [--origin-source PATH] [--reason TEXT --reason-by WHO --reason-source PATH] [--title T]
  journal.py add-result  --deck STEM --kind played --packet DIR --by WHO [--binding TEXT --version ID]
  journal.py add-result  --deck STEM --kind bot --version ID --source PATH --by WHO
  journal.py add-result  --deck STEM --kind setup --version ID --run DIR --tester FILE --measures JSON --by WHO ...
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


def committed(root, rel):
    """The last commit touching the path; refuses a path that does not exist, is not tracked, or has edits."""
    if not os.path.exists(os.path.join(root, rel)):
        raise Refused("source path does not exist: %s" % rel)
    if not _git(root, "ls-files", "--", rel).strip():
        raise Refused("source path is not committed: %s" % rel)
    dirty = [x for x in _git(root, "status", "--porcelain", "--", rel).splitlines() if not x.startswith("??")]
    if dirty:
        raise Refused("source path has uncommitted changes: %s" % rel)
    return _git(root, "log", "-1", "--format=%H", "--", rel).strip()


def head(root):
    try:
        return _git(root, "rev-parse", "HEAD").strip()
    except Refused:
        return "no-git"


def _main_ref(git):
    for r in ("main", "origin/main"):
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
    for k in ("deck", "schema"):
        if old.get(k) != new.get(k):
            problems.append("%s: %s changed" % (where, k))
    for v in old["versions"]:
        n = nv.get(v["id"])
        if n is None:
            continue
        for k in v:
            if k != "results" and n.get(k) != v[k]:
                problems.append("%s: version %s: %s was changed" % (where, v["id"], k))
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
        if v["parent"] is not None and v["parent"] not in seen:
            problems.append("%s: parent %s is not an earlier version" % (v["id"], v["parent"]))
        if v["plays_same_as"] is not None and v["plays_same_as"] not in seen:
            problems.append("%s: plays_same_as %s is not an earlier version" % (v["id"], v["plays_same_as"]))
        seen.append(v["id"])
    return problems


def save(path, doc, root=ROOT, ref="main"):
    """Write the journal after checking it against the copy on disk and main's committed copy."""
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
def add_version(doc, root, *, list_text=None, energy=None, pairs=None, origin, reason, by, commit=None, parent=None,
                file=None, origin_source=None, at=None, check_committed=True):
    """Add a version. The id, list, code_cards, diff, printing_only and plays_same_as are computed here."""
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
            file_commit = committed(root, file)
        with open(os.path.join(root, file), encoding="utf-8") as fh:
            if list_id(lines_of(fh.read())) != vid:
                raise Refused("%s is not this list (id %s)" % (file, vid))
    if origin_source and check_committed:
        committed(root, origin_source)
    if parent is not None:
        par, basis = find(doc, parent), "stated"
    elif doc["versions"]:
        par = min(doc["versions"], key=lambda v: _distance(v["code_cards"], cc))   # first of the fewest changes
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
    par = min(doc["versions"], key=lambda v: _distance(v["code_cards"], cc)) if doc["versions"] else None
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


def _env(kind, source, commit, by, at=None):
    return {"kind": kind, "at": at or now(), "by": by, "source": source, "commit": commit}


def add_played(doc, root, packet_rel, by, commit_check=True, binding="filmed deck code", version=None, at=None):
    """One game seen in a review packet, bound to a version by the filmed deck code (or by the weaker bindings)."""
    if binding not in BINDINGS:
        raise Refused("binding must be one of %s" % ", ".join(BINDINGS))
    pdir = os.path.join(root, packet_rel)
    source = packet_rel.rstrip("/") + "/QR_DECODE.json"
    commit = committed(root, source) if commit_check else "unchecked"
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
    outcome = None
    try:
        with open(os.path.join(pdir, "SUMMARY.json"), encoding="utf-8-sig") as fh:
            s = json.load(fh).get("result")
        outcome = s if s in ("win", "loss", "draw") else None
    except (OSError, ValueError):
        pass
    r = _env("played", source, commit, by, at)
    r.update({"video": video, "packet": packet_rel.rstrip("/"), "binding": binding, "result": outcome,
              "note": "a game seen in a review packet; not a ladder game unless the Ladder Log has it"})
    return _append(doc, version, r)


def _deck_info(v, root, git, main_ref):
    if not v.get("file"):
        raise Refused("version %s has no deck file on main: a bot number can only be filed under a list a bot "
                      "could have played from a committed deck file" % v["id"])
    with open(os.path.join(root, v["file"]), "rb") as fh:
        raw = fh.read()
    cl = mp.card_list_sha256(raw.decode("utf-8"))
    if cl[:12] != v["id"]:
        raise Refused("%s is not version %s any more" % (v["file"], v["id"]))
    versions = git.file_versions(v["file"])
    on_main = git.file_versions(v["file"], ref=main_ref) if main_ref else versions
    if not any(x["card_list_sha256"] == cl for x in on_main or []):
        raise Refused("%s as it is now is not committed on %s" % (v["file"], main_ref))
    return {"name": os.path.splitext(os.path.basename(v["file"]))[0], "file": v["file"], "version_id": cl[:12],
            "card_list_sha256": cl, "file_sha256": mp.sha256_bytes(raw), "file_versions": versions}


def add_bot(doc, root, vid, source_rel, by, at=None):
    """Bot results from a slow report, exam, replay (folder) or floor (page), built by make_predictions' own
    functions; refused unless the run tested this version's file (or a committed copy with the same card list)."""
    v = find(doc, vid)
    git = mp.Git(root)
    main_ref = _main_ref(git)
    deck = _deck_info(v, root, git, main_ref)
    abs_ = os.path.join(root, source_rel)
    if os.path.isdir(abs_) and not os.path.exists(os.path.join(abs_, "manifest.json")):
        source_rel = source_rel.rstrip("/") + "/" + deck["name"] + ".md"      # a floor folder: this deck's page
        abs_ = os.path.join(root, source_rel)
    commit = committed(root, source_rel)
    try:
        if os.path.isdir(abs_):
            bots = mp.harness_bots(abs_, source_rel.rstrip("/"), deck, git, main_ref)
        else:
            bots = [mp.floor_bot(abs_, source_rel, deck, git, main_ref, root)]
    except SystemExit as e:
        raise Refused(str(e))
    out = []
    for b in bots:
        r = _env("bot", source_rel.rstrip("/"), commit, by, at)
        r.update({"bot": b["id"], "label": b["label"], "run_kind": b["kind"], "arm": b["arm"], "pilot": b["pilot"],
                  "engine": {"label": b["engine"]["label"], "key": b["engine"].get("key")},
                  "current_engine": bool(b["in_bot_comparison"]), "counts": b["counts"],
                  "n": b["n"], "wins": b["wins"], "ties": b["ties"], "losses": b["losses"],
                  "number_pct": b["number_pct"], "ci95_wilson": b["ci95_wilson"], "games_sha256": b["games_sha256"],
                  "tested": b["source"].get("tested_version") or b["source"].get("deck_check", {}).get("how"),
                  "note": b.get("comparison_note")})
        out.append(_append(doc, vid, r))
    return out


def add_setup(doc, root, vid, run_rel, tester_rel, seeds, deals, clock, measures, by, paired=None, at=None):
    """A setup tester run. measures: {name: {"label", "x", "n"}}; the Wilson range is computed here."""
    commit = committed(root, run_rel)
    committed(root, tester_rel)
    ms = {}
    for k, m in sorted(measures.items()):
        if not (isinstance(m.get("x"), (int, float)) and isinstance(m.get("n"), int) and 0 <= m["x"] <= m["n"] > 0):
            raise Refused("measure %s needs x and n with 0 <= x <= n" % k)
        ms[k] = {"label": m.get("label", k), "x": m["x"], "n": m["n"], "pct": mp.r1(100.0 * m["x"] / m["n"]),
                 "wilson": mp.wilson(m["x"], m["n"]), "clock": m.get("clock")}
    r = _env("setup", run_rel.rstrip("/"), commit, by, at)
    r.update({"tester_sha256": mp.sha256_file(os.path.join(root, tester_rel)), "seeds": seeds, "deals": deals,
              "clock": clock, "measures": ms, "paired_vs_parent": paired})
    return _append(doc, vid, r)


def add_note(doc, root, vid, text, source, by, at=None):
    commit = committed(root, source)
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


def _vdate(video):
    m = re.match(r"(\d{4})(\d\d)(\d\d)_", video or "")
    return (int(m[2]), int(m[3])) if m else None


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


def _block(doc, group, label, played_by_group):
    root = group[0]
    ids = [v["id"] for v in group]
    results = [r for v in group for r in v["results"]]
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
        dates = [x for x in (_vdate(r["video"]) for r in played) if x]
        bind = sorted({r["binding"] for r in played})
        how = "from the deck code on video" if bind == ["filmed deck code"] else "binding: " + ", ".join(bind)
        head_ += "  (in %d of your games%s, %s)" % (len(played), ", " + _span(dates) if dates else "", how)
    L.append(head_)
    if len(group) > 1:
        L.append("  Also written with other printings of the same cards (plays the same): " + ", ".join(ids[1:]) + ".")
    if root["parent"] is None:
        L.append("  First version recorded.")
    else:
        par = find(doc, root["parent"])
        pname = ("the deck-%s file" % re.match(r"(\d+)-", par["file"].split("/")[-1])[1]) \
            if par.get("file") and re.match(r"(\d+)-", par["file"].split("/")[-1]) else par["id"]
        d = _plain_diff(root["diff"])
        L.append("  Changed from %s: %s." % (pname, d if d else "no card changes (printings only)"))
    rz = root["reason"]
    L.append("  Why: %s." % rz["text"] if rz["text"] == "not stated" else "  Why: %s (%s)." % (rz["text"], rz["by"]))
    setups = [r for r in results if r["kind"] == "setup"]
    if setups:
        s = setups[-1]
        for i, (k, m) in enumerate(sorted(s["measures"].items())):
            lead = "  Setup odds (%d deals, seeds %s; %s): " % (s["deals"], s["seeds"], s["clock"]) if i == 0 else "    "
            clock = (", clock: %s" % m["clock"]) if m.get("clock") else ""
            L.append("%s%s: %s (%s-%s)%s." % (lead, m["label"], _pct(m["pct"]), m["wilson"][0], m["wilson"][1], clock))
    else:
        L.append("  Setup odds: not computed yet.")
    bots = [r for r in results if r["kind"] == "bot"]
    cur = [r for r in bots if r["current_engine"]]
    old = [r for r in bots if not r["current_engine"]]
    items = []
    for r in cur:
        who = (" [on %s]" % r["source"].split("/")[-1]) if False else ""
        items.append("%s: %s (%s-%s range), %d games%s" % (r["label"], _pct(r["number_pct"]), r["ci95_wilson"][0],
                                                          r["ci95_wilson"][1], r["n"], who))
    if old:
        lo, hi = min(r["number_pct"] for r in old), max(r["number_pct"] for r in old)
        items.append("older engine, kept for the record and not compared: %d results from %d runs, %s to %s, %d games"
                     % (len(old), len({r["source"] for r in old}), _pct(lo), _pct(hi), sum(r["n"] for r in old)))
    if len(group) > 1 and items:
        items = ["(played on %s) %s" % (", ".join(sorted({v["id"] for v in group for r in v["results"] if r in bots})), x)
                 for x in items]
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
        L.append("  Note: %s" % n["text"])
    return "\n".join(L)


def render(doc):
    """The plain-words view: newest version first; the same input always gives the same text."""
    groups = _groups(doc)
    played_dates = []
    for i, g in enumerate(groups):
        ds = [x for x in (_vdate(r["video"]) for v in g for r in v["results"] if r["kind"] == "played") if x]
        played_dates.append(max(ds) if ds else None)
    now_i = max((i for i, d in enumerate(played_dates) if d), key=lambda i: (played_dates[i], i), default=None)
    out = ["%s: %d list%s recorded" % (doc["title"], len(groups), "" if len(groups) == 1 else "s")]
    for i in reversed(range(len(groups))):
        if now_i is not None:
            label = "NOW PLAYING" if i == now_i else ("OLDER" if i < now_i else "LISTED")
        else:
            label = "NEWEST" if i == len(groups) - 1 else "OLDER"
        out.append(_block(doc, groups[i], label, played_dates))
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
        s.add_argument("--ref", default="main")
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
            s.add_argument("--tester")
            s.add_argument("--measures")
            s.add_argument("--seeds")
            s.add_argument("--deals", type=int)
            s.add_argument("--clock")
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
                        parent=a.parent, reason=(a.reason, a.reason_by or a.by, a.reason_source), by=a.by)
        print("added version %s" % e["id"])
    else:
        _add_result(doc, a)
    save(p, doc, ROOT, ref=a.ref)
    _write_view(doc, p)
    return 0


def _add_result(doc, a):
    k = a.kind
    if k == "played":
        r = add_played(doc, ROOT, a.packet, a.by, binding=a.binding, version=a.version)
        print("filed a played game under %s" % [v["id"] for v in doc["versions"] if r in v["results"]][0])
    elif k == "bot":
        print("filed %d bot result(s)" % len(add_bot(doc, ROOT, a.version, a.source, a.by)))
    elif k == "setup":
        with open(a.measures, encoding="utf-8") as fh:
            blob = json.load(fh)
        add_setup(doc, ROOT, a.version, a.run, a.tester, a.seeds, a.deals, a.clock, blob.get("measures", blob), a.by,
                  paired=blob.get("paired"))
        print("filed a setup result")
    elif k == "note":
        add_note(doc, ROOT, a.version, a.text, a.source, a.by)
        print("filed a note")
    else:
        docs = rl.load_export(a.export)
        git = mp.Git(ROOT)
        ref = _main_ref(git)
        notes = rl.load_versions(a.versions, git, ROOT, ref)[0] if a.versions else {}
        src = os.path.relpath(os.path.abspath(a.export), ROOT).replace(os.sep, "/")
        commit = committed(ROOT, src)
        if k == "ladder-notes":
            add = ladder_from_notes(doc, a.version, docs, notes, src, a.by, commit)
        else:
            lines, result, _ = rl.read(a.export, a.predictions, (notes, [], a.versions or "no version notes"), git, ROOT,
                                       ref, counting=True)
            add = ladder_from_reading(doc, a.version, result, src, a.by, commit)
        print("filed a ladder result: test %s, feedback %s" % (add["test"], add["feedback"]))


if __name__ == "__main__":
    sys.exit(main())
