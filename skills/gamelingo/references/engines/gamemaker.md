# GameMaker

**Detect**: `data.win` (Windows), `game.unx` (Linux), `game.ios`/`game.droid`; `options.ini`.

**Difficulty**: medium — all assets and strings are inside `data.win`.

## Workflow
1. Open a **copy** of `data.win` with UndertaleModTool; export strings (String table / code text) to a text/CSV file.
2. Translate with the string table; strings used as identifiers (object/room names, file keys) must not be changed.
3. Import changed strings back into the copy, save as `data.win`, and install it with `gamelingo-pack` (backup first). Some games store dialogue in external `lang/*.json` or `.ini` files — much easier, use `strings_io.py`.
4. Fonts: GameMaker uses font resources built into `data.win` (or bitmap fonts); adding Arabic means adding a font resource with the needed glyph ranges and changing code that selects fonts. There is no built-in shaping/bidi → `visual` mode.

Keep the original `data.win` backed up; it is a single file and any error breaks the game.
