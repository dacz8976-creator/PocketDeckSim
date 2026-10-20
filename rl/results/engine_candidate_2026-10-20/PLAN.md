# Engine candidate, Oct 20, 2026: the change list, written BEFORE any build

**This is a CANDIDATE. It is not adopted.**
- main, START_HERE, the pin documents, `project_manifest.json`, `current_engine.py` and `rl/engine-2026-10-12/` stay untouched.
- The frozen AI judge (judge-prompt-frozen-4, engine tree 70652fff) also stays as it is.
- Adoption follows Astra's review and Dustin's yes. No API spend.

**Who and why:** the job comes from the coordinator, Oct 20, on Dustin's word: "I kind of think we should make the fixes if we aren't doing anything else right now". Astra voted to defer; its two conditions are this list and keeping the old pin intact.

**The base:** main b829787c, engine tree 70652fff, the Oct 12 pin main-c045ede.

## What goes in
Each item is its own commit on this branch. The sort tag says which group a changed self-check result from that item falls in:
- **(a)** expected from a named rule fix;
- **(b)** expected from an upstream change;
- **(c)** unexplained.

| # | Change | Where it comes from | Kind | Self-check results it is EXPECTED to change |
|---|---|---|---|---|
| 1 | **Growl to 0.** An attack cut to 0 by an attacker-side effect (Growl's and Teary Attack's carried cuts, Intimidating Fang) does 0. No Weakness and no defender-side "+X" is added. `persistent_defender_damage` mirrors it. | branch `claude/growl-zero-no-weakness` b887a9f8 (cherry-picked; its base 01e72446 has the same engine tree 70652fff). Evidence: Dustin's recording Growl_weakness_test, `rules/05` #11. Upstream #426 stays open, and our engine keeps its own version. | rule fix, (a) | Only games where a cut card is in play and an attack of 30 or less, after the attacker's own boosts, goes into a weak Active (or meets a defender-side +X). The cut cards in committed lists: **Bonsly B3 078** (t-lucario, research/lucario, the gauntlet lists v-lucario_2, v-lucario_swap1, v-lucario_swap2, g-mega_altaria_greninja, census c-mega_lucario) and Togepi A4 078 (one pause-game list). **Possible:** new17 pairings 21 and 22 (g-mega_altaria_greninja v t-hydreigon and v t-weezing) for k3, kp3 and km3; floor-page rows against t-lucario (decks 14 and 10); the kx3 poolmeta digest 31d638dbc818b0fa (t-lucario and research/lucario are in its pool). **Predicted unchanged** (a reading, not proven): the 28-cell research tables (research altaria's Psychic attacks are 40 or more; Bonsly has no Weakness), the km3 self-check 81b572198c04d5d1, the CLI, goldfish and run_screen. |
| 2 | **#385.** "Put this Pokémon from your hand onto your Bench" Abilities (Miraidon ex, Koraidon ex, Roaring Moon, Poltchageist) only on the owner's own turn: not in setup, not for the player off turn, and not through Team Rocket's Boss. | upstream 512fd56a (merged ed5a8253); table A row 2 in `rl/results/upstream_compare_2026-10-16/README.md` | rules repair (card text "during your turn"), (b) | None: no listed deck has these cards. Adoption needs Dustin's yes as a rules repair. |
| 3 | **#390.** Random multi-hit damage is enumerated grouped by hit counts in a fixed order (BTreeMap). This also makes a seed reproduce these attacks; today ours lists them in HashMap order. | upstream 34c6c420 (merged 5ff6f691); table A row 4. Our function is byte-identical to upstream's pre-change code. | determinism/speed, (b) | None in listed decks: the 10 "at random" multi-hit attackers (Gholdengo ex, Dragonite, Rayquaza ex, Zapdos, ...) are in no list. Probabilities are unchanged. |
| 4 | **#401, Fossil part only.** DiscardFossil was offered twice per Fossil. The ability loop now skips Fossils. | upstream e63d6289; table A row 6. Upstream's MCTS change and debug assert are NOT taken. | bug fix, (b) | None: no Fossil in any list. |
| 5 | **#344, narrow.** A deck whose Energy zone holds Dragon or Colorless is invalid; `get_color`'s bare todo!() becomes a named panic. The "empty Energy list" rejection is NOT taken, because the hidden-information templates clear the opponent's Energy on purpose. | upstream b9e7f920 and 5061431b (merged 67bc4ba2); table A row 7 | safety guard, (b) | None: all deck lists declare a legal Energy line. |
| 6 | **Upstream regression tests** (no change to the built programs): #383's tests (our own merged PR coming back), #346 Meganium, #347 Silcoon/Cascoon, #348 Coalossal. | table A row 10 | tests | None. A failing ported test is reported as (c) unless traced to a known, deliberate difference. |
| 7 | **engine/UPSTREAM.md refresh.** Drops the stale "take upstream's Helmet after #383" line and the 09e964f "missing" line. | Astra's handoff, `rl/results/upstream_and_cliff_review_2026-10-16/HANDOFF.md` | doc (engine/ tree id only) | None. |

`engine/src/players/`, `Cargo.toml` and `Cargo.lock` stay unchanged. km3, k3, kp3 and the other bots run as at the Oct 12 pin.

## Deferred: listed, not in this candidate
| Item | Why deferred |
|---|---|
| B4b card data (438 cards) + #395 trainer lookup by effect text + our id-keyed follow-ups (Iris/Haxorus ids, coin-plan id lists, Victini caveat) | The largest item. Dustin's Oct 15 decision was "Wait until there's a Garchomp list to test ... then do the switch", and no Mega Garchomp list is on main. The C1 set (Oct 28) brings another data refresh, so one data pin can carry both. claude/mega-garchomp is superseded by it; keep its test file for that pin. |
| #394, a cap of 100 actions per turn | A behaviour change, not a rules repair (Astra). Our engine counts more steps per turn, so the per-turn maximum must be logged first. It also adds a State field (Hash/Eq, State JSON). |
| #386 / #388, a crash when a knockout empties the Active while an EndTurn is queued | Unclear: upstream replaced #386 with #388's flag on Oct 17. The #388 form changes how Giratina ex's Broken-Space Bellow reaches EndTurn, which the bots read (brew-10). The crash (Kiawe + Electromagnetic Wall) was never reproduced in ours. |
| #368, shuffle the Tool in with "this Pokémon and all attached cards" | Needs a new action variant across bot and observation code. The basis is card text only. |
| #374, a type granted by an Ability counts for "if the opponent's Active is a [X] Pokémon" | Its bot twin is in players/value_functions.rs, kept unchanged at pins. The engine half alone would make the engine and the bot disagree. No list reaches it. |
| #343 Dragonair test | It encodes upstream's missing Dragon check and must be rewritten first. |
| #382 replay viewer | Large (59 files), changes the executable, needs Node. Dustin's choice later. |
| #367 / #418, Rocky Helmet reflects a delayed counterattack (merged upstream Oct 17, after the comparison) | A NEW difference between the two engines: Mega Sableye ex's Cursed Jewel against Rocky Helmet holders (brews 07/09). A rules call for Dustin. |
| A hit back counts as attack damage for the attacker's own cards (rules/09 open item); Prickly Powder v Rough Skin; the bots' block-coin and Junk Spark pricing | Need Dustin's word (the first), are large (the second), or change bot code (the third). |
| #392 forecast cap, perf_watch, #336 Guts refactor, #419 test moves, #401's MCTS half | Do-not-take (table A's list). |

## The self-checks (old v new)
**The old side.** The old pin's recorded games are the reference:
- `rl/results/engine_switch_rules2_2026-10/08a9b3a_*`, played by exactly the pinned programs (copied, never rebuilt).
- Its inputs still match main (34/35, the manifest aside, 65/65 and 16/16).
- The old pin is also re-run on a small sample, to show it still runs and reproduces: step 10 (the CLI, goldfish --coverage, run_screen), the km3 self-check on the slow-report pin's program, and the 1,120-game kd3 table.

**The new side** (the candidate's own build). Each run replays a reference's exact recorded command (its `.run` file) and is compared with `switch_check.py same`, on every recorded field:
1. The engine test suite: the Growl branch passed 2,106; add the ported tests.
2. The km3 self-check: must print 81b572198c04d5d1.
3. legality_scan:
   - k3, kp3 and km3 on the 28 research cells (14,000 games each);
   - the 17 new cells (8,500 games each);
   - the floor rows of steps 7c and 7c2 (km3, 3,360 games).
4. Step 10: CLI 5×240, goldfish --coverage, run_screen.
5. If the night allows: kog3, kq3, kpr3 and kd3 on the 28 cells; kta3 dev and fresh; km3's coverage rows (B2e, Scizor, the second lists); and the kx3 poolmeta self-check, with kx3's files overlaid on the candidate.

**Sorting.** Every changed game goes in exactly one group:
- **(a)** the first difference has a cut card in play and the Growl rule applies there;
- **(b)** the game also differs on a build of the candidate WITHOUT the Growl commit (U, built only if needed);
- **(c)** anything else, listed plainly.

## How it runs
- Heavy work runs at night only (Dustin, Oct 20): 02:00-13:00Z. A keeper freezes the job's own process group at 12:55Z and thaws it at 02:00Z.
- Builds: CARGO_BUILD_JOBS 2, nice 19, ionice -c3, one cargo at a time, a fresh target directory on the WSL disk.
- Disk: C: had 70 GB free (the floor is 15).
- The candidate's tested programs are kept, with their sha256, until an adoption copies them.
