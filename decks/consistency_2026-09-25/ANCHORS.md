# Consistency harness (A1): anchors and the answer to D1

Built 2026-09-24, late evening, on branch `laptop/engine-first-2026-09-24` (`lib/consistency.py`); fix pass later
the same night after a review. There is one page per list in this folder. The table at the bottom is rewritten by
`--batch`; the text above it was written by hand from that run (10,000 solitaire deals per seat and 150 engine
games per pilot per list, on the same seeds as the first version, so old and new numbers are paired).

## D1: does the harness separate the anchors that did well from the ones that did badly?

**Not shown.** The tempo numbers are consistent with the ladder, but so is the number of Basics. Six anchors
(about four independent) can't separate a real signal from the three-Energy design confounder.

- **What lines up.** The headline reading (points given up before the list's first attack that does 30 or more
  damage, scripted pilot, mean of the two seats): Skarmory 0.29, Brew 1 (05b) 0.70, brew-03a 0.72, brew-01 1.32,
  Payback 1.44 and 1.50. That is the ladder order (3-1, 3-3, 1-3, 1-3, 0-3, 0-3). But 05b against 03a (0.70
  against 0.72) is a coin flip at this noise (about ±0.08 each). The clear gaps are Skarmory against the rest, and
  brew-01 and the two Payback lists against the rest.
- **What lines up just as well without any simulation.** The number of Basics in the list (3, 5, 6, 6, 7, 7:
  fewer Basics, better record) and the chance of opening with exactly one Basic (86, 63, 52, 52, 41, 41%) put the
  six anchors in the same order, 13 of 13 pairs. Nobody thinks a lone-Basic opening wins games. It lines up
  because a list with few Basics has a short, simple plan, and so does a list with a fast attacker.
- **The confounder.** The four losing lists attack with a three-Energy attacker (Arceus ex CCC, Silvally CCC).
  Skarmory attacks for MM and Brew 1 for PP after Rare Candy. Counting the Energy on the main attack sorts these
  six lists the same way. Six lists can't tell "the harness measures tempo" apart from "cheap attackers won".
- **Chance.** With about four independent anchors (06 and 06b are near-copies; 01 and 03a are both Arceus ex CCC
  lists), a measure with no real signal still puts them in perfect order about 1 time in 24. The order check under
  the table looks at 15 measures, and they are correlated with each other, so a handful of perfect orders is what
  luck plus the confounder would give anyway.
- **Which measures fail the order** (order check under the table): main attacker online by own turn 3 going
  second (4 pairs reversed), online by turn 4 (4), combo by turn 4 (7), points given up before the main attacker's
  first attack (1: Brew 1 0.81 against brew-03a 0.78), dead cards per turn (3), and the `aa` pilot's damaging
  attack by turn 3 (3). The card-finding numbers from the solitaire model do not order the anchors, except "main
  attacker online by own turn 3 going first", which is only the Energy cost again (0% for every three-Energy
  attacker). The ones in ladder order: the lone-Basic rate, the Basic count (reversed), the scripted pilot's
  attack-by-turn-3 and attack-by-turn-4 numbers, points given up before the first attack of any kind or of 30+,
  and the Lab's k3 screen.
- **Withdrawn: "0.4 against 0.7 points, about 3.5 standard errors".** That figure measured how precisely 150
  goldfish games pin down each list's number. It said nothing about the ladder. The ± figures in the table are
  the same kind of noise and are labelled that way.
- **The ladder itself** supports only one difference: Skarmory 3-1 against the Payback lists 0-6 (one-sided
  Fisher p ≈ 0.03). The gap between 3-3 and 1-3 is noise.
- **The pilot moves the numbers.** Fixing the scripted pilot (below) moved brew-07 from 0.43 to 0.04 points on the
  same seeds, a bigger change than the gap between Brew 1 and brew-03a. Read big gaps, not second decimals.

**One metric, picked now, and the real test.** The harness's reading of a list is **points given up before its
first attack of 30+ damage** (scripted pilot, mean of the two seats). I picked it before this re-run but after
seeing the first run's numbers, so the six anchors cannot test it. Brews 07-10's first ladder games are the real
test. The harness says: 08 Entei 0.00 and 07 Hoopa 0.04 (fastest), 09 Sableye/Obstagoon 0.29, 10 Diancie/Giratina
0.48 (slowest of the four; a 30+ attack by own turn 3 in only 5% of games going first). None of the four is near
Payback (1.44-1.50). To check it with a few games, note in each ladder game **how many points you had given up
when your deck first hit for 30 or more**. Real opponents are faster than this goldfish, so expect bigger numbers,
but the order should hold (10 slowest). If 07 or 08 keeps giving up 2 points before it attacks, the metric is
wrong.

### About the pilots

- **The `aa` and `et` bots do not work as pilots.** Both never bench a Pokémon, not even at setup: the engine lists
  End Turn first among the legal moves, and both bots fall back to the first move. So `aa` against `aa` is a
  one-Pokémon duel that ends at the first knockout, and `et` never attacks. Every page still has the `aa` row, as
  the brief asked, and it does not order the anchors (3 pairs reversed).
- The readings come from a **scripted pilot** (the solitaire model's priorities) playing the real rules4 engine
  through the pdl_rl_env 0.7.2 add-on, against the same `aa` bot. That opponent is one Active Pokémon, so its clock
  is fixed and slow.
- **Fixed in this pass** (from the review):
  1. **Lead.** The pilot led with the Basic with the most HP outside the main line. In Payback that was Team
     Rocket's Mewtwo (100 HP, retreat 2), which got no Energy and could neither attack nor retreat. The pilot now
     leads with a Basic whose Ability works from the Active Spot (Pyukumuku's Innards Out, Entei ex's Legendary
     Pulse) when it has one; `--lead` (or a 7th column in `lists.tsv`) overrides.
  2. **Retreat.** It used to put Energy on the Active for a retreat only when exactly one more would do. Now, once a
     Benched main or combo Pokémon can attack and the Active can't, the turn's Energy goes on the Active until it
     can retreat. But if a main or combo Pokémon in front can attack this turn with that Energy, it gets the
     Energy and attacks.
  3. **Abilities and Master Plan.** It now uses Abilities that damage the opposing Active (Crobat's Cunning Link)
     or give it a Special Condition (Meowstic's Perplexing Ears, and Weezing ex's Boiler Smog, which the engine
     offers as a yes/no choice after the evolution; the old pilot always said no). It plays Team
     Rocket's Master Plan when the Active's attack gains from Confusion that turn (Hatterene's Mental Crush). And
     it retreats Meowstic to a ready Hatterene when Hatterene would do 40+ more.
  4. **Measure.** "First damaging attack" counted chip damage (Hatenna's Stampede for 10 was Brew 1's first
     damaging attack in a third of games). The headline is now the first attack of 30+ damage or a knockout, and
     each page says which Pokémon made it. Poison or Burn already on the opposing Active before the attack no
     longer counts toward it.
  5. **Seats.** The coin gives each list a different split of games going first and second (brew-01 90/60, Brew 1
     66/84), and the seats differ a lot. Every figure over both seats is now the plain mean of the two seat means.
- **The k3 screen agrees where it exists** (Skarmory 57%, Brew 1 28%, Payback 8% and 16%; Lab `screen/results.md`),
  with the same caveat: four lists, and the same confounder.

## Do the failure modes match the ladder notes?

| Ladder note (Ladder Log) | What the harness says |
|---|---|
| Payback: "Hitmonchan ex and Great Tusk took both Pyukumukus for 2 points before Silvally had 3 energy"; lesson 8 | **Reproduced, as a speed problem.** Silvally needs CCC, one Energy a turn and none on the first turn, so going first it can't attack before own turn 4 (the solitaire model has it online by own turn 3 going first in 0% of deals). In the goldfish going first, Payback gives up 1.71 points before its first 30+ attack (06b: 1.90) and never makes one in 58% of games (69%). Going second: 1.17 (1.10). Over both seats, 1.44 and 1.50 are the worst of the 18 lists. In the games, the Pokémon in front are knocked out before Silvally has CCC, as in the note. Sometimes Darkrai ex's Nightmare Aura knocks out Pyukumuku, and Innards Out does not fire because that isn't an attack. **Correction:** the first version said the wall in front "has no Energy to retreat". That described a pilot fault (it led Team Rocket's Mewtwo and never paid its retreat), not the ladder. With the fault fixed, Pyukumuku leads in half the games and the numbers barely moved on the same seeds: 1.33 to 1.42 points before the first damaging attack, and Silvally attacks by own turn 4 in 35% both ways. They stay at 1.3-1.5 whether the pilot leads Comfey or plays Team Rocket's Mewtwo as the attacker. |
| Payback: "Opened with only TR Mewtwo" | 12% of openings (exact). |
| Payback: "Never drew Rocky Helmet" | The single Helmet is drawn or fetched by own turn 3 in 63% of games (61% in 06b). Missing it is a one-in-three event: expected, not bad luck. |
| brew-01: "Never drew crobat, or xatu… Probably need more draw cards"; "Arceus ex takes 3 energy… too difficult to draw cards you need" | **Matches.** Crobat is in play by own turn 3 in 51% of deals and Xatu in 70%. All three pieces are in play by turn 4 in 45%, the lowest of the anchors (Skarmory 96%). Arceus ex is online by own turn 3 going first in 0% of deals. Going first, the list makes a 30+ attack by own turn 3 in 1% of games and gives up 1.73 points first. The pilot now uses Crobat's Cunning Link (30 a turn with Arceus in play), but that is an Ability, not an attack, so the tempo reading leaves it out. |
| Brew 1 (05b): "comfey the only basic to start" | 13% of openings (exact). The list opens with a single Basic 63% of the time. |
| Brew 1: "I don't have the second meowstic or hatterene" | Hatterene is in play by own turn 3 in 51% of deals and by turn 5 in 74-76%. Without Rare Candy it is 0%, because the list has no Hattrem. Rare Candy and Hatterene are the cards most often stuck in hand at the end of a turn (43% and 36% of turn-ends). **Its good "any damaging attack" number is mostly chip damage:** Hatenna or Espurr made the first damaging attack in 38% of games. On 30+ attacks, Brew 1 (0.70) sits next to brew-03a (0.72). The first 30+ attack comes from Hatterene in 69% of games and Meowstic in 20%. With Perplexing Ears, Master Plan and the Meowstic-to-Hatterene retreat now played, the points given up before Hatterene's first attack fell from 1.10 to 0.81 on the same seeds. That is still worse than brew-03a's 0.78, so this measure does not order the anchors. |
| brew-03a: "Teal mask ogerpon prevented poison" | This is a matchup fact. The harness has no opponent that cures conditions, so it cannot test this. |
| Skarmory 3-1 (no loss notes) | Best on every tempo number. Skarmory ex attacks by own turn 4 in 98% of games, with 0.29 points given up first. Its dead cards are extra Supporters (Red in 38% of turn-ends). |

## The new brews (07-10), unplayed

All four sit on the fast side of the table, next to Skarmory and the tournament lists. None has Payback's tempo
hole. The harness says nothing about matchups.

- **08 Entei (Rainbow Cave + Flame Patch)** is the fastest of all 18 lists. Its only Basics are the two Entei ex,
  so an Entei always starts. A 30+ attack comes by own turn 3 in 100% of games, with nothing given up first. The
  three pieces are together by turn 4 in 84% of deals.
- **07 Hoopa / Darkrai / Sableye**: 0.04 points given up first (0.43 in the first version: the pilot fault that hit
  Payback hit this list harder, with Darkrai ex (retreat 2) stuck in front). The first 30+ attack is Hoopa ex's
  one-Energy Shadow Bullet (30) in 94% of games. Its DDC attack (Dynamite Punch) is 0% online by own turn 3 going
  first.
- **09 Sableye / Obstagoon**: 0.29. Mega Sableye ex is online by own turn 3 in 92% of deals. Obstagoon is the slow
  half (Rare Candy only, no Linoone), so the combo is together by turn 4 in 63%.
- **10 Diancie / Giratina**: 0.48, the slowest of the four. Going first, a 30+ attack by own turn 3 comes in only
  5% of games, but Diancie attacks by turn 4 in 81% overall, and the combo is together by turn 4 in 90%.

## Tournament lists, for scale

Across the eight panel lists: main attacker online by own turn 3 in 41-88% of deals (Stage 1 and Stage 2 Megas:
41-73%), 0.24-0.90 points given up before the first 30+ attack, and combo by turn 4 in 27-82% (Lucario's Mega
Lucario ex plus Lucario is 27%). Altaria (about 53% on Limitless) gives up 0.90, between brew-03a (0.72) and
brew-01 (1.32). Consistency
alone does not make these lists good; most of them are merely "not slow". A bad tempo number is a warning, not a
verdict. Do not rank lists on it.

## Coverage flag, in short

15 of the 18 lists carry an (a) card, almost always Copycat. Hydreigon adds Mega Absol ex's Darkness Claw, Weezing
adds Mars and Suicune adds Team Rocket's Boss; blind k3 leaves these unpriced. Sceptile's Caterpie is also flagged,
because its automatic Quick Growth leaves the opposing bot's end of turn unpriced. (b), an attack whose extra damage
the bots never see, hits several main attackers:
- Silvally's Gold Breaker is read as 60 against an ex (150 on the card).
- Hatterene's Mental Crush is read as 70 against a Confused Pokémon (140 on the card).
- Also hit: Galarian Obstagoon, Team Rocket's Scyther, Vespiquen ex, Riolu, Xatu's Life Drain, Toxapex's Severe
  Poison and Mareanie's Venoshock.

So k3's position score (not the damage actually dealt in its searches) undervalues the main attackers of the Payback
lists and Brew 1, on top of whatever else it gets wrong. Every evolution
and every Trainer that changes the next exchange is invisible to the reply-search tiers (c). The per-card lists are
on each page.

## Limits

- Solitaire model: no opponent, no knockouts, no retreat. Setup by attack (Carbink's Glittering Gift, Tandemaus's
  Flock) is ignored, and Copycat assumes the opponent holds 4 cards.
- Scripted pilot: simple priorities. It now plays the damage and Special Condition Abilities and Master Plan
  above, but it never plays gusts or switching Supporters (Cyrus, Sabrina: this opponent never has a Bench),
  Red, Will or Team Rocket's Goo-zooka, and never plans a turn ahead. For example, it uses Perplexing Ears only
  when Meowstic is already in front, and retreats to Hatterene only when Hatterene is ready that turn.
- The tempo readings count attacks only. Damage from Abilities (Crobat's Cunning Link, Darkrai ex's Nightmare Aura)
  and from Tools (Rocky Helmet) is left out, so lists built on it (brew-01's Crobat, Weezing) look slower than they
  play.
- Damage is read at the opponent's next decision, after the Checkup. Poison and Burn already on the Pokémon are
  taken off; Checkup Abilities (such as a Darkrai that hurts an Asleep Pokémon) are not.
- The goldfish opponent is one Active Pokémon that never benches or plays a Trainer. Its clock is slow, and it can
  lose to retaliation alone (Payback beats its Hoopa ex with Innards Out, Rocky Helmet and Dynamite Punch's
  self-damage), so the "won" column means little.
- An engine behaviour I saw but did not check against the game: the engine let Giratina ex's Ability attach an
  Energy on the first player's own turn 1. The solitaire model does not allow that.

## How to run

In WSL, from the repo root:

    python3 lib/consistency.py decks/brews/<brew>.txt --main "<card>" --combo "<a>,<b>|<c>" [--lead "<Basic>"]   # about 35 s
    python3 lib/consistency.py --batch decks/consistency_2026-09-25/lists.tsv               # all 18, about 8 min
    python3 lib/consistency.py <deck> --goldfish 0                                           # no engine; any Python 3

Without `--main` or `--combo`, the harness infers them from the list (the page says so).

<!-- table:start (rewritten by lib/consistency.py --batch) -->
Run: 10,000 solitaire deals per seat, 150 engine games per pilot per list, seeds from 21,002,000,000 (list i: solitaire and scripted-pilot seeds 21,002,000,000 + 10,000·i, aa-pilot seeds that +5,000), opponent `decks/research/weezing.txt` piloted by aa. sp = scripted pilot on the real engine; aa = the engine's attach-and-attack bot as pilot. Every sp and aa figure is seat-balanced: the plain mean of the going-first and going-second means. "30+ attack" = the first attack that did 30 or more damage or knocked out; ± is its standard error over these games (simulation noise only, nothing about the ladder).

| List | Role | Ladder | k3 screen | Basics | 1-Basic open | Main online by T3 (1st / 2nd) | by T4 (1st / 2nd) | Combo by T4 (1st / 2nd) | sp: 30+ attack by T3 | **sp: pts conceded before the first 30+ attack** (± sim. noise) | sp: pts conceded before any damaging attack | sp: main attacks by T4 | sp: pts conceded before main | sp: dead cards/turn | aa: damaging attack by T3 | (a) cards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 07-skarmory-stall (main Skarmory ex) | anchor: did well | 3-1 | 57% | 3 | 86% | 95% / 95% | 97% / 97% | 96% / 96% | 77% | **0.29** ± 0.05 | 0.29 | 98% | 0.29 | 1.4 | 66% | 0 |
| brew-05b-meowstic-hatterene-comfey (main Hatterene) | anchor: middle | 3-3 | 28% | 5 | 63% | 51% / 50% | 64% / 63% | 53% / 52% | 60% | **0.70** ± 0.08 | 0.29 | 66% | 0.81 | 2.5 | 100% | 1 |
| brew-01-arceus-crobat-xatu (main Arceus ex) | anchor: did badly | 1-3 | - | 6 | 52% | 0% / 74% | 84% / 84% | 45% / 45% | 24% | **1.32** ± 0.10 | 1.00 | 46% | 1.32 | 2.4 | 80% | 0 |
| brew-03a-arceus-nihilego-toxapex (main Arceus ex) | anchor: did badly | 1-3 | - | 6 | 52% | 0% / 75% | 82% / 83% | 66% / 65% | 35% | **0.72** ± 0.08 | 0.72 | 48% | 0.78 | 0.7 | 70% | 0 |
| brew-06-pyukumuku-silvally-payback (main Silvally) | anchor: did badly | 0-3 | 8% | 7 | 41% | 0% / 72% | 83% / 83% | 83% / 84% | 15% | **1.44** ± 0.09 | 1.42 | 35% | 1.56 | 2.8 | 48% | 1 |
| brew-06b-pyukumuku-silvally-scyther-grass (main Silvally) | anchor: did badly | 0-3 | 16% | 7 | 41% | 0% / 72% | 83% / 83% | 84% / 83% | 12% | **1.50** ± 0.10 | 1.48 | 41% | 1.56 | 2.5 | 51% | 1 |
| brew-07-hoopa-darkrai-sableye (main Hoopa ex) | new brew (unplayed) | - | 62% | 4 | 75% | 0% / 85% | 91% / 91% | 78% / 78% | 82% | **0.04** ± 0.02 | 0.04 | 94% | 0.04 | 0.9 | 79% | 1 |
| brew-08-entei-rainbow-cave (main Entei ex) | new brew (unplayed) | - | 56% | 2 | 95% | 100% / 100% | 100% / 100% | 84% / 85% | 100% | **0.00** ± 0.00 | 0.00 | 100% | 0.00 | 2.3 | 100% | 1 |
| brew-09-sableye-obstagoon (main Mega Sableye ex) | new brew (unplayed) | - | 47% | 4 | 75% | 92% / 92% | 95% / 96% | 63% / 63% | 53% | **0.29** ± 0.04 | 0.25 | 71% | 0.38 | 2.0 | 100% | 1 |
| brew-10-diancie-giratina (main Mega Diancie ex) | new brew (unplayed) | - | 45% | 6 | 52% | 0% / 78% | 87% / 87% | 90% / 89% | 38% | **0.48** ± 0.07 | 0.48 | 81% | 0.54 | 2.6 | 9% | 1 |
| research-lucario (main Mega Lucario ex) | meta reference | Limitless ~50% | 52% | 4 | 75% | 72% / 73% | 80% / 81% | 28% / 27% | 83% | **0.24** ± 0.04 | 0.15 | 73% | 0.50 | 2.0 | 73% | 1 |
| research-altaria (main Mega Altaria ex) | meta reference | Limitless ~53% | 46% | 7 | 41% | 51% / 51% | 61% / 62% | 49% / 49% | 46% | **0.90** ± 0.09 | 0.63 | 41% | 1.17 | 2.2 | 73% | 1 |
| research-hydreigon (main Hydreigon) | meta reference | - | - | 4 | 75% | 53% / 53% | 65% / 66% | 55% / 56% | 53% | **0.65** ± 0.10 | 0.33 | 56% | 0.68 | 1.8 | 100% | 2 |
| research-weezing (main Hoopa ex) | meta reference (also the goldfish opponent) | - | - | 5 | 63% | 0% / 80% | 90% / 89% | 79% / 78% | 65% | **0.56** ± 0.07 | 0.49 | 77% | 0.59 | 1.8 | 87% | 2 |
| research-blaziken (main Mega Blaziken ex) | meta reference | - | - | 4 | 75% | 53% / 53% | 66% / 66% | 66% / 66% | 50% | **0.79** ± 0.08 | 0.32 | 60% | 0.92 | 2.9 | 79% | 1 |
| research-sceptile (main Mega Sceptile ex) | meta reference | - | - | 3 | 86% | 41% / 41% | 64% / 64% | 54% / 55% | 62% | **0.26** ± 0.04 | 0.26 | 40% | 0.50 | 2.7 | 100% | 2 |
| research-suicune (main Suicune ex) | meta reference | - | - | 5 | 63% | 87% / 88% | 92% / 92% | 75% / 74% | 62% | **0.61** ± 0.10 | 0.23 | 69% | 0.49 | 2.4 | 31% | 2 |
| research-vespiquen (main Vespiquen ex) | meta reference | - | - | 5 | 63% | 75% / 75% | 84% / 84% | 82% / 82% | 28% | **0.36** ± 0.08 | 0.36 | 72% | 0.34 | 1.7 | 100% | 1 |

### Order check on the 6 anchors

Pairs of anchor lists with different ladder records (the two 1-3 lists and the two 0-3 lists are not compared with each other): how many pairs each measure puts in the ladder's order. With only about four independent anchors (06 and 06b are near-copies; 01 and 03a are both Arceus ex CCC lists), a measure with no real signal still puts them in perfect order about 1 time in 24, and this table has 15 measures.

| measure | good direction | anchor pairs in ladder order | reversed | tied | reading |
|---|---|---|---|---|---|
| Basics in the list | none set (counted as higher) | 0 | 13 | 0 | exact reverse order |
| 1-Basic opening | none set (counted as higher) | 13 | 0 | 0 | ladder order |
| main online by T3, going first | higher | 9 | 0 | 4 | ladder order (with ties) |
| main online by T3, going second | higher | 9 | 4 | 0 | 4 inversions |
| main online by T4 (mean of seats) | higher | 7 | 4 | 2 | 4 inversions |
| combo by T4 (mean of seats) | higher | 6 | 7 | 0 | 7 inversions |
| sp: 30+ attack by T3 | higher | 13 | 0 | 0 | ladder order |
| **sp: pts conceded before the first 30+ attack (headline)** | lower | 13 | 0 | 0 | ladder order |
| sp: damaging attack (any) by T3 | higher | 13 | 0 | 0 | ladder order |
| sp: pts conceded before any damaging attack | lower | 12 | 0 | 1 | ladder order (with ties) |
| sp: main attacks by T4 | higher | 13 | 0 | 0 | ladder order |
| sp: pts conceded before the main attacker attacks | lower | 12 | 1 | 0 | 1 inversion |
| sp: dead cards per turn | lower | 9 | 3 | 1 | 3 inversions |
| aa: damaging attack by T3 | higher | 10 | 3 | 0 | 3 inversions |
| k3 screen (Lab) | higher | 5 | 0 | 0 | ladder order |

One line per list:

- 07-skarmory-stall: one-Basic opening 86%; Skarmory ex online by own T3 95% first / 95% second (T4 97%/97%); combo by T4 96%/96%; goldfish (scripted pilot v aa, seat-balanced): 0.29 pts conceded before the first 30+ damage attack (by own T3 in 77%), Skarmory ex attacks by T4 98% with 0.29 conceded first, 1.4 dead cards/turn; unpriced-text cards (a): 0
- brew-05b-meowstic-hatterene-comfey: one-Basic opening 63%; Hatterene online by own T3 51% first / 50% second (T4 64%/63%); combo by T4 53%/52%; goldfish (scripted pilot v aa, seat-balanced): 0.70 pts conceded before the first 30+ damage attack (by own T3 in 60%), Hatterene attacks by T4 66% with 0.81 conceded first, 2.5 dead cards/turn; unpriced-text cards (a): 1
- brew-01-arceus-crobat-xatu: one-Basic opening 52%; Arceus ex online by own T3 0% first / 74% second (T4 84%/84%); combo by T4 45%/45%; goldfish (scripted pilot v aa, seat-balanced): 1.32 pts conceded before the first 30+ damage attack (by own T3 in 24%), Arceus ex attacks by T4 46% with 1.32 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 0
- brew-03a-arceus-nihilego-toxapex: one-Basic opening 52%; Arceus ex online by own T3 0% first / 75% second (T4 82%/83%); combo by T4 66%/65%; goldfish (scripted pilot v aa, seat-balanced): 0.72 pts conceded before the first 30+ damage attack (by own T3 in 35%), Arceus ex attacks by T4 48% with 0.78 conceded first, 0.7 dead cards/turn; unpriced-text cards (a): 0
- brew-06-pyukumuku-silvally-payback: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 83%/84%; goldfish (scripted pilot v aa, seat-balanced): 1.44 pts conceded before the first 30+ damage attack (by own T3 in 15%), Silvally attacks by T4 35% with 1.56 conceded first, 2.8 dead cards/turn; unpriced-text cards (a): 1
- brew-06b-pyukumuku-silvally-scyther-grass: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 84%/83%; goldfish (scripted pilot v aa, seat-balanced): 1.50 pts conceded before the first 30+ damage attack (by own T3 in 12%), Silvally attacks by T4 41% with 1.56 conceded first, 2.5 dead cards/turn; unpriced-text cards (a): 1
- brew-07-hoopa-darkrai-sableye: one-Basic opening 75%; Hoopa ex online by own T3 0% first / 85% second (T4 91%/91%); combo by T4 78%/78%; goldfish (scripted pilot v aa, seat-balanced): 0.04 pts conceded before the first 30+ damage attack (by own T3 in 82%), Hoopa ex attacks by T4 94% with 0.04 conceded first, 0.9 dead cards/turn; unpriced-text cards (a): 1
- brew-08-entei-rainbow-cave: one-Basic opening 95%; Entei ex online by own T3 100% first / 100% second (T4 100%/100%); combo by T4 84%/85%; goldfish (scripted pilot v aa, seat-balanced): 0.00 pts conceded before the first 30+ damage attack (by own T3 in 100%), Entei ex attacks by T4 100% with 0.00 conceded first, 2.3 dead cards/turn; unpriced-text cards (a): 1
- brew-09-sableye-obstagoon: one-Basic opening 75%; Mega Sableye ex online by own T3 92% first / 92% second (T4 95%/96%); combo by T4 63%/63%; goldfish (scripted pilot v aa, seat-balanced): 0.29 pts conceded before the first 30+ damage attack (by own T3 in 53%), Mega Sableye ex attacks by T4 71% with 0.38 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1
- brew-10-diancie-giratina: one-Basic opening 52%; Mega Diancie ex online by own T3 0% first / 78% second (T4 87%/87%); combo by T4 90%/89%; goldfish (scripted pilot v aa, seat-balanced): 0.48 pts conceded before the first 30+ damage attack (by own T3 in 38%), Mega Diancie ex attacks by T4 81% with 0.54 conceded first, 2.6 dead cards/turn; unpriced-text cards (a): 1
- research-lucario: one-Basic opening 75%; Mega Lucario ex online by own T3 72% first / 73% second (T4 80%/81%); combo by T4 28%/27%; goldfish (scripted pilot v aa, seat-balanced): 0.24 pts conceded before the first 30+ damage attack (by own T3 in 83%), Mega Lucario ex attacks by T4 73% with 0.50 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1
- research-altaria: one-Basic opening 41%; Mega Altaria ex online by own T3 51% first / 51% second (T4 61%/62%); combo by T4 49%/49%; goldfish (scripted pilot v aa, seat-balanced): 0.90 pts conceded before the first 30+ damage attack (by own T3 in 46%), Mega Altaria ex attacks by T4 41% with 1.17 conceded first, 2.2 dead cards/turn; unpriced-text cards (a): 1
- research-hydreigon: one-Basic opening 75%; Hydreigon online by own T3 53% first / 53% second (T4 65%/66%); combo by T4 55%/56%; goldfish (scripted pilot v aa, seat-balanced): 0.65 pts conceded before the first 30+ damage attack (by own T3 in 53%), Hydreigon attacks by T4 56% with 0.68 conceded first, 1.8 dead cards/turn; unpriced-text cards (a): 2
- research-weezing: one-Basic opening 63%; Hoopa ex online by own T3 0% first / 80% second (T4 90%/89%); combo by T4 79%/78%; goldfish (scripted pilot v aa, seat-balanced): 0.56 pts conceded before the first 30+ damage attack (by own T3 in 65%), Hoopa ex attacks by T4 77% with 0.59 conceded first, 1.8 dead cards/turn; unpriced-text cards (a): 2
- research-blaziken: one-Basic opening 75%; Mega Blaziken ex online by own T3 53% first / 53% second (T4 66%/66%); combo by T4 66%/66%; goldfish (scripted pilot v aa, seat-balanced): 0.79 pts conceded before the first 30+ damage attack (by own T3 in 50%), Mega Blaziken ex attacks by T4 60% with 0.92 conceded first, 2.9 dead cards/turn; unpriced-text cards (a): 1
- research-sceptile: one-Basic opening 86%; Mega Sceptile ex online by own T3 41% first / 41% second (T4 64%/64%); combo by T4 54%/55%; goldfish (scripted pilot v aa, seat-balanced): 0.26 pts conceded before the first 30+ damage attack (by own T3 in 62%), Mega Sceptile ex attacks by T4 40% with 0.50 conceded first, 2.7 dead cards/turn; unpriced-text cards (a): 2
- research-suicune: one-Basic opening 63%; Suicune ex online by own T3 87% first / 88% second (T4 92%/92%); combo by T4 75%/74%; goldfish (scripted pilot v aa, seat-balanced): 0.61 pts conceded before the first 30+ damage attack (by own T3 in 62%), Suicune ex attacks by T4 69% with 0.49 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 2
- research-vespiquen: one-Basic opening 63%; Vespiquen ex online by own T3 75% first / 75% second (T4 84%/84%); combo by T4 82%/82%; goldfish (scripted pilot v aa, seat-balanced): 0.36 pts conceded before the first 30+ damage attack (by own T3 in 28%), Vespiquen ex attacks by T4 72% with 0.34 conceded first, 1.7 dead cards/turn; unpriced-text cards (a): 1
<!-- table:end -->
