# Independent verification: 20261009_195432000_iOS.MP4

**Decision: ACCEPT.** I reconciled the corrected `REVIEW.md`, `COVERAGE.md`, and `FINDINGS.json` with the source-bound, original-resolution proof and all eleven overview sheets. The source file independently hashes to SHA-256 `bc41e4a4b4239027164fccf4401ff10c9c9a0657e4f22e13470f6228789afdfd` and is 313,346,480 bytes. Its recorded duration is 170.702109 seconds. The overview covers setup through the terminal result and tail, with one battle and turns 1 through 8. No second match or recording gap is apparent.

The named opponent is the AI **Miraidon ex Deck (Deluxe Pack: Mega)**. The Auto option is visible OFF at [4 s](../proof_native/t4s.jpg) and ON before the battle at [5 s](../proof_native/t5s.jpg), then checked during play. This is a computer battle under the owner's routing rule, excluded from both external game logs. The [170 s result](../proof_native/t170s.jpg) confirms Victory, owner 2 points to opponent 0, eight turns, owner went second, and 240 damage. The [156 s board](../proof_native/t156s.jpg) has no opposing Active or Benched Pokemon after Magnezone ex is knocked out, and the [158 s score](../proof_native/t158s.jpg) shows only two lit points.

The decisive sequence is coherent. At [109 s](../proof_native/t109s.jpg), the first Storm Blade has reduced Conkeldurr from 150 to 20 HP and left Magnezone ex with three Lightning Energy after its discard. The first hit did not require Guts. On turn 7, Magnezone ex is back to four Energy at [130 s](../proof_native/t130s.jpg), and its second Storm Blade takes Conkeldurr from 20 to zero. The Guts check then succeeds: the [142 s message](../proof_native/t142s.jpg) says Conkeldurr was not knocked out, and [143 s](../proof_native/t143s.jpg) shows 10 HP with no opposing point. Conkeldurr's final Mega Punch deals 100 including weakness, enough to remove Magnezone ex's remaining 80 HP. The three owner attacks account for 40 + 100 + 100 = 240 damage.

I also checked ordinary development, not just the decisive turns: turn 1 Magnemite placement and the no-target Clemont response; turn 3 Magneton evolution, Volt Charge, and two Lightning by turn end; turn 4 the second Timburr, second Fighting Energy, Rare Candy evolution, Copycat, and no attack; and turn 6 the Research draw, Sandshrew Bench, third Fighting Energy, and first Mega Punch. Conkeldurr's Mega Punch shows a three-Energy cost, matching the absence of a turn 4 attack and its turn 6 use. Magnezone ex's Storm Blade shows a three-Lightning cost and discards one Lightning after each attack.

The one material omission found during verification was corrected before acceptance. On turn 5, Volt Charge takes Magneton/Magnezone ex to three Lightning. Magnezone ex still has three at [96 s](../proof_native/t96s.jpg), reaches four by [100 s](../proof_native/t100s.jpg) before its first Storm Blade, and is back to three at 109 s after discarding one. The corrected primary files include the additional normal Lightning attachment and bound it to after 96 s and by 100 s; the exact animation instant is not claimed. The turn 3 origins of Magneton's two Energy and hidden deck or hand contents remain appropriately unassigned.

This was a bounded independent check using the retained overview and native proof, without a duplicate full-video decode. I found no remaining required changes.

## Primary file hashes reconciled

| File | SHA-256 |
| --- | --- |
| `REVIEW.md` | `d64a190fa7265db7fd21cb0720ea6aa53846bc1647c5160772bf0b00a4c85cf5` |
| `COVERAGE.md` | `2ee9f22c068313b613be9af34b373544a831963a7b26061caf656a8dee1f3a90` |
| `FINDINGS.json` | `2724a3f434eb4a871f791b27e9e060893ee28e51f498e5d01d1c62e313b7a601` |
