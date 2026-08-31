# Build status

Read this first, before doing anything else. It says where we are in the Italy Road Trip Companion repository and what to do next. Updated at the end of every session, right before stopping, so a new session can pick up without being re-briefed.

**Last updated:** 2026-08-31

**Currently on:** The 21 daily Organic Maps bookmark imports and stable route legs are complete. A full coordinate-quality audit has corrected the suspect arrivals and replaced one demolished venue. The next map task is a single all-trip KML import, followed by current-location navigation from each POI link; print-pagination remains open after that (see Open Items below).

## Repository purpose

A 21-day Italy road trip companion site — one static HTML page per day (`days/dayN.html`), a shared stylesheet, a generated printable edition, and a single photo-credits page. The trip is presented in three stages (see `index.html` for the live grouping):

## Work done

- **`poi-legend` names are hyperlinked** to the fuller write-up about that POI
  elsewhere on the same day page, across all 21 days. Content cards
  (`<div class="name">`) got slug ids; legend entries link to them where a
  match exists, and are left as plain text where no dedicated card exists for
  that name (verified case by case, not just link-count checked). See
  `decisions.md`, 2026-08-26.
- **Organic Maps provides POI-visible navigation, with Google complete-route fallbacks:**
  all 21 days provide a downloadable KML bookmark collection generated from
  the numbered POI legend (301 bookmarks total). The user confirmed on Android
  that imported bookmarks remain visible while a stable Organic Maps two-point
  route is active. Each of the 34 existing route choices is therefore also
  available as explicit Organic Maps legs (100 links total) inside a collapsed
  section, preserving every ordered stop without using the unsupported v2 API.
  The original Google complete-route buttons remain visible as fallbacks. The
  21 overview buttons and 96 individual POI pin links remain unchanged. See
  `decisions.md`, 2026-08-31, 2026-08-30 and 2026-08-25.
- **All 301 POI coordinates passed a source-quality and cross-output audit:**
  37 suspect arrivals were corrected, replaced, or separated using current
  official addresses, named OpenStreetMap objects, and independent GPS sources.
  Major fixes include Trabocco Pesce Palombo (the old pin was about 2.3 km
  away), Vieste venues that had inherited a castle/old-town anchor, Lecce's
  Cartapesta workshop, and numerous food/accommodation storefronts. The
  demolished Caffè Pasticceria Mimì stop was replaced with current registered
  Africanetti producer Magic Pasticcio. Pasticceria Bolcato and Dolce Bassano
  are now separate businesses, bringing the total from 300 to 301. Automated
  validation confirms that generator data, all 21 KML files, all 21 aggregate
  Organic Maps links, and all page-legend GPS values agree. Two small Termoli
  storefronts remain honest street-address arrivals because no trustworthy
  doorway coordinate exists; broad destinations such as the Sassi remain
  deliberately labelled area anchors. See `decisions.md`, 2026-08-31.
- **Site is live via GitHub Pages** at `https://raeffer.github.io/ITALY_TRIP/`,
  serving directly from `main`. A local edit is not visible to the user until
  it is committed and pushed to `main` — check this before reporting any fix
  as done.
- **Printable-edition enforcement:** `scripts/install-hooks.sh` now installs
  `.git/hooks/pre-commit` as a live link to the tracked
  `scripts/pre-commit-hook.sh`, eliminating stale local copies. The hook watches the
  real stylesheet (`style-editorial.css`) and blocks a commit if `print-all.html`
  cannot be regenerated. Verified in disposable repositories against both successful
  regeneration and a missing-dependency failure on 2026-08-24.
- **CONTENT-to-page enforcement uses the real Stage 2 numbering:**
  `CONTENT.md` local Days 1–10 map to full-trip pages 4–13, so the pre-commit
  sync check now applies the required `+3` offset instead of demanding
  unrelated pages. The check remains fail-closed.
- **Stage 1 — The Fixed Leg (Days 1–3, 10–12 Sept 2026):** Venice Marco Polo → Santorso → Bassano del Grappa → San Giovanni in Persiceto/Vignola. Built (`days/day1.html`–`day3.html`).
- **Stage 2 — The Adriatic Coast (Days 4–13, 13–22 Sept 2026):** Ravenna through the Adriatic coast to the San Vito dei Normanni arrival — the original road trip. Built (`days/day4.html`–`day13.html`).
- **Stage 3 — Puglia villa week & Rome finale (Days 14–21, 23–30 Sept 2026):** Built (`days/day14.html`–`day21.html`). Day-by-day research, corrections, and open gaps for these days live in `STAGE3_CONTENT.md`.

All 21 day pages are committed and pushed to `main` (Stage 3 landed in `5648118`), and `print-all.html` covers the full set. Check `git log`/`git status` before assuming this is still current.

## Open Items

### Single all-trip POI import (next implementation)

Build one downloadable KML containing all 301 audited POIs so the traveller
can import the whole itinerary into Organic Maps once at the start of the trip.
Keep the 21 daily KML files as smaller recovery/re-import options. Duplicate
start/end anchors may be retained if their day context is useful, but bookmark
names must include enough day context to prevent ambiguous duplicates.

### Current-location POI navigation (discussion next)

The user wants every POI in the document to have a hot link that starts
navigation from wherever the traveller currently is. This is not part of the
route-leg rollout and must be discussed before implementation because the
stable Organic Maps v1 route API requires an explicit start coordinate; its
tested pin links can open the destination but still require the user to tap
"Route to" inside Organic Maps. Do not silently substitute the unsupported v2
`currentLocation` route format that failed on the user's installed app.

### Print-pagination fix (in progress)

`print-all.html` (generated by `scripts/build-print-all.py` from the day pages) has three known bugs in `style-editorial.css`'s `@media print` block:

1. No forced break after `.hero` — Overview content bleeds onto the same page below the hero image.
2. `.inline-photo` has no `max-height`/`object-fit` cap and is `break-inside: avoid` — oversized photos get pushed whole to the next page, leaving large blank gaps on the page before.
3. No page-break rule tied to section identity — sections split across pages arbitrarily.

Verified against the current `@media print` block in `style-editorial.css` on 2026-08-20: none of the three fixes are present yet — the hand-patch has not been applied. Check the actual `@media print` block before assuming this is done; don't trust this note once work on it starts.

The plan is to hand-patch `style-editorial.css` directly (Paged.js was evaluated and rejected — see `decisions.md`, 2026-08-19, for the reasoning).
