"""Freeze the nine lists read from the live Decks UI on October 6, 2026."""
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = [
('Wailord / Indeedee wall','Water','decks/dustin/03-wailord-indeedee-wall.txt',[
(2,'Wailmer','B4 036'),(1,'Wailord','B1 057'),(1,'Wailord ex','B4 037'),(2,'Indeedee ex','B1 121'),(2,'Poké Ball','P-A 005'),(2,'Lucky Ice Pop','B2 145'),(2,'Heavy Helmet','B1 219'),(2,"Professor's Research",'P-A 007'),(1,'Cyrus','A2 150'),(1,'Irida','A2a 072'),(1,'Pokémon Center Lady','A2b 070'),(1,'Copycat','B1 225'),(2,'Soothing Shore','B4 154')]),
('Mega Blaziken tournament list','Fire','decks/dustin/06-mega-blaziken-tournament-list.txt',[
(2,'Torchic','B1 033'),(2,'Mega Blaziken ex','B1 036'),(1,'Heatmor','B1 044'),(1,'Castform Sunny Form','B3 024'),(2,'Poké Ball','P-A 005'),(2,'Rare Candy','A3 144'),(2,'Flame Patch','B1 217'),(1,'Field Blower','B3 147'),(1,'Rocky Helmet','A2 148'),(2,"Professor's Research",'P-A 007'),(1,'Cyrus','A2 150'),(2,'Copycat','B1 225'),(1,'Hiking Trail','B2b 069')]),
('Mega Manectric / Heliolisk','Lightning','decks/dustin/09-mega-manectric-heliolisk.txt',[
(2,'Helioptile','B1a 028'),(2,'Heliolisk','B4 061'),(2,'Electrike','B2b 026'),(2,'Mega Manectric ex','B2b 027'),(2,'Poké Ball','P-A 005'),(2,"Clemont's Backpack",'B1a 066'),(1,'Field Blower','B3 147'),(1,'Elegant Cape','B3b 065'),(2,"Professor's Research",'P-A 007'),(1,'Cyrus','A2 150'),(1,'Clemont','B1a 068'),(1,'Copycat','B1 225'),(1,'Training Area','B2 153')]),
('Alolan Ninetales / Raticate','Water','decks/dustin/13-a-ninetales-raticate.txt',[
(2,'Alolan Vulpix','B2 028'),(2,'Alolan Ninetales ex','B2 029'),(2,"Team Rocket's Rattata",'B4a 058'),(2,"Team Rocket's Raticate ex",'B4a 059'),(2,'Poké Ball','P-A 005'),(1,'Field Blower','B3 147'),(1,'Elegant Cape','B3b 065'),(2,"Professor's Research",'P-A 007'),(1,'Sabrina','A1 225'),(1,'Cyrus','A2 150'),(1,'Ilima','A3 149'),(1,'Copycat','B1 225'),(1,'Sightseer','B2 150'),(1,'Soothing Shore','B4 154')]),
('Brew 7: Hoopa / Darkrai / Sableye','Darkness','decks/brews/brew-07-hoopa-darkrai-sableye.txt',[
(2,'Hoopa ex','B4 103'),(1,'Darkrai ex','A2 110'),(1,'Mega Sableye ex','B3b 041'),(2,"Professor's Research",'P-A 007'),(2,'Cyrus','A2 150'),(1,'Copycat','B1 225'),(1,'Pokémon Center Lady','A2b 070'),(2,'Poké Ball','P-A 005'),(2,'Lucky Ice Pop','B2 145'),(1,'Repel','A3a 064'),(1,'X Speed','P-A 002'),(1,'Field Blower','B3 147'),(2,'Deceptive Needle','B4 148'),(1,'Starting Plains','B2 154')]),
('Draft A: Shark Tempo','Water','decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt (on main since 9cc6667)',[
(2,'Carvanha','B4 034'),(2,'Mega Sharpedo ex','B4 035'),(2,'Alolan Vulpix','B2 028'),(2,'Alolan Ninetales ex','B2 029'),(1,'Lapras','A3 044'),(2,'Misty','A1 220'),(2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(1,'Copycat','B1 225'),(1,'Cyrus','A2 150'),(1,'Irida','A2a 072'),(1,'Elegant Cape','B3b 065'),(1,'Lucky Ice Pop','B2 145')]),
('Draft B: Tide Heal','Water','decks/brews/drafts_2026-10-01/draft-B-tide-heal.txt (on main since 9cc6667)',[
(2,'Staryu','B4 032'),(2,'Starmie','B4 033'),(2,'Feebas','A4a 021'),(2,'Milotic','A4a 022'),(1,'Wailmer','B1 056'),(1,'Wailord','B1 057'),(2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(1,'Copycat','B1 225'),(1,'Cyrus','A2 150'),(1,'Irida','A2a 072'),(1,'Soothing Shore','B4 154'),(1,'Lucky Ice Pop','B2 145'),(1,'Elegant Cape','B3b 065')]),
('Draft C: Meowstic / Hatterene v2','Psychic','decks/brews/drafts_2026-10-01/draft-C-meowstic-hatterene-v2.txt (on main since 9cc6667)',[
(2,'Espurr','B3 065'),(2,'Meowstic','B3 066'),(2,'Hatenna','B3 069'),(2,'Hatterene','B3 071'),(2,'Comfey','A3 080'),(2,'Rare Candy','A3 144'),(2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(1,'Copycat','B1 225'),(1,'Cyrus','A2 150'),(1,'Peculiar Plaza','B2 155'),(1,'Pokémon Center Lady','A2b 070')]),
('Draft D: Entei / Grimhound','Fire','decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt (amended Oct 2, branch sonnet/drafts-fixes 4c3184f; not yet on main)',[
(2,'Entei ex','A4a 010'),(2,'Houndour','A2a 011'),(1,'Mega Houndoom ex','P-B 080'),(2,'Victini','B3 025'),(2,'Magby','A4 032'),(2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(2,'Flame Patch','B1 217'),(2,'Rainbow Cave','B4 155'),(1,'Cyrus','A2 150'),(1,'Giant Cape','A2 147'),(1,'Copycat','B1 225')])]

decks=[]
for name,energy,version,rows in DATA:
    assert sum(c for c,_,_ in rows)==20
    decks.append({'deck_name_in_log':name,'energy_configuration':[energy],'log_list_version':version,
        'cards_in_log_order':[{'name':n,'variant':v} for c,n,v in rows for _ in range(c)],
        'counts_by_name_and_variant':[{'name':n,'variant':v,'count':c} for c,n,v in rows],
        'actual_card_count':20,'captured_source_text':'\n'.join(f'{c}\t{n}\t{v}' for c,n,v in rows),
        'exact_list_status':'verified_live_log_snapshot_game_version_awaits_film_or_QR',
        'game_version_binding_basis':None})
out=Path(__file__).parent/'LIVE_DECK_SNAPSHOT.json'
assert not out.exists(), 'Frozen snapshot already exists'
out.write_text(json.dumps({'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd','retrieved_utc':datetime.now(timezone.utc).isoformat(),
    'retrieval_basis':'Lead expanded all nine Decks UI lists through CUA and read each table; quantities and variant labels preserved.',
    'decks':decks,'limits':['Current log lists do not establish which version was filmed. QR comparison pending. Names in a deck do not prove concealed hands.']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
