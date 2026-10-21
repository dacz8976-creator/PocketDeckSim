#!/usr/bin/env python3
"""The Kingambit journal, first fill (regenerated Oct 15 under INTEGRATION_BRIEF Part E): deck 01, the list he plays
(A, 73dfed58d1d6, file decks/dustin/01-kingambit-as-played.txt), his 12 filmed games, the bot numbers filed under deck 01
(the only list a bot has played), the three lists of the deliverable (B, C, B+, withdrawn by his plan correction) and the
two current proposals (A1, A2). No setup result is filed. Refuses to run if the journal exists (later entries go through
journal.py add-version / add-result)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import journal as J  # noqa: E402

BY = "Sonnet credit worker (dacz8976-creator)"
STEM = "01-muk-glimmora-kingambit-regigigas"
DECK = "decks/dustin/%s.txt" % STEM
HIS_FILE = "decks/dustin/01-kingambit-as-played.txt"
KW = "rl/results/pause_games_decisions_2026-10-02/harness/test_oct13/KW261013_010837000.txt"
DELIVERABLE = "rl/results/deck_improvement/kingambit_2026-10-15/DELIVERABLE.md"
PK = "rl/results/battle_log_packets/"
PACKETS = [PK + p for p in (
    "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS", "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS",
    "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS", "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS",
    "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS", "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_010003000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_010837000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_014423000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_015659000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_020824000_iOS")]
R = "rl/results/"
BOT_SOURCES = [R + p for p in (
    "kx3_on_rules2_2026-10/replay_b",               # the current engine: km3 and kx3, 32 games each
    "strength_2026-10-03_kx3_dev", "strength_2026-10-04_kx3_v_k3", "strength_2026-10-04_km3_v_k3",
    "strength_2026-10-05_kx3_replay_d513", "strength_2026-10-06_kx3_tools_gate3", "strength_2026-10-08_kx3_combined",
    "thinking_time_2026-10/reg_m16_b", "thinking_time_2026-10/reg_m32_b",
    "floor_dustin_2026-09-30/%s.md" % STEM)]

WITHDRAWN = ("WITHDRAWN Oct 15: cuts cards his plan uses (the Pops keep Glimmora alive for its turn; Ilima pulls "
             "Regigigas back). ")
DELIVERABLE_BY = "the deliverable's author, Oct 15"
REVIEW_SOURCE = "laptop review + Astra's review, Oct 15 (tester fix brief section D)"
REVIEW_BY = "laptop review + Astra's review, Oct 15"
POPS, CANDY, COPYCAT = "-2 Lucky Ice Pop B2 145", "+1 Rare Candy A3 144", "+1 Copycat B1 225"
# (name, parent, changes against that parent, reason, origin_source, reason by, reason source, is a path)
PROPOSALS = [
    ("B", "A", [POPS, CANDY, COPYCAT],
     WITHDRAWN + "The deliverable's reason: consistency. +1 Rare Candy is the piece most often missing in his games and in "
     "its draw model; +1 Copycat is the model's main digging card; -2 Lucky Ice Pop (the setup numbers are the same "
     "whether Pops, Ilima or the Helmet are cut).", DELIVERABLE, DELIVERABLE_BY, DELIVERABLE, True),
    ("C", "B", ["-1 Ilima A3 149", "+1 Red A2b 071"],
     WITHDRAWN + "The deliverable's reason: matchup. +1 Red adds 20 to the Blade against an ex, so count 2 or 3 reaches more "
     "Mega ex; -1 Ilima never helps setup. Built on B so a test can isolate Red.", DELIVERABLE, DELIVERABLE_BY,
     DELIVERABLE, True),
    ("B+", "B", ["-1 Ilima A3 149", "+1 Juliana B3a 071"],
     WITHDRAWN + "The deliverable's reason: a larger package for the test. B with -Ilima, +Juliana (Juliana finds "
     "Kingambit).", DELIVERABLE, DELIVERABLE_BY, DELIVERABLE, True),
    ("A1", "A", ["-1 Lucky Ice Pop B2 145", "+1 Rare Candy A3 144"],
     "A second Rare Candy in place of one Lucky Ice Pop: Rare Candy is the piece most often missing in his games; not yet "
     "measured.", REVIEW_SOURCE, REVIEW_BY, "tester fix brief section D (not in the repo)", False),
    ("A2", "A", ["-1 Lucky Ice Pop B2 145", "-1 Professor's Research A4b 373", "+1 Rare Candy A3 144",
                 "+1 Juliana B3a 071"],
     "A second Rare Candy and Juliana (searches for Kingambit) in place of one Lucky Ice Pop and one Professor's Research; not yet measured.",
     REVIEW_SOURCE, REVIEW_BY, "tester fix brief section D (not in the repo)", False),
]


def edit(pairs, changes):
    """The (count, id) pairs of a list after '-N name id' / '+N name id' lines; ids and names checked by the journal."""
    counts = dict((cid, n) for n, cid in pairs)
    for c in changes:
        sign, n, rest = c[0], int(c[1]), c[2:].strip()
        cid = rest.split(" ", 1)[1] if rest[0].isdigit() else " ".join(rest.split()[-2:])
        cid = " ".join(c.split()[-2:])
        counts[cid] = counts.get(cid, 0) + (n if sign == "+" else -n)
        if counts[cid] == 0:
            del counts[cid]
    return [(n, cid) for cid, n in counts.items()]


def main():
    path = J._path(STEM)
    if os.path.exists(path):
        sys.exit("%s exists: use journal.py add-version / add-result" % path)
    doc = J.new_doc(STEM, "Kingambit")
    not_stated = ("not stated", BY, "none")
    J.add_version(doc, J.ROOT, list_text=open(os.path.join(J.ROOT, DECK), encoding="utf-8").read(),
                  origin="deck file on main", file=DECK, origin_source=DECK, reason=not_stated, by=BY)
    his = J.add_version(doc, J.ROOT, list_text=open(os.path.join(J.ROOT, KW), encoding="utf-8").read(),
                        origin="his list (filmed deck code)", file=HIS_FILE, origin_source=KW, reason=not_stated, by=BY)
    assert his["id"] == "73dfed58d1d6", his["id"]
    for p in PACKETS:
        J.add_played(doc, J.ROOT, p, BY)
    ids = {"A": his["id"]}
    for name, parent, changes, reason, source, rby, rsrc, is_path in PROPOSALS:
        par = J.find(doc, ids[parent])
        pairs = edit(J.pairs_of(par["list"]), changes)
        v = J.add_version(doc, J.ROOT, energy=J.parse_list("\n".join(par["list"]))[0], pairs=pairs,
                          origin="agent proposal", parent=par["id"], origin_source=source, reason=(reason, rby, rsrc),
                          by=BY, origin_source_is_path=is_path)
        ids[name] = v["id"]
        print("version %-3s %s  parent %s  diff against its parent: %s" % (name, v["id"], par["id"], v["diff"]))
    for s in BOT_SOURCES:
        try:
            got = J.add_bot(doc, J.ROOT, "35d98d0dcaf2", s, BY)
            print("bot: %s -> %d result(s)" % (s, len(got)))
        except J.Refused as e:
            print("NOT FILED: %s: %s" % (s, e))
    J.add_note(doc, J.ROOT, "73dfed58d1d6", "the deck-01 file on main is not the list you play; every Kingambit bot "
               "number so far was played on 35d98d0dcaf2 (deck 01)", "rl/deck_journal/SPEC.md", BY)
    os.makedirs(J.JOURNALS, exist_ok=True)
    J.save(path, doc, J.ROOT)
    with open(path[:-5] + ".md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(J.render(doc))
    print("wrote", path)
    print("ids:", ids)


if __name__ == "__main__":
    main()
