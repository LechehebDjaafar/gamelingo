---
name: gamelingo
description: Localize an installed PC game into any language (Arabic, Persian, Turkish, Spanish, Japanese, ...) by analyzing its files, extracting the text, translating it with context, fixing right-to-left rendering and fonts, and packaging a reversible patch. Use this whenever the user wants to translate a game, add Arabic or another language to a Steam / Epic Games / GOG game, make a game "support" a language it lacks, create a fan translation or localization mod, or asks "can you translate my game". Start here; it runs the whole pipeline and hands off to the gamelingo-* skills.
---

# GameLingo — full game localization pipeline

Turn "this game has no <language>" into a working, reversible translation patch for a game the user **owns and has installed**.

## Ground rules (never skip)

1. **Non-destructive.** Never edit the user's game files in place. Work on copies, then use `gamelingo-pack` to install with a backup. Every change must be undoable with `gamelingo-restore`.
2. **Own copy only.** Operate on the user's installed copy. Do not extract assets to share, do not copy game files into any repo or archive meant for distribution. Distribute translations as *overlays* (only changed text files), never full game files. See `references/legal-and-safety.md`.
3. **No DRM / anti-cheat circumvention.** If a game uses online anti-cheat (EasyAntiCheat, BattlEye, Vanguard) or is a competitive multiplayer title, warn the user that modifying files can get the account banned, and recommend single-player/offline use only. Stop if the only route requires bypassing protection.
4. **Ask before writing.** Show what will change and where before the pack step.
5. **Be honest about limits.** If the engine is unsupported or text is baked into images/audio, say so and offer what is possible.

## Inputs to collect (ask only for what is missing)

- Game: name or folder path (Steam, Epic, GOG, manual).
- Target language (any), and dialect/tone if relevant (e.g. Modern Standard Arabic vs. colloquial, formal vs. casual).
- Source language (default: the game's English text).
- Whether the user wants machine-quality speed or reviewed quality (affects batch size and QA depth).

## Pipeline

| Step | Skill | Result |
|------|-------|--------|
| 1. Find + identify | `gamelingo-scan` | game folder, engine, text-file candidates, existing languages |
| 2. Extract | `gamelingo-extract` | `strings.jsonl` string table |
| 3. Translate | `gamelingo-translate` | `target` filled, glossary honored, placeholders intact |
| 4. RTL + fonts | `gamelingo-rtl` | shaped text / font plan (RTL languages and complex scripts) |
| 5. QA | `gamelingo-qa` | `qa_check.py` clean, in-game test checklist |
| 6. Package + install | `gamelingo-pack` | overlay folder, backup, install steps |
| Undo anytime | `gamelingo-restore` | game back to original |

Run steps in order, report after each, and stop when a step reveals a blocker.

## Helper scripts

All deterministic work is done by stdlib-only Python scripts in `scripts/` (this skill's folder): `find_games.py`, `detect_engine.py`, `strings_io.py`, `placeholders.py`, `rtl.py`, `qa_check.py`, `backup.py`. Run `python <script> --help` for options. Prefer them over improvising: they are unit-tested.

## References (load only when needed)

- `references/string-table-format.md` — the `strings.jsonl` format.
- `references/rtl-arabic.md` — RTL / Arabic rendering theory and per-engine behavior.
- `references/legal-and-safety.md` — what is and is not acceptable.
- `references/engines/<engine>.md` — per-engine extraction and repack recipes (unity, unreal, godot, rpgmaker, renpy, gamemaker, electron-nwjs).
- `references/glossary-template.json` — starting glossary.

## Final report format

End with: engine, files touched, number of strings translated, QA result, backup location, how to undo, and known visual risks (overflow, fonts, RTL).
