"""Verify the five-game deliverable without reopening archived originals."""
import csv
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from setup_shark_batch_20261002 import ROOT,BATCH,SELECTED,packet_for,read,save,DESTINATION
from complete_shark_packet_20261002 import completion
from free_reviewed_video_space import metadata

def main():
    rows=list(csv.DictReader((ROOT/'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig',newline='')))
    by_name={r['Video']:r for r in rows};assert len(by_name)==len(rows)
    baseline=read(BATCH/'INDEX_BEFORE.json')
    assert all(by_name[r['Video']]==r for r in baseline),'Unrelated baseline row changed'
    assert set(by_name)-{r['Video'] for r in baseline}==set(SELECTED)
    events=[read(p) for p in (ROOT/'Review_Log'/'events').glob('*.json')]
    for event in events:
        event.setdefault('video_basename',event.get('video'));event.setdefault('logged_at_utc',event.get('timestamp_utc'))
    locations=read(ROOT/'MEDIA_LOCATIONS.json')['moved'];results=[]
    for name in SELECTED:
        p,s,a,lead=completion.validate(name)
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
        assert all((p/'worker_submission'/f).is_file() for f in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json'])
        assert not list(p.rglob('*.MP4'))
        result={'video':name,'source_sha256':s['sha256'],'source_bytes':s['bytes'],'duration_seconds':s['duration_seconds'],'outcome':summary['outcome'],'outcome_type':summary['outcome_type'],'outcome_detail':summary.get('outcome_detail',''),'opponent':summary['opponent_name'],'opponent_core':summary['opponent_deck_core'],'turn_order':summary['turn_order'],'final_score':summary['final_score'],'review':str((p/'REVIEW.md').relative_to(ROOT)).replace('\\','/'),'coverage':str((p/'COVERAGE.md').relative_to(ROOT)).replace('\\','/'),'decisive_evidence':summary['decisive_evidence'],'storage':metadata(current),'accepted':True,'registered':True,'archived_hash_verified':True,'external_verified':True}
        results.append(result)
    totals=read(BATCH/'EXTERNAL_BATCH_VERIFICATION.json')['totals']
    assert totals['games']==5 and totals['wins']==sum(v['outcome']=='win' for v in results) and totals['losses']==sum(v['outcome']=='loss' for v in results)
    statuses=Counter(r['Status'] for r in rows)
    archived=[p for p in (ROOT/'Reviewed').iterdir() if p.is_file() and p.suffix.lower()=='.mp4']
    assert len(archived)==statuses['Reviewed']
    for row in rows:assert (ROOT/row['Location'].replace('\\','/')).is_file(),row['Video']
    rule_names={e['video_basename'] for e in events if e['status']=='rule_test_review_complete'}
    storage={'checked_at':datetime.now(timezone.utc).isoformat(),'videos':5,'online_only':sum(v['storage']['online_only'] for v in results),'allocated_bytes':sum(v['storage']['allocated_bytes'] for v in results),'entries':[{'video':v['video'],**v['storage']} for v in results],'files_deleted':0,'originals_modified':False}
    save(BATCH/'RESULTS.json',{'destination':DESTINATION,'deck':'Draft A: Shark Tempo','totals':totals,'date_local':'2026-10-02','numeric_ratings':None,'results':results})
    save(BATCH/'STORAGE_STATUS.json',storage)
    checks={'checked_at':datetime.now(timezone.utc).isoformat(),'baseline_rows_preserved':len(baseline),'indexed_videos':len(rows),'accepted_full_reviews':statuses['Reviewed']-len(rule_names),'completed_rule_tests':len(rule_names),'archived_videos':len(archived),'pending_indexed_videos':len(rows)-statuses['Reviewed'],'all_five_coverage_lead_event_hash_location_external_checks_passed':True,'raw_first_passes_preserved':True,'live_ranked_ladder_entries':0,'external_artifact_entries':5,'old_external_entries_preserved':True,'numeric_ratings':None,'deck_changes_implemented':False,'simulator_changes':False,'training':False,'storage':storage}
    save(BATCH/'FINAL_CHECKS.json',checks)
    head=f'''# Shark Tempo competitive reviews, October 2, 2026

All five recordings are fully reviewed, independently accepted, registered and archived unchanged. Saved once each in [Pause Games]({DESTINATION}), under **Draft A: Shark Tempo**, and verified after reload: **four wins and one loss**. The wins include one opponent-return timeout and one concession. Actual earned scores are retained. These are owner-designated competitive games while ranked is paused; the exact selected queue is not visible. No ranked Ladder Log entries were added. Numeric ratings remain blank.

Dustin's review: **"It was fun and competitive. Could maybe combine with Wailord or the Soothing Shore Stadium."** This is owner testimony. Both combinations remain untested proposals.

| Source | Result and actual points | Order | Opponent visible core | Full review |
|---|---|---|---|---|
'''
    cores=['Chingling / Aerodactyl / Chandelure','Snorlax x2 / Rampardos x2 / Rowlet','Shaymin / Furfrou / Flygon ex','Sigilyph / Gardevoir x2 / Mewtwo ex','Teal Mask Ogerpon ex / Meowscarada ex']
    lines=[]
    for v,core in zip(results,cores):
        label='Win by concession' if v['outcome_type']=='win_by_concession' else 'Win by return timeout' if 'timeout' in v['outcome_detail'].lower() else v['outcome'].title()
        score=v['final_score'];order='second' if 'second' in v['turn_order'] else 'first'
        lines.append(f"| {v['video']} | {label}, {score['owner']}-{score['opponent']} | {order} | {v['opponent']}: {core} | [Review]({v['review']}) |")
    findings='''

## What the games support

Ninetales is central to the current plan. It supplies the late attacks in every game, all evolved attacks in the 3-0 Mewtwo win, and the winning attack in the 3-2 Aerodactyl game. Mega Sharpedo attacks and accelerates Bench Water in three of the five games; its free retreat enables switches while preserving Energy. It never attacks in the Mewtwo win and is never played in the Aerodactyl win. Those two games should not be treated as evidence of Turbo Shark's effectiveness.

The Flygon game shows the clearest Shark-to-Ninetales sequence: three Turbo Shark attacks add three Bench Water, then Ninetales takes Shaymin's point and keeps Flygon on one Fighting. Flygon is still alive at 20 HP when the opponent-return timeout ends the match. The Meowscarada game combines Misty-powered Lapras, one Turbo Shark attachment and a free switch into Ninetales before the opponent concedes. The Rampardos loss shows the limitation of Active Energy denial: the opponent's second Fossil already had Fighting and retained it through Rare Candy. These five games are a small sample, including two early endings, and do not establish a general win rate.

## Next test proposal

[Astra's card-text check](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/ASTRA_OPTIONS.md) supports trying **one Soothing Shore in place of the existing one Lucky Ice Pop**, keeping the other 19 cards and Water Energy. Shore heals 20 at the end of each player's own turn for each of that player's Pokemon with Water attached, including the Bench. It can sustain an attacker that takes several turns of damage, but also helps an opponent with Water attached. Compare whether it buys another attack or survival turn and whether opposing healing changes a knockout threshold. This swap is proposed, not applied or performance-validated. Lucky Ice Pop provided useful burst healing in the reviewed games, so the substitution has a real tradeoff.

Wailord is a larger, separate experiment. Normal Wailord has a four-Colorless attack and gets bonus damage per Water; Mega Sharpedo can add Water to a Benched Water Pokemon. The pairing is compatible, but requires Wailmer plus Wailord and still must build four Energy. Adding a full 2-2 Wailord line by replacing 2-2 Vulpix/Ninetales would remove the lock and finisher that mattered in these games. Keep the current Ninetales lineup as the comparison baseline before testing that rebuild. A one-card Lapras cut alone cannot accommodate the Wailmer/Wailord line.

## Bounded checks with Astra

- [Aerodactyl game, turn 8](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/ASTRA_T8_CHECK.md): retreating the 50-HP Ninetales into the four-Water Lapras could avoid the immediate two-point KO against the observed Heat Blast continuation. It spends two retreat Energy, drops Binding Snow and leaves a damaged, unpowered ex on Bench. Hidden responses prevent claiming a forced win or definite error.
- [Rampardos game, turn 13](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/ASTRA_RAMPARDOS_CHECK.md): a single-point Vulpix turn could extend the game. Rampardos was already below its conditional 50 self-damage threshold at 30 HP. A direct Vulpix KO would likely give one point each, bringing the score to 2-2; precise unobserved simultaneous point timing remains qualified. The second charged Fossil and hidden switches remain threats.
- [Mewtwo game](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/ASTRA_NINETALES_CHECK.md): Binding Snow's restriction includes Psy Shadow because it also attaches from the Energy Zone to the Active. Bench attachments remain legal. No attempted and rejected ability activation or opponent motive was observed.
- [Meowscarada game](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/ASTRA_FLOWER_TRICK_CHECK.md): Flower Trick schedules 70 damage to the Pokemon in the chosen spot at the end of the opponent's next turn. Lapras's damage after Surf is the delayed effect, not recoil or an Ability. The attack targets a spot rather than permanently following one Pokemon.
'''
    if storage['online_only']==5:
        storage_sentence='All five originals are confirmed online-only. Review packets and evidence remain pinned locally.'
    else:
        storage_sentence=f"{storage['online_only']} of 5 originals are confirmed online-only; {storage['allocated_bytes']/1e9:.2f} GB remains locally allocated while OneDrive sync or space release is pending. Review packets and evidence remain pinned locally."
    tail=f'''\n\n## Preservation and verification

All five before/after move hashes match. The {len(baseline)} baseline index rows are preserved exactly. Inventory when this batch completed: {len(rows)} indexed videos, {checks['accepted_full_reviews']} accepted full-battle reviews, {len(rule_names)} completed rule tests and {checks['pending_indexed_videos']} indexed pending items. The older pending backlog remains paused. Original filenames and bytes are preserved; no original was deleted.

{storage_sentence}

[Verification records](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/FINAL_CHECKS.json) and [saved-log proof](Recording_QA/BATCH_2026-10-02_SHARK_TEMPO/PAUSE_GAMES_SHARK_VERIFIED.png) are retained. Raw worker reports are kept in each packet's worker_submission folder alongside the accepted current report.
'''
    report=head+'\n'.join(lines)+findings+tail;assert '\u2014' not in report
    for ref in re.findall(r'\]\(([^)]+)\)',report):
        if not ref.startswith('https:'):assert (ROOT/ref).is_file(),ref
    (ROOT/'SHARK_TEMPO_COMPETITIVE_2026-10-02.md').write_text(report,encoding='utf-8')
    status_path=ROOT/'READ_ME_REVIEW_STATUS.md';text=status_path.read_text(encoding='utf-8-sig')
    if 'Updated after the October 2 Shark Tempo' not in text:
        title,rest=text.split('\n',1)
        update=f"\nUpdated after the October 2 Shark Tempo competitive batch. All five are fully reviewed, independently accepted, registered and archived with matching hashes, then saved once in Pause Games and verified after reload: four wins and one loss, including one opponent-return timeout and one concession. Owner feedback: fun and competitive. Wailord and Soothing Shore are untested proposals. See [full reviews and next-test findings](SHARK_TEMPO_COMPETITIVE_2026-10-02.md). {storage_sentence}\n"
        text=title+'\n'+update+rest
    text=re.sub(r'contains 122 videos: 106 accepted full-battle reviews and 8 completed rule tests',f"contains {len(rows)} videos: {checks['accepted_full_reviews']} accepted full-battle reviews and {len(rule_names)} completed rule tests",text)
    status_path.write_text(text,encoding='utf-8')
    for p in [BATCH,*[packet_for(n) for n in SELECTED]]:subprocess.run(['attrib','+P','-U',str(p/'*'),'/S','/D'],check=True,capture_output=True,text=True)
    print(str(totals)+'; '+str(len(rows))+' indexed; '+str(storage['online_only'])+' originals online-only')

if __name__=='__main__':main()
