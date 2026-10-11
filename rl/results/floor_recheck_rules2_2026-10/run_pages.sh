#!/usr/bin/env bash
# The new floor pages after rules switch 2 (PLAN.md here, "Part B"; the switch's PLAN.md step 15). Part B.
# Refuses unless Part A's verdicts.txt starts "RESULT PASSED". Writes only in pages/ here. Start it through
# rl/strength/launch_detached.sh:
#   launch_detached.sh start floor-pages2 -- bash rl/results/floor_recheck_rules2_2026-10/run_pages.sh
#   bash run_pages.sh --dry-run   every check that does not need the pin or Part A's result, and the plan; nothing written.
#   1. Deck 12, brew 07, brew 09: floor.py's own call with its defaults -> pages/12, pages/brew-07, pages/brew-09.
#   2. D_victini-passive: Oct 2's private copy rebuilt (today's floor.py + floor_copy.diff's one ROLES entry, the list path
#      changed to floor_7c/d_first/), run through run_copy.py -> pages/D_victini-passive; its games must equal Oct 2's.
#   3. D_root, D_amended: no games: 7c's replay page with the new engine named, Victini's row and the coverage file from
#      the new goldfish (--games 0 --coverage), and the one line the PLAN gives -> pages/D_root, pages/D_amended.
#   4. A note beside each page (OLD_PAGE.txt) naming its old page. No deck 10 page.
# Exit 0: done. Exit 1: stopped (an unexpected difference or failure: it goes to Dustin through the laptop session; the log
# says "PAGES STOPPED"). Exit 2: refused to start; nothing was written. Never rerun over existing outputs: move pages/ aside,
# named, first.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
MODE=run
case "${1:-}" in
  "") ;;
  --dry-run) MODE=dry ;;
  *) echo "usage: run_pages.sh [--dry-run]"; exit 2 ;;
esac
PG="$D/pages"; export PG
SW=rl/results/engine_switch_rules2_2026-10
F7=$SW/floor_7c
OLD2=rl/results/floor_drafts_2026-10-02
OLD30=rl/results/floor_dustin_2026-09-30
DFIRST=$F7/d_first/draft-D-entei-grimhound.txt
DAMEND=decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt
D12=decks/dustin/12-ariados-whimsicott-ogerpon.txt
B07=decks/brews/brew-07-hoopa-darkrai-sableye.txt
B09=decks/brews/brew-09-sableye-obstagoon.txt

# The Python helpers: one source, one subcommand per job (python3 -c "$PYSRC" CMD ARGS).
read -r -d '' PYSRC <<'PY' || true
import difflib, hashlib, importlib.util, json, os, re, subprocess, sys

NEW_GYM, NEW_GF = "rl/engine-2026-10-12/deckgym", "rl/engine-2026-10-12/goldfish"
NEW_GF_SHA = "d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84"
OLD_GYM, OLD_GF = "rl/engine-2026-10-02/deckgym", "rl/engine-2026-10-02/goldfish"
OLD_GF_SHA = "cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66"
D_FIRST_SHA = "4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585"
SW = "rl/results/engine_switch_rules2_2026-10"
OLD2 = "rl/results/floor_drafts_2026-10-02"
OLD30 = "rl/results/floor_dustin_2026-09-30"
DNAME = "draft-D-entei-grimhound"
# the PLAN's lists: page name -> (old page, expected change)
OLDPAGES = {
    "12": (f"{OLD30}/12-ariados-whimsicott-ogerpon.md",
           "expected to change in all 8 rows: each of its two Ariados now adds 1 to the Retreat Cost, which also feeds Grass Knot; "
           "judged through B2e's pairings 80-87 (step 9)"),
    "brew-07": (f"{OLD30}/brew-07-hoopa-darkrai-sableye.md",
                "may change where a panel attacker weak to Darkness hits a Mega Sableye ex in the turn after its Cursed Jewel (the hit "
                "back now takes Weakness); judged through step 8b's brew-07 v t-altaria row (pairing 36 of the 23,100,000,000 block). "
                "Brew 07's conclusions stay provisional until this page is read (Dustin, Oct 7)"),
    "brew-09": (f"{OLD30}/brew-09-sableye-obstagoon.md",
                "may change where a panel attacker weak to Darkness hits a Mega Sableye ex in the turn after its Cursed Jewel (the hit "
                "back now takes Weakness); judged through step 8b's brew-09 v t-altaria row (pairing 37 of the 23,100,000,000 block). "
                "Brew 09's conclusions stay provisional until this page is read (Dustin, Oct 7)"),
    "D_victini-passive": (f"{OLD2}/draft-D_victini-passive/{DNAME}.md",
                          "a reading for Dustin, not D's floor page: D's first list with Victini's role set to 'bench piece/passive "
                          "ability' (a proposed role, Dustin's to confirm). Expected: the same games as Oct 2's; only the engine "
                          "lines and Victini's caveat text change. A game that differs is a stop"),
    "D_root": (f"{OLD2}/{DNAME}.md",
               "text only, no games: step 7c's replay of D's first list, equal to Oct 2's page; only the engine lines and Victini's "
               "caveat text differ"),
    "D_amended": (f"{OLD2}/draft-D_amended/{DNAME}.md",
                  "text only, no games: step 7c's replay of D as amended at 9e139e6, equal to Oct 2's page; only the engine lines "
                  "and Victini's caveat text differ"),
}
D_LINE = ("> Games: step 7c's replays on the new engine, equal to Oct 2's, and no game was played for this page (the coordinator, "
          "Oct 11: draft D has no expected change, and the Victini caveat is text). Engine lines, Victini's row's caveat and "
          "the coverage file are the new engine's.")
COPY_NOTE = ("> **From a MODIFIED COPY of floor.py, not the committed one.** Victini's role on this page is \"bench piece/passive "
             "ability\": **proposed role, Dustin's to confirm**. The copy is today's `decks/screen/floor.py` plus one ROLES entry "
             "(`floor_copy.diff` here), naming the list by its path here, `%s`: the only difference from Oct 2's copy. Same games "
             "as Oct 2's page (`%s/draft-D_victini-passive/`), checked game for game; this page is a reading for Dustin, not D's "
             "floor page.")


def die(msg):
    print("STOP: " + msg)
    sys.exit(1)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def git(*a):
    p = subprocess.run(["git", *a], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def committed(path):          # the file on disk is HEAD's blob
    rc, want = git("rev-parse", "--verify", "--quiet", f"HEAD:{path}")
    return rc == 0 and os.path.isfile(path) and git("hash-object", "--", path)[1] == want


def read(path):
    return open(path, encoding="utf-8").read()


def page_facts(path):
    t = read(path)
    m = re.search(r"\*\*Verdict: (.+?)\.\*\* (\d+) wins in (\d+) games", t)
    pil = re.search(r"Pilots: (\S+) on the deck, (\S+) on the panel", t)
    eng = re.search(r"^- Engine: (\S+)", t, flags=re.M)
    if not (m and pil and eng):
        die(f"{path} does not read as a floor page")
    return dict(verdict=m[1], wins=int(m[2]), n=int(m[3]), pilots=pil.groups(), engine=eng[1])


def swap_once(text, old, new, what):
    if text.count(old) != 1:
        die(f"{what}: the text {old[:70]!r} occurs {text.count(old)} times, not once")
    return text.replace(old, new)


def strip_leading_note(text):
    lines = text.split("\n")
    i = 0
    while i < len(lines) and lines[i].startswith(">"):
        i += 1
    if i and lines[i] == "":
        i += 1
    return "\n".join(lines[i:])


def mask_victini(text):       # the "why flagged" cell of Victini's row (the caveat text), the only cell that may differ
    out, n = [], 0
    for line in text.split("\n"):
        if line.startswith("| Victini ("):
            cells = line.split(" | ")
            if len(cells) != 6:
                die(f"Victini's row does not have 6 cells: {line[:100]!r}")
            cells[2] = "<caveat>"
            line, n = " | ".join(cells), n + 1
        out.append(line)
    if n != 1:
        die(f"{n} Victini rows, not 1")
    return "\n".join(out)


def first_diff(a, b):
    la, lb = a.split("\n"), b.split("\n")
    d = [i for i in range(max(len(la), len(lb))) if (la[i] if i < len(la) else None) != (lb[i] if i < len(lb) else None)]
    if not d:
        return None
    i = d[0]
    return (f"{len(d)} line(s) differ (line {', '.join(str(j + 1) for j in d[:10])}); line {i + 1} now: "
            f"{(la[i] if i < len(la) else '(none)')[:160]!r}; Oct 2's, engine lines put in: {(lb[i] if i < len(lb) else '(none)')[:160]!r}")


def compare_page(new_md, old_md):
    """New page v Oct 2's: only the two engine lines and Victini's caveat may differ."""
    new = strip_leading_note(read(new_md))
    old = strip_leading_note(read(old_md))
    old = swap_once(old, f"\n- Engine: {OLD_GYM} (", f"\n- Engine: {NEW_GYM} (", "Oct 2's page")
    old = swap_once(old, f"\n- Coverage from {OLD_GF} (sha256 {OLD_GF_SHA}; ",
                    f"\n- Coverage from {NEW_GF} (sha256 {NEW_GF_SHA}; ", "Oct 2's page")
    d = first_diff(mask_victini(new), mask_victini(old))
    if d:
        die(f"{new_md} v {old_md}: {d}")
    return "equal but for the engine lines and Victini's caveat"


def compare_games(new, old):
    if open(new, "rb").read() != open(old, "rb").read():
        a, b = read(new).split("\n"), read(old).split("\n")
        d = [i + 1 for i in range(min(len(a), len(b))) if a[i] != b[i]]
        die(f"{new} differs from {old}: {len(d)} differing game(s) (first lines {d[:10]}), lengths {len(a)} v {len(b)}: "
            "a game that differs goes to Dustin")
    return "byte-equal"


def compare_coverage(new, old):
    """Byte-equal, or equal but for Victini's entries (the card-status text the switch changed)."""
    if open(new, "rb").read() == open(old, "rb").read():
        return "byte-equal"
    a, b = json.load(open(new, encoding="utf-8")), json.load(open(old, encoding="utf-8"))
    if sorted(a) != sorted(b):
        die(f"{new}: the cards covered differ from {old}'s")
    diff = [k for k in a if a[k] != b[k]]
    other = [k for k in diff if a[k].get("name") != "Victini" or b[k].get("name") != "Victini"]
    if other:
        die(f"{new} v {old}: entries other than Victini's differ: {other}")
    return f"equal but for Victini's entries {diff}"


def load_floor(root):
    spec = importlib.util.spec_from_file_location("floor_mod", os.path.join(root, "decks/screen/floor.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_refcheck(_):
    """The files Part B reads are the committed ones."""
    need = ([f"{OLD2}/{DNAME}.md", f"{OLD2}/{DNAME}_coverage.json", f"{OLD2}/{DNAME}_games.jsonl"]
            + [f"{OLD2}/draft-D_amended/{DNAME}{x}" for x in (".md", "_coverage.json", "_games.jsonl")]
            + [f"{OLD2}/draft-D_victini-passive/{x}" for x in
               (f"{DNAME}.md", f"{DNAME}_coverage.json", f"{DNAME}_games.jsonl", "floor_copy.diff", "run_copy.py")]
            + [f"{SW}/floor_7c/{d}/{DNAME}{x}" for d in ("D_root", "D_amended") for x in (".md", "_coverage.json", "_games.jsonl")]
            + [f"{SW}/floor_7c/d_first/{DNAME}.txt", "decks/screen/floor.py", "decks/brews/drafts_2026-10-01/" + DNAME + ".txt"]
            + [p for p, _ in OLDPAGES.values() if "floor_dustin" in p])
    bad = [p for p in need if not committed(p)]
    if bad:
        die("not committed as they are on disk: " + ", ".join(bad))
    if sha(f"{SW}/floor_7c/d_first/{DNAME}.txt") != D_FIRST_SHA:
        die(f"d_first's list is not the 9cc6667 blob (sha256 {D_FIRST_SHA[:8]}...)")
    for p in ("decks/dustin/12-ariados-whimsicott-ogerpon.txt", "decks/brews/brew-07-hoopa-darkrai-sableye.txt",
              "decks/brews/brew-09-sableye-obstagoon.txt"):
        if not os.path.isfile(p):
            die(f"missing {p}")
    src = read("decks/screen/floor.py")
    if src.count(ANCHOR) != 1:
        die("floor.py's ROLES table no longer ends as Oct 2's copy's diff expects; the copy can't be rebuilt as it was")
    print(f"Part B's inputs are the committed files; floor.py sha256 {sha('decks/screen/floor.py')[:16]}")


ANCHOR = '"Pyukumuku": "bench piece/passive ability", "Rocky Helmet": "Trainer (played)"},\n}\n'


def cmd_mkcopy(a):
    """Today's floor.py plus Oct 2's one ROLES entry with the list path changed; checked against Oct 2's diff."""
    out, listpath = a
    src = read("decks/screen/floor.py")
    entry = f'    "{listpath}": {{"Victini": "bench piece/passive ability"}},\n'
    new = swap_once(src, ANCHOR, ANCHOR.replace("\n}\n", "\n") + entry + "}\n", "floor.py")
    open(out, "w", encoding="utf-8", newline="\n").write(new)
    # the copy differs from floor.py by exactly that one line, and that line is Oct 2's with the path changed
    added = [l for l in difflib.unified_diff(src.split("\n"), new.split("\n"), lineterm="", n=0)
             if l and l[0] in "+-" and l[:3] not in ("+++", "---")]
    old_added = [l for l in read(f"{OLD2}/draft-D_victini-passive/floor_copy.diff").split("\n")
                 if l and l[0] in "+-" and l[:3] not in ("+++", "---")]
    old_path = "decks/brews/drafts_2026-10-01/" + DNAME + ".txt"
    want = [l.replace(old_path, listpath) for l in old_added]
    if added != want:
        die(f"the rebuilt copy's diff {added} is not Oct 2's {old_added} with the path changed")
    print(f"copy {out} sha256 {sha(out)[:16]}: today's floor.py plus the one ROLES entry for {listpath} (Oct 2's, path changed)")


def cmd_checkpage(a):
    name, md = a
    f = page_facts(md)
    if f["engine"] != NEW_GYM:
        die(f"{md} names engine {f['engine']}, not {NEW_GYM}")
    if f["pilots"] != ("km3", "km3") or f["n"] != 1920 or f["verdict"].startswith(("control reading", "no verdict")):
        die(f"{md} is not a floor page (verdict {f['verdict']!r}, pilots {f['pilots']}, n {f['n']})")
    print(f"{name}: {f['verdict']}, {f['wins']} of {f['n']}")


def cmd_cmpvictini(a):
    new_dir, listpath = a
    o = f"{OLD2}/draft-D_victini-passive"
    r = [("page", compare_page(f"{new_dir}/{DNAME}.md", f"{o}/{DNAME}.md")),
         ("games", compare_games(f"{new_dir}/{DNAME}_games.jsonl", f"{o}/{DNAME}_games.jsonl")),
         ("coverage", compare_coverage(f"{new_dir}/{DNAME}_coverage.json", f"{o}/{DNAME}_coverage.json"))]
    print("D_victini-passive v Oct 2's: " + "; ".join(f"{k} {v}" for k, v in r))
    # the page names it as a modified copy, as Oct 2's did
    text = read(f"{new_dir}/{DNAME}.md")
    open(f"{new_dir}/{DNAME}.md", "w", encoding="utf-8", newline="\n").write(COPY_NOTE % (listpath, OLD2) + "\n\n" + text)


def cmd_dtext(a):
    name, replay, oldref, deck, goldfish = a
    out = os.path.join(os.environ["PG"], name)
    os.makedirs(out, exist_ok=True)
    if sha(goldfish) != NEW_GF_SHA:
        die(f"{goldfish} is not the new goldfish (sha256 {NEW_GF_SHA[:8]}...)")
    cov_new = f"{out}/{DNAME}_coverage.json"
    subprocess.run([os.path.abspath(goldfish), "--deck", os.path.abspath(deck), "--panel", os.path.abspath("decks/screen/opponents"),
                    "--games", "0", "--coverage", os.path.abspath(cov_new)], check=True, capture_output=True, cwd="engine")
    fl = load_floor(".")
    db = fl.database()
    old_cov = json.load(open(f"{replay}/{DNAME}_coverage.json", encoding="utf-8"))
    new_cov = json.load(open(cov_new, encoding="utf-8"))
    fo, fn = fl.flagged_cards(old_cov, "km3", db), fl.flagged_cards(new_cov, "km3", db)
    if sorted(fo) != sorted(fn):
        die(f"{name}: the flagged cards differ: replay {sorted(fo)}, new goldfish {sorted(fn)}")
    for c in fo:
        if c != "Victini" and (fo[c]["reasons"] != fn[c]["reasons"] or fo[c]["ids"] != fn[c]["ids"]):
            die(f"{name}: flagged card {c}'s reasons differ between the replay's coverage and the new goldfish's")
    if "Victini" not in fo or fo["Victini"]["ids"] != fn["Victini"]["ids"]:
        die(f"{name}: Victini is not flagged under the same printings")
    old_why, new_why = "; ".join(fo["Victini"]["reasons"]), "; ".join(fn["Victini"]["reasons"])
    text = read(f"{replay}/{DNAME}.md")
    eng = r"\n- Engine: \S+ \(the manifest's available release\)"
    if len(re.findall(eng, text)) != 1:
        die(f"{name}: the replay page does not hold exactly one engine line")
    text = re.sub(eng, lambda m: f"\n- Engine: {NEW_GYM} (the manifest's available release)", text, count=1)
    text = swap_once(text, f"\n- Coverage from {OLD_GF} (sha256 {OLD_GF_SHA}; ", f"\n- Coverage from {NEW_GF} (sha256 {NEW_GF_SHA}; ",
                     f"{name}'s replay page")
    rows = [i for i, l in enumerate(text.split("\n")) if l.startswith("| Victini (")]
    if len(rows) != 1:
        die(f"{name}: {len(rows)} Victini rows in the replay page")
    lines = text.split("\n")
    cells = lines[rows[0]].split(" | ")
    if len(cells) != 6 or cells[2] != old_why:
        die(f"{name}: Victini's caveat cell in the replay page is not the old coverage's text")
    cells[2] = new_why
    lines[rows[0]] = " | ".join(cells)
    new_md = f"{out}/{DNAME}.md"
    open(new_md, "w", encoding="utf-8", newline="\n").write(D_LINE + "\n\n" + "\n".join(lines))
    games = f"{out}/{DNAME}_games.jsonl"
    open(games, "wb").write(open(f"{replay}/{DNAME}_games.jsonl", "rb").read())
    r = [("page", compare_page(new_md, oldref + f"/{DNAME}.md")), ("games", compare_games(games, oldref + f"/{DNAME}_games.jsonl")),
         ("coverage", compare_coverage(cov_new, oldref + f"/{DNAME}_coverage.json"))]
    print(f"{name} v Oct 2's: " + "; ".join(f"{k} {v}" for k, v in r) + f"; Victini's caveat now: {new_why[:120]}...")


def cmd_note(a):
    name, md = a
    old, expect = OLDPAGES[name]
    o, n = page_facts(old), page_facts(md)
    text = (f"New page: rl/results/floor_recheck_rules2_2026-10/pages/{name}/{os.path.basename(md)}\n"
            f"Old page: {old}\n"
            f"Old: {o['verdict']}, {o['wins']} of {o['n']} (engine {o['engine']}).\n"
            f"New: {n['verdict']}, {n['wins']} of {n['n']} (engine {n['engine']}).\n"
            f"What the PLAN expects: {expect}.\n"
            "Each new page goes to Dustin beside its old one; a new failure or judgment call stops and goes to him. A page's "
            "changed games are not checked one by one (floor.py has no watch build).\n")
    open(os.path.join(os.path.dirname(md), "OLD_PAGE.txt"), "w", encoding="utf-8", newline="\n").write(text)
    print(f"{name}: was {o['verdict']} {o['wins']}/{o['n']}, now {n['verdict']} {n['wins']}/{n['n']}")


globals()["cmd_" + sys.argv[1]](sys.argv[2:])
PY
py() { python3 -c "$PYSRC" "$@"; }

prechecks() {
  local hm f dry=0 bad="" pinbad="" rc=0
  [ "$MODE" = dry ] && dry=1
  hm=$(date -u +%H%M) || { echo "REFUSED: cannot read the clock"; return 2; }
  if [ "${ALLOW_DAYTIME:-0}" != 1 ] && [ $((10#$hm)) -ge 1015 ] && [ $((10#$hm)) -lt 2200 ]; then
    local tb="it is ${hm:0:2}:${hm:2:2} UTC, between 5:15 am and 5 pm Central: the laptop leaves at 7 am (ALLOW_DAYTIME=1 on a day Dustin is home)"
    if [ "$dry" = 1 ]; then echo "note: a real run would refuse now: $tb"; else bad+="$tb"$'\n'; fi
  fi
  if [ "$dry" = 0 ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ]; then
    bad+="not started through rl/strength/launch_detached.sh (it outlives the session that starts it)"$'\n'
  fi
  if [ -n "$(env | grep -E '^DECKGYM_' || true)" ]; then
    bad+="a DECKGYM_* variable is set: no DECKGYM_* variable is ever set for a floor run"$'\n'
  fi
  for f in PLAN.md run_check.sh run_pages.sh; do
    if ! git ls-files --error-unmatch -- "$D/$f" > /dev/null 2>&1; then
      pinbad+="$f is not committed: the plan and both runners come before any game (they are committed with the pin)"$'\n'
    elif ! git diff --quiet HEAD -- "$D/$f"; then
      pinbad+="$f differs from its commit"$'\n'
    fi
  done
  if [ -e "$PG" ]; then bad+="pages/ from an earlier run is here; move it aside, named, first"$'\n'; fi
  if [ -f "$D/verdicts.txt" ]; then
    case "$(head -n 1 "$D/verdicts.txt")" in
      "RESULT PASSED"*) ;;
      *) pinbad+="Part A's verdicts.txt does not start \"RESULT PASSED\""$'\n' ;;
    esac
  else
    pinbad+="Part A's verdicts.txt is not here: run_check.sh comes first and must pass"$'\n'
  fi
  local eo; eo=$(bash "$D/run_check.sh" --engine-check 2>&1) || rc=$?
  printf '%s\n' "$eo"
  if [ "$rc" != 0 ]; then
    if [ "$dry" = 1 ] && printf '%s' "$eo" | grep -q "not rules switch 2's"; then
      pinbad+="the engine is not pinned yet (the engine checks above)"$'\n'
    else
      bad+="the engine checks did not pass (above)"$'\n'
    fi
  fi
  py refcheck || bad+="Part B's inputs are not as committed (above)"$'\n'
  if [ "$dry" = 1 ]; then
    if [ -n "$bad" ]; then printf '%s' "$bad" | sed 's/^/REFUSED: /'; return 2; fi
    if [ -n "$pinbad" ]; then printf '%s' "$pinbad" | sed 's/^/BEFORE THE PIN OR PART A: a real run would refuse: /'; fi
    return 0
  fi
  if [ -n "$bad$pinbad" ]; then printf '%s' "$bad$pinbad" | sed 's/^/REFUSED: /'; return 2; fi
  return 0
}

t() { local tag=$1 s; shift; stage=$tag; s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$PG/timing.txt"; }

page() {      # page NAME DECK: floor.py's own call with its defaults
  local name=$1 deck=$2 stem
  stem=$(basename "$deck" .txt)
  t "$name" python3 decks/screen/floor.py "$deck" --out "$PG/$name"
  py checkpage "$name" "$PG/$name/$stem.md"
  py note "$name" "$PG/$name/$stem.md"
}

run() {
  stage=start
  trap 'rc=$?; if [ $rc != 0 ] && [ -n "$stage" ]; then echo "$(date -u +%FT%TZ) PAGES STOPPED in $stage: exit code $rc (an unexpected difference, failure or program stop: it goes to Dustin through the laptop session; move pages/ aside, named, before any rerun)"; fi' EXIT
  mkdir -p "$PG"
  echo "$(date -u +%FT%TZ) PAGES START: run_pages.sh $(sha256sum "$D/run_pages.sh" | cut -c1-16), PLAN.md $(sha256sum "$D/PLAN.md" | cut -c1-16) (sha256; HEAD $(git rev-parse --short HEAD)); Part A: $(head -n 1 "$D/verdicts.txt" | cut -c1-80)"
  printf '%s\n' "$PRE"
  page 12 "$D12"
  page brew-07 "$B07"
  page brew-09 "$B09"
  # draft D's victini-passive page, remade as on Oct 2: a private copy (today's floor.py + the one ROLES entry), run through run_copy.py
  stage=D_victini-passive
  mkdir -p "$PG/D_victini-passive"
  py mkcopy "$PG/D_victini-passive/floor_victini_passive.py" "$DFIRST"
  diff -u decks/screen/floor.py "$PG/D_victini-passive/floor_victini_passive.py" > "$PG/D_victini-passive/floor_copy.diff" || true
  cp "$OLD2/draft-D_victini-passive/run_copy.py" "$PG/D_victini-passive/run_copy.py"
  t D_victini-passive python3 "$PG/D_victini-passive/run_copy.py" "$PG/D_victini-passive/floor_victini_passive.py" \
    "$R/decks/screen/floor.py" "$DFIRST" --out "$PG/D_victini-passive"
  py checkpage D_victini-passive "$PG/D_victini-passive/draft-D-entei-grimhound.md"
  py cmpvictini "$PG/D_victini-passive" "$DFIRST"
  py note D_victini-passive "$PG/D_victini-passive/draft-D-entei-grimhound.md"
  # D's root and amended pages: text, no games
  GF=$(python3 -c "import json;print(json.load(open('project_manifest.json'))['available_release']['goldfish'])")
  stage=D_root; py dtext D_root "$F7/D_root" "$OLD2" "$DFIRST" "$GF"
  py note D_root "$PG/D_root/draft-D-entei-grimhound.md"
  stage=D_amended; py dtext D_amended "$F7/D_amended" "$OLD2/draft-D_amended" "$DAMEND" "$GF"
  py note D_amended "$PG/D_amended/draft-D-entei-grimhound.md"
  stage=
  echo "$(date -u +%F\ %T) PAGES DONE: 6 pages in pages/ (12, brew-07, brew-09, D_victini-passive, D_root, D_amended), each with OLD_PAGE.txt; no deck 10 page"
}

PRE=$(prechecks 2>&1) && prc=0 || prc=$?
if [ "$MODE" = dry ]; then
  printf '%s\n' "$PRE"
  [ "$prc" = 0 ] || exit 2
  echo "PLAN (dry run, nothing written): after Part A's RESULT PASSED, floor.py's own call (km3, 240 games per matchup, seed 7,100)" \
       "on deck 12, brew 07 and brew 09 (pages/12, brew-07, brew-09); Oct 2's private copy of floor.py rebuilt for D's first list" \
       "($DFIRST) and run through run_copy.py, its games compared byte for byte with Oct 2's (pages/D_victini-passive);" \
       "D_root and D_amended from 7c's replays plus the new goldfish's coverage (no games); an OLD_PAGE.txt beside each; no deck 10 page."
  exit 0
fi
if [ "$prc" != 0 ]; then printf '%s\n' "$PRE"; exit 2; fi
mkdir -p "$PG"
run 2>&1 | tee -a "$PG/run_pages.log"
