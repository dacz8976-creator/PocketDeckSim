from v2_helpers import P, B
D = 'v2deck_a75894a903'; G = '20261024_165913000_SR'
OR = 'Oricorio A3 066'; IE = 'Indeedee ex B1 121'; DE = 'Dedenne ex B3b 024'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; GC = 'Giant Cape A2 147'; CY = 'Cyrus A2 150'; CC = 'Copycat B1 225'
SP = 'Starting Plains B2 154'; SB = 'Small Balloon B3b 064'; CV = 'Clear Veil B4 149'
DD = 'Druddigon B2b 057'; DR = 'Dratini A3b 051'; OGC = 'Giant Cape A2 147'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CC, GC, CV, CV, CY], disc=[], dene='', board=[B(IE, 130)], ko=0),
  dict(hand_count=3, disc=[OPR], dene='', board=[B(DD, 120, tool=OGC), B(DR, 60), B(DR, 60)], ko=0),
  ['Play:Clear Veil', 'Tool:Clear Veil@0', 'Play:Copycat', 'Attach:1Lightning@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the Dratini printing is chosen by HP (60) only (its attack was not shown); the opponent's Trainer printings are "
              "not shown, the first listed printings are used",
  ambiguous=['Opponent Druddigon printing chosen by HP (100 before Giant Cape) and attack title (Clutch); only B2b 057 matches',
             'Opponent Dratini printing chosen by HP (60) only; A3b 051, A4b 267, A4b 268, B2b 051, B2b 105 and B4 116 match',
             'Opponent Giant Cape printing not shown; A2 147 used (A2 147, A4b 320 and A4b 321 match)',
             "Opponent Professor's Research printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"],
  draws={2: ['-' + GC, '-' + CV, '-' + CY, CV, SP, CY]},
  notes="Global 2 = his 1st turn (he went second, 33-38 s). Setup 38-65 s: Indeedee ex 130 Active, no Bench; hand Copycat, Giant "
        "Cape, two Clear Veil. 'Draw Cyrus' -> 5. Opponent: Druddigon 100 Active, two Dratini 60 Bench, hand 5 - 3 = 2; global 1 "
        "(66-87 s): draw 3, Professor's Research (-1 +2) 4, Giant Cape on Druddigon (100 -> 120) 3, no Energy, no attack -> 3. His move "
        "in the review's order: Clear Veil to Indeedee ex 91-97 s, Copycat 98-101 s (hand Giant Cape, Clear Veil, Cyrus shuffled; draws "
        "3 = the opponent's hand; the review shows Clear Veil, Starting Plains, Cyrus, and 'Starting Plains remains in hand'), Lightning "
        "to Indeedee ex 107 s, end turn, no attack. Druddigon's printing: its attack Clutch is shown from global 5 on; the card is "
        "face up on the board from the start."),
]
