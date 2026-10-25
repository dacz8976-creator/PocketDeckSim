from v2_helpers import P, B
D = 'v2deck_9633a01781'; G = '20261020_035443000_SR'
GO = 'Goomy B1 177'; HG = 'Hisuian Goodra B3b 050'; DT = 'Dratini B4 116'; DA = 'Dragonair B4 117'; DN = 'Dragonite B4 118'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; LIP = 'Lucky Ice Pop B2 145'
SL = 'Slugma A2 025'; MC = 'Magcargo A4 031'; OHH = 'Heavy Helmet B1 219'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AP_EZ = "; his zone's next Energy is not stated by the review: the Energy he received on his next turn is used"
AMB_SL = 'Opponent Slugma printing chosen by HP (70) only; A2 025 and A4 030 match'
AMB_MC = 'Opponent Magcargo printing chosen by HP (120) and attack (Spurt Fire): A4 031'


def _hp(v_hp):
    def f(v):
        v['me']['board'][0]['hp'] = v_hp
    return f


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[RC, LIP, PB, HH, DA], disc=[], dene='', board=[B(GO, 40)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(SL, 70, tool=OHH)], ko=0),
  ['Play:Poké Ball', 'Place:Dratini@1', 'Attach:1Metal@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Slugma printing is chosen by HP (70) only" + AP_EZ + " (Water)",
  ambiguous=[AMB_SL],
  draws={0: [DT]}, ez_now='M', ez_next='W',
  notes="Global 2 = his 1st turn (he went second). '19-41s': opening five Goomy, Rare Candy, Lucky Ice Pop, Poke Ball, Heavy Helmet; "
        "Goomy 40 Active, Bench empty -> 4 in hand. 'Global turn2, owner turn1': draws Dragonair -> 5; Poke Ball (Dratini), Dratini "
        "benched (the game showed it on the right; lowest empty slot @1, convention 1), Metal from the zone to Goomy, no attack. Opponent: "
        "Slugma 70 Active, no Bench; 'Global turn1': opening 5 - 1 = 4, draw (5), Heavy Helmet to Slugma (4). Zone: Metal now; next = "
        "Water (attached on global 4)."),
P(G, 4, 2, [0, 0],
  dict(hand=[RC, LIP, HH, DA, DT], disc=[PB], dene='', board=[B(GO, 40, 'M'), B(DT, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(MC, 120, 'R', tool=OHH, behind=[SL])], ko=0),
  ['Place:Dratini@2', 'Evolve:Dragonair@1', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the Slugma under the opponent's Magcargo is chosen by HP (70) only" + AP_EZ + " (Lightning)",
  ambiguous=[AMB_SL, AMB_MC],
  ez_now='W', ez_next='L',
  notes="Global 4 = his 2nd turn. Hand after global 2: Rare Candy, Lucky Ice Pop, Heavy Helmet, Dragonair; 'Global turn4': draws the "
        "second Dratini -> 5. Opponent 'Global turn3': draw (5), Fire to Slugma, Slugma -> Magcargo 120 (4); no attack. His move in the "
        "review's order: bench the second Dratini (the game showed it on the left; lowest empty slot @2), the earlier Dratini (slot 1) -> "
        "Dragonair, Water to Goomy, no attack. Zone: Water now; next = Lightning (attached global 6)."),
P(G, 6, 3, [0, 0],
  dict(hand=[RC, LIP, HH, PR], disc=[PB], dene='', board=[B(GO, 40, 'WM'), B(DT, 60), B(DA, 80, behind=[DT])], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(MC, 120, 'RR', tool=OHH, behind=[SL])], ko=0),
  ["Play:Professor's Research", 'Attach:1Lightning@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the Slugma under the opponent's Magcargo is chosen by HP (70) only; his Bench order is the review's left-to-right "
            "(Dratini left, Dragonair right)" + AP_EZ + " (Lightning)",
  ambiguous=[AMB_SL, AMB_MC],
  draws={0: [PR, CC]}, ez_now='L', ez_next='L',
  notes="Global 6 = his 3rd turn. Hand after global 4: Rare Candy, Lucky Ice Pop, Heavy Helmet; 'Global turn6': draws Professor's "
        "Research -> 4. Board as the review lists it left to right: Goomy 40 (Water+Metal) Active, Bench Dratini 60 (left), Dragonair 80 "
        "(right) -> compacted [Dratini, Dragonair]. Opponent 'Global turn5': draw (5), second Fire, no attack (Sticky Membrane). His move: "
        "Professor's Research (the second Research and Copycat), Lightning to the benched Dragonair (slot 2), no attack. Zone: Lightning "
        "now; next = Lightning (attached global 8)."),
P(G, 8, 4, [0, 1],
  dict(hand=[RC, LIP, HH, PR, CC, HG], disc=[PB, PR, GO], dene='WM', board=[B(DT, 60), B(DA, 30, 'L', behind=[DT])], ko=1),
  dict(hand_count=6, disc=[], dene='', board=[B(MC, 120, 'RRR', tool=OHH, behind=[SL])], ko=0),
  ['Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Play:Copycat', 'Place:Goomy@2', 'Play:Rare Candy', 'Evolve:Dragonite@0',
   'Attach:1Lightning@0 zone', 'Ability@1', 'AttachTypedFromDiscard:Water@0', 'EndTurn'],
  D, None,
  approx=AP + "; the Slugma under the opponent's Magcargo is chosen by HP (70) only" + AP_EZ + " (Water)",
  ambiguous=[AMB_SL, AMB_MC],
  draws={2: ['-' + RC, '-' + LIP, '-' + PR, '-' + HG, DN, HG, GO, LIP, RC, CY]}, ez_now='L', ez_next='W',
  notes="Global 8 = his 4th turn. Hand after global 6: Rare Candy, Lucky Ice Pop, Heavy Helmet, Professor's Research, Copycat; 'Global "
        "turn8': draws Hisuian Goodra -> 6. Opponent 'Global turn7': draw (6), third Fire, Spurt Fire: Goomy 100 (KO, 1 point; Goomy + "
        "Water + Metal to his discard), Dragonair 80 -> 30; he promoted Dratini 60. Bench compacted: Dragonair 30 (Lightning) slot 1. "
        "Opponent's hand 6 matches his Copycat drawing six. His move in the review's order: Heavy Helmet to the Active Dratini, Copycat "
        "(Rare Candy, Ice Pop, Research, Goodra shuffled away; draws Dragonite, Hisuian Goodra, Goomy, Lucky Ice Pop, Rare Candy, Cyrus), "
        "bench Goomy (slot 2), Rare Candy: Active Dratini -> Dragonite, Lightning to Dragonite, Dragon's Blessing from the benched "
        "Dragonair (Water from the discard to Dragonite), end without attack."),
P(G, 10, 5, [0, 2],
  dict(hand=[HG, LIP, CY, PR], disc=[PB, PR, GO, CC, RC, DA, DT], dene='ML',
       board=[B(DN, 70, 'WL', tool=HH, behind=[DT]), B(GO, 40)], ko=2),
  dict(hand_count=7, disc=[], dene='', board=[B(MC, 120, 'RRRR', tool=OHH, behind=[SL])], ko=0),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Play:Rare Candy', 'Evolve:Hisuian Goodra@1', 'Play:Lucky Ice Pop',
   'Attach:1Water@0 zone', 'Attack:Hyper Beam'],
  D, None,
  approx=AP + "; the Slugma under the opponent's Magcargo is chosen by HP (70) only" + AP_EZ + " (Lightning)",
  ambiguous=[AMB_SL, AMB_MC],
  draws={0: [RC, PB], 1: [], 4: []}, vpatch=_hp(90), ez_now='W', ez_next='L',
  notes="Global 10 = his 5th turn. Hand after global 8: Hisuian Goodra, Lucky Ice Pop, Cyrus; 'Global turn10': draws Professor's "
        "Research -> 4. Opponent 'Global turn9': draw (7), fourth Fire, Spurt Fire: Dragonite 150 - (100 - 20 Helmet) = 70, Dragonair 30 "
        "KO'd (2nd point; Dragonair + Dratini + Lightning to his discard). His discard Energy: Metal (Goomy's Water went to Dragonite) + "
        "Lightning. His move in the review's order: Professor's Research (Rare Candy, Poke Ball), Poke Ball (no Basic left: draws = []), "
        "Rare Candy: benched Goomy (slot 1) -> Hisuian Goodra, Lucky Ice Pop (70 -> 90, tails: discarded; vpatch sets 90), Water to "
        "Dragonite, Hyper Beam."),
P(G, 12, 6, [0, 2],
  dict(hand=[CY, LIP], disc=[PB, PR, GO, CC, RC, DA, DT, PR, PB, RC, LIP], dene='ML',
       board=[B(DN, 10, 'WWL', tool=HH, behind=[DT]), B(HG, 100, behind=[GO])], ko=2),
  dict(hand_count=4, disc=[LIP, LIP, 'Order Pad B4 145', 'Order Pad B4 145', 'Flame Patch B1 217'], dene='',
       board=[B(MC, 90, 'RRRR', tool=OHH, behind=[SL]), B(SL, 70, 'R')], ko=0),
  ['Attach:1Lightning@1 zone', 'Play:Lucky Ice Pop', 'Attack:Hyper Beam'],
  D, None,
  approx=AP + "; the opponent's Slugma printings are chosen by HP (70) only; the review names the opponent's two coin-flip Item "
            "searches 'Silver Pad', a name not in the card database: Order Pad (coin, heads: a random Item from the deck) is used; the "
            "opponent's Lucky Ice Pop and Flame Patch printings are not shown (the first listed printings are used); his zone's next "
            "Energy is not shown and the game ended before his next turn: Water is used as a placeholder",
  ambiguous=[AMB_SL, AMB_MC,
             "The opponent's two coin-flip Item searches are named 'Silver Pad' in the review; no card of that name exists in the card "
             "database; Order Pad B4 145 (flip a coin, heads: a random Item from the deck) is used",
             "Opponent's Flame Patch in the discard: printing not shown; B1 217 used (B1 217 and B1 331 match)"],
  draws={1: []}, vpatch=_hp(30), ez_now='L', ez_next='W',
  notes="Global 12 = his 6th turn. Hand after global 10: Cyrus (the opponent's Copycat on global 13 draws one card to match his sole "
        "Cyrus); 'Global turn12': draws Lucky Ice Pop -> 2. Board: Dragonite 90 -> 10 (global 11 Spurt Fire, 100 - 20), Water+Water+"
        "Lightning, Helmet; Bench Hisuian Goodra 100 (Goomy under it). Opponent 'Global turn11': draw (8), Lucky Ice Pop x3 over two "
        "copies (tails discard, heads return, tails discard: 6), 'Silver Pad' x2 both heads (+1 -1 each: 6), bench second Slugma 70 (5), "
        "Fire to it, Flame Patch (4) returns the Fire Hyper Beam discarded to Magcargo (4 Fire; opponent's discard Energy empty), Ice Pops "
        "30 -> 90, Spurt Fire. His move in the review's order: Lightning to the benched Goodra (slot 1), Lucky Ice Pop (10 -> 30, tails; "
        "vpatch sets 30), Hyper Beam. Count check: global 13 (draw 5, Magcargo 4, Flame Patch 3, Copycat played with 2 left) is "
        "smaller than the review's word 'large hand' there; the count here follows the visible plays (convention 2)."),
]
