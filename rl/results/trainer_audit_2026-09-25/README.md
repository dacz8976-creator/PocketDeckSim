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

**Next:**
- Check each flagged card against the bot's score (`value_functions.rs` and kp3's priced texts): is its effect visible at all? The first list goes to the Tool and turn-effect candidate's card census.
- A follow-up run on Field Blower targets and Stadium play, per Dustin's note that Pocket's own AI also misjudges Stadiums.
