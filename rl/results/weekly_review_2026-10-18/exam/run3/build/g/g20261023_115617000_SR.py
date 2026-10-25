from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_115617000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'; EI = 'Eiscue B1 080'; OR = 'Oricorio A3 066'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; CY = 'Cyrus A2 150'; LL = 'Lillie A3 155'
PL = 'Parasol Lady B3 152'; LIP = 'Lucky Ice Pop B2 145'; SS = 'Soothing Shore B4 154'
# opponent
RI = 'Riolu A2 091'; ML = 'Mega Lucario ex B3 081'; HM = 'Hitmonchan ex B1 124'; BO = 'Bonsly B3 078'; RH = 'Rocky Helmet A2 148'
AR = 'Arena of Antiquity B3 154'
OPR = "Professor's Research A4b 373"; OPB = 'Poké Ball A2b 111'; OXS = 'X Speed P-A 002'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
SHORE = {"card": "Soothing Shore B4 154", "owner": 0}
TA = [{"effect": {"ReducedAttackDamage": {"amount": 30}}, "turns": 1}]
AMB_HM = 'Opponent Hitmonchan ex printing chosen by HP (130) only; B1 124, B1 261, B1 279 and B3 229 match'
AMB_ML = 'Opponent Mega Lucario ex printing chosen by HP (190) and attack title (Fighting Pulse); B3 081, B3 184 and B3 204 match'
AMB_RH = 'Opponent Rocky Helmet printing not shown; A2 148, A4b 322 and A4b 323 match'
AMB_BO = 'Opponent Bonsly printing chosen by HP (30) and attack title (Teary Attack); B3 078 and B3 168 match'
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 and P-A 007 match"
AMB_PB = 'Opponent Poké Ball printing not shown; A2b 111 and P-A 005 match'
AMB_BO0 = 'Opponent Bonsly printing chosen by HP (30) only; B3 078 and B3 168 match'
TRAINERS = "; the opponent's Trainer printings are not shown (the first listed printings are used)"


def heads_back(hp):
    def f(v):
        v['me']['board'][0]['hp'] = hp
        v['me']['hand'].append(LIP)
    return f


def tails_disc(hp):
    def f(v):
        v['me']['board'][0]['hp'] = hp
        v['me']['discard'].append(LIP)
    return f


POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[PR, CC, LIP, PL, SS, OR], disc=[PR], dene='', board=[B(EI, 80), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[OPR], dene='', board=[B(RI, 60, 'F', tool=RH), B(HM, 130)], ko=0),
  ['Place:Oricorio@2', 'Play:Soothing Shore', 'Play:Copycat', 'Play:Poké Ball', 'Evolve:Wartortle@1', 'Attach:1Water@1 zone',
   'EndTurn'],
  D, None,
  approx=AP + TRAINERS,
  ambiguous=[AMB_HM, AMB_RH, AMB_PR],
  draws={2: ['-' + PR, '-' + LIP, '-' + PL, SS, WT, CY, PB], 3: [EI]},
  notes="Global 3 = his 2nd turn (he went first). Setup (0-37s): opening five Eiscue, Squirtle, Research, Copycat, Lucky Ice Pop; "
        "Eiscue 80 Active, Squirtle 60 Benched -> hand Research, Copycat, Lucky Ice Pop. Global 1: draw Research, play Research (draws "
        "Parasol Lady, Soothing Shore) -> Research, Copycat, Lucky Ice Pop, Parasol Lady, Soothing Shore. Global 3 draw Oricorio -> 6. "
        "Opponent: setup Riolu 60 Active (Jab 20 shown on global 2 -> A2 091); global 2 (49-73s): 4 + draw 5, Research -1 +2 = 6, Rocky "
        "Helmet on Riolu 5, Fighting to Riolu, bench Hitmonchan ex 130 = 4; Jab 20 reduced to 0 by Ice Face. His move in the review's "
        "order: bench Oricorio (slot 2), Soothing Shore, Copycat (shuffles Research, Lucky Ice Pop, Parasol Lady; draws four = the "
        "opponent's 4: Shore, Wartortle, Cyrus, Poke Ball), Poke Ball finds Eiscue (kept in hand), evolve benched Squirtle -> "
        "Wartortle, first Water to it, end without attacking."),
P(G, 5, 3, [0, 0],
  dict(hand=[SS, CY, EI, LIP], disc=[PR, CC, PB, SS], dene='', board=[B(EI, 30), B(WT, 90, 'W', behind=[SQ]), B(OR, 70)], ko=0),
  dict(hand_count=2, disc=[OPR, OPB], dene='', board=[B(ML, 190, 'FF', tool=RH, behind=[RI]), B(HM, 130), B(BO, 30)], ko=0),
  ['Play:Soothing Shore', 'Attach:1Water@1 zone', 'Play:Lucky Ice Pop', 'EndTurn'],
  D, None, stadium={"card": "Arena of Antiquity B3 154", "owner": 1},
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO0, AMB_PR, AMB_PB],
  draws={2: []}, vpatch=heads_back(50),
  notes="Global 5 = his 3rd turn. Hand after global 3: Soothing Shore (from Copycat), Cyrus, Eiscue; draw Lucky Ice Pop -> 4. Discard: "
        "Research (global 1), Copycat, Poke Ball, and his first Soothing Shore (replaced by Arena of Antiquity on global 4). Board: "
        "Eiscue 30 (Fighting Pulse 90 - 40 Ice Face on global 4), Wartortle 90/1 W, Oricorio 70 (Bench in order benched). Opponent "
        "global 4 (112-144s): 4 + draw 5, Poke Ball 5, bench Bonsly 30 4, Arena of Antiquity 3, evolve Active Riolu -> Mega Lucario ex "
        "190 (Rocky Helmet stays) 2, 2nd Fighting. His move in order: 2nd Shore replacing Arena, Water to Wartortle (2), Lucky Ice Pop "
        "heals Eiscue 30 -> 50 with Heads (Pop back to hand; variant patch), pass."),
P(G, 7, 4, [0, 1],
  dict(hand=[CY, EI, LIP, PR], disc=[PR, CC, PB, SS, EI], dene='', board=[B(OR, 70), B(WT, 90, 'WW', behind=[SQ])], ko=1),
  dict(hand_count=3, disc=[OPR, OPB, AR], dene='', board=[B(ML, 190, 'FFF', tool=RH, behind=[RI]), B(HM, 130), B(BO, 30)], ko=0),
  ["Play:Professor's Research", 'Evolve:Mega Blastoise ex@1', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO0, AMB_PR, AMB_PB],
  draws={0: [WT, MB]},
  notes="Global 7 = his 4th turn. Hand after global 5: Cyrus, Eiscue, Lucky Ice Pop (returned on Heads); draw Research -> 4. Opponent "
        "global 6 (169-189s): draw (2 -> 3), 3rd Fighting to Mega Lucario ex, Fighting Pulse 140 knocks out Eiscue 50 (opponent 1 "
        "point); he promotes Oricorio, Bench Wartortle 90/2 W. Discard adds Eiscue; Arena of Antiquity is in the opponent's discard; his "
        "2nd Shore is the Stadium. His move: Research draws Wartortle and Mega Blastoise ex, evolve benched Wartortle -> Mega Blastoise "
        "ex 230, 3rd Water to it, no attack."),
P(G, 9, 5, [0, 1],
  dict(hand=[CY, EI, LIP, WT, PB], disc=[PR, CC, PB, SS, EI, PR], dene='',
       board=[B(OR, 40, effects=TA), B(MB, 230, 'WWW', behind=[WT, SQ])], ko=1),
  dict(hand_count=4, disc=[OPR, OPB, AR, OPR, OXS], dene='F', board=[B(BO, 30), B(HM, 130), B(ML, 190, 'FFF', tool=RH, behind=[RI])],
       ko=0),
  ['Play:Lucky Ice Pop', 'Attach:1Water@1 zone', 'Play:Poké Ball', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it; the "
            "opponent's Bench order after the retreat follows the swap (Mega Lucario ex where Bonsly was)",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO, AMB_PR, AMB_PB],
  draws={0: [], 2: [SQ]}, vpatch=heads_back(60),
  notes="Global 9 = his 5th turn. Hand after global 7: Cyrus, Eiscue, Lucky Ice Pop, the 2nd Wartortle; draw Poke Ball -> 5. Opponent "
        "global 8 (210-238s): 3 + draw 4, Research -1 +2 = 5, 4th Fighting to Mega Lucario, X Speed 4, Mega Lucario retreats discarding "
        "one Fighting (3 left), Bonsly Active; Teary Attack 10 + 20 Weakness: Oricorio 70 -> 40, and Oricorio's attacks do -30 during "
        "this turn (effect set). His move in order: Lucky Ice Pop heals Oricorio 40 -> 60, Heads (back to hand; variant patch), 4th Water "
        "to benched Mega Blastoise ex, Poke Ball finds Squirtle (kept), pass."),
P(G, 11, 6, [0, 1],
  dict(hand=[CY, EI, LIP, WT, SQ, PL], disc=[PR, CC, PB, SS, EI, PR, PB], dene='',
       board=[B(OR, 30, effects=TA), B(MB, 230, 'WWWW', behind=[WT, SQ])], ko=1),
  dict(hand_count=5, disc=[OPR, OPB, AR, OPR, OXS], dene='F', board=[B(BO, 30), B(HM, 130), B(ML, 190, 'FFFF', tool=RH, behind=[RI])],
       ko=0),
  ['Play:Lucky Ice Pop', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it; the "
            "opponent's Bench order after the retreat follows the swap (Mega Lucario ex where Bonsly was)",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO, AMB_PR, AMB_PB],
  draws={0: []}, vpatch=tails_disc(50),
  notes="Global 11 = his 6th turn. Hand after global 9: Cyrus, Eiscue, Lucky Ice Pop, Wartortle, Squirtle; draw Parasol Lady -> 6. "
        "Opponent global 10 (265-283s): draw (4 -> 5), Fighting to benched Mega Lucario (4), Teary Attack 30: Oricorio 60 -> 30, -30 "
        "again. His move in order: Lucky Ice Pop heals Oricorio 30 -> 50, Tails (discarded; variant patch), Water to Oricorio, pass "
        "(Shore heals 20 at the end)."),
P(G, 13, 7, [0, 1],
  dict(hand=[CY, EI, WT, SQ, PL, CC], disc=[PR, CC, PB, SS, EI, PR, PB, LIP], dene='',
       board=[B(OR, 40, 'W', effects=TA), B(MB, 230, 'WWWW', behind=[WT, SQ])], ko=1),
  dict(hand_count=5, disc=[OPR, OPB, AR, OPR, OXS, OPB], dene='F',
       board=[B(BO, 30), B(HM, 130), B(ML, 190, 'FFFFF', tool=RH, behind=[RI])], ko=0),
  ['Play:Copycat', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it; the "
            "opponent's Poké Ball on global 12 found nothing (no-target warning) and is counted as played (his Copycat then drew 5 = "
            "the opponent's hand); the opponent's Bench order after the retreat follows the swap",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO, AMB_PR, AMB_PB],
  draws={0: ['-' + CY, '-' + EI, '-' + WT, '-' + SQ, '-' + PL, WT, PL, CY, LL, EI]},
  notes="Global 13 = his 7th turn. Hand after global 11: Cyrus, Eiscue, Wartortle, Squirtle, Parasol Lady; draw Copycat -> 6. Oricorio "
        "50 + Shore 20 = 70 at the end of global 11, 1 W. Opponent global 12 (303-323s): draw (5 -> 6), Fighting to benched Mega Lucario "
        "(5), Poke Ball with the no-target warning (5; Copycat's five draws confirm 5), Teary Attack 30: Oricorio 70 -> 40, -30 again. "
        "His move: Copycat (shuffles his five, draws Wartortle, Parasol Lady, Cyrus, Lillie, Eiscue), 5th Water to Mega Blastoise ex, "
        "end turn (Shore heals Oricorio to 60)."),
P(G, 15, 8, [0, 1],
  dict(hand=[WT, PL, CY, LL, EI, SQ], disc=[PR, CC, PB, SS, EI, PR, PB, LIP, CC], dene='',
       board=[B(OR, 30, 'W', effects=TA), B(MB, 230, 'WWWWW', behind=[WT, SQ])], ko=1),
  dict(hand_count=6, disc=[OPR, OPB, AR, OPR, OXS, OPB], dene='F',
       board=[B(BO, 30), B(HM, 130), B(ML, 190, 'FFFFFF', tool=RH, behind=[RI])], ko=0),
  ['Retreat:1', 'Attach:1Water@0 zone', 'Attack:Triple Bombardment'],
  D, None, stadium=SHORE,
  approx=AP + TRAINERS + "; the opponent's Poké Ball on global 4 is counted as finding the Bonsly benched right after it; the "
            "opponent's Poké Ball on global 12 found nothing (no-target warning) and is counted as played; the opponent's Bench order "
            "after the retreat follows the swap",
  ambiguous=[AMB_HM, AMB_ML, AMB_RH, AMB_BO, AMB_PR, AMB_PB],
  notes="Global 15 = his 8th turn. Hand after global 13: Wartortle, Parasol Lady, Cyrus, Lillie, Eiscue; draw Squirtle (the last card "
        "of his deck) -> 6. Board: Oricorio 30/1 W (global 14 Teary Attack 60 -> 30, -30 effect), Mega Blastoise ex 230/5 W. Opponent "
        "global 14 (349-363s): draw (5 -> 6), 6th Fighting to benched Mega Lucario. His move in order: retreat Oricorio (discards its "
        "Water) to Mega Blastoise ex, 6th Water to it, Triple Bombardment (130 knocks out Bonsly; 50 to Hitmonchan ex and 50 to Mega "
        "Lucario ex, the only two Benched)."),
]
