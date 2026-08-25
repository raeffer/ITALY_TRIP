# Decisions

Dated log of decisions made in this repository and the reasoning behind them. Newest entries first. Append-only — each entry is a record of what was true at the time and is never rewritten or deleted, even after it's superseded.

## 2026-08-25 — "View Today's Places" / "View All Options" rebuilt from each day's `poi-legend`, showing every POI

User expected the overview map button to show every point of interest mentioned for the day, not just a curated 4-5 stop subset (which is what it had shown since the `maps/search`→`maps/dir` fix earlier the same day). Rebuilt the button on all 21 day pages to be generated from each page's `poi-legend` list (the numbered legend built for the day's orientation-map image, in `.route-map .poi-legend ol`), extracting every `<li>`'s `GPS:` coordinate in document order and building one `maps/dir/lat,lng/lat,lng/...` URL per day. This list is deliberately more complete than the content cards alone — it already includes the day's actual starting accommodation (from the previous day) and gives real, distinct coordinates for small food stops that content cards sometimes only had a partial address for.

Every day page's `poi-legend` was verified to have a 1:1 `<li>` count to `GPS:` count (4 to 23 stops per day) before generating from it, so no text-based geocoding fallback was needed anywhere — every stop is placed by exact coordinate, avoiding the Cittadella/Malta failure mode entirely for this pass.

Known risk, not yet tested: Google's non-API `maps/dir/` link has no documented hard cap on stop count, but its web UI is known to behave unreliably somewhere past ~10 stops. Several days now have well over that (Day 1 has 23). If a busier day's button truncates or misbehaves in testing, the fix is to split it into two buttons or trim to only "essential"/non-alternate stops — not to revert to a shorter curated list silently.

Day 19 (a free "choose your own" day with no single fixed route) uses "View All Options" as its equivalent button and was regenerated the same way, from its own `poi-legend`.

`print-all.html` and `print-stage3.html` regenerated via `scripts/build-print-all.py` from the updated day pages, per the same convention as the earlier fix.

## 2026-08-25 — Day 2's "Cittadella" stop fixed with GPS coordinates; site confirmed live via GitHub Pages

After the `maps/search` → `maps/dir` fix below, Day 2's button still resolved its "Cittadella" stop to *The Citadel, Victoria, Gozo, Malta* instead of Cittadella, Padova (a real walled town on the route) — Google's geocoder ranked the well-known Maltese landmark over the Italian town for the bare word "Cittadella," which is also the generic Italian word for "citadel." Appending `PD` as a region qualifier did **not** fix it — Google's per-segment matching still favored the Malta result by text similarity. The fix that worked: replace the name with the exact GPS coordinates already present elsewhere on the same page (`45.6507763,11.7832170`, from the Cittadella card), since a raw lat/lng pair is placed directly with no text geocoding involved.

Separately, debugging this surfaced that **the site is deployed live via GitHub Pages** at `https://raeffer.github.io/ITALY_TRIP/`, serving directly from the `main` branch (`gh api repos/raeffer/ITALY_TRIP/pages` → `build_type: legacy`, `source: {branch: main, path: /}`). The user was viewing that live site, not a local file, while these Cittadella fixes were still sitting as uncommitted local changes — so a first round of edits appeared to have no effect. Any fix intended for the user to see must be committed and pushed to `main` before it's visible; a local edit alone does not reach the live site.

## 2026-08-25 — "View Today's Places" / "View All Options" buttons switched from `maps/search` to `maps/dir` path format

User reported the "View Today's Places" button failed on the first two days tried (Day 1 and Day 2). Root cause: the button used `https://www.google.com/maps/search/?api=1&query=Place+A,+Place+B,+...` — Google's `search` action resolves the whole `query` value as **one** location, not a list. A comma-joined string of several unrelated place names across different towns generally fails to geocode; it only ever worked by luck on days with few, closely clustered stops.

Fix: rebuilt all 47 "View Today's Places" buttons and 3 "View All Options" buttons (across all 21 day pages plus the two generated print editions) using the path-based multi-stop format `https://www.google.com/maps/dir/Place+A/Place+B/Place+C/...`, where each stop is its own path segment and gets geocoded independently. This is the same mechanism the pre-existing, working "Navigate Route" buttons use (`maps/dir/?api=1&origin=...&destination=...&waypoints=...`), just without a fixed origin/destination split.

`print-all.html` and `print-stage3.html` were not hand-edited — the day pages were fixed first, then both print editions were regenerated via `scripts/build-print-all.py` (default args, and `--start 14 --end 21 --output print-stage3.html --title "Stage 3 Printable Edition"` respectively) per the usage documented in that script's docstring, so the print editions stay derived rather than drifting from the source day pages.

If day-page route sections are regenerated or hand-edited in the future, use the `maps/dir/A/B/C` path format for any "show all stops" link — not `maps/search/?api=1&query=A,B,C`, which silently fails for 3+ stops spanning different towns.

## 2026-08-24 — Printable-edition check linked live and made fail-closed

The active `.git/hooks/pre-commit` was an outdated copy of the tracked
`scripts/pre-commit-hook.sh`: it watched `style.css` instead of the real
`style-editorial.css` and still named the retired `STANDARDS.md`. The installer now
creates a live link to the tracked script, so later check fixes take effect without
another copy step. The tracked check also blocks the commit when Python, Beautiful
Soup, or lxml is unavailable instead of warning and allowing a stale
`print-all.html`.

Verified in disposable repositories: the installer created the expected link; a
change to the tracked script was immediately seen through that link; a simulated
missing-dependency path exited with status 1; and a staged `style-editorial.css`
change rebuilt and staged `print-all.html` successfully with the real dependencies.

Trade-off: a source-page, credits, or stylesheet commit cannot proceed on a machine
missing the rebuild dependencies. This favors a reliably current printable guide over
allowing the commit and relying on CI to repair it later.

## 2026-08-19 — Hand-patch style-editorial.css directly instead of adopting Paged.js for the print-pagination bugs

`print-all.html` (generated by `scripts/build-print-all.py` from the day pages) has three known bugs in `style-editorial.css`'s `@media print` block:

1. No forced break after `.hero` — Overview content bleeds onto the same page below the hero image.
2. `.inline-photo` has no `max-height`/`object-fit` cap and is `break-inside: avoid` — oversized photos get pushed whole to the next page, leaving large blank gaps on the page before.
3. No page-break rule tied to section identity — sections split across pages arbitrarily.

**Paged.js was evaluated and rejected** — tested by actually rendering PDFs, not just reasoning about it. It fixed neither bug out of the box, broke the existing `file://`-based workflow (the polyfill needs http(s), not `file://`, due to an internal CORS-blocked XHR), would have required a new Node/npm/Puppeteer dependency this repo doesn't otherwise have, and introduced new regressions in `.poi-legend` and `.mosaic-grid` (both CSS Grid) — one wasted ~55% of a page, the other silently dropped an inline image. Decision: hand-patch `style-editorial.css` directly instead.

Note: this reasoning was first recorded in `build-status.md` on 2026-08-19 (commit `13d4308`) as part of a single commit that added the whole file; the exact date the Paged.js evaluation itself took place is not separately documented, so 2026-08-19 (the recording date) is used here as the best available date.

For current status of the hand-patch itself, see `build-status.md`.
