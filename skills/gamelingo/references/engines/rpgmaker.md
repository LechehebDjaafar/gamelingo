# RPG Maker MV / MZ (and older RGSS)

**Detect**: `js/rpg_core.js` (MV) or `js/rmmz_core.js` (MZ); `www/data/*.json` or `data/*.json`; `package.json`. Older: `Game.rgss3a`, `Data/*.rvdata2`/`.rxdata`.

**Difficulty**: easy (MV/MZ) — text is plain JSON.

## Where the text is
- `data/System.json`: `gameTitle`, `currencyUnit`, `terms.*` (arrays/objects), `switches`/`variables` names (usually leave).
- `data/Actors|Classes|Items|Skills|Weapons|Armors|Enemies|States.json`: `name`, `description`, `nickname`, `profile`, `message1..4`.
- `data/MapXXX.json`, `data/CommonEvents.json`, `data/Troops.json`: event commands; dialogue in code `401` (text line) and `101` (header), choices in `102`, scrolling text `405`. Text lives in `parameters`.
- `js/plugins.js` and `js/plugins/*.js`: plugin parameter text (JSON-in-strings) — handle carefully.
- Encrypted assets (`.rpgmvp`, `.rpgmvo`) are images/audio, not text; ignore.

## Extract / apply
```
python scripts/strings_io.py extract data/ -o strings.jsonl --keys name,nickname,profile,description,message1,message2,message3,message4,gameTitle,currencyUnit,parameters --min-len 2
python scripts/strings_io.py apply data/ strings.jsonl -o overlay/data
```
`parameters` also contains non-text values (file names, ids). Review the table and drop non-text rows; the `--min-len` and letter-only filters remove most noise. Do **not** translate `note` fields or plugin command arguments unless you know they are display text.

Control codes to keep: `\C[n] \N[n] \V[n] \I[n] \{ \} \. \| \! \> \< \^ \$`.

## Fonts
Place a font in `fonts/` and register it in `fonts/gamefont.css` (MV) or `js/plugins.js`/`css` settings (MZ). Windows use `$gameSystem.mainFontFace()`. RTL: see `rtl-arabic.md` for message-window caveats.

## Repack
Copy overlay files over `data/`. No repack step. RGSS archives: unpack with a community tool first, convert text, and repack or load loose files (the engine prefers loose files over archives).
