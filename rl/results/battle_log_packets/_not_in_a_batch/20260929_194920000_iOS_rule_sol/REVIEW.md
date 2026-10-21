# Rule test review: Eevee's Boosted Evolution

Reviewer: `sol_eevee_194920` (Sol). Review date: 2026-09-29 America/Chicago. Scope: entire supplied 1:09.26 **rule-test clip**, from setup through the final recorded first-turn screen. This is not a completed battle or a ladder result. Source identity is in [SOURCE.json](SOURCE.json); times below are elapsed video time. Auto is shown off during the visible turn. The opponent is marked AI at 00:03; the recording does not establish any PvP match.

> **Scope clarification:** The intended test is whether Eevee's permission spreads. The rejected Rattata evolution supports that it does not. See [accepted clarification](SCOPE_CLARIFICATION.md), which supersedes the earlier inconclusive framing below. The original review is retained for audit history.

## Finding

The printed Boosted Evolution ability is self-referential: **“As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it.”** The owner places that Eevee Active. On the owner's first turn, Team Rocket's Rattata is placed on the Bench, and Team Rocket's Raticate ex is present in hand. Raticate ex says it evolves from Team Rocket's Rattata. When the owner selects that evolution card after Rattata is on the Bench, the game says **“Unable to evolve”** and leaves Rattata unevolved. This recorded attempt was refused while Eevee's ability was active, consistent with the intended Eevee-only exception.

The clip does **not** isolate why Rattata was refused: it was both the owner's first turn **and** the turn Rattata was played. It also contains no Eevee evolution card or positive first-turn Eevee evolution. Therefore this footage confirms the refusal for this one non-Eevee target, but cannot by itself prove that the game implements every branch of the Active-only rule. The reported upstream simulator behavior is user-provided context, not a fact checked from simulator code in this review.

| Elapsed | Source observation | Retained evidence |
|---|---|---|
| 00:03-00:11 | Match setup shows an AI opponent and that the owner is going first. Opening hand includes Team Rocket's Raticate ex. Owner chooses Boosted Evolution Eevee as Active. | `evidence/t11.jpg` |
| 00:18-00:23 | Opponent has Active Galarian Ponyta and Benched Ralts. Eevee is Active. The game announces that Eevee can evolve during the first turn or the turn it is played; the owner's `Current turn: 1` marker appears. | `evidence/t19.jpg`, `evidence/t23.jpg` |
| 00:24-00:43 | Owner's first turn remains in progress. A Poké Ball is played, another Eevee enters hand, and Professor's Research is shown. No evolution occurs. | `evidence/t44.jpg` |
| 00:44-00:47 | Team Rocket's Rattata (40 HP) is selected from hand and placed on the owner's left Bench slot. Active Eevee remains in place. Raticate ex remains in hand. | `evidence/t44.jpg`, `evidence/t47.jpg` |
| 00:48-00:52 | The owner selects Team Rocket's Raticate ex. Its enlarged card identifies it as Stage 1, evolving from Team Rocket's Rattata. The game displays `Unable to evolve`; after the card returns to hand, Rattata remains on the Bench unevolved. | `evidence/t48.jpg`, `evidence/t49.jpg`, `evidence/t50.jpg` |
| 00:53-00:60 | Owner plays a second Boosted Evolution Eevee to the right Bench and attaches Lucky Egg to Active Eevee. Both Rattata and the new Eevee remain unevolved. | `evidence/t53.jpg`, `evidence/t56.jpg`, `evidence/t59.jpg` |
| 01:00-01:09.26 | Owner opens Active Eevee's Stampede attack preview. Clip ends on the first-turn battle screen before an attack resolves or the turn ends. No battle outcome is visible. | `evidence/t68.jpg` |

## Limits

- The phrase “this Pokémon” on Eevee's card directly limits the printed permission to that Eevee while Active; the visual test supplies a compatible rejection of a different Pokémon's evolution. The alert does not identify which ordinary evolution restriction was decisive.
- The second Eevee is placed on the Bench late in the clip, but no matching Eeveelution is seen in hand or attempted on either Eevee. Its lack of evolution is not an ability test.
- The user reported that upstream `deckgym` commit `ca4b67f` may permit whole-board first-turn evolution once Eevee is Active. That implementation claim has not been independently inspected here. A targeted simulator regression should compare the same board and hand and distinguish first-turn restriction from turn-played restriction.
- The source ends before an attack, turn transition, or result; hidden opponent cards and later gameplay are unknown.

