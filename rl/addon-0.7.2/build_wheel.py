"""Package an already verified Linux extension without claiming manylinux compatibility."""
from pathlib import Path
import argparse
import base64
import csv
import hashlib
import io
import zipfile

p = argparse.ArgumentParser()
p.add_argument("--module", type=Path, required=True)
p.add_argument("--version", choices=("0.7.2",), required=True)
p.add_argument("--output-dir", type=Path, required=True)
p.add_argument("--expect-sha256", required=True)
args = p.parse_args()

module = args.module.read_bytes()
actual = hashlib.sha256(module).hexdigest()
if actual != args.expect_sha256:
    raise SystemExit(f"Module SHA-256 mismatch: {actual}")
tag = "cp38-abi3-linux_x86_64"
dist = f"pdl_rl_env-{args.version}.dist-info"
filename = f"pdl_rl_env-{args.version}-{tag}.whl"
entries = {
    "pdl_rl_env.abi3.so": module,
    f"{dist}/METADATA": (
        f"Metadata-Version: 2.1\nName: pdl_rl_env\nVersion: {args.version}\nRequires-Python: >=3.8\n"
    ).encode(),
    f"{dist}/WHEEL": (
        f"Wheel-Version: 1.0\nGenerator: pdl-rules3-offline-package\nRoot-Is-Purelib: false\nTag: {tag}\n"
    ).encode(),
}
buf = io.StringIO()
record = csv.writer(buf, lineterminator="\n")
for name, data in entries.items():
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
    record.writerow((name, "sha256=" + digest, len(data)))
record.writerow((f"{dist}/RECORD", "", ""))
entries[f"{dist}/RECORD"] = buf.getvalue().encode()
args.output_dir.mkdir(parents=True, exist_ok=True)
output = args.output_dir / filename
with zipfile.ZipFile(output, "w") as archive:
    for name, data in entries.items():
        info = zipfile.ZipInfo(name, date_time=(2026, 9, 22, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, data)
print(output)
