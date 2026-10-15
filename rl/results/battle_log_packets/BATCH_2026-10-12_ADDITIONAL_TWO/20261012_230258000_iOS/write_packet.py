import json,copy,hashlib
from pathlib import Path
from PIL import Image
p=Path(__file__).resolve().parent
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'));v=src['video_basename'];sha=src['sha256'];gid='20261012_230258000_iOS_game_1'
live=json.loads((p.parent/'LIVE_DECK_SNAPSHOT.json').read_text(encoding='utf-8-sig'))
def save(n,x): (p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'F'+f'{t:07.2f}'.replace('.','_')
def refs(*ts):return [eid(t) for t in ts]
sources=[{'video_basename':v,'sha256':sha,'source_json':'SOURCE.json'}]
K='Kingambit';L='Lucky Ice Pop';M='Alolan Muk';R='Rare Candy';P='Pawniard';I='Ilima';Q='Professor’s Research';B='Poké Ball';G='Glimmora';g='Glimmet';A='Alolan Grimer';C='Copycat';Z='Mesagoza';H='Heavy Helmet'
roles={31.5:'opening_hand_before_active',48:'selected_preplay_hand',125:'selected_preplay_hand',201:'selected_preplay_hand',263:'selected_preplay_hand',302.2:'selected_preplay_hand',395:'selected_preplay_hand',494:'selected_preplay_hand_no_draw',87:'before_end_hand',147:'before_end_hand',212:'before_end_hand_attack_substitute',283:'before_end_hand',357:'before_end_hand',426:'before_end_hand_attack_substitute',497:'before_end_hand_attack_substitute'}
timings={1:(47.8,48,48.8,50.8,53.8,87,88),3:(124.6,125,125.6,127.6,130.6,147,147.5),5:(200,201,201,203,206,212,218),7:(262,263,263,265,268.5,283,284),9:(302,302.2,303,305,308,357,359),11:(394,395,395,397,400,426,432.5),13:(None,494,494,496,499,497,514)}
first={1:48.8,3:125.6,5:202,7:264,9:305,11:396,13:494.5}
for n,(de,chosen,c1,c3,c6,be,end) in timings.items():
 for t in (c1,c3,c6):roles[t]='draw_timed_candidate' if de else 'turn_start_candidate_no_draw'
 roles[chosen]='selected_preplay_hand' if de else 'selected_preplay_hand_no_draw'
frames=[]
for f in sorted((p/'turn_evidence').glob('t*.jpg')):
 if f.stem.endswith(('_top','_bottom')):continue
 t=float(f.stem[1:]);im=Image.open(f);w,h=im.size
 bot=f.with_name(f.stem+'_bottom.jpg');top=f.with_name(f.stem+'_top.jpg')
 if not bot.exists():im.crop((0,int(h*.8),w,h)).save(bot,quality=95)
 if not top.exists():im.crop((0,0,w,int(h*.31))).save(top,quality=95)
 n=next((n for n,times in timings.items() if t in times[1:]),None);de=timings[n][0] if n else None
 selected=n is not None and t==timings[n][1]
 suitable=selected or (n and t<first[n])
 frames.append({'evidence_id':eid(t),'role':roles.get(t,'native_action_or_board'),'turn_number':n,'who_played':'owner' if n else None,'source_video':v,'source_sha256':sha,'draw_animation_end_seconds':de,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':round(t-de,3) if n and de and t in timings[n][2:5] else None,'full_frame_path':str(f.relative_to(p)).replace('\\','/'),'native_dimensions':{'width':w,'height':h},'bottom_crop':{'path':str(bot.relative_to(p)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,int(h*.8),w,h]},'top_crop':{'path':str(top.relative_to(p)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,w,int(h*.31)]},'selected_for_start_hand':bool(selected),'before_first_play':bool(suitable) if n else None,'unzoomed':bool(selected) if n else None,'hand_spread':bool(selected) if n else None,'observation':'Native source-local frame; see ledger for its observed event.','suitability_or_limit':('Chosen hand before card/attachment commitment; candidate may show hand selection highlight.' if selected else 'Later draw-relative candidates cannot substitute for the chosen hand when an action or zoom has begun.' if n else 'Additional action/board evidence.')})
overview=[]
for f in sorted((p/'overview').glob('t*.jpg')):
 t=float(f.stem[1:]);im=Image.open(f)
 overview.append({'evidence_id':'O'+f'{t:07.2f}'.replace('.','_'),'source_video':v,'source_sha256':sha,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'path':str(f.relative_to(p)).replace('\\','/'),'dimensions':{'width':im.width,'height':im.height},'role':'reduced locating/action continuity; never native hand evidence'})
def cards(names,t):return [{'position':i+1,'name':n,'variant':None,'basis':'visible named hand slot','evidence_ids':refs(t),'limit_reason':None} for i,n in enumerate(names)]
def hand(names,t,basis='Observed named hand slots in native full frame and bottom crop'):
 return {'cards_left_to_right':cards(names,t),'count':len(names),'basis':basis,'evidence_ids':refs(t),'status':'observed','limit_reason':None}
def mon(name,hp,mx,energy=0,typ='Darkness',pos=None,tool='none',conditions=None,effects=None):
 return {'name':name,'variant':{'Regigigas':'Seal of Antiquity / Giga Turbo100','Glimmora':'Shattering Crystal / Venomous Hit30','Glimmet':'Hang Down20','Kingambit':'Overlord’s Blade60+','Alolan Muk':'Power of Alchemy / Sludge Bomb70','Alolan Grimer':'Sludge Toss30','Pawniard':'Slash30','Froakie':'Flop10, HP60','Staryu':'Smack20, HP50','Starmie ex':'Hydro Splash90, HP130','Greninja':'Water Shuriken20 / Mist Slash60, HP120'}.get(name),'bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'printed visible HP, no HP modifiers','damage':mx-hp if hp is not None else None,'attached_energy':{'total':energy,'by_type':{typ:energy} if energy else {}},'tool':tool,'special_conditions':conditions or [],'active_effects':effects or [],'evidence_ids':[],'status':'observed','limit_reason':'Semantic card version established; artwork/rarity not fully identified.'}
def reg(hp=150,e=0):return mon('Regigigas',hp,150,e,tool=H)
def gl(hp=90,e=0):return mon(G,hp,90,e)
def gm():return mon(g,60,60)
def fr(hp=60,e=0):return mon('Froakie',hp,60,e,'Water')
def st(e=0):return mon('Staryu',50,50,e,'Water')
def sx(hp=130,e=0):return mon('Starmie ex',hp,130,e,'Water')
def ki(hp=140,e=0):return mon(K,hp,140,e)
def mu(hp=110,e=0):return mon(M,hp,110,e,'Colorless')
def gr():return mon(A,70,70)
def pa():return mon(P,50,50)
def gn(e=0):return mon('Greninja',80,120,e,'Water')
# State transitions retain true Bench positions, including empty gaps.
states=[]
def state(oa,ob,xa,xb,op=0,xp=0):return {'owner_active':oa,'owner_bench':ob,'opponent_active':xa,'opponent_bench':xb,'owner_points':op,'opponent_points':xp}
r0=mon('Regigigas',150,150);states.append(state(r0,[gm(),None,None],fr(),[None,None,None]))
states.append(state(reg(),[gm(),None,gm()],fr(),[None,None,None]))
states.append(state(reg(),[gm(),None,gm()],fr(e=1),[None,None,fr()]))
states.append(state(reg(e=1),[gl(),None,gm()],fr(e=1),[None,None,fr()]))
states.append(state(gl(80),[reg(e=1),None,gm()],fr(e=1),[st(1),st(),fr()]))
poisonfr=fr(20,1);poisonfr['special_conditions']=['Poisoned']
states.append(state(gl(80,1),[reg(e=1),None,gm()],poisonfr,[st(1),st(),fr()]))
states.append(state(reg(e=1),[None,None,gm()],sx(e=2),[fr(20),sx(),fr()],0,1))
states.append(state(reg(e=2),[None,pa(),gl()],sx(e=2),[fr(20),sx(),fr()],0,1))
states.append(state(reg(80,2),[None,pa(),gl()],sx(e=2),[fr(20),sx(e=1),fr()],0,1))
states.append(state(reg(140,2),[gr(),ki(e=1),gl()],sx(e=2),[fr(20),sx(e=1),fr()],0,1))
states.append(state(reg(70,2),[gr(),ki(120,1),gl()],sx(e=2),[gn(),sx(e=2),fr()],0,1))
states.append(state(reg(90,3),[mu(e=1),ki(120,1),gl()],sx(30,2),[gn(),sx(e=2),fr()],0,1))
states.append(state(gl(),[mu(e=1),ki(120,1),None],sx(30,2),[gn(1),sx(e=2),fr()],0,2))
states.append(state(gl(e=1),[mu(e=1),ki(120,1),None],sx(e=2),[gn(1),None,fr()],2,2))
states.append(state(None,[gl(e=1),ki(120,1),None],sx(e=2),[gn(1),None,fr(e=1)],2,3))
starts=[48,92,126,152,201,223,263,286,304,362,395,436,494,516]
ends=[88,121,147.5,196,218,259,284,297.5,359,390,432.5,491,512,555]
def zone(typ,current,n,t):
 # The opponent-facing display supplies icons, not readable labeled counters.
 return {'this_turn':{'type':typ if current else None,'count':current,'available':bool(current) if current is not None else None},'next':{'type':typ,'count':None,'available':None},'basis':'Large generated-energy icon and empty circle distinguished from small next-energy icon in cited full frame. Next count has no numeric label.','evidence_ids':refs(t),'limit_reason':'Small next icon establishes type only. Count/availability of future Energy remain null; no turn-parity inference.'}
startcur=[(0,0),(0,1),(1,0),(0,1),(1,0),(0,1),(1,0),(0,1),(1,0),(0,1),(1,0),(0,1),(1,0),(0,1)]
endcur=[(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]
def board(idx,n,t,phase,cur):
 s=copy.deepcopy(states[idx]);b={'turn_number_displayed':n,'phase':phase,'stadium':'none' if idx==0 else Z,'owner':{},'opponent':{},'shared_effects':[],'evidence_ids':refs(t)}
 for who,typ in [('owner','Darkness'),('opponent','Water')]:
  a=s[who+'_active'];bench=s[who+'_bench']
  for i,x in enumerate(bench):
   if x:x['bench_position']=i+1
  ms=[x for x in [a]+bench if x]
  for x in ms:
   x['evidence_ids']=refs(t)
   if x['name']=='Regigigas':
    x['active_effects']=[{'name':'Seal of Antiquity attack restriction','source':'Regigigas','restriction':'Cannot attack without Regirock, Regice and Registeel on Bench','expiry':'while Ability applies'}] if idx<11 else [{'name':'Basic Ability suppressed','source':'Alolan Muk Power of Alchemy','expiry':'while Power of Alchemy applies'}]
    if x['tool']==H:x['active_effects'].append({'name':'Heavy Helmet','restriction':'20 less attack damage while retreat cost at least3','expiry':'while attached and condition met'})
   if idx>=11 and x['name'] in ['Alolan Muk','Froakie']:x['active_effects'].append({'name':'Basic Ability suppressed','source':'Alolan Muk Power of Alchemy','expiry':'while Power of Alchemy applies'})
  b[who]={'active':a,'bench_in_position_order':bench,'energy_zone':zone(typ,cur[0 if who=='owner' else 1],n,t),'points':s[who+'_points'],'board_effects':[{'name':'Power of Alchemy','source':'Alolan Muk','restriction':'Basic Pokemon in play have no Abilities','expiry':'while Alolan Muk in play'}] if idx>=11 else [],'evidence_ids':refs(t),'status':'observed','limit_reason':'An empty Bench position is represented by null; no Pokemon occupies it.'}
 return b
acts={}
def play(n,t,kind,name,target,result,energy=None,nested=None,response=None,prompt=None):
 a={'order':len(acts.setdefault(n,[]))+1,'kind':kind,'card_name':name,'target':target,'energy':energy,'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':None,'source_video':v,'timestamp_seconds':t,'evidence_ids':refs(t),'basis':'visible source action and resulting board/hand','limit_reason':None};acts[n].append(a);return a['order']
def attach(n,t,target,typ='Darkness'):
 return play(n,t,'energy_attachment',None,target,'One Energy attached; next icon remains distinct.',{'type':typ,'count':1,'destination':target,'retreat_payment_by_type':None})
def end(n,t,warn=False):return play(n,t,'prompt_response',None,None,'Ended turn without attack.',response='OK' if warn else 'End Turn',prompt='A Supporter card can be used' if warn else None)
play(1,49,'card_play',Q,'owner hand','Draw2: Poké Ball first, Heavy Helmet second.')
play(1,55,'card_play',B,'owner hand','Find Glimmet.')
play(1,63,'card_play',g,'Bench position3','Benched60HP.')
play(1,69,'tool_attachment',H,'Regigigas Active','Heavy Helmet attached; Regigigas remains150HP.')
play(1,78,'stadium',Z,'Stadium','Mesagoza replaces empty Stadium slot.')
play(1,81,'stadium_ability',Z,'owner hand','Heads; find Glimmora.',nested=[{'event':'heads','timestamp_seconds':84},{'event':'Glimmora revealed','timestamp_seconds':86}])
end(1,88)
play(2,95,'stadium_ability',Z,'opponent hand','Tails, no card found.')
play(2,103,'card_play',Q,'opponent hand','Two face-down cards drawn, identities unknown.')
play(2,109,'card_play','Froakie','Bench position3','Benched60HP.')
attach(2,119,'Froakie Active','Water');end(2,121)
play(3,126.5,'card_play',B,'owner hand','Find Pawniard, visible130.')
play(3,133,'evolution',G,'Glimmet Bench position1','Evolve to Glimmora90HP.')
play(3,138,'stadium_ability',Z,'owner hand','Heads; Alolan Muk revealed144.')
attach(3,146,'Regigigas Active');end(3,147.5)
play(4,156,'card_play',B,'opponent hand','Random Basic found face-down; identity remains unknown.')
play(4,162,'card_play','Staryu','Bench position1','Benched50HP; cannot equate it to earlier hidden search.')
play(4,169.5,'card_play','Sabrina','owner Active','Regigigas switched to Bench1; owner chooses Glimmora as newActive at172-175. No retreat payment.',nested=[{'event':'Owner compulsory replacement choice Glimmora','timestamp_seconds':172}])
attach(4,177,'Staryu Bench position1','Water')
play(4,181,'stadium_ability',Z,'opponent hand','Heads; face-down Pokemon found, identity unknown.')
play(4,191,'card_play','Staryu','Bench position2','Benched50HP; hidden search identity remains unknown.')
play(4,194,'attack','Froakie Flop','Glimmora Active','10 damage,90->80HP.')
play(5,203,'stadium_ability',Z,'owner hand','Tails; no Pokemon found.')
attach(5,209,'Glimmora Active')
play(5,212,'attack','Glimmora Venomous Hit','Froakie Active','30 damage60->30; Poison applied; checkup10 leaves20.')
play(6,226,'retreat',None,'Staryu Bench position1 becomesActive','Froakie retreats and recovers from Poison; oneWater discarded. Staryu carries its oneWater.',{'type':'Water','count':1,'destination':None,'retreat_payment_by_type':{'Water':1}})
play(6,232,'evolution','Starmie ex','Staryu Active','130HP, retainsWater1.')
play(6,237,'evolution','Starmie ex','Staryu Bench position2','130HP, Water0.')
attach(6,240,'Starmie ex Active','Water')
play(6,243,'attack','Starmie ex Hydro Splash','Glimmora Active','90 knocks out80HP. Shattering Crystal tails251 permits1opponentpoint. Owner promotes Regigigas259.',nested=[{'event':'Shattering Crystal tails','timestamp_seconds':251},{'event':'Opponent point1','timestamp_seconds':255},{'event':'Owner mandatory promotion Regigigas','timestamp_seconds':259}])
attach(7,265,'Regigigas Active')
play(7,269,'stadium_ability',Z,'owner hand','Heads272, Glimmora revealed275-277.')
play(7,277,'evolution',G,'Glimmet Bench position3','Glimmora90HP.')
play(7,281,'card_play',P,'Bench position2','Pawniard50HP.')
end(7,284)
attach(8,295,'Starmie ex Bench position2','Water')
play(8,296,'attack','Starmie ex Hydro Splash','Regigigas Active','90 reduced to70byHelmet;150->80HP.')
play(9,307,'stadium_ability',Z,'owner hand','Heads311, Alolan Grimer revealed312-313.')
play(9,315,'card_play',A,'Bench position1','70HP.')
play(9,318,'card_play',R,'Pawniard Bench position2','Rare Candy evolves Pawniard directly to Kingambit using handKingambit321;140HP.',nested=[{'event':'selectPawniard','timestamp_seconds':320},{'event':'Kingambit evolution','timestamp_seconds':321}])
play(9,328,'card_play',L,'Regigigas Active','Heal20,80->100. Tails332; discarded.')
play(9,335,'card_play',L,'Regigigas Active','Heal20,100->120. Heads341; returned tohand.')
play(9,347,'card_play',L,'Regigigas Active','Replay same returnedPop. Heal20,120->140. Heads353; returned tohand.')
attach(9,356,'Kingambit Bench position2')
end(9,358,True)
play(10,371,'card_play',R,'Froakie Bench position1','Rare Candy evolves damagedFroakie directly to Greninja.40damage carried:80/120HP.')
play(10,378,'ability','Greninja Water Shuriken','Kingambit Bench position2','20damage140->120HP.')
attach(10,387,'Starmie ex Bench position2','Water')
play(10,389,'attack','Starmie ex Hydro Splash','Regigigas Active','Helmet reduces90to70;140->70HP.')
play(11,397,'evolution',M,'Alolan Grimer Bench position1','Alolan Muk110HP. Power of Alchemy suppresses BasicAbilities, including Regigigasattackrestriction.',nested=[{'event':'BasicPokemoninplayhavenoAbilitiesnotice','timestamp_seconds':400}])
play(11,404,'card_play',L,'Regigigas Active','Heal20,70->90HP. Tails410; discarded.')
attach(11,414,'Regigigas Active')
play(11,417,'card_play',C,'owner hand','Shuffle soleIlima into one-card deck; draw Research thenIlima. Only2cardsavailable although opponentfan3. Endhand2.',nested=[{'event':'Ilima shuffled','timestamp_seconds':419},{'event':'Research revealed','timestamp_seconds':422},{'event':'Ilima revealed','timestamp_seconds':423}])
play(11,428,'attack','Regigigas Giga Turbo','Starmie ex Active','100damage130->30HP; generateColorless1 and attach to Alolan MukBench1 at432.',nested=[{'event':'100damage','timestamp_seconds':429},{'event':'chooseMukforattackEnergy','timestamp_seconds':431},{'event':'ColorlessattachedMuk','timestamp_seconds':432}])
play(12,441,'card_play',Q,'opponent hand','Two face-down cards drawn; both identitiesunknown.')
attach(12,457,'Greninja Bench position1','Water')
play(12,460,'ability','Greninja Water Shuriken','Regigigas Active','20damage90->70HP, not reducedbyattack-onlyHelmet.')
play(12,479,'attack','Starmie ex Hydro Splash','Regigigas Active','Helmet reduces90to70, exactly knocksout70HP. Opponentpoint2; owner promotesGlimmora491.')
attach(13,495,'Glimmora Active')
play(13,499,'attack','Glimmora Venomous Hit','Starmie ex Active','30damage knocksout30HP; Poisonnotice brieflyappears duringresolution. Owner earns2points505-507; opponent promotes secondStarmie ex511. No separatePoison10 is needed/observed to causeKO.')
play(14,529,'ability','Greninja Water Shuriken','Alolan Muk Bench position1','20damage110->90HP.')
play(14,539,'card_play','Cyrus','Alolan Muk damagedBench','Opponent chooses damagedMuk toActive. Glimmora movesBench1 withDarkness1. Forcedswitch, no retreatpayment.')
attach(14,542,'Froakie Bench position3','Water')
play(14,547,'attack','Starmie ex Hydro Splash','Alolan Muk Active','90damage exactly knocksout90HP. Opponentpoint3 at553; Defeat558 andfinal5642-3/14turns/160damage.')
def draw(kind,name,t,playorder=None,caused=None):return {'kind':kind,'caused_by':caused,'linked_play_order':playorder,'cards_in_reveal_order':[{'name':name,'reveal_position':1,'source_video':v,'timestamp_seconds':t,'evidence_ids':refs(t),'basis':'named visible reveal' if name else 'opponent face-down reveal','limit_reason':None if name else 'Hidden opponent card identity'}],'hand_count_before':None,'hand_count_after':None,'returned_or_discarded_cards':None,'source_video':v,'timestamp_seconds':t,'evidence_ids':refs(t),'limit_reason':None if name else 'Hidden opponent identity'}
draws={1:[draw('normal_draw',L,47),draw('supporter_draw',B,52,1,Q),draw('supporter_draw',H,53,1,Q),draw('search',g,58,2,B),draw('search',G,87,6,Z)],3:[draw('normal_draw',B,124.5),draw('search',P,130,1,B),draw('search',M,143,3,Z)],5:[draw('normal_draw',R,199)],7:[draw('normal_draw',L,262),draw('search',G,277,2,Z)],9:[draw('normal_draw',I,301),draw('search',A,313,1,Z)],11:[draw('normal_draw',C,393),draw('supporter_draw',Q,422,4,C),draw('supporter_draw',I,423,4,C)],13:[]}
for n,t in [(2,92),(4,152),(6,223),(8,284),(10,362),(12,436),(14,516)]:draws[n]=[draw('normal_draw',None,t)]
draws[2]+=[draw('supporter_draw',None,105,2,Q),draw('supporter_draw',None,111,2,Q)]
draws[4]+=[draw('search',None,159,1,B),draw('search',None,188,5,Z)]
draws[12]+=[draw('supporter_draw',None,443,1,Q),draw('supporter_draw',None,446,1,Q)]
hs={1:[Z,K,Q,L],3:[K,L,G,B],5:[K,L,P,M,R],7:[K,L,P,M,R,L],9:[K,L,M,R,L,I],11:[M,I,L,C],13:[Q,I]}
he={1:[K,L,G],3:[K,L,P,M],5:[K,L,P,M,R],7:[K,L,M,R,L],9:[M,I,L],11:[Q,I],13:[Q,I]}
fans={1:4,3:5,5:4,7:3,9:4,11:3,13:4}
auto={5:[{'event':'Poison checkup10','target':'opponent Froakie','hp_before':30,'hp_after':20,'timestamp_seconds':218,'evidence_ids':refs(218)}],6:[{'event':'Glimmora KO, ShatteringCrystal tails, opponentpoint1, Regigigasmandatorypromotion','timestamp_seconds':251,'evidence_ids':refs(251,255,259)}],11:[{'event':'GigaTurboColorless1 attachedMuk as nestedattackeffect','timestamp_seconds':432,'evidence_ids':refs(431,432)}],12:[{'event':'RegigigasKO, opponentpoint2, Glimmorapromotion','timestamp_seconds':491,'evidence_ids':refs(481,487,491)}],13:[{'event':'Normal draw unavailable: no cardsleftindeck','timestamp_seconds':494,'evidence_ids':refs(494)},{'event':'StarmieexKO, owner2points, opponentStarmieexpromotion','timestamp_seconds':511,'evidence_ids':refs(503,506,510,514)}],14:[{'event':'MukKO, opponentpoint3,Defeat','timestamp_seconds':553,'evidence_ids':refs(548,553,558,564)}]}
turns=[]
for n in range(1,15):
 owner=n%2==1;chosen=timings[n][1] if owner else starts[n-1];be=timings[n][5] if owner else ends[n-1]
 acting=hand(hs[n],chosen) if owner else {'cards_left_to_right':None,'count':None,'basis':'Opponent hand identities hidden','evidence_ids':refs(chosen),'status':'hidden','limit_reason':'Only fan and public reveals recorded; no exact private hand reconstruction.'}
 turns.append({'turn_number':n,'who_played':'owner' if owner else 'opponent','source_video':v,'timing':{'turn_start_seconds':[45,89,123,149,197,219,260,284,299,360,391,433,492,513][n-1],'draw_animation_end_seconds':timings[n][0] if owner else None,'first_voluntary_move_seconds':acts[n][0]['timestamp_seconds'],'before_end_action_seconds':be,'end_after_resolution_seconds':ends[n-1]},'hand_at_start':acting,'owner_hand_start':acting if owner else {'status':'not_applicable','cards_left_to_right':None,'count':None,'basis':'Opponent turn','evidence_ids':[],'limit_reason':'Owner-name hand requirement applies on owner turns.'},'opponent_hand_at_owner_turn_start':{'count':fans[n] if owner else None,'supported_range':None,'count_method':'Native top crop, count separate visible backs','basis':'observed fan' if owner else 'not applicable','evidence_ids':refs(chosen) if owner else [],'limit_reason':None if owner else 'Not an owner turn'},'draws_and_searches':draws[n],'plays_in_order':acts[n],'automatic_events_in_order':auto.get(n,[]),'board_at_start':board(n-1,n,starts[n-1],'afterdraw/generation beforecommitment; hand evidence may use earlierframe',startcur[n-1]),'board_after':board(n,n,ends[n-1],'after endingaction and consequences including requiredreplacement',endcur[n-1]),'owner_hand_before_end_action':hand(he[n],be) if owner else {'status':'not_applicable','count':None,'evidence_ids':[]},'owner_hand_end':hand(he[n],be,'Native before-end hand confirmed by post-action hand; attacks do not remove handcards.') if owner else {'status':'not_applicable','count':None,'evidence_ids':[]},'discard_snapshot_ids':['owner_unopened','opponent_unopened'],'turn_evidence_ids':refs(chosen,be,starts[n-1],ends[n-1]),'limits':['Opened discard piles are never shown. Opponent hidden draw/search identities remain null. Source seeks approximate eventtimes; actualframePTS not measured.']})
limits=['Neither player opens a discard pile; periodic complete pile snapshots unavailable throughout the supplied source.','Opponent face-down draws/searches remain unknown; later plays do not identify prior finds.','Semantic versions are established; artwork/rarity not fully identified.','Future Energy count/availability has no readable labeled numerical display and remains null despite visible next-type icon.','Turn13 has no normaldraw animation because deck is empty; native turn-start hand substitutes with explicit notice.','Later +1/+3/+6 candidate frames may show played cards/zooms; only the chosen earlier preplay hand supplies startingidentities.','Source timestamps are requested local seeks; exact framePTS not measured.']
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'turns':turns,'limits':limits})
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'source_sha256':sha,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':.2,'top_crop':'Top31percent includes clocks/fan/EnergyZone','fixed_grid_is_turn_start_evidence':False},'frames':frames,'overview_frames':overview,'discard_snapshots':[{'snapshot_id':who+'_unopened','turn_number':None,'pile_owner':who,'source_video':v,'timestamp_seconds':None,'cards_in_view':None,'scroll_coverage':'not shown','full_pile_established':False,'evidence_ids':[],'limit_reason':'No opened pile view anywhere in full recording; public top discard cards/actions are not full-pile snapshots.'} for who in ['owner','opponent']],'scheduled_capture_limits':limits})
save('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':sources,'deck_name_in_log':live['deck_label'],'source_url':live['source_url'],'captured_at':live['retrieved_utc'],'expected_card_count':20,'actual_card_count':20,'cards_in_log_order':live['cards_in_log_order'],'counts_by_name_and_variant':live['counts_by_name_and_variant'],'energy_configuration_from_log':'Darkness','capture_source_text_or_image':'../LIVE_DECK_SNAPSHOT.json','game_version_binding_basis':'Native1.5sQR byte-exactly matches live snapshot; QR_DECODE.json','exact_list_status':'verified_live_log_snapshot_and_matching_filmed_QR','qr_payload':live['qr_payload'],'conflicts_with_filmed_cards':[],'limits':['Semantic versions established; artwork/rarity not fully verified.']})
save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'review_date':'2026-10-12','sources':sources,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':live['deck_label'],'opening':{'source_video':v,'timestamp_seconds':31.5,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':cards([Z,K,'Regigigas',g,Q],31.5),'selected_active':{'name':'Regigigas','opening_position':3,'source_video':v,'timestamp_seconds':34,'evidence_ids':refs(31.5,34,35)},'setup_bench':[{'name':g,'position':1,'timestamp_seconds':41,'evidence_ids':refs(41,42)}],'redraw_or_replacement':[],'before_active_placement':True,'status':'observed','evidence_ids':refs(31.5),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'full_source_review_ready_for_independent_acceptance','source_game_count':1,'outcome':{'result':'loss','owner':'Dacz8976','opponent':'Giorno','owner_points':2,'opponent_points':3,'turns_played':14,'damage_done':160,'method':'Opponent third point from Starmie ex Hydro Splash KO of Alolan Muk','evidence_ids':refs(548,553,558,564)},'limits':limits,'lead_checked':False})
save('SUMMARY.json',{'source_video':v,'source_sha256':sha,'reviewer':'/root/pause_20261012_230258000_iOS','actual_worker_task':'/root/later_230258','model':'gpt-6.1-sol','reasoning_effort':'high','review_date':'2026-10-12','scope':'Entire0-564.253356source, one completehumanmatch','classification':'human','auto_control_visible':False,'queue_label':None,'owner':'Dacz8976','opponent':'Giorno','turn_order':'owner first','source_game_count':1,'turn_count':14,'result':'loss','owner_points':2,'opponent_points':3,'ending_method':'Opponent third point from MukKO, not inabilitytodraw','damage_done':160,'capture_status':'complete_with_recording_limits','deck_snapshot':'DECK_USED.json','qr_match':True,'limits':limits,'independent_acceptance_pending':True,'external_writes_performed':False})
save('UNCERTAINTIES.json',{'source_video':v,'source_sha256':sha,'unreviewed_intervals':[],'material_unresolved_events':[],'recording_limits':limits,'mode_limit':'Matchmaking and visibleopponent establishhumanbattle; specificqueue notdisplayed. NoAuto control in supplied footage.','artwork_rarity_limit':'QR matchessemanticlist; no assertionofexactartworkorrareprint forhidden cards.','opponent_hidden_searches':[{'turn':4,'timestamps':[159,188],'identities':None,'reason':'Face-downcards; subsequentStaryu plays are not identificationevidence.'}],'copycat_limit':'Opponentfan3 but only2availablecards; namedResearch422/Ilima423 andendinghand2 established. Exact shuffleddeck order is hidden.'})
lines=['# Full source review: '+v,'','Reviewer: /root/pause_20261012_230258000_iOS. Actualworker: /root/later_230258. Model: gpt-6.1-sol, highreasoning. Reviewdate: October12,2026. FrozenSHA-256: `'+sha+'`.','', 'One human match against Giorno. Dacz8976 went first and lost2-3 in14 turns. Native564seconds confirms Defeat,14turns,2ownerpoints,3opponentpoints and160damage. Starmie ex earned the finalpoint by knocking out damaged Alolan Muk. The emptydeck notice at493-495seconds prevents a draw but does not endthegame. No Auto control is visible. Specificqueue is notdisplayed. Independentleadacceptance, registration, archival andliveentry are outsideworkerwrites.','', 'Setup0-44seconds: filmedNewdeck16 andnativeQR1.5seconds match the batchlive20-card Darkness snapshot exactly. Opening31.5seconds, lefttoright: Mesagoza, Kingambit, Regigigas, Glimmet, Professor’s Research. Regigigas selectedActive34-35; Glimmet benchedleft41. OpponentActiveFroakie60. No redrawshown. Semanticversions are established; artwork/rarity remainslimited.','', '| Turn | Player | Source seconds | Complete action account |','|---|---|---|---|']
for tr in turns:
 n=tr['turn_number'];descr=' '.join(str(a['order'])+'. '+(a['card_name'] or a['kind'])+': '+a['result'] for a in tr['plays_in_order'])
 if n in hs:descr='Normaldraw: '+(draws[n][0]['cards_in_reveal_order'][0]['name'] if n!=13 else 'none, explicitemptydeck notice')+'. '+descr+' Endinghand '+str(len(he[n]))+'.'
 lines.append(f'| {n} | {tr["who_played"]} | {tr["timing"]["turn_start_seconds"]}-{tr["timing"]["end_after_resolution_seconds"]} | {descr} Ledger row {n}; native evidence F{starts[n-1]:07.2f}, F{ends[n-1]:07.2f}. |')
lines+=['','Decisive mechanics and observations:','', '- Regigigas cannot attack while Seal of Antiquity applies because the requiredthreeRegis are absent. Alolan Muk evolution397-400 suppresses BasicAbilities and removes thatrestriction. Actual GigaTurbo428-430 confirms the changedeligibility. HeavyHelmet remainsattached, reducing HydroSplash90to70 but not Greninja’s abilitydamage.','- Turn11Copycat417 shuffles soleIlima into the remainingone-carddeck. Research422 thenIlima423 are the onlytwodraws. Opponentfan has3cards; no thirdcard identity is invented. Handends2. GigaTurbo generatesColorlessEnergy, chosenforMuk431 andattached432. LaterMukActive544 visiblyhasColorless1; Kingambit retainsDarkness1.','- Turn9LuckyIcePop threeuses heal80->100->120->140. Firsttails332 discards; nextheads341 returns; replayheads353 returns. The Supporterwarning358 is explicitly confirmedOK, declining useofavailableSupporter. LuckyIcePop cardinspection303 is not a cardplay.','- OpponentSabrina169.5 forces the firstswitch; owner selectsGlimmora. OpponentCyrus539 forces the finaldamagedMukswitch. Neither is a paidretreat. OpponentFroakie226 doesretreat, discardingWater1 and recoveringPoison.','- Turn13VenomousHit30 knocksout the30HPStarmieex for2points. A Poisonnotice duringanimation is recorded, but no extra10Poisondamage is inventedasKOcause. Fresh secondStarmieex promotes511 and winsnextturn.','', 'Capture supplement:','', 'TURN_LEDGER.json has exactly14rows with bothboards, trueBenchpositions, HP/damage/Energy/Tools/effects/points, namedhands, numberedplays andnormal/research/search/Copycat reveals. TURN_EVIDENCE.json catalogs nativefullframes andbottom-fifth/topcrops plus separatelymarked reducedoverviewframes. Ownerdraw ends are estimatedfrom dense sourceinspection; candidates approximate+1/+3/+6 and laterplayed/zoomed views are markedunsuitable forstartinghand. Clearer earlier nativehands are selected beforecommitment. Turn13 has no drawanimation and records its explicitemptydeck substitute.','', 'Opponentfan counts at ownerturnstarts: T1=4, T3=5, T5=4, T7=3, T9=4, T11=3, T13=4. Separate cardbacks are countedfromnative topcrops. Neitherplayer opens a discardpile anywhere; unopenedpile limits are explicit instead of inventingcompletecontents. SmallnextEnergy icons establishtype, not futurecount/availability. All exacttimestamps are requestedsource-local seeks, not measuredframePTS.','', 'Reviewcoverage is completeforavailablefootage; capturecompleteness is complete_with_recording_limits. Hiddenopponentcards, unopeneddiscards and exactprintings remainunknown. Deckidentity uses frozenliveQRmatching, not guessedhandmembership.']
(p/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(p/'COVERAGE.md').write_text('# Source coverage\n\nFrozen source: '+v+'; SHA-256 '+sha+'.\n\nReviewed the entire0-564.253356seconds. One game; no splitclip or additionalmatch. Setup0-44, all14turns45-555, decisive thirdpoint553, Defeat558 andresults564 covered.\n\n|Phase|Coverage|\n|---|---|\n|Deck and filmedQR0-3|Native1.5/2QRdecoded andmatchedlive20slots.|\n|Matchmaking4-28|HumanGiorno profile; noAutooption.|\n|Opening29-44|Fivecards31.5, selectedRegigigas, benchGlimmet.|\n'+''.join(f'|Turn{n}|{[45,89,123,149,197,219,260,284,299,360,391,433,492,513][n-1]}-{ends[n-1]}seconds, numberedplays andbothboards; ledgerrow{n}.|\n' for n in range(1,15))+'|Terminal555-564.253356|Defeat andfinal14turns/2-3/160damage.|\n\nReduced2-second locatingframes plus boundednativeframes support continuity. Native draw-relative candidates andchosenpreplayhands retained. Fullcoverage is not aclaim ofhiddeninformation or exactsimulatorreplay. Neitherdiscardpile opened. Unreviewedintervals:none. Leadacceptancepending.\n',encoding='utf-8')
print('Wrote8 final review files,',len(turns),'turns and',len(frames),'nativeframes')
