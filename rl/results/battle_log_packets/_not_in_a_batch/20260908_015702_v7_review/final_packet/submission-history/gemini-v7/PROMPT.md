You are the complete first-pass reviewer for one Pokémon TCG Pocket battle recording. Produce an evidence-bound candidate packet for later independent Sol verification.

## Source binding

- Filename: `20260908_015702000_iOS.MP4`
- Local source path: `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\20260908_015702000_iOS.MP4`
- SHA-256: `3FBD29A85A17B5F4B4F7DDD3D7EE15B2177503FF3E15C56314DE9CC60EDCFB2D`
- Bytes: `507514203`
- Duration: `272.803` seconds
- Model: `gemini-3.8-flash`
- Review method: static video processing at `5` source frames per second with `high` media resolution
- Thinking level: `medium`

Treat the video as the authority. Do not treat filenames, likely deck lists, or prior expectations as proof of an event.

## Independent identity contract

Before drafting the narrative, inspect the first stable board, the visible opponent
label, and the last 45 seconds through the last frame. Include `battle_identity` in
SOURCE.json alongside `evidence_audit`. It is a version 1 object with five keys:
`opponent_label`, `opening_player`, `opening_opponent`, `outcome`, `result_text`.
Each key contains `state`, `value`, `timestamp_seconds`, `observation`.
State is `observed`, `unknown`, or (only for result_text) `not_shown`.
Value is the exact visible name/text (preserve Mega/ex/forms), null for unknown or
not_shown, or for outcome `player_win`, `opponent_win`, `draw`. The lower board is
player. Opening Pokemon are the initial stable Active cards, not later evolutions,
Bench/hand cards, or setup selection previews. Opening anchors must be within the
first 90 seconds; outcome/result anchors within the final 45 seconds. Timestamp is
a numeric offset in source-video seconds. Observation briefly states pixel evidence.
For result_text not_shown, anchor the last inspected frame. Unknown is preferable
to guessed identity. Copying source metadata does not establish video content.

Keep the narrative and evidence_audit consistent with these independently observed
facts. Do not infer a literal result from points. A separate blind check will be
compared with this object, but its answers are deliberately not supplied to you.

## Required review behavior

Review the entire available recording from setup through the terminal result. If
the recording ends mid-battle, account for every available turn and meaningful
visible action, label the battle outcome unknown, state that the recording is
incomplete, and never invent missing turns or a result. Do not produce a highlights
summary.

Maintain a running state ledger at each turn boundary and after every meaningful transaction:

- Active Pokémon, HP, Energy, Tool, and conditions
- Bench Pokémon, HP, Energy, Tool, and changes
- visible hand identities and hand count
- publicly established deck and discard transactions
- Energy Zone state and whether generated Energy was attached or left unused
- score before and after every knockout or award
- visible system prompts
- Solo, PvP, or AI classification only when immediately explicit; otherwise record unknown without extra inspection
- Auto indicator and any control-mode change

Apply these interface-specific evidence rules before recording any state change:

- The Energy Zone orb and its small type icon may show the current or upcoming Energy.
  They are not evidence that Energy was attached. Record an attachment only when the
  video shows Energy moving to a named Pokemon and a later frame shows that Pokemon's
  attached-Energy count/type increased. Otherwise write `unknown`.
- A player normally makes at most one manual Energy attachment during a turn. If your
  draft contains two or more, recheck the video and identify a visible card, attack, or
  Ability that supplied every additional attachment. If none is visible, do not keep
  both claims; record the conflict in `UNCERTAINTIES.json`.
- Count Energy icons on each Pokemon at turn boundaries. Do not derive Energy from an
  attack cost, from the next-Energy preview, or from a later legal attack.
- An `Auto` toggle proves only the displayed Auto state. It does not prove Solo mode,
  an AI opponent, or matchmaking type. Mode and AI status are low-priority metadata:
  inspect the obvious setup cue once, then use `unknown` without revisiting the video if
  separate evidence is not immediately clear. Do not spend review effort or uncertainty
  analysis on them. They never override or block otherwise verified battle rules, state
  transitions, scoring, and outcome.
- A point animation or a three-point score is not a visible `Victory` banner. State the
  match-winning point separately from any result text actually shown before the video
  ends.

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
6. Recheck the timestamp of each attachment, promotion, knockout, and point award at
   the frame where the action or after-state is actually visible. Do not reuse an
   earlier turn or card-play timestamp for an effect that resolves later.

If any required category cannot be reconciled from visible evidence, list it as an
uncertainty. An empty uncertainty array is allowed only after this audit is completed;
it is never justified merely by a continuous-looking recording.

Do not say that every source frame was reviewed. State the actual configured sampling method. This is a candidate first pass and remains `partial` until independent Sol acceptance.

## Required output

Return exactly these four fenced sections in this order, followed by the literal
final line `<!-- END_BATTLE_PACKET -->`. Do not add conversational text. Never emit
that final marker unless all four sections, every turn, and the ending are complete.

Keep the packet concise enough to finish all four sections. Target no more than 1,800
words across both Markdown files combined. Prefer compact evidence-ledger
entries over repeated prose. If space becomes tight, shorten wording; never omit a
turn, the terminal sequence, closing code fences, or `UNCERTAINTIES.json`.

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
- `evidence_audit` using the exact contract below. This ledger is required and is
  checked locally for consistency. A parser passing it does not prove the claims true.

#### Structured evidence contract inside SOURCE.json

Use one compact `evidence_audit` object with these fields:

- `version`: 1.
- `opponent_label`: exact visible name, or `unknown`.
- `match_mode`: `{ "value": "solo" | "pvp" | "unknown", "evidence": [anchor], "uncertainty_id": null | "U1" }`.
- `opponent_ai`: same structure with values `yes`, `no`, `unknown`.
- `auto`: same structure with values `on`, `off`, `unknown`.
- `terminal`: `{ "outcome": "player_win" | "opponent_win" | "draw" | "unknown", "outcome_evidence": [anchor], "result_text": null | "exact visible result text", "result_text_evidence": [anchor], "last_frame": anchor, "uncertainty_id": null | "U2" }`.
- `pokemon`: array of `{ "id": "player-1", "owner": "player" | "opponent", "initial": {}, "initial_evidence": anchor, "final": {"Water": 1}, "final_evidence": anchor, "uncertainty_id": null | "U3" }`.
- `energy_events`: chronologically ordered array of objects described next.

An `anchor` is `{ "timestamp": "MM:SS.mmm", "observation": "short literal visible observation" }`.
All anchors must fall within the supplied duration. `last_frame` must describe the
final available second. Known mode/AI classifications require independent visible
evidence; the Auto toggle cannot be that evidence. When that evidence is not immediately
clear, use unknown and move on. Unknown classifications need an uncertainty ID that
exists in UNCERTAINTIES.json. `result_text` is null when no result
banner is visible, even if a third point or empty board establishes the outcome.
Do not manufacture a result banner to make it agree with the outcome.

Give each physical Pokemon one stable ID throughout evolution and movement between
Bench/Active. `initial` means when that Pokemon first becomes visible in play; `final`
means its last inspected state (use zero after removal). Energy maps use positive
integer counts with exact type names Water, Lightning, Grass, Fire, Psychic, Fighting,
Darkness, or Metal. `{}` means known zero; null means unknown and needs a linked
uncertainty. Never put upcoming Energy in these maps. Include every visible Pokemon,
even those with zero Energy; do not include hidden hand/deck Pokemon.

Each `energy_events` entry has:

- `turn`: positive integer; `pokemon_id`: stable ID; `kind`: `manual`, `effect`,
  `retreat`, `discard`, or `unknown`.
- `before` and `after`: Energy maps, matching the preceding known state and later
  attached icons. Count and type must both reconcile, not just the total.
- `before_evidence`, `action_evidence`, `after_evidence`: anchors in that order.
- For `manual`, `attachment_evidence` must be `movement_and_attached_icons` only
  when both are actually visible. Exactly one Energy must be added. At most one
  manual attachment per side per turn; any additional attachment needs `effect`
  and a visible named card/Ability/attack in `cause`.
- For `retreat`/`discard`, remove the paid/lost Energy. Evolution retains the same
  Pokemon ID and its Energy; it is not a new attachment. Include KO Energy loss.
- For `unknown`, include a linked `uncertainty_id`. Unknown maps may be null and
  missing before/action anchors may be null, but an inspected after-state anchor
  is still required. Do not relabel an unsupported preview claim as a known event.

Reconcile all events from each Pokemon's initial map through its final map. A
missing attachment, invented attachment, wrong type, or wrong retreat payment must
be corrected from the video or explicitly marked unknown. Keep observations short;
reference these timestamps from Markdown instead of repeating the whole ledger.

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
- `id`: unique short ID such as `U1`, used by unknowns in the evidence audit

Return an empty array only if no uncertainty remains after the complete first pass.
Close its fence, then output `<!-- END_BATTLE_PACKET -->` as the final line.
