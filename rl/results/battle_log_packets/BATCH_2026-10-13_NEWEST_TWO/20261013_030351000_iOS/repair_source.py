from pathlib import Path
p=Path(__file__).resolve().parent
f=p/'build_packet.py'
s=f.read_text(encoding='utf-8')
pairs=[
 ("('Poké Ball',59),('Dragonair',59.5)","('Poké Ball',59.5),('Dragonair',60.5)"),
 ('Research58.5, Poké Ball59, Dragonair59.5','Research58.5, Poké Ball59.5, Dragonair60.5'),
 ('row(3,117.5,158,117.5,118.5,153','row(3,117.5,158,117.5,119,153'),
 ("play(1,'card_play',118.5,'Bench drawn Dratini right'","play(1,'card_play',119,'Bench drawn Dratini right; movement visible at119, settled placement confirmed121'"),
 ("('Rare Candy',128.5),('Haxorus',129)],128.5","('Rare Candy',126),('Haxorus',127)],126"),
 ('chosen=117.5,first=118.5','chosen=117.5,first=119'),
 ('row(5,184.2,217,184.2,185,204','row(5,184.2,217,184.2,186,204'),
 ("play(1,'card_play',185,'Evolve right benched Dratini", "play(1,'card_play',186,'Evolve right benched Dratini"),
 ('chosen=184.2,first=185','chosen=184.2,first=186'),
 ('chosen=322,first=324,before=353,hand=True','chosen=322,first=324,before=353,hand=False'),
 ('row(11,412.5,434,412.5,414,431','row(11,412.5,434,412.5,414,430'),
 ('chosen=412.5,first=414,before=431','chosen=412.5,first=414,before=430'),
 ("play(5,'end_turn',431,'End Turn; Druddigon cannot pay Fire+Water+Colorless Dragon Claw with two Metal')", "play(5,'prompt_response',430,'Decline available Supporter and accept End Turn warning',prompt='End your turn? A Supporter card can be used',response='OK',count=1),play(6,'end_turn',431,'End Turn transition; Druddigon cannot pay Fire+Water+Colorless Dragon Claw with two Metal')"),
 ('row(16,583,614,None','row(16,583,616,None'),
 ("phase='Turn16 terminal after attack and Haxorus KO, before result overlay'", "phase='Turn16 terminal after attack and Haxorus KO; board geometry614, final third point616'"),
 ("unzoom=True if selected and z['hand'] else None", "unzoom=z['hand'] if selected else None"),
 ("if selected and not z['hand']:obs=", "if selected and n==9:obs='Two named cards Lucky Ice Pop and Iris identified across321-322; selected322 has Lucky Ice Pop inspection zoom.';limit='Selected preplay frame is zoomed, not a spread unzoomed hand; count2 uses named draw and retained Lucky Ice Pop, not deck inference.'\n   elif selected and not z['hand']:obs="),
 ("('Single card raised/zoomed before immediate evolution/play; fully spread unzoomed view unavailable' if not z['hand'] else None)", "('Lucky Ice Pop inspection zoom covers hand at322; names/count2 use321-322 face sequence' if n==9 else ('Single card raised/zoomed before immediate evolution/play; fully spread unzoomed view unavailable' if not z['hand'] else None))"),
 ('T5 and T7 immediate single-card handling','T9 selected preplay frame is a Lucky Ice Pop inspection zoom and is qualified accordingly. T5 and T7 immediate single-card handling'),
 ('Single-card raised views at T5/T7 do not prove an unzoomed spread hand.','T5/T7 single-card raised views and T9 inspection zoom do not prove an unzoomed spread hand.'),
 ('T15 has no draw because deck is empty.','T9 selected322 has Lucky Ice Pop inspection zoom and cannot be called unzoomed. T15 has no draw because deck is empty.'),
 ('T11 attaches Fighting to Haxorus,','T11 visibly accepts the End Turn warning at430 that a Supporter can be used, leaving Iris in hand. T11 attaches Fighting to Haxorus,'),
]
for a,b in pairs:
 if a not in s:print('REPLACEMENT MISSING',a)
 s=s.replace(a,b)
s=s.replace("row(16,583,616,None", "b16['evidence_ids']=refs(614,616)\nb16['source_seconds']=616\nb16['opponent']['points_evidence_ids']=refs(616)\nb16['opponent']['points_basis']='Third point overlay616; board geometry614 still shows pre-award score2'\nrow(16,583,616,None")
f.write_text(s,encoding='utf-8')
print('Source repaired')
