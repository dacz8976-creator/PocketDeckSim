# 07 — Engine audit, 2026-09-22: what the simulator gets wrong

> **Historical audit snapshot.** This file preserves the engine findings as observed on 2026-09-22. Repairs for H1,
> H2 and M1–M6, plus a bounded set of earlier findings, are implemented in the `0.1.0-pdl.rules1` working tree.
> The repaired build is verified and active; see `09_engine_repairs_2026-09-22.md` for current scope and remaining questions.

Written 2026-09-22 (Claude). Engine checked: the `deckgym-fork-s193` working tree, i.e. the `unified1` source the project
runs (`Cargo.toml` version `0.1.0-pdl.unified1`). I rebuilt it in the cloud (the Aug 22 `deckgym-fork-s193.bundle` for
the scaffolding, with the whole working-tree `src/` copied over it) so suspected bugs could be **run**, not just read.

This extends the 2026-09-21 pass (README "Card-effect pass", 65 cards). Everything in the README's known-bug list
still stands; this file adds what was found today.

**How it was done.** Eight Sonnet reviewers split the engine: core game flow, damage/status/Checkup, the bots, every
unique attack effect in the card database (560 texts, in three groups), every Ability (156), every Trainer (163). Two
more searched the web (official FAQ sweep, grey-area rulings). Every High/Medium finding below was re-checked by me
against the code; the ones marked **RUN** were confirmed by running a small test against the built engine (the test
files are in `_research_notes/audit_2026-09-22/probes/`). Raw reports, including one-line "checked and OK" verdicts for
every card text, are in `_research_notes/audit_2026-09-22/`.

**Confidence labels:** RUN = shown by running the engine · READ = traced in the code end to end · PROBABLE · a rules
grade from this folder ([OFFICIAL], [OBSERVED], [COMMUNITY-TESTED], …) for what the real game does.

---

## 1. Short version

Coverage: 560/560 attack effects, 156/156 Abilities, 163/163 Trainers each got a verdict; ~45 core rules items checked.
Most of the engine matches the rules folder. The problems cluster in a few places:

| # | Problem | Real game | Engine | Who it hits | Conf. |
|---|---|---|---|---|---|
| H1 | **Opening hand too good** | Deal 5; if no Basic, swap one card for a Basic [COMMUNITY-TESTED, 2,000-game study] | Takes a Basic first, then 4 random cards | Every simulated game. A 4-Basic deck opens 2+ Basics **53%** of the time in the engine vs **25%** for real | READ + math |
| H2 | **Heavy Helmet blocks Poison, Burn and Ability damage** | "−20 damage from attacks" only [OFFICIAL card text + Mimikyu FAQ] | −20 to every kind of damage; a Poison tick does 0 | Dustin's deck 01 (Muk/Glimmora); any Helmet wall vs status decks | RUN |
| M1 | Checkup Knock Outs happen mid-Checkup | KO "at the end of Pokémon Checkup" [OFFICIAL] | KO the moment Poison/Burn lands, before Checkup heals | Garganacl; games ending on Checkup KOs | RUN |
| M2 | Clemont's Backpack misses the Bench | +20 to "your opponent's Pokémon" reaches Bench hits [OBSERVED ×2] | Active only | Dustin's deck 09 (Manectric/Heliolisk) | RUN |
| M3 | Glimmora / Dusknoir point-denial coin skipped | "When this Pokémon is Knocked Out, flip…" — any KO | Coin only on attack KOs; Poison/Burn/Ability KOs always score | Dustin's deck 01 | RUN (40/40 seeds scored) |
| M4 | Retaliation Abilities hard-wired | Ability loss stops Rough Skin, and an attack's effect resolves before retaliation [OFFICIAL JP FAQ] | Rough Skin family fires through Budew's Prickly Powder and Alolan Muk; two printings never fire at all | Deck 01 (Alolan Muk); Druddigon, Iron Jugulis, Dragalge ex | RUN / READ |
| M5 | Mythical Slab takes Basics | Keeps the top card if it's a **Psychic** Pokémon | Keeps it if it's a **Basic** | Psychic decks running Slab | READ |
| M6 | Two Stadiums in one turn | One Stadium play per turn [IN-GAME TEXT] | No per-turn limit | Lists with two different Stadium names | READ |
| M7 | Player choices made for the player | Retreat and untyped "discard N Energy" let the player pick [INFERRED from the UI] | Retreat keeps Grass by a fixed rule; Gouging Fire / Walking Wake discard at random | Mixed-Energy boards | READ |

Plus ~12 low-impact items (§3), one latent information leak in tooling nobody uses yet (§4), and the known list in the
README, all still present.

---

## 2. Findings in detail

### H1. The opening hand is dealt the wrong way (High — every game)
- **Real game** [COMMUNITY-TESTED]: two independent Japanese statistical studies. machapin (Qiita, 2,000 automated
  games, app v1.2.5, updated 2025-11-22) tested three models with Z-tests. With a 2-Basic deck both Basics were in the
  opening hand 62/1000 = **6.2%** of the time. Model 1 "take a Basic first, then 4 random" predicts 21.1% (rejected,
  p ≈ 10⁻³⁰). Model 2 "redeal until a Basic appears" predicts 11.8% (rejected). Model 3 "deal 5; if there's no Basic,
  swap one of them for a Basic" predicts 5.26% (fits; p = 0.18). A second deck (5 Basics) also fit Model 3 (p = 0.91)
  and rejected Model 1. Davoi (Qiita, 120 real games, 2-Basic deck) saw both Basics 8% of the time, which also rules
  out Model 1. Neither study was repeated on 1.7.x.
- **Engine**: `src/deck.rs:129-147` (`shuffle(initial_shuffle=true)`) puts one random Basic on top and shuffles
  everything else behind it. That's Model 1, the one both studies reject. (Dustin's guess was also Model 1, and
  `05_open_questions.md` #6 had it as "not worth testing". The studies settle it.)
- **Size of the error** (exact odds, 20-card decks):

| Basics in deck | P(opening hand has 2+ Basics) engine → real | Expected Basics in hand, engine → real | Dustin's decks with this count |
|---|---|---|---|
| 3 | 0.39 → 0.14 | 1.42 → 1.15 | 07 Skarmory |
| 4 | 0.53 → 0.25 | 1.63 → 1.28 | 03, 05, 06 Blaziken, 08, 09, 13, brew 05 |
| 5 | 0.65 → 0.37 | 1.84 → 1.44 | 01, 10, 11, 12, 14, 15, brew 04 |
| 6 | 0.74 → 0.48 | 2.05 → 1.63 | 02, brews 01–03a |
| 7 | 0.82 → 0.59 | 2.26 → 1.83 | 04, brew 03b |

- **Why it matters**: the engine roughly doubles how often a deck opens with a backup Basic. That hides the most
  common real loss ("one Basic, it gets KO'd early, no board") and flatters thin-Basic Stage 2 decks and anything that
  wants an early Bench (Mega Altaria's Mega Harmony counts Benched Pokémon). It also matters for "does this list set up
  by turn 2–3", which is exactly the question the sim is still trusted for (START_HERE).
- **Fix**: deal 5 at random; if none is a Basic, replace one random card in the hand with a random Basic from the deck
  and shuffle the replaced card back.
- **Confirmed in-game on the current app (Dustin's T1, added 2026-09-22):** 50 opening hands with a 2-Basic deck,
  both Basics in 3 (6%). Basic-first predicts ~10.5 (P(≤3) = 0.35%); swap-in predicts 2.6. Details:
  `_research_notes/audit_2026-09-22/T1_T10_results.md`.

### H2. Heavy Helmet reduces damage that isn't from attacks (High for Dustin's deck 01)
- **Card**: Heavy Helmet (B1 219): "If the Pokémon this card is attached to has a Retreat Cost of 3 or more, it takes
  −20 damage **from attacks** from your opponent's Pokémon." Poison/Burn, Ability and Tool damage are not "from an
  attack" [OFFICIAL, Mimikyu ex FAQ; `02` §4].
- **Engine**: `src/hooks/core.rs:682-695` `get_heavy_helmet_reduction` has no "is this from an attack" check; its
  siblings Metal Core Barrier (`:697`) and Steel Apron (`:719`) do.
- **RUN**: Blastoise (Retreat Cost 3), Poisoned, one Checkup: no Helmet 150 → 140; with Helmet 150 → **150**. The Helmet
  holder is immune to Poison ticks, shrugs off 20 of every Burn tick, and takes 20 less from Ability pings and Rocky
  Helmet.
- Also: it doesn't check that the attack came from the *opponent*, and it reads the **printed** Retreat Cost. Whether
  retreat changes (Ariados +1, Goo-zooka +1, Peculiar Plaza −2) switch the Helmet on/off is a rules question
  (`05` #19). The Sept 21 recording showed it switching with evolution only.
- **Fix**: add the same `is_from_active_attack` (and attacker-is-opponent) gate the siblings use.

### M1. Pokémon Checkup Knocks Out too early (Medium)
- **Real game** [OFFICIAL, in-app Tips]: "Any Pokémon that has no HP remaining **at the end of** Pokémon Checkup is
  Knocked Out."
- **Engine**: `src/actions/apply_action_helpers.rs:237-324` `apply_pokemon_checkup` deals Poison and Burn with
  `handle_damage`, which Knocks Out immediately (scores points, queues promotion). Garganacl's Blessed Salt heal runs
  afterwards (`:336-352`). A code comment (`:330-335`) says this is intended, but it contradicts the official wording.
- **RUN**: Poisoned Pokémon on 10 HP with Garganacl on its Bench → the engine Knocks it Out and gives the point. With
  the official timing it survives, whichever order heal and Poison go in (the order is still open, `05` #4).
- **Also matters for**: both Actives dropping to 0 in the same Checkup. The engine scores them one at a time, in seat
  order, and can end the game on the first point before the second KO is processed. The real game Knocks Out both
  together, and then the simultaneous-finish rules (`05` #2) decide.
- **Fix**: take damage with `handle_damage_only` through the whole Checkup (conditions, then Checkup Abilities), then
  one `handle_knockouts` at the end.

### M2. Clemont's Backpack's +20 never reaches the Bench (Medium, Dustin's deck 09)
- **Card**: Clemont's Backpack (B1a 066): "attacks used by your Magneton or Heliolisk do +20 damage to **your
  opponent's Pokémon**" (no "Active"). The Bench part of Electrispark got the +20 in two recordings (023151,
  trial-manectric) [OBSERVED].
- **Engine**: `src/hooks/core.rs:1007-1080` `get_increased_turn_effect_modifiers` returns 0 for any non-Active target
  (`:1015-1017`) for *every* turn-long boost. That's right for Giovanni, Blaine, Cynthia and Training Area ("…Active
  Pokémon") but wrong for the Backpack.
- **RUN**: Heliolisk Electrispark after Backpack: Bench took **10**; should be 30.
- **Fix**: special-case the Backpack effect (or tag each boost with its target scope). Don't just remove the gate.

### M3. Glimmora's and Dusknoir's "opponent gets no points" coin only flips for attack KOs (Medium, Dustin's deck 01)
- **Card**: Glimmora (B3a 045/078) Shattering Crystal and Dusknoir (B1 105) Fade into Darkness: "When this Pokémon is
  Knocked Out, flip a coin. If heads, your opponent can't get any points for it." Nothing limits it to attacks.
- **Engine**: the coin is set up only when an attack is being forecast (`apply_attack_action.rs` ~252-275
  `apply_defender_point_denial_if_needed` → `attack_outcome.rs` `split_with_point_denial`). `handle_knockouts`
  (`apply_action_helpers.rs` ~689) only reads the tag it leaves. Poison, Burn, Ability damage, Rocky Helmet and recoil
  KOs never flip.
- **RUN**: Poisoned Glimmora on 10 HP, 40 seeds: the opponent scored **40/40** (expected ≈20).
- **Fix**: flip at `handle_knockouts` time for every KO, or run the same split in the Checkup/ability paths.

### M4. Retaliation Abilities are wired by card number: they ignore Ability loss, fire too early, and miss two printings (Medium)
- **Real game** [OFFICIAL, JP Detailed Battle FAQ 57286218211225]: when Budew's **Prickly Powder** (B3 013/159, "The
  Defending Pokémon loses all Abilities…"; earlier notes called it "Itchy Pollen") hits Druddigon, **Rough Skin does
  not fire**: "effects that work after an attack" are already cut off by the attack's own effect. That's also official
  support for the observed order: attack damage → the attack's own effects → retaliation (`02` §5).
- **Engine**: `src/hooks/counterattack.rs`. `get_counterattack_damage` adds Rough Skin-type damage for a hard-coded
  list of card numbers. `should_poison_attacker` does the same for Dragalge ex. The central Ability lookup that knows
  about Ability loss (`get_in_play_ability_mechanic` → `abilities_switched_off`) is never consulted. Retaliation also
  runs inside `handle_damage_only` (`apply_action_helpers.rs:574-608`), **before** the attack's own effects
  (`attack_outcome.rs:133-167`).
- **RUN**: Budew's Prickly Powder into Druddigon: Budew 30 → **10** (should stay 30). With Alolan Muk in play ("Basic
  Pokémon in play … have no Abilities"; Druddigon is Basic), still 30 → **10**.
- **READ**: the lists miss **Iron Jugulis B3a 046** (Automated Combat never fires) and **Dragalge ex B3 231** (the
  fourth printing's Poison Point never fires). B1 160/263/281 work.
- Same family, lower stakes: Jellicent's Bouncy Body and Garganacl's Blessed Salt also use the raw lookup
  (`counterattack.rs:60`, `apply_action_helpers.rs:340`), so Prickly Powder doesn't switch them off.
- **Fix**: move these onto `AbilityMechanic` entries read through `get_in_play_ability_mechanic`, and run retaliation
  after the attack's own effects. Dustin's deck 01 plays Alolan Muk, so this touches his games directly.

### M5. Mythical Slab takes any Basic instead of a Psychic Pokémon (Medium, READ)
- Card A1a 065: "If that card is a [P] Pokémon, put it into your hand…". Engine `apply_trainer_action.rs:1862-1873`
  checks `card.is_basic()`. A Psychic Stage 1 goes to the bottom and a Colorless Basic goes to hand — wrong both ways.

### M6. No "one Stadium per turn" limit (Medium, READ)
- [IN-GAME TEXT] "You can't use any more Stadium cards this turn." `move_generation_trainer.rs:370-395`
  (`can_play_stadium`) blocks only a same-name Stadium and Snorlax's Massive Body. `has_used_stadium`
  (`state/mod.rs:323`) tracks the *Stadium's own once-per-turn use* (Mesagoza's flip etc.), not playing a card. Only
  matters for lists with two different Stadium names (knock out the opponent's Stadium, then set up your own, in one
  turn).
- **Confirmed in play (Dustin's T10 video, added 2026-09-22):** with Mesagoza played that turn, Arcade is refused with
  "You can't use any more Stadium cards this turn". The rule is also printed on every Stadium's green rules box.

### M7. Choices the engine makes for the player (Medium if the UI evidence holds; READ)
- **Retreat Energy**: `apply_action.rs:1368-1418`. "TODO: Maybe give option to user to select which energy to discard";
  it always discards non-Grass first. The in-app Tips say the discarded Energy "can be of any type", and the game opens
  a "Discard" picker [INFERRED from the UI, `04` §2]. Only matters with mixed Energy types on the retreating Pokémon.
- **Gouging Fire** (B3a 054) "Discard 2 Energy from this Pokémon" and **Walking Wake** (B3a 053) "Discard an Energy
  from this Pokémon": the engine discards at random (`random_active_energy_multisets`; `apply_attack_action.rs:3699`
  and `:3766-3793`). Cards that mean random say "random" (Piers, "Discard a random Energy…"); these don't.
- One in-game look settles all three (`08` T6).
- **Settled 2026-09-22 [DUSTIN]:** the player chooses in all three cases (retreat, and untyped "discard X Energy" attack
  costs). These are the only untyped Energy discards in the card pool. The engine should offer each distinct choice of
  Energy as a player decision. Not in the `rules1` repair batch (`09` lists it as unresolved).

---

## 3. Low-impact findings

| Item | What's wrong | Where | Conf. |
|---|---|---|---|
| Piers (B2 152) | "Discard 2 **random** Energy" takes the last two attached (comment: avoids tree growth) | `apply_trainer_action.rs` `piers_effect` | READ |
| Politoed (B3 035) Raid | "+50 if this Pokémon evolved **from Poliwhirl** this turn" also pays after Rare Candy from Poliwag | `ExtraDamageIfEvolvedThisTurn`, `apply_attack_action.rs:4937` | READ |
| Pichu Crackly Toss (A4 066/171, B2 213) | Should attach to a Benched **Basic**; engine allows any Benched Pokémon (wrong map entry; its Fire/Water twins use the right one) | `effect_mechanic_map.rs:1780-1786` | READ |
| Deck-contents blocks, two more | Mesagoza and Kid's Room can't be used unless a Pokémon / Tool is still in the deck (same class as known #4) | `stadiums.rs` `can_use_mesagoza`, `can_use_kids_room` | READ |
| Empty-deck blocks missing | Lisia, Sightseer, Team Rocket's Researcher, Traveling Merchant, May, Arven, Puppy-Loving Girl, Order Pad, Arcade's "draw until 7", Garchomp's Reckless Shearing can all be used with an empty deck (Poké Ball/Research are correctly blocked) | `move_generation_trainer.rs`, `move_generation_abilities.rs:197` | READ |
| Heal targets | Lillie, Marlon, Erika, Potion let the player pick an undamaged Pokémon when another is damaged (Pokémon Center Lady, Ilima etc. don't). Only a wasted-card risk | `apply_trainer_action.rs` | READ |
| Own-turn promotion | A Pokémon promoted after your own Active is Knocked Out during your turn counts as "moved from the Bench this turn" (Scizor, Golisopod, Crobat, Flutter Mane). The official ruling covers only promotion on the opponent's turn, which the engine handles right (flags reset each turn; evolving clears it) | `apply_action.rs:773-780` → `apply_activate` | READ; real rule open (`05` #20) |
| Vaporeon Wash Out | "As often as you like" is once per turn by default for speed; one use can move everything, so little is lost. `DECKGYM_UNBOUNDED_ENERGY_MOVES=1` restores it | `move_generation_abilities.rs:465-482` | READ |
| Deck legality | The simulation path never calls `Deck::is_valid()` (and that doesn't check 1–3 Energy types). A 0-Basic list panics. Real decklists from QR codes are legal anyway | `game.rs:138-153`, `simulate.rs`, `deck.rs:138` | READ |
| Place-into-Active | Move generation would let a hand Basic/Fossil go straight into an empty Active Spot outside setup. Probably unreachable (promotion always comes first) | `move_generation/mod.rs:176-186`, `move_generation_trainer.rs:952-968` | PROBABLE |
| Bidoof Super Fang | "Halve … remaining HP, rounded down" rounds down to a multiple of 10 | `apply_attack_action.rs:5992` | rules question |

Re-confirmed still present from the README's known list: Asleep/Paralyzed/Confused don't replace each other (#7 —
the Sept 10 fix only blocked attacking/retreating), Eevee (#5), Lum Berry vs Bad Dreams (#8), Caterpie (#9), Checkup
seat order (#12), Darkrai ex Nightmare Aura (#13). Jolteon ex's Electromagnetic Wall does **not** share #13's problem.

---

## 4. The bots: what they see and how they play

What a real player knows is in `04` §10. Findings (`_research_notes/audit_2026-09-22/bots_info.md`):

- **No hidden-information leak in simulated games** (READ). `Game::play_tick` (`game.rs:199-246`) hands every bot a
  `PlayerObservation` (`observation.rs`), which hides the opponent's hand, both decks' order and the Energy after
  "next". No real game calls the "omniscient" decision path.
- **The RL environment is clean too.** I checked `Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/src/lib.rs`: its
  features are built only from `PlayerObservation`, and it ships its own leak probes (`hidden_info_probe`,
  `hidden_move_probe`).
- **Latent leaks in tooling**: the `--data-output` exporter writes the full omniscient `State` per move (`game.rs:260`,
  `data_exporter.rs`), and the Python package `python/deckgym` exposes only the omniscient state. Harmless today;
  anyone who trains on either gets the opponent's hand as a feature.
- **k3 never looks at the opponent's reply** (`players/mod.rs:364-372`, `opponent_ply: 0`). Already finding E6 of the
  Sept 5 and Sept 10 audits; still true. It plans its own turn and scores the result with heuristics, so it walks into
  obvious KOs a human would see. The x3/y3/s3 players do search the reply but aren't the default.
- **Chance inside the search**: coin flips are enumerated with their probabilities, but draws and random targets are
  sampled once, and the bot imagines one shuffle of its own deck per decision (`search_state`). Decisions that hinge
  on what you'll draw are noisier than they need to be.
- `MctsPlayer` ("m") is a random mover in real games (`mcts_player.rs:27-40`). Don't use it as a pilot.

---

## 5. Suggested order for Astra's next engine batch

1. **Opening hand** (H1). One function; affects every game.
2. **Heavy Helmet gate** (H2). Two lines.
3. **Checkup: deal all damage, then Knock Out** (M1). Do this together with the known seat-order bug (#12) and the
   double-KO promotion order (#3); it's the same code.
4. **Retaliation onto AbilityMechanic + after the attack's own effects** (M4), plus Iron Jugulis and Dragalge ex B3 231.
5. **Glimmora/Dusknoir coin for every KO** (M3), **Clemont's Backpack Bench** (M2), **Mythical Slab** (M5),
   **Stadium per turn** (M6).
6. The known batch in the README (damage order, status trio exclusivity, Eevee, Quick-Grow/Wallace choice, Lum Berry
   order, playability rules).
7. After Dustin's one-look checks (`08` T6): player choice for retreat Energy, Gouging Fire and Walking Wake.
8. Low items in §3 when convenient.

The probe tests in `_research_notes/audit_2026-09-22/probes/` print the current (wrong) behaviour. Turned into
assertions, they become regression tests for these fixes. They drop into the engine's `tests/` folder as-is.

## 6. What this audit did not cover

- It read the code; apart from the probes it did not play full games. A per-card "does the effect happen" check
  against recorded games (replaying Astra's turn ledgers through the engine) would catch things reading can't.
  See `08` §3.
- Upstream deckgym and set B4b (out Sept 29–30) are not covered. B4b cards will need the same pass when they're added.
