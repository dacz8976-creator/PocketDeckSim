"""Root-authored source-qualified log notes, to save only after accepted review."""
from pathlib import Path
import json
b=Path(__file__).resolve().parent
records={
 '20261010_012303000_iOS':('win','first','Mega Absol ex / Nihilego / Zorua',
  'Opponent: ナチョス. Win3-2; went first;11 turns. Bedrock Breaker deals120 including Arena of Antiquity, knocking out Mega Absol ex at375s; third point388s and Victory390s. Turn5 Poké Ball visibly has no target. Turn9 ends without attacking after a visible attack-available warning. Exact20-card Fighting Conkeldurr / Garganacl list is bound to the filmed QR and continuous deck-to-game footage.'),
 '20261010_015821000_iOS':('conc','first','Frigibax / Baxcalibur / Suicune ex',
  'Opponent: よこっぴ. Concession win1-0; went first;6 turns;120 attack damage. Deluxe Pack: Mega Emblem Event is visible. Opponent conceded banner242s and Victory253s. Horsea Hook30 plus Poison/Burn knocks out Frigibax; Kingdra Stormy Prison90 leaves Suicune ex70HP. No Ice Maker or attack is observed on the final opponent turn. Exact20-card Water Kingdra ex / Team Rocket’s Weezing ex list is bound to the filmed QR and continuous deck-to-game footage.'),
 '20261010_020258000_iOS':('conc','second',"Team Rocket's Raticate ex / Team Rocket's Tinkaton / Lechonk",
  'Opponent: Pikachu. Concession win; last score2-1; went second;8 turns. Opponent conceded banner330s and Victory340-342s. Thieving Incisors transfers Water from Horsea to Raticate. Turn6 Poké Ball visibly has no target; Stormy Prison knocks out Raticate for2 points. Final Sabrina attempt ends in concession before a replacement is chosen. Exact20-card Water Kingdra ex / Team Rocket’s Weezing ex list is bound to the filmed QR and continuous deck-to-game footage.'),
 '20261010_020908000_iOS':('win','second',"Nihilego / Team Rocket's Magmar / Team Rocket's Koffing / Lapras",
  'Opponent: Desk. Win1-0; went second;7 turns;140 attack damage. Deluxe Pack: Mega Emblem Event is visible. At378s the notice says Your opponent did not return within the allowed time; Victory and final statistics388.8s confirm the win. Termination cause and intent are unknown; no explicit concession was observed. Opponent confused Magmar attack visibly did nothing, then Kingdra Stormy Prison110 including weakness knocked out Magmar. Both players had a visible no-target Poké Ball. Exact20-card Water Kingdra ex / Team Rocket’s Weezing ex list is bound to the filmed QR and continuous deck-to-game footage.'),
 '20261010_021629000_iOS':('loss','second','Snorlax ex / Indeedee ex',
  'Opponent: けい. Loss0-3; went second;25 turns;840 attack damage confirmed on Defeat results892s. Two Indeedee ex, Snorlax Full-Mouth Manner, Soothing Shore and Lucky Ice Pop repeatedly heal; Heavy Helmet reduces damage. Owner records no opposing knockout. Kingdra knockouts on turns23 and25 give the opponent2 then terminal3 points. Retreat payments and separate benched Water attachments on turns20/22 are source-verified. Research on turn18 draws exactly one remaining card; later empty-deck notices are preserved. Exact20-card Water Kingdra ex / Team Rocket’s Weezing ex list is bound to the filmed QR and continuous deck-to-game footage. The recorded network wait on turn17 does not establish hidden actions or intent. Turn4 has no clear unzoomed six-card start fan.'),
}
for stem,(result,order,opponent,detail) in records.items():
 p=b/stem
 game_id=json.loads((p/'PAUSE_GAME.json').read_text(encoding='utf-8-sig'))['game_id']
 note=f'Source: {stem}.MP4. Game1 of1; game ID: {game_id}. {detail} Full independently accepted review and opening, hand, draw, turn and board evidence: Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES/{stem}/ (REVIEW.md, TURN_LEDGER.json, TURN_EVIDENCE.json, DECK_USED.json, PAUSE_GAME.json). Times are source-local seconds. Hidden opponent cards and unshown discard contents remain unknown; artwork and rarity are unverified. Owner ratings were not supplied.'
 (p/'LIVE_NOTE.txt').write_text(note,encoding='utf-8')
 (p/'LIVE_FORM.json').write_text(json.dumps({'source':stem+'.MP4','date':'2026-10-09','deck':'filmed-qr-bc8737d983eb' if stem.endswith('012303000_iOS') else 'filmed-qr-b649812c0d42','result':result,'order':order,'opponent_core':opponent,'note':note},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
