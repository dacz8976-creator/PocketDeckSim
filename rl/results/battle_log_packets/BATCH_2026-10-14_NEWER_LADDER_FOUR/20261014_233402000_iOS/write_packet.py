from pathlib import Path
import json,hashlib,datetime
p=Path(__file__).parent
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
review='''# Full battle review: 20261014_233402000_iOS.MP4

Reviewer: /root/evening_233402, continued by /root/newer_233402. Model: gpt-6.1-sol, high. Review date: 2026-10-15 UTC. Primary review is complete; independent acceptance is pending.

1st | Alolan Ninetales ex T4 | opp 1 pt

Source: 770900030 bytes, 418.038333 seconds, SHA-256 32390ef837ec4ebc65700bc78d18d13c63230da6b71c7c54fed3760b627b0dcd. Recording creation: 2026-10-14T23:34:02Z, or October 14 at 18:34 Central. Exact binding and original path are in SOURCE.json. One complete battle is recorded, including deck selection, setup, all ten global turns, terminal knockout, Defeat, and results table.

The owner is Dacz8976. Opponent display name: ヴィオレ魔ぬ (transcribed from the visible result screen; see native evidence for authoritative glyphs). Ranked Match, Season B4b SP, Ultra Ball Rank 4, owner 734 points, are readable at 3.0 seconds. Both introduction panels show Ultra Ball Rank 4. No Auto control is visible. Classify as a human ranked ladder battle under the project rule.

Deck 13-A is selected. The pregame deck panel at 2.018 seconds visibly identifies Alolan Vulpix (60 HP, Gnaw 20), Alolan Ninetales ex (150 HP, Binding Snow 80), Team Rocket's Rattata (40 HP, Ambush 20+), and Team Rocket's Raticate ex (120 HP, Thieving Incisors, Boost Dash 70). These are not Bibarel or Alolan Rattata. No Mega form is present. The entire 20-card list is not visible. Water is the owner's configured Energy. Opponent visible core is Zorua (60 HP, Ascension), Zoroark ex (150 HP, Brutal Bash 30 per benched Darkness Pokemon), Poipole (60 HP, 2-Step), Naganadel (100 HP, Poison Horn 40), and Nihilego (70 HP, More Poison/New Wave). Hidden cards and exact unseen copies remain unknown.

## Evidence method

The overview locates phases. Native 1170 x 2532 keyframes, approximately one second apart, provide denser action evidence; key_times.csv maps key_NNN.jpg to exact source time. sheets/key3_NN.jpg show every third native keyframe with correct timestamps; sheets/action_*.jpg provide dense action crops. Original native frames remain in evidence. Additional seek frames include 82.30, 332.50 and 417.70 seconds. All times below are source-local, rounded. No narrative model or simulator supplied the battle account.

## Complete timecoded timeline

| Source time | Turn or phase | Observed account and reconciled state |
| --- | --- | --- |
| 0:00-0:24 | Pregame | Share-code overlay closes, Deck 13-A is shown, ranked queue is entered, opponent is found, introduction and coin sequence play. The 2.018-second deck panel resolves the owner's evolutionary lines. |
| 0:25-0:36 | Setup | Owner explicitly goes first. Owner chooses Alolan Vulpix 60 as the sole opening Active. Opponent reveals Zorua 60 Active. Owner's opening visible cards include Team Rocket's Raticate ex, Poke Ball, Sightseer, Elegant Cape and the Vulpix used for setup. |
| 0:37-1:15 | Global 1, owner T1 | Draw makes Sabrina visible in hand. Poke Ball at 49 seconds supplies the second Alolan Vulpix, which is benched by 55 seconds. Sightseer is played around 60 seconds; its four-card view shows Copycat, Poke Ball, Alolan Ninetales ex and another Supporter. Owner takes Ninetales ex into hand. No Energy is generated for the first player on this turn, and no attack occurs. Both Actives remain 60. Score 0-0. |
| 1:16-2:02 | Global 2, opponent T1 | Opponent equips Deceptive Needle to Zorua at about 82 seconds. Poke Ball is played around 85 seconds and Poipole 60 is benched around 92-94 seconds. Darkness Energy is attached to Active Zorua by 98 seconds. Red Card is played around 100 seconds, replacing the owner's four-card hand with three; Poke Ball, Cyrus and Team Rocket's Raticate ex are then visible. At 111.987 seconds Zorua uses Ascension, evolving from the deck into Zoroark ex by 117 seconds. This is an attack-based evolution, not an ordinary turn-one hand evolution. Deceptive Needle triggers at 119 seconds and deals 10 to owner Vulpix, 60 to 50. Score remains 0-0. |
| 2:03-2:39 | Global 3, owner T2 | Owner draws Elegant Cape at about 125 seconds. Poke Ball around 128 seconds supplies Team Rocket's Rattata, benched at 134 seconds. Water Energy is attached to the benched Vulpix at 143-145 seconds. Elegant Cape is attached to that benched Vulpix around 148-151 seconds; its +30 HP effect awaits Stage 1 evolution. Owner passes without attack. Active Vulpix remains 50, opposing Zoroark ex 150 with one Darkness. Score 0-0. |
| 2:40-3:13 | Global 4, opponent T2 | Opponent evolves Poipole into Naganadel 100 at about 166 seconds, plays a draw Supporter around 169 seconds, and attaches Darkness to Naganadel by 182 seconds. Zoroark ex uses Brutal Bash at 187-189 seconds with one benched Darkness Pokemon: 30 damage, owner Vulpix 50 to 20. Deceptive Needle then deals another 10 at 191-193 seconds, leaving Vulpix 10. No knockout, score 0-0. |
| 3:14-3:50 | Global 5, owner T3 | Owner draws Alolan Ninetales ex. Team Rocket's Rattata evolves into Team Rocket's Raticate ex 120 at 200 seconds. The Thieving Incisors prompt is accepted around 203 seconds; the opposing Active's one Darkness Energy is moved to Raticate ex. Native key206 shows Raticate with that Energy and Zoroark with none. Benched Vulpix evolves into Ninetales ex around 218 seconds; Elegant Cape raises it from 150 to 180 max/current HP. Owner attaches Water to Active Vulpix at 224 seconds and uses Gnaw at 227 seconds, dealing 20 to Zoroark ex, 150 to 130. This is the owner's first attack, but it is a supporting Vulpix attack on owner T3, not the main-attacker metric. Score 0-0. |
| 3:51-4:53 | Global 6, opponent T3 and forced promotion | Opponent benches Zorua 60 by 236 seconds. Opponent waits during much of this turn, then restores a Darkness Energy to Active Zoroark ex. At 273.507 seconds Brutal Bash is declared with two benched Darkness Pokemon, enough for 60 against Vulpix's remaining 10 HP. Vulpix is knocked out and opponent gains one point at 279-280 seconds. Owner chooses the caped Ninetales ex for promotion at 283-287 seconds. Deceptive Needle resolves after the knockout/promotion at 290 seconds, reducing the newly Active Ninetales from 180 to 170. Raticate ex stays benched at 120 with one stolen Darkness; Ninetales has one Water. Score owner 0, opponent 1. |
| 4:54-5:11 | Global 7, owner T4 | Owner draws Field Blower, plays it around 297 seconds and removes opposing Active Zoroark's Deceptive Needle; the owner's Elegant Cape remains. Owner attaches a second Water to Ninetales at 304 seconds. At 307.758 seconds Binding Snow is declared and deals 80, opposing Zoroark ex 130 to 50. Its next-turn restriction on Energy Zone attachment to the opposing Active is displayed. This is MAIN Alolan Ninetales ex's first attack: owner T4, global turn 7, opponent already has 1 point. Score 0-1. |
| 5:12-5:41 | Global 8, opponent T4 | Despite Binding Snow, the existing Active Energy remains usable. Opponent attaches Darkness to benched Zorua at 320 seconds and evolves it to a second Zoroark ex 150 at 323 seconds. Nihilego 70 is benched around 327 seconds, filling the third slot. Its More Poison passive notification appears; no actual poison damage is seen. Another played card produces a displayed 'Retreat Cost is 1 more' effect around 333 seconds, but its exact name is not readable. At 339 seconds Active Zoroark uses Brutal Bash with three benched Darkness Pokemon for 90, Ninetales 170 to 80. The earlier Deceptive Needle is gone, so no extra 10 follows. Score remains 0-1. |
| 5:42-6:20 | Global 9, owner T5 | Owner draws Sabrina and attaches the turn's Water Energy to benched Raticate ex by 357 seconds, giving it the stolen Darkness plus Water. Cyrus and Sabrina remain unplayed in hand. Ninetales uses Binding Snow a second time around 362-365 seconds for 80, knocking out the damaged first Zoroark ex (50 remaining). Owner gains two points at 372 seconds. Opponent selects the already energized second Zoroark ex for promotion at 378 seconds. Score becomes owner 2, opponent 1. |
| 6:21-6:51 | Global 10, opponent T5 and terminal | Opponent promotes second Zoroark ex 150 with its existing Darkness. A Poke Ball around 388 seconds supplies Poipole 60, benched by 390 seconds to refill the third Darkness slot alongside Naganadel and Nihilego. A new Deceptive Needle is attached to this Active Zoroark at 393-396 seconds. At about 402 seconds Brutal Bash is declared, dealing 90 to Ninetales's remaining 80 and knocking it out by 405 seconds. The ex knockout supplies two points, taking opponent from 1 to 3 at 408 seconds. Raticate remains 120 on the bench; no promotion is needed after the terminal third point. Defeat appears at 411 seconds. This is an attack knockout loss, not a concession. |
| 6:52-6:58.038 | Result transition/table | Results table is readable at 417.70 seconds: Went first, Turns played 10, Your points 2, Opponent's points 3, Damage done 180. This independently reconciles Gnaw 20 plus Binding Snow 80 twice. Clip ends on that result, with no second match. |

## Decisions and mechanical observations

The owner uses the first turn to establish a second Vulpix and find Ninetales through Sightseer. Red Card removes that known Ninetales from the hand before the owner can evolve on T2. The next natural Ninetales draw arrives on owner T3. This is observed hand disruption, not proof that the deck lacked other access.

The Raticate evolution is useful disruption: Thieving Incisors takes the opponent's Active Energy and supplies Raticate. The opponent can replace that Energy on the next turn. The owner spends T3's Water on the low-HP Active Vulpix to gain 20 chip damage while the caped Ninetales waits with one Water. The sacrifice gives the opponent one point and exposes the promoted Ninetales to the remaining Deceptive Needle trigger. These state changes are source observations; they do not prove a superior line existed.

Field Blower preserves Elegant Cape while removing the first Deceptive Needle. Binding Snow blocks new Energy Zone attachment to the opposing Active, but does not remove existing Energy, prevent a benched attachment, or prevent a benched energized attacker from being promoted. The opponent uses those openings to prepare the second Zoroark. The full bench raises Brutal Bash from 30 to 60 to 90, with the late third slot refilled before the final attack.

Owner T5 has Ninetales at 80 HP, opposing Active Zoroark at 50 HP, an energized second Zoroark already benched, Cyrus and Sabrina visible in hand, and Raticate with one Darkness before the turn's Water attachment. The owner takes the two-point knockout with Binding Snow and leaves Ninetales exposed to the replacement attacker. A different switch or attack line cannot be certified as winning from this footage: the displayed retreat-cost increase matters, opponent choices/hidden cards are unknown, and neither visible Supporter is actually used. No simulator prediction is substituted for source evidence.

## Limits

See UNCERTAINTIES.json. The full battle and outcome are established. The exact name of the late retreat-increasing card, one early Sightseer-revealed Supporter, and the opponent's early draw Supporter remain uncertain. No unseen deck slots, hidden Energy sources, or unshown cards are reconstructed. Independent checker and lead acceptance remain required before completion registration or archival. No shared index, event, external artifact or source file was changed by this worker.
'''
(p/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Coverage checklist

Source identity: SOURCE.json, matching assigned hash. One match. All supplied phases reviewed. Reviewer /root/evening_233402 continued by /root/newer_233402, gpt-6.1-sol/high. Independent acceptance pending.

| Phase / global turn | Source seconds | Coverage and evidence |
| --- | --- | --- |
| Pregame and deck | 0-24 | Complete; native key003 deck, key004 ranked screen, key022-024 introduction/coin. |
| Setup | 25-36 | Complete; key028 first-player notice, key031 opening placement, key034 reveal. |
| Global1 ownerT1 | 37-75 | Complete; key037-076, key3_02; Poke Ball, bench, Sightseer and pass. |
| Global2 opponentT1 | 76-122 | Complete; key076-122; tool, Poke Ball, Poipole, Red Card, Energy, Ascension/evolution, extra10. Dense action_a1/a2. |
| Global3 ownerT2 | 123-159 | Complete; key124-160; Cape draw/equip, Poke Ball/Rattata, Water to bench, pass. |
| Global4 opponentT2 | 160-193 | Complete; key160-193; Naganadel, draw Supporter, Energy,30+10. Dense action_b1/b2. |
| Global5 ownerT3 | 194-230 | Complete; key193-229; Ninetales draw, Raticate evolution and accepted Thieving Incisors, Ninetales/Cape, active Water, Gnaw20. Native key206 confirms stolen Energy. |
| Global6 opponentT3 + promotion | 231-293 | Complete; key229-292; Zorua, replacement Energy, waiting, Brutal Bash KO,1point, forced Ninetales promotion and Deceptive Needle10. Dense action_c1. |
| Global7 ownerT4 | 294-311 | Complete; key292-310; Field Blower, secondWater, firstBinding80 and restriction. Dense action_d1, exact307.758s declaration. |
| Global8 opponentT4 | 312-341 | Complete; key311-339; benchEnergy, secondZoroark, Nihilego, passive/effect notifications,90attack. Dense action_d2-d4. |
| Global9 ownerT5 | 342-380 | Complete; key340-380; Sabrina draw, Water toRaticate, secondBinding80/KO,2points and opponent promotion. |
| Global10 opponentT5 | 381-411 | Complete; key379-409; PokeBall/Poipole, tool, final90KO, opponent3points, Defeat. Dense action_e1/e2. |
| Results and file end | 412-418.038333 | Complete; key410 onward plus native t0417.70.jpg with result,10turns,2-3,180damage. No second battle. |

Overview is a navigation aid. The turn account uses dense native evidence and before/after HP, Energy and score transitions. No turn remains unreviewed. A fixed grid alone was not used to establish actions. The independent checker must still verify selected ordinary turns and decisive sequences before lead acceptance.
'''
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
summary={
 'source_filename':source['video_basename'],'source_sha256':source['sha256'],'source_bytes':source['bytes'],'source_duration_seconds':source['duration_seconds'],
 'source_creation_utc':source['source_creation_utc'],'match_date_local':'2026-10-14','reviewer':'/root/evening_233402','continued_by':'/root/newer_233402','model':'gpt-6.1-sol','reasoning_effort':'high',
 'scope':'Entire supplied recording, all ten global turns through result table','primary_review_complete':True,'independently_accepted':False,'battle_complete':True,'match_count':1,
 'mode':'ranked ladder','queue_evidence':'Ranked Match, Season B4b SP, Ultra Ball Rank 4, owner734pts visible at3.018s','auto_option_seen':False,'auto_enabled_observed':False,
 'owner':'Dacz8976','opponent':'ヴィオレ魔ぬ','opponent_name_evidence':'evidence/t0417.70.jpg','opponent_core':['Zorua','Zoroark ex','Poipole','Naganadel','Nihilego'],
 'deck_name':'Deck 13-A','deck_core':['Alolan Vulpix','Alolan Ninetales ex','Team Rocket\'s Rattata','Team Rocket\'s Raticate ex'],'full_deck_known':False,
 'result':'loss','result_method':'Final Brutal Bash attack knockout of Alolan Ninetales ex','concession':False,'owner_points':2,'opponent_points':3,'score':'2-3','result_timestamp_seconds':417.7,'global_turns':10,'damage_done_result_table':180,
 'went_first':True,'main_attacker':'Alolan Ninetales ex','first_main_attack':{'attack':'Binding Snow','own_turn':4,'global_turn':7,'timestamp_seconds':307.758,'opponent_points_before':1,'damage':80},
 'supporting_earlier_attacks':[{'attacker':'Alolan Vulpix','attack':'Gnaw','own_turn':3,'global_turn':5,'timestamp_seconds':227.5,'damage':20,'opponent_points_before':0}],
 'exact_three_item_note_prefix':'1st | Alolan Ninetales ex T4 | opp 1 pt','external_log_eligible':True,'external_log_written':False,
 'decisive_evidence':['evidence/key_003.jpg','evidence/key_028.jpg','evidence/key_206.jpg','evidence/key_306.jpg','evidence/key_397.jpg','evidence/key_406.jpg','evidence/key_409.jpg','evidence/t0417.70.jpg']}
(p/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
unc={'source_filename':source['video_basename'],'source_sha256':source['sha256'],'unreviewed_intervals':[],'outcome_uncertain':False,'items':[
 {'time_seconds':[64,68],'detail':'One of Sightseer\'s four revealed cards is a Supporter whose name is not resolved; Ninetales selection is clear. No unobserved decklist slots are inferred.'},
 {'time_seconds':[168,174],'detail':'Opponent plays an early draw Supporter; exact name is not resolved. Subsequent hand/board and attack are reviewed.'},
 {'time_seconds':[330,336],'detail':'A card play/effect displays Retreat Cost is 1 more. Exact source card name is unresolved; no claim of a legal alternate winning retreat line.'},
 {'time_seconds':[0,418.038333],'detail':'Hidden opponent hand/deck and unshown owner deck slots/versions are unknown. Opponent display-name glyphs should be copied from native result image if exact typography is required.'},
 {'time_seconds':[82,332.5],'detail':'Deceptive Needle name is confirmed from the rotated native discard crop. No full text transcription or external rules claim is made; its observed10damage triggers are source-bound.'}],
 'acceptance_limit':'Primary review only; independent checker and lead acceptance pending.'}
(p/'UNCERTAINTIES.json').write_text(json.dumps(unc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Discard only obsolete worker-generated derivative sets with initially incomplete labels.
for f in (p/'sheets').glob('key_[0-9]*.jpg'):f.unlink()
for f in (p/'sheets').glob('seq_*.jpg'):f.unlink()
for f in (p/'evidence').glob('seq_*.jpg'):f.unlink()
files={}
for name in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','key_times.csv']:
    files[name]=hashlib.sha256((p/name).read_bytes()).hexdigest()
for dirname in ['evidence','overview','sheets']:
    for f in sorted((p/dirname).glob('*')):
        if f.is_file():files[f.relative_to(p).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'source_filename':source['video_basename'],'source_sha256':source['sha256'],'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'primary_packet_immutable':True,'independent_acceptance_pending':True}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
bad=[n for n,h in files.items() if hashlib.sha256((p/n).read_bytes()).hexdigest()!=h]
assert not bad,bad
print(json.dumps({'frozen_files':len(files),'hash_verification':'PASS','score':summary['score'],'prefix':summary['exact_three_item_note_prefix']}))
