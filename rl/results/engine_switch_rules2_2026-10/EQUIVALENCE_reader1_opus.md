# Rules switch 2, precondition (f): reader one's equivalence reading (the diff reading)

*Reader one: the laptop session's read-only Opus subagent, Oct 9. P = `31616338` (engine tree `639d2f80`), on
`origin/claude/coin-prevention-round2`; the branch tip `31380294` changes nothing under `engine/`. Compared against the
official engine, main-8626a35 (tree `38af8b0`). Read-only: nothing was built, tested or played. Reader two (Sonnet) reads
later and on its own, tracing every caller.*

## In plain words

**What I was asked.** P rewrites code that every game runs. The Sept 28 rule says two readers must confirm three things
before the laptop plays:
1. wherever the new card rules don't apply, P plays exactly like today's official engine;
2. each rule's off switch brings back today's code exactly;
3. where a new rule applies, it does what the card says, and nothing more.

I read every change line by line (the "diff reading"). Reader two will follow every place the changed code is used.

**The answer: yes, with one exception.**
- Where the new rules don't apply, P offers the same moves, with the same chances, in the same order, and uses the same
  random numbers. What the bots see when they look ahead is the same too.
- Each of the 12 off switches gives back today's code at its spot.
- Where a new rule applies, it follows the card text: the seven attacks and the coin Abilities, Will, Victory Star, each
  Ariados counting, Guts, Perish Body, Luxury Coin, Fossils as Items, and the hit back taking Weakness (+20, or x2 under
  Bounded Field).

**The exception: a crash in one rare position (should fix, not a blocker).**
- **The position:** Mew ex copies the opponent's Mega Kangaskhan ex's "punch twice" attack, and the Kangaskhan's player
  has a coin-flip Pokémon such as Meowth in play. Rocky Helmet then Knocks Out Mew ex after the first punch.
- **What goes wrong:** P lines up the second punch before Mew's player picks a new Active. The punch then has no
  attacker, and the program stops with an error.
- **Today's engine** has the new Active pick first, so it doesn't crash.
- **No game we play can get there.** The only list with Mega Kangaskhan ex is an example deck we never play
  (`engine/example_decks/swampert-kanga-ninetails.txt`). No list we replay has a copier. A real Kangaskhan's own Knock Out
  is worth 3 points and ends the game first.
- **The fix** is one line plus a test.
- **My recommendation:** the cloud fixes it now, tests first. The laptop is held by the combined run until about Oct 10-11
  anyway. The fix moves P, so the suite reruns, both readers read the one changed spot, and the runners' P is updated.
- **If that doesn't fit:** ship P as it is and record the crash in `rules/09` as an open engine bug.
- This is the coordinator's call.

**What I first reported and then dropped after a second check:**
- *"A leftover `DECKGYM_...` setting could silently turn a rule off during a sitting."* The switch-2 runners already
  refuse to start when any such setting is present, and they log the check.
- *"Draft D's coverage file will differ by more than the caveat line."* The step-7c checker already allows Victini's whole
  caveat list to differ.
- *Corrected:* I wrote that no committed list holds Mega Kangaskhan ex. One does, the example deck named above. It is in
  no replayed set and has no coin-flip Pokémon.

**What reader two should look at hardest** (details at the end): every way a "new Active" choice can be lined up while
a queued hit is waiting, and the claim that only the Kangaskhan second punch can be waiting there.

## 1. Verdict per PLAN (f) item

PLAN.md:262 (row f) lists the code every game runs. Section 0 (PLAN.md:88) adds `handle_attack_retaliation` and P2's
callers. Section 9 question 2a (approved, PLAN.md:24-25) adds the seven other Fossil places. The columns are the three
questions above: (1) not acting = official? (2) its switch off = official? (3) acting = card text? Line numbers are at P;
"aaa" is `engine/src/actions/apply_attack_action.rs`, "aa" is `apply_action.rs`, "ao" is `attack_outcome.rs`, "tcp" is
`trainer_coin_plan.rs`.

| PLAN (f) item | Where at P | Gate | (1) | (2) | (3) | Verdict |
|---|---|---|---|---|---|---|
| `forecast_apply_damage` | aa:790-968 | G1, G3, G8 | yes | yes (G1 off; G8 off for Perish Body) | yes | **equivalent** (§A.11) |
| the both-sides prevention scan | aaa:277-313; ao:707-778 | G3 | yes | yes | yes | **equivalent** (§A.3) |
| the both-sides Guts scan | aaa:481-521; ao:780-859 | G7 | yes | yes | yes | **equivalent** (§A.8) |
| `modify_damage`'s cut on either side | `hooks/core.rs`:2078-2084 | G3 | yes | yes | yes | **equivalent** (§B.2) |
| the Retreat Cost loop | `hooks/retreat.rs`:251-277 | G6 | yes (0 or 1 Ariados) | yes | yes | **equivalent** (§B.4) |
| the Fossil check (the Item lock) | `move_generation_trainer.rs`:65-73 | G10 | yes | yes | yes | **equivalent** (§B.6) |
| the seven other Fossil checks (8 engine sites) | `models/card.rs`:114-120, :270-273; aaa:715, 5557, 7066, 8487; `apply_trainer_action.rs`:392; `move_generation_trainer.rs`:361; `shared_mutations.rs`:64; `apply_abilities_action.rs`:437 | G11 | yes | yes | yes | **equivalent** (§B.5, §B.6) |
| the promotion arm | `state/mod.rs`:1422-1436 | G2 | yes | yes | defender side yes; **attacker side no** | **equivalent except F1** (§B.7) |
| the Will check in `apply_attack_common_modifiers` | aaa:192-234 | G4 | yes | yes | yes | **equivalent** (§A.2) |
| the Victory Star staging | aaa:92-190; aa:185-398 | G4, G5 | yes | yes | yes | **equivalent** (§A.1, §A.10) |
| `coin_gated_choice`'s off-gate return | aaa:374-415 | G2 | yes: it hands back the very value it was given | yes | yes | **equivalent** (§A.5) |
| `handle_attack_retaliation` and P2's callers (section 0) | `apply_action_helpers.rs`:774-803; `hooks/core.rs`:1530-1543; `hooks/counterattack.rs`:13-42 | P2 | yes | yes | yes | **equivalent** (§B.1) |
| the switch plumbing (precondition e, where (f) depends on it) | `apply_action_helpers.rs`:616-769; `actions/mod.rs`:33-43 | all | no behaviour | n/a | n/a | **sound** (§B.8) |

## 2. Verdict per changed file

`git diff --no-renames 8626a35 31616338 -- engine/` changes 26 files: 17 source files and 9 test files
(`allowed_engine_files.tsv`; `diff/STAT.txt`). I covered all 17 source files. The decision on the runners (PLAN.md:40-42)
requires every file on the allowed list to be covered by both readers; this table is reader one's half of that mapping.

| File | +/- | What changed | Gate(s) | Verdict |
|---|---:|---|---|---|
| `actions/apply_attack_action.rs` | 391 | Victory Star gate helpers; the Will step and Will on the block coin; own-side prevention and Guts chains; the queued-choice constructor; `coin_gated_choice`; Chase Order, Wild Swing and Litter; the second punch; Tornado Shot, Wellspring Dance, Double Splash, Triple Bombardment and Mischievous Ring; four Fossil sites | G2, G3, G4, G5, G7, G11 | equivalent. The second punch (:2283-2288) is one half of F1. |
| `actions/attack_outcome.rs` | 168 | heads cuts tagged by side; Will helpers; the prevention and Guts splits generalized to either side; two items made `pub(crate)` | via G3, G4, G7 | equivalent |
| `actions/apply_action.rs` | 303 | Victory Star forecast; `forecast_apply_damage`'s coin step and Perish Body; a comment at Litter | G1, G3, G4, G5, G8 | equivalent |
| `actions/apply_action_helpers.rs` | 174 | P2 in `handle_attack_retaliation`; the switch plumbing | P2; all | equivalent |
| `actions/trainer_coin_plan.rs` | 17 | `luxury_coin_covers` | G9 | equivalent |
| `actions/mod.rs` | 11 | re-exports only | none | no behaviour |
| `actions/apply_trainer_action.rs` | 2 | Thieving Machine reads `is_printed_as` | G11 | equivalent |
| `actions/shared_mutations.rs` | 2 | `item_search_outcomes` reads `is_printed_as` | G11 | equivalent |
| `actions/apply_abilities_action.rs` | 3 | Raticate's top-4 peek reads `is_printed_as` | G11 | equivalent |
| `card_validation.rs` | 5 | caveat text: Victini's, and Gholdengo's (P1) | none (text) | no game effect; the text matches the code (§B.9) |
| `hooks/core.rs` | 33 | `attack_return_weakness_extra`; a doc comment; `modify_damage`'s own-side heads cut | P2, G3 | equivalent |
| `hooks/counterattack.rs` | 22 | `attack_counterattack_damage` pulled out (the same sum) | none | always equivalent |
| `hooks/mod.rs` | 2 | `pub(crate) use` lines | none | no behaviour |
| `hooks/retreat.rs` | 33 | Trap Territory counted per Ariados | G6 | equivalent |
| `models/card.rs` | 18 | `is_printed_as`, `is_item` | G11 | equivalent; no new field |
| `move_generation/move_generation_trainer.rs` | 10 | the Fossil lock; Thieving Machine's move | G10, G11 | equivalent |
| `state/mod.rs` | 10 | the queued-hit arm of `pending_hit_floor` | G2 | G2 off: equivalent. G2 on: **F1** |

**The 9 test files** (`engine/tests/`: b4a_attack_batch2, gholdengo_luxury_coin, galarian_cursola_perish_body,
legacy_ability_logic, meowth_carefree_steps, ursaluna_guts, rules_repair_trainers, victini_victory_star, and the new
rules_repair_return_damage_weakness). I didn't read their bodies line by line. I checked them as a set, from git objects
(`r2_read/e_tests_check.py`, output `r2_read/e/tests_check_out.txt`):
- 2,020 test names at 8626a35 and 2,104 at P: 5 removed and 89 added.
- No test under `engine/tests/` keeps its name with a changed body. The only two changed bodies are unit tests in
  `attack_outcome.rs`, and they change only for the new `(bool, idx, cut)` signature.
- The 5 removed names are old pins of the old behaviour. Each is back as a passing revert test, verbatim or through a
  helper that builds the same board (SECOND_READ_reader1_opus.md, (e)).

So no expectation that held at 8626a35 was loosened.

**No new game-state field.** The `State` derive (`state/mod.rs`:271), `types.rs`, `effects.rs` and `played_card.rs` are
not in the diff. `TrainerType`, `TrainerCard`, `Card` and `PokemonCard` gain only an `impl` block. So hashing, cloning,
serialization and every comparison the bots use are unchanged. The switches live outside `State`.

## 3. What I read, and how

- **The diff,** 8626a35 -> 31616338, one file per changed source file, with 12 lines of context. I also read the whole new
  and old files around every hunk (`r2_read/diff/`, `r2_read/new/`, `r2_read/old/`).
- **The code the answer depends on,** with `git show` and `git grep` at 8626a35, P and the tip:
  - the switch definitions (`apply_action_helpers.rs`:616-769);
  - `with_heads_coin_cuts` (ao:45-60) and `Outcomes::force_first_heads` (`outcomes.rs`:447-503, unchanged);
  - `guts_would_flip`, `handle_damage(_only)`, `handle_knockouts` and `wrap_with_common_logic`;
  - `modify_damage` (`hooks/core.rs`:1834-1854);
  - `trigger_promotion_or_declare_winner` (`state/mod.rs`:1366-1437);
  - the bots' handling of queued frames (`players/expectiminimax_player.rs`:631-717, `players/value_function_player.rs`:
    93-111). `engine/src/players/` is byte-identical at 8626a35 and P.
- **For each hunk,** I asked: (1) gate on but not acting, (2) gate off, (3) gate on and acting. A hunk with no gate gets (1)
  only.
- **The laptop's environment,** read-only. I looked for `DECKGYM_*` in the Windows process, user and machine
  environments, WSLENV, WSL's login and non-login shells, the shell start files and `/etc`. None is set.
- **The cloud's claims** were not taken on trust. Its recorded outputs are cited only where marked.
- **Every finding I flagged** was checked again by an adversarial pass that tried to refute it. Only what survived is
  listed as a finding. The rest is listed as withdrawn, with the reason.

## 4. Findings

### Surviving

**F1 (should fix; not a blocker): the queued-hit arm of `pending_hit_floor` leaves out the attacker's own empty Active.**

*Where.* `state/mod.rs`:1422-1436 at P, paired with aaa:2283-2288. The new arm:
```rust
// state/mod.rs:1429-1432 at P
SimpleAction::ApplyQueuedAttackDamage { targets, .. } =>
    crate::actions::queued_site_coin_on()
    && (*actor + 1) % 2 == player_with_empty_active
    && targets.iter().any(|(_, is_opponent, idx)| *is_opponent && *idx == 0),
```
The `ApplyDamage` arm beside it (:1424-1427, unchanged from old :1421-1422) also floors the promotion when
`*attacking_ref == (player_with_empty_active, 0)`, that is, when the pending hit's own attacker has left the Active spot.
The new arm has no counterpart of that clause.

*The position (G2 on, the default).*
- Mew ex uses Genome Hacking ("Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack";
  `effect_mechanic_map.rs`:110-117, CopyAttack OpponentActive). It copies the opponent's Mega Kangaskhan ex's
  Double-Punching Family.
- That Kangaskhan holds Rocky Helmet. Its player has 0 points and a coin-flip damage Pokémon in play, for example Meowth
  (Carefree Steps) on the Bench. That makes `coin_in_play` true at aaa:2283-2284.
- Mew ex has 20 HP or less. Mew's player has a Benched Pokémon.

*What P does* (the two adversarial checks agree):
1. The copied attack runs `mega_kangaskhan_ex_double_punching_family` with `action.actor` = Mew's player. The second
   punch is built as `ApplyQueuedAttackDamage{targets: [(40, true, 0)]}` (aaa:2285, :354-363) and inserted at index 0
   (aaa:2288).
2. The stack grew, so the first punch's `ResolveAttackRetaliation` frames are deferred and sit above the punch
   (ao:248-271).
3. Rocky Helmet's flat 20 Knocks Out Mew ex (`apply_action_helpers.rs`:782-796). Mew ex is worth 2 points, so a player at
   0 doesn't win (:1036-1046). `trigger_promotion_or_declare_winner(Mew's player)` runs with the punch still on the stack
   (:1071-1077).
4. The new arm needs `(*actor + 1) % 2 == player_with_empty_active`. For Mew's own frame that is false, and no
   `ApplyDamage` frame matches either. So `pending_hit_floor = 0`, and the promotion goes to index 0, **under** the punch
   (`state/mod.rs`:1435-1436).
5. The punch is the top frame (`move_generation/mod.rs`:45). It resolves through `finish_queued_attack_damage`
   (aaa:247-259, with no guard) and `handle_damage_only((Mew's player, 0), 40)` (ao:213, :229) into `modify_damage`.
   - The base damage is 40, not 0, so the early return at `hooks/core.rs`:1844-1847 doesn't apply.
   - So `state.in_play_pokemon[attacking_player][attacking_idx].as_ref().expect("Attacking Pokemon should be there when
     modifying damage")` (`hooks/core.rs`:1849-1851) **panics**.
   - The bots' look-ahead reaches the same panic.
6. *Variants.*
   - It happens every time when the coin Pokémon is on the Kangaskhan side's Bench.
   - With a copier that copies from the hand or deck (Mew's Miraculous Memory), the coin Pokémon can be that side's
     Active. With full prevention it then crashes only on tails, because a heads drops the hit.
   - If the first punch also Knocks Out the defender, the defender's promotion is floored above the punch and runs first.
     The crash follows.

*The official engine (and P with G2 off).* The punch is always
`ApplyDamage{attacking_ref: (actor, 0), [(40, opp, 0)], true}` (old aaa:2126-2145). The `ApplyDamage` arm matches its
`attacking_ref`, so Mew's player promotes first. The punch then comes from the new Active. That is an old oddity (one
could read the card as "no second attack once the attacker is gone"), but it isn't a crash. Whether the punch should
happen at all is a rules question outside this switch.

*Reach this switch.*
- A real Mega Kangaskhan ex can't get there. Its Knock Out is worth 3 points (`models/card.rs`:217-223), so the game ends
  before any promotion (`apply_action_helpers.rs`:1036-1045). The four printings with this attack are all named "Mega
  Kangaskhan ex" (`database.rs`:56449, 57689, 57919, 79060).
- The reachable form needs a non-Mega copier (CopyAttack). No list in a replayed set holds a copier (PLAN.md:195).
- One committed list holds Mega Kangaskhan ex: `engine/example_decks/swampert-kanga-ninetails.txt` (2 x B2 127). It has
  no coin-flip Pokémon, and it is in no replayed set.
- So no recorded or planned game reaches F1.
- The tests cover only the defender's Knock Out (`meowth_carefree_steps_test.rs`:559-606 and :1270-1360,
  `carefree_steps_flips_for_the_second_punch_after_a_knock_out`). PLAN.md:161's "the promotion still comes before the
  punch" is true for the defender only.

*The fix: inside the G2 test, never outside it.*
```rust
SimpleAction::ApplyQueuedAttackDamage { targets, .. } =>
    crate::actions::queued_site_coin_on()
    && (*actor == player_with_empty_active
        || ((*actor + 1) % 2 == player_with_empty_active
            && targets.iter().any(|(_, is_opponent, idx)| *is_opponent && *idx == 0))),
```
- Outside the G2 test, the new clause would act with G2 off. "G2 off = the official engine" would then break for any
  first-round queued frame.
- Inside it, the clause can only meet the second punch. That is because of §B.7's ordering argument, which reader two
  should confirm.
- Add a failing test first: the Mew ex position above, expecting Mew's player to promote before the punch and no panic.
- With the fix, P plays this position as the official engine does.

*Severity.* A crash, and new with G2 on. But no game this switch plays can reach it, G2 off restores the official
behaviour, and a crash fails loudly: it can't pass a wrong game. Should fix, low priority; not a blocker for the sittings.
Options:

| Option | What it costs | What it leaves |
|---|---|---|
| **A (recommended).** The cloud fixes it now, tests first. | One cloud commit; the suite at the new P; both readers read one hunk; `switch2.env`'s P and P_TREE and `allowed_engine_files.tsv` re-finalized. No laptop games (the laptop is held by the combined run until about Oct 10-11). No recorded game changes. | nothing |
| B. Ship P as it is; record it in `rules/09` as an open engine bug; fix it in the next rules round. | nothing now | a future list pairing a copier with a coin-flip Pokémon against Kangaskhan would crash its run (loudly) |

### Notes (not defects; for the other preconditions)

- **N1 (for a and c): the second punch's looser gate changes what the bots see, even when no coin can flip.**
  - With G2 on and any coin-flip Pokémon on the defending side, the punch is queued as `ApplyQueuedAttackDamage` (aaa:
    2283-2285), even if that Pokémon stays Benched and never takes the punch.
  - The bots resolve such a frame as a free continuation, even at depth 0 (`expectiminimax_player.rs`:659-717;
    `value_function_player.rs`:93-111). A plain `ApplyDamage` frame is an ordinary ply.
  - The punch also carries the attack's name into `modify_damage` (ao:222-236) and runs the attack-path splits.
  - So Mega Kangaskhan ex against a list holding Meowth B2 124, Togekiss A4 080, Bastiodon A2 114 or Hisuian Goodra
    B3b 050 can change in look-ahead with no coin flipped. This is by design (the comment at aaa:2278-2282).
  - No replayed list holds Kangaskhan.
- **N2 (for e): G2 off alone isn't the official engine at the seven sites when the hit lands on the board.**
  - G2 off restores the plain `ApplyDamage`. But with G1 on, `forecast_apply_damage` still flips the coin in it
    (aa:801-813).
  - The macro's doc line ("Off is the official engine ... at that gate") overstates this for G2. G2's own doc
    (`apply_action_helpers.rs`:697-700) says so.
  - On-board reverts at those sites need G1 and G2 together. In look-ahead G2 alone is enough (free-frame rule).
  - The recorded k3 (35, 9) "as neither engine" is this case.
- **N3 (for e): the switches are read when the code runs, not when a continuation was built.**
  - Turned off at a root that already holds a continuation built with it on, a switch evaluates a state the official
    engine never reaches. Examples:
    - G5 off at a Victory Star pause staged after a block coin takes `forecast_victory_star_choice`'s other branch
      (aa:390-397), which flips a second block coin;
    - G2 off at the retaliation frame between the punches puts the defender's promotion under the queued punch, and
      `modify_damage` panics at `hooks/core.rs`:1852-1854.
  - The revert check is safe only at roots whose state equals the official engine's (hash-equal at every tick before the
    first difference). That rules both cases out. This is the (e) read's F10. Step 8c must keep that precondition.
- **N4 (pre-existing, unchanged): the Guts flip order depends on HashMap's random seed.**
  - `forecast_apply_damage_after_coins` builds its Guts list from a `std::collections::HashMap` (aa:873-914; old
    :775-795). With two or more Guts Pokémon Knocked Out by one queued hit, the branch order can differ between runs.
  - It is the same in old and new. The new coin list uses a `BTreeMap`.
- **N5 (for a): `coin_gated_choice` decides each choice on its own** (aaa:398-415).
  - A Tornado Shot, Triple Bombardment or Wellspring Dance frame can mix `ApplyQueuedAttackDamage` and `ApplyDamage` when
    only a Benched coin Pokémon makes some choices convert.
  - The bots' free-continuation test needs every choice queued, so a mixed frame stays an ordinary ply.
- **N6 (card text, outside this package): recoil isn't a damage target.**
  - An attacker's damage to itself is applied directly (aaa:6491-6516). So the own-side coin (G3) and own-side Guts (G7)
    never see it, in old and new alike.
- **N7 (text): the caveat lines aren't gated.**
  - With every gate off, the program plays as the official engine but prints P's Victini and Gholdengo caveats
    (`card_validation.rs`:96-102).
  - This matters only if a page were made with the gates off.
- **N8 (players, unchanged): kt switch 3's `counter_cut` prices the hit back flat.**
  - It goes through the unchanged `get_counterattack_damage` (`players/value_functions.rs`:1936, :5038). The search sees
    P2's +20, but the kt3/ktc3 static clock doesn't.
  - Diagnostic presets only; inside the approved "players/ unchanged" scope.

### Withdrawn after the adversarial check

- **"Fourteen `DECKGYM_*` variables can silently turn rules off during a sitting" (was should fix).**
  - The engine part is accurate. Each switch is a `LazyLock` read once; "1" or "true" in any case turns it off
    (`apply_action_helpers.rs`:620-622, 652-656, 674-746).
  - But I had checked the switch-1 runners. The switch-2 runners (main a5f2e7e5) already refuse:
    - `sitting1.sh`:1315-1318 (`env_check` lists every exported `DECKGYM_*`, plus `PDL_EQUIV_DEALS` and
      `GOLDFISH_TRACE`), :1533 (a start refuses), :1400 (the dry run reports it), :1610 (the START line records
      "env: no DECKGYM_* set");
    - `sitting2.sh`:875, :1544, :1622;
    - `pin/pin_rules.sh`:342-343 and :348.
  - A start also refuses if a helper differs from its committed version, so the check can't be edited out before a run.
    Nothing in the runners sets such a variable.
- **"Step 7c must allow one more line for Victini's limitations list" (was a note).**
  - `sitting1_check.py --allow-caveat KEY` (:520-529) blanks KEY's whole `limitations` list on both sides before
    comparing, and reports the two lists.
  - A list that grows from 1 entry to 2 passes. `sitting1.sh`:109-110 also expects the coverage files to be equal.
- **Corrected reach statement.**
  - The earlier "no committed list holds Mega Kangaskhan ex" is wrong. See F1's reach.

## 5. For reader two: where to look hardest

1. **Every way a promotion can be lined up while an `ApplyQueuedAttackDamage` frame is on the stack.**
   - Cover every caller of `trigger_promotion_or_declare_winner`, `handle_knockouts`' early return while a
     `ResolveAttackRetaliation` frame is pending (`apply_action_helpers.rs`:850-851), and every `insert(0, ..)` under
     `engine/src/actions/`.
   - Confirm F1.
   - Confirm or refute §B.7's claim: every queued frame the official engine could already build is pushed above the
     deferred retaliation frame and is gone before any promotion. If so, the new arm (and the fixed one) can only meet the
     second punch.
   - The (e) read's F7 notes the arm's pattern is broader than Kangaskhan. The question is whether anything else can
     reach it.
2. **G1's reach.** Every builder of `ApplyDamage{is_from_active_attack: true}`; my `git grep` found them only in aaa.
   Also every scope where a heads-coin cut is in force (`with_heads_coin_cuts`; ao:45-60, :228-239). Confirm that no
   `forecast_apply_damage` forecast or mutation runs inside one, since §A.11's equivalence needs it.
3. **The bots' side of the queued frames.**
   - The free-continuation rule (`expectiminimax_player.rs`:659-717) and `value_function_player.rs`:93-111.
   - Mixed frames (N5) and the punch's looser gate (N1).
   - `players/public_reply.rs`:564, which calls `handle_attack_retaliation` on a successor state.
4. **`handle_attack_retaliation`'s routes.** These are ao:281, aa:635 and :959, `apply_action_helpers.rs`:531, and
   `public_reply.rs`:564. Also check:
   - the `attacking_ref` remap in `apply_activate` (`apply_action_helpers.rs`:1133-1147);
   - `damaged_actives`' de-duplication (:547-555, :609-611);
   - the decision not to read `NoWeakness` (`hooks/core.rs`:1534-1536).
5. **Retreat Cost readers.** The callers of `get_retreat_cost_for_player_internal`: the retreat itself, Heavy Helmet,
   Grass Knot (aaa:4700), and the bots' `active_retreat_cost`.
6. **Item readers.** Every caller of `is_printed_as` and `is_item`, and the raw `TrainerType::Item` reads left: the
   lock, `temp_deck.rs`, `tui/app.rs` and `value_functions.rs`:2385 (the excluded Junk Spark pricing).
7. **Luxury Coin's two entries** (tcp:616-618 sample, :846-849 search), the `active_stadium_owner = None` case, and the
   order against Penny's `choose_supporter_source` (tcp:622).
8. **Victory Star.** `forecast_victory_star_choice` (aa:376-398) reads its predicate when the choice is made. Check that
   nothing can play Will between the attack and the choice.

## Appendix: the per-hunk reading

### A. `apply_attack_action.rs` (aaa), `attack_outcome.rs` (ao), `apply_action.rs` (aa)

**The gates read in these files.** Each gate is `X_on()`: the thread's `with_X` setting if there is one, otherwise
`!(env DECKGYM_<...> || DECKGYM_ROUND2_OFF)` (the `round2_switch!` macro, `apply_action_helpers.rs`:674-689). All are on
by default. The gate tests are pure reads of the state, a thread-local and a `LazyLock`: they use no RNG and change
nothing. Where they sit in `&&` chains, they are evaluated after the cheaper card checks.

| Gate | Read at (P) | Off gives |
|---|---|---|
| G1 plain-hit coin | aa:801 `is_from_active_attack && plain_hit_coin_on()` | `coin_targets = vec![]`: the old Guts-only path |
| G2 seven sites | aaa:385, 427, 437, 2283; `state/mod.rs`:1430 | the plain `ApplyDamage` as built before; no queued-hit arm |
| G3 own side | aaa:304, aa:804, `hooks/core.rs`:2078-2079 | the opponent's Pokémon only |
| G4 Will on gate coins | aaa:134, 149, 211 | no Will step; the block coin flipped fairly; Victory Star not staged with a pending Will |
| G5 Victory Star after a block coin | aaa:147-148 | Victory Star not staged with a block coin |
| G7 own-side Guts | aaa:505 | the opponent's Pokémon only |
| G8 Perish Body on a queued hit | aa:878 | no Perish Body branch |
| G9 Luxury Coin on your own Stadium | tcp:46 | every Stadium covered |
| G11 Fossil as Item | `models/card.rs`:114-120, :270-273 | `self == printed`, the old `==` |

**A.1 Victory Star gate helpers, aaa:92-190 (old :89-160).**
- `has_block_coin` (aaa:92-97) is the old inline `get_active_effects().any(CoinFlipToBlockAttack)`.
- `victory_star_waits_for_gate_heads` (aaa:110-120) is the old `has_unverified_attacker_coin_gate`, word for word:
  `!sub && (confused || block)`.
- `gate_tails_outcomes` and `finish_attack_after_gate_heads` (aaa:167-190) are the old `confusion_tails_outcomes` and
  `finish_attack_after_confusion_heads`, renamed with the same bodies. The old names have no other callers (`git grep`
  at 8626a35).
- `victory_star_stages_gate_coins` (aaa:141-150) is `gates && !(block && !G5) && !(will && !G4)`.
  - (1) With no block coin and no pending Will, it is `!sub && confused`. That is the old
    `victory_star_waits_for_confusion_heads` (old :117).
  - (2) With G4 and G5 off, it is `!sub && confused && !block && !will`, the old function exactly.
  - (3) Victory Star's text covers "coins for an attack of 1 of your [R] Pokémon". The block coin is flipped for the
    opponent's effect, so it is never rerolled.

| State at the attack | old | P (G4, G5 on) | G4 off | G5 off | both off |
|---|---|---|---|---|---|
| not Confused, no block coin | no gate | no gate | no gate | no gate | no gate |
| Confused, no block coin, no Will | staged | staged | staged | staged | staged |
| Confused + Will, no block coin | legacy | staged (Will on the attack's batch) | legacy | staged | legacy |
| block coin, no Will | legacy | staged | staged | legacy | legacy |
| block coin + Will | legacy | staged, Will on the block coin | legacy | legacy | legacy |

("legacy" = `try_forecast_victory_star_attack` returns `None` and the ordinary path runs.)

**A.2 `apply_attack_common_modifiers`, aaa:192-234 (old :161-187).**
- New: a Will step before Confusion (aaa:208-217), gated `confused && !block && will && G4`.
- New: the block coin goes to `block_coin_heads_by_will` when `block && will && G4` (aaa:226-230).
- (1) With no Will pending, both tests are false, and the sequence is the old one: Confusion flip, block flip, defender
  modifiers.
  - With Will pending but no gate coin, both tests are also false, and `finish_forecast` applies Will as before
    (aa:683-706, unchanged).
  - `force_first_heads_using_will` returns `Err(self)` untouched when no branch has a first-heads path (ao:628-635).
- (2) G4 off makes both tests false.
- (3) Will (A4 156): "The next time you flip any number of coins for the effect of an attack, Ability, or Trainer card
  ... the first coin flip will definitely be heads."
  - The Confusion coin isn't flipped for an effect, so Will waits for the attack's own first coin. The forcing is applied
    before `prepend_nullifying_coin_gate` drops the coin paths, and `finish_forecast` then finds no paths
    (`outcomes.rs`:489-491). So Will is never used twice.
  - The block coin is flipped by the Will player for the opponent's attack effect, and it is that player's next coin. So
    Will makes it heads, and the attack's own coins stay fair (ao:678-689).

**A.3 `apply_defender_damage_prevention_if_needed`, aaa:277-313 (old :229-254).**
- The opponent's scan is unchanged apart from the tag `(true, idx, r)`. The own side is chained after it (aaa:304-306),
  filtered by G3.
- (1) `split_with_damage_prevention`'s tests reduce to the old ones for `target_side == true`:
  - ao:720 `is_opponent == target_side` is old `*is_opponent`;
  - ao:742-746 is old :656-661;
  - `resolved_heads_coin_cuts` maps `true` to `(opponent, idx)` (ao:189-195).
  - The flipping order is unchanged, so the mask-to-branch order is too.
  - With an own-side coin Pokémon that the attack doesn't damage, `reductions` is non-empty where old returned early. But
    every branch then has `flipping` empty and is pushed unchanged, in order (ao:725-728).
- (2) G3 off makes the chain empty.
- (3) "If any damage is done to this Pokémon by attacks" has no "your opponent's".

**A.4 `queued_attack_damage_choice` -> `queued_attack_damage_targets_choice`, aaa:335-371 (old :281-308).**
- A single target gives `ApplyQueuedAttackDamage{attack, [(damage, true, idx)]}` with the coin flag, or
  `ApplyDamage{(actor,0), [(damage, opp, idx)], true}` without it. Both are equal to old.
- Every first-round caller (aaa:3056, 3095, 3133, 4095, 4586, 4736, 6727) gets the same value.

**A.5 `any_coin_target`, `site_coin_gated_choice`, `coin_gated_choice`, aaa:374-415 (new).**
- `coin_gated_choice` returns the very `choice` it was given (moved back, unchanged) when:
  - it isn't `ApplyDamage{(actor,0), _, true}`;
  - or any target isn't the opponent's;
  - or no target has a coin Ability.
- `site_coin_gated_choice` with G2 off returns `choice` without looking.
- (1) and (2): byte-identical actions, in the same order.
- (3) The conversion labels the whole choice as the attack's own damage, so the coin flips through
  `finish_queued_attack_damage` (aaa:247-260).

**A.6 Chase Order, Wild Swing and Litter, aaa:423-476 (old :306-341), aa:1436.**
- `chosen_damage_choice` builds the old plain `ApplyDamage` (aaa:448-452). With a printed attack it calls
  `coin_gated_choice` on it.
- Old (:311-327): when the opponent's Active had a coin Ability and the printed Chase Order existed, it queued; otherwise
  plain. P gives `ApplyQueuedAttackDamage{chase_order, [(damage, true, 0)]}` exactly when old did.
- With G2 off, Wild Swing's and Litter's closures reject (aaa:427, 437). So they get the plain hit, equal to old (old aa:
  1716-1735 for Litter).
- (3) A copied attack isn't printed, so it keeps the plain path, and G1 flips it in `forecast_apply_damage`.

**A.7 Kangaskhan's second punch, aaa:2272-2290 (old :2126-2149).**
- Old: `insert(0, (actor, [ApplyDamage{(actor,0), [(40, opp, 0)], true}]))`.
- New: `queued_attack_damage_choice(actor, &attack, 40, 0, coin_in_play)`, with `coin_in_play = G2 && any opponent
  Pokémon has a coin Ability`, inserted at 0.
- With `false`, it is the same `ApplyDamage` (A.4). So (1) holds when no coin Ability is in play, and (2) holds with G2
  off.
- (3) The text: "This attack is used twice in a row. The second attack does 40 damage. (If the first attack Knocks Out
  your opponent's Active Pokémon, the second attack is used after your opponent chooses a new Active Pokémon.)"
  - The defender's promotion is handled by the new arm.
  - The attacker's is not: see F1.
  - For the looser gate, see N1.

**A.8 `apply_defender_guts_if_needed`, aaa:481-521 (old :348-372).**
- The opponent's slots are tagged `(true, idx)`. The own side is chained under G7.
- `split_with_guts_survival` (ao:780-859) gives the old answers for `true`: ao:800, :803 and :839-842.
- (1) An own Guts Pokémon the attack doesn't damage has `raw_total == 0`. `guts_would_flip` returns false at once
  (`apply_action_helpers.rs`:489-491).
- (2) G7 off leaves only the old slots.
- (3) "would be Knocked Out by damage from an attack" has no "your opponent's".
- The old `forecast_apply_damage` already flipped Guts on either side for a queued hit (old aa:779-795). This brings the
  attack path into line.

**A.9 The five other sites.** These are Tornado Shot (aaa:4032-4040), Wellspring Dance (:5895-5905), Double Splash and
Triple Bombardment (:6275-6278) and Mischievous Ring (:8581-8612).
- Each wraps the old `ApplyDamage` in `site_coin_gated_choice`. The choices are built and ordered as before.
- The new `attack` parameters (call sites aaa:935, 1660, 1748) change only what is passed. Mischievous Ring's
  `damage = attack.fixed_damage` (aaa:8583) is the value old received. Its gate reads the board after the Tools are
  shuffled away, at the same moment old built the action.
- Own-Bench forms fail the all-opponent test and stay plain.
- (3) One flip per attack damage, with no double flip. Where the choice is queued, the attack's own outcome carries no
  damage. Where it does carry damage (Wellspring tails, Tornado Shot with no Bench), the hit isn't queued.

**A.10 `try_forecast_victory_star_attack` and `forecast_victory_star_choice`, aa:185-398 (old :185-384).**
- The early return (aa:209-214) is `gates && !stages`. That is the old `!confusion_first && unverified` whenever the
  switches are off or no round-2 case holds.
- `will_on_block` is false unless G4 and a block coin with Will. So `!will_on_block && has_pending_will` (aa:223) is the
  old `has_pending_will`.
- In the old-equivalent case: tails `(1.0 - 0.5) * p` and heads `0.5 * p` are bit-identical to old `0.5 * probability`
  (old :300, :306). 1.0 - 0.5 is exact. The order is tails, then the pause, as old.
- `forecast_victory_star_choice` (aa:376-398) switches on `victory_star_stages_gate_coins` (old:
  `victory_star_waits_for_confusion_heads`). Nothing can play Will between the attack and this choice, so old and new
  take the same branch in every old-staged case.
- (3) Confused + block coin + Will: Will is spent in the Confusion-tails branches too (PLAN question 2b). The turn ends
  there, so no game changes.

**A.11 `forecast_apply_damage` and `forecast_apply_damage_after_coins`, aa:790-968 (old :768-838).**
- (1) and (2): `coin_targets` is empty when the hit isn't from an attack, G1 is off, no damaged target has a coin
  Ability, or such a target is the attacker's own and G3 is off. Then `after_coins(targets.to_vec(), vec![])` runs:
  - `with_heads_coin_cuts(vec![], f)` is a plain `f()` when no cut is in force (ao:46-48). Cuts are in force only inside
    an attack outcome's damage step and the split closures (ao:228-239), never around this forecast.
  - `perish_body` is false unless G8 and the defending Active has Perish Body.
  - `flipping` is the old HashMap filter (aa:873-914 vs old :775-795).
  - The single-branch path (aa:916-921) is old :797-802.
  - The multi-branch path with `perish_coins = [false]` gives probabilities `1.0/(combos*1)` x `combos`, the old value,
    and the same mutations in mask order.
  - So the branch count, probabilities and RNG draws are the same. Every `ApplyDamage` with
    `is_from_active_attack: true` is built in aaa (`git grep` at P), so G1 can't touch an Ability's or a Checkup's
    damage.
- (3) The four coin Abilities flip once per damaged carrier, in a deterministic `BTreeMap` order (aa:796-813).
  - Heads with full prevention drops that target's entries.
  - A finite cut is put in force for Guts, Perish Body and the damage itself (`hooks/core.rs`:2078-2084).
  - Perish Body (A4a 035) checks only the opponent's Active. It runs after the retaliation, and its handler re-checks
    the Knock Out and the Ability (ao:1258-1283).

**A.12 `attack_outcome.rs` otherwise.**
- `heads_coin_cuts` becomes `(bool, idx, cut)` (ao:94). Every constructor still sets `vec![]`.
- `using_will_first`, `force_first_heads_using_will` and `block_coin_heads_by_will` (ao:176-185, 627-689) are called
  only under G4.
  - The reweighting copies `Outcomes::force_first_heads` branch for branch: `None` kept; `Exact` filtered and scaled;
    `UntilTailsAtLeast{0}` x0.5 to `{1}`; then normalised.
  - The one difference is the early `Err` when no path starts with heads. Then Will stays unused, as the text needs.
- `would_knock_out` (ao:1226) and `coin_damage_prevention` (aaa:318) are made `pub(crate)`. That is visibility only.

**A.13 `trainer_coin_plan.rs`, tcp:45-49, applied at :616-618 and :846-849.**
- `luxury_coin_covers` is `!G9 || action isn't UseStadium || owner != Some(opponent)`. It runs after the pure
  `luxury_coin_source` and before any RNG use (Penny's `choose_supporter_source` is at :622). Play and search apply the
  same test.
- (1) With no Gholdengo, the source is `None` first, as before.
- (2) G9 off gives true.
- (3) Luxury Coin (B4a 051) covers "coins for an effect of your Trainer cards". The opponent's Stadium isn't yours. An
  unrecorded owner stays covered.

### B. The other files

**B.1 `handle_attack_retaliation` (P2), `apply_action_helpers.rs`:774-803 (old :614-633).**
```rust
let weakness_extra = if return_weakness_on() && attacking_ref.1 == 0 && attack_counterattack_damage(target) > 0 {
    state.in_play_pokemon[attacking_player][0].as_ref()
        .map_or(0, |attacker| attack_return_weakness_extra(state, target, attacker))
} else { 0 };
attacker.apply_damage(counter_damage + weakness_extra);   // was: attacker.apply_damage(counter_damage);
```
- (2) P2 off gives `weakness_extra = 0`, which is the old line. Nothing else in the loop changed.
- (1) The extra is 0 in each of these cases: no `CardEffect::Counterattack` on the target; the attacker isn't at index 0;
  the attacker's slot is empty; or `printed_weakness_application` returns `None`. Every call it makes is a pure read.
- (3) The hit back's sources:
  - Only `CardEffect::Counterattack` takes Weakness. Its producers are exactly the four map entries for the five attacks'
    text (`effect_mechanic_map.rs`:525-548, :2537-2544; `git grep` at P).
  - Rocky Helmet and `AbilityMechanic::CounterattackDamage` stay flat (`hooks/counterattack.rs`:13-29).
- (3) The receiver and the type:
  - The receiver is the attacker; the holder gives the type (`hooks/core.rs`:1537-1543).
  - Under Bounded Field (B3 155), `Double` applies when the holder isn't a Mega ex (core.rs:1518-1522). Then the attack's
    part is doubled; the Tool's and the Ability's parts are not. A Mega ex holder gets +20.
- (3) Who takes it:
  - Only an Active attacker takes it. `attacking_ref` is remapped by `apply_activate` (:1133-1147) when the attack's own
    effect switches the attacker.
  - One extra per damaged Active (`damaged_actives` de-duplicated, :547-555, :609-611).
  - `NoWeakness` is not read, by choice (core.rs:1534-1536). Its two producers cover only "your opponent's next turn",
    and a hit back always lands on the receiver's own turn.
- Every route goes through this function: ao:281, aa:635, aa:959, `apply_action_helpers.rs`:531, and
  `players/public_reply.rs`:564 (unchanged). So the bots' look-ahead sees the same damage.

**B.2 `hooks/core.rs`.**
- `attack_return_weakness_extra` (:1530-1543) is used only by B.1.
- :1604-1629 is doc comments only.
- `modify_damage`'s heads cut (G3), :2078-2084 (old :2061):
  ```rust
  let heads_coin_cut = if is_from_active_attack
      && (attacking_player != target_player || crate::actions::own_side_coin_on())
  { crate::actions::attack_outcome::heads_coin_cut((target_player, target_idx)) } else { 0 };
  ```
  - (2) With G3 off, this is the old condition character for character.
  - (1) An own-side key is put in force only by own-side staging (aaa:304, aa:804, both under G3). With none, the sum is
    0. Keys can't collide across sides.
  - (3) The cut comes off after Weakness, as the opponent's does.

**B.3 `hooks/counterattack.rs`:13-42; `hooks/mod.rs`:34-35.**
- `attack_counterattack_damage` is the old inline sum, character for character. The order and return values are
  unchanged.
- `hooks/mod.rs` adds `use` lines only.

**B.4 `hooks/retreat.rs`, the Retreat Cost loop (G6), :251-277 (old :251-260).**
- (2) With G6 off, `if !trap_territory_each_on()` (:258-266) runs the old loop line for line: the first matching
  Pokémon pushes one Colorless, then `break`.
- (1) With G6 on, the loop pushes `amount` for every match, with no `break`. The only producer is
  `effect_ability_mechanic_map.rs`:692 `{ amount: 1 }`. So with 0 or 1 Ariados the result is the same.
  - Both branches use the same `is_active` filter, the same pure `get_in_play_ability_mechanic` (suppression respected)
    and the same position after the reductions.
  - The Big Air Balloon early return (:158-160) is unchanged.
- (3) "Your opponent's Active Pokémon's Retreat Cost is 1 more", once per Ariados. It flows into every reader of the
  Retreat Cost: retreat, Heavy Helmet and Grass Knot.

**B.5 `models/card.rs`:110-121, :270-273 (P3's core).**
```rust
pub fn is_printed_as(&self, printed: &TrainerType) -> bool {
    self == printed || (crate::actions::fossil_as_item_on() && *printed == TrainerType::Item && *self == TrainerType::Fossil)
}
pub fn is_item(&self) -> bool { matches!(self, Card::Trainer(t) if t.trainer_card_type.is_printed_as(&TrainerType::Item)) }
```
- (2) G11 off is `self == printed`.
- (1) With G11 on, it differs from `==` only for (Fossil, Item).
- (3) A Fossil counts as an Item card wherever a card says "Item card" (`rules/01`, `rules/04` §6).
- No new field.

**B.6 The Fossil sites.**
- Thieving Machine: `apply_trainer_action.rs`:392 (outcome) and `move_generation_trainer.rs`:361 (move). Both read the same
  G11, so the move is never offered with an empty list.
- `shared_mutations.rs`:64: the two "random Item card from your deck" texts.
- `apply_abilities_action.rs`:437: Raticate's top-4 peek.
- aaa:715 (Scavenge), :5557 (hand disruption via `is_item`), :7066 (Junk Spark) and :8487 (Crackling Snap).
- (1) With no Fossil in the zone read, each is unchanged.
- The set is complete: every database "Item card" text now reads `is_printed_as`. The raw `TrainerType::Item` reads left
  are the lock (G10), `temp_deck.rs`, `tui/app.rs` and the excluded pricing at `value_functions.rs`:2385.
- The lock, `move_generation_trainer.rs`:65-73:
  ```rust
  if (trainer_card.trainer_card_type == TrainerType::Item
      || (crate::actions::fossil_item_lock_on() && trainer_card.trainer_card_type == TrainerType::Fossil))
      && !can_play_item(state)
  ```
  - (2) G10 off is the old `Item && !can_play_item` (old :65).
  - (1) With no `NoItemCards`, `can_play_item` is true and nothing changes.
  - (3) Under a lock, a Fossil gets no move.

**B.7 `state/mod.rs`, the promotion floor (G2), :1413-1436 (old :1419-1424).**
- The hunk turns `rposition(|(_, choices)|` into `rposition(|(actor, choices)|` and adds the arm quoted in F1.
- (2) With G2 off, the arm returns false. At 8626a35 a queued frame fell into `_ => false`.
- (1) **Which frames the arm can meet.** At 8626a35, `ApplyQueuedAttackDamage` frames were built at old aaa:293 and in
  `also_choice_bench_damage`.
  - All of them are pushed by the attack's post-effect *above* the deferred `ResolveAttackRetaliation` frame
    (ao:248-271).
  - While that frame is on the stack, `handle_knockouts` returns at once (`apply_action_helpers.rs`:850-851). So no
    promotion is lined up while those frames wait.
  - The arm acts only on frames inserted *below* the retaliation frame. The only one is the second punch (aaa:2288).
  - Reader two should confirm this, since F1's fix relies on it.
- (3) Defender's side: the first punch Knocks Out the defender, the defender's promotion goes above the queued punch, and
  the opponent picks first, as the card says. This is tested
  (`carefree_steps_flips_for_the_second_punch_after_a_knock_out`).
- (3) Attacker's side: missing. See F1.

**B.8 The switch plumbing, `apply_action_helpers.rs`:616-769; `actions/mod.rs`:33-43.**
- 12 settings: P2, and G1 to G11. Each is a process-wide `LazyLock<bool>` read once from an environment variable, plus a
  thread-local `Cell<Option<bool>>`.
  - `on = thread_local.unwrap_or(!(env_off || ROUND2_OFF))` (:629-631, :681-683).
  - "1" or "true" (any case) turns a gate off; anything else leaves it on. No `env!` or `option_env!` is involved, so the
    binary doesn't depend on the build environment.
- `with_*` and `scoped` restore the previous value on drop, a panic included. `with_round2` lists all 12 cells
  (:750-769).
- `with_*` is thread-local. `deckgym simulate` runs games on rayon workers (`simulate.rs`:185-254), so only the variable
  reaches those.
- The revert check's per-decision `with_*` is sound:
  - `engine/src/players/` has no threads (`git grep rayon|thread::spawn|par_iter` at P);
  - it keeps no cache across decisions.
- `actions/mod.rs` re-exports the 12 `with_*` functions as `pub` and the `_on()` functions as `pub(crate)`.
- Each `_on()` is a thread-local read and an atomic load. That costs time, not behaviour.

**B.9 `card_validation.rs`:97-98, :102 (text).**
- `get_implementation_status` (:80-82) reads only whether the list is empty. Victini and Gholdengo stay
  `RulesUnverified`. The only readers print the text (`bin/card_status.rs`, `cli_preflight.rs`:60).
- Gholdengo (P1): "offered on Arcade or Mesagoza only when the player activating it played that Stadium, not on the
  opponent's; a Stadium with no recorded player keeps the offer." This matches tcp:45-49. `active_stadium_owner` already
  existed (`state/mod.rs`:318).
- Victini matches aaa:99-150 and :192-231: gate coins first, never offered for a reroll; Will goes to the block coin if
  there is one, otherwise to the attack's own first coin; the order of Confusion and the block coin is left open.

### C. What the recorded outputs agree with (cited, not re-run)

`revert_switches/run_output.txt` at 31380294:
- `DECKGYM_ROUND2_OFF=1` reproduces the official engine's 8b rows byte for byte.
- 240 `deckgym simulate` games (digest 59dd3e38108dd725) match the official program's.
- G3 to G11, each off alone, change no 8b deal.
- G2 off alone leaves k3 (35, 9) as neither engine (N2).

The working files behind this document are in `r2_read/`: `EQUIV_part1.md` and `EQUIV_part2.md` (the two halves of the
reading), the extracted files under `diff/`, `new/` and `old/`, and `fin1.sh` and `fin2.sh` (the Kangaskhan list check).
The runners' environment guard and the step-7c caveat allowance were read in the working tree at main 0ed40102.
