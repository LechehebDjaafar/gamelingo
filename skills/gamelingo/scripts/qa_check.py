#!/usr/bin/env python3
"""Quality checks for a translated string table.

Checks
  ERROR    placeholder / control-code mismatch between source and target
  ERROR    leftover mask tokens (⟦0⟧)
  WARNING  glossary term missing in target
  WARNING  target identical to source
  WARNING  target much longer than source (UI overflow risk)
  WARNING  line-break count differs
  WARNING  target not written in the expected script (--expect-script)
  INFO     untranslated strings

Usage:
    qa_check.py table.jsonl [--glossary glossary.json] [--max-ratio 2.0]
                [--expect-script arabic|hebrew|cyrillic|cjk|hangul|none] [--field target]
                [--strict] [--json]
Exit code 1 when there are errors (or warnings with --strict).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from placeholders import find_tokens  # noqa: E402

SCRIPTS = {
    "arabic": re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"),
    "hebrew": re.compile(r"[\u0590-\u05FF\uFB1D-\uFB4F]"),
    "cyrillic": re.compile(r"[\u0400-\u04FF]"),
    "cjk": re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]"),
    "hangul": re.compile(r"[\uAC00-\uD7AF\u1100-\u11FF]"),
}
LETTER = re.compile(r"[^\W\d_]", re.UNICODE)


def check(rows, glossary=None, max_ratio=2.0, expect_script="none", field="target"):
    issues = []
    untranslated = 0
    glossary = glossary or {}
    script_re = SCRIPTS.get(expect_script)

    def add(level, row, code, msg):
        issues.append({"level": level, "code": code, "id": row["id"], "file": row.get("file", ""), "message": msg})

    for r in rows:
        src, tgt = r["source"], (r.get(field) or "")
        if not tgt.strip():
            untranslated += 1
            continue
        if Counter(find_tokens(src)) != Counter(find_tokens(tgt)):
            add("error", r, "placeholders",
                f"source tokens {sorted(find_tokens(src))} != target tokens {sorted(find_tokens(tgt))}")
        if "⟦" in tgt or "⟧" in tgt:
            add("error", r, "mask-leftover", "mask token left in target")
        if tgt.strip() == src.strip() and LETTER.search(src) and len(src) > 3:
            add("warning", r, "identical", "target identical to source")
        if len(src) >= 4 and len(tgt) / max(len(src), 1) > max_ratio:
            add("warning", r, "too-long", f"target is {len(tgt) / len(src):.1f}x longer than source")
        if src.count("\n") != tgt.count("\n"):
            add("warning", r, "newlines", f"line breaks: source {src.count(chr(10))}, target {tgt.count(chr(10))}")
        for term, wanted in glossary.items():
            if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", src, re.IGNORECASE) and wanted not in tgt:
                add("warning", r, "glossary", f"'{term}' should be translated as '{wanted}'")
        if script_re and len(LETTER.findall(src)) >= 8:
            letters = LETTER.findall(tgt)
            if letters and sum(1 for c in letters if script_re.match(c)) / len(letters) < 0.3:
                add("warning", r, "script", f"target does not look like {expect_script} text")

    return {
        "total": len(rows),
        "translated": len(rows) - untranslated,
        "untranslated": untranslated,
        "errors": sum(1 for i in issues if i["level"] == "error"),
        "warnings": sum(1 for i in issues if i["level"] == "warning"),
        "issues": issues,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("table")
    ap.add_argument("--glossary")
    ap.add_argument("--max-ratio", type=float, default=2.0)
    ap.add_argument("--expect-script", default="none", choices=["none", *SCRIPTS])
    ap.add_argument("--field", default="target")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.table, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    glossary = {}
    if args.glossary:
        glossary = json.loads(Path(args.glossary).read_text(encoding="utf-8")).get("terms", {})
    report = check(rows, glossary, args.max_ratio, args.expect_script, args.field)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{report['translated']}/{report['total']} translated, "
              f"{report['errors']} error(s), {report['warnings']} warning(s)")
        for i in report["issues"][:200]:
            print(f"  [{i['level'].upper():7}] {i['file']}:{i['id']}  {i['code']}: {i['message']}")
        if len(report["issues"]) > 200:
            print(f"  ... {len(report['issues']) - 200} more (use --json)")
    failed = report["errors"] or (args.strict and report["warnings"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
