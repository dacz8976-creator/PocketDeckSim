# How kp3 plays its Trainer cards (Sept 25 audit)

**In plain words:** the bot puts almost every Pokémon Tool on its Active Pokémon, whatever the Tool does.
- Protective Poncho only protects a Benched Pokémon, but 492 of 494 Ponchos went onto the Active. In most of them it never protected anything:
  - Lucario, a meta deck: 108 of 149 (72%)
  - Dustin's deck 05: 131 of 176 (74%)
  - brew 06b: 140 of 169 (83%)
- Other Tools went onto Pokémon they can never help:
  - Small Balloon (Basic Pokémon only) on Espeon, Igglybuff (Retreat Cost 0 already) and Mega Altaria ex: 80 of 167 in Altaria, also a meta deck.
  - Heavy Helmet (Retreat Cost 3 or more) on Glimmora and Indeedee ex: about half of deck 01's Helmets, and a quarter of deck 03's.
  - Elegant Cape (Stage 1 only) on Comfey, which never evolves, and on Basics that never evolved while wearing it: about a third in decks 09, 13 and 14.
  - Metal Core Barrier and Steel Apron on Indeedee ex in deck 07: 17-18%.
- Cards whose payoff comes on the opponent's turn are almost never played:
  - Jasmine: 1.2% of the turns it was playable.
  - Cheren: 2.3%.
  - Team Rocket's Goo-zooka: 2-5%.

This matches the blind spot found earlier today (`../skarmory_tool_jasmine_2026-09-25/`). The bot's score gives a flat bonus for having any Tool on the Active, and it never sees an effect that lands after its own turn ends. So it prefers the Active for every Tool and doesn't value Jasmine, Cheren or Goo-zooka. Two meta decks (Lucario, Altaria) are affected, so this reaches the Limitless table, not only Dustin's decks and brews.

**What was run:**
- **Games:** kp3 on both sides; each of the 36 decks (research, dustin, brews) against the 8 lists in `decks/screen/opponents`; 15 games per opponent per seat. That makes 240 games per deck and 8,640 in all.
- **Engine and load:** the official engine `rl/engine-2026-09-25/deckgym`, one thread per call at the lowest priority.
- **Seeds:** 21,104,000,000 + 10,000 × deck index + 1,000 × opponent index (+500 for seat 1).
- **Script:** `trainer_audit.py`. Games file: `games.jsonl.gz` (sha256 of the unzipped file 6e51dbb8…736965a); `plan.json` lists the decks and opponents.
- **Checked beforehand:** two independent checkers checked the Tool rules and windows against the card texts and the engine before the run.

**What's counted:**
- **Trainers** (`audit_trainers.tsv`): for each deck and card, the turns it was playable (for a Supporter, only turns with no other Supporter played) and the turns it was played. A low rate can be right (Team Rocket's Boss with no good target), so the list below is a list of things to check, not of bugs.
- **Tools** (`audit_tools.tsv`, `useless_tools.txt`): each physical Tool is followed from attachment until it leaves, across evolution. It is useless if either:
  - its holder never met the Tool's own condition (type, stage, Retreat Cost); or
  - it had chances to act and never could. For HP and damage Tools, a chance is the opponent's turn, with Poncho counting only while Benched. Rocky Helmet and Poison Barb count the opponent's attacks while on the Active. Deceptive Needle counts the owner's end of turn on the Active. Small Balloon and Inflatable Boat count the owner's retreats.
  - Tools attached as the game ended had no chance to act; they are flagged, not counted as useless.
- **Limits:**
  - Heavy Helmet uses the printed Retreat Cost here. Dustin confirmed tonight that the game uses the current one; no holder in these decks had its cost changed.
  - Elegant Cape on a Basic that was meant to evolve counts as useless only when it never did while wearing the Cape.
  - "Worked" means the Tool was in a place where it could act. It does not check that damage actually came.

**Tools with the most waste** (from `useless_tools.txt`; the full list is there):

| deck | Tool | attached | on the Active at attach | useless | main holders |
|---|---|---:|---:|---:|---|
| brew-06b | Protective Poncho | 169 | 169 | 140 (83%) | Ogerpon ex, Type: Null, Scyther, Silvally |
| dustin 05 | Protective Poncho | 176 | 175 | 131 (74%) | Indeedee ex, Lillipup, Stoutland |
| **research Lucario** | Protective Poncho | 149 | 148 | 108 (72%) | Mega Lucario ex, Riolu, Bonsly, Hitmonlee |
| **research Altaria** | Small Balloon | 167 | 166 | 80 (48%) | Espeon, Igglybuff, Mega Altaria ex |
| dustin 01 | Heavy Helmet | 210 | 209 | 100 (48%) | Glimmora, Glimmet, Alolan Grimer |
| dustin 14 | Elegant Cape | 169 | 144 | 62 (37%) | Comfey, Drowzee, Rattata |
| dustin 13 | Elegant Cape | 162 | 148 | 52 (32%) | Rattata, Alolan Vulpix |
| dustin 09 | Elegant Cape | 154 | 142 | 49 (32%) | Electrike, Helioptile |
| dustin 03 | Heavy Helmet | 385 | 352 | 107 (28%) | Indeedee ex |
| dustin 08 | Small Balloon | 159 | 159 | 42 (26%) | Garchomp, Gabite |
| dustin 07 | Steel Apron | 146 | 145 | 26 (18%) | Indeedee ex |
| dustin 07 | Metal Core Barrier | 274 | 274 | 47 (17%) | Indeedee ex |

Tools that work anywhere, or that belong on the Active, show little or no waste: Giant Cape, Lucky Egg, Leaf Cape in Grass decks, Deceptive Needle in Darkness decks, Inflatable Boat. Rocky Helmet shows 3-9%.

**Trainers playable in 30 or more games but played on under 15% of those turns** (from `analyze_audit.py`):
- **Effect lands on the opponent's turn:**
  - Jasmine (deck 07): 1.2%
  - Cheren (deck 05): 2.3%
  - Team Rocket's Goo-zooka: 2.1-4.6% in brews 03a and 03b and decks 14 and 15
- **Stadium:** Rainbow Cave: 6.7-9.6% in brew 08 and decks 08 and 11.
- **Situational; may be right:**
  - Team Rocket's Boss: 2.7-2.8% (brew 02, Suicune)
  - Pokémon Flute: 1-2% (decks 08, 14)
  - Ilima: 3.5-13% (decks 13, 15)
  - Iris: 5.9% (deck 11)
  - Will: 10% (brew 01)
  - X Speed: 12% (brew 05)

## What kp3's score can see, card by card (census, same evening)

Every Trainer card in the 36 decks, 61 in all, was checked in the code: can kp3's score see what the card does? Three readers each took a group (Tools, Supporters, Items and Stadiums), and a skeptic for each group tried to refute every row from the code. The skeptics made 25 corrections, all but three about wording; they are kept per card in `census.json`. The three that changed a class: Goo-zooka is partly read, not unread, because Whimsicott ex's Grass Knot in deck 12 reads the raised Retreat Cost in the same turn. Small Balloon and Inflatable Boat pay off on later turns. The table is `census_table.md`.

**In plain words:**
- **Tools.** Every Tool gets the same +10 when it sits on the bot's Active, whatever it does and whoever holds it (`value_functions.rs` 516, 667-672).
  - The score actually reads only these: the HP Capes (Giant Cape, and Leaf or Elegant Cape on a holder that qualifies), and the Active's Retreat Cost, for Small Balloon and Inflatable Boat.
  - Damage cuts and damage back are not read at all: Heavy Helmet, Metal Core Barrier, Rocky Helmet, Poison Barb, and Lucky Egg's draw.
  - Protective Poncho is read backwards: +10 on the Active, where it does nothing, and nothing on the Bench, where it works.
- **Anything that happens on the opponent's turn is invisible.** The search stops at the end of the bot's own turn. The score has no term for turn effects, Special Conditions or the opponent's Retreat Cost. So:
  - Jasmine and Cheren: not read.
  - Goo-zooka: read only through Grass Knot.
  - Stadiums: their value on later turns isn't read, for either player.
- **Team Rocket's Boss is invisible for a different reason.** The search can't see the opponent's hand, and an unknown card is never counted as a Basic.
- **What pays off inside the bot's own turn is read correctly:**
  - draws: Professor's Research, Copycat;
  - gusts: Cyrus, Sabrina;
  - damage boosts: Red, Korrina, Cynthia;
  - heals: Erika, Lillie;
  - Rare Candy, Flame Patch, X Speed and the rest.
  - When the bot attacks into the opponent's Tools, their effects are priced too, because that happens on the bot's turn.
- **A search-length cost.** A Tool, and any card that needs a target, uses 2 of the bot's 3 search actions. This makes long turns harder to see.

**For the Tool and turn-effect candidate's two switches:**
- **Switch 1, temporary reductions and turn effects in the clock:**
  - Jasmine, Cheren, Metal Core Barrier, Heavy Helmet, Steel Apron.
  - kd already has a path for the Tools: `persistent_defender_damage`.
  - Rocky Helmet and Poison Barb need damage back to the attacker credited the same way.
- **Switch 2, the flat +10 replaced by what each Tool does for its holder:**
  - This is where the waste measured above comes from: Poncho, Small Balloon, Elegant Cape, Heavy Helmet, Metal Core Barrier, Steel Apron on holders they can't help.
  - Field Blower, Guzma and Repel inherit the same +10 from the other side: removing any Tool from the opponent's Active scores +10, whatever it did.
  - Meta decks carrying these Tools: Lucario (Poncho), Altaria (Small Balloon), Blaziken (Rocky Helmet), Hydreigon and Weezing (Deceptive Needle), Suicune (Giant Cape, Inflatable Boat), Sceptile and Vespiquen (Leaf Cape). Field Blower is in six of the eight.
- **Outside both switches (later candidates):**
  - a Stadium's value over later turns;
  - the opponent's Retreat Cost (Goo-zooka, Peculiar Plaza);
  - Special Conditions on either Active (Pokémon Center Lady, Team Rocket's Master Plan);
  - Team Rocket's Boss and the hidden hand.

**Side confirmation:** two agents independently confirmed the Rare Candy vs Aerodactyl ex rules bug in the code.
- The only Primeval Law check is in ordinary evolution (`move_generation/mod.rs` 252-258, 270-282).
- `can_play_rare_candy` (`move_generation_trainer.rs` 663-685) and `rare_candy_effect` (`apply_trainer_action.rs` 1905-1928) skip it.

**Next:** a follow-up run on Field Blower targets and Stadium play, per Dustin's note that Pocket's own AI also misjudges Stadiums.
