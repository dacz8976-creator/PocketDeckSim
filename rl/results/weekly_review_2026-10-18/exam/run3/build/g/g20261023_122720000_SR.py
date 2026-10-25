from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_122720000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'; EI = 'Eiscue B1 080'; OR = 'Oricorio A3 066'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; CY = 'Cyrus A2 150'; LL = 'Lillie A3 155'
PL = 'Parasol Lady B3 152'; LIP = 'Lucky Ice Pop B2 145'; SS = 'Soothing Shore B4 154'
# opponent
WU = 'Wurmple B4 001'; SI = 'Silcoon B4 002'; BF = 'Beautifly B4 003'; CA = 'Cascoon B1 006'; DX = 'Dustox B4 005'
LC = 'Leaf Cape A3 147'; AZ = 'Area Zero B3a 074'; RC = 'Red Card P-A 006'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
SHORE = {"card": "Soothing Shore B4 154", "owner": 0}
AMB_WU = 'Opponent Wurmple printing chosen by HP (60) and attack title (Gnaw); B4 001 and B4 156 match'
AMB_WUB = 'Opponent Wurmple under Silcoon: printing chosen by HP (60) and attack title (Gnaw); B4 001 and B4 156 match'
AMB_CA = ('Opponent Cascoon printing chosen by HP (80) only (its attack was not shown); B1 006 (Harden) and B4 004 (Cocoon Collector) '
          'match')
AMB_CAB = ('Opponent Cascoon under each Dustox: printing chosen by HP (80) only; B1 006 and B4 004 match')
AMB_LC = 'Opponent Leaf Cape printing not shown; A3 147, A4b 324 and A4b 325 match'
AP_DX = ("; the Cascoon printing under each Dustox is chosen by HP (80) only (its attack was not shown); the opponent's Leaf Cape "
         "printing is not shown (the first listed printing is used)")




POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, LIP, PL, PR], disc=[], dene='', board=[B(EI, 80), B(OR, 70)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(WU, 60)], ko=0),
  ["Play:Professor's Research", 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active Wurmple (no Bench shown, no draw yet: he went first)",
  ambiguous=[AMB_WU],
  draws={0: [SS, EI]},
  notes="Global 1 = his 1st turn (he went first). Setup (0-38s): Eiscue 80 Active, Oricorio 70 Benched; opening hand those two plus "
        "Copycat, Lucky Ice Pop, Parasol Lady -> 3 in hand. Opponent Wurmple 60 Active (Gnaw shown on global 2), no Bench named. T1 "
        "(39-108s): Research drawn ~41s -> 4; his move: Research ~45s (draws Soothing Shore, 2nd Eiscue), nothing else played, end "
        "turn (no Energy on the first player's first turn)."),
P(G, 3, 2, [0, 0],
  dict(hand=[CC, LIP, PL, SS, EI, SQ], disc=[PR], dene='', board=[B(EI, 80), B(OR, 70)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(WU, 60, 'G')], ko=0),
  ['Place:Squirtle@2', 'Play:Soothing Shore', 'Place:Eiscue@3', 'Play:Copycat', 'Attach:1Water@0 zone', 'Play:Poké Ball', 'EndTurn'],
  D, None,
  approx=AP + "; Bench slots are compacted (the review's Bench reads Eiscue / Oricorio / Squirtle left to right at the end of the "
            "turn; the new Pokémon take the lowest empty slots here)",
  ambiguous=[AMB_WU],
  draws={3: ['-' + LIP, '-' + PL, LIP, PB, PR, WT, PL], 5: [SQ]},
  notes="Global 3 = his 2nd turn. Hand after T1: Copycat, Lucky Ice Pop, Parasol Lady, Soothing Shore, Eiscue; draw Squirtle ~125s -> "
        "6. Opponent T2 (109-122s): draw (4 -> 5), Grass to Wurmple, Gnaw 10 -> 0 by Ice Face. His move in time order: bench Squirtle "
        "~127s (review: right spot; compacted slot 2), Soothing Shore ~131-134s, bench 2nd Eiscue ~135-136s (review: left spot; "
        "compacted slot 3), Copycat ~142s (shuffles Lucky Ice Pop and Parasol Lady; draws five = the opponent's 5: Lucky Ice Pop, Poke "
        "Ball, Research, Wartortle, Parasol Lady), Water to Active Eiscue ~161-162s, Poke Ball ~166s finds the 2nd Squirtle (kept), "
        "end ~174s."),
P(G, 5, 3, [0, 0],
  dict(hand=[LIP, PR, WT, PL, SQ, PB], disc=[PR, CC, PB, SS], dene='', board=[B(EI, 80, 'W'), B(EI, 80), B(OR, 70), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(SI, 80, 'GG', behind=[WU]), B(CA, 80), B(CA, 80)], ko=0),
  ['Evolve:Wartortle@3', 'Play:Poké Ball', "Play:Professor's Research", 'UseStadium', 'Play:Soothing Shore', 'Attach:1Water@0 zone',
   'Attack:Ram'],
  D, None, stadium={"card": "Area Zero B3a 074", "owner": 1},
  approx=AP + "; both Benched Cascoon printings are chosen by HP (80) only (their attack was not shown)",
  ambiguous=[AMB_WUB, AMB_CA],
  draws={1: [], 2: [SS, CY], 3: ['-' + SQ, WT]},
  notes="Global 5 = his 3rd turn. (Area Zero's use, force index 3, is a chance step (v2_helpers.CHANCE_STADIUMS, Oct 25): its draws "
        "record takes the held Squirtle out and puts the drawn Wartortle in.) Hand after T3: Lucky Ice Pop, Research, Wartortle, Parasol Lady, Squirtle; draw Poke Ball ~198s -> 6. "
        "Discard: Research, Copycat, Poke Ball, his Soothing Shore (replaced by Area Zero on T4). Bench left to right per the review's "
        "T3 end line and T7's 'left Bench empty' after the 2nd Eiscue was promoted: Eiscue, Oricorio, Squirtle. Opponent T4 (175-195s): "
        "draw 6, 2nd Grass to Wurmple, Area Zero 5, evolve Silcoon 80 (Cocoon Collector) 4, Cocoon Collector puts two Cascoon 80 from "
        "the deck onto the Bench. His move in time order: evolve benched Squirtle -> Wartortle ~201-204s, Poke Ball ~207s with no Basic "
        "in his deck (found nothing; consumed: his hand at T8's Red Card was five), Research ~213s draws Shore and Cyrus, Area Zero "
        "~228-232s shuffles the held Squirtle and draws Wartortle ~234s, Shore ~236-240s replacing Area Zero, 2nd Water to Active "
        "Eiscue ~242s, Ram ~247-248s (50 to Silcoon)."),
P(G, 7, 4, [0, 1],
  dict(hand=[LIP, PL, CY, WT, SQ], disc=[PR, CC, PB, SS, PB, PR, EI], dene='WW',
       board=[B(EI, 80), B(OR, 70), B(WT, 90, behind=[SQ])], ko=1),
  dict(hand_count=1, disc=[AZ], dene='', board=[B(BF, 110, 'GG', tool=LC, behind=[SI, WU]), B(DX, 120, 'G', behind=[CA]),
                                                 B(DX, 120, behind=[CA])], ko=0),
  ['Attach:1Water@2 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + AP_DX,
  ambiguous=[AMB_WUB, AMB_CAB, AMB_LC],
  notes="Global 7 = his 4th turn. Hand after T5: Lucky Ice Pop, Parasol Lady, Cyrus, Wartortle (Area Zero draw); draw 2nd Squirtle "
        "~306s -> 5. Opponent T6 (250-303s): draw 5, Leaf Cape on Silcoon (30 -> 60 of 110) 4, evolve Beautifly 110/160 3, both "
        "Cascoon -> Dustox 120 (1), Variety Powder Burn and Poison, Grass to the LEFT Dustox, Evoflight 50 after Ice Face (80 -> 30), "
        "checkup Burn + Poison knock out Eiscue (opponent 1 point); its 2 W discarded; 2nd Eiscue promoted from the left Bench spot. Bench "
        "left to right: Oricorio (middle), Wartortle (right), compacted. His move: he starts to bench Squirtle and cancels (no action), "
        "Water to Wartortle ~313-314s (slot 2), confirms the end-turn warning."),
P(G, 9, 5, [0, 1],
  dict(hand=[CC, MB, CY, PL], disc=[PR, CC, PB, SS, PB, PR, EI], dene='WW',
       board=[B(EI, 10, cond=['Confused']), B(OR, 70), B(WT, 90, 'W', behind=[SQ])], ko=1),
  dict(hand_count=1, disc=[AZ, RC], dene='', board=[B(BF, 110, 'GG', tool=LC, behind=[SI, WU]), B(DX, 120, 'G', behind=[CA]),
                                                     B(DX, 120, 'G', behind=[CA])], ko=0),
  ['Evolve:Mega Blastoise ex@2', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + AP_DX,
  ambiguous=[AMB_WUB, AMB_CAB, AMB_LC],
  notes="Global 9 = his 5th turn. Opponent T8 (318-352s): draw (1 -> 2), Red Card (1) shuffles his five-card hand (Lucky Ice Pop, "
        "Parasol Lady, Cyrus, Wartortle, Squirtle) and he draws three: Copycat, Mega Blastoise ex, Cyrus; Grass to the right Dustox; "
        "Variety Powder Confusion and Burn; Evoflight 50 after Ice Face (80 -> 30), Burn 20 -> 10, Heads cures Burn, Confusion stays. "
        "T9 draw Parasol Lady ~354s -> 4. His move: evolve Wartortle -> Mega Blastoise ex ~356-360s (keeps 1 W), 2nd Water to it "
        "~377-379s, confirms the Supporter warning and ends."),
P(G, 11, 6, [0, 2],
  dict(hand=[CC, CY, PL, LL], disc=[PR, CC, PB, SS, PB, PR, EI, EI], dene='WW',
       board=[B(MB, 230, 'WW', behind=[WT, SQ]), B(OR, 70)], ko=2),
  dict(hand_count=2, disc=[AZ, RC], dene='', board=[B(BF, 110, 'GG', tool=LC, behind=[SI, WU]), B(DX, 120, 'GG', behind=[CA]),
                                                     B(DX, 120, 'G', behind=[CA])], ko=0),
  ['Attach:1Water@0 zone', 'Attack:Triple Bombardment'],
  D, None, stadium=SHORE,
  approx=AP + AP_DX,
  ambiguous=[AMB_WUB, AMB_CAB, AMB_LC],
  notes="Global 11 = his 6th turn. Hand after T9: Copycat, Cyrus, Parasol Lady; draw Lillie ~443s -> 4. Opponent T10 (383-440s): draw "
        "(1 -> 2), 2nd Grass to the left Dustox, Evoflight 90 knocks out Eiscue 10 (opponent 2 points); he promotes Mega Blastoise ex "
        "230/2 W, Oricorio 70 sole Bench. His move: 3rd Water to Mega Blastoise ex ~446-448s, Triple Bombardment ~467-470s (he opened "
        "the End Turn warning ~452s and cancelled it; no end-turn action applied)."),
]
