# Bounded independent verification

**Decision: ACCEPT.** The complete primary packet (`REVIEW.md`, `COVERAGE.md`, `FINDINGS.json`) was read and reconciled after saving. Its central finding, exact card cost, ordinary-turn check, HP/score reconciliation and ending agree with the bounded source checks below. No required correction remains. This independent acceptance supports the lead's completion check; the lead remains responsible for registration and safe archival.

Reviewer: `/root/helmet_independent`, assigned Sol independent source checker. Date: October 9, 2026. Scope: source evidence for the decisive mechanic, selected ordinary turns, ending, and reconciliation with the primary complete review. This is not a second complete visual pass. Registration, archival, browser changes and simulator changes remain outside this worker's scope.

Source: `20261009_223237000_iOS.MP4`, 567,700,019 bytes, 308.721667 seconds, 1170 x 2532. SHA-256 supplied by the lead's verified intake and recorded in `../SOURCE.json`: `7766e17b4e1141a72066e101b80869550bae11f72aa064951dfd7d23e8579f3f`. This checker reused the source-bound shared extraction and did not repeat the full-file hash. Nine additional native-resolution exact-seek frames were extracted directly from that source. Exact-seek filenames give the requested source timestamps; ordinary overview/dense labels are approximate filter-centered positions.

## Decisive interaction: confirmed

| Source time | Native evidence | Independently observed state |
| --- | --- | --- |
| 77.5s | `exact_77.5s.jpg`; shared `../wailmer_cost_native.jpg` | Active Wailmer has Heavy Helmet. Expanded retreat cost is three stars. Wave Splash deals 60 and costs three Water. One fulfilled blue Water plus two unfulfilled black Water symbols are distinct from the retreat stars. |
| 185s | `exact_185s.jpg` | Active Wailmer 100 HP with Helmet and four Water. Active Togedemaru 80 HP, two Metal, printed Bristling Spikes 30. No owner bench. |
| 187.5s | `exact_187.5s.jpg` | Normal Bristling Spikes attack displays 10 damage on Wailmer. |
| 190s | `exact_190s.jpg` | Wailmer settles at 90 HP. Togedemaru has the armed return-effect star and banner specifying 30 to the attacking Pokemon if damaged by an attack. This is the positive control for the equipped Helmet. |
| 207.5s | `exact_207.5s.jpg` | Before Wave Splash: Wailmer 90 HP, same Helmet, five Water. Togedemaru 80 HP, armed return effect, two Metal. Indeedee ex 130 HP is benched. |
| 211s | `exact_211s.jpg` | Wave Splash has reduced Togedemaru 80 to 20. Wailmer still reads 90 before its return damage resolves. |
| 212.5s | `exact_212.5s.jpg` | Helmet glows; return damage banner is 10. The red 90 is the old HP during animation, not the settled result. |
| 214s, 217.5s | `exact_214s.jpg`, `exact_217.5s.jpg` | Settled Wailmer 80 HP with the same Helmet and five Water; Togedemaru 20 with two Metal. |

The primary recorded result is **Bristling Spikes return damage 30 reduced to 10 by Heavy Helmet on active retreat-three Wailmer**. The settled change is 90 to 80, while a full 30 return would have left 60. The normal attack positive control is independently 100 to 90. No switch, evolution, replacement tool, healing or other relevant state change intervenes between the decisive pre-attack state and settled return. Indeedee ex was already benched but no Watch Over is used in this test window.

Heavy Helmet is identified both by its attached image and the independently inspected full card display in shared `dense/sec_125.jpg` (~124.5s), which states retreat cost three or more and -20 damage from attacks from the opponent's Pokemon. The armed Togedemaru effect is visible in the exact 190s frame. No external card database or simulator prediction was used as proof of the observed mechanic.

## Independent checks beyond the flagged mechanic

- Overview sheets 1-3, individual native frames, and ending evidence establish setup, development, score progression and the established terminal outcome. The primary `REVIEW.md` and `COVERAGE.md` give all 15 turns and the entire 308.721667-second recording; no unreviewed interval is declared. This checker reviewed their coverage and state reconciliation rather than independently repeating every turn.
- Selected ordinary turn seven was checked in shared `dense_sheet_05.jpg` and native `dense/sec_125.jpg`, `sec_134.jpg`, `sec_135.jpg`, plus `frames/overview_027.jpg` and `overview_028.jpg`: the second Helmet is drawn and retained, the third Water is attached, Pokemon Center Lady heals actual 20 from Wailmer 80 to 100, and Wave Splash 60 lowers Cinccino 90 to 30. These are ordinary resource/healing/attack actions, not merely the primary flagged claim.
- Native `frames/overview_009.jpg` (~42.5s) shows the original Helmet attached at full HP and its reduction tooltip. Native `overview_016.jpg` and exact 77.5s confirm Wailmer remains unevolved for the test.
- Later native `overview_054.jpg` (~267.5s), `overview_056.jpg` (~277.5s), `overview_057.jpg` (~282.5s), `overview_058.jpg` (~287.5s), `overview_059.jpg` (~292.5s), and `overview_060.jpg` (~297.5s) check the second Togedemaru promotion, Wailord ex/Helmet retention, reduced later attack, Watch Over healing, final attack return banner10, and third point. These are supplementary observations; the primary conclusion is grounded in the unevolved Wailmer test above.
- Native `dense/sec_309.jpg` (~308.5s) independently establishes Victory against Melmetal Deck (Eevee Grove), went first, 15 turns, owner3/opponent0, damage380. The three Wave Splashes for60 and two Wondrous Waves for100 in the primary review sum to380, consistent with the displayed result. No owner knockout appears in the bounded inspected score evidence.
- Auto is visibly available and OFF during the exact primary test frames, then ON in the later ending sequence. This is a computer battle under the owner's routing rule, excluded from Ladder Log and Pause Games. The named opponent is explicitly visible on the result screen.

## Reconciliation and limits

The checker initially misread two unfulfilled black Water silhouettes as Colorless symbols in the expanded Wailmer attack bar. Original-resolution `wailmer_cost_native.jpg` resolved that error: the correct attack cost is **three Water**, and the retreat cost is **three**. The primary report is correct on this point. No cost correction to the existing artifact is warranted.

Hidden cards, the exact 20-card owner deck, unreadable tiny collection identifiers, unrecorded decisions, and every possible retaliation mechanism remain outside what this video establishes. The tested interaction does not by itself prove identical handling for Rocky Helmet, Druddigon, ability damage, special conditions or other return effects. The primary report preserves these limits. Sampling timestamps are approximate except the directly sought key frames; these frames distinguish settled states without claiming frame-exact action onset.

Primary packet reconciliation, accepted file hashes and final acceptance are recorded in `VERIFICATION.json`. This checker has not changed the primary report, source, index, registry, archive or external artifact.
