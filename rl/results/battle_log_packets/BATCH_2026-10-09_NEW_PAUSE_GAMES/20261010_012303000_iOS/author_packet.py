import json,copy,re
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from PIL import Image
P=Path(__file__).resolve().parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'));V=S['video_basename'];H=S['sha256'];G='20261010_012303000_iOS_game1'
sources=[{'video_basename':V,'sha256':H,'source_json':'SOURCE.json'}]
def save(name,data): (P/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'F'+f'{t:07.2f}'.replace('.','')
def refs(*ts):return [eid(t) for t in ts]
def card(name,variant,hp,maxhp,energy=None,pos=None,tool=None,conditions=None,effects=None,ts=46.5):
 energy=energy or {};return {'name':name,'variant':variant,'bench_position':pos,'hp_now':hp,'hp_max':maxhp,'hp_max_basis':'Visible printed HP and unchanged tool modifiers','damage':maxhp-hp,'attached_energy':{'total':sum(energy.values()),'by_type':energy},'tool':tool,'special_conditions':conditions or [],'active_effects':effects or [],'evidence_ids':refs(ts),'status':'observed','limit_reason':None}
def nac(hp=70,pos=None,ts=46.5):return card('Nacli','Headbutt20',hp,70,pos=pos,ts=ts)
def tim(e=0,pos=None,ts=67):return card('Timburr','Corkscrew Punch20',60,60,{'Fighting':e} if e else {},pos=pos,ts=ts)
def cg(hp=150,f=0,c=0,pos=None,poison=False,ts=130):return card('Conkeldurr','Guts / Mega Punch80',hp,150,{k:v for k,v in {'Fighting':f,'Colorless':c}.items() if v},pos=pos,conditions=['Poisoned'] if poison else [],effects=['Guts: attack-damage KO coin check'] if hp else [],ts=ts)
def ns(ts=185):return card('Naclstack','Rock Throw50',110,110,pos=1,ts=ts)
def gd(hp=90,f=1,ts=319):return card('Gurdurr','Strength40',hp,90,{'Fighting':f},ts=ts)
def cb(hp=70,f=3,poison=False,ts=388):return card('Conkeldurr','Bedrock Breaker100; discard a Stadium',hp,150,{'Fighting':f},conditions=['Poisoned'] if poison else [],ts=ts)
def ga(ts=388):return card('Garganacl','Blessed Salt / Land Crush90',150,150,pos=1,effects=['Blessed Salt: heal10 from each owner Pokemon during Pokemon Checkup; no terminal checkup shown'],ts=ts)
def opp(hp=170,d=0,tool=False,bench=False,nd=0,zd=0,ts=46.5,removed=False):
 a=None if removed else card('Mega Absol ex','Darkness Claw80 / Mega Evolution ex rule:3points',hp,170,{'Darkness':d} if d else {},tool='Poison Barb' if tool else None,ts=ts)
 b=[card('Nihilego','More Poison / New Wave30',70,70,{'Darkness':nd} if nd else {},pos=1,effects=['More Poison: opponent Active takes +10 Poison damage; displayed at104.5s'],ts=ts),card('Zorua','Ascension',60,60,{'Darkness':zd} if zd else {},pos=3,ts=ts)] if bench else []
 return a,b
def ez(typ,available,ts):return {'this_turn':{'type':typ if available else None,'count':1 if available else 0,'available':available},'next':{'type':typ,'count':1,'available':True},'basis':'Direct current large Energy circle and small next symbol. Empty current circle recorded as no available Energy; next is displayed, not inferred from deck.','evidence_ids':refs(ts),'limit_reason':None}
def board(n,oa,ob,pa,pb,ts,opoints=0,ppoints=0,ownerzone=False,oppzone=False,stadium=True):
 return {'turn_number_displayed':n,'phase':'source-bound boundary after normal draw or resolved prior effects','stadium':'Arena of Antiquity' if stadium else None,'owner':{'active':oa,'bench_in_position_order':ob,'energy_zone':ez('Fighting',ownerzone,ts),'points':opoints,'board_effects':['Arena: Fighting attacks +20 against opponent Active ex'] if stadium else [],'evidence_ids':refs(ts),'status':'observed','limit_reason':None},'opponent':{'active':pa,'bench_in_position_order':pb,'energy_zone':ez('Darkness',oppzone,ts),'points':ppoints,'board_effects':['More Poison: additional10 poison damage to owner Active'] if pb else [],'evidence_ids':refs(ts),'status':'observed','limit_reason':None},'shared_effects':[],'evidence_ids':refs(ts)}
def makeboard(n,oa,ob,ts,hp=170,d=0,tool=False,bench=False,nd=0,zd=0,pp=0,op=0,oz=False,pz=False,st=True,removed=False):
 pa,pb=opp(hp,d,tool,bench,nd,zd,ts,removed);return board(n,oa,ob,pa,pb,ts,op,pp,oz,pz,st)
# A fresh copy is written per boundary; every value is bound to a retained native frame.
starts={
1:makeboard(1,nac(ts=46.5),[nac(pos=1,ts=46.5)],46.5,st=False),
2:makeboard(2,nac(ts=72),[nac(pos=1,ts=72),tim(pos=3,ts=72)],72,pz=True),
3:makeboard(3,nac(ts=109),[nac(pos=1,ts=109),tim(pos=3,ts=109)],109,d=1,tool=True,bench=True,oz=True),
4:makeboard(4,nac(ts=135),[nac(pos=1,ts=135),tim(pos=2,ts=135),cg(f=1,pos=3,ts=135)],135,d=1,tool=True,bench=True,pz=True),
5:makeboard(5,cg(f=1,ts=165.5),[nac(pos=1,ts=165.5),tim(pos=2,ts=165.5)],165.5,d=2,tool=True,bench=True,pp=1,oz=True),
6:makeboard(6,cg(f=2,ts=189),[ns(ts=189),tim(pos=2,ts=189)],189,d=2,tool=True,bench=True,pp=1,pz=True),
7:makeboard(7,cg(hp=70,f=2,ts=218.5),[ns(ts=218.5),tim(pos=2,ts=218.5)],218.5,d=2,tool=True,bench=True,zd=1,pp=1,oz=True),
8:makeboard(8,cg(hp=50,f=2,c=1,poison=True,ts=240),[ns(ts=240),tim(e=1,pos=2,ts=240)],240,hp=70,d=2,tool=True,bench=True,zd=1,pp=1,pz=True),
9:makeboard(9,tim(e=1,ts=310.5),[ns(ts=310.5)],310.5,hp=110,d=2,tool=True,bench=True,nd=1,zd=1,pp=2,oz=True),
10:makeboard(10,gd(f=2,ts=324),[ns(ts=324)],324,hp=110,d=2,tool=True,bench=True,nd=1,zd=1,pp=2,pz=True),
11:makeboard(11,gd(hp=10,f=2,ts=362.5),[ns(ts=362.5)],362.5,hp=110,d=2,tool=True,bench=True,nd=2,zd=1,pp=2,oz=True)}
ends={
1:makeboard(1,nac(ts=67),[nac(pos=1,ts=67),tim(pos=3,ts=67)],67),
2:makeboard(2,nac(ts=105),[nac(pos=1,ts=105),tim(pos=3,ts=105)],105,d=1,tool=True,bench=True),
3:makeboard(3,nac(ts=130),[nac(pos=1,ts=130),tim(pos=2,ts=130),cg(f=1,pos=3,ts=130)],130,d=1,tool=True,bench=True),
4:makeboard(4,cg(f=1,ts=162),[nac(pos=1,ts=162),tim(pos=2,ts=162)],162,d=2,tool=True,bench=True,pp=1),
5:makeboard(5,cg(f=2,ts=185),[ns(ts=185),tim(pos=2,ts=185)],185,d=2,tool=True,bench=True,pp=1),
6:makeboard(6,cg(hp=70,f=2,ts=215),[ns(ts=215),tim(pos=2,ts=215)],215,d=2,tool=True,bench=True,zd=1,pp=1),
7:makeboard(7,cg(hp=50,f=2,c=1,poison=True,ts=239),[ns(ts=239),tim(e=1,pos=2,ts=239)],239,hp=70,d=2,tool=True,bench=True,zd=1,pp=1),
8:makeboard(8,tim(e=1,ts=306),[ns(ts=306)],306,hp=110,d=2,tool=True,bench=True,nd=1,zd=1,pp=2),
9:makeboard(9,gd(f=2,ts=320),[ns(ts=320)],320,hp=110,d=2,tool=True,bench=True,nd=1,zd=1,pp=2),
10:makeboard(10,gd(hp=10,f=2,ts=359),[ns(ts=359)],359,hp=110,d=2,tool=True,bench=True,nd=2,zd=1,pp=2),
11:makeboard(11,cb(poison=True,ts=388),[ga(ts=388)],388,hp=0,d=2,tool=True,bench=True,nd=2,zd=1,pp=2,op=3,st=False,removed=True)}
CG='Conkeldurr (Guts / Mega Punch)';CB='Conkeldurr (Bedrock Breaker)';RE="Professor's Research";PB='Poké Ball'
hands={1:[CG,'Naclstack','Copycat','Arena of Antiquity'],3:[CG,'Rare Candy',CB,'Timburr'],5:[CB,RE],7:[CB,'Wally'],9:[CB,'Gurdurr'],11:[CB,'Garganacl']}
handends={1:[CG,'Rare Candy',CB],3:[CB],5:[CB],7:[CB],9:[CB],11:[]}
fan={1:4,3:1,5:3,7:4,9:4,11:5}
drawends={1:46,3:109,5:165.5,7:218.5,9:309.5,11:362}
selected={1:46.5,3:109,5:165.5,7:218.5,9:310.5,11:362.25}
preend={1:67,3:129,5:184,7:230,9:318,11:371}
times={1:(43,47,68),2:(68,74,106),3:(106,109.5,131),4:(131,132,162.5),5:(162.5,166,186),6:(186,199,216),7:(216,219.5,238),8:(238,247,306.5),9:(306.5,311,320),10:(320,331,360),11:(360,363,390)}
plays={};autos={n:[] for n in range(1,12)};draws={n:[] for n in range(1,12)}
def play(n,t,kind,name,target,result,energy=None,nested=None,prompt=None,response=None,count=None):
 row={'order':len(plays.setdefault(n,[]))+1,'kind':kind,'card_name':name,'target':target,'energy':energy,'result':result,'prompt_text':prompt,'response':response,'nested_events_in_order':nested or [],'hand_count_after':count,'source_video':V,'timestamp_seconds':t,'evidence_ids':refs(t),'basis':'Observed source action and native resulting board','limit_reason':None};plays[n].append(row);return row['order']
def energy(typ,dest):return {'type':typ,'count':1,'destination':dest,'retreat_payment_by_type':None}
def draw(n,kind,why,names,ts,linked=None,before=None,after=None,returned=None,limit=None):
 draws[n].append({'kind':kind,'caused_by':why,'linked_play_order':linked,'cards_in_reveal_order':[{'name':name,'reveal_position':i+1,'source_video':V,'timestamp_seconds':t,'evidence_ids':refs(t),'basis':'Direct native card reveal' if name else 'Hidden opponent card back','limit_reason':None if name else 'Opponent card face not revealed'} for i,(name,t) in enumerate(zip(names,ts))],'hand_count_before':before,'hand_count_after':after,'returned_or_discarded_cards':returned,'source_video':V,'timestamp_seconds':ts[0],'evidence_ids':refs(*ts),'limit_reason':limit})
for n,name,t in [(1,'Arena of Antiquity',45),(3,'Timburr',108),(5,RE,164),(7,'Wally',217.5),(9,'Gurdurr',308.5),(11,'Garganacl',361.5)]:draw(n,'normal_draw','Start of owner turn',[name],[t],before=len(hands[n])-1,after=len(hands[n]))
for n,t in [(2,72),(4,132),(6,189),(8,240),(10,324)]:draw(n,'normal_draw','Start of opponent turn',[None],[t],limit='One card added; identity remains hidden. Timestamp is first inspected post-draw fan, not an exact opponent draw-end measurement.')
play(1,47,'Stadium','Arena of Antiquity','Shared Stadium slot','Stadium established; Fighting attacks +20 against Active ex.',count=3)
play(1,53,'Supporter','Copycat','Owner hand/deck','Shuffle remaining Conkeldurr Guts and Naclstack into deck; draw4, matching directly counted opponent fan.',nested=['Play Copycat; hand3 becomes2','Return two remaining hand cards and shuffle','Reveal four replacement cards in order'],count=4)
draw(1,'supporter_draw','Copycat',[CG,'Rare Candy',CB,'Timburr'],[60,61,62,63],linked=2,before=0,after=4,returned=[CG,'Naclstack'])
play(1,65,'bench','Timburr','Owner Bench slot3','Timburr60HP placed at right Bench, following draw reveal63s and clear pre-play hand64.5s.',count=3)
play(1,67,'End Turn',None,None,'Owner ends without Energy or attack; first player turn.',count=3)
play(2,75,'Tool','Poison Barb','Mega Absol ex','Tool attached.')
play(2,81,'Energy attachment',None,'Mega Absol ex','First Darkness attached.',energy('Darkness','Mega Absol ex'))
play(2,87,'Supporter','Copycat','Opponent hand/deck','Shuffle3 remaining hidden cards, draw3 matching owner hand.',nested=['Fan5 after normal draw','Poison Barb leaves4','Copycat leaves3, returned/shuffled','Three hidden replacements drawn'])
draw(2,'supporter_draw','Copycat',[None,None,None],[90,90,90],linked=3,before=0,after=3,limit='All three opponent identities hidden; visual replacement fan3.')
play(2,96,'bench','Zorua','Opponent Bench slot3','Zorua60HP placed.')
play(2,99,'Item',PB,'Opponent deck','Search returns Nihilego; subsequently placed at left Bench.')
draw(2,'search',PB,['Nihilego'],[102],linked=5,before=1,after=2,limit='Exact reveal transition lies between99-102s; public Nihilego placement directly establishes the found card.')
play(2,102,'bench','Nihilego','Opponent Bench slot1','Nihilego70HP placed; More Poison displayed104.5s.')
play(2,105,'End Turn',None,None,'Opponent ends without attack.')
play(3,109.5,'bench','Timburr','Owner Bench slot2','Second Timburr60HP fills center Bench.',count=3)
play(3,117,'Item','Rare Candy','Timburr in owner Bench slot3','Evolve the right Timburr directly into Guts Conkeldurr150HP.',nested=['Rare Candy committed','Choose right Bench Timburr','Choose Guts Conkeldurr from hand','Evolution resolves'],count=1)
play(3,128,'Energy attachment',None,'Guts Conkeldurr Bench slot3','First Fighting attached.',energy('Fighting','Guts Conkeldurr Bench slot3'),count=1)
play(3,130,'End Turn',None,None,'Owner ends without attacking; Nacli remains unenergized.',count=1)
play(4,135,'Supporter',RE,'Opponent deck','Draw2 hidden cards.')
draw(4,'supporter_draw',RE,[None,None],[138,138],linked=1,before=1,after=3,limit='Both opponent draws hidden.')
play(4,144,'Energy attachment',None,'Mega Absol ex','Second Darkness attached.',energy('Darkness','Mega Absol ex'))
play(4,147,'attack','Darkness Claw','Owner Active Nacli','80 damage KOs Nacli70HP. Owner hand revealed contains Bedrock Conkeldurr only; no Supporter discarded.',nested=['Reveal owner hand','No Supporter target','80 attack damage','Nacli Knocked Out','Opponent receives1point'])
play(4,159,'forced replacement','Guts Conkeldurr','Owner Active Spot','Owner chooses right Bench Guts Conkeldurr150HP/1F as replacement.')
autos[4]=[{'order':1,'timestamp_seconds':156,'event':'Opponent point total0->1','evidence_ids':refs(156)}]
play(5,167,'Supporter',RE,'Owner deck','Draw Poké Ball then Naclstack.',count=3)
draw(5,'supporter_draw',RE,[PB,'Naclstack'],[169,170.5],linked=1,before=1,after=3)
play(5,174,'Item',PB,'Owner deck','Unsuccessful search. Message177s: There are no cards in the deck that can be the target of the effect.',nested=['Poké Ball played','No valid Basic target','No card added; Poké Ball discarded'],count=2)
draw(5,'unsuccessful_search',PB,[],[],linked=2,before=2,after=2,limit='No card found; empty result directly shown.') if False else None
draws[5].append({'kind':'unsuccessful_search','caused_by':PB,'linked_play_order':2,'cards_in_reveal_order':[],'hand_count_before':2,'hand_count_after':2,'returned_or_discarded_cards':[],'source_video':V,'timestamp_seconds':177,'evidence_ids':refs(177),'limit_reason':None,'result':'No valid target, no card added'})
play(5,180,'evolution','Naclstack','Owner Bench slot1 Nacli','Nacli70 becomes Naclstack110HP.',count=1)
play(5,183,'Energy attachment',None,'Active Guts Conkeldurr','Second Fighting attached.',energy('Fighting','Active Guts Conkeldurr'),count=1)
play(5,185,'End Turn',None,None,'Owner ends without attack; Guts needs three Energy.',count=1)
play(6,201,'Energy attachment',None,'Opponent Bench slot3 Zorua','First Darkness attached; native189->201 confirms destination.',energy('Darkness','Zorua Bench slot3'))
play(6,210,'attack','Darkness Claw','Owner Active Guts Conkeldurr','80 damage:150->70HP. Owner hand only Bedrock Conkeldurr; no Supporter discard.')
play(7,220,'Supporter','Wally','Active Guts Conkeldurr','Attach1 Colorless via Wally; Active now2F+1C. Normal Fighting still available.',energy('Colorless','Active Guts Conkeldurr'),nested=['Wally card text shown221s','Choose Stage2 Active','Colorless appears223s'],count=1)
play(7,226,'Energy attachment',None,'Owner Bench slot2 Timburr','Attach normal Fighting to Timburr.',energy('Fighting','Timburr Bench slot2'),count=1)
play(7,230.5,'attack','Mega Punch','Opponent Active Mega Absol ex','100 damage:80 base+20 Arena. Mega170->70HP.',nested=['Attack declaration','Damage resolves','Poison Barb makes owner Conkeldurr Poisoned','Nihilego-amplified Poison checkup:70->50HP'],count=1)
autos[7]=[{'order':1,'timestamp_seconds':234,'event':'Poison Barb triggers after damage','evidence_ids':refs(234)},{'order':2,'timestamp_seconds':237,'event':'Poisoned condition and20 checkup damage; owner70->50HP','evidence_ids':refs(237)}]
play(8,249,'Item','Lucky Ice Pop','Mega Absol ex','Heal20:70->90HP. Heads returns Lucky Ice Pop to hand.',nested=['Heal20','Heads coin','Return Item to hand'])
play(8,261,'Item','Lucky Ice Pop','Mega Absol ex','Replay Item, heal20:90->110HP. Tails discards Item.',nested=['Heal20','Tails coin','Discard Item'])
play(8,276,'Energy attachment',None,'Opponent Bench slot1 Nihilego','First Darkness attached.',energy('Darkness','Nihilego Bench slot1'))
play(8,282,'attack','Darkness Claw','Owner Active Guts Conkeldurr','80 damage is lethal to50HP. Guts coin tails; KO stands. Opponent receives second point.',nested=['Owner hand revealed; no Supporter','Attack damage to0','Guts coin check: tails288s','Conkeldurr/2F+1C discarded','Opponent1->2points'])
play(8,303,'forced replacement','Timburr','Owner Active Spot','Owner chooses Timburr60HP/1F; Bench Naclstack stays.')
autos[8]=[{'order':1,'timestamp_seconds':252,'event':'Lucky Ice Pop first flip heads','evidence_ids':refs(252)},{'order':2,'timestamp_seconds':264,'event':'Lucky Ice Pop second flip tails','evidence_ids':refs(264)},{'order':3,'timestamp_seconds':288,'event':'Guts tails; attack-damage KO confirmed','evidence_ids':refs(288)},{'order':4,'timestamp_seconds':294,'event':'Opponent point total1->2','evidence_ids':refs(294)}]
play(9,311.5,'evolution','Gurdurr','Active Timburr','Timburr60 becomes Gurdurr90HP; retains1F.',count=1)
play(9,315,'Energy attachment',None,'Active Gurdurr','Second Fighting attached; attack available.',energy('Fighting','Active Gurdurr'),count=1)
play(9,318,'End Turn request',None,None,'Owner requests end without attacking.',count=1)
play(9,319,'warning confirmation',None,None,'Owner accepts End Turn and declines available attack.',prompt='End your turn? An attack can be used',response='OK; opponent turn10 follows320s',count=1)
play(10,333,'Energy attachment',None,'Opponent Bench slot1 Nihilego','Second Darkness attached.',energy('Darkness','Nihilego Bench slot1'))
play(10,354,'attack','Darkness Claw','Owner Active Gurdurr','80 damage:90->10HP. No owner Supporter to discard; no Poison because owner did not attack.')
play(11,363,'evolution','Garganacl','Owner Bench slot1 Naclstack','Naclstack110 becomes Garganacl150HP.',count=1)
play(11,367,'evolution',CB,'Owner Active Gurdurr','150maxHP with80 carried damage gives70HP; retains2F.',count=0)
play(11,369,'Energy attachment',None,'Active Bedrock Conkeldurr','Third Fighting attached.',energy('Fighting','Active Bedrock Conkeldurr'),count=0)
play(11,372,'attack','Bedrock Breaker','Opponent Active Mega Absol ex','120 damage:100 base+20 Arena KOs Mega110HP. Stadium discarded; Poison Barb triggers; owner receives3points and wins3-2.',nested=['Declare Bedrock Breaker120','120 damage375s','Arena discarded','Poison Barb makes Conkeldurr Poisoned381s','Mega Absol ex KO and3points','Victory390s'],count=0)
autos[11]=[{'order':1,'timestamp_seconds':375,'event':'120 attack damage','evidence_ids':refs(375)},{'order':2,'timestamp_seconds':378,'event':'Stadium removed by attack effect','evidence_ids':refs(378)},{'order':3,'timestamp_seconds':381,'event':'Poison Barb applies Poisoned','evidence_ids':refs(381)},{'order':4,'timestamp_seconds':388,'event':'Mega KO grants3points; final score3-2','evidence_ids':refs(388)},{'order':5,'timestamp_seconds':390,'event':'Victory. No subsequent checkup or Blessed Salt heal is shown.','evidence_ids':refs(390)}]
turns=[]
for n in range(1,12):
 owner=n%2==1;first,last,after=times[n];h=hands.get(n);hs=selected.get(n,starts[n]['evidence_ids'][0]);endhand=handends[n] if owner else handends[n-1];et=preend.get(n,after)
 hand={'cards_left_to_right':h,'count':len(h) if h is not None else None,'basis':'Direct native hand crop after normal draw, before first play' if owner else 'Opponent identities hidden','evidence_ids':refs(selected[n]) if owner else starts[n]['evidence_ids'],'status':'observed' if owner else 'hidden','limit_reason':None if owner else 'Card backs only; no owner-by-name requirement for opponent turns'}
 ownerstart=copy.deepcopy(hand) if owner else {'cards_left_to_right':handends[n-1],'count':len(handends[n-1]),'basis':'Direct continuing owner hand visible during opponent turn','evidence_ids':starts[n]['evidence_ids'],'status':'observed','limit_reason':None}
 turns.append({'turn_number':n,'who_played':'owner' if owner else 'opponent','source_video':V,'timing':{'turn_start_seconds':first,'draw_animation_end_seconds':drawends.get(n),'first_voluntary_move_seconds':last,'before_end_action_seconds':preend.get(n),'end_after_resolution_seconds':after},'hand_at_start':hand,'owner_hand_start':ownerstart,'opponent_hand_at_owner_turn_start':{'count':fan.get(n),'supported_range':None,'count_method':'Count separate visible card backs in native top crop','basis':'Direct fan count' if owner else 'Not applicable on opponent turn','evidence_ids':refs(selected[n]) if owner else [],'limit_reason':None if owner else 'Owner-turn-start field only'},'draws_and_searches':draws[n],'plays_in_order':plays[n],'automatic_events_in_order':autos[n],'board_at_start':starts[n],'board_after':ends[n],'owner_hand_end':{'cards_left_to_right':endhand,'count':len(endhand),'basis':'Direct visible hand and independently reconciled public additions/removals','evidence_ids':refs(et if owner else starts[n]['evidence_ids'] and float(starts[n]['evidence_ids'][0][1:])/100),'status':'observed','limit_reason':None},'discard_snapshot_ids':[f'DISCARD_OWNER_T{n}',f'DISCARD_OPPONENT_T{n}'],'turn_evidence_ids':sorted(set(starts[n]['evidence_ids']+ends[n]['evidence_ids']+[e for x in plays[n] for e in x['evidence_ids']]+[e for x in draws[n] for e in x['evidence_ids']])),'limits':['Opponent hidden normal and Supporter draw identities remain unknown.','No opened discard-pile panel; exposed discard-top and played-card history do not establish full pile.','Action and draw-end times are bounded visual seeks; exact frame PTS not separately measured.']})
save('TURN_LEDGER.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,'turns':turns,'limits':['All11 recorded turns have one row. Native evidence and prose cover complete game; hidden opponent identities and unopened discard piles remain source limits.']})
# Frames retain source-native dimensions, actual coordinates and draw-tied candidate roles.
frames=[];selections=set(selected.values());pre=set(preend.values())
candidate={}
for n,t in drawends.items():
 for offset in (1,3,6):candidate[round(t+offset,2)]=(n,t,offset)
for path in sorted((P/'turn_evidence').glob('t*.jpg')):
 if '_bottom' in path.name or '_top' in path.name:continue
 t=float(path.stem[1:]);top=path.with_name(path.stem+'_top.jpg');bottom=path.with_name(path.stem+'_bottom.jpg')
 with Image.open(path) as im:
  if not top.exists():im.crop((0,0,1170,620)).save(top,quality=95)
  if not bottom.exists():im.crop((0,2025,1170,2532)).save(bottom,quality=95)
 nt=next((n for n,tx in selected.items() if tx==t),None);ca=candidate.get(t); nt=ca[0] if ca else nt
 role='selected_pre_play_hand' if t in selections else 'before_end_hand' if t in pre else 'draw_offset_candidate' if ca else 'targeted_event_or_board'
 if t==30:role='opening_five_before_active'
 frames.append({'evidence_id':eid(t),'role':role,'turn_number':nt,'who_played':'owner' if nt else None,'source_video':V,'source_sha256':H,'draw_animation_end_seconds':drawends.get(nt),'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':ca[2] if ca else None,'full_frame_path':str(path.relative_to(P)).replace('\\','/'),'native_dimensions':{'width':1170,'height':2532},'bottom_crop':{'path':str(bottom.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},'top_crop':{'path':str(top.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,1170,620]},'selected_for_start_hand':t in selections,'before_first_play':True if t in selections else (False if ca else None),'unzoomed':True if t in selections or t in pre or t==30 else None,'hand_spread':True if t in selections or t==30 else None,'observation':'Native pre-play hand names and both zones inspected' if t in selections else 'Source-bound event/board frame, or draw-offset candidate; see ledger for action context','suitability_or_limit':'Selected dense pre-play view; owner acts before +1s on turns1,3,5,7,11' if t in selections else 'Later than first play; retained scheduled candidate cannot replace pre-play hand' if ca else None})
discard=[]
for n in range(1,12):
 for who in ['OWNER','OPPONENT']:discard.append({'snapshot_id':f'DISCARD_{who}_T{n}','turn_number':n,'pile_owner':who.lower(),'source_video':V,'timestamp_seconds':times[n][2],'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'evidence_ids':ends[n]['evidence_ids'],'limit_reason':'No discard pile opened anywhere in this game. Board-edge top cards alone are not a full-pile snapshot. Ordered public discard history is in numbered plays.'})
save('TURN_EVIDENCE.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,'source_sha256':H,'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,'bottom_crop_height_fraction':0.2,'fixed_grid_is_turn_start_evidence':False},'frames':frames,'discard_snapshots':discard,'scheduled_capture_limits':['Owner acts before +1second after draw on turns1,3,5,7,11, so dense pre-play frames replace unsuitable scheduled candidates. Turn9 +1candidate310.5s is clear.','Before-end attack substitute: turn7 uses230s; turn11 uses371s. No post-terminal Poison checkup shown.']})
opening=['Nacli',CG,'Nacli','Naclstack','Copycat']
limits=['No discard pile opened; periodic pile-content snapshots unavailable.','Opponent hidden draws and full deck remain unknown.','Exact artwork/rarity not encoded by QR; deck snapshot preserves log variant labels.','Final results loading continues to398.13s; terminal3point/Victory already clear388-390s.','Source timestamps are local seeks; frame PTS not separately measured.']
save('PAUSE_GAME.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'review_date':'2026-10-10','sources':sources,'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'Conkeldurr / Garganacl','match_date':'2026-10-09','match_date_basis':'Filename UTC2026-10-10T01:23:03; independently batch-verified creation timezone => America/Chicago2026-10-09T20:23:03','opponent':'ナチョス','mode':'human online battle; specific queue label not established','auto_control_visible':False,'opening':{'source_video':V,'timestamp_seconds':30,'expected_card_slots':5,'recorded_card_count':5,'cards_left_to_right':[{'position':i+1,'name':name,'basis':'Direct native pre-Active view; Guts variant confirmed35s','evidence_ids':refs(30,35),'limit_reason':None} for i,name in enumerate(opening)],'selected_active':{'name':'Nacli','opening_position':1,'source_video':V,'timestamp_seconds':35,'evidence_ids':refs(30,35),'basis':'First left Nacli removed before second Nacli is benched; identical copies not individually distinguishable after placement'},'redraw_or_replacement':[],'before_active_placement':True,'status':'observed','evidence_ids':refs(30,35),'limit_reason':None},'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},'capture_status':'complete_with_recording_limits','battle_review_status':'worker_complete_pending_independent_acceptance','outcome':{'owner_result':'win','owner_points':3,'opponent_points':2,'terminal_turn':11,'result_evidence_seconds':[375,388,390],'evidence_ids':refs(375,388,390)},'limits':limits,'lead_checked':False})
live=json.loads((P.parent/'LIVE_NEW_DECKS_VERIFIED.json').read_text(encoding='utf-8'))
d=next(d for d in live['decks'] if d['name']=='Conkeldurr / Garganacl');slots=[];counts=[]
for count,name,variant in d['rows']:
 counts.append({'name':name,'variant':variant,'count':int(count)})
 for i in range(int(count)):slots.append({'slot':len(slots)+1,'name':name,'variant':variant})
save('DECK_USED.json',{'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,'deck_name_in_log':d['name'],'source_url':live['source_url'],'captured_at':live['retrieved_at_utc'],'log_list_version':'LIVE_NEW_DECKS_VERIFIED.json source snapshot frozen at retrieval','expected_card_count':20,'cards_in_log_order':slots,'counts_by_name_and_variant':counts,'energy_configuration_from_log':d['energy'],'actual_card_count':20,'capture_source_text_or_image':{'batch_path':'../LIVE_NEW_DECKS_VERIFIED.json','text':d['text']},'game_version_binding_basis':'Source-bound QR at1s has identical payload to live deck definition. Continuous QR/editor New deck6 -> matchmaking -> one game, same Fighting deck core and both Conkeldurr variants. All filmed cards compatible. QR is not used to infer any hand identity.','conflicts_with_filmed_cards':[],'exact_list_status':'verified_live20slot_snapshot_and_source_QR_semantic_match','limits':['Log labels identify semantic variants; exact physical artwork/rarity remains unverified. Live definition text cites sibling013009 source, but this source has independently decoded identical QR and continuous game binding.']})
q=json.loads((P/'qr_intake/QR_DECODE_0001.00.json').read_text(encoding='utf-8'));save('QR_DECODE_RECEIPT.json',q)
save('SUMMARY.json',{'is_template':False,'game_id':G,'source_video':V,'source_sha256':H,'reviewer':'/root/pause_012303','model':'gpt-6.1-sol','scope':'Entire398.131667s source; pregame, setup, all11 turns, terminal and loading tail','games_in_source':1,'mode':'human online battle; exact queue unknown','auto_control_visible':False,'owner':'Dacz8976','opponent':'ナチョス','deck':'Conkeldurr / Garganacl','result':'win','score':'3-2','turn_count':11,'battle_review_status':'worker_complete_pending_independent_acceptance','capture_status':'complete_with_recording_limits','external_log_written':False,'source_moved':False,'meaningful_findings':['Turn5 Poké Ball no valid target explicitly shown.','Turn7 Wally Colorless attachment to Guts Conkeldurr followed by normal Fighting to Timburr.','Turn8 Lucky Ice Pop heads return and tails discard; Guts tails KO.','Turn9 confirms attack-available warning and passes. Avoiding Poison leaves Gurdurr alive for next evolution.','Turn11 Bedrock Breaker120 KOs Mega Absol ex for3points.'],'limits':limits})
save('UNCERTAINTIES.json',{'is_template':False,'game_id':G,'unreviewed_intervals':[],'unresolved_material_outcome_claims':[],'recording_limits':[{'topic':x,'status':'inspected_source_limit'} for x in limits],'specific_limits':[{'topic':'Opening identical Nacli copy distinction','seconds':[30,35],'finding':'Two identical Nacli; chosen leftmost opening Nacli placement is visually compatible, no unique copy identifier exists.'},{'topic':'Opponent search timing','seconds':[99,102],'finding':'Nihilego public found/placed; exact search-reveal instant bounded, no hidden draw guessed.'},{'topic':'Specific human queue','seconds':[0,43],'finding':'Searching for opponent/match found visible; ranked/private/random label not shown. Human routing follows owner instruction.'}]})
viewed=['early_01.jpg','early_02.jpg','mid1_01.jpg','mid1_02.jpg','mid1_03.jpg','mid2_01.jpg','mid2_02.jpg','mid2_03.jpg','mid3_01.jpg','mid3_02.jpg','mid3_03.jpg','details_01.jpg','details_02.jpg','late_01.jpg','late_02.jpg','late_03.jpg','draws_01.jpg','draws_02.jpg','draws_03.jpg','draws_04.jpg','draws_05.jpg','finaldetail_01.jpg','finaldetail_02.jpg','finaldetail_03.jpg','finaldetail_04.jpg','finaldetail_05.jpg','overview/sheet_01.jpg','overview/sheet_07.jpg']
save('VIEWED_MANIFEST.json',{'reviewer':'/root/pause_012303','source_video':V,'source_sha256':H,'viewed_contact_sheets':viewed,'native_individually_viewed_seconds':[30,35,40,60,63,102,126,189,201,221,225,228,276],'native_selected_hand_crops_viewed_seconds':[46.5,109,165.5,218.5,310.5,362],'method':'Native extracted frames retained; source-wide targeted3s pass with denser draw/action windows. Contact sheets used to find events; selected source-native hand crops independently read.','not_claimed':'No real-time video playback or frame-by-frame scan. Exact frame PTS not separately measured.'})
pg=json.loads((P/'PAUSE_GAME.json').read_text(encoding='utf-8'))
pg['opening']['selected_active'].update({'opening_position':3,'timestamp_seconds':31,'evidence_ids':refs(30,31,31.5,32),'basis':'Position3 Nacli goes Active; position1 Nacli remains leftmost in native31/31.5 four-card hand, then is benched32s.'})
save('PAUSE_GAME.json',pg)
un=json.loads((P/'UNCERTAINTIES.json').read_text(encoding='utf-8'))
un['specific_limits'][0]={'topic':'Opening Active selection','seconds':[30,31,31.5,32],'finding':'Dense views resolve selected Nacli as opening position3. Position1 remains in hand and is then benched. No unresolved slot remains.'}
save('UNCERTAINTIES.json',un)
led=json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8'))
for turn in led['turns']:
 n=turn['turn_number']
 if n==9:
  turn['plays_in_order'][3]['evidence_ids']=refs(318.5,319,319.5,320)
 if n in (3,5,7):
  zone=turn['board_at_start']['owner']['energy_zone']
  zone['this_turn']={'type':None,'count':None,'available':None}
  zone['limit_reason']='Selected pre-play hand precedes completion of normal Energy generation. Current Energy availability is transitional here; later first-action native frame establishes Fighting1 before attachment. Next small symbol is directly Fighting.'
  turn['automatic_events_in_order'].insert(0,{'order':0,'event':'Normal Fighting Energy generation resolves after selected early hand view','timestamp_seconds':{3:110,5:166,7:219,11:364}[n],'evidence_ids':refs({3:110,5:166,7:219,11:364}[n])})
save('TURN_LEDGER.json',led)
vm=json.loads((P/'VIEWED_MANIFEST.json').read_text(encoding='utf-8'))
vm['viewed_contact_sheets']+=['reconcile_01.jpg','reconcile_02.jpg','openingdetail_01.jpg','bindfinal_01.jpg']
vm['native_individually_viewed_seconds']+=[81,218.5,378,381]
vm['native_selected_hand_crops_viewed_seconds']+=[362.25,362.5]
save('VIEWED_MANIFEST.json',vm)
print('Packet JSON authored',len(turns),'turns',len(frames),'native frames')
