# Magnemite A1 097 in game 20261005_034953: closed, no disagreement between the engine, the card text and the video

The question (Fable, Oct 12): the list for 20261005_034953 (Aegislash / Melmetal ex / Magnezone, Metal Energy only) read Magnemite A1 097, whose Lightning Ball costs a Lightning Energy, yet the ledger had him attacking with Magnemite on Metal. Does the engine disagree with the card text and the video?

**Answer: no. The card he played is the Metal Magnemite (A2a 053 / A2a 080), and it attacked with Tackle. The "Lightning Ball" came from my converter, not from the video.**

## 1. Card text (`lib/card.py Magnemite`, run read-only from the checkout)

| Printings | Type | Attack |
|---|---|---|
| A1 097, A4 217, A4b 133, A4b 134, P-A 024 | Lightning | [L] Lightning Ball 20 |
| A2a 053, A2a 080 | Metal | [M] Tackle 20 |
| (A2 051 Ram [C]; B1a 024 Electro Ball [L]; B3 052 Thunder Shock [LL]) | Lightning | |

Two different cards share the name. A Lightning Ball needs a Lightning Energy; Tackle needs a Metal.

## 2. What the engine does at the cost check

`engine/src/move_generation/attacks.rs` line 71 (and 124) offers an attack only if `contains_energy(active, cost, state, player)` holds. In `engine/src/hooks/core.rs` (`contains_energy` → `energy_missing`, line 2308 ff.) every non-Colorless cost symbol must be matched by one attached Energy of that exact type (taken from `get_effective_attached_energy`), and Colorless symbols are paid from what is left. So [L] is not paid by a Metal Energy. The engine agrees with the card text; nothing to change, and no `rules/09` entry.

## 3. What the video shows (Codex's ledger and review, not frames)

- The QR in DECK_USED.json (`filmed_QR`) lists Magnemite as entity 4770, "A2a 053 / A2a 080": the Metal card.
- The ledger names the card on the board as "A2a 053; Tackle20, HP60" (turn 2, evidence f0083_00).
- Owner attacks with Magnemite at game turns 2 and 4 (91 s and 131 s) read "Tackle: displayed 20 damage" after one Metal Energy from the zone; the review says the same ("Tackle: displayed 20 damage"). The word "Lightning Ball" appears nowhere in this game's ledger or review.
- Every Energy he attaches or has on the board in the game is Metal (7 attachments, 25 board readings), so no attack is used without its Energy.

## 4. How the "Lightning Ball" got into my read

The deck's Magnemite had no usable printing: the QR variant reads "A2a 053 / A2a 080" (two printings), which my deck parser threw out, and it then took the first printing of that name in the engine's database, A1 097. When the ledger's attack row did not name an attack that printing has, the converter wrote that printing's last attack title, Lightning Ball. km3 was then handed a Lightning Magnemite on Metal Energy and could never attack with it, which made some "he attacks, km3 does not" turns that were not real.

Fixed in `harness/ledger_to_positions.py`: a variant with two printings takes the first, and a printing the ledger itself names on his board (as "A2a 053; Tackle20, HP60") overrides a guessed or name-matched one. This also corrected Aegislash in the same list (B1 172 → B2 120, the printing the ledger names). All 121 positions and the km3 runs were redone; the effect is in `PAUSE_GAMES_NEW_READ_sonnet.md`: "he attacks, km3 does not" 6 → 3, "same attack" 24 → 27, first-move agreement 55 → 55.

## Not touched

`rules/09` and the other hold files are untouched; there is nothing to enter.
