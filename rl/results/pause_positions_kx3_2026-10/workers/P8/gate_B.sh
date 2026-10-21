S='s=lambda r:{k:v for k,v in r.items() if k not in ("ms","time","elapsed","wall_s")}'
cmp_km3() { python3 -c "import json,sys; $S; a=[s(json.loads(l)) for l in open(sys.argv[1]) if l.strip()]; b=[s(json.loads(l)) for l in open(sys.argv[2]) if l.strip()]; print(sys.argv[3], 'EQUAL' if a==b else 'DIFFERENT')" "$@"; }
