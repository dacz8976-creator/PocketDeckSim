# Engine switch plan: the second rules switch, the round-2 package (for Dustin's decision)

> **Unparked Oct 7, scheduled after the combined run** (Dustin's decision on Astra's review, relayed by the coordinator; `rl/RUN5.md` (E), 2bfb1b73). Section 0 below is the Oct 8 update: the scope now has a third part, Cursed Jewel's Weakness. Preparation is read-only while the combined run holds the laptop (pre-registered 143e2b51, expected to end Saturday night or Sunday, Oct 10-11). Sections 1-9 are the Oct 2 draft. Where section 0 differs, section 0 wins. The questions in section 9 still need Dustin's answers at the go.
>
> *History: parked Oct 2 (Dustin's direction, RUN5 "Where things stand"), when the work turned to the planning pilot.*
>
> **Oct 9 status** (the package for Dustin is `RELEASE_PACKAGE.md`):
> - **Done:**
>   - P2 with its off-switch and gates, and P3, the seven Fossil places (question 2a);
>   - the suite at the final engine commit **140c0be2** (tree 8d71f693), 2,072 passed and 0 failed;
>   - the inventory rerun (i): brews 07 and 09 only;
>   - step 8b on the cloud: 25 of 480 deals changed, **TRACE LOAD 0** (precondition d; `early_warning_8b/` on `claude/coin-prevention-round2` 63c28e6e);
>   - the probe's P2 check (RETURN).
> - **Open, sent to the cloud by the coordinator (Oct 9):**
>   - **P1** (`card_validation.rs`:102 at 140c0be2 still says "regardless of who played the Stadium");
>   - **(a)** the probe's round-2 conditions;
>   - **(b)** the shorter-game case, round 2's counter names in `validate_v2.py`, and the synthetic tests;
>   - **(e)** one revert switch per gate.
> - **Also sent to the cloud:** Bounded Field doubles a hit back's Weakness (×2), as its text reads. The test `bounded_field_keeps_the_hit_back_extra_at_20` is inverted, and the off switch stays (the coordinator, Oct 9).
> - **The Opus cloud only builds.**
> - **Readers for (c) and (f), on the final engine commit:**
>   - reader one: the laptop session's read-only Opus subagent;
>   - reader two: Sonnet, local, read-only, with no cargo.
> - **Dustin's answers to the package (Oct 9, about 4:50 pm Central): "1-3 sure."** So: (1) go, "update if everything passes",
>   with the two stricter checks; (2) the scope as recommended; (3) the new reference games as recommended. **(4) the laptop,
>   over the weekend** (Oct 9, about 5:15 pm Central, after the laptop-or-cloud comparison: "Alright it is fine to use the laptop over
>   the weekend"). He doesn't need it until Monday morning, Oct 12, so the sittings may run without a break from the combined run's
>   end. The school-morning rule applies on Monday: no new game after 5:15 am Central; a step still going pauses cleanly and resumes
>   Monday evening. The pin still waits for his word on any judgment call.
> - **Open rules question answered (Oct 9, Dustin's recording 20261009_223237000):** a hit back counts as attack damage for the
>   attacker's Heavy Helmet (Bristling Spikes' 30 cut to 10). The engine applies no cut, before or after this switch. It stays
>   **outside this switch's scope** (Dustin approved the scope without it; no list we play reaches it). It goes to the next rules
>   round, with the other cards by their own wording (`rules/09`, open bugs). It goes into this switch only if Dustin asks for it.
> - **The runners (main a5f2e7e5; the coordinator's decisions on six points, Oct 9 evening):**
>   1. **A changed game where no counter fired** passes only after 8c. 8c's probe must show the new rule inside the search at
>      the first differing move or its cause tick, and the pin counts the game as traced. Anything 8c can't show is
>      unexplained and stops.
>   2. **7c's deck 10 v t-weezing watch row** is named as allowed to change, under the same explanation rule (every changed game
>      shows Will acting). It goes on the "expected to change" list reported to Dustin, since the package named only the floor row.
>   3. **Step 4's allowed list at P** is approved at 26 files as listed in `allowed_engine_files.tsv`, on one condition: every file
>      on it is covered by both readers' equivalence reading. A file neither reader covered is read before any start. The mapping
>      is recorded in this folder before the TO FINALIZE marker comes off.
>   4. **floor.py** is accepted with the pinned-diff check (only the ATTACKERS table may differ).
>   5. **Step 8b** is 2,800 games, with brew-07/09 v t-altaria on the 23,100,000,000 block. The laptop's rows must equal the
>      cloud's.
>   6. **ALLOW_DAYTIME=auto**: Dustin's word covers Saturday and Sunday, and Monday's school-morning rule still applies.
> - **Oct 10: the final P is c7a25df4** (engine tree 70652fff). It is 31616338 plus the F1 fix: the cloud's f601abcb tests
>   first, then c7a25df4. G2's queued-hit promotion arm now also floors the promotion when the hit's own attacker has left the
>   Active Spot, the case reader one found. I re-read the hunk: it matches the `ApplyDamage` arm, and with G2 off nothing changes.
>   The suite at P passes 2,103 with 0 failed (fc6307c0). The c-magnezone card check passes 15 of 15 (232622de).
>   `trace_load.txt` gives the cloud's TRACE LOAD 0 (19a20e1a). Every data file is final except `allowed_engine_files.tsv`,
>   whose marker waits for reader two's file mapping (decision 3 above).
> - **Precondition (a)'s open test is closed** (the laptop session's reading, Oct 10; the cloud's 43ccdd1d,
>   `round2_readiness_2026-10-02/open_test_gate_R/`). As worded, "free exactly where gate_R > 0" holds in 540 of 1,126 games. The
>   two sides measure different things:
>   - the probe's `free` asks whether the *shortest* queued coin path is pure;
>   - R's gate counts *any* pure queued coin-target frame in the search.
>
>   When the probe walks past queued frames and uses R's own frame definition, it finds the gate in 1,126 of 1,126 games and in
>   none of the 279 controls. Its `queued` and `free` verdicts are unchanged in all 1,405 games. The test checks that the probe
>   sees what the bots' search sees, and the refined reading shows exactly that.
>
>   **Correction (reader two, Oct 10):** an earlier version of this note said 8c never reads `free`. It does, in one case:
>   `tightened_rule.py`:249 reads `free` when the condition is found at ply 3. There, a pure frame the probe misses makes the
>   game a JUDGMENT for Dustin, never "explained". So the as-worded miss can only send a game to Dustin, never pass one. No call
>   is needed now. The official probe stays as pinned in `tools_8c.tsv`.
> - **Reader two (Sonnet, sonnet/switch2-reader2 6cd65dac, integrated here):**
>   - **(f): equivalent.** One note, C1: F1's new arm also reaches the official engine's `ApplyQueuedAttackDamage` frames. No
>     producer in today's card database leaves one pending across a Knock Out; the exposing input is named in the file.
>   - **The second reads don't all match PLAN's wording.** These open items are for 8c (the revert-check driver), not sittings
>     1-2:
>     - the probe's self-test, P2 checks, 8b ticks and gate runs were made at 31616338, not P: rerun them at P;
>     - `control_clean` (negative controls) doesn't require round 2's kinds or trapleaf to be absent;
>     - the revert check on real games ran for G1+G2, P2 and all switches off only, never G3-G8 alone;
>     - there is no revert evidence for F1's G2 arm.
>   - Its file mapping covers all 26 files, so `allowed_engine_files.tsv` is final.
>   - **Closed, Oct 10:**
>     - **The remake at P.** The cloud's 04f2b6f7 remade the probe's self-test, the P2 checks, the 8b ticks and the gate run at
>       c7a25df4, and every result is unchanged. On the 8b deals, G1+G2 off returns every queued-kind change to the official
>       engine (km3 11 of 13, k3 7 of 12), and P2 off returns every RETURN change (km3 2, k3 5). Every other single gate leaves
>       them as P plays them, and no deal plays as neither engine.
>     - **control_clean = nothing_found:** Sonnet's 8c tools at main 486e146f, pinned in `tools_8c.tsv` at b29480f6.
>     - **F1's revert evidence.** The cloud's 1f995293 traced the test's play on the official engine and at c7a25df4 with G1+G2
>       off, and the two traces are identical byte for byte (promotion, then the second punch, 120 on seeds 0-4). Before the
>       fix, the split test shows the off call passing and the on call failing.
>   - **The per-gate revert check on 8c's own games** is `tools_8c/revert_8c.py` (Sonnet), run in 8c. It runs every game's
>     gates plus all switches off, and a root holding a pending continuation goes to Dustin.
> - **Shot List (Dustin's cleanup, Oct 9):** rows 23-33 came off the list. The four Cursed Jewel readings (rows 30-33) now rest on the
>   card text and their tests alone; the hit-back sub-cases stay in `P2_EVIDENCE_sonnet.md`. One row is kept: the hit-back against
>   Heavy Helmet (was row 22, now the list's only row). The old rows are in `rules/_research_notes/shot_list_archive_2026-10-09.json`.
> - **The cloud, 21:45 UTC:** P1 and Bounded Field ×2 done on `claude/coin-prevention-round2` (b8a8621a, b0dc4844; the suite at
>   b0dc4844, 2,073 passed and 0 failed, 5ec11518). Now (b), then (a) and (e). The readings stay with the two readers above
>   (the cloud's item 3 dropped by the coordinator's amendment).
> - **Recorded, not acted on:**
>   - the hit back as attack damage beyond Weakness (Sonnet's `P2_EVIDENCE_sonnet.md`, shot-list rows 22-29);
>   - Hala's own-turn risk;
>   - the four P2 readings as defaults (shot-list rows 30-33).

## 0. The Oct 8 update (the laptop; read-only preparation)

**Scope: three parts.**
1. **The round-2 coin package**, as in section 2: P = 20e2651, or the cloud's later engine commit (re-fetch first; the branch tip `origin/claude/coin-prevention-round2` is still 57c65860, Oct 2 19:04 UTC).
2. **The card-text job and its follow-up**, as in section 2. These include Trap Territory (two Ariados: deck 12 and h-whimsicott), Will, Victory Star, Guts, Perish Body, Luxury Coin and the Fossil lock.
3. **New: return damage set up by an attack takes Weakness** (`rules/02_damage_knockouts_points.md` §2; RUN5, Oct 6).
   - Five attacks read "During your opponent's next turn, if this Pokémon is damaged by an attack, do X damage to the Attacking Pokémon":
     - Mega Sableye ex's Cursed Jewel 40 (B3b 041/081/088);
     - Alolan Sandslash's Spike Armor 40 (A3 039);
     - Togedemaru's Bristling Spikes 30 (A3b 048, P-A 090);
     - Chesnaught's Needle Lariat 80 (B2 010);
     - Turtonator's Shell Trap 20 (B1 047).
   - The hit back takes +20 when the Attacking Pokémon is weak to the defender's type.
   - **Tools and Abilities stay flat**: Rocky Helmet's 20; Iron Jugulis's Automated Combat and the Druddigon family. The engine already does that.
   - Evidence:
     - 183108 @308 and @386: Cursed Jewel did 60 to a Darkness-weak Houndstone, twice;
     - 215749 @99 and @161: Rocky Helmet did a flat 20;
     - 20261006_220700000: Automated Combat did a flat 20 five times to Darkness-weak attackers;
     - Dustin, Oct 6: "It is from an attack the return damage is done, not from an ability."
   - **The engine today:** `handle_attack_retaliation` (`apply_action_helpers.rs`:614-633) adds no Weakness to any return damage. **No code for this part exists yet.**

**New and changed preconditions** (section 4's table gains (h) and (i); the rest stand):
- **(h) The Cursed Jewel change**, built by the cloud, tests first, as its own engine commit on top of P (call it P2). The tests:
  - each of the five attacks against a weak and a not-weak attacker, including a hit back that Knocks the attacker Out;
  - Rocky Helmet stays flat;
  - an Ability's return damage stays flat (Automated Combat and Rough Skin);
  - a Tool and an attack's return damage on the same defender, each judged by its own rule.
  - The suite at P2.
  - Step 4's allowed file list then takes P2's files. `players/` stays unchanged: the bots' look-ahead runs the engine, so it sees the new damage without a pricing change. Say so in P2's README.
- **(c) gains** an exact counter for "an attack's return damage took Weakness" and an off-gate counter for the rewritten retaliation lines running and giving the old answer. Both are proven on constructed boards, since no table list holds the five attacks.
- **(f) gains** `handle_attack_retaliation` (and any caller that P2 changes) for the two equivalence readers. It runs on every attack into a defender with any retaliation.
- **(i) The affected-game inventory, rerun.** The cloud reruns its readiness inventory (`round2_readiness_2026-10-02/`) with the five attacks' ids added, on main at the go, and names every recorded set that holds them.
  - A first look by the laptop (Oct 8, a scan of all 135 committed deck lists by set and number) found exactly two lists:
    - `decks/brews/brew-07-hoopa-darkrai-sableye.txt` (1 Mega Sableye ex);
    - `decks/brews/brew-09-sableye-obstagoon.txt` (2 Mega Sableye ex).
  - None of the frozen k3/kp3 table lists, the identity sets' lists, km3's coverage and research lists, the 8 panel lists, the kx3 pools, Dustin's 15 decks or the drafts holds one of the five.
  - So the new part can change only games with brew 07 or 09, and only when an attacker weak to Darkness hits their Mega Sableye ex in the turn after Cursed Jewel.

**What it changes in recorded games** (adds to section 3's table):

| Recorded set | Expected | What happens |
|---|---|---|
| Every identity set and the frozen table | **0** from the new part | As in section 3: a change is a stop. |
| brew 07's and brew 09's floor pages (`floor_brews_2026-09-28/`, `floor_dustin_2026-09-30/`, Sept 28 and 30 engines) | **can change** (rows against Darkness-weak panel attackers) | After the pin, step 15 gains their two new pages (2 × 1,920 games, under 30 minutes). Until then **their conclusions are provisional** (Dustin, Oct 7). |
| Any screen, CLI or goldfish row with brew 07 or 09 (the inventory names them) | can change | Named in the stop rule's expected rows, judged by the exact counter (their floor games have no watch build: section 3's limit). |

**Other things that moved since Oct 2:**
- **The laptop's schedule:** the school-morning rule (RUN5: no new game after 5:15 am Central on a school day, stopped by 6:30, pushed by 7:00) replaces section 8's "away hours". Friday Oct 9 is a school day. The sittings go on nights and weekends after the combined run, and Dustin names the nights (question 4).
- **The laptop's other work:** the combined run, then its reading. The cloud's draft-A-wallace slow report runs on the cloud and doesn't touch the laptop.
- **Not affected:** the combined run and every kx3 result so far use the official engine (main-8626a35). No development deck, panel list or kx3 pool list holds the five attacks, so the new part changes none of them. The round-2 package's Trap Territory and Will rows are as section 3 says.
- **Section 8's dates** (the earliest sitting "the night of Oct 3") are history. The new earliest is the night after the combined run ends and preconditions (a)-(i) are met.

Checked Oct 2 at origin/main 64e6d87 and rechecked at **26342a7** (its three later commits add draft A's Wallace list and the floor drafts' addendum; `engine/` is still the pinned tree 38af8b0, the same as main-8626a35's). The cloud's branch `origin/claude/coin-prevention-round2`, fetched, is at tip **57c6586** (19:04 UTC; the first draft read da08620). The package's engine is **20e2651** (`engine/` tree f95925c). Every later commit on the branch touches only `rl/results/` or merges main. Drafted by a planning workflow (three readers and one writer, reading only), then corrected after two reviews (accuracy and clarity). Nothing was built or played for this plan.

This plan follows the last rules switch, `../engine_switch_rules_2026-10/PLAN.md` (called "the last plan" below), and its README. That switch's tooling exists, so this plan points to it rather than explaining it again.

## 1. In one paragraph

This switch makes the engine follow the plain card text in the cases the last switch left open (your Oct 1 rule). The cloud built a package of fixes, and Sonnet's second read found it ready, with eight notes and none blocking. It adds three things:
- seven more attacks let Meowth, Togekiss, Bastiodon and Hisuian Goodra flip their coin, Gyarados's Wild Swing among them;
- Will now helps a Confused attacker and an attacker under a "flip or the attack doesn't happen" coin, and Victory Star works after that coin's heads;
- two Ariados now add 2 to the Retreat Cost, plus five smaller text fixes.

Unlike the last switch, **some recorded games are expected to change.** Your deck 12 and the B2e Whimsicott list each hold two Ariados. So 16 of km3's 96 B2e coverage pairings (8,000 games) should move, and so should deck 12's floor page. Deck 10's floor page can move in one row (v t-weezing, where Will now works for a Confused attacker). No table, scoreboard or identity game should change.

Before the laptop plays anything, five checks must be ready. They are how we tell a game that changed for the right reason from a fault:
- a probe that sees what the bots see when they look ahead (coin_probe v2). The cloud built its move counting today; it still has to learn round 2's new cases;
- the sorting script's fix for a game that is one move longer or shorter. The cloud did the "longer" case today; the rest is still to do;
- a second read of the cloud's new tallies (their test run passed today: 120 of 120 games had the same moves);
- the package traced on sample games with the last switch's tools (step 8c);
- the revert check: turn one fix off, and the old move must come back.

Then the laptop plays about **336,000 games in two sittings**: about 7 hours at the pace of Oct 1-2, about 11½ at most. The traces add about 1-2 hours, and the pin and the new pages add under 1 hour. Each of these stops everything and comes to you first: a changed game that isn't explained, or any change outside the named rows.

In all: about 353,000 games and about 8-10 laptop hours (14 at most), over two or three nights. The preconditions are the cloud's and Sonnet's work; apart from Sonnet's tool builds and checks, they use no laptop time.

You decide (section 9 gives one recommendation each):
- the go, including the stricter check for changed games (question 1);
- scope: fix the other seven Fossil spots now (2a), and leave the bots' Will pricing alone (2c);
- accepting the 16 new B2e rows, what happens to km's mixed B2e table, and the new floor pages (3);
- the nights (4), and the order against other work (5).

**Words used here.**
- *Identity replay:* recorded games replayed on the new engine. They must come out move for move the same.
- *Look-ahead:* the bots try moves a few steps ahead before choosing; a *ply* is one step of that.
- *Tally (counter):* the watch build's count of each time a rewritten rule acts. An *off-gate* tally counts the rewritten lines running and giving the old answer.
- *The classifier:* the script that sorts each changed game: the new rule acted on the board, the bots saw it in look-ahead, or unexplained.
- *Block coin:* "flip, and on tails the attack doesn't happen" (Mirror Shot).
- *P:* the package's engine commit. *P1:* the Gholdengo caveat text fix.

## 2. What the switch is

**The engine:** today's official engine (main-8626a35) plus the package, taken **by commit, not by branch head**. P is 20e2651, or the cloud's later engine commit if fix P1 (or question 2a) lands first. `git diff 8626a35 20e2651 -- engine/` (the same at the tip 57c6586) is 9 source files and 8 test files. Nothing in `engine/src/players/`, `Cargo.lock` or `Cargo.toml` changes (checked). The suite: 2,039 passed and 0 failed at 3090abb (the cloud's `suite_followup.log`; README line 125 on the branch). Sonnet's own re-run is still held.

What changes, by card. Card texts are from `lib/card.py`; line numbers are at the tip, and "aaa" is `apply_attack_action.rs`.
- **The four coin Abilities.** Meowth's Carefree Steps (B2 124/204), Togekiss's Celestial Blessing (A4 080), Bastiodon's Guarded Grill (A2 114, −100) and Hisuian Goodra's Securely Sheltered (B3b 050, −80) all read "If any damage is done to this Pokémon by attacks, flip a coin".
  - Seven more attacks now trigger the coin when their damage lands on one of them:
    - Wild Swing (Gyarados A4 045/215), with or without its discard;
    - Wellspring Dance (B2 048);
    - Tornado Shot (B3 051);
    - Double Splash (B1a 019) and Triple Bombardment (B1a 020/078/084);
    - Mischievous Ring (B4 077), after its Tool shuffle;
    - Litter (A4a 018);
    - Mega Kangaskhan ex's second punch (B2 127/189/202, B4 231). It has a new arm in `state/mod.rs`:1428 so the promotion still comes before the punch. Its gate is looser: any of the opponent's Pokémon with a coin Ability.

    The gate is `coin_gated_choice` (aaa:365). Every other choice stays a plain `ApplyDamage`.
  - Any other attack's queued plain hit now flips too (`forecast_apply_damage`, `apply_action.rs`:782). That includes a copied Chase Order or Wild Swing (Ditto) and the opponent's Active hit by an own-Bench choice.
  - They now also protect against your own attack's damage to your own Pokémon, for example Earthquake on your own Benched Meowth (aaa:255, `attack_outcome.rs`:707, `hooks/core.rs`:2062).
- **Will** (A4 156: "...for the effect of an attack, Ability, or Trainer card... the first coin flip will definitely be heads"):
  - **With a Confused attacker,** Will waits through the Confusion coin and makes the attack's own first coin heads, and Victory Star is still offered (`attack_outcome.rs`:627, before the Confusion gate at aaa:186-196).
  - **With a block coin** (for example Magnezone B1a 026's Mirror Shot: "your opponent flips a coin. If tails, that attack doesn't happen"), Will makes the block coin heads, and the attack's own coins stay fair (`attack_outcome.rs`:678, aaa:204-208).
- **Victini** (Victory Star, B3 025 / P-B 049): after a block coin's heads, it is now offered on the attack's own coins; before, nothing was offered. Its caveat text is rewritten (`card_validation.rs`:97-98).
- **Ariados** (Trap Territory, B1a 006: "Your opponent's Active Pokémon's Retreat Cost is 1 more"): each Ariados now adds 1 (`hooks/retreat.rs`:256). This moves retreats, Heavy Helmet, and Grass Knot (Whimsicott ex B1 016: "30 more damage for each Energy in your opponent's Active Pokémon's Retreat Cost").
- **Guts** (Ursaluna B3b 058, Conkeldurr A3 096) now flips for your own attack's damage too (aaa:449, `attack_outcome.rs`:780).
- **Perish Body** (Galarian Cursola A4a 035) now flips for an attack's plain queued hit that would Knock it Out (`apply_action.rs`:854).
- **Luxury Coin** (Gholdengo B4a 051) is no longer offered on the opponent's Stadium (`trainer_coin_plan.rs`:44).
- **A Fossil** can't be played under an Item lock (`move_generation_trainer.rs`:67), and Tools still can. Both are now settled by the cards: `rules/01`:19 for Fossils and `rules/04`:102 for Tools (Oct 2).
  - Seven other places still treat a Fossil as not an Item. The card settles it, so the plan recommends fixing them in this switch (question 2a). Only the timing is open: if the fix isn't ready when the rest is, the switch ships without it and it is recorded in `rules/09`.
- **Five old tests are removed:** three pins of old behaviour, the Wild Swing pin and the Luxury Coin pin. No other test's expected value changed (reader 1).

**The Oct 1 recordings' open items are all covered** on their plain reading (`../rules_recordings_2026-10-01/READOUT.md` §4, lines 329-334), so none is an open scope question:
- Victory Star with Confusion and a pending Will: Will item 1, test `b4a_attack_batch2_test.rs`:456 and :502. The reroll stays a fresh flip that Will doesn't touch (your Oct 1 word; test :456).
- Victory Star with a block coin: test :574.
- Will wasted on a Confused attacker: Will item 1.
- Two Trap Territories counted once: tests `legacy_ability_logic_test.rs`:634 and :661.
- The READOUT's case 4 (the copied Chase Order, the own-Bench form and the six other sites) is covered too.

**Fixed before the build (P1, the cloud, text only):** Gholdengo's caveat at `card_validation.rs`:102 still says Luxury Coin works "regardless of who played the Stadium". The code no longer does that (reader 1, finding B). No list holds Gholdengo, so no page prints it.

**Left out unless you say otherwise:**
- The bots still price a block coin at 50/50 even when Will makes it heads (`players/value_functions.rs`:1976 and 2011, reader 1). `players/` stays unchanged, and no list reaches it (question 2c).
- The B4b id-keyed items (the last README's backlog).

## 3. What it changes in recorded games, and the cost

**Expected to change: about 10,000 of the roughly 280,000 recorded games, all through two cards.** The two cards are Ariados (two in play) and Will (with a Confused Xatu).

This comes from the cloud's inventory (`round2_readiness_2026-10-02/inventory_output.txt` on the branch, at main 7c1b62f) and two independent scans that agree with it: Sonnet's `SECOND_READ_sonnet.md` and reader 2's scan by card id and text at main 9e139e6. No list in a replayed set holds a coin Ability (the carriers apart), a block-coin attacker, a copier, a Fossil, Gholdengo, Guts or Galarian Cursola. Only two kt census lists hold the block coin or a Fossil: `c-magnezone_ex_magnezone.txt` (Mirror Shot; step 8b uses it) and `c-dragonair_mega_rayquaza_ex.txt` (Skull Fossil; in kta's clause-(d) Rayquaza tables). No replayed set reaches them, and no research opponent holds a card that reads "Item card".

**Checked against the cloud's readiness README** (`round2_readiness_2026-10-02/README.md` §1, branch head 57c65860, fetched again Oct 2; "readiness" in the table). It agrees with this section: table 0 of 28, new 17 cells 0 of 17, step 7c's 32 pairings 0, B2e 16 of 96, and the floor pages to re-run are deck 12 (all 8 rows) and deck 10 (one row). It also names two things this section didn't list. Neither adds a changed baseline game or a game to play, so the counts and costs below stand:
- **Carriers, 1 of 36:** l-sharpedo v meowth_carefree (Wild Swing), one of the last switch's 8b rows (80 games a build). It sits in the step 8/8b row below, which isn't a baseline and isn't in the 280,000. The other 35 carrier pairings can't change through the package.
- **The screen's 60 lists, 11 pairings over 4 lists:** deck 12's 8, deck 10 v t-weezing, and brew-01 and brew-04 v t-weezing (Will with a Confused attacker). brew-01 and brew-04 have no floor page on record, and steps 10 and 15 replay only brew-06, 06b and deck 14, so no recorded game this plan replays holds them. Step 8's Will rows (deck 10, brew-01 and brew-04 v t-weezing) already play them new.

| Recorded set | Games | Expected | What happens |
|---|---:|---|---|
| k3/kp3 frozen table, 45 cells | 45,000 | **0** (readiness: 0 of 28, 0 of 17) | Identity replay (step 7). A change would come only from a fault in code every game runs, and it stops the switch. |
| Every other pilot's identity sets (kta3 fresh and development, km3, kog3, kq3, kpr3, kd3) | 106,240 | **0** | Identity replay; nothing re-registered. |
| km3 coverage, B2e: h-whimsicott (pairings 32-39) and deck 12 (80-87) v the 8 panel lists | 8,000 | **expected to change** (readiness: 16 of 96) | Each changed game must pass the mechanic check. The replay then replaces km3's B2e reference for those 16 rows (question 3a). |
| km3 coverage, the other 80 B2e pairings, Scizor and second lists | 58,500 | **0** | Identity, as on Oct 1. |
| Your floor page, deck 12 (`floor_dustin_2026-09-30/`, Sept 30 engine) | 1,920 | **expected to change** (all 8 rows; readiness: 8 of 8) | A new page after the pin. Today it **clears** (602 of 1,920, 31.4%; 419 clears). Stronger Grass Knot makes a drop unlikely. |
| Your floor page, deck 10 | 1,920 | 7 rows 0; the t-weezing row **can** change (240 games, rarely; readiness: 1 of 8, v t-weezing) | Replayed in step 7c. The 7 rows must be equal. A new page only if the t-weezing row differs. Today it **fails** (324 of 1,920; t-weezing 8/240). The t-weezing row would need 26 more wins (8 to 34 of 240) to reach borderline (350); not expected. |
| Draft D's three pages (`floor_drafts_2026-10-02/`). The root page and `draft-D_victini-passive/` were played on D's first list (sha256 4821877f, the 9cc6667 blob); `draft-D_amended/` on today's list (31035755: changed in place at 9e139e6, one Mega Houndoom ex instead of two, plus a Copycat) | 5,760 | 0 games; Victini's caveat text changes | Step 7c replays the root page from the 9cc6667 blob and the amended page from today's list, each blob-checked. The games must be equal, and only the caveat line may differ, in the page and in the coverage file. The passive page's games are the root page's (1,920 of 1,920 equal apart from `flagged`), so it isn't replayed in 7c; its page is remade in step 15. Replaying the root page from today's file would differ for a reason unrelated to the switch, and that would be a stop. |
| The other floor pages, the floor re-check, run_screen, CLI, goldfish | about 50,000 | 0 (readiness: step 7c's 32 pairings 0) | None. The re-check, run_screen, CLI and goldfish are replayed (steps 10 and 15), and they must be equal. |
| The last switch's step 8/8b rows | 72,960 | can change (where the new paths act; readiness: 1 of 36 pairings, l-sharpedo v meowth_carefree) | They aren't a baseline. They are this switch's "old" side (below). l-sharpedo v meowth_carefree is no longer a Wild Swing control. |

**Limit, stated plainly:** floor games come from `deckgym simulate`, which has no watch build, so changed floor games can't be checked one at a time. Instead:
- deck 12's change is judged on the same pairings in B2e rows 80-87;
- deck 10's is judged in step 8's Will rows (deck 10 v t-weezing).

**How many Trap Territory games change,** estimated from the cloud's smoke run: two Ariados were in play in 11 of 40 games (deck 12 v t-lucario 8 of 20, v t-weezing 3 of 20), and nearly every change needs two in play. If that rate carries over to h-whimsicott and the B2e panel, at most about 28% (roughly 14-41%) change: up to about 2,200 of the 8,000 (1,100-3,300), and about 530 of deck 12's 1,920. Grass Knot is deck 12's main attack. The replay gives the real number.

**What it does to the frozen tables and the pilots' baselines:**
- **Expected: nothing.** If step 7 passes, scoreboard v3's files stay the frozen k3/kp3 tables with the same hashes, and every pilot's baselines stand ("re-verified at the new engine, 45 cells", as on Oct 1).
- **If any table or identity game changes, it is a stop, not a re-baseline.** It comes to you. If you accept it:
  - the 45,000 replays become the new frozen table, and the old one is kept as history;
  - every pilot's baselines are re-registered from step 7's games (no extra games);
  - kta3's "adopted, unconfirmed" status and km3's thresholds come back to you, because they were measured on the old tables.
- **km3's B2e reference** for the 16 Trap Territory rows is replaced by step 9's replay, with your word (question 3a). km's Sept 30 reading stays a reading on its own engine. Any later reading that cites those rows uses the new reference ("every reading uses baselines from the same engine").
- **History, not redone:** the Sept 26 Whimsicott card checks (`b2e_card_check_2026-09-26/card_check_arch_whimsicott.md`, `card_check_dustin_whimsicott.md`), and these recorded sets that hold B2e pairings 32-39 and 80-87. None is replayed (step 7's identity files hold no B2e games); question 3a covers km's mixed table.

  | Folder | Recorded set | Games in the 16 pairings |
  |---|---|---:|
  | `km_tables_2026-09-30` | km's own mixed B2e table, `1f6319e_mixed_b2e_km3_first` | 2,000 |
  | `km_tables_2026-09-30` | `1f6319e_laptop_id_b2e_kta3_i20` | 320 |
  | `kta_tables_2026-09-29` | `fresh_b2e`, kta3 and kog3 | 8,000 each |
  | `kta_tables_2026-09-29` | `fresh_mixed_b2e_kta3_first` | 1,000 |
  | `kt_tables_2026-09-28` | `b2e_kta3` and `mixed_b2e_kta3_first` | 8,000 each |
  | `km_build_2026-09-30/identity` | `b2e_kta3_40` and `b2e_kog3_40` | 640 each |

**The real cost:**

| Part | Games | Laptop time at Oct 1-2's pace (in brackets: at most, at 8.6 games a second) |
|---|---:|---|
| Sitting 1, steps 4-7c | about 199,000 | about 4 hours (7) including builds |
| Sitting 2, steps 8b-10 | about 137,000 | about 3 hours (4.5) |
| 8c traces, probe and revert checks (Sonnet, on the laptop's cores) | — | about 1-2 hours (an estimate; Oct 1's 3,813 games took about 35 minutes) |
| After the pin: the floor re-check, deck 12's new page, D's passive page | about 17,200 | under 1 hour |
| **Total** | **about 353,000** | **about 8-10 hours (about 14 at most), in two or three nights** |

Where the pace comes from:
- Oct 1-2's pace is `../engine_switch_rules_2026-10/timing.tsv`. Sitting 1 played 191,240 games in 3 hours 37 minutes, builds included. Sitting 2 played about 145,000 in 3 hours 18 minutes.
- The last plan's 8.6 games a second was its upper bound.
- Step 8's and 8b's "old" side reuses the last switch's recorded new-engine games (`5a18d31_8_new_*`, `5a18d31_8b_new_*`). They were played by the pinned programs on the same seeds. That saves about 24,300 games.
- The cloud and Sonnet do the preconditions. They play no laptop games, apart from Sonnet's light tool builds and checks.

## 4. Preconditions (before the build; the laptop plays nothing until each is met)

| # | Precondition | Who | Evidence |
|---|---|---|---|
| a | **coin_probe v2, counting plies the way the bots do.** It copies the search in `expectiminimax_player.rs` (606-1021), reader 3's spec:<br>• the root move is always ply 1;<br>• game over, forced turn end, pure frames and complete promotion frames are free;<br>• it crosses a forced EndTurn into the mover's next turn and stops when the opponent acts;<br>• every other offered move costs a ply, the opponent's stack choices included;<br>• an unpriced move is a leaf.<br>**DONE: the ply counting** (the cloud, 57c6586, `round2_readiness_2026-10-02/coin_probe_v2.rs`; readiness README §3, `v2_summary.txt`), on main-8626a35. Self-test: 7 checks and 3 frame checks, 0 failures. Run with tightened_rule v2 over all 3,813 hand-off games: the first difference is step 8c's in 3,813 of 3,813; exactly the 8 expected verdicts moved (the five promotion games and km3 4/106 to lookahead; the two pairing-31 games to on the board) and 3,805 stayed the same. Verdicts now: 2,416 on the board, 1,397 lookahead, none unexplained. Golden checks 2,379 of 2,379; step 8c's 12 negative controls find nothing.<br>**DONE: the node limit.** The default stays v1's 60,000 (`--node-limit` names another). A probe that stops at the limit having found nothing is run again at 600,000 (`validate_v2.py`). That was 2 games (pairing 12, game 69, both bots), both then found queued 3 plies deep in a free frame; no control needed it.<br>**Still to do:** v2 looks only for v1's two conditions, QUEUED and CUT (README §3: "everything else is v1's"; `coin_probe_v2.rs`:28-31). It must also report the ply at which round 2's conditions are priced: the plain-hit coin, the own-side coin or Guts, Will on a Confused or block-coined attacker, the Victory Star gate pause, two or more Trap Territories read, and Perish Body on a queued hit. Without them a look-ahead Trap Territory or Will game in 8b or step 9 would read UNEXPLAINED. Then build it on P, keep the 600,000-node retry, and give it a second read.<br>**Tests:** v1's self-tests A-F plus the constructed boards. On 8c's 1,405 lookahead games: QUEUED inside the search in all 1,395 coin-Ability games; queued 3 (free) in the five promotion games and queued 2 in km3 4/106; free exactly where `revert_check.tsv`'s gate_R > 0 (1,126; not yet run).<br>**Of these, done at 57c6586:** queued 3 (free) in the five promotion games and queued 2 in km3 4/106; a coin path in 1,388 of the 1,397 lookahead verdicts (the 1,395 coin-Ability games less the 7 that read on the board), and the other 9 are Victory Star games, explained by the Victory Star probe. **Still open:** the gate_R > 0 match (1,126), and boards for round 2's conditions. | the cloud (the ply counting, done); Sonnet the rest (it owns the 8c tools), unless the coordinator sends it to the cloud; an Opus subagent second-reads it | its self-test output, committed in this folder |
| b | **The classifier's prefix fix.** Copies of `tightened_rule.py`, `classify_8c.py` and `coin_lookahead.py` go in this folder:<br>• `first_difference`'s length branch (`tightened_rule.py`:53) sets k to the first tick only the longer game has, and the cause to k−1;<br>• `counter_hits` (:73) reads the turn from the rows that exist;<br>• a length difference becomes a board difference (`classify_8c.py`:162, `coin_lookahead.py`:66).<br>This replaces the last plan's line 136 ("always UNEXPLAINED").<br>**DONE for the case where the new engine's game is the longer one** (the cloud, 57c6586, `tightened_rule_v2.py`, `extra_tick_hits`; readiness README §3): k3 p31 i81 and km3 p31 i12 now read ON THE BOARD (`vs_confused_choice_offered` and `_chosen` at the extra tick), and no other verdict moved (the 3,813-game check in (a)).<br>**Still to do:** the case where the new engine's game is the shorter one, as specified above (question 1 asks your word on both); the round-2 exact counter names, keyed counters included (`{attack: [ticks]}`), since `validate_v2.py` still uses round 1's REACH names (:30-32). That is right for the Oct 1 check it ran, but the readiness README doesn't change it for round 2 (unchanged at 57c65860, the earlier reader's finding); synthetic tests (no counter, an earlier turn, the new engine shorter). | the cloud (the longer case, done); Sonnet the rest; an Opus subagent second-reads it | the test output |
| c | **Counters for the new paths.** **DONE** (the cloud, da08620 and cf3cffe; readiness README §2): da08620 gives `instrument_scan.py` the exact counters (its docstring's EXACT list: 15 names over 11 mechanics) with every firing tick recorded, and off-gate counters for each rewritten site. They cover the card-text job and its follow-up as well as the coin round: Will with a Confused attacker or a block coin, Victory Star with a block coin, Trap Territory, Luxury Coin, the Fossil lock, Guts and Perish Body. Its constructed-board probe passes 49 of 49 (`round2_readiness_2026-10-02/counter_probe_readiness_output.txt`). cf3cffe ran the smoke check (`counter_smoke/`, 6 pairings): the moves are the same plain and watch in 120 of 120 games, and the two scripts apply in either order.<br>**Still to do:** a second read by someone other than the cloud. The Will counters stayed silent in the 40 real games (no Will list attacked while Confused), so, like the block-coin, own-side, Guts, Perish Body, Gholdengo and Fossil counters, they are proven only on the probe's boards. | the cloud (done); Sonnet or an Opus subagent (read) | the smoke output; the read |
| d | **The package traced with the 8c tools** (Sonnet's note 1, made worse by reader 1's finding C). **Still open:** the readiness work checked the tools on the Oct 1 hand-off only, not on games of P. The cloud's "No game changed in lookahead alone" (README line 245 on the branch) used the reading the tightened rule replaced. It ran at bfe8aeb (engine 29e126a, the seven sites only) against R 1abdbe8, not the pinned 38af8b0. It never ran the card-text job or the follow-up.<br>So the cloud plays step 8b's rows (below) on its build of P against main-8626a35's engine and classifies them with (a) and (b). That gives the trace load. | the cloud; Sonnet reads | `trace_load.txt` here: `TRACE LOAD <n> <commit>` |
| e | **The revert check, as a standard step** for every lookahead-kind game. It is the confirming half: it shows the package caused the different choice (`trace_8c_sonnet/REVERT_CHECK.md`, `revert_check.py`). On this engine one switch is not enough (reader 3): a plain hit now flips too, so the check needs:<br>• a switch that empties `forecast_apply_damage`'s coin targets;<br>• one switch per gate: the seven sites, the own side, Will, the Victory Star gate, Trap Territory, Guts and Perish Body;<br>• each switch run alone and all together;<br>• each switch first shown to give the old engine's scores where its gate doesn't act. | Sonnet | the switches' self-check |
| f | **The source equivalence, written by two readers.** The refactor rule (Dustin, Sept 28; RUN5:588) applies, because the package rewrites code every game runs:<br>• `forecast_apply_damage`;<br>• the both-sides prevention and Guts scans;<br>• `modify_damage`'s cut on either side;<br>• the Retreat Cost loop;<br>• the Fossil check (and, if question 2a lands first, the seven other Fossil checks);<br>• the promotion arm;<br>• the Will check in `apply_attack_common_modifiers`;<br>• the Victory Star staging;<br>• `coin_gated_choice`'s off-gate return.<br>One reader reads the diff, the other traces every caller, as on Sept 28 and Oct 1. | Sonnet and an Opus subagent of the laptop session | `EQUIVALENCE_*.md` here |
| g | **The suite at P,** and the tests-first commits failing at their parents. This is Sonnet's held re-run. If P1 moves P, the cloud runs it at the new P. | Sonnet or the cloud | `suite.log` naming P |

The Opus subagent second-reads (a) and (b) before step 8c, or it does the equivalence reading, whichever it isn't busy with.

## 5. The procedure, step by step

Steps 1-3 of the last plan become the preconditions above. Its runners are adapted, not rewritten. Copies of `sitting1.sh`, `sitting2.sh`, `sitting1_check.py`, `sitting2_check.py`, `switch_check.py`, `checkpoint.sh`, `quiet.sh` and `pin/pin_rules.sh` go in this folder, with one Opus review for evidence and one for safety, as on Oct 1. New seeds (8b's new rows and step 8's Will rows) come from a block outside every range in START_HERE's seed table, for example 23,300,000,000 + pairing × 10,000 + i. They are added there and committed before any game.

| # | Step | Games | Reuse |
|---|---|---:|---|
| 4 | **Candidate:** merge P into main off-tree. The allowed list is exactly the 17 engine files above; if question 2a lands first, it also takes `apply_trainer_action.rs`, `shared_mutations.rs`, `effect_mechanic_map.rs` and `effect_ability_mechanic_map.rs` (all in `engine/src/actions/`) and their tests. `players/`, `Cargo.lock` and `Cargo.toml` must be unchanged, and `engine/` must equal P's tree byte for byte. | — | as-is, new file list |
| 5 | **Plain build**, blob-checked references, hashed inputs | — | as-is |
| 6 | **Watch build:** the coin script from P's branch (da08620's version, unchanged at 57c6586) plus the Victory Star script | — | as-is, new script blob |
| 7 | **Identity for every pilot:** the same files as the last plan's step 7 | 151,240 | as-is |
| 7b | **Counters on the table** (k3 and kp3, 28 cells, watch build):<br>• every round-2 exact counter must be 0;<br>• each of `offgate_plain_attack_damage`, `offgate_by_attack` (the first round's helpers and Chase Order's discard) and `offgate_confused_attack` must be above 0 somewhere;<br>• the others are reported;<br>• watch must equal plain. | 28,000 | as-is, new counter list |
| 7c | **Your lists where rewritten lines run:**<br>• the last switch's four pages and 32 watch rows, as before (11,520);<br>• deck 10's page: its 7 rows must be equal, and the t-weezing row is reported (1,920);<br>• draft D: the root page replayed from D's first list (the 9cc6667 blob, sha256 4821877f) and the amended page from today's list (31035755), each blob-checked: every game equal, and only the Victini caveat line may differ (3,840). The passive page isn't replayed: its games are the root page's;<br>• watch rows for deck 10 and D's two lists v the panel, 60 deals, old and watch (2,880): `offgate_vs_ungated_built` must be above 0 on D. `offgate_confused_attack` is reported on deck 10 but not required there (it was silent in the smoke run's 20 deck 10 v t-weezing games); it is required only on the table (7b).<br>If deck 10 or D differs where it shouldn't, first replay that pairing on `rl/engine-2026-10-02/` to see whether the difference predates this switch. It still stops the switch. | 20,160 | adapted |
| 8b | **Early warning:**<br>• the last switch's 4 rows (old side reused);<br>• the cloud's 5 other smoke pairings (`counter_smoke/pairs.tsv`: deck 12 v t-weezing and v t-lucario, deck 10 and brew-04 v t-weezing, water_round2 v meowth_carefree);<br>• 2 block-coin rows: houndoom_victini and deck 10 v `kt_carrier_census_2026-09-26/decks/c-magnezone_ex_magnezone.txt` (Mirror Shot), after the cloud's card checks;<br>• 40 games a bot, k3 and km3, old/new/watch.<br>The laptop's rows must equal the cloud's (precondition d). | 2,320 | adapted |
| — | **The trace-load gate:** step 8 starts only with `TRACE LOAD n ≤ ~50`, or with a `DUSTIN` line | — | as-is |
| 8 | **Carriers:**<br>• the last switch's 32 pairings: new and watch, with the old side reused (48,000);<br>• **Will rows:** deck 10, brew-01 and brew-04 v t-weezing, km3 500 and k3 250, old/new/watch (6,750). | 54,750 | as-is plus the Will rows |
| 8c | **Traces:** every changed game of 8b, 8 and 9's 16 rows, through (a), (b) and (e), then hand traces for whatever the rule can't settle. The cloud's independent run is the cross-check. | — | adapted tools |
| 9 | **km3's coverage:**<br>• B2e 48,000, Scizor 4,000 and the second lists 14,500, against `km_tables_2026-09-30/1f6319e_*`;<br>• the 80 B2e pairings with no Ariados must be equal;<br>• **pairings 32-39 and 80-87 are named now as expected to change**, and their changed games go to 8c;<br>• the watch build plays those 16 pairings (8,000) for the counters. | 74,500 | adapted |
| 10 | **CLI, goldfish, screen:** equal to the recorded files (no Victini in goldfish's lists, so its coverage file is byte-equal) | about 5,040 | as-is |
| 11-14 | **The pin:** after PREPARE DONE and your word. Merge off-tree, `pin_rules.sh` with the new file list, and the programs to `rl/engine-<date>/`; main-8626a35 moves to history. The documents:<br>• `rules/09`'s open entries closed;<br>• `rules/04` §9's Victory Star lines, and its note on the two gate coins (question 2b);<br>• the stale items in Sonnet's note 8 and READOUT §4's "don't edit inside the switch";<br>• the engine README, CLAUDE.md, START_HERE's engine line and seed row, and RUN5;<br>• km3's new B2e reference for the 16 rows (question 3a). | — | as-is |
| 15 | **After the pin:**<br>• the floor's pre-use re-check (`../floor_recheck_2026-10/` runner, about 13,400 games);<br>• deck 12's new page (1,920);<br>• D's victini-passive page, remade the way it was made on Oct 2 (its copy rebuilt from `floor_copy.diff`, run through `run_copy.py` on D's first list; 1,920, since floor.py makes a page only by playing it);<br>• the new pages for deck 10 (if its row changed) and D's root and amended pages (text), taken from step 7c's replays. | about 17,200 | as-is plus pages |

**Two sittings:**
- sitting 1: steps 4-7c;
- sitting 2: 8b, the gate, 8, 9 and 10;
- then 8c, the pin and step 15.

## 6. The stop rule and the mechanic check

**Each of these stops the switch:**
- any identity mismatch in a row named equal (7, 7b, 7c's equal rows, 9's 80 pairings, Scizor and the second lists, and 10);
- a changed game anywhere outside the named rows (8b, 8, 9's pairings 32-39 and 80-87, and deck 10's t-weezing floor row). This rewords the last plan's line 150 for this switch only: a km3 difference stops, except in those named rows;
- a changed game that fails the mechanic check;
- an exact round-2 counter above 0 on the table, or a required off-gate counter at 0;
- watch not equal to plain;
- a program hash that changes mid-run.

A trace that needs a judgment call doesn't stop the replays, but the pin waits for your word on it. The manifest stays untouched, and the laptop reports to you first.

**The mechanic check** is the last plan's (lines 126-150), with three changes:
1. **The reach counters** are da08620's exact list. The supersets (`trap_territory_two_in_play`, `coin_defender_attack`, `vs_confused_attack`) never count as reach.
2. **A prefix game** (one game longer or shorter than the other) is judged like any other board difference (precondition b).
3. **"In lookahead"** needs both halves (the code gate, and v2 finding the condition inside the bots' search at the first differing tick). It also needs the revert check reproducing the old choice and scores (precondition e). A game that meets the first two but fails the revert check is a stop.

**Precedents, noted but not assumed:**
- **The condition-3 ruling** (the coordinator, Oct 1, `../engine_switch_rules_2026-10/README.md`:106). A game where only off-gate counters fired must be identical, unless a trace meets both halves. Then a repaired mechanic acted, and the game is explained. This plan carries it over only with your go (question 1).
- **Your acceptances** of Victory Star smoke game 28 (README:116) and of the 8 games the rule couldn't settle (`8c_DECISION.md`) were specific, documented exceptions for that switch. A similar game this time is a new judgment call, and it comes to you.

## 7. Who does what

| Part | Who |
|---|---|
| Routing, audit, operational calls, your questions, every cloud paste block | the Fable coordinator session |
| Done: the counters and their smoke check (da08620, cf3cffe), coin_probe v2's ply counting and the classifier's fix for a longer new game (57c6586). To do: P1, question 2a's fix if yes, the suite at P, 8b's early-warning rows classified, the 8c cross-check | the cloud (paste blocks through you) |
| coin_probe v2's round-2 conditions, the classifier's remaining cases, the revert switches, one equivalence reading, the counters' second read (or the subagent), the held suite re-run, every 8c trace | Sonnet ("Opus agents progress") |
| This plan, the adapted runners with two Opus reviews, the builds, steps 4-10, the pin, step 15; its Opus subagent does the other equivalence reading and the second reads of (a) and (b) | the laptop session |
| The go, the scope, re-baselining, the nights, any judgment call | you |

## 8. Schedule

- **The away hours on record** are only for Oct 1-2 (RUN5:413; the last plan's line 203): the laptop was away from about 7 am to 5 pm Central, and everything was committed and pushed, with main = origin/main, by 7:00 am. The other notes:
  - no class on Wednesdays (RUN5:394);
  - class on Mondays, 1-4 pm Central (Dustin, Sept 28, in the session notes; the pause pattern is `../engine_switch_2026-09-28/quiet_hours.sh`);
  - quiet hours apply only in class or travel; at home and overnight the laptop may run anything;
  - nothing is recorded for Oct 3 onward, and overnight authority is confirmed night by night (question 4).
- **The 7:00 am rule on a morning you take the laptop:** every sitting ends, commits and pushes by 7:00 am Central. The runners already carry it:
  - the deadline defaults to 11:30 UTC (6:30 am Central), with a hard stop 10 minutes later (`sitting2.sh`:106-107, :212);
  - checkpoint commits use a private index and push fast-forward only (`checkpoint.sh`).

  A sitting that can't finish stops at a step boundary, ends PAUSED, and resumes the next evening. Nothing mid-step is kept.
- **Expected:**
  - the preconditions take about a day of cloud and Sonnet time (the cloud's work today on (a)-(c) shortens it somewhat; the round-2 conditions in v2, the revert switches and the equivalence readings remain);
  - sitting 1 is about 4 hours (7 at most), and sitting 2 about 3 (4.5 at most);
  - 8c follows sitting 2;
  - the pin and step 15 come the same night if everything passes, with your word on any judgment call.

  The earliest is sitting 1 on the night of Oct 3 and the pin on Oct 4-5. Likely early next week.
- **What can move to the cloud:** the preconditions and the early-warning rows, yes. Steps 4-10 and the pin, no: the pin's evidence must come from the programs being pinned (the last plan's lines 219-228).

## 9. Questions for Dustin

1. **The switch: a conditional go, "pin if all pass"**, as on Oct 1, starting when every precondition in section 4 is met. **Recommended.**
   - "All pass" means every row named equal is equal, every tally reads as expected, and every changed game is explained. Either the new rule shows on the board at that move (its tally fires there), or the bots saw it in their look-ahead and the revert check brings the old move back.
   - Two changes from Oct 1: a game one move longer or shorter is judged like any other (last time the stricter reading sent you 2 games that were only Victory Star offers), and the revert check is now required (stricter). Both change the stop rule, so they need your word.
   - Oct 1's ruling carries over: a game where the new code ran but didn't act must come out the same, unless the trace shows the bots saw it in their look-ahead.
   - A judgment call is not a pass: it comes to you.
2. **Scope:** the package (20e2651's engine) plus the caveat fix P1. **Recommended.** What the package leaves open:
   - **a. Fossils as Items elsewhere.** The lock fix is in, but seven other places still leave Fossils out of "Item":
     - hand disruption (aaa:5523);
     - Team Rocket's Thieving Machine (`apply_trainer_action.rs`:392);
     - `item_search_outcomes` (`shared_mutations.rs`:64);
     - Junk Spark, Crackling Snap and Scavenge (`effect_mechanic_map.rs`:3429, 3600, 3671);
     - Raticate's evolve Ability (`effect_ability_mechanic_map.rs`:859).

     The card settles that a Fossil is an Item. **Recommended:** the cloud fixes all seven, tests first, before the build. No replayed list reaches a Fossil, so no game and no laptop time changes. If it lands first, step 4's allowed file list and precondition (f)'s list grow by those four files and their tests. If it isn't ready when the rest is, ship without it and record it in `rules/09`.
   - **b. The order of the Confusion coin and a block coin** needs no decision. Will skips the Confusion coin (your Oct 1 word), and a Confusion tails ends the turn, when Will lapses anyway. So the order can't change a game. (Sonnet's note 5 raised it: the engine spends Will on the block coin even in the Confusion-tails branch, aaa:204 and `apply_action.rs`:301-311, but that attack does nothing either way.) It will be noted in `rules/04` §9 at the pin, with no shot-list row.
   - **c. The bots' 50/50 price of a block coin when Will makes it heads.** **Recommended:** leave it out. Cost of leaving it: in that rare spot the bots undervalue attacking after Will. Fixing it would change the bots' code, which every recorded game depends on, for a case no list reaches.
3. **Re-baselining:**
   - **a.** Accept now that step 9's replay of B2e pairings 32-39 and 80-87 becomes km3's B2e reference for those 16 rows, once their changed games pass the mechanic check. **Recommended.** It costs no extra games. The other 80 pairings must still be equal. km's mixed B2e table (`km_tables_2026-09-30/1f6319e_mixed_b2e_km3_first`, 2,000 games in those rows) isn't replayed in this switch: a later km reading that uses those 16 rows replays them on the new engine first. **Recommended** too: nothing is spent now, and it keeps "every reading uses baselines from the same engine".
   - **b.** Don't pre-accept a change to the frozen tables or any identity set. **Recommended.** None is expected; one would mean a fault and comes to you as a stop.
   - **c.** New floor pages after the pin: deck 12's, deck 10's only if its t-weezing row changed, and D's three for the caveat text. Their changed games are judged through the same pairings' B2e and Will rows, not one by one (section 3). **Recommended.**
4. **When:**
   - **Recommended:** at home, overnight, starting the first night after the preconditions pass. Please say which nights the laptop may run unattended and which mornings you'll take it, since the 7:00 am rule applies only then.
   - About 8-10 laptop hours in all (about 14 at most), over two or three nights.
5. **The order against other work.** **Recommended:**
   - the preconditions now (cloud and Sonnet, no laptop games);
   - then the two sittings, before any new floor page for decks 10 or 12, and before A5's B4b merge trial is pinned (its identity references would move to this engine);
   - floor pages and small runs for lists without these cards don't change, so they can run in the daytime between sittings, never beside a sitting.
