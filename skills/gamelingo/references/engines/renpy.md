# Ren'Py

**Detect**: `renpy/` and `game/` folders, `*.rpa` archives, `.rpy`/`.rpyc` files.

**Difficulty**: easy — Ren'Py has a built-in translation system.

## Workflow
1. If `game/*.rpa` archives exist, unpack them with `unrpa`; if only `.rpyc` exist, decompile with `unrpyc` (needed only to *read* the script; the translation system works from compiled scripts when you generate translations with the launcher/SDK for that game).
2. Generate translation files: with the Ren'Py SDK use *Generate Translations* for the new language, or run `renpy.sh <project> translate <language>`. This creates `game/tl/<language>/*.rpy` with `translate <language> <id>:` blocks.
3. Extract/translate the dialogue lines inside those blocks (the text lines in quotes), then write them back. The `.rpy` format is not handled by `strings_io.py` — extract the quoted strings with a small script or by hand-built regexes and keep `translate` ids intact.
4. Add a language switch: in `game/tl/<language>/` include a `language.rpy` with `define config.default_language = "<language>"` or provide the preference menu entry; set a font via `translate <language> python:` `gui.text_font = "fonts/<font>.ttf"`, `gui.name_text_font`, `gui.interface_text_font`.

## Notes
- Keep `[variables]`, `{tags}` (e.g. `{b}…{/b}`, `{i}`, `{w}`) and `%` interpolation intact; QA treats them as placeholders.
- RTL: check the SDK documentation for your Ren'Py version; otherwise use `visual` mode with an Arabic font.
- Overlay = only the `game/tl/<language>/` folder plus the font; no original files are modified.
