from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_010556000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'
LIP = 'Lucky Ice Pop B2 145'; PL = 'Parasol Lady B3 152'; SS = 'Soothing Shore B4 154'
HL = 'Hitmonlee A1 154'
OPR = "Professor's Research A4b 373"; OSA = 'Sabrina A1 225'; ORC = 'Red Card P-A 006'   # the opponent's, by convention 3
AP = "opponent's list unknown; opponent's hand size from the visible plays"
APT = "the opponent's Trainer printings are not shown, the first printing cards.py lists is used"
AMB_HL = 'Opponent Hitmonlee printing chosen by HP (80) and attack title (Stretch Kick); A1 154 and B2 218 match'
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CC, CY, LI, PR], disc=[], dene='', board=[B(EI, 80), B(EI, 80)], ko=0),
  dict(hand_count=6, disc=[OPR], dene='', board=[B(HL, 80)], ko=0),
  ['Play:Copycat', 'Play:Poké Ball', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + APT + "; Copycat drew 6 (the opponent's 6 cards) and the review names 5 of them (Poke Ball, Soothing Shore, "
              "Parasol Lady, Wartortle, Professor's Research): the 6th is a stand-in (Lillie) in the verification variant only",
  ambiguous=[AMB_HL],
  draws={0: ['-' + CY, '-' + LI, '-' + PR, PB, SS, PL, WT, PR, LI], 1: [SQ]},
  notes="Global 2 = his 1st turn (he went second). REVIEW 'Opening deck and setup' 26-34s: opening five Copycat, Cyrus, Lillie, two "
        "Eiscue; full-art Eiscue Active, regular-art Eiscue benched -> 3. Global 2 (59-96s): draw Professor's Research -> 4. Opponent: "
        "Hitmonlee 80 only (5-1 = 4); global 1 draw (5), Professor's Research (+2 -> 6); no Energy, no attack. His move 59-96s: Copycat "
        "(shuffles Cyrus, Lillie, Research; draws 6 = the opponent's 6; named: Poke Ball, Soothing Shore, Parasol Lady, Wartortle, "
        "Research; the 6th card is not named, stand-in Lillie in the variant) -> Poke Ball (Squirtle, kept in hand) -> Water to Active "
        "full-art Eiscue -> end turn, no attack. Inspections of cards in hand are not actions."),
P(G, 4, 2, [0, 0],
  dict(hand=[SQ, SS, WT, OR], disc=[CC, PB], dene='', board=[B(EI, 80), B(EI, 80, 'W')], ko=0),
  dict(hand_count=5, disc=[OPR, OSA, ORC], dene='', board=[B(HL, 80, 'F')], ko=0),
  ['Place:Oricorio@2', 'Place:Squirtle@3', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + APT,
  ambiguous=[AMB_HL],
  notes="Global 4 = his 2nd turn. Global 3 (96-129s): opponent draw (7), Fighting to Hitmonlee, Sabrina (6; his regular-art Eiscue "
        "forced Active, the Water full-art Eiscue to the Bench @1), Red Card (5; his 6-card hand shuffled, he draws Squirtle, Soothing "
        "Shore, Wartortle), Stretch Kick on the benched full-art Eiscue for 0 (Ice Face). 129-148s: draw Oricorio -> 4. Discard: Copycat, "
        "Poke Ball. His move 129-148s: Oricorio benched ~136s (@2) -> Squirtle benched ~140s (@3) -> Water to Active regular-art Eiscue "
        "~144s -> end turn, no attack."),
P(G, 6, 3, [0, 0],
  dict(hand=[SS, WT, PR], disc=[CC, PB], dene='', board=[B(EI, 80, 'W'), B(EI, 80, 'W'), B(OR, 70), B(SQ, 30)], ko=0),
  dict(hand_count=6, disc=[OPR, OSA, ORC], dene='', board=[B(HL, 80, 'FF')], ko=0),
  ['Evolve:Wartortle@3', "Play:Professor's Research", 'Play:Poké Ball', 'Attach:1Water@0 zone', 'Attack:Ram'],
  D, None,
  approx=AP + "; " + APT,
  ambiguous=[AMB_HL],
  draws={1: [PB, LIP], 2: [SQ]},
  notes="Global 6 = his 3rd turn. After global 4 his hand is Soothing Shore, Wartortle; 169-202s draw Professor's Research -> 3. "
        "Global 5 (148-169s): opponent draw (6), 2nd Fighting to Hitmonlee, Stretch Kick 30 on the benched Squirtle (60 -> 30). His move "
        "169-202s: evolve the damaged Squirtle -> Wartortle (@3) ~175s -> Professor's Research (Poke Ball, Lucky Ice Pop) -> Poke Ball "
        "(2nd Squirtle, kept: Bench full) -> 2nd Water to Active Eiscue -> Ram 50 on Hitmonlee."),
P(G, 8, 4, [0, 0],
  dict(hand=[SS, LIP, SQ, CY], disc=[CC, PB, PR, PB], dene='',
       board=[B(EI, 80, 'WW'), B(EI, 80, 'W'), B(OR, 40), B(WT, 60, behind=[SQ])], ko=0),
  dict(hand_count=7, disc=[OPR, OSA, ORC], dene='', board=[B(HL, 70, 'FFF')], ko=0),
  ['Attach:1Water@2 zone', 'Play:Soothing Shore', 'Attack:Ram'],
  D, None,
  approx=AP + "; " + APT + "; the opponent's two Lucky Ice Pop plays on global 7 are counted as returned to the hand (heads both "
              "times, shown)",
  ambiguous=[AMB_HL],
  notes="Global 8 = his 4th turn. After global 6 his hand is Soothing Shore, Lucky Ice Pop, Squirtle; 246-267s draw Cyrus -> 4. Global 7 "
        "(202-246s): opponent draw (7), 3rd Fighting, Lucky Ice Pop 30 -> 50 heads (back, 7), again 50 -> 70 heads (back, 7), Stretch "
        "Kick 30 on the benched Oricorio (70 -> 40). His move 246-267s: Water to the benched Oricorio (@2) ~253s -> Soothing Shore "
        "~254-256s -> Ram 50 on Hitmonlee."),
]
