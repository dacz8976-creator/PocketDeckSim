# Card-text check: dustin:whimsicott (Plan B2e)

**List:** `decks/dustin/12-ariados-whimsicott-ogerpon.txt` (Energy: Grass, 20 cards, 14 distinct printings)
**Date:** 2026-09-26
**Engine side:** `python lib/card.py "<SET> <NUMBER>"` from the repo root (database `lib/deckgym-database.json`); trainer subtypes and raw Pokémon fields read straight from the same database (`trainer_card_type`, `weakness`, `retreat_cost`, `energy_required`, `fixed_damage`).
**Limitless side:** `https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` fetched with WebFetch (the page text is condensed by a small summarizing model; the effect texts below are what it returned as verbatim quotes).
**Coverage:** the official goldfish `rl/engine-2026-09-25/goldfish` (sha256 `318c82c8…dbe997`, matches the README) with `--games 0 --coverage`, no games played. Output: `rl/results/b2e_card_check_2026-09-26/coverage_dustin_whimsicott.json`.

## Verdict

- **14 of 14 cards checked against Limitless. 0 high-severity mismatches. 1 low-severity (wording only).**
- **3 cards carry bot coverage flags** (Whimsicott ex, Copycat, Team Rocket's Goo-zooka). All 14 are "Fully implemented" in the engine with no listed limitations; the flags are about what the k3 pilot prices, not about the rules being wrong.
- **Nothing unverified.**

## Per-card table

Fields compared: HP, type, stage / evolves from, weakness, retreat cost, each attack's cost / damage / effect, ability name and text, trainer type and text. "same" = identical beyond spelling/punctuation.

| # | Card (id) | Field | Engine | Limitless | Result |
|---|---|---|---|---|---|
| 1 | Spinarak (B1a 005) | type / stage | Grass, Basic | Grass, Basic | same |
| | | HP / weak / retreat | 50 / Fire / 1 | 50 / Fire / 1 | same |
| | | attack | [G] Sting 20, no effect | G Sting 20, no effect | same |
| 2 | Ariados (B1a 006) | type / stage | Grass, Stage 1 from Spinarak | Grass, Stage 1 from Spinarak | same |
| | | HP / weak / retreat | 90 / Fire / 1 | 90 / Fire / 1 | same |
| | | ability | Trap Territory: "Your opponent's Active Pokémon's Retreat Cost is 1 more." | Trap Territory: "Your opponent's Active Pokémon's Retreat Cost is 1 more." | same |
| | | attack | [G] Pierce 30, no effect | 1 Grass Pierce 30, no effect | same |
| 3 | Cottonee (B1 015) | type / stage | Grass, Basic | Grass, Basic | same |
| | | HP / weak / retreat | 50 / Fire / 1 | 50 / Fire / 1 | same |
| | | attack | [G] Razor Leaf 20, no effect | one Grass Razor Leaf 20, no effect | same |
| 4 | Whimsicott ex (B1 016) | type / stage | Grass, Stage 1 from Cottonee | Grass, Stage 1 from Cottonee | same |
| | | HP / weak / retreat | 140 / Fire / 1 | 140 / Fire / 1 | same |
| | | attack | [GC] Grass Knot 40 — "This attack does 30 more damage for each Energy in your opponent's Active Pokémon's Retreat Cost." | Grass, Colorless; Grass Knot 40+ "This attack does 30 more damage for each Energy in your opponent's Active Pokémon's Retreat Cost." | same ("40+" is Limitless's notation for variable damage) |
| 5 | Teal Mask Ogerpon ex (B2 017) | type / stage | Grass, Basic | Grass, Basic | same |
| | | HP / weak / retreat | 130 / Fire / 1 | 130 / Fire / 1 | same |
| | | ability | Soothing Wind: "Each of your Pokémon that has any Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions." | Soothing Wind: same text | same |
| | | attack | [GG] Energized Leaves 60 — "If the amount of Energy attached to both Active Pokémon is 5 or more, this attack does 60 more damage." | GG Energized Leaves 60+ same text | same |
| 6 | X Speed (P-A 002) | trainer type | Item | Trainer - Item | same |
| | | text | "During this turn, the Retreat Cost of your Active Pokémon is 1 less." | same | same |
| 7 | Poké Ball (P-A 005) | trainer type | Item | Trainer - Item | same |
| | | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | **low**: "a random" vs "1 random" — same meaning (one card). May be the fetch summarizer's rendering. |
| 8 | Quick-Grow Extract (B1a 067) | trainer type | Item | Trainer - Item | same |
| | | text | "Choose 1 of your [G] Pokémon in play. Put a random [G] Pokémon from your deck that evolves from that Pokémon onto that Pokémon to evolve it. You can't use this card during your first turn or on a Pokémon that was put into play this turn." | same | same |
| 9 | Team Rocket's Goo-zooka (B4a 068) | trainer type | Item | Trainer - Item | same |
| | | text | "Until the end of your opponent's next turn, your opponent's Active Pokémon's Retreat Cost is 1 more." | same | same |
| 10 | Leaf Cape (A3 147) | trainer type | Tool | Trainer - Tool | same |
| | | text | "The [G] Pokémon this card is attached to gets +30 HP." | same | same |
| 11 | Professor's Research (P-A 007) | trainer type | Supporter | Trainer - Supporter | same |
| | | text | "Draw 2 cards." | same | same |
| 12 | Copycat (B1 225) | trainer type | Supporter | Trainer - Supporter | same |
| | | text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same | same |
| 13 | Lisia (B1 226) | trainer type | Supporter | Trainer - Supporter | same |
| | | text | "Put 2 random Basic Pokémon with 50 HP or less from your deck into your hand." | same | same |
| 14 | Hiking Trail (B2b 069) | trainer type | Stadium | Trainer - Stadium | same |
| | | text | "At the end of each player's turn, that player draws cards until they have 3 cards in their hand." | same | same |

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording; identical meaning) |

No high-severity mismatch: every HP, type, stage, evolves-from, weakness, retreat cost, attack cost, attack damage, attack effect, ability text and trainer type/text agrees.

## Coverage flags (goldfish `--coverage`, games 0)

Engine status for all 14 printings: "Fully implemented", `limitations: []`, so there are **no** "engine limitation" or "not implemented" flags. The flags that fire:

| Card | Flag class | Detail from the tool |
|---|---|---|
| Whimsicott ex (B1 016) | printed-damage estimator | `Grass Knot: ExtraDamagePerRetreatCost estimated at printed damage` — k3's damage estimate values Grass Knot at 40, not 40 + 30 per Energy in the opponent's Retreat Cost (the attack itself resolves correctly in play; the bot just does not see the bonus when choosing). This is the deck's whole plan (Ariados / Goo-zooka raise the retreat cost to pump Grass Knot), so the pilot undervalues it. |
| Copycat (B1 225) | unpriced text rule | `its effect` — the text reads the opponent's hand; k3 leaves that unpriced (kp prices it only if the text is on the audited list). |
| Team Rocket's Goo-zooka (B4a 068) | pays off on the opponent's turn | `its effect` — "Until the end of your opponent's next turn…"; the search never plays out the opponent's turn, so the extra retreat cost it imposes is not valued (its same-turn effect on Grass Knot is also hidden by the estimator flag above). |

Unflagged (11): Spinarak, Ariados, Cottonee, Teal Mask Ogerpon ex (Energized Leaves uses `ExtraDamageIfCombinedActiveEnergyAtLeast`, which the estimator prices), X Speed, Poké Ball, Quick-Grow Extract, Leaf Cape, Professor's Research, Lisia, Hiking Trail.

Note: Ariados's Trap Territory ("Retreat Cost is 1 more") is not flagged by any of the tool's text markers, but its payoff runs through the same Grass Knot bonus that the estimator ignores, so the bot's numbers for this list should be read as untrusted, consistent with floor.py's rule for lists with flagged cards.

## Unverified

None.

## Files

- This report: `rl/results/b2e_card_check_2026-09-26/card_check_dustin_whimsicott.md`
- Coverage JSON: `rl/results/b2e_card_check_2026-09-26/coverage_dustin_whimsicott.json`
- Scratch scripts: `…\scratchpad\b2e\cov_dustin12_whimsicott_only.sh` (WSL runner), `…\scratchpad\b2e\trainer_types_dustin12.py` (database field dump)
