from pathlib import Path
import hashlib,json
P=Path(__file__).parent
M=P/'REVIEW_PACKET_HASHES.json'
files={str(f.relative_to(P)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(P.rglob('*')) if f.is_file() and f!=M}
M.write_text(json.dumps({'schema':'review_packet_hashes_v1','source_filename':'20261015_020931000_iOS.MP4','source_sha256':'a8e539e31976ed5591bba0a2cfba3db3a44168b61191e259b5cd55bf05e37060','reviewer':'/root/night_020931','freeze_rule':'No first-pass edits after manifest; corrections require a separate addendum.','files':files},indent=2)+'\n',encoding='utf-8')
loaded=json.loads(M.read_text(encoding='utf-8'))
bad=[name for name,h in loaded['files'].items() if hashlib.sha256((P/name).read_bytes()).hexdigest()!=h]
assert not bad,bad
assert len(list((P/'evidence').glob('*.jpg')))==91
print(json.dumps({'files_verified':len(files),'native_frames':91,'manifest_sha256':hashlib.sha256(M.read_bytes()).hexdigest(),'verification':'passed','frozen':True}))
