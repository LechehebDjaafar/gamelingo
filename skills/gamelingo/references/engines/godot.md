# Godot

**Detect**: `*.pck` next to the executable, or `project.godot` in unpacked projects; `*.translation` resources; `.csv`/`.po` translation sources.

**Difficulty**: easy if translations are CSV/PO; medium if packed in `.pck`.

## Workflow
1. Unpack the `.pck` with GDRE Tools (gdsdecomp) *for reading text only*. Look for `translations.csv`, `*.po`, `*.translation`, `.tres` resources and scripts/scenes with hard-coded strings.
2. CSV translations: first column is the key, other columns are locales (`en,fr,...`). Use
   `strings_io.py extract file.csv --key-col keys --source-col en`, translate, then `apply ... --target-col ar` to add the locale column.
3. `.translation` (compiled): regenerate from the CSV/PO source with the Godot editor/import pipeline; if only compiled files exist, extraction needs a specialised tool.
4. Add the locale to the project's translation list and ensure the game's locale selection includes it (project settings → Localization). Without the project source you can often load loose files via a `override.cfg`/patch `.pck` named after the main one (Godot loads `<game>.pck` patches and `--main-pack`); verify for the specific Godot version.
5. Fonts: add a `FontFile`/theme override or a fallback font list that includes an Arabic font. Godot 4 handles shaping/bidi, so use `none` mode; Godot 3 needs `shape`/`visual`.

## Safety
Ship a patch pack, never a modified copy of the original `.pck`.
