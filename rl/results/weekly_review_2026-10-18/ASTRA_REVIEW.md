# Astra's weekly review (outside view), Oct 18, 2026

Pasted by Dustin into the coordinator session on Oct 18 evening. Astra (Codex) checked main through f7e8b601, source
code, the diagnostic's stored arithmetic and primary sources; no builds, games, training, paid inference or edits.
Filed after the Claude-side review so the two reviews stayed independent.

## Verdict

Redirect the bot's planning and evaluation work rather than spend another week adding small scoring bonuses.

## A. Progress

Better diagnosis and supporting engine work, but no demonstrated new Kingambit capability, validated Kingambit deck
improvement, or reliable ladder prediction. Stage A's candidate passed 2 of 12 targeted checks (6 needed). The
diagnostic's 14 positions: the intended actions were available; km3 scored his completed turn lower in 11 and already
followed his line in 3. Astra re-checked the arithmetic of all 336 recorded score breakdowns: no discrepancies.
Matching his exact move is not by itself proof of better play; acceptable alternatives, unfamiliar positions and
completed play are still needed.

## B. Approach

Continuing unchanged is not the best investment. The score rewards immediate attack readiness and a simplified race;
his deck needs sequencing (sometimes prepare Kingambit, sometimes Muk or Glimmora first, sometimes preserve a Pokémon
rather than take immediate damage or points).

**Correction to the diagnostic's (c):** raising depth from 5 to 8 did not test genuine multi-turn planning. The search
stops at the turn boundary, or after bounded opponent replies, before searching his next turn
(engine/src/players/expectiminimax_player.rs:909 at f7e8b601), and the slow bot uses km3 to play its imagined
continuations, so more samples can reinforce km3's habits. "The tested deeper settings did not help" is supported;
"search cannot help" is not.

| Approach | Astra's assessment |
|---|---|
| More depth or isolated bonuses | Easy to extend; weak evidence another round fixes these failures. |
| Train a new generalist from scratch | Credible, but substantial engineering and unmeasured training cost; 14 positions are far from enough training evidence. |
| Test a different judge of complete plans | Best next bounded experiment: reuses the engine and recorded positions, directly challenges the current scoring; playing benefit unproven. |

Do not restrict that experiment to km3/kx3 disagreements: they can agree on the same mistake.

## C. Outside ideas

1. The DeckGym creator's Pocket-trained generalist: the closest collaboration opportunity; availability and strength
   on his decks unconfirmed. Upstream documents an external-bot interface with legal actions and hidden-information
   masking (docs/bot-protocol.md on bcollazo/deckgym-core main); compatibility with our fork still needs checking.
2. A model-assisted plan evaluator as a small experiment: give it the visible position, exact card text, the legal
   plans and their immediate consequences; test whether it judges preparation and sacrifices better. PTCG-Bench
   (arXiv 2605.29653) motivates it but studies the physical TCG and finds unstable improvement and strong dependence
   on how information is presented.
   A learned component need not need an expensive desktop to use: Unown's released Kaggle agent runs its policy on
   CPU (dipamc/kaggle-ptcg-ai-battle); training is a separate resource question.

## D. Feasibility

A useful next prototype is feasible; a dependable general-purpose deck optimizer remains an uncertain research goal.
The obstacle is how the bot evaluates and carries out plans, not a demonstrated need for more hardware. Recorded
costs (about 10 laptop hours for stage A, about $40 of API since Oct 14) justify tighter focus; his coordination and
labelling time counts too.

## One next step

Build and compare one model-assisted plan chooser on the existing engine, without letting km3's score veto its
choices. Include fresh examples where preparing, sacrificing, attacking immediately and abandoning a plan are each
correct. Agents prepare the examples and bring him only genuinely ambiguous judgments.

## Follow-up note (Astra, Oct 18 evening, after reading the coordinator's summary)

- **Technical distinction:** the tree search stops around the turn boundary. The play-outs do simulate later turns,
  but km3 chooses the moves in those futures. So the limitation is both how far the search plans and how well the
  simulated players carry out a strategy.
- **Points to preserve in the combined plan:**
  - The AI judge is a hypothesis to test, not an assumed improvement.
  - Include positions where both existing bots agree but play poorly; testing only their disagreements would miss
    shared weaknesses.
  - The week's deliverable is a runnable comparison with decisions, finished-game evidence where warranted, and
    measured cost, not another design document.
- If the two weekly reviews recommend different approaches, compare their reasoning before choosing ONE experiment;
  don't turn both into parallel projects.

Expand it only if better decisions carry into completed games against more than one opponent policy, at an
acceptable measured cost. If it only explains the old examples more convincingly: a maintenance period or the
upstream collaboration path instead of another tuning round.
