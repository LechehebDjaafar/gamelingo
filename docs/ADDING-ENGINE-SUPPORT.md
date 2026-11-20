# Adding support for a new engine or format

1. **Signature** — add detection in `skills/gamelingo/scripts/detect_engine.py` (file names / folders / extensions) and a test in `tests/test_scripts.py` using a synthetic folder.
2. **Recipe** — create `skills/gamelingo/references/engines/<engine>.md` with: detection, where text lives, extract/apply commands, fonts/RTL behavior, repack/install method, warnings. Map it in `DOC_BY_ENGINE`.
3. **Format handler** (if the text format is new) — add `<fmt>_extract` and `<fmt>_apply` to `strings_io.py`, register in `HANDLERS` and `SUPPORTED`, and test the round trip (extract → translate → apply → re-parse).
4. **Docs** — update the support table in `README.md` and `CHANGELOG.md`.

Status vocabulary: **Stable** = round-trip covered by tests · **Beta** = documented recipe that works with a third-party tool · **Experimental** = needs per-game investigation.
