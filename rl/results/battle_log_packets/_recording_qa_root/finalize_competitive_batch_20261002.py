"""Verify the usable five-game deliverable without reopening archived originals."""
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from intake_competitive_20261002 import ROOT, BATCH, read, save, packet_for, DESTINATION
from start_competitive_packet import SELECTED
from complete_competitive_packet import validate
from free_reviewed_video_space import metadata

def main():
    rows=list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
    by_name={r['Video']:r for r in rows}
    assert len(by_name)==len(rows)
    baseline=read(BATCH/'INDEX_BEFORE.json')
    assert all(by_name[r['Video']]==r for r in baseline), 'Unrelated baseline row changed'
    expected_added=set(SELECTED)|{'20261002_012229000_iOS.MP4'}
    assert set(by_name)-{r['Video'] for r in baseline}==expected_added
    events=[read(p) for p in (ROOT/'Review_Log'/'events').glob('*.json')]
    # Read the two legacy event schemas without rewriting their history.
    for event in events:
        event.setdefault('video_basename', event.get('video'))
        event.setdefault('logged_at_utc', event.get('timestamp_utc'))
    locations=read(ROOT/'MEDIA_LOCATIONS.json')['moved']
    results=[]
    for name in sorted(SELECTED):
        p,s,a,lead=validate(name)
        summary=read(p/'SUMMARY.json');receipt=read(p/f'MOVE_RECEIPT.{name}.json');external=read(p/'EXTERNAL_LOG_RECEIPT.json')
        current=ROOT/'Reviewed'/name
        assert current.is_file() and current.stat().st_size==s['bytes'] and not (ROOT/name).exists()
        assert receipt['identity_match'] and receipt['sha256_before']==receipt['sha256_after']==s['sha256']
        latest=max((e for e in events if e['video_basename']==name),key=lambda e:e['logged_at_utc'])
        assert latest['status']=='full_battle_review_complete' and latest['video_sha256']==s['sha256']
        assert by_name[name]['Status']=='Reviewed' and by_name[name]['Location'].replace('\\','/')=='Reviewed/'+name
        loc=[v for v in locations if v['filename']==name];assert len(loc)==1 and Path(loc[0]['current_path']).resolve()==current.resolve()
        assert external['verified_after_reload'] and external['destination']==DESTINATION and external['filename_occurrences_after_reload']==1
        assert summary['external_log_saved'] and summary['source_archived']
        result={'video':name,'source_sha256':s['sha256'],'source_bytes':s['bytes'],'duration_seconds':s['duration_seconds'],'outcome':summary['outcome'],'outcome_type':summary['outcome_type'],'opponent':summary['opponent_name'],'opponent_core':summary['opponent_deck_core'],'turn_order':summary['turn_order'],'final_score':summary['final_score'],'review':str((p/'REVIEW.md').relative_to(ROOT)).replace('\\','/'),'coverage':str((p/'COVERAGE.md').relative_to(ROOT)).replace('\\','/'),'decisive_evidence':summary['decisive_evidence'],'storage':metadata(current),'accepted':True,'registered':True,'archived_hash_verified':True,'external_verified':True}
        results.append(result)
    assert len(results)==5
    wins=sum(v['outcome']=='win' for v in results);losses=sum(v['outcome']=='loss' for v in results);concessions=sum(v['outcome_type']=='win_by_concession' for v in results)
    counts={'games':5,'wins':wins,'losses':losses,'concession_wins':concessions}
    assert read(BATCH/'EXTERNAL_BATCH_VERIFICATION.json')['totals']==counts
    statuses=Counter(r['Status'] for r in rows)
    reviewed_files=[p for p in (ROOT/'Reviewed').iterdir() if p.is_file() and p.suffix.lower()=='.mp4']
    assert len(reviewed_files)==statuses['Reviewed']
    for r in rows:
        loc=r['Location'].replace('\\','/')
        assert (ROOT/loc).is_file(),r['Video']
    rule_names={e['video_basename'] for e in events if e['status']=='rule_test_review_complete'}
    storage={'checked_at':datetime.now(timezone.utc).isoformat(),'videos':5,'online_only':sum(v['storage']['online_only'] for v in results),'allocated_bytes':sum(v['storage']['allocated_bytes'] for v in results),'entries':[{'video':v['video'],**v['storage']} for v in results],'files_deleted':0,'originals_modified':False}
    save(BATCH/'RESULTS.json',{'destination':DESTINATION,'artifact_title':'Pause Games','totals':counts,'date_local':'2026-10-01','numeric_ratings':None,'results':results})
    save(BATCH/'STORAGE_STATUS.json',storage)
    checks={'checked_at':datetime.now(timezone.utc).isoformat(),'baseline_rows_preserved':len(baseline),'indexed_videos':len(rows),'accepted_full_reviews':statuses['Reviewed']-len(rule_names),'completed_rule_tests':len(rule_names),'archived_videos':len(reviewed_files),'pending_indexed_videos':len(rows)-statuses['Reviewed'],'all_five_coverage_lead_event_hash_location_external_checks_passed':True,'root_unindexed_out_of_scope_video':'20261002_011527000_iOS.MP4','excluded_intake_only_video':'20261002_012229000_iOS.MP4','live_ranked_ladder_entries':0,'storage':storage}
    save(BATCH/'FINAL_CHECKS.json',checks)
    header=f'# Wailord competitive reviews, October 1, 2026\n\nAll five recordings are fully reviewed, independently accepted, registered and archived unchanged. Saved once each in [Pause Games]({DESTINATION}) and verified after reload: **{wins} wins, {losses} losses, {concessions} wins by concession**. Logged under the owner\'s Wailord / Indeedee wall with Water Energy. Each full review distinguishes visible cards from the configured hidden list. Competitive intent is owner testimony; the exact selected queue and hidden full lists remain unknown. These results are excluded from the ranked Ladder Log. Numeric ratings remain blank.\n\n'
    cores={'020315000':'Palkia ex / Baxcalibur / Milotic ex','020920000':'Charmander / Charmeleon / Entei ex','021402000':'Meloetta / Giratina ex / Mega Gardevoir ex / Mega Diancie ex','022135000':'Swablu / Mega Altaria ex / Greninja / Chingling','023418000':'Bonsly / Lucario / Mega Lucario ex / Hitmonchan'}
    first_attacks={'020315000':6,'020920000':8,'021402000':13,'022135000':7,'023418000':9}
    lines=['| Source | Result | Turn order | First attack, global turn | Opponent visible core | Full review |','|---|---|---|---|---|---|']
    for v in results:
        order='second' if 'second' in v['turn_order'] else 'first'
        score=v['final_score'];own=score.get('owner',score.get('owner_actual_points'));opp=score.get('opponent',score.get('opponent_actual_points'))
        label='Win by concession' if v['outcome_type']=='win_by_concession' else v['outcome'].title()
        key=v['video'].split('_')[1];core=cores[key]
        score_label='actual points at concession' if v['outcome_type']=='win_by_concession' else 'displayed points'
        lines.append(f"| {v['video']} | {label}, {own}-{opp} {score_label} | {order} | {first_attacks[key]} | {v['opponent']}: {core} | [Review]({v['review']}) |")
    findings='''

## What made it feel slow

Dustin reported: "How it felt was slow. Takes too long to build up energy." The reports distinguish the four-Energy requirement from rebuilding after a knockout, early evolution, forced switching and attachment choices. No acceleration was tested. Normal Wailord can use any Energy for its four-Colorless cost, but its bonus counts Water. Changing types alone does not reduce the number of attachments. Wailmer and Wailord ex require Water; Indeedee can heal without Energy but needs two Psychic to attack.

[Astra's Energy check](Recording_QA/BATCH_2026-10-02_COMPETITIVE/ASTRA_ENERGY_CHECK.md) confirms Misty is compatible with this core, with coin-dependent acceleration. Testing it first is a practical recommendation, not a measured improvement. Mega Sharpedo ex is another Water route: it attacks for one Water and adds Water to a Benched Water Pokémon, then can retreat free. It adds an evolution line and its knockout gives three points, so it needs a separate build and test. An alternate Energy route needs an actual acceleration engine to improve setup speed and can reduce normal Wailord's Water damage bonus. None of these is a validated fix or an implemented deck change.

## Bounded tactical findings

[Astra's retained-source checks](Recording_QA/BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md) accepted three narrow conclusions:

- In 020920, keeping Wailmer unevolved through turn 6 could enable Wave Splash for 80 into Charmeleon at 80 HP under the same visible continuation. The larger evolution HP buffer is traded for earlier damage, and later evolution must wait for another turn.
- In 021402, Indeedee can survive the observed 110 at 20 HP and retreat free under Peculiar Plaza before replacing that Stadium, permitting a turn 9 Wailord attack for 100. It would leave a vulnerable two-point Indeedee on the Bench. This is not a proven reversal of the loss.
- In 023418, Cyrus switches the opponent only. Bonsly's minus 30 remains on Wailord, so five-Water Whale Pump would deal 80 into Mega Lucario at 110 HP, leaving 30. The actual win is concession before attack; the opponent's reason is unknown.

In 022135, both Wailmer are lost; the remaining Indeedee heal but cannot attack with Water-only Energy. The terminal Indeedee ex knockout awards two points, while the final result panel has a maximum of three opponent point markers. Preserve that displayed 1-3 result without treating the ex knockout as a one-point event.

The earlier Garchomp/Froakie files 011527 and 012229 are outside this Wailord batch. Their source files remain in the main folder; 012229's initial assignment was explicitly corrected to intake-only in append-only history. Older pending excerpts remain pending.
'''
    storage_text=f'\n\n## Preservation and verification\n\nAll five before/after move hashes match. The {len(baseline)} baseline index rows were preserved exactly. Current inventory: {len(rows)} indexed, {statuses["Reviewed"]-len(rule_names)} full-battle reviews, {len(rule_names)} completed rule tests, {len(rows)-statuses["Reviewed"]} indexed pending items.\n\n{storage["online_only"]} of5 originals are confirmed online-only; local allocation is {storage["allocated_bytes"]/1e9:.2f}GB. OneDrive sync or local-space release remains pending for any locally allocated originals. No original was deleted. Review packets and evidence remain pinned locally. [Verification records](Recording_QA/BATCH_2026-10-02_COMPETITIVE/FINAL_CHECKS.json) and [saved-log proof](Recording_QA/BATCH_2026-10-02_COMPETITIVE/PAUSE_GAMES_5_VERIFIED.png) are retained.\n'
    storage_text=storage_text.replace(' of5 ', ' of 5 ').replace('GB.', ' GB.')
    (ROOT/'WAILORD_COMPETITIVE_2026-10-01.md').write_text(header+'\n'.join(lines)+findings+storage_text,encoding='utf-8')
    status_path=ROOT/'READ_ME_REVIEW_STATUS.md';text=status_path.read_text(encoding='utf-8-sig')
    first,rest=text.split('\n',1)
    update=f'\nUpdated after the October1 Wailord competitive batch. All five are fully reviewed, independently accepted, registered and archived with matching hashes, then saved once in Pause Games and verified after reload: {wins} wins and {losses} losses ({concessions} wins by concession). See [full reviews and Energy findings](WAILORD_COMPETITIVE_2026-10-01.md). {storage["online_only"]} of5 originals are online-only; remaining local data is pending OneDrive sync or space release. The two earlier Garchomp/Froakie uploads are outside this batch and retained as intake only.\n'
    update=update.replace('October1 ', 'October 1 ').replace(' of5 ', ' of 5 ')
    import re
    text=first+'\n'+update+rest
    text=re.sub(r'The \[review index\]\(BATTLE_REVIEW_INDEX.csv\) contains 116 videos: 101 accepted full-battle reviews and 8 completed rule tests in `Reviewed`, plus seven recording-limited excerpts in the main folder\.',f'The [review index](BATTLE_REVIEW_INDEX.csv) contains {len(rows)} videos: {statuses["Reviewed"]-len(rule_names)} accepted full-battle reviews and {len(rule_names)} completed rule tests in `Reviewed`, plus seven older recording-limited excerpts and one out-of-scope Garchomp intake in the main folder. A second out-of-scope Garchomp source remains unindexed.',text)
    status_path.write_text(text,encoding='utf-8')
    print(counts,checks['indexed_videos'],storage['online_only'])

if __name__=='__main__':main()
