# Evidence sheet for the weekly review, week of Nov 9-15, 2026

Written by the coordinator's worker (Claude, "Multi-agent project orchestration") on Sun Nov 15 at about 21:30Z, for tonight's Claude weekly review. It is short on purpose. Full entries are in the tried-before ledger (`LEDGER.txt` and `LEDGER_INDEX.txt`, kept outside this repository). The public summary is `TRIED_BEFORE_INDEX.md`. Anything after Sunday afternoon is not in here; read it live.

## A. This week's ledger entries, one line each

- **J11, gap investigation (Nov 10-13).** The pilot does not cheat, and the engine does not set up too fast. Real tournament win rates average 46.3%, not 50. The real-on-bot slope is 0.09, so a bot 55 means about 48-51 real. The firm under-rates are Magnezone/Miraidon (-19.5), Dragonair/Rayquaza (-12.4) and Altaria/Greninja (-9.8). Part of the Magnezone gap is the build: the common Turo builds score 6-11 points higher than our field list. No general habit goes with the gap. Conclusion: no bot-score threshold picks, ranks or rejects a deck.
- **J12, gap-run table (Nov 13).** 14 runs on a second seed set and the common builds, with 0 unfinished games and 0 seed mismatches. The first field-scan numbers reproduced, for example Magnezone 38.4 +-7.6 against 38.1.
- **C10, `_y3` look-ahead on f1 (Nov 13).** Failed its test. It did not repair the Mega Burst habit: the healthy-Mega pass rate went from 83.9% to 81.8%. Wins were +1.5 / +3.6 / +2.6, and only Dragonair cleared noise. It was 2.5-4.5x slower.
- **C11, `_q1` random-target estimate (Nov 14).** Adopted for new deck-work runs, since it repairs KP13. It matches the engine on all 30 random-target printings. Gains were +2.1 +-1.3 (Noivern) and +1.9 +-1.3 (a real Mega Dragonite ex / Dragonite list). Lists without those cards play the same: 0 of 299 games differ. The play page still uses plain f1. Astra independently recounted these numbers on Nov 15.
- **C12, `_a8` setup play-outs on f1_q1, turo-1 list (Nov 14).** Failed its mechanism check, so the paired win test was not run. Miraidon ex was placed at setup 67 of 67 times in both arms, and the setups were identical in 230 of 230 games. "Keep it in hand" was compared in only 20 real decisions, all for the seat that sets up first, and the play-outs never rated it higher. The second seat never gets the option, by code. This closes one configuration, not planning in general. About 6 minutes of laptop time.
- **K9, Dedenne ex / Indeedee ex, his event games (Nov 14 count).** Mixed, and the deck is still in use. The open question is how to keep the Tool count up after Indeedee is lost. No swap is justified yet.
- **K10, Memory Light on a real Mega Dragonite ex / Dragonite list (his idea, Nov 14).** The +1 / +2 swaps lost (-2.5 / -4.8 +-1.9) with this pilot. The card itself is unproven and the entry is closed. The follow-up count found the evolve-first choice on only 2-5 of about 1,700 charging turns. When the choice existed, the bot evolved.
- **K11, Magnezone / Miraidon ex / Oricorio, turo-1 list, his event games (Nov 13-14).** Positive, and the deck is still in use. The list is identical to the C12 bot test list. His game record is in the private ledger. Win methods were corrected on Nov 15 after Astra's review (3 by knockout, 7 concessions, 2 timeouts).
  - He held Miraidon ex at setup in 3 of 3 optional cases. The bot placed it in 37 of 37 optional cases.
  - He used Legendary Drive 10 of 10 times. The bot used it 103 of 193 times. That comparison is not an error rate: the benching circumstances differ, and declining can be right because the Ability moves all Energy to Miraidon.
  - On his word, there is no broad Legendary Drive diagnosis and no fix unless he asks.

## B. His direction, Nov 14 night, with Astra's correction

- **His conclusion after C12 (verbatim):** "So basically the bot can't think/plan ahead enough, us trying to make it quickly becomes exponentially more time consuming and complicated for the bot's decision making, without some kind of major technological breakthrough or new approach, this isn't possible". This is his conclusion, not an established finding.
- **What is established, as worded the same night after Astra's review (relayed by him):**
  - This approach has not delivered the reliable unusual-deck evaluator he wanted. The goal is kept, and it remains unmet.
  - C12 rejects one configuration. It does not settle planning in general.
  - Extra search bought some things, but the targeted planning faults persisted.
  - Stop launching variations that lack a credible new reason to work.
  - Keep the simulator, the records and the narrow jobs.
  - A future proposal must say what materially changes, which recorded failure it addresses, and how its result could show useful evaluation of unusual combinations.
  - "Fast and free" is not his requirement: trustworthy play comes first.
- **Astra's Nov 15 daily agrees.** Keep the Miraidon list, close the completed tests, and publish the committed history. Do not open a Legendary Drive investigation because the usage frequencies differ.

## C. Other work this week (not bot progress)

- **Records:**
  - The public index went to 148 entries. C12 is now listed, and "_a untested" was removed in all places.
  - Four local commits are waiting for his Push origin. This sheet adds a fifth.
  - A stale `.git/index.lock` (0 bytes, no git process) was removed on Nov 15.
- **Pocket Match Log (Nov 15, his ask):** one searchable page of his 190 ranked ladder games and 303 pause games. He made it to show deckgym's creator.
  - It breaks the record down by the opponent's main Pokémon, by his deck, by Energy and by week, with an adjustable timeframe and opponent 20-card lists.
  - On his rule, Energy and Pokémon types are kept apart: Dragon is a Pokémon type, not an Energy.
  - The opponent's actual Energy comes from Codex's review records: all 303 pause games and 139 of 190 ladder games. Every pause answer was read twice, with 0 corrections.
  - Counts were checked independently against the raw logs.
  - Its scripts are in `Pocket Deck Sim/match-log/`, outside the repository.
- **Mailbox:** the daily check task now notifies the Opus session. It ran unread on Nov 15 morning, which Dustin noticed.

## D. Outside search, Nov 15 (two web searches)

- **No new public result ties DeckGym to an RL release.** The deckgym-core engine can export (state, action) pairs as JSON for policy, value or imitation training.
  - https://github.com/bcollazo/deckgym-core
  - https://www.deckgym.com/
- **An Inven Global article (about 113 days old) describes an RL agent for TCG Pocket.** It ran 50 million episodes per model and does not read card text. The snippet does not say which engine it used; not checked further.
  - https://www.invenglobal.com/articles/24133/how-reinforcement-learning-ai-tackles-the-complex-rules-of-pok%C3%A9mon-trading-card-game-pocket
- **Other Pocket engines:** sethkarten/tcg is a C engine with Python bindings and PPO self-play. Pocket Showdown is a community simulator with deck analysis.
  - https://github.com/sethkarten/tcg
- **The Pokémon Company's Kaggle AI Battle Challenge** (physical TCG, about 2,000 cards, phases June-September 2026, finals in Japan) has Simulation and Strategy tracks.
  - https://www.kaggle.com/competitions/pokemon-tcg-ai-battle
- **PTCG-Bench** (LLM agents on the physical TCG) is already in the Nov 1 outside-research note.
- **Nothing found changes the direction above.** No 2026 source was found on planning or search for Pocket bots specifically.

## E. Not done

- The upstream watch (`tools/upstream_watch.py`) was not run for this sheet.
- The Google credits re-check that was due Nov 15 was not done by this worker.
