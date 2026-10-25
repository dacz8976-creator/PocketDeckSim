from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_031141000_SR'
WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'; CV = 'Carvanha B4 034'; MSH = 'Mega Sharpedo ex B4 035'
PB = 'Poké Ball P-A 005'; EC = 'Elegant Cape B3b 065'; CC = 'Copycat B1 225'; HH = 'Heavy Helmet B1 219'; WA = 'Wallace B3b 068'
BU = 'Budew B3 013'; SH = 'Shuckle ex A4 021'; CB = 'Combee A2 017'; VQ = 'Vespiquen ex B4 011'
OPR = "Professor's Research A4b 373"; OSS = 'Sightseer B2 150'; OCC = 'Copycat B1 225'
FF = {"card": "Fragrant Forest B3 153", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_SH = 'Opponent Shuckle ex printing chosen by HP (120) and Ability title (Solid Shell); A4 021, A4 186, A4 202 and A4b 023 match'
AMB_BU = 'Opponent Budew printing chosen by HP (30) and attack title (Prickly Powder); B3 013 and B3 159 match'
AMB_CB = 'Opponent Combee: its attack was not shown; printing chosen by HP (50) only'
AMB_VQ = 'Opponent Vespiquen ex printings chosen by HP (140) and attack title (Chase Order); B4 011, B4 180 and B4 194 match'


def no_energy_now(p):
    """The first player's first turn: no Energy from the zone. With energy_now set, pg_legal_v14 lists an attach as legal on
    global turn 1 (scratch/b3/t_t1energy.py); None makes the zone read ["None", "Some(Water)"]."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[PB, EC, CC, MSH], disc=[], dene='', board=[B(WM, 100), B(BT, 60)], ko=0),
  dict(hand_count=2, disc=[], dene='', board=[B(BU, 30), B(SH, 120), B(CB, 50)], ko=0),
  ['Play:Poké Ball', 'Place:Carvanha@2', 'Play:Elegant Cape', 'Tool:Elegant Cape@2', 'Play:Copycat', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Budew and Combee printings are chosen by name and HP (no attack used yet); no Energy on the first "
            "player's first turn (energy_now None)",
  ambiguous=['Opponent Budew printing chosen by name and HP (30); B3 013 and B3 159 match', AMB_SH, AMB_CB],
  draws={0: [CV], 4: ['-' + MSH, MSH, MSH]},
  notes="Global 1 = his 1st turn (he went first). 'Global turn 0': opening five Wailmer, Baltoy, Poke Ball, Elegant Cape, Copycat; "
        "Wailmer 100 Active, Baltoy 60 Bench -> 3 in hand. Opponent: Budew 30 Active, Shuckle ex 120 and Combee 50 Bench -> 5 - 3 = 2 "
        "in hand, no draw yet. 'Global turn 1': draw Mega Sharpedo ex -> 4. His move in the review's order: Poke Ball (Carvanha 50), "
        "Carvanha benched (@2), Elegant Cape on Carvanha, Copycat (the remaining hand, one Mega Sharpedo ex, shuffled in; draws two "
        "to match the opponent's 2: two Mega Sharpedo ex), end without Energy or attack. energy_now set to None after P().")),
P(G, 3, 2, [0, 0],
  dict(hand=[MSH, MSH, HH], disc=[PB, CC], dene='',
       board=[B(WM, 90, effects=[{"effect": "NoAbilities", "turns": 1}]), B(BT, 60), B(CV, 50, tool=EC)], ko=0),
  dict(hand_count=3, disc=[OPR], dene='', board=[B(BU, 30), B(SH, 120), B(CB, 50, 'G'), B(CB, 50)], ko=0),
  ['Evolve:Mega Sharpedo ex@2', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Professor's Research printing is not shown, the printing cards.py lists first is used; the "
            "opponent's Fragrant Forest use on global turn 2 is counted +1 card (its result is hidden; a Combee was benched after "
            "it); Prickly Powder's effect on Wailmer ('loses all Abilities ... until it leaves the Active Spot') is given as "
            "NoAbilities for 1 turn (Wailmer has no Ability); the second Combee's printing is chosen by HP (50) only",
  ambiguous=[AMB_BU, AMB_SH, AMB_CB, 'Opponent second Combee: its attack was not shown; printing chosen by HP (50) only'],
  notes="Global 3 = his 2nd turn. Hand after global 1: Elegant Cape played, Copycat drew two Mega Sharpedo ex -> hand two Mega "
        "Sharpedo ex. 'Global turn 3': draw Heavy Helmet -> 3. Board: Wailmer 90 Active (Prickly Powder 10 and its no-Abilities "
        "effect, global 2), Baltoy 60, Carvanha 50 with Elegant Cape. Discard Poke Ball, Copycat. Opponent 'Global turn 2': draw (3), "
        "Professor's Research (4), Fragrant Forest Stadium (3), Forest use (+1 = 4), 2nd Combee benched (3), Grass on the original "
        "Combee, Prickly Powder. Opp Bench order: Shuckle ex, Combee, 2nd Combee (benched order). His move in the review's order: "
        "Carvanha -> Mega Sharpedo ex (220 with Cape), Heavy Helmet on Wailmer, Water to Wailmer, end without attack."),
P(G, 5, 3, [0, 1],
  dict(hand=[MSH, WA], disc=[PB, CC, WM, HH], dene='W', board=[B(MSH, 220, tool=EC, behind=[CV]), B(BT, 60)], ko=1),
  dict(hand_count=3, disc=[OPR, OSS, BU], dene='', board=[B(VQ, 140, 'GG', behind=[CB]), B(SH, 120), B(VQ, 140, behind=[CB])], ko=0),
  ['Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Professor's Research and Sightseer printings are not shown, the printing cards.py lists first is "
            "used; on global turn 4 the opponent's Fragrant Forest use (hidden) is counted +1 and Sightseer's take is counted +1 "
            "(the second Vespiquen ex, played right after; the review does not say how many Stage 1 cards it took); the Combee "
            "printings under both Vespiquen ex are chosen by HP (50) only",
  ambiguous=[AMB_VQ, AMB_SH, 'Opponent Combee under each Vespiquen ex: its attack was not shown; printing chosen by HP (50) only'],
  notes="Global 5 = his 3rd turn. Hand after global 3: one Mega Sharpedo ex. 'Global turn 5': draw Wallace -> 2. 'Global turn 4': "
        "Chase Order (Budew discarded) 140 - Heavy Helmet 20 = 120 KOs Wailmer 90 (Wailmer, Helmet, Water to discard; score 0-1, ko "
        "1); he promotes caped Mega Sharpedo ex 220; Baltoy 60 on the Bench. Opponent global 4: draw (4), Forest (+1 = 5), original "
        "Combee -> Vespiquen ex (4), Budew retreats (cost 0) for Vespiquen, 2nd Grass to it, Sightseer (3, +1 = 4), 2nd Combee -> 2nd "
        "Vespiquen ex (3), Chase Order discarding Budew. Opp Bench: Shuckle ex, 2nd Vespiquen ex (no Energy). His move: Water to "
        "Mega Sharpedo, Turbo Shark 70 (no Water Pokemon on his Bench to take the Energy)."),
P(G, 7, 4, [0, 1],
  dict(hand=[MSH, WA, WL], disc=[PB, CC, WM, HH], dene='W', board=[B(MSH, 80, 'W', tool=EC, behind=[CV]), B(BT, 60)], ko=1),
  dict(hand_count=2, disc=[OPR, OSS, BU, OCC, BU], dene='', board=[B(VQ, 70, 'GG', behind=[CB]), B(SH, 120), B(VQ, 140, 'G', behind=[CB])],
       ko=0),
  ['Attach:1Water@1 zone', 'Retreat:1', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Professor's Research, Sightseer and Copycat printings are not shown, the printing cards.py lists first "
            "is used; global turn 4's Fragrant Forest and Sightseer counted +1 each; global turn 6's Forest use found nothing (no "
            "+1); the Combee printings under both Vespiquen ex are chosen by HP (50) only",
  ambiguous=[AMB_VQ, AMB_SH, AMB_BU, 'Opponent Combee under each Vespiquen ex: its attack was not shown; printing chosen by HP (50) only'],
  notes="Global 7 = his 4th turn. Hand after global 5: Mega Sharpedo ex, Wallace. 'Global turn 7': draw Wailord -> 3. Board: Mega "
        "Sharpedo ex 80 (global 6 Chase Order 140 into 220), one Water, Cape; Baltoy 60. Opponent 'Global turn 6': draw (4), 2nd "
        "Budew benched (3), Forest no target (3), Copycat (2, shuffle, draw 2 = his hand Mega Sharpedo ex + Wallace), Grass to the "
        "Benched 2nd Vespiquen, Chase Order discarding the new Budew. Active Vespiquen 70 (Turbo Shark on global 5), two Grass. His "
        "move in the review's order: Water to Baltoy (@1), retreat Mega Sharpedo (cost 0) for Baltoy (Retreat:1), end without "
        "attack (native 275 s: Water on both)."),
]
