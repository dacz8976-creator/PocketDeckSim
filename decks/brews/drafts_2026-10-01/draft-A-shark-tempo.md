# Draft A: Shark Tempo (Water)

Draft, not run, not a ranking. List: `draft-A-shark-tempo.txt`. Written Oct 1, 2026 by the Sonnet session "Opus agents progress".

## The list (Water energy)

| # | Card | Id | Text (from the database) |
|---|---|---|---|
| 2 | Carvanha | B4 034 | Water Basic, HP 50, weak Lightning. [W] Sharp Fang 30 |
| 2 | Mega Sharpedo ex | B4 035 | Water Stage 1 from Carvanha, HP 190, weak Lightning, retreat 0. [W] Turbo Shark 70: take a [W] Energy from your Energy Zone and attach it to 1 of your Benched [W] Pokémon |
| 2 | Alolan Vulpix | B2 028 | Water Basic, HP 60, weak Metal. [W] Gnaw 20 |
| 2 | Alolan Ninetales ex | B2 029 | Water Stage 1 from Alolan Vulpix, HP 150, weak Metal, retreat 2. [WW] Binding Snow 80: during your opponent's next turn they can't take any Energy from their Energy Zone to attach to their Active Pokémon |
| 1 | Lapras | A3 044 | Water Basic, HP 110, weak Lightning, retreat 2. [WWC] Surf 70 |
| 2 | Misty | A1 220 | Supporter: choose 1 of your [W] Pokémon, flip a coin until you get tails; for each heads take a [W] Energy from your Energy Zone and attach it to that Pokémon |
| 2 | Professor's Research | P-A 007 | Supporter: draw 2 cards |
| 2 | Poké Ball | P-A 005 | Item: put a random Basic Pokémon from your deck into your hand |
| 1 | Copycat | B1 225 | Supporter: shuffle your hand into your deck, draw a card for each card in your opponent's hand |
| 1 | Cyrus | A2 150 | Supporter: switch in 1 of your opponent's Benched Pokémon that has damage on it |
| 1 | Irida | A2a 072 | Supporter: heal 40 damage from each of your Pokémon that has any [W] Energy attached |
| 1 | Elegant Cape | B3b 065 | Tool: the Stage 1 Pokémon it is attached to gets +30 HP |
| 1 | Lucky Ice Pop | B2 145 | Item: heal 20 from your Active; if you healed any, flip a coin, heads puts it back in your hand |

Nine Pokémon (five Basics), eleven Trainers. Four ex: Mega Sharpedo ex gives three points when Knocked Out, Ninetales ex two.

**Amended Oct 1 (evening).** The first version ran Lapras ex (P-A 014: WWC 80, heal 20, HP 140, retreat 3, an ex). That card exists
only as a promo, and Dustin joined after it (the coordinator's note), so he cannot have it. The database has no other printing
of Lapras ex. The nearest card he can have is the plain **Lapras A3 044**: the same cost (WWC) and role, a third Basic to receive
Turbo Shark's and Misty's energy, 70 damage instead of 80, no self-heal (Irida, Lucky Ice Pop and the Cape do the healing), HP 110
instead of 140, retreat 2 instead of 3, and **no ex**, so the deck has one fewer two-point Knock Out to give away and one fewer card
for Arena of Antiquity and Korrina to punish. Other Water options that Dustin can have were weighed and not taken: Chien-Pao ex
(B2a 037, a WWW snipe for 130, but another ex) and Palkia ex (A2 049, WWWC for 150, but four energies).

## Why it exists

Dustin is 0-5 against the Fire decks on the ladder (Mega Charizard Y ex / Entei ex 0-3, Mega Blaziken ex 0-2), and Water is the type
that hits them for Weakness. The deck's whole plan is one card, Mega Sharpedo ex: **one Water energy buys 70 damage (90 against a
Fire Active) and puts a free energy on the Bench every turn.** Tempo: the first attack comes on your turn 2 for one energy, and the
second attacker is armed by turn 3 without spending the turn's attachment on it.

## The plan, by turn

Going second (you get an energy on your turn 1):
1. **Turn 1.** Carvanha Active, Alolan Vulpix on the Bench (Poké Ball and Research to find them), attach [W] to Carvanha.
2. **Turn 2.** Evolve Carvanha into Mega Sharpedo ex (it was played last turn). Attach, or play Misty on the Vulpix instead, and
   **Turbo Shark**: 70 (90 into Fire). One hit Knocks Out anything with 60 HP or less: Torchic, Riolu, Treecko, Houndour,
   Frigibax. The attack puts a [W] Energy on the Benched Vulpix.
3. **Turn 3.** Evolve Vulpix into Alolan Ninetales ex (it already holds one or two [W]). Either **Binding Snow** (80, and the
   opponent cannot attach from the Energy Zone to their Active next turn, so a Mega Lucario or Mega Blaziken waiting for its
   second energy stays a turn behind) or Turbo Shark again. Mega Sharpedo ex retreats for free, so the damaged one swaps out.
4. **Turn 4 on.** Irida, Lucky Ice Pop and the Cape keep Mega Sharpedo ex alive; Cyrus pulls up a damaged Benched Pokémon to
   finish it; the second Mega Sharpedo ex comes in off the second Carvanha. The win is a mix of one-hit Knock Outs on small Basics
   and two or three hits on the ex and Mega Actives.

Going first (no energy on turn 1, no evolving): the same, one turn later for the first attack: turn 1 bench Carvanha and Vulpix,
turn 2 attach and evolve, Turbo Shark.

## Interactions and engine support

Engine: all 13 card ids are complete in the official release's coverage (`goldfish --games 0 --coverage`), with no named limitation.
This is dispatch coverage, not a rules verification of each text.

- **Turbo Shark needs a Benched Water Pokémon** to receive the energy (Carvanha, Vulpix, Lapras, a second Mega Sharpedo ex,
  Ninetales ex). Keep one on the Bench or the attack does only its 70.
- **Binding Snow blocks only the attach from the Energy Zone to their Active.** They can still attach to the Bench and retreat.
  Whether it also stops Energy Zone abilities that attach to their Active (Baxcalibur's Ice Maker is in the panel) is not something
  I read in the engine; check before relying on it against Suicune.
- **Misty is a coin-until-tails Supporter**: expected one energy, sometimes none, sometimes three. Put it on a Benched Water Pokémon
  the turn Turbo Shark is not enough.
- **Elegant Cape fits Stage 1 only**: Mega Sharpedo ex (190 to 220) and Ninetales ex (150 to 180), not Lapras.
- **Training Area (their stadium) is symmetric**: it gives Stage 1 attackers +10 on both sides, Mega Lucario ex included.

## What the bot may get wrong in a test

- **Binding Snow is flagged**: "pays off during the opponent's turn, which the search doesn't play out". km3 may pick another Turbo
  Shark over Binding Snow, so Ninetales ex looks weaker on a floor page than it plays. Its default role is "attacker"; if the page
  shows it used on under 25% of its chances, that is this flag, not the deck.
- Misty is not flagged. Turbo Shark's benefit (energy on the Bench) is read only through the leaf value of the position.
- The t-lucario list carries Arena of Antiquity and Korrina, which km3 prices, so a floor page against it shows the ex penalty for
  real, not as a bot error.

## Versus the panel decks he loses to

**Blaziken and Charizard Y / Entei: Water hits them for Weakness (+20 on every Turbo Shark) and one energy buys the hit.** Deck 13,
which shares Ninetales ex, scored 72% against the panel's Blaziken on its floor page. **Weak against Lucario** (four ex, Arena +20
and Korrina +30 against an ex Active; Mega Sharpedo ex with the Cape has 220 HP against up to 210 before Weakness) and against
Lightning (Magnezone / Miraidon, Manectric). Suicune is a Water mirror and I claim nothing there.

## What would make me drop it

Mega Sharpedo ex Knocked Out (three points) before it has done its two hits; a Field Blower on the Cape; going second into a
Training Area Lucario.
