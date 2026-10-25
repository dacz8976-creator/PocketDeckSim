from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_120935000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; EI = 'Eiscue B1 080'; PB = 'Poké Ball P-A 005'
PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; CY = 'Cyrus A2 150'; LL = 'Lillie A3 155'; LIP = 'Lucky Ice Pop B2 145'
TR = 'Trapinch B3 076'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[LIP, CC, PB, CY], disc=[], dene='', board=[B(SQ, 60), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(TR, 60)], ko=0),
  ['Play:Poké Ball', 'Place:Eiscue@2', 'Play:Copycat', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active Trapinch (no Bench shown, no draw yet: he went first)",
  draws={0: [EI], 2: ['-' + LIP, '-' + CY, WT, PR, LL, CC]},
  notes="Global 1 = his 1st turn (he went first). Opening (0-38s): opening five Lucky Ice Pop, two Squirtle, Copycat, Poke Ball; "
        "Squirtle 60 Active, 2nd Squirtle 60 Benched -> hand Lucky Ice Pop, Copycat, Poke Ball; opponent Trapinch 60 Active (35s), no "
        "Bench named. Global 1 (38-64s): draw Cyrus -> 4. His move in time order: Poke Ball 42s reveals Eiscue 45s, bench it 48s "
        "(slot 2, next to the setup Squirtle), Copycat 53s (shuffles Lucky Ice Pop and Cyrus; draws to the opponent's 4: Wartortle, "
        "Research, Lillie, Copycat seen in the post-draw inspections), no Energy (first player's first turn), no attack."),
]
