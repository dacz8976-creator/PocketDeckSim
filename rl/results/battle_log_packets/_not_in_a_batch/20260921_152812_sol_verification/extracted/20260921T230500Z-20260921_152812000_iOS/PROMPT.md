You are the complete first-pass reviewer for one Pokémon TCG Pocket battle recording. Produce an evidence-bound candidate packet for later independent Sol verification.

## Source binding

- Filename: `20260921_152812000_iOS.MP4`
- Local source path: `/home/dacz8976/20260921_152812000_iOS.MP4`
- SHA-256: `5FEF7F20302FADC695346ED277CEF892E523CCC73DFF67F2907F4448EE10CDB0`
- Bytes: `568299605`
- Duration: `304.803` seconds
- Model: `gemini-3.8-flash`
- Review method: static video processing at `5` source frames per second with `high` media resolution
- Thinking level: `medium`

Treat the video as the authority. Do not treat filenames, likely deck lists, or prior expectations as proof of an event.

## Required review behavior

Review the entire available recording from setup through the terminal result. Account for every turn and every meaningful visible action. Do not produce a highlights summary.

Maintain a running state ledger at each turn boundary and after every meaningful transaction:

- Active Pokémon, HP, Energy, Tool, and conditions
- Bench Pokémon, HP, Energy, Tool, and changes
- visible hand identities and hand count
- publicly established deck and discard transactions
- Energy Zone state and whether generated Energy was attached or left unused
- score before and after every knockout or award
- visible system prompts
- Solo or PvP only when established
- Auto indicator and any control-mode change

For each meaningful transaction, record evidence anchors rather than reconstructing a
plausible sequence from the later board. Use a before timestamp when available, the
action/reveal timestamp, and an after-state timestamp. A later board state does not by
itself prove which card caused it, which target was chosen, or the order of actions.

If the sampled evidence does not show the action, target, result, or ordering clearly,
write `unknown` and add an entry to `UNCERTAINTIES.json`. Do not silently fill a gap
with the most likely legal play. Do not state that an action was verified merely
because the resulting state is legal or internally plausible.

Pay special attention to fast or reversible events:

- selected card versus successfully played card
- failed search and no-target prompts
- one physical card returning to hand and being replayed versus a second copy
- the card shuffled into the deck versus the card retrieved from the deck
- attack target, damage, weakness, healing, knockout, and point progression
- triggered Tools, Abilities, and knockout effects in their visible order
- concession menu, confirmation, transition, and result screen

Do not infer hidden cards or exact deck contents beyond what the video publicly establishes. Do not convert a visible possible line into a forced or mathematically unavoidable outcome. When evidence does not establish a fact, mark it unknown and provide the exact timestamp needing review.

Before finalizing, perform a second reconciliation pass over the complete timeline:

1. Inventory every visible Item, Supporter, Pokemon play/evolution, Energy movement,
   attack, Ability, prompt, switch, retreat, and Bench change in each turn.
2. Reconcile every deck search, failed search, hand-to-deck exchange, return-to-hand,
   replay, and revealed search result with timestamp anchors.
3. Reconcile each Pokemon's Energy from one turn boundary to the next. Name the source
   and destination of every attachment or acceleration; never infer the recipient from
   attack legality alone.
4. Reconcile HP, healing, damage, knockouts, promotions, and score changes.
5. Reconcile the terminal sequence and result screen.

If any required category cannot be reconciled from visible evidence, list it as an
uncertainty. An empty uncertainty array is allowed only after this audit is completed;
it is never justified merely by a continuous-looking recording.

Do not say that every source frame was reviewed. State the actual configured sampling method. This is a candidate first pass and remains `partial` until independent Sol acceptance.

## Required output

Return exactly these four fenced sections in this order. Do not add conversational text before or after them.

Place each exact filename heading OUTSIDE its code fence. Use this structure:

### SOURCE.json
```json
{ ... one source object, never an array ... }
```
### COVERAGE.md
```markdown
... coverage text ...
```
### REVIEW.md
```markdown
... review text ...
```
### UNCERTAINTIES.json
```json
[ ... uncertainty objects, or an empty array ... ]
```

The illustration above shows structure only; replace all placeholders with actual
content. SOURCE.json must use the exact keys `filename`, `source_path`, `sha256`,
`bytes`, `duration_seconds`, `review_status`, `index_update_performed`, and
`media_move_performed`. Copy the supplied source identity exactly. Use `partial`
for review_status and JSON `false` for both performed fields. Include the other
metadata described below. Successful formatting is not independent verification.

### 1. SOURCE.json

Return valid JSON containing:

- source identity fields provided above
- recording type and relationships
- model and sampling method
- reviewer attribution as `Gemini 3.8 Flash API first-pass draft`
- review status `partial`
- outcome
- explicit statement that no index update or media move was performed

### 2. COVERAGE.md

Return Markdown containing:

- setup interval
- every turn or phase with timestamp range
- for every turn, an `Evidence anchors` line and a `State delta` line
- terminal sequence
- a checked coverage item only when reviewed
- a separate list of unresolved intervals and the exact question for Sol
- an exact `## Required Event Audit` heading followed by these six labeled lines,
  each with timestamped findings, `none observed`, or `unknown` plus a linked
  uncertainty:
  - `Deck searches and failed searches:`
  - `Energy attachments and acceleration:`
  - `Return-to-hand, replay, and exchange events:`
  - `Knockouts and score changes:`
  - `Switches, retreats, and Bench changes:`
  - `Terminal sequence:`

### 3. REVIEW.md

Return Markdown containing:

- date if established from the source filename, otherwise unknown
- mode and Auto state
- players or AI identity only when visible
- starting board and visible opening hand
- full timestamped turn-by-turn timeline
- an exact `## Evidence Ledger` heading; within every turn list `Observed actions`,
  `State delta`, and `Evidence anchors`
- HP, Energy, Bench, hand transactions, and score reconciliation
- important mechanics and tactical observations
- outcome
- an exact `## Explicit Uncertainties` heading; use `None reported by Gemini` only
  when the required event audit supports an empty uncertainty array
- status `Partial pending independent Sol verification`

### 4. UNCERTAINTIES.json

Return valid JSON array. Each entry must contain:

- `start_timestamp`
- `end_timestamp`
- `claim_or_question`
- `why_uncertain`
- `consequence_if_wrong`
- `recommended_sol_check`

Return an empty array only if no uncertainty remains after the complete first pass.
