# Ogerpon lethal Confusion Gas sequence

Source: `/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/20260908_012720000_iOS.MP4`  
Source SHA-256: `b9e76626643d8950cb7a4277487da2262b5fa96faf9e87454495ebe896d47085`  
Focused resolution window: 188–205 seconds

## Finding

The earlier board reading was correct, and the intervening action is visible. At about 188 seconds the opponent plays **Cyrus**, whose displayed text switches a damaged opposing Benched Pokémon into the Active Spot. At 189 seconds **Whimsicott ex** is Active at 140 HP and **Teal Mask Ogerpon ex** is Benched at 40 HP. The switch animation follows, and by 192.5 seconds Ogerpon is Active while Whimsicott is Benched.

The settled pre-attack board at 193.5 seconds shows:

- Attacker: **Team Rocket's Weezing ex**, 140 HP, with two Darkness Energy.
- Target: **Teal Mask Ogerpon ex**, 40 remaining HP, with one Grass Energy and **Leaf Cape** attached.
- Owner Bench: Whimsicott ex at 140 HP.
- Points before the attack: owner 2, opponent 0.
- The green checked **Auto** control remains visible.

The attachment is not Clear Veil. Supporting frames show Leaf Cape in hand at 24 seconds; at 48 seconds that card is gone from the hand, the same green attachment thumbnail appears beside Ogerpon, and a `+30 HP` callout is displayed. At 52 seconds Ogerpon has risen from 120 to 150 remaining HP. This identifies the attachment as Leaf Cape and its visible contribution as HP only.

At 194–195.5 seconds Weezing ex uses **Confusion Gas**, whose displayed card text shows 60 damage and an effect that Confuses the opposing Active. The 196-second frame displays 60 damage over Ogerpon, and the next settled board shows Ogerpon at 0 HP. During the ensuing removal animation, at 198–200 seconds, the game displays **“Teal Mask Ogerpon ex didn't become Confused.”** Ogerpon is then removed and the opponent receives **+2 points** at 201–203 seconds. The post-resolution board at 204 seconds has no Ogerpon in play and shows the opponent at 2 points.

The visible order is therefore Cyrus gust, lethal attack damage, a failed Confusion result while the target is at 0 HP and dissolving, knockout removal, then point award. Because Ogerpon has Grass Energy and its only attached Tool is the HP-only Leaf Cape, the prevention shown here is attributable to its displayed **Soothing Wind** Ability. This directly establishes that Soothing Wind still prevents the attack's Special Condition on this lethal hit before knockout cleanup completes. The recording cannot expose every internal callback boundary, and it does not show recovery caused by attaching Energy.

The earlier Poison sequence is outside this focused resolution window and is not re-attributed here.

## Method

Eighteen low-resolution frames were independently sought at one-second intervals from 188 through 205 seconds. Seven native-resolution frames checked the settled board and attack/removal boundaries at 189.0, 192.5, 193.5, 195.5, 196.5, 198.5, and 201.5 seconds. A cropped native view at 193.5 checked Energy and attachments. Fifteen additional sparse supporting frames between 24 and 56 seconds isolated the Leaf Cape identity; only 24, 48, and 52 seconds are needed for that conclusion. Every decode used one thread and emitted one frame; the recording was not decoded end to end. No OCR, engine/source edit, simulation, or Cargo command was used.
