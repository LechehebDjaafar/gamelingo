# String table format (`strings.jsonl`)

One JSON object per line (UTF-8, no BOM).

```json
{"id": "/1/profile", "file": "data/Actors.json", "source": "A fearless courier", "target": "", "context": "Actor description", "note": ""}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable key inside the file. JSON → JSON Pointer (`/events/1/pages/0/list/1/parameters/0`); PO → `msgid` (with `msgctxt\x04` prefix when a context exists); CSV → value of the key column; `.properties` → the key |
| `file` | yes | Path relative to the extraction root (`/` separators) |
| `source` | yes | Original text, unescaped (real newlines, not `\n`) |
| `target` | after translation | Translation in logical order |
| `target_rtl` | optional | Output of `rtl.py` (shaped / visual order) |
| `source_masked`, `tokens`, `target_masked` | optional | Placeholder-protection fields |
| `context`, `note` | optional | Hints for translators; ignored by tools |

Rules: `(file, id)` is unique. Never edit `id`, `file` or `source`. Unknown fields are preserved by all scripts.
Plural PO entries (`msgid_plural`) are skipped by `strings_io.py`; handle them manually.
