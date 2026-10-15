"""Check the saved visible UI against accepted packets before issuing receipts."""
import re
from datetime import datetime, timezone
from setup_shark_batch_20261002 import BATCH, SELECTED, packet_for, read, save, DESTINATION

def entries(text, deck):
    return [re.split(r'\btext ',line,maxsplit=1)[1].strip() for line in text.splitlines()
            if re.search(r'\btext '+re.escape(deck)+r' 2026-',line)]

def main():
    snapshot=BATCH/'ARTIFACT_FINAL_LOG_RELOADED.txt'
    visible=snapshot.read_text(encoding='utf-8')
    before=(BATCH/'ARTIFACT_LOG_BEFORE.txt').read_text(encoding='utf-8')
    assert entries(visible,'Wailord / Indeedee wall')==entries(before,'Wailord / Indeedee wall'),'Old saved entries changed'
    games=entries(visible,'Draft A: Shark Tempo')
    assert len(games)==5 and len(entries(visible,'Wailord / Indeedee wall'))==5
    results=[]
    for name in SELECTED:
        p=packet_for(name);s=read(p/'SUMMARY.json');lead=read(p/'LEAD_ACCEPTANCE.json')
        assert lead['accepted'] and s['source_archived']
        assert visible.count(name)==1,name
        line=next(x for x in games if name in x)
        label='Win by concession' if s['outcome_type']=='win_by_concession' else s['outcome'].title()
        order='Went second' if 'second' in s['turn_order'] else 'Went first'
        assert line.startswith('Draft A: Shark Tempo 2026-10-02 '+label+' '+order+' '),line
        assert s['opponent_name'] in line and 'fun and competitive' in line and 'untested' in line
        assert 'numeric ratings not supplied' in line
        score=s['final_score'];assert f"{score['owner']}-{score['opponent']}" in line
        assert '\u2014' not in line
        if name=='20261002_132311000_iOS.MP4':assert 'timeout, not concession' in line
        receipt={'destination':DESTINATION,'artifact_title':'Pause Games','deck':'Draft A: Shark Tempo','source_video':name,'source_sha256':lead['source_sha256'],'match_date_local':'2026-10-02','result_label':label,'outcome':s['outcome'],'outcome_type':s['outcome_type'],'turn_order':order,'opponent':s['opponent_name'],'final_score':score,'owner_feedback':'Fun and competitive; could combine with Wailord or Soothing Shore','numeric_ratings':None,'proposals_tested':False,'verified_after_reload':True,'filename_occurrences_after_reload':1,'verification_snapshot':str(snapshot),'visible_saved_entry':line,'verified_at':datetime.now(timezone.utc).isoformat(),'ranked_ladder_eligible':False}
        save(p/'EXTERNAL_LOG_RECEIPT.json',receipt);results.append(s)
    totals={'games':5,'wins':sum(x['outcome']=='win' for x in results),'losses':sum(x['outcome']=='loss' for x in results),'concession_wins':sum(x['outcome_type']=='win_by_concession' for x in results),'timeout_wins':sum('timeout' in x.get('outcome_detail','').lower() for x in results)}
    assert totals=={'games':5,'wins':4,'losses':1,'concession_wins':1,'timeout_wins':1}
    save(BATCH/'EXTERNAL_BATCH_VERIFICATION.json',{'destination':DESTINATION,'totals':totals,'artifact_games_before':5,'artifact_games_after':10,'artifact_wins_after':6,'artifact_losses_after':4,'artifact_concessions_after':3,'old_entries_preserved':True,'filenames_once_each':True,'numeric_ratings':None,'verified_after_reload':True,'snapshot':str(snapshot),'verified_at':datetime.now(timezone.utc).isoformat()})
    print('All five saved UI entries match accepted packets; old entries preserved. '+str(totals))

if __name__=='__main__':main()
