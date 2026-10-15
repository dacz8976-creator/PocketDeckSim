# Glimmora Poison knockout rule test

**Reviewer:** sol_glimmora_200857, 2026-09-29. **Scope:** Entire 174.47-second supplied rule-test clip, with dense inspection of the consequential knockout. This is a mechanics review of the available test, not a completed battle or ladder result. The owner's Auto toggle is visibly off; opponent automation and Solo/PvP mode are not established. Source identity is in [SOURCE.json](SOURCE.json).

## Finding

The clip **confirms the tested Poison path**: a Poison tick reduces the owner's Active Glimmora from 10 HP to 0, *Shattering Crystal* triggers, the coin lands **heads**, and the game explicitly says the opponent was unable to get any points. Both players' three point markers remain unfilled through that message and the following replacement prompt. The ability is resolved before any point award for Glimmora is shown. This does not prove the internal implementation or the Burn path. No Burn knockout occurs in this clip.

The visible Glimmora card says: “When this Pokémon is Knocked Out, flip a coin. If heads, your opponent can't get any points for it.” See [115s](evidence/overview_024.jpg). The wording contains no visible attack-only restriction.

## Whole-clip coverage and evidence

| Time | Observed sequence |
| --- | --- |
| 0:00–0:20 | Game opens and both sides establish Actives: owner Glimmet, opponent Team Rocket's Magmar. Score markers empty. [Overview](evidence/sheet_1.jpg) |
| 0:20–1:00 | Opponent benches another Magmar and two Team Rocket's Koffing. Owner benches Glimmet and Regigigas; develops its Active through Glimmet toward the Glimmora test. No knockout or point occurs. [Overview](evidence/sheet_1.jpg) |
| 1:00–1:50 | Opponent's turn and owner's next turn proceed. Owner's Active Glimmet takes damage (visible 60 to 50 HP) then evolves into the 90-HP Glimmora; owner heals it back to 90 HP. Score remains 0–0. [Overview](evidence/sheet_2.jpg) |
| 1:50–2:05 | Glimmora card is inspected, showing *Shattering Crystal*. Glimmora's **Venomous Hit** damages opposing Magmar and Poisons it. A subsequent on-screen banner states “Glimmora is now Poisoned,” so both Actives become Poisoned. Exact source of the Poison on Glimmora is not independently assigned here. [Card](evidence/overview_024.jpg), [Poison banner](evidence/overview_025.jpg) |
| 2:05–2:35 | Repeated turn/checkup progression lowers both Poisoned Actives. Magmar is shown at 20 HP and Glimmora at 10 HP before the terminal test tick; both remain Active. Owner benches Pawniard. Score remains 0–0. [125s](evidence/overview_026.jpg), [150s](evidence/overview_031.jpg), [Overview](evidence/sheet_3.jpg) |
| 2:35–2:40 | Owner confirms ending the turn despite the “An attack can be used” prompt. The next Poison checkup displays **Poison 10** over Glimmora, and its HP changes **10 to 0**. Opponent Magmar also takes a Poison tick, 20 to 10 HP, and survives. [Before](evidence/end_006.jpg), [0 HP](evidence/end_008.jpg) |
| 2:41–2:46 | The *Shattering Crystal* ability banner appears. Its conditional coin text is displayed; the coin resolves **Heads**. [Banner](evidence/end_011.jpg), [coin text](evidence/end_015.jpg), [heads](evidence/end_021.jpg) |
| 2:46–2:51 | Glimmora leaves the Active slot. The game displays “Opponent was unable to get any points,” while the opponent's point markers stay empty. The owner is then asked to choose a Bench Pokémon to switch in. [Denial](evidence/end_027.jpg), [replacement](evidence/end_031.jpg) |
| 2:51–2:54.47 | Owner begins selecting a benched Glimmet as replacement. The clip ends during that choice; the larger battle result is not recorded. [Tail](evidence/tail_03.jpg) |

## Limits

- This is one observed Poison-triggered knockout and one heads outcome. It does not test Burn, tails, attack-caused knockout, simultaneous knockout, or later point accounting after another action.
- The visible denial message and empty score markers support that the opponent received no point for this Glimmora. The recording cannot expose the game's internal ordering beyond the visible sequence.
- This unfinished battle has no established winner and does not belong in the Ladder Log.
