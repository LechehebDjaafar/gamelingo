#!/usr/bin/env python3
"""Prepare right-to-left text (Arabic, Persian, Urdu, Hebrew) for engines with weak RTL support.

Modes (pick the one that matches the engine, see references/rtl-arabic.md):
    none    engine does shaping AND bidi itself              -> text left untouched
    shape   engine does bidi but not letter joining          -> reshape only (logical order)
    visual  engine does neither (draws glyphs left-to-right) -> reshape + reorder to visual order

Requires:  pip install arabic-reshaper python-bidi

Usage:
    rtl.py check
    rtl.py text "مرحبا بالعالم" --mode visual
    rtl.py table strings.jsonl -o strings.rtl.jsonl --mode shape [--field target] [--out-field target_rtl]
"""
from __future__ import annotations

import argparse
import json
import re
import sys

RTL_CHARS = re.compile(r"[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]")


def _libs():
    try:
        import arabic_reshaper  # type: ignore
    except ImportError:
        arabic_reshaper = None
    get_display = None
    try:
        from bidi import get_display  # type: ignore
    except ImportError:
        try:
            from bidi.algorithm import get_display  # type: ignore
        except ImportError:
            pass
    return arabic_reshaper, get_display


def has_rtl(text: str) -> bool:
    return bool(RTL_CHARS.search(text))


def process(text: str, mode: str = "shape") -> str:
    if mode == "none" or not has_rtl(text):
        return text
    reshaper, get_display = _libs()
    if mode in ("shape", "visual") and reshaper is None:
        raise RuntimeError("arabic-reshaper is not installed: pip install arabic-reshaper python-bidi")
    if mode == "visual" and get_display is None:
        raise RuntimeError("python-bidi is not installed: pip install python-bidi")
    out_lines = []
    for line in text.split("\n"):
        if not has_rtl(line):
            out_lines.append(line)
            continue
        shaped = reshaper.reshape(line)
        out_lines.append(get_display(shaped, base_dir="R") if mode == "visual" else shaped)
    return "\n".join(out_lines)


def main() -> int:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    t = sub.add_parser("text")
    t.add_argument("value")
    t.add_argument("--mode", choices=["none", "shape", "visual"], default="shape")
    tb = sub.add_parser("table")
    tb.add_argument("table")
    tb.add_argument("-o", "--output", required=True)
    tb.add_argument("--mode", choices=["none", "shape", "visual"], default="shape")
    tb.add_argument("--field", default="target")
    tb.add_argument("--out-field", default="target_rtl")
    args = ap.parse_args()

    if args.cmd == "check":
        reshaper, get_display = _libs()
        print("arabic-reshaper:", "ok" if reshaper else "MISSING")
        print("python-bidi    :", "ok" if get_display else "MISSING")
        return 0 if reshaper and get_display else 1
    if args.cmd == "text":
        print(process(args.value, args.mode))
        return 0
    with open(args.table, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    for r in rows:
        r[args.out_field] = process(r.get(args.field) or "", args.mode)
    with open(args.output, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"processed {len(rows)} records (mode={args.mode}) -> {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
