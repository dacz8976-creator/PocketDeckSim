import copy, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
p=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for name in names:
    f=p/name
    s=f.read_text(encoding='utf-8')
    if name.endswith('.md'):
        for a,b in {'At0seconds':'At 0 seconds','at26':'at 26','remains70HP':'remains 70 HP','at20':'at 20','reaches1Fighting+2 Metal':'reaches 1 Fighting + 2 Metal','at40':'at 40','now2Fighting':'now 2 Fighting','at518':'at 518','shows8cards':'shows 8 cards','and1Fighting/1 Metal':'and 1 Fighting / 1 Metal','at544':'at 544','at559':'at 559','confirm12turns':'confirm 12 turns','2-opponent 1,480':'2 to opponent 1, 480','4,2,2,1,0,0':'4, 2, 2, 1, 0, 0','1,3,5,7,9,11':'1, 3, 5, 7, 9, 11','limited;142-144':'limited; 142-144','setup,12':'setup, 12','0,26,27,28,41':'0, 26, 27, 28, 41','544,Victory':'544, Victory','550,results':'550, results'}.items():s=s.replace(a,b)
        s=s.replace('Rough Skin defeats the 20 HP Orthworm before any further Helmet damage to that target.','Rough Skin first brings the 20 HP Orthworm to zero. Rocky Helmet then visibly resolves at 296 with another 20 damage overlay at 297 before removal; HP remains zero.')
    else:
        s=s.replace('Chicago October12 21:25','Chicago October 12 at 21:25').replace('clock supports9:25','clock supports 9:25')
    f.write_text(s,encoding='utf-8')
ld=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
t=ld['turns'][5]
events=['Druddigon 100 to 90','Scyther Metal 1 to 2','Rough Skin 20 brings Orthworm from 20 HP to 0','Rocky Helmet visibly resolves at 296 with a further 20 overlay at 297 while Orthworm remains 0 HP, before removal','Owner gains first point','Opponent promotes Revavroom at 308']
t['automatic_events_in_order']=events
attack=[v for v in t['plays_in_order'] if v['kind']=='attack'][0]
attack['nested_events_in_order']=events
attack['evidence_ids']=['N0287.00','N0293.00','N0295.00','N0296.00','N0297.00','N0298.00','N0302.00','N0308.00']
(p/'TURN_LEDGER.json').write_text(json.dumps(ld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ed=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
existing={v['requested_source_seconds']:v for v in ed['frames']}
for ts in [296,297]:
    if ts not in existing:
        z=copy.deepcopy(existing[295])
        stem=f't{ts:07.2f}'
        z.update(evidence_id=f'N{ts:07.2f}',requested_source_seconds=ts,full_frame_path=f'turn_evidence/{stem}.jpg',role='turn 6 counterdamage resolution',observation='Rocky Helmet banner after Orthworm reaches 0 HP.' if ts==296 else 'Additional 20 damage overlay on Orthworm with HP still 0, before removal.')
        z['bottom_crop']['path']=f'turn_evidence/{stem}_bottom.jpg'
        z['top_crop']['path']=f'turn_evidence/{stem}_top.jpg'
        ed['frames'].append(z)
ed['frames'].sort(key=lambda v:v['requested_source_seconds'])
(p/'TURN_EVIDENCE.json').write_text(json.dumps(ed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Final prose and turn 6 counterdamage repaired. Run validation before freezing.')
