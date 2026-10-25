from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_221937000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'
CL = 'Claydol A3a 031'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent (printings by convention 3: the first cards.py lists among those matching what the review shows)
IG = 'Igglybuff A4a 059'; EV = 'Eevee B1 184'; DK = 'Darkrai B2b 040'; ES = 'Espeon B3a 020'; SW = 'Swablu A4a 064'
oPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR = "the opponent's Professor's Research printing is not shown; the first-listed printing (A4b 373) is used"
AM_IG = 'Opponent Igglybuff printing: A4a 059 is the only one listed (HP 30, Sleepy Lullaby)'
AM_EV = 'Opponent Eevee printing chosen by HP (50) and Ability title (Boosted Evolution); B1 184, P-B 011 and P-B 054 match'
AM_DK = 'Opponent Darkrai printing: B2b 040 is the only one with HP 100 and Bad Dreams'
AM_ES = 'Opponent Espeon printing: B3a 020 is the only one with HP 90 and Hypnoblast'
AM_SW = 'Opponent Swablu printing chosen by name and HP (50) only (no attack shown); A4a 064, B1 196, B3a 061, B3a 102 and P-B 017 match'
AM_TR = "Opponent's discarded Professor's Research: printing not shown; A4b 373 listed"


def wallace_ms(v):
    # the review: Wallace put Mega Sharpedo ex onto the Active Carvanha (20 HP left), keeping its 30 damage: 190 - 30 = 160
    v['me']['board'][0] = B(MS, 160, behind=[CV])


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[WA, CC, PR, HH, CV], disc=[], dene='', board=[B(CV, 20)], ko=0),
  dict(hand_count=4, disc=[oPR], dene='', board=[B(IG, 30), B(EV, 50), B(DK, 100)], ko=0),
  ['Place:Carvanha@1', 'Play:Wallace', 'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Water}', 'Attach:1Water@0 zone', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'],
  D, None,
  approx=AP + "; " + TR,
  ambiguous=[AM_IG, AM_EV, AM_DK, AM_TR],
  draws={1: []}, vpatch=wallace_ms,
  notes="Global 2 = his 1st turn (he went second). Review 'Deck and opening': opening five Carvanha, Wallace, Copycat, Professor's "
        "Research, Heavy Helmet; Carvanha Active (50), no Bench -> 4 in hand; opponent Igglybuff 30 Active, Eevee 50 Benched (3 in "
        "hand). Row '1 / opponent 1' 37-64s: draw (3->4), Darkrai benched (3), Professor's Research (4), Sleepy Lullaby 10 + Bad "
        "Dreams 20 -> Carvanha 20, sleep check heads (awake). Row '2 / owner 1' 64-97s: draws Carvanha (66s) -> 5. His move in time "
        "order: bench Carvanha 68-69s (slot 1), Wallace 70-73s on the Active Carvanha, Mega Sharpedo ex revealed and evolved 74-76s "
        "(160/190), Water to the Active 77-79s, Turbo Shark 82-84s (KO Igglybuff), its zone Water to the Benched Carvanha 85-87s. "
        "Variant: Wallace's random evolution is set by vpatch (Active Mega Sharpedo ex 160 over Carvanha)."),
P(G, 4, 2, [1, 0],
  dict(hand=[CC, PR, HH, CL], disc=[WA], dene='', board=[B(MS, 100, 'W', behind=[CV]), B(CV, 50, 'W')], ko=0),
  dict(hand_count=3, disc=[oPR, IG], dene='', board=[B(ES, 90, 'P', behind=[EV]), B(DK, 100), B(SW, 50)], ko=1),
  ["Play:Professor's Research", 'Place:Wailmer@2', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@2', 'Attach:1Water@2 zone',
   'Attack:Turbo Shark', 'Attach:1Water@2 fx'],
  D, None,
  approx=AP + "; " + TR,
  ambiguous=[AM_EV, AM_DK, AM_ES, AM_SW, AM_TR],
  draws={0: [WM, WM]},
  notes="Global 4 = his 2nd turn. His hand after global 2: Copycat, Professor's Research, Heavy Helmet; row '4 / owner 2' 129-160s "
        "draws Claydol (131s) -> 4. Discard Wallace. Board: Mega Sharpedo ex 160 - Hypnoblast 40 - Bad Dreams 20 = 100, one Water, "
        "awake (sleep check heads 127s); Benched Carvanha 50 one Water. Score 1-0 (Igglybuff KO). Opponent row '3 / opponent 2' "
        "97-130s: Eevee promoted after the KO; draw (4->5), Psychic to Eevee, Eevee -> Espeon 90 (4), Swablu benched (3), Hypnoblast. "
        "His move in time order: Research 134-136s (Wailmer, Wailmer), bench one Wailmer 140-142s (slot 2), Heavy Helmet on it "
        "144-148s, Water to it 149-151s, Turbo Shark 154-157s (Espeon 90->20), its zone Water to Wailmer (2 Water by native 170s)."),
]
