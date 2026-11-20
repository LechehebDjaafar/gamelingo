---
name: gamelingo-scan
description: Locate an installed game (Steam, Epic Games, GOG, or a custom folder), identify its engine (Unity, Unreal, Godot, RPG Maker, Ren'Py, GameMaker, Electron/NW.js), and find where its text and existing language files live. Use when the user names a game to translate, asks which engine a game uses, wants to know if a game can be localized, or says "scan my game folder".
---

# GameLingo · Scan

Find the game, identify the engine, and map where the text lives. Read-only.

## Steps

1. **Locate the game.** If the user gave a path, use it. Otherwise run
   `python ../gamelingo/scripts/find_games.py --name "<game name>"`
   It reads Steam (`appmanifest_*.acf`, all library folders) and Epic (`Manifests/*.item`) metadata. For GOG/itch/other installs pass `--root <folder>`. If nothing is found, ask for the install path (Steam: right-click game → Manage → Browse local files).
2. **Identify the engine.**
   `python ../gamelingo/scripts/detect_engine.py "<game_dir>" --json`
   Read `engines`, `text_candidates`, `language_hints`.
3. **Decide feasibility** using `references/engines/<engine>.md` (relative to the `gamelingo` skill folder). Classify as:
   - **Easy**: plain text/JSON/CSV/PO/properties/Ren'Py scripts.
   - **Medium**: text inside engine containers (Unity assets, `.locres`, `.pck`) that need an external tool.
   - **Hard / unsupported**: encrypted or custom binary formats, text rendered in images, online-only games.
4. **Check protections.** Look for `EasyAntiCheat`, `BattlEye`, `Vanguard`, `Denuvo` markers (folder/file names). If present, warn per the ground rules in `gamelingo` and recommend an offline-only approach or stopping.
5. **Report**: engine + variant, existing languages (if the game already ships several, the best route is often *adding a language to the existing localization table*), the files to extract, required external tools, risk level.

## Output

A short scan report plus the exact paths for the extract step. Do not modify anything.
