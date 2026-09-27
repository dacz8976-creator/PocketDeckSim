# kph registration: the one review (Sept 27)

Two independent reviewers read the draft against the code and the rules before registration. Verdicts: both "sound in principle, not ready to register"; every finding was a text fix and all were applied in `REGISTRATION.md`. No code or game had run.

## Engine code lens

| # | Finding | Fix applied |
|---|---|---|
| 1 | A is buildable, but `pokemon_online_score` is shared with kq's bench score (2456), and total = 0 returns 1.0 early (2401-2402). | A is a separate variant in the projected branch (2122-2124); `saturating_sub` for steps; the early return kept. |
| 2 | "With steps = 0 this is R exactly" was false: R has no max against the unprojected reading, and extra Energy can move the yardstick (2215-2216). | The max applies only when steps > 0; at steps = 0, A is R exactly. The "never below" test only on steps > 0 boards. |
| 3 | The Riolu test board wasn't pinned: it reads 0.5 mid-turn and 0 only after EndTurn, and the target depends on deck order. | Timing, Zone and deck stated; expected A 0 / 0.5, R 0.5 / 1.0. |
| 4 | The scan projects slot 0 only (983-989); the existing test (3837) covers R only. | Parameter widened to (horizon, slot, Zone-only); a B case added to that test. |
| 5 | B's Zone wording would give the opponent's benched Pokémon two Energy where its Active gets one. | s gets exactly the Zone terms of `projected_active_energy_and_discard`'s turn list, same `running` test, no `zone_blocked`; an opponent-side test added. |
| 6 | `NoEnergyFromZoneToActive` blocks only the Active. | No change needed. |
| 7 | `get_retreat_cost_for_player` includes this turn's X Speed, so on the real Q10 board (X Speed played) Shuckle ex read cost 0 and Vespiquen ex was credited; `has_retreated` wasn't checked. | `get_board_retreat_cost_for_player`; `!has_retreated` when the attack is this turn; the Q10 test built with X Speed and `has_retreated`; a positive control added. |
| 8 | Blocked retreat also covers `NoRetreat` and Fossils; "cost 0 always qualifies" contradicted the status block. | kq's player-aware block (1537-1540) reused; reworded to "cost 0 always passes the payment test". |
| 9 | Payment by count is enough (Colorless costs); card facts right. | No change needed. |
| 10 | Identity pattern fine; parser needs `kph` before `kp`; composed base needs its own identity. | Both added. |
| 11 | Code references correct. | None. |

## Rules and plan lens

| # | Finding | Fix applied |
|---|---|---|
| 1 | No constant, list-free; the line-4 quote had no recorded source. | Source stated (chat, Sept 27; recorded in the registration first). |
| 2 | The comparator was "the pilot in force", but kpg isn't in force (confirmation pending); no plan if kpg fails; no composed-base identities. | Comparator is kph's own base at the same engine; kph lapses with kpg; composed-base identities added. |
| 3 | Four RUN5 gate lines missing: footprint first (446), paired-noise veto wording (386-388), coverage no-harm only (417), confirmation size (390-393). | All four added. |
| 4 | Development cells not named; the veto rows contain the design deals. | All 45 cells declared development evidence; the three decks' mixed rows also reported on deals outside `selected.json`. |
| 5 | **The tempo-trade claim was backwards:** B gives a benched attacker with no Energy only one Zone Energy, so kph keeps R's tempo credit (DIAGNOSIS 235), the move Dustin rejected at Q10. | Rewritten: kph keeps it by design; listed as open in section 7; counted in the mechanism check, gating nothing. |
| 6 | "Price next turn's retreat every time" overstated (three notes); the Q10 note concerns the bench-feed alternative. | "In Q06, Q08 and Q10"; the Q10 note attributed to the bench-feed alternative. |
| 7 | Same as code 7 (X Speed on the Q10 board). | As code 7. |
| 8 | Mechanism check: no denominator, unreached positions, slice files unpinned, "beyond noise" undefined, no failure condition for B. | Denominator = reached identical boards, unreached reported; pass = more than half per slice and pooled; slice files pinned; B's failure condition added; noise = the deck's paired mixed-row interval used for kpf's vetoes. |
| 9 | Rayquaza check: "within noise" undefined, the Lucario pilot unnamed, gating unstated. | Same 200 deals, kp3 on Lucario, paired 95% intervals for kph − kpf3; diagnostic, never gating. |

## Added after the review, from Dustin (Sept 27)

- Section 7: "X Speed played and not used" (Q02's game, turn 2), a shared bot miss outside R.
