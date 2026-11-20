# Electron / NW.js games

**Detect**: `resources/app.asar` (Electron), `package.nw` or `nw.pak` (NW.js). RPG Maker MV/MZ also runs on NW.js (see `rpgmaker.md`).

**Difficulty**: easy — it is a web app; text is JS/JSON/HTML.

## Workflow
1. Electron: extract a **copy** of `app.asar` with `npx @electron/asar extract app.asar app/` (Node required). NW.js: `package.nw` is a zip archive.
2. Text is usually in JSON/locale files (`locales/`, `i18n/`, `lang/`), otherwise in JS bundles — for bundles prefer adding a runtime i18n layer instead of editing minified code.
3. Extract with `strings_io.py`, translate, apply to the overlay, repack with `asar pack` (or `zip` for NW.js) into a **new** file, or place loose files in `resources/app/` — Electron prefers an `app/` folder over `app.asar`.
4. Chromium shapes Arabic and applies bidi; add `@font-face` with an Arabic font and `dir="rtl"`/`direction: rtl` for the text containers.

Check for ASAR integrity/signature protections in newer builds; do not bypass them.
