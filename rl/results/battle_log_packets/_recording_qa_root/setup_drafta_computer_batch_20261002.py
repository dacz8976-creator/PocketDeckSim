"""Bound the owner's five Auto and three manual games, preserving originals."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD'
AUTO = ['205230', '205731', '210612', '210952', '211613']
MANUAL = ['214254', '215203', '215825']
SELECTED = ['20261002_' + stamp + '000_iOS.MP4' for stamp in AUTO + MANUAL]
PROBE = r'C:\Program Files\MiniTool Screen Recorder\FFmpeg\ffprobe.exe'
DESTINATION = None
DECK_SOURCE = 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def group(name):
    return 'auto' if name.split('_')[1][:6] in AUTO else 'manual'

def reviewer(name):
    return '/root/drafta_' + ('auto_' if group(name) == 'auto' else 'manual_') + name.split('_')[1][:6]

def packet_for(name):
    return BATCH / (Path(name).stem + ('_auto_sol' if group(name) == 'auto' else '_shark_sol'))

def initialize():
    BATCH.mkdir(exist_ok=True)
    if not (BATCH / 'INDEX_BEFORE.json').exists():
        save(BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
    screenshots = []
    screenshot_dir = BATCH / 'opponent_deck'; screenshot_dir.mkdir(exist_ok=True)
    for name in ['20261002_205209000_iOS.png', '20261002_205214000_iOS.png', '20261002_205218000_iOS.png']:
        original = ROOT / name; target = screenshot_dir / name
        sha = hashlib.sha256(original.read_bytes()).hexdigest()
        if not target.exists():
            shutil.copy2(original, target)
        assert hashlib.sha256(target.read_bytes()).hexdigest() == sha
        screenshots.append({'original': str(original), 'copy': str(target), 'sha256': sha})
    opponent = [('Wailmer',2),('Wailord ex',1),('Meowth',1),('Frigibax',2),('Arctibax',2),('Baxcalibur',1),('Squirtle',2),('Wartortle',2),('Mega Blastoise ex',1),('X Speed',1),('Poké Ball',2),("Professor's Research",2),('Soothing Shore',1)]
    owner = [('Carvanha','B4 034',2),('Mega Sharpedo ex','B4 035',2),('Alolan Vulpix','B2 028',2),('Alolan Ninetales ex','B2 029',2),('Lapras','A3 044',1),('Misty','A1 220',2),("Professor's Research",'P-A 007',2),('Poké Ball','P-A 005',2),('Copycat','B1 225',1),('Cyrus','A2 150',1),('Irida','A2a 072',1),('Elegant Cape','B3b 065',1),('Lucky Ice Pop','B2 145',1)]
    assert sum(c for _,c in opponent) == sum(c for _,_,c in owner) == 20
    if not (BATCH / 'OPPONENT_DECK.json').exists():
        save(BATCH / 'OPPONENT_DECK.json', {'deck_name':'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)', 'energy_configuration':['Water'], 'difficulty':None, 'difficulty_status':'Awaiting source-visible opening selection; screenshots show deck list, not difficulty.', 'cards_in_screenshot_order':[{'name':name,'variant':None} for name,count in opponent for _ in range(count)], 'counts_by_name':dict(opponent), 'total_card_slots':20, 'basis':'Root inspected all three owner-supplied native screenshots; overlap deduplicated, not treated as extra copies.', 'game_binding_basis':'Owner states all eight games use the same computer opponent; workers verify filmed core/setup for conflicts.', 'screenshots':screenshots, 'hidden_hand_rule':'A known complete opponent deck is not evidence of a concealed draw or held card.', 'set_ids_not_inferred':True})
    if not (BATCH / 'OWNER_DECK_SNAPSHOT.json').exists():
        save(BATCH / 'OWNER_DECK_SNAPSHOT.json', {'deck_name_in_log':'Draft A: Shark Tempo', 'source_url':DECK_SOURCE, 'retrieved_utc':datetime.now(timezone.utc).isoformat(), 'retrieval_basis':'Live visible Pause Games Decks tab read through browser; expanded Draft A list.', 'log_list_version':'Original Draft A with two Misty; displayed source draft-A-shark-tempo.txt, on main since 9cc6667', 'energy_configuration':['Water'], 'exact_list_status':'verified_live_20_card_snapshot_owner_version_confirmed', 'game_version_binding_basis':'Owner explicitly says original draft A list with Misty. Workers must flag conflicts with filmed cards; list does not establish unseen hands.', 'cards_in_log_order':[{'name':name,'variant':variant} for name,variant,count in owner for _ in range(count)], 'counts_by_name_and_variant':[{'name':name,'variant':variant,'count':count}for name,variant,count in owner], 'actual_card_count':20, 'owner_testimony':'Use the original draft A list (with Misty), same setup as draft A pause games.', 'limits':['Visible gameplay may use another printing of the same card. Log version labels are not automatically physical filmed printing identities.']})
    if not (BATCH / 'OWNER_CONTEXT.json').exists():
        save(BATCH / 'OWNER_CONTEXT.json', {'requested_utc':datetime.now(timezone.utc).isoformat(),'date_local':'2026-10-02','approved_games':8,'auto_games':5,'owner_piloted_games':3,'selected_sources':SELECTED,'requested_destination':DESTINATION,'protocol':'PAUSE_GAMES_REVIEW_PROTOCOL.md','explicit_protocol_scope_expansion':'Owner requests the full Pause Games protocol for these computer Auto and manual comparison games.','owner_setup':'Original Draft A: Shark Tempo with Misty; same computer opponent for all eight.','owner_recording_testimony':'Beginning screen through end for every recording.','classification':'computer_battle','excluded_from_ladder':True,'action_authorship':'Five Auto; three owner-piloted. Verify visible indicator and mode changes independently.','suffixes':{'auto':'_auto_sol','manual':'_shark_sol'},'opponent_deck':'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)','example_name_not_actual_deck':'User supplied Inteleon as an example folder name; screenshots establish Blastoise/Wailord.','no_simulator_changes':True,'no_training':True})
    for name in SELECTED:
        packet=packet_for(name);packet.mkdir(exist_ok=True)
        for template in (ROOT/'Review_Log/templates/pause_games').glob('*.template.json'):
            target=packet/template.name.replace('.template','')
            if not target.exists():shutil.copy2(template,target)
        if not (packet/'ASSIGNMENT.md').exists():
            shutil.copy2(ROOT/'Review_Log/templates/pause_games/ASSIGNMENT.md',packet/'ASSIGNMENT.md')
    note=BATCH/'BATCH_NOTE.md'
    if not note.exists():
        note.write_text('# Draft A against the fixed computer deck\n\nEight games: five Auto and three piloted by Dustin. All are computer battles and excluded from ladder totals. The owner confirms the original Draft A: Shark Tempo list, including two Misty, for this comparison. Auto packets use `_auto_sol`; owner-play packets use `_shark_sol`. Original movie names are preserved.\n\nComputer deck: **Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)**, Water Energy. Difficulty awaits confirmation from the beginning screens. The three preserved [deck screenshots](opponent_deck/) establish twenty opponent card slots; [the deck snapshot](OPPONENT_DECK.json) records duplicates. A deck list does not reveal concealed hand cards.\n\nThe full Pause Games protocol applies to all eight by the owner\'s explicit request. [Owner deck snapshot](OWNER_DECK_SNAPSHOT.json) was copied from the live Pause Games list. Each game will carry its own snapshot and structured turn ledger. Independent acceptance, registration and safe archival remain required.\n',encoding='utf-8')

def intake(name):
    packet=packet_for(name);video=ROOT/name;binding_path=packet/'SOURCE.json'
    if binding_path.exists():
        print(name+': source already bound; no new hash',flush=True);return
    assert video.is_file() and not (ROOT/'Reviewed'/name).exists()
    with (ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')as file:
        row=next((r for r in csv.DictReader(file)if r['Video']==name),None)
    assert row is None, 'New source already has a review assignment; coordinate first.'
    subprocess.run(['attrib','+P','-U',str(video)],check=True,capture_output=True)
    before=video.stat();print('Reading and registering '+name,flush=True)
    result=subprocess.run([sys.executable,str(ROOT/'Review_Log/review_log.py'),'--root',str(ROOT),'record','--video',name,'--reviewer',reviewer(name),'--status','in_progress','--scope','Whole new computer battle under full Pause Games capture protocol: setup, all turns, ending','--evidence',str(BATCH/'OWNER_CONTEXT.json'),'--notes','Bounded eight-game owner request. Original Draft A with Misty versus same computer deck. '+group(name)+' group; all excluded from ladder. Root is sole shared writer and archiver.'],capture_output=True,text=True)
    if result.returncode:
        wait_path = packet/'SOURCE_ACCESS_WAIT.json'
        if wait_path.exists():
            history = packet/'source_access_history'; history.mkdir(exist_ok=True)
            prior = read(wait_path)
            archive_name = prior['attempt_utc'].replace(':','').replace('+','_')+'.json'
            archive_path = history/archive_name
            if not archive_path.exists(): shutil.copy2(wait_path,archive_path)
        save(packet/'SOURCE_ACCESS_WAIT.json',{'source':name,'attempt_utc':datetime.now(timezone.utc).isoformat(),'operation':'Source hash and initial in-progress registration','status':'source_read_not_completed','source_binding_frozen':False,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'limit':'This is an access/delivery failure, not evidence of corrupt movie bytes. Owner states uploads/downloads take time.'})
        print(json.dumps({'source':name,'source_binding_frozen':False,'status':'Source read not completed; access receipt saved','error':result.stderr[-1200:]}),flush=True)
        return
    events=[read(p)for p in (ROOT/'Review_Log/events').glob('*.json')]
    event=max((e for e in events if e.get('video_basename')==name),key=lambda e:e['logged_at_utc'])
    assert event['status']=='in_progress' and event['reviewer']==reviewer(name)
    probe=json.loads(subprocess.check_output([PROBE,'-v','error','-show_entries','format=duration:stream=width,height,codec_name,start_time','-of','json',str(video)],timeout=300))
    after=video.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'Upload changed during intake; do not freeze.'
    assert event['video_bytes']==after.st_size
    save(binding_path,{'video_basename':name,'sha256':event['video_sha256'],'bytes':event['video_bytes'],'duration_seconds':float(probe['format']['duration']),'streams':probe['streams'],'source_path_at_review':str(video),'recording_relationships':[],'source_identity_basis':'Review_Log CLI verified SHA and stable file during hashing; size/mtime also stable through probe.','identity_verified_event_id':event['event_id'],'intake_utc':datetime.now(timezone.utc).isoformat(),'requested_log':DESTINATION,'owner_deck':'Original Draft A: Shark Tempo with Misty','owner_testimony':'Same computer opponent for eight complete recordings, five Auto followed by three manually piloted.','classification':'computer_battle','excluded_from_ladder':True,'expected_action_authorship':'game Auto'if group(name)=='auto'else'owner manual','match_date_local':'2026-10-02','recording_date_basis':'Owner supplied October2 batch and filenames; exact filename clock timezone not established.'})
    save(packet/'ASSIGNMENT.json',{'video_basename':name,'source_sha256':event['video_sha256'],'reviewer':reviewer(name),'review_model':'gpt-6.1-sol','reasoning_effort':'high','assigned_utc':datetime.now(timezone.utc).isoformat(),'requested_log':DESTINATION,'ranked_ladder_eligible':False,'group':group(name),'packet':str(packet),'owner_deck_snapshot':str(BATCH/'OWNER_DECK_SNAPSHOT.json'),'opponent_deck_snapshot':str(BATCH/'OPPONENT_DECK.json'),'protocol':str(ROOT/'PAUSE_GAMES_REVIEW_PROTOCOL.md'),'review_scope':'Entire supplied recording including all setup, turns and ending; draw-timed hand capture supplement required.','lead_only_shared_writes':True})
    print(json.dumps({'source':name,'packet':str(packet),'duration_seconds':float(probe['format']['duration']),'sha256':event['video_sha256'],'registered_in_progress':True}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--video',choices=SELECTED);parser.add_argument('--initialize-only',action='store_true');args=parser.parse_args()
    initialize()
    if not args.initialize_only:
        for name in [args.video]if args.video else SELECTED:intake(name)
