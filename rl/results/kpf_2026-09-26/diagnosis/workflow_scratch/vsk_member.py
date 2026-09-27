import json
F = {r["seed"]: r for r in json.load(open("vsk_feat.json"))}
for s in [72050043, 72050138, 72110059, 72050052, 72050130, 72110099, 72110228, 72050032, 72200113, 72200072, 72050064, 72160015,
          72250029, 72110021, 72110086, 72110157, 72050017, 72050051, 72160012]:
    r = F.get(s)
    if not r:
        print(s, "NOT IN VESPIQUEN SET")
        continue
    k, f = r["kp3"], r["kpf"]
    ka, fa = k["attach"] or {}, f["attach"] or {}
    print(f"{s} {r['kind']:6s} t{r['turn']} Z={k['zone']:11s} kp3 atk={k['attack']} att={ka.get('name')}@{ka.get('slot')}(E{ka.get('E_before')})->{ka.get('where_end')}:{k.get('holder_end')} endA={k['end_active']}"
          f" | kpf atk={f['attack']} att={fa.get('name')}@{fa.get('slot')}(E{fa.get('E_before')})->{fa.get('where_end')}:{f.get('holder_end')} endA={f['end_active']} ret={f['retreats']} xs={f['xspeed']}")
