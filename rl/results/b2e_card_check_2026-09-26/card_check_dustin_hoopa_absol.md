# Card-text check: dustin:hoopa_absol (Sept 26, 2026)

**List:** `decks/dustin/04-absol-hoopa-darkrai.txt` (Energy: Darkness; 20 cards, 13 distinct).
**Held-out archetype:** "Hoopa ex Mega Absol ex" (also the base of `decks/brews/brew-07-hoopa-darkrai-sableye.txt`).

**How it was checked.** Engine text: `python lib/card.py "<SET> <NUMBER>"` from the repo root
(`lib/deckgym-database.json`), plus the raw JSON entry for each card for the Trainer subtype and the
retreat-cost list, which card.py does not print. Limitless: the card page
`https://pocket.limitlesstcg.com/cards/<SET>/<NUMBER>` (no leading zeros: `P-A/2`, `B4a/63`). A WebFetch
summary was pulled first; it mislabelled Happiny's zero-cost attack as an ability, so every page was then
re-read as raw text in the browser pane and the table below rests on the raw text. "Match" means identical
beyond spelling and punctuation (Limitless prints "Pokemon" without the accent on some Trainers).

**Result: 13 of 13 cards verified, 0 high mismatches, 1 low (Poké Ball wording), 0 unverified.**

## Per-card table

| # | Card | Engine id | Field | Engine | Limitless | Result |
|---|---|---|---|---|---|---|
| 1 | Absol | B4 100 | type / stage | Darkness, Basic (no evolves-from) | Darkness, Pokémon - Basic | match |
| | | | HP / weakness / retreat | 70 / Grass / 1 | 70 / Grass / 1 | match |
| | | | attack Enhanced Blade | [D] 20 — "If this Pokémon has a Pokémon Tool attached, this attack does 30 more damage." | D, 20+ — same text | match ("20+" is Limitless's display for variable damage) |
| 2 | Darkrai ex | A2 110 | type / stage | Darkness, Basic | Darkness, Pokémon - Basic | match |
| | | | HP / weakness / retreat | 140 / Grass / 2 | 140 / Grass / 2 | match |
| | | | ability Nightmare Aura | "Whenever you attach a [D] Energy from your Energy Zone to this Pokémon, do 20 damage to your opponent's Active Pokémon." | same text | match |
| | | | attack Dark Prism | [DDC] 80, no effect | DDC, 80, no effect | match |
| 3 | Hoopa ex | B4 103 | type / stage | Darkness, Basic | Darkness, Pokémon - Basic | match |
| | | | HP / weakness / retreat | 150 / Grass / 2 | 150 / Grass / 2 | match |
| | | | attack Shadow Bullet | [D] 30 — "This attack also does 20 damage to 1 of your opponent's Benched Pokémon." | D, 30 — same text | match |
| | | | attack Dynamite Punch | [DDC] 100 — "This Pokémon also does 20 damage to itself." | DDC, 100 — same text | match |
| 4 | Bombirdier | B3 115 | type / stage | Darkness, Basic | Darkness, Pokémon - Basic | match |
| | | | HP / weakness / retreat | 70 / Lightning / 1 | 70 / Lightning / 1 | match |
| | | | ability Villainous Delivery | "As long as this Pokémon is on your Bench, your Active [D] Pokémon's Retreat Cost is 1 less." | same text | match |
| | | | attack Dark Cutter | [D] 30, no effect | D, 30, no effect | match |
| 5 | Happiny | B4a 063 | type / stage | Colorless, Basic | Colorless, Pokémon - Basic | match |
| | | | HP / weakness / retreat | 30 / none / 0 | 30 / none / 0 | match |
| | | | attack Chubby Cheer | cost none, 10 — "During your next turn, attacks used by your Pokémon do +20 damage to your opponent's Active Pokémon." | raw page line "0 Chubby Cheer 10" — same text | match (it is an attack, zero cost, 10 damage; the WebFetch summary's "ability" label was wrong) |
| 6 | X Speed | P-A 002 | Trainer type | Item | Trainer - Item | match |
| | | | text | "During this turn, the Retreat Cost of your Active Pokémon is 1 less." | same text | match |
| 7 | Poké Ball | P-A 005 | Trainer type | Item | Trainer - Item | match |
| | | | text | "Put **a** random Basic Pokémon from your deck into your hand." | "Put **1** random Basic Pokemon from your deck into your hand." | **low** — wording only ("a" vs "1"), same meaning |
| 8 | Deceptive Needle | B4 148 | Trainer type | Tool | Trainer - Tool | match |
| | | | text | "At the end of your turn, if the [D] Pokémon this card is attached to is in the Active Spot, do 10 damage to your opponent's Active Pokémon." | same text | match |
| 9 | Professor's Research | P-A 007 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Draw 2 cards." | same text | match |
| 10 | Sabrina | A1 225 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" | same text | match |
| 11 | Cyrus | A2 150 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." | same text | match |
| 12 | Copycat | B1 225 | Trainer type | Supporter | Trainer - Supporter | match |
| | | | text | "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | same text | match |
| 13 | Starting Plains | B2 154 | Trainer type | Stadium | Trainer - Stadium | match |
| | | | text | "Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP." | same text | match |

## Mismatches

| Card | Field | Engine | Limitless | Severity |
|---|---|---|---|---|
| Poké Ball (P-A 005) | text | "Put a random Basic Pokémon from your deck into your hand." | "Put 1 random Basic Pokemon from your deck into your hand." | low (wording; same meaning) |

No high-severity mismatch: every HP, type, stage, weakness, retreat cost, attack cost, attack damage,
effect text, ability text and Trainer type agrees with Limitless.

## Unverified

None.

## Coverage flags (`goldfish --coverage`, 0 games)

**Tool:** `rl/engine-2026-09-25/goldfish`, sha256 `318c82c897f08a376e836bd23f68d1aa53d8312adc00b04603137a6c86dbe997`
(matches `rl/engine-2026-09-25/README.md`). Run in WSL from the repo root:
`goldfish --deck decks/dustin/04-absol-hoopa-darkrai.txt --panel decks/screen/opponents --games 0 --coverage rl/results/b2e_card_check_2026-09-26/coverage_dustin_hoopa_absol.json`.
The tool writes the coverage file right after loading the list and then reads the panel folder, so `--panel`
is pointed at the screen panel to avoid a missing-folder panic; with `--games 0` it prints "0 games (0 crashed)"
and plays nothing. Exit code 0. Script: `scratchpad/b2e/coverage_dustin_hoopa_absol.sh`; raw output:
`coverage_dustin_hoopa_absol.json` beside this file.

| Card | Flag class | Detail (from the JSON) |
|---|---|---|
| Copycat (B1 225) | unpriced text rule | `unpriced_text_rule: ["its effect"]` — the text reads the opponent's hand ("Draw a card for each card in your opponent's hand"); k3 prices it with a fallback |
| Absol (B4 100) | printed-damage estimator | `Enhanced Blade: ExtraDamageIfToolAttached estimated at printed damage` — the estimator uses 20 and does not price the +30 with a Tool attached |
| Happiny (B4a 063) | printed-damage estimator | `Chubby Cheer: IncreasedDamageNextTurn estimated at printed damage` — the estimator uses 10 and does not price the +20 on next turn's attacks |

- **Pays off on the opponent's turn:** none flagged (Deceptive Needle triggers at the end of *your* turn, which is not one of the tool's reply markers).
- **Engine limitation:** none (`limitations: []` on every card).
- **Not implemented:** none (all 13 cards `engine_status: "Fully implemented"`, `engine_complete: true`).

Per the goldfish's own header comment, the bot's numbers for a list with flagged cards are marked untrusted on
its page; 3 of this list's 13 cards are flagged, so the k3 pilot's numbers for dustin:hoopa_absol carry that
caveat (the game rules themselves are complete for every card).
