"""Root's source observations; add configuration only after actual inspection."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
B=ROOT/'Recording_QA/BATCH_2026-10-14_NEW_LADDER_FOUR'
CONFIG={
 '20261014_153139000_iOS':{
    'section':'d12','deck_name':'Ariados / Whimsicott / Ogerpon','energy':'Grass',
    'opponent':'Chacho','opponent_deck':'Magnemite / Magneton / Magnezone','result':'loss',
    'note_prefix':'1st | Whimsicott ex T4 (missed) | opp 0 pts',
    'note':'1st | Whimsicott ex T4 (missed) | opp 0 pts | vs Chacho | recorded 2026-10-14 10:31:39 CDT | 20261014_153139000_iOS.MP4 | Grass Knot T4 failed confusion; first landed T5. Defeat1-3 at07:00.9.',
    'scope':'Whole one-game ranked ladder source; all12turns and terminal defeat; failed first main attack explicitly qualified; independent source checks and root acceptance',
    'registration_notes':'Independent source checker and root accepted. Deck12 loss1-3 versus Chacho; first; Whimsicott ex declared first Grass Knot ownT4/global7 with opponent0, but confusion tails caused no effect. First landed ownT5/global9. Hidden cards stay uncertain. External save/readback is separate.',
    'observations':[
      ('evidence/t0003.00.jpg','Ranked Match and Deck12 selected.'),
      ('evidence/t0238.00.jpg','Whimsicott ex Active; Grass Knot selected; opponent Chacho has0points before the first declared main attack.'),
      ('evidence/t0245.00.jpg','The attack did nothing following confusion tails; opponent remains0points. First attack attempt is explicitly qualified as missed.'),
      ('evidence/t0420.90.jpg','Defeat versus Chacho; went first;12turns;owner1/opponent3;260damage.'),
    ]},
 '20261014_153908000_iOS':{
    'section':'d12','deck_name':'Ariados / Whimsicott / Ogerpon','energy':'Grass',
    'opponent':'V1PER','opponent_deck':'Indeedee ex / Bulbasaur / Ivysaur / Mega Venusaur ex','result':'win',
    'primary_note_prefix':'second | Whimsicott ex first attack T2 | opponent points BEFORE: 0',
    'note_prefix':'2nd | Whimsicott ex T2 | opp 0 pts',
    'note':'2nd | Whimsicott ex T2 | opp 0 pts | vs V1PER | recorded 2026-10-14 10:39:08 CDT | 20261014_153908000_iOS.MP4 | Victory3-0 at04:17.37; Grass Knot170 KO Mega Venusaur ex at04:00.',
    'scope':'Whole one-game ranked ladder source; all8turns and terminal victory; independent source checks and root acceptance',
    'registration_notes':'Independent source checker and root accepted. Deck12 victory3-0 versus V1PER; second; Whimsicott ex first Grass Knot ownT2/global4 with opponent0 before. Supporting CottoneeT1 stays separate. Note prefix shortened without changing facts. External save/readback is separate.',
    'observations':[
      ('evidence/t0003.00.jpg','Ranked Match and Deck12 selected.'),
      ('evidence/t0136.00.jpg','Whimsicott ex Grass Knot130 selected before first main attack; opponent V1PER has0points.'),
      ('evidence/t0138.00.jpg','Named Whimsicott ex Grass Knot attack animation.'),
      ('evidence/t0257.37.jpg','Victory versus V1PER; went second;8turns;owner3/opponent0;490damage.'),
    ]},
 '20261014_143111000_iOS':{
    'section':'d12','deck_name':'Ariados / Whimsicott / Ogerpon','energy':'Grass',
    'opponent':'Ghezzuka','opponent_deck':'Mega Swampert ex / Mantyke / Cramorant','result':'loss',
    'note_prefix':'2nd | Whimsicott ex T2 | opp 0 pts',
    'note':'2nd | Whimsicott ex T2 | opp 0 pts | vs Ghezzuka | recorded 2026-10-14 09:31:11 CDT | 20261014_143111000_iOS.MP4 | Defeat2-3 at06:30; Mega Swampert ex terminal KO.',
    'scope':'Whole one-game ladder source; all11turns and terminal defeat; source-verified full-account corrections, independent checks and root acceptance',
    'registration_notes':'Independent source checker and root accepted the reconciled account. Deck12 loss2-3 versus Ghezzuka; second; Whimsicott first Grass Knot ownT2/global4 with opponent0. Addendum corrects Lisia identity, post-global9 two Water, and missing168 evidence pointer; initial rejection/frozen primary preserved. External save/readback is separate.',
    'clarifications':['LEAD_CLARIFICATION.md supersedes Lillie with Lisia, three-after Water with two, and the missing168 reference with retained169/170. Original rejection remains saved.'],
    'observations':[
      ('native/t0003.00.jpg','Ranked Match Season B4b SP; Ultra Ball Rank4; Deck12 selected.'),
      ('native/t0165.00.jpg','Before first main attack: Whimsicott ex Active, opponent Ghezzuka0points, owner0; Mantyke Active and Ariados/Ogerpon Bench.'),
      ('native/t0170.00.jpg','Named Whimsicott ex Grass Knot animation; opponent0points.'),
      ('native/t0390.00.jpg','Defeat versus Ghezzuka;went second;11turns;owner2/opponent3;410damage.'),
      ('native/t0239.00.jpg','Right owner discard shows Lisia, correcting the first-pass Lillie name.'),
      ('native/t0312.00.jpg','After Strong-Armed Destroyer, Mega Swampert ex has two Water icons, correcting the first-pass three-after count.'),
      ('native/t0327.00.jpg','Owner Current turn10; opponent2points; Mega Swampert ex retains two Water.'),
    ]},
 '20261014_145449000_iOS':{
    'section':'d12','deck_name':'Ariados / Whimsicott / Ogerpon','energy':'Grass',
    'opponent':'たお','opponent_deck':'Oricorio / Indeedee ex / Dedenne ex','result':'loss',
    'note_prefix':'2nd | Whimsicott ex no attack | opp pts N/A',
    'note':'2nd | Whimsicott ex no attack | opp pts N/A | vs たお | recorded 2026-10-14 09:54:49 CDT | 20261014_145449000_iOS.MP4 | Conceded0-0 at05:36.5; Defeat05:48. Supporting Ariados first PierceT2,opp0.',
    'scope':'Whole one-game ladder source; all12turns and explicit owner-concession defeat; no main attack, independent source checks and root acceptance',
    'registration_notes':'Independent source and root checks accepted. Visible core matches Deck12; selected deck-number label unrecorded. Loss by owner concession at0-0 versusたお; second; Whimsicott ex never attacks, moment/points N/A. Ariados supporting Pierce ownT2 opp0 stays separate. External save/readback is separate.',
    'observations':[
      ('evidence/native_0030.00.jpg','Opening explicitly declares You are going second.'),
      ('evidence/native_0198.00.jpg','Ariados Active with Whimsicott ex, Ariados and Teal Mask Ogerpon ex Bench; visible core matches Deck12; opponentたお0points and Oricorio Active.'),
      ('evidence/native_0336.50.jpg','Owner Concede confirmation dialog; opponent Bench has two Indeedee ex plus Dedenne ex; owner Whimsicott remains Bench and points0.'),
      ('evidence/native_0348.00.jpg','Defeat versusたお;went second;12turns;0-0points;140damage;Ariados Card of the Game.'),
    ]},
 '20261014_144627000_iOS':{
    'section':'d12','deck_name':'Ariados / Whimsicott / Ogerpon','energy':'Grass',
    'opponent':'へいちょー','opponent_deck':'Zeraora / Magneton / Magnezone / Miraidon ex','result':'loss',
    'note_prefix':'2nd | Whimsicott ex T2 | opp 1 pt',
    'note':'2nd | Whimsicott ex T2 | opp 1 pt | vs へいちょー | recorded 2026-10-14 09:46:27 CDT | 20261014_144627000_iOS.MP4 | Defeat2-3 at07:47; Miraidon ex terminal KO at07:32.',
    'scope':'Whole one-game ladder source; all11turns and terminal defeat; independent note-field/source checks and root acceptance',
    'registration_notes':'Independent Sol and root source checks accepted. Deck12 loss2-3; second; Whimsicott ex first Grass Knot ownT2/global4, opponent1 before. No Auto observed. Hidden lists/unreadable noncritical Trainer title remain qualified. External save/readback is separate.',
    'observations':[
      ('native/t0000.00.jpg','Deck12 selected; visible Spinarak/Ariados, Cottonee/Whimsicott ex and Ogerpon ex core.'),
      ('native/t0164.00.jpg','Before first Grass Knot: Whimsicott ex Active with two Grass; opponent へいちょー has1point, owner0; Zeraora Active, two Magneton on Bench.'),
      ('native/t0166.00.jpg','Named Whimsicott ex Grass Knot attack animation; opponent still has1point.'),
      ('native/t0467.00.jpg','Defeat versus へいちょー; went second;11turns;owner2/opponent3;220damage;Whimsicott ex Card of the Game.'),
    ]},
}

for stem,c in CONFIG.items():
    batch=ROOT/'Recording_QA/BATCH_2026-10-14_ADDITIONAL_TWO' if stem in ('20261014_153139000_iOS','20261014_153908000_iOS') else B
    packet=batch/stem
    out=packet/'ROOT_DECISION.json'
    if out.exists():
        continue
    source=json.loads((packet/'SOURCE.json').read_text(encoding='utf-8-sig'))
    c=dict(c)
    c.update({'source_filename':source['video_basename'],'source_sha256':source['sha256'],
        'checked_utc':datetime.now(timezone.utc).isoformat(),'lead':'/root','battle_complete':True,
        'root_read_full_timeline_and_coverage':True,'auto_option_seen':False,'clarifications':c.get('clarifications',[])})
    c['observations']=[{'path':rel,'finding':finding,'directly_viewed_by_root':True} for rel,finding in c['observations']]
    out.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out,flush=True)
