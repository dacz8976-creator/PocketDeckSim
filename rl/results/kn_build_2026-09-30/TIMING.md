Decision this informs: which rule, if any, replaces kn's N1 before a registration is written (the Fable coordinator via Dustin, Sept 30: "a bounded design assessment, no new build, no table games"). Registration stays the laptop's and Dustin's. Nothing was built or played for this note. It reads the code at `71877f6` (kn), the smoke in this folder, and the unplayed-Trainer diagnosis (`../trainer_unplayed_diag_2026-09-30/`).

Seeds: none; no game was played.

# Why kn3 plays Goo-zooka on a tie, and what would time it

## In plain words

- **Why it ties.** Under kn, Team Rocket's Goo-zooka is worth +1 (the opponent's Active costs one more to retreat) and costs 1 (a card leaves the hand). The two cancel on every turn it's offered, whatever the board.
  - The search never plays the opponent's turn, so it can't tell a turn where the extra cost will strand their Active from one where it changes nothing.
  - The tie then goes to the play by the order the moves are listed in, so kn3 plays it at the first chance: 492 of its 682 plays in the plain Goo-zooka deck, and 507 of 677 in the Grass Knot deck.
- **The cause.** N1 is a flat, unconditional term: the opponent's Retreat Cost counted the same on every board. The underlying gap is in km's clock: a threat on the Bench gets to the Active Spot for free, with no retreat to pay. That is the one place a raised cost would really slow the opponent, and the clock can't see it. N1 was a static stand-in for it, and a stand-in without the condition ties.
- **Three candidate rules** (all list-free and constant-free, like N2):
  - **C1:** keep N1's term but count it only when the opponent's Active is damaged or is not their clock's threat.
  - **C2:** charge a benched threat its Active's way out, in the clock.
  - **C3:** price the cost where an attack reads it (Grass Knot, Shadow Seeker) in the clock, and drop N1.
- **Recommendation: C2, with N1's static term off.**
  - It is the only rule that prices the play by what it does: the opponent's threat arriving a turn later, worth about 100 in the score, against the card's 1. So it is played on the turn it pays and held otherwise, with no tie.
  - By my reading of the diagnosis's traces, it covers 6 of the 7 turns the diagnosis judged worth playing, and none of the 3 it judged not.
  - It is also the widest change of the three, a change to the clock itself, so it needs the full footprint route.
  - C1 is the cheap fallback. C3 is a separate, small candidate for the Whimsicott carrier.
  - kn as built should not be registered.

## (1) Why the tie exists

**What the N1 term adds.**
- The score's retreat term becomes `(opp.active_retreat_cost − my.active_retreat_cost) × 1` (`value_functions.rs:796-799`).
- The opponent's cost is the engine's board cost of their Active (`get_active_retreat_cost`, `:961`, through `get_board_retreat_cost_for_player`).
- Goo-zooka puts `IncreasedRetreatCost { amount: 1 }` on their Active for 1 turn (`apply_trainer_action.rs:421-427`). The board cost pushes one more Colorless for it after every reduction (`hooks/retreat.rs:236-249`).
- **So on any board where their Active stays in front, the play moves N1 by exactly +1.** The only exception is an Active whose retreat is already free by an Ability or Big Air Balloon, which the code returns early for (`retreat.rs:141-160`).

**What it costs.** The card leaves the hand: the score's card term `(my.hand − opp.hand) × 1` (`:803`) drops by exactly 1.
- Nothing else in km's score reads the effect. The diagnosis measured this: km's score after playing minus after only discarding was 0.0 on all 147 Goo-zooka chance turns.
- **So the play is +1 − 1 = 0 against not playing it, on every chance turn.** The unit test `n1_goo_zooka_moves_kn_by_one_and_km_by_nothing` pins it: the whole play through the game moves km by −1 and kn by 0.

**Why the board can't break the tie.**
- km3's search has no opponent ply (`opponent_ply: 0`). It returns the static score the moment the turn passes (`expectiminimax_player.rs:98-104`), so every leaf is at or before the end of kn3's own turn.
- The effect is on the board at every such leaf. Its 1 turn left is counted down at the end of kn3's turn and removed only at the end of the opponent's (`played_card.rs:460-469`).
- So the search sees the +1 in every line where their Active stays in front, and never sees the opponent's turn, where the +1 pays off (a stranded Active, a spent attachment) or doesn't (they had no reason to retreat).
- Whether the turn "pays" is decided entirely in a turn the search doesn't look at.

**Why the tie goes to the play.**
- The legal moves are sorted by their JSON text before the search (`observation.rs:37-39`), and the root keeps the last of equal scores (`max_by`, `expectiminimax_player.rs:340-347`).
- `EndTurn` sorts first, then Attach, AttachTool, Attack, Evolve, Place, Play, Retreat, UseAbility. So on a tie Play beats ending the turn, attaching, attacking, evolving and placing.
- The parked text predicted exactly this ("The tie goes toward Play, by sort order and not by value", N1's "Honest size").

**Where it isn't a tie** (so the rest of the plays and non-plays aren't random):
- when a later move in the same line removes their Active (a knockout, or a gust after the play), so the +1 leaves with it: −1, no play;
- when an attack in the same turn reads the cost (Grass Knot's +30): a strict gain under km and kn alike, which is why km3 played it before Grass Knot in 359 of 360 plays;
- when Hiking Trail refills the hand at the end of the turn: the card term is refunded, so the play is a strict gain (+1 under km, +2 under kn);
- when the search's three moves are all needed for a better line: the play doesn't fit.

**The smoke agrees** (`smoke/games.jsonl`):

| deck | code | Goo-zooka plays | on the game's first chance turn | on a turn the deck attacked | chance turns not played |
|---|---|---|---|---|---|
| goo (no Grass Knot) | km3 | 3 | 0 | 2 | 2,684 |
| goo | kn3 | 682 | 492 | 430 | 110 |
| grass_goo (Whimsicott ex) | km3 | 360 | 44 | 360 | 1,634 |
| grass_goo | kn3 | 677 | 507 | 490 | 93 |

## (2) Which simplification causes it

Four simplifications meet. The first two make the tie; the third makes it cost the carrier; the fourth is why N1 was needed at all.

1. **N1 has no "it matters" condition** (the parked text's choice: "Same weight, same extraction, no new function").
   - The opponent's cost counts the same whether their Active is their attacker, a damaged Basic that must leave, or a Pokémon stuck anyway.
   - Its unit (1 per Energy) equals the card term's (1 per card). So the effect's price equals the card's price exactly, on every board.
2. **No opponent ply.** The payoff lands on the opponent's turn, which the search never plays. This is the census's second fix sketch ("or search one public opponent reply", `../trainer_audit_2026-09-25/census_table.md`).
   - I don't propose it as a candidate: it changes every decision the search makes. The §42 notes also record that searching a reply only on some leaves prices lines inconsistently (`expectiminimax_player.rs:110-123`).
3. **Grass Knot's damage is not in the clock** (the parked text's own listed simplification).
   - Under km, the only positive price Goo-zooka ever gets is a Grass Knot in the same turn, which the search finds through the points and HP terms. So km3 plays it exactly then.
   - Under kn the tie fires earlier, and with 2 copies the card is gone before the Grass Knot turn: 120 of kn3's 677 plays came before a Grass Knot, against 359 of km3's 360.
   - This is the carrier's cost in the smoke (paired deals won only with km3 against only with kn3: 23 to 3 and 17 to 3 in two matchups).
4. **The clock gives a benched threat a free path to the Active Spot.**
   - km's clock (`kt_clock_stadium`, `:1766`) picks the threat among every in-play Pokémon by its missing Energy alone (`threat_candidates`, `:1340-1390`; "fewest missing Energy … whatever its slot").
   - A benched threat is never charged the retreat its side's Active must make first.
   - The one situation where a raised Retreat Cost really slows the opponent is their threat waiting behind an Active that can't pay to leave. The clock can't see that situation, which is why a static term was used as a stand-in for it.
   - (kq has a retreat "escape" in its first-attack arithmetic, `:1723-1745` and `:2058-2090`, but kq's features are off in km.)

## (3) Candidate rules

Each is list-free (keyed on effects and board numbers the engine already computes, never on card names) and constant-free (no weight or threshold of its own).

### C1: count N1 only where a retreat is wanted

- **The rule.** In N1's term, count the opponent's Active board Retreat Cost only when, at the leaf:
  - their Active is damaged; or
  - it is not the threat their clock counts (the threat's slot in `kt_clocks` is on the Bench).
  - Otherwise count 0. Setup, the weight and the bot's own term are unchanged.
- **What it prices.** Goo-zooka, gust targets (Cyrus brings up a damaged Pokémon, so C1 prefers the one that costs most to leave), Plaza, Trap Territory and their retreat Tools, all only on those boards.
- **What it doesn't fix.**
  - On a counted board the play is still +1 − 1 = 0, a tie resolved by move order. It lands only on counted turns, but still by the tie.
  - "Not their threat" is true on many early boards (a Basic in front of a developing attacker), so some turn-2 plays will remain.
  - It doesn't check whether they can pay the raised cost anyway.
  - By my reading of the diagnosis's 10 judged Goo-zooka turns (`../trainer_unplayed_diag_2026-09-30/README.md`, question 3):
    - it counts all 7 "yes" turns;
    - but also 7100 turn 9, where Mega Altaria ex was damaged and stayed in, and 14600 turn 4 (Hoopa ex, stuck anyway). Those are plays that do nothing.
- **Expected footprint.**
  - Goo-zooka and Plaza lists: most games still differ from km, though fewer plays than kn's 86% of chances.
  - The 45 cells: no more than kn's (gusts, Field Blower on Balloon or Boat, close lines), so of the order of 1% of games or less. Not measured.
- **Carrier:** Whimsicott ex Ariados (as for kn); reach as kn's (decks 12, 14, 15, brews 03a and 03b for Goo-zooka; 05b and 10 for Plaza).
- **Smoke:**
  - the same scratch smoke (`smoke/run_smoke.sh`, with the new code in kn3's place);
  - plus, per play, whether the opponent's Active was damaged at the end of the turn and whether they retreated next turn and could pay;
  - plus the diagnosis's 10 judged turns replayed with the diagnosis's replay program: the play should come on the 7 and not on 8103.

### C2: a benched threat pays its Active's way out (in the clock) — recommended

- **The rule.** In km's clock (both sides, as N2 is), a threat candidate on the Bench adds to its missing Energy what its side's Active still lacks to retreat: `max(0, board Retreat Cost of the Active − Energy attached to the Active)`.
  - The turn's attachment goes either to the retreat or to the attacker. It is the same arithmetic as kq's escape, `retreat_cost + short <= attached + attach_next`.
  - The Active's board cost is read with the effects live on the turn the threat would attack, as switch 1 reads a temporary cut for turn f ("an effect with d turns left is live through turn t + d"). So Goo-zooka's +1 counts only if their threat would otherwise come in on their next turn.
  - A benched candidate whose Active can't retreat at all (a Special Condition that blocks it, `NoRetreat`) gets no extra. That case is left as it is today, a stated limit.
  - N1's static term is off.
- **What it prices, by value, not by a tie:**
  - Goo-zooka is worth a turn of their threat's clock (weight 100) exactly when their threat is benched and their Active can't pay the raised cost on their next turn. Otherwise it is worth 0 and the card's −1 holds it.
  - The same term prices a gust that strands (Cyrus: bring up the Pokémon with the largest shortfall in front of their benched threat), Trap Territory, Plaza for either side, and both sides' retreat Tools and Bombirdier, all where the retreat is really needed.
  - On the bot's own side it prices keeping a cheap-to-leave Active in front of its own developing attacker.
- **By my reading of the 10 judged turns** (the boards in `../trainer_unplayed_diag_2026-09-30/turns.jsonl` and their traces; not computed by the rule):
  - It counts 6 of the 7 "yes" turns:
    - 9102: Deino at 0 Energy, Hydreigon benched;
    - 12600: Chien-Pao ex at 1 Energy, Suicune ex benched;
    - 9600: Deino at 1 Energy;
    - 8101: Torchic at 0 Energy after Sabrina;
    - 11602: Grovyle at 0 Energy, Butterfree benched;
    - 7102: Igglybuff at cost 0, Espeon on the Bench.
  - It misses 13600, where the benched Shuckle ex is probably not the clock's threat. The value there is the damaged ex left in front, a knockout, which C2 doesn't price.
  - It counts none of the 3 "no" turns: in 7100 the Active is their threat; in 8103 the effect sits on a benched Pokémon; in 14600 Hoopa ex is itself the threat.
- **Expected footprint: large, the largest of the three.**
  - It moves the clock wherever a side's threat is on the Bench behind an Active short of its retreat. That is common in early turns, on both sides, and on every list, not only lists with N1's cards.
  - I can't size it without games. It should be read by a full footprint route like kt's, and a footprint of 15% or more is plausible.
  - The bot's-own-side half is most of that reach. A one-sided diagnostic code (the opponent's clock only) would split the halves if the footprint needs attributing.
- **Carrier:** for Goo-zooka's timing, the Whimsicott ex Ariados list and Dustin's decks 14 and 15. For the change as a whole, every list, because it is a clock rule; so it is read like kt's switch 1, by the table's footprint and the registered outcomes, not by a carrier alone.
- **Smoke:**
  - the same scratch smoke with the new code: Goo-zooka plays per chance, plays before Grass Knot, paired wins, and the control deck's games that differ (the early warning for the footprint);
  - the diagnosis's 10 judged turns (the play on the 6, not on the 3);
  - a unit pin that a benched threat's missing count equals the engine's retreat arithmetic on boards with Goo-zooka, Plaza, Trap Territory, Balloon, Boat and Bombirdier, as N2's pin compares with `modify_damage`.

### C3: price the cost where an attack reads it (in the clock)

- **The rule.** In km's clock, a hit by an attack with `ExtraDamagePerRetreatCost` on a victim as the Active carries its bonus for that victim's board Retreat Cost. The effects count only while live, as in C2.
  - The attacks are Whimsicott ex's Grass Knot (+30 a Energy), Tangrowth's Grass Knot (+40) and Team Rocket's Arbok's Shadow Seeker (+10).
  - It is kd's per-defender bonus (`defender_identity_bonus`, `:1620`) extended by one mechanic, applied the way N2's bonus is (`damage_on(victim)`).
  - N1's static term is off.
- **What it prices.** Trap Territory for the whole time Ariados is in play (every future Grass Knot is +30); Plaza and the opponent's retreat Tools against these attacks; gust targets for them.
  - Goo-zooka itself stays km's: its +1 is gone before the bot's next attack, so only the same-turn Grass Knot reads it, which the search already finds (359 of 360).
- **What it doesn't fix.** Goo-zooka in decks without these attacks (Dustin's 14 and 15), where the diagnosis judged 7 of 10 turns worth playing, stays unplayed as under km.
- **Expected footprint.** Only lists with these three attacks: none of the 45 cells' lists; B2e's Whimsicott rows; Dustin's deck 12. Near 0 elsewhere.
- **Carrier:** Whimsicott ex Ariados.
- **Smoke:**
  - the scratch smoke's `grass_goo` rows (Goo-zooka still before Grass Knot, Ariados put in play earlier or more often, Grass Knot's damage);
  - a unit pin of the bonus against `modify_damage` for the three attacks.

## (4) Recommendation

- **Don't register kn as built.** Its rate rises through the tie, and on the carrier it spends the card before the turn the carrier's own attack would use it.
- **Build and smoke C2 next, as a new code on km with N1's static term off.** It is the only rule of the three that values the play by what it does on the turn it does it. That is the opponent's threat arriving a turn later, worth about 100, against the card's 1. So the choice is by value and not by move order, and it fits the diagnosis's judged turns best.
  - Its cost is reach: it is a clock change on both sides. It should go through the full footprint route, and its smoke should include the control deck and the one-sided diagnostic before any table.
- **If C2's footprint is judged too wide,** C1 is the cheap fallback: one condition on the existing term, footprint no wider than kn's. But it still lands by the tie on counted turns.
- **C3 is independent of both,** small, and specific to the Whimsicott carrier. It is worth its own later decision if the carrier is read. Composing it with C2 would need its own check (two switches, two decisions, as Dustin ruled for km).
- These are recommendations only; which rule to register, and whether, is the laptop's and Dustin's.

## Limits

- The "counts" and "misses" for C1 and C2 on the diagnosis's judged turns are my reading of the boards and traces, not the rules computed. The replay proposed in each smoke would compute them.
- No footprint here was measured. They are expectations from the code and from which lists carry what.
- The line numbers are at `71877f6`.
