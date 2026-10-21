from pathlib import Path
import json,copy,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;B=P.parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'));A=json.loads((P/'ASSIGNMENT.json').read_text(encoding='utf-8-sig'));M=json.loads((P/'EXTRACTION_MANIFEST.json').read_text())
V=S['video_basename'];SHA=S['sha256'];src=[{'video_basename':V,'sha256':SHA,'source_json':'SOURCE.json'}]
def save(n,o): (P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def f(t):return f'F{t:07.2f}'
def mon(i,n,h,m,e,pos=None):return {'instance_id':i,'name':n,'variant':None,'bench_position':pos,'hp_now':h,'hp_max':m,'hp_max_basis':'Visible printed HP, persistent evolution; no attached Tool/HP modifier observed','damage':m-h,'attached_energy':{'total':e,'by_type':{'Water':e}},'tool':'none','special_conditions':[],'active_effects':[],'evidence_ids':[],'status':'observed_and_reconciled','limit_reason':'Printing set number not inferred. Individual fields reconcile native boundary and continuous instance/action history.'}
O={'active':mon('O-L','Lapras',110,110,0),'bench':[None,None,None],'points':0};C={'active':mon('C-W1','Wailmer',100,100,0),'bench':[None,None,mon('C-B','Frigibax',60,60,0,3)],'points':0};stadium='none'
def en(m,n):m['attached_energy']={'total':n,'by_type':{'Water':n}}
def hp(m,n):m['hp_now']=n;m['damage']=m['hp_max']-n
def ev(m,n,maxh):m['name']=n;m['hp_now']=maxh-m['damage'];m['hp_max']=maxh;m['active_effects']=[]
def zone(w,n,end,t):
 current=0 if end or w!=('owner' if n%2==0 else 'opponent') or n in [1,3,5,7,9,11,17,19] else 1
 return {'this_turn':{'type':'Water'if current else None,'count':current,'available':bool(current),'phase':'generated_available'if current else'consumed_or_inactive_empty'},'next':{'type':'Water','count':1,'available':False,'phase':'displayed_preview'},'basis':'Native large current orb versus small Water preview; empty current is not generated Energy','evidence_ids':[f(t)],'limit_reason':'Boundary phase differs from draw/generation animation. Other phase-specific anchors are in candidate evidence.'}
def board(n,end,t):
 b={'turn_number_displayed':n,'phase':'after end action, attack/KO/replacement/checkup resolution'if end else'turn start before first voluntary play','stadium':stadium,'source_video':V,'timestamp_seconds':t,'shared_effects':[],'evidence_ids':[f(t)]}
 for w,s in [('owner',O),('opponent',C)]:
  active=copy.deepcopy(s['active']);bench=[copy.deepcopy(x)for x in s['bench']if x]
  for m in ([active]if active else[])+bench:
   m['evidence_ids']=[f(t)];m['attribute_provenance']={'name':'Native board/card reveal, physical instance preserved','hp_now':'Boundary plus continuous attack/heal reconciliation','hp_max':'Printed HP, carried forward without modifiers','energy':'Water icons/group count reconciled with attachments/payments','tool':'No Tool observed through instance history','conditions':'No Special Condition observed'}
   if m['name']=='Wartortle'and m['bench_position']:m['active_effects']=[{'name':'Shell Shield','restriction':'Prevents all attack damage while on Bench','expiry':'While on Bench'}]
  b[w]={'active':active,'bench_in_position_order':bench,'bench_slots':[x['instance_id']if x else None for x in s['bench']],'energy_zone':zone(w,n,end,t),'points':s['points'],'board_effects':[],'evidence_ids':[f(t)],'status':'observed_and_reconciled','limit_reason':'No single transition frame claimed to show every attribute; individual carry-forward basis supplied.'}
 if n==17:b['opponent']['board_effects']=[{'name':'Binding Snow','source':'O-N1','target':'C-S Active','restriction':'Cannot take Energy from Energy Zone to attach to Active during opponent turn17','expires':'End of opponent turn17','status':'active'if not end else'ended; visible icon persists during transition','evidence_ids':[f(271.4),f(274.4)]}]
 return b
I='Irida';CP='Copycat';MS='Mega Sharpedo ex';N='Alolan Ninetales ex';R="Professor's Research";PB='Poké Ball';MI='Misty';LC='Lucky Ice Pop';EC='Elegant Cape'
starts={1:22.4,2:31.4,3:47.2,4:63.3,5:69.4,6:88.4,7:120.3,8:141.4,9:148.4,10:165.4,11:174.4,12:195.4,13:204.3,14:221.4,15:238.4,16:261.4,17:274.4,18:290.4,19:324.4}
ends={1:27.9,2:44.8,3:58.3,4:68.3,5:85.4,6:118.4,7:136.4,8:148.4,9:160.4,10:174.4,11:190.4,12:200.4,13:216.4,14:235.4,15:256.4,16:271.4,17:286.4,18:321.4,19:343.4}
drawend={2:30.4,4:62.3,6:87.4,8:140.4,10:164.4,12:194.4,14:220.4,16:260.4,18:290.4}
first={2:32.7,4:64.8,6:89.7,8:142.7,10:166.7,12:196.6,14:222.2,16:262.7,18:290.8}
before={2:43.4,4:67.4,6:110.6,8:144.5,10:171.5,12:197.2,14:223.4,16:268.4,18:303.4}
normal={2:N,4:LC,6:R,8:'Carvanha',10:EC,12:MI,14:'Carvanha',16:'Alolan Vulpix',18:'Cyrus'}
hands={2:[I,CP,MS,R,N],4:[I,CP,MS,N,N,LC],6:[I,CP,MS,N,LC,R],8:[I,CP,MS,N,MI,MS,'Carvanha'],10:[I,CP,MS,N,MI,MS,EC],12:[I,CP,N,MI,MS,EC,MI],14:[I,CP,N,MI,MS,EC,MI,'Carvanha'],16:[I,CP,N,MI,MS,EC,MI,'Alolan Vulpix'],18:[I,CP,N,MI,EC,MI,'Cyrus']}
ending={2:[I,CP,MS,N,N],4:[I,CP,MS,N,LC],6:[I,CP,MS,N,MI,MS],8:[I,CP,MS,N,MI,MS],10:[I,CP,N,MI,MS,EC],12:[I,CP,N,MI,MS,EC,MI],14:[I,CP,N,MI,MS,EC,MI],16:[I,CP,N,MI,EC,MI],18:[I,CP,MI,EC,MI]}
fans={2:5,4:3,6:2,8:2,10:2,12:3,14:3,16:4,18:4}
def hand(ns,t,basis='Direct native visible left-to-right hand; public transaction counts reconcile'):
 return {'cards_left_to_right':[{'position':i+1,'name':n,'variant':None,'basis':basis,'evidence_ids':[f(t)],'limit_reason':None}for i,n in enumerate(ns)],'count':len(ns),'basis':basis,'evidence_ids':[f(t)],'status':'observed_and_reconciled','limit_reason':None}
def pl(k,c,target,result,t,energy=None,nested=None):
 return {'order':0,'kind':k,'card_name':c,'target':target,'energy':energy or {'type':None,'count':None,'destination':None,'retreat_payment_by_type':None},'result':result,'prompt_text':None,'response':None,'nested_events_in_order':nested or [],'hand_count_after':None,'source_video':V,'timestamp_seconds':t,'evidence_ids':[f(t)]if any(x['requested_source_seconds']==t for x in M)else[],'basis':'Continuous locator chronology plus targeted native card/board evidence','limit_reason':'Timestamp is retained event anchor; exact touch instant not asserted'}
def att(target,t):return pl('energy_attachment',None,target,'Attach one Water Energy',t,{'type':'Water','count':1,'destination':target,'retreat_payment_by_type':None})
def ret(target,t,count):return pl('retreat',None,target,f'Pay {count} Water to retreat and promote target',t,{'type':'Water','count':count,'destination':None,'retreat_payment_by_type':{'Water':count}})
def draw(k,names,t,cause=None,order=None):
 return {'kind':k,'caused_by':cause,'linked_play_order':order,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':V,'timestamp_seconds':t+i if len(names)>1 else t,'evidence_ids':[f(t)]if any(x['requested_source_seconds']==t for x in M)else[],'basis':'Visible owner reveal/hand transition'if n else'Visible concealed computer card back','limit_reason':None if n else'Hidden identity remains null'}for i,n in enumerate(names)],'source_video':V,'timestamp_seconds':t,'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':[],'evidence_ids':[],'limit_reason':None}
rows=[];table=[]
for n in range(1,20):
 owner=n%2==0;st=starts[n];end=ends[n];start=board(n,False,st);plays=[];auto=[];draws=[draw('normal_draw',[normal[n]if owner else None],drawend[n]if owner else st)]
 if n==1:
  plays=[pl('card_play',R,'computer hand','Draw two hidden cards',22.4)];draws.append(draw('supporter_draw',[None,None],25.4,R,1));text='Research draws two hidden cards; first turn has no generated Energy; end without attack.'
 if n==2:
  plays=[pl('card_play',R,'owner hand','Draw Ninetales ex then Poke Ball',33.4),pl('card_play',PB,'owner deck','Find Alolan Vulpix',37.7),pl('bench','Alolan Vulpix','owner Bench3','Bench searched Vulpix',43.4),att('O-L',44.8)]
  draws +=[draw('supporter_draw',[N,PB],35.0,R,1),draw('search',['Alolan Vulpix'],40.0,PB,2)]
  O['bench'][2]=mon('O-N1','Alolan Vulpix',60,60,0,3);en(O['active'],1);text='Research; Poke Ball finds Vulpix; bench Vulpix right; Water to Lapras; end without attack.'
 if n==3:
  plays=[pl('evolution','Arctibax','C-B','Evolve right Frigibax',48.3),pl('stadium','Soothing Shore','shared','Stadium enters play',50.3),att('C-W1',55.8),pl('card_play',PB,'computer deck','Find one hidden Basic',55.8),pl('bench','Squirtle','computer Bench1','Bench Squirtle left',58.3)]
  ev(C['bench'][2],'Arctibax',90);stadium='Soothing Shore';en(C['active'],1);C['bench'][0]=mon('C-S','Squirtle',70,70,0,1);draws.append(draw('search',[None],55.8,PB,4));text='Evolve Arctibax; Soothing Shore; Water to Wailmer; Poke Ball hidden search; bench Squirtle. No attack.'
 if n==4:
  plays=[pl('evolution',N,'O-N1','Evolve Vulpix',65.3),att('O-L',68.3)];ev(O['bench'][2],N,150);en(O['active'],2);text='Evolve right Vulpix to Ninetales; second Water to Lapras; end without attack.'
 if n==5:
  plays=[pl('evolution','Baxcalibur','C-B','Evolve Arctibax',72.2),pl('evolution','Wartortle','C-S','Evolve Squirtle; Shell Shield visible',74.2),pl('ability','Baxcalibur','C-W1','Ice Maker adds Water to Active Wailmer',78.5),att('C-W1',80.4),pl('attack','Wailmer','O-L','Wave Splash60; Lapras110 to50',83.4)]
  ev(C['bench'][2],'Baxcalibur',140);ev(C['bench'][0],'Wartortle',90);en(C['active'],3);hp(O['active'],50);text='Evolve Baxcalibur then Wartortle; Ice Maker and ordinary Water to Wailmer; Wave Splash60 leaves Lapras50.'
 if n==6:
  plays=[pl('card_play',R,'owner hand','Draw Misty then Sharpedo',90.4),pl('card_play',LC,'O-L','Heal20, Heads, return to hand',95.2,nested=['Lapras50 to70','Heads at101.3','Lucky Ice Pop returns to hand']),pl('card_play',LC,'O-L','Heal20, Tails, discard',106.4,nested=['Lapras70 to90','Tails at109.3','Lucky Ice Pop discarded']),att('O-L',111.4),pl('attack','Lapras','C-W1','Surf70 leaves Wailmer30',111.4)]
  draws.append(draw('supporter_draw',[MI,MS],92.0,R,1));hp(O['active'],110);en(O['active'],3);hp(C['active'],30);auto=['Soothing Shore heals Lapras90 to110 at118.4'];text='Research draws Misty then Sharpedo. Lucky Ice Pop twice: Heads then Tails, total40heal. Third Water to Lapras; Surf70; Shore restores Lapras110.'
 if n==7:
  plays=[pl('card_play','X Speed','C-W1','Retreat cost reduced by1 this turn',126.6),ret('C-B',126.6,2),pl('ability','Baxcalibur','C-B','Ice Maker Water to Active Baxcalibur',130.3),att('C-S',136.4)]
  old=C['active'];en(old,1);C['active']=C['bench'][2];C['active']['bench_position']=None;old['bench_position']=3;C['bench'][2]=old;en(C['active'],1);en(C['bench'][0],1);hp(old,50);auto=['Shore heals benched Wailmer30 to50'];text='X Speed; Wailmer retreats for2Water to Baxcalibur. Ice Maker to Baxcalibur; ordinary Water to Wartortle. End; Wailmer heals50.'
 if n==8:
  plays=[pl('bench','Carvanha','owner Bench2','Bench drawn Carvanha',143.4),att('O-N1',144.5),pl('attack','Lapras','C-B','Surf70; Baxcalibur140 to70',146.4)];O['bench'][1]=mon('O-S1','Carvanha',50,50,0,2);en(O['bench'][2],1);hp(C['active'],70);text='Bench Carvanha middle; first Water to Ninetales; Surf70 damages Baxcalibur.'
 if n==9:
  plays=[pl('ability','Baxcalibur','C-B','Ice Maker second Water to Baxcalibur',154.3),att('C-S',160.4),pl('bench','Wailmer','computer Bench2','Bench second Wailmer',160.4)];en(C['active'],2);en(C['bench'][0],2);C['bench'][1]=mon('C-W2','Wailmer',100,100,0,2);hp(C['active'],90);hp(C['bench'][2],70);auto=['Shore heals Baxcalibur70 to90, original Wailmer50 to70'];text='Ice Maker second Water to Baxcalibur; ordinary second Water to Wartortle; bench second Wailmer. No attack; both damaged Water Pokemon heal20.'
 if n==10:
  plays=[pl('evolution',MS,'O-S1','Evolve middle Carvanha',167.4),att('O-N1',170.4),pl('attack','Lapras','C-B','Surf70; Baxcalibur90 to20',174.4)];ev(O['bench'][1],MS,190);en(O['bench'][2],2);hp(C['active'],20);text='Evolve middle Carvanha to Sharpedo; second Water to Ninetales; Surf70 leaves Baxcalibur20.'
 if n==11:
  plays=[pl('card_play',PB,'computer deck','Find hidden Basic; not immediately benched',180.4),pl('ability','Baxcalibur','C-B','Ice Maker third Water to Baxcalibur',184.4),att('C-S',186.4),ret('C-W2',186.4,3)]
  draws.append(draw('search',[None],180.4,PB,1));en(C['bench'][0],3);old=C['active'];en(old,0);C['active']=C['bench'][1];C['active']['bench_position']=None;old['bench_position']=2;C['bench'][1]=old;hp(C['bench'][2],90);auto=['Shore heals original Wailmer70 to90; Baxcalibur no Water so stays20'];text='Poke Ball hidden search; Ice Maker third Water to Baxcalibur; ordinary third Water to Wartortle. Baxcalibur retreats for3Water to fresh Wailmer. Original Wailmer heals90.'
 if n==12:
  plays=[att('O-S1',197.4),pl('attack','Lapras','C-W2','Surf70; Wailmer100 to30',200.4)];en(O['bench'][1],1);hp(C['active'],30);text='First Water to middle Sharpedo; Surf70 against fresh Wailmer.'
 if n==13:
  plays=[pl('evolution','Mega Blastoise ex','C-S','Evolve left Wartortle with3Water',208.3),pl('ability','Baxcalibur','C-W2','Ice Maker first Water to Active Wailmer',212.4),att('C-W1',212.4)];ev(C['bench'][0],'Mega Blastoise ex',230);en(C['active'],1);en(C['bench'][2],2);hp(C['active'],50);hp(C['bench'][2],100);auto=['Shore heals active Wailmer30 to50 and original90 to100'];text='Evolve Blastoise; Ice Maker first Water to Active Wailmer; ordinary second Water to original Wailmer. Both heal, no attack.'
 if n==14:
  plays=[pl('bench','Carvanha','owner Bench1','Bench second Carvanha left',223.4),att('O-S2',223.4),pl('attack','Lapras','C-W2','Surf70 KOs Wailmer50; owner point1; Blastoise promoted',226.4)];O['bench'][0]=mon('O-S2','Carvanha',50,50,1,1);C['active']=C['bench'][0];C['active']['bench_position']=None;C['bench'][0]=None;O['points']=1;auto=['Opponent forced replacement Blastoise at235.4'];text='Bench second Carvanha left, give Water. Surf KOs second Wailmer; owner1point. Blastoise becomes Active with3Water.'
 if n==15:
  plays=[pl('ability','Baxcalibur','C-S','Ice Maker fourth Water to Blastoise',242.4),att('C-S',244.8),pl('attack','Mega Blastoise ex','O-L','Triple Bombardment130 KOs Lapras, no Bench bonus at5Water',245.4)];en(C['active'],5);C['points']=1;O['active']=O['bench'][2];O['active']['bench_position']=None;O['bench'][2]=None;auto=['Owner forced replacement chooses Ninetales150,2Water at256.4'];text='Ice Maker and ordinary Water take Blastoise3 to5. Triple Bombardment130 KOs Lapras; computer1point. Auto selects Ninetales Active.'
 if n==16:
  plays=[pl('bench','Alolan Vulpix','owner Bench3','Bench drawn second Vulpix',263.4),pl('evolution',MS,'O-S2','Evolve left Carvanha',266.4),att('O-N2',267.4),pl('attack',N,'C-S','Binding Snow80; Blastoise230 to150; Active attachment block next opponent turn',271.4)];O['bench'][2]=mon('O-N2','Alolan Vulpix',60,60,1,3);ev(O['bench'][0],MS,190);hp(C['active'],150);text='Bench Vulpix right; evolve left Carvanha; Water to Vulpix; Binding Snow80 blocks Active attachments during computer turn17.'
 if n==17:
  plays=[att('C-W1',278.4),pl('bench','Frigibax','computer Bench1','Bench second Frigibax',278.4),pl('attack','Mega Blastoise ex','O-N1','Triple Bombardment130; Ninetales150 to20; no Bench bonus at5Water',280.3)];en(C['bench'][2],3);C['bench'][0]=mon('C-B2','Frigibax',60,60,0,1);hp(O['active'],20);hp(C['active'],170);auto=['Shore heals Blastoise150 to170'];text='Active attachment block visible. Water to benched original Wailmer; bench Frigibax. Blastoise130 leaves Ninetales20, then heals20.'
 if n==18:
  plays=[pl('evolution',N,'O-N2','Evolve right Vulpix before+1 candidate',293.4),pl('card_play','Cyrus','C-B','Pull Baxcalibur20; Blastoise to Bench2',296.4),ret('O-S1',301.4,2),att('O-N2',303.4),pl('attack',MS,'C-B','Turbo Shark70 KOs Baxcalibur; Water to damaged benched Ninetales',309.4,nested=['Baxcalibur20 takes70 and KO','Take Water from Zone; attach to O-N1','Owner gains second point','Opponent promotes Blastoise'])]
  ev(O['bench'][2],N,150);en(O['bench'][2],2);old=C['active'];C['active']=C['bench'][1];C['active']['bench_position']=None;old['bench_position']=2;C['bench'][1]=old
  oldO=O['active'];en(oldO,1);hp(oldO,40);O['active']=O['bench'][1];O['active']['bench_position']=None;oldO['bench_position']=2;O['bench'][1]=oldO
  C['active']=C['bench'][1];C['active']['bench_position']=None;C['bench'][1]=None;O['points']=2;auto=['Turbo Shark adds Water to O-N1 after retreat consumed2; Shore heals it20 to40'];text='Evolve right Vulpix; Cyrus pulls Baxcalibur20; retreat damaged Ninetales for2Water into middle Sharpedo; ordinary Water to new Ninetales. Turbo Shark KOs Baxcalibur, energizes old Ninetales; it heals40. Owner2points.'
 if n==19:
  plays=[pl('evolution','Arctibax','C-B2','Evolve left Frigibax',327.4),att('C-S',330.4),pl('evolution','Wailord ex','C-W1','Evolve original Wailmer,3Water',333.4),pl('attack','Mega Blastoise ex','O-S1; O-N1; O-N2','130Active plus50 to each benched Ninetales; old Ninetales40 KO for final2points',339.4,nested=['Active Sharpedo190 to60','Old benched Ninetales40 to0','New benched Ninetales150 to100','Computer1 to3points; terminal Defeat'])];ev(C['bench'][0],'Arctibax',90);en(C['active'],6);ev(C['bench'][2],'Wailord ex',250);hp(O['active'],60);O['bench'][1]=None;hp(O['bench'][2],100);C['points']=3;text='Evolve Arctibax; sixth Water to Blastoise; evolve Wailord. Triple Bombardment130 plus two50Bench hits KOs Ninetales40 for final2points. Sharpedo survives60. Defeat.'
 if n in [1,2,3,4,7,9,11,13]:plays.append(pl('end_turn',None,None,'End without attack; no visibly offered Supporter warning',end))
 for idx,p in enumerate(plays):p['order']=idx+1
 hs=hand(hands[n],st)if owner else {'cards_left_to_right':None,'count':None,'basis':'Concealed computer hand','evidence_ids':[f(st)],'status':'hidden','limit_reason':'Concealed draws stay null'}
 ownerhs=hs if owner else hand(ending.get(n-1,[I,CP,MS,R]),st,'Owner hand carried from prior observed end through computer turn; no owner hand-changing effect observed')
 he=hand(ending[n],before[n])if owner else hand(ending.get(n-1,[I,CP,MS,R]),end,'Owner hand carried from prior observed end; no owner hand-changing computer effect')
 fan={'count':fans[n]if owner else None,'supported_range':None,'count_method':'Count distinct exposed backs/lower edges left to right'if owner else None,'basis':'Direct native top crop'if owner else'Not an owner turn','evidence_ids':[f(st)]if owner else[],'limit_reason':None if owner else'Owner-start fan count on even rows'}
 timing={'turn_start_seconds':st,'draw_animation_end_seconds':drawend.get(n),'draw_end_precision':'Approximate fully joined hand checkpoint; not exact first animation-complete decoder frame','first_voluntary_move_seconds':first.get(n),'before_end_action_seconds':before.get(n),'end_after_resolution_seconds':end}
 row={'turn_number':n,'who_played':'owner_auto'if owner else'opponent','source_video':V,'timing':timing,'hand_at_start':hs,'owner_hand_start':ownerhs,'opponent_hand_at_owner_turn_start':fan,'draws_and_searches':draws,'plays_in_order':plays,'automatic_events_in_order':[{'order':i+1,'event':x,'evidence_ids':[f(end)]}for i,x in enumerate(auto)],'board_at_start':start,'board_after':board(n,True,end),'owner_hand_end':he,'discard_snapshot_ids':[],'turn_evidence_ids':[f(st),f(end)],'limits':['Approximate action anchors are distinct from exact decoder PTS.','Opponent identities concealed until public play.','No opened discard piles.'],'narrative':text}
 rows.append(row);table.append(f'| {n} | {"Owner Auto"if owner else"Computer"} | {st:.1f} to {end:.1f} | {text} | {len(ending[n])if owner else"same"} | {O["points"]}-{C["points"]} |')
for row in rows:
 if row['who_played']=='opponent':
  row['timing']['turn_start_precision']='Retained transition checkpoint at/before generated Energy and first voluntary play; preceding turn header can persist during draw animation.'
 for d in row['draws_and_searches']:
  if d['kind']=='supporter_draw' and row['turn_number']==2:
   for card,t in zip(d['cards_in_reveal_order'],[36.4,36.8]):card['evidence_ids']=[f(t)];card['timestamp_seconds']=t
  if d['kind']=='supporter_draw' and row['turn_number']==6:
   for card,t in zip(d['cards_in_reveal_order'],[92.0,93.0]):card['evidence_ids']=[f(t)];card['timestamp_seconds']=t
 if row['who_played']=='owner_auto':
  count=row['owner_hand_start']['count']
  normal_d=row['draws_and_searches'][0];normal_d['hand_count_before']=count-1;normal_d['hand_count_after']=count
  for action in row['plays_in_order']:
   if action['kind'] in ['bench','evolution']:count-=1
   elif action['kind']=='card_play':
    count-=1
    if action['card_name']==R:count+=2
    if action['card_name']==PB:count+=1
    if action['card_name']==LC and 'Heads' in action['result']:count+=1
   action['hand_count_after']=count
  assert count==row['owner_hand_end']['count'],(row['turn_number'],count)
  for d in row['draws_and_searches'][1:]:
   p=row['plays_in_order'][d['linked_play_order']-1]
   d['hand_count_after']=p['hand_count_after'];d['hand_count_before']=p['hand_count_after']-len(d['cards_in_reveal_order'])
 if row['turn_number'] in [4,8,12,16,18]:row['discard_snapshot_ids']=[f'DISCARD_LIMIT_T{row["turn_number"]}_{who}'for who in ['owner','opponent']]
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':P.name,'sources':src,'turns':rows,'limits':['One row per displayed turn1 through19; setup separate.','Physical-instance board fields individually provenance qualified.','Start timestamps include draw/generation transition; null type at an empty large orb is distinct from the small Water preview.']})
opening=hand([I,'Lapras',CP,MS,R],14.8)
opening.update({'source_video':V,'timestamp_seconds':14.8,'expected_card_slots':5,'recorded_card_count':5,'selected_active':{'name':'Lapras','opening_position':2,'source_video':V,'timestamp_seconds':15.4,'evidence_ids':[f(15.4)]},'redraw_or_replacement':'No redraw or replacement of opening observed','before_active_placement':True,'status':'observed','limit_reason':None})
save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':P.name,'review_date':'2026-10-02','sources':src,'destination':str(P),'deck_name':'Draft A: Shark Tempo','opening':opening,'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'first_pass_submitted_awaiting_independent_acceptance','outcome':'loss','limits':['No opened discard piles; hidden computer draws stay null.','Local computer comparison; no online game entry.'],'lead_checked':False})
deck=json.loads((B/'OWNER_DECK_SNAPSHOT.json').read_text(encoding='utf-8-sig'))
deck.update({'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':P.name,'source_video':V,'source_sha256':SHA,'capture_source_text_or_image':'../OWNER_DECK_LOG_CAPTURE.txt','source_snapshot':'../OWNER_DECK_SNAPSHOT.json','snapshot_sha256':hashlib.sha256((B/'OWNER_DECK_SNAPSHOT.json').read_bytes()).hexdigest(),'filmed_deck_binding':'Setup shows Draft A: Shark Tempo; owner confirms original Misty version. Visible names/attacks agree; alternate physical art does not establish printed set identifiers.'})
save('DECK_USED.json',deck)
frames=[]
candidate_times={}
for n,de in drawend.items():
 for off in [1,3,6]:candidate_times[round(de+off,1)]=(n,off)
for m in M:
 x=copy.deepcopy(m);t=x['requested_source_seconds'];x.update({'role':'targeted_event_or_board','turn_number':None,'who_played':None,'draw_animation_end_seconds':None,'offset_after_draw_seconds':None,'selected_for_start_hand':False,'before_first_play':None,'unzoomed':None,'hand_spread':None,'observation':'Retained native source event/board checkpoint; context in turn ledger and prose','suitability_or_limit':'Event anchor does not by itself establish all carried-forward fields.'})
 if t in candidate_times:
  n,off=candidate_times[t];x.update({'role':'owner_draw_offset_candidate','turn_number':n,'who_played':'owner_auto','draw_animation_end_seconds':drawend[n],'offset_after_draw_seconds':off,'selected_for_start_hand':t==starts[n],'before_first_play':t<first[n],'unzoomed':True,'hand_spread':True,'observation':'Start hand '+', '.join(hands[n]) if t<first[n] else'Later candidate after first voluntary move; excluded from start hand selection','suitability_or_limit':'Usable full-board hand before move'if t<first[n] else'Post-play; cannot establish original start hand'})
 if t==290.4:x.update({'role':'fast_preplay_owner_start','turn_number':18,'who_played':'owner_auto','draw_animation_end_seconds':290.4,'offset_after_draw_seconds':0,'selected_for_start_hand':True,'before_first_play':True,'unzoomed':True,'hand_spread':True,'observation':'Seven-card fully joined owner hand includes newly drawn Cyrus before first evolution at about290.8','suitability_or_limit':'Fast alternate; +1,+3,+6 are all post-evolution'})
 if t in before.values():
  n=next(k for k,v in before.items()if v==t);x.update({'role':'owner_before_end_action','turn_number':n,'who_played':'owner_auto','observation':'Owner remaining hand before final attachment/attack/end action; names/count in ledger','unzoomed':True,'hand_spread':True})
 if t in [14.8,14.95]:x.update({'role':'five_card_opening_before_placement','turn_number':0,'who_played':'owner_auto','before_first_play':True,'unzoomed':True,'hand_spread':True,'observation':'Five opening cards Irida, Lapras, Copycat, Mega Sharpedo ex, Research'})
 if t==0:x.update({'role':'setup_identity','observation':'Computer Mega Blastoise ex & Wailord ex Deck (Deluxe Pack Mega), Draft A, Auto checked'})
 if t==352.4:x.update({'role':'result','observation':'Defeat; went second;19turns; owner2/opponent3points;500damage'})
 frames.append(x)
discard=[]
for n in [4,8,12,16,18]:
 for who in ['owner','opponent']:discard.append({'snapshot_id':f'DISCARD_LIMIT_T{n}_{who}','turn_number':n,'pile_owner':who,'source_video':V,'timestamp_seconds':before[n],'cards_in_view':None,'scroll_coverage':'none; no opened pile shown','full_pile_established':False,'evidence_ids':[f(before[n])],'limit_reason':'Source never opens discard; side-stack top does not prove complete discard list.'})
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':P.name,'sources':src,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'fixed_grid_is_turn_start_evidence':False},'frames':frames,'discard_snapshots':discard,'scheduled_capture_limits':['Periodic discard views cannot be manufactured because original source never opens either pile.','Native candidates retained even when post-play; turn18 requires0-offset alternate.']})
summary={'source_video':V,'source_sha256':SHA,'source_identity_basis':'Preserved root-verified SOURCE.json; worker did not repeat movie hash','match_date_local':'2026-10-02','recording_duration_seconds':S['duration_seconds'],'reviewer':'drafta_auto_210952 Sol first-pass reviewer','model':'gpt-6.1-sol','effort':'high','full_review_complete':True,'complete_first_pass':True,'independent_accepted':False,'classification':'computer_battle','ranked_ladder_eligible':False,'human_pause_games_eligible':False,'actual_requested_log':None,'online_log_requested':False,'online_game_entry_requested':False,'destination':str(P),'routing_receipt':'ROUTING.json','owner_deck':'Draft A: Shark Tempo, original Misty version','opponent_deck':'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)','opponent':'AI computer','step_up_category':'Advanced','category_basis':'../ADVANCED_CATEGORY_CONFIRMATION.json; owner-supplied source-bound screenshot and same-setup testimony','separate_difficulty_selector':False,'difficulty_label_visible_in_video_setup':False,'auto_control_present':True,'auto_enabled':'On throughout visible gameplay','auto_changes':[],'action_authorship':'game Auto; no manual gameplay override observed','went':'second','result':'loss','owner_points':2,'opponent_points':3,'turns':19,'damage_dealt':500,'result_evidence_ids':[f(343.4),f(352.4)],'result_source_seconds':352.4,'result_basis':'Native Defeat screen explicitly reports second,19turns,2-3points,500damage. Decisive Triple Bombardment bench KO independently reconciles result.','capture_status':'complete_with_recording_limits','owner_turn_rows':9,'opponent_turn_rows':10,'owner_draws_named':9,'research_draw_cards_named':4,'owner_search_cards_named':1,'owner_opening_cards_named':5,'misty_plays':0,'copycat_plays':0,'opened_discard_views':0,'deck_snapshot_conflicts':[],'native_captures':len(M),'coverage':'All18locator grids inspected; entire0-357s recording covered. Targeted native timed hand, board, card and result evidence retained.','limits':['Concealed opponent draws/search identities remain null.','No opened discard census; no unfilmed prompt declines inferred.','Printed set identifiers from deck list are not physical art assertions.','Turn-start transition anchors can precede displayed next header or Energy generation. Exact touch times are approximate.']}
save('SUMMARY.json',summary)
save('UNCERTAINTIES.json',{'source_video':V,'source_sha256':SHA,'consequential_ambiguities':[],'requires_astra':False,'recording_limits':[{'topic':'computer hand','status':'hidden','limit':'All normal draws, Research draws and Poke Ball finds stay null until public play; complete deck snapshot cannot identify a hidden draw.'},{'topic':'discard piles','status':'not_shown','limit':'Neither pile opened at any time; periodic source-bound unavailable markers retained. Top visible stack cards and play history are partial only.'},{'topic':'action timestamps','status':'approximate','limit':'Narrative/action seconds locate event or native anchor; measured selected-frame PTS is separately retained. One-fps full-source scan is not proof of every subsecond touch.'},{'topic':'physical printing','status':'not_inferred','limit':'Alternate red/rainbow/blue artworks readable; official set identifier in exact deck snapshot not asserted for a filmed physical art.'},{'topic':'Advanced','status':'separate_evidence','limit':'Beginning opponent selector identifies deck/AI, not menu category; Advanced comes from source-bound owner screenshot, with same-setup confirmation. No separate selectable difficulty.'},{'topic':'turn boundary','status':'phase_qualified','limit':'Some captured starts retain preceding header during draw transition. Empty current Energy is recorded separately from preview; board attributes use public instance continuity where boundary image alone is insufficient.'}]})
metrics={'source_video':V,'source_sha256':SHA,'model':'gpt-6.1-sol','effort':'high','reviewer':'drafta_auto_210952','locator_samples':357,'locator_grids':18,'locator_grids_visually_inspected':18,'native_full_frames_extracted':len(M),'native_crop_files':len(M)*2,'native_images_visually_inspected_count':None,'native_images_visually_inspected_lower_bound':80,'inspection_count_basis':'Tool history shows extensive direct full-frame and crop inspection; exact distinct displayed-image count was not separately measured. All required draw candidates and key setup/result/decision boards inspected.','native_cap':160,'native_cap_remaining':160-len(M),'source_full_decode_passes':1,'source_rehashes_by_worker':0,'elapsed_seconds':None,'elapsed_measurement_limit':'No continuous worker timer recorded; do not infer from intake clock.','actual_token_usage':None,'actual_dollar_cost':None,'usage_measurement_limit':'Per-worker token and dollar usage not exposed; not estimated','completed_utc':datetime.now(timezone.utc).isoformat()}
save('METRICS.json',metrics)
turntable='# Turn record: '+V+'\n\nSource SHA256: `'+SHA+'`. Owner Auto went second and lost2–3 at turn19. All times are source-local seconds; event anchors are approximate.\n\n| Turn | Actor | Boundary seconds | Ordered observed course | Owner remaining hand | Points owner-computer |\n|---|---|---|---|---:|---:|\n'+'\n'.join(table)+'\n\n## Owner draw and hand checkpoints\n\n| Turn | Named normal draw | Draw end | +1,+3,+6 candidates | Selected preplay | Before ending action | Opponent fan count |\n|---|---|---:|---|---:|---:|---:|\n'
for n,de in drawend.items():turntable+=f'| {n} | {normal[n]} | {de} | {de+1:.1f}, {de+3:.1f}, {de+6:.1f} | {starts[n]} | {before[n]} | {fans[n]} |\n'
turntable+='\nT18 first evolution begins about290.8, so all three default offset candidates are after play. The fully joined native290.4hand is the selected alternate. No hidden computer identities are filled from the opponent list.\n'
(P/'TURN_TABLE.md').write_text(turntable,encoding='utf-8')
review='''# Full battle review: 20261002_210952000_iOS.MP4

The owner, with game Auto enabled, loses2–3 in19turns after going second. The final native result at352.4seconds explicitly says Defeat and damage dealt500. The deciding attack leaves the Active Mega Sharpedo ex alive at60HP, but knocks out the damaged benched Alolan Ninetales ex for the computer's final two points. This is a local computer comparison packet, excluded from human Pause Games and ranked ladder results under ROUTING.json. It awaits independent acceptance.

## Source and setup

The immutable SOURCE.json binds the 357.008333 second, 652990464 byte, 1170 x 2532 recording to SHA256 8dc56261d95966327b98d5e3964d7858d3e35afe64302fab8d79e598e41e9a4d. The reviewer reused that identity and did not rehash the movie or move it. The opening selector at 0 seconds shows Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega), AI, and Draft A: Shark Tempo. The Auto control is checked throughout visible gameplay. No Auto changes or manual overrides are observed; owner gameplay actions are attributed to game Auto.

The source-bound owner screenshot in ../ADVANCED_CATEGORY_CONFIRMATION.json establishes this deck's Step-Up Battle category as Advanced. The owner confirms the same setup across this batch and says there are no separate difficulty settings. Advanced is therefore the menu category, not a difficulty guessed from the deck name or a selector visible in this recording's opening. The exact twenty-card owner snapshot is copied into DECK_USED.json from the logged original Draft A with two Misty. Its Pause Games URL remains deck provenance only. Filmed card names and attacks agree with that list. Alternate artworks do not prove the log's set identifiers for each filmed physical card. The supplied opponent twenty-card list is context, never a way to fill concealed draws.

## Opening and complete course

At14.8and14.95seconds, all five cards are readable before Active placement, left to right: Irida, Lapras, Copycat, Mega Sharpedo ex and Professor's Research. Lapras from opening slot2 becomes Active at15.4. No opening redraw is observed. The computer starts Wailmer100HP Active and Frigibax60HP on right Bench3. Owner starts no Bench Pokemon. The opening flip sends owner second.

On computer turn1, a hidden normal draw and Research drawing two concealed cards are shown. No first-turn generated Energy or attack occurs. Owner turn2 draws Alolan Ninetales ex; Research then reveals another Alolan Ninetales ex followed by Poke Ball. Poke Ball finds Alolan Vulpix, which goes on right Bench3. A Water attaches to Lapras. Computer turn3 evolves the right Frigibax to Arctibax, puts Soothing Shore into play, attaches Water to Wailmer, uses Poke Ball for a concealed Basic, and benches Squirtle left. No attack occurs. Owner turn4 draws Lucky Ice Pop, evolves the right Vulpix to Ninetales and gives Lapras its second Water; no attack yet.

Computer turn5 evolves Arctibax to Baxcalibur and Squirtle to Wartortle. Ice Maker supplies Water to Active Wailmer and the ordinary generated Water also goes there, reaching3. Wave Splash60 leaves Lapras50HP. Owner turn6 draws the second Research. It reveals Misty first and the second Mega Sharpedo ex next. Lucky Ice Pop heals Lapras50to70 and flips Heads, returning to hand; its second play heals70to90 and flips Tails, sending it away. Third Water goes to Lapras, whose Surf70 leaves Wailmer30HP. At the owner end-of-turn checkup, Soothing Shore heals Lapras90to110.

Computer turn7 uses X Speed, retreats the original Wailmer for2Water and promotes Baxcalibur. Wailmer keeps1Water. Ice Maker gives Active Baxcalibur1Water; the ordinary Water goes to left Wartortle. There is no attack. Shore heals benched Wailmer30to50. Owner turn8 draws Carvanha, benches it middle and attaches the first Water to right Ninetales. Surf70 leaves Baxcalibur70HP. Computer turn9 adds the second Water to Baxcalibur with Ice Maker and the second ordinary Water to Wartortle; a second Wailmer is benched middle. End checkup heals Baxcalibur70to90 and original Wailmer50to70. Owner turn10 draws Elegant Cape, evolves middle Carvanha to Mega Sharpedo ex, gives Ninetales its second Water and Surfs Baxcalibur90to20.

Computer turn11 uses its second Poke Ball for a concealed Basic, with no immediate bench play from that search. Ice Maker gives Baxcalibur its third Water; the ordinary third Water goes to Wartortle. Baxcalibur retreats for3Water and ends with0; fresh Wailmer becomes Active. Shore heals original Wailmer70to90. The damaged Baxcalibur remains20 because it has no Water attached. Owner turn12 draws the second Misty, attaches first Water to middle Sharpedo and Surfs fresh Wailmer100to30. Computer turn13 evolves Wartortle to Mega Blastoise ex, carrying3Water. Ice Maker gives Active Wailmer its first Water; the ordinary Water goes to original benched Wailmer, reaching2. Shore heals Active Wailmer30to50 and original Wailmer90to100.

Owner turn14 draws the second Carvanha and benches it left with1Water. Surf70 knocks out the fresh Wailmer50HP for owner point1. The computer promotes Mega Blastoise ex with3Water. Computer turn15 uses Ice Maker and the ordinary Water to take Mega Blastoise3to5Water. Triple Bombardment130 knocks out Lapras for computer point1. At five Water, there is no additional Bench damage. Auto selects the first Ninetales150HP with2Water as owner replacement Active.

Owner turn16 draws the second Vulpix, benches it right and evolves the left Carvanha into the second Mega Sharpedo ex. The normal Water goes to new Vulpix. Active Ninetales uses Binding Snow80, leaving Blastoise150HP and visibly restricting Energy Zone attachment to the opposing Active during computer turn17. On turn17, the computer attaches ordinary Water to benched original Wailmer, reaching3, and benches a second Frigibax left. Blastoise stays at5Water and attacks for130, leaving Active Ninetales20HP. There is again no Bench bonus. Shore heals Blastoise150to170.

Owner turn18 draws Cyrus. Auto starts evolving right Vulpix around290.8, before the default+1second candidate. The290.4native full frame and bottom crop preserve the fully joined seven-card start hand including Cyrus. After the evolution, Cyrus pulls damaged Baxcalibur20HP from middle Bench to Active and sends Blastoise to middle Bench. The old damaged Ninetales retreats for its2Water, promoting middle Sharpedo190HP with1Water. The ordinary Water attaches to the new right Ninetales, reaching2. Turbo Shark70 knocks out Baxcalibur and gives a Water from the Energy Zone to old benched Ninetales, which had0after retreat. Owner reaches2points. Blastoise returns Active. Shore heals old Ninetales20to40 because it now has Water.

Computer turn19 evolves left Frigibax to Arctibax, attaches the sixth ordinary Water to Active Blastoise, then evolves original right Wailmer to Wailord ex250HP with3Water. Triple Bombardment deals130to Active Sharpedo, leaving60HP. Its six-Water bonus deals50to each of the two selected benched Ninetales. Old Ninetales40HP is knocked out; new Ninetales150to100HP survives. The left benched Sharpedo190HP is not one of those two targets and remains intact. The old Ninetales knockout awards two points, taking computer1to3 and ending the game before any further checkup. The Defeat screen persists through the end of the source.

## Hand, Energy and result reconciliation

The nine named normal draws, in owner turn order2,4,6,8,10,12,14,16,18, are Ninetales, Lucky Ice Pop, Research, Carvanha, Elegant Cape, Misty, Carvanha, Vulpix and Cyrus. Research reveal order is separate from later hand order: turn2 Ninetales then Poke Ball; turn6 Misty then Sharpedo. Owner Poke Ball finds Vulpix at40seconds. Copycat and Irida are never played. Both Misty stay unused; no Misty flip or zero-heads action occurs. Elegant Cape is drawn and remains unused. Lucky Ice Pop has two distinct uses and distinct coin outcomes. No opened discard pile, Tool attachment, Special Condition, no-effect attempt or offered-and-declined Supporter warning is observed.

The owner start hand counts are5,6,6,7,7,7,8,8,7; the corresponding native computer fan counts are5,3,2,2,2,3,3,4,4. All computer normal/Research/search identities are null until public play. The fan counts rely on native upper views, not deck completion or card name inference. TURN_LEDGER.json preserves ordered names at each owner start and before the final ending action. Turn18 ends with five hand cards: Irida, Copycat, Misty, Elegant Cape and Misty.

Every board row preserves physical instances, slots, current/max HP, damage, typed attached Energy, Tools, conditions, effects, Stadium and points for both sides. Some board fields use directly observed public action continuity rather than claiming a single transition frame proves everything. Empty large current Energy slots are distinct from the small Water preview. Owner starts have generated Water available; several computer start anchors precede generation. Ordinary Water attachments are separate from Ice Maker and Turbo Shark. Retreat payments of2Water for Wailmer,3for Baxcalibur and2for owner Ninetales are recorded separately. The turn17 Binding Snow restriction and turn18 expiration are explicit.

Damage500 independently reconciles as five Lapras Surf attacks at70 each, Ninetales Binding Snow80 and Sharpedo Turbo Shark70. Owner points come from one regular Wailmer and one regular Baxcalibur knockout. Computer points come from Lapras1plus Ninetales ex2. The decisive old Ninetales40HP/50damage bench event, surviving Active Sharpedo60HP and final result screen establish the loss together. Neither supplied deck list establishes hidden actions.

## Coverage and limits

Every one of18grids spanning nominal0through356seconds was visually inspected, and targeted native frames/crops were inspected for opening, draws, all nine+1/+3/+6candidate sets, before-end hands, fan counts, boards, major effects and the final result. There are142native captures, with measured decoder PTS, hashes and lossless original-dimension lower20percent hand and upper fan crops. Eighteen captures remain within the shared160cap for independent exceptions. The reduced357sample one-fps scan locates events and is not presented as a frame-by-frame certificate or proof of a hidden touch. Actual decoded times are separate from requested seek seconds.

No discard pile is opened. Periodic turn4,8,12,16,18both-player unavailable records describe that recording limit; visible stack tops cannot certify a full pile. Exact action instants are approximate retained anchors. There is no material unresolved identity or result ambiguity requiring Astra. Full first-pass review is complete, while capture status is complete_with_recording_limits. Independent Sol acceptance is still required, and root alone registers or archives the original.
'''
import re
def readable(text):
 return '\n'.join(line if 'SHA256' in line or '.MP4' in line else re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',line)for line in text.split('\n'))
(P/'REVIEW.md').write_text(readable(review),encoding='utf-8')
locator=json.loads((P/'LOCATOR_PREPROCESSING.json').read_text(encoding='utf-8-sig'))
coverage='# Coverage: '+V+'\n\nSource SHA256: `'+SHA+'`. All recording intervals reviewed from the opponent selector through persistent Defeat screen,0to357.008333seconds.\n\n## Whole-source locator inspection\n\n'
for g in locator['grids']:coverage+='- '+Path(g).name+': visually inspected all panels.\n'
coverage+='''
The helper metadata's preprocessed_not_visually_reviewed label describes extraction, not this later inspection. This coverage receipt explicitly records all18grids as inspected. One actual full decode pass produced357nominal1fps source samples. Early available grids were assembled from the same decoded images, without another decode; the helper completed its normal final grids. Reduced grids locate events only. No second whole-source decoding or source hashing was performed.

## Native evidence

142native full frames and284lossless source-dimension crops are bound in EXTRACTION_MANIFEST.json. Requested seconds and measured selected decoded PTS are separate. Full frames1170x2532; lower crop[0,2025,1170,2532], upper crop[0,0,1170,550]. All draw-offset candidate sets and before-end views were directly inspected; setup, physical-instance evolution/damage/healing, energy/retreat, final sequence and result received targeted native inspection. TURN_EVIDENCE.json classifies the captures and rejects post-play candidates as original start hands. Turn18uses290.4fast preplay because291.4,293.4and296.4follow the first evolution.

## Source limits and completeness

Nine owner and ten computer real turns are serialized, including no-attack ending actions and automatic effects. Concealed computer identities stay null. No opened discard pile is filmed, so periodic markers are unavailable for both sides. No invisible warning response, touch or card printing identity is inferred. No interruption or recording gap is observed across the continuous overview course. Exact subsecond touch timings remain approximate.

First-pass whole battle review is complete. Capture supplement is complete_with_recording_limits. Independent acceptance is pending. Original SOURCE.json, ASSIGNMENT.json and movie are preserved. Shared index/events, external logs, archival, simulator and other packets were not changed by this worker. Routing is local only per ROUTING.json.
'''
(P/'COVERAGE.md').write_text(readable(coverage),encoding='utf-8')
(P/'TURN_TABLE.md').write_text(readable(turntable),encoding='utf-8')
core=['SOURCE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','TURN_TABLE.md','METRICS.json','EXTRACTION_MANIFEST.json','ROUTING.json','LOCATOR_PREPROCESSING.json']
save('SUBMISSION.json',{'source_video':V,'source_sha256':SHA,'model':'gpt-6.1-sol','effort':'high','reviewer':'drafta_auto_210952','complete_first_pass':True,'independent_accepted':False,'completed_utc':datetime.now(timezone.utc).isoformat(),'files':{n:hashlib.sha256((P/n).read_bytes()).hexdigest()for n in core}})
import sys
sys.path.insert(0,str(B))
from validate_packet import validate
check=validate(P)
save('WORKER_STRUCTURAL_CHECK.json',check)
print(json.dumps(check))
