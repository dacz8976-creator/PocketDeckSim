import json,hashlib,datetime,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
def read(n):return json.loads((P/n).read_text(encoding='utf-8-sig'))
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reject=read('independent_sol/CHECK_RESULT.json')
for n,h in reject['checked_input_sha256'].items():
 assert hashlib.sha256((P/'independent_sol/rejected_original_8'/n).read_bytes()).hexdigest()==h

# R1: each reveal uses the native full-frame zoom of that arrival.
x=read('TURN_LEDGER.json');g=x['turns'][0]['draws_and_searches'][2]
for card,t,ref in zip(g['cards_in_reveal_order'],[66.,67.,68.,68.5],['n66_00','n67_00','n68_00','n68_50']):
 card['timestamp_seconds']=t;card['evidence_ids']=[ref]
g['timestamp_seconds']=66.;g['evidence_ids']=['n66_00','n67_00','n68_00','n68_50']
g['timing_basis']='Observed retained reveal anchors, not exact arrival onset.'
x['turns'][0]['turn_evidence_ids']=list(dict.fromkeys(x['turns'][0]['turn_evidence_ids']+['n66_00']))

# R2: recursively replace only clear-hand/board references in the ledger.
def clear_ref(v):
 if isinstance(v,dict):return {k:clear_ref(i) for k,i in v.items()}
 if isinstance(v,list):return [clear_ref(i) for i in v]
 if v=='n168_50':return 'n167_50'
 return v
x=clear_ref(x);x['turns'][2]['timing']['before_end_action_seconds']=167.5
x['turns'][2]['timing']['terminal_error_visible_seconds']=168.5
x['turns'][2]['board_after']['phase']='Last clear board at 167.50 before terminal modal; no turn 3 voluntary play'
save('TURN_LEDGER.json',x)

x=read('TURN_EVIDENCE.json')
labels={65.5:'Copycat draw transition before first Research zoom; no settled Research yet.',66:'Copycat FIRST Professor\'s Research reveal zoom, no prior Research settled in hand.',66.5:'Copycat two Research cards in transition; first beneath second arriving card.',67:'Copycat SECOND Professor\'s Research reveal zoom, first Research already in hand.',67.5:'Copycat arrival transition; not selected as individual reveal anchor.',68:'Copycat THIRD reveal Heavy Helmet zoom, two Research cards settled underneath.',68.5:'Copycat FOURTH reveal Lucky Ice Pop zoom, Helmet and two Research beneath it.',69:'Copycat post-arrival transition into four-card hand.',69.5:'Copycat settled four-card hand after all four reveals; not Pop arrival anchor.',167.5:'Last clear five-card hand and both boards before terminal modal; one unused Darkness visible.',168.5:'Terminal error modal already enlarged over blurred board/hand; unsuitable for final hand or board evidence.'}
for f in x['frames']:
 t=f['requested_source_seconds']
 if t in labels:f['observation']=labels[t];f['suitability_or_limit']=labels[t]
 if t in [66,67,68,68.5]:f['role']='native_individual_Copycat_reveal';f['unzoomed']=False;f['hand_spread']=False
 if t==69.5:f['role']='native_post_Copycat_settled_hand';f['unzoomed']=True;f['hand_spread']=True
 if t==167.5:f['role']='before_end_hand';f['unzoomed']=True;f['hand_spread']=True;f['before_first_play']=True
 if t==168.5:f['role']='native_terminal_error';f['unzoomed']=False;f['hand_spread']=False;f['selected_for_start_hand']=False;f['before_first_play']=None
x['discard_snapshots']=clear_ref(x['discard_snapshots'])
x['scheduled_capture_limits']=[z.replace('native167 and168.5','native167 and167.5') for z in x['scheduled_capture_limits']]
save('TURN_EVIDENCE.json',x)
x=clear_ref(read('UNCERTAINTIES.json'));save('UNCERTAINTIES.json',x)

# Opening card1's clipped label is explicitly corroborated by its retained artwork.
x=read('PAUSE_GAME.json');c=x['opening']['cards_left_to_right'][0]
c['basis']='Opening card artwork at 27.50 matches the clearly named Copycat retained at 43.50; opening name label clipped.'
c['evidence_ids']=['n27_50','n43_50'];c['limit_reason']='Opening label clipped; identity corroborated by same artwork in later named hand.'
save('PAUSE_GAME.json',x)

for n in ['REVIEW.md','COVERAGE.md']:
 text=(P/n).read_text(encoding='utf-8')
 text=text.replace("Professor's Research at 67.00, another Professor's Research at 68.00, Heavy Helmet at 68.50, Lucky Ice Pop at 69.50", "Professor's Research at 66.00, another Professor's Research at 67.00, Heavy Helmet at 68.00, Lucky Ice Pop at 68.50. These are observed reveal sample anchors, not exact onset times. Native 69.50 shows the settled four-card hand after all arrivals")
 text=text.replace('60.50,67.00,68.00,68.50,69.50,71.50','60.50,66.00,67.00,68.00,68.50,69.50,71.50')
 text=text.replace('Native168.50 retains the last clear hand and board immediately before terminal error','Native167.50 retains the last clear hand and board before terminal error;168.50 already shows the error modal over a blurred board and hand')
 text=text.replace('native 168.50,5 cards before terminal error','native 167.50,5 cards before terminal error')
 text=text.replace('164.50,166.00,167.00,168.50,169.00','164.50,166.00,167.00,167.50,168.50,169.00')
 if n=='REVIEW.md':text=text.replace('At27.50 all five initial cards are visible before placement, left to right: Copycat,','At27.50 all five initial card faces are visible before placement. The first name label is clipped, but its artwork matches the clearly named Copycat at43.50. Left to right: Copycat,')
 if n=='COVERAGE.md':text=text.replace('All 5 named, position4 Pawniard','All 5 named; opening Copycat label clipped and artwork corroborated at43.50; position4 Pawniard')
 # Space authored prose without changing filenames, IDs, hashes, dates or URLs.
 text=re.sub(r'\b(at|At|to|Native|native|overview|Turn|turn|fan|hand|candidate|confirms|show|damage|visible|the|retrieved|Duration|position)(?=\d)',r'\1 ',text)
 text=re.sub(r'(?<=\d)(HP)\b',r' \1',text)
 text=text.replace('Source:20261013','Source: 20261013').replace('Reviewer:/root','Reviewer: /root').replace('SHA-256:739','SHA-256: 739').replace('arithmetic:3','arithmetic: 3').replace(' =4',' = 4').replace('October 12,2026','October 12, 2026').replace('March','March')
 text=re.sub(r',(?=\d)',', ',text);text=re.sub(r';(?=\w)','; ',text)
 (P/n).write_text(text,encoding='utf-8')

cmd=['C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-X','utf8','Recording_QA/BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py',str(P)]
r=subprocess.run(cmd,text=True,capture_output=True,encoding='utf-8');print(r.stdout);assert r.returncode==0
(P/'STRUCTURAL_VALIDATION.json').write_text(r.stdout,encoding='utf-8')
hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in names}
save('REVIEW_PACKET_HASHES.json',dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_video=read('SOURCE.json')['video_basename'],source_sha256=read('SOURCE.json')['sha256'],files=hashes,file_count=8,status='refrozen_pending_independent_R1_R2_recheck',reviewer='/root/pause_20261013_015011000_iOS',repairs=['R1','R2'],rejected_original_directory='independent_sol/rejected_original_8'))
print(json.dumps({'refrozen_count':8,'files':hashes},indent=2))
