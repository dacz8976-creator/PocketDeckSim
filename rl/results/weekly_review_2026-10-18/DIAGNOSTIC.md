# Kingambit planning diagnostic (Astra's experiment, Oct 18)

**Question.** km3 missed Dustin's move in 14 positions:
- the counted positives that stage A's bots missed (all but cases 10 and 11);
- the three Energy positions;
- the two Glimmet positions.

For each, is his move (a) missing from the moves km3's search considers, (b) considered but scored lower, or (c) found by a deeper search? And does Kingambit survive in his real game?

**How.**
- **(a):** stage A's own score dumps, which give every candidate's score at every decision (seeds 1-12).
- **(b):** a print-only term dump in a scratch copy of stage A's pg_pos. It scores km3's whole turn and his whole turn, with his line forced, by km3's own evaluation, term by term.
  - Checks: the terms sum to km3's score in all 336 dumps, and km3's plans are identical to stage A's on all 168 position-seeds.
- **(c):** the 14 positions were re-run with stage A's binary on block seeds 25,090,000,001-012:
  - km at depth 5 and 8;
  - upstream's expectiminimax `e5`/`e8`;
  - `y5o3`/`y8o3`, which also search 3 of the opponent's public replies.
- **Kingambit's survival:** from the Codex reviews of the 8 games (a Sonnet credit job, spot-checked).

| # | Position | His move (key part) | km3 plays instead | Class | Gap | Biggest terms behind the gap | Deeper search | Kingambit in his game |
|---|---|---|---|---|---|---|---|---|
| 3 | 010837 t07 | Candy → Kingambit; Energy on Glimmet (Glimmora next) | Energy on the new Kingambit | b | 680 | clock +600 | never his | never KO'd; Blade 180 KO; win |
| 4 | 225319 t06 | Energy, then retreat Pawniard | Pawniard attacks (Slash) | b | 596 | Active readiness +250, clock +200 | never his | never in play (Pawniard sniped); loss |
| 5 | 014423 t07 | Energy on Benched Pawniard | Energy on the Active | b | 217 | Active readiness +167 | never his | never in play; loss |
| 6 | 015659 t05 | bench Pawniard, Energy on it | Energy on the Active | b | 547 | clock +400, Active readiness +167 | never his | never in play (no Candy); loss |
| 7 | 010837 t09 | 2 Pops, Energy, Glimmet's Hang Down | retreat, Kingambit's Blade now | b* | 799 | Pokémon value +380, clock +300 | never his | never KO'd; win |
| 9 | 210041 t06 | Energy on Benched Pawniard | Ilima, then Pawniard attacks | b | 672 | Active readiness +250, value +200, clock +200 | never his | never in play (Copycat shuffled it); loss |
| 12 | 010706 t11 | Heavy Helmet + Energy on Benched Kingambit | Helmet + Energy on the Active | b | 247 | Active readiness +167, clock +100 | never his | never KO'd; winning Blade; win |
| 13 | 010837 t05 | Energy on Benched Pawniard | Energy on the Active (Regigigas) | b | 167 | Active readiness +167 | never his | never KO'd; win |
| 14 | 014423 t03 | Energy on Benched Pawniard | Energy on the Active, or Copycat | b* | 80 | Active readiness +167 | never his | never in play; loss |
| 15 | 203719 t11 | Helmet on Benched Kingambit, Energy on Muk | Energy on Kingambit, Helmet on the Active (Regigigas, 10 HP) | b | 640 | clock +600 | never his | never KO'd; no attack (opponent conceded); win |
| E1 | 203719 t09 | Stadium, Energy on Muk | Energy on Kingambit | b | 630 | clock +600 | never his | as 15 |
| E2 | 210823 t06 | Candy → Kingambit, Energy on it | **his line** (+ a free Stadium use) | same | 0 | – | his line | never KO'd; no attack; win |
| G1 | 010706 t13 | bench Glimmet, Energy | **his line** | same | 0 | – | his line | as 12 |
| G2 | 203719 t13 | bench Glimmet, Energy, Venomous Hit | **his line** | same | 0 | – | his line | as 15 |

- **Gap:** km3's whole turn minus his whole turn, both by km3's own evaluation at the end of the turn (median over 12 seeds).
- **b\*:** seeds disagree. In 7, his second Pop needs heads, so 3 of 12 forced lines stopped early. In 14, km3's line varies by seed.
- **kmbc3** (stage A's runs) matches his line only in 3 of 12 seeds at 14. Elsewhere it either plays as km3 does, or moves further from his line: at 9, 15, E1, E2, G1 and G2 it skips the Glimmet, attacks first, or moves the Energy to the Active.
- **The terms, in plain words:**
  - *Clock* is km3's count of how many turns each side needs to win.
  - *Active readiness* is how close the Active Pokémon is to its attack.
  - *Pokémon value* is HP × (Energy + 1) summed.

## What it shows
- **(a) never happens.** Every one of his actions was among the moves km3 scored, at every step. The bot sees his choices.
- **(b) is the whole story.** In 11 of 14 positions km3 scores his turn lower, by 80 to 800. The other 3 are positions where km3 already plays his line.
  - The gap comes from two terms. *Clock* rewards whatever can attack soonest. *Active readiness* counts only the Pokémon in front.
  - His moves prepare for a later turn of his plan, and neither term gives that any credit:
    - Energy and the Helmet on the Benched Pawniard or Kingambit (5, 6, 9, 12, 13, 14, 15);
    - Energy on the next Glimmora rather than on Kingambit (3);
    - Energy on Muk rather than on Kingambit (E1);
    - retreating Pawniard instead of trading it (4);
    - Glimmet's chip attack instead of an early Blade (7).
  - In 3, 15 and E1 the bot is MORE eager to power Kingambit than he is. So the bot isn't just ignoring Kingambit: it charges whatever finishes soonest by its clock, while he follows his plan's order.
- **(c) never happens.** No deeper setting picks his line in the 11.
  - Depth 5 to 8 changed 24 of about 2,500 scores. The opponent-reply search changed scores in 5 positions but no decision.
  - km's and upstream's search ends at the end of our own turn, or a few public replies after it. His choices pay off several turns later, when Kingambit swings.
- **Kingambit's survival** (his real measure, 8 games):
  - It was never knocked out.
  - In the 4 wins it came out late and was ready: two knock-out or winning Blades, and two games ended first.
  - In the 4 losses it never came into play: no Rare Candy, shuffled away by Copycat, or Pawniard sniped.
  - In his games the failure was Kingambit not arriving, not Kingambit dying.

**Search or learned evaluator?** The evaluation, not the search. His moves are generated and scored; they lose on the scoring, and no feasible depth reaches a payoff several turns away.
- That points to a learned evaluator, or a plan-aware term that credits readying a Benched attacker for a later turn.
- **Caveat:** 14 positions from 8 of his games are far too few to train or validate one. Astra's milestone, good choices on positions the bot wasn't tuned on, applies to whatever replaces the evaluation.

*Files on the laptop's WSL:*
- score dumps and the classifier: `~/diag/sweep`, `~/diag/classify_*.json`;
- the term dump: `~/diag/terms`, built from `~/diag/src_terms`, print-only;
- the survival read: `~/diag/surv`.

*Cost:* two Sonnet credit jobs, $0.68.
