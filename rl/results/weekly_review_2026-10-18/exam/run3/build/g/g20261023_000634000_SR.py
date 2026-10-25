from v2_helpers import P, B
D = 'v2deck_ba2eca5816'; G = '20261023_000634000_SR'
GO = 'Goomy B1 177'; TR = 'Trapinch B3 076'; DA = 'Dragonair B4 117'
XS = 'X Speed P-A 002'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'
SU = 'Suicune ex A4a 020'; FB = 'Frigibax B2a 034'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CY, PB, RC, PR, XS], disc=[], dene='', board=[B(TR, 60)], ko=0),
  dict(hand_count=5, disc=['Poké Ball A2b 111'], dene='', board=[B(SU, 140), B(FB, 60)], ko=0),
  ['Play:Poké Ball', "Play:Professor's Research", 'Place:Goomy@1', 'Place:Trapinch@2', 'Attach:1Fighting@0 zone', 'Attack:Mud-Slap'],
  D, None,
  approx=AP + "; the opponent's global-1 Poke Ball is counted as +1 (Frigibax, benched) and Legendary Pulse's end-of-turn draw as +1; "
              "the opponent's Poke Ball printing is not shown, the first printing listed is used; Suicune ex and Frigibax printings chosen by "
              "the shown facts only; ez_next is the Fighting his zone generated on global 4 (the review does not name the preview on "
              "global 2)",
  ambiguous=['Opponent Suicune ex printing: A4a 020, A4a 080, A4a 090 and B2a 127 match (HP 140, Legendary Pulse)',
             'Opponent Frigibax printing chosen by HP (60) only (its attack was not shown); B2a 034 and P-B 037 match'],
  draws={0: [TR], 1: [GO, DA]},
  ez_now='F', ez_next='F',
  notes="Global 2 = his 1st turn (he went second). REVIEW 0-35s: opening five Cyrus, Poke Ball, Rare Candy, Professor's Research, "
        "Trapinch; Trapinch 60 Active, empty Bench -> 4 in hand. 46-78s: draw X Speed (inspected, not played) -> 5. Opponent 0-46s: "
        "Suicune ex 140 Active, no Bench at setup (5-1 = 4); global 1 draw (5), Poke Ball (hidden result, +1, 5), Frigibax 60 benched (4), "
        "Legendary Pulse draw at end of turn (5); no Energy, no attack. Cross-check: the opponent's global-3 Copycat drew to his 4-card "
        "hand. His move 46-78s in order: Poke Ball (2nd Trapinch) -> Professor's Research (Goomy, Dragonair) -> Goomy benched 63-65s "
        "(@1) -> 2nd Trapinch benched 67s (@2) -> Fighting to Active Trapinch 69-70s -> Mud-Slap 10 on Suicune 75s."),
]
