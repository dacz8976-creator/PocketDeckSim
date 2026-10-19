# BUILD: exam of Dustin's ladder decisions, as engine positions

Built **51** positions from **27** ladder games (cap 4 per game; max here 4). All are for the engine program in `/home/dacz8976/exam/bin/pg_legal` (legal-moves-only, no bot). Files: `positions.json` (the positions), `legal.jsonl` (pg_legal output), `selection.json` (picked / dropped / not picked, with reasons).

## Points built, per deck and kind

| deck | prepare | attack now | sacrifice | abandon | total |
|---|---:|---:|---:|---:|---:|
| 12 | 4 | 8 | 2 | 0 | 14 |
| 13-A | 12 | 10 | 1 | 0 | 23 |
| Kingambit | 8 | 3 | 3 | 0 | 14 |
| **all** | 24 | 21 | 6 | 0 | 51 |

Kingambit share: 27.5% (cap 35%). Sacrifice: all 6 usable sacrifice turns are in. Abandon: the inventory has 0 usable abandon turns (1 near-usable), so none is in. Attack now: 21 (need 12). Usable turns in the eligible games per inventory.json: 91.

## Points dropped, and why

- 20261014_163325000_iOS turn 3 (prepare): the review shows Mesagoza played every turn, and Mesagoza is not in the deck-12 list we were told to use (Ariados/Whimsicott/Ogerpon list); the position cannot be built from that list without inventing a different deck
- 20261015_201850000_iOS turn 8 (prepare): not built: opponent Garchomp/Gabite/Dragonair line's Energy counts and Tools (Memory Light, Rainbow Cave Energy) are not readable from the review, and 7 earlier turns of hand/discard tracking including a Lucky Ice Pop with unrecorded coin; cost judged too high for a clean position
- 20261015_201850000_iOS turn 9 (attack now): not built, same reason as turn 8

Everything else eligible but not picked is listed with a reason in `selection.json` (`eligible_not_picked`: 'kind other' turns were left out because only sacrifice/abandon/attack/prepare were asked for; the rest were left for spread across games or because other turns were more unusual).

## Label mappings

- Every forced label in every position matched a legal action **exactly** in the legal-moves run; no prefix mapping was needed.
- Where two different legal actions carried one `pg_label` (Field Blower's choice of which Tool to discard), the tool's legal list now appends the action's arguments, e.g. `DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0}`; those exact strings are in the force lines of LAD-20261014_234728000_iOS-t5 and LAD-20261014_233402000_iOS-t7.
- Two force lines (LAD-20261014_153908000_iOS-t6 and LAD-20261014_164328000_iOS-t4) contain the plain step name `ChooseRandomEvolutionTarget` for Quick-Grow Extract's random evolution; the engine's real label carries arguments (e.g. `ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Grass}`) and the step is a hidden random pick, so it is not an exact match and is not applied; the tool stops there. In the verification copy the Extract and that step are replaced by the evolved board.
- One opponent choice inside Dustin's turn resolved itself (only one option): `Activate:1@1`, Sabrina's switch in LAD-20261014_225451000_iOS-t4. It is not in the force line (the force line holds only Dustin's actions); the tool records it as `auto_opponent`.
- Engine step names that are not obvious from the card: playing a Tool is `Play:<Tool>` then `Tool:<Tool>@slot`; Field Blower is `Play:Field Blower` then `DiscardActiveStadium` or `DiscardToolFromPokemon{...}`; Rare Candy is `Play:Rare Candy` then `Evolve:...`; Raticate ex's Thieving Incisors is `Evolve:...` then `Ability@slot` (yes) or `Noop` (no); Giga Turbo's Energy goes to a Benched Pokémon by a second step `Attach:1Colorless@slot fx`; Quick-Grow Extract is `Play:Quick-Grow Extract` then the engine's own random `ChooseRandomEvolutionTarget`.

## How hidden cards were handled

- The shipped force line is Dustin's whole move in order. `legal.jsonl` applies it action by action and **stops** at a hidden draw or search (Professor's Research, Poké Ball, Copycat, Lisia, Sightseer, Mesagoza, Lucky Ice Pop's coin, Quick-Grow Extract's random evolution), recording the legal list up to and including that action (the stop reason is in `stopped`). Nothing hidden is put in a position: no deck order, no next draw, no coin result, no `top`.
- To check that the rest of each move is also legal, I ran a second, **verification-only** copy (not shipped) in which the cards he drew are put in the hand up front (taken from the review's own account of what he drew or searched), the draw card is removed, and the coin-flip card (Lucky Ice Pop) or random evolution is resolved as the review shows. In that copy every forced label matched, step by step. Positions with such a variant are marked in the table below.
- Where the review does not name what a Copycat drew (LAD-20261016_024253000_iOS-t1: two of the five cards), stand-in cards (Glimmora) were used in the verification copy only.

## Per-position result

'Shipped run' = `legal.jsonl` (stops at hidden draws); 'verify run' = the verification-only variant (all forced labels matched in every row; the stop reason is where the line ended). 'Variant' says whether a verification variant was needed.

| id | deck | kind | forced steps | shipped run stops | verify run ends | variant |
|---|---|---|---:|---|---|---|
| LAD-20261014_153908000_iOS-t4 | 12 | attack now | 7 | hidden draw or coin at Play:Poké Ball | the turn is over (opponent's frame) | yes |
| LAD-20261014_153908000_iOS-t6 | 12 | prepare | 5 | hidden random choice (ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Grass}) | end of line | yes |
| LAD-20261014_142546000_iOS-t7 | 12 | attack now | 10 | hidden draw or coin at Play:Professor's Research | game over | yes |
| LAD-20261014_143111000_iOS-t8 | 12 | attack now | 3 | end of line | end of line | no |
| LAD-20261014_143111000_iOS-t10 | 12 | prepare | 6 | hidden draw or coin at Play:Professor's Research | hidden draw or coin at EndTurn | yes |
| LAD-20261014_144627000_iOS-t2 | 12 | sacrifice | 5 | hidden draw or coin at Play:Professor's Research | the turn is over (opponent's frame) | yes |
| LAD-20261014_145449000_iOS-t4 | 12 | prepare | 8 | hidden draw or coin at Play:Poké Ball | end of line | yes |
| LAD-20261014_160506000_iOS-t6 | 12 | attack now | 5 | hidden draw or coin at Play:Lisia | end of line | yes |
| LAD-20261014_160506000_iOS-t10 | 12 | prepare | 5 | end of line | end of line | no |
| LAD-20261014_161324000_iOS-t5 | 12 | sacrifice | 7 | hidden draw or coin at Play:Professor's Research | hidden draw or coin at EndTurn | yes |
| LAD-20261014_161324000_iOS-t7 | 12 | attack now | 4 | hidden draw or coin at Play:Professor's Research | the turn is over (opponent's frame) | yes |
| LAD-20261014_164328000_iOS-t4 | 12 | attack now | 9 | hidden draw or coin at Play:Lisia | the turn is over (opponent's frame) | yes |
| LAD-20261014_214436000_iOS-t6 | 13 | attack now | 5 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261014_214436000_iOS-t10 | 13 | prepare | 6 | hidden draw or coin at Play:Professor's Research | end of line | yes |
| LAD-20261014_215114000_iOS-t6 | 13 | attack now | 4 | hidden draw or coin at Play:Sightseer | end of line | yes |
| LAD-20261014_215114000_iOS-t12 | 13 | prepare | 3 | end of line | end of line | no |
| LAD-20261014_225451000_iOS-t4 | 13 | attack now | 5 | end of line | end of line | no |
| LAD-20261014_230328000_iOS-t3 | 13 | prepare | 9 | hidden draw or coin at Play:Poké Ball | the turn is over (opponent's frame) | yes |
| LAD-20261014_233402000_iOS-t5 | 13 | sacrifice | 5 | end of line | end of line | no |
| LAD-20261014_233402000_iOS-t9 | 13 | attack now | 2 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261014_231006000_iOS-t3 | 13 | prepare | 8 | hidden draw or coin at Play:Professor's Research | the turn is over (opponent's frame) | yes |
| LAD-20261014_231006000_iOS-t9 | 13 | attack now | 4 | end of line | end of line | no |
| LAD-20261014_234728000_iOS-t7 | 13 | prepare | 7 | hidden draw or coin at Play:Professor's Research | end of line | yes |
| LAD-20261014_234728000_iOS-t9 | 13 | prepare | 3 | hidden draw or coin at Play:Sightseer | the turn is over (opponent's frame) | yes |
| LAD-20261015_015320000_iOS-t4 | 13 | attack now | 3 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261015_015320000_iOS-t8 | 13 | attack now | 2 | end of line | end of line | no |
| LAD-20261015_015320000_iOS-t10 | 13 | prepare | 3 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261015_020931000_iOS-t3 | 13 | prepare | 5 | hidden draw or coin at Play:Copycat | end of line | yes |
| LAD-20261015_021533000_iOS-t5 | 13 | prepare | 6 | end of line | end of line | no |
| LAD-20261015_022206000_iOS-t3 | 13 | prepare | 7 | hidden draw or coin at Play:Sightseer | the turn is over (opponent's frame) | yes |
| LAD-20261015_201201000_iOS-t3 | Kingambit | prepare | 6 | hidden draw or coin at Play:Lucky Ice Pop | the turn is over (opponent's frame) | yes |
| LAD-20261015_201201000_iOS-t7 | Kingambit | prepare | 2 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261015_205332000_iOS-t5 | Kingambit | sacrifice | 2 | end of line | end of line | no |
| LAD-20261015_205332000_iOS-t9 | Kingambit | prepare | 4 | end of line | end of line | no |
| LAD-20261015_210617000_iOS-t2 | Kingambit | attack now | 6 | hidden draw or coin at Play:Poké Ball | end of line | yes |
| LAD-20261015_210617000_iOS-t6 | Kingambit | prepare | 2 | end of line | end of line | no |
| LAD-20261016_030833000_iOS-t2 | Kingambit | prepare | 9 | hidden draw or coin at Play:Poké Ball | end of line | yes |
| LAD-20261016_031512000_iOS-t2 | Kingambit | attack now | 3 | hidden draw or coin at Play:Poké Ball | the turn is over (opponent's frame) | yes |
| LAD-20261016_031512000_iOS-t8 | Kingambit | sacrifice | 2 | the turn is over (opponent's frame) | the turn is over (opponent's frame) | no |
| LAD-20261016_015753000_iOS-t5 | Kingambit | prepare | 5 | hidden draw or coin at Play:Lucky Ice Pop | the turn is over (opponent's frame) | yes |
| LAD-20261016_015753000_iOS-t7 | Kingambit | attack now | 5 | hidden draw or coin at Play:Lucky Ice Pop | end of line | yes |
| LAD-20261016_015753000_iOS-t9 | Kingambit | sacrifice | 3 | end of line | end of line | no |
| LAD-20261016_020517000_iOS-t2 | Kingambit | prepare | 4 | hidden draw or coin at Play:Mesagoza | the turn is over (opponent's frame) | yes |
| LAD-20261016_024253000_iOS-t1 | Kingambit | prepare | 5 | hidden draw or coin at Play:Copycat | the turn is over (opponent's frame) | yes |
| LAD-20261014_234728000_iOS-t5 | 13 | attack now | 5 | hidden draw or coin at Play:Copycat | the turn is over (opponent's frame) | yes |
| LAD-20261014_215114000_iOS-t10 | 13 | attack now | 3 | hidden draw or coin at Play:Poké Ball | the turn is over (opponent's frame) | yes |
| LAD-20261014_142546000_iOS-t3 | 12 | attack now | 6 | hidden draw or coin at Play:Copycat | the turn is over (opponent's frame) | yes |
| LAD-20261014_143111000_iOS-t6 | 12 | attack now | 4 | hidden draw or coin at Play:Lisia | the turn is over (opponent's frame) | yes |
| LAD-20261014_214436000_iOS-t4 | 13 | prepare | 6 | hidden draw or coin at Play:Professor's Research | the turn is over (opponent's frame) | yes |
| LAD-20261014_215114000_iOS-t4 | 13 | prepare | 7 | hidden draw or coin at Play:Professor's Research | the turn is over (opponent's frame) | yes |
| LAD-20261014_233402000_iOS-t7 | 13 | attack now | 4 | end of line | end of line | no |

All 51 positions have `problems: []` in `legal.jsonl` (the `position` lines).

## Approximations (every position carrying `"approximate": true`)

All 51 are approximate because the opponent's list is unknown and his hand size is estimated from visible plays (the engine's opponent hidden cards are filled from Dustin's own list, as in the example). Specifics:

- opponent hand size estimated from the visible plays; opponent's list unknown: 4 position(s): 20261014_153908-t4, 20261014_153908-t6, 20261014_142546-t7, 20261014_145449-t4
- opponent hand size and discard estimated from the visible plays; opponent's list unknown: 15 position(s): 20261014_143111-t8, 20261014_144627-t2, 20261014_160506-t6, 20261014_160506-t10, 20261014_161324-t5, 20261014_161324-t7, 20261014_214436-t6, 20261014_214436-t10, 20261014_215114-t6, 20261014_215114-t12, 20261014_225451-t4, 20261014_233402-t5, 20261015_021533-t5, 20261015_022206-t3, 20261015_201201-t7
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; the Tool on his Mega Swampert ex (a retreat-reducing Tool) was unreadable and is left off: 1 position(s): 20261014_143111-t10
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; Chien-Pao's Energy count after Diving Icicles taken as 2 Water: 1 position(s): 20261014_164328-t4
- opponent hand size, discard and Energy estimated from the visible plays; opponent's list unknown: 20 position(s): 20261014_230328-t3, 20261014_231006-t3, 20261014_231006-t9, 20261014_234728-t7, 20261014_234728-t9, 20261015_015320-t4, 20261015_015320-t8, 20261015_015320-t10, 20261015_205332-t9, 20261015_210617-t2, 20261015_210617-t6, 20261016_031512-t2, 20261016_031512-t8, 20261016_015753-t9, 20261014_234728-t5, 20261014_215114-t10, 20261014_143111-t6, 20261014_214436-t4, 20261014_215114-t4, 20261014_233402-t7
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; one retreat-cost-raising card the opponent played was unreadable and is left out: 1 position(s): 20261014_233402-t9
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; Bonsly's printing chosen by name and HP only: 1 position(s): 20261015_020931-t3
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; Lucky Ice Pop's coin results are not in the position (it can return to hand on heads), so the three plays are checked on a variant without them: 1 position(s): 20261015_201201-t3
- opponent hand size, discard and Energy estimated from the visible plays; opponent's list unknown; Lucky Ice Pop (returned to the opponent's hand on heads) is in his hand count, not his discard: 1 position(s): 20261015_205332-t5
- opponent hand size and discard estimated from the visible plays; opponent's list unknown; Lucky Ice Pop's coin and Copycat's draw are hidden, so the line is checked on a variant that resolves them as they happened: 1 position(s): 20261016_030833-t2
- opponent hand size, discard and Energy estimated from the visible plays; opponent's list unknown; Lucky Ice Pop's coin is hidden (it returned to hand on heads), so the line is checked on a variant without that play: 1 position(s): 20261016_015753-t5
- opponent hand size, discard and Energy estimated from the visible plays; opponent's list unknown; Lucky Ice Pop's two coins are hidden, so the line is checked on a variant with the Pops already resolved (Kingambit at 110): 1 position(s): 20261016_015753-t7
- opponent hand size estimated from the visible plays; opponent's list unknown; Bonsly's printing chosen by name and HP only; Mesagoza's coin is hidden (it found Glimmet): 1 position(s): 20261016_020517-t2
- opponent hand size estimated from the visible plays; opponent's list unknown; Copycat's draw is hidden: the review names Glimmet, Regigigas and Mesagoza but not the other two cards, so the line is checked on a variant with two stand-in cards (Glimmora): 1 position(s): 20261016_024253-t1
- opponent hand size, discard and Energy estimated from the visible plays; opponent's list unknown; Copycat's four drawn cards are the four the review shows afterward (Lisia, Research, Ariados, X Speed): 1 position(s): 20261014_142546-t3

Other things to know:
- The opponent's discard lists only what the review names; cards he played that the review did not name are missing. Opponent Energy counts after attacks that discard Energy (Mega Burst, Hyper Ray, Blazing Beatdown, Diving Icicles) are my reading of the account and are marked approximate; the review says per-turn Energy counts on stacked icons are not always readable.
- Opponent printings were picked by name, HP and the attack/Ability titles in the review; unclear ones are in each position's `opp_ambiguous`.
- The review's 'Shell Balloon' is not a card in the data; Small Balloon stands in for it (it is on the opponent's Rayquaza in the 234728 positions for turns 3, and in his discard in turns 4 and 5).
- Hiking Trail (owner Dustin) is set as the Stadium in the games where it was in play (160506, 161324, 164328); Soothing Shore, Training Area, Rainbow Cave likewise. Opponent Stadium effects the engine does not model on the position are not added.
- Per-Pokémon effects set: Bonsly's Teary Attack on Dustin's Active (LAD-20261015_020931000_iOS-t3, LAD-20261016_020517000_iOS-t2: `ReducedAttackDamage 30`), Mega Sableye ex's Counterattack 40 (LAD-20261015_205332000_iOS-t5). Other one-turn effects from the opponent's last turn were not set.
- `knockouts` is Dustin's own Pokémon knocked out earlier (for Overlord's Blade); set on every position where it is nonzero.
- `heldout: true` on all positions, as the brief intends (an exam no bot was developed on); I did not check any bot's history myself.
- Hands: the review names Dustin's cards when it says what he drew/played/kept; every hand here follows the opening five, each turn's draw, and what the account says he played or searched, so each is consistent with the engine's deck-count checks (no 'more copies than the list' problem). A hand the account leaves unclear was not built.

## Engine tool and self-check

- `/home/dacz8976/exam/src_legal` (copy of stageA/src_pg) with `--legal-only` added to `engine/examples/pg_pos.rs`; built with `cargo build --release --locked --example pg_pos` into `/home/dacz8976/exam/t_legal`; binary copied to `/home/dacz8976/exam/bin/pg_legal`. Four small additions after the first build (all inside the `--legal-only` branch; the free and forced runs are untouched): treat the engine's `ChooseRandom...` frame as a hidden random choice; auto-apply an opponent's single-option choice inside Dustin's turn; widen the hidden-draw check (known draw/search/coin cards, or any new card entering the hand, or a deck-size change); disambiguate equal labels.
- The legal-only branch builds the position, prints the `position` (and `state`) lines, then the `legal` line, and `continue`s before the existing free and forced runs. It only uses random players that are never asked to move; it never constructs a bot (`km3`) or calls a decision function.

- **Self-check:** `pg_legal --positions schema/example_position.json --legal-only --dump-state --deck ...` printed the position, state and legal lines (EndTurn, Play:Rare Candy, Attach@0-3 for that example) and its stderr had **0** lines containing PGDUMP. The same check was made on the full 51-position run (the assembling script flags any PGDUMP in stderr; none was flagged), for both the shipped and the verification run. No search ran.
- Reminder for the later step: positions with a hidden draw have forced lines that continue past it; a bot run has to take those cards from the engine's own draw, not from this file.
