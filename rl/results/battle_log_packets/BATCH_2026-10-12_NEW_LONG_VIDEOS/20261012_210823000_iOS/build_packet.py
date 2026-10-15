raise RuntimeError('Superseded after independent rejection. Do not rerun; use repaired packet and repair provenance.')
from pathlib import Path
import json,copy
from PIL import Image
p=Path(__file__).parent
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig')); video=src['video_basename']; sha=src['sha256']; game='20261012_210823000_iOS_Hons'
binding=[{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
def eid(t):return f'native_{t:07.2f}'
def ids(*ts):return [eid(t) for t in ts]
def save(n,d): (p/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def hand(names,t,basis='Visible left-to-right native hand'):
 return {'cards_left_to_right':[{'position':i+1,'name':name,'variant':None,'basis':'observation','evidence_ids':ids(t),'limit_reason':None} for i,name in enumerate(names)],'count':len(names),'basis':basis,'evidence_ids':ids(t),'status':'observed','limit_reason':None}
luck='Lucky Ice Pop'; research="Professor's Research"; ball='Poké Ball'
opening=[luck,research,'Copycat','Alolan Muk','Alolan Grimer']
starts={2:[luck,research,'Copycat','Alolan Muk','Mesagoza'],4:[luck,'Copycat','Alolan Muk','Pawniard','Regigigas'],6:['Kingambit','Ilima','Glimmora',luck,'Rare Candy','Glimmet'],8:['Ilima','Glimmora',luck,'Glimmet',luck],10:['Glimmora',luck,luck,'Regigigas',research],12:[luck,luck,ball]}
ends={2:[luck,'Copycat','Alolan Muk','Pawniard'],4:['Kingambit','Ilima','Glimmora',luck,'Rare Candy'],6:['Ilima','Glimmora',luck,'Glimmet'],8:['Glimmora',luck,luck,'Regigigas'],10:[luck,luck,ball],12:[luck,luck,ball]}
pre={2:54.5,4:117,6:206.5,8:292,10:355.5,12:429}
before={2:84.5,4:159,6:219.5,8:304,10:378,12:432}
drawend={2:53,4:117,6:206,8:292,10:355.5,12:None}
first={2:55.5,4:117.25,6:208,8:293,10:357,12:None}
candidate={2:[54,56,59],4:[118,120,123],6:[207,209,212],8:[293,295,298],10:[357,359,362],12:[]}
timings=[(34,50),(50,86),(86,114),(114,161),(161,201),(201,221),(221,288),(288,314),(314,353),(353,387),(387,426),(426,433)]
boundary=[35,50,85.5,114,160,200,220.5,287,314,352,388,426,432]
maxhp={'Alolan Grimer':70,'Alolan Muk':110,'Glimmet':60,'Glimmora':90,'Pawniard':50,'Kingambit':140,'Regigigas':150,'Meowth':50,'Alolan Meowth':50,'Pidgey':60,'Mega Pidgeot ex':210}
def mon(name,hp=None,dark=0,colorless=0,tag=None,tool='none',cond=None):
 return {'name':name,'variant':tag,'bench_position':None,'hp_now':maxhp[name] if hp is None else hp,'hp_max':maxhp[name],'hp_max_basis':'Printed HP and visible board; no HP modifier shown','damage':maxhp[name]-(maxhp[name] if hp is None else hp),'attached_energy':{'total':dark+colorless,'by_type':{'Darkness':dark,'Colorless':colorless},'basis':'Visible attached Energy icons and source attachments; Colorless origin separately limited'},'tool':tool,'special_conditions':cond or [],'active_effects':[],'evidence_ids':[],'status':'observed','limit_reason':None}
def O(a,b):return {'active':a,'bench_in_position_order':b}
def bench(lst):
 for i,m in enumerate(lst):
  if m:m['bench_position']=i+1
 return lst
owners=[
 O(mon('Alolan Grimer'),[None,None,None]),
 O(mon('Alolan Grimer'),[None,None,None]),
 O(mon('Alolan Grimer',dark=1),[mon('Glimmet'),None,None]),
 O(mon('Alolan Grimer',dark=1),[mon('Glimmet'),None,None]),
 O(mon('Regigigas'),[mon('Glimmora',tag='Full art, Shattering Crystal / Venomous Hit'),mon('Alolan Muk'),mon('Pawniard')]),
 O(mon('Regigigas'),[mon('Glimmora',tag='Full art, Shattering Crystal / Venomous Hit'),mon('Alolan Muk'),mon('Pawniard')]),
 O(mon('Regigigas'),[mon('Glimmora',tag='Full art, Shattering Crystal / Venomous Hit'),mon('Alolan Muk'),mon('Kingambit',dark=1)]),
 O(mon('Regigigas',hp=50),[mon('Glimmora',tag='Full art, Shattering Crystal / Venomous Hit'),mon('Alolan Muk'),mon('Kingambit',dark=1)]),
 O(mon('Glimmora',dark=1,tag='Full art, Shattering Crystal / Venomous Hit'),[mon('Glimmet'),mon('Alolan Muk'),mon('Kingambit',dark=1)]),
 O(mon('Glimmet'),[None,mon('Alolan Muk'),mon('Kingambit',dark=1)]),
 O(mon('Glimmora',dark=1,tag='Regular art, Shattering Crystal / Venomous Hit'),[mon('Regigigas'),mon('Alolan Muk'),mon('Kingambit',dark=1,tool='Heavy Helmet')]),
 O(mon('Glimmora',dark=1,tag='Regular art, Shattering Crystal / Venomous Hit'),[mon('Regigigas'),mon('Alolan Muk'),mon('Kingambit',dark=1,tool='Heavy Helmet')]),
 O(mon('Glimmora',dark=1,tag='Regular art, Shattering Crystal / Venomous Hit'),[mon('Regigigas'),mon('Alolan Muk'),mon('Kingambit',dark=1,tool='Heavy Helmet')])]
def am():return mon('Alolan Meowth',tag='50 HP, Nasty Plot; ability title unreadable')
def me(d=0):return mon('Meowth',dark=d,tag='50 HP, Carefree Steps / Feelin\' Fine')
def pg(d=0,c=0,h=210,mark='first',poison=False):return mon('Mega Pidgeot ex',hp=h,dark=d,colorless=c,tag=mark+' physical evolution stack, Giant Twister',cond=['Poisoned'] if poison else [])
opponents=[O(me(),[None,None,None]),O(me(),[am(),None,None]),O(me(),[am(),None,None]),O(me(1),[am(),mon('Pidgey',tag='Peck 30'),None]),O(me(1),[am(),mon('Pidgey',tag='Peck 30'),None]),O(me(1),[am(),pg(1,1),mon('Pidgey',tag='Gust 10')]),O(me(1),[am(),pg(1,1),mon('Pidgey',tag='Gust 10')]),O(pg(2,1),[am(),me(),pg(mark='second')]),O(pg(2,1,h=170,poison=True),[am(),me(),pg(mark='second')]),O(pg(2,1,h=180,poison=True),[am(),me(),pg(1,1,mark='second')]),O(pg(2,1,h=140,poison=True),[am(),me(),pg(1,1,mark='second')]),O(pg(2,1,mark='second'),[am(),me(),pg(1,0,h=160)]),O(pg(2,1,mark='second'),[am(),me(),pg(1,0,h=160)])]
effect={'name':'Power of Alchemy','source':'Owner Alolan Muk','affected':'Basic Pokémon in play on both boards','restriction':'Basic Pokémon have no Abilities','expiry':'While this Alolan Muk remains in play','basis':'Visible card text and ability-off symbols'}
def zone(available,t):
 return {'this_turn':{'type':'Darkness' if available else None,'count':1 if available else 0,'available':available},'next':{'type':'Darkness','count':1,'available':False},'basis':'Large current Energy circle and small next Darkness icon; availability is this captured phase only','evidence_ids':ids(t),'limit_reason':None}
def board(n,idx,phase,t):
 b={'turn_number_displayed':n,'phase':phase,'stadium':'none' if idx<2 else ('Mesagoza' if idx<7 else 'Soothing Shore'),'owner':copy.deepcopy(owners[idx]),'opponent':copy.deepcopy(opponents[idx]),'shared_effects':[copy.deepcopy(effect)] if idx>=4 else [],'evidence_ids':ids(t),'source_seconds':t}
 for who in ['owner','opponent']:
  side=b[who];side['bench_in_position_order']=bench(side['bench_in_position_order']);side['points']=0 if who=='owner' else (1 if idx>=9 else 0)
  side['board_effects']=[copy.deepcopy(effect)] if idx>=4 else []
  acting=(who=='owner')==(n%2==0)
  avail=phase=='start_after_normal_draw' and acting and n!=1
  if phase=='start_after_normal_draw' and who=='owner' and n in [4,10]:avail=False
  if phase=='start_after_normal_draw' and n==11 and who=='opponent':avail=False
  if n==12 and who=='owner':avail=True
  side['energy_zone']=zone(avail,t);side['evidence_ids']=ids(t);side['status']='observed';side['limit_reason']=None
  for m in [side['active']]+side['bench_in_position_order']:
   if m:
    m['evidence_ids']=ids(t)
    if idx>=4 and m['name'] in ['Regigigas','Meowth','Alolan Meowth']:m['active_effects']=[{'name':'Basic Ability suppressed','source':'Power of Alchemy','expiry':'While Muk is in play'}]
    if m['name']=='Kingambit' and idx>=9:m['active_effects'].append({'name':'Overlord\'s Blade damage increased after owner knockout','source':'Printed attack; one owner Pokémon was knocked out','expiry':'Battle','basis':'Printed text and the turn 9 Glimmora knockout'})
 return b
turns=[]
for n,(a,z) in enumerate(timings,1):
 who='owner' if n%2==0 else 'opponent'; row={'turn_number':n,'who_played':who,'source_video':video,'source_sha256':sha,'source_time_range_seconds':[a,z],'timing':{'turn_start_seconds':a,'draw_animation_end_seconds':drawend.get(n),'first_voluntary_move_seconds':first.get(n),'before_end_action_seconds':before.get(n),'end_after_resolution_seconds':boundary[n]},'draws_and_searches':[],'plays_in_order':[],'automatic_events_in_order':[],'board_at_start':board(n,n-1,'start_after_normal_draw',pre.get(n,{1:38,3:87,5:166,7:224,9:316,11:388}.get(n,boundary[n-1]))),'board_after':board(n,n,'end_after_effects_checkup_and_replacement',boundary[n]),'discard_snapshot_ids':[],'turn_evidence_ids':ids(boundary[n-1],boundary[n]),'limits':[]}
 if who=='owner':
  h=hand(starts[n],pre[n]);row['hand_at_start']=h;row['owner_hand_start']=copy.deepcopy(h);row['owner_hand_end']=hand(ends[n],before[n]);row['owner_hand_before_end_action']=copy.deepcopy(row['owner_hand_end'])
  fan={2:(None,[5,6]),4:(None,[6,7]),6:(3,None),8:(2,None),10:(2,None),12:(4,None)}[n]
  row['opponent_hand_at_owner_turn_start']={'count':fan[0],'supported_range':fan[1],'count_method':'Distinct card backs in native top crop, not public-transaction arithmetic','basis':'observation','evidence_ids':ids(pre[n]),'limit_reason':'Overlap prevents a unique exact edge count' if fan[1] else None}
  row['draw_timed_candidate_ids']=ids(*candidate[n]);row['turn_evidence_ids']+=ids(pre[n],before[n],*candidate[n])
  if n in [4,8,10]:row['limits'].append('The draw-relative scheduled candidates include an action already underway. The retained dense pre-play selection is listed separately; no later hand is substituted for it.')
  if n==12:row['limits'].append('No normal draw animation or added card is shown. No draw-end timestamp or scheduled offsets are manufactured. The unchanged three-card hand and terminal boundary are retained.')
 else:
  row['hand_at_start']={'cards_left_to_right':None,'count':None,'basis':'Hidden card backs','evidence_ids':ids(boundary[n-1]),'status':'hidden','limit_reason':'Opponent card identities not shown'};row['owner_hand_start']={'cards_left_to_right':None,'count':None,'status':'not_applicable_opponent_turn','evidence_ids':[],'limit_reason':'Owner hand is transcribed on owner turns'};row['owner_hand_end']={'cards_left_to_right':None,'count':None,'status':'not_applicable_opponent_turn','evidence_ids':[],'limit_reason':'Owner does not act this turn'};row['opponent_hand_at_owner_turn_start']={'count':None,'supported_range':None,'status':'not_applicable_opponent_turn','evidence_ids':[],'limit_reason':'Opponent turn, not an owner-turn fan capture'}
 turns.append(row)
def play(n,t,kind,card,result,target=None,energy=None,nested=None):
 r=turns[n-1];r['plays_in_order'].append({'order':len(r['plays_in_order'])+1,'kind':kind,'card_name':card,'target':target,'energy':energy or {'type':None,'count':None,'destination':None,'retreat_payment_by_type':None},'result':result,'prompt_text':None,'response':None,'nested_events_in_order':nested or [],'hand_count_after':None,'source_video':video,'timestamp_seconds':t,'evidence_ids':ids(t),'basis':'observation','limit_reason':None})
def draw(n,t,kind,names,cause=None,order=None,returned=None):
 turns[n-1]['draws_and_searches'].append({'kind':kind,'caused_by':cause,'linked_play_order':order,'cards_in_reveal_order':[{'name':name,'reveal_position':i+1,'source_video':video,'timestamp_seconds':tm,'evidence_ids':ids(tm),'basis':'observation' if name else 'hidden opponent card','limit_reason':None if name else 'Only card back is visible'} for i,(name,tm) in enumerate(names)],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':returned,'source_video':video,'timestamp_seconds':t,'evidence_ids':ids(*[tm for name,tm in names]) if names else ids(t),'limit_reason':None})
def auto(n,t,text):turns[n-1]['automatic_events_in_order'].append({'timestamp_seconds':t,'event':text,'basis':'observation','evidence_ids':ids(t)})
play(1,44,'card_play',research,'Draws two hidden cards')
play(1,47,'card_play','Alolan Meowth','Bench left, 50 HP, Nasty Plot printing')
play(1,49,'end_turn',None,'Ends without attack or Energy attachment')
draw(1,44,'supporter_draw',[(None,44),(None,47)],research,1)
draw(2,53,'normal_draw',[('Mesagoza',53)])
play(2,56,'card_play',research,'Draws Glimmet, then Poké Ball')
draw(2,59,'supporter_draw',[('Glimmet',59),(ball,59.5)],research,1)
play(2,62,'card_play',ball,'Search finds Pawniard')
draw(2,65.5,'search',[('Pawniard',65.5)],ball,2)
play(2,70,'card_play','Glimmet','Bench left, 60 HP')
play(2,74,'card_play','Mesagoza','Installs Stadium')
play(2,79,'stadium_activation','Mesagoza','Tails at 80-81 seconds; no card found')
draw(2,80,'search',[], 'Mesagoza',5)
play(2,83,'energy_attachment',None,'Attaches one Darkness to Active Alolan Grimer','Alolan Grimer',{'type':'Darkness','count':1,'destination':'Active Alolan Grimer','retreat_payment_by_type':None})
play(2,85.5,'end_turn',None,'Ends without attack')
play(3,91,'card_play','Pidgey','Bench center, 60 HP, Peck 30 printing')
play(3,94,'stadium_activation','Mesagoza','Tails; no card found')
play(3,109,'energy_attachment',None,'One Darkness to Active Meowth','Meowth',{'type':'Darkness','count':1,'destination':'Active Meowth','retreat_payment_by_type':None})
play(3,110,'attack','Meowth','Feelin\' Fine draws one hidden card; no damage')
draw(3,112,'attack_draw',[(None,112)],'Feelin\' Fine',4)
draw(4,117,'normal_draw',[('Regigigas',117)])
play(4,117.5,'card_play','Regigigas','Bench center, 150 HP')
play(4,124,'stadium_activation','Mesagoza','Tails at 128 seconds; no card found')
draw(4,128,'search',[],'Mesagoza',2)
play(4,129,'energy_attachment',None,'Second Darkness to Active Alolan Grimer','Alolan Grimer',{'type':'Darkness','count':1,'destination':'Active Alolan Grimer','retreat_payment_by_type':None})
play(4,132,'retreat',None,'Moves Alolan Grimer to center Bench, promotes Regigigas','Regigigas',{'type':None,'count':None,'destination':None,'retreat_payment_by_type':{'Darkness':2}})
play(4,136,'evolution','Alolan Muk','Evolves benched Alolan Grimer; Power of Alchemy removes Basic Abilities on both boards')
auto(4,138,'Basic Pokémon in play have no Abilities. Basic suppression symbols appear on Regigigas and opposing Basics.')
play(4,141,'card_play','Pawniard','Bench right, 50 HP')
play(4,144,'card_play','Copycat','Shuffles the remaining Lucky Ice Pop into deck, then draws six cards')
draw(4,149,'supporter_draw',[('Kingambit',149),('Ilima',149.5),('Glimmora',151),('Lucky Ice Pop',151.5),('Rare Candy',152.5),('Glimmora',153.5)],'Copycat',7,[{'name':luck,'destination':'deck','basis':'Visible sole remaining card before Copycat'}])
play(4,155,'evolution','Glimmora','Evolves left Glimmet using full-art Glimmora')
play(4,160,'end_turn',None,'Ends without attack; Regigigas has no attached Energy')
play(5,176,'card_play','Pidgey','Bench right, 60 HP, Gust 10 printing')
play(5,178,'card_play',ball,'No eligible card in deck; no-effect search message at 181-182 seconds')
draw(5,181,'search',[],ball,2)
play(5,183.5,'card_play','Rare Candy','Chooses center Pidgey and Mega Pidgeot ex from hand; skips Stage 1')
auto(5,195,'The newly evolved Mega Pidgeot ex displays one Colorless Energy icon before the Darkness attachment. Its origin is not explicitly identified by readable source text.')
play(5,196,'energy_attachment',None,'One Darkness to center Mega Pidgeot ex; now Darkness plus Colorless icons','Mega Pidgeot ex first',{'type':'Darkness','count':1,'destination':'Center Bench Mega Pidgeot ex','retreat_payment_by_type':None})
play(5,198,'attack','Meowth','Feelin\' Fine draws one hidden card; no damage')
draw(5,199,'attack_draw',[(None,199)],'Feelin\' Fine',5)
draw(6,206,'normal_draw',[('Glimmet',206)])
play(6,209,'card_play','Rare Candy','Chooses right Pawniard and Kingambit from hand; evolves directly to Kingambit')
play(6,217,'energy_attachment',None,'One Darkness to right Kingambit','Kingambit',{'type':'Darkness','count':1,'destination':'Right Bench Kingambit','retreat_payment_by_type':None})
play(6,220.5,'end_turn',None,'Ends without attack')
play(7,236,'stadium_activation','Mesagoza','Tails; no card found')
play(7,244,'card_play','Soothing Shore','Replaces Mesagoza; Mesagoza moves to owner discard')
play(7,251,'retreat',None,'Active Meowth moves to center Bench; first Mega Pidgeot ex becomes Active','Mega Pidgeot ex first',{'type':None,'count':None,'destination':None,'retreat_payment_by_type':{'Darkness':1}})
play(7,254,'energy_attachment',None,'One Darkness to Active first Mega Pidgeot ex; now two Darkness plus one Colorless','Mega Pidgeot ex first',{'type':'Darkness','count':1,'destination':'Active Mega Pidgeot ex first','retreat_payment_by_type':None})
play(7,262,'card_play','Copycat','Shuffles opponent remaining hand into deck; draws four hidden cards matching owner four-card hand')
draw(7,263,'supporter_draw',[(None,263),(None,263),(None,263),(None,263)],'Copycat',5)
play(7,271,'card_play','Rare Candy','Right Pidgey evolves to second Mega Pidgeot ex')
play(7,278,'attack','Mega Pidgeot ex','Giant Twister: two heads, one tails; 100 damage to Regigigas, 150 to 50 HP. Regigigas had no Energy to discard','Regigigas',nested=[{'order':1,'event':'Three coins: 2 heads, 1 tails at 283 seconds'},{'order':2,'event':'No attached Regigigas Energy to remove'},{'order':3,'event':'100 damage, Regigigas remains at 50 HP'}])
draw(8,290,'normal_draw',[(luck,290)])
play(8,294,'card_play','Ilima','Returns damaged 50/150 HP Regigigas to hand; no Energy attached; promotes full-art Glimmora')
play(8,302,'card_play','Glimmet','Places second Glimmet in left Bench slot')
play(8,304,'energy_attachment',None,'One Darkness to Active Glimmora','Glimmora',{'type':'Darkness','count':1,'destination':'Active Glimmora full art','retreat_payment_by_type':None})
play(8,306,'attack','Glimmora','Venomous Hit deals 30 to first Mega Pidgeot ex, 210 to 180 HP, and Poisons it','Mega Pidgeot ex first')
auto(8,314,'Poison checkup deals 10 damage, first Mega Pidgeot ex 180 to 170 HP. Points remain 0-0.')
play(9,316,'card_play',research,'Draws two hidden cards')
draw(9,320,'supporter_draw',[(None,320),(None,321)],research,1)
play(9,322,'energy_attachment',None,'One Darkness to right second Mega Pidgeot ex; one Colorless icon also appears with this sequence; origin unresolved','Mega Pidgeot ex second',{'type':'Darkness','count':1,'destination':'Right Bench Mega Pidgeot ex second','retreat_payment_by_type':None})
play(9,326,'attack','Mega Pidgeot ex','Giant Twister: one head, two tails. Discards Glimmora one Darkness and deals 100 damage; Glimmora is knocked out','Glimmora full art',nested=[{'order':1,'event':'Three coins: 1 head, 2 tails at 329 seconds'},{'order':2,'event':'Removes one Darkness from Active Glimmora'},{'order':3,'event':'100 damage knocks out 90 HP Glimmora'}])
auto(9,340,'Shattering Crystal flips tails. Hons receives one point, shown at 346 seconds.')
auto(9,346,'Owner promotes benched Glimmet, 60 HP. Alolan Muk and Kingambit remain in play.')
auto(9,350,'Soothing Shore heals first Mega Pidgeot ex 20, 170 to 190 HP.')
auto(9,352,'Poison checkup deals 10, 190 to 180 HP. Owner 0 points, Hons 1.')
draw(10,355.5,'normal_draw',[(research,355.5)])
play(10,357,'evolution','Glimmora','Evolves Active Glimmet into regular-art Glimmora, 90 HP')
play(10,362,'card_play',research,'Draws Poké Ball, then Heavy Helmet')
draw(10,364,'supporter_draw',[(ball,364),('Heavy Helmet',365)],research,2)
play(10,371,'tool_attachment','Heavy Helmet','Attaches to right Kingambit; visible damage-reduction message, HP maximum remains 140','Kingambit')
play(10,374,'energy_attachment',None,'One Darkness to Active Glimmora','Glimmora',{'type':'Darkness','count':1,'destination':'Active Glimmora regular art','retreat_payment_by_type':None})
play(10,378,'card_play','Regigigas','Returns the Ilima-recovered Regigigas to left Bench at full 150 HP')
play(10,382,'attack','Glimmora','Venomous Hit deals 30, first Mega Pidgeot ex 180 to 150 HP, and applies Poison','Mega Pidgeot ex first')
auto(10,388,'Poison checkup deals 10, first Mega Pidgeot ex 150 to 140 HP. Points remain owner 0, Hons 1.')
play(11,400,'retreat',None,'First Mega Pidgeot ex retreats into right Bench; second Mega Pidgeot ex becomes Active at 210 HP. Poison clears','Mega Pidgeot ex second',{'type':None,'count':None,'destination':None,'retreat_payment_by_type':{'Darkness':1,'Colorless':1}})
play(11,412,'energy_attachment',None,'One Darkness to second Active Mega Pidgeot ex, now two Darkness and one Colorless','Mega Pidgeot ex second',{'type':'Darkness','count':1,'destination':'Active Mega Pidgeot ex second','retreat_payment_by_type':None})
play(11,416,'attack','Mega Pidgeot ex','Giant Twister flips three tails; attack does nothing. Owner Glimmora stays at 90 HP with one Darkness','Glimmora regular art',nested=[{'order':1,'event':'0 heads, 3 tails at 420 seconds'},{'order':2,'event':'Explicit attack-did-nothing message at 422 seconds'}])
auto(11,424,'Soothing Shore heals damaged benched first Mega Pidgeot ex, 140 to 160 HP.')
auto(12,429,'No added owner card or draw animation is shown. Three-card hand remains Lucky Ice Pop, Lucky Ice Pop, Poké Ball.')
auto(12,433,'Battle transitions to result without a visible owner voluntary play. Exact terminal cause not shown.')
for r in turns:
 if r['who_played']=='opponent':r['limits'].append('Opponent normal draws and named card acquisitions remain hidden; their identities are not reconstructed from the deck or later plays.')
 r['limits'].append('Neither player opens a discard-pile contents view this turn; only top discard cards and play history are available.')
 # Gather every referenced event and hand frame.
 r['turn_evidence_ids']=sorted(set(r['turn_evidence_ids']+[x for event in r['plays_in_order']+r['automatic_events_in_order'] for x in event['evidence_ids']]))
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':binding,'turns':turns,'limits':['One row for each of the 12 displayed turns. Setup is separate.','Bench arrays have three physical slots; null with empty_slots_known=true means visibly empty, not uninspected.','The blue printed set mark on Pidgey/Mega Pidgeot ex is not counted as a Tool.','Colorless attached Energy icons are transcribed as visible, but their generating mechanism is not established by readable text.'],'empty_slots_known':True})
frames=[]
allnative=sorted([f for f in (p/'turn_evidence').glob('t*.jpg') if '_' not in f.stem])
for f in allnative:
 t=float(f.stem[1:]);roles=[];tn=None;de=None;offset=None;selected=False;preplay=None;suit='Native targeted action, board, reveal or result evidence.'
 for n in starts:
  if t in candidate[n]:
   roles.append('draw_timed_candidate');tn=n;de=drawend[n];offset=t-de;preplay=t<first[n] if first[n] else True
   suit='Before first committed play' if preplay else 'First committed play has already occurred; unsuitable as original starting hand'
  if t==pre[n]:roles.append('selected_start_hand');tn=n;selected=True;preplay=True
  if t==before[n]:roles.append('before_end_hand');tn=n
 if t==25.5:roles.append('opening_hand')
 if t in boundary:roles.append('board_boundary')
 if t==439:roles.append('victory_result')
 with Image.open(f) as im:
  # Bottom fifth begins at floor(0.8 * 2532)=2025.
  bp=p/'turn_evidence'/(f.stem+'_bottom.jpg');tp=p/'turn_evidence'/(f.stem+'_top.jpg')
  if not bp.exists():im.crop((0,2025,1170,2532)).save(bp,quality=95)
  if not tp.exists():im.crop((0,0,1170,1050)).save(tp,quality=95)
 frames.append({'evidence_id':eid(t),'role':', '.join(roles) or 'native_action_or_reveal','turn_number':tn,'who_played':'owner' if tn else None,'source_video':video,'source_sha256':sha,'draw_animation_end_seconds':de,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':offset,'full_frame_path':str(f.relative_to(p)),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(bp.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(tp.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,1050]},'selected_for_start_hand':selected,'before_first_play':preplay,'unzoomed':True if selected or 'before_end_hand' in roles or 'opening_hand' in roles else None,'hand_spread':True if selected or 'before_end_hand' in roles or 'opening_hand' in roles else None,'observation':'Retained hand slots are readable; see TURN_LEDGER.json for their individual names' if selected or 'before_end_hand' in roles or 'opening_hand' in roles else None,'suitability_or_limit':suit})
overview=[]
for f in sorted((p/'seek_overview').glob('t*.jpg')):
 t=float(f.stem[1:]);overview.append({'evidence_id':'overview_'+f.stem,'source_video':video,'source_sha256':sha,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'path':str(f.relative_to(p)),'dimensions':{'width':390,'height':844},'role':'Coarse continuity overview only; never native hand evidence'})
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':binding,'frames':frames,'overview_frames':overview,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'top_crop_pixel_bounds':[0,0,1170,1050],'fixed_grid_is_turn_start_evidence':False},'discard_snapshots':[{'snapshot_id':f'discard_not_shown_turn_{n}_{who}','turn_number':n,'pile_owner':who,'source_video':video,'timestamp_seconds':pre[n],'cards_in_view':None,'scroll_coverage':'No opened pile view','full_pile_established':False,'evidence_ids':ids(pre[n]),'limit_reason':'Neither discard pile is opened during source. A top card is not a full pile snapshot.'} for n in [4,8,12] for who in ['owner','opponent']],'scheduled_capture_limits':['Draw ends are approximate source-time observations, not measured media PTS. Exact actual frame PTS is null.','Turns 4, 8 and 10 act before one or more scheduled candidates; dense pre-play hand retained separately.','Turn 12 shows no normal draw. No offsets are fabricated. Last pre-terminal hand at 432 seconds substitutes for a before-end action because no owner ending action occurs.']})
deck=json.loads((p.parent/'PREPARED_FILMED_DECK.json').read_text(encoding='utf-8-sig'));d=deck['deck']
save('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'sources':binding,'deck_name_in_log':None,'deck_name_in_source':'New deck 16','semantic_deck_name':d['name'],'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','captured_at':deck['prepared_utc'],'log_list_version':None,'expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'actual_card_count':20,'capture_source_text_or_image':'QR_DECODE.json and intake/t0000.00.jpg; preserved batch PREPARED_FILMED_DECK.json','cards_in_filmed_qr_order':d['cards_in_log_order'],'filmed_counts_by_name_and_variant':d['counts_by_name_and_variant'],'energy_configuration_from_filmed_qr':'Darkness','game_version_binding_basis':'Source 0 seconds QR, source 2 seconds New deck 16 editor, source 3 seconds same selected New deck 16 event queue, then continuous matchmaking/setup/game. No deck change is shown.','conflicts_with_filmed_cards':[],'exact_list_status':'exact_filmed_qr_verified_live_log_snapshot_unavailable','limits':[deck['live_list_status'],deck['live_snapshot_status'],'Exact 20 semantic card slots are established by filmed QR. QR reference IDs do not establish artwork or rarity for each copy.']})
limits=[{'id':'live_deck_snapshot','status':'external_source_limit','detail':'Pause Games current deck definition is absent and Add Deck UI is unavailable. The filmed QR verifies all 20 semantic slots, but no live-log deck snapshot is claimed.'},{'id':'discard_views','status':'recording_limit','detail':'Neither pile is opened in the source. No full discard contents or scroll coverage is available.'},{'id':'fan_overlap','status':'recording_limit','detail':'Owner turn 2 and 4 top fans overlap; supported ranges are kept. Copycat separately reveals six owner cards.'},{'id':'normal_draw_turn_12','status':'recording_limit','detail':'No normal draw occurs visibly on turn 12. Hand remains three. Exhausted deck is a plausible arithmetic explanation, not a substituted observation.'},{'id':'terminal_cause','status':'recording_limit','detail':'Victory versus Hons is explicit. The last board is owner 0, opponent 1. No concession, disconnect or timeout cause wording is visible.'},{'id':'opponent_colorless','status':'recording_limit','detail':'Colorless Energy icons appear on Mega Pidgeot ex evolution/attachment sequences. Exact source of the extra Colorless Energy is not established by readable source text.'},{'id':'opponent_meowth_variant','status':'recording_limit','detail':'Bench Alolan Meowth has 50 HP and Nasty Plot; its exact artwork/collection ID and small ability title are not fully readable.'},{'id':'result_stats','status':'recording_limit','detail':'Source ends on Victory and Glimmora Card of the Game. No detailed result statistics or battle-log tab is opened.'}]
save('UNCERTAINTIES.json',{'reviewer':'/root/added_210823','game_id':game,'unresolved':limits,'unreviewed_intervals':[],'consequential_material_drafts_remaining':[]})
pgame={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':game,'review_date':'2026-10-12','sources':binding,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','external_write_performed':False,'deck_name':d['name'],'opening':{'source_video':video,'timestamp_seconds':25.5,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':hand(opening,25.5)['cards_left_to_right'],'selected_active':{'name':'Alolan Grimer','opening_position':5,'source_video':video,'timestamp_seconds':27,'evidence_ids':ids(25.5,27)},'redraw_or_replacement':'No setup redraw is shown','before_active_placement':True,'status':'observed','evidence_ids':ids(25.5,27),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'full_source_review_submitted_for_independent_acceptance','outcome':'owner_win','terminal_cause':None,'last_observed_points':{'owner':0,'opponent':1},'owner_turn_order':'second','game_count_in_source':1,'queue':'Deluxe Pack: Mega Emblem Event','auto_control_visible':False,'limits':limits,'lead_checked':False}
save('PAUSE_GAME.json',pgame)
save('SUMMARY.json',{'video_basename':video,'source_sha256':sha,'reviewer':'/root/added_210823','registered_reviewer_alias':'/root/pause_20261012_210823000_iOS','review_model':'Inherited Sol review worker','review_scope':'Complete source setup, every displayed turn, and terminal result','game_count':1,'turn_count':12,'opponent':'Hons','owner':'Dacz8976','match_date':'2026-10-12','match_date_basis':'SOURCE_TIME.json, America/Chicago','classification':'human_event_battle','queue':'Deluxe Pack: Mega Emblem Event','owner_turn_order':'second','auto_control_visible':False,'owner_choices':'Manual visible taps; no Auto control observed','outcome':'win','terminal_cause':None,'outcome_evidence':ids(439),'last_observed_points':{'owner':0,'opponent':1},'deck_core':['Glimmora','Alolan Muk','Kingambit','Regigigas'],'opponent_visible_core':['Mega Pidgeot ex','Meowth','Alolan Meowth'],'capture_status':'complete_with_recording_limits','review_status':'submitted_for_independent_acceptance','external_logged':False,'source_moved':False,'unreviewed_intervals':[]})
intro=f'''# Complete source review: {video}

Reviewer: /root/added_210823. Registered assignment alias: /root/pause_20261012_210823000_iOS. Review date: October 12, 2026. Frozen source SHA-256: {sha}. This packet is submitted for independent acceptance. The reviewer has not accepted, registered completion, moved the source, or written an external game entry.

One human event battle is recorded against Hons. The owner, Dacz8976, goes second. The source shows Deluxe Pack: Mega Emblem Event at 3 seconds, with New deck 16 continuously selected after the filmed QR and editor. No Auto control is visible. The whole source is covered, including pre-game deck binding, setup, all 12 displayed turns, and the terminal result. Native frames and crops are source-local; the three-second reduced overview is only a continuity aid.

The explicit result is **Victory! versus Hons**, visible at 439 seconds. The last observed board has owner 0 points and Hons 1 point. The exact terminal cause is unknown. No explicit concession, disconnect, or timeout wording is visible in the dense 426-433.5 second ending. The source ends with Glimmora as Card of the Game. Detailed result statistics are not opened.

The original opening five at 25.5 seconds, left to right, are Lucky Ice Pop, Professor's Research, Copycat, Alolan Muk and Alolan Grimer. The owner puts Alolan Grimer in the Active Spot at approximately 27 seconds. No redraw is shown. Both benches are initially empty; opposing Active is the 50 HP Meowth with Carefree Steps and Feelin' Fine. The opponent later shows Alolan Meowth, two Pidgey printings, and two Mega Pidgeot ex.

The exact 20 semantic cards and Darkness configuration are verified from the filmed QR, not reconstructed from hands. The QR, New deck 16 editor, selected event deck and gameplay form a continuous source binding. This list is absent from the current Pause Games deck choices, and the artifact exposes no Add Deck control. DECK_USED.json therefore keeps the verified filmed list separately and does not claim a live-log snapshot.

## Per-turn account

Each numbered play below matches the corresponding TURN_LEDGER.json row. Start/end boards contain all three bench slots, typed attached Energy, HP, tools, conditions, points, Stadium and both Energy Zones. Null physical bench slots mean visibly empty. The owner starts turns with a Darkness available and a next Darkness icon; used Energy is absent at the pre-end boundary. Turn 12 retains its unused Darkness. Opposing Darkness Energy is visible rather than inferred from deck membership. Colorless icons are transcribed, but their origin remains explicitly unresolved.

| Turn | Player | Source interval | Meaningful sequence and resulting state |
|---|---|---|---|
'''
rows=[]
for r in turns:
 n=r['turn_number']; seq='; '.join(str(v['order'])+'. '+(v['card_name']+' ' if v['card_name'] else '')+v['result'] for v in r['plays_in_order'])
 autos='; '.join(v['event'] for v in r['automatic_events_in_order'])
 a,z=r['source_time_range_seconds'];rows.append(f'| {n} | {r["who_played"]} | {a}-{z} s | {seq or "No owner voluntary play shown"}. {autos} |')
supp='''

## Owner draws and hand reconciliation

- Turn 2: normal draw Mesagoza. Research individually reveals Glimmet at 59 seconds and Poké Ball at 59.5 seconds. Poké Ball finds Pawniard at 65.5 seconds. Five cards after the normal draw become six after Research, remain six after Poké Ball replaces itself, then become four after benching Glimmet and playing Mesagoza. Ending hand: Lucky Ice Pop, Copycat, Alolan Muk, Pawniard.
- Turn 4: normal draw Regigigas. Bench Regigigas, evolve Alolan Muk, and bench Pawniard reduce five cards to Lucky Ice Pop plus Copycat. Copycat returns Lucky Ice Pop to deck and individually reveals Kingambit, Ilima, regular Glimmora, Lucky Ice Pop, Rare Candy, then full-art Glimmora. Evolving the latter leaves five: Kingambit, Ilima, regular Glimmora, Lucky Ice Pop, Rare Candy. Mesagoza flips tails, so it adds nothing.
- Turn 6: normal draw Glimmet. Six-card hand loses Rare Candy and Kingambit in the direct evolution, leaving four: Ilima, Glimmora, Lucky Ice Pop, Glimmet.
- Turn 8: normal draw the second Lucky Ice Pop. Ilima is used, Regigigas returns to hand, and Glimmet is benched. Five starting cards therefore end as four: regular Glimmora, Lucky Ice Pop, Lucky Ice Pop, Regigigas. Returning Regigigas and replacing the Active is recorded within Ilima, not as a paid retreat.
- Turn 10: normal draw Professor's Research. Evolution uses regular Glimmora. Research individually draws Poké Ball, then Heavy Helmet. Helmet attaches to Kingambit; Regigigas is benched at full HP. Ending hand is three: Lucky Ice Pop, Lucky Ice Pop, Poké Ball.
- Turn 12: no normal draw or added card is visible. The same three cards persist through the terminal boundary. No timestamp is invented for a draw that the recording does not show.

The scheduled native +1/+3/+6 second candidates are retained for owner turns 2, 4, 6, 8 and 10. Their approximate draw ends are 53, 117, 206, 292 and 356 seconds. Turn 4 benches before +1, and turns 8 and 10 also act very quickly. TURN_EVIDENCE.json labels action-contaminated candidates and separately selects the dense original hand at 117, 292 and 355.5 seconds. The owner ending hands use 84.5, 159, 219.5, 304 and 378 seconds, with attack-ending substitution explicitly recorded for turns 8 and 10. The last clear turn 12 hand at 432 seconds substitutes for a before-end view because no owner end action occurs.

## Board and outcome reconciliation

Alolan Grimer receives Darkness on turns 2 and 4. Its turn 4 retreat pays both Darkness, and Regigigas becomes Active. The owner evolves the now-benched Grimer into Alolan Muk, creating the observed Basic Ability suppression on both boards. Regigigas has no attached Energy while Active. Kingambit is built from Pawniard with Rare Candy on turn 6, receives one Darkness, and later takes Heavy Helmet on turn 10. No HP modifier is attributed to Helmet: Kingambit remains 140 HP.

The first Giant Twister has two heads and one tails, with 100 damage to unenergized Regigigas, 150 to 50 HP. Ilima returns that damaged Regigigas and the owner promotes Glimmora. Venomous Hit deals 30 and applies Poison, putting the first Mega Pidgeot ex from 210 to 180 and then 170 HP at checkup. The second Giant Twister has one head and two tails, removes Glimmora's one Darkness, and knocks it out with 100 damage. Shattering Crystal flips tails, allowing Hons one point. The owner promotes Glimmet. Soothing Shore heals Mega Pidgeot ex from 170 to 190 and Poison takes it to 180.

The second Glimmora attacks on turn 10 for 30, leaving that Mega Pidgeot ex at 150, then Poison takes it to 140. On turn 11 the damaged Mega retreats, pays one Darkness and one Colorless, and clears Poison. The fresh Mega becomes Active at 210 HP. Its Giant Twister flips three tails and the visible message says the attack did nothing. Glimmora stays at 90 HP with its one Darkness. Soothing Shore heals the benched damaged Mega from 140 to 160. The owner wins during the next displayed turn without a visible owner attack or point award.

The printed blue set mark on opposing Pidgey and Mega Pidgeot ex is not a Tool attachment. The only observed Tool play is owner Heavy Helmet onto Kingambit. No Special Condition other than Poison is established. Basic Ability suppression persists after Muk evolves. No item lock, Energy-Zone block or delayed-damage mark is shown. No visible declined Supporter warning occurs; unchosen options are not classified as declines.

## Recording and external-source limits

Neither player opens a discard-pile contents panel. The top discard cards and inferred play history do not establish full piles, duplicates or hidden scroll contents. TURN_EVIDENCE.json records unavailable snapshots for both players at the periodic owner-turn checkpoints. The opponent's identities remain hidden unless publicly played; normal draws and Research/Copycat acquisitions are not named by guessing. Early fan overlap is retained as ranges, and later clear fans as counts. The exact source of the Colorless Energy icons on the Mega evolution/attachment sequences remains unknown. Bench Alolan Meowth's small ability title and exact collection printing remain unreadable.

The battle result is certain, but its exact terminal cause and detailed result statistics are unavailable. These limits do not create unreviewed intervals. UNCERTAINTIES.json preserves each limit, and the capture supplement is complete with recording limits. Independent acceptance remains pending.
'''
(p/'REVIEW.md').write_text(intro+'\n'.join(rows)+supp,encoding='utf-8')
coverage='''# Source coverage

Reviewer: /root/added_210823. Status: full source review submitted for independent acceptance. No source move or completion registration performed.

| Interval | Covered phase | Evidence |
|---|---|---|
| 0-24 seconds | Filmed QR, New deck 16 editor, selected event deck, matchmaking, opponent reveal and second-player setup order | intake/t0000.00.jpg; native 2, 3, 20-24; overview sheet 1 |
| 24-34 seconds | Original five-card opening, chosen Alolan Grimer Active and opponent setup | native 25.5, 26.5, 27, 34 |
'''
for n,(a,z) in enumerate(timings,1):coverage+=f'| {a}-{z} seconds | Turn {n}, {"owner" if n%2==0 else "opponent"}; meaningful actions and both boundary states | TURN_LEDGER.json row {n}; native boundary {boundary[n-1]} and {boundary[n]}; retained targeted native event frames |\n'
coverage+='''| 433-439.96 seconds | Result transition, explicit Victory versus Hons and Glimmora Card of the Game; file end | native 433.5, 434, 435, 439 |

The complete file contains one game. All 12 displayed turns are represented once in TURN_LEDGER.json; setup is not a fabricated turn 0. Source-local native evidence is 1170 by 2532. Bottom crops span full width and y=2025-2532; top crops span y=0-1050. Reduced three-second seek overview supports continuity only. The first continuous coarse decoder was stopped after 14 samples because it was slow; the complete seek overview replaced it and its coverage is not attributed to the interrupted extraction.

Owner turns have named starting and ending hands, ordered plays, individually identified normal/Research/Copycat/search cards and draw-relative native candidates, or the precise turn 12 no-draw limitation. Both boards, Energy Zones, HP, conditions, tools, Stadium and points are reconciled. The only knockout is full-art Glimmora on turn 9. Shattering Crystal tails grants Hons the sole displayed point. The last board is 0-1, while the explicit final result is owner victory with cause unknown.

No opened discard views, hidden opponent identities, exact unreadable ability label, absent result statistics, or unavailable live deck snapshot are reconstructed. These are enumerated in UNCERTAINTIES.json. There are no unreviewed source intervals. Independent source-bound acceptance is still required.
'''
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
print('Wrote eight requested packet files; independent acceptance remains pending.')
