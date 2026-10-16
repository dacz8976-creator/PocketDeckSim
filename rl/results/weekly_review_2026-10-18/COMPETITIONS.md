# Competition methods that might help PocketDeckSim

Researched October 16, 2026 for the October 18 weekly review. This fills the competition gap in [OUTSIDE_IDEAS.md](OUTSIDE_IDEAS.md), read at main `b136facb`. No programs, training, simulations or paid inference were run. This document proposes a comparison; it does not authorize one.

## What this changes for Dustin

The goal remains a bot that can test and improve decks Dustin enjoys. **There is useful outside evidence, but no ready-made replacement that can be cheaply matched against km3.** The leading Kaggle entries play the physical card game, not Pocket. PokéAgent plays the video games. Their policies, card representations and trained weights are not interchangeable with ours.

The encouraging result is that small learned policies achieved strong competition results, and one leading entry publishes its exact CPU-only submitted agent. Expensive training and inexpensive use are different questions. The difficult part for us is obtaining a policy trained for Pocket that understands Dustin's plans, not merely fitting a network into memory.

These findings also weaken the survey's certainty that our existing search-plus-hand-written-score architecture should be retained. The competition does not establish that claim. It supplies alternatives worth considering, without establishing that a rewrite would help us.

## Which results were actually verified

The official **final Simulation leaderboard** lists **Luca first, palsystem second, and Unown Gradiant third**, with ratings 1398.2, 1297.8 and 1280.5. The rendered page was read directly after the text-only reader returned an empty page. These are ratings against other submitted agents and their chosen decks, not human win rates or isolated measures of pilot quality. [Final Simulation leaderboard](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/leaderboard?episodeId=82017244&submissionId=54072877)

The separate **Strategy category** judges reports as well as performance. Its writeups currently show Main Track prize badges for Luca first, Unown second and palsystem third. The `/winners` page did not render successfully, so this is a report of the visible badges, not verification of a complete award list. Neither set of placements establishes the winner of the later in-person second round. The organizer describes a 60-card game using a designated physical-TCG card pool and a later best-of-three final. The older survey's reference to September finals should not be relied on. [Organizer's rules and schedule](https://ptcg-abc.pokemon.co.jp/?lang=en)

## Kaggle's top three: methods, evidence and availability

All measurements below are the entrants' reported experiments, not experiments independently rerun here. PPO is reinforcement learning from played games; a policy scores the available moves. A Transformer is the network used to represent the board and choices. AI coding assistance is not an AI language model choosing moves during play.

### 1. Luca

- **Method:** a 2.24-million-parameter Transformer trained through four stages of self-play PPO, moving from broad deck experience to fixed Dragapult specialists. This is primarily a learned policy, not an LLM pilot.
- **Evidence:** first on the Simulation ladder. Its local arena used 256 games per opposing archetype and examined matchups, counter-decks and card swaps. Those checks do not establish human-level play or generalization to arbitrary creative decks.
- **Training:** four RTX 5090 GPUs, with C++ simulation and JAX learning. Reproducing that training is not a CPU-laptop job.

[Luca's full writeup](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1784257142000)

**Availability:** the author's repository currently contains figures and supporting spreadsheets, with code promised after the second round. No runnable agent, weights or repository license was found. The writeup's MIT label does not make unpublished code available. CPU latency and total memory are unconfirmed. Repository snapshot: `5b6d99c5a425849e4686df0197af98ab50d84f68`. [Repository](https://github.com/yijieyuan/kaggle-pokemon-tcg)

### 2. palsystem

- **Method:** a 2.4-million-parameter Transformer learned across 3,341 decks, followed by a Crustle/Mega Kangaskhan specialist. Before scoring moves, it simulates legal choices and follow-up selections to describe their consequences. It stops at unknown information or an opponent decision. This is learned choice informed by short simulations, not a language-model pilot or three-turn search.
- **Evidence:** second on the Simulation ladder. A controlled comparison of deeper consequence features reported roughly two percentage points more wins across training checkpoints. This was not a multi-seed replication. Specialist checks used 256 games per matchup against a fixed generalist, with alternating seats. Local/public matchup correlation was 0.30 broadly and 0.75 for its specialist; local win rates generally ran high.
- **Training:** about 12 billion generalist steps plus 4.2 billion specialist steps, using eight RTX 5090 GPUs. Not a laptop training recipe.
- **Availability:** the writeup links deck CSVs, but no agent code or weights was found. Its MIT notice licenses the writeup, not an independently verified code release. Full CPU/RAM requirements remain unknown.

[palsystem's full writeup](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/new-writeup-1788449799640)

### 3. Unown Gradiant

- **Method:** a roughly 4.4-million-parameter policy using attention to score legal actions, trained with self-play PPO across roughly 500 decks. An LLM assisted deck-swap suggestions; it was not the move-by-move pilot.
- **Evidence:** third on the Simulation ladder, plus a fixed six-deck development battery and matchup comparisons. Those are relevant competitive results, not Pocket results.
- **Training:** roughly six billion steps on a rented eight-RTX-3090 machine. That recipe is not practical on this laptop.

[Unown Gradiant's full writeup](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle-challenge-strategy/writeups/team-unown-gradiant-solution-all-decks-on-hand)

**The most usable public release:** its MIT-licensed repository includes submitted code, deck, supporting tables and `submission/model.pt`, verified as **19,534,121 bytes, about 18.6 MiB**. The submitted `main.py` specifies `device="cpu"`, `cfg=None` and greedy choices. Despite the class name `SearchAgent`, this final bundle does not run the optional search found elsewhere in the repository. Do not credit later code with the competition result. The exact submitted runtime is kept separately from newer development code. [Submitted bundle and instructions](https://github.com/dipamc/kaggle-ptcg-ai-battle/tree/main/submission), [entry point](https://github.com/dipamc/kaggle-ptcg-ai-battle/blob/main/submission/main.py), [MIT license](https://github.com/dipamc/kaggle-ptcg-ai-battle/blob/main/LICENSE)

The repository documents CPU evaluation, but requires separate competition SDK and card-data downloads. I verified the checkpoint's presence and size without downloading or executing it. The repository has an MIT license and no separate checkpoint license was found; the external engine and Pokémon assets retain separate terms. Snapshot: `a176778d99da74a44b495bf19299b4795faf12f2`. [Repository and requirements](https://github.com/dipamc/kaggle-ptcg-ai-battle)

**Laptop verdict:** using this existing agent in its own game looks plausible; 7.6 GB total memory use and actual latency remain unmeasured. A small checkpoint is not proof the complete installation fits. Training requires NVIDIA/CUDA tooling. Its weights encode a different game and cannot be installed as a km3 replacement.

### Two additional writeups that check the interpretation

The **15th-place** entrant used a 7.5-million-parameter recurrent policy, population self-play and direct move selection, without runtime search or card-specific overrides. It reports about 5.5 billion decisions and roughly five RTX-4090 GPU-days. Same-deck, swapped-seat tests supported improvement, but the author still observed missed actions and unfinished plans. No code/weights release was linked in that writeup; a reusable license and laptop memory use were not established. Stronger results did not eliminate strategic mistakes. [15th-place writeup, read in full](https://www.kaggle.com/competitions/pokemon-tcg-ai-battle/writeups/15th-place-solution)

The **12th-place** entrant publishes a 20-million-parameter learning pipeline and reports generalist training plus deck specialists. It used about 11 billion generalist steps and four H200 GPUs, with frozen-policy comparisons as well as the competition ladder. The repository listing contained no checkpoint or license file when checked, so public source should not be treated as licensed reusable software or a downloadable trained pilot. Snapshot: `4fbf2c5d855061fb220db0110a55906118fd16e6`. [Repository](https://github.com/Michal1337/pkmn-kaggle), [full writeup](https://github.com/Michal1337/pkmn-kaggle/blob/main/WRITEUP.md)

## PokéAgent: useful ideas, but no card-game track

The official challenge and results paper describe **Showdown competitive battles and Pokémon Emerald speedrunning**, not TCG or Pocket. I found no card-game entry to import. [Official battling track](https://pokeagentchallenge.com/battling.html), [speedrunning track](https://pokeagentchallenge.com/speedrunning.html)

Two winners are relevant as method examples:

| Entry | Method and measured result | Public availability and laptop assessment |
|---|---|---|
| **FoulPlay, Gen 9 OU winner** | Selective tree search, a hand-written evaluator, grouped random outcomes and sampled hidden opponent sets. Won its final **50–14 against Team Q**. | [FoulPlay code](https://github.com/pmariglia/foul-play) is GPL-3.0; [its Rust battle engine](https://github.com/pmariglia/poke-engine) is MIT. No trained network is needed. CPU search is plausible, but no 7.6 GB measurement or relevant Pocket timing was found. It requires its Showdown-specific simulator and rules. |
| **PA-Agent, Gen 1 OU winner** | Repeated offline learning from collected play, using Metamon as its foundation; won its final **50–28 against 4thLesson**. | [Code](https://github.com/PolarisShi/pokeagent) is MIT and links trained weights via Baidu. The linked weight download and its separate license were not verified. Pocket compatibility and 7.6 GB memory use are unconfirmed. Reproducing its data and training pipeline is not a small laptop experiment. |

The competition paper supplies these final scores and method descriptions. They measure agents against agents in specific video-game formats. Neither result demonstrates performance against Pocket players. [Results and entrant methods, especially appendices B and E](https://arxiv.org/html/2603.15563)

The transferable FoulPlay idea is spending search effort on strategically different futures, rather than expanding every random outcome separately. This is an analogy to test, not permission to merge Pocket outcomes with different card effects. That could matter for our long plans, but implementing a faithful imperfect-information search is a larger project than the small comparison below. Its existence also prevents a simplistic conclusion that learned policies always beat hand-written search.

## One small comparison worth considering

**No external entrant can fairly play km3 as-is.** Running Unown's checkpoint against its own game's opponents would check installation, not help Dustin choose a Pocket deck. Porting an engine, card vocabulary and trained policy would not be a cheap test.

The smallest useful borrowed idea is **palsystem's action-consequence representation**: ensure a proposed move includes its targets and subsequent public choices before judging it. Our own-turn search already explores sequences, so this is not a recommendation to add generic lookahead again. First identify whether a missed plan is lost because a consequence never reaches the evaluator, the evaluator values it badly, or the payoff lies beyond the opponent's reply. The last case needs a planning, opponent-model or future-value change. A same-turn representation patch cannot solve it.

Proposed bounded comparison, within a future approved pilot round:

1. Use existing permitted development positions to inspect Energy placement, Bench preparation and delayed attacks. For each, show km3's legal candidates, the resolved state each candidate reaches, and where the useful line disappears. Use the same public information a player has. Do not reveal the actual unseen draw to the selector.
2. If a concrete missing consequence is found, prototype only that general representation change in a separately named candidate. Compare it with unchanged km3 and frozen kx3 on a small, fresh set of whole-game-derived positions. Include positions where waiting is right and where attacking immediately is right. Record acceptable alternatives before the candidate answers; matching Dustin's exact move is not the only valid outcome.
3. **It helps at this stage** if it repairs that mechanism on unseen positions without breaking the opposite cases. If both bots already see the same consequences, the payoff requires later turns, or only the taught examples improve, stop this representation idea. A substantive planning or learned-evaluation prototype remains an option; it does not have to pass through a successful small patch first.
4. A later strength claim needs completed play: same deck and engine, paired deals and both seats, with more than one fixed opponent policy. Report the paired uncertainty, planning behavior and actual runtime. An interval spanning zero remains inconclusive. This would still not establish ladder calibration or reliable deck-variant rankings.

This proposal needs no new GPU or LLM API, and should reuse the existing position harness. Implementation time and memory are **not measured**; if it requires building a training pipeline or porting CABT, it is no longer this small test. The currently registered experiments keep their existing rules.

## Recommendation for Sunday's decision

**Keep pursuing a better Pocket pilot, but do not treat either the present architecture or a large RL rewrite as proven.** Compare the released action representations and search ideas with our actual failure traces. Choose one bounded prototype around the failure that comparison identifies. That may mean changing multi-turn planning or learning an evaluator, not another small correction to km3.

The competition evidence makes a learned component a credible direction, not a laptop-ready solution. No new practical deck improvement was delivered by this research. Its useful result is a verified set of leading methods, one genuinely public CPU agent to study, and clear reasons not to spend a week trying to plug a different game's model into km3.

## Verification limits

- Read the three leading Kaggle writeups in the rendered browser, the final Simulation leaderboard, the organizer's rules, the PokéAgent results paper and linked repositories. Checked public file listings and licenses; did not execute entrants' code or reproduce their experiments.
- The Strategy winners route was unavailable. Writeup prize badges were visible, as distinguished above. CPU capacity estimates are engineering judgments, not measured benchmarks.
- Existing project evidence was limited to the mission, current survey/evidence sheet and already permitted design records. No reserved confirmation outcomes were opened.
- This document supersedes only the competition-gap claims in the survey. It does not modify that file, the release, the pilot defaults or any adoption decision.
