---
name: gamelingo-restore
description: Undo a GameLingo patch and return a game to its original state from a verified backup. Use when the user wants to uninstall the translation, revert changes, the game crashes after patching, a game update broke the patch, or they want to switch to a different translation build.
---

# GameLingo · Restore

1. Find the backup folder (contains `manifest.json`). Show details: `python ../gamelingo/scripts/backup.py info "<backup_dir>"`.
2. Verify integrity: `python ../gamelingo/scripts/backup.py verify "<backup_dir>"`. If damaged, stop and tell the user to use the launcher's file verification instead (Steam: Properties → Installed Files → Verify integrity of game files; Epic: Library → ⋯ → Manage → Verify).
3. Close the game, then restore: `python ../gamelingo/scripts/backup.py restore "<backup_dir>" [--game-dir "<game_dir>"]`. Files added by the patch (fonts etc.) are removed; modified files return to their original bytes.
4. Confirm by running `detect_engine.py` or launching the game. Report what was restored.

If no backup exists, use the launcher's "verify files" feature — it re-downloads the original files. Never delete game files manually.
