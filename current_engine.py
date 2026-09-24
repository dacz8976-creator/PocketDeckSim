#!/usr/bin/env python3
"""Resolve the one manifest-authorized engine; reject a different binary override."""
import hashlib
import json
import os
import sys
from pathlib import Path


def resolve(project=None, override=None):
    root = Path(project) if project is not None else Path(__file__).resolve().parent
    release = json.loads((root / "project_manifest.json").read_text())["available_release"]
    canonical = (root / release["artifact"]).resolve(strict=True)
    chosen = Path(override).expanduser().resolve(strict=True) if override else canonical
    expected = release["sha256"]
    for path in {canonical, chosen}:
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError(f"engine is not executable: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"engine differs from available_release: {path}")
    return canonical


if __name__ == "__main__":
    try:
        print(resolve(override=sys.argv[1] if len(sys.argv) > 1 else None))
    except (OSError, ValueError, KeyError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
