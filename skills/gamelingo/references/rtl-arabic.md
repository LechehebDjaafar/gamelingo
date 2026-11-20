# Right-to-left and Arabic rendering in games

## Three separate problems
1. **Shaping** — Arabic letters change form (isolated / initial / medial / final) depending on neighbors. Engines without a shaping engine (e.g. HarfBuzz) draw every letter in its isolated form: "مرحبا" shows as disconnected letters.
2. **Bidirectional ordering (bidi)** — Arabic flows right-to-left, while numbers and Latin words flow left-to-right inside it. Engines without bidi draw the string reversed.
3. **Glyph coverage** — the game's font may not contain Arabic at all (boxes □ or `?`).

## Solutions
| Situation | Fix |
|---|---|
| Engine shapes + does bidi | Provide a font with Arabic coverage. Done. |
| Engine does bidi only | Pre-shape text (`rtl.py --mode shape`) into Unicode Presentation Forms (U+FB50–FDFF, U+FE70–FEFF); font must contain those glyphs. |
| Engine does neither | Pre-shape and reorder (`--mode visual`); manual line breaks only, because the engine's auto-wrap will fight you. |

Pre-shaped text is for the **game file only**. Keep the logical `target` as your master copy.

## Engine tendencies (verify per game and version)
- **Godot 4**: text server with complex-text layout and RTL support; usually needs only a font. Godot 3 needs pre-shaping.
- **Unreal Engine**: shapes via HarfBuzz and handles bidi in Slate/UMG; usually font coverage and sometimes text-box flow direction.
- **Unity**: legacy UI Text and many TextMeshPro setups lack shaping; common fixes are an RTL plugin for TextMeshPro, or pre-shaped text with an Arabic SDF font atlas.
- **RPG Maker MV/MZ**: Chromium-based, so single strings shape correctly, but message windows draw character by character, which can break letter joining and alignment; common fixes are pre-shaping or a plugin that draws whole lines.
- **Ren'Py**: check the documentation of the Ren'Py version for RTL/shaping support; if absent, use `visual` mode with an Arabic font.
- **GameMaker / custom engines**: typically no shaping and no bidi → `visual` mode and a bitmap or TTF font with presentation forms.

## Punctuation, digits, mixing
- Arabic comma `،`, semicolon `؛`, question mark `؟`. Western digits are safest across game fonts; Arabic-Indic digits (٠-٩) only if the font and engine support them.
- Latin names inside Arabic sentences are reordered by bidi; test with names, numbers and parentheses.
- Placeholders such as `{name}` may move in visual mode — check them in-game.

## Recommended free fonts (SIL OFL)
Noto Sans Arabic, Noto Naskh Arabic, Cairo, Tajawal, IBM Plex Sans Arabic, Amiri (classical/Naskh). Include the license file when you ship them.

## Other scripts
Persian/Urdu need extra letters (پ چ ژ گ ک ی; Urdu also ٹ ڈ ڑ ں ے) — ensure the font has them. Hebrew has no shaping but needs bidi. Thai, Devanagari and similar scripts need shaping and combining-mark support, so treat them like Arabic. CJK mostly needs a font with enough glyphs and a character atlas that includes them.
