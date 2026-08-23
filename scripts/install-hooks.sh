#!/usr/bin/env bash
# Run this once after cloning the repo to activate the CONTENT.md/HTML sync check.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_DIR="$(git rev-parse --git-dir)/hooks"
HOOK_SOURCE="$REPO_ROOT/scripts/pre-commit-hook.sh"

mkdir -p "$HOOK_DIR"
chmod +x "$HOOK_SOURCE"
ln -sfn "$HOOK_SOURCE" "$HOOK_DIR/pre-commit"

echo "Pre-commit hook linked to scripts/pre-commit-hook.sh."
echo "CONTENT.md edits require matching day HTML, and print-all.html is rebuilt from changed sources."
