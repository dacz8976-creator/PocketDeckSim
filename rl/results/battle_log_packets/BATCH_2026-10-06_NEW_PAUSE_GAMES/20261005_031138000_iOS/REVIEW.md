# 20261005_031138000_iOS.MP4 full battle review

Reviewer: Sol, task `/root/pause_031138`. Review date: October 6, 2026. Worker completed the whole source; independent lead acceptance is pending. The source stays unchanged and this worker has not registered completion, moved it, or written an external game entry.

Source: 408,576,397 bytes, 226.181667 seconds, SHA-256 `15ab9ced3d29c711ffe0ed069480cf549180d1acad56439ff31e1c51f9e4d66e`. Frozen identity is in SOURCE.json. Embedded UTC creation time corresponds to October 4, 2026 at 22:11:38 America/Chicago, as preserved in RECORDING_METADATA.json.

Dacz8976 wins against 九兎, level 59, by opponent concession. The final result screen reports went second, seven turns played, owner 2 points, opponent 0, and 180 damage done. The filmed queue is Deluxe Pack: Mega Emblem Event. No Auto control or option appears anywhere in the inspected source, so this is a human event battle for the requested Pause Games routing.

## Inspection and evidence

Reviewed the complete 0-226.181667-second source with a two-second overview to locate every turn/action, then native 1170x2532 focused frames for all owner hands, draws, searches, ordered plays, opponent actions, board transitions and outcome. The overview is a navigation aid. Native retained images and bottom-fifth/top-screen crops supply the hand evidence. Requested source seek times are known; exact decoded frame PTS were not measured. All times below are source-local and approximate within about 0.1-0.5 seconds.

TURN_LEDGER.json has exactly one row for each of the seven recorded turns. TURN_EVIDENCE.json binds native images, crop coordinates and selected candidate roles to the source hash. Each timestamp below references `turn_evidence/tNNNN.NN.jpg` through the matching `fNNNN.NN` evidence ID. No interval remains uninspected and no linked continuation is needed.

## Deck and setup, 0-44 seconds

At 0-3 seconds the source shows a deck QR. Native frame 2 seconds decodes to 20 slots with Psychic Energy, all semantic entities resolved in the pinned catalog, and a successful payload roundtrip. QR_DECODE.json preserves the payload, native image hash, catalog hashes, duplicates and printing limits. The source proceeds continuously to the New deck 6 selection at about 5 seconds and the ensuing battle. No deck editing occurs. The slot label alone is not a unique deck identity.

This is the newly prepared Hatterene / Aromatisse / Togekiss list, distinct from the earlier Water deck that also used the New deck 6 slot. DECK_USED.json saves all 20 slots from the filmed QR and the lead's prepared new log entry. The initial nine-list live snapshot did not contain this new Psychic list. The lead must finish live-save verification and update the deck receipt before claiming the new list is in the external artifact.

The owner goes second. At 29 seconds, before Active placement, the five original cards are visible left to right: Spritzee, Poke Ball, Hatenna, Hatterene, Professor's Research. Spritzee with Sweet Scent, 60 HP is chosen Active at about 36 seconds. No redraw, replacement hand, or setup Bench placement is shown. The owner's remaining four cards are Poke Ball, Hatenna, Hatterene and Research. Opponent reveals Tapu Koko ex, 130 HP, Plasma Hurricane 20 / Mach Bolt 90 as Active. Both begin at 0 points with empty Benches, no Tools and no Stadium.

## Turn account

| Turn / player | Source seconds | Ordered plays and resolved state | Hand and evidence |
| --- | --- | --- | --- |
| 1 / opponent | 44-50 | Normal hidden draw. 1. Bench Froakie, Flop 10, 60 HP, in right Bench slot at about 48. 2. End turn. No attachment or attack; first-turn current Energy circle empty, next Lightning preview visible. | Owner still four cards; opponent five after draw, four after Froakie. Native46/50. |
| 2 / owner | 50-78 | Draw Research at52. 1. Bench original Hatenna in middle slot at53. 2. Poke Ball at57.5, reveal Hatenna at60 and add it. 3. Full-art Research at64, draw Aromatisse first at66, Togetic second at67. 4. Bench searched Hatenna in left slot at72. 5. Attach1 Psychic to Active Spritzee at75. 6. Select End Turn at77. 7. Accept OK on "An attack can be used", ending without Sweet Scent. All Pokemon remain undamaged. | Start five: Poke Ball, Hatenna, Hatterene, Research, Research. Dense pre-play52.5; scheduled approximately+1/+3/+6 frames53/55/58 already show actions or zooms. End four: Hatterene, Research, Aromatisse, Togetic at76. Opponent fan counted4. |
| 3 / opponent | 78-112 | Hidden normal draw. 1. Attach1 Lightning to Koko at84. 2. Rare Candy at89, evolve right-slot Froakie directly into Greninja120HP, Water Shuriken / Mist Slash60. 3. Water Shuriken at95, targeting original middle Hatenna,60->40HP. 4. Plasma Hurricane at109, Spritzee60->40HP; effect attaches a second Lightning to Koko. No points gained. | Opponent5 after draw,3 after Rare Candy and Greninja. Owner remains four. Native83/90/100/110/112; top discard later clearly Rare Candy. |
| 4 / owner | 112-142 | Draw Togekiss at115. 1. Evolve Active Spritzee into Aromatisse at118,70/90HP with the prior20 damage and1 Psychic retained. 2. Research at121.5; Hatterene first at125, Hattrem second at126. 3. Evolve left Hatenna into Hattrem at128,80HP. 4. Attach1 Psychic to left Hattrem at132. 5. Aromatisse Confounding Cologne at135,40 damage to Koko130->90 and Confused. | Start five: Hatterene, Research, Aromatisse, Togetic, Togekiss. Selected116.5 pre-play; +3/+6 candidates118.5/121.5 already contain plays. End four: Hatterene, Togetic, Togekiss, Hatterene. Last pre-attack hand134.5; same four visible at130/134. Opponent fan3. |
| 5 / opponent | 142-178 | Hidden normal draw. 1. Bench Zeraora90HP, Thunderclap Flash / Lightning Claw50, middle slot at148. 2. Attach third Lightning to Koko at150. 3. Electric Generator at152.5; visible Tail at156.2, no Energy gained. This no-effect item remains an action. 4. Water Shuriken at161, target left Hattrem80->60HP. 5. Koko attempts an attack while Confused at173; tails and "The attack did nothing" at177. Aromatisse remains70HP; no damage or extra Energy. Koko stays Confused and at90HP with3 Lightning. | Opponent4 after draw,2 after Zeraora and Electric Generator. Owner remains four. Native146/152.5/156.2/164/174/176/178. Selected attack name is not shown because the confusion check fails. |
| 6 / owner | 178-207 | Draw Pound20 Togepi50HP at180. 1. Bench Togepi in right slot at181.2. 2. Evolve left Hattrem into Hatterene at186,130/150HP with20 damage and1 Psychic retained. 3. Retreat Aromatisse at191, pay its1 Psychic and promote Hatterene; Aromatisse moves left Bench slot with0 Energy. 4. Attach second Psychic to Active Hatterene at193.5. 5. Mental Crush at196 deals140 against Confused Koko, knocking it out. Owner gains2 points at203. Opponent promotes Zeraora at206. | Start five: Hatterene, Togetic, Togekiss, Hatterene, Togepi. Dense180.5 pre-play hand is clear; +1/+3/+6 frames181.5/183.5/186.5 already show the first play or later evolution. End three: Hatterene, Togetic, Togekiss at195.5. Opponent fan2. |
| 7 / opponent | 207-214 | Hidden normal draw increases opponent fan2->3. Current Lightning Energy generated and remains unused. 1. Opponent concedes at213. No attachment, ability or attack precedes concession in this turn. | Native210/212/214. Owner hand remains three, owner2points, opponent0. |

## Terminal sequence and source ending, 214-226.181667 seconds

The concession message at213-214 is followed by the Victory animation at216-217. Loading resolves to a results screen at225 through source end. Hatterene is Card of the Game, and the screen confirms seven turns, owner2points, opponent0, damage180. This matches Confounding Cologne40 plus Mental Crush140. Victory is established; no unrecorded result is inferred.

## State and capture reconciliation

Owner turn2 ending count is4: four after setup + normal draw1 - first Hatenna1 - Poke Ball1 + search1 - Research1 + Research2 - second Hatenna1. Turn4 is4: prior4 + normal draw1 - Aromatisse1 - Research1 + two draws - Hattrem1. Turn6 is3: prior4 + normal draw1 - Togepi1 - Hatterene1. Retreat and generated Energy do not remove hand cards. These counts also match the native ending fans.

The owner board develops Spritzee -> Aromatisse Active; left searched Hatenna -> Hattrem -> Hatterene, middle original Hatenna and right Togepi. Water Shuriken hits the middle original Hatenna on turn3 and the left Hattrem on turn5. These separate20-damage marks explain middle Hatenna40/60, Hattrem60/80 and later Hatterene130/150. Plasma Hurricane's20 persists as Aromatisse70/90. No healing, Tool, Stadium, status other than Koko's Confused, delayed mark, Item lock, Energy Zone block or other board restriction is shown.

Each start/end board includes both Energy Zones. The small next icons are Psychic for owner, Lightning for opponent throughout; they are previews. Current generated Energy is consumed by each normal attachment, plus Koko's second Energy from Plasma Hurricane. Turn1 current Energy is absent. Opponent turn7 Lightning remains available and unused at concession. Energy generation on owner turn6 finishes immediately after the dense180.5 hand frame;181.5 verifies it before any Energy attachment.

Neither player opens a discard pile anywhere. Public top discard cards and ordered plays establish Research twice, Poke Ball and the retreat payment for owner; Rare Candy, Electric Generator and the knocked-out Koko stack for opponent. This is a play-derived history, not a full viewed discard pile or a periodic pile snapshot. No retrospective pile contents are invented.

## Limits and lead checks

Hidden opponent hand/deck cards remain unknown. The failed confusion attack name is not publicly revealed. QR gives semantic entities, not exact artwork/rarity/printing. Live verification of the prepared new external deck entry remains the lead's responsibility. These are captured in UNCERTAINTIES.json; none represents an uninspected battle turn.

Recommended independent source checks: opening29; first owner hand52.5 and first play53; Poke Ball57.5/60, Research64/66/67; ordinary turn4 first evolution116.5/118 and Research125/126; no-effect Electric Generator152.5/156.2; turn6 hand180.5, retreat190-192, attachment193.5, ending hand195.5, attack196, points204, replacement206, concession214 and final results225. Independent acceptance, shared registration, external save and archival are pending root.

Independent reveal-evidence correction: first turn4 Research draw is named Hatterene at125s, not the still face-down124s frame. Native125s full frame and top/bottom crops retained. Original submission is preserved.
