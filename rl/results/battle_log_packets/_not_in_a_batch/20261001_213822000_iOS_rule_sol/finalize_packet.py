from pathlib import Path
import json
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_213822000_iOS_rule_sol')
for name in ['REVIEW.md','COVERAGE.md','write_packet.py']:
 f=p/name;t=f.read_text(encoding='utf-8-sig').replace('Seafaring Shore','Soothing Shore').replace('Opponent draws; no new attachment is visible.','Opponent draws and attaches one Fire to benched Quilava.').replace('native/t0000.00.jpg; overview3/sheet_01.jpg','native/t0000.00.jpg; t0001.50.jpg; t0004.00.jpg; overview3/sheet_01.jpg').replace('t0206.00.jpg; t0209.00.jpg','t0206.00.jpg; t0208.00.jpg; t0209.00.jpg')
 f.write_text(t,encoding='utf-8')
f=p/'COVERAGE.md';t=f.read_text(encoding='utf-8').replace('| 0, 15, 17;', '| 0, 1.50, 4, 15, 17;').replace('Inferno lethal110, effect flip tails','Fire to benched Quilava, Inferno lethal 110, effect flip tails').replace('203 removal, 206 opponent1','203 removal, 206 opponent 1, 208 settled empty board');f.write_text(t,encoding='utf-8')
f=p/'SUMMARY.json';d=json.loads(f.read_text());d['key_findings'][1]='Turbo Shark deals 90 including weakness, knocks out 80-HP Ogerpon and increases benched Gyarados Water from 2 to 3 while Sharpedo retains 1 Water.';d['key_findings'][2]='Wild Swing discards Mega Sharpedo ex and Mega Gyarados ex, deals 100 after Carefree Steps tails, and awards no opponent points for the discards.';d['key_findings'][3]='Wild Swing can attack with empty Bench: 20 base plus 20 weakness equals 40.';d['key_findings'][4]='Empty-board defeat occurs at opponent 1 point versus owner 2; results damage 230 includes overkill.';d['independent_check_times'][0]['times']=[0,1.5,4,15,17];d['independent_check_times'][-1]['times']=[191,194,197,201.5,203,206,208,209,215,217];f.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
for name in ['SUMMARY.json','UNCERTAINTIES.json']:json.loads((p/name).read_text())
for name in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
 t=(p/name).read_text();assert '\u2014' not in t;print(name, len(t),'characters')
