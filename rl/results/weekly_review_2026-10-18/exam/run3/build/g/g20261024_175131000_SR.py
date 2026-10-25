from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_175131000_SR'
MGY = 'Mega Gyarados ex B1 052'; MK = 'Magikarp P-B 014'; CV1 = 'Carvanha B4 034'; CV2 = 'Carvanha P-B 081'; MSH = 'Mega Sharpedo ex B4 035'
PB = 'Poké Ball P-A 005'; CC = 'Copycat B1 225'; LI = 'Lisia B1 226'; CA = 'Cabbie B3 150'; WA = 'Wallace B3b 068'; SS = 'Soothing Shore B4 154'
MM = 'Mega Mawile ex B2 113'; SA = 'Steel Apron A4 153'
OTG = 'Team Rocket Grunt A2b 072'; OLI = 'Lucky Ice Pop B2 145'; OSP = 'Starting Plains B2 154'; OPC = 'Pokémon Center Lady A2b 070'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_MM = 'Opponent Mega Mawile ex printing chosen by HP (170) and attack title (Heat-Up Crunch); B2 113, B2 188, B2 201 and B4a 108 match'
AMB_TG = ('Opponent Team Rocket Grunt printing not shown; A2b 072 used (A2b 072 and A2b 091 match); the review shows it making his '
          'Active Confused with a coin for the opponent\'s own Active, which is not the database text of Team Rocket Grunt')
AMB_LI = 'Opponent Lucky Ice Pop: only B2 145 matches'
AMB_PC = 'Opponent Pokémon Center Lady printing not shown; A2b 070 used (A2b 070 and A2b 089 match)'


def evolve_active(v):
    v['me']['board'][0] = B(MSH, 190, behind=[CV1])


def evolve_karp(v):
    v['me']['board'][1] = B(MGY, 210, 'WWW', behind=[MK])


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CA, PB, WA, MSH, LI], disc=[], dene='', board=[B(CV1, 50, cond=['Confused'])], ko=0),
  dict(hand_count=4, disc=[OTG], dene='', board=[B(MM, 170)], ko=0),
  ['Play:Poké Ball', 'Place:Magikarp@1', 'Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Water}','Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None,
  approx=AP + "; the Carvanha printing (Sharp Fang, B4 034) is the review's reading of the starter",
  ambiguous=[AMB_MM, AMB_TG],
  draws={0: [MK], 2: []},
  vpatch=evolve_active,
  notes="Global 2 = his 1st turn (owner going second). Setup 24-69 s: opening five Carvanha (Sharp Fang version), Cabbie, Poke Ball, "
        "Wallace, Mega Sharpedo ex; Carvanha Active, no Bench -> hand Cabbie, Poke Ball, Wallace, Mega Sharpedo ex. 'Draw is Lisia85' "
        "-> 5. Opponent: lone Mega Mawile ex 170, hand 5 - 1 = 4; global 1: draw 5, Team Rocket Grunt (74-75 s) 4, Carvanha Confused "
        "(76 s), opponent's coin heads. His move in the review's order: Poke Ball 90 s finds Magikarp, benched 95-96 s (slot 1), Wallace "
        "105 s on the Active Carvanha -> Mega Sharpedo ex from the deck (190 HP, Confusion removed), Water to the Active, Turbo Shark 116 "
        "s (70; its Water from the zone goes to the only Benched Pokemon, Magikarp). Variant: Wallace's random evolution set on the board "
        "(vpatch), Poke Ball's Magikarp put in hand. The Wallace steps are removed in the variant; scratch/b9/t_g8.py (mode t2) shows "
        "'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Water}' in the legal list after Wallace on this turn."),
P(G, 4, 2, [0, 0],
  dict(hand=[CA, MSH, LI, CV2], disc=[PB, WA], dene='', board=[B(MSH, 190, 'W', behind=[CV1]), B(MK, 50, 'W')], ko=0),
  dict(hand_count=1, disc=[OTG, OLI, OLI], dene='', board=[B(MM, 160, 'M', tool=SA)], ko=0),
  ['Place:Carvanha@2', 'Play:Cabbie', 'Play:Soothing Shore', 'Attach:1Water@1 zone', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'],
  D, None, stadium={"card": OSP, "owner": 1},
  approx=AP,
  ambiguous=[AMB_MM, AMB_TG, AMB_LI],
  draws={1: [SS]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Cabbie, Mega Sharpedo ex, Lisia; 'Draw Carvanha161 (Aqua Jet version)' -> 4. "
        "Discard: Poke Ball, Wallace. Board: Mega Sharpedo ex 190 (one Water) Active, Magikarp 30+20 = 50 (one Water from Turbo Shark) "
        "Bench, under the opponent's Starting Plains. Opponent global 3 (121-158 s): hand 4, draw 5, Metal to Mawile, Steel Apron 4, "
        "Lucky Ice Pop 3 (tails, discarded), Lucky Ice Pop 2 (tails, discarded), Starting Plains 1 (Mawile 140 -> 160). His move in the "
        "review's order: bench Carvanha 163 s (slot 2), Cabbie 167 s finds Soothing Shore (the only Stadium in his list), Soothing Shore "
        "173-175 s replaces Starting Plains, Water to Magikarp 178-179 s, Turbo Shark 183-185 s (60 after Steel Apron), its Water to "
        "Magikarp (prompt 186 s; 'Attach:1Water@1 fx', Carvanha @2 the other option). pg_legal_v14 stops at Cabbie as a hidden "
        "search, but Cabbie is not in v2_helpers.DRAW, so check_game finds 'no chance step in the line' and runs no variant; the "
        "draws record (Soothing Shore) is given for when it is; scratch/b9/t_g8.py (mode t4: Soothing Shore in hand, Cabbie in the "
        "discard, Carvanha placed) applies the other four labels."),
P(G, 6, 3, [0, 0],
  dict(hand=[MSH, LI, WA], disc=[PB, WA, CA], dene='', board=[B(MSH, 130, 'W', behind=[CV1]), B(MK, 30, 'WWW'), B(CV2, 50)], ko=0),
  dict(hand_count=1, disc=[OTG, OLI, OLI, OSP, OPC], dene='', board=[B(MM, 110, 'MM', tool=SA)], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Water}','Retreat:1', 'Attach:1Water@0 zone', 'Attack:Mega Blaster'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; Heat-Up Crunch's lasting +30 on the opponent's Mega Mawile ex (used on global 5, it stays Active) is not set: the "
              "engine form for it is not in the brief's effect list",
  ambiguous=[AMB_MM, AMB_TG, AMB_LI, AMB_PC],
  draws={0: []},
  vpatch=evolve_karp,
  notes="Global 6 = his 3rd turn. Hand after global 4: Mega Sharpedo ex, Lisia; 'Draw second Wallace209' -> 3. Discard adds Cabbie. "
        "Soothing Shore (his) in play. Board: Mega Sharpedo ex 190 - 60 = 130 (one Water) Active; Bench Magikarp 30 (three Water), "
        "Carvanha (Aqua Jet) 50. Opponent global 5 (189-206 s): hand 1, draw 2, second Metal, Pokemon Center Lady 1 (Mawile 80 -> 110), "
        "Heat-Up Crunch 60 to Sharpedo; Starting Plains went to the opponent's discard when replaced on global 4. His move in the "
        "review's order: Wallace 213 s on benched Magikarp -> Mega Gyarados ex from the deck (210, three Water kept), retreat Sharpedo "
        "(no Energy paid) 222-225 s, Gyarados Active, Water to it 226 s, Mega Blaster 229 s (130 after Steel Apron, KOs Mawile, +3, "
        "game over). Variant: the random evolution set on the board (vpatch). pg_legal_v14 stops at the random evolution choice "
        "('hidden random choice') without matching its label, which its legal list holds exactly, so check_game counts the label "
        "as unmatched and runs no variant; scratch/b9/t_g8w.py shows the same with no label or a bare label, and scratch/b9/t_g8t6v.py "
        "(Gyarados set on Magikarp, Wallace in the discard) applies Retreat, Attach and Mega Blaster."),
]
