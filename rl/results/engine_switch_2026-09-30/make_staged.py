"""Step 10 of the Sept 30 engine switch, prepared as copies: the screen and floor default pilot kog3 -> km3, and
floor.py's pricing-pilot pattern fixed to match every code B builds as PublicPricingPlayer (and not k3).

Writes staged/decks/screen/floor.py and staged/decks/screen/run_screen.py from the working copy's current files by
exact text replacements (each old text must occur exactly once), and staged/BASE.sha256 with the sha256 of the files
they were made from. pin.sh installs the staged copies only if the working copy still has those exact files; if
floor.py or run_screen.py changed in between, re-run this and re-review staged/staged.patch.
The test (staged/decks/screen/test_floor_pricing_pilot.py) is written by hand, not generated.
Last, staged/STAGED.sha256 records the three staged files and staged.patch as they are now (the reviewed copies):
pin.sh installs only files that still match it, so an edit to staged/ after the review stops the pin until this is
re-run and staged/staged.patch re-reviewed.

Usage (WSL, from anywhere): python3 make_staged.py   (also writes staged/staged.patch, the diff to review)
"""
import difflib, hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
STAGED = os.path.join(HERE, "staged")

PATTERN = r"k(?:p|q|d|pr|pf|pg|ph|pha|phb|oa|ob|or|og|oh|t|ta|tb|tc|m)\d+"

FLOOR = [
    ("    python3 decks/screen/floor.py DECK.txt --out DIR [--games 240] [--pilot kog3] [--meta-pilot kog3]\n",
     "    python3 decks/screen/floor.py DECK.txt --out DIR [--games 240] [--pilot km3] [--meta-pilot km3]\n"),
    ("A floor verdict needs all of: 240 games per matchup, the working pilot on both sides (kog3 since the Sept 28 engine\n"
     "switch, kp3 before it; re-checked in rl/results/floor_recheck_2026-09-28/), the opponents in decks/screen/opponents/, and\n"
     "the coverage from the official release's goldfish (project_manifest.json available_release, hash checked). Any other\n",
     "A floor verdict needs all of: 240 games per matchup, the working pilot on both sides (km3 since the Sept 30 engine\n"
     "switch, kog3 from Sept 28, kp3 before; re-checked in rl/results/floor_recheck_2026-09-30/), the opponents in\n"
     "decks/screen/opponents/, and the coverage from the official release's goldfish (project_manifest.json\n"
     "available_release, hash checked). Any other\n"),
    ("  incomplete engine status or a named limitation; a text the pilot leaves unpriced (the opponent-hand/deck text rule;\n"
     "  for a public-pricing pilot, kp/kq/kd, texts in kp's 62 audited texts are priced and drop out); an attack k's damage\n"
     "  estimate prices at printed damage; an effect that pays off during the opponent's turn, which the search doesn't\n",
     "  incomplete engine status or a named limitation; a text the pilot leaves unpriced (the opponent-hand/deck text rule;\n"
     "  for a public-pricing pilot, any code PRICING_PILOT matches (kp3 ... km3, not k3), texts in kp's 62 audited texts\n"
     "  are priced and drop out); an attack k's damage estimate prices at printed damage; an effect that pays off during\n"
     "  the opponent's turn, which the search doesn't\n"),
    ('FLOOR_PILOT = "kog3"   # the working pilot (Sept 28 engine switch; kp3 before)\n',
     'FLOOR_PILOT = "km3"   # the working pilot (Sept 30 engine switch; kog3 from Sept 28, kp3 before)\n'),
    ('PRICING_PILOT = re.compile(r"k(?:[pqd]|og)\\d+")   # codes built as PublicPricingPlayer (players/mod.rs); kog added Sept 28\n',
     "# Every code players/mod.rs get_player builds as PublicPricingPlayer, and not k<N> (Sept 30 engine switch; the old\n"
     "# pattern k(?:[pqd]|og) missed kpr, koa, kob, kor, kpf, kpg, koh, kph, kpha, kphb, kt, kta, ktb, ktc and km). The list\n"
     "# and a check against mod.rs are in test_floor_pricing_pilot.py; self_check() asserts the floor's own pilot matches.\n"
     f'PRICING_PILOT = re.compile(r"{PATTERN}")\n'),
    ('    print("self-check passed: edges 349/350/418/419 (n 1,920) and 78/79/113/114 (n 480); untrusted rule; Supporter turns")\n',
     "    # the floor's pilot must get kp's audited texts (a pattern that misses it flags priced cards and can read 'untrusted')\n"
     '    assert PRICING_PILOT.fullmatch(FLOOR_PILOT) and not PRICING_PILOT.fullmatch("k3"), FLOOR_PILOT\n'
     '    print("self-check passed: edges 349/350/418/419 (n 1,920) and 78/79/113/114 (n 480); untrusted rule; Supporter turns")\n'),
]

SCREEN = [
    ("usage: run_screen.py DECK.txt [DECK2.txt ...] [--engine PATH/TO/deckgym] [--pilot kog3] [--meta-pilot kog3]\n",
     "usage: run_screen.py DECK.txt [DECK2.txt ...] [--engine PATH/TO/deckgym] [--pilot km3] [--meta-pilot km3]\n"),
    ("refuses a binary whose hash differs). Pilots: kog3 on both sides by default, the working pilot since the Sept 28\n"
     "engine switch (kp3 before it, from the plan revised Sept 25); --pilot kp3 --meta-pilot kp3 reproduces the Sept 25-27\n"
     "screen, and --pilot k3 --meta-pilot k3 the Sept 24 one.\n",
     "refuses a binary whose hash differs). Pilots: km3 on both sides by default, the working pilot since the Sept 30\n"
     "engine switch (kog3 from Sept 28, kp3 before it, from the plan revised Sept 25); --pilot kog3 --meta-pilot kog3\n"
     "reproduces the Sept 28-30 screen, --pilot kp3 --meta-pilot kp3 the Sept 25-27 one, and --pilot k3 --meta-pilot k3\n"
     "the Sept 24 one. Since Sept 30, kt3, kta3, ktb3 and ktc3 in the official engine are the kog-based presets (kta3 is\n"
     "the adopted one; kt3, ktb3 and ktc3 are diagnostic); the older kp-based ones are only in rl/engine-2026-09-28/.\n"),
    ("ap.add_argument('--pilot', default='kog3', help=\"the screened deck's bot (default kog3)\")\n"
     "ap.add_argument('--meta-pilot', default='kog3', help=\"the panel decks' bot (default kog3)\")\n",
     "ap.add_argument('--pilot', default='km3', help=\"the screened deck's bot (default km3)\")\n"
     "ap.add_argument('--meta-pilot', default='km3', help=\"the panel decks' bot (default km3)\")\n"),
]


def stage(rel, edits):
    src = os.path.join(ROOT, rel)
    raw = open(src, "rb").read()
    assert b"\r\n" not in raw, f"{rel} has CRLF line endings; the edits assume LF"
    text = raw.decode("utf-8")
    for old, new in edits:
        n = text.count(old)
        assert n == 1, f"{rel}: expected the old text exactly once, found {n}:\n{old}"
        text = text.replace(old, new)
    dst = os.path.join(STAGED, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "wb").write(text.encode("utf-8"))
    return hashlib.sha256(raw).hexdigest()


base = {rel: stage(rel, edits) for rel, edits in (("decks/screen/floor.py", FLOOR), ("decks/screen/run_screen.py", SCREEN))}
with open(os.path.join(STAGED, "BASE.sha256"), "w", encoding="utf-8", newline="\n") as f:
    for rel, h in base.items():
        f.write(f"{h}  {rel}\n")
# the review diff: the working copy's files -> the staged copies, and the new test
diff = []
for rel in (*base, "decks/screen/test_floor_pricing_pilot.py"):
    cur = os.path.join(ROOT, rel)
    a = open(cur, encoding="utf-8").read().splitlines(True) if os.path.exists(cur) else []
    b = open(os.path.join(STAGED, rel), encoding="utf-8").read().splitlines(True)
    diff += difflib.unified_diff(a, b, f"a/{rel}" if a else "/dev/null", f"b/{rel}", n=3)
open(os.path.join(STAGED, "staged.patch"), "w", encoding="utf-8", newline="\n").write("".join(diff))
# the reviewed copies: pin.sh checks every staged file (and the patch) against this before it installs anything
with open(os.path.join(STAGED, "STAGED.sha256"), "w", encoding="utf-8", newline="\n") as f:
    for rel in (*base, "decks/screen/test_floor_pricing_pilot.py", "staged.patch"):
        f.write(f"{hashlib.sha256(open(os.path.join(STAGED, rel), 'rb').read()).hexdigest()}  {rel}\n")
print("staged:", ", ".join(base), "->", STAGED, "; review diff: staged/staged.patch; record: staged/STAGED.sha256")
