#!/usr/bin/env python3
"""The spec's first fill: the Kingambit journal, with deck 01 and his list 73dfed58d1d6. Refuses to run if the
journal exists (later entries go through journal.py add-version / add-result)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import journal as J  # noqa: E402

BY = "Sonnet credit worker (dacz8976-creator)"
STEM = "01-muk-glimmora-kingambit-regigigas"
DECK = "decks/dustin/%s.txt" % STEM
KW = "rl/results/pause_games_decisions_2026-10-02/harness/test_oct13/KW261013_010837000.txt"
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


def main():
    path = J._path(STEM)
    if os.path.exists(path):
        sys.exit("%s exists: use journal.py add-version / add-result" % path)
    doc = J.new_doc(STEM, "Kingambit")
    not_stated = ("not stated", BY, "none")
    J.add_version(doc, J.ROOT, list_text=open(os.path.join(J.ROOT, DECK), encoding="utf-8").read(),
                  origin="deck file on main", file=DECK, origin_source=DECK, reason=not_stated, by=BY)
    his = J.add_version(doc, J.ROOT, list_text=open(os.path.join(J.ROOT, KW), encoding="utf-8").read(),
                        origin="his list (filmed deck code)", origin_source=KW, reason=not_stated, by=BY)
    assert his["id"] == "73dfed58d1d6", his["id"]
    for p in PACKETS:
        J.add_played(doc, J.ROOT, p, BY)
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


if __name__ == "__main__":
    main()
