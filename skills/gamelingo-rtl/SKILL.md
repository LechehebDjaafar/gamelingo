---
name: gamelingo-rtl
description: Make Arabic, Persian, Urdu or Hebrew (right-to-left, joined-letter scripts) actually render correctly inside a game - letter shaping, bidirectional ordering, fonts with the right glyphs, UI mirroring, numbers. Also covers font replacement for CJK, Thai and other scripts the game font lacks. Use whenever the target language is RTL or the game shows boxes, question marks, disconnected or reversed letters after translation.
---

# GameLingo · RTL, shaping and fonts

Translated text that is correct in a file can still look broken in-game. Fix rendering **after** translation. Read `references/rtl-arabic.md` (in the `gamelingo` skill) for the theory.

## 1. Pick the rendering mode for the engine

| Engine behavior | Mode | What to do |
|---|---|---|
| Does shaping + bidi itself (modern browsers/Chromium-based, Godot 4 TextServer, Unreal with proper font, Unity with an RTL-aware text package) | `none` | ship logical-order text, just fix fonts |
| Does bidi but not letter joining | `shape` | reshape only |
| Does neither (draws glyphs left→right) | `visual` | reshape + reorder per line |

Do not guess: take the engine note in `references/engines/<engine>.md`, make a 5-string test patch, look at the result in-game, then choose.

## 2. Process the table

```
pip install arabic-reshaper python-bidi
python ../gamelingo/scripts/rtl.py check
python ../gamelingo/scripts/rtl.py table strings.jsonl -o strings.rtl.jsonl --mode shape   # or visual
```
This adds `target_rtl`; apply it with `strings_io.py apply ... --field target_rtl`. Keep the logical `target` untouched as the source of truth.

Caveats of `visual` mode: manual line breaks are respected but the engine's automatic word wrap will reverse line order; keep dialogue lines short or insert explicit `\n`. Placeholders such as `{name}` may move; run QA and review samples.

## 3. Fonts

- The game font almost never contains Arabic glyphs. Plan a replacement font with full coverage: Noto Sans Arabic, Cairo, Tajawal or IBM Plex Sans Arabic (all SIL OFL, free to bundle in a patch).
- Match the engine's font mechanism (see engine reference): TextMeshPro SDF atlas for Unity, font asset for Unreal, `gui.text_font` for Ren'Py, `Theme`/`FontFile` for Godot, `fonts/` + CSS `@font-face` for RPG Maker MV/MZ.
- Include Arabic-Indic and Western digits, punctuation (، ؛ ؟), Latin letters (for mixed text) and presentation forms (U+FB50–FDFF, U+FE70–FEFF) when mode is `shape` or `visual`.

## 4. UI details

Mirror layouts only if the engine offers it cheaply; otherwise keep the layout and make sure alignment inside text boxes is right-aligned for RTL. Check: numbers next to Arabic, parentheses direction, quotes, mixed Latin names, truncated text.

Report which mode and font you chose and why, and list in-game screens the user should check.
