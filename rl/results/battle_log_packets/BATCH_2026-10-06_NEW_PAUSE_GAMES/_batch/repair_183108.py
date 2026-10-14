"""One-time root corrections of four frozen independent 183108 findings."""
import hashlib,json,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
B=Path(__file__).resolve().parent;P=B/'20261005_183108000_iOS'
receipt=P/'independent_sol/CHECK_RESULT.json';r=json.loads(receipt.read_text(encoding='utf-8'))
backup=P/'original_before_R1_R4';assert not backup.exists();backup.mkdir()
shutil.copy2(receipt,P/'independent_sol/CHECK_RESULT.rejected_R1_R4.json')
for n,h in r['checked_input_sha256'].items():
    assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
    shutil.copy2(P/n,backup/n)
def read(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
l=read('TURN_LEDGER.json')
draw=l['turns'][5]['draws_and_searches'][0]
assert (draw['hand_count_before'],draw['hand_count_after'])==(3,4)
draw['hand_count_before']=4;draw['hand_count_after']=5
draw['evidence_ids']=['F_0203_00','F_0205_00']
draw['hand_count_basis']='Four native card backs203, five205 after hidden normal draw, still five217 before buffered refresh; three219.5 after two Pokemon cards leave.'
tools=0;stadia=0
for t in l['turns']:
    for key in ('board_at_start','board_after'):
        b=t[key]
        if b.get('stadium') is None:
            b['stadium']='none';b['stadium_status']='observed_absent';b['stadium_basis']='No Stadium in this cited pre-Plaza native frame.';stadia+=1
        for player in ('owner','opponent'):
            side=b[player]
            for mon in [side.get('active')]+side.get('bench_in_position_order',[]):
                if isinstance(mon,dict) and mon.get('name') and mon.get('status')!='visibly_empty' and mon.get('tool') is None:
                    mon['tool']='none';mon['tool_status']='observed_absent';mon['tool_basis']='No attached Tool visible on this Pokemon in cited native evidence.';tools+=1
end=l['turns'][4]['owner_hand_end']
end['basis']='Copycat and Scolipede are readable in the two-card ending fan beneath the enlarged Active attack selection overlay.'
end['limit_reason']='196.5 has a large Scolipede attack zoom; it is a witnessed two-card ending hand, not an unzoomed board.'
terminal=l['turns'][9]['board_after']
def replace_refs(value):
    if isinstance(value,dict):
        for key,val in value.items():
            if key=='evidence_ids':value[key]=['F_0389_00' if v=='F_0392_00' else v for v in val]
            else:replace_refs(val)
    elif isinstance(value,list):
        for val in value:replace_refs(val)
replace_refs(terminal)
terminal['timestamp_seconds']=389
terminal['phase']='Composite terminal boundary: clean post-removal board389 with owner2/opponent1; separate392 award establishes opponent capped total3.'
terminal['basis']='Pokemon, empty slots, Energy Zones, Stadium and owner points are witnessed389. Opponent awarded total comes from392 overlay, which obscures Active spots.'
terminal['evidence_ids']=['F_0389_00','F_0392_00']
terminal['opponent']['points_before_award']=1
terminal['opponent']['points_before_award_seconds']=389
terminal['opponent']['points_before_award_evidence_ids']=['F_0389_00']
terminal['opponent']['points']=3
terminal['opponent']['points_observed_seconds']=392
terminal['opponent']['points_evidence_ids']=['F_0392_00']
terminal['opponent']['evidence_ids']=['F_0389_00','F_0392_00']
terminal['owner']['points_observed_seconds']=389
terminal['owner']['points_evidence_ids']=['F_0389_00']
auto=next(a for a in l['turns'][9]['automatic_events_in_order'] if a['kind']=='knockout_removal')
auto['first_clear_empty_active_seconds']=389
auto['result']='388 removal animation;389 first clean empty owner Active. Benched Mega170 Darkness1 remains; no terminal promotion.'
if 'F_0389_00' not in auto['evidence_ids']:auto['evidence_ids'].append('F_0389_00')
if 'F_0389_00' not in l['turns'][9]['turn_evidence_ids']:l['turns'][9]['turn_evidence_ids'].append('F_0389_00')
save('TURN_LEDGER.json',l)
e=read('TURN_EVIDENCE.json');frames={f['requested_source_seconds']:f for f in e['frames']}
mapping=next(x for x in r['required_repairs'] if x['id']=='R3_CAPTURE_QUALIFICATIONS')['supported_unzoomed_hand_spread_by_requested_seconds']
for sec,flags in mapping.items():
    f=frames[float(sec)]
    f.update(flags)
    if float(sec)==196.5:
        f['observation']='Large Scolipede attack zoom; Copycat and Scolipede ending fan readable/count2.'
        f['suitability_or_limit']='Before attack resolution, but enlarged Active overlay; ending hand witnessed, unzoomed qualification false.'
    elif f.get('before_first_play') is False:
        f['suitability_or_limit']='Postplay candidate: actual zoom/spread properties recorded independently; changed hand is unsuitable as original intact preplay hand.'
save('TURN_EVIDENCE.json',e)
save('ROOT_CORRECTIONS_R1_R4.json',{'repaired_utc':datetime.now(timezone.utc).isoformat(),'frozen_rejection':'independent_sol/CHECK_RESULT.rejected_R1_R4.json','R1':'T6 hidden normal draw4 to5; unknown card and buffered action order remain unknown.','R2':{'known_absent_stadia':stadia,'occupied_noTool_fields':tools},'R3':mapping,'R4':'Board fields389, opponent award3 separately392, removal animation388 and first clean emptyActive389 separated.','independent_recheck_required':True})
(P/'CORRECTION_LEDGER.md').write_text('# Independent corrections\n\nFrozen first-pass inputs retained in original_before_R1_R4. Root corrected native T6 fan counts, known-absence values, independent capture properties and terminal composite evidence. Astra and Sol agree on the buffered transition limit. No concealed card identities or buffered action order reconstructed. A narrow independent recheck is required.\n',encoding='utf-8')
views=read('ROOT_VIEWED_EVIDENCE.json');n='turn_evidence/t0389.00.jpg'
views['frames'].append({'path':n,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest(),'observation':'Clean first empty ownerActive before award: benchedMega170 Dark1/noTool; Houndstone60 Psychic2; rightMeloetta10/noEnergy; Plaza; points2-1.'})
save('ROOT_VIEWED_EVIDENCE.json',views)
result=subprocess.run([sys.executable,str(B/'validate_packet.py'),str(P)],capture_output=True,text=True,encoding='utf-8',check=True)
structure=json.loads(result.stdout);assert structure['structural_pass'];save('ROOT_REPAIR_STRUCTURE_CHECK.json',structure)
print('183108 R1-R4 corrected; independent recheck required')
