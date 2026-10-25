from v2_helpers import P, B
D = 'v2deck_6328cc45fe'; G = '20261023_005124000_SR'
BX = 'Buzzwole ex A3a 006'; PH = 'Pheromosa A3a 007'; CE = 'Celesteela A3a 062'; BZ = 'Buzzwole B2 014'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'; LC = 'Leaf Cape A3 147'
RH = 'Rocky Helmet A2 148'; LU = 'Lusamine A3a 069'; CC = 'Copycat B1 225'; SP = 'Starting Plains B2 154'; FB = 'Field Blower B3 147'
FF = 'Fragrant Forest B3 153'
CT = 'Caterpie B3b 001'; MP = 'Metapod A1 006'; BF = 'Butterfree B3b 003'; TK = 'Treecko B3 005'; GV = 'Grovyle B3 006'
MS = 'Mega Sceptile ex B3 008'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_CT = 'Opponent Caterpie printing chosen by HP (40) and Ability title (Quick Growth); B3b 001 and B3b 091 match'
AMB_MP = 'Opponent Metapod printing chosen by HP (80) only (its attack was not shown); A1 006, B3b 002 and B3b 092 match'
AMB_BF = 'Opponent Butterfree printing chosen by HP (130) and attack title (Sunny Wind); B3b 003 and B3b 093 match'
AMB_TK = 'Opponent Treecko printing chosen by HP (60) only; B3 005, B3 156 and P-B 061 match'
AMB_GV = 'Opponent Grovyle printing chosen by HP (80) only; B3 006 and B3 157 match'
AMB_MS = 'Opponent Mega Sceptile ex printing chosen by HP (210); B3 008, B3 180, B3 194 and P-B 087 match'
BIGBEAT = [{"effect": {"CannotUseAttack": "Big Beat"}, "turns": 1}]
REF = ("The review's Fragrant Forest uses that end with a no-eligible-target message (his on global 4 and 6, the opponent's on global 7) "
       "and his refused 2nd Poke Ball on global 12 ('conditions not met', nothing consumed) are read as attempts the game refused, not "
       "actions, and are not in force.")
GV7 = ("the opponent's global-7 Caterpie -> Metapod (named Quick Growth in the review, but Caterpie was benched) is counted as 1 card "
       "from the hand (a Metapod or a Quick-Grow Extract; either way -1)")
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[BZ, LU, PR, LC, SA], disc=[], dene='', board=[B(CE, 120)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(CT, 40)], ko=0),
  ["Play:Professor's Research", 'Place:Pheromosa@1', 'Place:Buzzwole@2', 'Ability@0', 'Attach:1Grass@0 zone', 'Play:Fragrant Forest',
   'UseStadium', 'Place:Buzzwole ex@3', 'Play:Leaf Cape', 'Tool:Leaf Cape@3', 'Attack:Jump Blues'],
  D, None,
  approx=AP + "; Caterpie printing chosen by HP and Ability title",
  ambiguous=[AMB_CT],
  draws={0: [PH, FF], 6: [BX]},
  notes="Global 2 = his 1st turn (he went second). REVIEW 'Opening' 0-38s: opening five Celesteela, non-ex Buzzwole, Lusamine, "
        "Research, Leaf Cape; Celesteela Active, no Bench -> 4. Global 2 (45-107s): draw Sabrina -> 5. Opponent: Caterpie 40 Active, "
        "no Bench (5-1 = 4), global 1 draw (5), nothing played. His move 45-107s in order: Professor's Research (Pheromosa, Fragrant "
        "Forest) -> Pheromosa benched (@1) -> Buzzwole benched (@2) -> Ultra Thrusters from Active Celesteela (Ability@0; Pheromosa "
        "comes in; the engine's only Benched Ultra Beast choice, applied by the tool) -> Grass to Active Pheromosa -> Fragrant Forest -> "
        "use it (Buzzwole ex) -> Buzzwole ex benched (@3) -> Leaf Cape on Buzzwole ex (@3) -> Jump Blues 20 (no opponent Bench)."),
P(G, 4, 2, [0, 0],
  dict(hand=[LU, SA, PH], disc=[PR], dene='', board=[B(PH, 10, 'G'), B(CE, 120), B(BZ, 110), B(BX, 170, tool=LC)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(BF, 130, 'G', behind=[MP, CT]), B(TK, 60)], ko=0),
  ['Play:Sabrina', 'Attach:1Grass@3 zone', 'Attack:Jump Blues'],
  D, None,
  stadium={"card": FF, "owner": 0},
  approx=AP + "; the opponent's global-3 Fragrant Forest use is counted as +1 (Treecko, benched); Metapod and Treecko printings "
              "chosen by HP only",
  ambiguous=[AMB_BF, AMB_MP.replace('Opponent Metapod', 'Opponent Metapod under Butterfree:'),
             AMB_CT.replace('Opponent Caterpie', 'Opponent Caterpie under Butterfree:'), AMB_TK],
  notes="Global 4 = his 2nd turn. After global 2 his hand is Lusamine, Sabrina; 131-152s draw 2nd Pheromosa -> 3. Board: Active "
        "Pheromosa 70-60 = 10 with 1 Grass; Bench Celesteela 120, Buzzwole 110, Buzzwole ex 170 with Leaf Cape (Celesteela took "
        "Pheromosa's slot @1 in the switch). His Fragrant Forest in play. Opponent: end of global 2 Quick Growth Caterpie -> Metapod 60 "
        "(from the deck); global 3 (107-131s): draw (6), Metapod -> Butterfree 110 (5), Grass attached, Forest use (Treecko +1, benched, "
        "5), Sunny Wind 60 and heal 20 -> Butterfree 130. His move 131-152s: Sabrina (the opponent's only Bench, Treecko, comes in; "
        "applied by the tool) -> " + "Grass to the benched Buzzwole ex (@3) -> Jump Blues (20 Treecko, 20 the benched Butterfree; the "
        "engine's bench-target step is two identical 'ApplyQueuedAttackDamage' labels, never written). " + REF),
P(G, 6, 3, [0, 1],
  dict(hand=[LU, PH, CC], disc=[PR, SA, PH], dene='G', board=[B(BZ, 110), B(CE, 120), B(BX, 170, 'G', tool=LC)], ko=1),
  dict(hand_count=5, disc=[], dene='', board=[B(BF, 130, 'G', behind=[MP, CT]), B(GV, 80, behind=[TK]), B(CT, 40)], ko=0),
  ['Play:Copycat', 'Place:Pheromosa@3', 'Ability@1', 'Activate:0@3', 'Play:Field Blower', 'DiscardActiveStadium', 'Attach:1Grass@0 zone',
   'Attack:Jump Blues'],
  D, None,
  stadium={"card": FF, "owner": 0},
  approx=AP + "; the opponent's global-5 Forest use is counted as +1 (Caterpie, benched) and its Lucky Ice Pop as returned (heads, "
              "shown); the opponent's Grovyle retreat on global 5 shows no Energy and no discard, so no opponent discard is listed; "
              "Metapod, Treecko and Grovyle printings chosen by HP only; the opponent's Bench is listed Grovyle then Caterpie (the "
              "review does not give left and right)",
  ambiguous=[AMB_BF, AMB_MP.replace('Opponent Metapod', 'Opponent Metapod under Butterfree:'),
             AMB_CT.replace('Opponent Caterpie', 'Opponent Caterpie (under Butterfree and on the Bench):'), AMB_GV,
             AMB_TK.replace('Opponent Treecko', 'Opponent Treecko under Grovyle:')],
  draws={0: ['-' + LU, '-' + PH, LU, LU, FB, PR, PH]},
  notes="Global 6 = his 3rd turn. After global 4 his hand is Lusamine, Pheromosa; 223-294s draw Copycat -> 3. Global 5 (152-223s): "
        "Sunny Wind KOs Pheromosa (its Grass to his discard; opponent 1 point), Buzzwole 110 promoted from @2; Bench Celesteela @1, "
        "Buzzwole ex 170 Cape 1 Grass @2. Opponent global 5: draw (6), Forest (Caterpie, +1 -> 7), Caterpie benched (6), Treecko -> "
        "Grovyle (5), Lucky Ice Pop heads (back to hand, 5), Grovyle retreat to Butterfree, Sunny Wind. His move 223-294s: Copycat "
        "(shuffles Lusamine, Pheromosa; draws 5 = opponent's 5: Lusamine, Lusamine, Field Blower, Research, Pheromosa; the canceled "
        "Energy drag is not an action) -> 2nd Pheromosa benched (@3) -> Ultra Thrusters from Benched Celesteela (Ability@1: Active "
        "Buzzwole out, Pheromosa @3 in) -> Field Blower on his own Forest -> Grass to Active Pheromosa -> Jump Blues (20 Butterfree, 20 "
        "the benched Grovyle). " + REF + " G1 DROP (drops/LAD-20261023_005124000_SR-t6.txt): the engine does not treat Buzzwole B2 014 "
        "as an Ultra Beast, so Ultra Thrusters cannot switch the Active Buzzwole; 'Activate:0@3' (Pheromosa) is the choice label the "
        "engine would ask for with three Benched Ultra Beasts; the labels after the switch apply in scratch/b6/t_fieldblower_test.py."),
P(G, 8, 4, [0, 1],
  dict(hand=[LU, LU, PR, CY], disc=[PR, SA, PH, CC, FF, FB], dene='G',
       board=[B(PH, 10, 'G'), B(CE, 120), B(BX, 170, 'G', tool=LC), B(BZ, 110)], ko=1),
  dict(hand_count=3, disc=[], dene='', board=[B(BF, 130, 'G', behind=[MP, CT]), B(MS, 190, 'G', behind=[GV, TK]), B(MP, 80, behind=[CT])],
       ko=0),
  ['Play:Lusamine', 'AttachFromDiscard{in_play_idx:2,num_random_energies:1}', 'Attach:1Grass@3 zone', 'Attack:Jump Blues'],
  D, None,
  stadium={"card": FF, "owner": 1},
  approx=AP + "; " + GV7 + "; the opponent's Grovyle retreat on global 5 shows no Energy and no discard, so no opponent discard is "
              "listed; Metapod and Treecko/Grovyle printings chosen by HP only; the opponent's Bench is listed Mega Sceptile ex then "
              "Metapod (the review does not give left and right)",
  ambiguous=[AMB_BF, AMB_MS, AMB_MP.replace('Opponent Metapod', 'Opponent Metapod (under Butterfree and on the Bench):'),
             AMB_CT.replace('Opponent Caterpie', 'Opponent Caterpie (under Butterfree and under Metapod):'),
             AMB_GV.replace('Opponent Grovyle', 'Opponent Grovyle under Mega Sceptile ex:'),
             AMB_TK.replace('Opponent Treecko', 'Opponent Treecko under Mega Sceptile ex:')],
  notes="Global 8 = his 4th turn. After global 6 his hand is Lusamine, Lusamine, Research; 354-414s draw Cyrus -> 4. Board after global "
        "6: Active Pheromosa 70-60 = 10 with 1 Grass; Bench Celesteela 120 @1, Buzzwole ex 170 Cape 1 Grass @2, Buzzwole 110 @3 (no "
        "Energy). Discard: Research, Sabrina, Pheromosa, Copycat, Fragrant Forest (his, Field Blower), Field Blower; Grass 1. Opponent "
        "global 7 (294-354s): draw (6), its own Fragrant Forest (5), Grass to Grovyle, Grovyle -> Mega Sceptile ex 190 (4), Caterpie -> "
        "Metapod 80 (3), Forest no target, Sunny Wind -> Butterfree 130. His move 354-414s: Lusamine on the benched Buzzwole ex (the one "
        "discarded Grass; engine AttachFromDiscard slot 2) -> Grass from the zone to the benched Buzzwole (@3) -> Jump Blues (20 "
        "Butterfree, 20 the benched Mega; bench-target step not written). Celesteela's Ability is inspected, not used."),
P(G, 10, 5, [0, 2],
  dict(hand=[LU, PR, CY, SP], disc=[PR, SA, PH, CC, FF, FB, LU, PH], dene='G',
       board=[B(BX, 170, 'GG', tool=LC), B(CE, 120), B(BZ, 110, 'G')], ko=2),
  dict(hand_count=3, disc=['Quick-Grow Extract B1a 067'], dene='',
       board=[B(BF, 130, 'G', behind=[MP, CT]), B(MS, 170, 'GG', behind=[GV, TK]), B(BF, 130, behind=[MP, CT])], ko=0),
  ['Play:Starting Plains', 'Play:Cyrus', 'Attach:1Grass@0 zone', 'Attack:Big Beat'],
  D, None,
  stadium={"card": FF, "owner": 1},
  approx=AP + "; " + GV7 + "; the opponent's Quick-Grow Extract printing is not shown, the first printing is used; Metapod and "
              "Treecko/Grovyle printings chosen by HP only; the opponent's Bench is listed Mega Sceptile ex then Butterfree, his "
              "Celesteela then Buzzwole (the review does not give left and right)",
  ambiguous=[AMB_BF, AMB_MS, AMB_MP.replace('Opponent Metapod', 'Opponent Metapod under each Butterfree:'),
             AMB_CT.replace('Opponent Caterpie', 'Opponent Caterpie under each Butterfree:'),
             AMB_GV.replace('Opponent Grovyle', 'Opponent Grovyle under Mega Sceptile ex:'),
             AMB_TK.replace('Opponent Treecko', 'Opponent Treecko under Mega Sceptile ex:')],
  notes="Global 10 = his 5th turn. After global 8 his hand is Lusamine, Research, Cyrus; 445-472s draw Starting Plains -> 4. Global 9 "
        "(414-445s): opponent draw (4), Grass to Mega (2), Quick-Grow Extract (3) Metapod -> Butterfree 130, Sunny Wind KOs Pheromosa "
        "(its Grass to his discard; opponent 2 points), Buzzwole ex promoted from @2; Bench Celesteela @1, Buzzwole 110 1 Grass "
        "(compacted @2). His move 445-472s: Starting Plains (replaces the opponent's Forest) -> Cyrus (the damaged Mega, the only "
        "damaged Bench Pokemon) -> Grass to Active Buzzwole ex -> Big Beat 120 on Mega."),
P(G, 12, 6, [0, 2],
  dict(hand=[LU, PR, PB], disc=[PR, SA, PH, CC, FF, FB, LU, PH, CY], dene='G',
       board=[B(BX, 130, 'GGG', tool=LC, effects=BIGBEAT), B(CE, 140), B(BZ, 130, 'G')], ko=2),
  dict(hand_count=3, disc=['Quick-Grow Extract B1a 067', FF, 'Lucky Ice Pop B2 145'], dene='G',
       board=[B(BF, 130, 'G', behind=[MP, CT]), B(MS, 70, 'G', behind=[GV, TK]), B(BF, 130, behind=[MP, CT])], ko=0),
  ['Play:Poké Ball', "Play:Professor's Research", 'Play:Rocky Helmet', 'Tool:Rocky Helmet@2', 'Place:Celesteela@3', 'Ability@1',
   'Activate:0@2', 'Attach:1Grass@0 zone', 'Ability@3', 'Activate:0@2', 'EndTurn'],
  D, None,
  stadium={"card": SP, "owner": 0},
  approx=AP + "; " + GV7 + "; the opponent's Trainer printings (Quick-Grow Extract, Lucky Ice Pop) are not shown, the first printings "
              "are used; Metapod and Treecko/Grovyle printings chosen by HP only; the opponent's Bench is listed Mega Sceptile ex then "
              "Butterfree, his Celesteela then Buzzwole (the review does not give left and right)",
  ambiguous=[AMB_BF, AMB_MS, AMB_MP.replace('Opponent Metapod', 'Opponent Metapod under each Butterfree:'),
             AMB_CT.replace('Opponent Caterpie', 'Opponent Caterpie under each Butterfree:'),
             AMB_GV.replace('Opponent Grovyle', 'Opponent Grovyle under Mega Sceptile ex:'),
             AMB_TK.replace('Opponent Treecko', 'Opponent Treecko under Mega Sceptile ex:')],
  draws={0: [CE], 1: [RH, PB]},
  notes="Global 12 = his 6th turn. After global 10 his hand is Lusamine, Research; 500-588s draw Poke Ball -> 3. Board: Active "
        "Buzzwole ex 190-60 = 130 (Plains, Cape) with 3 Grass and Big Beat locked; Bench Celesteela 140, Buzzwole 130 1 Grass. Opponent "
        "global 11 (472-500s): draw (4), Lucky Ice Pop tails (discarded, 3), retreat Mega discarding 1 Grass, Butterfree in, Sunny Wind "
        "60. Opponent discard also has its Forest (replaced by Plains on global 10). His move 500-588s: Poke Ball (2nd Celesteela) -> "
        "Professor's Research (Rocky Helmet, 2nd Poke Ball) -> [2nd Poke Ball refused, not an action] -> Rocky Helmet on Buzzwole (@2) "
        "-> 2nd Celesteela benched (@3) -> Ultra Thrusters from the 1st Celesteela (Ability@1: Buzzwole ex out, Buzzwole @2 in) -> Grass "
        "to Active Buzzwole -> Ultra Thrusters from the 2nd Celesteela (Ability@3: Buzzwole out, Buzzwole ex @2 back in) -> the timer "
        "ran out, no attack (EndTurn stands for the timer's end of turn). G1 DROP (drops/LAD-20261023_005124000_SR-t12.txt): the engine "
        "does not treat Buzzwole B2 014 as an Ultra Beast, so neither Ultra Thrusters switch can apply."),
]
