"""Source-local first-pass authoring; not independent acceptance or registration."""
import json, copy, datetime, hashlib
from pathlib import Path
from PIL import Image

P=Path(__file__).resolve().parent
source=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
V=source['video_basename']; SHA=source['sha256']; G=V.removesuffix('.MP4')
sources=[{'video_basename':V,'sha256':SHA,'source_json':'SOURCE.json'}]
frames={}
def eid(t): return 'f'+f'{t:07.2f}'.replace('.','_')
def evidence(times, role='action_or_board', turn=None, observation=None):
    result=[]
    for t in times:
        k=eid(t); result.append(k)
        if k in frames: continue
        name=f't{t:07.2f}.jpg'; path=P/'turn_evidence'/name
        if not path.exists(): raise ValueError(str(path))
        with Image.open(path) as im:
            assert im.size==(1170,2532)
            for suffix,bounds in [('bottom',(0,2025,1170,2532)),('top',(0,0,1170,700))]:
                im.crop(bounds).save(P/'turn_evidence'/f'{name[:-4]}_{suffix}.png')
        frames[k]={'evidence_id':k,'role':role,'turn_number':turn,'source_video':V,'source_sha256':SHA,
          'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,
          'full_frame_path':'turn_evidence/'+name,'native_dimensions':{'width':1170,'height':2532},
          'bottom_crop':{'path':f'turn_evidence/{name[:-4]}_bottom.png','pixel_bounds_x0_y0_x1_y1':[0,2025,1170,2532]},
          'top_crop':{'path':f'turn_evidence/{name[:-4]}_top.png','pixel_bounds_x0_y0_x1_y1':[0,0,1170,700]},
          'selected_for_start_hand':False,'before_first_play':None,'unzoomed':None,'hand_spread':None,
          'observation':observation,'suitability_or_limit':'Native sought frame; requested time is not measured presentation timestamp.'}
    return result
def hand(cards,times,hidden=False):
    return {'cards_left_to_right':None if hidden else cards,'count':cards if hidden else len(cards),
      'basis':'Visible card backs; identities hidden' if hidden else 'Native intact fan, checked against named reveals and removals',
      'evidence_ids':evidence(times),'status':'hidden_identities' if hidden else 'observed',
      'limit_reason':'Opponent faces are hidden.' if hidden else None}
names={'sand':('Sandshrew','B2 077 Double Scratch',60), 'slash':('Sandslash','B2 078 Fury Swipes',90),
 'timb':('Timburr','A3 094 Corkscrew Punch',60),'conk':('Conkeldurr','B4 089 Bedrock Breaker',150),
 'hit':('Hitmonchan ex','Quick Straight functional entity 12060',130),
 'tink':("Team Rocket's Tinkatink",'Lunge Out 20',60), 'tuff':("Team Rocket's Tinkatuff",'Corkscrew Punch 50',80),
 'tinkaton':("Team Rocket's Tinkaton",'Pile-Driving Hammer 80',140),'tog':('Togedemaru','Tumbling Attack 20+',70),
 'staka':('Stakataka','Brass Rock 40; temporary damage reduction 20',110),'cuf':('Cufant','Rollout 40',90),
 'copper':('Copperajah','Heavy Impact 80',160)}
def mon(key,hp=None,en=None,effects=None):
    if key is None:return {'name':None,'status':'visibly_empty','limit_reason':None,'tool':'none','special_conditions':[],'active_effects':[],'attached_energy':{'total':0,'by_type':{}},'hp_now':None,'hp_max':None,'damage':None}
    name,var,maxhp=names[key]; hp=maxhp if hp is None else hp; en=en or {}
    return {'name':name,'variant':var,'hp_now':hp,'hp_max':maxhp,'hp_max_basis':'Native revealed card / native public field, retained around transition',
      'damage':maxhp-hp,'attached_energy':{'total':sum(en.values()),'by_type':en},'tool':'none',
      'tool_basis':'No attached Tool visible on this public card during this interval',
      'special_conditions':[],'active_effects':effects or [],'status':'observed','limit_reason':None}
F=lambda n:{'Fighting':n} if n else {}
M=lambda n:{'Metal':n} if n else {}
FC=lambda n:{'Fighting':n,'Colorless':1}
def state(oa,ob,pa,pb,score):return {'owner':{'active':oa,'bench':ob,'points':score[0]},'opponent':{'active':pa,'bench':pb,'points':score[1]}}
empty=lambda:mon(None)
S=[]
S.append(state(mon('sand'),[mon('sand'),empty(),empty()],mon('tink'),[empty(),mon('tog'),mon('staka')],(0,0)))
S.append(copy.deepcopy(S[-1]))
S.append(state(mon('sand',40),[mon('sand'),empty(),empty()],mon('tink',60,M(1)),[mon('cuf'),mon('tog'),mon('staka')],(0,0)))
S.append(state(mon('slash',90,F(1)),[mon('sand'),empty(),empty()],mon('staka'),[mon('cuf'),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',90,F(1)),[mon('sand'),empty(),empty()],mon('staka',110,M(1)),[mon('cuf'),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',90,F(1)),[mon('sand',60,F(1)),empty(),empty()],mon('staka',80,M(1)),[mon('cuf'),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',50,F(1)),[mon('sand',60,F(1)),empty(),empty()],mon('staka',80,M(2),['Brass Rock: reduce incoming attack damage by 20 during owner turn 7']),[mon('copper'),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',90,F(2)),[mon('sand',60,F(1)),empty(),empty()],mon('staka',70,M(2)),[mon('copper'),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',50,F(2)),[mon('sand',60,F(1)),empty(),empty()],mon('staka',70,M(2),['Brass Rock: reduce incoming attack damage by 20 during owner turn 9']),[mon('copper',160,M(1)),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',70,F(2)),[mon('sand',60,F(1)),empty(),mon('timb',60,F(1))],mon('staka',30,M(2)),[mon('copper',160,M(1)),mon('tog'),empty()],(1,0)))
S.append(state(mon('slash',30,F(2)),[mon('sand',60,F(1)),empty(),mon('timb',60,F(1))],mon('staka',30,M(2),['Brass Rock: reduce incoming attack damage by 20 during owner turn 11']),[mon('copper',160,M(2)),mon('tog'),empty()],(1,0)))
S.append(state(mon('conk',150,FC(2)),[mon('sand',60,F(1)),empty(),mon('slash',30,F(1))],mon('copper',160,M(2)),[empty(),mon('tog'),empty()],(2,0)))
S.append(state(mon('conk',70,FC(2)),[mon('sand',60,F(1)),empty(),mon('slash',30,F(1))],mon('copper',160,M(3)),[mon('cuf'),mon('tog'),mon('tink')],(2,0)))
S.append(state(mon('conk',70,FC(3)),[mon('sand',60,F(1)),empty(),mon('slash',30,F(1))],mon('copper',60,M(3)),[mon('cuf'),mon('tog'),mon('tink')],(2,0)))
S.append(state(mon('slash',30,F(1)),[mon('sand',60,F(1)),empty(),empty()],mon('copper',60,M(3)),[mon('cuf'),mon('tog'),mon('tuff',80,M(1))],(2,1)))
S.append(state(mon('slash',30,F(1)),[mon('sand',60,F(1)),mon('hit'),mon('timb',60,F(1))],mon('copper',30,M(3)),[mon('cuf'),mon('tog'),mon('tuff',80,M(1))],(2,1)))
S.append(state(mon('hit'),[mon('sand',60,F(1)),empty(),mon('timb',60,F(1))],mon('copper',30,M(3)),[mon('cuf'),mon('tog'),mon('tinkaton',140,M(2))],(2,2)))
S.append(state(mon('hit',130,F(1)),[mon('sand',60,F(1)),empty(),mon('timb',60,F(1))],empty(),[mon('cuf'),mon('tog'),mon('tinkaton',140,M(2))],(3,2)))

W='Wally'; C='Cyrus'; RC='Rare Candy'; L='Lucky Ice Pop'; PB='Poké Ball'; PR='Professor’s Research'; CA='Conkeldurr [A3 096 Guts / Mega Punch]'; CB='Conkeldurr [B4 089 Bedrock Breaker]'; SL='Sandslash [B2 078 Fury Swipes]'; SA='Sandslash [A1 138 Slash]'
H={1:[W,C,L,SL],3:[W,C,L,SL,RC],5:[W,C,RC,L],7:[W,C,RC,L,RC],9:[W,C,RC,RC,L,PB],11:[W,C,RC,RC,CB],13:[C,RC,CA],15:[C,RC,CA,PR],17:[C,RC,CA,SA]}
HE={1:H[1],3:[W,C,RC],5:H[5],7:[W,C,RC,RC,L],9:[W,C,RC,RC],11:[C,RC],13:H[13],15:[C,RC,CA],17:H[17]}
starts={1:59.5,3:94.5,5:158.3,7:197.5,9:264,11:332.8,13:433,15:485.6,17:570}
drawend={1:58.5,3:94.5,5:158.3,7:196.5,9:264,11:332.6,13:432.5,15:485.6,17:570}
first={1:63,3:94.7,5:159,7:198,9:264.5,11:333,13:435,15:486,17:571}
before={1:62,3:109,5:161.5,7:216.5,9:281,11:353,13:440,15:505.5,17:573}
candidates={1:[59.5,61.5,64.5],3:[95.5,97.5,100.5],5:[159.5,161.5,164.5],7:[197.5,199.5,202.5],9:[265.4,267.4,270.4],11:[333.5,335.6,338.6],13:[433.5,435.5,438.5],15:[486.5,488.5,491.5],17:[571.5,573.5,576.5]}
quals={1:['Intact four-card fan, before End Turn','Intact four-card fan, before End Turn','After End Turn; opponent turn banner'],3:['Lucky Ice Pop already selected; original five-card fan changed','Ice Pop heal resolution; not a preplay hand','After Ice Pop discard; fewer cards'],5:['Energy selection underway; same four-card fan','After Energy attachment, before attack','Attack presentation; not intact preplay field'],7:['Intact five-card fan before Ice Pop','Ice Pop is selected / zoomed','Heal resolution, original hand changed'],9:['Poké Ball removed / played','Search resolution; original hand changed','Searched Timburr is being benched'],11:['Rare Candy already used; original five-card fan changed','Candy resolution; four cards remain','Conkeldurr evolution resolved; three-card fan'],13:['Intact three-card fan before attachment','Energy target selection underway','After Energy attachment, original three-card identities remain'],15:['Research already played; original four-card fan changed','Research resolution; original hand changed','Timburr second Research draw displayed; changed hand'],17:['Energy attachment underway; current zone consumed','After attachment, before attack presentation; same four-card identities','Attack resolution; not preplay']}
fan={1:2,3:3,5:4,7:4,9:5,11:6,13:4,15:4,17:3}
starttimes={1:59.5,2:68,3:94.5,4:142,5:158.3,6:176,7:197.5,8:234,9:264,10:302,11:332.8,12:367,13:433,14:450,15:485.6,16:520,17:570}
endtimes={1:64,2:93,3:139,4:154,5:176,6:194,7:230,8:261,9:298,10:330,11:366,12:429,13:448,14:482,15:516,16:566,17:582}
bounds={1:[56,65],2:[65,92],3:[92,141],4:[141,155],5:[155,178],6:[178,194],7:[194,230],8:[230,261],9:[261,300],10:[300,330],11:[330,367],12:[367,429],13:[429,448],14:[448,484],15:[484,518],16:[518,567],17:[567,583]}
turns=[]
def zone(player,n,end=False):
    typ='Fighting' if player=='owner' else 'Metal'; acting=('owner' if n%2 else 'opponent')==player
    generating=(n in [11,15,17] and player=='owner' and not end)
    available=acting and not end and not(n==1 and player=='owner')
    return {'this_turn':{'type':None if generating or not available else typ,'count':None if generating else int(available),
       'available':None if generating else available,'status':'empty_or_generating_at_selected_frame' if generating else ('visible_generated_energy' if available else 'empty_large_circle')},
      'next':{'type':typ,'count':1,'available':False,'status':'small_preview_only'},
      'basis':'Large current circle and separate small preview inspected; no preview counted as current Energy.',
      'limit_reason':'Selected hand frame precedes full current Energy generation; later attachment proves availability in this turn.' if generating else None}
def board(st,n,t,end=False):
    refs=evidence([t]); b={'turn_number_displayed':None,'turn_number_limit_reason':'No readable Current turn numeral in the cited settled board frame; row number follows visible turn transitions.',
      'phase':'concluded_turn_after_attack_and_promotion_if_required' if end else 'public_state_before_actions; draw-end hand is a separate capture',
      'stadium':{'name':'none','basis':'No Stadium present in inspected full battlefield'},'shared_effects':[],'evidence_ids':refs}
    for who in ['owner','opponent']:
        p=copy.deepcopy(st[who]); p['bench_in_position_order']=p.pop('bench')
        for i,m in enumerate(p['bench_in_position_order']):m['bench_position']=i+1;m['position_label']=['left','center','right'][i];m['evidence_ids']=refs
        p['active']['bench_position']=None;p['active']['evidence_ids']=refs
        p.update({'energy_zone':zone(who,n,end),'board_effects':[],'evidence_ids':refs,'status':'observed_public_state',
           'limit_reason':'Turn 6 pre-evolution state uses the immediately preceding settled board; evolution is already complete by 179s.' if n==6 and not end else None})
        b[who]=p
    return b
def play(n,kind,name,target,result,times,count=None,energy=None,nested=None,prompt=None,response=None):
    a={'order':len(turns[n-1]['plays_in_order'])+1,'kind':kind,'card_name':name,'target':target,
       'result':result,'source_video':V,'timestamp_seconds':times[0],'evidence_ids':evidence(times,turn=n),
       'hand_count_after':count,'energy':energy,'nested_events_in_order':nested,'prompt_text':prompt,'response':response,
       'basis':'Visible public card input/reveal or target change; remote opponent finger input is hidden.',
       'limit_reason':'Input timestamp bounds public presentation, not remote tap.' if not n%2 else None}
    turns[n-1]['plays_in_order'].append(a)
def draw(n,kind,name,times,linked=None,beforecount=None,aftercount=None,limit=None):
    cards=[] if name is None else [{'name':name,'reveal_position':1,'source_video':V,'timestamp_seconds':times[0], 'evidence_ids':evidence(times),'basis':'Visible face-up named reveal','limit_reason':None}]
    turns[n-1]['draws_and_searches'].append({'kind':kind,'caused_by':'normal turn draw' if kind=='normal_draw' else kind,
      'linked_play_order':linked,'cards_in_reveal_order':cards,'hand_count_before':beforecount,'hand_count_after':aftercount,
      'source_video':V,'timestamp_seconds':times[0],'evidence_ids':evidence(times), 'returned_or_discarded_cards':None,'limit_reason':limit})

for n in range(1,18):
    own=bool(n%2); prev=(n-1 if own else n-1)
    oh=H[n] if own else HE[n-1]
    startrefs=evidence([starts[n]] if own else [starttimes[n]],'selected_start_hand' if own else 'opponent_turn_start',n)
    row={'turn_number':n,'who_played':'owner' if own else 'opponent','source_video':V,
      'timing':{'turn_transition_start_seconds':bounds[n][0],'draw_animation_end_seconds':drawend.get(n),
        'first_voluntary_move_seconds':first.get(n),'before_end_action_seconds':before.get(n),'end_after_resolution_seconds':endtimes[n]},
      'hand_at_start':hand(oh,[starts[n]]) if own else hand({2:3,4:4,6:5,8:5,10:6,12:7,14:5,16:5}[n],[starttimes[n]],True),
      'owner_hand_start':hand(oh,[starts[n] if own else starttimes[n]]),
      'opponent_hand_at_owner_turn_start':{'count':fan[n] if own else None,'supported_range':None,
        'count_method':'Visible separated card backs in the native top crop','basis':'Native start fan' if own else None,
        'evidence_ids':startrefs if own else [],'limit_reason':None if own else 'This is an opponent turn, not an owner-turn start sample.'},
      'draws_and_searches':[],'plays_in_order':[],'automatic_events_in_order':[],
      'board_at_start':board(S[n-1],n,starttimes[n]),'board_after':board(S[n],n,endtimes[n],True),
      'owner_hand_end':hand(HE[n] if own else HE[n-1],[before[n] if own else endtimes[n]]),
      'discard_snapshot_ids':[],'turn_evidence_ids':startrefs,'limits':[]}
    if own:
        for i,t in enumerate(candidates[n]):
            k=evidence([t],'draw_end_offset_candidate',n)[0];f=frames[k]
            f.update({'who_played':'owner','draw_animation_end_seconds':drawend[n], 'offset_after_draw_seconds':round(t-drawend[n],3),
             'requested_offset_target_seconds':[1,3,6][i],'before_first_play':t<first[n],
             'unzoomed':not('zoom' in quals[n][i] or 'presentation' in quals[n][i]),
             'hand_spread':'original_intact_fan' if t<first[n] else 'changed_or_action_in_progress',
             'observation':quals[n][i],'suitability_or_limit':'Inspected candidate: '+quals[n][i]})
        frames[startrefs[0]].update({'selected_for_start_hand':True,'before_first_play':True,'unzoomed':True,
          'hand_spread':'original_intact_fan','draw_animation_end_seconds':drawend[n],
          'offset_after_draw_seconds':round(starts[n]-drawend[n],3),
          'observation':'Selected intact hand before the first voluntary move; all '+str(len(oh))+' faces readable.',
          'suitability_or_limit':'Dense alternate selected when the scheduled offsets are already after a play; current Energy is independently bounded if still generating.'})
        evidence([before[n]],'before_end_action',n,'Last field/hand view before attack presentation or manual End Turn; action-selection state qualified in ledger.')
        row['capture_candidates']=evidence(candidates[n])
        row['selected_start_hand_evidence_ids']=startrefs
        row['before_end_action_evidence_ids']=evidence([before[n]])
    else:
        row['limits'].append('Normal draw identity is hidden; no unseen card reconstructed. Remote input order comes from public resolutions.')
    turns.append(row)

draw(1,'normal_draw',SL,[57.5,59.5],beforecount=3,aftercount=4)
play(1,'end_turn',None,None,'Ends without Energy attachment, evolution or attack; four-card hand retained.',[62,63,64],4,prompt=None,response='End Turn selected')
draw(2,'normal_draw',None,[66,68],beforecount=2,aftercount=3,limit='Hidden opponent normal draw')
play(2,'energy_attachment',None,'Active Team Rocket Tinkatink','One Metal attached before Research.',[72,74,75],3,{'type':'Metal','count':1,'destination':'opponent Active'})
play(2,'supporter',PR,'opponent hand','Draws two hidden cards; fan grows from 2 to 4 after Supporter consumption.',[79,80,82],4)
draw(2,'supporter_draw',None,[80,82],2,2,4,'Two faces hidden; no guessed identities.')
play(2,'bench','Cufant','opponent left bench','Benches 90-HP Cufant; fan falls to 3.',[83,84],3)
play(2,'attack',"Team Rocket's Tinkatink: Lunge Out",'owner Active Sandshrew','20 damage, 60 to 40 HP.',[87,88,89,91,93],3)
draw(3,'normal_draw',RC,[94,94.5],beforecount=4,aftercount=5)
play(3,'item',L,'owner Active Sandshrew','Heals 40 to 60; tails; Lucky Ice Pop discarded.',[95,96,98,99,103,104],4,nested=['Heal20','Coin tails','Discard item'])
play(3,'evolution',SL,'owner Active Sandshrew','Normal evolution to Fury Swipes Sandslash; 90/90 HP.',[105,107,108],3)
play(3,'energy_attachment',None,'owner Active Sandslash','Adds one Fighting.',[107,108],3,{'type':'Fighting','count':1,'destination':'owner Active'})
play(3,'attack','Sandslash: Fury Swipes','opponent Active Tinkatink','Two heads, one tail; 60 damage and knockout. Owner earns point 1; opponent subsequently promotes Stakataka.',[110,114,116,120,122,126,138,139],3,
 nested=['Attack selection','Three coins: two heads / one tail','60 damage / HP0 at 120','Removal122','Point126','Stakataka promoted138-139'])
turns[2]['board_after']['evidence_ids']=evidence([126,139]);turns[2]['limits'].append('Promotion waiting phase extends well beyond attack; no Active Stakataka claimed at the empty prepromotion frame.')
draw(4,'normal_draw',None,[141,142],beforecount=3,aftercount=4,limit='Hidden opponent draw.')
play(4,'energy_attachment',None,'opponent Active Stakataka','First Metal attachment; attack not used this turn.',[143,144,146],4,{'type':'Metal','count':1,'destination':'opponent Active'})
play(4,'end_turn',None,None,'Ends with one Metal on Stakataka and no damage.',[153,154,155],4,response='Turn ends; remote button press hidden')
draw(5,'normal_draw',L,[157,158.3],beforecount=3,aftercount=4)
play(5,'energy_attachment',None,'owner left Bench Sandshrew','Adds one Fighting to bench, leaving Active one Fighting.',[159,160,161],4,{'type':'Fighting','count':1,'destination':'owner left bench'})
play(5,'attack','Sandslash: Fury Swipes','opponent Active Stakataka','One head, two tails; 30 damage, 110 to 80.',[162,168,174,176],4)
draw(6,'normal_draw',None,[178,179],beforecount=4,aftercount=5,limit='Hidden opponent draw; close draw/evolution transition.')
play(6,'evolution','Copperajah','opponent left Bench Cufant','Evolves into 160-HP Heavy Impact Copperajah, before second Metal on Stakataka.',[176,178,179],4)
play(6,'energy_attachment',None,'opponent Active Stakataka','Second Metal attached after Copperajah evolution.',[180,181,182],4,{'type':'Metal','count':1,'destination':'opponent Active'})
play(6,'attack','Stakataka: Brass Rock','owner Active Sandslash','40 damage, 90 to 50. Stakataka gains next-owner-turn 20-damage reduction.',[185,189,190,194],4)
draw(7,'normal_draw',RC,[196,197.5],beforecount=4,aftercount=5)
play(7,'item',L,'owner Active Sandslash','Heals 50 to 70; heads; item returns.',[198,200,202,205,206],5,nested=['Heal20','Heads','Return to hand'])
play(7,'item',L,'owner Active Sandslash','Reuses returned item, heals 70 to 90; heads at214.7; returns again.',[207,208,211,214.7,216,218],5,nested=['Heal20','Heads','Return to hand'])
play(7,'energy_attachment',None,'owner Active Sandslash','Second Fighting attached.',[216,216.5,217],5,{'type':'Fighting','count':1,'destination':'owner Active'})
play(7,'attack','Sandslash: Fury Swipes','opponent Active Stakataka','One head, two tails; raw30 reduced20 to10, 80 to70.',[217,224,228,230],5)
draw(8,'normal_draw',None,[232,234],beforecount=4,aftercount=5,limit='Hidden opponent draw.')
play(8,'energy_attachment',None,'opponent left Bench Copperajah','First Metal on Copperajah.',[250,252,254],5,{'type':'Metal','count':1,'destination':'opponent left bench'})
play(8,'attack','Stakataka: Brass Rock','owner Active Sandslash','40 damage, 90 to50; next-turn protection renewed.',[256,258,260,261],5)
draw(9,'normal_draw',PB,[263,264],beforecount=5,aftercount=6)
play(9,'item',PB,'owner deck','Searches Timburr; item consumption and one searched card leave count6.',[265,266,268,269],6)
draw(9,'item_search','Timburr',[268,269],1,5,6)
play(9,'bench','Timburr','owner right bench','Benches 60-HP Timburr.',[270,271],5)
play(9,'item',L,'owner Active Sandslash','Heals50 to70; tails; discarded.',[272,273,276,279,280],4,nested=['Heal20','Tails','Discard'])
play(9,'energy_attachment',None,'owner right Bench Timburr','Adds first Fighting to Timburr.',[280,281,283],4,{'type':'Fighting','count':1,'destination':'owner right bench'})
play(9,'attack','Sandslash: Fury Swipes','opponent Active Stakataka','Two heads, one tail; raw60 reduced20 to40,70 to30.',[282,288,294,296,298],4)
draw(10,'normal_draw',None,[300,302],beforecount=5,aftercount=6,limit='Hidden opponent draw.')
play(10,'energy_attachment',None,'opponent left Bench Copperajah','Second Metal: one at314 and two at318.',[310,314,318,322],6,{'type':'Metal','count':1,'destination':'opponent left bench'})
play(10,'attack','Stakataka: Brass Rock','owner Active Sandslash','40 damage,70 to30; next-turn protection renewed.',[324,326,328,330],6)
draw(11,'normal_draw',CB,[332,332.8],beforecount=4,aftercount=5)
play(11,'item_evolution',RC,'owner right Bench Timburr','Rare Candy selected333; reveal335; Conkeldurr B4 selected337 and revealed338. Evolves directly to Stage2, retaining its Fighting.',[333,335,335.6,337,338,338.6],3,nested=['Consume Rare Candy:5 to4','Select Conkeldurr B4 from hand:4 to3','Evolution resolves:150HP with prior1F'])
play(11,'supporter',W,'owner right Bench Conkeldurr','Adds one Colorless, visibly star symbol. Generated Fighting remains available after Wally.',[341,342,343,344,345],2,{'type':'Colorless','count':1,'destination':'owner right bench'},nested=['Wally consumed','One Colorless added','Large Fighting current zone remains'])
play(11,'energy_attachment',None,'owner right Bench Conkeldurr','Normal Fighting attachment leaves2F+1Colorless.',[346,347,348],2,{'type':'Fighting','count':1,'destination':'owner right bench'})
play(11,'retreat',None,'Sandslash to right bench; Conkeldurr to Active','Pays one Fighting from Sandslash, which retains one. Conkeldurr promoted by retreat, not knockout.',[349,350,351,352,353],2,{'type':'Fighting','count':1,'retreat_payment_by_type':{'Fighting':1}})
play(11,'attack','Conkeldurr B4: Bedrock Breaker','opponent Active Stakataka','100 raw reduced20 to80. Stakataka30 to0; removed; point2; Copperajah promoted only after.',[353,354,355,356,358,360,364,366],2,nested=['Attack input/presentation','80 damage after protection','HP0 356','Removal358','Point2 360','Copperajah promotion364-366','No Stadium existed, so Stadium-discard clause has no target'])
draw(12,'normal_draw',None,[367,368],beforecount=6,aftercount=7,limit='Hidden opponent draw.')
play(12,'energy_attachment',None,'opponent Active Copperajah','Third Metal attached.',[368,370,372],7,{'type':'Metal','count':1,'destination':'opponent Active'})
play(12,'supporter','May','opponent hand/deck','Public May reveal; searches two hidden Pokémon and shuffles two random hand Pokémon back. Final hand before benching6 after Supporter consumption.',[378,380,382,386,388,396,402,408.5],6,nested=['May removed7 to6','Two hidden Pokémon searched: temporary8','Two random hand Pokémon shuffled:6'])
draw(12,'supporter_search_and_return',None,[380,386,396,402],2,6,6,'Search and shuffled-back identities hidden. Temporary fan overlaps during animation; counts use printed effect and final six separated backs, not guessed identities.')
play(12,'bench',"Team Rocket's Tinkatink",'opponent right bench','Benches60-HP Tinkatink; hand6 to5.',[413,414,415],5)
play(12,'bench','Cufant','opponent left bench','Benches90-HP Cufant; hand5 to4.',[416,417,418],4)
play(12,'attack','Copperajah: Heavy Impact','owner Active Conkeldurr','80 damage,150 to70.',[423,425,426,428,429],4)
draw(13,'normal_draw',CA,[431,433],beforecount=2,aftercount=3)
play(13,'energy_attachment',None,'owner Active Conkeldurr B4','Third Fighting added, plus Wally Colorless retained.',[435,438],3,{'type':'Fighting','count':1,'destination':'owner Active'})
play(13,'attack','Conkeldurr B4: Bedrock Breaker','opponent Active Copperajah','100 damage,160 to60. No Stadium target exists.',[442,444,446,448],3,nested=['Attack','100 damage','No Stadium discard target'])
draw(14,'normal_draw',None,[448,450],beforecount=4,aftercount=5,limit='Hidden opponent draw.')
play(14,'evolution',"Team Rocket's Tinkatuff",'opponent right Bench Tinkatink','Evolves to80HP.',[452,454,456],4)
play(14,'energy_attachment',None,'opponent right Bench Tinkatuff','One Metal attached.',[460,462,464],4,{'type':'Metal','count':1,'destination':'opponent right bench'})
play(14,'attack','Copperajah: Heavy Impact','owner Active Conkeldurr','80 damage defeats70HP Conkeldurr. Opponent point1; owner selects damaged Sandslash after point award.',[468,470,472,474,476,480,482],4,nested=['Damage80','Conkeldurr HP0/removal472','Opponent point1 474-476','Owner mandatory promotion Sandslash480-482'])
draw(15,'normal_draw',PR,[485,485.6],beforecount=3,aftercount=4)
play(15,'supporter',PR,'owner hand','Research input486; reveal488; draws Poké Ball first490 then Timburr491. Hand4 -1 +2 =5.',[486,486.5,488,490,491,491.5],5,nested=['Consume Research','Reveal Poké Ball first','Reveal Timburr second'])
draw(15,'supporter_draw',PB,[490],1,3,4);draw(15,'supporter_draw','Timburr',[491,491.5],1,4,5)
turns[14]['draws_and_searches'][-1]['cards_in_reveal_order'][0]['reveal_position']=2
play(15,'item',PB,'owner deck','Searches Hitmonchan ex; hand remains5 after item/search.',[492,493,495,496],5)
draw(15,'item_search','Hitmonchan ex',[495,496],2,4,5)
play(15,'bench','Hitmonchan ex','owner center bench','Benches130HP, no Energy.',[497,500],4)
play(15,'bench','Timburr','owner right bench','Benches60HP.',[502,503],3)
play(15,'energy_attachment',None,'owner right Bench Timburr','First Fighting to Timburr; Hitmonchan ex stays unenergized.',[505,505.5,507],3,{'type':'Fighting','count':1,'destination':'owner right bench'})
play(15,'attack','Sandslash: Fury Swipes','opponent Active Copperajah','One head,two tails;30damage,60 to30.',[506,508,512,516],3)
draw(16,'normal_draw',None,[518,520],beforecount=4,aftercount=5,limit='Hidden opponent draw.')
play(16,'energy_attachment',None,'opponent right Bench Tinkatuff','Second Metal attached before evolution.',[528,530,531],5,{'type':'Metal','count':1,'destination':'opponent right bench'})
play(16,'evolution',"Team Rocket's Tinkaton",'opponent right Bench Tinkatuff','Evolves to140HP and retains two Metal.',[545,546,547,548],4)
play(16,'attack','Copperajah: Heavy Impact','owner Active Sandslash','80damage defeats30HP Sandslash. Opponent point2; owner then promotes unenergized Hitmonchan ex.',[550,551,552,554,558,560,562,563,564,566],4,nested=['Attack80','HP0/removal554','Opponent point2 558','Promotion prompt560/562','Hitmonchan ex selected563, Active by566'])
draw(17,'normal_draw',SA,[569,570],beforecount=3,aftercount=4)
play(17,'energy_attachment',None,'owner Active Hitmonchan ex','First Fighting attached after generation. Small next preview was not counted as current.',[570,571,571.5,573],4,{'type':'Fighting','count':1,'destination':'owner Active'})
play(17,'attack','Hitmonchan ex: Quick Straight','opponent Active Copperajah','50 damage with no Weakness application;30 to0, removed, then third point and Victory.',[573,574,576,577,578,579,582,583,590,591],4,nested=['Attack presentation574','Damage50 / HP0 577','Removal578','Active visibly empty579','Third owner point582','Victory590/591'])
turns[16]['board_after']['evidence_ids']=evidence([579,582]);turns[16]['board_after']['opponent']['active']['evidence_ids']=evidence([579])
turns[16]['limits'].append('Final board HP/removal and third-point award use different frames; no post-win opponent promotion is shown.')

discards=[]
for n in [1,5,9,13,17]:
    for who in ['owner','opponent']:
        sid=f'discard_{who}_t{n:02}'
        discards.append({'snapshot_id':sid,'turn_number':n,'pile_owner':who,'source_video':V,'timestamp_seconds':starts[n],
         'cards_in_view':None,'scroll_coverage':None,'full_pile_established':False,'status':'pile_not_opened_in_recording',
         'evidence_ids':evidence([starts[n]]),'limit_reason':'The recording never opens or scrolls this discard pile. A battlefield top-card preview is not a full pile view.'})
        turns[n-1]['discard_snapshot_ids'].append(sid)
for row in turns:
    allrefs=set(row['turn_evidence_ids'])
    for a in row['plays_in_order']+row['draws_and_searches']:allrefs.update(a['evidence_ids'])
    for k in ['board_at_start','board_after','owner_hand_end']:allrefs.update(row[k]['evidence_ids'])
    allrefs.update(row.get('capture_candidates',[]));allrefs.update(row.get('before_end_action_evidence_ids',[]))
    row['turn_evidence_ids']=sorted(allrefs)

opening_names=[W,'Sandshrew',C,'Sandshrew',L]
opening={'source_video':V,'timestamp_seconds':28,'expected_card_slots':5,'recorded_card_count':5,
 'cards_left_to_right':[{'position':i+1,'name':x,'basis':'Original five-card fan before any Active placement', 'evidence_ids':evidence([28],'original_opening'), 'limit_reason':None} for i,x in enumerate(opening_names)],
 'selected_active':{'name':'Sandshrew','opening_position':4,'source_video':V,'timestamp_seconds':29,'evidence_ids':evidence([29],'opening_active_selection')},
 'initial_bench_placement':{'name':'Sandshrew','opening_position':2,'bench_position':'left','evidence_ids':evidence([31,33],'opening_bench')},
 'redraw_or_replacement':'none visible','before_active_placement':True,'status':'observed','evidence_ids':evidence([28,29,31,33]),'limit_reason':None}
limits=['Matching exact20 list is absent from retrieved live Pause Games deck snapshot; QR establishes filmed semantic entities and Energy, not an existing live log version.',
 'Opponent normal draws, May search/shuffle identities and hidden hand faces are unknown.',
 'Neither discard pile is opened anywhere. Full pile content/order cannot be established.',
 'QR functional entities do not encode exact artwork/rarity. Hitmonchan ex artwork printing remains qualified.',
 'Frame times are source-local requested seek values; actual decoded presentation timestamps were not measured.',
 'This is the first-pass packet. Independent visual acceptance, duplicate check, registration and external save verification belong to the lead.']
qr=json.loads((P/'qr_intake/QR_DECODE_0002.00.json').read_text(encoding='utf-8'))
expanded=[]
for card in qr['cards']:
    for _ in range(card['count']):expanded.append({**card,'count':1,'slot':len(expanded)+1})
deck={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,
 'deck_name_in_log':None,'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
 'captured_at':'2026-10-06T17:07:52.454484+00:00','log_list_version':'batch native live snapshot, nine decks; exact matching list absent',
 'expected_card_count':20,'cards_in_log_order':None,'counts_by_name_and_variant':None,'energy_configuration_from_log':None,'actual_card_count':None,
 'capture_source_text_or_image':'../LIVE_PAUSE_GAMES_SNAPSHOT.json (lead retained snapshot; no matching deck)',
 'game_version_binding_basis':{'filmed_deck_title':'New deck 6','review_label':'Conkeldurr / Sandslash / Hitmonchan ex',
  'continuity':'QR popup closes to same selected deck, then Battle and human matchmaking. No intervening edit or deck selection change.',
  'evidence_ids':evidence([0,4,5,6,7,12,18,20,22,24],'qr_to_game_continuity'),
  'qr_image':'qr_intake/t0002.00.png','qr_receipt':'qr_intake/QR_DECODE_0002.00.json'},
 'conflicts_with_filmed_cards':[],'exact_list_status':'filmed_QR_exact20_resolved; matching_live_log_version_absent',
 'filmed_qr':{'payload_ascii_sha256':qr['payload_ascii_sha256'],'cards_in_payload_order':expanded,'counts_by_semantic_entity':qr['cards'],
   'card_count':20,'energy_configuration':[{'name':'Fighting','value':6}],
   'binding_limit':'Payload ordering groups trainers then Pokemon; it is not the missing live log display order.',
   'catalog_provenance':qr['dependencies']['catalog_provenance'],'printing_limit':'QR artwork/rarity is not encoded. Functional distinctions Conkeldurr A3/B4 and Sandslash B2/A1 are explicit.'},
 'limits':limits[:1]+limits[3:4]}
outcome={'result':'win','owner':'Dacz8976','opponent':'Adgbag','points_owner':3,'points_opponent':2,'turns':17,
 'basis':'Third knockout of opponent Copperajah by Hitmonchan ex Quick Straight, then owner third point, Victory vs Adgbag.',
 'evidence_ids':evidence([573,574,577,578,579,582,583,590,591,594],'terminal_result'),
 'concession':'none established','mode':'Deluxe Pack: Mega Emblem Event human matchmaking', 'ranked_status':'not established as ranked; event menu visible',
 'auto_control':'No Auto control/option visible during setup, all battle turns or result. Human matchmaking shown.'}
pause={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'review_date':'2026-10-06','sources':sources,
 'destination':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','deck_name':'Conkeldurr / Sandslash / Hitmonchan ex',
 'opening':opening,'packet_files':{'prose':'REVIEW.md','coverage':'COVERAGE.md','deck':'DECK_USED.json','turns':'TURN_LEDGER.json','evidence':'TURN_EVIDENCE.json'},
 'capture_status':'complete_with_recording_limits','battle_review_status':'full_first_pass_pending_independent_acceptance',
 'outcome':outcome,'limits':limits,'lead_checked':False,'match_date_local':'2026-10-05','game_count_in_source':1}
ledger={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,'turns':turns,'limits':limits}
ev={'is_template':False,'schema':'pause-games/turn-capture-v1','game_id':G,'sources':sources,'source_sha256':SHA,
 'default_capture_policy':{'owner_turn_offsets_after_draw_seconds':[1,3,6],'before_end_action_required':True,'native_resolution_required':True,
   'bottom_crop_height_fraction':0.2,'top_crop':'Native bounds [0,0,1170,700], opponent hand/clocks/Energy',
   'fixed_grid_is_turn_start_evidence':False,'discard_target_every_owner_turns':[2,3]},
 'frames':sorted(frames.values(),key=lambda x:x['requested_source_seconds']),'discard_snapshots':discards,
 'scheduled_capture_limits':['Offsets can occur after immediate plays. All candidates retained and qualified; earlier intact fans selected for turns3,5,9,11,15,17.',
 'Turn17 before-end frame573 is after Energy attachment and before attack presentation, with unzoomed intact hand. Turn15 before-end505.5 retains hand while Energy animation finishes.']}
summary={'source_video':V,'source_sha256':SHA,'review_status':'whole_source_first_pass_complete_pending_independent_acceptance','game_count':1,
 'games':[{'game_id':G,'match_date_local':'2026-10-05','outcome':outcome,'deck':'Conkeldurr / Sandslash / Hitmonchan ex'}],
 'coverage_seconds':[0,616.08966],'review_method':'Full-source visual traversal using locator grids followed by native setup, ordinary-turn action, draw and result inspection. Grids are locators only.',
 'external_registration_status':'not_performed_by_worker','archive_status':'not_performed_by_worker','limits':limits,
 'independent_acceptance_targets':[
 {'interval_seconds':[28,33],'claim':'Original5 and Active opening position4'},
 {'interval_seconds':[56,65],'claim':'Ordinary first decision: no development, End Turn; selected hand59.5'},
 {'interval_seconds':[65,93],'claim':'Full ordinary opponent turn2: Metal before Research, Cufant bench, LungeOut20'},
 {'interval_seconds':[176,194],'claim':'Full opponent turn6: Copperajah evolution before second Metal Stakataka'},
 {'interval_seconds':[194,230],'claim':'Two Lucky Ice Pops, both heads, Energy attachment and reduced10damage'},
 {'interval_seconds':[330,367],'claim':'Candy, Wally Colorless, normalFighting, retreatcost1, damage80, separatedKO/score/promotion'},
 {'interval_seconds':[367,429],'claim':'Full opponent turn12, May hidden search/shuffle, two benches, HeavyImpact'},
 {'interval_seconds':[484,518],'claim':'Research reveals Poké Ball then Timburr, searchHitmonchan, Energy goesTimburr'},
 {'interval_seconds':[518,594],'claim':'Two Metal onTinkaton; SandslashKO; promotion; currentEnergy generation; terminalHP0/removal/point/Victory'}]}
uncertainties={'source_video':V,'source_sha256':SHA,'consequential_unresolved_visual_ambiguities':[],
 'bounded_resolved':[{'issue':'Second Lucky Ice Pop coin','resolution':'Native214.7 clearly Heads; return observed218'},
 {'issue':'Wally Energy type','resolution':'Native342text and344symbols showColorless; later normal Fighting distinct'},
 {'issue':'Copperajah attachment order turn6','resolution':'Native179alreadyCopperajah; Stakataka secondMetal animation181'},
 {'issue':'Research reveal order turn15','resolution':'Poké Ball490, thenTimburr491'}],
 'remaining_recording_or_external_limits':[{'issue':x,'status':'explicit_limit','resolution':'Do not infer unavailable fact'} for x in limits],
 'astra_escalation':'Not needed: consequential candidate ambiguities resolved by bounded native inspection; hidden identities and absent external version remain limits.'}
def save(name,value):(P/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name,value in [('DECK_USED.json',deck),('PAUSE_GAME.json',pause),('TURN_LEDGER.json',ledger),('TURN_EVIDENCE.json',ev),('SUMMARY.json',summary),('UNCERTAINTIES.json',uncertainties)]:save(name,value)
(P/'REVIEW.md').write_text('''# Whole-source first pass

Source: `20261006_020518000_iOS.MP4`, SHA-256 `64968acf700ddfecc51cc5bcb01014db7afa855545057bd6934226afd35a53e7`, source-local 0.000 to 616.08966 seconds. Native frame dimensions 1170 by 2532. Review date October 6, 2026. Chicago recording date October 5, 2026, from retained metadata, not filename guessing.

One human event battle, Dacz8976 versus Adgbag. Owner wins 3 to 2 in 17 turns. The final Quick Straight deals 50 to the 30-HP Copperajah, which reaches zero HP and is removed before the third owner point and the explicit Victory result. Frames 577, 578, 579, 582 and 591 separate damage, removal, empty Active, score and result. No concession is established. Deluxe Pack: Mega Emblem Event is visible in the menu. No Auto option/control appears anywhere in the source.

The QR popup at 2 seconds belongs to New deck 6. Closing it returns directly to that selected deck, and the source proceeds to matchmaking without an intervening edit or deck change. The frozen retained QR decode resolves exactly twenty semantic card entities and Fighting-only Energy. It distinguishes Bedrock Breaker Conkeldurr from Guts Conkeldurr and Fury Swipes Sandslash from Slash Sandslash. It does not encode printing/artwork. The retrieved live Pause Games snapshot does not contain this exact deck. DECK_USED.json retains that missing-live-version limitation instead of presenting the prepared proposed deck entry as an already saved live version.

Opening before placement at 28 seconds: Wally, Sandshrew, Cyrus, Sandshrew, Lucky Ice Pop, left to right. The second Sandshrew, opening position 4, becomes Active; position 2 goes to left Bench. No redraw is visible. Opponent starts Team Rocket's Tinkatink Active with Togedemaru center and Stakataka right Bench.

All seventeen turns have separate structured rows. The nine owner-turn hand fans are retained at 59.5, 94.5, 158.3, 197.5, 264, 332.8, 433, 485.6 and 570 seconds. Each has a full native frame, full-width bottom fifth and native top crop. Draw-end offsets near 1, 3 and 6 seconds are retained and qualified, including those that are already after an immediate play. They are not mislabelled as preplay hands. Before-ending-action captures retain the final hands; turn15 at505.5 is during the last Energy animation and turn17 at573 is after attachment, before attack presentation.

The first owner decision is simply End Turn with four cards and no development. Opponent turn2 attaches Metal before Research, then benches Cufant and uses Lunge Out for20. Owner turn3 heals Sandshrew, evolves to Fury Swipes Sandslash, attaches Fighting and knocks out Tinkatink with two heads. Promotion waiting and actual Stakataka promotion are distinct from the knockout. Turn4 only attaches Stakataka's first Metal and ends. Turn5 benches its generated Fighting on Sandshrew and attacks for30.

On opponent turn6, Copperajah evolution occurs before the second Stakataka Metal attachment. Brass Rock then deals40 and gives Stakataka the temporary20 reduction. Owner turn7 plays Lucky Ice Pop twice, heals50 to70 to90, with two separate visible Heads returns, then attaches Fighting and attacks for10 after reduction. Opponent turn8 puts its generated Metal on Copperajah and repeats Brass Rock. Turn9 Poké Ball searches Timburr, which is benched right; Ice Pop heals20 and is discarded on tails; Fighting goes to Timburr; two-head Fury Swipes deals40 after reduction. Turn10 gives Copperajah its second Metal and repeats Brass Rock, leaving owner Sandslash30HP and Stakataka30HP.

Turn11 draws Bedrock Breaker Conkeldurr. Rare Candy converts right Bench Timburr directly to it. Wally then adds one Colorless, not Fighting; the normal large-circle Fighting is attached separately, leaving Conkeldurr2Fighting plus1Colorless. Sandslash pays one Fighting to retreat and keeps one. Conkeldurr's100 attack is reduced to80 and defeats Stakataka. HP zero, removal, second point and later Copperajah promotion are independently cited. No Stadium is present, so the discard-Stadium clause has no target.

Opponent turn12 adds Copperajah's third Metal, plays May with hidden searched/shuffled identities, benches Tinkatink right and Cufant left, and Heavy Impact leaves Conkeldurr70. Turn13 adds a third Fighting to Conkeldurr and attacks Copperajah from160 to60. Turn14 evolves right Tinkatink to Tinkatuff, adds Metal, and Heavy Impact defeats Conkeldurr; opponent earns its first point, then owner promotes the30-HP Sandslash.

Turn15 draws Research, plays it, and reveals Poké Ball first then Timburr. Poké Ball searches Hitmonchan ex. Hitmonchan ex is benched center, Timburr right, and Fighting attaches to Timburr. Fury Swipes deals30, leaving Copperajah30. Opponent turn16 adds Tinkatuff's second Metal, evolves it into Tinkaton, then Heavy Impact defeats Sandslash. Opponent earns point2, and owner promotes unenergized Hitmonchan ex. Turn17 draws the100-HP Slash Sandslash, attaches newly generated Fighting to Active Hitmonchan ex, and Quick Straight wins. Its no-Weakness clause explains the50 damage despite Copperajah's visible Fighting weakness.

Neither discard pile is opened or scrolled. Periodic structured discard records explicitly preserve that recording limit; the small battlefield top-card preview does not establish the pile. Hidden opponent draws and May identities remain unknown. No Tool, Stadium or special condition is visible during the checked public board states. Visible Brass Rock temporary protection is recorded and expires after its affected owner turn.

The packet is a complete first pass with recording limits, pending independent visual acceptance. The worker has not logged externally, registered, archived or certified lead acceptance. Target intervals in SUMMARY.json include ordinary owner turn1, complete opponent turns2/6/12, healing, Wally and the terminal sequence, rather than only unusual flags.
''',encoding='utf-8')
(P/'COVERAGE.md').write_text('''# Source coverage

The review traversed the complete source in chronological order, using locator grids followed by native inspection around setup, ordinary public actions, reveals, transitions and results. Grids locate footage and do not substitute for the native evidence. Exact frame presentation timestamps were not measured; all citations use source-local requested seek times.

| Source-local seconds | Material | Treatment |
|---|---|---|
| 0 to5 | QR New deck6, deck selection | Native QR receipt plus direct continuity check |
| 5 to24 | Event menu, Battle selection, human matchmaking, versus | Native menu/matchmaking frames; no second game or edit |
| 24 to56 | Opening5, Active/Bench placement, first-player setup | Original intact five before placement; selected Active traced |
| 56 to141 | Turns1 to3, ordinary first decision and opponent turn, first KO and promotion wait | All actions, draws, HP, Energy and score transitions reconciled |
| 141 to194 | Turns4 to6 | No-attack end, bench Energy, evolution order and Brass Rock |
| 194 to261 | Turns7 to8 | Both Ice Pop uses and heads, attack reduction, opponent bench Energy |
| 261 to330 | Turns9 to10 | Search/bench/heal/attachment, attack coins, ordinary opponent attachment/attack |
| 330 to367 | Turn11 and mandatory opponent promotion | Candy, Wally Colorless, separate Fighting, retreat, HP0/removal/point/promotion |
| 367 to429 | Full opponent turn12 including waiting | May reveal and hidden-identity limits, both benches, thirdMetal, attack |
| 429 to484 | Turns13 to14 and mandatory owner promotion | Attachments, evolution, attacks, KO/point and chosen Sandslash |
| 484 to518 | Turn15 | Research draw order, Poké Ball search, both bench plays, Energy target, coins |
| 518 to567 | Full opponent turn16 and promotion | Energy then Tinkaton evolution, attack, KO/point, Hitmonchan promotion |
| 567 to594 | Turn17, final KO, score and Victory | Current generation separated from preview; terminal events independently supported |
| 594 to616.08966 | Result interaction, thanks, event menu, home/end | Native frames594,600,608,615 plus end boundary; no further match |

No inter-source continuation, montage gap or second battle is present. Waiting periods, menus and all result material remain inside coverage. There is no audio-based hidden-card inference. TURN_LEDGER.json contains seventeen rows; TURN_EVIDENCE.json contains qualified start-hand candidates, native crops, before-end frames and periodic explicit discard-view limits. Original source and frozen intake identity remain unchanged.
''',encoding='utf-8')
print(json.dumps({'written':True,'turns':len(turns),'frames':len(frames),'game_count':1}))
