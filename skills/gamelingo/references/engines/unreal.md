# Unreal Engine

**Detect**: `*.pak` (and `*.utoc`/`*.ucas`) in `<Game>/Content/Paks`, `Engine/` folder, `*-Win64-Shipping.exe`, `*.locres`.

**Difficulty**: medium — text is in `.locres` string tables and `.uasset` files inside pak archives.

## Where text lives
- `Game/Content/Localization/<Target>/<culture>/<Target>.locres` — compiled localization resources (best case).
- `.uasset` StringTables, DataTables, widget blueprints with hard-coded `FText` (often with namespaces/keys).
- Some games ship only the base culture; others ship `en`, `fr`, ... as separate `.locres` files.

## Workflow
1. Extract the needed `.locres`/`.uasset` from the paks with repak, UnrealPak or FModel (read-only extraction of **text resources only**).
2. Convert `.locres` ⇄ CSV/PO with a localization tool (e.g. UE4localizationsTool) — the CSV/PO round-trip is supported by `strings_io.py`.
3. For a new culture: copy the base `.locres` into a new culture folder (`ar/`), translate, and add the culture to the game's enabled cultures via `Engine.ini`/`GameUserSettings.ini` (`Culture=ar`) or by overriding the default culture file.
4. Package the changed files as a **patch pak**: place `<GameName>-<Platform>_P.pak` (the `_P` suffix gives it priority) in `Content/Paks` (some games use `Content/Paks/~mods`). Never modify the original pak.
5. Fonts: override the Slate/UMG font with a composite font that includes Arabic; Unreal shapes and applies bidi itself. Check text box `FlowDirection`.

## Warnings
IoStore (`.utoc/.ucas`) and encrypted paks need the AES key — if you do not have it legitimately, stop. Many Unreal games use EasyAntiCheat/BattlEye: only single-player/offline.
