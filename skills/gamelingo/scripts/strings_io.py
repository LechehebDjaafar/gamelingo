#!/usr/bin/env python3
"""Extract translatable strings from game text files into a string table, and write translations back.

Supported formats: .json  .po/.pot  .csv  .properties

String table = JSON Lines, one record per string:
    {"id": "/events/3/text", "file": "data/Map001.json", "source": "Hello", "target": ""}

Commands:
    extract SRC [-o strings.jsonl] [--keys name,description] [--min-len 1]
            [--key-col KEY] [--source-col SRC]              (CSV options)
    apply   SRC TABLE -o DEST [--field target] [--target-col NAME]
    stats   TABLE

`apply` NEVER overwrites SRC. DEST receives only the files that actually changed,
so it works directly as a mod/overlay folder.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import sys
from pathlib import Path

SUPPORTED = {".json", ".po", ".pot", ".csv", ".properties"}
LETTER = re.compile(r"[^\W\d_]", re.UNICODE)


# ----------------------------------------------------------------------------- helpers
def is_text(s: str, min_len: int = 1) -> bool:
    return len(s.strip()) >= min_len and bool(LETTER.search(s))


def read_text(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig"), bom


def write_text(path: Path, text: str, bom: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


# ----------------------------------------------------------------------------- JSON
def _ptr_escape(part) -> str:
    return str(part).replace("~", "~0").replace("/", "~1")


def _ptr_unescape(part: str) -> str:
    return part.replace("~1", "/").replace("~0", "~")


def _walk_json(node, path, key, out, keys):
    if isinstance(node, str):
        if (not keys or key in keys):
            out.append(("/" + "/".join(_ptr_escape(p) for p in path) if path else "", node))
    elif isinstance(node, dict):
        for k, v in node.items():
            _walk_json(v, path + [k], k, out, keys)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _walk_json(v, path + [i], key, out, keys)


def json_extract(path: Path, opts) -> list[tuple[str, str]]:
    text, _ = read_text(path)
    data = json.loads(text)
    found: list[tuple[str, str]] = []
    _walk_json(data, [], None, found, opts.keys)
    return [(i, s) for i, s in found if is_text(s, opts.min_len)]


def _detect_indent(text: str):
    for line in text.splitlines()[1:6]:
        if line.startswith("\t"):
            return "\t"
        stripped = len(line) - len(line.lstrip(" "))
        if stripped:
            return stripped
    return None


def _json_set(data, pointer: str, value: str) -> bool:
    if pointer == "":
        return False
    parts = [_ptr_unescape(p) for p in pointer.split("/")[1:]]
    node = data
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value
    return True


def json_apply(path: Path, translations: dict[str, str], opts) -> tuple[str | None, int]:
    text, _ = read_text(path)
    data = json.loads(text)
    n = 0
    for pointer, value in translations.items():
        try:
            if _json_set(data, pointer, value):
                n += 1
        except (KeyError, IndexError, ValueError, TypeError):
            print(f"warning: {path.name}: pointer {pointer!r} not found", file=sys.stderr)
    if not n:
        return None, 0
    indent = _detect_indent(text)
    if indent is None and text.count("\n") < 3:
        out = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    else:
        out = json.dumps(data, ensure_ascii=False, indent=indent or 2)
    if text.endswith("\n"):
        out += "\n"
    return out, n


# ----------------------------------------------------------------------------- PO
_PO_KW = re.compile(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+"(.*)"\s*$')
_PO_CONT = re.compile(r'^"(.*)"\s*$')


def _po_unescape(s: str) -> str:
    return re.sub(r'\\(["\\nrt])', lambda m: {"n": "\n", "r": "\r", "t": "\t"}.get(m.group(1), m.group(1)), s)


def _po_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def parse_po(lines: list[str]) -> list[dict]:
    entries: list[dict] = []
    cur = None
    field = None
    for i, line in enumerate(lines):
        s = line.strip()
        m = _PO_KW.match(s)
        if m:
            kw, val = m.groups()
            if kw == "msgctxt" or (kw == "msgid" and (cur is None or "msgid" in cur)):
                if cur:
                    entries.append(cur)
                cur = {"spans": {}}
            if cur is None:
                continue
            cur[kw] = _po_unescape(val)
            cur["spans"][kw] = [i, i + 1]
            field = kw
            continue
        c = _PO_CONT.match(s)
        if c and cur is not None and field:
            cur[field] += _po_unescape(c.group(1))
            cur["spans"][field][1] = i + 1
            continue
        if cur is not None:
            entries.append(cur)
            cur, field = None, None
    if cur:
        entries.append(cur)
    return entries


def _po_id(e: dict) -> str:
    return (e["msgctxt"] + "\x04" + e["msgid"]) if "msgctxt" in e else e["msgid"]


def po_extract(path: Path, opts) -> list[tuple[str, str]]:
    text, _ = read_text(path)
    out = []
    for e in parse_po(text.splitlines()):
        if "msgid_plural" in e or not e.get("msgid"):
            continue
        if is_text(e["msgid"], opts.min_len):
            out.append((_po_id(e), e["msgid"]))
    return out


def po_apply(path: Path, translations: dict[str, str], opts) -> tuple[str | None, int]:
    text, _ = read_text(path)
    lines = text.splitlines()
    n = 0
    for e in reversed(parse_po(lines)):
        if "msgid_plural" in e or not e.get("msgid") or "msgstr" not in e:
            continue
        tid = _po_id(e)
        if tid in translations:
            a, b = e["spans"]["msgstr"]
            lines[a:b] = [f'msgstr "{_po_escape(translations[tid])}"']
            n += 1
    if not n:
        return None, 0
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), n


# ----------------------------------------------------------------------------- CSV
def _csv_dialect(text: str):
    try:
        return csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        return csv.excel


def _col(header: list[str], ref, default: int) -> int:
    if ref is None:
        return default
    if str(ref).isdigit():
        return int(ref)
    if ref in header:
        return header.index(ref)
    raise SystemExit(f"CSV column {ref!r} not found. Columns: {header}")


def csv_extract(path: Path, opts) -> list[tuple[str, str]]:
    text, _ = read_text(path)
    rows = list(csv.reader(io.StringIO(text, newline=""), _csv_dialect(text)))
    if not rows:
        return []
    header = rows[0]
    k = _col(header, opts.key_col, 0)
    s = _col(header, opts.source_col, 1)
    out = []
    for idx, row in enumerate(rows[1:], start=1):
        if len(row) <= max(k, s):
            continue
        rid = row[k] or f"row{idx}"
        if is_text(row[s], opts.min_len):
            out.append((rid, row[s]))
    return out


def csv_apply(path: Path, translations: dict[str, str], opts) -> tuple[str | None, int]:
    text, _ = read_text(path)
    dialect = _csv_dialect(text)
    rows = list(csv.reader(io.StringIO(text, newline=""), dialect))
    if not rows:
        return None, 0
    header = rows[0]
    k = _col(header, opts.key_col, 0)
    if not opts.target_col:
        raise SystemExit("CSV apply needs --target-col (existing column name/index, or a new name such as 'ar').")
    if opts.target_col.isdigit():
        t = int(opts.target_col)
    elif opts.target_col in header:
        t = header.index(opts.target_col)
    else:
        header.append(opts.target_col)
        t = len(header) - 1
    n = 0
    for idx, row in enumerate(rows[1:], start=1):
        if len(row) <= k:
            continue
        rid = row[k] or f"row{idx}"
        if rid in translations:
            row.extend([""] * (t + 1 - len(row)))
            row[t] = translations[rid]
            n += 1
    if not n:
        return None, 0
    width = len(header)
    for row in rows[1:]:
        row.extend([""] * (width - len(row)))
    buf = io.StringIO()
    csv.writer(buf, dialect, lineterminator="\n").writerows(rows)
    return buf.getvalue(), n


# ----------------------------------------------------------------------------- .properties
_PROP = re.compile(r"^(\s*)([^=:\s#!][^=:]*?)(\s*[=:]\s*)(.*)$")


def _prop_unescape(s: str) -> str:
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    return s.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")


def _prop_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")


def prop_extract(path: Path, opts) -> list[tuple[str, str]]:
    text, _ = read_text(path)
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith(("#", "!")):
            continue
        m = _PROP.match(line)
        if m:
            value = _prop_unescape(m.group(4))
            if is_text(value, opts.min_len):
                out.append((m.group(2), value))
    return out


def prop_apply(path: Path, translations: dict[str, str], opts) -> tuple[str | None, int]:
    text, _ = read_text(path)
    lines = text.splitlines()
    n = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith(("#", "!")):
            continue
        m = _PROP.match(line)
        if m and m.group(2) in translations:
            lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{_prop_escape(translations[m.group(2)])}"
            n += 1
    if not n:
        return None, 0
    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), n


HANDLERS = {
    ".json": (json_extract, json_apply),
    ".po": (po_extract, po_apply),
    ".pot": (po_extract, po_apply),
    ".csv": (csv_extract, csv_apply),
    ".properties": (prop_extract, prop_apply),
}


# ----------------------------------------------------------------------------- driver
def iter_files(src: Path):
    if src.is_file():
        yield src, Path(src.name)
    else:
        for p in sorted(src.rglob("*")):
            if p.is_file() and p.suffix.lower() in SUPPORTED:
                yield p, p.relative_to(src)


def cmd_extract(args) -> int:
    src = Path(args.src)
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2
    args.keys = set(args.keys.split(",")) if args.keys else None
    records = []
    for path, rel in iter_files(src):
        handler = HANDLERS.get(path.suffix.lower())
        if not handler:
            print(f"skip (unsupported): {rel}", file=sys.stderr)
            continue
        try:
            items = handler[0](path, args)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"skip ({type(exc).__name__}): {rel}", file=sys.stderr)
            continue
        for sid, source in items:
            records.append({"id": sid, "file": rel.as_posix(), "source": source, "target": ""})
    lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    if args.output:
        Path(args.output).write_text(lines, encoding="utf-8")
    else:
        sys.stdout.write(lines)
    print(f"extracted {len(records)} strings", file=sys.stderr)
    return 0


def load_table(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def cmd_apply(args) -> int:
    src, dest = Path(args.src), Path(args.output)
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2
    if src.resolve() == dest.resolve():
        print("refusing to write over the source. Choose a different -o destination.", file=sys.stderr)
        return 2
    args.keys = None
    args.min_len = 1
    by_file: dict[str, dict[str, str]] = {}
    for r in load_table(args.table):
        value = r.get(args.field) or ""
        if value.strip():
            by_file.setdefault(r["file"], {})[r["id"]] = value
    total = changed = 0
    for path, rel in iter_files(src):
        trans = by_file.get(rel.as_posix())
        if not trans:
            continue
        handler = HANDLERS.get(path.suffix.lower())
        new_text, n = handler[1](path, trans, args)
        if new_text is None:
            continue
        _, bom = read_text(path)
        target = dest / rel if src.is_dir() else (dest if dest.suffix else dest / rel)
        write_text(target, new_text, bom)
        total += n
        changed += 1
        print(f"wrote {target}  ({n} strings)", file=sys.stderr)
    print(f"applied {total} translations to {changed} file(s)", file=sys.stderr)
    return 0


def cmd_stats(args) -> int:
    rows = load_table(args.table)
    done = sum(1 for r in rows if (r.get("target") or "").strip())
    files = {}
    for r in rows:
        files.setdefault(r["file"], [0, 0])
        files[r["file"]][0] += 1
        files[r["file"]][1] += 1 if (r.get("target") or "").strip() else 0
    print(f"{done}/{len(rows)} translated ({(100 * done / len(rows)) if rows else 0:.1f}%)")
    for f, (total, d) in sorted(files.items()):
        print(f"  {d:>6}/{total:<6} {f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract")
    e.add_argument("src")
    e.add_argument("-o", "--output")
    e.add_argument("--keys", help="JSON only: comma-separated key names to keep (e.g. name,description,text)")
    e.add_argument("--min-len", type=int, default=1)
    e.add_argument("--key-col", help="CSV: column holding the string id (name or index, default 0)")
    e.add_argument("--source-col", help="CSV: column holding the source text (name or index, default 1)")
    e.set_defaults(func=cmd_extract)

    a = sub.add_parser("apply")
    a.add_argument("src")
    a.add_argument("table")
    a.add_argument("-o", "--output", required=True)
    a.add_argument("--field", default="target", help="table field holding the translation (default: target)")
    a.add_argument("--target-col", help="CSV: column to write translations into (created if missing)")
    a.add_argument("--key-col", help="CSV: column holding the string id")
    a.add_argument("--source-col", help=argparse.SUPPRESS)
    a.set_defaults(func=cmd_apply)

    s = sub.add_parser("stats")
    s.add_argument("table")
    s.set_defaults(func=cmd_stats)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
