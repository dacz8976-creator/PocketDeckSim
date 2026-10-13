#!/usr/bin/env python3
"""make_table.py: POSITION_TABLE.md, one row per position: his line, km3's free-run modal plan, km3 step by step along his line, and a short reading.
usage: make_table.py (run in the folder)"""
import json, os

pos = {p['id']: p for p in json.load(open('positions_all.json', encoding='utf-8'))}
summ = {s['id']: s for s in json.load(open('km3_summary.json', encoding='utf-8'))}
forced = {s['id']: s for s in json.load(open('runs_forced/forced_summary.json', encoding='utf-8'))}
meta = json.load(open('games_meta.json', encoding='utf-8'))
LISTROW = {r['position_id']: ('' if r['switch2_flag'] == 'no' else r['switch2_flag']) for r in json.load(open('position_list.json', encoding='utf-8'))}

# the reading of the positions where km3 and he part for a reason that is not a tie or an order (written by hand after reading the positions, the ledgers and the reviews)
READING = {
    '010837000-t03': "He evolves Glimmora, puts the Energy on Pawniard and retreats it (paying that Energy). Pawniard's Slash (30) would have knocked out the 30-HP Pichu on the opponent's Active: a point on turn 3. km3 attacks with Slash in 4 of 12 seeds and plays Copycat first in the other 8 (its plan is cut there); it scores his retreat 10,600 below its best. The cost of the knock-out would have been small: the opponent put its Mega Kangaskhan ex Active by retreating Pichu for free and knocked out Glimmora anyway. Looks like a miss.",
    '010837000-t05': "Muk before or after benching Glimmet is a tie. The Energy: he puts it on the benched Pawniard (it becomes Kingambit next turn), km3 on the Active Regigigas (150 HP, which can attack once Muk shuts off Seal of Antiquity, but needs three Energy).",
    '010837000-t07': "Both Rare Candy Kingambit. He puts the Energy on Glimmet (his next Active), km3 on Kingambit, which would then hold the 2 Energy Overlord's Blade needs (the Blade is 100 here: 1 Pokémon of his knocked out). A bait-and-feed plan against a build-up plan; km3's score gap is small (658).",
    '010837000-t09': "He heals Glimmet with two Lucky Ice Pops and attacks for 20 (Hang Down); km3 retreats Glimmet and attacks with Kingambit's Overlord's Blade. The runner now carries the count (2 of his Pokémon knocked out): the Blade is 140, not a knock-out of the 180-HP Mega Kangaskhan ex. km3's gap grew from 340 to 787 with the real damage.",
    '010837000-t11': "The clearest disagreement, and the count changes nothing here. The Active is Pichu (30 HP, nothing reduces damage). He plays Heavy Helmet and attacks with Glimmet's Hang Down (20), leaving Pichu at 10. km3 retreats Glimmet and knocks Pichu out with Kingambit's Overlord's Blade (Kingambit already holds the 2 Energy; 60 would already do it, 140 with the count of 2): a point. km3 scores his line 9,200 below its own. His reason may be the next turns (Glimmet was knocked out on the opponent's turn, which raised the Blade to 180 for turn 13).",
    '010837000-t13': "Both attack with the Blade. With the count (3) km3 now sees 180 and the knock-out of Raticate ex (2 points); in the first read it saw 60. He puts the third Energy on the Active, km3 on the benched Muk.",
    '010837000-t15': "The opponent did not come back; no plan of his. km3: the Blade alone (180 with 3 knocked out = Mega Kangaskhan ex's 180 HP, a winning knock-out at 2-2); in the first read it attached first because the Blade counted 60.",
    '010003000-t01': "He uses Mesagoza (a free coin flip) before Professor's Research, km3 plays Research first; the flip does not depend on the order. Same turn.",
    '010003000-t03': "He evolves and attacks and keeps Heavy Helmet in hand; km3 puts it on Regigigas first. Same turn, an earlier Tool.",
    '010003000-t07': "Glimmora has 20 HP. km3 plays Lucky Ice Pops first (each heads returns the Pop; up to four in a row), he does not and attacks; Glimmora is then knocked out (the opponent got no point: Shattering Crystal, heads). To get above the 70 she needed three Pops, so two heads in a row (1 in 4).",
    '010003000-t11': "He was about to attack with Regigigas (the opponent conceded as the attack menu opened); km3 attacks at once with Giga Turbo. Same turn.",
    '014423000-t01': "Opening: Poké Ball, Copycat or Research first; km3's scores are 114, 180 and 467 (a weak preference for Copycat; Poké Ball in 5 of 12 seeds).",
    '014423000-t03': "He puts the Energy on the benched Pawniard; this is also km3's top choice in seed 1 (8 of 12 seeds go to the Active). The Active, Grimer, is knocked out next turn.",
    '014423000-t05': "Helmet on Regigigas and Copycat as he did. The Energy goes to the Active Regigigas (which cannot attack) in km3's plans, and to the new Glimmet in his.",
    '014423000-t07': "He evolves Glimmora and puts the Energy on the benched Pawniard; km3 puts it on the Active Regigigas (50 HP, no way to attack), which Dedenne ex's 100 damage knocks out on the next turn. He looks right.",
    '014423000-t09': "Both use Venomous Hit. He attaches first; km3 attacks without attaching (all its options tie in a lost position).",
    '015011000-t01': "Opening: Poké Ball first in 9 of 12 seeds.",
    '015011000-t03': "The opponent did not come back; no plan of his.",
    '015659000-t01': "Same opening.",
    '015659000-t03': "Evolution, Lucky Ice Pop, Energy: the same cards, km3 starts with the Pop (tie).",
    '015659000-t05': "He evolves Glimmora, benches Pawniard and puts the Energy on Pawniard; km3 puts it on the Active Regigigas (30 HP, a Fighting weakness against Mega Lucario ex's 90), which is knocked out next turn. He looks right.",
    '015659000-t07': "Same plan.",
    '015659000-t09': "Same first move (Poké Ball).",
    '015659000-t13': "He conceded this turn (0-2, 10-HP Pokémon, Mega Lucario ex benched); km3 starts with Research as he did.",
    '020824000-t01': "Same opening.",
    '020824000-t03': "He evolves Glimmora and Alolan Muk (Power of Alchemy switches off Shuckle ex's Solid Shell and Ogerpon ex's Soothing Wind, which stopped the Poison last turn) and attacks; km3 benches Pawniard first and plays the same turn.",
    '020824000-t05': "Same first move (Research).",
    '020824000-t07': "He benches Regigigas, uses Mesagoza (tails), attaches to Glimmet and retreats it into Regigigas without attacking. km3 attaches, uses Mesagoza, and, in 9 of 12 seeds, the flip brings a Glimmora: it evolves and attacks with Venomous Hit. His flip was tails.",
    '020824000-t09': "He only attaches. km3 attaches and uses the Stadium (Fragrant Forest), which finds a random Grass Basic: his deck has none, so it does nothing.",
    '020824000-t11': "He plays a Lucky Ice Pop (tails), then Ilima to put the damaged Regigigas back in his hand, benches it at full 150 HP and retreats into it. km3 does not use Ilima (it ranks it 270 points below its Lucky Ice Pop chain). Looks like a good idea of his that km3 misses.",
    # ---- the eight games added later (v2: the deck lists of 010706, 203719 and 030351 are built from the filmed QR and the live log snapshot, which agree, so all 92 positions are on verified lists)
    '010706000-t09': "He uses Mesagoza (tails) before attaching and attacking with Giga Turbo (100 on Mega Diancie ex); km3 attaches and attacks at once. Same turn.",
    '010706000-t11': "Heavy Helmet goes on the benched Kingambit in his line, on the Active Muk in km3's (small gap).",
    '010706000-t21': "He wins the game here: Overlord's Blade after three of his Pokémon were knocked out is 180 (+20 weakness) on a 130-HP Mega Gardevoir ex, 3 points, 3-2. km3 plays the same two steps in 12 of 12 seeds, and now the game ends there (in the first read the runner's count was 0: the Blade did 80, no win, the turn went on).",
    '203719000-t11': "Heavy Helmet goes on the benched Kingambit in his line, on the 10-HP Active Regigigas in km3's; the Energy on Glimmora (his) or Kingambit (km3). The opponent's Active Drampa is Poisoned (now represented). Small gap (21).",
    '203719000-t07': "Rare Candy Kingambit, then Ilima puts his 10-HP Regigigas back in his hand to bench it at 150. km3 finds the same Ilima reset in 12 of 12 seeds; it then promotes Kingambit and uses the Blade, he promoted Glimmora (his plan's last step, Giga Turbo, is a converter slip: the converter does not follow Ilima's promotion; the review says Glimmora's Venomous Hit).",
    '203719000-t15': "Evolve, three Lucky Ice Pops, Energy on Kingambit, Venomous Hit; km3 starts with the Pops (up to four).",
    '203719000-t17': "NEW with the knock-out count. Glimmora has 10 HP: he heals it with Pops (tails, heads, tails), puts the Energy on the benched Glimmora and attacks with Venomous Hit (30 on Drampa, 100 to 70, Poison to 60). km3 attaches, plays Pops, retreats into Kingambit and uses the Blade: with 1 of his Pokémon knocked out the Blade is exactly 100, the 100 HP of the opponent's Active Drampa, so a knock-out and a point (1-1 to 2-1). km3 scores his line 9,900 below. In the first read the Blade counted 60 and the gap was 40. Glimmora was knocked out on the opponent's next turn (its 2nd point). The ledger's damage trail on that Drampa (100, 70, 60 after his turn, 50, then 20 and 10 on turn 19) confirms its 100 HP; an exact knock-out, so it depends on nothing else reducing the damage.",
    '210041000-t14': "He conceded here (0-2), no plan of his. km3's plan changed from the first read (retreat and attach, now attach and Slash; every score is near -11,000, a lost position). Two things are new in this position: the opponent's Active Riolu is Poisoned and 3 of his Pokémon are knocked out. I did not trace which one moved the plan; no weight.",
    '210041000-t06': "Mega Lucario ex (Fighting Pulse 90, Regigigas weak to Fighting) faces his 40-HP Regigigas. He puts the Energy on Pawniard and ends the turn (the game warns that a Supporter can still be played; he confirms). km3 plays Ilima in 12 of 12 seeds (Regigigas back in hand, fresh at 150 HP, Pawniard Active, Slash). Regigigas was knocked out next turn (0-1). The scores tie, so not clearly a mistake; a chance he left unused.",
    '210041000-t14': "He conceded here (0-2).",
    '210823000-t02': "His turn 1: Research first (draw 2); km3 plays Copycat first (the opponent holds 5 cards: draw 5; 877 higher). Unchanged from the first read: a hand-quality judgement, no condition or count involved.",
    '210823000-t08': "Ilima resets his 50-HP Regigigas (both). He then attacks with Glimmora's Venomous Hit (the plan's 'Giga Turbo' is the same converter slip); km3 promotes Kingambit and uses the Blade (60: none of his Pokémon knocked out yet, so the count changes nothing).",
    '210823000-t12': "The opponent conceded as he found his deck empty; no plan of his.",
    '225319000-t04': "He puts Heavy Helmet on Pawniard (Retreat Cost 1, below the Helmet's 3, so it does nothing until it becomes Kingambit) and uses Copycat. km3 starts with Mesagoza's coin flip in 8 of 12 seeds and with Copycat in 3.",
    '225319000-t06': "He attaches to Pawniard and retreats it, paying with that Energy (the zone Energy as a free retreat); km3 attaches and attacks with Slash. Same habit as 010837 t03.",
    '230258000-t09': "Mesagoza, Grimer, Rare Candy Kingambit, then Lucky Ice Pops; km3 plays the Pops first. Order.",
    '022530000-t09': "He uses Rainbow Cave (a fresh Fighting) and Dragonair's Dragon's Blessing (one more Energy for Haxorus from the discard) before Frenzied Blade; km3 attaches once and attacks, using neither.",
    '030351000-t03': "His Active Dratini is Asleep (now represented). He evolves it to Dragonair, which cures the Sleep, uses Rainbow Cave and attaches. km3 also evolves, before Research (the two tie at that step); in the first read it used the Stadium instead.",
    '030351000-t05': "His Dragonair (20 HP) is Asleep, and Darkrai's Bad Dreams (20) knocks it out at the checkup: the Sleep is now represented and km3 sees it. It plays Dragon's Blessing before the Energy attach (a tie) and its plan runs on into the checkup (promotion). The gap of 8,600 in the first read, when km3 attacked with Draconic Whip, is gone.",
    '030351000-t07': "His Haxorus is Asleep (now represented; it cannot attack). He heals it with a Pop, uses Rainbow Cave and Dragon's Blessing; km3 plays the Pop twice before the Blessing (9 of 12 seeds), gap 70. Order.",
    '030351000-t13': "His Druddigon is Asleep (no retreat, no attack; now represented) and Bad Dreams knocks it out at the checkup (opponent's 2nd point). His line starts with Professor's Research, so the compared part is one step: km3 plays Research too, 12 of 12. The gap of 10,100 in the first read (km3 retreated and attacked) was the missing Sleep.",
    '030351000-t15': "Could not be run in the first read (the deck count was off by 4 cards; the knocked-out Dragonair and Druddigon were missing from the discard, now restored). He uses Dragon's Blessing on the Active Haxorus, retreats paying with it, Iris, and Frenzied Blade for the knock-out of Igglybuff (2 points). km3 plays Retreat, Iris and Frenzied Blade as he did and the Blessing too, but starts with the Energy attach; the score of his first step (the Blessing) is 10,030 below (-18,763 v -8,733). Same cards, different order; I did not trace the size of the score gap.",
    '020824000-t13': "Lucky Ice Pops and an Energy on Regigigas; km3 adds the useless Fragrant Forest use and plays up to seven Pops in a row.",
}

lines = [f'# The {len(pos)} positions (v2): his line, km3, and a short reading', '',
         '`first`: in how many of 12 seeds km3\'s first move is his. `line`: km3 step by step along his line (his plan cut at its first draw card): the first step where km3 would play something else in most seeds, with the gap between km3\'s best score and the score of his step (seed 1; scores are km3\'s own evaluation, a very negative number means km3 thinks the game is lost, ties at the top are common there). Switch 2: the position holds a card the rules switch changed.', '',
         '| position | game turn, points | his plan | km3 modal plan (12 seeds) | first | line | switch 2 | reading |', '|---|---|---|---|---|---|---|---|']
for pid, p in pos.items():
    s = summ.get(pid, {})
    f = forced.get(pid, {})
    dev = f.get('first_deviation')
    if not p['his_plan']:
        line = 'no plan of his'
    elif dev is None:
        line = 'km3 plays all of it'
    else:
        top = max(dev['km3_plays'].items(), key=lambda x: x[1])[0]
        gap = dev.get('gap_seed1')
        line = f"step {dev['step'] + 1} ({dev['his']}): km3 plays {top}" + (f", gap {gap:,.0f}" if gap is not None else '')
    short = pid.split('_', 1)[1]
    sw = LISTROW.get(pid, '')
    lines.append(f"| {short} | {p['turn_count']}, {p['points'][0]}-{p['points'][1]} | {' > '.join(p['his_plan']) or '-'} | {' > '.join(s.get('modal', [])) or '-'} | {s.get('same_first', '-')}/12 | {line} | {sw} | {READING.get(short, '')} |")
open('POSITION_TABLE.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(len(pos), 'rows;', sum(1 for pid in pos if pid.split('_', 1)[1] in READING), 'with a reading')
