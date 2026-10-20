"""Byte-exact text patches that keep each file's line endings. A patch = (file, old, new). old/new are written with \\n; the
patch uses CRLF if old occurs in the file in CRLF form, else LF. old must occur exactly once. Usage: bpatch.py ROOT SPEC.py
where SPEC.py defines PATCHES = [(relpath, old, new), ...]."""
import runpy, sys

root, spec = sys.argv[1], sys.argv[2]
patches = runpy.run_path(spec)['PATCHES']
for rel, old, new in patches:
    p = f'{root}/{rel}'
    data = open(p, 'rb').read()
    crlf = old.replace('\n', '\r\n').encode('utf-8')
    lf = old.encode('utf-8')
    n_crlf, n_lf = data.count(crlf), data.count(lf)
    if '\n' in old and n_crlf == 1:
        o, nw = crlf, new.replace('\n', '\r\n').encode('utf-8')
    elif n_lf == 1 and (n_crlf == 0 or '\n' not in old):
        o, nw = lf, new.encode('utf-8')
    else:
        sys.exit(f'{rel}: old text found {n_crlf} times (CRLF) / {n_lf} times (LF); need exactly one')
    before_cr = data.count(b'\r')
    data = data.replace(o, nw, 1)
    open(p, 'wb').write(data)
    print(f'{rel}: patched ({"CRLF" if o is crlf else "LF"}), CR count {before_cr} -> {data.count(b"\r")}')
