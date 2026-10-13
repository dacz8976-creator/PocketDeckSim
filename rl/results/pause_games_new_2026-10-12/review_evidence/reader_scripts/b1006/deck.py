import json, sys
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
g = sys.argv[1]
d = json.load(open(B + g + '/DECK_USED.json', encoding='utf-8'))


def walk(o, path='', depth=0):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)):
                print('  ' * depth + f'{k}:')
                walk(v, path + '.' + k, depth + 1)
            else:
                print('  ' * depth + f'{k}: {str(v)[:220]}')
    elif isinstance(o, list):
        if all(isinstance(x, dict) and 'name' in x for x in o):
            for x in o:
                print('  ' * depth + '- ' + json.dumps({k: v for k, v in x.items() if k in ('name', 'variant', 'count', 'position', 'entity', 'entity_id', 'set', 'number', 'printing', 'card_id', 'id')}, ensure_ascii=False))
        else:
            for x in o:
                if isinstance(x, (dict, list)):
                    walk(x, path, depth + 1)
                else:
                    print('  ' * depth + '- ' + str(x)[:220])


walk(d)
