# Independent verification: 20261009_193905000_iOS.MP4

Decision: **ACCEPT**. Required corrections: none.

Reviewer: /root/verify_193905. Bounded independent Sol verification, gpt-6-sol, high effort; actual spawn settings supplied by the lead. Source SHA-256: bade03dea4b20d3b08476f78cf677487ea803905503968aef31ceb60286ecc77. Source duration: 176.924377s, 324,765,990 bytes. Source identity was verified by the lead; this check reused shared native frames and timestamp indexes without a second full decode or media rehash.

## Checks and conclusions

- **Setup and routing:** action_001 at 0s shows Mega Charizard X ex Deck (Deluxe Pack: Mega), Draft A: Shark Tempo, AI and Auto On. The versus screen also identifies AI. This is a computer game, excluded from both Ladder Log and human-only Pause Games.
- **All four knockouts and points:** Torkoal Flamethrower 70 knocks out Carvanha 50, AI point 1. Ninetales Binding Snow knocks out both 100-HP Torkoal, then 70-HP Charmander. Point progression is 0-0, 0-1, 1-1, 2-1, 3-1. Before/after HP, attack animation, removal and point overlays were reconciled.
- **Search and draw resources:** owner Poke Ball visibly returns Alolan Vulpix in T1. AI Poke Ball has a hidden result before second Torkoal benches; the primary correctly qualifies that association. Copycat in T2 and Research in T4/T6 match dense native evidence. Ninetales and Cyrus T1 reveals are draws, not plays; no Irida search is observed.
- **Misty order:** evolution leaves Ninetales with zero Energy. Misty result is 1 head, 1 tail at90.012s (action_085). One attached Water is visible at92.013s (action_087) with ordinary Water still in the Zone. Normal attachment at93.013s (action_088) supplies the second. This enables the first Binding Snow.
- **Energy and damage:** Rainbow Cave discards generated Fire; Flame Patch returns Fire from discard in T2. T4 Research 110.8s (dense_208) precedes Fire to benched Charmander 113.2s, while second Active Torkoal stays unpowered. T5 gives Ninetales a third Water. T6 Flame Patch adds the second Fire to Active Charmander despite the Energy Zone restriction; subsequent Rainbow Cave and normal Bench attachment are distinct routes. Charmander's Flame Tail 30 changes Ninetales 150 to 120. Binding Snow 80 plus Water weakness 20 agrees with each KO; final attack explicitly displays 100 at161.053s (action_151).
- **Independent ordinary-turn sample:** chose owner T1 before primary files were available. Complete action and dense sequence confirms Mega Sharpedo draw, Poke Ball/Vulpix, bench placement, Research/Ninetales/Cyrus draw sequence and pass without attachment or attack. This sample was selected independently of flagged issues.
- **Ending:** T7 leaves Lucky Ice Pop and newly drawn Vulpix in hand, no heal, Ninetales 120 HP and three attached Water. Final KO and owner third point are visible; action_159 at169.055s shows final 3-1. action_160 at175.005s explicitly shows Victory; action_161 at176.005s identifies Ninetales as Card of the Game.

All primary files were read after these source checks. Their seven-turn account, phase coverage, resource ordering, outcome and limits are consistent with the evidence. Their first-pass status correctly leaves lead registration and archival separate from this acceptance.

## Retained proof and limits

Native evidence copies are in evidence/, with timestamps and hashes listed in VERIFICATION.json. All remain 1170 x 2532. The original shared frame indexes provide source-local timestamps; contact sheets were navigation aids.

This is bounded independent verification, not a second full-battle first pass. Opponent hidden draws, hidden Poke Ball face, exact 20-card decks and printing IDs remain unknown. A phone notification partly obscures the T4 fan. No hidden identity, fourth Water attachment or manual owner choice was inferred. No source, index, registration, external game log, simulator or archival change was made here.

## Reconciled primary-file SHA-256

- REVIEW.md: cbff706c10ac99ba14a63555f9f6a032a69b7668a6e1798208c3988b0d8ac3ca
- COVERAGE.md: 8c197809f6c4439647a029502a80f7318104442e84ce5794311a3f394ffa12a2
- FINDINGS.json: f7ff2d75403b92f797477b7dbb4a89a7a5160237ff34d40e041a8ec8d89bba0b
