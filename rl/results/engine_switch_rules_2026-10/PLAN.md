# Engine switch plan: the rules switch, Victory Star / Confusion and coin-flip damage prevention (for Dustin's decision)

Checked Sept 30 at origin/main 4690810 and the cloud branch head cae37a3 (`claude/pensive-ptolemy-spwc0b`; last engine commit c9df626). First written at 648e260, then revised after a critic's review. Nothing was built or played for this plan.

## In one paragraph

This switch changes the game rules, not the pilots. It brings in two repairs the cloud drafted: (A) Victory Star with a Confused attacker, and (B) coin-flip damage prevention, including Chase Order. It also carries kd's two one-line follow-ons. Both repairs were reviewed with no blockers. Seven small fixes (tests, one line of text, counters) and a few traces go to the cloud and Sonnet before anything is built. One order question comes first: the cloud has started N1 (kn) on the same branch, and that job changes `players/` (question 7). Then the laptop builds the candidate and replays every pilot's recorded games. No list under `decks/` holds a card either repair touches, so every table, screen and floor game should come out identical. A replay of identical games proves nothing about the changed code, so the laptop also plays about 24,000 games per build on real "carrier" lists that do hold those cards. Every changed game must reach the repaired mechanic. That is about 335,000 games before the pin: about 11 hours at 8.6 games a second, or about 7 at Sept 30's pace, in two sittings at home or overnight. Then, with your word, the laptop pins, and the floor's pre-use re-check follows (about 1 hour). Any mismatch or unexplained changed game stops everything, and it comes to you first.

## What the switch is

- **Engine:** today's official engine (main-d363ba8, whose `engine/` equals 2711df0's) plus:
  - **(A) Victory Star / Confusion:** 265ce95 (failing tests), 4d026a5 (line endings), 6415e39 (the fix), d4fbc2a (a test addition). Never take 265ce95 alone: it wrote a test file with the wrong line endings.
  - **(B) Coin-flip prevention and Chase Order:** 0785365 (the fixtures flipped, failing), d21511a (failing tests), 5942d1a (the fix), c350e70 (Chase Order's failing tests), e52a73b (Chase Order's fix), 52daee6 (S1, S2 and S4 tests), c9df626 (S1's hardening). S3's rerun and trace are in 3a31ce2, which touches `rl/results/` only.
  - **kd's follow-ons** in `persistent_defender_damage` and the engine fixes F1-F4 and F7 below, and nothing else.
- **How to take it: by commit, not by branch head.** The rules candidate is **R**, the cloud's last commit of F1-F7. Its hash goes in the cloud's README. No kn commit may touch `engine/` between c9df626 and R.
  - Since cae37a3 the cloud is building N1 (kn<N>) on this same branch, and it expects to change `engine/src/players/`. So either F1-F7 come first on the branch, or they go on a branch of their own cut from cae37a3 before kn's first engine commit (question 7). Steps 4 and 11 use R, never "the cloud head".
  - `git diff 4690810..cae37a3 -- engine/` is exactly A + B: 8 files, none in `players/` (checked at cae37a3; `engine/` is unchanged since c9df626). R adds only F1-F4's and F7's files to that.
  - Do not cherry-pick 5942d1a and e52a73b alone. That leaves the old kd fixture in `core.rs`, which fails, and it drops S1's guard against an empty nested call inheriting an outer cut.
- **Files that change:**
  - rules code: `apply_action.rs`, `apply_attack_action.rs`, `attack_outcome.rs`, `hooks/core.rs`, and `card_validation.rs` (one caveat text);
  - tests: `b4a_attack_batch2_test.rs`, `victini_victory_star_test.rs`, `hisuian_goodra_securely_sheltered_test.rs`, `meowth_carefree_steps_test.rs`, plus the new tests from F3, F4 and F7 (exact paths filled in here once the cloud has chosen their files);
  - `engine/src/players/` and `Cargo.lock` must not change.
- **kd's follow-ons ride along** (rules/09: "Fix the engine first; kd follows"). Only kd reaches this code: only KD sets `defender_modifiers` (`players/value_functions.rs:425-428`), and km3 never calls it. They change kd3's pricing only in games where one of these coin-Ability Pokémon is in play.
- **Left out:**
  - **Upstream 09e964f** (two knockout-promotion fixes). It is not a clean pick: 12 files, mostly observation and serde.
    - Fix 1: whether the fork already covers it is **unchecked** (rules/09:80). One reading of `apply_action_helpers.rs` 691-820 (knockouts resolve in waves) suggests it does, but there's no test and no second reader yet (F8).
    - Fix 2 would contradict the official JP ruling the fork follows for a lethal Knock Back: a Pokémon moved to the Bench is Knocked Out on the Bench (rules/06_sources.md:124). It would also break `rules_repair_retaliation_timing.rs:136`.
    - No list reaches either fix.
  - **PR #383.** Still open upstream. Main already carries the same fix for all four cards. Applying it anyway would undo the current-Retreat-Cost fix that your decks 01 and 03 rely on (Heavy Helmet), and it conflicts with B's `modify_damage` hunk. At the next upstream merge, keep ours.
  - **B4b card data** (9044ff6, reprint-only). It stays tied to Mega Garchomp ex's release. Once it lands, both repairs reach further (`b4b_prep_2026-09-26/B4B_REPRINT_CHECK_2026-09-29.md` lines 70, 99, 235, 322, 407):
    - Victini is reprinted as B4b 044 and 267, so repair A has real reach;
    - Meowth B2 124 is reprinted as B4b 180 and 352, and Vespiquen ex as B4b 015, so B's reach grows too.
    - The engine's gates read card effects and mechanics, not ids. But two things are keyed by id and would miss the new ones: F2's caveat arm (`card_validation.rs:96`, `B3025Victini | PB049Victini`) and `COIN_IDS` in the coin `instrument_scan.py` (also any F5 counter keyed the same way). They go on the B4b refresh's to-do, in the switch README's backlog.
- **What should change:** 0 games in every table cell, every new-17 cell, B2e, the gauntlet, the variant lists, the screen and the floor, for every pilot. Games change only where a coin-Ability Pokémon (Meowth B2 124/204, Togekiss A4 080, Bastiodon A2 114, Hisuian Goodra B3b 050) or Victini (B3 025, P-B 049) is in play.
- **Steps that come back** because this is a rules switch: the suite, the mechanic check, the refactor rule, a second reader, the carrier games, and the frozen-table check on all 45 cells.

## The integrator's review

**Repair A: correct, minimal and gated.**
- **The rule:** the Confusion coin comes first and is never offered for a reroll. On tails the attack does nothing and nothing is offered. On heads, Victory Star is offered on the attack's own coins, and a reroll gets no second Confusion check (rules/04 §9, recordings 202314 and 203025; the card text from `lib/card.py`).
- **The gate:** no new line runs unless the side has a working Victini, a Fire Active and Victory Star unused this turn (`apply_action.rs:193`). Then it also needs a Confused Active's own attack, with no CoinFlipToBlockAttack and no Will pending (`apply_attack_action.rs:117-132`). An attack with no coins of its own keeps the old path (`apply_action.rs:217-220`).
- The two halves each have probability 0.5 and sum to 1. The choice re-reads the same gate.
- The net diff applies cleanly to main, and its hunks don't overlap B's. The two repairs do meet in play, though. A Keep or Reroll into a coin-Ability defender runs `finish_attack_after_confusion_heads` and then B's cut. Nothing tests that yet (F7), and no carrier pairing puts Victini against such a defender.
- **Still to do:**
  - Five of the smoke check's 13 changed games (i = 0, 7, 17, 22, 28) had no Victory Star choice while Confused, and none has been traced yet. Game 0 had no counted Confused attack at all on the repaired engine. I checked this against the committed smoke files.
  - Victory Star with CoinFlipToBlockAttack, and with Confusion plus a pending Will, stays on the old resolution because neither has been seen in the game. These are gated, not fixed.

**Repair B: correct. The per-thread value and the Chase Order gate are safe.**
- **The rule:** Guarded Grill (−100) and Securely Sheltered (−80) now come off in rules/02 step 4, after the attacker's bonuses and Weakness. Queued attack damage (snipes, and damage to the Pokémon switched in) now flips the coin. Every test number checks out against `lib/card.py`.
- **The per-thread heads-cut value** (`attack_outcome.rs:31-60`):
  - Only `with_heads_coin_cuts` writes it, and only around synchronous calls: `handle_damage_only` and four forecast checks (`expected_damage_to`, Guts, point denial, and the attacker-knockout check for Perish Body). Only `modify_damage` reads it (`core.rs:2065-2069`), and only for attack damage to the other player. Everywhere else it reads 0.
  - It is restored on a normal return, on a nested call (since c9df626, an empty inner call clears it) and on a panic. Nothing sets panic=abort.
  - No thread pool runs inside a game (rayon only splits whole games), and the value is not part of the game state: never cloned, hashed, saved or seen by a bot. So `--threads 1` and `--threads 14` give the same games.
  - The four forecast wraps can't matter with today's cards; they are future-proofing.
- **Chase Order's gate:**
  - Without the discard, it is gated like the other helpers: the opponent's Active must have a coin Ability.
  - With the discard (`apply_attack_action.rs:311-343`), it also needs the attacker's Active to print the Chase Order mechanic. Only Vespiquen ex (B4 011, 180, 194) does, so Gyarados's Wild Swing keeps the old path, and S2 pins that.
  - **Known limits:**
    - A copied Chase Order's discard branch keeps the old path.
    - A future card that printed both attacks would misfire. The clean fix needs a field in `types.rs`.
    - Wild Swing, the own-Bench form of `also_choice_bench_damage` and six other sites still skip the coin. That is recorded for a later round, not a regression.
- **Off the gate, nothing changes:** the queued choice is the old `ApplyDamage`, field for field, with no extra random draws. `players/` and `types.rs` are untouched.
- **Side effects on the redirected path** (admitted in its README): the attack's name reaches `modify_damage`, and Guts, point denial and Perish Body run for that target.
- **Suite:** 2,011 passed, 0 failed at c9df626 (the cloud's `suite.log`). Tests came first in every round.

**Confirmed findings. Everything below is fixed before the build; none of it goes to the laptop.**

| # | Finding | Fix | Who |
|---|---|---|---|
| F1 | kd's follow-ons aren't on the branch. | Tests first: flip the last asserts of `guarded_grill_under_bounded_field_comes_off_after_weakness` (`core.rs:3221`, 60 → 70) and `a_direct_damage_snipe_on_togekiss_flips_celestial_blessing` (`:3274`, 30 → 15) to (engine, engine), and rewrite both tests' doc comments ("kd has not followed yet ... It is the laptop's", about `:3189-3194` and `:3224-3229`). Commit them failing. Then, in `persistent_defender_damage`: take the heads cut off `hit(base_damage)`'s result, drop the `engine_flips_coin` exception (about `:1657-1667`), and update the doc comment (`:1595-1599`). | cloud |
| F2 | Victini's card-status caveat (`card_validation.rs:96-98`) still says Confusion bypasses the reroll prompt. | Text only. Keep RulesUnverified, naming the two cases still unverified (CoinFlipToBlockAttack; Confusion with Will pending). No test reads the string. | cloud |
| F3 | No test checks that a Confusion tails on the new path ends the attack and the turn. Dropping the wrap at `apply_action.rs:300` would pass every test. | A test that the turn moves on after a Confusion tails, as `victini_victory_star_test.rs:180-184` already checks elsewhere, or a twin-seed comparison with Victory Star marked used. | cloud |
| F4 | The Will carve-out (`apply_attack_action.rs:131`) is untested. | A guard test: Confused, Will pending, Victini on the Bench. Expect no pause, no offer, and the old result. | cloud |
| F5 | The counters are wider than the gates. A's `vs_confused_attack` counts any Confused Fire attack with Victini in play, coins or not. `vs_confused_choice` counts only a heads that led to a choice, so it misses the tails half, where the new branch is built but nothing is chosen. B's `coin_defender_attack` fired in all 40 smoke games; the cloud README says it "can't tell changed games from unchanged ones". `coin_queued_attack_damage` counts only queued choices that were *chosen*: in S3's 4 games it read 0 where the repair had changed the offered choice on the board. | In both `instrument_scan.py` scripts, add exact counters, each with the move number of its first firing:<br>• (A) the Confusion-first branch was built: the gate held and the attack has coin paths, heads or tails;<br>• (B a) a heads finite cut was recorded for a Bastiodon or Goodra target taking more than 0 damage;<br>• (B b and Chase Order) the queued coin-path choice was *offered*;<br>• full prevention: an attack's own damage at a Meowth or Togekiss taking more than 0 (for step 2's `retain` check);<br>• the off-gate queued choices the rewritten helpers build. This is the proof that the table runs them.<br>Say how each is detected. An off-gate choice is a plain `ApplyDamage`, field for field, so the scan has to tell where it came from, for example by the mechanic of the `Attack` move before it. If it can't, it needs a watch-only hook, but a hook would put code in `engine/`, so it would ride in R and get Sonnet's read. A counter the scan can only approximate is labelled superset. **Only exact counters count as reach.** The superset counters stay, to back "all counters 0 means identical". Both scripts must still apply in either order. | cloud |
| F6 | Five Victory Star smoke games changed with no Confused choice made (i = 0, 7, 17, 22, 28). | First re-count them with F5's exact counters. A game where the Confusion-first branch was built at or before its first difference is explained on the board. Trace the rest to their first difference, as S3 did for the coin smoke (`coin_trace.rs`, `first_diff.py`). That is at least game 0, which had no counted Confused attack. | cloud |
| F7 | Nothing tests A and B together (Sonnet's second read listed these untested cases). A Keep or Reroll after a Confusion heads runs `finish_attack_after_confusion_heads` and then B's cut (`with_heads_coin_cuts`). | Tests first: a Confused Fire attacker with Victini, taking Keep and Reroll, into Bastiodon or Hisuian Goodra. The heads cut must come off after Weakness. Optional: a Confused attacker whose attack flips no coins keeps the old path (`apply_action.rs:217-220`); and the CoinFlipToBlockAttack guard test also checks that the result equals the old path's (today it checks only "no pause, no offer"). | cloud |
| F8 | Optional; it doesn't gate the build. Whether the fork covers 09e964f's fix 1 is unchecked (rules/09:80). | Port upstream's `hp_aura_promotion_test.rs` (the Lilligant case) as a scratch test under `rl/results/`, like `probe_coin_helpers.rs`, and not in `engine/`, so the switch's scope doesn't grow. A second reader of `apply_action_helpers.rs` 691-820 would also do. Until one of them does, the "unchecked" wording stays. | cloud |

- **Refuted, for the record:** "no test puts a finite cut on queued damage". `b4a_zapdos_thunderclaw_test.rs` already has one.
- **Also before the build:**
  - Sonnet gives the second read of F1 to F5 and F7 (engine rules need a second reader; its first read stopped at dc9618c, and the integrator's review covered c9df626).
  - The cloud runs the full suite at R.
  - Two readers write down the source equivalence (step 2 below): Sonnet, and an Opus subagent of the laptop session. The subagent only reads, so the laptop runs nothing.
  - The cloud extracts the carrier lists (step 8).

## The procedure, step by step

Times use 8.6 games a second on the laptop, so treat them as upper bounds: Sept 30's preparation ran 139,280 games in about 3 hours. The cloud runs at about half that speed. The laptop runs at home or overnight, not during class or travel.

**Before the build** (cloud and Sonnet; the laptop does nothing here):

| # | Step | Where | Evidence |
|---|---|---|---|
| 1 | F1 to F7 (F8 optional), tests before fixes, ending at R. Then the full suite at R, and the gates' line numbers re-cited at R (template part 1). | cloud, about half a day; Sonnet reads it | `suite.log`; the cloud README updated, naming R |
| 2 | **The refactor rule applies to B.** B rewrites lines that table games run with no cut and no coin target:<br>• `queued_attack_damage_choice` rebuilds the `ApplyDamage` literal for the six helpers and Chase Order, off the gate;<br>• `with_heads_coin_cuts` wraps `handle_damage_only` (every attack) and the four forecast checks. On the table every call takes its early return: no cuts and none in force, so it just runs `f()` (`attack_outcome.rs:46-48`);<br>• `modify_damage` reads the per-thread value, which is 0 there, and subtracts it.<br>`split_with_damage_prevention`'s new `retain` isn't reached on the table: `apply_defender_damage_prevention_if_needed` returns early unless a coin-Ability Pokémon is in the defending side's play (`apply_attack_action.rs:255-258`). For it, write the full-prevention equivalence: with `u32::MAX` the old `filter_map` dropped the entry, and `retain` drops it. Only a finite cut differs, and that is the repair. Its condition 3 comes from the carrier games (step 8): games where the full-prevention counter fired and no exact changed-mechanic counter fired must be identical.<br>Write down the source equivalence hunk by hunk, as Sept 28 did, by two independent readers: one reads the diff and one traces every caller. Repair A needs none: no new line runs without a Victini. | Sonnet, plus an Opus subagent of the laptop session (reading only) | the switch README's equivalence table |
| 3 | Extract the carrier lists (step 8) from the committed Limitless archive, then card-check them (`lib/card.py`, card status, a legality scan). No B4b card is allowed. | cloud, about 1 hour | the lists, committed before any game |

**Build** (laptop, about 45 minutes, no games):

| # | Step | Evidence |
|---|---|---|
| 4 | **Candidate:** merge R into main off-tree (merge-tree, commit-tree), never touching the working copy, as in `prepare.sh` steps 0-1. Adapt `candidate_checks`: allow exactly the files listed under "What the switch is", with F3's, F4's and F7's test paths filled in, and require `players/` and `Cargo.lock` unchanged. `engine/` must equal R's byte for byte, so the cloud's suite counts. If it doesn't, the laptop runs the suite itself (about 20 minutes). | `candidate.txt`, the tree check line |
| 5 | **Plain build:** `deckgym`, `legality_scan` and `goldfish` from one `git archive`, `cargo --locked`. Record the sha256s, extract the references blob-checked, and hash the inputs. | `PIN_STATUS.txt` |
| 6 | **Watch build:** `legality_scan` with both `instrument_scan.py` scripts (F5 version) applied, in their own folder (template part 2). | its sha256 |

**Replays** (laptop). Every replay is matched by (pairing, game number), with counts asserted, on every recorded field, as `prepare.sh` does. The "without" side is the recorded reference games named in each row, not games played by the Sept 30 programs. Most were replayed identical at the Sept 28 or Sept 30 pin (`engine_switch_2026-09-30/identity_check.txt`). k3's and kp3's new-17 files were played at 9bffbda on Sept 27's engine and haven't been replayed since (see the frozen tables below). Where a step needs an old program (7c, 8, 8b), it is the pinned `rl/engine-2026-09-30/` one.

| # | Step | Games | Time | Evidence |
|---|---|---:|---|---|
| 7 | **Identity for every pilot.** This is also the table replay: k3 and kp3 on the 28 cells, with changes listed per repair.<br>• kta3, fresh: `kta_tables_2026-09-29/ec7e1a8_fresh_kta3_{table,new17}` (14,000 + 8,500)<br>• kta3, development: `kt_tables_2026-09-28/ec7e1a8_kta3_{table,new17}` (14,000 + 8,500)<br>• km3: `km_tables_2026-09-30/1f6319e_km3_{table,new17}` (14,000 + 8,500)<br>• k3 and kp3: `kpf_2026-09-26/reading/table_*` and `new17_*` (14,000 + 8,500 each)<br>• kog3: `kog_2026-09-27/a823b6d_kog3_500` plus `kog_composition_2026-09-27/new17_kog3` (14,000 + 8,500)<br>• kq3: `kt_2026-09-26/identity/official_kq3_500` (14,000)<br>• kpr3: `kpf_2026-09-26/reading/table_kpr3`, i < 40 (1,120)<br>• kd3: `kt_2026-09-26/identity/43cef0b_kd3_40` (1,120). **Now a gate:** it checks that kd's follow-ons stay out of table games.<br>kt3, ktb3 and ktc3 carry no identity claim.<br>Both kta3 sets stay (about 1.5 hours), though both were identical on d363ba8. Each is the recorded baseline of a different kta reading, development and fresh, and a baseline that isn't replayed on the new engine can't be cited there. | 151,240 | ~4.9 h | `identity_check.txt`, one line per file, n of n |
| 7b | **Counters on the table:** the watch build plays k3 and kp3 on the 28 cells. Every repair counter must be 0 in every game, except the two off-gate counters (F5). **Both** must be above 0 somewhere, because they prove the table runs B's rewritten lines (condition 3 of the refactor rule):<br>• `offgate_helper_choice` for the helpers;<br>• `offgate_discard_then_damage` for Chase Order's discard fall-through. research/vespiquen's discard runs hundreds of times per cell (`SECOND_READ_F1_F7_opus.md`, finding 2). The watch games must equal the plain ones. | 28,000 | ~55 min | `table_counters.txt` |
| 7c | **Your decks that run B's rewritten helpers** (condition 3: "the check has to be where the change is"; the Sept 28 precedent replayed your recorded Skarmory games). None of your decks holds a coin or Victory Star card, but four hold attackers whose queued-damage helpers B rewrote: 06 (Heatmor), 02 (Absol), 08 (Gabite) and 14 (Team Rocket's Hypno). Their recorded km3 floor games on d363ba8 exist: `floor_dustin_2026-09-30/{02,06,08,14}-*_games.jsonl`, 1,920 each.<br>• Plain: replay the 4 pages with floor.py's own call (`deckgym simulate --seed-stream`, same seeds) on the new program. Every game must equal the recorded one.<br>• Watch: the floor games come from `deckgym`, not `legality_scan`, so the watch build plays the same 32 pairings through `legality_scan` (60 deals each), and so does the pinned old `legality_scan`, on the same seeds. The two must be identical. Every repair counter must be 0, and the off-gate counter above 0 on 06, 02 or 08. The seeds come from the new block below, recorded before any game. | 11,520 | ~22 min | `identity_check.txt`, `table_counters.txt` |
| 8 | **Carrier games** ("the check has to be where the change is", the Sept 28 pattern). No list under `decks/` or `rl/` holds these cards, apart from the upstream `coinflip_deck.txt` and the cloud's scratch decks. Limitless development has real archetypes that do. The committed archive holds their decklists (`limitless_skill_model_2026-09-25/raw/*_standings.json.gz`, 126 files, checked Sept 30), so no web access is needed. The cloud picks one development list each by `decklist_sources.json`'s rule (the most frequent exact list among the top 8):<br>• Garchomp Meowth (`garchomp-b4a-meowth-b2`, 20 lists in the archive): Meowth<br>• Togekiss Meowth (`togekiss-a4-meowth-b2`, 4): Togekiss A4 080 and Meowth<br>• the most-played Hisuian Goodra list (for example `dragonair-b4-hisuian-goodra-b3b`, 4): the (a) finite cut<br>• Mega Houndoom ex Victini (`mega-houndoom-ex-p-b-victini-b3`, 1, Sept 12): repair A<br>Each plays the 8 panel lists (`decks/screen/opponents/t-*.txt`), 32 pairings. The panel reaches B through t-blaziken's Heatmor, t-suicune's Chien-Pao ex, t-vespiquen's Chase Order, and t-lucario's Hitmonlee and t-sceptile's Grovyle (named in the cloud's README). It reaches A through t-weezing's Confusion Gas, the panel's only Confusion. km3 plays 500 deals and k3 250, each on the old build, the new and the watch build; watch must equal plain for both. Seeds are 23,100,000,000 + pairing × 10,000 + i, added to START_HERE's seed table before any game.<br>If a list can't be had, it falls back to a made list: `coinflip_deck.txt`, a panel list with 2 Meowth B2 124 swapped in (like Sept 28's 2-Blue list), or `fire_victini.txt`.<br>Bastiodon (Stage 2 from a fossil) and Pull In and Pound, if unreached, rest on their tests, as Beast Wall did. | 72,000 | ~2.3 h | `touched_check.txt` with reach per mechanic |
| 8b | **A non-kog3 bot through the cloud's scratch decks** (Sept 30 backlog). km3 and k3 play 40 games each on the old, new and watch builds, in 4 pairings:<br>• `fire_victini` v `psychic_confuse`<br>• `fire_heatmor` v `meowth_carefree`<br>• t-vespiquen v `meowth_carefree` (Chase Order: the pair S3 never ran)<br>• l-sharpedo v `meowth_carefree` (the Wild Swing control; its Chien-Pao ex does change)<br>They are pairings 32-35 of the same seed block. The cloud runs them first on its scratch build of R as an early warning (a few minutes). The laptop's rows must equal the cloud's. | 960 | ~2 min | same |
| 8c | **The traces** (the lookahead half of the mechanic check). The cloud's early-warning rows (8b) give the share of changed games that no exact counter explains. Multiplied by step 8's games, that is the trace load; write it here before step 8 starts. If it comes to more than about 50 hand traces, it goes to you before step 8.<br>The cloud automates what it can: `first_diff.py` plus a check of the gate's condition at the first difference. A game that check can't settle is traced by hand. The laptop sends the unexplained games' seeds in your paste block, and the cloud's answers come back as a commit. Sonnet reads every hand trace. This runs alongside steps 9 and 10. | — | depends on the load | `touched_check.txt` complete, then **PREPARE DONE** |
| 9 | **km3's coverage baselines** (reading baselines, "no exceptions"): B2e 48,000, Scizor 4,000 and the second lists 14,500, against `km_tables_2026-09-30/1f6319e_*`. | 66,500 | ~2.1 h | `identity_check.txt` |
| 10 | **Command line, goldfish, screen:**<br>• `simulate` 240 games: k3, kp3 and kog3 repeat 150/90/0, 144/96/0 and 149/91/0, and kta3 and km3 must equal `14c39f4_cli_*.txt`<br>• goldfish byte-equal to `14c39f4_goldfish*`<br>• `run_screen` under km3 on brew-06 and 06b equal to `floor_recheck_2026-09-30/run_screen.txt`. This repeats step 15's `run_screen` on purpose: before the pin, a difference stops the switch; after it, it can only hold up the floor. | ~5,000 | ~10 min | `PIN_STATUS.txt`, then **REPLAYS DONE** (PREPARE DONE waits for 8c) |

- **Totals:** about 335,000 games, about 10.8 hours at 8.6 a second (about 7 at Sept 30's pace), plus about 45 minutes of builds.
- **Two sittings:**
  - first: steps 4-7c, about 7 hours;
  - second: steps 8-10, about 4.7 hours;
  - then 8c on the cloud, with Sonnet reading.
- The passes are resumable, with anchored status lines and a lock, as in `prepare.sh`.

**The mechanic check** (for steps 8 and 8b, and for any changed game anywhere):
- Every changed game must reach its repair's mechanic.
- **On the board.** This is the coordinator's wording, Oct 1, tightening the earlier "first fires at or before". It is made exact in `tightened_rule.py`'s header (Sonnet), which the coordinator accepted.
  - A changed game is on the board only if an exact F5 counter fired at a tick at or before the first differing tick k, and either in the same turn as k or at the cause tick (the move just before k). A chosen-move counter fires at the move before k, which is in the previous turn when that move ends the turn.
  - Counters record every firing tick. A firing after k, or in an earlier turn other than the cause tick, never explains a game.
  - These are **board differences:** the offered moves differ on the same state; a forced move (n = 1) differs; the state differs after identical moves; or one game is a prefix of the other. A board difference with no counter is **UNEXPLAINED** and stops the switch.
  - A **lookahead difference** is the same state with the same offered moves and a different choice. It needs the probe (`vs_probe.rs` for A, `coin_probe.rs` and `coin_lookahead.py` for B) to find the gate inside the mover's search depth at tick k: both halves of "in lookahead" below.
  - This follows the laptop's second read of R (`SECOND_READ_F1_F7_opus.md`, finding 4): `coin_queued_offered` fired in 13 of the coin smoke's 28 unchanged games.
  - Only exact counters count as reach:
  - (A) the Confusion-first branch built;
  - (B a) a heads finite cut recorded on a Bastiodon or Goodra taking more than 0;
  - (B b and Chase Order) the queued coin-path choice offered.
  - The superset counters (`vs_confused_attack`, `coin_defender_attack`) never count as reach. They only back "all counters 0 means identical".
- **In lookahead only** counts if both halves hold:
  1. the code gate, as read in the code;
  2. a trace to the first difference showing the gate's condition within the bot's search depth.
- The cloud runs these traces (step 8c). Anything else fails, and that engine waits. A trace that needs a judgment call instead of meeting both halves goes to you.
- A game where every counter is 0 must be identical.
- **If the table's combined change is not 0,** build the intermediate engines to split it per repair: d4fbc2a is A alone, e52a73b is A plus B without S1 or kd.
- A kta3 or km3 difference in an identity, table, floor or coverage replay (steps 7, 7b, 7c, 9, 10) is never "explained by the rules change": it stops the switch. Games in steps 8 and 8b are expected to change, and they are judged only by this check.

**The frozen k3 and kp3 tables.** The rule: k3 and kp3 on all 45 cells at the new engine are the frozen table.
- **Why no new tables are expected:**
  - step 7 replays k3 and kp3 on all 45 cells against scoreboard v3's own files;
  - if every game is identical, those files already *are* the new engine's table, with the same hashes;
  - the switch README records "scoreboard v3 re-verified at the new engine, 45 cells".
  - The Sept 28 and Sept 30 pins checked only the 28 cells. The 17 new cells were last played on Sept 27's engine, so this is their first check since then.
- **What makes that argument fail:**
  - any k3 or kp3 game that differs on any cell;
  - any table counter above 0 other than the off-gate one (that would contradict the census);
  - a reference file whose sha256 doesn't match its record.
- **If it fails:**
  - The replay files become the new frozen table, the old one is kept as history with its hashes, and every pilot's baselines must be re-played on the new engine.
  - If a difference is only in the 17 new cells, first replay that pairing on `rl/engine-2026-09-30/` to learn whether it predates this switch. It still stops and goes to you.

**The pin** (after PREPARE DONE and your word; one commit; no games):

| # | Step |
|---|---|
| 11 | **Merge R into main** off-tree. `engine/` must be byte-identical to the built candidate. Nothing outside `rl/results/` and the listed engine files may come along, and nothing may be deleted. |
| 12 | **`pin.sh`, adapted:**<br>• gate 5 allows the listed rules and test files, and still refuses `players/`;<br>• drop the staged screen and floor files and the 13-file count, since the defaults stay km3;<br>• copy the programs to `rl/engine-<date>/` with `SHA256SUMS`;<br>• in the manifest, main-d363ba8 moves to history as superseded. |
| 13 | **Documents:**<br>• rules/09's three entries at lines 85-128 (the two coin-flip entries and Victory Star): mark the fixed parts fixed, which are the cut's order, the queued choices of the six helpers and Chase Order, and Victory Star after a Confusion heads. Keep one open entry listing what remains: `also_choice_bench_damage`'s own-Bench form, the six other sites, Wild Swing and a copied Chase Order's discard branch still skip the coin; Victory Star with CoinFlipToBlockAttack, and with Confusion plus a pending Will, stays gated. Word rules/04 §9's "engine mismatch" line the same way (edited only now);<br>• rules/09:78-83 and RUN5:468 on 09e964f only as question 10 is answered. Fix 1 keeps "unchecked" unless F8 or a second reader settles it;<br>• the engine README, this folder's README and PIN_STATUS, START_HERE's engine line and seed row, CLAUDE.md, RUN5;<br>• the switch README's backlog: the B4b refresh's id-keyed items (see "Left out").<br>The floor re-check's PLAN is committed with the pin, before any of its games. |
| 14 | **After the pin:** Fetch origin before Push origin. Then tell Sonnet, and the cloud through your paste block, the new engine name. The working pilot stays km3. |

**After the pin** (laptop, ~13,400 games, 30-60 minutes):

| # | Step |
|---|---|
| 15 | **The floor's pre-use re-check under km3.** brew-06 and 06b must read "fail", and the deck 14 k3 control "untrusted". `run_screen` must give the floor's wins exactly. It should equal Sept 30 exactly: 125, 262, 196, 577 and 1,098. If it fails, the floor isn't used until you have seen the pages. |

## The stop rule

Each of these stops the switch:
- any identity mismatch, in a gate or an extra;
- a changed game that fails the mechanic check;
- a changed kta3 or km3 game in any identity, table, floor or coverage replay (steps 7, 7b, 7c, 9, 10), for any reason. Games in steps 8 and 8b are expected to change and are judged only by the mechanic check;
- a table counter above 0 (other than the off-gate one);
- watch not equal to plain;
- a program whose hash changes mid-run.

A trace that needs a judgment call doesn't stop the replays, but the pin waits for your word on it.

The manifest stays untouched, nothing is pinned, and the laptop reports to you first. Script slips (like Sept 28's unquoted path) are fixed and re-run, and recorded.

## Who does what, and what not to duplicate

- **Laptop:** the candidate, the builds, steps 7-10, the pin and the floor re-check. It edits no engine code or test and runs no traces. Its Opus subagent gives one of the two equivalence readings, reading only.
- **Cloud:** F1 to F7 (F8 optional) ending at R, the suite, the carrier lists, the early-warning scratch rows and every trace. It builds no release program and plays no table, identity or carrier game. Its current job, since cae37a3, is N1: kn<N>, approved by you for two days, "probably most of a day", and it changes `engine/src/players/`. Its order against F1-F7 is question 7.
- **Sonnet:** the second read of F1-F5 and F7, the other equivalence reading, and every hand trace in 8c.

## Schedule (added Sept 30 evening, for the Oct 1-2 laptop hours)

**The constraint** (Dustin, Sept 30): the laptop is away about 7 am to 5 pm Central on Oct 1 and 2. It is closed at 7:15 am with no warning, and each morning everything must be committed and pushed, with main = origin/main, by 7:00 am. He prefers a plain laptop run straight through. Checkpoints are only for a run that can't finish in time, and the cloud is the last resort.

**Which case this is: the switch cannot start tonight.** Its first laptop step (4, the candidate) needs R, and R needs F1-F7, their second read and the carrier lists. None of that exists yet, and the cloud is on N1. So tonight the laptop runs no switch game. The work that can move forward tonight is the preparation (steps 1-3), which isn't the laptop's.
- **Routing suggestion (the coordinator's call):** F1-F7 are small code and test changes ("targeted engineering"), so Sonnet can do them tonight in its own worktree.
  - Sonnet's `cargo test` runs on the laptop, which is fine this evening.
  - The second read of F1-F7 then goes to someone other than its author: an Opus subagent of the laptop session, or the cloud.
  - The carrier lists (step 3) are a short job: the cloud if it has room beside N1, otherwise Sonnet.
  - That keeps N1 on the cloud and puts R on its own branch, cut from cae37a3, with no `players/` change (question 7).
- **Expected finish, if preparation is done by Oct 1 at 5 pm Central:**
  - **Sitting 1** (Oct 1, from about 5 pm): steps 4-7c. That is a build of about 45 minutes, then about 191,000 games: about 6.2 hours at 8.6 games a second, about 4.3 at Sept 30's pace. It ends between about 10 pm and midnight Central, is committed and pushed, and has a margin of 7 or more hours before 7:00 am.
  - **Sitting 2** (Oct 1 overnight if time allows, else Oct 2 from 5 pm): steps 8-10, about 144,000 games, 3.3 to 4.7 hours. The trace load from 8b goes to Dustin first if it tops about 50 (step 8c).
  - **Then the pin, with Dustin's word, and the floor re-check** (about 1 hour), the same night if everything passed.
  - Earliest finish: late Oct 1. Likely: the evening of Oct 2.
- **If preparation is done early tonight** (before about midnight Central), sitting 1 could start tonight. It would end about 5-7 hours later, which is too close to 7:00 am for Dustin's "with margin". So it only starts tonight if it can finish by about 5:30 am. Otherwise it waits for Oct 1 evening.
- **Checkpoints, for the fallback only:** every step ends in an anchored STATUS line and a pushed commit of its files. A pass started late stops itself at the last step boundary that finishes before 6:30 am Central, commits, pushes and leaves main = origin/main by 7:00. It resumes from the next step the next evening. Nothing mid-step is kept.

**What can move to the cloud, and what can't:**

| Step | Can move to the cloud? | Why |
|---|---|---|
| 1-3 (F1-F7, the suite at R, the carrier lists), 8b's early-warning rows, 8c's traces | yes: they are the cloud's or Sonnet's already | short jobs, or code and tests |
| 4-6 (candidate, builds) | no | the pinned programs must be the ones built and tested; a Rust program built on another machine is different bytes |
| 7-10 (the replays, counters, carrier games, coverage, CLI) | no, not as the pin's evidence | the pin's evidence has to come from the programs being pinned, the laptop's. A cloud run of these at its own build is at most an early warning, agreement on the tested games, and the laptop's run is still needed |
| 11-14 (the pin), 15 (the floor re-check) | no | they change main's official engine and use the pinned programs |

**The pin itself waits until every replay is in** (Dustin, Sept 30), whoever ran each step.

## Questions for Dustin

1. **The switch:** a conditional go, "pin if all pass", as on Sept 30, starting once F1-F7, the second read and the equivalence write-up are done. **Recommended.** "All pass" means:
   - every replay is identical and every counter reads as expected;
   - every changed carrier or scratch game is explained, either on the board by an exact counter, or in lookahead by a trace that meets both halves (step 8c).
   - A trace that needs a judgment call is not a pass. It comes to you, and the pin waits for your word on it.
2. **Scope:** A + B + kd's follow-ons + the small fixes, and leave out 09e964f, PR #383 and B4b. **Recommended.** None of the three is ready, and none reaches a list.
3. **The per-thread value for the heads cut:** keep it. **Recommended.** It is reviewed, tested and hardened by S1, and it needs no change outside the repair's own files. The cloud's README names three other routes:
   - a field on `DamageModifierContext`, which is also built in `players/`. That edit would be mechanical, and step 7's replays would re-prove it, but it breaks this switch's rule that `players/` doesn't change;
   - passing the cut through `handle_damage_only` (`apply_action_helpers.rs`);
   - a temporary stored effect on the defender (a method in `played_card.rs`).
   Switching to any of them would restart the review.
4. **Carrier lists:** have the cloud extract four real development lists from the committed Limitless archive (**recommended**), rather than made test lists only. Real lists test the repairs where ladder games would meet them. The made lists stay as the fallback.
5. **km3's coverage baselines:** replay them at this switch (**recommended**, about 2 hours, as a gate), or at the next candidate's build. A difference there would be a km3 difference, so it's better found before the pin.
6. **kd3's identity as a gate** instead of an extra: **recommended**, 1,120 games, about 2 minutes.
7. **The order against N1 (kn).** The cloud started N1 at cae37a3 on your two-day approval. It says "probably most of a day", and it changes `engine/src/players/`. F1-F7 take about half a day.
   - **Recommended:** F1-F7 first, either first on the branch or on a branch of their own cut from cae37a3, so R carries no `players/` change. Then N1 resumes.
   - kn's identity and tables are then played on whichever engine is official when they run, with baselines from that same engine ("every reading uses baselines from the same engine"). If this switch pins first, kn's games are on the rules engine, and km3's baselines there are the step 7 and 9 replays.
8. **When the laptop runs.** Two sittings, about 7 and 4.7 hours at 8.6 games a second (less at Sept 30's pace). On Oct 1-2 the laptop is away from about 7 am to 5 pm Central, so each sitting runs in the evening and overnight, and it must commit and push by 7:00 am.
   - **Recommended:** confirm the laptop may run them overnight on those nights, since the overnight authority is confirmed night by night.
   - The passes resume where they stopped, so a sitting that runs short loses nothing.
9. **If a Victory Star game fails the mechanic check** (in F6 or step 8).
   - **Recommended:** hold A, and ship B + kd if B passes.
   - B's commits sit on top of A, so there is no B-only build today. It needs a revert commit of A: the fix 6415e39 and its tests 265ce95, 4d026a5 and d4fbc2a. Their hunks don't overlap B's.
   - Then it needs a new build and the replays again on it, which is two more sittings.
   - The alternative is to hold both.
10. **Upstream 09e964f's wording.** rules/09:78 and RUN5:468 both say to take its two fixes "at the next upstream merge". Step 13 would change that, and that is a recorded decision.
    - **Recommended:** record fix 2 as not taken, with the reason: it contradicts the JP ruling the fork follows (rules/06_sources.md:124) and would break `rules_repair_retaliation_timing.rs:136`.
    - Keep fix 1 "unchecked" until F8 or a second reader settles it.
    - Without your word, both lines stay as they are.
