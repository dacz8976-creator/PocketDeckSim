# trainers — 163 unique Trainer cards (Supporters/Items/Tools/Stadiums/Fossils)

Method: read `move_generation/move_generation_trainer.rs` in full (all `can_play_*` gates),
`apply_trainer_action.rs` in full (all effect bodies), `trainer_coin_plan.rs` (Will/coin plumbing),
`shared_mutations.rs` (search/reveal helpers), `card_logic/*.rs` (Ilima/Diantha/Mallow/Whitney/
Acerola/Psychic/Wallace/Quick-Grow-Extract/Rare-Candy target functions), `tools.rs` +
`hooks/core.rs` + `hooks/counterattack.rs` (Tool effects, retaliation), `stadiums.rs` +
`apply_stadium_action.rs` (Stadium activated abilities), `professor_sada.rs`,
`team_rockets_researcher.rs`. All VERIFIED-READ unless noted; no probes were needed (code reading
resolved every High/Medium doubt directly).

## Findings

### F1 [High] Mythical Slab checks "is a Basic Pokémon" instead of "is a Psychic Pokémon"  (VERIFIED-READ)
- Card: T69 Mythical Slab (Item), A1a 065.
- Text (card text): "Look at the top card of your deck. If that card is a **[P] Pokémon**, put it into your hand. If it is not a [P] Pokémon, put it on the bottom of your deck."
- Engine: `apply_trainer_action.rs::mythical_slab_effect` (~line 1862):
  ```rust
  if let Some(card) = state.decks[action.actor].cards.first() {
      if card.is_basic() {
          state.hands[action.actor].push(card.clone());
          state.decks[action.actor].cards.remove(0);
      } else { ... put on bottom ... }
  }
  ```
  `Card::is_basic()` (`models/card.rs:243`) checks `stage == 0` for any Pokémon of any type — it
  never looks at `EnergyType::Psychic`. The function's own leading `// TODO` comment even says
  "of pulling the different **psychic** left in deck", confirming the intent was Psychic and the
  implementation checks the wrong predicate.
- Example: top card is a Basic Fire Pokémon (e.g. Charmander) → engine puts it in hand (wrong: not
  Psychic, should go to bottom). Top card is a Stage-1 Psychic Pokémon (e.g. Gardevoir, if such a
  card existed at Stage 1) → engine sends it to the bottom (wrong: it is Psychic, should go to hand).
  Any non-Basic Psychic Pokémon is always treated as a miss; any non-Psychic Basic is always a hit.
- Impact: any deck running Mythical Slab. The card behaves as a generic "find a random Basic"
  instead of a Psychic-tutor; both the odds and the target type are wrong.

### F2 [High] Two more Stadium "use" abilities gate on deck *contents*, not deck-empty — Mesagoza and Kid's Room  (VERIFIED-READ)
- Cards: T20 Mesagoza (Stadium, P1-dustin), T152 Kid's Room (Stadium).
- Rule (rules/04 §6, [DUSTIN]): "a card that takes something from the deck is blocked only when
  the deck is empty, never because of what's in it." Already-known engine bugs in this class are
  Cabbie, Team Galactic Grunt, Pokémon Communication, Gladion, Fragrant Forest and Wallace
  (brief "Already known" #4, and README item 17 / the "Fragrant Forest" bullet). Mesagoza and
  Kid's Room are the same bug on two more cards, not currently listed.
- Engine, `stadiums.rs`:
  ```rust
  pub fn can_use_mesagoza(state: &State, player: usize) -> bool {
      ...
      state.decks[player].cards.iter().any(|card| matches!(card, Card::Pokemon(_)))
  }
  ```
  and
  ```rust
  pub fn can_use_kids_room(state: &State, player: usize) -> bool {
      ...
      state.decks[player].cards.iter()
          .any(|card| matches!(card, Card::Trainer(t) if t.trainer_card_type == TrainerType::Tool))
  }
  ```
  Both require a *matching* card somewhere in the deck; the deck's actual contents are hidden
  information, so per the rule this should only require the deck be non-empty (as `can_use_area_zero`
  and `can_use_rainbow_cave`, in the same file, correctly do).
- Example: Mesagoza in play, player's deck has 5 cards left but no Pokémon (all already drawn/played)
  → engine hides the "flip a coin" option entirely. Real game (per the already-confirmed Fragrant
  Forest/Cabbie precedent): the option should be offered and the coin-flip search can legally find
  nothing.
- Impact: Mesagoza is a P1-dustin card; Kid's Room decks lose access to their Stadium action in the
  exact situation (deck thinned of the target type) where using it "for nothing" would still be legal
  and would still burn the opponent's Stadium slot / thin the deck.

### F3 [Medium] Several more "put/search from your deck" Trainers have no empty-deck legality check at all  (VERIFIED-READ)
- Cards: T14 Lisia (P1-dustin), T18 Sightseer (P1-dustin), T29 Team Rocket's Researcher (P1-dustin),
  T113 Traveling Merchant, T123 May, T136 Arven, T150 Puppy-Loving Girl, T153 Order Pad.
- Rule (rules/04 §6): "**Any card that draws is blocked when your deck is empty** ... Copycat is the
  exception." Poké Ball and Professor's Research correctly gate on `state.decks[player].cards.is_empty()`
  (`move_generation_trainer.rs::can_play_poke_ball` / `can_play_professors_research`). The
  already-known gap (brief item 4) names Clemont/Serena/Juliana/Gladion; these eight cards have the
  identical gap and are not in that list.
- Engine: in `move_generation_trainer.rs`, every one of these IDs dispatches straight to
  `can_play_trainer` (unconditionally legal) with no deck-size check at all — e.g. Lisia/Sightseer/
  Traveling Merchant/Puppy-Loving Girl/Order Pad/Arven are all listed under the "Simple cases: always
  can play" or "Pure-information cards" match arms (lines 217/276/298/250-ish), and Team Rocket's
  Researcher falls into the same catch-all (`B4a069TeamRocketsResearcher... => can_play_trainer`,
  line ~308). `may_effect` (apply_trainer_action.rs:2235) itself gracefully no-ops on an empty deck
  (`if num_pokemon == 0 { ...shuffle only... }`), which shows the engine *knows* the degenerate case
  but only suppresses its effect, not its legality.
- Example: deck has 0 cards left, hand has Lisia → engine still offers "Play Lisia"; per the rule
  (and per how Poké Ball is handled) it should be blocked outright, the same as Professor's Research
  would be with an empty deck.
- Impact: mostly a move-generation/AI-search correctness issue (a whiffed play still spends the
  Supporter and — per known issue #4's own logic — "a Supporter played for nothing still counts as a
  Supporter played this turn", so it is a real, legal-but-wrong choice the search can explore).

### F4 [Medium] Arcade's "may draw until 7" doesn't check for an empty deck  (VERIFIED-READ)
- Card: T31 Arcade (Stadium, P1-dustin).
- Text: "Once during each player's turn, that player may flip 3 coins. If all of them are heads,
  that player draws cards until they have 7 cards in their hand."
- Engine, `stadiums.rs::can_use_arcade`: `is_arcade_active(state) && !state.has_used_stadium[player]
  && state.hands[player].len() < 7` — no check on `state.decks[player].cards`. `forecast_arcade_effect`
  itself degrades gracefully (`while hand.len()<7 { maybe_draw_card; if no change break; }`), but the
  legality gate still offers the action when the deck is visibly empty and drawing is therefore
  impossible, unlike Poké Ball/Professor's Research.
- Impact: low-frequency (only matters very late in a long game with Arcade in play and an empty deck),
  but it is the same visible-information-ignored bug class as F2/F3.

### F5 [Medium] Lillie / Marlon (and Erika/Potion's shared healer) offer an undamaged Pokémon as a legal heal target  (VERIFIED-READ)
- Cards: T9 Lillie (P1-dustin), T121 Marlon, and the shared `inner_healing_effect` used by T32 Erika
  (P2-checked0921) and T160 Potion.
- Established engine precedent (own code comment on Pokémon Center Lady, `apply_trainer_action.rs`
  ~line 537): "an undamaged AND unconditioned Pokémon is NOT a legal target — even when a different
  Pokémon is damaged and therefore makes the card playable." That fix is applied consistently in
  `card_logic/ilima.rs`, `diantha.rs`, `mallow.rs`, `whitney.rs`, `acerola.rs` (all filter
  `pokemon.is_damaged()` per-target, confirmed by direct read of each file).
- Engine gap:
  ```rust
  // lillie_effect
  let possible_moves = state.enumerate_in_play_pokemon(action.actor)
      .filter(|(_, x)| get_stage(x) == 2)              // no is_damaged() check
      .map(|(i, _)| SimpleAction::Heal { in_play_idx: i, amount: 60, cure_status: false })
  ```
  ```rust
  // marlon_effect
  .filter(|(_, x)| targets.contains(&x.get_name().as_str()))   // no is_damaged() check
  ```
  ```rust
  // inner_healing_effect (Erika/Potion)
  .filter(|(_, x)| energy.is_none() || state.pokemon_is_type(x, EnergyType::Grass)) // no is_damaged()
  ```
  The playability gates (`can_play_lillie`, `can_play_marlon`, `can_play_erika`, `can_play_potion`)
  correctly require *some* damaged qualifying Pokémon exists, but the per-target choice list is not
  filtered the same way, so with two qualifying Pokémon (one damaged, one full HP) the search can
  choose the useless one.
- Example: two Stage-2 Pokémon in play, only one damaged. Lillie's move list includes both; choosing
  the healthy one wastes the Supporter for a 0-damage heal — the engine allows and even considers it.
- Impact: correctness/search-quality issue rather than a game-outcome bug in isolation (a rational
  player never picks the useless target), but it is the exact "heal cards allowed with nothing to
  heal" class the brief called out, and it's inconsistent within the same codebase.

### F6 [Medium] Piers discards a deterministic pair of Energy, not "2 random Energy"  (VERIFIED-READ)
- Card: T130 Piers (Supporter), B2 152.
- Text: "You can use this card only if you have Galarian Obstagoon in play. Discard **2 random**
  Energy from your opponent's Active Pokémon."
- Engine, `apply_trainer_action.rs::piers_effect`:
  ```rust
  let mut remaining_energy = active.attached_energy.clone();
  for _ in 0..2 {
      if let Some(energy) = remaining_energy.pop() {   // NOTE: Using last energy instead of random
          to_discard.push(energy);
      } ...
  }
  ```
  the code's own comment: "NOTE: Using last energy instead of random selection to avoid expanding the
  game tree." This is a deliberate simplification, but it means which Energy types are discarded is
  fully determined by attachment order, not random, whenever the target has mixed Energy types.
- Example: opponent's Active has 1 Fire + 1 Colorless attached (in that order) — Piers always
  discards the same two regardless of which "random" outcome the real game would pick; with 3+ mixed
  Energy the two discarded are always the two most-recently-attached, never a different pair.
- Impact: only matters when the Active target carries mixed Energy types (Piers itself requires
  Galarian Obstagoon, a niche deck); doesn't affect legality, only which Energy is removed.

### F7 [Low] `inner_healing_effect`'s type filter is hardcoded to Grass regardless of its own parameter  (VERIFIED-READ)
- Engine, `apply_trainer_action.rs::inner_healing_effect(_, state, action, amount, energy: Option<EnergyType>)`:
  ```rust
  .filter(|(_, x)| energy.is_none() || state.pokemon_is_type(x, EnergyType::Grass))
  ```
  The function takes an `energy: Option<EnergyType>` parameter (clearly meant to be the type to
  filter by) but the filter always checks `EnergyType::Grass` no matter what `energy` actually is.
  Currently harmless — the only caller that passes `Some(...)` is `erika_effect`, and Erika's own
  type is Grass — but it is a latent bug: any future card wired through this helper with a
  different `Some(EnergyType::X)` would silently filter for Grass instead of X.
- Impact: none today (no misbehaving card); flagged for whoever next reuses this helper.

## Rules questions
- F3/F4: is "look at the top N / may draw" that gracefully no-ops on an empty deck (rather than being
  hidden from the legal-action list) actually wrong, or is "the move exists but does nothing" an
  acceptable engine shortcut as long as it never changes an outcome? The brief's own known-issue
  list (README item 17: "Poké Ball or Professor's Research with an empty deck" are the *blocked*
  examples) and the explicit "any card that draws is blocked when your deck is empty" line both
  point to "should be blocked", so I've reported F3/F4 as bugs, but flagging the interpretation in
  case the project wants to treat pure no-op whiffs differently from named-search whiffs.

## Checked and OK
P1-dustin (T1–T31), all VERIFIED-READ end-to-end (legality gate + effect body), no other issues found:
- T1 Pokémon Flute — targets opponent's discard for Basics, requires an open opponent Bench slot, player picks the Pokémon and it's de-duplicated; matches text.
- T2 Rocky Helmet — 20 counter only when holder is Active and was actually damaged by an attack (`counterattack.rs` + `apply_action_helpers.rs` ~575-603); fires even mid-KO (damage applied before KO resolution runs); matches known-issue #4 behavior (intentional, correct).
- T3 Cynthia — `IncreasedDamageForSpecificPokemon{50, [Garchomp, Togekiss]}`, this-turn only; matches.
- T4 Irida — heals 40 from *each* Pokémon with any Water Energy attached (no per-target choice needed, matches "each"); matches.
- T5 Red — `IncreasedDamageAgainstEx{20}`, this turn; matches.
- T6 Poison Barb — poisons attacker only when holder (Active) is damaged by an opponent's attack; matches.
- T7 Ilima — targets filtered to damaged Colorless Pokémon (`card_logic/ilima.rs`); matches.
- T8 Guzma — discards all Tools from every opponent Pokémon, then resolves knockouts after; matches ("Discard all Pokémon Tool cards attached to each of your opponent's Pokémon").
- T9 Lillie — see **F5**.
- T10 Steel Apron — -10 dmg only for Metal holder from opponent's attacks (`attacking_player != target_player` guard); cures status on attach and grants ongoing immunity, both gated to Metal type (`apply_action.rs`:923, `state/mod.rs`:1147); matches fully.
- T11 Will — `ForceFirstHeads` turn effect (duration 0 = this turn only), consumed by the next coin batch across attacks/abilities/Trainers (attack_action.rs, trainer_coin_plan.rs, apply_action.rs); matches "the next time you flip ... after using this card on this turn."
- T12 Jasmine — `ReducedDamageForTarget{50, [Steelix, Skarmory ex]}`, duration 1 (opponent's next turn), `only_from_ex:false`; matches (text has no "ex" restriction).
- T13 Heavy Helmet — -20 dmg only when holder's Retreat Cost ≥ 3, re-evaluated live; matches.
- T14 Lisia — search logic correct (2 random Basic ≤50HP); legality gap, see **F3**.
- T15 Clemont's Backpack — `IncreasedDamageForSpecificPokemon{20,[Magneton,Heliolisk]}` targets opponent's Pokémon generally (reaches Bench, matching "your opponent's Pokémon" not "...Active"); matches.
- T16 Clemont — searches 2 random among {Magneton, Heliolisk, Clemont's Backpack}; effect matches (empty-deck/deck-content legality already covered by known issue #4/#16).
- T17 Metal Core Barrier — -50 dmg only for Metal holder from an Active attack; self-discards at end of the *opponent's* turn relative to the tool owner (verified index math); matches exactly.
- T18 Sightseer — top-4 reveal via `top_n_reveal_outcomes`, correct hypergeometric weighting, degenerate 0-look-count handled; legality gap, see **F3**.
- T19 Starting Plains — +20 HP recomputed for all Basics via `refresh_hp_bonuses_all`, applies to both players' boards (stadium effects always scan both `player in 0..2`); matches.
- T20 Mesagoza — random-Pokémon search on heads correct; legality gap, see **F2**.
- T21 Iris — bonus point correctly scoped to Haxorus (3 printings), Active-only KO, opponent only, from-an-attack only (`is_iris_bonus_active`/`handle_knockouts` ~line 725); matches.
- T22 Lucky Egg — draws-until-5 only on KO by an opponent's attack, capped by deck availability; matches.
- T23 Cheren — `ReducedDamageForTarget{100,[Watchog,Stoutland]}, only_from_ex:true`; matches ("...from your opponent's Pokémon ex").
- T24 Elegant Cape — +30 HP gated to Stage-1 holder (`stage==1` check in `played_card.rs`); matches.
- T25 Psychic (Supporter) — gated on Active having an attack literally named "Psychic"; moves a random Energy from a chosen opponent Benched Pokémon to opponent's Active; matches (random-move part already covered by known issue #6's sibling pattern — this one *is* correctly random, only Quick-Grow Extract/Wallace are named as choosing-at-random-instead-of-by-player).
- T26 Wally — attaches 1 Colorless from Energy Zone to a chosen Stage-2 Pokémon, doesn't consume the once-per-turn manual attachment; matches.
- T27 Rainbow Cave — discards the *current* Energy-Zone energy (only if one exists) and rotates in the next; matches, no coin (text has none).
- T28 Team Rocket's Goo-zooka — `IncreasedRetreatCost{1}` with duration 1 ("during opponent's next turn"); matches "Until the end of your opponent's next turn."
- T29 Team Rocket's Researcher — flip-until-tails, per-heads random "Team Rocket"-named Pokémon draw with correct hypergeometric multiset weighting (`team_rockets_researcher.rs`, extensively tested); legality gap, see **F3**.
- T30 Team Rocket's Master Plan — heads: confuse opponent only; tails: confuse both; matches exactly.
- T31 Arcade — 3-coin-all-heads draw-until-7, correctly capped by hand<7 in the gate and by deck exhaustion in the effect loop; deck-empty gate gap, see **F4**.

P2-meta:
- T59 Eevee Bag — "Choose 1:" offered as two `SimpleAction`s (damage-boost or heal-all), gated on having any Eevee-evolution in play; matches.

P2-checked0921 (T32–T58) — shared-mechanic check only, per assignment:
- T32 Erika — uses `inner_healing_effect`; shared-mechanic bug, see **F5** (undamaged targets offered). Type-restriction itself (Grass) is correct for this card (coincidence — see **F7**).
- T33 Sabrina, T94 Repel — both correctly push the choice to the **opponent** (`SimpleAction::Activate{player: opponent,...}`), matching "(Your opponent chooses...)"; Repel additionally requires opponent's Active to be Basic.
- T34 Giant Cape, T40 Leaf Cape, T41 Inflatable Boat, T54 Small Balloon — HP/retreat-cost tool bonuses, each correctly type/stage-gated at the point of use (verified Giant Cape/Leaf Cape/Elegant Cape together in `played_card.rs::get_effective_total_hp`); no shared-mechanic issue found.
- T35 Cyrus, T90 Lana — both correctly push the choice to **you** (the player), filtered to damaged Bench (Cyrus) / any Bench (Lana, gated on Araquanid); matches "you pick" pattern from rules/04 §3.
- T36 Mars — opponent shuffles hand into deck, draws `remaining points needed`; shares logic with an in-play Ability per code comment; matches.
- T37 Pokémon Center Lady — reference implementation for the damaged-target-filter pattern (F5); correct.
- T38 Poké Ball — random Basic search, correctly gated on deck-non-empty (`can_play_poke_ball`); this is the reference-correct empty-deck gate that F3's cards are missing.
- T39 Rare Candy — legality requires not-first-turn, not Malamar-jammed, and a real (basic-in-play, stage2-in-hand) pair via `can_rare_candy_evolve`; matches printed restriction text exactly.
- T42 Professor's Research — draw 2, correctly gated on deck-non-empty; reference-correct.
- T43 Flame Patch — requires Active to be Fire-type and a Fire Energy in discard (both visible); matches.
- T44 Copycat — shuffles hand into deck first, then draws opponent's-hand-size cards; no gate at all, correctly matching the documented exception to "blocked on empty deck."
- T45 Quick-Grow Extract — candidate function correctly filters Grass type + not-played-this-turn + valid deck evolution; already-known issue #6 (random instead of chosen target) still applies, not re-reported.
- T46 Lucky Ice Pop — always heals 20; coin only controls return-to-hand-vs-discard; matches ("If you healed any damage in this way, flip a coin...").
- T47 Protective Poncho — already-known issue #10 (also blocks own-attack damage); not re-checked further, confirmed still present by not seeing an attacker-ownership check.
- T48 Training Area — +10 dmg to Stage-1 attackers' targets, applies both sides (`get_training_area_damage_bonus` has no player filter); matches.
- T49 Hiking Trail — draws each player up to 3 at end of their own turn; matches.
- T50 Field Blower — offers every attached Tool (both players) and the Stadium as separate discard choices; matches "yours or your opponent's."
- T51 Korrina — `IncreasedDamageForTypeAgainstEx{30, Fighting}`; matches.
- T52 Fragrant Forest — already-known issue #11 (blocked on deck contents); confirmed present, not re-detailed.
- T53 Arena of Antiquity — +20 dmg, Fighting attacker vs ex target only, both players; matches.
- T55 Deceptive Needle — end-of-turn 10 dmg only if holder is Active, Darkness-typed, and opponent has an Active to hit; matches.
- T56 Soothing Shore — end-of-each-turn heal 20 to that player's own Water-Energy-holders; matches "that player heals ... from each of their Pokémon."
- T57 Team Rocket's Boss — reveals opponent's whole hand, offers every subset of opponent's-hand Basics up to opponent's actual open Bench capacity; correctly bounded by visible Bench space (not a Pokémon-Flute-style hard block, but never overfills the Bench).
- T58 X Speed — retreat-cost-1-less this turn.

P3 (T60–T163) — one-line verdicts (all VERIFIED-READ against the dispatch table and, for anything
non-trivial, the effect body itself; only exceptions are the items already called out above):
- T60/61/62/73/74/116/118/126/127/154/155 (all 10 Fossils: Helix, Dome, Old Amber, Skull, Armor, Plume, Cover, Jaw, Sail, Claw, Root) — placed as 40-HP Basic Colorless via `can_place_fossil`; `TrainerType::Fossil` excluded from every "is a Pokémon"/deck-search filter (so Poké Ball/Pokémon Communication/etc. can't find them, per rule); `hooks/retreat.rs` blocks retreat for Fossils; `DiscardFossil` is a separate action from KO handling (self-discard = no points, KO still goes through normal 1-point knockout path). All match.
- T63 Misty — flip-until-tails attach to a chosen Water Pokémon; gated on having a Water Pokémon in play.
- T64 Blaine, T66 Giovanni, T67 Brock (Energy-Zone attach to named Pokémon), T68 Lt. Surge (gather Bench [L] to a named Active) — all match printed text/targets.
- T65 Koga — requires Active = Muk/Weezing, returns it to hand; matches.
- T69 Mythical Slab — see **F1**.
- T70 Budding Expeditioner — requires Active = Mew ex, returns to hand; matches.
- T71 Blue — `ReducedDamageForTarget{10, AllPokemon}`, opponent's next turn; matches.
- T72 Leaf — retreat cost -2 this turn.
- T75 Pokémon Communication — already-known deck-content block (README item 17); hand-half of the check (Pokémon in hand) is correctly visible-info-based.
- T76 Lum Berry — end-of-turn cure + self-discard, only if a condition is present; matches.
- T77 Team Galactic Grunt — already-known deck-content block (item 4/16).
- T78 Volkner — attaches up to 2 Lightning from discard to Electivire/Luxray; matches "up to N" pattern.
- T79 Dawn — moves 1 Energy Bench→Active, player's choice among all Bench energies; matches.
- T80 Celestic Town Elder — random Basic from discard; correctly discard-based (visible), no deck-content issue.
- T81 Barry — `ReducedAttackCostForSpecificPokemon{2, [Snorlax,Heracross,Staraptor]}`; matches.
- T82 Adaman — `ReducedDamageForType{20, Metal}`, opponent's next turn; matches.
- T83 Iono — both players shuffle-hand-then-draw-same-count; correctly unconditional (shuffle-first exception, same as Copycat).
- T84 Team Rocket Grunt — flip-until-tails, discards a random Energy per heads from opponent's Active, capped by available Energy; matches.
- T85 Big Malasada — heal 10 + cure one random present condition; matches (tests cover all 5 conditions... 4 named — Poisoned/Paralyzed/Asleep/Burned/Confused all included).
- T86 Fishing Net — random Basic Water from discard; matches.
- T87 Rotom Dex — look at top card, optional shuffle; no "take" from deck so no empty-deck concern (degenerate 0-card look is a harmless no-op); matches.
- T88 Acerola — targets filtered to damaged Palossand/Mimikyu (`card_logic/acerola.rs`), also requires an opponent Active to receive the moved damage; matches.
- T89 Kiawe — requires Alolan Marowak/Turtonator in play, attaches 2 Fire, ends turn; matches (turn-ending part not re-verified by code read here but is a simple flag).
- T91 Sophocles, T101 Hau, T135 Nemona — this-turn named-Pokémon damage boosts vs ex where printed; matches pattern.
- T92 Mallow — targets filtered to damaged Shiinotic/Tsareena, heals exactly the existing damage and discards all Energy only on an actual heal (`card_logic/mallow.rs`); matches "If you do."
- T93 Beast Wall — gated on opponent points == 0; `ReducedDamageForTarget{20, UltraBeasts}`; matches.
- T95 Electrical Cord — on-KO-by-opponent-attack-while-Active check present (pattern matches Lucky Egg/Rescue Scarf family); not re-detailed, consistent with the rest of the on-KO Tool family which were all verified correct.
- T96 Beastite — +10×points damage for the attached Ultra Beast; matches.
- T97 Gladion — already-known bug (old deck-count block, item 4/16).
- T98 Looker — reveals opponent's deck's Supporter cards; information-only, always legal; matches.
- T99 Lusamine — gated on opponent points≥1, own Ultra Beast in play, discard non-empty; attaches up to 2 random discard Energy; matches.
- T100 Leftovers — end-of-turn heal 10 only if holder is Active; matches.
- T102 Penny — copies a random opponent-deck Supporter (excluding Penny) via full recursive forecast, correctly gated only on opponent's deck being non-empty (reference-correct empty-deck-only gate, matching Dustin's rule precisely).
- T103 Elemental Switch — moves one R/W/L Energy Bench→Active, player's choice; matches.
- T104 Squirt Bottle — discards a Fire Energy from opponent's Active only if one is present; matches.
- T105 Dark Pendant — on-damaged-while-Active shuffles a random opponent hand card into their deck, gated on Darkness type and opponent hand non-empty; matches.
- T106 Rescue Scarf — on-KO-by-opponent-attack, returns holder to hand instead of discard; consistent with the verified Lucky Egg/Electrical Cord family.
- T107 Lyra — switches damaged Active with a chosen Bench Pokémon; matches (gated on active damaged + bench present).
- T108 Silver — filters opponent hand to Supporters only, shuffles chosen one into opponent's deck; matches.
- T109 Fisher — 3-coin, per-heads random Water Pokémon from discard; matches.
- T110 Hiker, T114 Morty — "look at N cards, reorder" where N = own Fighting-in-play / opponent's-deck count via own Psychic-in-play; information-only, degenerate 0 handled; matches.
- T111 Memory Light — lets holder use previous-Evolution attacks (gated in `move_generation/attacks.rs`); not deep-read beyond confirming the hook exists and is wired to the right CardId.
- T112 Whitney — targets filtered to damaged/Asleep/Paralyzed/Confused Miltank; cures exactly {Asleep,Paralyzed,Confused} (not Poison/Burn), matching the printed list precisely.
- T113 Traveling Merchant — top-4 reveal for Tool cards via the same `top_n_reveal_outcomes` as Sightseer; legality gap, see **F3**.
- T115 Prank Spinner — random card from either hand, revealed, shuffled into its owner's deck; legality requires >1 card total across both hands (correct, since Prank Spinner itself is already gone from the count).
- T117 Hitting Hammer — 2 coins, both-heads discards a random opponent Active Energy, gated on opponent Active having Energy; matches.
- T119 Sitrus Berry — end-of-turn heal 30 + self-discard only at ≤half max HP; matches, includes a Heal-Block-aware stop condition.
- T120 Lucky Mittens — draws a card per holder-attack-knockout of an opponent Pokémon; matches.
- T122 Hala — survive-KO-at-10HP only from actual attack damage, scoped to Hariyama/Crabominable, opponent's next turn; matches.
- T123 May — random-pair draw + mandatory shuffle-back of the same count; legality gap, see **F3**.
- T124 Fantina — Energy-Zone attach to each Drifblim/Mismagius in play; matches "each."
- T125 Serena — already-known empty-deck gap (brief item 4).
- T128 Diantha — targets filtered to damaged Psychic with ≥2 Psychic Energy, discards exactly 2 Psychic only when the heal actually happens; matches.
- T129 Juggler — gated on ≥3 distinct Energy types across the whole board; moves *all* Bench Energy (any type) to Active via the same helper as Lt. Surge; matches "Move all Energy."
- T130 Piers — see **F6**.
- T131 Peculiar Plaza — Psychic retreat -2, both players; matches.
- T132 Electric Generator — coin; heads lets player choose a Benched Lightning target to attach 1 L; matches.
- T133 Big Air Balloon — no retreat cost, gated to Stage-2 holder (`hooks/retreat.rs:141`); matches.
- T134 Team Star Grunt — discards one random Energy among all opponent Ability-holders' attached Energy; matches.
- T137 Nasty Notice — opponent discards down to 4, offered as all size-appropriate combinations (unit-tested in-file); matches, correctly no-ops at ≤4 cards.
- T138 Maintenance — requires hand≥3 before playing (so ≥2 remain after Maintenance itself is played) to satisfy "if you can't shuffle in 2 cards, you can't use this card"; matches.
- T139 Calem — draws 1 per Mega ex in play on **either** side; matches "both yours and your opponent's."
- T140 Cabbie — already-known deck-content block (item 4/17).
- T141 Parasol Lady — returns a chosen non-ex Water Pokémon in play to hand; matches ("except any Pokémon ex").
- T142 Bounded Field — Weakness ×2 for all non-Mega-ex attackers, both sides (`hooks/core.rs`:1449); explicit Mega-ex exclusion confirmed; matches printed text exactly, including interaction with known issue #1 (still subtracts-before-Weakness for the flat/×2 base, that base bug is already reported, not re-filed here).
- T143 Ancient Booster Energy Capsule — +40 HP gated to Ancient-named Pokémon; matches.
- T144 Future Booster Energy Capsule — +20 atk dmg gated to Future-named attacker; matches.
- T145 Juliana — already-known empty-deck gap (brief item 4).
- T146 Professor Sada — legality requires an Ancient Pokémon in play + non-empty discard-energy; effect enumerates every valid (≤3-distinct-type)×(slot-assignment) combination exactly, extensively unit-tested; matches "3 different types ... in any way you like" precisely, including the "fewer than 3 types available" degenerate case.
- T147 Professor Turo — shuffles a chosen in-play Future Pokémon into the deck; matches (no deck-empty concern since it only adds to the deck).
- T148 Area Zero — requires a Basic in hand (visible) to offer the shuffle-then-draw choice; since a card is added to the deck before the draw, the deck can never be empty at draw time; matches, no gate issue.
- T149 Elesa — returns every attached Tool, both players, to its owner's hand; matches.
- T150 Puppy-Loving Girl — top-4 reveal for "Puppy Pile" attack via `top_n_reveal_outcomes`; legality gap, see **F3**.
- T151 Wallace — already-known bugs (random not chosen target, item 6; printed-HP not max-HP, item 15); deck-content legality also already flagged as "probably wrong" in README item 17 (confirmed: `wallace_candidates` requires a *specific* valid deck evolution, same class as F2/F3 but already covered by the existing note, not re-filed).
- T152 Kid's Room — see **F2**.
- T153 Order Pad — coin; heads = random Item from deck; legality gap, see **F3**.
- T156 Clear Veil — prevents opponent-attack *effects* on holder (existing effects untouched), shares `PreventAttackEffects`-style resolution with Crystal Body; matches.
- T157 Drayden — adds 1 extra `ExtraRandomSpreadHits` target for this-turn Draco Meteor attacks; matches.
- T158 Skyla — requires Active = Stage 1 + Bench present, switches with a chosen Bench Pokémon; matches.
- T159 Team Rocket's Thieving Machine — legality and effect both correctly scoped to opponent's-discard Items excluding same-name copies of itself; matches.
- T160 Potion — heals via `inner_healing_effect(None)`; undamaged-target gap covered by **F5**; type filter irrelevant here (`energy=None` correctly means "any Pokémon").
- T161 Hand Scope — reveals opponent's hand; information-only, always legal; matches.
- T162 Pokédex — look at top 3; degenerate <3-card deck handled the same way as Hiker/Morty (no empty-deck bug since it never *takes* a card); matches.
- T163 Red Card — opponent shuffles hand into deck, draws 3; unconditional, matches the Iono/Copycat shuffle-first exception pattern.

## Not independently re-run
No probes were used — every High/Medium item above was resolved by reading the exact code path
(playability gate + effect body) rather than by inference, so confidence is VERIFIED-READ throughout.
