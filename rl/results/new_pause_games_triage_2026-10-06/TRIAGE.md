# Triage of the new Pause Games batch (Oct 6, 2026)

Batch folder: `Battle Logs\Recording_QA\BATCH_2026-10-06_NEW_PAUSE_GAMES\` (18 game packets from 17 recordings; 13 exact QR lists plus
the edited Water-only Snorlax / Persian / Silvally list = 14 lists). One pass, read-only on the batch; nothing in the batch or the
shared checkout was changed. Recordings are named by the time part of the file name, so `183108` means
`20261005_183108000_iOS.MP4`; every "@123" is seconds into that recording. `012927/g2` is the second game of that recording.

Context from Dustin: an event rewarded wins with 8 Pokémon of each Energy type, so these lists were improvised, and the opponents
play uncommon decks he can only partly see. An opponent's unseen cards stay unknown here.

**What this says in short**

1. Engine coverage: nothing missing, nothing partial. All 363 card printings in the 14 lists and all 97 opponent card names are in
   the pinned engine's data with status Complete (details in section 1 and `ENGINE_COVERAGE.md`).
2. Rules: one real divergence found. Mega Sableye ex's Cursed Jewel hit back for 60 on a Darkness-Weak attacker (twice, `183108`
   @308 and @386), so the game added Weakness to that retaliation; the engine adds none and would deal 40. Rocky Helmet's retaliation
   got no Weakness in the same batch (`215749`), so the difference is by source. That needs a decision, not my change. Everything
   else the games did matches card text, the rules folder, or the engine (I also ran one engine check for Deck and Cover into Rocky
   Helmet; it matches the video).
3. Human evidence: his hand is known at the start of all 82 of his turns. Nine good build-up and tempo positions are listed in
   section 3 (not built).
4. Results: 8 wins, 10 losses over the 18 games. Eleven of the 14 lists are setup decks. If any list gets a simulator check, the
   best candidates are Conkeldurr / Sandslash / Hitmonchan ex and Aegislash / Melmetal ex / Magnezone, with Scolipede / Mega Sableye ex
   after the Cursed Jewel decision.
5. Pending: nothing. All 18 packets are accepted and registered.

---

## 1. Engine coverage

Method: each card slot in the prepared deck entries (`NEW_DECK_ENTRIES.json`, `EDITED_DECK_ENTRY.json`) was resolved to every
printing it can mean (the QR names the playable card, not the artwork) and each printing's status was read from the pinned official
engine's card-status dump (main-8626a35, `engine_version 0.1.0-pdl.rules4`, 3,879 cards: Complete 3,871, RulesUnverified 8). Opponent
cards come from the ledgers: both boards at every turn boundary, every opponent play, every public reveal, and the Stadium in play.
Hidden draws and searches have no name and are not counted. "Complete" means every effect is wired into the engine; it is not an
independent rules certification.

| Check | Result |
|---|---|
| Printings in his 14 lists | 363, all Complete; none missing, none partial |
| Opponent card names in the 18 ledgers | 97, every one found in the card data, all Complete |
| The 8 RulesUnverified cards | None is in his lists or among the opponent cards named |
| HP in the packets vs the card data | 175 of 175 checked values match (capes and printed HP taken into account) |
| Attack and ability names in the packets vs the card data | 158 checked; 14 differences are artwork notes in the packet label, plus one spelling difference (Hungry Draw / Hungrily Draw) |

Nothing needs listing under "missing or partial", so there are no games to attach to one. The full per-list tables and the opponent
table (each card with the recordings it appears in) are in `ENGINE_COVERAGE.md`.

One ledger label to correct when someone next touches that packet: `032023` turn 13 (opponent, @453) says Finizen evolved to Palafin
and "effective maximum 130 with retained Giant Cape". Palafin is 130 HP printed and the Giant Cape adds 20, so the engine's rule gives
150 maximum with the 20 damage carried over, which is 130 current HP. The "130" in the packet is almost certainly the current HP,
mislabelled as the maximum. Not a rules question.

---

## 2. Rules questions

I checked the unusual events against card text (`lib/card.py`), the `rules/` folder and the engine source. Only the first item is a
real open question.

### 2.1 Open: does Weakness add 20 to retaliation damage? (Cursed Jewel says yes, Rocky Helmet says no)

- **What the game did.** Mega Sableye ex (Darkness) used Cursed Jewel (text: "During your opponent's next turn, if this Pokémon is
  damaged by an attack, do 40 damage to the Attacking Pokémon."). Houndstone (Psychic, Weakness Darkness) then attacked it. In
  `183108`:
  - turn 8, @306-308: Houndstone 130/130 uses Last Respects on the Mega (170 to 40); Houndstone ends at 70/130, so it took **60**.
  - turn 10, @384-386: Greavard 60/70 evolves to Houndstone (120/130) and attacks the Mega (80 to 0); Houndstone ends at 60/130, so it
    took **60** again.
  The review reads both as "cursed_jewel_retaliation: 60 with Weakness". The only other damage source on that side, the Mega's
  Deceptive Needle, fires at the end of its owner's own turn, not on those hits.
- **The contrast in the same batch.** In `215749` Torchic (Fire) holding a Rocky Helmet was hit by Tinkatink (Metal, Weakness Fire).
  The Helmet returned exactly 20 (Tinkatink 60 to 40) at t2 @99 and again at t4 @161 (after a Potion, 40 to 60, then 20 back to 40),
  with no +20. So a Tool's retaliation got no Weakness while an attack-armed retaliation did.
- **What the engine does.** `handle_attack_retaliation` (`engine/src/actions/apply_action_helpers.rs:614-633`) adds the plain sum from
  `get_counterattack_damage` (`engine/src/hooks/counterattack.rs`) with `apply_damage`, and no Weakness is applied anywhere on that path.
  It would deal 40 here. I read the code; I did not run this case. The same path serves four attack-armed retaliation amounts
  (20, 30, 40, 80 in `engine/src/actions/effect_mechanic_map.rs`, lines 529, 538, 547, 2540), Rocky Helmet and the retaliation abilities.
- **What the rules folder says.** `rules/02` section 4 lists retaliation damage (Rough Skin) as not "damage from an attack", so
  Weakness would not apply; that row rests on [COMMUNITY] sources and the Mimikyu ex FAQ for abilities and Tools. It has no
  observation for retaliation that an attack arms. The card text for Cursed Jewel does not mention Weakness either way.
- **So.** This is the first [OBSERVED] data on attack-armed retaliation, and it contradicts the engine for that kind. The Tool kind
  (Rocky Helmet) is consistent with the engine and with `rules/02`. What the batch does not settle is retaliation from an Ability
  (Rough Skin style), which `rules/02` also treats as "no Weakness" on [COMMUNITY] grounds only. Other Helmet hits in the batch
  (`214731` t2, t4, t8) had attackers that are not Weak to the holder, so they say nothing about Weakness.
- **Decision needed (not mine).** Changing the engine for attack-armed retaliation is a rules change, so it goes to Dustin through the
  laptop. The fix would be small (add the Weakness bonus in `handle_attack_retaliation` for the effect-armed part only, leaving Tools
  and Abilities alone), but I have not made it. Until then, any simulator number for Mega Sableye ex against Psychic decks undercounts
  Cursed Jewel's return hit by 20 each time.
- **Proposed shot-list row** (format of `rules/08`), only for the part the batch leaves open:

  | # | Settles | Type | Setup | Look for |
  |---|---|---|---|---|
  | T15 | Weakness on retaliation from an Ability (`183108` shows +20 on Cursed Jewel's attack-armed retaliation; `215749` shows none on Rocky Helmet's) | Any game | Attack a holder of a retaliation Ability (Rough Skin style) with a Pokémon that is Weak to the holder's type | Damage on the attacker: the Ability's amount alone, or the amount plus 20 |

### 2.2 Checked: the game matched the card text, the rules folder or the engine

Each of these is already settled in `rules/`; the batch adds a fresh [OBSERVED] confirmation at the timestamp shown.

| What happened | Where | Settled by |
|---|---|---|
| Accelgor's Deck and Cover into a Rocky Helmet holder: the attacker is shuffled away and no Helmet damage lands on it or on the Pokémon promoted afterwards (Butterfree stays at 50) | `214731` t6 @280-298 | `rules/04` (Helmet only hits the attacking Pokémon after its own effects). **Engine run:** a scratch test (Deck and Cover into a Helmet holder, then promote the damaged Butterfree from either Bench slot) shows the same: the shuffle comes first, the retaliation step finds an empty slot, the promoted Butterfree keeps 50 HP. Test file kept as `scripts/helmet_scratch_test.rs`, not for the engine's test folder |
| Rocky Helmet damage after Sunny Wind's own healing, not before (heal 50 to 70, then Helmet back to 50) | `214731` t8 @333-346; t4 @218 | `rules/04` line 105 and `rules/02` |
| Rocky Helmet returns a flat 20 even onto an attacker Weak to the holder's type (Metal Tinkatink hitting Fire Torchic) | `215749` t2 @99, t4 @161 | `rules/02` section 4 (Tool damage gets no Weakness) |
| Poké Ball played with no Basic left in a non-empty deck: no effect, card used | `213625` t5 @209, t11 @396; `123812` t9 @317; `032023` t6 @186 | `rules/09` (Poké Ball is blocked only by an empty deck; engine `can_play_poke_ball`) |
| Research with one card left draws that one card; empty deck is never a loss | `213625` t11 @396-407 | `rules/01`, `rules/04` |
| Fragrant Forest with no valid Basic: no effect | `213625` t8 @282 (opponent) | `rules/09` hidden-deck rule |
| Rainbow Cave used before the turn's Energy is attached, never after | `012927` t10 @340; `124532` t2, t4; `034953` t7, t9 | `rules/04` line 116 |
| Wally's Colorless Energy to a Stage 2 is separate from the turn's attachment | `183108` t5 @181; `012140` t6; `020518` t11 | `rules/04` |
| Weakness +20 on the Active only: Poison Sting 40, Venoshock 90, Sunny Scorching 50 (including +20 on Tinkatink), Peck 40 | `183108` t3, t5; `215749` t5 @208; `123812` t3, t5 | `rules/02` |
| Teal Mask Ogerpon ex's Soothing Wind on the opponent's Bench blocked Poison and Paralysis from Deck and Cover | `213625` t11 @407-410 | Engine implements `SoothingWind` (`apply_action.rs`); `rules/03` |
| Hiking Trail refill to 3 cards at each turn's end; Elegant Cape (+30 on a Stage 1, so Houndstone is 160 from 130); Giant Cape, Leaf Cape | many | Card text; engine `get_effective_total_hp` (`played_card.rs:290-310`) is stage-gated and recomputed on evolve |
| Garchomp's Mach Stealth after a KO; Land Crush 120; Carefree Steps coin | `012927` g1 t5 @194-196 | Card text |
| Vespiquen ex's Chase Order (discard a benched Grass Basic for +70 = 140) | `213625` t8 @312, t10 @378, t12 @443 | Card text |

### 2.3 Not rules questions

- `214731` t3 @181-182: the opponent's turn ended with the time limit at 0 and no attack. The simulator has no clock; nothing to settle.
- Interface behaviour (end-turn warnings about an unused Supporter or Energy, abandoned retreat prompts such as `012927` t10 @346,
  the "no valid target" banner on Poké Ball) does not change the game state.
- Concessions and the zero-turn Victory in `214518` are results, not rules events.

---

## 3. Human evidence

All 82 owner turns in the 18 packets have the start-of-turn hand recorded (status observed or visible), so every one of his turns
is a position whose hand is fully known; the opponent's hand is a count only (the ledger's `opponent_hand_at_owner_turn_start`).
One packet (`214518`) has no turns: it is a Victory during setup (0 turns, no tactical content). It still counts as a win below.

### 3.1 Which lists are setup decks and which are fast decks

My rule: **fast** = a Basic or one-evolution attacker reaches its best attack by his own turn 2 or 3; **setup** = the best attack
needs a Stage 2 or three or more Energy. "First attack" is his own turn number; "attacked" is the share of his own turns with an attack
(chip attacks such as Lunge Out count).

| List (label) | Class | Why | First attack / attacked (games) |
|---|---|---|---|
| Butterfree / Accelgor (New deck 24) | setup | Stage 2 plus Accelgor line, built with Quick-Grow Extract; attackers cost 1 Energy so it attacks early | #2, 5 of 6 (`213625`); #1, 4 of 4 (`214731`) |
| Mega Blaziken / Combusken (New deck 1) | setup | Stage 2 Mega ex, Combusken first | #3, 1 of 3 (`215749`) |
| Wailord / Mega Sharpedo ex / Suicune ex (New deck 6) | setup | Wailord's best attack costs 4 Energy; Wallace and Irida support | #5, 3 of 7 (`003547`) |
| Hatterene / Aromatisse / Togekiss (New deck 6) | setup | 14 Pokémon, four Stage 2 | #2, 2 of 3 (`031138`) |
| Aegislash / Tinkaton ex / Team Rocket's Tinkaton | setup | Three Stage 2 lines, 3-Energy attacks, Rare Candy dependent; Lunge Out chips meanwhile | #1, 6 of 6 chips; first real attacker on turn 6 (`032023`) |
| Aegislash / Team Rocket's Tinkaton | setup | Same engine, thinner Bench | #1, 3 of 4 (`032857`) |
| Skarmory ex / Aegislash / Orthworm | fast | Basic ex attacker for 2 Energy (Steel Wing 70, +30 with Cursed Metal on the board) | #3, 3 of 5 (`033529`); #2, 2 of 4 (`034229`) |
| Aegislash / Melmetal ex / Magnezone | setup | Magnemite line chips while Melmetal ex builds to Metal Arms | #1, 6 of 8 (`034953`) |
| Nidoking / Nihilego / Darkrai ex (two lists) | setup | Nidoking Stage 2; Darkrai ex needs 3 Energy | #2, 2 of 5 (`123812`); #3, 1 of 4 (`124532`) |
| Scolipede / Mega Sableye ex | fast | Mega Sableye ex is a Basic with a 2-Energy 80-damage attack; Scolipede line behind it | #2, 4 of 5 (`183108`); #1, 3 of 3 (`012140`) |
| Terapagos ex / Silvally / Persian | setup | 3 and 4 Energy attackers, Rainbow Cave; two turns lost to Feelin' Fine | #1, 2 of 5 (`012927` g1) |
| Conkeldurr / Sandslash / Hitmonchan ex | fast | Sandslash (Stage 1, 1 Energy) attacks from turn 2; Hitmonchan ex a Basic | #2, 8 of 9 (`020518`) |
| Snorlax ex / Team Rocket's Persian / Silvally (Water) | setup | Snorlax ex's attack costs 4 | no attack in 2 turns (`012927` g2, opponent conceded) |

Eleven setup lists, three fast lists. Build-up positions below come from setup decks, tempo positions from fast ones.

### 3.2 Best candidate positions (not built)

Tags: **prep** = preparing an attacker; **sac** = managing a sacrifice; **win** = immediate win or KO; **adapt** = adapting to new
information. "Opp list" is only what the video showed; unseen cards are unknown. Seconds are the span of the turn in that recording.

Ordered by how much I think each would teach.

**P1. `020518` t15 then t17, @486-506 and @570-573. Conkeldurr / Sandslash / Hitmonchan ex (fast). Tags: prep, sac, win.**
Hand (t15): Cyrus, Rare Candy, Conkeldurr (A3 096), Professor's Research. Board: Active Sandslash 30/90 (1 Fighting), Sandshrew 60/60
(1 Fighting) on the Bench; points 2 to 1 for him. Opp: Copperajah 60/160 with 3 Metal Active, Cufant 90, Togedemaru 70, Team Rocket's
Tinkatuff 80 (1 Metal); hand 4. He played Research, Poké Ball (to Hitmonchan ex, benched with no Energy), benched Timburr with an
Energy, and used Fury Swipes (30), leaving Copperajah at 30. The opponent KO'd Sandslash (Heavy Impact 80, opponent point 2); he
promoted the unenergised Hitmonchan ex and won with one Energy and Quick Straight 50 (t17 hand: Cyrus, Rare Candy, Conkeldurr, Sandslash).
A two-turn line where the 30 HP Active Sandslash is the sacrifice and Hitmonchan ex is the finisher (whether he planned it that way is
not recorded). Opp list (approx): Copperajah, Cufant, Stakataka, Togedemaru, Team Rocket's
Tinkatink / Tinkatuff / Tinkaton, May, Professor's Research.

**P2. `183108` t9, @318-351. Scolipede / Mega Sableye ex (fast). Tags: sac, win.**
Hand: Cyrus, Lucky Ice Pop, Mega Sableye ex. Board: Active Mega Sableye ex 40/170 (2 Darkness, Deceptive Needle), empty Bench; points
1 to 1. Opp: Houndstone 70/130 (2 Psychic) Active, Greavard 70/70, Meloetta 10/70; hand 4. He used Lucky Ice
Pop twice (40 to 80), benched a second Mega Sableye ex with an Energy, and used Cursed Jewel (80 + 20 Weakness) to KO Houndstone for
1 point; Cyrus stayed in hand (the game warned about the unused Supporter and he continued). The opponent evolved Greavard into
Houndstone and Last Respects (170) KO'd the 80 HP Mega for 3 points and the game (2 to 3). Good continuation experiment: is the
Active Mega at 80 HP the right sacrifice, and does Cyrus on Meloetta or Greavard change anything. The Cursed Jewel decision in 2.1 matters
here. Opp list (approx): Pumpkaboo, Gourgeist, Greavard / Houndstone, Meloetta, Chingling, Peculiar Plaza, Professor's Research.

**P3. `034953` t6, @150-162. Aegislash / Melmetal ex / Magnezone (setup). Tag: prep.**
Hand: Aegislash, Aegislash, Magneton. Board: Active Magnemite 60/60 (1 Metal); Bench Honedge 60/60 and Melmetal ex 170/170 (1 Metal, Steel
Apron). Opp: Fraxure 50/90 Active; Munchlax 50/50, Haxorus 150/150 (1 Fire, 1 Metal) on the Bench; hand 3; 0 to 0. He evolved
Magnemite to Magneton (Rolling Attack needs 2 Energy, it had 1), attached the Energy to Melmetal ex and ended the turn with no attack.
Alternative: keep Magnemite and Tackle for 20. A clean "give up a small attack to build the real attacker" decision; the game went 16
turns and Metal Arms (180) did the work on turns 12 and 14. Opp list (approx): Axew, Fraxure, Haxorus, Munchlax, Happiny, Rainbow Cave.

**P4. `032023` t12, @397-439. Aegislash / Tinkaton ex / Team Rocket's Tinkaton (setup). Tags: prep, adapt.**
Hand: Aegislash, Team Rocket's Tinkaton, Aegislash, Professor's Research (Research then drew Rare Candy and Tinkaton ex). Board:
Active Honedge 60/60 (2 Metal); Bench two Team Rocket's Tinkatink at 10/60, one with 2 Metal; points 0 to 1. Opp: Wugtrio ex 120/140
(3 Water) Active, Finizen 60/80 with Giant Cape (2 Water), Comfey 70/70, Manaphy 30/50. He used Rare Candy on the Active Honedge
(Aegislash, Superb Shield), added the third Metal, and hit Wugtrio ex 120 to 40. The alternative is Rare Candy on the benched
Tinkatink holding 2 Metal. Aegislash had sat in his hand from his first turn (t2) to t12, six of his turns, which is the whole deck's problem.
Opp list (approx): Finizen / Palafin, Wugtrio ex, Wiglett, Manaphy, Comfey, Giant Cape, X Speed, Lucky Ice Pop.

**P5. `214731` t6, @246-280. Butterfree / Accelgor (setup). Tag: sac.**
Hand: Accelgor, Lucky Ice Pop, Hiking Trail. Board: Active Butterfree 10/130 (1 Grass); Bench Shelmet 70/70, Accelgor 80/80 (1 Grass),
Metapod 80/80. Opp: Mega Rayquaza ex 90/180 with Rocky Helmet, Dragonair with Leftovers, Cyclizar; hand 3. He replaced the Stadium,
evolved a Shelmet to Accelgor, healed Butterfree 10 to 50 with Lucky Ice Pop twice, retreated it, attached an Energy, and used Deck and
Cover (Poison and Paralysis, Accelgor shuffled into the deck), then promoted Butterfree and let Hiking Trail refill. A multi-step line
with several valid orders and the Rocky Helmet interaction from 2.2. Won 3 to 0. Opp list (approx): Mega Rayquaza ex, Dratini / Dragonair
/ Cyclizar, Rocky Helmet, Leftovers, Rainbow Cave, Copycat.

**P6. `031138` t6, @181-196. Hatterene / Aromatisse / Togekiss (setup). Tags: prep, win.**
Hand: Hatterene, Togetic, Togekiss, Hatterene, Togepi. Board: Active Aromatisse 70/90 (1 Psychic); Bench Hattrem 60/80 (1 Psychic),
Hatenna 40/60. Opp: Tapu Koko ex 90/130 (3 Lightning, Confused) Active, Zeraora 90/90, Greninja 120/120; hand 2. He benched Togepi,
evolved Hattrem to Hatterene, retreated Aromatisse (1 Psychic), attached the second Psychic and used Mental Crush for 140 on the
Confused Koko ex, a 2-point KO. Five steps in one turn, each constrained by Energy. Opp list (approx): Tapu Koko ex,
Zeraora, Greninja, Froakie, Electric Generator, Rare Candy.

**P7. `034229` t5, @214-228. Skarmory ex / Aegislash / Orthworm (fast list, build-up turn). Tag: prep.**
Hand: Metal Core Barrier (two arts), Aegislash (Cursed Metal, 140 HP), Lucky Ice Pop, Rare Candy. Board: Active Skarmory ex 140/140 (no
Energy); Bench Honedge (1 Metal); points 0 to 1. Opp: Mega Gardevoir ex 200/210 (2 Psychic) Active, Mega Diancie ex 170 (3 Psychic), two
Mewtwo ex; hand 1. He used Rare Candy on Honedge, put a Barrier on Skarmory ex, attached the one Energy to Skarmory ex (1 of the 2 it
needs) and did not attack. Which attacker gets the Energy is the whole question. Opp list (approx): Ralts, Mega Gardevoir ex, Mega Diancie
ex, Mewtwo ex, Peculiar Plaza, Copycat, Rare Candy.

**P8. `213625` t5, @209-221. Butterfree / Accelgor (setup). Tag: prep.**
Hand: Butterfree, Butterfree, Poké Ball. Board: Active Metapod 80/80 (1 Grass); Bench Shelmet 70, Caterpie 40, Shelmet 70; points 1 to 0.
Opp: Pinsir 90/90 Active, Exeggcute, Teal Mask Ogerpon ex, Combee (1 Grass); hand 3. He played Poké Ball (no Basic left, no effect),
evolved Butterfree, put the Energy on a benched Shelmet (for the Accelgor line) instead of the Active, and Sunny Wind took Pinsir to 30.
A clean "Energy to the next attacker" decision. Opp list (approx): Pinsir, Exeggcute, Combee, Budew, Teal Mask Ogerpon ex, Vespiquen ex,
Leaf Cape, Fragrant Forest, Hiking Trail.

**P9. `032857` t4, @123-142. Aegislash / Team Rocket's Tinkaton (setup). Tag: prep.**
Hand: Aegislash, Doublade, Team Rocket's Tinkaton, Rare Candy, Metal Core Barrier twice. Board: Active Honedge 60/60 (1 Metal), one
Team Rocket's Tinkatink on the Bench, nothing else. Opp: Ivysaur 130/130 with Leaf Cape alone, hand 4. He used Rare Candy on his second
turn (Aegislash), a Barrier, a second Metal, and did not attack (Slicing Blade needs 3). He never had more than two Pokémon in play and
lost 0 to 2 when the last one fell. Tests whether the pilot overcommits to one attacker on a thin Bench. Opp list (approx): Bulbasaur /
Ivysaur / Mega Venusaur ex, Leaf Cape, Sabrina, Serena, Quick-Grow Extract.

Left out on purpose: `214731` t8 (a trivial immediate win, KO'd Mega Rayquaza ex at 20 HP), `003547` t9 (Wailord heal-and-attack, good but
a repeat of the 4-Energy theme), `213625` t11 (a lost game's last turn; Deck and Cover at 110 to 60 decided nothing).

---

## 4. Decks worth his time

### 4.1 Results per list (every win counts as a win, concession and the zero-turn Victory included)

| List | Games (W-L) | Notes: what beat him, or how it won |
|---|---|---|
| Butterfree / Accelgor (New deck 24) | `213625` L 2-3; `214731` W 3-0; `214518` W (0 turns). 2-1 (1-1 without the zero-turn game) | Lost to Vespiquen ex's Chase Order (140 three times, Leaf Cape, Ogerpon ex's Soothing Wind blocking Poison). Won against Mega Rayquaza ex with Helmet. Only `213625` has the exact QR list; the other two are the same label and the same core, version unverified |
| Mega Blaziken / Combusken (New deck 1) | `215749` W 1-0 (opponent conceded after turn 5) | Thin: three turns, one attack |
| Wailord / Mega Sharpedo ex / Suicune ex | `003547` L 0-3 | Gourgeist's Soul Shot 70 (three times) then Houndstone's Last Respects 130 (twice). Four Energy for Wailord's best attack |
| Hatterene / Aromatisse / Togekiss | `031138` W 2-0 (opponent conceded) | Mental Crush 140 on a Confused Tapu Koko ex |
| Aegislash / Tinkaton ex / Team Rocket's Tinkaton | `032023` L 0-3 | Aegislash and Team Rocket's Tinkaton sat in hand for six turns; Wugtrio ex's Pop Out Throughout picked off the Bench; Finizen to Palafin |
| Aegislash / Team Rocket's Tinkaton | `032857` L 0-2 | Mega Venusaur ex 270 HP (Leaf Cape), Sabrina, Critical Bloom (Poison and Sleep); thin Bench ran out |
| Skarmory ex / Aegislash / Orthworm | `033529` L 1-3; `034229` L 0-3 (version unverified) | Mega Lucario ex with Arena of Antiquity; Mega Gardevoir ex / Mega Diancie ex / Mewtwo ex. 0-2 |
| Aegislash / Melmetal ex / Magnezone | `034953` W 2-1 (opponent conceded, turn 16) | Slow build, Metal Arms 180 won it |
| Nidoking / Nihilego / Darkrai ex (two Darkrai) | `123812` L (he conceded at 1-2) | Mega Gardevoir ex and Mega Diancie ex outpaced Nidoran |
| Nidoking / Nihilego / Darkrai ex (one Darkrai) | `124532` L 0-3 | Charizard ex's Crimson Storm 200 on Darkrai ex |
| Scolipede / Mega Sableye ex | `183108` L 2-3; `012140` W 2-0 (opponent conceded; list unbound). 1-1 | Lost to Houndstone's Last Respects 170 on an 80 HP Mega (see P2). Won against Dialga ex with Poison plus Venoshock 120 |
| Terapagos ex / Silvally / Persian | `012927` g1 L | Garchomp (Land Crush 120 plus Mach Stealth); two turns spent on Feelin' Fine |
| Conkeldurr / Sandslash / Hitmonchan ex | `020518` W 3-2 (17 turns) | Won on Hitmonchan ex's Quick Straight after Sandslash was KO'd (P1) |
| Snorlax ex / Team Rocket's Persian / Silvally (Water) | `012927` g2 W (opponent conceded after 2 turns) | No attack was made; tells us nothing about the list |

Overall 8 wins and 10 losses across the 18 packets; one list got two or three games, most got one, so none of this ranks lists.

What beat him, where the record is clear:
- In at least four of the ten losses the last KO was on his own ex or Mega ex (Mega Sharpedo ex and Mega Sableye ex for 3 points each,
  Darkrai ex and Snorlax ex for 2): a list that spends ex Pokémon gives up 2 or 3 points a KO.
- Psychic decks with Last Respects or Mega ex (Houndstone twice, Gardevoir / Diancie twice) account for four losses.
- Stage 2 lists reached their attacker late: in `032023` Aegislash sat in hand for six of his turns before Rare Candy arrived; in `033529`
  Doublade, Aegislash and Rare Candy were in his opening hand but the first Honedge came down on turn 3 and Aegislash only on turn 7.
- Lucky Ice Pop was played 29 times on 18 of his 82 turns; healing 20 at a time did not outrun 100-plus damage.

### 4.2 Is any list worth a simulator screen?

The only simulator check allowed today is the floor check (km3 on both sides, 1,920 games per list, bar 20%, band about plus or minus
1.8); ranking stays on hold. It costs about 4 minutes of the laptop's time per list (km3 runs about 8.6 games a second on the laptop) and none of
his, but it only says "not broken", and each list first needs writing as a deck file (all 14 are in `NEW_DECK_ENTRIES.json` /
`EDITED_DECK_ENTRY.json`, one small job). The 15-minute games he plays are the expensive part, so a screen is worth it only where it would
change which list he plays next:

1. **Conkeldurr / Sandslash / Hitmonchan ex.** Exact QR list, the only fast list with a clean win (3 to 2, attacked on 8 of 9 turns), and its
   win came from a plan the bot could be asked about (P1).
2. **Aegislash / Melmetal ex / Magnezone.** Exact QR list, a 16-turn win, and its game is a slow build the bot's planning should show.
3. **Scolipede / Mega Sableye ex** (exact QR list, 1 to 1), but only after the Cursed Jewel decision in 2.1, otherwise the screen
   undercounts its retaliation.

I would not screen the Aegislash / Tinkaton lists, the Skarmory lists, the Nidoking lists or Terapagos / Silvally / Persian: the
losses had a common cause (late or missing Stage 2 or thin Bench) that a floor check would not explain, and he can see that directly in the
packets. Hatterene and Mega Blaziken have one short win each; not enough to point at.

---

## 5. Pending

Nothing is pending in the batch. All 18 game packets carry an accepted `LEAD_ACCEPTANCE.json` and a `REGISTRATION_RESULT.json`; the
last three accepted were `012140` (21:06 UTC), `020518` (21:10) and `183108` (21:14), and `BATCH_COMPLETION_CHECK.json` (verified
2026-10-06 21:16:55 UTC, 17 sources, 18 games, all complete) says the batch is finished. If three packets were still awaiting
acceptance when the request was written, they have been accepted since. Noted only.

---

## Files in this folder

- `ENGINE_COVERAGE.md`: the per-list card tables, the opponent card table with the games each appears in, and the RulesUnverified check.
- `scripts/cov.py`, `scripts/make_cov_md.py`: build the coverage tables from the batch, the card data and the engine's status dump.
- `scripts/cand.py`: prints the hand, seconds and opponent cards for the candidate turns in 3.2.
- `scripts/helmet_scratch_test.rs`: the scratch engine test described in 2.2 (Deck and Cover into Rocky Helmet). It was run in a private
  copy of the engine (passed); it is not meant for the engine's test folder.
- The script paths point at the batch folder and the pinned engine's status dump on Dustin's machine; they only read those and write
  their own output next to themselves (`cov.json`, `cov_summary.txt`, `out/ENGINE_COVERAGE.md`), which are not committed.
