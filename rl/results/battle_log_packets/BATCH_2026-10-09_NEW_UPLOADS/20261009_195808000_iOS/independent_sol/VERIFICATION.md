# Independent verification: 20261009_195808000_iOS.MP4

Decision: **ACCEPT**. Verifier: `/root/verify_195808`, model `gpt-6-sol`, reasoning effort `high`. Source SHA-256: `0bb422f9b945c7f3b02b39c318d408ecfa420be5eda2acd1bd9b9612536dd410`.

The final packet accurately identifies one computer battle against **Mega Gardevoir ex Deck (Deluxe Pack: Mega)**. The AI label is visible, Auto changes from Off on the setup screen to On before play, and the owner goes second with New deck 16. The terminal result is **Defeat, owner 1 to computer 3**. Exclusion from the Ladder Log and human-only Pause Games log is correct.

I independently checked setup, Auto, all four knockouts and point transitions, the visible Poké Ball and Strange Singing searches, Rare Candy evolutions, ordinary turns, consequential Energy attachments, damage, both Shattering Crystal tails, and the result. Meloetta's 30 remaining HP is removed by Glimmora's displayed 50 attack damage before Poison damage. Mega Gardevoir's Fantasia Force starts with two Psychic Energy, deals 110, and adds three Energy from the zone: the post-attack board shows three on Gardevoir and two on Diancie. Diancie later reaches three Psychic Energy for Brilliant Storm's 160 damage, then four for its final 180 damage. Kingambit's 140 attack reflects the owner's two previously Knocked Out Glimmora. Both Shattering Crystal tails award the computer its points. The score path is 0-0, 1-0, 1-1, 1-2, 1-3.

The primary review covers 0.000-242.227 s, including the post-result tail. Original-resolution proof frames checked include `native_proof/5.jpg`, `90.jpg`, `104.jpg`, `111.jpg`, `121.jpg`, `122.jpg`, `124.jpg`, `132.jpg`, `134.jpg`, `137.jpg`, `160.jpg`, `172.jpg`, `175.jpg`, `181.jpg`, `186.jpg`, `214.jpg`, `216.jpg`, `219.jpg`, `228.jpg`, `234.jpg`, and `235.jpg`. Overview sheets and the dense 78-86 s sheets supported intervening play. This was a bounded independent check, not a second full decode. Hidden opponent cards and the complete owner deck list remain unknown.

Corrections reconciled before acceptance: direct Meloetta attack KO, Strange Singing's random Pokémon search, ordinary Energy attachments, Fantasia Force's three-Energy acceleration and final allocation, Brilliant Storm's whole-board Energy count, and Kingambit's bonus from the owner's two lost Glimmora. Required changes: none.

Final primary files read and reconciled (SHA-256):

| File | SHA-256 |
| --- | --- |
| `REVIEW.md` | `20dbbe1a8eadc3542876a6872dd321b45ef02f41257ace97aa9127366a88ec6e` |
| `COVERAGE.md` | `3d1e7985d99b5cadadccf858d698ffc46c2e2ea8025a2fb1bd643bbecfcf43c3` |
| `FINDINGS.json` | `601b79e335bcfb3fa74dfd0c7f8bb2e99b24e009fdf6cdbcc119e86c300f40e0` |
