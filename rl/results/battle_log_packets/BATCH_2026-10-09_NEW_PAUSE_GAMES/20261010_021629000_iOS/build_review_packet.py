from pathlib import Path
import json,copy,hashlib
p=Path(__file__).parent
gid=p.name;video=gid+'.MP4';sha='c6780bc6ef6fe89e7db6ccee1f4d06e3ff3b0bc8a9db488a76345b5a46ee185d'
source=[{'video_basename':video,'sha256':sha,'source_json':'SOURCE.json'}]
def save(n,x): (p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def eid(t): return f'E_{t:07.2f}'
def refs(t):
 q=p/'turn_evidence'/f't{t:07.2f}.jpg'
 return [eid(t)] if q.exists() else [f'D_{4*round(t/4):07.2f}']
W="Team Rocket’s Weezing ex";K="Team Rocket’s Koffing";R="Professor’s Research";S="Soothing Shore";C="Rare Candy";B="Poké Ball";G="Kingdra ex";H="Horsea";D="Seadra";I="Indeedee ex";N="Snorlax ex"
limits=[
 {'id':'L1','scope':'whole source','limit':'Review uses explicit bounded sought frames and every-turn four-second overview, with native targeted transitions. No continuous real-time playback or sub-frame timing was measured. Requested source seeks are approximate timestamps; actual decoded presentation timestamps are unset.'},
 {'id':'L2','scope':'hidden information','limit':'Opponent hand names, normal draw identities and search results are hidden. Counted backs are direct fan observations, not identities. No complete discard pile was opened; top cards and recorded plays cannot establish an exhaustive pile.'},
 {'id':'L3','scope':'turn 4 start','limit':'Poké Ball normal draw is identifiable in animation but is played before a clear unzoomed six-card fan. Five retained cards plus this named draw establish composition and count; sixth fan position is not claimed from a clear view.'},
 {'id':'L4','scope':'turns 6,8,12,14,16,18','limit':'First voluntary move follows the draw within about one second. Required +1/+3/+6 captures therefore include played or zoomed hands. Earlier native pre-move frames are separately selected. The grid alone is not start-hand evidence.'},
 {'id':'L5','scope':'turns 20,22,24 and late opponent turns','limit':'Empty-deck notice appears; there is no successful normal draw and no draw-animation-end timestamp. Captures are instead tied to the visible turn-start notice. No card identity is fabricated.'},
 {'id':'L6','scope':'turn 17','limit':'Network waiting message and Lucky Ice Pop coin remain on screen approximately 584-644s. No unrecorded action is reconstructed. Turn ends after waiting without a visible attack; intent to decline attack or manually End Turn is unknown.'},
 {'id':'L7','scope':'opponent turn 1 / Lucky Ice Pop','limit':'First Professor’s Research is established by its visible discard top at 61-67s and two back-only draw animations early in turn 1. Exact click time and opponent draw identities are unknown. Lucky Ice Pop coin face/return on turn 15 is not securely established; turn 17 ends with it visible on the discard top.'},
 {'id':'L8','scope':'board phases','limit':'board_after is the resolved post-checkup state before the next draw, rather than the attack impact alone. Printed effects and action events separately preserve transient Burn, Sleep and healing. Exact first-turn opponent generated Energy availability is visibly empty.'},
 {'id':'L9','scope':'deck identity','limit':'Live log has the exact 20 slots and printed set identifiers. Filmed QR matches semantic identities and Water Energy. In-game artwork differs for some copies; set/artwork variants are not inferred from QR and no unshown opponent deck slots are guessed.'},
]
opening=['Hiking Trail',H,W,C,'Small Balloon']
ownerhands={2:['Hiking Trail',W,C,'Small Balloon',G],4:['Hiking Trail',W,C,'Small Balloon',G,B],6:[W,H,D,W],8:[D,W,'Copycat'],10:['Sabrina',S,C,W],12:[S,C,W,G],14:[S,C,W,K],16:[S,C,W,B],18:[S,C,R],20:[S,C,R],22:[S,C,R],24:[S,C,R]}
endhands={2:ownerhands[2],4:[W,H,D],6:[D,W],8:['Sabrina',S,C],10:[S,C,W],12:[S,C,W],14:[S,C,W],16:[S,C],18:[S,C,R],20:[S,C,R],22:[S,C,R],24:[S,C,R]}
fan={2:4,4:2,6:2,8:3,10:4,12:4,14:5,16:2,18:3,20:3,22:3,24:3}
starts=[43,63,81,106,153,183,219,251,281,315,355,388,419,438,463,513,563,659,689,724,747,782,803,847,869]
ends=[62,78,105,152,182,218,250,280,314,354,387,418,437,462,512,562,658,684,724,746,781,802,846,868,882]
drawends={2:66,4:107,6:186,8:254,10:318,12:390,14:443,16:516,18:661,20:None,22:None,24:None}
selected={2:67,4:107.3,6:186,8:254,10:319,12:389.5,14:442.5,16:516.5,18:661,20:725,22:782,24:848}
preend={2:74,4:136,6:206,8:268,10:342,12:400,14:448,16:538,18:674,20:734,22:788,24:851}
normal={2:(G,64),4:(B,106),6:(W,184),8:('Copycat',252),10:(W,316),12:(G,389),14:(K,441),16:(B,514),18:(R,660)}
opnext={2:'Psychic',4:'Water',6:'Water',8:'Water',10:'Water',12:'Water',14:'Water',16:'Psychic',18:'Water',20:'Water',22:'Psychic',24:'Psychic'}
opcurrent={1:None,3:'Psychic',5:'Water',7:'Water',9:'Water',11:'Water',13:'Water',15:'Water',17:'Psychic',19:'Water',21:'Water',23:'Psychic',25:'Psychic'}
def hand(names,t,basis='Direct native hand view with named draw/play continuity',limit=None):
 return {'cards_left_to_right':[{'position':None if limit and i==5 else i+1,'name':n,'basis':basis,'evidence_ids':refs(t),'limit_reason':limit if i==5 else None} for i,n in enumerate(names)],'count':len(names),'basis':basis,'evidence_ids':refs(t),'status':'observed_with_limits' if limit else 'observed','limit_reason':limit}
def mon(name,id,hp,e=0,pos=None,tool=None,conds=None,variant=None):
 mx={H:50,D:70,G:170,K:60,W:140,I:130,N:160}[name]
 energy={'Water':e} if isinstance(e,int) and e else (e if isinstance(e,dict) else {})
 return {'name':name,'instance_id':id,'variant':variant,'bench_position':pos,'hp_now':hp,'hp_max':mx,'hp_max_basis':'Printed card and displayed undamaged HP in footage','damage':mx-hp,'attached_energy':{'total':sum(energy.values()),'by_type':energy},'tool':tool,'special_conditions':conds or [],'active_effects':[],'evidence_ids':[],'status':'observed_with_transition_continuity','limit_reason':None}
def ownerstate(t):
 # End of turn state; A is first Horsea/Kingdra, B is second Horsea/Kingdra.
 if t<4: return mon(H,'A',50,1 if t>=2 else 0),[]
 hpA=[170]*9+[40,60,60,80,80,100,100,120,120,140,10,30,30,50,0,0,0][t] if False else {4:170,5:170,6:170,7:170,8:170,9:40,10:60,11:60,12:80,13:80,14:100,15:100,16:120,17:120,18:140,19:10,20:30,21:30,22:50,23:0,24:0,25:0}[t]
 ea=2 if t<14 else 3
 if t in [12,13]: ea=2
 a=mon(G,'A',hpA,ea)
 left=mon(K if t<6 else W,'W1',60 if t<6 else 140,1 if t>=18 else 0,1,'Small Balloon',variant='factory illustration when evolved')
 b=None
 if t>=6:
  bn=H if t<8 else D if t<12 else G
  hb=50 if t<8 else 70 if t<12 else {12:170,13:170,14:170,15:170,16:170,17:170,18:170,19:170,20:170,21:40,22:60,23:60,24:80,25:0}[t]
  eb=1 if t<8 else 2 if t<10 else 3
  if t in [16,17]:eb=4
  b=mon(bn,'B',hb,eb,2,variant='second copy; shiny Kingdra artwork when evolved')
 right=mon(K if t<16 else W,'W2',60 if t<16 else 140,1 if t>=24 else 0,3,variant='shiny Weezing artwork when evolved') if t>=14 else None
 activeB=t in list(range(12,18))+[20,21,23,24]
 active=b if activeB else a
 if t==25:active=None
 bench=[left]
 if t<23:bench.append(a if activeB else b)
 if right:bench.append(right)
 bench=[x for x in bench if x is not None];
 for x in bench:
  if x['instance_id'] in ['A','B']:x['bench_position']=2
 if active:active['bench_position']=None
 return active,bench
ophp={0:160,1:160,2:150,3:160,4:90,5:160,6:60,7:130,8:50,9:120,10:70,11:150,12:60,13:140,14:50,15:150,16:50,17:140,18:60,19:130,20:50,21:120,22:40,23:110,24:30,25:30}
def oppstate(t):
 original=t<10
 e1={} if t<3 else {'Psychic':1,'Water':min(3,(t-3)//2)}
 e1={k:v for k,v in e1.items() if v}
 e2={} if t<11 else {'Water':min(4,(t-9)//2)}
 if t>=17:e2['Psychic']=1
 cond=['Poisoned'] if t in [6,7,8,9] or t>=16 else []
 if t in [9,23,25]:cond.append('Asleep')
 tool='Heavy Helmet' if original or t>=15 else 'Small Balloon' if t>=11 else None
 a=mon(N,'S1' if original else 'S2',ophp[t],e1 if original else e2,tool=tool,conds=cond)
 bench=[]
 if t>=3:
  bench=[mon(I,'I1',130,{'Psychic':1} if t>=23 else {},1,variant='full illustration'),mon(I,'I2',130,{},2,variant='regular illustration')]
  h=160 if original else 120 if t==10 else 140 if t in [11,12] else 160
  bench.append(mon(N,'S2' if original else 'S1',h,{} if original else e1,3,None if original else 'Heavy Helmet'))
 return a,bench
def zone(typ,count,nxt,phase): return {'this_turn':{'type':typ,'count':count,'available':bool(count)},'next':{'type':nxt,'count':1 if nxt else None,'available':False},'basis':'Visible large current and small next Energy icons; values separately marked at phase','evidence_ids':[],'limit_reason':None if nxt else 'Small next icon not independently fixed for this sampled phase'}
def board(t,phase,playing,start=False):
 state=max(0,t-1) if start else t
 oa,ob=(mon(H,'A',50),[]) if state==0 else ownerstate(state)
 pa,pb=oppstate(state)
 nxtop=opnext.get(t) if playing=='owner' else (None if start else opnext.get(t+1))
 ownerz=zone('Water' if playing=='owner' and start else None,1 if playing=='owner' and start else 0,'Water',phase)
 oc=opcurrent.get(t) if playing=='opponent' else None
 available=playing=='opponent' and t!=1 and (start or t in [21,25])
 opz=zone(oc if available else None,1 if available else 0,nxtop,phase)
 for m in [oa,pa]+ob+pb:
  if m:m['evidence_ids']=refs(selected.get(t,starts[t-1]) if start else ends[t-1])
 if pa and state%2==0 and state>=4:pa['active_effects']=['Stormy Prison: cannot retreat during next opponent turn; clears after that turn']
 stadium=None if state<1 else 'Hiking Trail' if state==4 else S
 return {'turn_number_displayed':t,'phase':phase,'stadium':stadium,'owner':{'active':oa,'bench_in_position_order':ob,'energy_zone':ownerz,'points':0,'board_effects':[],'evidence_ids':refs(starts[t-1] if start else ends[t-1]),'status':'observed_with_transition_continuity','limit_reason':None},'opponent':{'active':pa,'bench_in_position_order':pb,'energy_zone':opz,'points':3 if state==25 else 2 if state>=23 else 0,'board_effects':[],'evidence_ids':refs(starts[t-1] if start else ends[t-1]),'status':'observed_with_transition_continuity','limit_reason':None},'shared_effects':['Shore heals 20 at end of each player turn to that player’s Pokemon with at least two Energy'] if stadium==S else ['At end of each player turn, Hiking Trail draws until three cards'] if stadium else [],'evidence_ids':refs(starts[t-1] if start else ends[t-1])}
actions={
1:[(45,'supporter',R,None,'Two hidden card-back draws; visible Research discard top at 61-67s. Exact play instant bounded early turn.'),(54,'stadium',S,'shared','Stadium established'),(58,'tool','Heavy Helmet','S1','Attached; reduces attack damage 20')],
2:[(69,'energy','Water','A','Attach 1 Water'),(76,'attack','Hook','S1','30 printed; Helmet reduces to 10; S1 160 to 150')],
3:[(84,'energy','Psychic','S1','Attach 1 Psychic'),(86,'item',B,None,'Hidden search; result identity not revealed'),(92,'bench',N,'bench 3','Place S2'),(96,'bench',I,'bench 2','Place I2'),(100,'bench',I,'bench 1','Place I1'),(104,'ability','Watch Over','S1','Heal 20, capped at 160')],
4:[(108,'item',B,None,'Search visibly reveals Team Rocket’s Koffing at 113s'),(116,'bench',K,'bench 1','Place W1'),(120,'item',C,'A','Evolve Horsea directly to Kingdra ex at 124s'),(130,'tool','Small Balloon','W1','Attach to Koffing'),(134,'stadium','Hiking Trail','shared','Replace opposing Soothing Shore'),(137,'energy','Water','A','Attach 1; total 2 Water'),(141,'attack','Stormy Prison','S1','Helmet reduces 90 to 70; 160 to 90; retreat lock')],
5:[(156,'stadium',S,'shared','Replace Hiking Trail'),(160,'energy','Water','S1','Attach 1; Water1 Psychic1'),(164,'ability','Watch Over','S1','Heal20'),(168,'ability','Watch Over','S1','Heal20')],
6:[(187,'evolve',W,'W1','Evolve Koffing; Boiler Smog offered'),(193,'ability','Boiler Smog','S1','Owner accepts Yes; opponent Active Poisoned and Burned'),(200,'bench',H,'bench 2','Place B'),(204,'energy','Water','B','Attach 1 Water'),(207,'attack','Stormy Prison','S1','70 after Helmet; then Poison10 and Burn20; 60 HP after checkup')],
7:[(224,'ability','Watch Over','S1','Heal20'),(232,'ability','Watch Over','S1','Heal20'),(236,'energy','Water','S1','Attach1; Water2 Psychic1')],
8:[(255,'evolve',D,'B','Evolve Horsea to Seadra'),(260,'supporter','Copycat',None,'Shuffle remaining shiny Weezing into deck; draw three named cards'),(269,'energy','Water','B','Attach1; total2 Water'),(272,'attack','Stormy Prison','S1','70 plus Poison10; 130 to 50')],
9:[(286,'energy','Water','S1','Attach1; Water3 Psychic1'),(288,'ability','Watch Over','S1','Heal20'),(292,'ability','Watch Over','S1','Heal20'),(296,'attack','Flop-Down Punch','A','130 damage; A170 to40; Snorlax becomes Asleep')],
10:[(330,'supporter','Sabrina','opponent Active','Opponent promotes S2 at336s; S1 moves bench3; Poison and Sleep removed'),(340,'energy','Water','B','Attach1; total3 Water'),(346,'attack','Stormy Prison','S2','90; 160 to70; retreat lock')],
11:[(360,'ability','Watch Over','S2','Heal20'),(364,'ability','Watch Over','S2','Heal20'),(368,'energy','Water','S2','Attach1 Water'),(376,'tool','Small Balloon','S2','Attach')],
12:[(391,'evolve',G,'B','Seadra evolves to second Kingdra'),(395,'energy','Water','A','Attach1; A2 to3 Water'),(398,'retreat',G,'A to bench2; B to Active','A pays1 Water: pre3, after2. B retains3. Retreat menu and one-energy payment visible at398; post at400/418.'),(408,'attack','Stormy Prison','S2','90; 150 to60')],
13:[(420,'energy','Water','S2','Attach1; total2 Water'),(424,'ability','Watch Over','S2','Heal20'),(428,'ability','Watch Over','S2','Heal20')],
14:[(443,'bench',K,'bench3','Place W2'),(447,'energy','Water','A on bench2','Attach1; A2 to3 Water'),(452,'attack','Stormy Prison','S2','90; 140 to50')],
15:[(470,'item','Lucky Ice Pop','S2','Heal20:50 to70; return coin face not securely established'),(476,'ability','Watch Over','S2','Heal20'),(480,'ability','Watch Over','S2','Heal20'),(484,'energy','Water','S2','Attach1; total3 Water'),(492,'supporter',R,None,'Two hidden draws'),(500,'tool','Heavy Helmet','S2','Replace Small Balloon; card inspected visibly')],
16:[(517,'item',B,None,'No target: There are no cards in the deck that can be the target of the effect. No card gained.'),(524,'evolve',W,'W2','Evolve right Koffing'),(531,'ability','Boiler Smog','S2','Owner selects Yes; Poisoned and Burned'),(540,'energy','Water','B','Attach1; B3 to4 Water'),(544,'attack','Stormy Prison','S2','Helmet reduces to70; Poison10 and Burn20; 150 to50')],
17:[(569,'energy','Psychic','S2','Attach1; Water3 Psychic1'),(576,'ability','Watch Over','S2','Heal20'),(580,'ability','Watch Over','S2','Heal20'),(584,'item','Lucky Ice Pop','S2','Heal20; prolonged coin/network wait to644s; card visible on discard top648s')],
18:[(663,'supporter',R,None,'One remaining card visibly drawn: regular Professor’s Research. No second card shown; deck then empty.'),(668,'retreat',G,'B to bench2; A to Active','B pays1 Water: pre4 at667 payment menu, post3 at670. A retains3.'),(672,'energy','Water','W1 left bench','Attach1; 0 to1 Water, left Weezing'),(676,'attack','Stormy Prison','S2','70 plus Poison10; 140 to60')],
19:[(692,'ability','Watch Over','S2','Heal20'),(696,'ability','Watch Over','S2','Heal20'),(700,'energy','Water','S2','Attach1; Water4 Psychic1'),(704,'attack','Flop-Down Punch','A','130; A140 to10; Snorlax Asleep')],
20:[(726,'retreat',G,'A to bench2; B to Active','A pays1 Water: pre3 at724/725, payment726/728, after2 at729/732. B retains3.'),(733,'energy','Water','A on bench2','Attach1 to benched first Kingdra: 2 to3. Native734 zone empty, native738 A three Water. This is a separate visible attachment, not an assumed transfer.'),(736,'attack','Stormy Prison','S2','70 plus Poison10;130 to50')],
21:[(750,'ability','Watch Over','S2','Heal20'),(756,'ability','Watch Over','S2','Heal20'),(760,'attack','Flop-Down Punch','B','130; B170 to40; Snorlax Asleep')],
22:[(783,'retreat',G,'B to bench2; A to Active','B pays1 Water: pre3 at782, retreat menu/payment784-786, after2 before attachment. A retains3.'),(788,'energy','Water','B on bench2','Attach1 to benched second Kingdra: 2 to3. Native788 attachment motion/zone consumed; native790/794 post counts. Do not collapse with retreat payment.'),(792,'attack','Stormy Prison','S2','70 plus Poison10;120 to40')],
23:[(808,'ability','Watch Over','S2','Heal20'),(812,'ability','Watch Over','S2','Heal20'),(814,'energy','Psychic','I1 left bench','Attach1 Psychic'),(820,'attack','Flop-Down Punch','A','130; A50 knocked out; opponent takes2 points'),(830,'replacement',G,'B to Active','Owner promotes second Kingdra with60HP; first Kingdra and its stack leave board')],
24:[(849,'energy','Water','W2 right bench','Attach1;0 to1 Water, right Weezing'),(852,'attack','Stormy Prison','S2','Helmet reduces to70;110 to40 then Poison10 to30')],
25:[(872,'attack','Flop-Down Punch','B','130; B80 knocked out; opponent reaches terminal3 points at880s')]
}
def makeplays(t):
 out=[]
 for n,(tm,kind,name,target,result) in enumerate(actions[t],1):
  ene={'type':name if kind=='energy' else None,'count':1 if kind=='energy' else None,'destination':target if kind=='energy' else None,'retreat_payment_by_type':{'Water':1} if kind=='retreat' else None}
  hc={2:[5,5],4:[6,5,3,2,1,1,1],6:[3,3,2,2,2],8:[2,3,3,3],10:[3,3,3],12:[3,3,3,3],14:[3,3,3],16:[3,2,2,2,2],18:[3,3,3,3],20:[3,3,3],22:[3,3,3],24:[3,3]}.get(t)
  nested=[{'order':1,'kind':'ability offered after evolution','name':'Boiler Smog','response':'Yes','resolution_play_order':n+1}] if kind=='evolve' and name==W else []
  out.append({'order':n,'kind':kind,'card_name':name,'target':target,'energy':ene,'result':result,'prompt_text':'Use Boiler Smog?' if name=='Boiler Smog' else None,'response':'Yes' if name=='Boiler Smog' else None,'nested_events_in_order':nested,'hand_count_after':hc[n-1] if hc else None,'source_video':video,'timestamp_seconds':tm,'evidence_ids':refs(tm),'basis':'Visible animation/card/board transition; approximate seek timestamp; hand size reconciled from named public removals/additions and ending native view','limit_reason':'Opponent hidden hand and click instant unknown' if t%2 else None})
 return out
def draw(kind,cause,cards,ts,link=None,before=None,after=None,ret=None,limit=None):
 return {'kind':kind,'caused_by':cause,'linked_play_order':link,'cards_in_reveal_order':[{'name':n,'reveal_position':i+1,'source_video':video,'timestamp_seconds':tt,'evidence_ids':refs(tt),'basis':'Named owner face visible' if n else 'Hidden opponent card back','limit_reason':None if n else 'Identity not revealed'} for i,(n,tt) in enumerate(zip(cards,ts))],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':ret,'source_video':video,'timestamp_seconds':ts[0] if ts else None,'evidence_ids':refs(ts[0]) if ts else [],'limit_reason':limit}
turns=[];last_hand=opening[:1]+opening[2:]
for t in range(1,26):
 who='owner' if t%2==0 else 'opponent';plays=makeplays(t);draws=[]
 if t%2==0:
  if t in normal:
   n,tm=normal[t];draws.append(draw('normal_draw','turn start',[n],[tm],before=len(last_hand),after=len(last_hand)+1))
  else:draws.append(draw('normal_draw_failed','empty deck',[],[],before=3,after=3,limit='Visible empty deck notice; no successful draw.'))
  if t==4:
   draws.append(draw('search',B,[K],[113],1,5,6));draws.append(draw('stadium_draw','Hiking Trail',[H,D],[148,150],5,1,3))
  if t==8:draws.append(draw('supporter_draw','Copycat',['Sabrina',S,C],[266,267,268],2,1,3,[{'name':W,'destination':'deck','count':1}]))
  if t==16:draws.append(draw('search_failed',B,[],[],1,3,3,limit='No eligible Basic Pokemon; explicit no-target notice520s.'))
  if t==18:draws.append(draw('supporter_draw',R,[R],[666],1,2,3,limit='Only one remaining card is visibly gained, not two.'))
  hs=hand(ownerhands[t],selected[t],limit=limits[2]['limit'] if t==4 else None);he=hand(endhands[t],ends[t-1]);last_hand=endhands[t]
  oppfan={'count':fan[t],'supported_range':[fan[t],fan[t]],'count_method':'Direct count of visible opponent card backs in selected native top/fan view','basis':'Native top crop and selected fan grid; separate from arithmetic','evidence_ids':refs(selected[t]),'limit_reason':'Card identities hidden'}
 else:
  draws.append(draw('normal_draw' if t<19 else 'normal_draw_failed','turn start',[None] if t<19 else [],[starts[t-1]+1] if t<19 else [],limit='Opponent draw identity hidden' if t<19 else 'Empty deck notice; no gained card'))
  if t in [1,15]:draws.append(draw('supporter_draw',R,[None,None],[47,49] if t==1 else [494,496],1 if t==1 else 5,limit='Opponent draws hidden; turn1 exact play instant bounded by discard continuity'))
  if t==3:draws.append(draw('search',B,[None],[88],2,limit='Opponent found Basic identity not shown; later placements are not attributed to search.'))
  hs=hand(last_hand,starts[t-1]);he=hand(last_hand,ends[t-1]);oppfan={'count':None,'supported_range':None,'count_method':'Not applicable: opponent turn','basis':None,'evidence_ids':[],'limit_reason':'Required fan snapshots are at owner starts'}
 auto=[]
 if t>=3 and t%2: auto.append('Snorlax Full-Mouth Manner heals20 at end of its own turn, capped at160.')
 if t>=5: auto.append('Soothing Shore heals20 to ending player’s Pokemon with at least2 Energy; capped at printed maxHP.')
 if t in [6,16]:auto+=['Poison10 plus Burn20 during checkup. Burn coin recovers Burn; Poison remains.']
 elif t in [7,8,9] or 17<=t<=24:auto+=['Poison10 during checkup on opponent Snorlax.']
 if t in [9,19,21,23,25]:auto+=['Flop-Down Punch makes attacking Snorlax Asleep.']
 if t in [19,21,24]:auto+=['Observed heads Sleep recovery after checkup.']
 if t==23:auto+=['Sleep tails; Snorlax remains Asleep.']
 if t==4:auto+=['Hiking Trail draws Horsea then Seadra, raising owner hand1 to3.']
 if t==25:auto+=['Terminal Defeat screen follows; no subsequent turn.']
 ts=drawends.get(t)
 turns.append({'turn_number':t,'who_played':who,'source_video':video,'timing':{'turn_start_seconds':starts[t-1],'draw_animation_end_seconds':ts,'first_voluntary_move_seconds':actions[t][0][0],'before_end_action_seconds':preend.get(t,actions[t][-1][0]-1),'end_after_resolution_seconds':ends[t-1]},'hand_at_start':hs if who=='owner' else {'cards_left_to_right':None,'count':None,'basis':'Opponent names hidden','evidence_ids':refs(starts[t-1]),'status':'hidden','limit_reason':'Not owner-visible'},'owner_hand_start':hs,'opponent_hand_at_owner_turn_start':oppfan,'draws_and_searches':draws,'plays_in_order':plays,'automatic_events_in_order':auto,'board_at_start':board(t,'post normal draw / before first play',who,True),'board_after':board(t,'resolved end including checkup / before next draw',who),'owner_hand_end':he,'discard_snapshot_ids':[f'DISC_{t}_{q}' for q in ['owner','opponent']] if t in [4,8,12,16,20,24] else [],'turn_evidence_ids':refs(selected.get(t,starts[t-1]))+refs(ends[t-1]),'limits':['Hidden opponent identities and full discard contents remain unset.']+(['Required timed captures follow immediate first move; earlier selected native frame supplements them.'] if t in [6,8,12,14,16,18] else [])})
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':source,'turns':turns,'limits':limits})
pg={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'review_date':'2026-10-09','sources':source,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'Kingdra ex / Team Rocket’s Weezing ex','opening':{'source_video':video,'timestamp_seconds':28,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':n,'basis':'Visible five-card hand before placement','evidence_ids':[eid(28)],'limit_reason':None} for i,n in enumerate(opening)],'selected_active':{'name':H,'opening_position':2,'source_video':video,'timestamp_seconds':30,'evidence_ids':[eid(28),'D_0032.00']},'redraw_or_replacement':None,'before_active_placement':True,'status':'observed','evidence_ids':[eid(28)],'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'whole_source_first_review_complete_pending_independent_acceptance','outcome':{'owner':'Dacz8976','opponent':'けい','opponent_level':60,'owner_order':'second','result':'loss','points_owner':0,'points_opponent':3,'turns':25,'damage_dealt_owner':840,'result_evidence':[eid(882),eid(892)],'match_date_local':'2026-10-09','classification':'human','auto_control_seen':False,'mode':'human match, ladder/unranked selector not fixed from this recording'},'limits':limits,'lead_checked':False}
save('PAUSE_GAME.json',pg)
frames=[]
rolemap={}
for t in range(2,25,2):
 for offset in [1,3,6]:
  base=drawends[t] if drawends[t] is not None else selected[t]
  tm=base+offset
  rolemap.setdefault(tm,[]).append((t,f'draw_end_plus_{offset}' if drawends[t] is not None else f'empty_deck_notice_plus_{offset}'))
 rolemap.setdefault(selected[t],[]).append((t,'selected_start_hand'))
 rolemap.setdefault(preend[t],[]).append((t,'before_end_action'))
for fp in sorted((p/'turn_evidence').glob('t*.jpg')):
 if '_hand' in fp.name or '_top' in fp.name:continue
 tm=float(fp.stem[1:]);roles=rolemap.get(tm,[]);turn=roles[0][0] if roles else next((i+1 for i,(a,b) in enumerate(zip(starts,ends)) if a<=tm<=b),None)
 de=drawends.get(turn);selectedflag=turn in selected and selected[turn]==tm
 frames.append({'evidence_id':eid(tm),'role':[r for _,r in roles] or ['targeted_transition_or_resolution'],'turn_number':turn,'who_played':None if turn is None else 'owner' if turn%2==0 else 'opponent','source_video':video,'source_sha256':sha,'draw_animation_end_seconds':de,'requested_source_seconds':tm,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':tm-de if de is not None else None,'full_frame_path':str(fp.relative_to(p)).replace('\\','/'),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':'turn_evidence/'+fp.stem+'_hand.jpg','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':'turn_evidence/'+fp.stem+'_top.jpg','pixel_bounds_x0_y0_x1_y1':[0,0,1170,850]},'selected_for_start_hand':selectedflag,'before_first_play':selectedflag and (turn!=4),'unzoomed':selectedflag and turn!=4,'hand_spread':selectedflag and turn!=4,'observation':'See turn row; preserved native full and crops. Early selected frame supersedes played/zoomed timed candidates.','suitability_or_limit':'Turn4 drawn Poké Ball already enlarged; no unzoomed six-card hand.' if turn==4 and selectedflag else 'Retained targeted frame; full native pixels do not imply reviewer inspected every full frame. Actual viewed surfaces listed separately.'})
discard=[]
for t in [4,8,12,16,20,24]:
 for q in ['owner','opponent']:discard.append({'snapshot_id':f'DISC_{t}_{q}','turn_number':t,'pile_owner':q,'source_video':video,'timestamp_seconds':ends[t-1],'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'evidence_ids':refs(ends[t-1]),'status':'not_shown','limit_reason':'No discard overlay opened. Visible top card/recorded plays cannot establish full pile.'})
missing=[{'turn':t,'requested_seconds':tm,'role':r,'limit':'Native capture not yet extracted'} for tm,rr in rolemap.items() for t,r in rr if not (p/'turn_evidence'/f't{tm:07.2f}.jpg').exists()]
for f in frames:
 t=f['turn_number'];tm=f['requested_source_seconds']
 if t:
  f['before_first_play']=tm<actions[t][0][0]
  if any('plus_' in r for r in f['role']) and not f['before_first_play']:
   f['suitability_or_limit']='Already at/after first voluntary move; cannot establish start hand. Earlier selected frame or explicit turn4 limit used.'
 if not f['selected_for_start_hand']:
  f['unzoomed']=None;f['hand_spread']=None
overview=[{'evidence_id':f'D_{float(q.stem[1:]):07.2f}','role':'four-second action overview only, not native hand capture','source_video':video,'source_sha256':sha,'requested_source_seconds':float(q.stem[1:]),'path':str(q.relative_to(p)).replace('\\','/'),'dimensions':{'width':390,'height':844},'actual_frame_seconds_if_measured':None} for q in sorted((p/'detailed').glob('t[0-9]*.jpg'))]
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':gid,'sources':source,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':.2,'top_crop':'opponent fan, clocks and Energy Zone; native pixel bounds retained','fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]},'frames':frames,'overview_frames':overview,'discard_snapshots':discard,'scheduled_capture_limits':missing+limits})
save('UNCERTAINTIES.json',{'game_id':gid,'sources':source,'items':limits,'blocking_for_outcome':False,'blocking_for_full_hidden_state':True,'unknowns_not_guessed':['opponent exact20','opponent hidden hand/draw/search identities','unshown discard contents','Lucky Ice Pop turn15 coin result','precise decoded frame presentation timestamps','unranked/ranked selector']})
save('SUMMARY.json',{'schema':'battle-review-summary-v1','game_id':gid,'sources':source,'reviewer_role':'fresh whole-source Sol reviewer','whole_source_reviewed':True,'source_duration_seconds':892.645,'game_count':1,'covered_turns':list(range(1,26)),'classification':'human','auto_control_seen':False,'auto_enabled':None,'owner_choices':'visible owner inputs','owner':'Dacz8976','opponent':'けい','opponent_level':60,'match_date_local':'2026-10-09','owner_deck_core':[G,W],'opponent_deck_core':[N,I],'outcome':'loss','score':'0-3','result_seconds':[882,892],'turns':25,'owner_damage':840,'pause_game_capture_status':'complete_with_recording_limits','exact_deck_snapshot':'DECK_USED.json','review_complete':True,'independent_acceptance':'pending','safe_to_archive':False,'external_write_performed':False,'uncertainties':'UNCERTAINTIES.json'})
save('RELATED_GAME_PACKETS.json',{'source_video':video,'source_sha256':sha,'game_count':1,'games':[{'game_number':1,'packet':'.','start_seconds':12,'end_seconds':892.645,'turn_count':25,'outcome':'loss'}],'other_games_found':False})
viewed=['qr_intake/t0002.00.jpg','scout/scout.jpg','detailed/early.jpg']+[f'detailed/temp_{i:02}.jpg' for i in range(1,26)]+[f'turn_evidence/preview_{i:02}.jpg' for i in range(1,6)]+[f'turn_evidence/hand_sheet_{i:02}.jpg' for i in range(6,16)]+['turn_evidence/SELECTED_TOP_FANS.jpg','turn_evidence/EARLY_ACTIONS.jpg']
full=[24,28,67,105,108,110,113,118,126,136,206,254,268,328,398,418,661,663,666,670,724,728,731,738,782,786,788,846,848,850,852,854,47,49,99,101]
viewed += [f'turn_evidence/t{t:07.2f}.jpg' for t in full if (p/'turn_evidence'/f't{t:07.2f}.jpg').exists()]
viewed += ['turn_evidence/t0067.00_top.jpg','turn_evidence/t0442.50_top.jpg']
entries=[]
for f in dict.fromkeys(viewed):
 q=p/f
 if q.exists():entries.append({'path':f,'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'view_method':'tool-rendered image inspected','scope':'Native full frame' if '/t' in f and '_top' not in f else 'Grid/crop of explicit source frames; not continuous playback'})
save('ACTUAL_VIEW_MANIFEST.json',{'source_video':video,'source_sha256':sha,'review_model':'gpt-6.1-sol','review_effort':'high','entries':entries,'extra_sheet_history':[{'generation':'first41extra sought frames','viewed':'extra_sheet_01 through05; files subsequently regenerated by second23frame batch; original native component frames retained','component_seek_manifest':'Native t*.jpg names; selected evidence and ledger preserve timestamps','original_grid_hash':'not retained before regeneration; not represented as currently byte-verified grid'},{'generation':'second23 early actions and T18offsets','viewed':['extra_sheet_01','extra_sheet_02','extra_sheet_03'],'combined_full_grid':'EARLY_ACTIONS.jpg','note':'extra_sheet_01 was regenerated again for731; all23 native component frames and EARLY_ACTIONS retained'},{'generation':'third single731','viewed':'native full731 separately inspected','note':'Latest extra_sheet_01 is not separately claimed viewed'}],'excluded_from_claim':'Retained captures and overview files not listed were not claimed individually viewed. Grid views are recorded as grids, not all original full-frame views.'})
review=f'''# Whole-source review: {video}

One continuous human game is visible, ending in an explicit Defeat. Dacz8976 went second against けい (level 60), using Kingdra ex / Team Rocket’s Weezing ex against Snorlax ex / Indeedee ex. The results screen shows 0-3, 25 turns and 840 damage dealt. No Auto control was seen during the reviewed source. The ranked/unranked selector is not established. Recording UTC identity maps to October 9, 2026 in Chicago, per the batch date verification.

The filmed QR at 2s matches the exact live 20-slot deck recorded in DECK_USED.json, including Water-only Energy. Continuity from that QR through deck search, setup and the match is visible. Live log identity is filmed-qr-b649812c0d42; the current shared snapshot has 25 decks. No complete opponent list is inferred.

Opening at 28s, before active placement: Hiking Trail, Horsea, Team Rocket’s Weezing ex, Rare Candy, Small Balloon. Horsea is selected Active. This is a five-card opening, with no visible redraw. The owner’s first turn is turn 2.

The first Horsea hits into Heavy Helmet for10. Rare Candy makes the first Kingdra on turn4, followed by repeated Stormy Prison. Hiking Trail briefly replaces Soothing Shore and draws Horsea then Seadra at148/150s; opponent replaces it with Soothing Shore on turn5. Boiler Smog is visibly accepted on turns6/16, applying Poison and Burn. Burn recovers after those checkups; Poison persists. Copycat on turn8 returns one Weezing and reveals Sabrina, Soothing Shore, Rare Candy in order. Sabrina on turn10 replaces the poisoned original Snorlax with the spare; retreat clears the original conditions.

Owner makes the second Kingdra on turn12 and alternates Active Kingdra to spread damage. The opponent uses two Watch Over abilities, Full-Mouth Manner, Soothing Shore and Lucky Ice Pop to repeatedly recover. Heavy Helmet replaces the spare Snorlax’s Small Balloon on turn15. The second owner Poké Ball on turn16 explicitly fails for lack of an eligible target. Professor’s Research on turn18 gains exactly one remaining card, another Research, leaving the deck empty. Turns20/22/24 therefore have an empty-deck notice rather than a successful normal draw.

All four owner retreats are one-Water payments. Turn12: first Kingdra A has3 Water after395s attachment, pays1 at398s, remains benched with2 at418s; second Kingdra B has3 and becomes Active. Turn18: B has4 at667s payment menu, pays1 and retains3 at670s; A retains3. Turn20: A has3 at724/725s, pays1 at726/728s, then visibly receives that turn’s Water on the bench at733/734s, restoring3 at738s. Turn22: B starts3 at782s, pays1 at783-786s, then visibly receives Water on the bench at788s, restoring3 in the post view. These are separate attachment and retreat events, not inferred transfers. The left Weezing gets Water on turn18; the right Weezing gets Water on turn24.

Flop-Down Punch deals130 on turns9/19/21/23/25. First Kingdra is knocked out on turn23 for2 points, leaving second Kingdra at60 HP Active. It attacks on turn24 and Shore raises it to80, while Poison leaves opponent Snorlax at30. Sleep recovers before turn25. The final130 attack knocks out second Kingdra and ends the game at3 points. Both benched Weezing remain visible. Owner never knocks out an opponent.

The displayed840 damage reconciles to Hook10, three Helmet-reduced70 attacks on turns4/6/8, three90 attacks on turns10/12/14, and five70 attacks on turns16/18/20/22/24. Poison and Burn are recorded separately as checkup events.

TURN_LEDGER.json contains one row for every turn1-25 with ordered plays, named owner normal/Research/Copycat/search draws, both boards, HP, typed Energy, tools, conditions, Stadium, points and Energy Zones. TURN_EVIDENCE.json retains native1170x2532 frames and native bottom/top crops. Selected early frames supplement +1/+3/+6 candidates where a move begins immediately. Turn4 has no clear unzoomed six-card start fan; its separately named Poké Ball draw is preserved without claiming that fan position. The late empty-deck turns use notice-timed captures and null draw-end timestamps.

No discard pile is opened anywhere reviewed. Periodic rows on turns4/8/12/16/20/24 explicitly say not shown, with unknown contents. Opponent card identities behind the fan remain unknown. Turn17 includes a prolonged network wait during Lucky Ice Pop; no hidden actions or intent are reconstructed. Exact decoded frame PTS were not measured. Source-local seek seconds are approximate. UNCERTAINTIES.json preserves these limits.

This is the first whole-source reviewer packet, pending the independent acceptance and root registration gate. No external artifact, shared index, event log, simulator, other backlog or source file was changed by this reviewer. Source archival is not authorized by this packet alone.
'''
review+='\n| Turn | Player | Source seconds | Ordered actions and resolved outcome | Ledger and evidence |\n|---|---|---|---|---|\n'
for row in turns:
 t=row['turn_number'];acts='; '.join(f"{x['order']}. {x['card_name']} ({x['kind']}): {x['result']}" for x in row['plays_in_order'])
 tm=selected.get(t,starts[t-1]);ev=f'turn_evidence/t{tm:07.2f}.jpg' if (p/'turn_evidence'/f't{tm:07.2f}.jpg').exists() else f'detailed/t{4*round(tm/4):07.2f}.jpg'
 review+=f"| {t} | {row['who_played']} | {starts[t-1]}-{ends[t-1]} | {acts} | [TURN_LEDGER row {t}](TURN_LEDGER.json), [chosen frame]({ev}) |\n"
(p/'REVIEW.md').write_text(review,encoding='utf-8')
coverage='''# Coverage and actual inspection

Source binding: 20261010_021629000_iOS.MP4, SHA256 c6780bc6ef6fe89e7db6ccee1f4d06e3ff3b0bc8a9db488a76345b5a46ee185d, duration892.645s, native1170x2532.

0-40s: filmed QR, continuous deck selection/search, opponent identity, five-card pre-placement setup. 43-882s: all25 turns covered by explicit4-second overview sought frames from32 through888, dense native owner draw/hand snapshots, and targeted native transition views. 882-892.645s: terminal score and explicit Defeat screen. The source has exactly one game; no game_02 is required.

Viewed detailed/temp_01 through25 are rendered frame grids, not continuous playback. Native crops were inspected separately for start-hand reading. EARLY_ACTIONS.jpg targets turn1 Research/Stadium/tool and turn3 hidden search/bench placements. Selected native full frames target Stadium, named draws, retreat payments, late bench Energy attachments and terminal transitions. ACTUAL_VIEW_MANIFEST.json lists the images actually inspected; retained unviewed captures are not represented as individually inspected full frames.

TURN_EVIDENCE.json contains native frames with exact crop pixel bounds and requested seeks. Actual decoded presentation timestamps remain null. 25 individual turn rows, with start and resolved end boards, are in TURN_LEDGER.json. End-of-turn board includes healing and checkup, so transient attack HP/status is separately captured in plays and automatic events.

Known recording limits: turn4 Poké Ball played before a clear six-card fan; immediate post-draw moves on6/8/12/14/16/18 make later timed candidates unsuitable; late turns have no successful draw; all opponent hidden names and exhaustive discard contents unknown; approximately584-644s network waiting. No recording gap was filled with guessed play. Independent reviewer still required before acceptance or archive.
'''
(p/'COVERAGE.md').write_text(coverage,encoding='utf-8')
print('Wrote packet; nativeframes',len(frames),'turns',len(turns),'missing_native_schedule',len(missing))
