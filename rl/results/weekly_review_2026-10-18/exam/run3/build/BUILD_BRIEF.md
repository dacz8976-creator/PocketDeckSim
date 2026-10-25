# Exam v2: how to build a position (the builders' and verifiers' brief)

You are building positions for exam v2 (run 3) of Dustin's PocketDeckSim project. The game is Pokémon TCG Pocket, the mobile game, which is not the physical TCG; read `/home/dacz8976/exam_v2/inv_in_p1/RULES_FOR_AGENTS.md` first.

Each point is one of Dustin's real ranked turns. You build the position at the START of that turn (after his draw for the turn, before his first action), plus his whole recorded move for that turn, as engine labels. Later, bots and an AI judge are tested on these positions, and a separate labeller writes the answer key. **The positions must be exactly what the game showed him, no more and no less.**

## Hard rules (they protect the exam; breaking one can void it)
- **Read only these:**
  - `/home/dacz8976/exam_v2/build/` (this brief, `v2_helpers.py`, the tools, `batches.json`);
  - `/home/dacz8976/exam_v2/decks/` (his exact lists);
  - your games' folders `/home/dacz8976/exam_v2/inv_in_p<k>/sources/<game>/`, as `batches.json` names them;
  - `/home/dacz8976/exam_v2/inv_in_p<k>/window.json`;
  - `RULES_FOR_AGENTS.md` (above).
  Text files only, never images or videos.
- **Never open:**
  - `/home/dacz8976/exam_v2/inv_out_p*`, `selcode_out_p*`, `selcode_in_p*/turns.json`, `select/agreement.json` (the usability codings);
  - `/home/dacz8976/exam_v2/snapshot/`, `/home/dacz8976/exam/` (the earlier exam), `~/exam_run1/`, `~/exam_run2/`;
  - anything under `rl/results/weekly_review_2026-10-18/` or `rl/ai_judge/`;
  - the agent mailbox, any `.MOV`, any other batch's games.
- **Write only:**
  - `/home/dacz8976/exam_v2/build/g/g<game>.py` for YOUR games;
  - `/home/dacz8976/exam_v2/build/drops/<point id>.txt`;
  - files under `/home/dacz8976/exam_v2/build/scratch/b<batch>/`.
- **No bots.** No git, no cargo. Never run pg_pos or any bot or judge. The only engine tool is `pg_legal_v14`, through `check_game.py`, and it lists legal moves only. Never set DECKGYM_* variables, never print environment variables or keys, no subagents.
- **Never judge his play.** Don't say what he should have done, what was good or bad, or what the turn is "about". The answer kind and the acceptable alternatives are not your job.
- **No hidden future.** The position holds only what he could know at the start of the turn:
  - no deck order, no next draw, no coin result;
  - no opponent's hand cards (only their count);
  - nothing that was revealed later.

## How to run things (Windows host, WSL Ubuntu)
- **Files:** read and write them with the Read and Write tools through UNC paths, e.g. `\\wsl.localhost\Ubuntu\home\dacz8976\exam_v2\build\g\g20261016_184635000_SR.py`.
- **Commands,** from PowerShell (no quotes needed):
  - `wsl python3 -B /home/dacz8976/exam_v2/build/check_game.py 20261016_184635000_SR`: check one game's build file;
  - `wsl python3 -B /home/dacz8976/exam_v2/build/check_game.py 20261016_184635000_SR --show`: also print every step's legal list and the engine's summary of the position (to find a label, or to see how the engine read it);
  - `wsl python3 -B /home/dacz8976/exam_v2/build/cards.py mega gyarados`: cards whose name has all these words, with HP, type, weakness, retreat, evolves-from, Ability and attacks;
  - `wsl python3 -B /home/dacz8976/exam_v2/build/cards.py --deck v2deck_589bb9927a`: his list, each card in full;
  - `wsl python3 -B /home/dacz8976/exam_v2/build/cards.py --id B1 016`: one card by its set id.
- **Quoting:** inline `wsl bash -c "..."` with `$`, quotes, apostrophes or parentheses breaks under PowerShell. Write a script into your scratch folder and run `wsl bash /home/dacz8976/exam_v2/build/scratch/b<N>/x.sh` instead. Search card names without apostrophes (`cards.py professor research`).

**The tools touch a few places outside your read list, and that is expected:**
- `check_game.py` runs `/home/dacz8976/exam/bin/pg_legal_v14`, the legal-moves tool. Its crash messages name `examples/pg_pos.rs`, the source it is built from in legal-only mode; no bot runs.
- It reads `/home/dacz8976/exam_v2/select/selection.json` (the list of points) and `/home/dacz8976/exam_v2/bin/decks.args`.

Don't open those yourself.

## Your inputs, per game (`batches.json` → your batch)
- **The game's folder** holds:
  - `REVIEW.md`, Codex's account of the whole battle, turn by turn;
  - `UNCERTAINTIES.json`;
  - `LEAD_ACCEPTANCE.json`;
  - `LADDER_ENTRY.json`, where present;
  - the QR file of his deck code (`QR_ID.json` or `QR_DECODE.json`). Ignore the QR file's printings and any `equivalent_base_card`: his printings are the deck file's.
- **A battle recorded in two clips** has `clip01_…/` and `clip02_…/` and `CLIPS.json`. In all three such battles here, the clips' REVIEW.md is ONE review of the whole battle (`CLIPS.json` says so): read it once and count every turn once.
- **The game's deck key** (`deck`, e.g. `v2deck_589bb9927a`) names his exact list: `/home/dacz8976/exam_v2/decks/<deck>.txt`. Every card of his you name must be one of that list's printings. The list's first line gives its Energy types.
- **The points:** each is `LAD-<game>-t<n>`, where n is the game's ONE global turn count. That is the game's own turn counter, both players' turns, starting at 1 for the first player's first turn. Build exactly these turns, and every one of them.

## Conventions (settled by the pilot build, Oct 25; follow them so all builders agree)
1. **The Bench is compacted.** The position format holds no empty slot: a `None` in `board` crashes the tool, and a `slot` key is ignored.
   - List his and the opponent's Benched Pokémon left to right as the review shows them at the start of the turn, with no gaps. If the review doesn't give the arrangement, list them in the order they were benched.
   - A `Place:<X>@<n>` in his move uses the LOWEST empty slot, whatever spot the game showed. Say so in `notes` when the review names another spot.
   - The `"slot"` in `--show`'s engine summary is output only.
2. **Hidden searches in the opponent's hand count.** Count a hidden Poké Ball or other search as +1 card, unless the review shows it found nothing, and say so in `approx`. Count a draw by the number of cards it draws.
3. **Printings the review can't separate.** This covers cards that differ only in art (A2b 008 / A2b 099), and the opponent's Trainers in his discard. Use the printing `cards.py <name>` lists FIRST among those matching every shown fact: name, HP, and attack and Ability titles. Name the choice in `ambiguous` when more than one printing matches. His own cards always use his list's printing.
4. **The opponent's next Energy (`zone`)** is set only from what the review shows at or before the start of the turn, never from a later turn.
5. **Attack follow-ups.**
   - An attack's own target choice (which Benched Pokémon to hit, when the engine asks) is a label in `force`, right after the `Attack:...` label. Take it from `--show`'s legal list.
   - Never write `ApplyQueuedAttackDamage`.
   - Never write an `EndTurn` after an attack that ends the turn.
6. **Duplicate legal labels** (`Play:Deceptive Needle` listed twice with two in hand) are the same action; write the label once per play.
7. **Your scratch folder** is `scratch/b<your batch number>/` (verifiers: `scratch/v<batch number>/`).

## The build file: `/home/dacz8976/exam_v2/build/g/g<game>.py`
One file per game, defining `POS`, a list with one `P(...)` per point, in turn order:

```python
from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261024_181948000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; PB = 'Poké Ball P-A 005'   # his cards, as his list names them
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 5, 3, [1, 0],
  dict(hand=[PB, WT, 'Copycat B1 225'], disc=['Professor\'s Research P-A 007'], dene='', board=[B(SQ, 60, 'W'), B('Eiscue B1 080', 80)], ko=0),
  dict(hand_count=4, disc=['Poké Ball P-A 005'], dene='', board=[B('Pikachu ex A1 096', 90, 'LL')], ko=1),
  ['Play:Poké Ball', 'Evolve:Wartortle@0', 'Attach:1Water@0 zone', 'Attack:Waterfall'],
  D, None, approx=AP, draws={0: ['Squirtle P-A 033']},
  notes='Turn 5 (his 3rd): ... (cite the review lines you used; build-only, never shown)'),
]
```

**`P(game, turn_count, his_turn, points, me, opp, force, deck, kind, stadium=None, approx=None, ambiguous=None, notes="", draws=None, vpatch=None, ez_now=None, ez_next=None)`**
- **`turn_count`:** the global turn (n in the point id). **`his_turn`:** his own turn number (his 1st, 2nd, ... turn).
- **`points`:** `[his points, the opponent's points]` at the start of the turn, by the game's scoring (a knocked-out Pokémon gives 1 point, an ex 2, a Mega ex 3; 3 points win).
- **`me`:**
  - `hand`: his WHOLE hand at the start of this turn, INCLUDING this turn's draw. It follows from his opening hand, every draw and search, and every card played or discarded, as the review gives them.
  - `disc`: his discard (cards). `dene`: his discarded Energy, as letters (G W R L P F D M; e.g. 'WW').
  - `board`: his Active first (slot 0), then his Bench, compacted (convention 1).
  - `ko`: how many of HIS Pokémon were knocked out earlier in the game.
- **`opp`:**
  - `hand_count`: the opponent's hand size at the start of the turn (convention 2).
  - `disc` and `dene`: the opponent's discard, as far as the review names it.
  - `board` and `ko`: as for `me`.
  - `zone`: optionally, the opponent's next Energy as a letter, only if the review shows it.
- **`force`:** his whole recorded move this turn, in order, as engine labels (below). It ends with `EndTurn` unless the turn ended by his attack, which ends the turn by itself, or the game ended.
- **`kind`:** always `None`.
- **`stadium`:** `{"card": "<name> <set id>", "owner": 0}` if his, `1` if the opponent's; `None` when there is no Stadium.
- **`approx`:** the approximations, in plain words. Always at least the opponent's list being unknown and the hand size from visible plays; add each specific estimate (an Energy count you could not read, a printing chosen by HP only, ...).
- **`ambiguous`:** a list of FACTS about unclear printings or readings (e.g. "Charmander printing chosen by HP (70) only"). These are shown to the bots and the judge, so: facts only, no advice, nothing about his move.
- **`notes`:** build-only and never shown to anyone being tested. Say how you read the turn, citing the review's turn headings or lines.
- **`draws` and `vpatch`:** see "Hidden draws and coins".
- **`ez_now` and `ez_next`:** the Energy his zone showed this turn and next, as letters. **Required for a deck with more than one Energy type:**
  - v2deck_ba2eca5816: Grass, Fighting;
  - v2deck_2c68a379f5: Fighting, Metal;
  - v2deck_9633a01781: Water, Lightning, Metal;
  - v2deck_8561e086a0: Grass, Darkness, Metal.
  If the review doesn't show the next Energy, give the most likely one and say so in `approx`. A one-type deck needs neither.

**`B(card, hp, e='', tool=None, cond=None, behind=None, effects=None)`:** one Pokémon in play.
- `card`: "<name> <set id>". His Pokémon use his list's printing. The opponent's are picked by name, HP and the attack or Ability titles the review shows (`cards.py`); put a doubtful choice in `ambiguous`.
- `hp`: its REMAINING HP as the game showed it, bonuses included.
- `e`: attached Energy as letters, e.g. 'WWC'.
- `tool`: '<name> <set id>'.
- `cond`: a list from Asleep, Paralyzed, Confused, Poisoned, Burned.
- `behind`: the cards under it, the immediate pre-evolution first. Wartortle: `behind=[SQ]`. Mega Blastoise ex: `behind=[WT, SQ]`.
- `effects`: a lasting effect from an earlier turn that still applies, in the engine's form:
  - `[{"effect": {"ReducedAttackDamage": {"amount": 30}}, "turns": 1}]`;
  - `[{"effect": "CannotAttack", "turns": 1}]`.
  The engine names: NoRetreat, ReducedDamage{amount}, ReducedAttackDamage{amount}, IncreasedVulnerability{amount}, IncreasedAttackCost{amount}, CannotAttack, CannotUseAttack("<attack>"), PreventAllDamageAndEffects, NoWeakness, Counterattack{amount}, NoAbilities, IncreasedRetreatCost{amount}, ReducedDamageFromEx{amount}.
  Ability-derived effects (Safeguard, Shell Armor, ...) are NOT set: the engine derives them.
- **A turn effect on the whole player** from the opponent's last turn (e.g. no Supporters this turn) goes in `p['turn_effects']` after `P()`: `p = P(...); p['turn_effects'] = [{"turn": <this turn_count>, "effect": "NoSupportCards"}]`. The names are NoSupportCards, NoItemCards, NoTrainerCards, NoEnergyFromZoneToActive, ReducedRetreatCost{amount}, NoEvolutionFromHand. Write such a P() in the list as a small function or a two-line block.
- **The free-text check.** Everything the bots see is checked for evaluative or advisory words, after card, Ability and attack names are taken out: should, better, best, mistake, misplay, threat, lethal, plan, intend, want, correct, wrong, risky, safe, good, bad, optimal, ideal, blunder, must, needs to, ought, and their inflections. That covers `ambiguous`, effects, the Stadium and turn effects. None of his move's labels may appear there either. `check_game.py` enforces this.

## Labels (his move, `force`)
**Use the exact labels `check_game.py --show` lists as legal at each step.** The common ones:
- `Place:<Name>@<slot>`: a Basic to the Bench.
- `Evolve:<Name>@<slot>`.
- `Attach:1<Type>@<slot> zone`: Energy from the zone.
- `Play:<Trainer name>`: a Trainer. Its follow-up choice is a separate label after it:
  - a Tool: `Play:<Tool>` then `Tool:<Tool>@<slot>`;
  - Rare Candy: `Play:Rare Candy` then `Evolve:...`;
  - Field Blower: `Play:Field Blower` then `DiscardActiveStadium` or `DiscardToolFromPokemon{...}`.
- `Ability@<slot>`, with `Noop` for "no" where the engine asks.
- `Retreat:<slot>`: the Bench slot that comes in.
- `Attack:<attack title>`.
- `UseStadium`.
- `EndTurn`.

**Where two legal actions would share a label,** the tool appends the arguments, e.g. `DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0}`. Use exactly that.

**Slots change during the turn** (a Bench Pokémon placed, a retreat, a knockout). Follow them step by step, with the legal lists to confirm.

**A step the opponent decides inside his turn** (e.g. a new Active after Sabrina) is not in `force`. The tool applies a single-option choice itself.

**Order matters:** write his actions in the order the review gives. If the review doesn't give the order, use the order the engine needs and say so in `notes`.

## Hidden draws and coins (Professor's Research, Poké Ball, Copycat, Lucky Ice Pop, Mesagoza, Quick-Grow Extract, Wallace, Fragrant Forest, Dustox's Variety Powder, ...)
- `force` keeps his WHOLE move, past the draw. `check_game.py` applies it up to the hidden draw or coin, where the engine stops ("hidden draw or coin at ...").
- **Then it checks the rest** on a verification variant: the cards he drew are put in his hand up front, the chance actions are removed, and your coin patch is applied.
- **`draws={<force index>: [cards drawn or found]}`:** for EVERY chance step in `force`, give the cards the review says it drew or found. Use '-<card>' for a card it removes from his hand. For Copycat, which shuffles his hand away, list '-' for each card of his hand and then the new cards.
- **`vpatch=lambda v: ...`:** edits the variant position for a coin or random result the review shows. Examples: Lucky Ice Pop's heads (returned to hand); a random evolution, by setting the evolved Pokémon on the board.
- **If the review does not name a drawn card,** use a stand-in from his list in the variant only, and say so in `notes` and `approx`. The shipped position never holds a drawn card.

## When it is done
`check_game.py <game>` must print OK for every point of the game:
- no position problem;
- his whole move applies step by step, to the end of the turn or to a hidden draw;
- after a hidden draw, the variant applies the rest;
- the candidate view passes.

"More copies of X seen than the list holds" means the hand, board, discard or Stadium names more copies than his list has: a reading error to fix.

**A point is never dropped because it is hard.** The only allowed drop is G1: his recorded move cannot apply in ANY position consistent with the review. That means an illegal recorded action, or a label no legal action can match after the position is right. Then:
- write `/home/dacz8976/exam_v2/build/drops/<point id>.txt` with the VERBATIM `check_game.py` output that shows it, plus one line saying why no consistent position fixes it;
- keep the point's `P()` in the file, with your best position.

Most "unmatched" results are position errors (a wrong slot, a missing Energy, a wrong HP or printing, a card not in the hand). Fix those first.
