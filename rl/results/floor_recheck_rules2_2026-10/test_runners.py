#!/usr/bin/env python3
"""Tests for run_check.sh (Part A) and run_pages.sh (Part B), written before either runner was trusted. No game is played and
no deckgym runs: each test builds a small fake repository (git, committed references, fake programs, a fake floor.py and
run_screen.py that copy canned pages) and runs the real runner source in it, with only the engine's hashes, P, its tree,
D's first list's sha256 and Oct 2's commit replaced by the fake ones (every replacement is asserted to have happened).

    python3 test_runners.py                run the tests (RUNNER_DIR=<folder> tests another copy of the runners)
    python3 test_runners.py --mutations    break the runners on purpose, one change at a time; each must fail a test
"""
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER_DIR = os.environ.get("RUNNER_DIR", HERE)
REAL_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FR = "rl/results/floor_recheck_rules2_2026-10"
OLD1 = "rl/results/floor_recheck_2026-10"
OLD2 = "rl/results/floor_drafts_2026-10-02"
OLD30 = "rl/results/floor_dustin_2026-09-30"
SW = "rl/results/engine_switch_rules2_2026-10"
DNAME = "draft-D-entei-grimhound"
OPPS = ["t-sceptile", "t-blaziken", "t-hydreigon", "t-altaria", "t-suicune", "t-weezing", "t-lucario", "t-vespiquen"]
STEMS = ["brew-06-pyukumuku-silvally-payback", "brew-06b-pyukumuku-silvally-scyther-grass", "control_k3/14-comfey-raticate-hypno",
         "brew-05b-meowstic-hatterene-comfey", "07-skarmory-stall"]
WINS = {STEMS[0]: 125, STEMS[1]: 262, STEMS[2]: 196, STEMS[3]: 577, STEMS[4]: 1098}
OLD_GYM, NEW_GYM = "rl/engine-2026-10-02/deckgym", "rl/engine-2026-10-12/deckgym"
OLD_GF, NEW_GF = "rl/engine-2026-10-02/goldfish", "rl/engine-2026-10-12/goldfish"
OLD_GF_SHA = "cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66"
REAL = dict(deckgym="0a9199bca480acf6f862342e042b7f36bb885416659eafeef24485c1783158c4",
            legality_scan="bf9d75020558b843a4f71d80a848d9150daff44e34f3b2159c16539b015a0ec7",
            goldfish="d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84")
REAL_P = "c7a25df49e0b4acdc61f8b78f2cab599d86f5c76"
REAL_TREE = "70652fff03af511e32a169e16209e158a998dda6"
REAL_OLDC = "2d7082cf9fccfd8ae7976c508320f1c8ca4e6b4f"
REAL_DFIRST = "4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585"
BUILT = {"deckgym": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/deckgym",
         "legality_scan": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/examples/legality_scan",
         "goldfish": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/examples/goldfish"}
FAKE_GOLDFISH = """#!/usr/bin/env bash
deck=""; cov=""
while [ $# -gt 0 ]; do case $1 in --deck) deck=$2; shift 2;; --coverage) cov=$2; shift 2;; *) shift;; esac; done
case "$deck" in *d_first*) cp "$FAKE_FIX/newcov_root.json" "$cov";; *) cp "$FAKE_FIX/newcov_amended.json" "$cov";; esac
"""
FAKE_FLOOR = '''import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ROLES = {
    "decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt": {
        "Silvally": "attacker", "Team Rocket's Scyther": "attacker",
        "Pyukumuku": "bench piece/passive ability", "Rocky Helmet": "Trainer (played)"},
}


def database():
    return {}


def flagged_cards(coverage, pilot, db):
    out = {}
    for cid, c in sorted(coverage.items()):
        if not c["engine_complete"] or c["limitations"]:
            e = out.setdefault(c["name"], dict(name=c["name"], ids=set(), reasons=[]))
            e["ids"].add(cid)
            e["reasons"].append(f"engine: {c['engine_status']}" + (f"; {', '.join(c['limitations'])}" if c["limitations"] else ""))
    return out


def main():
    a = sys.argv[1:]
    deck, out = a[0], a[a.index("--out") + 1]
    stem = os.path.splitext(os.path.basename(deck))[0]
    if os.environ.get("FAKE_FAIL") == stem:
        sys.exit(3)
    rel = os.path.relpath(os.path.abspath(deck), ROOT)
    key = "dvp" if rel in ROLES and "d_first" in rel else stem
    os.makedirs(out, exist_ok=True)
    for x in (".md", "_coverage.json", "_games.jsonl"):
        src = os.path.join(os.environ["FAKE_FIX"], "new", key + x)
        open(os.path.join(out, stem + x), "wb").write(open(src, "rb").read())


if __name__ == "__main__":
    main()
'''


def sha(b):
    return hashlib.sha256(b).hexdigest()


def opp_lines(total):
    w = [total // 8] * 8
    w[0] += total - sum(w)
    return w


def page_md(stem, total, gym, gf, gfsha, verdict="fail", pilots=("km3", "km3"), victini=None, note="", engine_text=None,
            extra=""):
    name = os.path.basename(stem)
    L = [note] if note else []
    L += [f"# Floor check: {name}", "", f"**Verdict: {verdict}.** {total} wins in 1920 games (x%) against the 8 lists.",
          "Flagged cards: none.", "",
          f"- Engine: {engine_text or gym} (the manifest's available release). Pilots: {pilots[0]} on the deck, {pilots[1]} on the "
          "panel. 240 games per matchup.", "", "## Worst matchups", ""]
    L += [f"- {o}: {w}/240 = {100 * w // 240}%" for o, w in zip(OPPS, opp_lines(total))]
    L += ["", "| card | role | why flagged | opportunities | used | share |", "|---|---|---|---|---|---|"]
    if victini:
        role, why = victini
        L.append(f"| Victini (B3 025) | {role} (set for this deck) | {why} | 100 | 90 | 90.0% |")
    L += ["", "## For a second reader", "",
          f"- Coverage from {gf} (sha256 {gfsha}; the official release; `--games 0 --coverage`): `x_coverage.json`." + extra]
    return "\n".join(L) + "\n"


def screen_txt(gym):
    out = []
    for s in STEMS[:2]:
        out.append(f"== {s}: {WINS[s]}/1920 = 7% vs the panel  (km3 on the deck, km3 on the panel, 240 games per matchup; engine {gym})")
        out += [f"   {o:<14} {w}-{240 - w}    2%" for o, w in zip(OPPS, opp_lines(WINS[s]))]
        out.append("")
    return "\n".join(out) + "\n"


def cov(victini_text, extra=None):
    c = {"B3 025": {"engine_complete": False, "engine_status": "Implemented with unverified rule boundaries",
                    "limitations": [victini_text], "name": "Victini"},
         "A4a 010": {"engine_complete": True, "engine_status": "Fully implemented", "limitations": [], "name": "Entei ex"}}
    if extra:
        c["B1 225"] = {"engine_complete": False, "engine_status": "Implemented with unverified rule boundaries",
                       "limitations": [extra], "name": "Gholdengo ex"}
    return json.dumps(c, indent=1) + "\n"


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text if isinstance(text, bytes) else text.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    if mode:
        os.chmod(path, mode)


def git(repo, *a, check=True):
    p = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


class Fake:
    """One fake repository. build() takes hooks to break one thing before the references or the pin are committed."""

    def __init__(self, tmp, pinned=True, ref_hook=None, pin_hook=None, post_hook=None, runner_replace=None,
                 manifest_edit=None, skip_programs_record=False):
        self.repo = os.path.join(tmp, "repo")
        self.fix = os.path.join(tmp, "fix")
        self.D = os.path.join(self.repo, FR)
        self.pinned = pinned
        self.runner_replace = runner_replace or []
        r = self.repo
        os.makedirs(r)
        git(r, "init", "-q")
        write(r + "/.gitattributes", "* -text\n")
        self.gold = FAKE_GOLDFISH.encode()
        self.prog = {"deckgym": b"#!/bin/sh\necho deckgym\n", "legality_scan": b"#!/bin/sh\necho scan\n", "goldfish": self.gold}
        self.fake = {k: sha(v) for k, v in self.prog.items()}
        self.d_first = b"Energy: Fire\n2 Entei ex A4a 010\n"
        self.fake_dfirst = sha(self.d_first)
        self._references()
        self._support()
        if ref_hook:
            ref_hook(self)
        git(r, "add", "-A")
        git(r, "commit", "-qm", "references")
        self.oldc = git(r, "rev-parse", "HEAD")
        write(r + "/engine/src/lib.rs", "// P\n")
        git(r, "add", "-A")
        git(r, "commit", "-qm", "P")
        self.p = git(r, "rev-parse", "HEAD")
        self.tree = git(r, "rev-parse", "HEAD:engine")
        write(r + "/engine/../notes.txt", "after P\n")
        git(r, "add", "-A")
        git(r, "commit", "-qm", "src")
        self.src = git(r, "rev-parse", "HEAD")
        self._programs_record(skip_programs_record)
        if pinned:
            for k, v in self.prog.items():
                write(f"{r}/rl/engine-2026-10-12/{k}", v, 0o755)
            write(r + "/rl/engine-2026-10-12/SHA256SUMS", "".join(f"{h}  {k}\n" for k, h in self.fake.items()))
        self._manifest(manifest_edit)
        self._runners()
        if pin_hook:
            pin_hook(self)
        git(r, "add", "-A")
        git(r, "commit", "-qm", "pin")
        self._new_outputs()
        if post_hook:
            post_hook(self)

    # ---- fixtures
    def _references(self):
        r = self.repo
        for s in STEMS:
            gfsha = OLD_GF_SHA
            write(f"{r}/{OLD1}/{s}.md", page_md(s, WINS[s], OLD_GYM, OLD_GF, gfsha, "control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted" if "control" in s else "fail",
                                                  ("k3", "k3") if "control" in s else ("km3", "km3")))
            write(f"{r}/{OLD1}/{s}_coverage.json", f'{{"cov": "{s}"}}\n')
            write(f"{r}/{OLD1}/{s}_games.jsonl", f'{{"games": "{s}"}}\n')
        write(f"{r}/{OLD1}/run_screen.txt", screen_txt(OLD_GYM))
        # Part B's references
        for name, d in (("root", f"{OLD2}"), ("amended", f"{OLD2}/draft-D_amended"), ("dvp", f"{OLD2}/draft-D_victini-passive")):
            role = "bench piece/passive ability" if name == "dvp" else "attacker"
            old_c = cov("old caveat", extra="gh old" if name == "amended" else None)
            note = "> **From a MODIFIED COPY of floor.py**\n> second line\n\n" if name == "dvp" else ""
            write(f"{r}/{d}/{DNAME}.md", note + page_md(DNAME, 693, OLD_GYM, OLD_GF, OLD_GF_SHA, "clears the floor",
                                                         victini=(role, "engine: Implemented with unverified rule boundaries; old caveat")))
            write(f"{r}/{d}/{DNAME}_coverage.json", old_c)
            write(f"{r}/{d}/{DNAME}_games.jsonl", f"{role} games\n" if name == "dvp" else "root games\n")
        write(f"{r}/{OLD2}/draft-D_victini-passive/floor_copy.diff",
              "--- a/floor.py\n+++ floor_victini_passive.py\n@@ -91,6 +91,7 @@\n context\n"
              '+    "decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt": {"Victini": "bench piece/passive ability"},\n context\n')
        shutil.copy(os.path.join(REAL_ROOT, OLD2, "draft-D_victini-passive/run_copy.py"), f"{r}/{OLD2}/draft-D_victini-passive/run_copy.py")
        for d, amended in (("D_root", False), ("D_amended", True)):
            write(f"{r}/{SW}/floor_7c/{d}/{DNAME}.md", page_md(DNAME, 693, NEW_GYM, OLD_GF, OLD_GF_SHA, "clears the floor",
                  victini=("attacker", "engine: Implemented with unverified rule boundaries; old caveat"),
                  engine_text="../../../../../../../home/x/engine-rules2/engine/target/release/deckgym"))
            write(f"{r}/{SW}/floor_7c/{d}/{DNAME}_coverage.json", cov("old caveat", extra="gh old" if amended else None))
            write(f"{r}/{SW}/floor_7c/{d}/{DNAME}_games.jsonl", "root games\n")
        write(f"{r}/{SW}/floor_7c/d_first/{DNAME}.txt", self.d_first)
        for s, v in (("12-ariados-whimsicott-ogerpon", 602), ("brew-07-hoopa-darkrai-sableye", 1168), ("brew-09-sableye-obstagoon", 835)):
            write(f"{r}/{OLD30}/{s}.md", page_md(s, v, "rl/engine-2026-09-30/deckgym", "rl/engine-2026-09-30/goldfish", "8f60", "clears the floor"))
        write(f"{r}/decks/dustin/12-ariados-whimsicott-ogerpon.txt", "deck\n")
        write(f"{r}/decks/brews/brew-07-hoopa-darkrai-sableye.txt", "deck\n")
        write(f"{r}/decks/brews/brew-09-sableye-obstagoon.txt", "deck\n")
        write(f"{r}/decks/brews/drafts_2026-10-01/{DNAME}.txt", "Energy: Fire\n2 Entei ex A4a 010\n2 Houndour A2a 011\n")

    def _support(self):
        r = self.repo
        write(r + "/decks/screen/floor.py", FAKE_FLOOR)
        write(r + "/decks/screen/run_screen.py", "import sys\nprint(open(__import__('os').environ['FAKE_FIX'] + '/new/run_screen.txt').read(), end='')\n")
        write(r + "/decks/screen/panel_ladder_2026-09-26/calibrate.py",
              "import os\ndef working_pilot():\n    return os.environ.get('FAKE_PILOT', 'km3'), 'fake'\n")
        write(r + "/current_engine.py",
              "import json, os\ndef resolve(project=None):\n    m = json.load(open(os.path.join(project, 'project_manifest.json')))\n"
              "    return os.path.join(project, os.environ.get('FAKE_RESOLVE') or m['available_release']['artifact'])\n")
        for o in OPPS:
            write(f"{r}/decks/screen/opponents/{o}.txt", f"{o}\n")
        write(r + "/engine/src/players/public_pricing_player.rs", "// pricing\n")
        write(r + "/lib/deckgym-database.json", "[]\n")
        os.makedirs(r + "/engine/examples", exist_ok=True)

    def _programs_record(self, skip):
        lines = "".join(f"{self.fake[k]}  {BUILT[k]}\n" for k in BUILT)
        if skip:
            lines = ""
        write(f"{self.repo}/{SW}/programs.sha256", lines)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "record", "--allow-empty")

    def _manifest(self, edit):
        old = {"name": "main-8626a35", "artifact": OLD_GYM}
        if self.pinned:
            rel = {"name": "main-" + self.src[:7], "artifact": "rl/engine-2026-10-12/deckgym", "sha256": self.fake["deckgym"],
                   "legality_scan": "rl/engine-2026-10-12/legality_scan", "legality_scan_sha256": self.fake["legality_scan"],
                   "goldfish": "rl/engine-2026-10-12/goldfish", "goldfish_sha256": self.fake["goldfish"], "source_commit": self.src}
            hist = [{"name": "main-8626a35", "superseded": "2026 by main-x"}]
        else:
            rel = dict(old, source_commit=self.src, goldfish="rl/engine-2026-10-02/goldfish")
            hist = []
        m = {"available_release": rel, "historical_releases": hist}
        if edit:
            edit(m, self)
        write(self.repo + "/project_manifest.json", json.dumps(m, indent=1) + "\n")

    def _runners(self):
        """The real runner sources with the fake hashes put in; each replacement must happen."""
        pairs = [(REAL[k], self.fake[k]) for k in REAL] + [(REAL_P, self.p), (REAL_TREE, self.tree), (REAL_OLDC, self.oldc),
                                                           (REAL_DFIRST, self.fake_dfirst)]
        need = {"run_check.sh": [REAL[k] for k in REAL] + [REAL_P, REAL_TREE, REAL_OLDC],
                "run_pages.sh": [REAL["goldfish"], REAL_DFIRST]}
        fake_of = dict(pairs)
        for name in ("run_check.sh", "run_pages.sh"):
            text = open(os.path.join(RUNNER_DIR, name), encoding="utf-8").read()
            for a in need[name]:
                assert a in text, f"{name} does not hold {a[:12]}"
                text = text.replace(a, fake_of[a])
            for a, b in self.runner_replace:
                assert a in text, f"{name}: no {a!r}"
                text = text.replace(a, b)
            write(f"{self.D}/{name}", text)
        write(f"{self.D}/PLAN.md", "# plan\n")

    def _new_outputs(self):
        """What the fake floor.py and run_screen.py will write: Oct 2's pages with the engine lines put in."""
        n = self.fix + "/new"
        for s in STEMS:
            old = open(f"{self.repo}/{OLD1}/{s}.md", encoding="utf-8").read()
            old = old.replace(f"- Engine: {OLD_GYM} (", f"- Engine: {NEW_GYM} (").replace(f"- Coverage from {OLD_GF} (sha256 {OLD_GF_SHA};",
                              f"- Coverage from {NEW_GF} (sha256 {self.fake['goldfish']};")
            write(f"{n}/{os.path.basename(s)}.md", old)
            for x in ("_coverage.json", "_games.jsonl"):
                write(f"{n}/{os.path.basename(s)}{x}", open(f"{self.repo}/{OLD1}/{s}{x}", "rb").read())
        write(f"{n}/run_screen.txt", screen_txt(NEW_GYM))
        for s, v in (("12-ariados-whimsicott-ogerpon", 700), ("brew-07-hoopa-darkrai-sableye", 1100), ("brew-09-sableye-obstagoon", 800)):
            write(f"{n}/{s}.md", page_md(s, v, NEW_GYM, NEW_GF, self.fake["goldfish"], "clears the floor"))
            write(f"{n}/{s}_coverage.json", "{}\n")
            write(f"{n}/{s}_games.jsonl", f"{s}\n")
        write(f"{n}/dvp.md", page_md(DNAME, 693, NEW_GYM, NEW_GF, self.fake["goldfish"], "clears the floor",
                                      victini=("bench piece/passive ability", "engine: Implemented with unverified rule boundaries; new caveat")))
        write(f"{n}/dvp_coverage.json", cov("new caveat"))
        write(f"{n}/dvp_games.jsonl", "bench piece/passive ability games\n")
        write(f"{self.fix}/newcov_root.json", cov("new caveat"))
        write(f"{self.fix}/newcov_amended.json", cov("new caveat", extra="gh old"))

    # ---- running
    def env(self, **extra):
        shim = os.path.join(self.fix, "bin")
        write(shim + "/date", '#!/bin/sh\nif [ "$1" = "-u" ] && [ "$2" = "+%H%M" ]; then echo "${FAKE_HHMM:-0300}"; else exec /bin/date "$@"; fi\n', 0o755)
        e = {"PATH": shim + ":" + os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp"), "FAKE_FIX": self.fix,
             "LAUNCH_DETACHED_RUN": "test-run", "PYTHONDONTWRITEBYTECODE": "1"}
        e.update(extra)
        return {k: v for k, v in e.items() if v is not None}

    def run(self, script, *args, **env):
        p = subprocess.run(["bash", f"{self.D}/{script}", *args], cwd=self.repo, env=self.env(**env), capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def files(self):
        out = set()
        for base, ds, fs in os.walk(self.D):
            out |= {os.path.relpath(os.path.join(base, f), self.D) for f in fs}
            out |= {os.path.relpath(os.path.join(base, d), self.D) + "/" for d in ds}
        return out

    def new_files(self, before):
        return self.files() - before


BASE = None


class Base(unittest.TestCase):
    def mk(self, **kw):
        tmp = tempfile.mkdtemp(prefix="fr_test_")
        self.addCleanup(shutil.rmtree, tmp, True)
        self.f = Fake(tmp, **kw)
        self.before = self.f.files()
        return self.f

    def assertRefused(self, rc_out, text=None):
        rc, out = rc_out
        self.assertEqual(rc, 2, out)
        self.assertEqual(self.f.files(), self.before, "a refused run wrote files")
        if text:
            self.assertIn(text, out)

    def verdicts(self):
        return open(self.f.D + "/verdicts.txt", encoding="utf-8").read()


class RealConstants(unittest.TestCase):
    def test_the_runner_holds_the_specs_values(self):
        s = open(os.path.join(RUNNER_DIR, "run_check.sh"), encoding="utf-8").read()
        for want in ('NEW = "rl/engine-2026-10-12"', REAL["deckgym"], REAL["legality_scan"], REAL["goldfish"], REAL_P, REAL_TREE,
                     REAL_OLDC, 'SUPERSEDED = "main-8626a35"', 'OLD = "rl/results/floor_recheck_2026-10"', "-ge 1015", "-lt 2200",
                     'OCT2 = {"brew-06": 125, "brew-06b": 262, "control": 196, "brew-05b": 577, "deck-07": 1098}'):
            self.assertIn(want, s)
        self.assertIn(REAL_DFIRST, open(os.path.join(RUNNER_DIR, "run_pages.sh"), encoding="utf-8").read())

    def test_real_record_names_sitting_1s_builds(self):
        rec = open(os.path.join(REAL_ROOT, SW, "programs.sha256"), encoding="utf-8").read()
        for k in REAL:
            self.assertIn(f"{REAL[k]}  {BUILT[k]}", rec)


class PartA(Base):
    def test_happy_path_passes(self):
        f = self.mk()
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 0, out)
        v = self.verdicts()
        self.assertTrue(v.startswith("RESULT PASSED main-"), v[:200])
        self.assertNotIn("NOT MET", v)
        self.assertNotIn("RECHECK STOPPED", out)
        self.assertEqual(v.count("equal but for the engine lines"), 6)       # 5 pages + run_screen.txt
        self.assertEqual(v.count("byte-equal"), 10)
        self.assertIn("input (reported, not a gate)", out)
        self.assertTrue(f.files() >= {"verdicts.txt", "timing.txt", "run_check.log", "run_screen.txt", "control_k3/14-comfey-raticate-hypno.md"})

    def test_result_line_is_first_when_not_passed(self):
        f = self.mk()
        p = f.fix + "/new/brew-06-pyukumuku-silvally-payback_games.jsonl"
        write(p, b'{"games": "changed"}\n')
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertTrue(self.verdicts().startswith("RESULT NOT PASSED main-"))
        self.assertIn("brew-06-pyukumuku-silvally-payback_games.jsonl differs", self.verdicts().split("\n")[0])

    def test_games_and_coverage_have_no_exceptions(self):
        for x in ("_games.jsonl", "_coverage.json"):
            f = self.mk()
            write(f.fix + f"/new/07-skarmory-stall{x}", b"X\n")
            rc, out = f.run("run_check.sh")
            self.assertEqual(rc, 1, out)
            self.assertIn(f"NOT MET 07-skarmory-stall{x} v", self.verdicts())

    def test_a_changed_byte_elsewhere_in_a_page(self):
        f = self.mk()
        p = f.fix + "/new/brew-05b-meowstic-hatterene-comfey.md"
        write(p, open(p, encoding="utf-8").read().replace("Flagged cards: none.", "Flagged cards: nonE."))
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("1 line differs", self.verdicts())

    def test_the_engine_line_left_old_or_doubled(self):
        f = self.mk()
        p = f.fix + "/new/07-skarmory-stall.md"
        t = open(p, encoding="utf-8").read().replace(NEW_GYM, OLD_GYM)
        write(p, t)
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT MET engine on every page", self.verdicts())

    def test_an_old_engine_line_twice_in_a_reference_page(self):
        def twice(fk):
            p = f"{fk.repo}/{OLD1}/07-skarmory-stall.md"
            t = open(p, encoding="utf-8").read()
            line = [l for l in t.split("\n") if l.startswith("- Engine:")][0]
            write(p, t.replace(line, line + "\n" + line))
        f = self.mk(ref_hook=twice)
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("holds the engine line", self.verdicts())
        self.assertIn("2 times, not 1", self.verdicts())

    def test_the_old_engine_line_not_exactly_twice_in_run_screen(self):
        def once(fk):
            p = f"{fk.repo}/{OLD1}/run_screen.txt"
            t = open(p, encoding="utf-8").read()
            write(p, t.replace(f"; engine {OLD_GYM})", "; engine x)", 1))
        f = self.mk(ref_hook=once)
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("1 times, not 2", self.verdicts())

    def test_wins_differ_from_oct2(self):
        f = self.mk()
        p = f.fix + "/new/brew-06-pyukumuku-silvally-payback.md"
        write(p, open(p, encoding="utf-8").read().replace("125 wins", "126 wins"))
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT MET wins equal Oct 2's exactly", self.verdicts())

    def test_a_page_that_reads_pass_where_fail_is_needed(self):
        f = self.mk()
        p = f.fix + "/new/brew-06b-pyukumuku-silvally-scyther-grass.md"
        write(p, open(p, encoding="utf-8").read().replace("**Verdict: fail.**", "**Verdict: clears the floor.**"))
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("brew-06b: 'clears the floor'", self.verdicts())

    def test_the_control_must_read_untrusted(self):
        f = self.mk()
        p = f.fix + "/new/14-comfey-raticate-hypno.md"
        write(p, open(p, encoding="utf-8").read().replace("untrusted", "fail"))
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT MET control deck 14", self.verdicts())

    def test_run_screen_must_equal_the_floor(self):
        f = self.mk()
        p = f.fix + "/new/run_screen.txt"
        write(p, open(p, encoding="utf-8").read().replace("t-sceptile     20-", "t-sceptile     19-", 1))
        rc, out = f.run("run_check.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("NOT MET brew-06: plain run_screen.py", self.verdicts())

    def test_a_missing_output_file(self):
        f = self.mk()
        os.remove(f.fix + "/new/brew-05b-meowstic-hatterene-comfey_coverage.json")
        rc, out = f.run("run_check.sh")
        self.assertNotEqual(rc, 0, out)
        self.assertNotIn("RESULT PASSED", out)

    def test_a_mid_run_stop_writes_no_result(self):
        f = self.mk()
        rc, out = f.run("run_check.sh", FAKE_FAIL="brew-05b-meowstic-hatterene-comfey")
        self.assertEqual(rc, 3, out)
        self.assertIn("RECHECK STOPPED in brew-05b", out)
        self.assertNotRegex(out, r"RESULT (NOT )?PASSED")
        self.assertNotIn("verdicts.txt", f.files())
        self.assertIn("RECHECK STOPPED", open(f.D + "/run_check.log").read())

    def test_refuses_before_the_pin_and_writes_nothing(self):
        f = self.mk(pinned=False)
        self.assertRefused(f.run("run_check.sh"), "not rules switch 2's rl/engine-2026-10-12/deckgym")

    def test_dry_run_before_the_pin(self):
        f = self.mk(pinned=False)
        rc, out = f.run("run_check.sh", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("BEFORE THE PIN: a real run would refuse on the engine check", out)
        self.assertIn("PLAN (dry run, nothing written)", out)
        self.assertEqual(f.files(), self.before)

    def test_dry_run_after_the_pin(self):
        f = self.mk()
        rc, out = f.run("run_check.sh", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("BEFORE THE PIN", out)
        self.assertIn("main-" + f.src[:7], out)
        self.assertEqual(f.files(), self.before)

    def test_dry_run_still_fails_on_what_is_not_the_pins(self):
        f = self.mk(pinned=False)
        os.remove(f.repo + f"/{OLD1}/07-skarmory-stall.md")
        rc, out = f.run("run_check.sh", "--dry-run")
        self.assertEqual(rc, 2, out)
        self.assertIn("is not Oct 2's file as committed", out)

    def test_engine_check_mode(self):
        f = self.mk()
        rc, out = f.run("run_check.sh", "--engine-check")
        self.assertEqual((rc, f.files()), (0, self.before), out)
        f2 = self.mk(pinned=False)
        self.assertRefused(f2.run("run_check.sh", "--engine-check"))

    def test_unknown_argument(self):
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", "--go"), "usage")

    def test_clock_window(self):
        f = self.mk()
        for hhmm, ok in (("1014", True), ("1015", False), ("1200", False), ("2159", False), ("2200", True), ("0300", True)):
            rc, out = f.run("run_check.sh", "--dry-run", FAKE_HHMM=hhmm)       # a dry run only notes it
            self.assertEqual("a real run would refuse now" in out, not ok, (hhmm, out))
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", FAKE_HHMM="1200"), "between 5:15 am and 5 pm Central")
        f = self.mk()
        rc, out = f.run("run_check.sh", FAKE_HHMM="1200", ALLOW_DAYTIME="1")
        self.assertEqual(rc, 0, out)
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", FAKE_HHMM="1015"))

    def test_a_deckgym_variable(self):
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", DECKGYM_THREADS="2"), "DECKGYM_")

    def test_not_started_through_launch_detached(self):
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", LAUNCH_DETACHED_RUN=None), "launch_detached.sh")

    def test_earlier_outputs_present(self):
        for name in ("timing.txt", "verdicts.txt", "run_screen.txt", "brew-06-x.md", "a_games.jsonl", "a_coverage.json", "run_check.log"):
            f = self.mk(post_hook=lambda fk, name=name: write(f"{fk.D}/{name}", "old\n"))
            self.before = f.files()
            self.assertRefused(f.run("run_check.sh"), "from an earlier run is here")
        f = self.mk(post_hook=lambda fk: os.makedirs(fk.D + "/control_k3"))
        self.assertRefused(f.run("run_check.sh"), "control_k3")

    def test_plan_or_runner_not_committed_unchanged(self):
        f = self.mk(post_hook=lambda fk: write(fk.D + "/PLAN.md", "# plan edited\n"))
        self.assertRefused(f.run("run_check.sh"), "PLAN.md differs from its commit")
        f = self.mk(post_hook=lambda fk: open(fk.D + "/run_check.sh", "a").write("# x\n"))
        self.assertRefused(f.run("run_check.sh"), "run_check.sh differs from its commit")
        f = self.mk(post_hook=lambda fk: open(fk.D + "/run_pages.sh", "a").write("# x\n"))
        self.assertRefused(f.run("run_check.sh"), "run_pages.sh differs from its commit")

        def untracked(fk):
            git(fk.repo, "rm", "-q", "--cached", f"{FR}/PLAN.md")
            git(fk.repo, "commit", "-qm", "x")
        f = self.mk(post_hook=untracked)
        self.assertRefused(f.run("run_check.sh"), "PLAN.md is not committed")

    def test_a_reference_file_missing_or_changed(self):
        f = self.mk(post_hook=lambda fk: os.remove(f"{fk.repo}/{OLD1}/07-skarmory-stall_games.jsonl"))
        self.assertRefused(f.run("run_check.sh"), "is not Oct 2's file as committed")
        f = self.mk(post_hook=lambda fk: write(f"{fk.repo}/{OLD1}/run_screen.txt", "changed\n"))
        self.assertRefused(f.run("run_check.sh"), "run_screen.txt is not Oct 2's file as committed")

        def gone(fk):
            git(fk.repo, "rm", "-q", f"{OLD1}/07-skarmory-stall.md")
            git(fk.repo, "commit", "-qm", "gone")
        f = self.mk(post_hook=gone)
        self.assertRefused(f.run("run_check.sh"), "07-skarmory-stall.md is not Oct 2's file")

    def test_engine_program_hash_and_files(self):
        f = self.mk(post_hook=lambda fk: write(f"{fk.repo}/rl/engine-2026-10-12/goldfish", b"#!/bin/sh\nother\n", 0o755))
        self.assertRefused(f.run("run_check.sh"), "goldfish has sha256")
        f = self.mk(post_hook=lambda fk: os.remove(f"{fk.repo}/rl/engine-2026-10-12/legality_scan"))
        self.assertRefused(f.run("run_check.sh"), "legality_scan is missing")
        f = self.mk(post_hook=lambda fk: os.chmod(f"{fk.repo}/rl/engine-2026-10-12/deckgym", 0o644))
        self.assertRefused(f.run("run_check.sh"), "not executable")
        f = self.mk(pin_hook=lambda fk: write(fk.repo + "/rl/engine-2026-10-12/SHA256SUMS", "bad  deckgym\n"))
        self.assertRefused(f.run("run_check.sh"), "SHA256SUMS does not hold exactly")

        def uncommitted(fk):
            git(fk.repo, "rm", "-q", "--cached", "rl/engine-2026-10-12/deckgym")
            git(fk.repo, "commit", "-qm", "x")
        f = self.mk(post_hook=uncommitted)
        self.assertRefused(f.run("run_check.sh"), "deckgym is not committed as it is on disk")

    def test_the_programs_record_must_name_sitting_1s_builds(self):
        f = self.mk(skip_programs_record=True)
        self.assertRefused(f.run("run_check.sh"), "programs.sha256 records None")

    def test_manifest_facts(self):
        def noname(m, fk):
            m["available_release"]["name"] = "main-abcdef0"
        f = self.mk(manifest_edit=noname)
        self.assertRefused(f.run("run_check.sh"), "is named 'main-abcdef0'")

        def nosuper(m, fk):
            m["historical_releases"] = [{"name": "main-8626a35"}]
        f = self.mk(manifest_edit=nosuper)
        self.assertRefused(f.run("run_check.sh"), "main-8626a35 is not in the manifest's historical_releases as superseded")

        def nohist(m, fk):
            m["historical_releases"] = []
        f = self.mk(manifest_edit=nohist)
        self.assertRefused(f.run("run_check.sh"), "historical_releases")

        def badsha(m, fk):
            m["available_release"]["goldfish_sha256"] = "0" * 64
        f = self.mk(manifest_edit=badsha)
        self.assertRefused(f.run("run_check.sh"), "goldfish_sha256")

        def badsrc(m, fk):
            m["available_release"]["source_commit"] = "1" * 40
            m["available_release"]["name"] = "main-1111111"
        f = self.mk(manifest_edit=badsrc)
        self.assertRefused(f.run("run_check.sh"), "source_commit")

    def test_p_and_its_tree(self):
        f = self.mk(runner_replace=[]) if False else None
        # P not in the source commit: the runner is told a different P
        def other_p(fk):
            pass
        tmp = tempfile.mkdtemp(prefix="fr_test_")
        self.addCleanup(shutil.rmtree, tmp, True)
        f = Fake(tmp)
        self.f, self.before = f, f.files()
        # rewrite the runner with a P that is not an ancestor, and recommit it
        for name in ("run_check.sh",):
            t = open(f.D + "/" + name).read().replace(f.p, f.oldc)      # the references commit: an ancestor of src, so use a commit after src
        other = git(f.repo, "commit-tree", f"{f.src}^{{tree}}", "-m", "unrelated")
        t = open(f.D + "/run_check.sh").read().replace(f.p, other)
        write(f.D + "/run_check.sh", t)
        git(f.repo, "add", "-A"); git(f.repo, "commit", "-qm", "p changed")
        self.before = f.files()
        self.assertRefused(f.run("run_check.sh"), f"P ({other[:7]}) is not in the source commit")
        t = open(f.D + "/run_check.sh").read().replace(f.tree, "0" * 40)
        write(f.D + "/run_check.sh", t)
        git(f.repo, "add", "-A"); git(f.repo, "commit", "-qm", "tree changed")
        self.assertRefused(f.run("run_check.sh"), "is not P's tree")

    def test_pricing_file_must_equal_the_source_commits(self):
        def change(fk):
            write(fk.repo + "/engine/src/players/public_pricing_player.rs", "// changed\n")
            git(fk.repo, "add", "-A"); git(fk.repo, "commit", "-qm", "later")
        f = self.mk(post_hook=change)
        self.assertRefused(f.run("run_check.sh"), "public_pricing_player.rs differs from the source commit's")

    def test_resolve_and_pilot(self):
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", FAKE_RESOLVE="rl/engine-2026-10-02/deckgym"), "current_engine.py resolves")
        f = self.mk()
        self.assertRefused(f.run("run_check.sh", FAKE_PILOT="kta3"), "default to kta3, not km3")


class PartB(Base):
    def passed(self, fk):
        write(fk.D + "/verdicts.txt", "RESULT PASSED main-x: the floor stays usable\n\nPASS x\n")

    def mkb(self, **kw):
        post = kw.pop("post_hook", None)

        def hook(fk):
            self.passed(fk)
            if post:
                post(fk)
        f = self.mk(post_hook=hook, **kw)
        self.before = f.files()
        return f

    def test_happy_path(self):
        f = self.mkb()
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 0, out)
        self.assertIn("PAGES DONE", out)
        pages = {p.split("/")[1] for p in f.files() if p.startswith("pages/") and "/" in p[6:]}
        self.assertEqual(pages, {"12", "brew-07", "brew-09", "D_victini-passive", "D_root", "D_amended"})   # and no deck 10
        for name in pages:
            note = open(f"{f.D}/pages/{name}/OLD_PAGE.txt").read()
            self.assertIn("Old page:", note)
            self.assertIn("Old: ", note)
        self.assertIn("floor_dustin_2026-09-30/12-ariados", open(f"{f.D}/pages/12/OLD_PAGE.txt").read())
        for d in ("D_root", "D_amended"):
            md = open(f"{f.D}/pages/{d}/{DNAME}.md").read()
            self.assertTrue(md.startswith("> Games: step 7c's replays on the new engine, equal to Oct 2's, and no game was played"))
            self.assertIn("new caveat", md)
            self.assertNotIn("old caveat", md)
            self.assertIn(f"- Engine: {NEW_GYM} (", md)
            self.assertIn(f"- Coverage from {NEW_GF} (sha256 {f.fake['goldfish']};", md)
            self.assertNotIn("home/x/engine", md)
            self.assertEqual(open(f"{f.D}/pages/{d}/{DNAME}_coverage.json").read().count("new caveat"), 1)
        vp = open(f"{f.D}/pages/D_victini-passive/{DNAME}.md").read()
        self.assertTrue(vp.startswith("> **From a MODIFIED COPY of floor.py"))
        self.assertIn("floor_7c/d_first/draft-D-entei-grimhound.txt", vp.split("\n\n")[0])
        copy = open(f"{f.D}/pages/D_victini-passive/floor_victini_passive.py").read()
        self.assertEqual(copy.count('"Victini": "bench piece/passive ability"'), 1)
        self.assertIn(f"{SW}/floor_7c/d_first/{DNAME}.txt", copy)
        self.assertIn("D_victini-passive: clears the floor, 693 of 1920", out)
        self.assertNotIn("PAGES STOPPED", out)

    def test_refuses_without_a_passed_part_a(self):
        f = self.mk()
        self.assertRefused(f.run("run_pages.sh"), "verdicts.txt is not here")
        f = self.mk(post_hook=lambda fk: write(fk.D + "/verdicts.txt", "RESULT NOT PASSED main-x: ...\n"))
        self.before = f.files()
        self.assertRefused(f.run("run_pages.sh"), "does not start \"RESULT PASSED\"")

    def test_refuses_before_the_pin(self):
        f = self.mkb(pinned=False)
        self.assertRefused(f.run("run_pages.sh"), "not rules switch 2's")

    def test_dry_run(self):
        f = self.mk(pinned=False)
        rc, out = f.run("run_pages.sh", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("BEFORE THE PIN OR PART A", out)
        self.assertIn("PLAN (dry run, nothing written)", out)
        self.assertEqual(f.files(), self.before)
        f = self.mkb()
        rc, out = f.run("run_pages.sh", "--dry-run")
        self.assertEqual((rc, f.files()), (0, self.before), out)
        self.assertNotIn("BEFORE THE PIN", out)

    def test_dry_run_still_fails_on_inputs_that_are_not_the_pins(self):
        f = self.mk(pinned=False, post_hook=lambda fk: open(f"{fk.repo}/{SW}/floor_7c/D_root/{DNAME}.md", "a").write("x\n"))
        rc, out = f.run("run_pages.sh", "--dry-run")
        self.assertEqual(rc, 2, out)
        self.assertIn("not committed as they are on disk", out)

    def test_earlier_pages_present(self):
        f = self.mkb(post_hook=lambda fk: os.makedirs(fk.D + "/pages"))
        self.assertRefused(f.run("run_pages.sh"), "pages/ from an earlier run")

    def test_clock_launch_and_deckgym_refusals(self):
        f = self.mkb()
        self.assertRefused(f.run("run_pages.sh", FAKE_HHMM="1200"), "5:15 am")
        self.assertRefused(f.run("run_pages.sh", LAUNCH_DETACHED_RUN=None), "launch_detached.sh")
        self.assertRefused(f.run("run_pages.sh", DECKGYM_X="1"), "DECKGYM_")
        rc, out = f.run("run_pages.sh", FAKE_HHMM="1200", ALLOW_DAYTIME="1")
        self.assertEqual(rc, 0, out)

    def test_plan_and_runner_must_be_committed(self):
        f = self.mkb(post_hook=lambda fk: open(fk.D + "/run_pages.sh", "a").write("# x\n"))
        self.assertRefused(f.run("run_pages.sh"), "run_pages.sh differs from its commit")

    def test_a_victini_passive_game_that_differs_is_a_stop(self):
        f = self.mkb()
        write(f.fix + "/new/dvp_games.jsonl", "bench piece/passive ability games, one differs\n")
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("STOP:", out)
        self.assertIn("a game that differs goes to Dustin", out)
        self.assertIn("PAGES STOPPED in D_victini-passive", out)
        self.assertFalse(os.path.exists(f.D + "/pages/D_root"))

    def test_a_victini_passive_page_that_differs_elsewhere_is_a_stop(self):
        f = self.mkb()
        p = f.fix + "/new/dvp.md"
        write(p, open(p).read().replace("Flagged cards: none.", "Flagged cards: some."))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("line(s) differ", out)

    def test_a_non_victini_coverage_difference_is_a_stop(self):
        f = self.mkb()
        write(f.fix + "/newcov_amended.json", cov("new caveat", extra="gh NEW text"))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("flagged card Gholdengo ex's reasons differ", out)
        self.assertIn("PAGES STOPPED in D_amended", out)

    def test_an_unflagged_coverage_entry_that_differs_is_a_stop(self):
        f = self.mkb()
        c = json.loads(cov("new caveat"))
        c["A4a 010"]["engine_status"] = "Changed text"
        write(f.fix + "/newcov_root.json", json.dumps(c))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("entries other than Victini's differ", out)

    def test_victini_no_longer_flagged_is_a_stop(self):
        f = self.mkb()
        c = json.loads(cov("new caveat"))
        c["B3 025"].update(engine_complete=True, limitations=[])
        write(f.fix + "/newcov_root.json", json.dumps(c))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("flagged cards differ", out)

    def test_floor_failure_is_a_stop(self):
        f = self.mkb()
        rc, out = f.run("run_pages.sh", FAKE_FAIL="brew-07-hoopa-darkrai-sableye")
        self.assertEqual(rc, 3, out)
        self.assertIn("PAGES STOPPED in brew-07", out)
        self.assertNotIn("PAGES DONE", out)

    def test_a_page_that_is_not_a_floor_page_is_a_stop(self):
        f = self.mkb()
        p = f.fix + "/new/12-ariados-whimsicott-ogerpon.md"
        write(p, open(p).read().replace("Pilots: km3 on the deck", "Pilots: k3 on the deck"))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("is not a floor page", out)
        p = f.fix + "/new/12-ariados-whimsicott-ogerpon.md"

    def test_a_page_naming_the_old_engine_is_a_stop(self):
        f = self.mkb()
        p = f.fix + "/new/brew-09-sableye-obstagoon.md"
        write(p, open(p).read().replace(NEW_GYM, OLD_GYM))
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn(f"not {NEW_GYM}", out)

    def test_inputs_must_be_the_committed_files(self):
        f = self.mkb(post_hook=lambda fk: write(f"{fk.repo}/{OLD2}/{DNAME}_games.jsonl", "edited\n"))
        self.assertRefused(f.run("run_pages.sh"), "not committed as they are on disk")
        f = self.mkb(post_hook=lambda fk: write(f"{fk.repo}/{SW}/floor_7c/d_first/{DNAME}.txt", "Energy: Water\n"))
        self.assertRefused(f.run("run_pages.sh"), "not committed as they are on disk")

    def test_d_first_must_be_the_9cc6667_blob(self):
        def other(fk):
            write(f"{fk.repo}/{SW}/floor_7c/d_first/{DNAME}.txt", "Energy: Water\n")
            git(fk.repo, "add", "-A"); git(fk.repo, "commit", "-qm", "x")
        f = self.mkb(post_hook=other)
        self.assertRefused(f.run("run_pages.sh"), "d_first's list is not the 9cc6667 blob")

    def test_floor_py_without_the_roles_anchor(self):
        def edit(fk):
            p = fk.repo + "/decks/screen/floor.py"
            write(p, open(p).read().replace('"Rocky Helmet": "Trainer (played)"},\n}\n', '"Rocky Helmet": "Trainer (played)"},\n    "x": {},\n}\n'))
            git(fk.repo, "add", "-A"); git(fk.repo, "commit", "-qm", "x")
        f = self.mkb(post_hook=edit)
        self.assertRefused(f.run("run_pages.sh"), "ROLES table no longer ends")

    def test_the_copy_differs_from_floor_py_by_exactly_oct2s_line(self):
        f = self.mkb(post_hook=lambda fk: None)
        # Oct 2's diff names a different added line: the rebuilt copy must be refused
        p = f"{f.repo}/{OLD2}/draft-D_victini-passive/floor_copy.diff"
        write(p, open(p).read().replace("Victini", "Victini2"))
        git(f.repo, "add", "-A"); git(f.repo, "commit", "-qm", "x")
        self.before = f.files()
        rc, out = f.run("run_pages.sh")
        self.assertEqual(rc, 1, out)
        self.assertIn("is not Oct 2's", out)


def mutations():
    """Break the runners on purpose; each broken copy must fail at least one test."""
    M = [
        ("run_check.sh", "an old engine line may occur any number of times", "        if want.count(a) != n:", "        if False:"),
        ("run_check.sh", "coverage files are not compared", '"_coverage.json", "_games.jsonl")] + [("run_screen.txt", RS_SUBS)]', '"_games.jsonl")] + [("run_screen.txt", RS_SUBS)]'),
        ("run_check.sh", "any difference is accepted", "    if new == want.encode(\"utf-8\"):", "    if True:"),
        ("run_check.sh", "the engine lines are not put in", '"\\n- Engine: {NEW_GYM} (", 1),', '"\\n- Engine: {OLD_GYM} (", 1),'),
        ("run_check.sh", "RESULT line not first", 'out = [result, ""] + L', 'out = L + ["", result]'),
        ("run_check.sh", "NOT PASSED exits 0", "sys.exit(1 if short else 0)", "sys.exit(0)"),
        ("run_check.sh", "wins need not equal Oct 2's", "need(got == OCT2,", "need(True,"),
        ("run_check.sh", "run_screen is not compared with the floor", 'need(len(p["opp"]) == 8 and s["opp"] == p["opp"] and s["total"] == p["wins"], f"{k} run_screen",', 'need(True, f"{k} run_screen",'),
        ("run_check.sh", "the control may read anything", 'need(c["verdict"] == "untrusted" and', 'need(True or'),
        ("run_check.sh", "a mid-run stop says nothing", "RECHECK STOPPED in $stage", "recheck in $stage"),
        ("run_check.sh", "the window opens at 10:30", "-ge 1015", "-ge 1030"),
        ("run_check.sh", "the window closes at 21:00", "-lt 2200", "-lt 2100"),
        ("run_check.sh", "the DECKGYM check is gone", "if [ -n \"$(env | grep -E '^DECKGYM_' || true)\" ]; then", "if false; then"),
        ("run_check.sh", "launch_detached is not required", 'if [ "$dry" = 0 ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ]; then', "if false; then"),
        ("run_check.sh", "earlier outputs are ignored", 'if [ -e "$f" ]; then shellbad+="$(basename "$f") from an earlier run', 'if false; then shellbad+="$(basename "$f") from an earlier run'),
        ("run_check.sh", "an uncommitted plan is accepted", "if ! git ls-files --error-unmatch -- \"$D/$f\" > /dev/null 2>&1; then", "if false; then"),
        ("run_check.sh", "a changed plan is accepted", "elif ! git diff --quiet HEAD -- \"$D/$f\"; then", "elif false; then"),
        ("run_check.sh", "reference blobs are not checked", "    if not blob_equal(p, OLDC):", "    if False:"),
        ("run_check.sh", "the pin check is gone", 'engine_pinned = rel.get("artifact") == f"{NEW}/deckgym"', "engine_pinned = True"),
        ("run_check.sh", "the pin does not refuse", 'if bad or (pin and MODE != "dry"):', 'if bad:'),
        ("run_check.sh", "program hashes are not checked", "        if sha(p) != h:", "        if False:"),
        ("run_check.sh", "SHA256SUMS is not checked", "    if sums != PROGS:", "    if False:"),
        ("run_check.sh", "superseded is not checked", "    if not any(r.get(\"name\") == SUPERSEDED and r.get(\"superseded\")", "    if False and not any(r.get(\"name\") == SUPERSEDED and r.get(\"superseded\")"),
        ("run_check.sh", "P need not be in the source commit", 'if git("merge-base", "--is-ancestor", P_COMMIT, src)[0]:', "if False:"),
        ("run_check.sh", "the engine tree is not checked", 'if git("rev-parse", "--verify", "--quiet", src + ":engine")[1] != ENGINE_TREE:', "if False:"),
        ("run_check.sh", "the pricing file is not checked", "    if not blob_equal(PRICING, src):", "    if False:"),
        ("run_check.sh", "the pilot is not checked", '    if pilot != "km3":', "    if False:"),
        ("run_check.sh", "current_engine is not checked", '    if gym != f"{NEW}/deckgym":', "    if False:"),
        ("run_check.sh", "the programs record is not checked", "    if rec.get(BUILT[k]) != PROGS[k]:", "    if False:"),
        ("run_check.sh", "the dry run writes a file", '  dry)\n    printf', '  dry)\n    echo x > "$D/dry.txt"; printf'),
        ("run_check.sh", "the dry run creates a folder", '  dry)\n    printf', '  dry)\n    mkdir -p "$D/pages"; printf'),
        ("run_pages.sh", "Part A's result is not required", '"RESULT PASSED"*) ;;', '*) ;;'),
        ("run_pages.sh", "an earlier pages/ is accepted", 'if [ -e "$PG" ]; then bad+=', 'if false; then bad+='),
        ("run_pages.sh", "Victini-passive games are not compared", 'if open(new, "rb").read() != open(old, "rb").read():', 'if False:'),
        ("run_pages.sh", "other coverage entries may differ", 'if other:', 'if False:'),
        ("run_pages.sh", "the flagged cards may differ", 'if sorted(fo) != sorted(fn):', 'if False:'),
        ("run_pages.sh", "the one line is not written", 'D_LINE + "\\n\\n" + "\\n".join(lines)', '"\\n".join(lines)'),
        ("run_pages.sh", "a page naming the old engine is accepted", '    if f["engine"] != NEW_GYM:', '    if False:'),
        ("run_pages.sh", "a non-floor page is accepted", '    if f["pilots"] != ("km3", "km3") or f["n"] != 1920', '    if False and f["n"] != 1920'),
        ("run_pages.sh", "the copy's diff is not checked", "    if added != want:", "    if False:"),
        ("run_pages.sh", "the ROLES anchor is not checked", '    if src.count(ANCHOR) != 1:', '    if False:'),
        ("run_pages.sh", "committed inputs are not checked", "    if bad:\n        die(\"not committed", "    if False:\n        die(\"not committed"),
        ("run_pages.sh", "the 9cc6667 list is not checked", "    if sha(f\"{SW}/floor_7c/d_first/{DNAME}.txt\") != D_FIRST_SHA:", "    if False:"),
        ("run_pages.sh", "a stop is not logged", "PAGES STOPPED in $stage", "pages in $stage"),
        ("run_pages.sh", "the DECKGYM check is gone", "if [ -n \"$(env | grep -E '^DECKGYM_' || true)\" ]; then", "if false; then"),
        ("run_pages.sh", "the clock is ignored", "-ge 1015", "-ge 3000"),
        ("run_pages.sh", "launch_detached is not required", 'if [ "$dry" = 0 ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ]; then', "if false; then"),
        ("run_pages.sh", "the plan commit is not checked", 'elif ! git diff --quiet HEAD -- "$D/$f"; then', "elif false; then"),
        ("run_pages.sh", "a dry run before the pin fails", '"not rules switch 2\'s"', '"never matches"'),
        ("run_pages.sh", "Victini's caveat is not replaced", "    cells[2] = new_why\n", "    cells[2] = old_why\n"),
        ("run_pages.sh", "no note beside a page", "OLD_PAGE.txt\"), \"w\"", "OLD_PAGE.tx\"), \"w\""),
    ]
    results, survived = [], []

    def one(m):
        fname, what, old, new = m
        src = open(os.path.join(HERE, fname), encoding="utf-8").read()
        assert src.count(old) == 1, f"mutation {what!r}: {old!r} occurs {src.count(old)} times"
        tmp = tempfile.mkdtemp(prefix="fr_mut_")
        for n in ("run_check.sh", "run_pages.sh"):
            shutil.copy(os.path.join(HERE, n), tmp)
        open(os.path.join(tmp, fname), "w", encoding="utf-8").write(src.replace(old, new))
        env = dict(os.environ, RUNNER_DIR=tmp, PYTHONWARNINGS="ignore")
        p = subprocess.run([sys.executable, "-m", "unittest", "-f", "test_runners"], cwd=HERE, env=env, capture_output=True, text=True)
        shutil.rmtree(tmp, True)
        failed = re.findall(r"^(?:FAIL|ERROR): (\S+) \(([\w.]+)\)", p.stderr, flags=re.M)
        first = f"{failed[0][1].split('.')[-2]}.{failed[0][0]}" if failed else None
        print(f"{'KILLED  ' if first else 'SURVIVED'} {fname}: {what} -> {first}", flush=True)
        return fname, what, first

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=int(os.environ.get("MUT_WORKERS", "6"))) as ex:
        results = list(ex.map(one, M))
    survived = [w for _, w, first in results if not first]
    print(f"\n{len(results) - len(survived)} of {len(results)} broken runners failed a test")
    return 1 if survived else 0


if __name__ == "__main__":
    if "--mutations" in sys.argv:
        sys.exit(mutations())
    unittest.main()
