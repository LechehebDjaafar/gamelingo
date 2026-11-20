# Architecture

```
┌────────────────────────── Claude Code ──────────────────────────┐
│  /gamelingo  (orchestrator skill)                                 │
│     ├─ gamelingo-scan      find game → detect engine → text map   │
│     ├─ gamelingo-extract   files → strings.jsonl                  │
│     ├─ gamelingo-translate strings.jsonl → translated + glossary  │
│     ├─ gamelingo-rtl       shaping / bidi / fonts                 │
│     ├─ gamelingo-qa        placeholders, glossary, in-game list   │
│     ├─ gamelingo-pack      overlay + backup + install             │
│     └─ gamelingo-restore   undo                                   │
└───────────────┬───────────────────────────────────────────────────┘
                │ calls deterministic, unit-tested helpers
        skills/gamelingo/scripts/
          find_games.py  detect_engine.py  strings_io.py
          placeholders.py  rtl.py  qa_check.py  backup.py
```

## Design principles
1. **Claude does the judgment, scripts do the plumbing.** Translation, glossary decisions and engine reasoning are LLM work; parsing, writing back, hashing and backups are scripts, so they are repeatable and tested.
2. **One interchange format** — `strings.jsonl` (see `references/string-table-format.md`) decouples engines from translation.
3. **Overlay, never in-place.** `strings_io.py apply` writes only changed files into a separate folder; `backup.py` records hashes and removes files the patch added.
4. **Progressive disclosure.** Each `SKILL.md` stays short; per-engine detail is loaded from `references/engines/` only when needed.
5. **No binary downloads, no DRM bypass.** External tools are named, never fetched automatically.

## Data flow
`game folder` → `detect_engine` → (unpack with engine tool) → `strings_io extract` → `strings.jsonl` → translate → `qa_check` → `rtl` (optional) → `strings_io apply` → `overlay/` → `backup snapshot` → copy into game.
