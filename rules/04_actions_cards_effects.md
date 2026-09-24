# 04 — Actions and card types: Energy, retreat, switching, evolution, Abilities, Trainers, effects

Grades as in `01_game_structure.md`. Sources in `06_sources.md`. Card text quoted here is from the local
`deckgym-database.json`; use `python lib/card.py "<name>"` for anything not quoted.

---

## 1. Attaching Energy

- Once per turn, attach the Energy generated in your Energy Zone to your Active **or** a Benched Pokémon; "You can attach Energy of one type to Pokémon of a different type." [OFFICIAL] in-app Tips + [IN-GAME TEXT]
- There is no rule against attaching to a Pokémon put into play this turn. [INFERRED — no restriction in any source or UI message]
- Effects can forbid it ("Can't attach any Energy from the Energy Zone to Active Pokémon") or react to it (Jolteon ex's Electromagnetic Wall does 20 to the Pokémon the opponent attaches to, Active or Bench [OBSERVED]; Darkrai ex's Nightmare Aura). Some effects hit an "Energy limit" ("Unable to attach any more Energy as limit has been reached"). [IN-GAME TEXT]
- Card effects that attach Energy from the Zone are separate from the manual attachment and don't use it up. [OBSERVED 020124]
- If a player doesn't attach, the Energy is discarded at the end of the turn. [COMMUNITY]

## 2. Retreat

| Rule | Grade |
|---|---|
| **Once per turn.** "You can only retreat once per turn." | [OFFICIAL] in-app Tips + [IN-GAME TEXT] |
| "Discard 1 Energy from your Active Pokémon for each Colorless Energy symbol listed in its Retreat Cost. The discarded Energy can be of any type." Then **you choose** which Benched Pokémon becomes Active. **The player picks which Energy** when there's a choice (the game opens a "Discard" Energy picker). The same goes for an attack that says "discard X Energy" without saying "random" (Gouging Fire, Walking Wake). | [OFFICIAL] in-app Tips; player's choice [DUSTIN, 2026-09-22; his T6 video is with Astra for processing]. ⚠ The `unified1` engine doesn't let the player pick (retreat keeps Grass by a fixed rule; the two attacks discard at random) — `07` M7 |
| Cost reductions lower the Energy actually discarded, down to 0: X Speed (−1 this turn), Leaf (−2 this turn), Small Balloon (Basic, −1), Peculiar Plaza (Psychic −2), Wimpod's first-turn free retreat. Increases exist ("Retreat Cost is X more"). | card text + [OBSERVED] X Speed took a 1-cost Carvanha to 0 and it kept its Energy (024406) |
| Can't retreat when: Asleep or Paralyzed; an effect says so; no Benched Pokémon; not enough Energy; the Active is a Fossil. | [OFFICIAL] in-app Tips (Energy, Bench) + [IN-GAME TEXT] separate messages for each; Fossil = card text |
| Retreating does **not** end the turn; the new Active can attack. | [IN-GAME TEXT] |
| The retreated Pokémon keeps its damage and remaining Energy, and loses all Special Conditions and all effects of attacks on it. | [OFFICIAL] in-app Tips + Detailed Battle FAQ |
| Retreat is only a main-phase action on your own turn. | [OBSERVED second-altaria] |

## 3. Switching effects are not retreat

- Sabrina, Repel, Cyrus, Lana, Lyra, Skyla, switching Abilities (Greninja ex, Revavroom Metal Transport, Solgaleo ex, Celesteela…) and switching attack effects (Abra Teleport, Tapu Koko Volt Switch, Jumpluff ex) **cost no Energy, don't count as your retreat for the turn, and work on an Asleep/Paralyzed Pokémon**. [OBSERVED] "this is a Supporter-forced switch, not a retreat" (232035) + [COMMUNITY]
- Who chooses the new Active is printed on the card. "Switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)" — the **opponent** picks; seen four times with Sabrina. [OBSERVED] Cyrus/Lana/Umbreon ex: **you** pick one of their (damaged, for Cyrus) Benched Pokémon. [OBSERVED ×2]
- A card that can't do anything is blocked (Sabrina with an empty opposing Bench, Pokémon Flute with a full opposing Bench). [COMMUNITY] + [IN-GAME TEXT] "conditions … have not been met"
- "Moved from your Bench to the Active Spot this turn" (Scizor Gale Thrust) is true after **your own** retreat or switch during your turn, false after promotion following a Knock Out on the opponent's turn, and false if Scyther moved up and then evolved into Scizor. [OFFICIAL]

## 4. Evolution

| Rule | Grade |
|---|---|
| Play the Evolution card from hand onto the Pokémon it "Evolves from". As many evolutions per turn as you like. | [IN-GAME TEXT] |
| **Not on either player's first turn. Not on a Pokémon put into play this turn. Not twice on the same Pokémon in one turn.** Tips: "You can't evolve a Pokémon on its first turn in play." / "Neither player can evolve Pokémon on the first turn, whether they go first or second." Tutorial: "…or if it already evolved during this turn." | [OFFICIAL] in-app Tips + [IN-GAME TEXT] |
| Rare Candy (Basic → Stage 2) and Quick-Grow Extract print the same limits: "You can't use this card during your first turn or on a Basic Pokémon that was put into play this turn." | card text + [OBSERVED] Rare Candy use in several games |
| Exceptions are card-specific: Eevee's Boosted Evolution (while Active, can evolve on your first turn or the turn it's played — [OBSERVED accepted-232035, going second, turn 2]); Eevee ex (can evolve into any Eevee evolution; normal timing limits); Aerodactyl ex's Primeval Law stops the opponent evolving their **Active** from hand. Card effects that evolve are not stopped by the general limits unless they print them: **Wallace** works on your first turn [OBSERVED 150630, turn 1] and, per Dustin, on a Pokémon benched this turn [DUSTIN]; **Caterpie's Quick Growth** evolved it at the end of the opponent's first turn [OBSERVED 150630]. Rare Candy and Quick-Grow Extract print the limits, so they keep them. | card text; [COMMUNITY] pokemon-zone (Primeval Law = Active only) |
| **Kept on evolution: damage, all attached Energy, Tools.** "Even if a Pokémon evolves, it keeps all attached Energy and any damage." | [IN-GAME TEXT] + [OBSERVED] Tools kept (Leaf Cape Rowlet → Decidueye ex; Rocky Helmet Deino → Hydreigon; Elegant Cape Electrike → Mega Manectric) |
| **Removed on evolution: all Special Conditions.** | [OBSERVED] "Ivysaur recovered from being Asleep" + [COMMUNITY] |
| **Removed on evolution: effects of attacks on that Pokémon** ("can't attack next turn", "−20 damage next turn", "on the next turn, attacks do more damage"). "When a Pokémon evolves, any effects of attacks … or Special Conditions affecting the Pokémon end." | [OFFICIAL] in-app Tips (settles what was open question #5) |
| Evolving is not "moving to the Active Spot". | [OFFICIAL] Scizor ruling |
| Evolving can trigger Abilities: Team Rocket's Raticate ex Thieving Incisors, Team Rocket's Weezing ex Boiler Smog ("when you play this Pokémon from your hand to evolve"). | card text + [OBSERVED 232035] |
| **Mega Evolution ex**: evolves like any evolution from its printed pre-evolution (Mega Blaziken ex from Combusken; Rare Candy works from Torchic), or is itself a Basic (Mega Absol ex, Mega Diancie ex). It is worth **3 points** when Knocked Out. **Mega Evolving does not end your turn** — the Mega can attack the same turn. | [COMMUNITY] Bulbapedia, Game8 + [OBSERVED] Torchic → Mega Blaziken ex by Rare Candy then Mega Burning (234514); Swablu → Mega Altaria then attack (first-altaria); Carvanha → Mega Sharpedo ex then attack (220914) |
| Pokémon ex can be evolved forms (Charizard ex; Aerodactyl ex evolves from Old Amber). | card data |
| "Team Rocket's X" evolves only from "Team Rocket's Y" because that is the printed "Evolves from" name — not a separate rule. | card data (every Team Rocket's evolution in the database names a Team Rocket's pre-evolution) |
| Fossils evolve into their printed Pokémon (Helix → Omanyte, Old Amber → Aerodactyl / Aerodactyl ex, Root → Lileep, …). | card data |
| Devolving exists as an effect ("Devolved" log message). | [IN-GAME TEXT] |

## 5. Abilities

| Rule | Grade |
|---|---|
| Using an Ability does not end the turn and does not use up the attack — Crobat used Cunning Link, then attacked. Activated Abilities are used by tapping the Pokémon; "Some Abilities work all the time automatically even without you using them as long as the Pokémon is in play. Also, some Abilities work only if certain conditions are met." | [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED 025604] |
| **"Once during your turn" is per Pokémon**: two Indeedee ex each used Watch Over in the same turn; two Baxcalibur each used Ice Maker. | [OBSERVED 023511, 181914] |
| Abilities work from the Bench unless the text says "in the Active Spot"; Nightmare Aura fired both Benched and Active. | [OBSERVED 031901] + card text |
| **Passive same-name Abilities stack**: two Lucario = Fighting Coach +40. | [COMMUNITY] pokemon-zone |
| Special Conditions don't stop Abilities. | [INFERRED] — no source or message restricts them |
| Ability-negation: Alolan Muk's Power of Alchemy ("Basic Pokémon in play … have no Abilities") shut off both Suicune ex Legendary Pulses at once; Budew's Prickly Powder (JP ひりひりパウダー; "Itchy Pollen" in earlier notes). When a negation ends, passive Abilities work again (Mimikyu ex's Disguise works "on the first attack after an Ability-nullifying effect has worn off"). | [OBSERVED 181914] + [OFFICIAL] Mimikyu and Prickly Powder FAQs. ⚠ Engine: retaliation Abilities (Rough Skin family, Dragalge ex's Poison Point) and a few others ignore both negations (`07` M4) |
| Mimikyu ex's Disguise ("first damaged by an attack after coming into play") ignores non-attack damage and is skipped by attacks that ignore effects (Ledian's Swift). | [OFFICIAL] |
| Link Abilities (A2a) only work if you have Arceus or Arceus ex in play. | [COMMUNITY] Bulbapedia + card text |
| Whether a Pokémon that used a Basic's "once during your turn" Ability can use its evolved form's Ability after evolving that turn | Moot in the current card pool: no line has an activated Ability on both stages (Drizzile → Inteleon's Swift Shot triggers when the card is played to evolve, and a Pokémon can't evolve twice in a turn). See `05`. |

## 6. Trainers

### Supporters
- **One per turn** ("You can play only one Supporter card per turn"), on any turn including the first. Played Trainers go to the discard pile (Tools and Stadiums stay in play until removed). [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED]
- Some print conditions ("You can use this card only if…"). Kiawe ends your turn ("Your turn ends."). Some Abilities/attacks stop the opponent's Supporters ("Can't use Supporter cards"). [card text / IN-GAME TEXT]

### Items
- **Unlimited per turn** ("You may play as many Item cards as you like during your turn"). Two Clemont's Backpacks in one turn both added +20. [IN-GAME TEXT] + [OBSERVED trial-manectric]
- Item-lock effects exist ("Can't play Item cards"); Fossils are Items, so they are presumably blocked too. [IN-GAME TEXT; Fossil part INFERRED]

### Unplayable cards and "whiffs"
- The game **blocks** a Trainer/Ability/Tool/Stadium whose condition can't be met ("The conditions for using this Item card have not been met" etc.): healing with nothing damaged, Sabrina with no opposing Bench, Kid's Room with an empty hand, Pokémon Flute with a full opposing Bench. [IN-GAME TEXT] + [OBSERVED 020124] + [COMMUNITY]
- **Heal targets (Dustin, restated 2026-09-22):** healing cards can't be used on a full-HP Pokémon at all, whether as a target or to make the card playable. The one exception is Pokémon Center Lady ("Heal 30 damage… and it recovers from all Special Conditions"), which can target a full-HP Pokémon if it has a Special Condition. [DUSTIN] The `unified1` engine let Potion/Erika/Lillie/Marlon pick an undamaged target; `09` lists that as repaired.
- **The rule that decides it (Dustin):** "If you can't 'see' whether or not you can use it (the information is hidden), it lets you play the Supporter/Stadium/Item. If you clearly can't use the card based on the seen information, you cannot play it." [DUSTIN]
  - Visible = your hand, both boards, discard piles, and whether your deck has any cards left. Hidden = what is left *in* your deck.
  - Playable because the deck is hidden: Poké Ball with no Basics left (as long as the deck has cards) [OBSERVED + DUSTIN]; **Cabbie with no Stadium in the deck** [DUSTIN + OBSERVED 145205, 150630 — the game plays it and shows "There are no cards in the deck that can be the target of the effect."]; **Pokémon Communication with no Pokémon in the deck** [DUSTIN, "almost positive"]; a Stadium that searches for Grass Pokémon with none left in the deck [DUSTIN].
  - Blocked because it's visibly impossible: Misty with no Water Pokémon in play; Poké Ball or Professor's Research with an empty deck; **Pokémon Communication with no Pokémon in hand** [DUSTIN].
  - **Any card that draws is blocked when your deck is empty** — Dustin is "almost positive there are no exceptions" [DUSTIN]. **Copycat is the exception that proves it:** it shuffles your hand into the deck *first* and then draws, so it can be played with an empty deck [DUSTIN]. (Untested corner: Copycat with an empty deck and no other cards in hand.)
  - Exception: since v1.7.0 the named-card searches (Clemont, Gladion, Team Galactic Grunt) can be played even when you can *see* every named card is out of the deck (next bullet but one) [SINGLE source, confirmed in play: recording 152812, 04:27–04:30 — with both of Dustin's Silvally (each on its Type: Null) in play, Gladion was played and the game showed "There are no cards in the deck that can be the target of the effect."]. Before 1.7.0 they followed the rule. They are still blocked when the deck is empty [DUSTIN, same test] — that part follows the rule.
  - **A Supporter played for nothing still counts as "a Supporter played this turn."** In 152812 (turn 10) the empty Gladion powered Silvally's Brave Buddies (+50, 100 total). [OBSERVED] So a whiff can matter.
- Random searches **can** be played and find nothing: Poké Ball with no Basic left ("no eligible target", card used up), Mesagoza Heads with no Pokémon in deck. [OBSERVED 234514, 225430]
- **Searches for named cards can be played and find nothing, since v1.7.0 (Jul 29, 2026).** Clemont, Gladion and Team Galactic Grunt used to be unplayable once every copy of the named cards was out of the deck (sources differ on which zones counted); the 1.7.0 "rule changes for some cards" made them playable anyway. Searches that don't name cards (Serena, Juliana) could always be played for nothing. [SINGLE] JP blog (daradara-pokepoke.blog.jp/archives/14227362.html) quoting the notice: "山札から指定のカードを手札に加える効果などで、使用できない条件が一部変更になりました" ("for effects such as putting specified cards from the deck into the hand, some of the conditions under which a card can't be used have changed"). The printed card text did not change. Seen in play for Gladion (recording 152812); Clemont and Grunt not yet.
  ⚠ Engine (`deckgym-fork-s193/src/move_generation/move_generation_trainer.rs`): Clemont, Serena, Juliana always playable ✓. **Gladion still has the old block** (wrong — Dustin's test) (unplayable once 2 Type: Null + 2 Silvally are in play/discard, ~line 675). **Team Galactic Grunt is blocked unless a Glameow/Stunky/Croagunk is in the deck** (~line 1152). By Dustin's rule these deck-content checks are also wrong: **Cabbie** (blocked unless a Stadium is in the deck, ~1051) and **Pokémon Communication** (blocked unless a Pokémon is in the deck, ~655; its hand check is right). Probably also wrong by the same rule [INFERRED]: **Wallace** (blocked unless a matching Water evolution is in the deck, `card_logic/wallace.rs`) and the Tool-searching Ability check (`move_generation_abilities.rs` ~405, needs a Tool in the deck). Checks on whether the deck is *empty* (Poké Ball, Professor's Research) are right — and the same empty-deck block should apply to every "from your deck" card; the engine has none for Gladion, Clemont, Serena or Juliana (they're always playable), so those are wrong with an empty deck. Clean spec for the fix: a card that takes something from the deck is blocked only when the deck is empty, never because of what's in it. Low impact: a Supporter played for nothing only matters for hand size and "played a Supporter this turn" effects.
- "Up to N" / variable effects do as much as they can: Manaphy's Oceanic Gift with one Benched Pokémon; Team Rocket Grunt's 3 Heads discarded only the 2 Energy that existed. [COMMUNITY] + [OBSERVED 220914]

### Pokémon Tools
| Rule | Grade |
|---|---|
| Attach to your Active or Benched Pokémon; unlimited Tools per turn; **one per Pokémon** (Revavroom's Dual Customization allows 2 — two Sitrus Berries both triggered: 20→50→80). | [IN-GAME TEXT] + [OBSERVED trial-revavroom] |
| "Once a Pokémon Tool has been attached to a Pokémon, it remains attached until the Pokémon leaves play." Stays through retreat, evolution and turn changes. You can't take it off by choice. | [IN-GAME TEXT] + [COMMUNITY] Game8 JP |
| When the Pokémon leaves play (Knock Out, returned to hand by Ilima/Koga, discarded by Wild Swing), the Tool goes to the discard pile, never to the hand. | [COMMUNITY] + [OBSERVED 025604, 220914] |
| Removal effects: Field Blower (one Tool or the Stadium, yours or the opponent's — seen used on its owner's own Stadium), Guzma (all of the opponent's Tools), Starly's Pluck (before damage). | card text + [OBSERVED 000905] |
| Some Tools discard themselves: Lum Berry and Sitrus Berry after triggering, Metal Core Barrier at the end of the opponent's turn. | card text + [OBSERVED] |
| Conditional Tools re-check live (Heavy Helmet switched on/off as the holder's Retreat Cost changed through evolution). Whether Retreat Cost *changes* (Plaza, Ariados, Goo-zooka) also switch it is open (`05` #19). Historical `unified1` defect: Heavy Helmet also cut non-attack damage (`07` H2); repaired in rules1 and retained in active rules3. | [OBSERVED first-altaria] |
| Rocky Helmet: only while the holder is Active; only on attack damage; still fires if the holder is Knocked Out (see file 02). Poison Barb: poisons the attacker after it damages the holder. | card text + [OBSERVED] |

### Stadiums (from B2, Jan 2026)
| Rule | Grade |
|---|---|
| **One Stadium play per turn** ("You can't use any more Stadium cards this turn"), separate from the Supporter limit. Printed in the green rules box on every Stadium: "You may play only 1 Stadium card during your turn. Put it next to the Active Spot, and discard it if another Stadium comes into play. A Stadium with the same name can't be played." Seen in play: Arcade refused after Mesagoza that turn (Dustin's T10 video, 2026-09-22). ⚠ `unified1` has no such limit (`07` M6); repaired in the verified `0.1.0-pdl.rules1` build (`09`). | [OFFICIAL] printed rules box + [IN-GAME TEXT] + [OBSERVED T10] |
| **Only one Stadium in play.** A Stadium with a **different name replaces** the one in play — yours or your opponent's — and the old one is discarded. | [IN-GAME TEXT] tutorial ("We discarded the Stadium that your opponent put in play…") + [OBSERVED] 000905, 181914 |
| **You can't play a Stadium with the same name as the one in play.** | [IN-GAME TEXT] |
| **Stadiums affect both players.** Starting Plains gave +20 HP to Basics on both sides; Training Area boosted the opponent's Stage 1 too. | [IN-GAME TEXT] + [OBSERVED ×5] |
| "Once during each player's turn, that player may…" Stadiums (Mesagoza, Kid's Room, Rainbow Cave) can be used by either player on their own turn. | card text + [OBSERVED] |
| Which discard pile a replaced Stadium goes to | [INFERRED] its owner's (paper-TCG rule); not observed |

### Fossils
- Item cards. "Play this card as if it were a 40-HP Basic [C] Pokémon. At any time during your turn, you may discard this card from play. This card can't retreat." [card text]
- Not a Pokémon in hand or deck: can't be placed at setup, can't be found by Poké Ball. [COMMUNITY] Bulbapedia, gameland
- In play it counts as a Basic Colorless Pokémon (counts for Bench-count effects). Energy can be attached. Knocked Out = 1 point to the opponent; discarding it yourself = no points. [COMMUNITY]

## 7. How long effects last

- **Effects on a Pokémon end when it moves to the Bench.** "All effects applied to a Pokémon are removed when that Pokémon returns to the Bench" — Buzzwole ex can use Big Beat again after a trip to the Bench; retreating dodges Mismagius's Cursed Prose (90 at the end of the next turn). The in-app Tips say the same for retreat *and* evolution ("any effects of attacks … or Special Conditions affecting the Pokémon end"). [OFFICIAL, three FAQ articles + in-app Tips]
- **Player-wide effects are not tied to a Pokémon.** Happiny's "+20 next turn" effect still boosted Absol after Happiny was Knocked Out. Giovanni/Red/Blaine/Cynthia ("during this turn, attacks used by your Pokémon…"), Blue ("during your opponent's next turn, all of your Pokémon take −10") work the same way. [OBSERVED 031901] + card text
- "During your opponent's next turn" ends at the end of that turn; "during your next turn" at the end of yours.
- "During your opponent's last turn" conditions (Marshadow/Bouffalant Revenge) are remembered across the Checkup. Revenge needs a Knock Out "by damage from an attack"; Poison/Ability KOs don't count. [OBSERVED ×3] + [COMMUNITY]
- **On evolution, effects of attacks on that Pokémon end** — same as going to the Bench. [OFFICIAL] in-app Tips

## 8. Copying attacks (Mew ex Genome Hacking and similar)

- Pay Mew ex's own cost; the copied attack's Energy cost and types are ignored. [COMMUNITY] pokemon-zone, JP blog
- Everything the copied text refers to is Mew ex's side: "discard N Energy" uses Mew's Energy, "for each Energy attached to this Pokémon" counts Mew's Energy (a copied Hydro Bazooka didn't copy the Blastoise ex's boosted damage), Bench counts use Mew's Bench, recoil hits Mew. [COMMUNITY] + [SINGLE, first-hand report]
- Can't copy another copy attack; Ditto can't copy Genome Hacking. [COMMUNITY]

## 9. Coin flips and randomness

- Flips are independent 50/50 ("first coin … will definitely be heads" is a specific card effect). "Flip until you get tails" has no cap. [IN-GAME TEXT] + [COMMUNITY]
- Re-flip effects (Victini's Victory Star) replace the whole batch; the original results don't count. [OBSERVED 020124, 014933]
- Many effects pick "at random" and the game decides (Poké Ball = random Basic; Prank Spinner = one random card from either hand; Draco Meteor targets). [OFFICIAL Prank Spinner] + card text
- Poké Ball's in-game text: "Put a random Basic Pokémon from your deck into your hand." — the player doesn't choose. [IN-GAME TEXT, read in 220914 and 025604 frames] The engine matches: `pokemon_search_outcomes` (shared_mutations.rs) gives each eligible Basic in the deck an equal chance, then shuffles.
- Lucky Ice Pop heals every time; the coin only decides whether the card returns to hand. [OBSERVED ×7]
- A card taken from the opponent's discard by Team Rocket's Thieving Machine is yours for the rest of that battle (Lucky Ice Pop returns to *your* hand; Copycat shuffles it into *your* deck). [OFFICIAL]

## 10. Public and hidden information

- Public: everything in play (Pokémon, HP/damage, Energy, Tools, conditions, effect icons), the Stadium, both discard piles, points, and both Energy Zones including the **next** Energy. [IN-GAME TEXT + OBSERVED] Discard piles, officially: "Cards are always placed face up in the discard pile. Both players in a battle can see how many cards are in either discard pile, and they can look at all the cards in either discard pile at any time." The deck is face down. [OFFICIAL] in-app Tips ("About the zones used in battle")
- Also public: each player's **hand size** (the opponent's hand is shown as a fan of card backs at the top of the screen) and **deck count** (a number badge next to the deck, e.g. "8"). [OBSERVED 025604 at 137 s, 220914]
- Hidden: hand contents and deck order. Hand Scope / Copycat-type effects reveal or count the opponent's hand.
- **Every Trainer the opponent plays is shown face-up** (the card flips from its back and is shown full size before going to the discard). [OBSERVED ×many]
- **A card fetched by Poké Ball is not shown to the opponent.** It goes from deck to hand face-down, and you only learn what it was if and when it is played. Seen frame by frame in two games: 220914 at ~45–50 s (opponent's Poké Ball → a card back joins their hand → Professor's Research → Rookidee benched later from hand) and 025604 at ~148–151 s (opponent's hand goes from 2 to 3 card backs, nothing face-up). Review 170229 says the same. [OBSERVED ×3] The 220914 review's "searches/reveals Rookidee" was the reviewer reading back from the later bench play; the frames show no reveal.
- **General rule: any card that goes from a deck into a hand is hidden from the other player** — they only see card backs arriving (draws, Professor's Research, Poké Ball, Lisia, etc.). [DUSTIN] + [OBSERVED Poké Ball ×3]
- What the other player can still work out: how many cards arrived; what the card text guarantees (Poké Ball → it was a Basic); and, when a search finds nothing ("no eligible target"), that the deck has none of that kind left. [INFERRED + OBSERVED no-target message]
- **Cards that go into a hand from a public zone are known to both players**: Team Rocket's Thieving Machine taking a card from the opponent's discard (the game shows the card: Poké Ball revealed in 152812 at 03:32–03:36, then played by Dustin), Ilima or Koga returning a Pokémon from play, Lucky Ice Pop returning to hand on Heads. [DUSTIN + OBSERVED]
- Cards shuffled from a hand back into the deck (Copycat, Red Card) become hidden again, and the cards drawn in their place are hidden. [INFERRED]
- For the bot: model the opponent's hand as the known cards (from public zones) plus a count of unknown cards; after Poké Ball it should know *that* a Basic arrived but not *which* one. Checked 2026-09-22 (`07` §4): in simulated games every bot decides from a `PlayerObservation` that hides the opponent's hand, both decks' order and the Energy after "next"; the RL environment (`pdl_rl_env`) builds its features from the same observation. Only the `--data-output` exporter and the Python package expose the full state (latent, unused).

## 11. Names, categories, subtypes

- Same-name limit counts exact names: "X", "X ex", "Mega X ex", "Team Rocket's X" are all different. [IN-GAME TEXT + COMMUNITY]
- Effects that name a Pokémon ("your Garchomp") don't include its ex version. [COMMUNITY] pokemon-zone
- **Ultra Beasts** are a real category that cards refer to (Lusamine "Choose 1 of your Ultra Beasts", Celesteela, "Ultra Beasts take −X damage"). One agent's source called it "flavor only" — that is wrong for rules purposes.
- **Past / Future** (B3a) are labels that specific cards refer to ("Attacks used by Future Pokémon cost 1 less…"). [IN-GAME TEXT + COMMUNITY]
- **Baby Pokémon** (A4): Basic, 30 HP, no Weakness, no Retreat Cost, free attacks — by printed stats, not a special rule. [COMMUNITY]

## 12. Official card-specific rulings (Detailed Battle FAQ, full list as of 2026-09-21)

1. Team Rocket's Thieving Machine — stolen card is treated as yours for the battle (§9).
2. Wallace — uses current maximum HP; a 50-HP Staryu with Giant Cape (70) can't be chosen.
3. Damage calculation order — file 02 §1.
4. End-of-turn effect order — file 03 §5.
5. Mimikyu ex Disguise vs attacks — ignored by Ledian's Swift and by Ability negation; works again after negation ends.
6. Jolteon ex Electromagnetic Wall — only Energy attached from the Energy Zone (manual or by effect); not from discard, not moved between Pokémon.
7. Prank Spinner — returns only one random card from either hand.
8. Points for discarded Pokémon — none; only Knock Outs score.
9. Mismagius Cursed Prose — removed if the Pokémon retreats first.
10. Scizor Gale Thrust — only after your own Bench→Active move that turn.
11. Mimikyu ex Disguise vs non-attack damage — doesn't stop Poison/Burn, Ability or Tool damage.
12. Buzzwole ex Big Beat — the "can't use next turn" effect is cleared by going to the Bench.
13. (Japanese page only) Budew's Prickly Powder (ひりひりパウダー, B3 013/159; "Itchy Pollen" was a translation) — stops "after the attack" Abilities like Rough Skin on that attack; doesn't stop a "−30 from attacks" Ability already in effect for that attack, but removes it for later attacks.

Community rulings collected by pokemon-zone for A1a, A2 and A2a are listed in `06_sources.md`.
