# Draft D: Entei / Grimhound (Fire)

Draft, not run, not a ranking. List: `draft-D-entei-grimhound.txt`. Written Oct 1, 2026 by the Sonnet session "Opus agents
progress". It keeps what worked in Dustin's brew 08 (Entei ex, Rainbow Cave, Flame Patch) and adds a finisher.

## The list (Fire energy)

| # | Card | Id | Text (from the database) |
|---|---|---|---|
| 2 | Entei ex | A4a 010 | Fire Basic, HP 140, weak Water, retreat 2. Ability Legendary Pulse: at the end of your turn, if this Pokémon is in the Active Spot, draw a card. [RR] Blazing Beatdown 60: 60 more damage if it has at least 2 extra [R] Energy attached |
| 2 | Houndour | A2a 011 | Fire Basic, HP 60, weak Water. [R] Flare 20 |
| 2 | Mega Houndoom ex | P-B 080 | Fire Stage 1 from Houndour, HP 190, weak Water, retreat 2. [RRC] Grimhound Flare 80: flip 3 coins, 80 damage for each heads |
| 2 | Victini | B3 025 | Fire Basic, HP 70, weak Water. Ability Victory Star: once during your turn, after you flip any coins for an attack of 1 of your [R] Pokémon, you may ignore all results of those coin flips and begin flipping those coins again; not more than 1 Victory Star Ability each turn. [RC] V-Flame 40 |
| 2 | Magby | A4 032 | Fire Basic, HP 30, no Weakness, retreat 0. [-] Toasty Toss: take a [R] Energy from your Energy Zone and attach it to 1 of your Benched Basic Pokémon |
| 2 | Professor's Research | P-A 007 | Supporter: draw 2 |
| 2 | Poké Ball | P-A 005 | Item: a random Basic from your deck into your hand |
| 2 | Flame Patch | B1 217 | Item: attach a [R] Energy from your discard pile to your Active [R] Pokémon |
| 2 | Rainbow Cave | B4 155 | Stadium: once during each player's turn, that player may discard the Energy generated in their Energy Zone; if they do, the next Energy is produced |
| 1 | Cyrus | A2 150 | Supporter: switch in 1 of your opponent's Benched Pokémon that has damage on it |
| 1 | Giant Cape | A2 147 | Tool: +20 HP |

Ten Pokémon (eight Basics), ten Trainers. Four ex: Entei ex (two points each) and Mega Houndoom ex (three).

## Why it exists

Two of the panel decks he loses to are Grass (Mega Sceptile ex, Vespiquen ex), and Fire hits Grass for Weakness. Brew 08's floor
page against them (km3: Sceptile 65%, Vespiquen 83%) says the Entei shell already does that. Its holes were Blaziken (36%) and Suicune
(43%), and on the ladder it lost to Dragonite, Mega Diancie / Gardevoir and Mega Lucario. This draft changes the **finisher** and the
**first turn**:
- **Mega Houndoom ex**: 80 damage per heads on three coins. With Victory Star (reroll once, after seeing the flips) the best policy
  is to keep two or three heads and reroll zero or one: final heads 3 / 2 / 1 / 0 with probability 3/16, 9/16, 3/16, 1/16, which
  is 150 damage on average (120 without the reroll) and 75% for two or more heads. Into a Grass Active add 20: 180 on two heads
  Knocks Out Vespiquen ex (140); Mega Sceptile ex (210) needs three heads (19%), or a second hit.
- **Magby** is the answer to the first-player turn with no energy: Toasty Toss costs nothing, so it can be used on turn 1 (a
  zero-cost attack is allowed on the first turn, `RULES_FOR_AGENTS.md`) and puts a [R] on a Benched Basic.

## The plan, by turn

First player (no energy on turn 1, no evolving):
1. **Turn 1.** Magby Active; bench Houndour and Entei ex (or Victini). **Toasty Toss**: [R] on the Houndour.
2. **Turn 2.** Attach [R] to the Houndour (two), evolve it into Mega Houndoom ex, Magby uses Toasty Toss again (Entei gets [R]).
3. **Turn 3.** Attach (Houndoom has RRC), retreat Magby for nothing, Houndoom is Active: **Grimhound Flare**, Victory Star on the
   coins, 150 on average. Entei ex is the second attacker: it holds the one [R] from the second Toasty Toss, Blazing Beatdown is 60 with
   two energies and 120 with four, and it draws a card at the end of every turn it is Active.
4. **Later.** Rainbow Cave (discard the Zone energy) feeds Flame Patch, which puts a [R] from the discard on the Active: with both
   in hand that is one extra energy a turn. Cyrus finishes a damaged Benched Pokémon.

Second player (energy on turn 1): the same a turn earlier, and the best case is Grimhound Flare on turn 2 (energy on turns 1 and 2
plus one Toasty Toss on turn 1, then evolve, retreat Magby for free and attack). That needs Magby, Houndour and Mega Houndoom ex in the first hands, which is not usual.

## Interactions and engine support

Engine: all 11 ids are in the coverage; **Victini (B3 025) is "Implemented with unverified rule boundaries"** and no other card has a
status or named limitation. The Victory Star text is "supports printed attack-effect coin batches; confusion and attacker-side coin
gates currently bypass the reroll prompt pending Pocket rule verification".

- **Victory Star on the Bench works**: the text has no Active requirement. One use a turn across all copies, so the second Victini
  is a spare, not a second reroll. It rerolls Mega Houndoom ex's three coins (a printed attack-effect coin batch, supported).
- **Victory Star is not offered while the attacker is Confused in the official engine.** The game offers it after the Confusion
  coin shows heads (Dustin's recordings, `rules/09`, `rules/04` section 9). The repair is in the rules switch's candidate, not in the
  official engine yet. A Confused Houndoom is an edge case, but a floor page run before the pin would not include the repair.
- **Toasty Toss targets a Benched Basic only**: Houndour, Entei ex, Victini, not Mega Houndoom ex (Stage 1). Energy for the Houndoom
  comes from the turn's attachment, Toasty Toss on the Houndour before it evolves, and Flame Patch once it is Active.
- **Flame Patch needs a [R] in the discard pile and a Fire Pokémon Active.** Rainbow Cave is the source of the discard; it is
  symmetric, and a multi-type opponent can use it as well.
- Magby's retreat is 0 and Entei ex's is 2: Magby is the free pivot into Entei ex or Houndoom, not the other way.

## What the bot may get wrong in a test

- **Victini is flagged (engine status), with the default role "attacker".** Its job is the passive Ability. On a floor page a
  fail, borderline or untrusted verdict would be marked provisional on that default; the role is Dustin's to set on the page.
- Keep or Reroll is a search choice over the coin outcomes; three coins and one reroll is a small tree, so I do not expect a
  pricing hole beyond the Confusion bypass above. Run the page after the pin.
- Entei ex's draw and Magby's zero-cost Toasty Toss are not flagged. A first-turn Magby needs the bot to see "attack with nothing
  to deal damage" as worth it; whether km3 plays it on turn 1 is a thing to read in the trace, not to assume.

## Versus the panel decks he loses to

**Sceptile and Vespiquen: +20 on every hit, and Grimhound Flare is 180 on two heads.** Cousin brew 08 scored 65% and 83% against them
on the floor. **Weak against Suicune** (Water hits every Pokémon in the list for Weakness, and Suicune ex's Crystal Waltz scales
with benches), **Lucario** (four ex into Arena and Korrina; cousin 08 scored 54%) and **Blaziken** (mirror, and Mega Blaziken's
Burn; cousin 08: 36%). Draft D is the draft that is aimed at one half of the panel and accepts the other.

## What would make me drop it

Mega Houndoom ex Knocked Out (three points) before its first attack; Houndoom, Houndour and Magby all missing from a game's first
eight cards in too many games on the floor page's "could attack with a main attacker by turn 3" line; a floor page where Victini's
use is under 25% for a reason other than the Confusion gate.
