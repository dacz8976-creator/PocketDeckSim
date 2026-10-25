from v2_helpers import P, B
D = 'v2deck_2c68a379f5'; G = '20261024_143157000_SR'
GO = 'Goomy B1 177'; AX = 'Axew B2b 054'; HX = 'Haxorus B2b 056'; HA = 'Happiny B4a 063'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; IR = 'Iris B2b 067'
HO = 'Hoopa ex B4 103'; DN = 'Deceptive Needle B4 148'
OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'; OPR = "Professor's Research A4b 373"; ORE = 'Repel A3a 064'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_HO = 'Opponent Hoopa ex printing chosen by name, HP (150) and attack title (Shadow Bullet); B4 103, B4 186 and B4 199 match'
AMB_T = "Opponent Trainer printings in the discard are not shown; the first listed printing is used (Poké Ball A2b 111 of A2b 111 / P-A 005; Copycat B1 225 of B1 225 / B1 270)"
AMB_T2 = AMB_T[:-1] + "; Professor's Research A4b 373 of A4b 373 / P-A 007)"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[RC, IR, PR, CY, PB], disc=[], dene='', board=[B(GO, 40)], ko=0),
  dict(hand_count=4, disc=[OPB, OCC], dene='', board=[B(HO, 150)], ko=0),
  ['Play:Poké Ball', 'Place:Axew@1', "Play:Professor's Research", 'Attach:1Fighting@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) follows Copycat drawing 4 (his hand count at that time); the opponent's Trainer "
              "printings are not shown, the first listed printings are used; his next Energy (Fighting) is read from the Energy he "
              "attached on his next turn (global 4), the review does not show the zone preview",
  ambiguous=[AMB_HO, AMB_T],
  draws={0: [AX], 2: [IR, RC]},
  ez_now='F', ez_next='F',
  notes="Global 2 = his 1st turn (he went second, 'Going second21s'). Setup: opening five Goomy, Rare Candy, Iris, Professor's "
        "Research, Cyrus; Goomy Active, no Bench -> hand Rare Candy, Iris, Professor's Research, Cyrus. Global turn2: 'Draw Poke Ball64s' "
        "-> 5 cards. Opponent: Hoopa ex 150 Active, no Bench, no Energy (global 1: no bench, Energy or attack). Opponent hand: 5 - Active "
        "= 4; draw 5; Poke Ball (-1 +1 hidden) = 5; Copycat (-1, shuffle, draw to his hand count 4) = 4. His move in the review's order: "
        "Poke Ball 67s reveals Axew, bench Axew 72s (slot 1), Professor's Research 74-76s draws Iris and Rare Candy, Fighting to benched "
        "Axew 79-80s, no attack. Zone: Fighting now; next is Fighting (global 4 attaches 'current Fighting')."),
P(G, 4, 2, [0, 0],
  dict(hand=[RC, RC, IR, IR, CY, HX], disc=[PB, PR], dene='', board=[B(AX, 30, 'F'), B(GO, 20)], ko=0),
  dict(hand_count=4, disc=[OPB, OCC, OPR, ORE], dene='', board=[B(HO, 150, 'D', tool=DN)], ko=0),
  ['Retreat:1', 'Attach:1Fighting@1 zone', 'Play:Rare Candy', 'Evolve:Haxorus@1', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Trainer printings are not shown, the first listed printings are used; his next Energy (Metal) is "
              "read from the Energy he attached on his next turn (global 6), the review does not show the zone preview",
  ambiguous=[AMB_HO, AMB_T2],
  ez_now='F', ez_next='M',
  notes="Global 4 = his 2nd turn. Hand after global 2: Rare Candy, Iris, Cyrus + Iris, Rare Candy (Research) = 5; 'Draw Haxorus127s' "
        "-> 6. Discard: Poke Ball, Professor's Research. Board after global 3: Repel forced Goomy to the Bench, Axew Active; Shadow Bullet "
        "30 to Axew 70->40 and 20 to Goomy 40->20; Needle 10 more, Axew 40->30. Axew holds 1 Fighting. Opponent global 3: hand 4, draw 5, "
        "Research (-1 +2) 6, Needle (-1) 5, Repel (-1) 4; Darkness attached to Hoopa ex, Needle on it. His move in the review's order: "
        "retreat Axew to Goomy 135-138s (Retreat:1, the Fighting paid; Axew now slot 1), current Fighting to benched Axew 140-141s, Rare "
        "Candy 143-147s Axew -> Haxorus (110 HP), end turn with Goomy Active, no Supporter or attack. Zone next: Metal (global 6)."),
]
