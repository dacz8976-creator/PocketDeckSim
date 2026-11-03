# R8 catch-up: release notes

Branch `laptop/r8-catchup-2026-10-29`, from main's merge-base `ebc97535`. R8 catches the fork up with upstream's
card code through #439 (`7aa4ef0`), carries the bot-protocol adapter, and adds the rule rows and item 11 that
Dustin's clips and decisions settled. Every commit from `ebc97535` to the tip is in the adoption list (section 10).
Nothing goes to main without Dustin's word.

## 1. What R8 brings, by commit group

- **R8-00, the bot-protocol adapter** (merge d8eae013 of the adapter tip 2639a261; the Oct 27 prototype Dustin said yes
  to (coordinator-058), accepted by coordinator-094): `deckgym simulate --players proto,...` runs an outside bot over upstream's bot protocol v1, with
  opt-in `pdl_*` keys (`engine/docs/pdl-protocol-extensions.md`).
- **R8-01 and R8-02:** test helpers and reprint-equivalence tests; Trainer dispatch by canonical printing (upstream
  #395, looked up id-first), with a census test that pins the set of 28 direct-route printings. No game change.
- **R8-03:** upstream's Clear Veil and Dragon's Blessing tests (#427, #428; the fork already behaved that way); the
  refusal tests move off C1 019 Volcanion to a test-only status override. Tests only.
- **R8-04:** #433's map entries (Venusaur, Sawsbuck, Volcanion, Amoonguss, Ceruledge), Charizard's Flame Aura and
  Raboot's Jumping Coach (stacking); a Flame Aura Knock Out inside its owner's attack is Ability damage; R8's census
  copy. New printings only.
- **R8-05:** Melmetal's Metal Scrum (#436), Dewgong's Dual Blizzard, Palkia's Spacial Rend (opponent's Stadium only,
  Starting Plains refreshed at once) and Frogadier's Sudden Duplication (#437). New printings only.
- **R8-06:** #435's Super Potion, Max Repel, Full Heal, Genome Converter Y, Eviolite and Light Ball. New printings
  only.
- **R8-07:** Sweet Honey (choose a damaged Pokémon first, then flip), Ribombee's Honey Gather and Vespiquen's Honey
  Rush; the Misty/coin-plan trace is pinned (FNV 150a2e50095a6bd0). New printings only.
- **R8-08:** #438's map entries (17 printings), Deoxys's Psycho Boost, Abandoned Station, the pinned Pokémon Checkup
  trace (FNV 1e07ca5347ea46f4), Jigglypuff's Soothing Lullaby, and Lunala's Wings of the Moone as whole distributions
  (R8-08h). New printings only.
- **R8-09:** tests of Starting Plains' +20 HP leaving play with the Stadium (Shatter, Bedrock Breaker, Spacial Rend,
  Field Blower). Tests only.
- **was_choice** (e9b10864, 28b9d4c8): Protocol adapter: `pdl_since_last` no longer carries `opponent_choices`: whether
  the opponent had more than one legal action depends on its hidden hand. `PublicEvent.was_choice` stays engine-side
  only. Test `opponent_hidden_options_do_not_reach_the_bot`. No game change.
- **The rule rows** (b20d75c0, R8-10a to R8-10e) and **item 11**: section 2.
- **The flake commit** (2da36d75, 4c1e2699; tests only): `protocol_adapter_test` runs its Python-starting tests one at
  a time under one lock, warms Python up once before any timed hello, gives `bot_failures_fall_back_and_are_counted`
  5 s instead of 1.5 s (a test value) and `first_legal_bot_finishes` a 30 s per-game limit. Production's 10,000 ms and
  engine/src unchanged; no assertion changed.
- **This commit:** docs and comments only (no code change).

## 2. The rule rows

Each row is its own commit, written test-first, with its replay prediction recorded before its tests
(`RULE_ROWS.md` in this folder). No row's prediction was replayed. The R8-10a-d predictions were searched at
28b9d4c8 over the replay check, floor check, lane replays, self-checks and every tracked deck-like file under
`decks/` and `rl/results/` (names only; never-open paths were not searched).

- **R8-10a (tests only):** Misty (A1 220, A1 267) already asks for its [W] Pokémon before any coin, as the real game
  does; a new test pins this for both printings played from the hand. Sweet Honey (C1 119, C1 152) already asked for
  its damaged Pokémon before the coins (R8-07a); R8-10a's fix adds a test that its Play flips no coin, on both
  printings. No game changes.
  - Prediction: 0 games change (the "already so" branch).
- **R8-10b (rule row, Dustin's decision of Nov 1):** Darkrai ex's Nightmare Aura (A2 110, A2 187, A2 202, A4b 245,
  A4b 378, P-A 042) now also does its 20 when an effect attaches a [D] Energy from the Energy Zone to it, not only the
  turn's Energy. Today only Sableye's Jeweled Gift (B3a 040, P-B 070) can do that. A Knock Out by it inside Jeweled
  Gift counts as an Ability Knock Out. No existing deck's games change.
  - Dustin (Nov 1, not filmed): "I don't think there are any cards that add dark energy like there are with fire so
    I'm not sure if there is any way to test the darkrai ex", then "But that doesn't mean it's not worth fixing so we
    are prepared if a new card does add that".
  - Prediction: 0 games change (no tracked deck-like file under decks/ or rl/results/ holds B3a 040 or P-B 070).
- **R8-10c (rule row):** Iris (B2b 067, B2b 081, B4b 212, B4b 378, B4b 421) now gives its extra point for every
  Haxorus printing, adding B4b 176 and B4b 348 to B2b 056, B2b 110 and P-B 045 (the check is now the exact name
  "Haxorus"). No tracked deck holds the two B4b printings; no existing deck's games change.
  - Prediction: 0 games change (deck 11, the only Iris deck in `decks/`, holds B2b 056).
- **R8-10d (rule row):** Mega Blastoise ex's Triple Bombardment (B1a 020, B1a 078, B1a 084, B4b 054, B4b 414), with
  3 extra [W] Energy attached and exactly 1 opponent's Benched Pokémon, now also does its 50 to that Pokémon
  (rules/04_actions_cards_effects.md:93: an effect does as much as it can). 0 or 2+ Benched, the [W] gate and Double
  Splash are unchanged. No existing deck's games change.
  - Prediction: 0 games change (only a computer deck and its copy hold Mega Blastoise ex, and no check plays them).
- **R8-10e (rule row; Dustin, Nov 3).** When Machop's Shatter (B2 079), Conkeldurr's Bedrock Breaker (B4 089) or
  Palkia's Spacial Rend (C1 038, C1 140) discards Starting Plains (B2 154, B4b 235, B4b 401), a Pokémon the attack's
  damage leaves in play that the lost +20 then Knocks Out still gives its point, and its owner promotes. It is no
  longer the attack's Knock Out: no Revenge or Rally Back flag, no Dark Vengeance type, Rescue Scarf, Lucky Egg,
  Innards Out, Final Scream, Offload Pass, Lucky Mittens, Electrical Cord (A3a 065) or any other "Knocked Out by
  damage from an attack" effect. Tested: the Revenge flag, Rescue Scarf, Dark Vengeance's tally, Innards Out and Lucky
  Mittens; read in the code only: Lucky Egg, Offload Pass, Final Scream and Electrical Cord. The attack's own damage
  Knock Outs (at HP + 20) are unchanged, and promotion order is unchanged (after a double Knock Out in one of these
  attacks the attacker promotes first: settled, rules/02 §7). This is Dustin's expected reading, Nov 3 (damage, then
  discard); to be confirmed in game (rules/08 T15). Field Blower is unchanged: Dustin's ruling (rules/02 §7-§8;
  Nov 3: not an attack). A double Knock Out outside an attack: section 5.
  - Dustin (Nov 3, chat) [DUSTIN, Field Blower and a replaced Stadium]: "The starting plains question is dumb. That
    clearly is not an attack. Just like using greninja snipe isn't an attack."
  - Dustin (Nov 3, chat) [expected, to be confirmed in game, the three attacks]: "Oh the one attack that takes away
    the stadium, I would need to test to make sure. That wasn't how you worded the question above. If the attack
    damage is enough to KO then yes, I assume the stadium discard occurs next and that wouldn't count if they were
    still alive prior to that step."
  - Prediction: 0 games change (searched at b20d75c0, names only, never-open paths not searched: no deck list under
    `decks/` holds Machop B2 079, Conkeldurr B4 089 or either Palkia).
- **Item 11 (rule row; adoption question 2):** every in-play type check now reads the in-play type, so Urshifu's
  Double Type (B3 051, B3 113) counts. For real cards only Snover's Ice Shard (+30) and Sealeo's Frozen Splash (+70)
  change, against an Active Urshifu whose Ability is on. Leaf Cape and the bots' pricing stay on the printed type
  (bots: a post-R8 follow-up).
  - Prediction: 0 games change (searched at 2d62a11b, names only, never-open paths not searched: no deck list under
    `decks/` holds either Urshifu; no deck list under `decks/` or `rl/results/` holds Snover A2 044 or Sealeo B4 039).

## 3. New cards: the lines to know

- **Eviolite:** consistent with Dustin's clip of Oct 29: Wobbuffet's Headbutt Bounce did the full 30 to an Alolan
  Diglett with no Tool at ~00:53; the Eviolite was attached on his next turn at ~01:02. No clip yet shows Eviolite
  during a hit.
- **Vespiquen's Honey Rush:** the bots ignore its reveal of the Sweet Honey cards, as they ignore Puppy Pile's; it is
  not recorded in their knowledge, and INFORMATION_MODEL stays v8.
- **Jigglypuff:**
  - Jigglypuff C1 051 / C1 184: RulesUnverified. Card text, not filmed: a Soothing Lullaby Sleep flips 2 coins at
    Pokémon Checkup and wakes only if both are heads. Unverified (not filmed): an ordinary Sleep on a Soothing Lullaby
    sleeper resets it to 1 coin (the reset reading, as upstream). The 2 coins are recorded only when the Sleep lands,
    so a protected or immune Pokémon that is already Asleep keeps 1 coin (upstream gives 2).
  - The observation template gains `sleep_coins_override` only on a Soothing Lullaby sleeper; the same key appears in
    ProtocolPlayer's `agent_snapshot` and `pdl_observation` on such states. Every other observation, saved state and
    ply export is byte-identical; INFORMATION_MODEL stays v8.
- **Lunala's Wings of the Moone:** Lunala with more than 256 possible final boards chooses one Energy type at a time,
  in a fixed order, lowest first (Grass, Fire, Water, Lightning, Psychic, Fighting, Darkness, Metal, Dragon,
  Colorless). In practice that needs 3 Benched Pokémon (e.g. [3,2,2] = 360); on 2 Benched Pokémon it starts at 9
  Energy over 7 or more types (17 with 3 types), and on 1 it never happens. When 3 or more types go one at a time (on
  3 Benched Pokémon: 7+ Energy over 3 types apart from [5,1,1] and [6,1,1], or 6+ over 4 or more types), the depth-3
  searchers (km3, y3, x3) stop before the Knock Out and score the board by the Energy still on Lunala: they ended the
  turn instead of using Wings of the Moone, whether or not its Knock Out won, when [P] was moved first or second (on
  3 types, always the case with Wally's [C]), and attacked when [P] was moved last. After one other action (an
  attach, an Item, or a retreat that brings a Benched Lunala in), 2 types one at a time are not priced either. One
  type passes 256 only at 22+ Energy and is not handled separately. On some of these boards the old
  one-Energy-per-action chain would have attacked.
  - Cost: With Wings of the Moone ahead one bot decision can take about a second (release test build, wall clock on
    our laptop): km3 took 0.75-1.0 s at the turn root of a live turn with an 8-Energy Lunala (252 boards in one
    choice, 12 root options), 0.93 s at the first choice with 11 Energy over 3 types (2250 boards), and 1.19 s at the
    turn root (1.17 s at the first choice) with 17 Energy over 2 types (2475 boards). One type at a time keeps each
    choice small, but a decision can still search every final board (2 types at the turn root, 3 at the first
    choice); all well inside the bots' 10 s decision timeout (`deckgym simulate --bot-timeout-ms`, default 10,000).
  - ValueFunctionPlayer (v) does not price Wings of the Moone's Knock Out, point or win when Lunala has a Benched
    Pokémon: after the 110 the top frame is the Wings of the Moone choice (one option or many), which
    `value_after_mandatory_continuation` (players/value_function_player.rs:82-110) does not resolve, and the Knock Out
    waits in `ResolveAttackRetaliation` below it (actions/apply_action_helpers.rs:899-901). With no Benched Pokémon
    nothing is offered and the Knock Out resolves with the attack. Unchanged in R8: no players/ pricing edit
    (coordinator-088 Q3).
- **Starting Plains leaving play** (Shatter, Bedrock Breaker, Spacial Rend, Field Blower): the +20 HP leaves every
  Basic in play on both sides (card text) at once, and a Pokémon whose damage then reaches its HP is Knocked Out at
  once (rules/02 §8). After Field Blower, the catch-all check after the Item scores it and the turn goes on (Dustin's
  ruling, rules/02 §7-§8). After one of the three attacks, the attack's own Knock Out check scores it, so after a
  double Knock Out the attacker promotes first (rules/02 §7); whether it is the attack's Knock Out is R8-10e's row
  (section 2). Pinned by `tests/stadiums/starting_plains_removal_test.rs`. R8-09 adds tests only. The Shatter,
  Bedrock Breaker and Field Blower refreshes predate R8; Spacial Rend's came with Palkia in R8-05b.

## 4. Protocol adapter

- was_choice: section 1.
- `chance_events` near deck-out, the seed and the hello timeout: section 5 (known limits 1-3); the protocol doc
  carries the first two.

## 5. Known limits

1. **The seed.** The protocol adapter is for trusted bots and runs. Any bot that sets pdl_observation in its hello
   receives pdl_search_seed, which can be turned back into the game seed (its own deck order, the RNG behind later
   chance). The protocol logs record the seed too. A run with an untrusted bot also needs unpredictable game seeds;
   our registered seed blocks are public. No registered result used it: the Gemini arm's bot opts in but never reads
   the seed, and the in-repo protocol bot uses it only to replay in-process search (parity).
2. **`chance_events` near deck-out.** An action whose forecast has one branch draws nothing from the RNG, and a
   shuffle of a 1-card deck draws nothing, so `chance_events` can show whether a deck search near deck-out had a
   choice (e.g. Poké Ball with 2 cards left). The Gemini arm's bot counts chance events for its re-ask (COUNTERS
   since 93fa49a8), so in that rare case its re-ask timing could depend on it: when Gemini is asked again, never what
   it sees (the same class as deviation 16). The Oct 30 chance audit (wf_d91d342a-460) did not cover this case.
3. **The hello timeout.** Under heavy CPU load a Python bot's first hello can miss the 10 s decision timeout (seen
   once in the test suite, at nice 19 with other tests running); the adapter then falls back and counts it as a bot
   failure.
4. **Soothing Lullaby's count in views (R15).** `ViewState` (the `state` of a protocol `decide`, as upstream's) and
   the Python binding's `asleep` show a Soothing Lullaby Sleep as plain Asleep, with no coin count. Bots that opt in
   to `agent_snapshot` or `pdl_observation` (as the engine's protocol_bot does), and rl/strength pilots, get the count.
5. **A forged Benched count (R14).** A forged Benched count is ignored by the Checkup (1 coin);
   `sleep_checkup_coins()` still reports the filtered count. The forged worst case is 22 coins (a hand-edited file
   with both Actives at 4 coins and 6 more Benched sleepers, all Burned).
6. **Lunala's per-type choices, cost and ValueFunctionPlayer:** section 3.
7. **A double Knock Out outside an attack.** A double Knock Out during a turn that isn't from an attack (for example,
   Starting Plains removed by Field Blower or a new Stadium) promotes in seat order, not turn player first as after an
   attack. Dustin (Nov 3) would treat it like the attack case for now, but said to leave the engine as it is unless a
   recording shows otherwise or it affects a game. Shot-list row `double-ko-no-attack`. Pokémon Checkup double Knock
   Outs: rules/05 #21, open.
8. **Flame Aura and Nightmare Aura cascades.** A later-wave Knock Out set off by a Flame Aura (Charizard C1 018,
   C1 136) or Nightmare Aura (Darkrai ex) Knock Out keeps the wave-wide "from an attack" value. That happens through
   an HP drop from Toughness Aroma, or from Jungle Totem with Regal Bloom: the engine's older cascade reading. Untested.
9. **A coin pause.** A ResolveKnockoutPoints coin pause rebuilds the list empty on re-entry. That can't happen today
   (apply_action_helpers.rs:946-963, the known-limits comment at the per-Knock-Out flag).
10. **Lost-+20 cascades.** A later wave set off by a lost-+20 Knock Out is reported, not extended (post-R8 list).
11. **Offload Pass and Nightmare Aura.** Passimian ex's Offload Pass moves Energy through the same attach hook. If a
    future card moved a [D] that way onto Darkrai ex, Nightmare Aura would fire. None does today (Offload Pass moves
    only [F]).
12. **Copy attacks.** Whether a copy-attack Pokémon can use Shatter, Bedrock Breaker or Spacial Rend was not checked
    (it would go through the same code).
13. **Vaporeon's unbounded Wash Out path** (`vaporeon_wash_out`) runs only under an environment flag. Item 11
    converted it to the in-play type check, but no test covers it.

## 6. Timing note (report only)

The slowest km3/y3/x3 decision on Lunala's heavy timing rows, at each check: was_choice 1148.7, R8-10 1102.1,
R8-10e 1244.8, item 11 1033.8, flake 1095.7 ms. The thresholds stay as they are: the 1 s rule is report-only for
every Wings of the Moone timing row (coordinator-134; set after the data), and the 3 s tripwire stays.

The adapter-only gate was also set after the data (coordinator-135): a full suite whose only failures are
`protocol_adapter_test`'s hello tests counted as passing for a commit only when the commit could not reach the
adapter, each failed test passed alone on one thread, every other gate held, and the note said so. The flake commit
and any commit that touched the adapter needed a clean full suite.

## 7. rustfmt and clippy (report only)

At 4c1e2699: rustfmt 1.8.0, report-only: 467 hunks on R8 lines (809 hunks in the 49 touched files; 660 in untouched
child modules); clippy `--all-targets`, report-only: 77 distinct messages, 6 on R8-added lines, 24 in R8-touched
files. No fmt-only commit (coordinator-125): the fork is not rustfmt-clean, and an upstream PR is formatted on its own
branch. Full suite at that check: 2,633 passed.

## 8. Housekeeping

- **The census copy.** `census.py` here is a copy of `rl/results/opening_active_census_2026-09-26/census.py` (source
  sha256 e2d82ad9…, last commit fb124297). It differs from its source only by the provenance block and the
  `VARIANT_CLASS` lines for R8-04b, R8-05a, R8-05c and R8-07b. The registered folder has 0 changes across R8.
- **`census.json` still says `"engine_map_entries": 163`;** there are 164 since R8-08a's Pawmot. It changes at the
  next census-copy rerun (opening_class.rs's doc comment says 164 since this commit).
- **The R8 plan (laptop-068, its R8_PLAN.md kept outside the repo) is stale on Frogadier:** its limitation rule, its
  predicted 11 RulesUnverified (which counted Frogadier's 2 printings) and its Frogadier shot-list row.
  Coordinator-088 overrides it: Frogadier follows the card text, with no row.

## 9. Commit-message corrections (messages are never amended)

- **d8eae013 (R8-00):** its subject calls the adapter "Dustin's Oct 27 prototype". It is the Oct 27 prototype
  Dustin said yes to (coordinator-058), accepted by coordinator-094.
- **2e92b776 (R6b):** its message reads the R6b smoke rows as a limit of that board ("none of them sees a lethal
  opposing attack at all"). The corrected reading: km, x and y never search an opposing attack on observation states;
  they see only public-reply certificates, and the stack filter matters only for B tiers.
- **654fcb5f:** its subject cites rules/04:92; the line is rules/04_actions_cards_effects.md:93.
- **722fcf3d:** its message names Iris as reachable; corrected in 60388eb6's message (no current card reaches it).
- **13286c20:** its message left out the prediction's search conditions; 2d62a11b's body repeats the whole recorded
  prediction.
- **13286c20 and 2d62a11b** repeat "No file under decks/ names Machop B2 079, Conkeldurr B4 089 or either Palkia"
  and "Conkeldurr B4 089 is only in 3 single-deck files"; **22638651 and 4c948025** say "No file under decks/ holds
  either Urshifu". The right wording is "No deck list under decks/" and "in 3 single-deck files and one reader script
  there"; RULE_ROWS.md carries it from this commit.

## 10. The adoption list, with pairings (groups in commit order; each fix listed with the commit it goes with)

Adoption question 1 is R8 as a whole, with the official-program switch and one re-pin; adoption question 2, last,
is item 11. Each group below is adopted or dropped as a whole; "alone" means it can be dropped by itself.

1. **The adapter group (R8-00), droppable as a group:** the adapter branch 2ab56c9e, 05ea1501, 5eba8503, 584b4095,
   03da4f14, 44f93f23, a8c38589, 46abe8e2, a70c7ce2, dda2fba2, 5ec46b5e, 2639a261, and the merge d8eae013. If it is
   ever offered upstream, known limit 1 must be stated, or post-R8 item 1 (b) or (c) done first.
2. **The neutral group, R8-01 to R8-09, not dropped one by one:**
   - R8-01 af11a708 · R8-02 6ac33c91 · census hardening 3ccbdfb9
   - R8-03 304f4683, 11773cd8, 25a7d910
   - R8-04 ef3c8eea, 783d3960, 722fcf3d, 60388eb6, b7ac6c8f
   - R8-05 b3ad08db, 9fd01986, cc24d9bb, 6b843f3c
   - R8-06 a5a24724, efed360a, c4431a48
   - R8-07 82e9aeae, 534320f6, 5d1e503a
   - R8-08 d21f14ce, fdcad5ac, 3b77c6dd, 8484daa8; d80815f1, f9cb9408, 2e92b776; 45e87ed2, efd960e8, cf00c6e7;
     R8-08h 743b5bc3; R8-08h fix 9521f417
   - R8-09 a0034cf9, 92234aa0, 6165ee20
3. **was_choice:** e9b10864 with 28b9d4c8 (its test fix).
4. **The rule rows, each droppable alone:**
   - b20d75c0: the R8-10a-d predictions (docs only), alone. It creates RULE_ROWS.md, which a9861326, 22638651 and
     this commit extend.
   - R8-10a Misty (tests only): 6ebe05a9 with a4200c3c; drop them together.
   - R8-10b Darkrai ex: 9904450e with 0b42dcf5.
   - R8-10c Iris: aae606e3, alone.
   - R8-10d Triple Bombardment: 654fcb5f, alone.
   - R8-10e Starting Plains: a9861326 (prediction) with 13286c20 (row) and 2d62a11b (docs fix).
   - Commit order in this group: b20d75c0, 6ebe05a9, 9904450e, aae606e3, 654fcb5f, a4200c3c, 0b42dcf5, a9861326,
     13286c20, 2d62a11b.
5. **Item 11 (adoption question 2, last):** 22638651 (prediction) with 4c948025 (row).
6. **The flake commit (tests only):** 2da36d75 with 4c1e2699 (its review fix).
7. **This commit (docs and comments only), with the docs fix commit right after it (docs only).** Dropping any group above also means removing its lines here.
8. **Root `CLAUDE.md:14`, Dustin's call (not in R8's commits):** one line adding `cargo build --release --example
   goldfish` and `cargo test --release --test goldfish_card_support_test`. Nobody edits it before his word.

## 11. Adoption-screen sentences

- Starting Plains (B2 154) is in 9 tracked deck files (brew-07, brew-08, brew-09, brew-10, Dustin's 02, 04 and 07,
  b2e's h-hoopa_absol, and the brew08 copy in `pause_games_decisions_2026-10-02/decks/`). No tracked deck list holds
  Machop B2 079, Conkeldurr B4 089, or Palkia C1 038 or C1 140, so no existing game changes. The decks Dustin plays
  now (the combos page decks 01-31, kept outside the repo) hold none of these four cards.
- The decks Dustin plays now (the combos page decks 01-31, kept outside the repo) hold no Urshifu, Snover or Sealeo.
- Electrical Cord (A3a 065) now stays off for lost-+20 Knock Outs too.
- Lunala: on some 3-type boards R8's bots end the turn where the old chain would have attacked (coordinator-134,
  option A; one board recorded, the rest inferred). No combos deck holds Lunala; Field Blower is in 07v2, 27 and 29.

## 12. After R8 (each item needs Dustin's word)

Every new finding goes on this list (the time box).

1. **The seed:** (b) send the seed only to a runner-trusted seat; (c) independent per-seat search seeds, or a keyed
   hash (a game change); unpredictable seeds for untrusted runs (publish a hash of the seed list first). Any upstream
   offer of the adapter needs (b) or (c) first.
2. **The `chance_events` fix** (a game change).
3. **A separate, longer hello timeout** (a production change). Until then, check the bot-failure count in real runs.
4. **Turn player first for in-turn non-attack double Knock Outs, only on evidence** (his Nov 3 condition).
5. **Lost-+20 cascades,** then the Flame Aura / Nightmare Aura [G] cascade on Lilligant or Serperior (known limit 8).
6. **Offload Pass moving [D] through the attach hook.**
7. **Copy-attack Pokémon using Shatter, Bedrock Breaker or Spacial Rend.**
8. **The bots' type pricing** at `players/value_functions.rs:1604` (item 11's follow-up).
9. **Lunala and search:** finish a pending attack's own choices before the static score (players/); y3's depth-0
   `opponent_ply_node` without the Unknown-hand guard (expectiminimax_player.rs:873 v :773), a hidden-information look
   first; a Carefree Steps per-type test (low priority).
10. **Aerodactyl's Primal Wingbeat loses its Tool:** a rules check first, then a fix with a test, maybe an upstream
    offer.
11. **Reveals (Honey Rush and Puppy Pile) as one INFORMATION_MODEL v9 item,** only if a tested deck holds Vespiquen
    or Puppy Pile, or he asks.
12. **`has_used_stadium` is not cleared when a new Stadium replaces the old one the same turn** (a rules question).
13. **Upstream batches, each on his OK:** Crunch's hard-coded 20 with Iris B4b 176/348; the R8-10b/c/d fixes; the
    Starting Plains +20 refresh, first shown by a test that fails on upstream 7aa4ef0; Sweet Honey order and targets,
    Super Potion Energy timing, Eviolite hit back and Fossil (drafts only). Any upstream PR must pass fmt and clippy.
14. **Coordinator-111's R8 items (Oct 30, from laptop-087), not done in R8:** (a) the lister stays without
    `with_public_pricing` (a standing rule: Penny/Portrait would leak under it); (b) UseStadium and stack follow-ups
    get a text check, or a note that none is needed; (c) make Lusamine's AttachFromDiscard ordering deterministic (no
    HashMap order; `generate_energy_combinations`, actions/apply_action.rs:2030-2039).
