from v2_helpers import P, B
D = 'v2deck_6328cc45fe'; G = '20261023_001330000_SR'
BX = 'Buzzwole ex A3a 006'; PH = 'Pheromosa A3a 007'; CE = 'Celesteela A3a 062'; BZ = 'Buzzwole B2 014'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'; LC = 'Leaf Cape A3 147'
LU = 'Lusamine A3a 069'; CC = 'Copycat B1 225'; SP = 'Starting Plains B2 154'; FB = 'Field Blower B3 147'; FF = 'Fragrant Forest B3 153'
CM = 'Charmander A1 033'; CL = 'Charmeleon B2b 008'; LW = 'Litwick B1 041'; CH = 'Chandelure B1 043'
OPB = 'Poké Ball A2b 111'   # the opponent's, by convention 3 (first printing cards.py lists)
AP = "opponent's list unknown; opponent's hand size from the visible plays"
APT = "the opponent's Trainer printings (Copycat, Poke Ball, Rare Candy) are not shown, the first printings are used"
AMB_CM = 'Opponent Charmander printing chosen by HP (60) only (its attack was not shown); several 60-HP Charmander printings exist'
AMB_CL = 'Opponent Charmeleon printing chosen by HP (80), Ability title (Ignition) and attack title (Slash); B2b 008 and B2b 092 match'
AMB_LW = 'Opponent Litwick printing chosen by HP (50) only (its attack was not shown); B1 041 (Fire) and B2 067 (Psychic) match'
AMB_CH = 'Opponent Chandelure printing chosen by HP (140), Ability title (Slow Sear) and attack title (Heat Blast); B1 043 and B1 231 match'
BIGBEAT = [{"effect": {"CannotUseAttack": "Big Beat"}, "turns": 1}]
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[SA, LC, LU, CY, PB], disc=[], dene='', board=[B(BX, 140)], ko=0),
  dict(hand_count=2, disc=[CC, OPB], dene='', board=[B(CM, 60), B(CM, 60), B(LW, 50)], ko=0),
  ['Play:Poké Ball', 'Place:Celesteela@1', 'Play:Leaf Cape', 'Tool:Leaf Cape@0', 'Play:Sabrina', 'Ability@1', 'Attach:1Grass@1 zone',
   'EndTurn'],
  D, None,
  approx=AP + "; the opponent's global-1 Copycat drew 4 (his 4-card hand) and its Poke Ball is counted as +1 (Litwick, benched); " + APT +
              "; Charmander and Litwick printings chosen by HP only; the opponent's Bench is listed in the order benched (the review does "
              "not give left and right)",
  ambiguous=[AMB_CM, AMB_LW],
  draws={0: [CE]},
  notes="Global 2 = his 1st turn (he went second). REVIEW 'Opening deck identity' 25-32s: opening five Buzzwole ex, Sabrina, Leaf Cape, "
        "Lusamine, Cyrus; Buzzwole ex Active, no Bench -> 4. 93-132s: draw Poke Ball -> 5. Opponent global 1 (61-93s): Charmander 60 "
        "Active (5-1 = 4), draw (5), Copycat (shuffle, draws 4 = his hand), 2nd Charmander benched (3), Poke Ball (+1, 3), Litwick benched "
        "(2). His move 93-132s: Poke Ball (Celesteela) -> Celesteela benched (@1) -> Leaf Cape on Active Buzzwole ex -> Sabrina (the "
        "opponent chose the benched forest-art Charmander; not in force) -> Celesteela's Ultra Thrusters (Ability@1: Buzzwole ex to the "
        "Bench, Celesteela Active) -> Grass to the benched Buzzwole ex (now @1) -> end turn, no attack. The after-chance variant stops "
        "at the opponent's choice after Sabrina (two Benched Pokemon, so the tool does not apply it), so the labels after Sabrina are "
        "not checked there; a scratch copy with one opponent Bench Pokemon (scratch/b6/t_sabrina_test.py) applies all 7 variant labels "
        "(the opponent's 'Activate:1@1' and his single-option 'Activate:0@1' after Ability@1 are applied by the tool)."),
P(G, 4, 2, [0, 0],
  dict(hand=[LU, CY, SP], disc=[PB, SA], dene='', board=[B(CE, 80), B(BX, 170, 'G', tool=LC)], ko=0),
  dict(hand_count=1, disc=[CC, OPB], dene='', board=[B(CL, 80, 'RR', behind=[CM]), B(CL, 80, 'R', behind=[CM]), B(LW, 50)], ko=0),
  ['Play:Starting Plains', 'Attach:1Grass@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + APT + "; Charmander (under both Charmeleon) and Litwick printings chosen by HP only; the opponent's Bench is "
              "listed with the original Charmander's line first (the review does not give left and right)",
  ambiguous=[AMB_CL, AMB_CM.replace('Opponent Charmander', 'Opponent Charmander under each Charmeleon:'), AMB_LW],
  notes="Global 4 = his 2nd turn. After global 2 his hand is Lusamine, Cyrus; 162-183s draw Starting Plains -> 3. Board: Celesteela "
        "120-40 = 80 Active (Slash on global 3), Buzzwole ex 140+30 (Leaf Cape) = 170 on the Bench with 1 Grass. Discard Poke Ball, "
        "Sabrina. Opponent global 3 (132-162s): draw (2->3), Fire to the benched original Charmander, Active Charmander -> Charmeleon "
        "(Ignition: Fire to Active), benched Charmander -> Charmeleon (Ignition: 2nd Fire to Active) -> hand 1; Active Charmeleon 80 2 "
        "Fire, Bench Charmeleon 80 1 Fire, Litwick 50; Slash 40. His move 162-183s: Starting Plains -> 2nd Grass to the benched Buzzwole "
        "ex (@1) -> end turn (inspecting Buzzwole ex is not an action)."),
P(G, 6, 3, [0, 0],
  dict(hand=[LU, CY, FF], disc=[PB, SA], dene='', board=[B(CE, 60), B(BX, 190, 'GG', tool=LC)], ko=0),
  dict(hand_count=1, disc=[CC, OPB], dene='', board=[B(CL, 80, 'RR', behind=[CM]), B(CL, 80, 'RR', behind=[CM]), B(LW, 70), B(LW, 70)], ko=0),
  ['Play:Fragrant Forest', 'UseStadium', 'Place:Pheromosa@2', 'Ability@0', 'Activate:0@1', 'Attach:1Grass@0 zone', 'Attack:Big Beat'],
  D, None,
  stadium={"card": SP, "owner": 0},
  approx=AP + "; " + APT + "; Charmander and Litwick printings chosen by HP only; the opponent's Bench is listed in the order benched",
  ambiguous=[AMB_CL, AMB_CM.replace('Opponent Charmander', 'Opponent Charmander under each Charmeleon:'), AMB_LW],
  draws={1: [PH]},
  notes="Global 6 = his 3rd turn. After global 4 his hand is Lusamine, Cyrus; 199-247s draw Fragrant Forest -> 3. Starting Plains "
        "(his) in play: Celesteela 140 max, 100-40 (Slash, global 5) = 60; Buzzwole ex 190 with 2 Grass and Leaf Cape. Opponent global 5 "
        "(183-199s): draw (1->2), 2nd Litwick benched (70 under Plains, ->1), Fire to the benched Charmeleon (2 Fire), Slash 40. Litwicks "
        "70 each. His move 199-247s: Fragrant Forest (replaces Plains) -> use Forest (Pheromosa) -> Pheromosa benched (@2) -> Ultra "
        "Thrusters (Ability@0, Celesteela Active: Buzzwole ex in, Celesteela to the Bench) -> 3rd Grass to Active Buzzwole ex -> Big Beat "
        "120 KOs the Active Charmeleon."),
P(G, 8, 4, [1, 0],
  dict(hand=[LU, CY, FB], disc=[PB, SA, SP, PR], dene='',
       board=[B(BX, 170, 'GGG', tool=LC, effects=BIGBEAT), B(CE, 40), B(PH, 70)], ko=0),
  dict(hand_count=0, disc=[CC, OPB, 'Rare Candy A3 144', CL, CM], dene='RR',
       board=[B(CH, 140, 'R', behind=[LW]), B(CL, 80, 'RR', behind=[CM]), B(LW, 50)], ko=1),
  ['UseStadium', 'Place:Buzzwole@3', 'Ability@1', 'Activate:0@2', 'Attach:1Grass@0 zone', 'Attack:Jump Blues'],
  D, None,
  stadium={"card": FF, "owner": 0},
  approx=AP + "; " + APT + "; Charmander and Litwick printings chosen by HP only; the opponent's hand count (0) follows from its plays "
              "(draw, Rare Candy, Chandelure); his Bench is listed Celesteela then Pheromosa (the review does not give left and right)",
  ambiguous=[AMB_CH, AMB_CL, AMB_CM.replace('Opponent Charmander', 'Opponent Charmander under Charmeleon and in the discard:'),
             AMB_LW.replace('Opponent Litwick', 'Opponent Litwick (under Chandelure and on the Bench):')],
  draws={0: [BZ]},
  notes="Global 8 = his 4th turn. After global 6 his hand is Lusamine, Cyrus; 272-314s draw Field Blower -> 3. Board after global 6: "
        "Active Buzzwole ex 170 (Plains gone) with 3 Grass, Leaf Cape and Big Beat locked this turn; Bench Celesteela 40, Pheromosa 70. "
        "Discard: Poke Ball, Sabrina, Starting Plains, Professor's Research (Slow Sear, 270s). Opponent: global 6 KO of the 2-Fire Active "
        "Charmeleon (discard Charmeleon, Charmander, RR), Litwick 50 promoted; global 7 (247-272s): draw (1->2), Rare Candy, Litwick -> "
        "Chandelure 140 (->0), Fire attached (1), Slow Sear, no attack. His move 272-314s: use Forest (non-ex Buzzwole) -> Buzzwole "
        "benched (@3) -> Ultra Thrusters (Ability@1, Celesteela on the Bench: Buzzwole ex out, Pheromosa in) -> Grass to Active Pheromosa "
        "-> Jump Blues (20 Chandelure, 20 the selected benched Charmeleon). The engine's bench-target choice after Jump Blues is listed "
        "as two identical 'ApplyQueuedAttackDamage' labels (Charmeleon @1, Litwick @2), which the brief says never to write, so the "
        "target is not in force."),
P(G, 10, 5, [1, 1],
  dict(hand=[LU, CY, FB, PB], disc=[PB, SA, SP, PR, CC, PH], dene='G',
       board=[B(BZ, 110), B(CE, 40), B(BX, 170, 'GGG', tool=LC)], ko=1),
  dict(hand_count=1, disc=[CC, OPB, 'Rare Candy A3 144', CL, CM], dene='RR',
       board=[B(CH, 120, 'RR', behind=[LW]), B(CL, 60, 'RR', behind=[CM]), B(LW, 50)], ko=1),
  ['Play:Poké Ball', 'UseStadium', 'Play:Lusamine', 'AttachFromDiscard{in_play_idx:0,num_random_energies:1}', 'Attach:1Grass@0 zone', 'Ability@1', 'Activate:0@2', 'Attack:Big Beat'],
  D, None,
  stadium={"card": FF, "owner": 0},
  approx=AP + "; " + APT + "; Charmander and Litwick printings chosen by HP only; his Bench is listed Celesteela then Buzzwole ex (the "
              "review does not give left and right)",
  ambiguous=[AMB_CH, AMB_CL, AMB_CM.replace('Opponent Charmander', 'Opponent Charmander under Charmeleon and in the discard:'),
             AMB_LW.replace('Opponent Litwick', 'Opponent Litwick (under Chandelure and on the Bench):')],
  draws={0: [CE], 1: [PH]},
  notes="Global 10 = his 5th turn. After global 8 his hand is Lusamine, Cyrus, Field Blower; 343-408s draw Poke Ball -> 4. Opponent "
        "global 9 (314-343s): draw (0->1), Slow Sear mills his Copycat, Fire to Chandelure (2), Heat Blast 100 KOs Pheromosa (its 1 Grass "
        "to his discard), non-ex Buzzwole 110 promoted from @3. Board: Active Buzzwole 110; Bench Celesteela 40 (@1), Buzzwole ex 170 3 "
        "Grass Leaf Cape (@2, where Pheromosa was). Opponent Chandelure 120, Charmeleon 60 (Jump Blues). His move 343-408s: Poke Ball "
        "(2nd Celesteela, kept in hand) -> use Forest (2nd Pheromosa, kept in hand) -> Lusamine on Active Buzzwole (1 Grass from the "
        "discard, the only Energy there) -> Grass from the zone to Buzzwole -> Ultra Thrusters (Ability@1: Buzzwole ex in) -> Big Beat "
        "120 KOs Chandelure. G1 DROP (drops/LAD-20261023_001330000_SR-t10.txt): the engine does not treat Buzzwole B2 014 as an Ultra "
        "Beast, so Lusamine cannot target the Active Buzzwole (AttachFromDiscard offers slots 1 and 2 only) and Ultra Thrusters cannot "
        "switch it out; the Lusamine target label is written in the engine's AttachFromDiscard form for slot 0."),
]
