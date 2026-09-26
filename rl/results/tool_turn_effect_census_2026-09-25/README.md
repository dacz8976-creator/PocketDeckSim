Decision this informs: whether the next candidate after kpr (the Tool / turn-effect blind spot, Dustin-approved) can be read on the Limitless table, and what its spec should be; nothing is built until kpr's table is read. Census engine: 1981bb4 (kp3's code path, unchanged since the table; the counting tool was built in a scratch copy, and the repo's engine/ is untouched).

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

## Draft spec: `kt<N>` (for the laptop and Dustin; not registered, nothing built)

**Base.** `kt<N>` = `kp<N>` (k's blind search, PublicPricingPlayer with its audited texts) plus two evaluator changes. It is built on kp, not kd or kpr. kq's, kd's and kpr's features are off. The player code is "kt<N>", parsed before "k<N>". k3, kp3 and kq3 must replay the table unchanged, proven by replay before any kt table.

**(1) The defender's temporary damage cuts, in the threat clock, for the attacker's next attack.**
- **Which cuts.** Every cut that will be in force on the victim during the threatening side's next attack, from public state only, keyed on the effect type, never on card names:
  - turn effects on that turn: `ReducedDamageForTarget`, if its scope covers the victim and its "only from ex" condition holds for the threat (Jasmine, Blue, Cheren, Beast Wall); and `ReducedDamageForType`;
  - the victim's own effects still live then: `CardEffect::ReducedDamage`, and `ReducedDamageFromEx` against an ex threat (Stiffen, Steel Wing, Protect Charge; Superb Shield);
  - reduction Tools on the victim that apply to it: Metal Core Barrier (−50, [M] holder, gone after that turn), Steel Apron (−10, [M]), Heavy Helmet (−20, retreat cost 3 or more). Heavy Helmet follows the engine, which reads the printed Retreat Cost. Dustin says the game reads the current one (Sept 25, test pending; on rules/09's open list). As with kd's coin rule, the scorer mirrors the engine, and a test pins it so it changes when the engine is fixed.
- **Which hits.** Only the first hit on the Active, which is the attacker's next attack. Later hits keep k's arithmetic. The first-hit arithmetic already exists: `ko_turns_after_first_attack(hp, first, max_damage)`, with `first = max(0, damage − cuts)`, summed as the engine sums them.
- **Timing.** "The attacker's next attack" is this turn if the attacker is to move and its turn is running, otherwise its next turn. The turn effects are read for that turn, and a card effect counts only if it is still live then. This is kq's first-attack timing, on the defender's side.
- **Both sides.** The evaluator's own Active as the victim in the opponent's clock, and the opponent's Active in its own.
- **Not included:** anything on the attacker's side (Teary Attack's −30 on the Defending Pokémon is kq's feature); permanent Ability cuts (kd's); and the Weakness order (kp's clock has no Weakness).

**(2) The flat Tool bonus replaced by what the Tool does for its holder.**
- **Now.** kp adds 10 when the Active holds any Tool, and subtracts 10 when the opponent's does (`active_has_tool`, weight 10). That flat 10 is why kp3 plays the Poncho on its Active and Small Balloon on a Stage 1, and why it Field Blowers the opponent's Active Tool. The game allows those plays (Dustin, Sept 25: any Tool may go on any Pokémon, and an unmet condition just means no effect), so they are bot mistakes, not engine bugs.
- **Proposed.** Drop the flat term (weight 0 in `kt`). A Tool is then worth what it does, through the terms that already measure each effect:
  - HP Tools (Giant Cape, Leaf Cape, Elegant Cape): the remaining HP. It is already in the board value, the Active's safety and the clock, so a Giant Cape is already worth about +20 before the flat 10;
  - retreat Tools (Small Balloon, Inflatable Boat): the Active's retreat cost term, only where they apply;
  - damage-cut Tools (Metal Core Barrier, Steel Apron, Heavy Helmet): through (1);
  - anything the evaluator doesn't model (Rocky Helmet, Deceptive Needle, Lucky Egg, Poison Barb, the Poncho's Bench protection): 0, as asked.

**What (2) would change, from the census.** This is prediction, not measurement:
- The useless plays stop: 427 Ponchos on the Active, and 225 Small Balloons where they cut nothing, out of 2,800 games.
- HP Tools keep being played: +20 to +30 HP outweighs the card leaving the hand (−1).
- Retreat Tools become a tie: +1 on the retreat term against −1 for the card. Move order would decide, so they'd be played about half the time or less.
- Field Blower is then worth what the removed Tool did for its holder. Against Leaf Cape and Giant Cape it's still worth playing (−20 to −30 HP for them). Against Rocky Helmet, Deceptive Needle or Small Balloon it's worth nothing more than the card, so it wouldn't be played.
- **Rocky Helmet and Deceptive Needle would stop being played entirely** (478 + 937 + 847 plays; Blaziken, Hydreigon and Weezing). "0 when the effect isn't modelled" values real effects at nothing: 20 back per hit, and 10 a turn to the opponent's Active.

## Open choices before registration (Dustin's and the laptop's)

1. **Tools whose effect isn't modelled.** Recommendation: (b), so the table measures what kt models and not what it can't see.
   - **(a) 0, as written.** kt stops playing Rocky Helmet and Deceptive Needle. That will likely read as those three decks getting weaker, for a reason outside the spec.
   - **(b) Keep kp's +10 only for Tools whose effect the evaluator doesn't model.** Rocky Helmet and Deceptive Needle play as now. Tools that do nothing for their holder where they sit (the Poncho on the Active, Small Balloon on a non-Basic, Leaf Cape on a non-[G], a cut Tool on the wrong type) get 0.
   - **(c) Model them.** End-of-turn damage to the opponent's Active in the clock, retaliation damage to the attacker. This widens the candidate, and would be a later step.
2. **Permanent reduction Tools (Steel Apron, Heavy Helmet) on every hit, or only the next attack?** The request says the next attack, which is narrower and consistent with the temporary cuts. Pricing every hit is kd's approach, which wasn't adopted.
3. **HP Tools.** Should they get anything beyond the HP already counted? Proposed: nothing, since the HP is already in three terms. The alternative, the HP again as a Tool value, counts it twice.

## How kt would be tested

- **Part (2) is visible on the table.** The 28-matchup table against kp3 under rule v2, as for every candidate. The laptop's mixed rows would separate each deck's own Tools from its opponents'.
- **Part (1) is not.** The table has 55 Stiffens in 700 Suicune games. Its test is Dustin's decks:
  - 07 (Jasmine, Metal Core Barrier, Steel Wing), plus 05 (Cheren) and 11 (Protect Charge), and the held-out decks the laptop names;
  - a paired A/B of kt3 against kp3 piloting the deck, against the floor panel, on new seeds from 22,000,000,000;
  - the Skarmory check's measure: deck 07's win rate, and Jasmine's play rate on turns it's playable.
  The laptop's causal test with Jasmine given kp's +10 (82% played, +5.7 points) is the size to compare with. kt prices Jasmine by the turns it saves, not by a flat 10, so the size may differ either way.

## Files

- `tool_census.rs`: the counting tool (an engine example built in a scratch copy).
- `kp3_census.txt`: its output. `kp3_census_games.jsonl`: one fingerprint per game (identical to kp3's table). `kp3_census.log`, `timing.txt`: progress and wall time.
