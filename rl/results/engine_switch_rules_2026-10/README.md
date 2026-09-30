# The rules engine switch (Oct 2026): decisions and who does what

The plan is `PLAN.md` (0a68b0a). This file records the decisions on it and who did which part.

## Dustin's decisions (Sept 30 evening)

Given in the Fable coordinator session ("Work delegation and task routing") and relayed to the laptop session. The coordinator put the plan's questions 1-6 and 8-10 to him as nine items, each with the plan's recommendation. His answer, verbatim: **"Sure go for all 9"**. So, as recommended (numbers as in `PLAN.md`):
1. **A conditional go: "pin if all pass".**
   - Every replay must be identical and every counter must read as expected.
   - Every changed carrier or scratch game must be explained: on the board by an exact counter, or in lookahead by a trace that meets both halves.
   - A trace that needs a judgment call comes to him, and the pin waits for his word on it.
2. **Scope:** A + B + kd's follow-ons + F1-F7. 09e964f, PR #383 and B4b data are left out.
3. **The per-thread heads-cut value** is kept.
4. **Carrier lists:** real development lists, extracted by the cloud from the committed Limitless archive. The made lists are the fallback.
5. **km3's coverage baselines** are replayed at this switch, as a gate.
6. **kd3's identity** is a gate.
8. **When:** overnight laptop runs on the Oct 1 and Oct 2 nights. Each morning everything is committed and pushed, with main = origin/main, by 7:00 am Central.
9. **If A fails its mechanic check:** hold A, and ship B + kd if B passes (a revert commit of A, a new build and the replays again).
10. **09e964f:**
    - Fix 2 is recorded as not taken. It contradicts the JP ruling the fork follows (`rules/06_sources.md:124`) and would break `rules_repair_retaliation_timing.rs:136`.
    - Fix 1 stays "unchecked" until F8 or a second reader settles it.

**Question 7** (the order against the cloud's N1) was the coordinator's operational decision:
- Sonnet does F1-F7 tonight on `sonnet/rules-fixes`, cut from cae37a3, with no `players/` change, and pushes it.
- R is that branch's head.
- The cloud stays on N1.

## The carrier lists (step 3; the coordinator's choice under Dustin's Q4 answer)

The cloud extracted them from the committed Limitless archive (commit e0d149a on `claude/pensive-ptolemy-spwc0b`, `carriers/`; provenance in its `README.md` and `selection.json`). By the plan's rule, the most frequent exact list among top-8 development finishes, only one exists:
- **`garchomp_meowth.txt`** (Meowth B2 124). Shaquill10, BEC'S KING OF THE HILL, 95 players, 2026-09-18, 5th place (4-1).

The other three have real development lists, but none placed top-8. These are the "alternates":
- **`alternates/togekiss_meowth.txt`** (Togekiss A4 080 and Meowth). Alolan Jay, The Breakfast Club Nightly, 118 players, 2026-09-07, 19th place (5-3).
- **`alternates/hisuian_goodra.txt`** (Hisuian Goodra B3b 050, the (a) finite cut). tommyboistreams, TH Event's "When DX Pack?!", 68 players, dropped (0-3).
- **`alternates/houndoom_victini.txt`** (Victini B3 025, repair A). foodking90, Dark League Pocket Tournament, 118 players, 2026-09-12, dropped after round 1 (0-1).

**The coordinator's decision** (Sept 30, operational, under Dustin's Q4 answer "real lists, made lists as fallback"): step 8's carriers are `garchomp_meowth.txt` plus the three alternates.
- The reason: a carrier's job is to reach the mechanic in real play, not to measure strength, and a poor record doesn't change which cards a list holds.
- The made lists (`coinflip_deck.txt`, `fire_victini.txt`) are used only in 8b's scratch rows.
- Every list passed the cloud's card checks: one printing per id, no B4b card, the validator clean, and a 560-game legality scan with no findings.
- Each list's Energy line was added from its Pokémon's attack costs, since the archive's decklists carry none (`select_carriers.py`).

**R stays Sonnet's branch head,** never the cloud's head. The cloud's kn (N1) build is on the same cloud branch (71877f6) and changes `players/`.

## Who does what

| Part | Who |
|---|---|
| Repairs A and B, S1-S4 | the cloud (commits on `claude/pensive-ptolemy-spwc0b`) |
| The second read of A and B | Sonnet (`../coin_prevention_repair_2026-09-30/SECOND_READ_sonnet.md`) |
| The integrator's review and this plan | the laptop session (Opus), with its subagents, reading only |
| F1-F7 (tests first, then fixes), ending at R | Sonnet, on `sonnet/rules-fixes` |
| The second read of F1-F7 | an Opus subagent of the laptop session, reading only |
| The step 2 equivalence readings | the laptop's Opus subagent (`EQUIVALENCE_opus.md`, tracing every caller) and Sonnet (the other reading) |
| The carrier lists (step 3) | the cloud, beside N1, via Dustin's paste block |
| The build, the replays, the pin and the floor re-check | the laptop |
| The traces (step 8c) | the cloud, with Sonnet reading every hand trace |
| Routing and audit | the Fable coordinator session |

This table is updated as each part lands.
