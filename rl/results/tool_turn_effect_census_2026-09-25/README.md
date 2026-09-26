Decision this informs: whether the next candidate after kpr (the Tool / turn-effect blind spot, Dustin-approved) can be read on the Limitless table, and what its spec should be (revised Sept 26 with the laptop's per-card table and three switches); nothing is built until kpr's table is read. Census engine: 1981bb4 (kp3's code path, unchanged since the table; the counting tool was built in a scratch copy, and the repo's engine/ is untouched).

Seeds: the table's deals only, 72,000,000 + pairing × 10,000 + i, i < 100, even i = the first-named deck in seat 0. The 2,800 census games are kp3's own table games: 2,800 of 2,800 move fingerprints equal `../public_pricing_2026-09-25/kp3_500_*.jsonl`.

# Tools and temporary damage cuts in the table's games, and a draft spec (Sept 25)

## In plain words

- **The flat Tool bonus is everywhere on the table.** Every one of the eight lists runs a Tool, and kp3 plays one on 60–92% of the turns it can, almost always on the Active. Six lists run Field Blower, and it mostly removes the opponent's Active Tool. Replacing the flat +10 will move the table.
- **The temporary damage cuts are almost absent.** None of the eight lists has Jasmine, Metal Core Barrier or any "take −X damage during your opponent's next turn" Supporter or Tool. The only one is Frigibax's Stiffen in the Suicune list, used 55 times in 700 Suicune games. So the table can't read that part; its test has to be Dustin's decks 07, 05 and 11.
- **A lot of the Tool plays do nothing where they go.**
  - Lucario's Protective Poncho goes on the Active 427 times out of 428. It only protects a Benched Pokémon.
  - 45% of Altaria's Small Balloons (225 of 501) go where they do nothing: on Espeon or Mega Altaria ex, which aren't Basics, and on Igglybuff, whose Retreat Cost is already 0. The laptop's Trainer audit (`rl/results/trainer_audit_2026-09-25/` on main, 8,640 kp3 games) finds 48%.

## The census

kp3 on both sides, the table's first 100 deals of all 28 pairings; each deck plays 700 games. "Offered" counts the owner's turns on which the card could be played, "played" the turns on which it was. The tool is `tool_census.rs`; its raw output is `kp3_census.txt`.

**Tools:**

| deck | Tool | what it does | turns offered | turns played | on the Active | where it does nothing |
|---|---|---|---:|---:|---:|---:|
| Altaria | Small Balloon | Basic: retreat −1 | 567 | 501 (88%) | 496 | 225: Stage 1 (Espeon 93, Mega Altaria ex 67), or retreat already 0 (Igglybuff 65) |
| Blaziken | Rocky Helmet | 20 back to an attacker that damages the Active holder | 691 | 478 (69%) | 471 | — |
| Hydreigon | Deceptive Needle | end of turn, [D] Active holder: 10 to the opponent's Active | 1,176 | 937 (80%) | 918 | — |
| Lucario | Protective Poncho | Benched holder: no damage | 632 | 428 (68%) | 427 | 427 on the Active |
| Sceptile | Leaf Cape | [G] holder: +30 HP | 539 | 497 (92%) | 442 | — |
| Suicune | Giant Cape | +20 HP | 614 | 554 (90%) | 423 | — |
| Suicune | Inflatable Boat | [W] holder: retreat −1 | 836 | 501 (60%) | 493 | — |
| Vespiquen | Leaf Cape | [G] holder: +30 HP | 1,016 | 839 (83%) | 681 | — |
| Weezing | Deceptive Needle | as above | 1,164 | 847 (73%) | 828 | — |

**Field Blower** (six lists): offered 5,911 turns, played 1,763 (30%). Of the plays, 1,703 removed the opponent's Tool, 1,414 of them from the Active; 26 removed the player's own Tool; 34 removed a Stadium. Per deck and target: `kp3_census.txt`.

**Temporary damage cuts:**
- Frigibax's Stiffen (Suicune list; "During your opponent's next turn, this Pokémon takes −20 damage from attacks"): offered on 124 turns, used on 55 (44%).
- Jasmine, Metal Core Barrier, Blue, Cheren, Beast Wall, Steel Apron: in none of the eight lists.
- Shuckle ex's Solid Shell (Vespiquen) is a permanent cut, which kd priced. It isn't in scope here.

**Where Dustin's decks have them** (read from the lists in `decks/dustin/`):
- Temporary cuts:
  - 07 (Skarmory stall): Jasmine ×2, Metal Core Barrier ×2, Skarmory ex's Steel Wing;
  - 05: Cheren, "Watchog and Stoutland take −100";
  - 11: Archaludon's Protect Charge, −30.
- Permanent reduction Tools: Steel Apron (07), Heavy Helmet (01, 03).
- Other Tools: Lucky Egg, Giant Cape (02); Deceptive Needle (04); Protective Poncho (05); Rocky Helmet (06); Small Balloon (08); Elegant Cape (09, 13, 14); Poison Barb (10); Leaf Cape (12).

## Draft spec: `kt<N>` (revised Sept 26 with the laptop's per-card table; not registered, nothing built)

The laptop's per-card census (`rl/results/trainer_audit_2026-09-25/census_table.md` on main, 61 Trainer cards, each re-checked by a skeptic) says for each card what kp3's score reads. The laptop and Fable suggested three switches, so that a failure can be traced to one part. This draft follows them.

**Base.** `kt<N>` = `kp<N>` (k's blind search, PublicPricingPlayer with its audited texts) with three evaluator switches, each its own `EvalFeatures` flag, all three on in `kt`. It is built on kp, not kd or kpr; kq's, kd's and kpr's features are off.
- For tracing, each switch also gets a diagnostic code with only that switch on. Names are fixed at registration, parsed before "kt" and "k".
- k3, kp3 and kq3 must replay the table unchanged, proven by replay before any kt table.
- Nothing is built until kpr's table is read. The engine fixes queued on rules/09 go in first, each with its replay.

**Switch 1: the defender's temporary damage cuts and reduction Tools, in the threat clock.**
- **Which cuts.** Every cut in force on the victim during the threatening side's next attack, from public state only, keyed on the effect type, never on card names:
  - turn effects registered for that turn: `ReducedDamageForTarget`, when its scope covers the victim and its "only from ex" condition holds for the threat (Jasmine, Cheren, Blue, Beast Wall); `ReducedDamageForType`;
  - the victim's own effects still live then: `CardEffect::ReducedDamage`, and `ReducedDamageFromEx` against an ex threat (Stiffen, Steel Wing, Protect Charge; Superb Shield);
  - reduction Tools on the victim, through the Tool stages kd's `persistent_defender_damage` already runs: Metal Core Barrier (−50 for an [M] holder), Steel Apron (−10, [M]), Heavy Helmet (−20 at Retreat Cost 3 or more). kd's other stages (Weakness, Ability cuts) are not taken over.
- **Which hits.**
  - Temporary cuts (turn effects, the victim's own effects, Metal Core Barrier, which is discarded after that turn) count on the first hit only, the attacker's next attack: `ko_turns_after_first_attack(hp, max(0, damage − cuts), max_damage)`.
  - Steel Apron and Heavy Helmet stay attached, so they count on every hit against their holder.
- **Heavy Helmet reads the current Retreat Cost**, as the game does (confirmed in `heavyhelmet_test.MP4`). The engine's printed-cost read is on rules/09 and is fixed before kt is built, so kt uses the engine's own function. If kt were built first, it would mirror the engine, with a test that fails when the engine changes.
- **Timing.** kq's first-attack timing, from the defender's side: the attacker's next attack is this turn if the attacker is to move and its turn is running, otherwise its next turn. Turn effects are read for that turn; a card effect counts only if still live then.
- **Both sides.**
- **Where the table sees it.** Only Frigibax's Stiffen (Suicune list, 55 uses in 700 games), plus Heavy Helmet and Steel Apron if they appear. Its test is Dustin's decks (below).

**Switch 2: the flat +10 for a Tool on the Active, replaced by what each Tool does for its holder.**
- **Now.** kp adds 10 when the Active holds any Tool and subtracts 10 when the opponent's does (`active_has_tool`, weight 10), whatever the Tool does. All the measured waste comes from here:
  - Protective Poncho: rewarded on the Active, where it does nothing, and not credited on the Bench, where it works. 492 of 494 went on the Active in the laptop's audit; 427 of 428 here;
  - Small Balloon where it cuts nothing (45–48%);
  - Elegant Cape, Heavy Helmet, Metal Core Barrier and Steel Apron on holders that can't use them.
  Field Blower, Guzma and Repel inherit the same +10 from the opponent's side.
- **Proposed.** The flat term goes (weight 0 in `kt`). Each Tool counts through what it changes for its holder where it sits:

  | Tool | what it's worth |
  |---|---|
  | HP Tools (Giant Cape, Leaf Cape) | the HP, already in the board value, the Active's safety and the clock; nothing more. An ineligible holder gets nothing, since the HP isn't added (`get_effective_total_hp` gates it). |
  | Elegant Cape | its +30 HP counts on a Stage 1. On a Basic it is worth nothing unless an evolution is available in the owner's deck or hand, and then the HP is discounted as `evolution_potential` discounts it. |
  | Retreat Tools (Small Balloon, Inflatable Boat) | the Active's retreat-cost term, which already prices the eligible case. Nothing on a holder it can't help. |
  | Damage-cut Tools (Metal Core Barrier, Steel Apron, Heavy Helmet) | through switch 1, on a holder that qualifies. |
  | Protective Poncho | on the Bench, the damage it prevents from the opponent's Bench-hitting attacks and Abilities on its next turn, up to the holder's HP. Nothing while Active. |
  | Rocky Helmet, Poison Barb | switch 3. |
  | Deceptive Needle | already partly read: its first 10 lands inside EndTurn, which the search plays out. Crediting the repeat chips is left for later. |
  | Lucky Egg | not read; nothing. Only Dustin's deck 02 runs it. |

- **Symmetric.** The same values for the opponent's Tools. Field Blower, Guzma and Repel then gain exactly what removing or moving the Tool changes.

**Switch 3: damage back to the attacker, in the clock.**
- **Rocky Helmet** (Blaziken list): while the holder is Active, each hit the opponent's threat lands on it costs the threat 20 (`get_counterattack_damage`). This is counted against the threat's HP in the holder's own side's KO clock.
- **Poison Barb:** the expected Poison damage to the attacker, per Checkup until it leaves the Active, in the same clock.
- Kept separate from switch 2 so a change in Blaziken's row can be read on its own.

**What the switches would change, from the census.** Prediction, not measurement:
- Switch 2 stops the waste: 427 Ponchos on the Active and 225 Small Balloons that cut nothing, in 2,800 games; Barrier, Apron and Elegant Cape misplacements in Dustin's decks.
- HP Tools keep being played (+20 to +30 HP against −1 for the card).
- Retreat Tools on an eligible Active become roughly a tie (+1 retreat term against −1 for the card), so they'd be played less.
- Field Blower is played only where the removed Tool did something for its holder.
- Deceptive Needle keeps about its current value (its first chip, roughly the old +10).
- Rocky Helmet keeps being played only if switch 3's credit covers the card.

**Not in this candidate, for later** (the laptop's list):
- a Stadium's value over later turns;
- the opponent's Retreat Cost (Goo-zooka, Peculiar Plaza);
- Special Conditions;
- Team Rocket's Boss against the hidden hand;
- the search-length cost: a Tool, or any card that needs a target, uses 2 of kp3's 3 own-turn actions. If kt gains less than the audit's waste predicts, check this first.

## How kt would be tested

- **Switches 2 and 3 are visible on the table.** Every one of the eight lists runs a Tool, Field Blower is in six, and Rocky Helmet is in Blaziken. Read the 28-matchup table against kp3 under rule v2, and the laptop's mixed rows, with the single-switch codes to trace any change to its part.
- **Switch 1 is not.** Its test is Dustin's decks: 07 (Jasmine, Metal Core Barrier, Steel Apron, Steel Wing), 05 (Cheren), 11 (Protect Charge), 01 and 03 (Heavy Helmet), and the held-out decks the laptop names.
  - A paired A/B of kt3 against kp3 piloting the deck, against the floor panel, on new seeds from 22,000,000,000.
  - The Skarmory check's measures: deck 07's win rate, and Jasmine's play rate on turns it's playable (1.2% under kp3).
  - The laptop's causal test with Jasmine given kp's +10 (82% played, +5.7 points) is the size to compare with. kt prices Jasmine by the turns it saves, not by a flat 10, so the size may differ either way.

## Files

- `tool_census.rs`: the counting tool (an engine example built in a scratch copy).
- `kp3_census.txt`: its output. `kp3_census_games.jsonl`: one fingerprint per game (identical to kp3's table). `kp3_census.log`, `timing.txt`: progress and wall time.
