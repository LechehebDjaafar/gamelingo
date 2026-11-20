#!/usr/bin/env python3
"""Validate every skills/*/SKILL.md: frontmatter, naming, size, and referenced files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
errors: list[str] = []


def err(skill: str, msg: str) -> None:
    errors.append(f"{skill}: {msg}")


def main() -> int:
    dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if not dirs:
        print("no skills found")
        return 1
    for d in dirs:
        md = d / "SKILL.md"
        if not md.exists():
            err(d.name, "missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            err(d.name, "missing YAML frontmatter")
            continue
        fm = dict(re.findall(r"^([a-z\-]+):\s*(.*)$", m.group(1), re.M))
        if fm.get("name") != d.name:
            err(d.name, f"frontmatter name {fm.get('name')!r} must equal folder name")
        desc = fm.get("description", "")
        if len(desc) < 40:
            err(d.name, "description too short to trigger reliably")
        if len(desc) > 1024:
            err(d.name, "description longer than 1024 characters")
        if text.count("\n") > 500:
            err(d.name, "SKILL.md is over 500 lines; move detail into references/")
        for ref in re.findall(r"`((?:\.\./gamelingo/|\./)?(?:scripts|references)/[\w./\-]+)`", text):
            base = d if not ref.startswith("../") else d
            target = (base / ref).resolve()
            alt = (SKILLS / "gamelingo" / ref.split("gamelingo/")[-1]).resolve() if "gamelingo/" in ref else None
            alt2 = (SKILLS / "gamelingo" / ref).resolve()
            if not (target.exists() or (alt and alt.exists()) or alt2.exists()):
                err(d.name, f"referenced file not found: {ref}")
    for e in errors:
        print("ERROR", e)
    print(f"checked {len(dirs)} skill(s): {'FAILED' if errors else 'all good'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
