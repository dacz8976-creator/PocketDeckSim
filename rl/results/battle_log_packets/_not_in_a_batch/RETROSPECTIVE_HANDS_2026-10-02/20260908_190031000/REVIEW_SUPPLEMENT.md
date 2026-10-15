# Retrospective field supplement: 20260908_190031000_iOS.MP4

Source review: complete_with_recording_limits. Independent acceptance pending. Accepted old review and outcome remain unchanged.

Setup: Small Balloon, Copycat, Professor's Research, Poké Ball, Eevee, left to right in native23s before Active selection. Eevee becomes Active. No positional opening order was claimed by the inherited unordered list.

Mode: no Auto control was visible in inspected native frames or the168-sample reduced locator. Match mode remains uncertain under the owner rule.

## Turn 1 (opponent)

Inherited accepted account retained verbatim in INHERITED_TURNS.json with source line. Fresh fields are in TURN_LEDGER.json.

Start owner hand: ['Small Balloon', 'Copycat', "Professor's Research", 'Poké Ball'].
1. tool: Heavy Helmet; Attached; reduction condition not active at retreat cost 1. [t0048.00]

## Turn 2 (owner)

Inherited accepted account retained verbatim in INHERITED_TURNS.json with source line. Fresh fields are in TURN_LEDGER.json.

Start owner hand: ['Small Balloon', 'Copycat', "Professor's Research", 'Poké Ball', 'Mega Altaria ex'].
Before-end owner hand: ['Copycat', 'Mega Altaria ex', 'Training Area'].
1. item: Poké Ball; Search reveals Darkrai. [t0054.00]
2. supporter: Professor's Research; Draw Swablu then Training Area. [t0064.00]
3. bench: Swablu; Placed. [t0074.00]
4. bench: Darkrai; Placed. [t0074.00]
5. tool: Small Balloon; Attached. [t0080.00]
6. retreat: Eevee; Free retreat with Small Balloon; paid zero Energy. [t0084.00]
7. energy_attachment: ; Attach 1 Psychic Energy. [t0087.00]
8. attack: Sing; Asleep applied. [t0090.00]

## Turn 3 (opponent)

Inherited accepted account retained verbatim in INHERITED_TURNS.json with source line. Fresh fields are in TURN_LEDGER.json.

Start owner hand: ['Copycat', 'Mega Altaria ex', 'Training Area'].
Before-end owner hand: ['Copycat', 'Mega Altaria ex', 'Training Area'].
1. item: Lucky Ice Pop; Heal20:40to60; heads returns Ice Pop to hidden hand. [t0112.00]
2. energy_attachment: ; Attach1Grass. [t0115.00]
3. item: Quick-Grow Extract; Evolve to Ivysaur; Sleep removed. [t0116.50 preceding; t0120.00/t0126.00 resolved]
4. attack: Synthesis; Take2Grass from Energy Zone and attach; total3. [t0126.00]

## Turn 4 (owner)

Inherited accepted account retained verbatim in INHERITED_TURNS.json with source line. Fresh fields are in TURN_LEDGER.json.

Start owner hand: ['Copycat', 'Mega Altaria ex', 'Training Area', 'Field Blower'].
Before-end owner hand: ['Copycat'].
1. item: Field Blower; Helmet discarded; no reduction after removal. [t0139.00]
2. evolution: Mega Altaria ex; Evolves to190HP with carried Psychic1. [t0143.00]
3. stadium: Training Area; Stage1 attacks+10 to Active. [t0148.00]
4. energy_attachment: ; Attach1Psychic; total2. [t0150.00]
5. attack_selection: Mega Harmony; Displayed110. [t0154.00]
6. prompt_response: ; OK confirms ending attack; Copycat stays unplayed. [t0155.00]

## Recording limits

- Opponent unplayed cards and normal draw identities are hidden by card backs.
- No discard panel was opened in the retained 1 fps locator scan; visible pile-top cards are recorded separately, full pile identities and order remain null.
- One reduced sample per second does not examine every instant; brief subsecond prompts or panels can be missed.
- Requested source-local times are retained; actual decoded frame PTS was not independently measured.
- The exact historical 20-card log list is unavailable; visible core only.

Independent field repair: ending owner hands are now populated in all four turn rows from native48 (four cards),102 (three),130 (three) and165.5 (one Copycat). Quick-Grow uses native116.5 only as its preceding-state anchor, with evolution/recovery supported by120 and the resolved Ivysaur/closed Item discard corroborated by126. Exact input time remains unmeasured.

Serialization bindings: every row now collects its existing nested native evidence IDs, and rows2/3/4 link their already retained periodic pile snapshots. Turn1 has no assigned pile snapshot. This adds references only and does not introduce new card observations or claim opened-pile coverage.
