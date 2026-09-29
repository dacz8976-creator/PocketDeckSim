#!/usr/bin/env python3
"""kta's --pairs files (REGISTRATION.md 3.2 and its "Tool limit" bullet), written by run_kta.sh before any game.

legality_scan takes a new seed base only with --pairs (--decks has 72,000,000 fixed), and asserts that a file's
seed_first column equals base + pairing x 10,000. So every group is played from a --pairs file whose seed columns match
its base. Only the seed columns (seed_first, seed_last, sub_block_end) ever change; every other field is the source's.

  make_pairs.py table28 --base B --deals N --out F [--group table]
        the 28 table cells as a --pairs file: pairing p = the table's p-th (a, b), a < b, in the alphabetical order of
        legality_scan's NAMES; held_file / panel_file decks/research/<name>.txt (the lists --decks reads).
  make_pairs.py d --base B --deals N --out F [--group d] [--compare kt_tables_2026-09-28/d_rayquaza.tsv]
        clause (d): the census Rayquaza list v the eight panel lists (index 0-7, altaria to weezing), as kt's
        d_rayquaza.tsv, with seed_last = seed_first + N - 1.
  make_pairs.py rebase --src F --base B --deals N --out F2 [--group G] [--same-as-src]
        a copy of F with its seed columns moved to base B (every row kept; --pairings picks rows at play time).
  make_pairs.py list F [--side a|b] [--only 1,2,3]
        the file's pairing numbers (comma-separated), optionally only its variant_side rows / only those in --only.

--group checks every row's seeds, first to sub_block_end, lie in that group's fresh sub-block (3.2); --compare and
--same-as-src check the written file equals the given file field for field (the development files, so the identity
run proves this code writes the files the development games were played from). One line per file is printed.
"""
import argparse, sys

NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
HEADER = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last", "sub_block_end"]
RAYQUAZA = "rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt"
KTA_BLOCK = (23_000_000_000, 23_009_999_999)
# The fresh sub-blocks of REGISTRATION.md 3.2 (the A/B's and the traces' are used by kta_ab_play.py and run_kta.sh).
SUB = {
    "table": (23_000_000_000, 23_000_279_999),   # the 28 table cells; Lucario's, Suicune's, Weezing's second lists
    "new": (23_001_000_000, 23_001_249_999),     # Scizor rows (0-7) and the 17 new cells (8-24) of new_decks.tsv
    "b2e": (23_002_000_000, 23_002_959_999),     # B2e's 96 pairings; Charizard Y's second list (pairings 40-47)
    "d": (23_003_000_000, 23_003_079_999),       # clause (d), 8 rows x 2,000 deals (used to 23,003,071,999)
    "ab": (23_004_000_000, 23_004_999_999),      # the Dustin-deck A/B
    "trace": (23_005_000_000, 23_005_001_199),   # the Rayquaza traces, 200 games each at 23,005,000,000 and +1,000
}
_spans = sorted(SUB.values())
assert all(lo >= KTA_BLOCK[0] and hi <= KTA_BLOCK[1] for lo, hi in _spans), "a sub-block outside kta's block"
assert all(_spans[k][1] < _spans[k + 1][0] for k in range(len(_spans) - 1)), "two sub-blocks overlap"


def read_tsv(path):
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    header = [h.strip() for h in lines[0].split("\t")]
    rows = [[x.strip() for x in ln.split("\t")] for ln in lines[1:]]
    for r in rows:
        if len(r) < len(header):
            sys.exit(f"{path}: short row {r}")
    return header, rows


def reseed(header, rows, base, deals):
    c = {h: header.index(h) for h in ("pairing", "seed_first", "seed_last", "sub_block_end") if h in header}
    if "pairing" not in c or "seed_first" not in c:
        sys.exit("a --pairs file needs pairing and seed_first columns")
    out = []
    for r in rows:
        r = list(r)
        s = base + int(r[c["pairing"]]) * 10_000
        r[c["seed_first"]] = str(s)
        if "seed_last" in c:
            r[c["seed_last"]] = str(s + deals - 1)
        if "sub_block_end" in c:
            r[c["sub_block_end"]] = str(s + 9_999)
        out.append(r)
    return out


def write(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def check_group(path, header, rows, group, deals):
    lo, hi = SUB[group]
    ip, isf = header.index("pairing"), header.index("seed_first")
    for r in rows:
        first = int(r[isf])
        end = int(r[header.index("sub_block_end")]) if "sub_block_end" in header else first + 9_999
        if not (lo <= first and first + deals - 1 <= hi and end <= hi):
            sys.exit(f"{path}: pairing {r[ip]} seeds {first}-{end} leave the fresh sub-block {group} {lo}-{hi}")


def compare(path, header, rows, other):
    h2, r2 = read_tsv(other)
    if h2 != header or r2 != rows:
        diff = [k for k in range(min(len(rows), len(r2))) if rows[k] != r2[k]]
        sys.exit(f"{path} differs from {other}: header equal {h2 == header}, {len(rows)} v {len(r2)} rows, "
                 f"first differing row {diff[:1]}")
    return len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["table28", "d", "rebase", "list"])
    ap.add_argument("file", nargs="?", help="list: the --pairs file")
    ap.add_argument("--src")
    ap.add_argument("--base", type=int)
    ap.add_argument("--deals", type=int)
    ap.add_argument("--out")
    ap.add_argument("--group", choices=sorted(SUB))
    ap.add_argument("--compare")
    ap.add_argument("--same-as-src", action="store_true")
    ap.add_argument("--side", choices=["a", "b"])
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    if a.cmd == "list":
        header, rows = read_tsv(a.file)
        ps = [r[header.index("pairing")] for r in rows]
        if a.side:
            ps = [r[header.index("pairing")] for r in rows if r[header.index("variant_side")] == a.side]
        if a.only is not None:
            keep = set(x for x in a.only.split(",") if x)
            ps = [p for p in ps if p in keep]
        print(",".join(ps))
        return
    if a.base is None or a.deals is None or not a.out:
        sys.exit("--base, --deals and --out are needed")
    if not 1 <= a.deals <= 10_000:
        sys.exit("--deals must be 1 to 10,000 (one pairing's sub-block; legality_scan's --pairs limit)")
    if a.cmd == "table28":
        pairs = [(x, y) for i, x in enumerate(NAMES) for y in NAMES[i + 1:]]
        header = HEADER
        rows = [[str(p), "table", x, f"decks/research/{x}.txt", y, f"decks/research/{y}.txt", "0", "0", "0"]
                for p, (x, y) in enumerate(pairs)]
        what = "the 28 table cells (legality_scan's NAMES order)"
    elif a.cmd == "d":
        header = HEADER
        rows = [[str(p), "d", "c-rayquaza", RAYQUAZA, y, f"decks/research/{y}.txt", "0", "0", "0"] for p, y in enumerate(NAMES)]
        what = "clause (d): the census Rayquaza list v the 8 panel lists"
    else:
        header, src_rows = read_tsv(a.src)
        rows = src_rows
        what = f"a copy of {a.src}"
    new = reseed(header, rows, a.base, a.deals)
    if a.cmd == "rebase":
        seedcols = {header.index(h) for h in ("seed_first", "seed_last", "sub_block_end") if h in header}
        for r0, r1 in zip(rows, new):
            if any(r0[k] != r1[k] for k in range(len(r0)) if k not in seedcols):
                sys.exit("rebase changed a non-seed column")  # cannot happen; kept as the check the text promises
    write(a.out, header, new)
    msg = f"{a.out}: {what}, {len(new)} rows, seed base {a.base:,}, {a.deals} deals per pairing"
    if a.group:
        check_group(a.out, header, new, a.group, a.deals)
        msg += f"; inside the fresh sub-block {a.group} {SUB[a.group][0]:,}-{SUB[a.group][1]:,}"
    if a.same_as_src:
        msg += f"; equal to its source field for field ({compare(a.out, header, new, a.src)} rows)"
    if a.compare:
        msg += f"; equal to {a.compare} field for field ({compare(a.out, header, new, a.compare)} rows)"
    if a.cmd == "rebase" and not a.same_as_src:
        msg += "; only seed_first, seed_last and sub_block_end differ from the source"
    print(msg)


if __name__ == "__main__":
    main()
