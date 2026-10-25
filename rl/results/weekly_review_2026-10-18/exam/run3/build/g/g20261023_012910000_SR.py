from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_012910000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'; EI = 'Eiscue B1 080'; OR = 'Oricorio A3 066'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; CY = 'Cyrus A2 150'; LL = 'Lillie A3 155'
PL = 'Parasol Lady B3 152'; LIP = 'Lucky Ice Pop B2 145'; SS = 'Soothing Shore B4 154'
# opponent
HM = 'Hitmonchan ex B1 124'; RI = 'Riolu A2 091'; ML = 'Mega Lucario ex B3 081'; GC = 'Giant Cape A2 147'; EC = 'Elegant Cape B3b 065'
OPR = "Professor's Research A4b 373"; OCC = 'Copycat B1 225'; OLF = 'Leaf A1a 068'; OXS = 'X Speed P-A 002'; OPB = 'Poké Ball A2b 111'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
SHORE = {"card": "Soothing Shore B4 154", "owner": 0}
AMB_HM = 'Opponent Hitmonchan ex printing chosen by HP (130) and attack title (Quick Straight); B1 124, B1 261, B1 279 and B3 229 match'
AMB_ML = 'Opponent Mega Lucario ex printing chosen by HP (190) and attack title (Fighting Pulse); B3 081, B3 184 and B3 204 match'
AMB_RI = ("Opponent Riolu: its HP and attack were not shown; printing A2 091 (60 HP) is the first listed Riolu; Riolu printings have "
          "60 or 70 HP")
AMB_RIB = ("Opponent Riolu under each Mega Lucario ex: its HP and attack were not shown; printing A2 091 is the first listed Riolu")
AMB_GC = 'Opponent Giant Cape printing not shown; A2 147, A4b 320 and A4b 321 match'
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 and P-A 007 match"
AMB_CC = 'Opponent Copycat printing not shown; B1 225 and B1 270 match'
AMB_LF = 'Opponent Leaf printing not shown; A1a 068, A1a 082, A4b 346 and A4b 347 match'
AMB_PB = 'Opponent Poké Ball printing not shown; A2b 111 and P-A 005 match'
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[MB, PR, CC, CC, PB], disc=[], dene='', board=[B(OR, 70)], ko=0),
  dict(hand_count=4, disc=[OPR], dene='', board=[B(HM, 150, tool=GC), B(RI, 60)], ko=0),
  ['Play:Poké Ball', 'Place:Squirtle@1', "Play:Professor's Research", 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; his draw for the turn is not named in the review: Poké Ball, the only card he played that was not in his opening "
            "five; the opponent's Riolu HP is not shown (60 used, the first listed printing); the opponent's Trainer printings are not "
            "shown (the first listed printings are used)",
  ambiguous=[AMB_HM, AMB_RI, AMB_GC, AMB_PR],
  draws={0: [SQ], 2: [SS, LIP]},
  notes="Global 2 = his 1st turn (he went second). Opening five (19-35s): Oricorio, Mega Blastoise ex, Professor's Research, two "
        "Copycat; Oricorio 70 Active, empty Bench -> 4 in hand. His draw is not named; he plays a Poke Ball at ~53-56s that was not in "
        "the opening five, so the draw was Poke Ball -> 5 cards. Opponent global 1 (35-52s): opening 5 - Hitmonchan ex Active = 4, draw "
        "5, bench Riolu 4, Professor's Research -1 +2 = 5, Giant Cape on Active Hitmonchan ex (130 -> 150) = 4; no Energy. His move in "
        "time order: Poke Ball ~56s finds Squirtle ~58s, bench it ~61-63s (slot 1), Professor's Research ~66s draws Soothing Shore and "
        "Lucky Ice Pop (both kept), Water to benched Squirtle ~71s, pass without attack."),
P(G, 4, 2, [0, 0],
  dict(hand=[MB, CC, CC, SS, LIP, PR], disc=[PB, PR], dene='', board=[B(OR, 70), B(SQ, 60, 'W')], ko=0),
  dict(hand_count=4, disc=[OPR, OPR], dene='', board=[B(HM, 150, 'F', tool=GC), B(RI, 60), B(ML, 190, behind=[RI])], ko=0),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Place:Eiscue@2', 'Play:Soothing Shore', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Riolu HP is not shown (60 used, the first listed printing); the opponent's Trainer printings are not "
            "shown (the first listed printings are used); the second card his Professor's Research drew is not named in the review: "
            "Lillie is a stand-in for it in the after-draw check only",
  ambiguous=[AMB_HM, AMB_ML, AMB_RI, AMB_RIB, AMB_GC, AMB_PR],
  draws={0: [PB, LL], 1: [EI]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Mega Blastoise ex, two Copycat, Soothing Shore, Lucky Ice Pop; draw "
        "Professor's Research (~90-96s) -> 6. Board: Oricorio 70; Squirtle 60/1 W. Discard Poke Ball, Professor's Research. Opponent "
        "global 3 (74-90s): 4 + draw 5, Professor's Research -1 +2 = 6, bench 2nd Riolu 5, evolve the RIGHT (first) Riolu into Mega "
        "Lucario ex 190 = 4; Fighting to Active Hitmonchan ex; Quick Straight blocked by Safeguard. Bench left to right: the 2nd Riolu "
        "(middle; it is the 'middle Riolu' evolved on global 5), Mega Lucario ex (right). His move in time order: Professor's Research "
        "~96s (draws two: Poke Ball, inspected ~99s, and a card the review does not name; Lillie is the variant stand-in), Poke Ball "
        "~102s finds Eiscue ~104s, bench ~107s (slot 2), Soothing Shore ~114s, Water to Squirtle ~116-117s, pass."),
P(G, 10, 5, [0, 0],
  dict(hand=[PL, LL, MB, CC], disc=[PB, PR, PR, PB, CC], dene='',
       board=[B(OR, 70), B(SQ, 60, 'WWWW'), B(EI, 80), B(EI, 80)], ko=0),
  dict(hand_count=5, disc=[OPR, OPR, OCC], dene='',
       board=[B(HM, 150, 'F', tool=GC), B(ML, 190, behind=[RI]), B(ML, 220, 'FFF', tool=EC, behind=[RI])], ko=0),
  ['Play:Copycat', 'Evolve:Wartortle@1', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Trainer printings are not shown (the first listed printings are used)",
  ambiguous=[AMB_HM, AMB_ML, AMB_RIB, AMB_GC, AMB_PR, AMB_CC],
  draws={0: ['-' + PL, '-' + LL, '-' + MB, LL, SS, WT, MB, SQ]},
  notes="Global 10 = his 5th turn. Hand: after global 4 he held Mega Blastoise ex, two Copycat, Lucky Ice Pop and the unnamed card; "
        "global 6 draw Cyrus, Copycat (~151s) shuffled Mega Blastoise ex, Copycat, Lucky Ice Pop, the unnamed card and Cyrus away and drew "
        "Eiscue, Parasol Lady, Lillie (3 = the opponent's 3); Eiscue benched; global 8 draw Mega Blastoise ex (~179s); global 10 draw "
        "Copycat (~197s) -> Parasol Lady, Lillie, Mega Blastoise ex, Copycat. Discard: Poke Ball x2, Professor's Research x2, Copycat. "
        "Board: Oricorio 70; Squirtle 60 with 4 W (Water on global 2, 4, 6, 8); Eiscue 80 (global 4), Eiscue 80 (global 6), Bench in "
        "order benched. Soothing Shore (his, global 4) in play. Opponent: Hitmonchan ex 150 Giant Cape, 1 F; middle Mega Lucario ex 190 "
        "(global 5), right Mega Lucario ex 220 with Elegant Cape and 3 F (global 5, 7, 9). Opponent hand: 4 after global 3; global 5 "
        "draw 5, Copycat -1 then draws 5 (his 5), evolve 4, Elegant Cape 3; global 7 draw 4; global 9 draw 5 (= his Copycat's 5 draws). "
        "His move: Copycat ~201s (draws Lillie, Soothing Shore, Wartortle, Mega Blastoise ex, Squirtle), evolve Squirtle -> Wartortle "
        "~211-214s, 5th Water to Wartortle ~217s, pass."),
P(G, 12, 6, [0, 0],
  dict(hand=[LL, SS, MB, SQ, CY], disc=[PB, PR, PR, PB, CC, CC], dene='',
       board=[B(OR, 70), B(WT, 90, 'WWWWW', behind=[SQ]), B(EI, 80), B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[OPR, OPR, OCC, OLF, OXS], dene='',
       board=[B(ML, 220, 'FFFF', tool=EC, behind=[RI]), B(ML, 190, behind=[RI]), B(HM, 150, 'F', tool=GC)], ko=0),
  ['Evolve:Mega Blastoise ex@1', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Trainer printings are not shown (the first listed printings are used)",
  ambiguous=[AMB_HM, AMB_ML, AMB_RIB, AMB_GC, AMB_PR, AMB_CC, AMB_LF],
  notes="Global 12 = his 6th turn. Hand after global 10: Lillie, Soothing Shore, Mega Blastoise ex, Squirtle; draw Cyrus ~247s -> 5. "
        "Board: Oricorio 70; Wartortle 90 with 5 W; Eiscue 80 x2. Opponent global 11 (219-245s): draw 6, 4th Fighting to the caped Mega "
        "Lucario, Leaf 5, X Speed 4, retreat Hitmonchan ex (keeps its Cape and 1 F, no Energy discarded) for the caped Mega Lucario 220; "
        "Fighting Pulse blocked by Safeguard. Opponent Bench left to right: the uncaped (middle) Mega Lucario 190, Hitmonchan ex 150 at "
        "the right where the caped Mega Lucario was. His move: evolve Wartortle -> Mega Blastoise ex ~251-253s (keeps 5 W), Water to "
        "Active Oricorio ~255-257s, pass without attack."),
P(G, 14, 7, [0, 0],
  dict(hand=[LL, SS, SQ, CY, WT], disc=[PB, PR, PR, PB, CC, CC], dene='',
       board=[B(OR, 70, 'W'), B(MB, 230, 'WWWWW', behind=[WT, SQ]), B(EI, 80), B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[OPR, OPR, OCC, OLF, OXS, OPB], dene='',
       board=[B(ML, 220, 'FFFFF', tool=EC, behind=[RI]), B(HM, 130), B(ML, 190, behind=[RI]), B(HM, 150, 'F', tool=GC)], ko=0),
  ['Retreat:1', 'Attach:1Water@0 zone', 'Attack:Triple Bombardment',
   'ApplyDamage{attacking_ref:(0,0),targets:[(130,1,0),(50,1,1),(50,1,3)],is_from_active_attack:true}'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Trainer printings are not shown (the first listed printings are used)",
  ambiguous=[AMB_HM, AMB_ML, AMB_RIB, AMB_GC, AMB_PR, AMB_CC, AMB_LF, AMB_PB],
  notes="Global 14 = his 7th turn. Hand after global 12: Lillie, Soothing Shore, Squirtle, Cyrus; draw Wartortle ~275s -> 5. Board: "
        "Oricorio 70 with 1 W (global 12); Mega Blastoise ex 230 with 5 W; Eiscue 80 x2. Opponent global 13 (258-273s): draw 5, Poke Ball "
        "~261s finds the 2nd Hitmonchan ex (5), bench it LEFT ~266-267s (4); 5th Fighting to the Active caped Mega Lucario 220; Fighting "
        "Pulse blocked. Opponent Bench left to right: Hitmonchan ex 130, Mega Lucario ex 190, caped Hitmonchan ex 150/1 F. His move in "
        "time order: retreat Oricorio ~277-280s discarding its 1 W, Mega Blastoise ex comes in; 6th Water to Mega Blastoise ex ~283s; "
        "Triple Bombardment with both Benched Hitmonchan ex chosen for the 50s (~286-294s)."),
]
