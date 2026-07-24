#!/usr/bin/env bash
#
# Pre-commit hook: enforce that any edit to CONTENT.md is accompanied,
# in the same commit, by an edit to the corresponding day's HTML page.
#
# How it detects "which day changed":
#   It looks at the staged diff of CONTENT.md and finds every "Day N ---"
#   header line that appears within the changed hunks (added or removed
#   context lines near a change). That gives the set of day numbers whose
#   section was touched. It then checks that days/dayN.html is also staged.
#
# Install: copy this file to .git/hooks/pre-commit and `chmod +x` it.
# (Git hooks are local-only, so this must be installed by each person who
#  commits, or set up via git config core.hooksPath — see install notes.)

set -euo pipefail

# --- Auto-regenerate print-all.html ---------------------------------------
# If any source that print-all.html is built from is staged, rebuild it and
# stage the result, so print-all.html can never go stale in a commit.
PRINT_SOURCES_CHANGED=$(git diff --cached --name-only | grep -E '^(days/day[0-9]+\.html|credits\.html|style\.css)$' || true)

if [ -n "$PRINT_SOURCES_CHANGED" ]; then
  if command -v python3 >/dev/null 2>&1 && python3 -c "import bs4, lxml" >/dev/null 2>&1; then
    python3 scripts/build-print-all.py
    git add print-all.html
    echo "print-all.html regenerated and staged (source changed: $(echo "$PRINT_SOURCES_CHANGED" | tr '\n' ' '))"
  else
    echo ""
    echo "WARNING: day page(s)/credits.html/style.css changed but print-all.html"
    echo "could not be regenerated (missing python3 or bs4/lxml)."
    echo "Install with: pip install beautifulsoup4 lxml --break-system-packages"
    echo "print-all.html may now be stale relative to this commit."
    echo ""
  fi
fi
# ----------------------------------------------------------------------------

CONTENT_FILE="CONTENT.md"

# Only run if CONTENT.md is actually staged for this commit.
if ! git diff --cached --name-only | grep -qx "$CONTENT_FILE"; then
  exit 0
fi

# Get the staged diff of CONTENT.md with line numbers, so we can map
# changed lines back to which "Day N" section they fall under.
DIFF_OUTPUT=$(git diff --cached -U0 -- "$CONTENT_FILE" || true)

if [ -z "$DIFF_OUTPUT" ]; then
  exit 0
fi

# Get the full staged version of CONTENT.md so we can find day headers
# and their line ranges.
STAGED_CONTENT=$(git show :"$CONTENT_FILE" 2>/dev/null || cat "$CONTENT_FILE")

# Build a list of (line_number, day_number) for every "Day N ---" header
# in the staged version of the file.
declare -a HEADER_LINES=()
declare -a HEADER_DAYS=()

line_num=0
while IFS= read -r line; do
  line_num=$((line_num + 1))
  # Matches headers like: # **Day 10 --- Something**
  if [[ "$line" =~ Day[[:space:]]+([0-9]+)[[:space:]]*---  ]]; then
    day_num="${BASH_REMATCH[1]}"
    HEADER_LINES+=("$line_num")
    HEADER_DAYS+=("$day_num")
  fi
done <<< "$STAGED_CONTENT"

if [ "${#HEADER_LINES[@]}" -eq 0 ]; then
  echo "WARNING: pre-commit hook could not find any 'Day N ---' headers in $CONTENT_FILE."
  echo "Skipping the CONTENT.md/HTML sync check (nothing to map changes to)."
  exit 0
fi

# Parse the diff to find which line numbers in the NEW file were touched.
# Using `git diff -U0` hunk headers: @@ -a,b +c,d @@
declare -a CHANGED_LINES=()
while IFS= read -r hunk_line; do
  if [[ "$hunk_line" =~ ^@@\ -[0-9]+(,[0-9]+)?\ \+([0-9]+)(,([0-9]+))?\ @@ ]]; then
    start="${BASH_REMATCH[2]}"
    count="${BASH_REMATCH[4]:-1}"
    for ((i=0; i<count; i++)); do
      CHANGED_LINES+=($((start + i)))
    done
  fi
done <<< "$DIFF_OUTPUT"

if [ "${#CHANGED_LINES[@]}" -eq 0 ]; then
  # CONTENT.md was staged but diff shows no line changes (e.g. rename only)
  exit 0
fi

# For each changed line, find which day section it falls in (the last
# header whose line number is <= the changed line number).
declare -A TOUCHED_DAYS=()

for changed_line in "${CHANGED_LINES[@]}"; do
  best_day=""
  for idx in "${!HEADER_LINES[@]}"; do
    if [ "${HEADER_LINES[$idx]}" -le "$changed_line" ]; then
      best_day="${HEADER_DAYS[$idx]}"
    else
      break
    fi
  done
  if [ -n "$best_day" ]; then
    TOUCHED_DAYS["$best_day"]=1
  fi
done

if [ "${#TOUCHED_DAYS[@]}" -eq 0 ]; then
  exit 0
fi

# Now check that each touched day's HTML file is also staged.
STAGED_FILES=$(git diff --cached --name-only)

MISSING_DAYS=()
for day in "${!TOUCHED_DAYS[@]}"; do
  html_path="days/day${day}.html"
  if ! echo "$STAGED_FILES" | grep -qx "$html_path"; then
    MISSING_DAYS+=("$day")
  fi
done

if [ "${#MISSING_DAYS[@]}" -gt 0 ]; then
  echo ""
  echo "COMMIT BLOCKED: CONTENT.md changes detected for Day(s): ${MISSING_DAYS[*]}"
  echo "but the matching HTML page(s) were not staged in this commit:"
  for day in "${MISSING_DAYS[@]}"; do
    echo "  - days/day${day}.html"
  done
  echo ""
  echo "Per STANDARDS.md: 'Any edit to CONTENT.md must be mirrored in the"
  echo "corresponding day's HTML page in the same pass.'"
  echo ""
  echo "Fix: update the listed HTML file(s) to match, then 'git add' them"
  echo "before committing again."
  echo ""
  echo "To bypass in a genuine exception (e.g. CONTENT.md-only research"
  echo "notes with no HTML page yet), commit with:"
  echo "  git commit --no-verify"
  echo ""
  exit 1
fi

exit 0
