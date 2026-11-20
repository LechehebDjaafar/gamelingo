---
name: gamelingo-qa
description: Validate a translated game string table and guide in-game testing - placeholder integrity, glossary consistency, wrong-script output, overflow risk, untranslated leftovers, plus a screen-by-screen checklist for text clipping, missing glyphs and RTL problems. Use after translation or before packaging, or when a translated game shows crashes, garbled text, boxes, or cut-off lines.
---

# GameLingo · QA

## Automated checks

```
python ../gamelingo/scripts/qa_check.py strings.jsonl --glossary glossary.json --expect-script arabic [--strict]
```
- **Errors** (must fix): placeholder/control-code mismatch, leftover mask tokens — these crash games or show raw codes.
- **Warnings** (review): glossary misses, identical-to-source, target ≫ source length, line-break count, wrong script.
- Fix the table, rerun until zero errors. Use `--json` for details.

## Manual review (sample)

Read ~30 random translated strings aloud to yourself: natural phrasing? consistent names? right tone per character? Check the first and last strings of each file and every string with a placeholder.

## In-game checklist (give to the user)

- Main menu, options, save/load, pause, inventory, skill/quest screens
- First 5 minutes of dialogue; one long dialogue box; one choice menu
- Item/skill tooltips with numbers and variables
- Battle/HUD text, notifications, tutorials, credits
- Special characters: punctuation, numbers, mixed Latin names, line wraps
- For RTL: letters connected? word order correct? punctuation on the correct side? alignment right?
- Boxes (□) or `?` ⇒ missing glyphs → font problem (`gamelingo-rtl`). Cut-off text ⇒ shorten translation or enlarge box. Crash on a screen ⇒ check that screen's placeholders.

Ask the user for screenshots of problems; map each to its string `id`, fix the table, rebuild the overlay with `gamelingo-pack`.
