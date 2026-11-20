# Changelog
All notable changes follow [Keep a Changelog](https://keepachangelog.com) and [SemVer](https://semver.org).

## [0.1.1] - 2026-11-20
### Fixed
- CI on Windows: added `.gitattributes` (LF line endings) so multi-line CSV fixtures parse identically on every OS.
- Console output is forced to UTF-8 so Arabic text prints correctly in Windows terminals.
### Changed
- Minimum Python is now 3.10 (3.9 is end-of-life and `arabic-reshaper`/`python-bidi` dropped it); CI tests 3.10, 3.12, 3.13.

## [0.1.0] - 2026-11-20
### Added
- 8 skills: `gamelingo`, `-scan`, `-extract`, `-translate`, `-rtl`, `-qa`, `-pack`, `-restore`.
- Scripts: `find_games`, `detect_engine`, `strings_io` (JSON/PO/CSV/properties), `placeholders`, `rtl`, `qa_check`, `backup`.
- Engine recipes: RPG Maker, Ren'Py, Godot, Unity, Unreal, GameMaker, Electron/NW.js.
- Arabic/RTL guide, legal notes, unit tests, CI, installers for macOS/Linux/Windows.
