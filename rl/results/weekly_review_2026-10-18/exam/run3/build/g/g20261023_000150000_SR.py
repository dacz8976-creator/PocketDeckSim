from v2_helpers import P, B
D = 'v2deck_ba2eca5816'; G = '20261023_000150000_SR'
GO = 'Goomy B1 177'; TR = 'Trapinch B3 076'; FX = 'Flygon ex B3 126'; DT = 'Dratini B4 116'; DA = 'Dragonair B4 117'
XS = 'X Speed P-A 002'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'
CC = 'Copycat B1 225'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; CP = 'Chien-Pao ex B2a 037'; MK = 'Magikarp A1 077'; WA = 'Wallace B3b 068'
OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"   # the opponent's, by convention 3 (first printing cards.py lists)
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_CV = 'Opponent Carvanha printing chosen by HP (50) only (its attack was not shown); B4 034 and P-B 081 match'
AMB_MS = 'Opponent Mega Sharpedo ex printing: B4 035, B4 182 and B4 196 match (HP 190, Turbo Shark)'
AMB_CP = 'Opponent Chien-Pao ex printing: B2a 037, B2a 102, B2a 112 and P-B 041 match (HP 130); its attacks were not shown'
AMB_MK = 'Opponent Magikarp printing chosen by HP (30) only (its attack was not shown); several 30-HP Magikarp printings exist'
WALL = ("the opponent's hand count assumes Wallace (played on global 2, the opponent's first turn) put the Mega Sharpedo ex from the deck "
        "onto Carvanha (the review leaves Wallace's mechanism qualified; evolving from the hand is not possible on a player's first turn); "
        "if the Mega came from the hand, the count is 1 lower")
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[XS, PB, FX, CC], disc=[], dene='', board=[B(GO, 40), B(DT, 60)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(CV, 50), B(CP, 130)], ko=0),
  ['Play:Poké Ball', 'Place:Trapinch@2', 'Play:Copycat', 'EndTurn'],
  D, None,
  approx=AP + "; going first, his zone generates no Energy on global 1: ez_now is set to Grass, the Energy the zone generated on "
              "his next turn (global 3), and ez_next Grass likewise; the opponent's Carvanha and Chien-Pao ex printings are chosen by HP only",
  ambiguous=[AMB_CV, AMB_CP],
  draws={0: [TR], 2: ['-' + XS, '-' + FX, DA, RC, DA]},
  ez_now='G', ez_next='G',
  notes="Global 1 = his 1st turn (he went first). REVIEW 'Exact deck and setup': opening five X Speed, Poke Ball, Goomy, Flygon ex, "
        "Dratini; Goomy Active, Dratini right Bench -> 3 in hand. Row 44-48: draw Copycat -> 4 (X Speed, Poke Ball, Flygon ex, Copycat). "
        "Opponent: Carvanha 50 Active, Chien-Pao ex 130 left Bench; 5 - 2 = 3 in hand, no draw yet (going second). His move rows 49-73: "
        "Poke Ball (Trapinch 60) -> Trapinch benched in the LEFT slot (engine: lowest empty slot @2, Dratini compacted to @1) -> Copycat "
        "(X Speed and Flygon ex shuffled back; draws 3 = opponent's 3 cards: Dragonair, Rare Candy, Dragonair) -> end turn, no Energy, no "
        "attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[DA, RC, DA, PR], disc=[PB, CC], dene='', board=[B(GO, 40), B(TR, 60), B(DT, 60)], ko=0),
  dict(hand_count=3, disc=[WA], dene='', board=[B(MS, 190, 'W', behind=[CV]), B(CP, 130)], ko=0),
  ['Evolve:Dragonair@2', "Play:Professor's Research", 'Play:Poké Ball', 'Place:Dratini@3', 'Attach:1Grass@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + WALL + "; the opponent's Trainer printing (Wallace) is not shown, the first printing is used; Carvanha under the "
              "Mega and Chien-Pao ex printings chosen by HP only",
  ambiguous=[AMB_MS, AMB_CV.replace('Opponent Carvanha', 'Opponent Carvanha under Mega Sharpedo ex:'), AMB_CP],
  draws={1: [TR, PB], 2: [DT]},
  ez_now='G', ez_next='F',
  notes="Global 3 = his 2nd turn. After global 1 his hand is Dragonair, Rare Candy, Dragonair (row 64-71); row 94-106 draw Professor's "
        "Research -> 4. Board: Goomy 40 Active; Bench left Trapinch 60, right Dratini 60 (listed left to right, compacted: Trapinch @1, "
        "Dratini @2). Discard Poke Ball, Copycat. Zone: generated Grass, next preview Fighting (row 94-106). Opponent global 2 (rows "
        "74-93): draw (3->4), Wallace (->3) with Carvanha becoming Mega Sharpedo ex 190, one Water attached; no attack. His move rows "
        "107-144: evolve right Bench Dratini -> Dragonair (@2) -> Professor's Research (Trapinch, Poke Ball) -> Poke Ball (Dratini) -> "
        "Dratini benched in the middle slot (engine lowest empty slot @3) -> Grass to left Bench Trapinch (@1) -> end turn, no attack."),
P(G, 5, 3, [0, 1],
  dict(hand=[DA, RC, TR, CY], disc=[PB, CC, PR, PB, GO], dene='', board=[B(TR, 60, 'G'), B(DT, 60), B(DA, 80, behind=[DT])], ko=1),
  dict(hand_count=3, disc=[WA, OPB, OPR], dene='', board=[B(MS, 190, 'WW', behind=[CV]), B(CP, 130, 'W'), B(MK, 30), B(CV, 50)], ko=0),
  ['Place:Trapinch@3', 'Evolve:Dragonair@1', 'Attach:1Fighting@3 zone', 'Attack:Mud-Slap'],
  D, None,
  approx=AP + "; " + WALL + "; global 4's Poke Ball is counted as +1 (Magikarp, benched); the opponent's Trainer printings (Wallace, "
              "Poke Ball, Professor's Research) are not shown, the first printings are used; Carvanha, Chien-Pao ex and Magikarp printings "
              "chosen by HP only; ez_next is the Fighting the zone still held on global 7 (the review does not name the preview on global 5)",
  ambiguous=[AMB_MS, AMB_CV.replace('Opponent Carvanha', 'Opponent Carvanha (under Mega Sharpedo ex and on the Bench):'), AMB_CP, AMB_MK],
  ez_now='F', ez_next='F',
  notes="Global 5 = his 3rd turn. After global 3 his hand is Dragonair, Rare Candy, Trapinch; row 189-198 draw Cyrus -> 4. Global 4 "
        "(rows 145-188): Turbo Shark 70 KOs Goomy (opponent 1 point), Trapinch with 1 Grass promoted from the left Bench; Bench now middle "
        "Dratini 60, right Dragonair 80 (compacted @1, @2). Discard: Poke Ball, Copycat, Professor's Research, Poke Ball, Goomy. Opponent "
        "global 4: draw (3->4), Poke Ball (Magikarp, ->4), Magikarp benched (->3), Water to Mega (2 Water), Professor's Research (->4), "
        "Carvanha benched (->3); Turbo Shark's Water to Chien-Pao ex. Bench left to right Chien-Pao ex 130, Magikarp 30, Carvanha 50. His "
        "move rows 189-215: 2nd Trapinch benched in the LEFT slot (engine lowest empty slot @3) -> evolve middle Dratini -> Dragonair (@1) "
        "-> Fighting to the Benched 2nd Trapinch (@3) -> Mud-Slap 10 on Mega Sharpedo."),
]
