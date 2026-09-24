# 01 — Game structure: decks, setup, turns, Energy Zone, winning, timers

Pokémon TCG Pocket rules as of app version 1.7.x (September 2026), card pool through B4a.
Grades: **[OFFICIAL]** the in-app Tips › About Battle Rules text, Pokémon/Creatures support pages, or printed card text · **[IN-GAME TEXT]** the game's own
tutorial/UI strings (extracted text, v1.7.1) · **[OBSERVED]** seen in Dustin's recorded games · **[COMMUNITY]**
wikis/guides (two or more agree) · **[SINGLE]** one community source · **[INFERRED]** my reasoning, not a source · **[DUSTIN]** stated by Dustin from his own play ·
**[UNRESOLVED]** conflicting or unknown. Sources for every tag are in `06_sources.md`.

---

## 1. Deck construction

| Rule | Grade |
|---|---|
| Exactly **20 cards**. A deck with 21–30 cards can be *saved* but not used. | [IN-GAME TEXT] deck-legality dialog + "Decks must have exactly 20 cards. Decks with more cards (up to 30) can be saved but not used" |
| At least **one Basic Pokémon**. | [IN-GAME TEXT] |
| **No more than two cards with the same name.** "X" and "X ex" are different names (2 Blastoise + 2 Blastoise ex is legal). "Team Rocket's X" is a different name from "X". | [IN-GAME TEXT] + [COMMUNITY] Bulbapedia, pokemon-zone |
| **1 to 3 Energy types** may be selected ("You may only select up to three Energy types"). The deck must have Energy selected "that allows one or more Pokémon to use their attacks". | [IN-GAME TEXT]. Note: an older pokemon-zone guide says "limited to two types" — outdated; the current in-game message says three. The deck *recommendation* feature says "select up to two types", which is a different screen. |
| Fossils are Trainer (Item) cards in the deck; they are **not** Pokémon while in the deck or hand. | [COMMUNITY] Bulbapedia Fossil page |

## 2. Setup

Order: **coin flip → each player draws 5 → each player places an Active (face-down) and up to 3 Bench → both reveal → first turn.** [OFFICIAL] in-app Tips ("Setting up to play happens in this order": coin flip, heads goes first → cards drawn automatically → choose an Active and any Bench → Start Battle → both sides turned face up). While setting up, "players can't see which Pokémon their opponent has put in play." The Tips don't give the number of cards or say how the Basic is guaranteed.

| Rule | Grade |
|---|---|
| A coin flip at the start decides who goes first; the result ("You are going first/second") is shown **before** setup, so both players know turn order when choosing their Active. | [OBSERVED] the setup prompt "Please put a Basic Pokémon in the Active Spot" appears together with "You are going first/second" (videos 013104, 021327, 022627; OCR scan) + [COMMUNITY] GameWith |
| Opening hand is 5 cards and **always contains at least one Basic Pokémon**; there is **no mulligan**. It is a hard guarantee, not a probability: a deck with only one Basic has that Basic in the opening hand every time. | [COMMUNITY] Bulbapedia, GameWith, Game8 + [DUSTIN] his own play (stated 2026-09-21) |
| **How it's dealt: 5 random cards; if none is a Basic, one of them is swapped for a Basic.** So a hand that already has a Basic is an ordinary random hand; extra Basics are *not* favoured. With a 2-Basic deck both Basics show up ~5–6% of the time (not ~21% as with "one Basic first, then 4 random"). | [COMMUNITY-TESTED] two Qiita studies: machapin, 2,000 automated games on v1.2.5, three models Z-tested, this one fits (p = 0.18 and 0.91), "Basic first" rejected at p ≈ 10⁻³⁰; Davoi, 120 games, 8% observed. **Confirmed on the current app by Dustin's test T1 (2026-09-22): both Basics in 3 of 50 opening hands with a 2-Basic deck; "Basic first" would give ~10 (p = 0.0035).** [OBSERVED] Evidence: `_research_notes/audit_2026-09-22/T1_T10_results.md`. ⚠ The `unified1` engine deals a Basic first (`07` H1); the verified `0.1.0-pdl.rules1` build implements the swap-in (`09`). |
| Place 1 Basic face-down in the Active Spot (mandatory), then "up to 3 Basic Pokémon onto your Bench" (optional), then tap Start Battle. Both players set up at the same time ("Waiting for opponent to set up…"). | [IN-GAME TEXT] + [COMMUNITY] pokemon-zone, GameWith |
| Setup has a time limit: "Players that go over the time limit for setting up to play will have a random Basic Pokémon placed in their Active Spot, and the battle will begin." Tapping Reset before finishing returns the Pokémon already put into play to the hand. | [OFFICIAL] in-app Tips (2026-09-22 screenshot) |
| **Fossils cannot be placed during setup** ("they do not count as Pokémon cards while in a player's hand"). | [COMMUNITY] Bulbapedia (single wiki, but consistent with the card text "Play this card as if it were…") |

## 3. Turn structure

1. **Draw 1 card** (mandatory). **The player going first also draws on turn 1.**
   - [OBSERVED] in four of Dustin's games where he went first (battles 020124, 024406, 225430, 224312: "Turn draw is Revavroom", "Turn draw is Rare Candy", …). Game8's English rule-differences page says the first player does *not* draw — **that is contradicted by the recordings; treat Game8 as wrong here.**
   - Hand already at 10: the draw is skipped, the card stays in the deck ("Hand full; unable to draw cards"). [IN-GAME TEXT] + [COMMUNITY] Game8 JP ("手札が10枚ある場合…トラッシュすることはありません")
   - Empty deck: nothing happens and **you do not lose** ("A player will not lose even if they run out of cards in their deck"; "No cards left in deck; unable to draw cards"). [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED] (battle 220914, twice) + [COMMUNITY] Bulbapedia, pokemon-zone, Game8 JP. Game8 EN's "battle system" page claims deck-out is a loss — wrong.
2. **Energy Zone rotates**: the "next" Energy becomes your usable Energy for this turn and a new "next" is generated (see §4). [OFFICIAL] in-app Tips: "When your turn starts, you draw a card from your deck and put it in your hand. After that, Energy will be automatically generated in your Energy Zone. The Energy Zone will display the Energy that was just generated and the Energy that will be generated next."
3. **Main phase, any order, any number of times unless limited:**
   - Put Basic Pokémon from hand onto the Bench (Bench max 3: "There are three spots on the Bench, and if any spots are open, you can put as many Basic Pokémon as you [want]" — [OFFICIAL] in-app Tips).
   - Evolve Pokémon (limits in `04_actions_cards_effects.md` §3).
   - Attach the turn's Energy from the Energy Zone — **once per turn** — to the Active or a Benched Pokémon.
   - Play Items (unlimited), Pokémon Tools (unlimited, one per Pokémon), **one Supporter**, **one Stadium**.
   - Use Abilities ("Unlike attacks, using an Ability does not end your turn").
   - **Retreat once per turn** ("You can still use an attack even if you retreated during that turn").
   - [IN-GAME TEXT] for each of these; [OBSERVED] throughout the recordings.
4. **Attack** (optional). Only the Active Pokémon can attack, and only if the required Energy is attached (typed symbols need that type; Colorless symbols take any type). Energy stays attached unless the attack says otherwise. "After you attack, your turn ends." [OFFICIAL] in-app Tips. Even a zero-damage attack (e.g. a draw attack) ends the turn. [OBSERVED] battle 025604.
   - Nothing can be done after attacking. [OBSERVED] — the game warns before you attack or end the turn if something is still usable ("Energy can be attached", "A Supporter card can be used", "An attack can be used", "Basic Pokémon can be put in play"); the player can dismiss the warning. [IN-GAME TEXT] + [OBSERVED] first-altaria.
5. **End of turn**: "at the end of your turn / each turn" effects, then **Pokémon Checkup** (both players' Active Pokémon), then the other player's turn. Full order in `03_status_checkup_timing.md`.

### First turn of the game

| | Player going first (P1) | Player going second (P2) |
|---|---|---|
| Draws a card | **Yes** [OBSERVED ×4] | Yes |
| Energy from the Energy Zone | **None** — "On the first turn of the player who goes first, no Energy will be generated in the Energy Zone." [OFFICIAL] in-app Tips. The large (current) slot is empty; only the "next" preview is shown. [OBSERVED] battle 232035 (two separate reviews of the same recording) + [COMMUNITY] pokemon-zone, GameWith, Bulbapedia | Yes, one [OBSERVED 232035] |
| Supporter | **Allowed** (including Supporters that attach Energy) [COMMUNITY] Bulbapedia, Game8 + [OBSERVED] battle 225430 (P1 played Professor's Research on turn 1) | Allowed |
| Attack | **Allowed** if the attack's cost can be paid — in practice a zero-cost attack, or Energy put on by a card effect. [OFFICIAL] Battle Rules FAQ ("can be used on the first turn of the player that goes first") + [COMMUNITY] Bulbapedia | Allowed |
| Evolve (incl. Rare Candy, Quick-Grow Extract) | **No** — "Neither player can evolve Pokémon on the first turn, whether they go first or second." [OFFICIAL] in-app Tips + printed Rare Candy text | **No** (same rule) |
| Retreat | Allowed (no rule against it; Wimpod's Ability "During your first turn, this Pokémon has no Retreat Cost" presupposes it) [INFERRED from card text] | Allowed |
| Exceptions | Cards that say so: Eevee's Boosted Evolution ("can evolve during your first turn or the turn you play it" while Active) [OBSERVED battle accepted-232035]; card effects that evolve without printing the limit — Wallace on turn 1 and Caterpie's Quick Growth at the end of turn 1 [OBSERVED 150630]; Zeraora's Thunderclap Flash attaches Energy "at the end of your first turn". | same |

## 4. Energy Zone

| Rule | Grade |
|---|---|
| Energy is not a card. Each turn one Energy is generated in your Energy Zone ("When it is your turn, an Energy is generated in the Energy Zone"). You may attach it to your Active or a Benched Pokémon, and "You can attach Energy of one type to Pokémon of a different type." | [IN-GAME TEXT] + [OFFICIAL] in-app Tips |
| You can see the **next** Energy ("You can also see the Energy that will be generated during your next turn"). Both players' current and next Energy are shown on the board. | [IN-GAME TEXT] for your own; the opponent's zone being visible is [OBSERVED] (reviewers read the opponent's "next-Psychic preview") |
| Both players get a "next" preview before turn 1; P1 has no current Energy on turn 1. At the start of each of your turns, next → current and a new next is rolled. | [COMMUNITY] pokemon-zone; matches deckgym's model |
| With 2–3 types selected, each generated Energy is a random one of those types ("a different type will generate at random on each of your turns"); JP guides say equal probability. The wording "different type" does **not** mean it can't repeat — it means random among the selected types. | [IN-GAME TEXT] + [COMMUNITY] GameWith JP ("確率は均等") |
| **Unattached Energy is discarded at the end of your turn** (it does not carry over). | [COMMUNITY] pokemon-zone, Bulbapedia Battle page ("the generated Energy is discarded if it wasn't attached"). One garbled Game8 sentence suggested otherwise; not credible. |
| Card effects that attach Energy "from your Energy Zone" (Moltres ex, Misty, Manaphy, attack effects like Turbo Shark) **do not use up** the once-per-turn manual attachment. | [OBSERVED] battle 020124: manual Fire attachment and Heat Charged's attachment in the same turn |
| The engine treats "attached from the Energy Zone" as its own event (both the manual attachment and card effects that take Energy from the Zone), distinct from Energy moved between Pokémon or taken from the discard pile. | [OFFICIAL] Jolteon ex FAQ |
| Some cards change the Zone: Rainbow Cave discards the current Energy and produces the next one; some effects change the type of the next Energy ("Changed the type of the next Energy generated"). | card text + [IN-GAME TEXT] + [OBSERVED] battles 014933, 020124 |
| Discarded Energy (retreat, attack costs, KO) goes to the discard pile and can be reused by effects like Flame Patch or Volkner. | [COMMUNITY] pokemon-zone + [OBSERVED] battle 225430 |

## 5. Hand limit

- **10 cards.** "You can have up to 10 cards in your hand, and you use these cards during the battle." Draws beyond 10 are skipped (card stays in deck). [IN-GAME TEXT] + [COMMUNITY] + [OFFICIAL] in-app Tips: "A player can only have up to 10 cards in their hand."
- A multi-card draw is partly skipped: e.g. Professor's Research at 9 cards after playing it gives 1 card; the second draw is skipped. [COMMUNITY] Game8 JP ("11枚目以降はデッキから引くことができなくなります")
- An effect that would return a card to a full hand fails: "Hand full; unable to return card". Where that card ends up is **[UNRESOLVED]**. Playing a card from hand frees a slot first, so Lucky Ice Pop, Koga or Ilima returning one card can't overflow a hand on their own; the likely trigger is an evolved Pokémon (2+ cards) going back to a hand of 9 [INFERRED].

## 6. Winning, losing, ties

| Rule | Grade |
|---|---|
| **Points.** Knocking Out an opponent's Pokémon gives 1 point; Pokémon with a Rule Box give more: **Pokémon ex = 2**, **Mega Evolution Pokémon ex = 3**. "If a player Knocks Out more than one Pokémon at the same time, they get a point for each Pokémon." Score display caps at 3. | [OFFICIAL] in-app Tips + [IN-GAME TEXT] (ex = 2; Mega ex = 3) + [OBSERVED] ("+3 points!", battle 025604) |
| Points come **only from Knock Outs**. Discarding an opponent's Pokémon with an effect gives no points. | [OFFICIAL] Detailed Battle FAQ |
| **Win:** "If one player gets the set number of points for that battle or more **before the other player**, that player wins the battle." (3 in versus; Solo battles can set another number.) | [OFFICIAL] in-app Tips |
| **Lose:** "If a player doesn't have any Pokémon remaining in play, that player loses the battle **regardless of the number of points each player has**." Immediate — no prompt. | [OFFICIAL] in-app Tips + [OBSERVED] empty-Bench KOs went straight to "Defeat" |
| **Concede** = loss "regardless of the state of cards in play or the number of points". **Running out of cards is never a loss.** | [OFFICIAL] in-app Tips |
| Ties exist ("Tie" result). In Ranked a tie changes no rank points but resets the win streak. | [OFFICIAL] Gameplay FAQ + [IN-GAME TEXT] |

**When both players hit a condition at the same moment** (recoil, retaliation, Checkup KOs, self-damage), apply the two official lines above:

| Situation after the Knock Outs resolve | Result | Grade |
|---|---|---|
| One player has no Pokémon left, the other does, and neither reached 3 | The player with no Pokémon loses | [OFFICIAL] |
| In the observed T2 setup, a player at 2 points receives the 3rd point while their last Pokémon is Knocked Out in the same attack; opponent still has Pokémon and fewer than 3 | **Tie** | [OBSERVED] T2 video, one seat; opponent final 2 points inferred from the ex Knock Out, not shown on the overlay. Rules4 implements this narrow case; both-seat engine regression fixtures are not video evidence. See `05` #2 and the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md) |
| Both reach 3+ at once, but one of them has no Pokémon left | The player who still has Pokémon wins (two win conditions against one) | [COMMUNITY] pokemon-zone; not seen |
| Both players have no Pokémon left | Tie | [INFERRED] both meet the losing condition + [COMMUNITY] Dexerto |
| Both reach 3+ at once and both still have Pokémon | Tie (nobody got there "before the other player") | [INFERRED] from the wording + [COMMUNITY] Dexerto, Game8 JP, GameWith |
| Only one reaches 3+ and both still have Pokémon | That player wins | [OFFICIAL] |

The broader pokemon-zone "count the win conditions" model (3+ points; opponent has no Pokémon) is a [COMMUNITY] hypothesis. T2 supports only the specific one-seat arrangement in the table above; rules4 adds this narrow tie and retains its prior behavior for the other simultaneous-finish rows; those outcomes remain unverified as game rules. Do not treat the broader model as settled.
| A double KO where neither player reaches 3 simply awards both players their points and play continues. | [OBSERVED] battle 225430 (Rocky Helmet retaliation KO'd the attacker; "each player receives one point") |

## 7. Turn limit and timers

| Rule | Grade |
|---|---|
| "Battles have a limited number of turns. Once the turn limit is reached, the battle ends in a tie." [OFFICIAL] in-app Tips. The limit is **30 turns in versus, 50 in Solo** ("The battle is over because the turn limit has been reached"). | Tie: [OFFICIAL] in-app Tips. Numbers: [COMMUNITY] Bulbapedia, GameWith, Game8 JP + [IN-GAME TEXT] message. The on-screen turn counter counts **both players' turns**: in battle 225430 Dustin's turn (turn 5) was followed by the banner "Opponent's turn — Current turn: 6" [OBSERVED, frame 168 s], and in 220914 "Opponent's turn — Current turn: 2" was followed by "Your turn — Current turn: 3" [OBSERVED]. So 30 turns ≈ 15 each, as deckgym counts it — assuming the limit uses that counter [INFERRED]. An X post quoting the in-app rules text: "Games in Pokemon TCG Pocket can last a maximum of 30 turns. If you reach the limit, the duel ends in a tie." One Yahoo answer disputes Solo = 50 ("30"). Whether the 30th turn's end-of-turn step and Checkup still happen is open (`05` #22); the engine runs them and lets a Checkup win stand. |
| **Turn timer:** "A player who reaches this time limit will have their turn forcibly ended, and their opponent's turn will begin. This timer resets on each turn." It is 90 seconds (no attack happens; unattached Energy is discarded). In Ranked, running out halves your next turn's timer. | [OFFICIAL] in-app Tips (rule); [COMMUNITY] Bulbapedia, Game8, pokemon-zone (90 s, Ranked halving) |
| **Waiting-for-input timer:** when the game needs your input during the opponent's turn (e.g. choosing a new Active) or during Pokémon Checkup, a separate short limit applies; if it runs out "the game will automatically resolve the situation". It resets each time either player is asked for input. | [OFFICIAL] in-app Tips |
| **Battle clock, one per player (20 minutes):** "A player who reaches their time limit **loses the battle**." It also runs on the opponent's turn while the game is waiting for your input. Two clocks are shown on screen (e.g. 19:41 and 19:15 at the same moment). | [OFFICIAL] in-app Tips + [OBSERVED] OCR scan (232617 and others) + [COMMUNITY] Game8 JP. **Bulbapedia and Game8 EN ("points are compared") are wrong.** 20 minutes: [COMMUNITY] |
| Solo battles can have their own rules ("Maximum of N turns", "N points to win", "Time limit of N seconds per turn" / "No time limit per turn"). | [IN-GAME TEXT] |

## 8. Disconnects and conceding

- Disconnect in a versus match: a short window to reconnect (the support.pokemon.com Gameplay FAQ, updated 2026-07-30, says ~120 s; the in-app help article 44994624550809, updated 2026-01-29, says "around 60 seconds" — sources disagree, the newer says 120), during which the battle clocks keep running; fail and you **lose**; if the opponent fails to reconnect you win; **if both players are disconnected, it counts as a loss for both**. Solo battles can be resumed after reconnecting or restarting the app. [OFFICIAL] in-app Tips + Gameplay FAQ + [IN-GAME TEXT]
- Concede is available from the menu; the conceding player loses regardless of the board or points. [OFFICIAL] in-app Tips + [IN-GAME TEXT]
- Ranked unlocks at player level 3; rental decks can't be used in versus. [OFFICIAL] Gameplay FAQ

## 9. Rules history that matters for old data

- Launch (Oct 30, 2024): only Poisoned, Asleep, Paralyzed existed; **Burned and Confused and Pokémon Tools arrived with A2 Space-Time Smackdown (Jan 29–30, 2025)**. [COMMUNITY] Bulbapedia
- Ranked Match added Mar 26, 2025 (v1.2.0). Stadiums added Jan 29, 2026 (B2 / v1.5.0). Mega Evolution ex added Oct 30, 2025 (B1).
- v1.7.0 (Jul 29, 2026): "rule text for some cards will be updated" and Ranked losses cost 0 points below Master Ball rank. What changed, per a JP blog quoting the notice [SINGLE]: Supporters that search for **named** cards (Clemont, Gladion, Team Galactic Grunt) became playable even when they can't find anything; the printed text didn't change. See `04_actions_cards_effects.md` §6.
- v1.7.1 (Aug 5–6, 2026) and v1.7.2 (Sep 3–4, 2026): "bug fixes" only, no itemized notes published anywhere (checked 2026-09-22). No 1.8 yet.
- Next sets: **B4b on Sep 29–30, 2026**, then **C1 (a new series) on Oct 28, 2026** [COMMUNITY, checked 2026-09-22]. The engine and this folder cover cards through B4a; new cards need the same card-effect pass (`07`).
