# Rules switch 2: reader one's second reads of preconditions (a), (b), (c) and (e)

*Reader one: the laptop session's read-only Opus subagent, Oct 9. The code was read at P = `31616338` (engine tree
`639d2f80`) against the official engine main-8626a35. The tools were read at the branch tip `31380294` of
`origin/claude/coin-prevention-round2`; it changes nothing under `engine/`, and `engine/src/players/` is the same at
8626a35 and P. The laptop's runners were read at main `0ed40102`. Read-only: no cargo, builds, tests or games. Nothing
the cloud wrote about its own work was taken on trust. Every finding I flagged was checked again by an adversarial pass
that tried to refute it. Only what survived is listed as a finding; the rest is listed as withdrawn, with the reason.*

## In plain words

Before the laptop replays about 336,000 games on the new engine, four checking tools the cloud built have to be right.
I re-read each one.
- **(a) The probe.** When a game changes only because the bots saw a new rule while looking ahead, the probe shows
  where. **It does what PLAN asks.** One wording fix is needed: the probe looks at the real game, not at the bots'
  partial view. The real safety net is the revert check, which is already required. One test that PLAN still lists
  as open was never run.
- **(b) The sorting scripts.** They decide why a changed game changed. **They do what PLAN asks.**
- **(c) The tallies.** They count each time a new rule acts during a game. **They work for every game this switch will
  play.** There is one crash in the tally code, but only on a board that no deck in this switch can reach: two Energy
  types on one Pokémon facing two Ariados. If it ever happened, the sitting would stop; it can't let a bad game through.
- **(e) The off switches.** There is one per new rule, used to prove a rule caused a change. **They work. No defect.**

**Blockers in the code: none.**

**Bookkeeping to finish before the sittings:**
1. **Before sitting 1:** PLAN's probe row still lists one test as open, the "gate_R > 0" match. It was never run. The
   coordinator either has it run (cloud) or waives it in writing. PLAN §4 says the laptop plays nothing until every
   precondition is met.
2. **Before sitting 2:** `tools_8c.tsv` still names older copies of the 8c tools.
   - Its revert score dump is a version that doesn't compile.
   - Its classifier is the copy from before the review's fixes.
   - Two classifier copies are missing.
   - It should name the copies I read (listed in §5). The file is already marked "TO FINALIZE".
3. *Outside my four reads, noticed in passing:* the suite log the cloud committed doesn't name P. The runner's
   precondition-(g) check would refuse it. The start fails safe, but someone needs a log that names P.
4. *From the equivalence reading* (`EQUIVALENCE_reader1_opus.md`): the coordinator decides whether the cloud fixes the
   rare Kangaskhan-copy crash now (recommended) or it is recorded in `rules/09`. It is not a blocker.

**Before step 8c** (after sitting 2):
- a small driver that runs the revert check for every look-ahead game and records the result (the pin already refuses
  without it);
- the probe's wording fix.

**Later or optional:** listed in §5.

## 1. The verdicts against PLAN's definitions

| Precondition | PLAN's definition (PLAN.md row, plus section 0) | Verdict | Surviving findings |
|---|---|---|---|
| (a) coin_probe v2 | :257. Plies counted as the bots count them; the round-2 conditions reported with their ply; built on P; the 600,000-node retry kept; a second read | **met in substance.** One PLAN test is still open (the gate_R > 0 match): run it or waive it. | A1 (documentation, minor) |
| (b) the classifier copies | :258. The length branch of `first_difference`; `counter_hits` reading existing rows; a length difference = a board difference; round 2's counter names (keyed); synthetic tests | **met** | none (notes only) |
| (c) the counters | :259, with section 0's P2 counters (:87). Exact and off-gate counters for every new path; proven on constructed boards; a second read of blob `306f1f69` (switch2.env:22-24) | **met for this switch's rows** | C-1 (latent crash, low); C-2 (some probe rows not re-run at P, low) |
| (e) the revert switches | :261. A switch emptying `forecast_apply_damage`'s coin targets; one per gate; each alone and all together; each shown to give the old scores where its gate doesn't act | **met. No defect.** | none (notes only) |

## 2. (a) coin_probe v2 with round 2's conditions

**What I read.**
- `rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs`: at the tip (byte-identical to 056158c3, blob `31857834`),
  and at 77aa8e3d and 57c65860. Also its self-test outputs (`coin_probe_v2_selftest.txt`, `_before_r2.txt`,
  `_before_return.txt`), `p2_probe_checks_output_r2.txt`, `early_warning_8b_ticks_r2.{sh,txt}`, and README §"Round 2's
  conditions".
- The `R2_FNS` it includes from `instrument_scan.py` (`r2_tick` :290-560).
- The bots at P: `players/expectiminimax_player.rs`, `players/mod.rs`, `players/value_functions.rs`, `observation.rs`.

### Against PLAN (a)'s definition

| PLAN (a) | The bots (`expectiminimax_player.rs` at P) | The probe (`coin_probe_v2.rs`) | Met? |
|---|---|---|---|
| the root move is always ply 1 | every move gets `max_depth - 1` (:319-330; `score_candidates` :266-277) | `step(a, plies + 1)` at the root (:524-532); a queued frame at the root costs 1 (:482) | yes |
| game over is free | static (:608-611) | returns, no leaf (:465) | yes |
| forced turn end is free; crosses a forced EndTurn into the mover's next turn | exactly one EndTurn, ResolveKnockoutPoints, ResolveAttackRetaliation, ResolvePokemonCheckup, FinishPokemonCheckup or ResolveEndTurnEvolution on top, or an empty stack with `end_turn_pending`; same depth, before the depth check (:633-657) | `forced_continuation` (:403-415) at the same `plies`, before the depth check (:534-540) | yes |
| pure frames are free | a pending attack-coin, Misty or trainer-coin choice, or a top frame of only `ApplyQueuedAttackDamage` / `ChooseRandomEvolutionTarget`; same depth, also at depth 0 (:659-717) | `free_frame` (:418-423), same `plies` (:541-549) | yes |
| complete promotion frames are free | a complete Promote frame offering the whole Bench (:719-771; `is_current_promotion_frame` :204-241) | `promotion_frame` (:427-433), without the whole-Bench test | yes in play (the engine always offers the whole Bench) |
| stops when the opponent acts | `current_player != myself` -> static (:773-798) | `state.current_player != actor` -> leaf (:550-557) | yes |
| every other offered move costs a ply, the opponent's stack choices included | the mover's moves at depth-1 (:941-969); the opponent's forced choices in the mover's turn at depth-1 (:970-1021) | `step(a, plies + 1)` for every move (:559-565); 3 plies -> leaf (:550) | yes |
| an unpriced move is a leaf | `hidden_continuation_reason` (:441-454) or a forecast error (:457-473); the tree is `observation.search_state(rng)` (:397) | only a forecast error (:336); the true state (:980-992) | **partly** (A1) |
| report the ply at which round 2's conditions are priced | — | PLAIN, OWN, GUTS, WILL, VS, TRAP (+ `trapleaf`), PERISH, and RETURN for P2. Each is read from the watch build's own `r2_tick` counters, included from the same text, at the ply its move is charged (chosen) or would be chosen (offered) | yes |
| build it on P | — | the self-test was built at 31616338: 46 checks, 0 failures (`coin_probe_v2_selftest.txt`:60-191; README:302) | yes |
| keep the 600,000-node retry | — | `--node-limit`; the retry runs when nothing at all was found (B4) | yes |
| tests: the gate_R > 0 match (1,126) | — | **never run.** PLAN.md:257 still lists it as open. A `git grep gate_R` at the tip (`round2_readiness_2026-10-02`, `engine_switch_rules2_2026-10`, `coin_prevention_round2_2026-10-01`) and at main finds only PLAN.md:257. | **open**: run or waive in writing |

**Mapping the gates to the probe's kinds** (`apply_action_helpers.rs`:692-745):

| Gate | Probe kind |
|---|---|
| G1 | PLAIN |
| G2 | QUEUED (by card id) |
| G3 | OWN, and PLAIN on the own side |
| G4 | WILL |
| G5 | VS |
| G6 | TRAP and `trapleaf` |
| G7 | GUTS |
| G8 | PERISH |
| P2 | RETURN |
| G9-G11 | none: Luxury Coin and the Fossils are outside PLAN (a), as the probe says at :67-69 |

The prefilters only save time. `chosen_fact` (:262-271) and `offered_read` (:311-315) are supersets of the counters' own
tests. `trapleaf` is right for k3 and km3: the leaf's only Retreat Cost term is the mover's own
`-my.active_retreat_cost` (`value_functions.rs`:782, :707).

**The new boards are real tests.**
- At 77aa8e3d (tests first), exactly the 19 positives fail (`_before_r2.txt`: 46 checks, 19 failures).
- At 056158c3 all 46 pass. The only self-test change is a label, "K" to "X", so no expected value was fitted to the
  code.
- The 13 negatives sit on each gate's edge. Examples: Confused without Will, a block coin without Will, one Ariados, the
  opponent's Ursaluna, and Chase Order into a 400-HP Cursola.
- Depth below the root is tested: plain = 2, perish = 3, will = 2 and vs = 2.

The other recorded outputs agree:
- `p2_probe_checks_output_r2.txt`: with P2 off, the self-test fails exactly H, I, J and M.
- `early_warning_8b_ticks_r2.txt`: the 21 ticks and 4 controls give the same RESULT and RESULT_P2 as
  `classify_output.txt`.
- RESULT_R2 is "none" everywhere. No real game has yet exercised a round-2 kind.

### Surviving finding

**A1 (minor; documentation only): the probe searches the referee's true state and never asks the bots'
"unpriced move" rule.**
- *The code.* The probe walks the true `State` (`coin_probe_v2.rs`:992), and only a forecast error ends a path (:336).
  It never calls `hidden_continuation_reason` (`expectiminimax_player.rs`:441-454; `observation.rs`:56-57, :478-484).
- *Where it matters.* For the blind k3 (`players/mod.rs`:542-550, no public pricing), a move k3 scores as a static leaf
  is still expanded and counted (:509-513). A valid case:
  - k3's Active is Confused and Will is in hand;
  - the attack reads "Flip a coin. If heads, discard a random card from your opponent's hand."
  - The probe reports WILL = 2, INSIDE THE SEARCH, but k3 scores that attack as a leaf.
  - The check found that Copycat, which both pairing-37 decks hold, works the same way.
- *Narrower than I first wrote.* My first example was Professor's Research, then Will. It can't happen, because both are
  Supporters, and one Supporter per turn (`apply_action_helpers.rs`:1184-1186; `move_generation_trainer.rs`:62;
  `hooks/core.rs`:658-677).
  - km3 is a PublicPricingPlayer (`players/mod.rs`:682-700). It lifts the opponent-hand-or-deck text rule for all 62
    audited texts (`observation.rs`:479; the whole-inventory test `public_pricing_player.rs`:310-336 is ok in
    `suite_default.txt`:268).
  - The own-deck part stays inside the probe's stated meaning. `search_state` shuffles the unrevealed deck uniformly
    (`observation.rs`:144-158), so the true order is one of the bot's possible worlds ("has positive probability",
    `coin_probe_v2.rs`:90-91, :116-117).
- *No recorded verdict is affected.* All 25 recorded probes read RESULT_R2 none. The revert check replays each decision
  through `game.play_tick`, which calls the bot's own decision function on its own observation (`score_dump_round2.rs`;
  `game.rs`:224-232). So it tests the bots' real search. It restored the official choice at 21 of 21 ticks.
- *The fix.*
  - Say in the readiness README §3, or in the 8c procedure, that the probe searches the referee's state without
    `hidden_continuation_reason`. An INSIDE found through a move the bot leaves unpriced is not evidence by itself, and
    the per-game revert check stays mandatory for every look-ahead verdict (it is: `pin_rules.sh`:470).
  - Replace the Research/Will example with a valid one.
  - Editing `coin_probe_v2.rs`'s own header would change the blob `tools_8c.tsv` pins, so prefer the README.

### Notes

- **A2.** There is no gates-off control for the round-2 boards. P2 had one: `DECKGYM_FLAT_RETURN_DAMAGE=1` fails
  exactly H, I, J and M. Run at P with `DECKGYM_ROUND2_OFF=1`, the self-test should fail exactly the 19 round-2 positives
  plus H, I, J and M, and each gate off alone should fail its own boards. Cheap (cloud), not required.
- **A4.** The probe's speed on two-Ariados boards is unmeasured. With two Ariados in play, `trap_fact` holds at almost
  every node, and `r2_tick` runs a move generation and two forecasts per node. A dry run on counter_smoke's deck-12 games
  (11 of 40 had two Ariados in play) would size step 8c's time for step 9's Trap Territory games. Recommended before
  8c.
- **A5.** In Trap Territory pairings the probe half is weak. TRAP fires at ply 1 at almost any decision (Retreat on
  one side, Grass Knot on the other). Nearly every look-ahead game there will read both halves, so the G6 revert check is
  the real test.
- **A6.** What the probe skips is all in the safe direction: it gives UNEXPLAINED or JUDGMENT, never a false pass.
  - A mixed-Energy ChooseRetreatEnergy against two Ariados is never asked (:282, :310).
  - QUEUED-by-card-id misses Kangaskhan's second punch when the coin Pokémon is Benched (EQUIVALENCE N1).
  - A queued frame isn't expanded (:506).
  - `promotion_frame` lacks the whole-Bench test.
- **N1.** The probe header's line numbers for the bots' file are off. At P: forced 633-657; free 659-717; promotion
  719-771; hidden-hand guard 773-798; opponent's forced choices 970-1021; root 306-335. Documentation only.

## 3. (b) The classifier copies

**What I read.**
- `rl/results/engine_switch_rules2_2026-10/` at the tip, all unchanged since 8106a900:
  - `tightened_rule.py` (blob `9817f8bc`), `test_tightened_rule.py` (`6a5e7924`), `classify_8c.py` (`a487a34f`) and
    `coin_lookahead.py` (`25122f62`);
  - the six `tests_*.log` files, `classify_check_8b/`, and `early_warning_8b/classify_8b.py` with `classify_output.txt`.
- `coin_prevention_round2_2026-10-01/revert_switches/`.

### Against PLAN (b)'s definition

| PLAN (b) | The code | Met? |
|---|---|---|
| `first_difference`'s length branch: k is the first tick only the longer game has; the cause is k-1 | `tightened_rule.py`:81-103. With no differing tick in the common length m, kind "length", k = m, cause = m-1, plus `longer`. Equal lengths (only the last move's effect differs) get k = m, cause m-1, a sensible reading of a case PLAN doesn't name. | yes |
| `counter_hits` reads the turn from the rows that exist | :106-123. It uses `rows[k]` if it exists, else the longer game's row at k, else `rows[-1]`. A tick at or before k in k's turn, or at the cause tick, explains; ticks past the rows are skipped. classify_8c passes only the new game's turns (:202). | yes |
| a length difference is a board difference | `classify_8c.py`:204-212, `coin_lookahead.py`:101-120. A length, movegen or state difference with no reach counter is UNEXPLAINED, never sent to the probe; only a look-ahead difference goes to the probe. | yes |
| round 2's counter names, keyed counters included | `round2_reach` (:136-141): R2_COUNTERS plus R2_KEYED, less `offgate_*` and `trap_territory_two_in_play`. That is 16 names: the 15 EXACT plus `attack_return_weakness`. `coin_queued_by_attack` is filtered to ROUND2_QUEUED (:147-154, :166-178), and a keyed counter given as a flat list is refused (:173-174). (PLAN named `validate_v2.py` for these names; the copies carry them instead, and `tools_8c.tsv` rightly leaves `validate_v2.py` out.) | yes |
| synthetic tests (no counter, an earlier turn, the new engine shorter) | tests first: `tests_before_tightened_rule.log` 3 FAIL + 9 ERROR, then 16 of 16; `_before_classifiers` 23 ERROR, then 39 of 39; `_before_review_fixes` 4 ERROR, then 43 of 43 | yes |

**ROUND2_QUEUED checked against P's database.** The 7 site mechanics map one to one to the 8 titles:
- DiscardOwnBenchedTypeForDamage is Wild Swing;
- CoinFlipAlsoChoiceBenchDamage is Wellspring Dance;
- SelfDiscardEnergyAndChoiceBenchDamage is Tornado Shot;
- ConditionalBenchDamage is Double Splash and Triple Bombardment;
- ShuffleOpponentToolsIntoDeckBeforeDamage is Mischievous Ring;
- DiscardToolsFromHandForDamage is Litter;
- MegaKangaskhanExDoublePunchingFamily is Double-Punching Family.

No other mechanic uses those titles (`c_titles.py`).

**25 of 25.** I compared `classify_check_8b/classify_8c_out/verdicts.tsv` with `early_warning_8b/classify_output.txt`
game by game: kind, k, cause, the explaining counters, every probe field and the verdict are equal in all 25. It is a
regression check of the shared paths. None of the 25 is a length difference, a round-2 kind, a JUDGMENT or a strict
divergence, so the new paths rest on the 43 synthetic tests.

### Notes

- **B3.** A probe title cut to one character can be read as a later-round attack. `short()` cuts each action at 87
  characters (:153-156), so an attack costing four Energy keeps one title character. `_title` (`tightened_rule.py`:
  215-221) maps that character to the first ROUND2_QUEUED name it begins ("D", "T", "W", "L", "M"). The revert check is
  the backstop. Fix: read the title from the uncut action, or require at least 4 characters.
- **B4.**
  - The 600,000-node retry runs only when nothing at all was found. A truncated probe that found only `trapleaf`, a kind
    only at ply 4, or a first-round QUEUED stays JUDGMENT or strict-UNEXPLAINED: more judgment calls, never wrong
    passes.
  - The controls come from the first changed pairing per bot.
  - CONDITION 3 looks at the whole game.

## 4. (c) The counters

**What I read.**
- `rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py`, blob `306f1f69` (sha256 `7cc1914e`). It is the same
  blob at b7e3bc00, P and the tip, and the one `switch2.env`:22-24 pins and says this read must cover.
  - Its history: da086209 (round 2's counters), cf3cffee (the smoke), b7e3bc00 (P2's two counters).
  - P2's off-switch, P3, Bounded Field x2 and the revert switches don't touch it.
- `engine/examples/legality_scan.rs`, byte-identical at 8626a35, 140c0be2 and P. So every anchor the script needs still
  occurs once.
- The probe `counter_probe_readiness.rs` and its outputs; the smokes; the 8b and revert outputs; the laptop's
  `counters.tsv`.

### Against PLAN (c)'s definition

- **Exact counters for every new path.** Each counter strips one printed Ability (or the attacker's printed Weakness)
  and lets the engine's own forecast decide (`instrument_scan.py`:173-181, :262-270). Abilities come only from the
  printed card (`effect_ability_mechanic_map.rs`:878-917), so that is the right test.

| Counter (scan line) | What P does | Fires exactly when it acts? |
|---|---|---|
| `coin_queued_by_attack` {title} (:306-312) | `coin_gated_choice`, `site_coin_gated_choice`, `chosen_damage_choice` and the second punch build `ApplyQueuedAttackDamage` | yes for the 8 round-2 titles. Its other keys build the same choice on both engines, so both classifiers filter it (`tightened_rule.py`:62, :147-154). It fires when the punch is offered (D2). |
| `coin_plain_damage_by_attack` / `_chosen` (:327-368) | `forecast_apply_damage` (aa:790-862) | yes: the branch count rises exactly when an effective coin Ability takes damage |
| `perish_plain_hit_offered` / `_chosen` | aa:864-950 (G8) | yes |
| `coin_own_side_split` (:372-389) | own-side chain (aaa:277-305, G3) | yes at Attack and ApplyQueuedAttackDamage; misses at Victory Star's Keep/Reroll (D3) |
| `guts_own_side_split` | aaa:481-520 (G7) | as above (D3) |
| `will_confused_attack` (:393-423) | the Will step (aaa:209-218, G4); Victory Star staging with Will | yes |
| `will_block_coin_attack` | `block_coin_heads_by_will` (aaa:226-231) | yes |
| `vs_block_coin_built` | `victory_star_stages_gate_coins` (G5) | yes (non-stack) |
| `vs_block_coin_choice_offered` (:424-428) | Keep/Reroll offered with a block coin | a superset edge for a copied attack (D5) |
| `trap_territory_offer_changed` / `_outcome_changed` (:432-459) | each Ariados adds its amount (G6) | yes when the payment is decided at the Retreat tick; a mixed-Energy payment frame: see C-1; a Benched Ariados' stripped Ability: D6 |
| `luxury_coin_opp_stadium` (:463-473) | tcp:45-49 (G9) | yes |
| `fossil_item_lock` (:481-496) | the lock (G10) | yes on P, but by conditions, not by an engine comparison (D4) |
| `attack_return_weakness` (:505-558) | `handle_attack_retaliation` with `attack_return_weakness_extra` (P2), Bounded Field x2 included | yes: taking the Weakness away gives `WeaknessApplication::None`, so the +20 and the x2 both vanish |

- **Off-gate counters for each rewritten site.** Each fires where its rewritten line ran and gave the old answer:
  `offgate_by_attack` (:313-319), `offgate_plain_attack_damage` (:365-367), `offgate_guts_opponent_split`,
  `offgate_confused_attack`, `offgate_block_coin_attack`, `offgate_vs_ungated_built`, `offgate_trap_territory_one`,
  `offgate_luxury_coin_offered`, `offgate_fossil_offered` and `offgate_return_by_source`.
  - The callers of the rewritten constructor are all in R2_SITES (:135-140).
- **Supersets stay out of reach.** `round2_reach` (`tightened_rule.py`:136-141) and `counters.tsv` agree. The supersets
  never explain a game: `trap_territory_two_in_play`, `coin_defender_attack`, `coin_queued_attack_damage` and
  `vs_confused_attack`. `counters.tsv`'s 27 round-2 rows equal the script's 23 R2_COUNTERS plus 4 R2_KEYED.
- **Proven.**
  - The probe passes 78 of 78 on P2's engine. Its run without P2 fails exactly the 11 P2 rows.
  - At P, coin_probe v2's self-test runs `r2_tick`'s text on 32 boards: Will, Victory Star, Trap Territory, own side,
    Guts, plain hit, Perish Body and RETURN. That is 46 checks with 0 failures.
  - The smokes: 120/120 (da086209), 200/200 (P2), and 8b's watch 240/240 (140c0be). The counters change no play.
- **With a gate off, the exact counters go silent, by code.** Each compares the engine's own forecasts, and the revert
  tests fix those forecasts with each gate off on the same boards. For example, `b4a_attack_batch2_test.rs`:682: with G4
  off, Will stays pending in every branch and nothing pauses, so `will_confused_attack` can't fire. The exception is
  `fossil_item_lock` (D4).

**P3 (G11) has no counter, and that is in scope.** P3 entered by question 2a, which adds it to step 4's file list and to
precondition (f), not (c) (PLAN.md:360). The "Fossil lock" in row (c) is G10, which has both counters. `counters.tsv`:
6-7 already records "G11 ... has no counter". A changed P3 game would read UNEXPLAINED and stop the switch, and no
replayed list holds a Fossil.

**Step 7b** (the table: 28 cells, k3 and kp3).
- The table lists hold no coin Ability, Ariados, Will, block coin, Guts, Cursola, Gholdengo, Fossil, return attack or
  site attacker (`c_table_cards.py`).
- So "every round-2 exact counter = 0" can't fire falsely there. Its value is showing that `r2_tick` neither fires
  falsely nor crashes over 28,000 games.
- The three required off-gate counters are reachable on the table, and together with identity they show three rewritten
  areas running and giving the old answer:
  - Team Rocket's Weezing ex confuses;
  - Vespiquen ex's Chase Order runs `chosen_damage_choice`;
  - ordinary snipes and queued hits run the rest.

### Surviving findings

**C-1 (low; latent): the watch build panics at a paid retreat with mixed Energy against two Ariados.**
- *The code.* `r2_tick` runs on every tick with no guard (`instrument_scan.py`:715-740). For a chosen
  `ChooseRetreatEnergy` while two or more Ariados face the Active, `sig(&old)` (:455-456) replays the chosen payment on
  the board with one Ariados.
  - That path is deterministic (aa:497, :1026-1027).
  - `finish_paid_retreat`'s `assert!(legal.iter().any(|choice| choice == energies), ...)` (aa:1657) fails, because the
    payment is one Energy too big for the lower cost.
  - `legality_scan` has no `catch_unwind` (rayon `into_par_iter`, :681), so the run aborts.
  - At the Retreat tick itself, no counter fires either. The board and the offers are equal, and `r2_board`
    (:236-248) leaves the stack out.
  - The cloud knows this: `coin_probe_v2.rs`:84-87 and README:289-290; the probe skips the case (:282).
- *When it can happen.* Only with a `ChooseRetreatEnergy` frame.
  - `apply_retreat` builds one only when `retreat_payment_choices` returns two or more payments (aa:1633-1644).
  - That function groups the attached Energy by type (`energy_discard_choices.rs`:40-69). A Pokémon carrying a single
    Energy type has one payment, made inside Retreat (aa:1639-1640), which the stripped board pays at its lower cost
    without trouble.
- *Reach this switch: none.* The watch rows that reach two Ariados are:
  - 8b's deck 12 v t-weezing and v t-lucario (PLAN.md:279);
  - step 9's pairings 32-39 and 80-87: h-whimsicott and deck 12 against the 8 panel lists (PLAN.md:283, files from
    `1f6319e_b2e_km3.jsonl`).
  - All ten lists have a single Energy line: Fighting, Psychic, Grass, Grass, Water, Darkness, Darkness and Fire for the
    panel, and Grass for deck 12 and h-whimsicott.
  - The Energy zone draws only the deck's own types (`state/mod.rs`:935). The cards that attach Energy add the zone's own
    type (Flame Patch, Roar in Unison, Ice Maker), and nothing gives the opponent Energy.
  - The recorded smoke agrees: deck 12 v t-weezing and v t-lucario logged two Ariados on 257 ticks in 11 games, and the
    watch build finished 120 of 120 games (`counter_smoke/compare_output.txt`:1, :5, :13).
- *Severity.* One check rated it should-fix before sitting 2's watch rows. Two checks traced every list in those rows and
  found no way to reach it. I side with the reach analysis.
  - If it did happen, the watch game would panic, "watch = plain" would fail, and the sitting would stop. It fails safe.
  - Fixing it now would move the pinned coin script: `sitting1.sh`:1737-1742 halts unless the script is `306f1f69` and
    equals P's blob. So that would mean a new P.
  - **Leave it for after this switch.** Fix it before any watch row puts a list that can hold two Energy types on one
    Pokémon against deck 12 or h-whimsicott: skip `sig(&old)` when the chosen move is ChooseRetreatEnergy (the cause
    tick's board compare already covers the payment), and add a mixed-Energy board to the probe.

**C-2 (low): three of the readiness probe's row groups were not exercised again at P.**
- The 78/78 ran on P2's engine (b7e3bc00's script at 5543a4ba). At P, only the self-test's 32 boards ran `r2_tick`.
- The seven-site, Luxury Coin and Fossil-lock rows were not re-run after the revert switches added `&& _on()` to their
  gates. By code the switches change nothing with defaults (the EQUIVALENCE reading). The games stay byte-equal with
  defaults (`revert_switches/run_output.txt`).
- Re-running `counter_probe_readiness` at P (cloud; it needs a build) would close it. Nice to have, not required.

### Notes

- **D2.** `coin_queued_by_attack[Double-Punching Family]` fires when the punch is offered. When the first punch Knocks
  Out the defender, the first difference is "state" at the promotion tick, with the cause at the Attack tick, so the
  game would read UNEXPLAINED (a stop). No list holds Kangaskhan. A companion counter at the tick that leaves a new queued
  frame would close it (P2's frame logic, :527-542, is the model).
- **D3.** On a Victory Star attack, the own-side coin and Guts splits happen at Keep/Reroll, which
  `coin_own_side_split` and `guts_own_side_split` don't look at (:372). Round 1's `coin_cut_recorded` has the same limit.
  No replayed list has Victini with such an attacker.
- **D4.** `fossil_item_lock` fires on conditions (the builder offers the Fossil, NoItemCards is in force, NoTrainerCards
  isn't), not on an engine comparison. With `DECKGYM_FOSSIL_UNDER_ITEM_LOCK=1` it would still fire. Adding
  `&& !actions.iter().any(<Place of that Fossil>)` would make it engine-checked.
- **D5.** `vs_block_coin_choice_offered` can fire on both engines for a copied attack under a block coin. Requiring that
  the Attack which built the pause was not `is_stack` closes it. No list has it.
- **D6.** Stripping a Benched Ariados' Ability also removes "has an Ability" for Team and for Honchkrow's Evil
  Admonition (aaa:4506-4517), so the Trap Territory counters could fire where Trap Territory changes nothing. No panel
  list, nor deck 12 or h-whimsicott, holds Honchkrow.
- **Kangaskhan's promotion crash** (found while checking D2) is EQUIVALENCE F1.

## 5. (e) The revert switches

**What I read.**
- The code at P against 8626a358.
- The switch commit's diff (ade21150..31616338) and the tests-first diff (b0dc4844..ade21150).
- The cloud's recorded outputs at the tip (`rl/results/coin_prevention_round2_2026-10-01/revert_switches/`).

### Against PLAN (e)'s definition

| PLAN (e) | The switch (`apply_action_helpers.rs` at P) | Met? |
|---|---|---|
| a switch that empties `forecast_apply_damage`'s coin targets | G1 `DECKGYM_NO_PLAIN_HIT_COIN`; `with_plain_hit_coin` (:691-695) | yes |
| the seven sites | G2 `DECKGYM_PLAIN_QUEUED_SITES` (:696-701); it also covers the pending-hit arm in `state/mod.rs` | yes |
| the own side | G3 `DECKGYM_NO_OWN_SIDE_COIN` (:702-706) | yes |
| Will | G4 `DECKGYM_WILL_SKIPS_GATE_COINS` (:707-711), both Will cases | yes |
| the Victory Star gate | G5 `DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN` (:712-717) | yes |
| Trap Territory | G6 `DECKGYM_TRAP_TERRITORY_ONCE` (:718-721) | yes |
| Guts | G7 `DECKGYM_NO_OWN_SIDE_GUTS` (:722-726) | yes |
| Perish Body | G8 `DECKGYM_NO_PERISH_ON_QUEUED_HIT` (:727-732) | yes |
| (added) Luxury Coin, the Fossil lock, P3 | G9 (:733-737), G10 (:738-741), G11 `DECKGYM_FOSSIL_NOT_ITEM` (:742-746) | yes |
| (added) P2 | `DECKGYM_FLAT_RETURN_DAMAGE`, `with_return_weakness` (:620-645). One switch removes both the +20 and Bounded Field's x2, since both sit inside one gated call (:783; `hooks/core.rs`:1537) | yes |
| each switch run alone and all together | test level: each alone through `with_*` (the revert tests), all through `DECKGYM_ROUND2_OFF=1` (the suite). Game level: each alone and all, on 8b's 480 deals. Score level: G1+G2 and all at the 17 Wild Swing ticks, P2 and all at the 4 RETURN ticks, each alone at the 4 controls. | yes (F2, F3 below) |
| each first shown to give the old engine's scores where its gate doesn't act | game level: G3-G11, each alone, leave all 480 8b deals as the head's. Score level: every switch at the 4 controls. Code: each `<gate>_on()` is an extra conjunct with no side effects. | yes (thin at score level, F3) |

**Each switch, off, takes exactly the old path.** I mapped every behaviour change in
`git diff 8626a358 31616338 -- engine/src` (17 files) to a gate. The details are in `EQUIVALENCE_reader1_opus.md` §1 and
its appendix. In short:
- **G1:** coin targets empty -> the old forecast, provided G8 is also off for Perish Body.
- **G2:** the plain `ApplyDamage` at every site, and no queued-hit arm.
- **G3:** the opponent only.
- **G4 and G5:** the old Victory Star and block-coin paths, each alone restoring its own case.
- **G6:** the old loop verbatim.
- **G7:** opponent slots only.
- **G8:** no Perish branch.
- **G9:** always covered.
- **G10:** the old lock.
- **G11:** `==`.
- **P2:** `weakness_extra = 0`.

With every switch off, only the Victini and Gholdengo caveat text differs from the official engine.

**The 51 tests that fail with round 2 off.** I re-derived this from git objects and the two committed suite logs
(`r2_read/e_tests_check.py`, `r2_read/e/tests_check_out.txt`):
- The same 101 binaries and the same 2,100 named tests in both runs: 2,100 ok, against 2,049 ok and 51 FAILED.
- The 51 equal the 51 rows of `suite_off_failures_new_since_8626a358.tsv`.
- None of the 51 names exists anywhere under `engine/` at 8626a358. This is a cross-file search; the cloud's own script
  looked only in the same file.
- Removed 5, added 89 (51 failing plus 38 passing with round 2 off). The only changed bodies under the same name are the
  2 `attack_outcome.rs` unit tests (signature only). So every old test that still exists passes with every gate off.
- The 5 deleted pins are back as passing revert tests, verbatim or through `blocked_moltres` and
  `confused_moltres_after_will` (`b4a_attack_batch2_test.rs`:424, :531), which build the same boards.

**The revert check, 21 of 21, and the controls, 4 of 4.**
- `score_dump_round2.rs` plays the head to tick k and makes that one decision inside `with_off(gates, ||
  game.play_tick())`. Main's unchanged `score_dump.rs` (b77652d6), built into 8626a358, replays the same game, with the
  same seed formula, seat rule and players.
- It compares the chosen action and every candidate's score, by position and action text, within 1e-9.
- It isn't vacuous: 2 to 12 candidates at each tick, and the head's choice differs from the official one at all 21. If
  the per-thread setting failed to reach the search, the check would fail; it can't falsely pass that way.
- The 21 ticks are exactly the 8b classifier's look-ahead verdicts, and the 4 controls its negative controls.
- Why G2 alone reverts the 17 look-ahead deals and G1 alone none: the bots price a frame of only
  `ApplyQueuedAttackDamage` for free, even at depth 0 (`expectiminimax_player.rs`:659-717). A plain `ApplyDamage` frame
  costs a ply.

### Surviving findings

None.

### Notes

- **F2.** At the 17 Wild Swing ticks, the score dumps used G1+G2 together and all off, not each alone. For attribution in
  8c, add `g2` and `g1` to that loop (`run_revert_gates.sh`:168-173): 34 more dumps.
- **F3.** The score-level controls are four early ticks in one pairing with no coin Pokémon in play
  (`run_revert_gates.sh`:171). The game level is the stronger evidence of inertness. A cheap addition: G3-G11 alone at
  the 21 ticks, each expected to equal the head's dump.
- **F4.** The `deckgym simulate` check (240 games of altaria v blaziken) can't show anything about the gates, since no
  gate acts there. The worker-thread property is shown by the 8b all-off rows (`legality_scan`'s rayon pool) and by the
  code. The README overstates it.
- **F5.** The caveat text isn't gated (EQUIVALENCE N7). This matches step 7c.
- **F6.** G2 alone isn't the old damage on the board. With G1 on, the coin still flips inside the plain hit (k3 35/9,
  `run_output.txt`:27). On-board reverts at a seven-site attack need G1+G2. In look-ahead, G2 alone is enough.
- **F7.** G2's pending-hit arm matches any queued frame aimed at the opponent's empty Active, not only Kangaskhan's. The
  EQUIVALENCE reading (§B.7) argues that only the second punch can reach it. Reader two should confirm.
- **F8.** `score_dump_round2.rs` at P doesn't compile: `fn with_off<'a, R>` needs `R: 'a` (E0309). The cloud's fix is
  at 31380294 (`fn with_off<'a, R: 'a>`, blob `b2553655`). See the `tools_8c.tsv` item in §6.
- **F9.** No tool yet picks the gate for a look-ahead verdict. See the 8c driver in §6.
- **F10.** The per-decision revert is valid only at a root whose state equals the official engine's, including any frame
  already queued under a gate (`score_dump_round2.rs`:61-67). The classifier's "hash equal at every tick before the
  first difference" gives this. It also rules out EQUIVALENCE N3's cases. Step 8c must keep the precondition for every
  game it reverts.
- **F11.** P2's own gate runs predate Bounded Field x2 and `ROUND2_OFF`. By code they carry over: only `|| *ROUND2_OFF`
  was added, and the x2 sits inside the gated call. At P, P2 off is shown again on 8b's pairing 37 and its 4 RETURN ticks.
- **F12.** The suite logs don't record their command or environment. The `DECKGYM_ROUND2_OFF=1` setting is inferred from
  the failures across all 12 gates.

## 6. What must happen, and when

| When | Item | Who | Severity | Why |
|---|---|---|---|---|
| before sitting 1 | (a)'s open test, the gate_R > 0 match on Oct 1's 1,126 games: run it or waive it in writing | coordinator (run: cloud) | procedural | PLAN.md:257 lists it as open, and PLAN §4 says the laptop plays nothing until each precondition is met. It tests v2's ply counting on round 1's hand-off, not round 2. |
| before sitting 1 (outside my reads) | precondition (g): `SUITE_AT_P` must name a log that names P | coordinator / cloud | procedural; fails safe | `suite_default.txt` at 31380294 contains no `3161633` (0 matches), and `sitting1.sh`:788 refuses a log that doesn't name P's short hash |
| before sitting 1 (from (f)) | decide on EQUIVALENCE F1: the cloud fixes it now (recommended) or `rules/09` | coordinator | should fix; not a blocker | a crash no replayed game reaches; fixing it moves P |
| before sitting 2 | finalize `tools_8c.tsv` to the blobs this read covered | the laptop session | required (finalization) | see below |
| before 8c | the revert-check driver | Sonnet (8c tools) | required by the pin | see below |
| before 8c | A1's wording | the cloud or Sonnet | minor | see §2 |
| before 8c (recommended) | A4's dry run of the probe on two-Ariados games | cloud | note | sizes 8c's time |
| later / optional | A2 gates-off self-test; C-2 probe re-run at P; D2-D6; F2, F3 extra dumps; B3 title prefix; a real-game G6 and all-off run on counter-smoke pairings 0-1 (§7) | cloud | notes | none blocks |
| after this switch | C-1's guard, before any watch row with a two-Energy-type list against two Ariados | whoever owns the coin script then | low (latent) | §4 |

**`tools_8c.tsv` (main a5f2e7e5, marked TO FINALIZE).** It pins every 8c tool at 056158c3, the tip when it was written.
`sitting2.sh` refuses unless each tool is the blob named (:37, :264-266). Since then:

| Role | Pinned (056158c3) | At the tip 31380294 | Change |
|---|---|---|---|
| `revert_score_dump` `score_dump_round2.rs` | `35374de6` (`fn with_off<'a, R>`, :20) | `b2553655` (`fn with_off<'a, R: 'a>`) | the pinned copy is P's, which doesn't compile (F8). `git log` shows only 31616338 and 31380294 touch it. |
| `classifier` `tightened_rule.py` | `1451a0c6` (384d91dc) | `9817f8bc` (8106a900) | the review's fixes (cut titles, Kangaskhan's golden check, control_clean, CONDITION 3); 4 of its tests fail on the pinned copy (b1fb3032) |
| `classifier_tests` `test_tightened_rule.py` | `f0c87c2c` | `6a5e7924` | as above |
| `classify_8c.py` | not listed | `a487a34f` (c012104e, 8106a900) | PLAN (b)'s copy; missing |
| `coin_lookahead.py` | not listed | `25122f62` (c012104e, 8106a900) | PLAN (b)'s copy; missing |
| `probe`, `classify_8b`, `tracer`, `revert_check` | `31857834`, `18a7cc14`, `3fbc20d2`, `0c7c2b90` | the same | none |

My second reads of (a) and (b) cover the tip's blobs. As pinned, 8c's revert dump would fail to build (loudly), and 8c
would get the classifier from before the review's fixes (quietly).

**The revert-check driver (before 8c).** Nothing in the code reports a look-ahead game as explained before its revert
check:
- `classify_8c.py`:24-25 says it doesn't run the check; it writes every look-ahead verdict to `lookahead.tsv` (:334-340)
  under the key `lookahead_for_the_revert_check` (:370).
- The pin's gate 3 stops unless `8c_RESULT.txt` says `revert <l> of <l> reproduced` for all l look-ahead games
  (`pin/pin_rules.sh`:444-470).

But no tool yet runs the check per game from `lookahead.tsv`. `run_revert_gates.sh`'s section 6 is hard-coded to 8b's
ticks (:168-175). Without the driver, 8c stalls at the pin; it can't pass falsely. The driver needs:
- the gate from the probe kind: PLAIN -> G1; QUEUED -> G1+G2 on the board, G2 in look-ahead (F6); OWN -> G3; WILL -> G4;
  VS -> G5; TRAP and `trapleaf` -> G6; GUTS -> G7; PERISH -> G8; RETURN -> P2; plus "all off" as the second run;
- the tip's `score_dump_round2.rs`;
- only roots that are hash-equal to the official game (F10);
- a recorded pass or fail per game.

## 7. Withdrawn after the adversarial check

| Was | Claimed | Why withdrawn | Now |
|---|---|---|---|
| (a)/(b) B1, should fix | the revert check isn't enforced; a game could read "explained" with a failed revert | the pin enforces it (`pin_rules.sh`:470), and `classify_8c`'s exit 0 is not the 8c pass. The 8b look-ahead games all had the check run (17 of 17 with G1+G2, 4 of 4 with P2, 21 of 21 all off) | the driver is planned 8c work (§6) |
| (a)/(b) B2, should fix | PLAN step 6 names a stale watch script, and a missing counter is read as "never fired" | the runners pin `COIN_SCRIPT_BLOB=306f1f69` (`switch2.env`:22-24) and halt on another blob (`sitting1.sh`:1737-1742) or a missing counter (:1753-1755). `sitting2_check.py` raises on a watch game lacking a counter (:274-279), and the hand-off lists only counters that fired (:339). My proposed "refuse a missing name" would reject valid rows (`test_tightened_rule.py`:286-290) | nit: PLAN.md:275's step-6 wording is out of date |
| (a)/(b) C1, should fix | the mixed-Energy panic can stop 8b or step 9 | no list in those rows can make the board (§4, C-1) | C-1, latent |
| (a) A1's example | Research, then Will drawn, then attack | both are Supporters; km3 lifts the hidden-text rule for the audited texts | A1 kept, narrowed, documentation only |
| (c) G1, should fix | no counter for P3, which (c) covers | P3 is in (f)'s scope, not (c)'s (PLAN.md:360). It is recorded (`counters.tsv`:6-7), fails safe, and no replayed list holds a Fossil. The cloud's P3 smoke gave 640 of 640 equal, 320 with the Skull Fossil list | note |
| (c) G2, should fix | the round-2 counters were never shown silent with their gates off, nor re-run at P | silence follows from the code plus the revert tests. 32 boards ran at P (46 checks, 0 failures). Bounded Field x2 and the punch-after-promotion need no new logic | C-2 (low) for the three row groups not re-run; the crash part is C-1 |
| (c) G3, should fix | require `offgate_return_by_source` > 0 in 7b | every damaging attack into an Active already runs P2's rewritten lines, so identity covers them. A Rocky Helmet hit can't reach P2's only new logic (the gate needs an attack's Counterattack, :783). The counter fires merely because the Helmet holder was damaged (scan :546, :553). It is reported anyway (`sitting1.sh`:1802 `--report-rest`) | nit |
| (c) D1, should fix | the same panic as C1 | as C1 | C-1 |
| (e) F1, should fix | play G6 and G4 off in real games against the official engine before 8c | the code already reverts both (`hooks/retreat.rs`:255-266 = old :254-262; `will_on_gate_coins_on` read only at aaa:134, :149, :211). The same macro already moved real games for G1, G2 and ROUND2_OFF. The G4 half can't happen in those games (Will never attacked while Confused there). 8c's per-decision check compares every score with the official dump, so a faulty switch would fail visibly | optional: G6 and all off on counter-smoke pairings 0-1 |

## Appendix: outside rules switch 2, the split-run collector

These findings concern `rl/strength/split_collect.py` on `origin/claude/pensive-ptolemy-spwc0b` (tip ff6da9ef;
`r2_read/REVIEW_collector.md`). That file is not in P, not on the switch-2 branch, not on main, and not one of PLAN §4's
rows, so none of them affects this switch. All four survived the adversarial check. They must be fixed before the first
real split run's merge counts as a registered run.

| Id | Severity (after the check) | What |
|---|---|---|
| F2 | major | The program, manifest and engine checks rest only on `worker.json`. That file is overwritten by the stamp (:262-268), can be written after play, and hashes whatever program sits at `--program` then. Game records carry no program or engine hash (`main.rs`:336-342, :277), and a resume skips keys already done (:239-252). A worker that played half its slice on the wrong engine, rebuilt and re-stamped merges as COMPLETE. README:37's "stamped before play" is false for the proof's straight folder (`run_proof.sh`:54-55). |
| F1 | should fix (medium) | `merge` always writes `OUT/games.jsonl` (:278-282) and keeps games from workers it flagged for program, manifest, engine or slice problems (:130-170). INCOMPLETE shows only in the exit code and MERGE_RECORD.md. With `--out` at the registration folder, `strength_report.py --dir` would report a complete run with 0 errors. |
| F3 | should fix (minor) | The engine-tree check is skipped silently when the manifest's engine text has no `tree <hex>` (`registered_tree`, :56-62). The real Oct 4 km3 and kx3 manifests parse to None. The build record's `program_sha256` isn't checked against the program (:245-249, :263). A rebuild is accepted on equal self-check lines alone (:43-53), which is weaker than `slow_report.py`'s rule, though the docstring claims to copy it. |
| F4 | should fix | Decks are matched by name only. The manifest's deck sha256s are never compared with the files a worker loads (`main.rs`:120-125, :194, :258-259). A worker on a later checkout would play an edited list under the same name and seeds. |
