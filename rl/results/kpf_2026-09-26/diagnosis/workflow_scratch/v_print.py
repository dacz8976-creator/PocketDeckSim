import json, sys
rows = json.load(open("v_rows.json"))
kind = sys.argv[1]
flt = sys.argv[2] if len(sys.argv) > 2 else None
for r in rows:
    if r["kind"] != kind:
        continue
    if flt and not eval(flt, {}, {"r": r}):
        continue
    print(f"--- {r['seed']} t{r['turn']} v {r['opp']} (i={r['i']}, change {r['change']:+.1f})  first: {r['kp3']} -> {r['kpf']}")
    print(f"   own: {r['own']}")
    print(f"   opp: {r['opp_board']}")
    print(f"   kp3: {' ; '.join(r['seq_b'])}   | zone {r['b_zone']} atk {r['b_attack']} ret {r['b_retreat']}")
    print(f"   kpf: {' ; '.join(r['seq_f'])}   | zone {r['f_zone']} atk {r['f_attack']} ret {r['f_retreat']}")
    print(f"   end kp3: {r['b_end']}")
    print(f"   end kpf: {r['f_end']}")
