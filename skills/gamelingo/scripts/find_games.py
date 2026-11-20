#!/usr/bin/env python3
"""List games installed through Steam and the Epic Games Launcher.

Usage:
    python find_games.py                     # table of every game found
    python find_games.py --name "hollow"     # filter by name (case-insensitive)
    python find_games.py --json              # machine-readable output
    python find_games.py --root D:\\Games    # also list sub-folders of a custom root (GOG, itch, ...)

Only reads launcher metadata. Never modifies anything.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import sys
from pathlib import Path


def steam_roots() -> list[Path]:
    system = platform.system()
    home = Path.home()
    candidates: list[Path] = []
    if system == "Windows":
        for env in ("PROGRAMFILES(X86)", "PROGRAMFILES"):
            base = os.environ.get(env)
            if base:
                candidates.append(Path(base) / "Steam")
    elif system == "Darwin":
        candidates.append(home / "Library/Application Support/Steam")
    else:
        candidates += [
            home / ".steam/steam",
            home / ".local/share/Steam",
            home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
        ]
    return [p for p in candidates if p.exists()]


def parse_vdf_values(text: str, key: str) -> list[str]:
    """Return every value of `"key" "value"` pairs (good enough for Steam's flat files)."""
    pattern = r'"%s"\s+"([^"]*)"' % re.escape(key)
    return [m.replace("\\\\", "\\") for m in re.findall(pattern, text, flags=re.IGNORECASE)]


def steam_libraries(root: Path) -> list[Path]:
    libs = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    if vdf.exists():
        text = vdf.read_text(encoding="utf-8", errors="replace")
        for p in parse_vdf_values(text, "path"):
            path = Path(p)
            if path.exists() and path not in libs:
                libs.append(path)
    return libs


def find_steam() -> list[dict]:
    games: list[dict] = []
    seen: set[str] = set()
    for root in steam_roots():
        for lib in steam_libraries(root):
            steamapps = lib / "steamapps"
            if not steamapps.exists():
                continue
            for manifest in steamapps.glob("appmanifest_*.acf"):
                text = manifest.read_text(encoding="utf-8", errors="replace")
                appid = (parse_vdf_values(text, "appid") or [""])[0]
                name = (parse_vdf_values(text, "name") or [""])[0]
                installdir = (parse_vdf_values(text, "installdir") or [""])[0]
                path = steamapps / "common" / installdir
                if not installdir or not path.exists() or appid in seen:
                    continue
                seen.add(appid)
                games.append({"launcher": "steam", "id": appid, "name": name, "path": str(path)})
    return games


def epic_manifest_dirs() -> list[Path]:
    dirs = []
    if platform.system() == "Windows":
        program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        dirs.append(Path(program_data) / "Epic" / "EpicGamesLauncher" / "Data" / "Manifests")
    return [d for d in dirs if d.exists()]


def find_epic() -> list[dict]:
    games: list[dict] = []
    for d in epic_manifest_dirs():
        for item in d.glob("*.item"):
            try:
                data = json.loads(item.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            location = data.get("InstallLocation")
            if location and Path(location).exists():
                games.append({
                    "launcher": "epic",
                    "id": data.get("AppName", ""),
                    "name": data.get("DisplayName", data.get("AppName", "")),
                    "path": location,
                })
    return games


def find_custom(roots: list[str]) -> list[dict]:
    games = []
    for r in roots:
        base = Path(r)
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir():
                games.append({"launcher": "manual", "id": "", "name": child.name, "path": str(child)})
    return games


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="case-insensitive name filter")
    ap.add_argument("--root", action="append", default=[], help="extra folder whose sub-folders are games")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    games = find_steam() + find_epic() + find_custom(args.root)
    if args.name:
        needle = args.name.lower()
        games = [g for g in games if needle in g["name"].lower()]
    games.sort(key=lambda g: g["name"].lower())

    if args.json:
        print(json.dumps(games, indent=2, ensure_ascii=False))
    elif not games:
        print("No games found. Use --root <folder> to point at a custom install location.", file=sys.stderr)
        return 1
    else:
        for g in games:
            print(f"[{g['launcher']:<6}] {g['name']}\n          {g['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
