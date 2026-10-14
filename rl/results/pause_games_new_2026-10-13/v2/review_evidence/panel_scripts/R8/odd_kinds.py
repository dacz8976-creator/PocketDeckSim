import json, os
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
ODD = {'attack_attempt', 'no_effect', 'opponent_concession', 'stadium_activation', 'menu_open', 'concession', 'concede', 'system_turn_timeout', 'replacement_choice', 'promotion', 'prompt_response', 'tool', 'stadium', 'stadium_ability', 'stadium_effect', 'bench', 'item', 'supporter', 'tool_attachment', 'ability'}
for g in games:
    nm = os.path.basename(g)[2:15]
    led = json.load(open(os.path.join(R8, 'norm', os.path.basename(g), 'TURN_LEDGER.json'), encoding='utf-8'))
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for i, p in enumerate(t.get('plays_in_order') or []):
            if str(p.get('kind')) in ODD:
                print(f"{nm} t{t['turn_number']} [{i}] {p.get('kind')} card={p.get('card_name')!r} target={str(p.get('target'))[:60]!r} result={str(p.get('result'))[:150]!r} resp={str(p.get('response'))[:60]!r}")
