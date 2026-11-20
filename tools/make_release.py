#!/usr/bin/env python3
"""Build dist/gamelingo-<version>.zip containing the repository (without VCS/cache files)."""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
out = ROOT / "dist" / f"gamelingo-{version}.zip"
out.parent.mkdir(exist_ok=True)
SKIP = {".git", "__pycache__", "dist", ".venv"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP) and p.suffix != ".pyc":
            z.write(p, Path("gamelingo") / p.relative_to(ROOT))
print(out)
