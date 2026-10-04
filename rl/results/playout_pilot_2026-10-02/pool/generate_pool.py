"""The play-out pilot's candidate pools (round 4, Oct 4; Fable via Dustin): regenerates the two embedded constants of
engine/src/players/playout_pool.rs and writes pool_manifest.tsv beside this script.

- META (the pool since Oct 2; `_poolmeta`): decks/screen/opponents/t-*.txt and decks/research/*.txt.
- WIDE (`_poolwide`, the default from round 4): META plus every other list under decks/ except Dustin's own
  (decks/dustin) and the brews and drafts (decks/brews, drafts included), plus the six B2e held-out tournament lists
  (rl/results/b2e_card_check_2026-09-26/decks/h-*.txt), which Fable named.
- A file is a list if every non-empty line is a header (Energy:, Pokémon:, Trainer:) or a card line "N Name SET NUM" or
  "N SET NUM", and the counts add up to 20. Goldfish outputs and check files are not lists.
- The wide pool's additions are refused by content as well as by path: any list holding the same cards (a multiset of
  card ids) as a list under decks/brews or decks/dustin, as KX_EXTRA_LISTS refuses one. The 16 META files are kept as
  they have been since Oct 2 (the panel; t-blaziken holds the same cards as decks/dustin/06-mega-blaziken-tournament-list,
  the public tournament list Dustin also owns), and the manifest says so.
Each entry carries its file's sha256. Run from the repository root: python3 rl/results/playout_pilot_2026-10-02/pool/generate_pool.py
"""
import hashlib, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
OUT_RS = ROOT / "engine/src/players/playout_pool.rs"
MANIFEST = Path(__file__).resolve().parent / "pool_manifest.tsv"
CARD = re.compile(r"^(\d+)\s+(?:(.+?)\s+)?(\S+)\s+(\S+)$")
HEADER = ("Energy:", "Pokémon:", "Trainer:")


def read_list(path):
    """(card-id multiset, energy line) if the file is a 20-card list, else None."""
    text = path.read_text(encoding="utf-8")
    ids, energy = Counter(), ""
    for line in text.splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("Energy:"):
            energy = t[len("Energy:"):].strip()
            continue
        if t.startswith(HEADER):
            continue
        m = CARD.match(t)
        if not m:
            return None
        ids[f"{m.group(3)} {m.group(4)}"] += int(m.group(1))
    return (ids, energy) if sum(ids.values()) == 20 else None


def rel(p):
    return p.relative_to(ROOT).as_posix()


protected = {}
for folder in ("decks/brews", "decks/dustin"):
    for p in sorted((ROOT / folder).rglob("*.txt")):
        r = read_list(p)
        if r:
            protected[rel(p)] = r[0]
if len(protected) < 10:
    sys.exit(f"only {len(protected)} protected lists found: run from the repository root")

meta_files = sorted((ROOT / "decks/screen/opponents").glob("t-*.txt")) + sorted((ROOT / "decks/research").glob("*.txt"))
wide_files = [
    p for p in sorted((ROOT / "decks").rglob("*.txt"))
    if not rel(p).startswith(("decks/brews/", "decks/dustin/")) and p not in meta_files
] + sorted((ROOT / "rl/results/b2e_card_check_2026-09-26/decks").glob("h-*.txt"))


def name_of(p):
    r = rel(p)
    if r.startswith("decks/screen/opponents/"):
        return p.stem
    if r.startswith("decks/research/"):
        return "research/" + p.stem
    return p.stem


rows, entries = [], {"META": [], "WIDE": []}
for group, files in (("META", meta_files), ("WIDE", wide_files)):
    for p in files:
        r = read_list(p)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if r is None:
            rows.append((name_of(p), rel(p), sha, group, "", "not a 20-card list"))
            continue
        copy_of = next((q for q, ids in protected.items() if ids == r[0]), None)
        if copy_of and group == "WIDE":
            rows.append((name_of(p), rel(p), sha, group, r[1], f"refused: the same cards as {copy_of}"))
            continue
        text = p.read_text(encoding="utf-8")
        assert '"#' not in text
        entries[group].append((name_of(p), rel(p), sha, text))
        rows.append((name_of(p), rel(p), sha, group, r[1], "in" + (f" (kept: the panel list; the same cards as {copy_of})" if copy_of else "")))

names = [e[0] for g in entries.values() for e in g]
assert len(names) == len(set(names)), "pool names must be unique"


def const(name, doc, items):
    body = "".join(f'    ("{n}", "{p}", "{s}", r#"{t}"#),\n' for n, p, s, t in items)
    return f"{doc}\npub const {name}: [(&str, &str, &str, &str); {len(items)}] = [\n{body}];\n"


rs = OUT_RS.read_text(encoding="utf-8")
start = rs.index("/// (name, source path, sha256 of the source file, the list text).\npub const POOL")
end = rs.index("\n];\n", rs.index("pub const WIDE") if "pub const WIDE" in rs else start) + len("\n];\n")
block = (
    const("POOL", "/// (name, source path, sha256 of the source file, the list text).", entries["META"])
    + "\n"
    + const(
        "WIDE",
        "/// The wide pool's other lists (round 4, `_poolwide`, the default): every list under decks/ but Dustin's own and the\n"
        "/// brews and drafts, and the six B2e held-out lists; generated by rl/results/playout_pilot_2026-10-02/pool/generate_pool.py.",
        entries["WIDE"],
    )
)
OUT_RS.write_text(rs[:start] + block + rs[end:], encoding="utf-8")
with open(MANIFEST, "w", encoding="utf-8") as f:
    f.write("name\tpath\tsha256\tpool\tenergy\tstatus\n")
    for row in rows:
        f.write("\t".join(row) + "\n")
print(f"META {len(entries['META'])} files, WIDE {len(entries['WIDE'])} more; not lists or refused: "
      f"{sum(1 for r in rows if r[5] != 'in')}")
for row in rows:
    if row[5] != "in":
        print("  ", row[1], "-", row[5])
