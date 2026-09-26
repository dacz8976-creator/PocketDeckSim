# REGISTERED (Sept 26 evening, before any kpf code or game): kpf

**Registered after its one review (`REVIEW.md`; every fix applied).** Dustin: "Write the spec. Register before building, one review, then the 45 cells, as the plan says." The one question left to him, whether R includes kpr's amendment 5 (1981bb4), was settled the same evening: included, covered by option 2 (section 2). Dustin approved the direction on Sept 26 ("Agree with the recommendation, with two
conditions on the spec"). His two conditions are sections 3 and 4. Nothing here is built.

## 1. In plain words

- **The problem.** kp3, the adopted pilot, plays decks built on discard-cost attacks and discard-pile Energy badly.
  - The gauntlet's first run (`../gauntlet_runs_2026-09-26/`) found this.
  - Rayquaza (Dragonair / Mega Rayquaza ex) scores 22% against the panel under kp3. Its real Limitless score is 46%.
  - kp3 skips Mega Burst and Gouging Fire's Scorching Interruption on about 40% of the turns they're available, and usually doesn't attack at all instead.
  - It plays Rainbow Cave on 17% of the turns it could and uses its effect on 33%.
  - Dustin, Sept 26: the deck "relies on dragonair's ability to pull discarded energy onto dragons", and Rainbow Cave's ability should be used "as soon as you can to put energy into the discard pile".
- **Half the fix exists already.** kpr3 counts the Energy the Active will get by its next attack, so it stops thinking a discard-cost attack leaves it stranded.
  - It lifts Rayquaza to 43.7% (real 45.9).
  - Over all 45 scoreboard cells it has the lowest real error: 12.7, against kp3's 15.3 on the development half.
  - It raises Rainbow Cave use only to 28% played and 40% used, because kp gives Energy in the discard pile no value of its own.
- **kpf = kpr's projection (part R) plus a list-free value for Energy in the discard pile when the deck can pull it back (part F).**
  - It is judged on all 45 scoreboard cells under the ordinary adoption rule.
  - It is then read on the coverage decks before any verdict is final (section 7).

## 2. What kpf is

`kpf<N>` is kp<N>, the public-pricing pilot, plus two parts. Each part is behind its own flag, so it can be isolated.

- **R, projected readiness:** kpr's `projected_active_energy`, exactly as built at e09fb46, used where kpr uses it (the Active's online score and the clock's missing-Energy count, both sides, with kpr's horizons).
  - That includes all of kpr's amendments as built, including amendment 5 (1981bb4, the opponent-side horizon fix).
  - Dustin did not approve 1981bb4 when it was made (`../table_readings_2026-09-24/kpr3_paired_reading.md` §8).
  - **Settled Sept 26 evening: included, covered by option 2.** Dustin approved it on one check, "what 1981bb4 changes, in one sentence". The laptop session read the commit:
    - It changes only when each side's projection is read. The evaluating player's own Active is read through its next turn; the opponent's Active at its very next attack, from the Zone Energy of the turn actually in progress. This stops the opponent's Energy Abilities being counted twice across the turn boundary (the Suicune/Baxcalibur clock stepping from 10 to 2 in the commit's example).
    - It adds no source and no parameter: same public sources, and k, kp, kq and kd unchanged (1981bb4's message).
  - Dustin: "If it's what its name suggests — the opponent-side projection reading the right Energy Zone for the side to move … then it's inside option 2 as I approved it … my approval covers it. Record it that way and it's settled."
  - He also gave the reason for including it: the kpr3 evidence behind kpf (Rayquaza 22 → 44, the 45-cell 12.7) came from the build that contains it.
- **F, the fuel credit** (section 4).

Diagnostic codes, never adopted:
- `kpr<N>`, R only, already exists.
- `kpg<N>`, F only.

The builder confirms that neither code shadows an existing parser prefix (`players/mod.rs`), as §117's `g<N>` did.

## 3. Condition one: R is not narrowed

Dustin: "Damping a general term until one deck's cell lands is tuning to a cell, which is what the plan forbids."

- **Checked (Sept 26, laptop session, reading e09fb46's `players/value_functions.rs` 2086-2208):** R already projects only Energy an Ability can actually attach, given its conditions. For each Ability, once a turn, it checks:
  - whether that Ability was already used this turn, or switched off (through `get_in_play_ability_mechanic`);
  - where its holder sits, where the text requires it:
    - on the Active for `AttachEnergyFromZoneToYourTypedPokemon`, `AttachEnergyFromZoneToSelf`, Roar in Unison and Combust;
    - on the Bench for Dragon's Blessing;
    - no position condition for Ice Maker, whose text has none;
  - the Active's type (typed attaches, Ice Maker, Dragon's Blessing). Dragon's Blessing allows "an Energy" of any type, and `best_discard_energy_for` tries every type in the pile; its conditions match the move generator's (`move_generation_abilities.rs` 265-272);
  - whether a turn effect blocks Zone attaches;
  - whether the needed type is in the discard pile, each discarded Energy taken once;
  - whether the self-damage would knock the Active out.

  It skips Abilities that end the turn and one-off Abilities.
- **Its known limits are listed in its own doc comment and carried over unchanged:**
  - a sleeping attach still counts;
  - a `next` Energy drawn inside the search is a guess;
  - an estimate that reads the board doesn't see projected Energy;
  - a yardstick shift with mixed costs;
  - an observation hides the opponent's stack.
- **So R goes in as built. No Hydreigon-shaped coefficient.**
  - Hydreigon has no attach Ability. Its overshoot comes from R's general principle: chipping costs less when next turn's Zone attach refills.
  - It is recorded as an open cause (section 8) and left for the 45 cells to judge.
- If the review finds R projecting an Ability whose condition it doesn't check, the fix is to check the condition, in the draft, before any game. That is a principled narrowing and is allowed.

## 4. F, the fuel credit, and condition two: list-free

The credit is added to the value of the side whose discard pile holds the Energy:

> credit = K × min(E, CAP), with K = 15 and CAP = 4.

- **E** is that side's discard-pile Energy that R's projection did not already use, so nothing is counted twice.
- **The constants are §117's**, read-only in Pocket Deck Lab: `C:\Users\dacz8\Projects\Pocket Deck Lab\s117_prereg.txt`.
  - Its lines 2 and 14-15 read "Written BEFORE any g-tier game" and "15.0 × min(4, …) … fixed here, not tuned".
  - In code they are the repo engine's `value_functions.rs` 1200-1206, and 1569-1575 in kpr's tree.
  - Only the file's own text shows it came first: its timestamp is a bulk-copy time from Aug 18.
  - Context, disclosed: §117 aimed those constants at a Rayquaza-Dragonair deck, and the g tier was "dominated in probes" (f6a921a).
  - They were never fitted to any cell here, and nothing new is chosen.
- **When it counts:** only when that side can pull the Energy back.
  - **Own side (the evaluating player knows its own list):** a recovery source is in play, or is among the player's own cards not yet discarded (hand or deck). Its own list is its own information.
  - **Opponent's side (list-free, Dustin's condition two):** only when a recovery source is visible on the opponent's board, meaning either:
    - a Pokémon in play that can use such an Ability as its text allows, holder position included (a Dragonair in the Active Spot can't use Dragon's Blessing);
    - a Tool or Stadium in play with such an effect. None exists today (the review searched `lib/deckgym-database.json`); the clause covers future cards.
    - Never from their hand, deck or list, and never inferred from an archetype.
    - This keeps kp's tier-1 property (§40): no hidden information about the opponent, and no list.
- **Recovery source:** any card whose effect puts Energy from its owner's discard pile onto a Pokémon.
  - Abilities: `AttachEnergyFromDiscardToActiveTypedFromBench` (Dragon's Blessing) and `AttachEnergyFromDiscardToSelfAndDamage` (Combust).
  - Trainers: Professor Sada, Flame Patch, and every other card with such text.
  - Attacks: any that attach from the discard pile.
  - **The builder enumerates the class from `lib/card.py` card texts ("from your discard pile" together with Energy attached to a Pokémon), lists every card with its effect code in the build note, and the reviewer checks the list.** The class is defined by what a card does, never by which decks play it.
- **The class today is exactly 6 cards** (the review's search of the card database; the builder re-checks it):
  - Dragonair B4 117 (Dragon's Blessing)
  - Flareon ex A3b 009 (Combust)
  - Flame Patch B1 217
  - Professor Sada B3a 072
  - Lusamine A3a 069
  - Volkner A2 153
- **Conditions:** a source counts only Energy the effect can move, to a Pokémon it can target, under its play conditions. For example:
  - Dragon's Blessing: to an Active [N], from the Bench;
  - Flame Patch: Fire;
  - Sada: Ancient Pokémon, 3 different types;
  - Lusamine: Ultra Beasts, once the opponent has a point;
  - Volkner: [L] to Electivire or Luxray.
- On the own side, "can target" means a qualifying Pokémon is in play or in its own remaining cards. On the opponent's side, it must be in play.
- Otherwise the credit is 0 for that source.
- **Why the value is right in principle:**
  - Energy that can come back is part of the fuel reserve, so a move that puts it in the pile at no other cost gains value. Rainbow Cave's effect (the Energy is replaced) and Mega Burst's discard are examples.
  - Energy that can't come back gains nothing.

## 5. Build

- The cloud builds kpf on the engine that is the baseline when the build starts.
  - The repaired engine: af8489f, engine e935f42, the rules/09 fixes; its k3 and kp3 table references ran on Sept 26 (070cf2d on the cloud branch).
  - Otherwise 7fc6ccb's line, if the repaired engine isn't accepted by then.
  - Every reading is at one build, with k3, kp3 and kpr3 run at that same build. The 17 new cells are re-run for all three there.
- Tests pin, on constructed boards:
  - the credit's on/off conditions on each side (a Dragonair in play or not, a recovery Trainer in the own deck but not the opponent's);
  - the no-double-count rule with R;
  - the cap;
  - that kpf with F off equals kpr, and kpf with R off equals kpg.
- Identity:
  - kp3 at the kpf build equals kp3's reference on 2 pairings × 40 deals;
  - kpr3 equals the cloud's kpr3 table there, or the difference is explained by the engine repairs alone.
- Seeds: kpf's reading uses existing deals (section 6). Smokes and trace diagnostics use 21,108,900,000 – 21,108,999,999 (already in START_HERE).

## 6. The reading (the plan's order: registered, one review, then the 45 cells)

- **The scoreboard: the 45 cells.**
  - The 28 table cells: 72,000,000 + pairing × 10,000 + i, i < 500.
  - The 17 new cells: 21,108,000,000 + pairing × 10,000 + i, i < 500, pairings 8-24 of `../gauntlet_runs_2026-09-26/tsv/new_decks_run.tsv`.
  - k3, kp3, kpr3 and kpf3 all at the one build.
- **The held-out archetypes, read in every candidate's reading** (RUN5 "Test groups"): B2e's 48 pairings on its deals (21,106 block), with Dustin's matching files reported beside.
- **The adoption rule in force** (RUN5 "Rules"), on the 45 cells, development half, against kp3:
  - paired ΔMSE bootstrap with the whole 95% interval below zero;
  - vetoes (a cell's miss grows more than 6, a deck's gap more than 2, a held-out deck more than 2 further) count only through mixed rows on the same deals (the changed pilot's own side worse beyond the row's paired noise), and never on a cell whose Limitless band is wider than ±15.
  - Real error, average miss, favourites right and correlation are reported, not decided on.
  - The pooled half is reported beside.
- **Development data (Dustin, Sept 26):**
  - The 17 new cells were used to diagnose Rayquaza and design kpf, so they are development data for kpf.
  - Its holdout for the 17 is Limitless events after the freeze date, not a split of the 17 (Dustin).
  - The freeze date: events starting after the window's last event on Sept 24, 2026 (`../b2e_card_check_2026-09-26/README.md` 71-72).
  - For the 28, this is already the rule for every candidate after kp3: the Sept 25 holdout was spent and is not reopened.
  - So confirmation for all 45 is on post-freeze events. This follows from the two rules; it is not a new one.
- **Diagnostics, reported beside, never decided on:**
  - Rayquaza's panel average and Rayquaza v Lucario;
  - the per-turn use rates of Mega Burst, Scorching Interruption, Rainbow Cave (play and effect) and Dragon's Blessing, from `trace_pilot.py` on 200 Rayquaza v Lucario deals, under kp3, kpr3, kpg3 and kpf3;
  - kpg3 on the 45 cells, to show F's own share.

## 7. Coverage before any verdict is final (the Sept 26 rule)

Whatever the 45 cells say, kpf's verdict stays provisional until it is read on the coverage decks:
- the B2e held-out archetypes (already in section 6's reading);
- the variation check's second lists that joined the gauntlet (Lucario, Suicune, Weezing, Charizard Y);
- the Scizor coverage row, if the promotion repair is in kpf's build. If it isn't, the reading says so and doesn't wait for that row.

Coverage evidence can reopen a "not adopted". It can't turn a scoreboard failure into an adoption on its own; that takes a new reading under the rules.

## 8. Open causes, recorded and not targeted

- **Hydreigon overshoot** (kpr3's Hydreigon cells above Limitless). Candidates:
  - Lucario's counterplay against a chipping Hydreigon;
  - how real opponents answer the chip;
  - the chip interacting with Darkness Claw's pricing.

  Not damped in kpf (section 3).
- **Altaria/Greninja's gap** (43% under k3, 41% kp3, 44% kpr3; real 59% dev, 51% pooled): not yet diagnosed. kpf isn't aimed at it.
- **Trainer pricing:** single-Trainer swaps moved decks 4 to 7 points on average in the variation check (Team Rocket's Boss especially). It is queued beside the Tool fix (`kt`), not in kpf.

## 9. What would make kpf wrong (stated before any game)

- F makes the bot hoard Energy in the discard pile: discarding Energy it needs on board, or retreating to discard.
  - The trace diagnostics would show Energy discarded without a recovery used within two turns.
  - The mixed rows would show the kpf side worse.
- The credit fires on the opponent's side without a visible source. A test pins this; a violation is a bug, not a result.
- kpf improves Rayquaza but fails the ΔMSE rule on the 45 cells. Then the verdict is "not adopted, provisional" and the coverage read follows. kpg3's and kpr3's own shares say which part helped.
