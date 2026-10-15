from pathlib import Path
p=Path(__file__).parent
q=p/'write_packet.py'
t=q.read_text()
t=t.replace('Chimchar','Victini')
t=t.replace('The in-battle opponent label is simply Opponent.','The introduction explicitly labels the opponent AI at 2 s (setup/t0002.00.jpg); the in-battle opponent label is Opponent.')
t=t.replace('A star rule popup at81-83 s says Fire-Pokemon attack coin flips may be restarted. This is a visible battle modifier; no such attack-coin reroll occurs in this game.','Victini\'s Victory Star ability produces a popup at81-83 s saying Fire-Pokemon attack coin flips may be restarted. No such attack-coin reroll occurs in this game.')
a=t.index('Rainbow Cave is used at168-170 s, replacing generated Fighting with Water.')
b=t.index('\n\nGarchomp\'s action menu',a)
t=t[:a]+'''Rainbow Cave is used at168-170 s. The resulting current generated Energy is still Fighting, with Water shown as the next Energy preview (dense/t0173.00.jpg). That Fighting attaches to the left Bench Froakie at174 s. The Cave refresh does not give the current attachment a Water identity.'''+t[b:]
t=t.replace('hidden search result and the cave/attachment ordering detail','hidden search result')
t=t.replace('Coin/deal graphics do not establish more hidden information.','The 5 s screen explicitly says Going first. Coin/deal graphics do not establish more hidden information.')
t=t.replace('Turn 2, opponent, 41-60 s','Turn 2, opponent, 41-59 s').replace('Turn 3, owner, 60-77 s','Turn 3, owner, 59-77 s')
q.write_text(t,encoding='utf-8')
