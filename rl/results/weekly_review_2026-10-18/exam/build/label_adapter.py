"""Lossless converter between the legal-moves tool's labels (engine brace form) and the AI judge's target-preserving form.

engine: Name{field:value,...}   (Rust Debug-style, fields in struct order, e.g. DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0})
judge:  Name#{"field":value,...} (serde_json compact; keys sorted, as serde_json orders map keys without its preserve_order feature)
Plain labels (no braces, no '#') pass through unchanged. Compare labels with same_action(), which parses the arguments, so key order
can never decide a match. Never strip the arguments: they are the target (which Pokemon, which Tool)."""
import json, re
FIELD_ORDER = {'DiscardToolFromPokemon': ['player', 'in_play_idx', 'tool_idx'],
               'ChooseRandomEvolutionTarget': ['in_play_idx', 'energy_type']}
_ENG = re.compile(r'^([A-Za-z]+)\{(.*)\}$')

def _val(v):
    return int(v) if re.fullmatch(r'-?\d+', v) else v

def parse(label):
    """(name, args dict or None)"""
    if '#' in label:
        name, js = label.split('#', 1)
        return name, json.loads(js)
    m = _ENG.match(label)
    if m:
        args = {}
        for part in filter(None, m.group(2).split(',')):
            k, v = part.split(':', 1)
            args[k.strip()] = _val(v.strip())
        return m.group(1), args
    return label, None

def to_judge(label):
    name, args = parse(label)
    return label if args is None else name + '#' + json.dumps(args, sort_keys=True, separators=(',', ':'))

def to_engine(label):
    name, args = parse(label)
    if args is None:
        return label
    order = FIELD_ORDER.get(name, list(args))
    return name + '{' + ','.join(f'{k}:{args[k]}' for k in order) + '}'

def same_action(a, b):
    return parse(a) == parse(b)

if __name__ == '__main__':  # tiny fixture check
    for e in ['DiscardToolFromPokemon{player:1,in_play_idx:2,tool_idx:0}', 'ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}', 'Attach:1Grass@0 zone']:
        j = to_judge(e)
        assert to_engine(j) == e and same_action(e, j), (e, j)
        print(e, '<->', j)
    assert not same_action('ChooseRandomEvolutionTarget{in_play_idx:1,energy_type:Grass}', 'ChooseRandomEvolutionTarget{in_play_idx:0,energy_type:Grass}')
    print('adapter fixture OK')
