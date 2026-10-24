# Run 2: a dated note on v1.6's first segments (Oct 24, 2026 UTC)

The coordinator asked for this note in coordinator-038 (mailbox id 20261024T0210Z). It sits beside `RESULTS_run2.md`. Nothing in run 2's results, inputs or reports is changed, and exam v1.6 stays frozen.

**What was found.** Run 3's frozen-lister check (`../run3/check_lister_v2.py`; `../run3/PREREG_RUN3.md`, addendum 5, G2) was tried on v1.6's 51 points and 67 accepted lines. It found that v1.6's `cut()` stopped LATER than frozen-7's plan lister on 4 points, 5 lines:
- after Sabrina, where the opponent must choose a new Active, which the lister ends as an opponent's choice;
- at Team Rocket's Raticate ex's Thieving Incisors, a random Energy move, which the lister ends as a chance event.

**What it affects.** The first segment decides each point's full/partial/none scope label, so v1.6's scope labels are off on those 4 points. Only the SECONDARY full-scope reading uses those labels.

**What it does not affect.** Run 2's PRIMARY prefix result is unaffected. frozen-7's `formal.py` matches each accepted line to its plan by plan identity (`map_references`; `full_plan_agreement`, lines 440-443), and all 67 lines reached their plan.

**For run 3,** addendum 5's R1 makes the first segment follow frozen-7's lister. The coordinator accepted it on Oct 24 (G13). In run 3's pooled secondaries, run 2's points keep v1.6's recorded segments and scope labels.
