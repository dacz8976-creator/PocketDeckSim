# Guide update: 20261002_210952000_iOS.MP4

Author: gpt-6-astra, high effort. Status: awaiting separate independent review.

Fresh native reads cover every owner turn start. Bench positions are screen left, middle and right. Each row below gives current/max HP and attached Water; every unlisted slot is explicitly empty in the JSON. Tools, evolution history and evidence are recorded per Pokemon.

| Turn | Source PTS | Owner Active; Bench 1 / 2 / 3 | Opponent Active; Bench 1 / 2 / 3 | Points |
|---|---:|---|---|---|
| 2 | 31.4133 | Lapras 110/110 HP, W0; empty / empty / empty | Wailmer 100/100 HP, W0; empty / empty / Frigibax 60/60 HP, W0 | 0-0 |
| 4 | 63.305 | Lapras 110/110 HP, W1; empty / empty / Alolan Vulpix 60/60 HP, W0 | Wailmer 100/100 HP, W1; Squirtle 70/70 HP, W0 / empty / Arctibax 90/90 HP, W0 | 0-0 |
| 6 | 88.4133 | Lapras 50/110 HP, W2; empty / empty / Alolan Ninetales ex 150/150 HP, W0 | Wailmer 100/100 HP, W3; Wartortle 90/90 HP, W0 / empty / Baxcalibur 140/140 HP, W0 | 0-0 |
| 8 | 141.4 | Lapras 110/110 HP, W3; empty / empty / Alolan Ninetales ex 150/150 HP, W0 | Baxcalibur 140/140 HP, W1; Wartortle 90/90 HP, W1 / empty / Wailmer 50/100 HP, W1 | 0-0 |
| 10 | 165.41 | Lapras 110/110 HP, W3; empty / Carvanha 50/50 HP, W0 / Alolan Ninetales ex 150/150 HP, W1 | Baxcalibur 90/140 HP, W2; Wartortle 90/90 HP, W2 / Wailmer 100/100 HP, W0 / Wailmer 70/100 HP, W1 | 0-0 |
| 12 | 195.407 | Lapras 110/110 HP, W3; empty / Mega Sharpedo ex 190/190 HP, W0 / Alolan Ninetales ex 150/150 HP, W2 | Wailmer 100/100 HP, W0; Wartortle 90/90 HP, W3 / Baxcalibur 20/140 HP, W0 / Wailmer 90/100 HP, W1 | 0-0 |
| 14 | 221.413 | Lapras 110/110 HP, W3; empty / Mega Sharpedo ex 190/190 HP, W1 / Alolan Ninetales ex 150/150 HP, W2 | Wailmer 50/100 HP, W1; Mega Blastoise ex 230/230 HP, W3 / Baxcalibur 20/140 HP, W0 / Wailmer 100/100 HP, W2 | 0-0 |
| 16 | 261.407 | Alolan Ninetales ex 150/150 HP, W2; Carvanha 50/50 HP, W1 / Mega Sharpedo ex 190/190 HP, W1 / empty | Mega Blastoise ex 230/230 HP, W5; empty / Baxcalibur 20/140 HP, W0 / Wailmer 100/100 HP, W2 | 1-1 |
| 18 | 290.402 | Alolan Ninetales ex 20/150 HP, W2; Mega Sharpedo ex 190/190 HP, W1 / Mega Sharpedo ex 190/190 HP, W1 / Alolan Vulpix 60/60 HP, W1 | Mega Blastoise ex 170/230 HP, W5; Frigibax 60/60 HP, W0 / Baxcalibur 20/140 HP, W0 / Wailmer 100/100 HP, W3 | 1-1 |

Soothing Shore is first present at the owner-start snapshot for turn 4, remains in later snapshots, and belongs to the opponent. It is excluded from the owner inventory.

Every owner turn is attributed to game Auto with the visible control anchor and limits listed in JSON. No toggle or override is observed in the reviewed sequence. Each owner-start image visibly shows checked Auto.

On opponent turn 15, Auto promotes the original right Ninetales after Lapras is knocked out. At 254.3 seconds the visible Bench candidates are Carvanha left, Sharpedo middle and Ninetales right. Ninetales enlarges at 255.4 and occupies Active at 256.4. At measured253.503 the written prompt says "Please choose a Pokémon to switch in", with the three Bench candidates highlighted. No human touch is visible; Auto remains checked. The final turn knocks out that same old Ninetales on the Bench while Active Sharpedo survives at 60 HP; the game ends without another owner choice. All other opponent turns have explicit no-observed-choice records.

Lower evolution faces are not freshly readable in current views. The JSON links each known lower card to its earlier visible top and evolution anchor in this recording. No stack is inferred from the supplied deck list. Neither discard pile is opened; only exposed top cards are named, and discard totals remain unknown.

The companion inventory supports at least 19 distinct owner cards. It does not visually recover the exact 20-card deck. Repeated hand/board sightings are not added together. See SEEN_CARD_INVENTORY.md and its JSON for copy evidence.

No original movie, frozen core file, external log or shared index was changed. No new frames were extracted. Independent acceptance is pending.

Independent correction retains the explicit switch-in prompt in independent_sol:F0253.50. Original four-file guide submission remains preserved in guide_submission_before_repair.
