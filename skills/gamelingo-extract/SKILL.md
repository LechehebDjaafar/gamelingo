---
name: gamelingo-extract
description: Extract all translatable text from a game's files into a clean string table (strings.jsonl) - from JSON, CSV, PO/POT, .properties, RPG Maker data, Ren'Py scripts, Godot translations, Unity or Unreal localization tables. Use after scanning a game, or when the user wants to pull dialogue, UI text, item names or subtitles out of game files for translation.
---

# GameLingo · Extract

Produce `strings.jsonl` (format in `references/string-table-format.md` of the `gamelingo` skill). Work on a **copy** of the game files in a scratch workspace, never the originals.

## Workflow

1. Create a workspace, e.g. `./gamelingo-work/<game>/` with `original/` (copied text files only), `strings.jsonl`, `overlay/`.
2. Copy only the text-bearing files from the game into `original/` (keep relative paths).
3. **File-based formats (JSON / CSV / PO / properties)** — use the bundled tool:
   ```
   python ../gamelingo/scripts/strings_io.py extract original/ -o strings.jsonl [--keys name,description,parameters] [--min-len 2] [--source-col en --key-col key]
   ```
   - JSON: use `--keys` to keep only text-bearing keys and avoid file names, ids and script data. RPG Maker typical keys: `name, nickname, profile, description, message1..4, gameTitle, currencyUnit, parameters`. Read `references/engines/rpgmaker.md`.
   - CSV: pass `--source-col` (e.g. `en`) and `--key-col`; later apply with `--target-col <lang code>`.
4. **Container formats** (Unity assets, `.locres`, `.pck`, `.rpa`, `data.win`, `app.asar`): follow `references/engines/<engine>.md` to unpack the text with the recommended third-party tool first, convert it to one of the supported file formats, then run the command above. Tell the user which external tool is needed and where to get it; do not download binaries silently.
5. **Sanity-check the table**: count, sample 20 random rows, make sure there are no file paths, identifiers, base64, code or asset names. Tighten `--keys` / `--min-len` and re-run if needed. Add context hints for ambiguous strings ("Save" button vs. verb) in an optional `context` field.
6. Report string count per file (`strings_io.py stats strings.jsonl`) and any text you could not reach (images, audio, hard-coded in binaries).

## Never

- Never extract or keep game assets (textures, audio, models) — text only.
- Never write to the game folder in this step.
