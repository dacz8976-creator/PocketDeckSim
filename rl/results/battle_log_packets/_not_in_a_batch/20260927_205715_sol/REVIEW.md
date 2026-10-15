# 2026-09-27 20:57:15 battle review

Reviewer/session: `/root/sep27_205715` (Sol). Source identity is in `SOURCE.json`; interval accounting is in `COVERAGE.md`. Times are source video positions, approximately. One continuous Pokémon TCG Pocket match is visible from setup through a terminal result. The lower player is **Dacz8976** and the upper player is **locura**. The named opponent and “Waiting for opponent” UI are visible, but the recording does not separately show a mode selection or establish the opponent's control mode. No Auto setting is established from the available frames.

## Turn account

| Turn / time | Visible account |
|---|---|
| Setup, 00:00-00:15 | Dacz8976 is going first. Galarian Zigzagoon (70 HP) is selected Active and Deino (60 HP) goes to the Bench. locura opens a lone Magikarp (30 HP). Initial hand shows Hydreigon, Galarian Obstagoon and Professor's Research, but those are not yet playable evolutions. [setup](frames/t012.jpg) |
| 1 Dacz8976, 00:15-00:40 | Draw is **Deceptive Needle**, attached to Active Galarian Zigzagoon. Professor's Research draws two cards. A second Galarian Zigzagoon (70 HP) is put on the Bench; Rare Candy is visible in hand but not played. No attack or Energy attachment is visible. At turn end, Deceptive Needle deals 10 to Active Magikarp, reducing it from 30 to 20 HP. Both point tracks remain empty. [Tool card](frames/t017.jpg), [attached Tool](frames/t022.jpg), [10 damage](frames/t038.jpg) |
| 2 locura, 00:40-01:13 | locura attaches Water Energy to Magikarp. Sabrina is played, requiring Dacz8976 to switch; the other Galarian Zigzagoon becomes Active at 70 HP, while the original Zigzagoon with Deceptive Needle moves to the Bench. locura plays Lucky Ice Pop on Magikarp, healing it from 20 to 30 HP; the coin result is **tails**. No Magikarp attack or point change is visible. [turn 2](frames/t040.jpg), [Sabrina](frames/t056.jpg), [switched board](frames/t061.jpg), [healed Magikarp](frames/t073.jpg) |
| 3 Dacz8976, 01:13-01:33 | Deino evolves into Zweilous (90 HP) on the Bench. Rare Candy is played on Active Galarian Zigzagoon, evolving it directly into Galarian Obstagoon (150 HP); the other Zigzagoon with Deceptive Needle stays Benched. Dark Energy is attached to Active Obstagoon. No attack occurs before the turn ends, and Magikarp remains at 30 HP. All point tracks remain empty. [Zweilous](frames/t079.jpg), [Obstagoon evolution](frames/t088.jpg), [end of turn](frames/t093.jpg) |
| 4 locura, 01:33-01:42.06 | The opponent turn begins with Magikarp still Active at 30 HP and no Bench. Before a further play or attack is visible, the message explicitly says **“Your opponent conceded”** at about 01:37. The result animation then explicitly shows **Victory!** for Dacz8976 at about 01:41.3. [concession](frames/t097_concession.jpg), [Victory](frames/t101_victory.jpg) |

## Outcome and interpretation

- **Outcome:** Dacz8976 wins by opponent concession during turn 4. This is an explicit result, not an inferred knockout. Score remains 0-0 throughout the visible board state; neither side takes a point before concession.
- **Visible board at concession:** locura has Magikarp at 30 HP with Water Energy and no Bench. Dacz8976 has Active Galarian Obstagoon at 150 HP with one Dark Energy, plus Benched Zweilous at 90 HP and Galarian Zigzagoon at 70 HP with Deceptive Needle. The attack text on Obstagoon shows Merciless Strike needs two Dark Energy, so no immediate attack with the one visible Energy is established.
- **No strategic grade:** The opponent concedes before a substantive exchange. The recording does not establish why locura conceded. It cannot demonstrate the later effectiveness of this setup or a rules defect.
- **Recording relationship:** The later `20260927_205926000_iOS.MP4` starts fresh matchmaking against a different opponent, so this is not a split battle requiring a continuation.

## Limits

- Unknown opponent hand and deck contents stay unknown. The source does not show any hidden cards being revealed.
- Full-file AAC decoding found mean and maximum volume at -91.0 dB and silence at a -45 dB threshold across 102.045737 seconds. No audible speech is available for transcription.
- Selected original-source stills document the timeline; one-second full-clip scanning and targeted source checks were also performed. Lead acceptance, review logging, and source move are recorded in this packet and the folder indexes.
