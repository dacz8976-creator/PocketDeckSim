from v2_helpers import P, B
D = 'v2deck_5469f7747f'; G = '20261020_034756000_SR'
BA = 'Baltoy A3a 030'; DU = 'Dustox B4 005'; MK = 'Alolan Muk B2 097'; MKX = 'Alolan Muk ex A3 111'; PBR = 'Poison Barb A3 146'
RC = 'Rare Candy A3 144'; PB = 'Poké Ball P-A 005'; WU = 'Wurmple B4 001'; GR80 = 'Alolan Grimer B2 096'; GR70 = 'Alolan Grimer A3 110'
CT = 'Caterpie B3b 001'; MP = 'Metapod A1 006'; BF = 'Butterfree B3b 003'; TR = 'Treecko B3 005'; MS = 'Mega Sceptile ex B3 008'
FF = {"card": "Fragrant Forest B3 153", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_CT = 'Opponent Caterpie printing chosen by HP (40) and Ability (Quick Growth); B3b 001 and B3b 091 match'
AMB_TR = 'Opponent Treecko printing chosen by HP (60) only; B3 005, B3 156 and P-B 061 match'
AMB_MP = 'Opponent Metapod printing chosen by HP (80) only; A1 006, B3b 002 and B3b 092 match'
AMB_BF = 'Opponent Butterfree printing chosen by HP (130) and attack (Sunny Wind); B3b 003 and B3b 093 match'
AMB_MS = 'Opponent Mega Sceptile ex printing chosen by HP (210) only; B3 008, B3 180, B3 194 and P-B 087 match'


def _cond(c):
    def f(v):
        v['opp']['board'][0].setdefault('conditions', []).append(c)
    return f


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[DU, DU, MK, PBR, RC], disc=[], dene='', board=[B(BA, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(CT, 40), B(TR, 60)], ko=0),
  ['Play:Poison Barb', 'Tool:Poison Barb@0', 'UseStadium', 'Place:Wurmple@1', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Treecko printing is chosen by HP (60) only",
  ambiguous=[AMB_CT, AMB_TR],
  draws={2: [WU]},
  notes="Global 2 = his 1st turn (he went second). '0-34s': opening five Baltoy, Dustox, Alolan Muk, second Dustox, Poison Barb; Baltoy "
        "60 Active, no Bench -> 4 in hand. 'Global2 / owner1': draws Rare Candy -> 5. Opponent 'Global1': Caterpie 40 Active; opening 5 - "
        "1 = 4, draw (5), Fragrant Forest played (4), used: Treecko 60 (5), benched (4). His move in the review's order: Poison Barb to "
        "Baltoy, Fragrant Forest (Wurmple 60), bench Wurmple (slot 1), Darkness to Baltoy, end turn (Spinning Attack costs 2)."),
P(G, 4, 2, [0, 1],
  dict(hand=[DU, DU, MK, RC, PB], disc=[BA, PBR], dene='D', board=[B(WU, 60)], ko=1),
  dict(hand_count=4, disc=[], dene='', board=[B(BF, 120, 'G', cond=['Poisoned'], behind=[MP, CT]), B(TR, 60), B(CT, 40)], ko=0),
  ['UseStadium', 'Place:Wurmple@1', 'Play:Poké Ball', 'Place:Alolan Grimer@2', 'Play:Rare Candy', 'Evolve:Dustox@0', 'Ability@0',
   'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Treecko printing is chosen by HP (60) only; the Metapod under Butterfree is chosen by HP (80) only",
  ambiguous=[AMB_CT, AMB_TR, AMB_MP, AMB_BF],
  draws={0: [WU], 2: [GR80], 6: []}, vpatch=_cond('Confused'),
  notes="Global 4 = his 2nd turn. Hand after global 2: two Dustox, Alolan Muk, Rare Candy; 'Global4 / owner2': draws Poke Ball -> 5. "
        "End of global 2: Caterpie's Quick Growth puts Metapod from the deck onto it (no hand change). Opponent 'Global3': draw (5), "
        "Metapod -> Butterfree 130 (4), Grass attached, Fragrant Forest -> second Caterpie (5), benched (4), Sunny Wind 60 + Weakness = "
        "80 KOs Baltoy 60 (1 point), Poison Barb poisons Butterfree, checkup 130 -> 120. He promoted Wurmple 60; Baltoy, Barb and one "
        "Darkness to his discard. His move in the review's order: Fragrant Forest (second Wurmple), bench it (slot 1), Poke Ball (Alolan "
        "Grimer 80), bench it (slot 2), Rare Candy: Active Wurmple -> Dustox, Variety Powder (random: Confused; vpatch adds it in the "
        "after-chance variant), Darkness to Dustox, no attack."),
P(G, 6, 3, [0, 1],
  dict(hand=[DU, MK, GR70], disc=[BA, PBR, PB, RC], dene='D',
       board=[B(DU, 60, 'D', behind=[WU]), B(WU, 60), B(GR80, 80)], ko=1),
  dict(hand_count=4, disc=[], dene='',
       board=[B(BF, 120, 'G', cond=['Poisoned', 'Confused'], behind=[MP, CT]), B(TR, 60), B(MP, 80, behind=[CT])], ko=0),
  ['Place:Alolan Grimer@3', 'Ability@0', 'Attach:1Darkness@2 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Treecko printing is chosen by HP (60) only; the Metapod printings are chosen by HP (80) only; no Energy "
            "attachment by the opponent is shown on its 3rd turn, so Butterfree has one Grass",
  ambiguous=[AMB_CT, AMB_TR, AMB_MP, AMB_BF],
  draws={1: []}, vpatch=_cond('Burned'),
  notes="Global 6 = his 3rd turn. Hand after global 4: Dustox, Alolan Muk; 'Global6 / owner3': draws Alolan Grimer 70 (A3 110) -> 3. "
        "Board: Dustox 120 -> 60 (Sunny Wind), one Darkness, Rare Candy line (Wurmple under it); Bench Wurmple 60, Grimer 80. Opponent "
        "'Global5': draw (5), benched Caterpie -> Metapod 80 from the hand (4; Quick Growth only works Active), Confusion heads, Sunny Wind "
        "60 heals 20 (110 -> 130), poison checkup -> 120; no Energy attachment named. His move in the review's order: bench Grimer 70 "
        "(slot 3), Variety Powder (random: Burned; vpatch), Darkness to the benched Grimer 80 (slot 2), no attack."),
P(G, 8, 4, [0, 2],
  dict(hand=[DU, MK, MKX], disc=[BA, PBR, PB, RC, DU, WU], dene='DD',
       board=[B(GR80, 80, 'D'), B(WU, 60), B(GR70, 70)], ko=2),
  dict(hand_count=2, disc=['Rare Candy A3 144'], dene='G',
       board=[B(BF, 130, 'G', behind=[MP, CT]), B(MS, 210, behind=[TR]), B(BF, 90, behind=[MP, CT])], ko=0),
  ['Evolve:Alolan Muk ex@0', 'Evolve:Alolan Muk@2', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the Metapod printings are chosen by HP (80) only; the opponent's Rare Candy printing in the discard is not shown (the "
            "first listed printing is used); the Benched Butterfree's retreat is taken to have discarded its one Grass (the review "
            "does not transcribe the retreat's Energy discard)",
  ambiguous=[AMB_CT, AMB_TR, AMB_MP, AMB_BF, AMB_MS,
             "Opponent's Rare Candy in the discard: printing not shown; A3 144 used (A3 144, A4b 314, A4b 315 and A4b 379 match)"],
  notes="Global 8 = his 4th turn. Hand after global 6: Dustox, Alolan Muk; 'Global8 / owner4': draws Alolan Muk ex -> 3. Opponent "
        "'Global7': draw (5), Rare Candy + Mega Sceptile ex on Treecko (3), benched Metapod -> second Butterfree 130 (2), original "
        "Butterfree 90 retreats (retreat 1: its one Grass; Poison and Confusion gone), fresh Butterfree Active with Grass, Sunny Wind KOs "
        "Dustox 60 (2nd point). He promoted Grimer 80 (one Darkness); Dustox + Wurmple under it + one Darkness to his discard. Bench "
        "compacted: Wurmple 60 (slot 1), Grimer 70 (slot 2). Opponent Bench: Mega Sceptile ex (Treecko's slot), Butterfree 90 (Metapod's "
        "slot). His move in the review's order: Active Grimer 80 -> Alolan Muk ex, benched Grimer 70 -> Alolan Muk, Darkness to Muk ex, "
        "no attack."),
]
