#!/usr/bin/env bash
# Run this once after cloning the repo to activate the CONTENT.md/HTML sync check.
HOOK_DIR="$(git rev-parse --git-dir)/hooks"
cp scripts/pre-commit-hook.sh "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-commit"
echo "Pre-commit hook installed: CONTENT.md edits now require a matching day HTML edit in the same commit."
