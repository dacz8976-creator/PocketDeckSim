# Draft C: Meowstic / Hatterene v2 (Psychic, no ex)

Draft, not run, not a ranking. List: `draft-C-meowstic-hatterene-v2.txt`. Written Oct 1, 2026 by the Sonnet session "Opus agents
progress". This is Dustin's brew 05b with the edits his own game notes asked for.

## The list (Psychic energy)

| # | Card | Id | Text (from the database) |
|---|---|---|---|
| 2 | Espurr | B3 065 | Psychic Basic, HP 60, weak Darkness. [P] Mumble 20 |
| 2 | Meowstic | B3 066 | Psychic Stage 1 from Espurr, HP 90. Ability Perplexing Ears: once during your turn, if this Pokémon is in the Active Spot, you may make your opponent's Active Pokémon Confused. [P] Psyshot 40 |
| 2 | Hatenna | B3 069 | Psychic Basic, HP 60. [C] Stampede 10 |
| 2 | Hatterene | B3 071 | Psychic Stage 2 from Hattrem, HP 150, retreat 2. [PP] Mental Crush 70: if your opponent's Active Pokémon is Confused, 70 more damage |
| 2 | Comfey | A3 080 | Psychic Basic, HP 70, weak Metal. Ability Flower Shield: each of your Pokémon that has any [P] Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions. [PC] Spinning Attack 30 |
| 2 | Rare Candy | A3 144 | Item: evolve a Basic in play into its Stage 2 from your hand, skipping the Stage 1 (not your first turn, not a Pokémon played this turn) |
| 2 | Professor's Research | P-A 007 | Supporter: draw 2 |
| 2 | Poké Ball | P-A 005 | Item: a random Basic from your deck into your hand |
| 1 | Copycat | B1 225 | Supporter: shuffle your hand into your deck, draw a card for each card in your opponent's hand |
| 1 | Cyrus | A2 150 | Supporter: switch in 1 of your opponent's Benched Pokémon that has damage on it |
| 1 | Peculiar Plaza | B2 155 | Stadium: the Retreat Cost of each [P] Pokémon in play (both yours and your opponent's) is 2 less |
| 1 | Pokémon Center Lady | A2b 070 | Supporter: heal 30 from 1 of your Pokémon, and it recovers from all Special Conditions |

Ten Pokémon (six Basics), ten Trainers, no ex.

## What changed from brew 05b, and why (his own notes)

| Edit | His note |
|---|---|
| Comfey 1 to 2, Espurr and Hatenna stay at 2: six Basics instead of five | "comfey the only basic to start off, not ideal" (brew 05); Comfey first and dead before it could protect the rest |
| Both Team Rocket's Master Plan out | Cast once in four games (the Season Brews page, brew 1b); Meowstic confuses for free every turn, and Plan's tails confuses you |
| Cyrus in (neither 05b nor 05c had one) | "this deck not having cyrus also not ideal" (05c) |
| Pokémon Center Lady in | "no way to remove helmet or heal" against Hitmontop and Rocky Helmet (brew 05); it also cures a Special Condition |
| One Copycat out | the slot for the Lady |

No Elegant Cape (the 05c variant): Hatterene is a Stage 2 and cannot wear it, and Meowstic's job is to stay Active one turn.

## The plan, by turn

The sequence is **Meowstic confuses, retreats, Hatterene hits** (Peculiar Plaza makes the retreat free):
1. **Turn 1.** Espurr or Comfey Active, Hatenna on the Bench. Attach [P] to the Hatenna (you want two on it by the time it
   becomes Hatterene).
2. **Turn 2.** Espurr into Meowstic if it is the Active one: **Perplexing Ears** confuses their Active. Rare Candy puts Hatterene
   on Hatenna (not the turn Hatenna was played). Play Plaza and retreat Meowstic for nothing, and Hatterene is Active.
3. **Attack.** Mental Crush is 140 into a Confused Active. The best case is turn 2 for the second player (energy on turns 1 and 2); the
   usual case is turn 3 or 4, because Hatterene, Candy, Plaza and an Espurr all have to come together.
4. Confusion stays until they retreat or evolve, and each Confused attack flips: tails does nothing. Meowstic or the Lady covers
   a turn when Hatterene is not up. Cyrus pulls a damaged Benched Pokémon up so the next 140 finishes it.

## Interactions and engine support

Engine: all 12 ids complete in the coverage, no named limitation. Confusion, Special Conditions and retreat rules are the rules4
ones (`RULES_FOR_AGENTS.md`: Confused = tails and the attack does nothing; retreating removes all conditions).

- **Perplexing Ears needs Meowstic in the Active Spot** the turn it is used; Hatterene needs to be Active to attack. That is why
  the retreat matters, and why Plaza is in. Plaza is symmetric: it frees their Psychic Pokémon too.
- **Comfey's shield covers only Pokémon with a [P] Energy attached**, and a Special Condition cannot be put on it at all, so
  Mega Sceptile ex's Poison, Mega Blaziken ex's Burn and Espeon's Sleep do nothing to a Hatterene or Meowstic that has an energy.
  It does not stop damage.
- **Mental Crush is exact against Suicune's Basics**: 70 + 70 = 140, equal to Suicune ex's HP (140), Baxcalibur's (140) and Chien-Pao
  ex's (130), unless a Giant Cape or Starting Plains adds HP. Against the Megas it is 140 of 190 to 210.

## What the bot may get wrong in a test

- **Hatterene is flagged: "Mental Crush: ExtraDamageIfDefenderStatus estimated at printed damage".** The search prices the attack at
  70, not 140, so it undervalues the whole confuse, retreat, attack line, and a floor page probably understates the deck. The near-identical 05b
  page (30% overall; Hatterene attacker 96.8% used) is the only measure, and its worst cells (Hydreigon 13%, Weezing 18%,
  Suicune 22%, Sceptile 22%) are the ones this flag could be distorting.
- The page's role for Hatterene is "attacker", which is right.
- Peculiar Plaza is priced under km3 (the retreat-cost item N1; the Sept 28 review had it played on 91% of its chances on 05b's
  page).

## Versus the panel decks he loses to

**Suicune: a confused Hatterene Knocks Out Suicune ex, Chien-Pao ex and Baxcalibur in one hit.** Sceptile and Blaziken: Comfey blanks
their Poison and Burn, and a Confused Mega attacks half the time. **Lucario: 58% on the floor page of 05b**, with the Lady and Cyrus
as the answer to the Hitmontop / Rocky Helmet loss. Weak against every Darkness deck (Weezing, Hydreigon: Psychic is weak to
Darkness) and the second Psychic deck (Altaria).

## What would make me drop it

A Darkness opponent, a first turn with only Espurr or Hatenna Active and a Darkness attacker facing it, or a ladder record that
repeats brew 05's 3-3 with the same losses.
