# R8 catch-up: release notes

Branch `laptop/r8-catchup-2026-10-29`, from main's merge-base `ebc97535`. R8 catches the fork up with upstream's
card code through #439 (`7aa4ef0`), carries the bot-protocol adapter, and adds the rule rows and item 11 that
Dustin's clips and decisions settled. Every commit from `ebc97535` to S8 (543dad00) is in the adoption list (section 10), apart from the merge of main (c76ad922, Nov 4: main's two newer files, START_HERE.md and a weekly-review file; no engine or deck change). After S8 come the build record and the adoption commit (section 13).
Dustin's word came on Nov 4 ("Adopt all three"): the official programs switch to main-543dad0 (section 13).

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
- **The docs commits** (e5e4e58b with 63657e0a, and the second docs commit): docs and comments only (no code change).

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
  - Jigglypuff C1 051 / C1 184: RulesUnverified. Filmed (Oct 29, Codex's review of Dustin's clips): a Soothing
    Lullaby Sleep flipped 2 coins at Pokémon Checkup twice (`…11-59-31`, 03:02 and 03:18); an ordinary Sleep flipped 1
    (`…11-53-36`). By the card text, it wakes only if both are heads. Not filmed: the coin count after an ordinary
    Sleep replaces it (Dustin saw the icon change from the plus mark to plain Sleep). The engine resets it to 1 coin
    (the reset reading, as upstream). The 2 coins are recorded only when the Sleep lands,
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
14. **kx3 is slow on R8's honey cards (time only).** In Lane N's kx3 smoke (kx3 on K8 v km3, 72 games), 9 kx3
    decisions took over 30 s, all with deck a01-grass-honey v t-altaria in turns 2-4 (Place Cutiefly, Professor's
    Research, Evolve Ribombee and Vespiquen, Play Sweet Honey, UseStadium); the slowest took 102,823.2 ms, under the
    smoke's 120 s stop (`~/pincand_work/RR_R8_48dec4f5/smoke/a_kx3/SLOW.tsv`). Over all 769 kx3 decisions: mean 4,561,
    median 3,124, p95 13,014 ms. No game result depends on it; it costs only time (coordinator-150 §3).

## 6. Timing note (report only)

The slowest km3/y3/x3 decision on Lunala's heavy timing rows, at each check: was_choice 1148.7, R8-10 1102.1,
R8-10e 1244.8, item 11 1033.8, flake 1095.7, docs 1342.0 ms; 0 decisions over 3 s in every check. The docs commits
change no code, so 1095.7 → 1342.0 ms is laptop load. The thresholds stay as they are: the 1 s rule is report-only
for every Wings of the Moone timing row (coordinator-134; set after the data), and the 3 s tripwire stays.

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
  next census-copy rerun (opening_class.rs's doc comment says 164 since e5e4e58b).
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
  there"; RULE_ROWS.md carries it from e5e4e58b.

## 10. The adoption list, with pairings (groups in commit order; each fix listed with the commit it goes with)

Adoption question 1 is R8 as a whole, with the official-program switch and one re-pin; adoption question 2, last,
is item 11. Each group below is adopted or dropped as a whole; "alone" means it can be dropped by itself.

The pairing rule (coordinator-147 §2.3): a fix goes with what it fixes (e9b10864 with 28b9d4c8; 2da36d75 with
4c1e2699; e5e4e58b with 63657e0a and the second docs commit). The three prediction commits (b20d75c0, a9861326,
22638651) stay in every case: each is the record made before its row's test, like a pre-registration. Dropping a row
removes only the row's own commits and its release-notes lines, and adds "dropped at adoption, <date>" beside its
prediction in RULE_ROWS.md.

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
4. **The three prediction commits (docs only), kept in every case:** b20d75c0 (the R8-10a-d predictions; it creates
   RULE_ROWS.md, which a9861326, 22638651 and e5e4e58b extend), a9861326 (R8-10e's prediction) and 22638651
   (item 11's prediction).
5. **The rule rows, each droppable alone (its prediction stays, group 4):**
   - R8-10a Misty (tests only): 6ebe05a9 with a4200c3c; drop them together.
   - R8-10b Darkrai ex: 9904450e with 0b42dcf5.
   - R8-10c Iris: aae606e3, alone.
   - R8-10d Triple Bombardment: 654fcb5f, alone.
   - R8-10e Starting Plains: 13286c20 (row) with 2d62a11b (docs fix).
   - Commit order of these rows with their predictions: b20d75c0, 6ebe05a9, 9904450e, aae606e3, 654fcb5f, a4200c3c,
     0b42dcf5, a9861326, 13286c20, 2d62a11b.
6. **Item 11 (adoption question 2, last):** 4c948025 (row; its prediction stays, group 4).
7. **The flake commit (tests only):** 2da36d75 with 4c1e2699 (its review fix).
8. **The docs group (docs and comments only):** e5e4e58b with 63657e0a (its docs fix, docs only) and the second docs
   commit (docs only: Lullaby filmed, its rules/ entry, this pairing rule, the timing note). Dropping any group above
   also means removing its lines here.
   The second docs commit is 55f67837, with its fix cdadc04f (docs only; coordinator-148 §1). After his yes (Nov 4,
   "Adopt all three"): one more docs commit (known limit 14, section 12 item 15).
9. **Root `CLAUDE.md:14`, Dustin's call (not in R8's commits):** one line adding `cargo build --release --example
   goldfish` and `cargo test --release --test goldfish_card_support_test`. His word came on Nov 4 (the third yes in "Adopt all three"); the adoption commit adds it as a new bullet after line 15 (coordinator-155 §3; section 13).

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
15. **Jigglypuff's limitation text (a text fix, in the first engine commit after R8):** `card_validation.rs:117-118`,
    the Jigglypuff C1 051 / C1 184 limitation that card_status prints, still says "Card text, not filmed" for the
    2-coin Soothing Lullaby Checkup. Section 3 and rules/03_status_checkup_timing.md:73 say the 2 coins were filmed
    (Codex's review of his clips). Not changed in R8: it would move the tested engine tree (coordinator-150 §4).

## 13. The adoption: the official programs switch to main-543dad0 (Nov 4)

In plain words:
- The official programs are now R8's: upstream's card code through #439, the protocol adapter (used only when a run asks for it), the rule rows R8-10a to R8-10e and item 11.
- All 260 C1, SP1 and P-C printings now play: 256 Complete and 4 RulesUnverified (C1 015 Ribombee, C1 051 Jigglypuff, C1 135, C1 184). The official programs refuse no real printing any more. The card-support refusal stays in the code and still stops a deck with a card the engine cannot play, but no printing in the card list is such a card now.
- So the screen, the floor and the brew pages (goldfish) play every deck made of printings in the card list on main-543dad0.
- The slow report stays on the old engine (main-affe56e) until its own check on the new engine passes, and its pages say so. Until then, a slow report of a deck that holds one of the 55 printings main-affe56e could not play registers and then stops with its pinned program's card-support message (exit 2), while the official programs play that deck.
- This is a catch-up with upstream's card code and our rule rows, not a strength change. On the replayed decks the new programs gave main-affe56e's results. Nothing here measures how well the bots play the new cards, and kx3 is slow on the honey cards (section 5, known limit 14).

Dustin's words, verbatim, with their sources:
- **The adoption.** Nov 4, at about 14:35Z, answering "Do you adopt R8 as the page lays out?" on the approval page "R8 Approval Sheet", relayed by the coordinator in coordinator-153: "Adopt all three". The three: (1) adopt R8 with nothing dropped (section 10), including the START_HERE and CLAUDE.md pin lines named on the page; (2) yes to item 11 (4c948025); (3) yes to the CLAUDE.md:14 goldfish line (section 10 item 9).
- **The two-step pin.** His Oct 21 words, via coordinator-072: "Move the slow-report program only after its replay check passes. Until then, its reports must clearly identify the old engine."
- **Baselines as on Oct 21.** His Oct 21 words, via coordinator-072: "Leave historical scoreboards and mixed-opponent comparisons alone. Revisit them only if a future decision relies on them." The old rows are listed below ("Tied to the old engine"); their files are left as they are, and nothing is recomputed.

### What the adoption activates
- **The three programs** in `rl/engine-2026-11-04/` (`deckgym` a5c71c00… blob, sha256 75090673c20939a0aee431eb293dde0d2a988194da0b8429604a7570dc150310; `legality_scan` 2c6df06583ec366735785eb234ed2bbd13dd6a1161036cfecfc80afd4af3fea4; `goldfish` 814d72b5ab7c705738a731ed96d5b5b62059494cece0cd82442e60ad77d7a5ed): S8's tested bytes, the same git blobs as `r8_release/programs_final/`, mode 100755, never rebuilt.
- **The current-engine selector.** `project_manifest.json`'s `available_release` names them, and main-affe56e (`rl/engine-2026-10-29/`) moves to `historical_releases`; its folder stays as history. `current_engine.py`, `decks/screen/floor.py` and `decks/screen/run_screen.py` read the manifest, so the screen and the floor switch with it. `make_predictions.py`'s `CURRENT_ENGINE` moves with it: floor pages made on `rl/engine-2026-11-04/deckgym` count as current, and no slow report does until the slow report's re-pin.
- **The pin lines.** START_HERE's engine line and CLAUDE.md's engine paragraph name main-543dad0, and CLAUDE.md gains the goldfish card-support bullet (section 10 item 9).
- **The slow-report program: not moved by this commit.** The pinned program stays kx3 on main-affe56e's engine (`/home/dacz8976/kx_r4/strength`, sha256 23d8a9b5…; built from `laptop/kx3-on-r6-2026-10-29` e3ddc014, engine tree cd970db6). Its pages already name that engine ("kx3 (d513e37b's files, on main-affe56e)"), and `make_predictions.py` counts no slow report as current. The re-pin's program is built and checked: kx3's six files on 48dec4f5 (K8 b5f15351, branch `laptop/kx3-on-r8-2026-11-04` on origin, not main; engine tree f33d2c49baf4), `/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength` (sha256 d4d4e43a…; harness c4f7da21…; jobs 2), both self-checks equal to the pin's texts (below). Its kx3 replay check on R8 comes next; the re-pin follows only if it passes. **Until the re-pin**, a slow report of a deck that holds one of the 55 printings main-affe56e could not play registers and then stops with the pinned program's card-support message (exit 2), while the official programs play that deck (`rl/strength/README.md`, "Unsupported cards").
- **The harness source does not move.** It is c4f7da21… at affe56e8 and at S8 (the pin's hash), so, unlike at R6, no pin test turns red on main and the cloud `--program` route is not held back by this commit (the rl/strength modules give the same results before and after it: "Checks of the adoption commit" below).

### Release identity
- Built from S8, `543dad0007a345128ec95e9c2698699c8b5493ce` (2026-11-04, 14:46-14:56 UTC, 638 s): the tip of `laptop/r8-catchup-2026-10-29` after the merge of main (c76ad922) and the docs commit. Engine tree 014b4371a3b8. main's `engine/` after the adoption is that tree, byte for byte: no exception.
- Built in WSL with `cargo build --release --locked` plus `--example legality_scan` and `--example goldfish`, in the clean worktree `/home/dacz8976/lane_r8_w` at S8, with a fresh target directory (`/home/dacz8976/lane_r8_target`), CARGO_BUILD_JOBS 2, nice 19 (`lane/lane_r8.sh`). The five programs built from S8 (deckgym, legality_scan, goldfish, card_status, card_enum_generator) have Lane N's sha256 (Lane N: 48dec4f5, the same engine tree), so Lane N's checks are cited (coordinator-151, Q2 (A)).
- The engine reads the same 14 `DECKGYM_*` switches as main-affe56e, none set by default. R8's only new environment variable, `TEST_CARD_SUPPORT_MISSING_ATTACK`, is read only in a build with the test-utils feature.
- The build record is `r8_release/` at 933f2790 (one parent, S8; it changes only that folder), the commit this one sits on. Its `programs_final/` holds the same bytes; the adoption copies those blobs and never rebuilds.
- **Activation checks** (after the merge, in the repository root, on Linux):
  1. `cd rl/engine-2026-11-04 && sha256sum -c SHA256SUMS`: three OK lines.
  2. `git ls-tree HEAD rl/engine-2026-11-04/`: deckgym a5c71c00…, legality_scan d62354d1…, goldfish 71bcb5ef…, each 100755.
  3. `python3 current_engine.py`: prints this repository's `rl/engine-2026-11-04/deckgym` (it refuses a file whose hash is not the manifest's).
  4. The manifest's three sha256 equal `SHA256SUMS`.
  5. `git rev-parse HEAD:engine` prints 014b4371a3b809273c01a1809a058de5980cdfd1, S8's engine tree.

### The switch's checks (`r8_release/` and Lane N)
| Check | Result |
|---|---|
| Build: deckgym, legality_scan, goldfish | OK in 638 s (2026-11-04, 14:46-14:56 UTC), fresh target directory |
| sha256 against Lane N's programs (48dec4f5, the same engine tree) | equal, so Lane N's rows below are cited (coordinator-151, Q2 (A)) |
| gencmp (`card_ids.rs`, `database.rs`), the official build's own lane on S8 | SAME, SAME |
| card_status | all 4,577 cards = 4,565 Complete + 12 RulesUnverified; C1, SP1 and P-C: 260 = 256 Complete + 4 RulesUnverified; older cards neither Complete nor RulesUnverified: 0 (STATUS_CHECK OK) |
| Suite (Lane N) | 2,633 passed, 0 failed, 0 ignored |
| goldfish steps (Lane N) | no test variable in the plain programs; the plain card-support test: 1 passed |
| 18 identity replays (Lane N) | 15 SAME against the 08a9b3a references and the 3 known Growl-rule rows (new17_k3 8 of 8,500 deals, dev_km3_new17 7 of 8,500, 8_new_km3 1 of 16,000); all 18 equal to R6's S ("v S: SAME"); every rules page with no RULE finding; 156,520 games or deals |
| The same 18 replays on the official build's lane (unplanned) | equal to Lane N's |
| Floor re-check, 12 pieces, on S8's deckgym | 24,960 games (11 deck pieces 21,120, run_screen 3,840): games and coverage files byte-equal to R6's pages on S (floor2S), each page equal apart from the engine path only |
| R8's goldfish on the 11 floor decks | coverage byte-equal |
| kx3's rebuild on R8 (K8 b5f15351) | `/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength`, sha256 d4d4e43a…, harness c4f7da21…, jobs 2 |
| Self-checks | km3 81b572198c04d5d1 (on strength_L, R8's km3 build) and kx3 31d638dbc818b0fa (on strength_K8, 5,377 s): equal to the pin's texts |
| `rl/strength` Python suite | 1,438 tests OK |

### Tied to the old engine: not re-run, nothing recomputed
1. **The slow report and kx3's recorded games**, until the re-pin (above). The reports so far stay main-affe56e's, or older.
2. **Scoreboard v3's frozen cells and thresholds, kta3's status, km3's thresholds, the mixed kt/kta clause-(d) tables and RUN5's development real error:** records of their old engines, as on Oct 21 and at R6.
3. **The ladder predictions** (`rl/results/ladder_validation/predictions/`), never overwritten.
4. **Run 3, K21 and the exam rows:** v7, frozen, not pooled with v8 rows.
5. **R6's floor re-check pages (floor2S) and its replays:** records beside the new ones above, never replacements.
6. **The deck journal's "current engine" flags** mean "current when added".

What carries over unchanged: every replayed row that came out equal.

### Checks of the adoption commit (a scratch worktree, before main moved; no engine run)
Run before main moved, on e6de0f98, with `r8_release/tools/adoption/verify_r8.sh draft <scratch worktree> e6de0f98 <baseline>`; the baseline is the same checks on the R8 tip before this commit, the build record 933f2790 (`verify_r8.sh baseline`). Python tests only, no engine run:
- The commit's shape: one parent, the build record, whose one parent is S8; 18 paths (PASS (18 paths; want the 18 of adopt_r8.py)); START_HERE.md PASS (1 hunk(s)), CLAUDE.md PASS (1 hunk(s)) (coordinator-155 section 3).
- The five activation checks: PASS (rl/engine-2026-11-04: 3 OK lines); PASS (deckgym a5c71c00 legality_scan d62354d1 goldfish 71bcb5ef each 100755, the programs_final blobs); PASS (rc=0, prints <WT>/rl/engine-2026-11-04/deckgym); PASS (manifest v SHA256SUMS: True); PASS (HEAD:engine 014b4371a3b8, S's 014b4371a3b8). available main-543dad0 543dad00 rl/engine-2026-11-04; history tail main-4d48844 main-affe56e | superseded: True.
- `make_predictions.py --selftest`: rc=0 | FAIL lines 0 | ok lines 136 | SELF-TEST PASSED (0 failed). `read_ladder.py --selftest`: rc=0 | FAIL lines 0 | SELF-TEST PASSED (0 failed).
- `test_journal`: rc=1 | Ran 61 | FAILED (failures=1) | FAIL: test_the_first_fill_holds_the_proposals_and_withdrawn_lists (test_journal.PartB.test_the_first_fill_holds_the_proposals_and_withdrawn_lists). The same failure, unchanged, at the baseline 933f2790 and on main 08bd9602 (`verify_r8.sh baseline` on main, the same day): it predates R8 and is not this commit's; reported to the coordinator.
- `floor_recheck_rules2_2026-10/test_runners`: rc=0 | Ran 55 | OK | no FAIL/ERROR. `test_calibration_safety`: rc=0 | Ran 168 | OK | no FAIL/ERROR. `test_run_screen_weights`: rc=0 | Ran 21 | OK | no FAIL/ERROR. `test_floor_pricing_pilot`: rc=0 | Ran 5 | OK | no FAIL/ERROR. `read_km.py --selftest`: rc=0 | selftest ok: route from integers; tau and dMSE boundary logic at both edges (a printed +0.0 lower bound read from score.py's unrounded one, K7); M1/M2 compared with the exact T (a rate displayed as T but below it fails), the kta3 guard at exactly T, 'cannot pass', never offered; T parsed only as an exact fraction; the amendment's numbers found in the text; the gating table by route and label (M lines only in the fallback, τ̂ on the ordinary route only in the fallback, (c) only on the reserve route); holding lines first; per-label failure names; the skip report; the five-field match with deck files . `test_km_thresholds`: rc=0 |   ok    P3 read_km.py still writes `out[int(0.025 * reps)], out[int(0.975 * reps)]` twice (2 found) and it picks what score.pct picks at 4,000 and 20,000 reps (True) ALL CASES GIVE THEIR KNOWN ANSWER .
- `rl/strength`'s modules, KX_RUNS_DIR and STRENGTH_PROGRAM unset: test_slow_report rc=0 | Ran 492 | OK | no FAIL/ERROR; test_slow_report_existing rc=0 | Ran 42 | OK | no FAIL/ERROR; test_slow_report_page rc=0 | Ran 201 | OK | no FAIL/ERROR; test_slow_report_paired rc=0 | Ran 69 | OK | no FAIL/ERROR; test_slow_report_process rc=0 | Ran 115 | OK | no FAIL/ERROR; test_slow_report_registration rc=0 | Ran 244 | OK | no FAIL/ERROR; test_slow_report_runloop rc=0 | Ran 78 | OK | no FAIL/ERROR; test_split_collect rc=0 | Ran 54 | OK | no FAIL/ERROR; test_strength_card_support rc=0 | Ran 4 | OK (skipped=4) | no FAIL/ERROR; test_strength_prereg_use rc=0 | Ran 121 | OK | no FAIL/ERROR; test_strength_report rc=0 | Ran 18 | OK | no FAIL/ERROR.
- Against the baseline: 20 checks equal; the one expected difference was the draft's own placeholder for this text; nothing else differed (verdict: as expected).
- Placeholders: none in the final (the draft held only the one for this text).

### Left as is on purpose
- `engine/UPSTREAM.md` stays as built: it is part of S8's tree.
- Jigglypuff's limitation text in `card_validation.rs` (section 12 item 15) waits for the first engine commit after R8: changing it now would move the tested engine tree.
- `census.json`'s `"engine_map_entries": 163` (section 8) waits for the next census-copy rerun.
- `rl/engine-2026-10-29/` (main-affe56e) stays in the repository as history.
- kx3's rebuild on R8 (K8) stays on its branch and on the laptop until the slow report's re-pin.
