#!/usr/bin/env python3
"""Detect which game engine a game folder uses and where its text probably lives.

Usage:
    python detect_engine.py <game_dir> [--json]

Output: engine candidates with evidence, plus likely localization/text files.
Read-only. Walks at most MAX_FILES files and MAX_DEPTH directory levels.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_FILES = 40000
MAX_DEPTH = 6

TEXT_NAME = re.compile(r"(local|lang|string|text|dialog|subtitle|translation|i18n|l10n|locale|msg|message)", re.I)
TEXT_EXT = {".json", ".csv", ".po", ".pot", ".locres", ".strings", ".dlstrings", ".ilstrings", ".properties",
            ".xml", ".txt", ".tsv", ".yaml", ".yml", ".ini", ".translation", ".rpy", ".lang", ".loc", ".resx"}
LANG_HINT = re.compile(r"(?:^|[_\-.\s/])(en|english|fr|french|de|german|es|spanish|ja|japanese|zh|chinese|ru|russian|"
                       r"pt|portuguese|it|italian|ko|korean|ar|arabic|tr|turkish|pl|polish)(?:[_\-.\s/]|$)", re.I)

DOC_BY_ENGINE = {
    "Unity": "engines/unity.md",
    "Unreal Engine": "engines/unreal.md",
    "Godot": "engines/godot.md",
    "RPG Maker MV/MZ": "engines/rpgmaker.md",
    "RPG Maker (RGSS)": "engines/rpgmaker.md",
    "Ren'Py": "engines/renpy.md",
    "GameMaker": "engines/gamemaker.md",
    "Electron / NW.js": "engines/electron-nwjs.md",
}


def walk(root: Path):
    count = 0
    stack = [(root, 0)]
    while stack:
        current, depth = stack.pop()
        try:
            entries = list(current.iterdir())
        except OSError:
            continue
        for e in entries:
            count += 1
            if count > MAX_FILES:
                return
            yield e
            if e.is_dir() and depth < MAX_DEPTH:
                stack.append((e, depth + 1))


def detect(root: Path) -> dict:
    files = list(walk(root))
    names = {p.name.lower() for p in files}
    rel = [p.relative_to(root).as_posix().lower() for p in files]
    exts: dict[str, int] = {}
    for p in files:
        if p.is_file():
            exts[p.suffix.lower()] = exts.get(p.suffix.lower(), 0) + 1

    def has_name(*n):
        return any(x.lower() in names for x in n)

    def has_rel(suffix):
        return any(r.endswith(suffix) for r in rel)

    def has_dir(name):
        return any(p.is_dir() and p.name.lower() == name.lower() for p in files)

    found: list[dict] = []

    def add(engine, confidence, evidence, variant=""):
        found.append({"engine": engine, "variant": variant, "confidence": confidence, "evidence": evidence,
                      "reference": DOC_BY_ENGINE.get(engine, "")})

    # Unity
    unity_ev = []
    if has_name("UnityPlayer.dll", "UnityPlayer.so", "UnityPlayer.dylib"):
        unity_ev.append("UnityPlayer runtime")
    if any(p.is_dir() and p.name.endswith("_Data") for p in files) and has_name("globalgamemanagers", "data.unity3d"):
        unity_ev.append("*_Data folder with globalgamemanagers / data.unity3d")
    if unity_ev:
        variant = "IL2CPP" if has_name("GameAssembly.dll", "GameAssembly.so", "global-metadata.dat") else (
            "Mono" if has_name("Assembly-CSharp.dll") else "")
        if has_rel("streamingassets/aa/settings.json") or has_dir("aa"):
            unity_ev.append("Addressables (StreamingAssets/aa)")
        add("Unity", "high" if len(unity_ev) > 1 else "medium", unity_ev, variant)

    # Unreal
    ue_ev = []
    if exts.get(".pak"):
        ue_ev.append(f"{exts['.pak']} .pak archive(s)")
    if exts.get(".utoc") and exts.get(".ucas"):
        ue_ev.append("IoStore containers (.utoc/.ucas)")
    if has_dir("Engine") and has_dir("Content"):
        ue_ev.append("Engine/ and Content/ folders")
    if any(n.endswith("-win64-shipping.exe") or n.endswith("-shipping.exe") for n in names):
        ue_ev.append("*-Shipping.exe")
    if exts.get(".locres"):
        ue_ev.append(f"{exts['.locres']} .locres localization file(s)")
    if len(ue_ev) >= 2 or (ue_ev and exts.get(".locres")):
        add("Unreal Engine", "high" if len(ue_ev) >= 3 else "medium", ue_ev)

    # Godot
    godot_ev = []
    if exts.get(".pck"):
        godot_ev.append(".pck package")
    if has_name("project.godot"):
        godot_ev.append("project.godot (unpacked project)")
    if exts.get(".translation"):
        godot_ev.append(".translation resources")
    if godot_ev:
        add("Godot", "high" if has_name("project.godot") else "medium", godot_ev)

    # RPG Maker
    if has_rel("js/rmmz_core.js"):
        add("RPG Maker MV/MZ", "high", ["js/rmmz_core.js"], "MZ")
    elif has_rel("js/rpg_core.js"):
        add("RPG Maker MV/MZ", "high", ["js/rpg_core.js"], "MV")
    elif has_name("System.json") and has_dir("data") and has_name("package.json"):
        add("RPG Maker MV/MZ", "medium", ["data/System.json + package.json"])
    if exts.get(".rgss3a") or exts.get(".rvdata2") or exts.get(".rxdata") or exts.get(".rvdata"):
        add("RPG Maker (RGSS)", "high", ["RGSS archives / rvdata / rxdata files"])

    # Ren'Py
    if has_dir("renpy") and has_dir("game"):
        ev = ["renpy/ and game/ folders"]
        if exts.get(".rpa"):
            ev.append(".rpa archives")
        if exts.get(".rpyc") or exts.get(".rpy"):
            ev.append(".rpy/.rpyc scripts")
        add("Ren'Py", "high", ev)

    # GameMaker
    if has_name("data.win", "game.unx", "game.ios", "game.droid"):
        add("GameMaker", "high", ["data.win / game.unx"])

    # Electron / NW.js
    if has_rel("resources/app.asar"):
        add("Electron / NW.js", "high", ["resources/app.asar"], "Electron")
    elif has_name("package.nw", "nw.pak"):
        add("Electron / NW.js", "high", ["package.nw / nw.pak"], "NW.js")

    # Misc
    if exts.get(".vpk"):
        found.append({"engine": "Source engine (VPK)", "variant": "", "confidence": "medium",
                      "evidence": [".vpk archives"], "reference": ""})
    if exts.get(".ba2") or exts.get(".esm") or exts.get(".esp"):
        found.append({"engine": "Bethesda Creation Engine", "variant": "", "confidence": "medium",
                      "evidence": [".ba2/.esm/.esp files; text lives in Strings/*.strings"], "reference": ""})
    if has_name("data.wolf"):
        found.append({"engine": "Wolf RPG Editor", "variant": "", "confidence": "high",
                      "evidence": ["Data.wolf"], "reference": ""})
    if exts.get(".love"):
        found.append({"engine": "LÖVE", "variant": "", "confidence": "medium",
                      "evidence": [".love archive (zip)"], "reference": ""})

    # Likely text sources
    candidates = []
    existing_langs = set()
    for p in files:
        if not p.is_file():
            continue
        r = p.relative_to(root).as_posix()
        ext = p.suffix.lower()
        if ext in TEXT_EXT and (TEXT_NAME.search(r) or ext in {".locres", ".po", ".pot", ".strings", ".translation", ".rpy"}):
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            candidates.append({"path": r, "size": size})
            m = LANG_HINT.search(r)
            if m:
                existing_langs.add(m.group(1).lower())
    candidates.sort(key=lambda c: (-c["size"], c["path"]))

    return {
        "root": str(root),
        "engines": found,
        "text_candidates": candidates[:60],
        "language_hints": sorted(existing_langs),
        "top_extensions": dict(sorted(exts.items(), key=lambda kv: -kv[1])[:12]),
        "files_scanned": len(files),
    }


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("game_dir")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.game_dir)
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    result = detect(root)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    print(f"Scanned {result['files_scanned']} entries in {root}")
    if not result["engines"]:
        print("Engine: unknown (no known signature). Inspect the file list manually.")
    for e in result["engines"]:
        variant = f" [{e['variant']}]" if e["variant"] else ""
        print(f"Engine: {e['engine']}{variant}  (confidence: {e['confidence']})")
        for ev in e["evidence"]:
            print(f"   - {ev}")
        if e["reference"]:
            print(f"   > see references/{e['reference']}")
    if result["language_hints"]:
        print("Language hints in file names:", ", ".join(result["language_hints"]))
    if result["text_candidates"]:
        print("Likely text sources (largest first):")
        for c in result["text_candidates"][:20]:
            print(f"   {c['size']:>10,}  {c['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
