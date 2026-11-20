#!/usr/bin/env python3
"""Protect and compare placeholders / control codes inside game strings.

Game text is full of tokens that must survive translation untouched:
    {0}  {player}  %s  %1$d  <b>..</b>  [color=red]  \\C[2]  \\N[1]  \\n  ${name}  {{var}}

Library use:
    from placeholders import find_tokens, protect, restore
CLI (operates on a string table):
    placeholders.py protect table.jsonl -o masked.jsonl    # adds source_masked
    placeholders.py restore masked.jsonl -o table.jsonl    # target_masked -> target
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter

PATTERNS = [
    r"\{\{[^{}\n]*\}\}",                       # {{var}}
    r"\$\{[^{}\n]*\}",                         # ${name}
    r"\{[^{}\n]*\}",                           # {0} {player}
    r"%\([^)\n]+\)[sdif]",                     # %(name)s
    r"%(?:\d+\$)?[-+#0]*\d*(?:\.\d+)?[sdifuxXcgeE%]",  # %s %d %1$s %%
    r"</?[A-Za-z][^<>\n]*>",                   # <b> </b> <color=#fff>
    r"\[/?[A-Za-z][A-Za-z0-9_]*(?:=[^\]\n]*)?\]",     # [b] [color=red]
    r"\\[A-Za-z]+\[\d*\]",                     # \C[2] \N[1] \V[3]
    r"\\[nrt]",                                # literal \n \r \t
    r"\\[{}.|!><^$]",                          # RPG Maker \{ \} \. \| \! \> \< \^ \$
]
TOKEN_RE = re.compile("|".join(f"(?:{p})" for p in PATTERNS))
MASK_RE = re.compile(r"⟦\s*(\d+)\s*⟧")


def find_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def protect(text: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def sub(m: re.Match) -> str:
        tokens.append(m.group(0))
        return f"⟦{len(tokens) - 1}⟧"

    return TOKEN_RE.sub(sub, text), tokens


def restore(masked: str, tokens: list[str]) -> str:
    def sub(m: re.Match) -> str:
        i = int(m.group(1))
        return tokens[i] if i < len(tokens) else m.group(0)

    return MASK_RE.sub(sub, masked)


def same_tokens(source: str, target: str) -> bool:
    return Counter(find_tokens(source)) == Counter(find_tokens(target))


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def _save(rows, path):
    with open(path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("protect", "restore"):
        p = sub.add_parser(name)
        p.add_argument("table")
        p.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    rows = _load(args.table)
    for r in rows:
        if args.cmd == "protect":
            r["source_masked"], r["tokens"] = protect(r["source"])
        else:
            if r.get("target_masked"):
                r["target"] = restore(r["target_masked"], r.get("tokens", []))
    _save(rows, args.output)
    print(f"{args.cmd}: {len(rows)} records -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
