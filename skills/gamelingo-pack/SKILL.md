---
name: gamelingo-pack
description: Write translated strings back into game files as a safe overlay, back up the originals, install the patch into the game folder, and produce an installer plus uninstall instructions. Use after translation and QA, or when the user says "apply the translation", "install the patch", "build the mod", or wants to share a translation patch without redistributing game files.
---

# GameLingo · Pack & install

## 1. Build the overlay (no game folder writes yet)

```
python ../gamelingo/scripts/strings_io.py apply original/ strings.jsonl -o overlay/ [--field target_rtl] [--target-col ar]
```
`overlay/` receives **only the files that changed**, same relative paths as in the game. Container formats (Unity assets, `.pak`, `.pck`, `.rpa`, `app.asar`): repack with the tool from `references/engines/<engine>.md`, or use the engine's mod-loading mechanism (e.g. Unreal `~mods`/`_P.pak`, Ren'Py `game/tl/<lang>/`, BepInEx plugin folders) so originals stay untouched.

Add the font files from `gamelingo-rtl` into the overlay at the path the engine expects.

## 2. Back up, then install

1. List every path the overlay will touch (including new files).
2. `python ../gamelingo/scripts/backup.py snapshot "<game_dir>" "<backup_dir>" --paths <rel1> <rel2> ...`
3. Verify: `python ../gamelingo/scripts/backup.py verify "<backup_dir>"`
4. Show the user the list and get confirmation, then copy `overlay/*` over the game folder.
5. Tell the user to launch the game and run the checklist from `gamelingo-qa`. Mention that **Steam "Verify integrity of game files" and game updates will revert the patch**; re-apply after updates.

## 3. Distribution package (optional)

Create `<game>-<lang>-patch/` with: `overlay/` (translated text + fonts you have the right to distribute), `install.py`/`install.bat` (backup + copy), `uninstall` (calls restore), `README` (supported game version, steps, credits). **Never include original game files, extracted assets, or copyrighted text from the game beyond what the translation overlay necessarily contains.** Read `references/legal-and-safety.md` first and tell the user about publisher policies on fan translations.

## Output

Overlay path, backup path, install result, how to undo (`gamelingo-restore`).
