#!/usr/bin/env python3
"""make_predictions.py: save the bots' numbers for one deck version before his ladder games are read.

Ladder validation (rl/results/ladder_validation/SPEC.md, details in DETAILS.md). Writes <out-dir>/<deck>@<id>.json
and never overwrites it. <id> is the version: the first 12 hex digits of the card-list hash, the sha256 of the deck's
normalised card list (Energy types, then each card's count, name, set and number, sorted). Comments, spacing, line
endings and line order are not part of it; the raw file sha256 is kept beside it.

When: as soon as a deck version gets a slow report or goes on the ladder sheet. The laptop then commits the file on
main itself (by path), never through a merge or fast-forward. read_ladder.py counts a game as a test of this file
only if its video started at least 10 minutes after the file reached main.

Inputs, all read only:
  --deck         the deck file (its card list must be committed on main).
  --log-doc      the Ladder Log section its games are logged under (d12, brew-07, ...); repeatable.
  --log-label    optional: how the notes name this deck when several deck files share a section ("Deck 13-A").
  --slow-report  a slow report folder (manifest.json + games.jsonl): arm X (the frozen kx3) and arm ref (km3, same deals).
  --exam         an exam folder in the same format (Oct 5 exam: frozen kx3 + km3; reg_m64 / reg_m32: m64 / m32 + km3).
  --floor        a floor page (.md, beside its _games.jsonl): km3 v km3, 240 games per list, wins only.
  --export       the Ladder Log export at writing (as read_ladder.py reads it): the game ids already logged are saved,
                 and the reader treats those games as feedback whatever the clocks say.
  --newest-video the newest video name in the Battle Logs folder at writing (same purpose).
Every committed slow report and exam that tested this card list must be given (with git the script checks main and
refuses otherwise); floor pages do not record their card list, so the writer gives every floor page of this version.
The forecast's shape is the newest current-engine floor, else the newest older-engine floor (flagged).

A number added later for the same version (m64 on request, say) goes in <deck>@<id>+<tag>.json (--addendum TAG):
new bots only (refused if it restates a bot of the base file), scored with the base file's floor shape.

Run on main by the laptop (deck 12; the staged command lines are in DETAILS.md), then commit the file on main:
  python3 rl/results/ladder_validation/make_predictions.py --deck decks/dustin/12-ariados-whimsicott-ogerpon.txt \\
    --log-doc d12 --slow-report ... --exam ... --floor ... --export <Ladder Log export> \\
    --first-game 2026-10-14T14:25:46Z --games-already-read 10 --note "..."

Self-test on deck 12's real files (writes only to a temporary folder; nothing in the repository):
  python3 make_predictions.py --selftest [--repo PATH] [--no-git]
Standard library only.
"""
import argparse
import collections
import contextlib
import datetime
import decimal
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
import unicodedata

SCHEMA = "ladder-predictions v3"
PANEL = ["t-altaria", "t-blaziken", "t-hydreigon", "t-lucario", "t-sceptile", "t-suicune", "t-vespiquen", "t-weezing"]
BAND_GAMES = (10, 20, 40)
DEFAULT_OUT = "rl/results/ladder_validation/predictions"
HERE = os.path.dirname(os.path.abspath(__file__))

# The engine pinned now. Update at the next engine pin; numbers from older engines are kept, flagged, and left out
# of the bot comparison. Each bot also records its engine key, so a reading made after the next pin can tell them apart.
CURRENT_ENGINE = {
    "label": "main-4d48844 (Growl-to-0, the hit back as attack damage, upstream fixes; pinned @@PIN_DATE_SHORT@@)",
    "harness_engine_trees": ["64de03e2c3c2"],          # slow reports / exams: "engine tree <12 hex>" in manifest.json (kx3 on main-4d48844)
    "floor_engines": ["rl/engine-2026-10-21/deckgym"],  # floor pages: "- Engine: <path>"
}
# The Oct 12 pin's value. Deck 12's self-test reads files written under it, so it runs with this one.
CURRENT_ENGINE_OCT12 = {
    "label": "rules switch 2 (main-c045ede, pinned Oct 12)",
    "harness_engine_trees": ["4ebb30a94173"],
    "floor_engines": ["rl/engine-2026-10-12/deckgym"],
}

WHO_PLAYS_THE_PANEL = ("km3 plays the 8 panel lists in every run (slow reports, exams and floors). The frozen kx3 "
                       "(and m64 or m32, slower kx3 settings) knows the 8 lists and expects one of them, so its number "
                       "is the optimistic end; km3 on the deck v km3 on the panel is the like-for-like number. The "
                       "Ladder Log's opponent field says nothing about the opponent's skill or rank.")

# ---------------------------------------------------------------- opponent matching, rule v1
# Saved in every predictions file; read_ladder.py applies the saved copy. Order matters: the first list that fits wins.
MATCH_RULE = {
    "version": "v1 (2026-10-14)",
    "how": [
        "Clean the text: lower case; curly quotes straightened; hyphens and dashes to spaces; spaces collapsed; "
        "'m <name>' read as 'mega <name>' for the Pokemon whose Mega this rule names (altaria, blaziken, lucario, "
        "sceptile, charizard, sharpedo, rayquaza, absol).",
        "A game goes on a list when the text names one of the list's 'names' alternatives (every phrase of it, as "
        "whole words) and none of its 'unless' words; the first list in order wins.",
        "'exact' when every Pokemon the text names is in that list (from the list's file); 'variant' when anything "
        "else is named. Words in parentheses, after a ';', and the words in 'filler' are ignored for this.",
        "A guess word ('likely', 'maybe', 'probably', 'possibly', '?') makes the game 'inferred': its record is "
        "shown apart and it is never scored.",
        "Lists marked readout_only have no bot number: their games count with the off-panel games.",
        "Everything else is 'unmatched' (off the panel, no prediction). A concession before the opponent's attacker "
        "showed is unmatched by construction; the game still counts in every record (see the reading rule on the "
        "bias this causes).",
    ],
    "guess_words": ["likely", "maybe", "probably", "possibly", "?"],
    "filler": ["ex", "mega", "tr", "team", "rocket", "rocket's", "and", "with", "or", "deck", "list", "core", "build",
               "line", "pile"],
    "lists": [
        {"list": "t-altaria", "names": [["mega altaria"]], "unless": [],
         "pokemon": ["Swablu", "Mega Altaria ex", "Eevee", "Espeon", "Darkrai", "Igglybuff"]},
        {"list": "t-blaziken", "names": [["mega blaziken"]], "unless": [],
         "pokemon": ["Torchic", "Mega Blaziken ex", "Heatmor", "Castform Sunny Form"]},
        {"list": "t-hydreigon", "names": [["hydreigon"]], "unless": [],
         "pokemon": ["Deino", "Hydreigon", "Bombirdier", "Mega Absol ex"]},
        {"list": "t-lucario", "names": [["mega lucario"]], "unless": ["raticate"],
         "pokemon": ["Riolu", "Mega Lucario ex", "Lucario", "Bonsly", "Hitmonlee"]},
        {"list": "t-sceptile", "names": [["mega sceptile"]], "unless": [],
         "pokemon": ["Caterpie", "Metapod", "Butterfree", "Treecko", "Grovyle", "Mega Sceptile ex"]},
        {"list": "t-suicune", "names": [["suicune ex"], ["suicune", "baxcalibur"]], "unless": [],
         "pokemon": ["Frigibax", "Baxcalibur", "Suicune ex", "Chien-Pao ex"]},
        {"list": "t-vespiquen", "names": [["vespiquen"]], "unless": [],
         "pokemon": ["Combee", "Vespiquen ex", "Shuckle ex", "Teal Mask Ogerpon ex"]},
        {"list": "t-weezing", "names": [["weezing ex"]], "unless": ["magmar"],
         "pokemon": ["Hoopa ex", "Team Rocket's Koffing", "Team Rocket's Weezing ex", "Darkrai ex"]},
        {"list": "h-charizardy_entei", "names": [["mega charizard y"]], "unless": [], "readout_only": True,
         "pokemon": ["Charmander", "Charmeleon", "Mega Charizard Y ex", "Entei ex"]},
        {"list": "l-sharpedo", "names": [["mega sharpedo"]], "unless": [], "readout_only": True,
         "pokemon": ["Carvanha", "Mega Sharpedo ex", "Magikarp", "Gyarados", "Mantyke", "Chien-Pao ex"]},
        {"list": "g-dragonair_mega_rayquaza", "names": [["mega rayquaza"]], "unless": [], "readout_only": True,
         "pokemon": ["Dratini", "Gouging Fire", "Dragonair", "Mega Rayquaza ex"]},
    ],
    "list_files": {
        "t-altaria": "decks/screen/opponents/t-altaria.txt", "t-blaziken": "decks/screen/opponents/t-blaziken.txt",
        "t-hydreigon": "decks/screen/opponents/t-hydreigon.txt", "t-lucario": "decks/screen/opponents/t-lucario.txt",
        "t-sceptile": "decks/screen/opponents/t-sceptile.txt", "t-suicune": "decks/screen/opponents/t-suicune.txt",
        "t-vespiquen": "decks/screen/opponents/t-vespiquen.txt", "t-weezing": "decks/screen/opponents/t-weezing.txt",
        "h-charizardy_entei": "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt",
        "l-sharpedo": "decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt",
        "g-dragonair_mega_rayquaza": "decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt",
    },
}

FORECAST_RULE = {
    "version": "calibrated-v1",
    "matched": "f_k = expit(logit(floor_k) + c): the km3 floor's shape across the 8 lists (240 games a list), shifted "
               "by one logit constant c, solved by bisection, so that the equal-weight mean of the 8 forecasts equals "
               "the bot's own number. The raw per-list cells (6-20 games a list) are saved, not used: mostly noise.",
    "shape": "the newest current-engine floor given; if there is none, the newest older-engine floor, flagged. An "
             "addendum uses its base file's shape.",
    "unmatched": "no matchup forecast; the game is in the off-panel record. The level check uses the bot's number "
                 "for every game, labelled with its assumption (off-panel opponents are like the panel on average).",
    "inferred": "not scored: the list was guessed.",
}

READING_RULE_VERSION = "r2 (2026-10-15)"
TEST_MARGIN_MINUTES = 10
VERDICT_TEST_GAMES = 20
READING_RULE = [
    "Registration: this file counts from its first readable commit on main, made on main itself (by path), never "
    "merged or fast-forwarded from another branch. Its time is that commit's committer time (the committing "
    "machine's clock), or this file's own written_at if that is later, or the time main's reflog shows the commit "
    "arriving if that is later still.",
    "Test or feedback: a game is a test of this file only if its play time is known from an iOS video name (in the "
    "Ladder Log note, or recovered by an agent from the Battle Logs listing into the committed version notes), it "
    "started at least %d minutes after the registration time, it was not yet in the Ladder Log when this file was "
    "written, and its video is newer than the newest video that existed then. A game with no video name is 'time "
    "unknown' and a game whose video starts after its log time is 'time doubtful': both are feedback. Every other "
    "game is feedback." % TEST_MARGIN_MINUTES,
    "Ties: a game is read with the version in the deck file on main when it was played ('assumed'), or with the "
    "version an agent's committed version note gives ('confirmed', citing the evidence path). If several deck files "
    "share a Ladder Log section, the file's log_label in the note decides, else the game is not read (ambiguous). "
    "Before each reading an agent compares his side's cards in each test game's review packet with the card list and "
    "notes 'checked' or 'mismatch: <card>'; mismatched games are not read, and the reading gives the record on checked "
    "games beside the record on all games. His notes help but are never required.",
    "Each reading leads with the matched games (wins v expected wins, the chance in words), then the off-panel record "
    "with no prediction, then the level check labelled with its assumption. Exact and variant matches are shown apart.",
    "A win by the opponent's concession is a full win in every record and check. Early concessions often hide the "
    "attacker, so they land off the panel: the matched games are short of wins and the matched check leans against "
    "the bot. Each reading counts those wins and repeats the matched check with 1 in 4 of them counted as panel wins.",
    "Only the bots on the engine pinned when this file was written are compared. The running tally keeps one forecast "
    "per game and per bot and engine (the earliest registered): wins minus expected wins on matched test games. It "
    "says nothing about screening or ranking decks.",
    "Verdict: the first reading with %d test games of this version is its verdict; if the season ends or the version "
    "is retired first, the reading then is. Every other reading is interim." % VERDICT_TEST_GAMES,
]


def _norm_text(s):
    t = unicodedata.normalize("NFKC", s if isinstance(s, str) else ("" if s is None else str(s))).casefold()
    for a, b in (("’", "'"), ("‘", "'"), ("`", "'"), ("“", '"'), ("”", '"')):
        t = t.replace(a, b)
    t = re.sub(r"[-‐‑‒–—−]", " ", t)
    return " ".join(t.split())


def _mega_stems(rule):
    stems = set()
    for row in rule["lists"]:
        for alt in row["names"]:
            for ph in alt:
                m = re.match(r"mega (\w+)", ph)
                if m:
                    stems.add(m.group(1))
        for p in row["pokemon"]:
            m = re.match(r"mega (\w+)", _norm_text(p))
            if m:
                stems.add(m.group(1))
    return sorted(stems)


def normalise_opponent(text, rule=None):
    rule = rule or MATCH_RULE
    t = _norm_text(text)
    stems = _mega_stems(rule)
    if stems:
        t = re.sub(r"(?<![\w'])m\.? (%s)\b" % "|".join(stems), r"mega \1", t)
    return t


def _words(t):
    return " " + " ".join(re.findall(r"[\w']+", t)) + " "


def _has(phrase, words):
    return (" " + _norm_text(phrase) + " ") in words


def _forms(name):
    f = _norm_text(name)
    out = {f}
    for g in list(out):
        if g.endswith(" ex"):
            out.add(g[:-3])
    for g in list(out):
        if g.startswith("team rocket's "):
            out.add(g[len("team rocket's "):])
    return out


def match_opponent(text, rule=None):
    """The Ladder Log's opponent text -> {list, status, fit, extra, normalised}.
    status: panel / readout / inferred / ruled out / unmatched; fit: exact / variant (matched lists only)."""
    rule = rule or MATCH_RULE
    t = normalise_opponent(text, rule)
    words = _words(t)
    guess = any((g in t) if not g.isalnum() else _has(g, words) for g in rule["guess_words"])
    for row in rule["lists"]:
        alt = next((a for a in row["names"] if all(_has(ph, words) for ph in a)), None)
        if alt is None:
            continue
        bad = [u for u in row["unless"] if _has(u, words)]
        if bad:
            return {"list": None, "status": "ruled out", "fit": None, "why": "%s with '%s'" % (row["list"], bad[0]),
                    "normalised": t}
        main = re.sub(r"\([^)]*\)", " ", t).split(";")[0]
        rest = _words(main)
        phrases = [_norm_text(p) for p in alt] + sorted({f for p in row["pokemon"] for f in _forms(p)}, key=len,
                                                         reverse=True)
        for ph in phrases:
            while (" " + ph + " ") in rest:
                rest = rest.replace(" " + ph + " ", " ")
        ignore = set(rule["filler"]) | {g for g in rule["guess_words"] if g.isalnum()}
        extra = [w for w in rest.split() if w not in ignore and not w.isdigit()]
        fit = "variant" if extra else "exact"
        status = "inferred" if guess else ("readout" if row.get("readout_only") else "panel")
        return {"list": row["list"], "status": status, "fit": fit, "extra": extra, "normalised": t}
    return {"list": None, "status": "unmatched", "fit": None, "normalised": t}


# ---------------------------------------------------------------- deck versions
def card_list(text):
    """A deck file's normalised card list: Energy types, then '<count> <name> <set> <number>' lines, sorted.
    Comments ('#' or '//'), blank lines, spacing, line endings, line order and leading zeros are ignored."""
    energy, cards = set(), collections.Counter()
    for raw in text.replace("﻿", "").splitlines():
        line = re.split(r"(?:^|\s)(?:#|//)", unicodedata.normalize("NFC", raw), maxsplit=1)[0]
        line = " ".join(line.split())
        if not line:
            continue
        if line.lower().startswith("energy:"):
            energy |= {e.strip().casefold() for e in re.split(r"[,/]", line.split(":", 1)[1]) if e.strip()}
            continue
        m = re.fullmatch(r"(\d+) (.+?) (\S+) (\S+)", line)
        if not m:
            raise ValueError("cannot read deck line %r" % raw)
        cards[(m.group(2).casefold(), m.group(3).upper(), m.group(4).lstrip("0") or "0")] += int(m.group(1))
    lines = ["energy: " + ", ".join(sorted(energy))]
    lines += ["%d %s %s %s" % (n, name, st, num) for (name, st, num), n in sorted(cards.items())]
    return lines


def card_list_sha256(text):
    return sha256_bytes(("\n".join(card_list(text)) + "\n").encode("utf-8"))


def card_list_sha256_or_none(data):
    try:
        return card_list_sha256(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, AttributeError):
        return None


# ---------------------------------------------------------------- maths
def wilson(x, n, z=1.959964):
    if n == 0:
        return None
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(max(0.0, p * (1 - p) / n + z * z / (4 * n * n))) / d
    return [r1(100 * (c - h)), r1(100 * (c + h))]


def _lchoose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _lbeta(a, b):
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def predictive_pmf(m, x, n):
    """Chance of each win count in m ladder games if his ladder rate equalled the bot's x/n, the bot's own
    uncertainty included (beta-binomial, Beta(x+1/2, n-x+1/2))."""
    a, b = x + 0.5, n - x + 0.5
    return [math.exp(_lchoose(m, w) + _lbeta(w + a, m - w + b) - _lbeta(a, b)) for w in range(m + 1)]


def band_from_pmf(pm, alpha=0.05):
    m = len(pm) - 1
    cum, lo = 0.0, 0
    for w in range(m + 1):
        if cum + pm[w] > alpha / 2:
            lo = w
            break
        cum += pm[w]
    cum, hi = 0.0, m
    for w in range(m, -1, -1):
        if cum + pm[w] > alpha / 2:
            hi = w
            break
        cum += pm[w]
    return [lo, hi]


def predictive_band(m, x, n, alpha=0.05):
    """Wins in m ladder games, 95% range, if his ladder rate equalled the bot's x/n."""
    return band_from_pmf(predictive_pmf(m, x, n), alpha)


def poisson_binomial(ps):
    d = [1.0]
    for p in ps:
        nd = [0.0] * (len(d) + 1)
        for k, v in enumerate(d):
            nd[k] += v * (1 - p)
            nd[k + 1] += v * p
        d = nd
    return d


def logit(p):
    return math.log(p / (1 - p))


def expit(v):
    return 1 / (1 + math.exp(-v))


def r1(v):
    """One decimal, halves rounded up as the report pages do (61.25 -> 61.3)."""
    if v is None:
        return None
    return float(decimal.Decimal(repr(v)).quantize(decimal.Decimal("0.1"), rounding=decimal.ROUND_HALF_UP))


def calibrate_shift(shape, level):
    """c such that the mean over lists of expit(logit(shape_k) + c) equals level (bisection; the mean rises with c)."""
    lo, hi = -30.0, 30.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if sum(expit(logit(s) + mid) for s in shape) / len(shape) < level:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------- files, times and git
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def utc(stamp):
    d = datetime.datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
    return d.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_strict(stamp, what):
    """An ISO time that must carry 'Z' or an explicit offset (a bare time would be read in the machine's zone)."""
    try:
        d = datetime.datetime.fromisoformat(stamp.strip().replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise SystemExit("%s: cannot read the time %r (use e.g. 2026-10-14T14:25:46Z)" % (what, stamp))
    if d.tzinfo is None:
        raise SystemExit("%s: %r has no time zone; add 'Z' for UTC or an offset like -05:00" % (what, stamp))
    return d.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def code_sha256():
    """sha256 of this script and of read_ladder.py beside it (None if absent): saved in every file, checked at reading."""
    out = {}
    for f in ("make_predictions.py", "read_ladder.py"):
        p = os.path.join(HERE, f)
        out[f] = sha256_file(p) if os.path.exists(p) else None
    return out


def find_repo(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, "decks")) and os.path.isdir(os.path.join(d, "rl", "results")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


class Git:
    """Read-only git: rev-parse, hash-object (no -w), log, show, cat-file, ls-tree, reflog, merge-base --is-ancestor."""

    def __init__(self, repo, enabled=True):
        self.repo = repo
        self.ok = False
        self._memo = {}
        self._anc = {}
        if enabled:
            try:
                self.run("rev-parse", "--git-dir")
                self.ok = True
            except Exception:
                self.ok = False

    def run(self, *args, binary=False):
        key = (args, binary)
        if key not in self._memo:   # memoised: one Git object never sees the repository change
            r = subprocess.run(["git", "-c", "safe.directory=*", "-C", self.repo] + list(args), capture_output=True)
            if r.returncode != 0:
                raise RuntimeError("git %s: %s" % (" ".join(args[:2]), r.stderr.decode("utf-8", "replace").strip()[:300]))
            self._memo[key] = r.stdout if binary else r.stdout.decode("utf-8", "replace")
        return self._memo[key]

    def verify_ref(self, ref):
        try:
            self.run("rev-parse", "--verify", "--quiet", ref + "^{commit}")
            return True
        except RuntimeError:
            return False

    def history(self, rel, ref="--all", first_parent=False):
        """[(commit, date_utc, new_blob)] for every commit that changed the path, newest first. With first_parent,
        a merge counts as changing the path when it differs from its first parent (--diff-merges=first-parent)."""
        args = ["log", ref] + (["--first-parent", "--diff-merges=first-parent"] if first_parent else []) + \
               ["--no-renames", "--raw", "--no-abbrev", "--format=C %H %cI", "--", rel]
        out = self.run(*args)
        res, cur = [], None
        for line in out.splitlines():
            if line.startswith("C "):
                _, h, d = line.split(" ", 2)
                cur = (h, utc(d))
            elif line.startswith(":") and cur is not None:
                fields = line.split("\t")[0].split()
                if len(fields) >= 4:
                    res.append((cur[0], cur[1], fields[3]))
        return res

    def content_commits(self, rel):
        """[(date_utc, commit)], oldest first, of every commit on any branch that wrote the path's present content."""
        if not self.ok:
            return []
        try:
            blob = self.run("hash-object", "--", rel).strip()
            return sorted((d, h) for h, d, nb in self.history(rel) if nb == blob)
        except RuntimeError:
            return []

    def is_ancestor(self, commit, ref):
        key = (commit, ref)
        if key not in self._anc:
            r = subprocess.run(["git", "-c", "safe.directory=*", "-C", self.repo, "merge-base", "--is-ancestor", commit, ref],
                               capture_output=True)
            self._anc[key] = r.returncode == 0
        return self._anc[key]

    def first_commit_of_content(self, rel, ref=None):
        """Earliest commit whose version of the path equals the file as it is now: on any branch, or (with `ref`)
        the earliest such commit that is in ref's history."""
        for d, h in self.content_commits(rel):
            if ref is None or self.is_ancestor(h, ref):
                return {"commit": h, "date": d}
        return None

    def show_bytes(self, commit, rel):
        try:
            return self.run("show", "%s:%s" % (commit, rel), binary=True)
        except RuntimeError:
            return None

    def blob_bytes(self, blob):
        return self.run("cat-file", "blob", blob, binary=True)

    def sha256_at(self, commit, rel):
        b = self.show_bytes(commit, rel)
        return None if b is None else sha256_bytes(b)

    def file_versions(self, rel, ref="--all"):
        """Every version the path has had (on any branch, or in ref's history): raw sha256, card-list sha256, first commit."""
        if not self.ok:
            return None
        seen = {}
        for h, d, nb in self.history(rel, ref=ref):
            if set(nb) == {"0"}:
                continue
            data = self.blob_bytes(nb)
            sha = sha256_bytes(data)
            if sha not in seen or d < seen[sha]["first_date"]:
                seen[sha] = {"sha256": sha, "card_list_sha256": card_list_sha256_or_none(data),
                             "first_commit": h, "first_date": d}
        return sorted(seen.values(), key=lambda v: v["first_date"])

    def head(self):
        try:
            return self.run("rev-parse", "HEAD").strip() if self.ok else None
        except RuntimeError:
            return None

    def reflog_arrival(self, ref, commit):
        """When the commit first became part of ref, by this clone's reflog: (time_utc or None, how)."""
        try:
            out = self.run("reflog", "show", "--date=unix", "--format=%H %gd", ref, "--")
        except RuntimeError:
            return None, "no reflog for %s in this clone" % ref
        entries = []
        for line in out.splitlines():
            m = re.match(r"([0-9a-f]{40}) \S*@\{(\d+)\}", line.strip())
            if m:
                entries.append((m.group(1), int(m.group(2))))
        entries.reverse()   # oldest first
        if not entries:
            return None, "no reflog for %s in this clone" % ref
        if self.is_ancestor(commit, entries[0][0]):
            return None, "this clone's reflog of %s begins after the commit (not checked)" % ref
        lo, hi = 0, len(entries) - 1
        if not self.is_ancestor(commit, entries[hi][0]):
            return None, "not in this clone's reflog of %s" % ref
        while lo < hi:                       # first entry whose tip contains the commit
            mid = (lo + hi) // 2
            if self.is_ancestor(commit, entries[mid][0]):
                hi = mid
            else:
                lo = mid + 1
        t = datetime.datetime.fromtimestamp(entries[lo][1], datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return t, "reflog"


def commit_info(git, rel, main_ref):
    if not git.ok:
        return {"path": rel, "first_commit": None, "first_commit_on_main": None, "git": "not available"}
    return {"path": rel, "first_commit": git.first_commit_of_content(rel),
            "first_commit_on_main": git.first_commit_of_content(rel, main_ref) if main_ref else None}


def fixed_at(infos):
    """A number is fixed when the last of its files reached its present content in a commit (any branch)."""
    dates = [i["first_commit"]["date"] if i.get("first_commit") else None for i in infos]
    return None if (not dates or None in dates) else max(dates)


def same_list_shas(deck):
    """Raw sha256s of every committed copy of the deck file with this version's card list (and the file itself)."""
    return {deck["file_sha256"]} | {v["sha256"] for v in deck.get("file_versions") or []
                                    if v.get("card_list_sha256") == deck["card_list_sha256"]}


def check_tested_version(tested_sha, deck, where):
    """The source tested this version: the same file, or an earlier committed copy with the same card list."""
    if tested_sha == deck["file_sha256"]:
        return "the same file (sha256 %s)" % tested_sha[:12]
    for v in deck.get("file_versions") or []:
        if v["sha256"] == tested_sha and v.get("card_list_sha256") == deck["card_list_sha256"]:
            return "an earlier copy of the file with the same card list (sha256 %s, first committed %s)" % (
                tested_sha[:12], v["first_commit"][:8])
    hint = "" if deck.get("file_versions") is not None else " (without git the script cannot look up that file's card list)"
    raise SystemExit("%s tested %s with file sha256 %s, not this version (card list %s): refusing%s"
                     % (where, deck["name"], str(tested_sha)[:12], deck["version_id"], hint))


# ---------------------------------------------------------------- sources
def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


SCORE = {"deck": 1.0, "tie": 0.5, "opp": 0.0}
ROW_KEYS = ("list", "n", "wins", "ties", "losses", "x", "pct", "ci95")   # x = the score counted (see "counts")


def summarize(rows, ties_count_half):
    """rows: (opponent list, outcome in deck/tie/opp). Overall and per-list numbers."""
    def block(sub):
        n = len(sub)
        w = sum(1 for _, o in sub if o == "deck")
        t = sum(1 for _, o in sub if o == "tie")
        x = w + (0.5 * t if ties_count_half else 0.0)
        return {"n": n, "wins": w, "ties": t, "losses": n - w - t, "x": x,
                "pct": r1(100.0 * x / n) if n else None, "ci95": wilson(x, n)}

    extra = sorted({k for k, _ in rows} - set(PANEL))
    if extra:
        raise SystemExit("source has opponents outside the panel: %s" % extra)
    overall = block(rows)
    per = []
    for k in PANEL:
        b = block([r for r in rows if r[0] == k])
        b["list"] = k
        per.append(b)
    return overall, per


def short_pilot(pilot):
    m = re.search(r"_m(\d+)$", pilot or "")
    return "m%s" % m.group(1) if m else pilot


def knows_panel(short):
    return bool(short) and (short == "kx3" or bool(re.fullmatch(r"m\d+", short)))   # kx3 and its slower settings


def bot_label(kind, arm, short, current, src):
    who = "frozen kx3" if short == "kx3" else short
    eng = "current engine" if current else "older engine"
    if kind == "floor":
        return "%s floor" % short if current else "%s floor (older engine)" % short
    if kind == "slow_report":
        return ("%s (slow report, %s)" % (who, eng)) if arm == "X" else \
               ("%s (slow report same deals)" % who if current else "%s (slow report same deals, older engine)" % who)
    return ("%s (exam %s, %s)" % (who, src, eng)) if arm == "X" else ("%s (exam %s same deals, %s)" % (who, src, eng))


def engine_short(key):
    if not key:
        return "unknown"
    if re.fullmatch(r"[0-9a-f]{12}", key):
        return key[:8]
    parts = [p for p in key.replace("\\", "/").split("/") if p and p not in ("deckgym", "release", "target")]
    return parts[-1] if parts else key


def bot_id(role, engine_key, current):
    return role if current else "%s@%s" % (role, engine_short(engine_key))


def signature_sha(sig):
    return sha256_bytes(json.dumps(sig, sort_keys=True, default=str).encode("utf-8"))


def harness_bots(folder, rel_folder, deck, git, main_ref):
    man_path = os.path.join(folder, "manifest.json")
    games_path = os.path.join(folder, "games.jsonl")
    if not (os.path.exists(man_path) and os.path.exists(games_path)):
        raise SystemExit("%s: needs manifest.json and games.jsonl" % rel_folder)
    with open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)
    entry = [d for d in man.get("decks", []) if d.get("name") == deck["name"]]
    if not entry:
        raise SystemExit("%s: deck %s is not in this run" % (rel_folder, deck["name"]))
    tested = check_tested_version(entry[0].get("sha256"), deck, rel_folder)
    games = [g for g in load_jsonl(games_path) if g.get("deck") == deck["name"]]
    kind = "slow_report" if "slow_report" in man or "/slow_reports/" in "/" + rel_folder + "/" else "exam"
    trees = re.findall(r"engine tree (?:as archived )?([0-9a-f]{12})", man.get("engine", ""))
    tree = trees[0] if trees else None
    is_current = tree in CURRENT_ENGINE["harness_engine_trees"]
    files = [commit_info(git, rel_folder + "/games.jsonl", main_ref), commit_info(git, rel_folder + "/manifest.json", main_ref)]
    src = os.path.basename(rel_folder.rstrip("/"))
    out = []
    for arm, pilot in (("X", man.get("pilot")), ("ref", man.get("reference"))):
        gs = [g for g in games if g.get("arm") == arm]
        if not gs:
            continue
        bad = {g.get("winner") for g in gs} - set(SCORE)
        if bad:
            raise SystemExit("%s: unknown winner values %s" % (rel_folder, bad))
        overall, per = summarize([(g["opp"], g["winner"]) for g in gs], ties_count_half=True)
        short = short_pilot(pilot)
        tag = "slow" if kind == "slow_report" else "exam"
        role = ("%s_%s" % (short, tag)) if arm == "X" else ("%s_%s_same_deals" % (short, tag))
        sig = sorted((g.get("key"), g.get("seed"), g.get("winner")) for g in gs)
        out.append({
            "id": bot_id(role, tree, is_current), "role": role,
            "label": bot_label(kind, arm, short, is_current, src), "kind": kind, "arm": arm,
            "pilot": pilot, "panel_pilot": sorted({str(g.get("pilot_opp")) for g in gs}),
            "knows_the_panel_lists": knows_panel(short),
            "counts": "win 1, tie 1/2, loss 0",
            "n": overall["n"], "wins": overall["wins"], "ties": overall["ties"], "losses": overall["losses"],
            "number_pct": overall["pct"], "ci95_wilson": overall["ci95"], "x": overall["x"],
            "per_opponent": [{k: b[k] for k in ROW_KEYS} for b in per],
            "wins_range_95_if_ladder_equalled_this": {str(m): predictive_band(m, overall["x"], overall["n"]) for m in BAND_GAMES},
            "engine": {"key": tree, "tree": tree, "current_when_written": is_current,
                       "label": CURRENT_ENGINE["label"] if is_current else "older engine (before %s)" % CURRENT_ENGINE["label"],
                       "text": man.get("engine", "").split(";")[0][:300]},
            "in_bot_comparison": is_current,
            "comparison_note": None if is_current else "older engine: kept for the record, out of the bot comparison",
            "source": {"folder": rel_folder, "manifest_name": man.get("name"), "stage": man.get("stage"),
                       "registered_at": man.get("created_at"), "repo_commit_at_registration": man.get("repo_commit"),
                       "program_sha256": man.get("program_sha256"), "manifest_file_sha256": sha256_file(man_path),
                       "deck_sha256_in_manifest": entry[0].get("sha256"), "tested_version": tested, "files": files},
            "fixed_at": fixed_at(files),
            "games_sha256": signature_sha(sig),
            "_signature": sig,
        })
    return out


def floor_bot(path, rel_path, deck, git, main_ref, repo):
    if os.path.isdir(path):
        md = os.path.join(path, deck["name"] + ".md")
    elif path.endswith("_games.jsonl"):
        md = path[: -len("_games.jsonl")] + ".md"
    else:
        md = path
    gj = md[:-3] + "_games.jsonl"
    if not (os.path.exists(md) and os.path.exists(gj)):
        raise SystemExit("%s: needs the floor page .md and its _games.jsonl" % rel_path)
    rel_md = os.path.relpath(md, repo).replace(os.sep, "/")
    rel_gj = os.path.relpath(gj, repo).replace(os.sep, "/")
    with open(md, encoding="utf-8") as fh:
        txt = fh.read()
    title = re.search(r"^# Floor check: (\S+)", txt, re.M)
    if not title or title.group(1) != deck["name"]:
        raise SystemExit("%s is not a floor page for %s" % (rel_md, deck["name"]))
    eng = re.search(r"- Engine: (\S+).*?Pilots: (\S+) on the deck, (\S+) on the panel", txt)
    engine, pilot, panel_pilot = (eng.group(1), eng.group(2), eng.group(3)) if eng else (None, None, None)
    head = re.search(r"(\d+) wins in (\d+) games", txt)
    games = load_jsonl(gj)
    rows = [(g["opponent"], "deck" if g.get("won") else ("tie" if g.get("draw") else "opp")) for g in games]
    overall, per = summarize(rows, ties_count_half=False)
    empty = [b["list"] for b in per if not b["n"]]
    if empty:
        raise SystemExit("%s: no games against %s; a floor needs all 8 lists" % (rel_md, ", ".join(empty)))
    if head and (int(head.group(1)), int(head.group(2))) != (overall["wins"], overall["n"]):
        raise SystemExit("%s: page says %s wins in %s games, its games file has %d in %d"
                         % (rel_md, head.group(1), head.group(2), overall["wins"], overall["n"]))
    files = [commit_info(git, rel_gj, main_ref), commit_info(git, rel_md, main_ref)]
    deck_check = {"how": "the deck file's card list at the commit that first holds these floor games (a floor page "
                         "does not record the card list it ran, so this check cannot tell two lists apart if the deck "
                         "file changed before the run)", "card_list_sha256": None, "matches": None}
    first = files[0].get("first_commit")
    if git.ok and first:
        data = git.show_bytes(first["commit"], deck["file"])
        cl = card_list_sha256_or_none(data) if data is not None else None
        deck_check.update(card_list_sha256=cl, file_sha256=sha256_bytes(data) if data is not None else None,
                          matches=(cl == deck["card_list_sha256"]), commit=first["commit"])
        if cl != deck["card_list_sha256"]:
            raise SystemExit("%s: the deck file at %s has card list %s, not this version %s: refusing"
                             % (rel_md, first["commit"][:8], str(cl)[:12], deck["version_id"]))
    is_current = engine in CURRENT_ENGINE["floor_engines"]
    role = "%s_floor" % (pilot or "floor")
    sig = sorted((g.get("opponent"), g.get("seed"), g.get("seat"), bool(g.get("won")), bool(g.get("draw"))) for g in games)
    return {
        "id": bot_id(role, engine, is_current), "role": role,
        "label": bot_label("floor", None, pilot or "floor", is_current, None),
        "kind": "floor", "arm": None, "pilot": pilot, "panel_pilot": [panel_pilot] if panel_pilot else [],
        "knows_the_panel_lists": knows_panel(pilot),
        "counts": "wins only (a draw is not a win), as the floor pages count",
        "n": overall["n"], "wins": overall["wins"], "ties": overall["ties"], "losses": overall["losses"],
        "number_pct": overall["pct"], "ci95_wilson": overall["ci95"], "x": overall["x"],
        "per_opponent": [{k: b[k] for k in ROW_KEYS} for b in per],
        "wins_range_95_if_ladder_equalled_this": {str(m): predictive_band(m, overall["x"], overall["n"]) for m in BAND_GAMES},
        "engine": {"key": engine, "path": engine, "current_when_written": is_current,
                   "label": CURRENT_ENGINE["label"] if is_current else "older engine (before %s)" % CURRENT_ENGINE["label"]},
        "in_bot_comparison": is_current,
        "comparison_note": None if is_current else "older engine: kept for the record, out of the bot comparison",
        "source": {"page": rel_md, "games": rel_gj, "deck_check": deck_check, "files": files},
        "fixed_at": fixed_at(files),
        "games_sha256": signature_sha(sig),
        "_signature": sig,
    }


def committed_harness_sources(git, ref, deck):
    """Folders on ref holding a manifest.json that names this deck and a games.jsonl: [(folder, this version?)]."""
    out = git.run("ls-tree", "-r", "--name-only", ref, "--", "rl/results")
    paths = set(out.splitlines())
    shas = same_list_shas(deck)
    found = []
    for m in sorted(p for p in paths if p.endswith("/manifest.json")):
        folder = m[: -len("/manifest.json")]
        if folder + "/games.jsonl" not in paths:
            continue
        try:
            man = json.loads((git.show_bytes(ref, m) or b"{}").decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        entries = [d for d in man.get("decks", []) if isinstance(d, dict) and d.get("name") == deck["name"]]
        if entries:
            found.append((folder, entries[0].get("sha256") in shas))
    return found


def floor_pages_on_ref(git, ref, deck):
    out = git.run("ls-tree", "-r", "--name-only", ref, "--", "rl/results")
    paths = set(out.splitlines())
    return sorted(p for p in paths if p.endswith("/" + deck["name"] + ".md")
                  and p[:-3] + "_games.jsonl" in paths)


# ---------------------------------------------------------------- forecasts
def _clamp(x, n):
    return min(max(x / n, 0.5 / n), 1 - 0.5 / n)


def floor_shape(fl):
    rows = fl["per_opponent"]
    if [r["list"] for r in rows] != PANEL or any(not r["n"] for r in rows):
        raise SystemExit("the floor %s does not cover all 8 lists: no forecast shape" % fl["id"])
    return [_clamp(r["x"], r["n"]) for r in rows]


def pick_shape_floor(bots):
    """The newest current-engine floor (by when its games were first committed), else the newest older one."""
    floors = [b for b in bots if b["kind"] == "floor"]
    if not floors:
        return None
    cur = [b for b in floors if b["in_bot_comparison"]] or floors
    return sorted(cur, key=lambda b: b.get("fixed_at") or "", reverse=True)[0] if any(b.get("fixed_at") for b in cur) else cur[0]


def calibrated_forecasts(bots, shape_from=None):
    """shape_from: (floor bot id, shape list, engine current?, note) from a base file, for an addendum."""
    if shape_from is None:
        fl = pick_shape_floor(bots)
        if fl is None:
            return {"rule": FORECAST_RULE, "floor_bot": None, "per_bot": {}, "note": "no floor source given: no matchup forecasts"}
        shape_from = (fl["id"], floor_shape(fl), fl["in_bot_comparison"],
                      None if fl["in_bot_comparison"] else "the only floor is on an older engine: the forecasts' shape comes from it")
    fid, shape, cur, note = shape_from
    per_bot = {}
    for b in bots:
        level = _clamp(b["x"], b["n"])
        c = calibrate_shift(shape, level)
        f = [expit(logit(s) + c) for s in shape]
        per_bot[b["id"]] = {"level": round(level, 6), "shift_logit": round(c, 6),
                            "per_list": {k: round(v, 6) for k, v in zip(PANEL, f)},
                            "per_list_pct": {k: r1(round(100 * v, 9)) for k, v in zip(PANEL, f)},
                            "mean_of_lists_pct": r1(round(100 * sum(f) / len(f), 9))}
    return {"rule": FORECAST_RULE, "floor_bot": fid, "floor_engine_current": cur, "note": note,
            "shape": [round(s, 6) for s in shape], "per_bot": per_bot}


# ---------------------------------------------------------------- build
def resolve(p, repo):
    """A source path: absolute, relative to the current folder if it exists there, else relative to the repository."""
    if os.path.isabs(p):
        return p
    return os.path.abspath(p) if os.path.exists(p) else os.path.join(repo, p)


def relative(p, repo):
    rp = os.path.relpath(os.path.abspath(p), repo).replace(os.sep, "/")
    if rp.startswith(".."):
        raise SystemExit("%s is outside the repository %s" % (p, repo))
    return rp


def out_dir_path(arg, repo):
    """--out-dir: resolved against the current folder (never the repository); inside the repository only DEFAULT_OUT."""
    default = os.path.normpath(os.path.join(repo, DEFAULT_OUT))
    if not arg:
        return default
    if os.sep == "/" and (re.match(r"^[A-Za-z]:", arg) or "\\" in arg):
        raise SystemExit("--out-dir %r looks like a Windows path; under WSL write it as /mnt/c/..." % arg)
    p = os.path.normpath(os.path.abspath(arg))
    inside = os.path.commonpath([p, os.path.normpath(repo)]) == os.path.normpath(repo)
    if inside and p != default:
        raise SystemExit("--out-dir %s is inside the repository but is not %s: refusing" % (p, DEFAULT_OUT))
    return p


def ladder_log_at_writing(export, newest_video):
    """What already existed when the file was written: the Ladder Log's game keys and the newest video start."""
    out = {"export": None, "export_sha256": None, "game_keys": None, "games_logged": None,
           "newest_logged": None, "newest_video": None, "newest_video_start": None}
    starts = []
    if export:
        sys.path.insert(0, HERE)
        import read_ladder as rl   # noqa: E402  (beside this script; it imports this module too)
        docs, info = rl.load_export(export, with_info=True)
        keys, ts = [], []
        for d, gs in sorted(docs.items()):
            for g in gs:
                if isinstance(g, dict) and g.get("id"):
                    keys.append("%s/%s" % (d, g["id"]))
                if isinstance(g, dict) and isinstance(g.get("ts"), (int, float)) and g["ts"] > 1e11:
                    ts.append(g["ts"])
                if isinstance(g, dict):
                    v = rl.video_start(str(g.get("note") or ""))
                    if v:
                        starts.append(v)
        out.update(export=os.path.basename(os.path.normpath(export)), export_sha256=info["sha256"],
                   game_keys=sorted(keys), games_logged=len(keys),
                   newest_logged=rl.iso(rl.from_ms(max(ts))) if ts else None)
    if newest_video:
        sys.path.insert(0, HERE)
        import read_ladder as rl   # noqa: E402
        v = rl.video_start(newest_video)
        if not v:
            raise SystemExit("--newest-video %r is not an iOS video name like 20261014_234728000_iOS.MP4" % newest_video)
        starts.append(v)
    if starts:
        best = max(starts)
        out.update(newest_video_start=best[0], newest_video=best[1])
    return out


def base_clash(base_bots, b):
    """Base-file bots that a new addendum bot would restate: the same id, or the same bot role on the same engine."""
    return [k for k in base_bots if k["id"] == b["id"] or
            (k.get("role") == b["role"] and (k.get("engine") or {}).get("key") == b["engine"]["key"])]


def build(args, repo, git, check_sources=True):
    deck_path = resolve(args.deck, repo)
    if not os.path.exists(deck_path):
        raise SystemExit("deck file not found: %s" % args.deck)
    if not args.log_doc or any(not (d or "").strip() for d in args.log_doc):
        raise SystemExit("--log-doc is required and may not be empty: the Ladder Log section this deck's games are logged under (e.g. d12)")
    deck_rel = relative(deck_path, repo)
    with open(deck_path, "rb") as fh:
        raw = fh.read()
    try:
        lines = card_list(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise SystemExit("%s: %s" % (deck_rel, e))
    cl = sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    deck = {"name": os.path.splitext(os.path.basename(deck_path))[0], "file": deck_rel,
            "version_id": cl[:12], "card_list_sha256": cl, "file_sha256": sha256_bytes(raw),
            "card_list": lines, "card_count": sum(int(x.split(" ", 1)[0]) for x in lines[1:]),
            "log_docs": [d.strip() for d in args.log_doc], "log_label": (args.log_label or "").strip() or None}
    versions = git.file_versions(deck_rel) if git.ok else None
    if git.ok:
        on_main = git.file_versions(deck_rel, ref=args.main_ref) if args.main_ref else versions
        if not any(v["card_list_sha256"] == cl for v in on_main or []):
            raise SystemExit("%s as it is now (card list %s) is not committed on %s: commit the deck file there first"
                             % (deck_rel, cl[:12], args.main_ref or "any branch"))
    deck["file_versions"] = versions
    deck["committed"] = (True if git.ok else None)

    base = None
    if args.addendum:
        base = load_base(args, deck, repo)

    bots = []
    for p in args.slow_report + args.exam:
        f = resolve(p, repo)
        bots += harness_bots(f, relative(f, repo), deck, git, args.main_ref)
    for p in args.floor:
        f = resolve(p, repo)
        bots.append(floor_bot(f, relative(f, repo), deck, git, args.main_ref, repo))
    if not bots:
        raise SystemExit("no sources given (--slow-report, --exam, --floor)")

    kept, duplicates, ids = [], [], set()
    base_bots = base["doc"]["bots"] if base else []
    for b in bots:
        same = [k for k in kept if k["kind"] == b["kind"] and k["_signature"] == b["_signature"]]
        same_base = [k for k in base_bots if k.get("games_sha256") == b["games_sha256"]]
        if same or same_base:
            duplicates.append({"id": b["id"], "source": b["source"].get("folder") or b["source"].get("page"),
                               "same_games_as": (same or same_base)[0]["id"] + ("" if same else " (base file)")})
            continue
        clash = base_clash(base_bots, b)
        if clash:
            raise SystemExit("addendum: %s restates %s of the base file %s with other games; one game may not get two "
                             "pre-registered forecasts from the same bot and engine: refusing" % (b["id"], clash[0]["id"], base["name"]))
        base_id, i = b["id"], 2
        while b["id"] in ids or any(k["id"] == b["id"] for k in base_bots):
            b["id"] = "%s_%d" % (base_id, i)
            i += 1
        ids.add(b["id"])
        kept.append(b)
    if base and not kept:
        raise SystemExit("addendum: nothing new; every source is already in the base file %s" % base["name"])
    labels = collections.Counter(b["label"] for b in kept + list(base_bots))
    for b in kept:
        if labels[b["label"]] > 1:
            b["label"] = "%s [%s]" % (b["label"], os.path.basename((b["source"].get("folder") or b["source"].get("page") or "").rstrip("/")))

    # every committed slow report or exam that tested this version must be in the base file or this file
    given = {b["source"]["folder"] for b in bots if b["kind"] != "floor"}
    if base:
        given |= {(b.get("source") or {}).get("folder") for b in base_bots}
        given |= {d.get("source") for d in base["doc"].get("duplicates") or []}
    sources_check = {"how": "manifests on %s naming this deck with this card list (slow reports and exams)" % (args.main_ref or "-"),
                     "checked": False, "not_given": [], "other_versions": [], "floor_pages_not_given": []}
    if git.ok and args.main_ref:
        found = committed_harness_sources(git, args.main_ref, deck)
        missing = [f for f, this in found if this and f not in given]
        sources_check.update(checked=True, not_given=missing, other_versions=[f for f, this in found if not this])
        floors_given = {b["source"]["page"] for b in bots if b["kind"] == "floor"}
        if base:
            floors_given |= {(b.get("source") or {}).get("page") for b in base_bots}
        sources_check["floor_pages_not_given"] = [p for p in floor_pages_on_ref(git, args.main_ref, deck) if p not in floors_given]
        if missing and check_sources:
            raise SystemExit("committed sources that tested this version were left out: %s. Give every one (no picking "
                             "after seeing games)." % ", ".join(missing))
    first_game = utc_strict(args.first_game, "--first-game") if args.first_game else None
    for b in kept:
        del b["_signature"]
        if first_game:
            b["committed_before_first_game"] = None if not b["fixed_at"] else b["fixed_at"] < first_game

    doc = {
        "schema": SCHEMA,
        "deck": deck,
        "written_at": now_utc(),
        "written_by": {"script": "make_predictions.py", "code_sha256": code_sha256(), "repo_head": git.head()},
        "first_game_already_played": first_game,
        "games_already_read": args.games_already_read,
        "ladder_log_at_writing": ladder_log_at_writing(args.export, args.newest_video),
        "notes": args.note,
        "who_plays_the_panel": WHO_PLAYS_THE_PANEL,
        "reading_rule_version": READING_RULE_VERSION,
        "reading_rule": READING_RULE,
        "sources_check": sources_check,
        "bots": kept,
        "duplicates": duplicates,
        "matching_rule": MATCH_RULE,
    }
    if base:
        b0 = base["doc"]
        fl = next((b for b in b0["bots"] if b["id"] == b0["forecast"].get("floor_bot")), None)
        if fl is None:
            raise SystemExit("addendum: the base file %s has no floor shape to score with" % base["name"])
        doc["addendum_to"] = {"file": base["name"], "sha256": base["sha256"], "floor_bot": fl["id"]}
        doc["forecast"] = calibrated_forecasts(kept, (fl["id"], floor_shape(fl), b0["forecast"].get("floor_engine_current"),
                                                      "the base file's floor shape (%s)" % fl["id"]))
    else:
        doc["forecast"] = calibrated_forecasts(kept)
    return doc


def load_base(args, deck, repo):
    name = "%s@%s.json" % (deck["name"], deck["version_id"])
    path = args.base or os.path.join(out_dir_path(args.out_dir, repo), name)
    if not os.path.exists(path):
        raise SystemExit("--addendum needs its base file %s (pass --base PATH)" % path)
    if os.path.basename(path) != name:
        raise SystemExit("--base %s is not %s" % (path, name))
    with open(path, "rb") as fh:
        data = fh.read()
    doc = json.loads(data.decode("utf-8"))
    if doc.get("schema") != SCHEMA or doc.get("addendum_to"):
        raise SystemExit("--base %s is not a base predictions file of schema %s" % (path, SCHEMA))
    return {"name": name, "path": path, "sha256": sha256_bytes(data), "doc": doc}


def out_name(deck, addendum):
    tag = ""
    if addendum:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", addendum):
            raise SystemExit("--addendum: letters, digits, '.', '_' or '-' only")
        tag = "+" + addendum
    return "%s@%s%s.json" % (deck["name"], deck["version_id"], tag)


def write_new(path, doc):
    """Create the file whole or not at all, never overwriting (raises FileExistsError). LF line endings everywhere."""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    if os.path.lexists(path):
        raise FileExistsError(path)
    data = (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(prefix=".partial_", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.link(tmp, path)            # atomic, and fails if the name exists
        except FileExistsError:
            raise
        except OSError:                   # no hard links on this file system: create exclusively, then fill
            with open(path, "xb") as fh:
                fh.write(data)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp)


def parser():
    ap = argparse.ArgumentParser(description="Save the bots' numbers for one deck version before his ladder games are read.")
    ap.add_argument("--deck")
    ap.add_argument("--log-doc", action="append", default=[], help="Ladder Log section of this deck (e.g. d12); repeatable")
    ap.add_argument("--log-label", help="how the notes name this deck when several deck files share a section (e.g. 'Deck 13-A')")
    ap.add_argument("--slow-report", action="append", default=[])
    ap.add_argument("--exam", action="append", default=[])
    ap.add_argument("--floor", action="append", default=[])
    ap.add_argument("--export", help="the Ladder Log export at writing (saves the game ids already logged)")
    ap.add_argument("--newest-video", help="the newest video name in the Battle Logs folder at writing")
    ap.add_argument("--repo", help="repository root (default: found from the current folder, then from this script)")
    ap.add_argument("--out-dir", help="default <repo>/" + DEFAULT_OUT + " (a relative path is taken from the current folder)")
    ap.add_argument("--addendum", help="tag for a later file on the same version: <deck>@<id>+<tag>.json")
    ap.add_argument("--base", help="the base predictions file of an --addendum (default: in --out-dir)")
    ap.add_argument("--first-game", help="UTC time of the first ladder game of this version, if one was already played (with Z or an offset)")
    ap.add_argument("--games-already-read", type=int, default=0, help="games of this version already read when the file is written")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--main-ref", default="main", help="branch for 'first_commit_on_main' and the source check (default main)")
    ap.add_argument("--no-git", action="store_true", help="skip git (commit times, version history and the source check are left empty)")
    ap.add_argument("--selftest", action="store_true", help="run on deck 12's real files into a temporary folder")
    return ap


def main(argv=None, git=None, check_sources=True):
    args = parser().parse_args(argv)
    repo = args.repo or find_repo(os.getcwd()) or find_repo(HERE)
    if not repo or not os.path.isdir(repo):
        raise SystemExit("repository not found: pass --repo")
    repo = os.path.abspath(repo)
    if args.selftest:
        return selftest(repo, use_git=not args.no_git)
    if not args.deck:
        raise SystemExit("--deck is required")
    out_dir = out_dir_path(args.out_dir, repo)
    git = git or Git(repo, enabled=not args.no_git)
    if not args.no_git and not git.ok:
        raise SystemExit("git not found (or %s is not a git repository); pass --no-git to write without commit times" % repo)
    if git.ok and args.main_ref and not git.verify_ref(args.main_ref):
        raise SystemExit("no branch %r in %s; pass --main-ref (e.g. origin/main)" % (args.main_ref, repo))
    doc = build(args, repo, git, check_sources=check_sources)
    path = os.path.join(out_dir, out_name(doc["deck"], args.addendum))
    try:
        write_new(path, doc)
    except FileExistsError:
        print("REFUSED: %s exists. Predictions are never overwritten; a later number for this version goes in an --addendum file."
              % path, file=sys.stderr)
        return 3
    print("written %s (version %s = card list sha256 %s...; file sha256 %s...)"
          % (path, doc["deck"]["version_id"], doc["deck"]["card_list_sha256"][:16], doc["deck"]["file_sha256"][:16]))
    for b in doc["bots"]:
        print("  %-48s %5s%% %-14s n=%-5d fixed %s%s%s" % (
            b["label"], b["number_pct"], b["ci95_wilson"], b["n"], b["fixed_at"],
            "" if "committed_before_first_game" not in b else ("  before first game: %s" % b["committed_before_first_game"]),
            "" if b["in_bot_comparison"] else "  (out of the comparison)"))
    for d in doc["duplicates"]:
        print("  (%s from %s: the same games as %s, not repeated)" % (d["id"], d["source"], d["same_games_as"]))
    fc = doc["forecast"]
    print("  forecast shape: %s%s" % (fc.get("floor_bot"), (" (%s)" % fc["note"]) if fc.get("note") else ""))
    sc = doc["sources_check"]
    if sc["checked"]:
        print("  source check on %s: every committed slow report and exam of this version given%s" % (
            args.main_ref, ("; floor pages with this deck's name not given (another version?): " + ", ".join(sc["floor_pages_not_given"]))
            if sc["floor_pages_not_given"] else ""))
    else:
        print("  source check: not done (no git)")
    return 0


# ---------------------------------------------------------------- self-test
DECK12 = "decks/dustin/12-ariados-whimsicott-ogerpon.txt"
DECK12_SHA = "4d059bd2c5cba229cc025746f05dca2d03281ebe07c0712917d9fc8d53c65bd5"
DECK12_ID = "5c3b7d688afa"
D12_SOURCES = {
    "slow": "rl/results/slow_reports/2026-10-13_12-ariados-whimsicott-ogerpon",
    "exam5": "rl/results/strength_2026-10-05_kx3_exam",
    "m64": "rl/results/exam_m32_m64_2026-10/reg_m64",
    "m32": "rl/results/exam_m32_m64_2026-10/reg_m32",
    "floor": "rl/results/floor_recheck_rules2_2026-10/pages/12/12-ariados-whimsicott-ogerpon.md",
    "floor_sep30": "rl/results/floor_dustin_2026-09-30/12-ariados-whimsicott-ogerpon.md",
}


def d12_argv(repo, out_dir, sources=("slow", "exam5", "m64", "m32", "floor", "floor_sep30"), extra=()):
    a = ["--repo", repo, "--deck", DECK12, "--log-doc", "d12"]
    for k in sources:
        a += [{"slow": "--slow-report", "floor": "--floor", "floor_sep30": "--floor"}.get(k, "--exam"), D12_SOURCES[k]]
    return a + ["--first-game", "2026-10-14T14:25:46Z", "--games-already-read", "10", "--out-dir", out_dir] + list(extra)


# id: (n, number, ci95, per-list pct in PANEL order, label, in the comparison); the floors' per-list check is on wins.
D12_EXPECT = {
    "kx3_slow": (160, 61.3, [53.5, 68.5], [60.0, 40.0, 80.0, 45.0, 55.0, 65.0, 65.0, 80.0],
                 "frozen kx3 (slow report, current engine)", True),
    "km3_slow_same_deals": (160, 34.1, [27.2, 41.7], [40.0, 22.5, 40.0, 25.0, 40.0, 20.0, 45.0, 40.0],
                            "km3 (slow report same deals)", True),
    "kx3_exam@31dbd2e6": (48, 62.5, [48.4, 74.8], [66.7, 33.3, 66.7, 50.0, 50.0, 66.7, 83.3, 83.3],
                          "frozen kx3 (exam strength_2026-10-05_kx3_exam, older engine)", False),
    "km3_exam_same_deals@31dbd2e6": (48, 27.1, [16.6, 41.0], [33.3, 16.7, 33.3, 33.3, 16.7, 33.3, 16.7, 33.3],
                                     "km3 (exam strength_2026-10-05_kx3_exam same deals, older engine)", False),
    "m64_exam@69a5a441": (48, 68.8, [54.7, 80.1], [66.7, 66.7, 83.3, 33.3, 50.0, 100.0, 66.7, 83.3],
                          "m64 (exam reg_m64, older engine)", False),
    "m32_exam@69a5a441": (48, 70.8, None, None, "m32 (exam reg_m32, older engine)", False),
    "km3_floor": (1920, 33.1, [31.0, 35.2], None, "km3 floor", True),
    "km3_floor@engine-2026-09-30": (1920, 31.4, None, None, "km3 floor (older engine)", False),
}
D12_FLOOR_WINS = [113, 42, 81, 58, 66, 77, 76, 122]
D12_BANDS = {"kx3_slow": {"10": [3, 9], "20": [8, 17], "40": [18, 31]},
             "km3_slow_same_deals": {"10": [1, 7], "20": [3, 11], "40": [7, 20]},
             "km3_floor": {"10": [1, 6], "20": [3, 11], "40": [8, 19]},
             "m64_exam@69a5a441": {"10": [4, 10], "20": [9, 18], "40": [19, 35]}}
# Calibrated forecasts (%), PANEL order: the km3 floor's shape, shifted so the mean equals the bot's number.
D12_FORECAST = {"kx3_slow": [75.2, 42.0, 63.5, 52.1, 56.4, 61.7, 61.2, 77.9],
                "km3_slow_same_deals": [48.2, 18.2, 34.8, 25.0, 28.4, 33.1, 32.7, 52.0],
                "km3_floor": [47.1, 17.5, 33.8, 24.2, 27.5, 32.1, 31.7, 50.8]}
# Fixed before game 1 (2026-10-14T14:25:46Z)? m64's merged games file (22:15Z) and m32's (20:55Z) are later.
D12_BEFORE_FIRST = {"kx3_slow": True, "km3_slow_same_deals": True, "kx3_exam@31dbd2e6": True,
                    "km3_exam_same_deals@31dbd2e6": True, "m64_exam@69a5a441": False, "m32_exam@69a5a441": False,
                    "km3_floor": True, "km3_floor@engine-2026-09-30": True}
# Rule v1, decided case by case: (opponent text, list, status, fit). Deck 12's ten opponents first, then last season's
# edge cases, then spellings the rule must survive, then cases decided on purpose.
MATCH_CASES = [
    ("Mega Sharpedo ex / Magikarp / Mantyke", "l-sharpedo", "readout", "exact"),
    ("Mega Swampert ex / Mantyke / Cramorant", None, "unmatched", None),
    ("Zeraora / Magneton / Magnezone / Miraidon ex", None, "unmatched", None),
    ("Oricorio / Indeedee ex / Dedenne ex", None, "unmatched", None),
    ("Magnemite / Magneton / Magnezone", None, "unmatched", None),
    ("Indeedee ex / Bulbasaur / Ivysaur / Mega Venusaur ex", None, "unmatched", None),
    ("Tapu Koko ex / Oricorio", None, "unmatched", None),
    ("Charmander / Charmeleon / Charizard", None, "unmatched", None),
    ("Castform Sunny Form / Torchic / Mega Blaziken ex", "t-blaziken", "panel", "exact"),
    ("Chien-Pao ex / Baxcalibur / Suicune ex", "t-suicune", "panel", "exact"),
    ("team rocket: magmar, weezing ex,", None, "ruled out", None),
    ("lucario ex and team rocket raticate ex", None, "unmatched", None),
    ("Mega Lucario ex / Riolu / Hitmontop / Bonsly", "t-lucario", "panel", "variant"),
    ("Mega sableye ex / hydreigon", "t-hydreigon", "panel", "variant"),
    ("Team Rocket’s Raticate ex / Alolan Ninetales ex", None, "unmatched", None),
    ("Darkrai espeon sleep", None, "unmatched", None),
    ("Mega Altaria ex? likely", "t-altaria", "inferred", "exact"),
    # spellings
    ("Mega-Blaziken ex", "t-blaziken", "panel", "exact"),
    ("M Altaria ex / Espeon", "t-altaria", "panel", "exact"),
    ("Suicune / Baxcalibur", "t-suicune", "panel", "exact"),
    ("Suicune ex / Baxcalibur", "t-suicune", "panel", "exact"),
    ("TR Weezing ex / Hoopa ex", "t-weezing", "panel", "exact"),
    ("Team Rocket's Weezing ex / Hoopa ex", "t-weezing", "panel", "exact"),
    ("M Rayquaza ex", "g-dragonair_mega_rayquaza", "readout", "exact"),
    ("Hydreigon ex / Mega Absol ex", "t-hydreigon", "panel", "exact"),
    ("Entei ex / Charmander / Charmeleon / Mega Charizard Y ex; full list unknown", "h-charizardy_entei", "readout", "exact"),
    # decided on purpose
    ("Suicune", None, "unmatched", None),                       # no 'ex' and no Baxcalibur: could be another Suicune
    ("Altaria ex", None, "unmatched", None),                    # the Mega is not named
    ("Lucario ex (Mega)", None, "unmatched", None),             # 'mega lucario' not written as such
    ("Weezing / Koffing", None, "unmatched", None),             # the non-ex Weezing is another card
    ("weezing (gas leak not team rocket), nihilego, darkrai ex", None, "unmatched", None),
    ("Mega Lucario ex / TR Raticate ex", None, "ruled out", None),
    ("Weezing ex / Magmar (not TR)", None, "ruled out", None),  # any Magmar rules Weezing out (ruling P3)
    ("Combee / Vespiquen ex?", "t-vespiquen", "inferred", "exact"),
    ("maybe Mega Sceptile ex", "t-sceptile", "inferred", "exact"),
    ("Hydreigon / Mega Absol ex hoopa ex", "t-hydreigon", "panel", "variant"),   # Hoopa ex is not in the list
    ("Mega Lucario ex / Lucario", "t-lucario", "panel", "exact"),
    ("Hydreigon / bombirdier", "t-hydreigon", "panel", "exact"),
    ("Mega Altaria ex / Espeon / Darkrai / Igglybuff", "t-altaria", "panel", "exact"),
    ("Mega Charizard Y ex / Entei ex", "h-charizardy_entei", "readout", "exact"),
    ("Entei ex / Charmander / Charmeleon / Mega Charizard ex; Mega form and full list unknown", None, "unmatched", None),
    ("Charizard ex / entei ex", None, "unmatched", None),
    ("Drampa / Mega Rayquaza ex / Dragonair", "g-dragonair_mega_rayquaza", "readout", "variant"),
    ("magikarp/carvanha", None, "unmatched", None),             # conceded before Mega Sharpedo showed
]


def _expect_refusal(fn, words):
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            fn()
        return False, "no refusal"
    except SystemExit as e:
        return (words in str(e)), str(e)


def selftest(repo, use_git=True):
    # Deck 12's real files were written under the Oct 12 pin: its checks expect that pin's CURRENT_ENGINE.
    global CURRENT_ENGINE
    saved, CURRENT_ENGINE = CURRENT_ENGINE, CURRENT_ENGINE_OCT12
    try:
        return _selftest(repo, use_git)
    finally:
        CURRENT_ENGINE = saved


def _selftest(repo, use_git=True):
    fails = []

    def check(cond, what):
        print(("  ok    " if cond else "  FAIL  ") + what)
        if not cond:
            fails.append(what)

    print("self-test on deck 12's real files in %s" % repo)
    git = Git(repo, enabled=use_git)
    if use_git and not git.ok:
        raise SystemExit("git not found: run the self-test with --no-git")
    print("git: %s" % ("available (read only)" if git.ok else "not used"))
    for k, p in D12_SOURCES.items():
        if not os.path.exists(os.path.join(repo, p)):
            raise SystemExit("missing %s: is --repo the PocketDeckSim repository?" % p)
    tmp = tempfile.mkdtemp(prefix="ladder_predictions_selftest_")
    nogit = [] if use_git else ["--no-git"]
    try:
        # versions: the card-list id ignores comments, spacing, line endings and line order; a card change is new
        with open(os.path.join(repo, DECK12), "rb") as fh:
            raw = fh.read().decode("utf-8")
        lines = raw.splitlines()
        cosmetic = "﻿# deck 12, a comment\r\n" + "\r\n".join("  " + " ".join(l.split()).replace(" ", "   ") + "  "
                                                                     for l in reversed(lines)) + "\r\n\r\n"
        changed = raw.replace("1 Lisia B1 226", "1 Sabrina A1 225")
        check(card_list_sha256(raw)[:12] == DECK12_ID, "deck 12's version id (card list) is %s" % card_list_sha256(raw)[:12])
        check(card_list_sha256(cosmetic) == card_list_sha256(raw), "a comment, spacing, CRLF and line-order edit keeps the version")
        check(card_list_sha256(changed) != card_list_sha256(raw) and changed != raw, "one card changed makes a new version")
        check(card_list_sha256(raw.replace("2 Spinarak B1a 005", "1 Spinarak B1a 005\n1 Spinarak B1a 5")) == card_list_sha256(raw),
              "two lines of the same card, and a number without leading zeros, read as one entry")

        argv = d12_argv(repo, tmp, extra=["--note", "self-test"] + nogit)
        args = parser().parse_args(argv)
        doc = build(args, repo, git)
        check(doc["deck"]["file_sha256"] == DECK12_SHA, "deck 12 file sha256 is 4d059bd2c5cb...")
        check(doc["deck"]["version_id"] == DECK12_ID and doc["deck"]["card_count"] == 20 and doc["deck"]["log_docs"] == ["d12"],
              "version %s, 20 cards, Ladder Log section d12" % doc["deck"]["version_id"])
        bots = {b["id"]: b for b in doc["bots"]}
        check(sorted(bots) == sorted(D12_EXPECT), "bots: %s" % ", ".join(sorted(bots)))
        for bid, (n, num, ci, per, label, comp) in D12_EXPECT.items():
            b = bots.get(bid)
            if not b:
                check(False, "%s present" % bid)
                continue
            check((b["n"], b["number_pct"]) == (n, num) and (ci is None or b["ci95_wilson"] == ci),
                  "%s: %s%% %s n=%d (expected %s%% %s n=%d)" % (bid, b["number_pct"], b["ci95_wilson"], b["n"], num, ci, n))
            check(b["label"] == label and b["in_bot_comparison"] == comp,
                  "%s labelled '%s', in the bot comparison: %s" % (bid, b["label"], b["in_bot_comparison"]))
            check(b["panel_pilot"] == ["km3"], "%s: the panel is played by %s" % (bid, b["panel_pilot"]))
            if per is not None:
                got = [r["pct"] for r in b["per_opponent"]]
                check(got == per, "%s per list %s" % (bid, got))
        check(len({b["label"] for b in doc["bots"]}) == len(doc["bots"]), "every bot's label is unique in the file")
        check(bots["kx3_slow"]["knows_the_panel_lists"] and bots["m64_exam@69a5a441"]["knows_the_panel_lists"]
              and bots["m32_exam@69a5a441"]["knows_the_panel_lists"]
              and not bots["km3_slow_same_deals"]["knows_the_panel_lists"] and not bots["km3_floor"]["knows_the_panel_lists"],
              "kx3, m64 and m32 marked as knowing the 8 lists (optimistic end); km3 not")
        fl = bots.get("km3_floor")
        if fl:
            check([r["wins"] for r in fl["per_opponent"]] == D12_FLOOR_WINS and fl["wins"] == 635,
                  "km3 floor wins per list %s, total %d of %d (draws %d)"
                  % ([r["wins"] for r in fl["per_opponent"]], fl["wins"], fl["n"], fl["ties"]))
            check(fl["engine"]["current_when_written"] and fl["engine"]["key"] == "rl/engine-2026-10-12/deckgym",
                  "km3 floor is on the current engine (key %s)" % fl["engine"]["key"])
        check(bots["km3_floor@engine-2026-09-30"]["wins"] == 602, "the Sept 30 floor (older engine): 602 wins, kept for the record")
        check(bots["kx3_slow"]["engine"]["key"] == "4ebb30a94173" and not bots["kx3_exam@31dbd2e6"]["engine"]["current_when_written"]
              and not bots["m64_exam@69a5a441"]["engine"]["current_when_written"], "engines: slow report current; the exams older")
        for bid, bands in D12_BANDS.items():
            got = bots[bid]["wins_range_95_if_ladder_equalled_this"]
            check(got == bands, "%s wins range %s" % (bid, got))
        dups = [(d["source"], d["same_games_as"]) for d in doc["duplicates"]]
        check(dups == [(D12_SOURCES["m64"], "km3_exam_same_deals@31dbd2e6"), (D12_SOURCES["m32"], "km3_exam_same_deals@31dbd2e6")],
              "reg_m64's and reg_m32's km3 arms are the Oct 5 km3 arm, game for game: kept once (%s)" % dups)
        check(doc["forecast"]["floor_bot"] == "km3_floor" and doc["forecast"]["floor_engine_current"],
              "the forecast's shape is the current-engine floor, not the Sept 30 one")
        for bid, want in D12_FORECAST.items():
            fc = doc["forecast"]["per_bot"].get(bid, {})
            got = [fc.get("per_list_pct", {}).get(k) for k in PANEL]
            mean = sum(fc.get("per_list", {}).values()) / 8 if fc else None
            check(got == want and mean is not None and abs(mean - bots[bid]["x"] / bots[bid]["n"]) < 1e-6,
                  "calibrated forecasts for %s: %s, mean %.4f = its number %.4f"
                  % (bid, got, mean or 0, bots[bid]["x"] / bots[bid]["n"]))
        check(doc["written_by"]["code_sha256"]["make_predictions.py"] == sha256_file(os.path.abspath(__file__)),
              "the file records this script's sha256 (and read_ladder.py's: %s)" % str(doc["written_by"]["code_sha256"]["read_ladder.py"])[:12])
        check(doc["reading_rule_version"] == READING_RULE_VERSION and "time unknown" in " ".join(doc["reading_rule"]),
              "reading rule %s: no video name means 'time unknown', feedback" % doc["reading_rule_version"])
        for text, lst, status, fit in MATCH_CASES:
            m = match_opponent(text)
            check((m["list"], m["status"], m["fit"]) == (lst, status, fit),
                  "match %-58s -> %s %s %s" % (text[:58], m["list"], m["status"], m["fit"] or ""))
        # every Pokemon named in rule v1 is a card in that list's file
        for row in MATCH_RULE["lists"]:
            p = os.path.join(repo, MATCH_RULE["list_files"][row["list"]])
            with open(p, encoding="utf-8") as fh:
                names = {" ".join(l.split()[1:-2]) for l in fh.read().splitlines() if l.strip() and l[0].isdigit()}
            missing = [x for x in row["pokemon"] if x not in names]
            check(not missing, "rule v1's Pokemon for %s are all in %s%s" % (row["list"], MATCH_RULE["list_files"][row["list"]],
                                                                           (": missing %s" % missing) if missing else ""))
        # refusals
        fake = os.path.join(tmp, "fake_slow_report")
        os.makedirs(fake)
        with open(os.path.join(repo, D12_SOURCES["slow"], "manifest.json"), encoding="utf-8") as fh:
            man = json.load(fh)
        for d in man["decks"]:
            d["sha256"] = "0" * 64
        with open(os.path.join(fake, "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(man, fh)
        shutil.copy(os.path.join(repo, D12_SOURCES["slow"], "games.jsonl"), os.path.join(fake, "games.jsonl"))
        ok, msg = _expect_refusal(lambda: harness_bots(fake, "fake_slow_report", doc["deck"], Git(repo, enabled=False), ""), "refusing")
        check(ok, "a source that tested another version is refused (expected: %s)" % msg[:90])
        bad_floor = dict(bots["km3_floor"], per_opponent=[dict(r) for r in bots["km3_floor"]["per_opponent"]])
        bad_floor["per_opponent"][3].update(n=0, x=0)
        ok, msg = _expect_refusal(lambda: floor_shape(bad_floor), "does not cover all 8 lists")
        check(ok, "a floor with no games against a list is refused (expected: %s)" % msg[:80])
        ok, msg = _expect_refusal(lambda: utc_strict("2026-10-14T14:25:46", "--first-game"), "no time zone")
        check(ok, "a --first-game without a time zone is refused (expected: %s)" % msg[:70])
        ok, msg = _expect_refusal(lambda: build(parser().parse_args(["--deck", DECK12, "--log-doc", "", "--slow-report", D12_SOURCES["slow"]] + nogit), repo, git), "may not be empty")
        check(ok, "an empty --log-doc is refused")
        if os.sep == "/":
            ok, msg = _expect_refusal(lambda: out_dir_path("C:\\Users\\x\\out", repo), "Windows path")
            check(ok, "a Windows --out-dir under WSL is refused (expected: %s)" % msg[:70])
        ok, msg = _expect_refusal(lambda: out_dir_path(os.path.join(repo, "decks"), repo), "inside the repository")
        check(ok, "an --out-dir inside the repository other than %s is refused" % DEFAULT_OUT)
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            check(out_dir_path("rel_out", repo) == os.path.join(tmp, "rel_out"), "a relative --out-dir is taken from the current folder")
        finally:
            os.chdir(cwd)
        if git.ok:
            v = doc["deck"]["file_versions"] or []
            check(len(v) == 1 and v[0]["sha256"] == DECK12_SHA and v[0]["card_list_sha256"][:12] == DECK12_ID
                  and v[0]["first_commit"].startswith("83fd3496"),
                  "deck file has one version, first committed %s at %s"
                  % (v[0]["first_commit"][:8] if v else None, v[0]["first_date"] if v else None))
            for bid, before in D12_BEFORE_FIRST.items():
                b = bots[bid]
                check(b.get("committed_before_first_game") == before,
                      "%s fixed at %s; before the first game: %s" % (bid, b["fixed_at"], b.get("committed_before_first_game")))
            check(fl["source"]["deck_check"]["matches"] is True, "the floor games' commit holds this deck version")
            sc = doc["sources_check"]
            check(sc["checked"] and sc["not_given"] == [], "source check on main: every committed slow report and exam of this version given")
            ok, msg = _expect_refusal(lambda: build(parser().parse_args(d12_argv(repo, tmp, sources=("slow", "exam5", "m64", "floor"))), repo, git), "left out")
            check(ok and "reg_m32" in msg, "leaving out a committed source (reg_m32) is refused (expected: %s)" % msg[:110])
        else:
            print("  skip  commit times, deck history and the source check (no git)")
        path = os.path.join(tmp, out_name(doc["deck"], None))
        check(os.path.basename(path) == "12-ariados-whimsicott-ogerpon@%s.json" % DECK12_ID, "file name %s" % os.path.basename(path))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = main(argv, git=git)
        check(rc == 0 and os.path.exists(path), "first write creates the file")
        with open(path, "rb") as fh:
            before = fh.read()
        check(b"\r\n" not in before and not [f for f in os.listdir(tmp) if f.startswith(".partial_")],
              "the file has LF line endings and no partial file is left behind")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc2 = main(argv, git=git)
        with open(path, "rb") as fh:
            after = fh.read()
        print("  (expected refusal, as printed: %s)" % err.getvalue().strip().replace(tmp, "<tmp>"))
        check(rc2 == 3 and before == after and err.getvalue().startswith("REFUSED"), "second write is refused and the file is unchanged")
        check(os.path.commonpath([os.path.abspath(path), tmp]) == tmp, "wrote only inside the temporary folder")
        # addenda: new bots only, scored with the base file's shape
        tmp2 = os.path.join(tmp, "addendum_case")
        with contextlib.redirect_stdout(io.StringIO()):
            rcb = main(d12_argv(repo, tmp2, sources=("slow", "exam5", "m64", "floor", "floor_sep30")) + nogit, git=git, check_sources=False)
            rca = main(["--repo", repo, "--deck", DECK12, "--log-doc", "d12", "--exam", D12_SOURCES["m32"], "--out-dir", tmp2,
                        "--addendum", "m32"] + nogit, git=git)
        ap = os.path.join(tmp2, "12-ariados-whimsicott-ogerpon@%s+m32.json" % DECK12_ID)
        add = json.load(open(ap, encoding="utf-8")) if os.path.exists(ap) else {}
        check(rcb == 0 and rca == 0 and [b["id"] for b in add.get("bots", [])] == ["m32_exam@69a5a441"]
              and add.get("addendum_to", {}).get("file") == "12-ariados-whimsicott-ogerpon@%s.json" % DECK12_ID
              and add["forecast"]["floor_bot"] == "km3_floor" and "m32_exam@69a5a441" in add["forecast"]["per_bot"],
              "an exam-only addendum (m32) holds only its new bot and is scored with the base file's floor shape")
        check([d["same_games_as"] for d in add.get("duplicates", [])] == ["km3_exam_same_deals@31dbd2e6 (base file)"],
              "the addendum's km3 arm, already in the base file, is not repeated")
        ok, msg = _expect_refusal(lambda: main(["--repo", repo, "--deck", DECK12, "--log-doc", "d12", "--exam", D12_SOURCES["m64"],
                                                "--out-dir", tmp2, "--addendum", "again"] + nogit, git=git), "nothing new")
        check(ok, "an addendum repeating the base file's sources is refused (expected: %s)" % msg[:80])
        base_doc = json.load(open(os.path.join(tmp2, "12-ariados-whimsicott-ogerpon@%s.json" % DECK12_ID), encoding="utf-8"))
        restated = dict(bots["kx3_slow"], id="kx3_slow_rerun", games_sha256="f" * 64)
        clash = base_clash(base_doc["bots"], restated)
        other = dict(bots["kx3_slow"], id="kx3_slow_next_pin", role="kx3_slow", engine={"key": "0123456789ab"})
        check([k["id"] for k in clash] == ["kx3_slow"] and not base_clash(base_doc["bots"], other),
              "an addendum bot restating a base bot (same bot, same engine, other games) clashes; the same bot on a new engine does not")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELF-TEST %s (%d failed)" % ("PASSED" if not fails else "FAILED", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
