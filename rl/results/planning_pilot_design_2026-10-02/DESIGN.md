# A pilot built for playing strength: design note (Oct 2)

For Dustin: about ten minutes. The details are in two appendices in this folder:
- `APPENDIX_EVIDENCE.md`: the code read of km3, the evidence, and the full account of past failures. It is the first draft of this note; its recommendation is superseded, but its evidence stands.
- `APPENDIX_COSTS.md`: the arithmetic behind every time and money figure.

Numbers marked [estimate] haven't been measured. Nothing new was built or played for this note.

## 1. The goal, in your words

The simulator should save your hours by telling you which decks are worth your own 10-minute games. So trustworthy
playing quality comes first. Speed and game counts are not requirements. For each option the note gives the time and
money, and you decide whether it's worth it: "Prioritize trustworthy playing quality. Report the time and cost needed
to achieve it, and let me decide whether that tradeoff is worthwhile."

"Trustworthy" is defined by four things the bot must do with any deck (Astra's milestones):
- prepare attackers;
- manage sacrifices;
- recognise immediate wins;
- adapt when its first plan stops working.

The official engine (main-8626a35) and km3 stay the reference. The new pilot lives on an experimental branch and
replaces nothing until you say so.

## 2. What km3 gets wrong

**From the code** (`APPENDIX_EVIDENCE.md` section 1):
- **It looks ahead only three actions.** A turn averages about 7 decisions (69.4 per game over 2,000 games).
- **It never looks at the opponent's turn.** A knockout on its Active next turn is invisible unless it ends the game.
- **Its score pays mainly for the Active being ready to attack now.**
  - An Energy on a Benched attacker is worth about a third to a fifth of the same Energy on the Active.
  - A ready backup attacker is worth nothing.
  - Nothing charges it for leaving a powered-up Pokémon in front of a knockout.

**From your own turns.** Sonnet rebuilt 34 positions from your draft A pause games and asked km3 at each one
(`results/pause_games_decisions_2026-10-02/`, TABLES.md):
- **Immediate wins:** it found all three.
- **Attacks:** where both of you attacked, it chose the same attack as you in 21 of 22 turns.
- **The differences are mostly around the attack:**
  - which Supporter, and in what order (it played Irida on 11 turns where you didn't);
  - retreat and promotion order (4 turns);
  - the order of identical actions (Lucky Ice Pop heals the Active, so retreating first healed Lapras instead of the Mega Sharpedo ex).
- **Turbo Shark's Bench target is close to a coin toss for it.** The targets differ by 10-50 points in its score, against 100-1,400 for a different first action. It matched your target in 2 of 4 real choices.

**Two cautions from Astra.**
- The "Bench Energy undervalued 3-5x" figure compares km3's own numbers with each other. Nobody knows the right value.
- The detector networks' big gains were specialised: Hydreigon +25.2 and Altaria about +15.8 over kp3, each in its
  own matchup only. Some earlier candidates really were worse, not just blocked by a thin table. For example, kpr3 moved
  its habit and scored 48.8% head to head against kp3.

## 3. Why speed used to be a requirement (your question)

Nobody decided it for you. It came from the method, in three ways:
1. **The engine came from upstream deckgym.** It was built for bots that play millions of fast games for training.
2. **The project's accuracy yardstick needed huge game counts.** Every candidate pilot was judged on 45 Limitless
   matchups at 1,000 games each, plus gates. Telling a 1-2 point change apart takes tens of thousands of games per
   candidate, so a candidate had to be cheap. Run 6's network design even set "no more than 3x k3's time" as a target
   (`rl/RUN5.md:102-103`).
3. **So the cheap kind of change won by default.** That meant hand-set scoring terms, at about km3's speed.

**What it cost.**
- The slow kinds of pilot were never candidates:
  - The play-out method below was used only as a diagnostic.
  - The search that looked at the opponent's reply (b3o3n4, about 16-17x k3's time) was read only on the Limitless table, never on playing strength.
- Most of the effort went into cheap terms that moved a habit without making the bot play better: kq3, kpr3, koh and kd3 (`APPENDIX_EVIDENCE.md` section 6).

## 4. The options, honestly

"Shown here" means a result in this repo. Everything else is unmeasured. Money is the API bill. Local options cost
electricity only. A "deck question" is one deck's result against the panel to about ±5 points (about 400 games; ±10
needs about 100 and ±3 about 1,070). Times are [estimates] until week 1 measures them.

| Option | What it is | Shown here | Not known yet | To a first runnable version | Time and money per deck question (±5) |
|---|---|---|---|---|---|
| **Play-out chooser** (recommended) | At each real choice, play km3's top moves out to the end of the game many times, with unseen cards drawn at random, and keep the move that wins most | Play-outs from real positions priced exactly your habits (below) | Whole games played this way; strength against km3 | 3-4 days after Monday | 1-13 laptop hours; $0 |
| **Fitted scoring formula** | km3's search with new terms (ready backup, evolution value, exposed Active), weights fitted by self-play | The holes it targets (the code read). No term of this kind has made the bot stronger yet; kq3 and kpr3 moved habits and played decks worse | Whether fitted weights do better than hand-set ones | 1-2 weeks, including fit nights | minutes; $0 |
| **Two-turn search** | My turn, a modelled reply by the opponent's visible board, then my next turn | Nothing on strength (b3o3n4 was read on Limitless only) | Everything | about 10 days | under an hour; $0 |
| **LLM pilot** | A Claude model picks from the engine's legal moves, given card texts, rules and computed damage | Nothing here. The strength harness can already run one and record its cost | Strength; arithmetic slips; game-to-game variation | 3-5 days | several hours; about $76-164 (Haiku), $148-328 (Sonnet), $292-652 (Opus) |
| **Learned network** | A network trained on card descriptions, used as km3's leaf score | Detector networks beat kp3 in their own matchups. None has ever transferred to an unseen deck | Transfer | 2-3 weeks or more | minutes; $0 |
| **Hybrids** | A slow pilot gives the verdicts or teaches a fast one | — | — | after one of the above exists | depends |

## 5. Recommendation: the play-out chooser, on top of km3

**What it is.**
- km3 still proposes moves. At each of the bot's own decisions with real alternatives, the bot takes km3's best few
  moves and plays each one out to the end of the game many times (16-32 [estimate]), with km3 on both sides.
- In each play-out, the cards it can't see (the opponent's hand and deck, its own deck order, coins) are drawn at
  random from what could be there.
- Every candidate move gets the same random draws, so the comparison is fair.
- It keeps the move that wins most. When the difference is within the noise, it keeps km3's move.

**Why this one first.**
1. **It's the only option whose core has already worked here, on exactly your complaints.** Play-outs from real
   positions priced the Lucario network's better moves:
   - attacking instead of retreating: +15.4 points (+8.4 to +22.4);
   - the network's moves overall: +3.0 ± 1.0 per position where it differed;
   - "a sacrificial front Pokémon while building the real attacker behind it";
   - Altaria's opening Active: +19.4 ± 4.6
   (`results/lucario_network_divergence_2026-09-25/README.md:15-51`; `results/altaria_network_divergence_2026-09-26/RESULT.md:4-6`).
2. **It sees the opponent's turn and its own next turn by playing them.** "Attack now, or take a hit and attack next
   turn" is answered by what happens, not by a number someone chose. That is Astra's next-turn planning requirement.
3. **No hand-set numbers.** The failures in section 3 were hand-set terms.
4. **It treats every kind of decision the same way,** including the ones Sonnet found: which Supporter, retreat order,
   and the order of identical actions.
5. **The parts exist:**
   - `engine/examples/net_divergence.rs` has the play-out code;
   - `engine/src/players/list_aware_player.rs` draws hidden cards from a list.
   - About 300-500 new lines [estimate].
   - Same deals give the same games. The money cost is $0.

**What could go wrong.**
- **The play-outs are played by km3,** so later turns carry km3's habits. A plan that needs several good turns in a row
  can still be undervalued.
- **Close choices are noisy.** It falls back to km3's move then, so a small gain may not show.
- **It needs the opponent's 20-card list** to draw their hidden cards. That's the information you have once you
  recognise a deck. It never sees their actual hand or deck order. km3 doesn't use the list today, so this is part of
  the decision below.
- **It's slow:** from about 6 seconds to about 2 minutes a game on the laptop, depending on how many decisions get
  play-outs [estimate]. Week 1 measures it.
- **It may not be stronger.** If its games against km3 show no gain on the development decks, and its choices on your
  positions don't move toward yours, it is the wrong first prototype. In that case, the next step is the two-turn
  search or the LLM pilot, with their measured costs.

## 6. How it will be judged

**Development and the final exam are kept apart** (Astra).
- **Development:**
  - three fast decks and three slow ones of yours, picked by game length on the floor: Manectric, Mega Blaziken and Xatu/Weezing; Wailord, Muk and Indeedee/Stoutland;
  - plus draft A;
  - against the 8 panel lists.
- **The final exam:**
  - your other 9 decks, drafts C and D, and a quarter of the pause-game positions;
  - locked in the harness, so a development run can't touch them;
  - run once, after the prototype is frozen.

**Three yardsticks, read separately.**
1. **Strength against km3.** Same deals, both seats, in Sonnet's harness (`rl/strength/`, on main; it replays the
   official km3 game for game).
   - Every deck's row is printed, with its interval and the time per game.
   - A deck that gets worse is reported to you, not hidden and not a veto.
2. **Decisions on real positions.**
   - Your 34 pause-game positions (tagged: preparing an attacker 18, a sacrifice 7, an immediate win 3, adapting 2)
     and the 55 quiz positions.
   - Then a new blind quiz built from the positions where the prototype and km3 disagree. That's the natural first
     thing to ask you once it runs.
3. **The game's Auto pilot, a tier between km3 and you.**
   - On positions rebuilt from recordings where Auto plays a deck, compare Auto's choice with km3's, the prototype's,
     and yours where you played the same deck.
   - **What it can show:** how often the bots agree with Auto on the same positions.
   - **What it can't show:** head-to-head strength, since our bot can't play the game's bot. We also don't know yet
     how good Auto is.
   - So "as good as Auto" is a floor we can measure, not proof of competence. Sonnet is counting the Auto recordings
     that exist and will build them as a separate position set.

**Line rates** (does Turbo Shark arm the Bench by turn 3, and so on) are printed as a footprint only. They never count as
a gain: kq3 and kpr3 changed their habits and still played worse.

**What's missing for the four milestones.**
- "Immediate wins" (3 positions) and "adapting" (2) are thin.
- Every pause-game position is draft A, an aggro deck. The slow decks have almost none.
- Sonnet builds the missing positions from recordings: it already has the position builder. That replaces the
  "cloud data pipeline" in the earlier routing; this prototype needs no training data. The cloud writes the
  prototype's code instead.

## 7. The first week (respecting the token budget)

| When | What | Who |
|---|---|---|
| Now to Mon 7 am | No coding. Your optional recordings (section 8) if you want to do them this weekend | you |
| Mon Oct 5, after the reset | Write the prototype on an experimental branch, with unit tests. km3 untouched | cloud (one paste block) |
| Tue Oct 6 | One review and its fixes. Laptop build. km3 must reproduce its pinned self-check and the official games | cloud, laptop |
| Wed Oct 7 (no class) | The prototype on the 34 positions (examples of how it decides differently). Overnight: a development run against km3, sized from the measured time per game, left unattended | laptop |
| Thu Oct 8 | Read the run. Build the blind quiz from its disagreements with km3 | laptop, Sonnet |
| Fri Oct 9 | To you: the runnable prototype, examples of its decisions, its strength against km3 with intervals, and its time per game | laptop |

The next real update to you is that prototype with evidence, not another document.

**Rough token cost to build it:** about 3-5 million tokens of agent work, mostly re-reading engine code during the build
and its one review [estimate]. For scale, today's first design workflow used about 1.8 million. The game runs cost
laptop time, not tokens.

## 8. What I need from you

**The one decision.** Go on the play-out chooser as the first prototype? It would know the opponent's 20-card list,
but never their hand or deck order. It would be built after Monday's reset, unless you'd rather it start sooner.

**Optional, since you offered: the smallest set of recordings that fills the gaps.**
- **Four games, about an hour with recording:**
  - two with Wailord (a slow deck with no positions yet): one played by you, one by the game's Auto;
  - two with Manectric (fast): one you, one Auto.
- **Each video should show:**
  - your hand at the start of every turn;
  - every card drawn, by name;
  - the plays in their exact order;
  - the opponent's hand size.
- If Sonnet's count finds Auto recordings with these decks already, those games drop off this list.

## 9. Addendum: approved, with amendments (Oct 2)

Dustin, verbatim: "I approve the build now." Adopted with the approval (the coordinator's amendments and Astra's points).
Where they differ from sections 5-8, they win:
1. **Candidates.** Every distinct legal first action where practical, not only km3's best few.
2. **Information.** The pilot knows only what its side may know.
   - Giving it the opponent's exact 20-card list (section 5) is a labelled laboratory condition, not the realistic setting.
   - Realistic brew testing needs uncertainty about the opponent's list: recognising an archetype doesn't reveal its 20 cards.
   - The meta side is never handed the brew's exact list.
3. **No leak.** Every play-out starts from a state sampled from what the pilot may see. `engine/examples/net_divergence.rs` starts its play-outs from the real saved state, hidden cards included; the pilot must not.
4. **Coordinated plans.** The first demonstrations include a plan that needs several coordinated decisions: charge a Benched attacker, keep a sacrificial Active, promote at the right time. That shows whether km3's later mistakes inside the play-outs hide good first moves (the first risk in section 5).
5. **Reporting.** The 34 pause-game positions are development examples, not an exam. Agreement with Auto doesn't establish Auto-level strength.
6. **Both sides of the result.** The report brings back examples of improved decisions and of remaining failures.

Who does what:
- The cloud writes the code on `claude/playout-pilot`.
- The laptop reviews it once, then builds it beside the pinned engine. km3 in that build must reproduce the pinned self-check and the official games.
- It then runs on the development positions, and the laptop sizes and launches the unattended development run in the strength harness. The harness's groups and the locked list are filled (`rl/strength/`, 8521b291).

---

## Appendix: what the strength harness needs (for Sonnet)

- **`groups.json`:**
  - "aggro": 09-mega-manectric-heliolisk, 06-mega-blaziken-tournament-list, 10-xatu-oricorio-tr-weezing (the three shortest average games on the Sept 30 floor: 8.4, 8.9 and 9.4 turns);
  - "setup": 03-wailord-indeedee-wall, 01-muk-glimmora-kingambit-regigigas, 05-indeedee-stoutland (the three longest: 15.5, 12.9 and 11.2 turns).
  - Draft A joins development through its positions and as a deck.
  - Deck 07 has no floor games of its own, so it isn't labelled.
- **`heldout.json` (locked):** 02-arceus-crobat, 04-absol-hoopa-darkrai, 07-skarmory-stall, 08-garchomp-toolbox,
  11-archaludon-haxorus-dragonair, 12-ariados-whimsicott-ogerpon, 13-a-ninetales-raticate, 14-comfey-raticate-hypno,
  15-jolteon-oricorio-raticate, draft-C-meowstic-hatterene-v2, draft-D-entei-grimhound. Draft B stays set aside.
- **`intended_lines.json`:** keep the current lines (Turbo Shark by own turn 3; Eevee Active on own turn 1; Hyper Ray
  without a knockout; Thieving Incisors). Add two card-agnostic lines for every deck ("*"), if the trace can carry them:
  - **exposed Active:** an own turn ends with a 2- or 3-point Pokémon Active that can't attack on its next turn even
    with one more Energy, while a Benched Pokémon could;
  - **ready backup:** at each promotion after a knockout, whether a Benched Pokémon could attack that same turn.
  - Both need the board at those moments, which may mean a new counter kind. Build them after the reset; they are
    footprint only.
