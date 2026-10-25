from v2_helpers import P, B
D = 'v2deck_2c68a379f5'; G = '20261024_164318000_SR'
GO = 'Goomy B1 177'; AX = 'Axew B2b 054'; HX = 'Haxorus B2b 056'; HA = 'Happiny B4a 063'; RM = 'Roaring Moon B3a 047'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; IR = 'Iris B2b 067'
CC = 'Copycat B1 225'; SB = 'Small Balloon B3b 064'
PC = 'Pichu A4 066'; MG = 'Magby A4 032'; MK = 'Mega Kangaskhan ex B2 127'
OPR = "Professor's Research A4b 373"
SS = {"card": "Soothing Shore B4 154", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_PC = 'Opponent Pichu printing chosen by HP (30) and attack title (Crackly Toss); A4 066, A4 171 and B2 213 match'
AMB_MG = 'Opponent Magby printing chosen by HP (30) and attack title (Toasty Toss); A4 032, A4 166 and B2 206 match'
AMB_MK = ('Opponent Mega Kangaskhan ex printing chosen by HP (180) and attack title (Double-Punching Family); B2 127, B2 189, B2 202 '
          'and B4 231 match')
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"
POS = [
P(G, 4, 2, [0, 0],
  dict(hand=[SB, IR, RC, RC, CY, RM, IR], disc=[PR], dene='', board=[B(GO, 40, 'M')], ko=0),
  dict(hand_count=4, disc=[OPR], dene='', board=[B(PC, 30, 'W'), B(MG, 30), B(MK, 180, 'L')], ko=0),
  ['Place:Roaring Moon@1', 'Ability@1', 'Attach:1Fighting@1 zone', 'EndTurn'],
  D, None, stadium=SS,
  approx=AP + "; his next Energy (Metal) is read from the Energy he attached on global 6, the review does not show the zone preview",
  ambiguous=[AMB_PC, AMB_MG, AMB_MK, AMB_PR],
  ez_now='F', ez_next='M',
  notes="Global 4 = his 2nd turn (he went second). Setup 24-44 s: opening Goomy, Professor's Research, Small Balloon, Iris, Rare "
        "Candy; Goomy Active, no Bench -> hand Research, Small Balloon, Iris, Rare Candy. Global 2: draw Rare Candy, Research draws "
        "Cyrus and Roaring Moon, Metal to Goomy -> hand Small Balloon, Iris, Rare Candy x2, Cyrus, Roaring Moon. Global 4: 'Draw second "
        "Iris at107-108s' -> 7. Opponent: setup Pichu 30 Active, Magby 30 Bench, hand 5 - 2 = 3; global 1 draw 4, Research 5, Soothing "
        "Shore 4; global 3 draw 5, bench Mega Kangaskhan ex 4, Water to Pichu, Crackly Toss puts Lightning on the benched Kangaskhan "
        "(no damage) -> 4. Bench order Magby (setup), Kangaskhan. His move in the review's order: bench Roaring Moon 109-112 s (slot 1), "
        "Yes to Ancient Roar 113-115 s ('Ability@1'; Ace chooses Magby 146-149 s, not in force), Fighting to Roaring Moon 152-154 s, end "
        "turn 157 s (no Supporter, no attack). check_game stops after 'Ability@1' at the opponent's choice of the new Active (two "
        "options, Magby or Kangaskhan; opponent's frame), so the Attach and EndTurn are not reached there; scratch/b9/t_g4t4.py (Magby "
        "Active, Pichu benched, Roaring Moon placed) applies both."),
P(G, 6, 3, [0, 0],
  dict(hand=[SB, IR, RC, RC, CY, IR, AX], disc=[PR], dene='', board=[B(GO, 40, 'M'), B(RM, 100, 'F')], ko=0),
  dict(hand_count=5, disc=[OPR], dene='', board=[B(PC, 30, 'W'), B(MG, 30), B(MK, 180, 'WLL')], ko=0),
  ['Place:Axew@2', 'Attach:1Metal@2 zone', 'Play:Small Balloon', 'Tool:Small Balloon@2', 'EndTurn'],
  D, None, stadium=SS,
  approx=AP + "; his next Energy (Fighting) is read from the Energy he attached on global 8, the review does not show the zone "
              "preview",
  ambiguous=[AMB_PC, AMB_MG, AMB_MK, AMB_PR],
  ez_now='M', ez_next='F',
  notes="Global 6 = his 3rd turn. Hand after global 4: Small Balloon, Iris x2, Rare Candy x2, Cyrus; 'Draw Axew at182-183s' -> 7. "
        "Board: Goomy 40 (Metal) Active, Roaring Moon 100 (Fighting) Bench. Opponent global 5 (158-180 s): hand 4, draw 5, Water to the "
        "first Kangaskhan, Magby retreats for zero, Pichu Active again (Magby back to the slot Pichu took after Ancient Roar), Crackly "
        "Toss adds a second Lightning to that Kangaskhan (Water + two Lightning), no damage. His move in the review's order: bench Axew "
        "184-185 s (slot 2), Metal to Axew 186-187 s, Small Balloon to Axew 192-196 s, end turn 198 s, no attack."),
P(G, 8, 4, [0, 1],
  dict(hand=[IR, RC, RC, CY, IR, PR], disc=[PR, GO], dene='M', board=[B(RM, 60, 'F'), B(AX, 70, 'M', tool=SB)], ko=1),
  dict(hand_count=6, disc=[OPR], dene='', board=[B(MK, 180, 'WLLL'), B(MG, 30), B(PC, 30, 'W')], ko=0),
  ["Play:Professor's Research", 'Place:Goomy@2', 'Attach:1Fighting@1 zone', 'EndTurn'],
  D, None, stadium=SS,
  approx=AP + "; his next Energy (Metal) is read from the Energy he attached on global 10, the review does not show the zone preview",
  ambiguous=[AMB_MK, AMB_MG, AMB_PC, AMB_PR],
  draws={0: [GO, CC]},
  ez_now='F', ez_next='M',
  notes="Global 8 = his 4th turn. Hand after global 6: Iris x2, Rare Candy x2, Cyrus; 'Draw Professor's Research at240s' -> 6. "
        "Discard: Research, Goomy (KO global 7) and its Metal. Board: Roaring Moon 100-40 = 60 (Fighting) promoted Active 230-234 s; "
        "Bench Axew 70 (Metal, Small Balloon). Opponent global 7 (199-238 s): hand 5, draw 6, third Lightning to the first Kangaskhan "
        "(Water + three Lightning), Pichu retreats for zero, Kangaskhan Active (Pichu to its slot), Double-Punching Family 80 KOs Goomy "
        "(+1), second hit 40 to Roaring Moon. His move in the review's order: Research 242-244 s draws Goomy and Copycat, bench Goomy "
        "249-251 s (slot 2), Fighting to Axew 252-253 s (Fighting + Metal), end turn, no attack."),
P(G, 10, 5, [0, 2],
  dict(hand=[IR, RC, RC, CY, IR, CC, HX], disc=[PR, GO, PR, RM], dene='MF', board=[B(AX, 30, 'FM', tool=SB), B(GO, 40)], ko=2),
  dict(hand_count=6, disc=[OPR], dene='', board=[B(MK, 180, 'WLLL'), B(MG, 30), B(PC, 30, 'W'), B(MK, 180, 'W')], ko=0),
  ['Play:Rare Candy', 'Evolve:Haxorus@0', 'Attach:1Metal@0 zone', 'Play:Copycat', 'Place:Axew@2', 'Attack:Frenzied Blade'],
  D, None, stadium=SS,
  approx=AP + "; his next Energy is not shown (the game ended on the opponent's next turn), Fighting is assumed",
  ambiguous=[AMB_MK, AMB_MG, AMB_PC, AMB_PR],
  draws={3: ['-' + IR, '-' + RC, '-' + CY, '-' + IR, CY, HA, HX, IR, AX, RC]},
  ez_now='M', ez_next='F',
  notes="Global 10 = his 5th turn. Hand after global 8: Iris x2, Rare Candy x2, Cyrus, Copycat; 'Draw Haxorus at293-294s' -> 7. "
        "Discard adds Research, Roaring Moon (KO global 9) and its Fighting. Board: Axew 70-40 = 30 (Fighting, Metal, Small Balloon) "
        "promoted Active 285-287 s; Bench Goomy 40. Opponent global 9 (256-291 s): hand 6, draw 7, bench second Mega Kangaskhan ex 6, "
        "Water to it, first Kangaskhan's Double-Punching Family KOs Roaring Moon (+1, total 2), second hit 40 to Axew. 6 matches the "
        "review's 'six-card hand' at Copycat. His move in the review's order: Rare Candy 295-303 s Active Axew -> Haxorus (110 HP), Metal "
        "304-307 s, Copycat 320-324 s (hand Iris, Rare Candy, Cyrus, Iris shuffled; draws Cyrus, Happiny, Haxorus, Iris, Axew, Rare "
        "Candy), bench Axew 332-334 s (slot 2), Frenzied Blade 339-342 s for 150 (Kangaskhan 180 -> 30)."),
]
