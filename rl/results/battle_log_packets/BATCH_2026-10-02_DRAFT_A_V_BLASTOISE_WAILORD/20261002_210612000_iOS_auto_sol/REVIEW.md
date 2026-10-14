# Full first-pass battle review

**Source:** 20261002_210612000_iOS.MP4; SHA-256 9dcc8b0fab462433546cc35161d2a5e92ada7a571f4bbff6020ad99fbb72ad03. Reviewer /root/drafta_auto_210612, gpt-6.1-sol, high effort. Review date October2,2026.

**Outcome:** Auto owner wins 3-0 on turn13. Final native evidence F0194.80 shows third point; F0203.00 shows Victory against fixed Blastoise/Wailord computer deck. This is excluded from ladder. Advanced category is established by the owner screenshot receipt ADVANCED_CATEGORY_CONFIRMATION.json, separately from the source setup whose category label is absent.

The source is covered from setup through results, including all13 turns. All11 locator grids (207 nominal1fps samples) were inspected; original-resolution evidence supplies hands, card identities, phase boundaries and consequential state. No source cut is identified. Frame PTS, crop dimensions and hashes are in EXTRACTION_MANIFEST.json and TURN_EVIDENCE.json. The first pass awaits independent acceptance.

Setup0-20s: F0000.50 shows Draft A: Shark Tempo, fixed opponent AI, Auto On. F0015.00 shows allfive opening cards left to right: Lucky Ice Pop, Mega Sharpedo ex, Alolan Vulpix, Irida, Alolan Ninetales ex. Auto places Vulpix Active; computer places Squirtle. Owner goes first. Auto remains checked at retained in-game views with no observed mode change.

## Turn 1: owner, 20-24s

Starting exposed hand: Lucky Ice Pop, Mega Sharpedo ex, Irida, Alolan Ninetales ex, Elegant Cape. Native preplay F0023.00; opponent fan directly counts 4 backs. Ending owner hand 5 cards: Lucky Ice Pop, Mega Sharpedo ex, Irida, Alolan Ninetales ex, Elegant Cape.
1. end_turn , target none: Ends without attack; no warning choice shown (F0023.20).
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row1; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 2: opponent, 24-28s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. energy_attachment , target P-S1: Attach one normal Water from current Energy Zone (F0028.00).
2. end_turn , target none: Ends without attack; no warning choice shown (F0028.00).
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row2; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 3: owner, 28-50s

Starting exposed hand: Lucky Ice Pop, Mega Sharpedo ex, Irida, Alolan Ninetales ex, Elegant Cape, Misty. Native preplay F0031.20; opponent fan directly counts 5 backs. Ending owner hand 3 cards: Lucky Ice Pop, Mega Sharpedo ex, Irida.
1. evolution Alolan Ninetales ex, target O-V1: Vulpix -> Ninetales ex 150HP (F0036.00).
2. supporter Misty, target O-V1: 0 heads, 1 tails; zero Energy (F0041.50).
3. energy_attachment , target O-V1: Attach one normal Water from current Energy Zone (F0044.00).
4. tool Elegant Cape, target O-V1: Effective maximum/current HP 150 -> 180. F0048.90 shows attachment; the before-end hand at F0049.40 shows the intermediate HP count-up at 170. F0052.00 confirms settled 180 HP, Cape and one Water through uninterrupted footage. The resolved endpoint therefore uses composite HP provenance.
5. end_turn , target none: Ends without attack; no warning choice shown (F0049.40).
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row3; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 4: opponent, 50-59s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. evolution Wartortle, target P-S1: Squirtle -> Wartortle90; retain Water1 (F0054.00).
2. energy_attachment , target P-S1: Attach one normal Water from current Energy Zone (F0055.50).
3. stadium Soothing Shore, target shared field: Stadium enters; no healing necessary (F0058.50).
4. end_turn , target none: Ends without attack; no warning choice shown (F0058.50).
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row4; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 5: owner, 59-77s

Starting exposed hand: Lucky Ice Pop, Mega Sharpedo ex, Irida, Poké Ball. Native preplay F0062.20; opponent fan directly counts 4 backs. Ending owner hand 3 cards: Lucky Ice Pop, Mega Sharpedo ex, Irida.
1. item Poké Ball, target owner deck: Find Carvanha (F0066.50).
2. bench Carvanha, target owner bench3: 50HP, zero Energy (F0070.80).
3. energy_attachment , target O-V1: Attach one normal Water from current Energy Zone (F0071.20).
4. attack Binding Snow, target P-S1: 80 damage; opponent Active position blocked from Energy Zone attachment during next opponent turn (F0075.80).
Resolution: 80 damage and Binding Snow attachment-block effect.
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row5; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 6: opponent, 77-87s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. bench Squirtle, target opponent bench2: 70HP, zero Energy (F0081.50).
2. energy_attachment , target P-S2: Attach one normal Water from current Energy Zone (F0081.50, F0086.00).
3. end_turn , target none: Ends without attack; no warning choice shown (F0086.00).
Resolution: Soothing Shore automatically heals Active Wartortle 10 to30.
Resolution: Binding Snow restriction applies through this opponent turn, expires for next owner turn; refreshed by next attack..
Endpoint points 0-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row6; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 7: owner, 87-113.5s

Starting exposed hand: Lucky Ice Pop, Mega Sharpedo ex, Irida, Professor's Research. Native preplay F0090.20; opponent fan directly counts 4 backs. Ending owner hand 4 cards: Lucky Ice Pop, Irida, Copycat, Professor's Research.
1. supporter Professor's Research, target owner deck: Draw Copycat then Research (F0096.20).
2. evolution Mega Sharpedo ex, target O-C1: Carvanha -> Mega Sharpedo ex190 (F0099.50).
3. energy_attachment , target O-C1: Attach one normal Water from current Energy Zone (F0100.80).
4. attack Binding Snow, target P-S1: 80 damage; opponent Active position blocked from Energy Zone attachment during next opponent turn (F0112.50).
Resolution: 80 damage and Binding Snow attachment-block effect.
Resolution: Wartortle knocked out; owner point1.
Resolution: Squirtle promoted.
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 1-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row7; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 8: opponent, 113.5-125s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. item Poké Ball, target opponent deck: One concealed Basic found; identity unknown (F0118.50).
2. bench Wailmer, target opponent bench2: Wailmer100HP, zero Energy before attachment (F0121.30).
3. energy_attachment , target P-W: Attach one normal Water from current Energy Zone (F0122.50).
4. retreat , target P-S2 -> P-W: Squirtle pays/discards one Water; Wailmer becomes Active with one Water (F0123.50).
5. end_turn , target none: Ends without attack; no warning choice shown (F0124.50).
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Resolution: Binding Snow restriction applies through this opponent turn, expires for next owner turn; refreshed by next attack..
Endpoint points 1-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row8; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 9: owner, 125-142s

Starting exposed hand: Lucky Ice Pop, Irida, Copycat, Professor's Research, Lapras. Native preplay F0128.20; opponent fan directly counts 4 backs. Ending owner hand 5 cards: Lucky Ice Pop, Irida, Copycat, Cyrus, Mega Sharpedo ex.
1. supporter Professor's Research, target owner deck: Draw Cyrus then second Mega Sharpedo ex (F0134.00).
2. bench Lapras, target owner bench2: Lapras110, zero Energy initially (F0135.60).
3. energy_attachment , target O-L: Attach one normal Water from current Energy Zone (F0136.80).
4. attack Binding Snow, target P-W: 80 damage; opponent Active position blocked from Energy Zone attachment during next opponent turn (F0140.50).
Resolution: 80 damage and Binding Snow attachment-block effect.
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 1-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row9; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 10: opponent, 142-151s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. energy_attachment , target P-S2: Attach one normal Water from current Energy Zone (F0146.50).
2. end_turn , target none: Ends without attack; no warning choice shown (F0150.00).
Resolution: Soothing Shore automatically heals Active Wailmer20 to40.
Resolution: Binding Snow restriction applies through this opponent turn, expires for next owner turn; refreshed by next attack..
Endpoint points 1-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row10; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 11: owner, 151-170s

Starting exposed hand: Lucky Ice Pop, Irida, Copycat, Cyrus, Mega Sharpedo ex, Alolan Vulpix. Native preplay F0155.20; opponent fan directly counts 5 backs. Ending owner hand 5 cards: Lucky Ice Pop, Irida, Copycat, Cyrus, Mega Sharpedo ex.
1. bench Alolan Vulpix, target owner bench1: Vulpix60, zero Energy initially (F0156.10).
2. energy_attachment , target O-V2: Attach one normal Water from current Energy Zone (F0157.80).
3. attack Binding Snow, target P-W: 80 damage; opponent Active position blocked from Energy Zone attachment during next opponent turn (F0160.20).
Resolution: 80 damage and Binding Snow attachment-block effect.
Resolution: Wailmer knocked out; owner point2.
Resolution: Squirtle promoted.
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 2-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row11; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 12: opponent, 170-176s

Normal computer draw is concealed. Owner hand is unchanged during this opponent turn.
1. bench Frigibax, target opponent bench2: Frigibax60, zero Energy initially (F0174.50).
2. energy_attachment , target P-F: Attach one normal Water from current Energy Zone (F0175.30).
3. end_turn , target none: Ends without attack; no warning choice shown (F0175.30).
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Resolution: Binding Snow restriction applies through this opponent turn, expires for next owner turn; refreshed by next attack..
Endpoint points 2-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row12; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Turn 13: owner, 176-196.5s

Starting exposed hand: Lucky Ice Pop, Irida, Copycat, Cyrus, Mega Sharpedo ex, Alolan Ninetales ex. Native preplay F0180.20; opponent fan directly counts 5 backs. Ending owner hand 5 cards: Lucky Ice Pop, Irida, Copycat, Cyrus, Mega Sharpedo ex.
1. evolution Alolan Ninetales ex, target O-V2: Vulpix -> second Ninetales ex150, retain Water1 (F0183.80).
2. energy_attachment , target O-V2: Attach one normal Water from current Energy Zone (F0185.20).
3. attack Binding Snow, target P-S2: 80 damage; opponent Active position blocked from Energy Zone attachment during next opponent turn (F0187.50).
Resolution: 80 damage and Binding Snow attachment-block effect.
Resolution: Squirtle knocked out; owner point3, terminal win.
Resolution: Game ends before replacement.
Resolution: Soothing Shore end-turn healing check has no HP change to a full-HP Water Active or a knocked-out empty Active..
Endpoint points 3-0. Both boards, HP, physical instances, Water, Cape, active block duration and Energy phases are preserved in ledger row13; attributes use individual provenance and continuous carry-forward. No offered warning or explicit declined option appears.

## Reconciliation and interpretation

Owner hand arithmetic: setup5-Active1=4; normaldraw T1 ->5; T3 +1- evolution1-Misty1-Cape1 ->3; T5 +1-PokeBall1+Carvanha1-bench1 ->3; T7 +1-Research1+draw2-evolution1 ->4; T9 +1-Research1+draw2-benchLapras1 ->5; T11 +1-benchVulpix1 ->5; T13 +1-evolutionNinetales1 ->5. Energy attachments and attacks do not consume hand cards. Research reveal order is preserved separately from later left-to-right fan. Copycat remains held, so there are no Copycat-generated draws.

Opponent HP: Wartortle90-80=10 (T5); Soothing Shore heals20 ->30 (T6); 80 attack KOs T7. Wailmer100-80=20 (T9); Soothing Shore heals20 ->40 (T10); 80 attack KOs T11. Squirtle70-80 KOs T13. The owner Active reaches180HP with Cape and never takes damage. Opponent spends current Water on bench after Binding Snow locks the Active Energy Zone attachment. Wartortle has onlytwo Water with three-Energy attack; computer never attacks in this game.

Strategic interpretation: early Ninetales evolution and the second normal Water make repeated Binding Snow possible despite a failed Misty. The lock constrains Active development while Auto develops Sharpedo, Lapras and the second Vulpix/Ninetales. This single computer win does not establish Draft A superiority over another deck or player policy.

## Recording limits

Neither discard pile is opened. Periodic actual visible tops are retained; play-derived history is explicitly inferential. Opponent concealed draws and Poke Ball result are unknown. Advanced category is owner-supplied screenshot evidence. Exact filmed set/rarity numbers are unverified; the saved20-card log snapshot is a dated owner-version binding, not a reconstruction from hand footage. Requested +1/+3/+6 captures can fall in fast actions or nextturn; each owner turn also has a clear preplay native hand and before-end hand. No unrecorded input or decline is invented.
