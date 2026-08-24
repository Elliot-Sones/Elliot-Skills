#!/usr/bin/env bash
# Link all skills from one section (learning|engineering|finance) into a target project.
# Usage: ./install.sh <section> [/path/to/project]   (target defaults to current dir)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECTION="${1:?usage: ./install.sh <section> [target]}"
TARGET="${2:-$PWD}"
[ -d "$REPO/$SECTION" ] || { echo "no such section: $SECTION" >&2; exit 1; }
mkdir -p "$TARGET/.claude/skills"
n=0
for s in "$REPO/$SECTION"/*/; do
  [ -f "$s/SKILL.md" ] || continue
  ln -sfn "${s%/}" "$TARGET/.claude/skills/$(basename "$s")"
  echo "linked: $(basename "$s") -> $TARGET/.claude/skills/"
  n=$((n+1))
done
[ "$n" -gt 0 ] || echo "section $SECTION has no skills yet"
