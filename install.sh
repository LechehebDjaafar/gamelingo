#!/usr/bin/env bash
# Install GameLingo skills into ~/.claude/skills (personal, all projects).
set -euo pipefail
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DEST"
for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "$DEST/$name"
  cp -R "$d" "$DEST/$name"
  echo "installed: $name"
done
echo "Done. Restart Claude Code, then try: /gamelingo"
echo "Optional (Arabic/RTL): python3 -m pip install -r \"$HERE/requirements-rtl.txt\""
