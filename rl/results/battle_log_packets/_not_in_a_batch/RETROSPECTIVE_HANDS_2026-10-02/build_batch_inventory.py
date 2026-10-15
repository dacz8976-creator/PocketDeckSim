import csv, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
groups = {
    'sharpedo': ['20261002_132311000', '20261002_115323000', '20261002_143837000'],
    'wailord': ['20261002_021402000', '20261002_022135000'],
    'ladder': ['20260907_232617000', '20260908_012720000', '20260908_021327000', '20260908_022627000', '20260908_190031000', '20260908_190933000', '20260909_023151000', '20260909_032418000', '20260928_200654000', '20260929_002539000', '20260929_020916000']
}
index = {r['Video']: r for r in csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig')) if r.get('Video')}
def winpath(p):
    if p.startswith('/mnt/c/'):
        return 'C:/' + p[7:]
    return p
inventory = []
for group, stems in groups.items():
    for stem in stems:
        name = stem + '_iOS.MP4'
        row = index[name]
        refs = [winpath(p.strip()) for p in row['Review evidence'].split('|')]
        events = []
        for eventpath in (ROOT/'Review_Log/events').glob('*.json'):
            event = json.loads(eventpath.read_text(encoding='utf-8-sig'))
            if event.get('video_basename') == name:
                events.append({'path': str(eventpath), 'status': event.get('status'), 'timestamp': event.get('logged_at_utc', event.get('log_time_utc')), 'reviewer': event.get('reviewer')})
        inventory.append({'group':group, 'source':name, 'index_status':row['Status'], 'location':str(ROOT/row['Location']), 'logical_bytes':(ROOT/row['Location']).stat().st_size, 'accepted_evidence':[{'path':p,'exists':Path(p).exists()} for p in refs], 'events':events, 'supplement_status':'pilot_in_progress' if stem in groups['sharpedo'] else 'queued', 'supplement_path':str(BATCH/stem)})
(BATCH/'INVENTORY.json').write_text(json.dumps({'generated_utc':datetime.now(timezone.utc).isoformat(),'approved_limit':19,'recordings':inventory},indent=2),encoding='utf-8')
deckrows = {
    'Draft A: Shark Tempo': [('Carvanha','B4 034',2),('Mega Sharpedo ex','B4 035',2),('Alolan Vulpix','B2 028',2),('Alolan Ninetales ex','B2 029',2),('Lapras','A3 044',1),('Misty','A1 220',2),("Professor's Research",'P-A 007',2),('Poké Ball','P-A 005',2),('Copycat','B1 225',1),('Cyrus','A2 150',1),('Irida','A2a 072',1),('Elegant Cape','B3b 065',1),('Lucky Ice Pop','B2 145',1)],
    'Wailord / Indeedee wall': [('Wailmer','B4 036',2),('Wailord','B1 057',1),('Wailord ex','B4 037',1),('Indeedee ex','B1 121',2),('Poké Ball','P-A 005',2),('Lucky Ice Pop','B2 145',2),('Heavy Helmet','B1 219',2),("Professor's Research",'P-A 007',2),('Cyrus','A2 150',1),('Irida','A2a 072',1),('Pokémon Center Lady','A2b 070',1),('Copycat','B1 225',1),('Soothing Shore','B4 154',2)]
}
decks=[]
for label, rows in deckrows.items():
    slots = [{'name':n,'variant':v} for n,v,c in rows for _ in range(c)]
    assert len(slots)==20
    decks.append({'deck_name':label,'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','retrieved_utc':datetime.now(timezone.utc).isoformat(),'retrieval_method':'Live browser accessibility reading, Decks tab, list expanded','captured_text':str(BATCH/'DECK_LOG_CAPTURE.txt'),'energy_configuration':'Water','exact_list_status':'verified_current_log_20_slots','historical_version_status':'current_snapshot; no unseen hand identities inferred; compare historical log and filmed variants before declaring exact game version','cards_in_log_order':slots,'counts_by_name_and_variant':[{'name':n,'variant':v,'count':c} for n,v,c in rows]})
(BATCH/'DECK_SNAPSHOTS.json').write_text(json.dumps({'is_template':False,'decks':decks},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'recordings':len(inventory),'missing_accepted_paths':sum(not p['exists'] for r in inventory for p in r['accepted_evidence']),'deck_slots':[len(d['cards_in_log_order']) for d in decks]}))
