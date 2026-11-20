#!/usr/bin/env python3
"""Snapshot, verify and restore game files so every modification is reversible.

Usage:
    backup.py snapshot <game_dir> <backup_dir> --paths rel/path1 rel/path2 ...
    backup.py verify   <backup_dir>             # are the backed-up files intact?
    backup.py restore  <backup_dir> [--game-dir DIR]
    backup.py info     <backup_dir>

Paths that do not exist yet are recorded as "new" and are deleted again on restore.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = "manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_rel(rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        raise SystemExit(f"unsafe path (must be relative, no '..'): {rel}")
    return p


def snapshot(game_dir: Path, backup_dir: Path, paths: list[str]) -> None:
    if not game_dir.is_dir():
        raise SystemExit(f"game dir not found: {game_dir}")
    if (backup_dir / MANIFEST).exists():
        raise SystemExit(f"{backup_dir} already holds a snapshot. Use a new folder (never overwrite a backup).")
    entries = []
    for rel in paths:
        r = safe_rel(rel)
        src = game_dir / r
        if src.is_file():
            dst = backup_dir / "files" / r
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            entries.append({"path": r.as_posix(), "existed": True, "sha256": sha256(src), "size": src.stat().st_size})
        elif src.exists():
            raise SystemExit(f"not a regular file: {rel}")
        else:
            entries.append({"path": r.as_posix(), "existed": False})
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "game_dir": str(game_dir.resolve()),
        "files": entries,
    }
    (backup_dir / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    kept = sum(1 for e in entries if e["existed"])
    print(f"snapshot ok: {kept} file(s) saved, {len(entries) - kept} marked as new -> {backup_dir}")


def load(backup_dir: Path) -> dict:
    mf = backup_dir / MANIFEST
    if not mf.exists():
        raise SystemExit(f"no {MANIFEST} in {backup_dir}")
    return json.loads(mf.read_text(encoding="utf-8"))


def verify(backup_dir: Path) -> bool:
    ok = True
    for e in load(backup_dir)["files"]:
        if not e["existed"]:
            continue
        f = backup_dir / "files" / e["path"]
        if not f.exists() or sha256(f) != e["sha256"]:
            print(f"CORRUPT/MISSING backup: {e['path']}")
            ok = False
    print("backup intact" if ok else "backup damaged")
    return ok


def restore(backup_dir: Path, game_dir: Path | None) -> None:
    manifest = load(backup_dir)
    if not verify(backup_dir):
        raise SystemExit("refusing to restore from a damaged backup")
    target = game_dir or Path(manifest["game_dir"])
    restored = removed = 0
    for e in manifest["files"]:
        dst = target / safe_rel(e["path"])
        if e["existed"]:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_dir / "files" / e["path"], dst)
            restored += 1
        elif dst.exists():
            dst.unlink()
            removed += 1
    print(f"restore ok: {restored} file(s) restored, {removed} added file(s) removed in {target}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("game_dir")
    s.add_argument("backup_dir")
    s.add_argument("--paths", nargs="+", required=True)
    for name in ("verify", "info"):
        sub.add_parser(name).add_argument("backup_dir")
    r = sub.add_parser("restore")
    r.add_argument("backup_dir")
    r.add_argument("--game-dir")
    args = ap.parse_args()

    if args.cmd == "snapshot":
        snapshot(Path(args.game_dir), Path(args.backup_dir), args.paths)
    elif args.cmd == "verify":
        return 0 if verify(Path(args.backup_dir)) else 1
    elif args.cmd == "info":
        print(json.dumps(load(Path(args.backup_dir)), indent=2))
    else:
        restore(Path(args.backup_dir), Path(args.game_dir) if args.game_dir else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
