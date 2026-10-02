#!/usr/bin/env python3
import collections, csv
rows = list(csv.DictReader(open("/home/dacz8976/c8c/out/revert_check_cut.tsv", encoding="utf-8"), delimiter="\t"))
print("games with a finite-cut Pokemon in a deck:", len(rows))
print("finite-cut Pokemon on the board at the first differing tick:", collections.Counter(r["finite_on_board"] for r in rows))
for grp in ("yes", "no", "all"):
    sub = [r for r in rows if grp == "all" or r["finite_on_board"] == grp]
    print(f"\n== finite on board = {grp}: {len(sub)} games")
    for n in ("queued_only_ok", "cut_only_ok", "full_ok"):
        print(f"   {n}: {collections.Counter(r[n] for r in sub)}")
print("\nby verdict (all):", sorted(collections.Counter((r["verdict"], r["queued_only_ok"], r["cut_only_ok"], r["full_ok"]) for r in rows).items()))
print("\ngames where the cut-only revert reproduces old (alone):", [(r["bot"], r["pairing"], r["i"], r["k"]) for r in rows if r["cut_only_ok"] == "yes"][:20])
print("games where queued-only fails but full reproduces (the cut order matters):", [(r["bot"], r["pairing"], r["i"], r["k"]) for r in rows if r["queued_only_ok"] != "yes" and r["full_ok"] == "yes"][:30])
print("games where full fails:", [(r["bot"], r["pairing"], r["i"], r["k"], r["old_choice"][:40], r["full_choice"][:40]) for r in rows if r["full_ok"] != "yes"][:30])
by = collections.Counter((r["bot"], int(r["pairing"])) for r in rows)
print("\nby (bot, pairing):", sorted(by.items()))
