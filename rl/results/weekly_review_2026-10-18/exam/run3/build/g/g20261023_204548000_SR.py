from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_204548000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'; EI = 'Eiscue B1 080'; OR = 'Oricorio A3 066'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; CY = 'Cyrus A2 150'; LL = 'Lillie A3 155'
LIP = 'Lucky Ice Pop B2 145'; SS = 'Soothing Shore B4 154'
# opponent
AGP = 'Alolan Grimer P-A 072'; AGS = 'Alolan Grimer A3 110'; MUK = 'Alolan Muk B2 097'; MK = 'Mega Kangaskhan ex B2 127'
OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
SHORE = {"card": "Soothing Shore B4 154", "owner": 0}
TRAINERS = "; the opponent's Trainer printings are not shown (the first listed printings are used)"
HANDGAP = ("; his Copycat on global 11 drew 3 (the review: the opponent's three cards), while the opponent's visible plays give 7 "
           "there; with no play on global 10, 4 cards left the opponent's hand unseen on one or more of global 2, 4, 6 and 8, so this "
           "count may be too high by up to 4")
AMB_AGS = ('Opponent second Alolan Grimer printing chosen by HP (70) and attack title (Sludge Toss); A3 110, A4b 233 and A4b 234 '
           'match')
AMB_MUK = 'Opponent Alolan Muk printing chosen by HP (110), Ability title (Power of Alchemy) and attack title (Sludge Bomb); B2 097 and B2 173 match'
AMB_MK = ('Opponent Mega Kangaskhan ex printing chosen by HP (180) and attack title (Double-Punching Family); B2 127, B2 189, B2 202 '
          'and B4 231 match')
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 and P-A 007 match"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[SS, PB, LIP, OR], disc=[], dene='', board=[B(EI, 80), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(AGP, 70)], ko=0),
  ['Play:Poké Ball', 'Place:Oricorio@2', 'Play:Soothing Shore', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active Alolan Grimer (no Bench, no draw yet: he went first)",
  draws={0: [SQ]},
  notes="Global 1 = his 1st turn (he went first). Setup (0-35s): opening five Eiscue, Squirtle, Soothing Shore, Poke Ball, Lucky Ice "
        "Pop; Eiscue 80 Active, Squirtle 60 Benched -> Shore, Poke Ball, Lucky Ice Pop; opponent Alolan Grimer 70 Active (the Poison Gas "
        "one, P-A 072), no Bench. Global 1 (36-61s): draw Oricorio -> 4. His move in time order: Poke Ball 40-43s finds the 2nd Squirtle "
        "(kept), bench Oricorio 46-48s (compacted slot 2; the review's end-of-turn Bench reads Oricorio, Squirtle), Soothing Shore 58-59s, "
        "end (no Energy on the first player's first turn)."),
P(G, 3, 2, [0, 0],
  dict(hand=[LIP, SQ, SS], disc=[PB], dene='', board=[B(EI, 70, cond=['Poisoned']), B(OR, 70), B(SQ, 60)], ko=0),
  dict(hand_count=6, disc=[OPR], dene='', board=[B(AGP, 70, 'D')], ko=0),
  ['Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + HANDGAP + "; Bench order Oricorio, Squirtle from the review's end-of-global-1 line, read left to right",
  ambiguous=[AMB_PR],
  notes="Global 3 = his 2nd turn. Hand after global 1: Lucky Ice Pop, Squirtle; draw 2nd Soothing Shore -> 3. Opponent global 2 "
        "(62-87s): 4 + draw 5, Darkness to Grimer, Research -1 +2 = 6, Poison Gas poisons Eiscue, checkup 80 -> 70. His move: Water to "
        "Active Eiscue 91-93s, no attack (Shore then heals 10, Poison 10 back to 70)."),
P(G, 5, 3, [0, 0],
  dict(hand=[LIP, SQ, SS, PR], disc=[PB], dene='', board=[B(EI, 60, 'W', cond=['Poisoned']), B(OR, 70), B(SQ, 60)], ko=0),
  dict(hand_count=6, disc=[OPR, OPR], dene='', board=[B(MUK, 110, 'DD', behind=[AGP]), B(AGS, 70)], ko=0),
  ["Play:Professor's Research", 'Evolve:Wartortle@2', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + HANDGAP + "; Bench order Oricorio, Squirtle from the review's end-of-global-1 line, read left to right",
  ambiguous=[AMB_AGS, AMB_MUK, AMB_PR],
  draws={0: [WT, CY]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Lucky Ice Pop, Squirtle, Shore; draw Research -> 4. Eiscue 70 after global 3; "
        "opponent global 4 (102-121s): draw 7, 2nd Darkness to Grimer, Research -1 +2 = 8, bench 2nd Alolan Grimer 70 (Sludge Toss) 7, "
        "evolve Active -> Alolan Muk 110 (Power of Alchemy) 6; no attack; Poison 70 -> 60. His move: Research 125-127s draws Wartortle "
        "and Cyrus, evolve benched Squirtle -> Wartortle 131-133s, Water to Wartortle 149-151s, end."),
P(G, 7, 4, [0, 1],
  dict(hand=[LIP, SQ, SS, CY, PB], disc=[PB, PR, EI], dene='W', board=[B(OR, 70), B(WT, 90, 'W', behind=[SQ])], ko=1),
  dict(hand_count=5, disc=[OPR, OPR], dene='', board=[B(MUK, 110, 'DDD', behind=[AGP]), B(MUK, 110, behind=[AGS]), B(MK, 180)], ko=0),
  ['Play:Poké Ball', 'Attach:1Water@1 zone', 'Place:Eiscue@2', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + HANDGAP + "; the opponent's Bench is listed in the order benched (no arrangement given)",
  ambiguous=[AMB_AGS, AMB_MUK, AMB_MK, AMB_PR],
  draws={0: [EI]},
  notes="Global 7 = his 4th turn. Hand after global 5: Lucky Ice Pop, Squirtle, Shore, Cyrus; draw Poke Ball -> 5. Opponent global 6 "
        "(159-188s): draw 7, 3rd Darkness to Active Muk, bench Mega Kangaskhan ex 180 (6), evolve 2nd Grimer -> 2nd Muk 110 (5), Sludge "
        "Bomb 70 knocks out Eiscue 70 (its 1 W discarded; opponent 1 point), he promotes Oricorio; Bench Wartortle 90/1 W. His move in "
        "time order: Poke Ball 192-195s finds the 2nd Eiscue, 2nd Water to Wartortle 203-205s, bench Eiscue 207-208s (compacted slot "
        "2), end."),
P(G, 9, 5, [0, 2],
  dict(hand=[LIP, SQ, SS, CY, MB], disc=[PB, PR, EI, PB, OR], dene='W', board=[B(WT, 90, 'WW', behind=[SQ]), B(EI, 80)], ko=2),
  dict(hand_count=2, disc=[OPR, OPR], dene='', board=[B(MUK, 110, 'DDD', behind=[AGP]), B(MUK, 110, behind=[AGS]), B(MK, 180, 'D')],
       ko=0),
  ['Evolve:Mega Blastoise ex@0', 'Attach:1Water@0 zone', 'Attack:Triple Bombardment'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's hand (2) is back-computed: his Copycat on global 11 drew 3 (the review: the opponent's three "
            "cards), the opponent drew 1 on global 10 and the review observes no Trainer or board change that turn, so 2 at the end of "
            "global 8; the visible plays give 6, so 4 cards left the opponent's hand unseen on or before global 8"
            "; the opponent's Bench is listed in the order benched (no arrangement given)",
  ambiguous=[AMB_AGS, AMB_MUK, AMB_MK, AMB_PR],
  notes="Global 9 = his 5th turn. Hand after global 7: Lucky Ice Pop, Squirtle, Shore, Cyrus; draw Mega Blastoise ex 235-236s -> 5. "
        "Opponent global 8 (210-232s): draw 6, Darkness to benched Mega Kangaskhan ex, Sludge Bomb knocks out Oricorio 70 (no Energy; "
        "opponent 2 points); he promotes Wartortle 90/2 W; Bench Eiscue 80. His move: evolve Active Wartortle -> Mega Blastoise ex "
        "238-241s, 3rd Water 243-244s, Triple Bombardment 246-249s (130 knocks out the Active Muk; no Bench damage with 3 Water). "
        "Verifier v7: opponent hand set to 2 (was 6 from the visible plays): global 11's Copycat drew 3 = the opponent's hand, global 10 "
        "(265-279s) was a draw with 'No Trainer or board change observed', so the hand at the end of global 8 was 2."),
P(G, 11, 6, [1, 2],
  dict(hand=[LIP, SQ, SS, CY, CC], disc=[PB, PR, EI, PB, OR], dene='W', board=[B(MB, 230, 'WWW', behind=[WT, SQ]), B(EI, 80)], ko=2),
  dict(hand_count=3, disc=[OPR, OPR, MUK, AGP], dene='DDD', board=[B(MUK, 110, behind=[AGS]), B(MK, 180, 'DD')], ko=1),
  ['Place:Squirtle@2', 'Attach:1Water@0 zone', 'Play:Copycat', 'Attack:Triple Bombardment'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's hand (3) is the number of cards his Copycat drew this turn (the review: the opponent's "
            "three cards); the visible plays give 7, so 4 cards left the opponent's hand unseen earlier",
  ambiguous=[AMB_AGS, AMB_MUK, AMB_MK, AMB_PR],
  draws={2: ['-' + LIP, '-' + SS, '-' + CY, SS, CY, LL]},
  notes="Global 11 = his 6th turn. Hand after global 9: Lucky Ice Pop, Squirtle, Shore, Cyrus; draw Copycat -> 5. Board: Mega "
        "Blastoise ex 230/3 W; Bench Eiscue 80. Opponent: after the global 9 knockout (Muk, its Grimer and 3 Darkness discarded; he "
        "scores 1) the 2nd Muk 110 (no Energy) was promoted; global 10 (265-279s): 2nd Darkness to benched Mega Kangaskhan ex, no "
        "attack. His move in time order: bench 2nd Squirtle 286-288s (slot 2), 4th Water to Mega Blastoise ex 289-290s, Copycat 291-297s "
        "(shuffles Lucky Ice Pop, Shore, Cyrus; draws three: Shore, Cyrus, Lillie), Triple Bombardment 303-306s (KO Muk; no Bench "
        "damage with 4 Water)."),
]
