# Bounded Arena and terminal-sequence check

Scope: two requested interpretation questions only, checked against retained source frames on 2026-09-30. Both recordings are owner-declared Auto versus computer, not Ladder. No full-video review, source hashing, engine inspection, source moves, or shared report/log edits were performed here. Source identities below are supplied by the parent review.

## Arena eligibility correction

**The Arena text uses the Fighting fist symbol, not the BASIC badge.** In the clearer source-161633 frame at 144.00 seconds, the text reads: "Attacks used by each [Fighting symbol] Pokémon in play (both yours and your opponent's) do +20 damage to the opponent's Active Pokémon ex."

The source-162102 Arena at 123.00 seconds has the same small Fighting glyph. A read-only enlarged crop of source-161633 at x620, y2330, width280, height110 was used to resolve the glyph; source-162102 was cross-checked at x33, y1450, width235, height80. Crops were displayed from memory and not saved. These views support **Fighting eligibility** with high confidence. Source-161633 is the clearer textual anchor. Basic status is visible on Drilbur and Passimian ex, but it is not the eligibility condition printed on Arena. This corrects the source-161633 prose and preserves the source-162102 Fighting interpretation.

## 20260930_161633000_iOS.MP4

Supplied SHA-256: `0795e24efb0f71c3461d23b5860a736a30755cf2071a3047eb4b90a731193a79`.

Exact inspected frame paths, relative to the workspace:

- `Recording_QA/20260930_161633000_iOS_auto_sol/targets/t0144.00.jpg`: held Arena and its text; Drilbur has Headbutt Bounce 30; opposing Active Bellibolt ex displays 70 remaining HP and Fighting weakness +20. The owner's point display is 0 and opponent's is 2.
- `Recording_QA/20260930_161633000_iOS_auto_sol/targets/t0147.00.jpg`: Drilbur has two Fighting Energy, satisfying the two Colorless symbols printed on Headbutt Bounce; Arena remains held; Bellibolt remains at 70.
- `Recording_QA/20260930_161633000_iOS_auto_sol/targets/t0157.00.jpg`: Bellibolt is at 20 after the actual attack; the subsequent 70-damage hit on Drilbur is being animated.

**Accept the immediate-KO alternative as a printed-text conditional inference.** Drilbur is Fighting, Bellibolt is the opposing Active Pokémon ex, and the displayed arithmetic is 30 attack +20 weakness +20 Arena =70, matching the displayed remaining HP. The actual 70-to-20 change supports the unboosted 50. Bellibolt's attached HP tool is already reflected in the displayed remaining 70; do not add its HP bonus again to that number. Bellibolt's Stage 1 status does not invalidate the target condition, which is Active Pokémon ex.

Required wording limit: "If Arena could be played before this attack and its printed effect applied, Headbutt Bounce would reach 70 and KO the 70-HP Bellibolt ex." The images support this specific tactical alternative, not a tested engine branch or eventual owner victory. No visible modifier in these inspected anchors defeats that immediate arithmetic. The full turn's legality and hidden implementation were not independently tested in this bounded check.

## 20260930_162102000_iOS.MP4

Supplied SHA-256: `e23850f05a3e9a8b1b838c190a17cecfd88a50e7359013ffaee15c8c9a2758a5`.

All following exact inspected paths share `Recording_QA/20260930_162102000_iOS_auto_sol/targeted/`:

- `t0123.00.jpg`: Arena is in play; Passimian ex shows Seismic Toss 60, Fighting Energy, 70 HP, and attached Rocky Helmet; Mega Manectric ex has 190 HP and Fighting weakness +20. Rocky Helmet text on the held duplicate says an opponent's attack damaging the attached Active Pokémon causes 20 damage to the attacking Pokémon.
- `t0126.00.jpg`: transition after Korrina leaves the hand; this is not the 130-damage popup.
- `t0129.00.jpg`: Korrina effect caption explicitly identifies Fighting-type attacks and +30 damage to the opponent's Active Pokémon ex. Mega still displays 190. This frame is not a 130-damage popup.
- `t0132.00.jpg`: explicit **130** damage popup with Weakness, while Mega's displayed HP is still animating from 190. Do not call this a settled 60-HP frame.
- `t0135.00.jpg`: settled Mega HP is **60**; Passimian is 70.
- `t0141.00.jpg`: explicit **80** damage popup on 70-HP Passimian; Mega is 60.
- `t0144.00.jpg`: Passimian displays **0** HP while still on the board, with an effect burst on Mega. Mega still shows 60 in this sampled frame.
- `t0147.00.jpg`: owner Active and Bench are empty; Mega displays **40** HP; Passimian and Helmet are going to/visible at the discard area; owner point display is 1.
- `t0150.00.jpg`: explicit opponent **+2 points**, with opponent markers 1 and 2 lit and 3 unlit; owner remains at 1.
- `t0152.00.jpg`: explicit **Defeat**.

**Accept 130 =60 Seismic Toss +20 Fighting weakness +20 Arena +30 Korrina.** Both Arena and Korrina use Fighting eligibility here, with different values. Passimian meets that condition. The displayed 130 and settled 190-to-60 change independently support the total, while attribution of individual increments rests on the printed text and Korrina caption.

**Accept the recorded loss with owner 1 / opponent 2 after the owner's field becomes empty.** Do not recast it as the opponent reaching three points. The footage establishes the outcome directly.

**Accept the narrow Helmet observation:** following the lethal 80 hit, Passimian is shown at 0, Mega subsequently falls from60 to40, the owner's field becomes empty, then +2 opponent points and Defeat appear. The attached Helmet and its visible text support the 20-damage attribution. These sampled anchors do not resolve the exact internal ordering of HP subtraction versus card removal, and do not establish a general engine rule for all simultaneous KO, damage, point, or victory checks. Prefer "Helmet's 20 damage still resolved after the lethal hit, before the result screen" over a claim that it necessarily resolves after complete card removal.

## Requested corrections

1. Correct source-161633 Arena eligibility from Basic to Fighting; leave the conditional Drilbur 70-damage KO inference intact.
2. Preserve Fighting in source-162102 Arena wording. Keep Korrina's separate +30 effect explicit.
3. Correct source-162102 time anchors: Korrina caption129; 130 popup132; settled60 at135.
4. Preserve source-162102 final score1-2 and explicit Defeat, with empty-field context and narrowly worded Helmet sequence.

Confidence: high for displayed values, printed Fighting glyph, attack arithmetic, and explicit defeat; bounded/conditional for the unplayed Arena alternative; no implementation or eventual-win conclusion.
