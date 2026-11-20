# Contributing to GameLingo

Thanks for helping players enjoy games in their own language!

## Ways to contribute
- **Engine recipes** — add or improve `skills/gamelingo/references/engines/<engine>.md` and the signature in `detect_engine.py`.
- **Format handlers** — new formats in `strings_io.py` (e.g. `.xliff`, `.resx`, `.lang`), always with tests.
- **RTL / fonts knowledge** — verified notes for specific engines and versions.
- **Skills** — sharper instructions, better trigger descriptions.
- **Language packs** — glossary templates for other languages.

## Setup
```bash
git clone https://github.com/LechehebDjaafar/gamelingo && cd gamelingo
python -m pip install -r requirements-rtl.txt
make validate test      # or: python tools/validate_skills.py && python -m unittest discover -s tests
```
Scripts use the Python standard library only (RTL features optionally use `arabic-reshaper` and `python-bidi`). Python ≥ 3.10.

## Rules
1. **No game files, no copyrighted text.** Test fixtures must be synthetic.
2. Scripts must be non-destructive: never overwrite sources; refuse unsafe paths.
3. Every behavior change needs a test in `tests/`.
4. Skills: `name` equals folder name; `description` says what *and when* (keep under 1024 chars); keep `SKILL.md` under 500 lines — move detail to `references/`.
5. Be honest in the README support table: *Stable* means covered by tests; recipes that rely on third-party tools are *Beta* or *Experimental*.

## Pull requests
Small, focused PRs. Fill in the template. By contributing you agree your work is released under the MIT license.
