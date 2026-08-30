## A Note on What Belongs Here

This file documents facts about the PROJECT ITSELF — content rules, design system, file structure, project history — that stay true no matter which AI tool or app someone uses to work on it. It should NOT contain instructions specific to one app or interface (e.g. how to configure a particular tool's settings, that tool's bugs or workarounds). If a note is really about troubleshooting a specific app rather than the project, it doesn't belong in this file.

## Content Philosophy
- This is a decision-making travel companion, not a guidebook — practical, honest, for reading in a moving car.
- Every day follows this structure: Theme, Overview (with a routing note checking what's actually on the road between stops, not just the destination), Stops, Coffee, Pasticceria, Lunch/Dinner, Local Speciality, What to Buy, Hidden Gem, Cool/Interesting/Quirky, Accommodation, If Time Is Tight, If You've Got Half a Day, Skip It, Today's Winners, Road Trip Score.
- Sourcing priority: Italian tourism sites, comune/Pro Loco sites, Slow Food, Gambero Rosso, Italian food writers first. English-language sites only to sanity-check major attractions aren't missed.
- Honesty over polish: flag mixed reviews, closures on the actual travel date, genuine gaps (e.g. "no real $$$ option exists here"), and conflicting information rather than forcing a confident-sounding but shaky recommendation.
- "Cool, Interesting & Quirky" is a menu to browse, not a mandatory itinerary — use what fits the day.
- The "how did you find this?" bar applies to every section, not just Hidden Gem. Coffee, Lunch, Dinner, What to Buy, and even Stops themselves must be researched with the same standard: check for a genuinely unusual, authentic, or surprising option before defaulting to the obvious/famous pick. "No standout option here, go with something simple" is not an acceptable default — if the research genuinely turns up nothing unusual, say so explicitly and explain why, rather than quietly settling for generic.
- Any edit to CONTENT.md must be mirrored in the corresponding day's HTML page in /days/ in the same pass — CONTENT.md is the source of research, but the live site is what the user actually sees, and the two must not be allowed to drift out of sync.
- This is enforced by a git pre-commit hook (`scripts/pre-commit-hook.sh` — run `scripts/install-hooks.sh` once per local clone to activate it). The installer creates a live link, not a copy, so the active check stays matched to the tracked script. If a commit is blocked by this hook, fix the missing HTML sync rather than bypassing it — do not use `git commit --no-verify` unless the user has explicitly confirmed this is a genuine one-off exception. At the start of any session doing repo work, check that `.git/hooks/pre-commit` links to `scripts/pre-commit-hook.sh`; if not, run `scripts/install-hooks.sh`.

## Photo Standards
- Only Creative Commons / properly licensed photos (Wikimedia Commons primarily), always with photographer name and license credited in credits.html.
- MANDATORY before using any photo: actually open and view the image itself to confirm it shows the real, recognizable subject — not a texture, crop, or unrelated detail (this was learned after a "Guaita Tower" photo turned out to be a close-up of a door).
- Every day page must include a minimum of 3 inline images integrated naturally throughout the content.
- Every day page must include a minimum of 3 gallery images at the end of the page.
- Every day page must include at least one food or drink image, tied directly to that day's Coffee, Pasticceria, Local Speciality, What to Buy, Lunch, or Dinner content.
- Gallery images should be different from the inline images wherever practical.
- Images must relate directly to locations, food, experiences, or quirky points of interest featured on that day's itinerary.
- Prioritize variety across the page, including where appropriate: local food, local life, quirky details, architecture, scenery, viewpoints, and cultural experiences.
- Avoid pages consisting primarily of panoramas or exterior building shots.
- Images should enhance the storytelling and decision-making value of the guide, not simply decorate it.
- The end-of-day photo-finale section must show completely different subject matter than anything pictured inline earlier on that same page wherever practical — no repeats of the same subject, even as a different image of it.
- Avoid repeating the same specific photo subject anywhere in the whole document, even on different days. Use variety at the subject level, not just different filenames or angles: for example, do not use more than one trabocco photo in the document, and do not use the same food more than once. Different sea structures, different dishes, different streets, different buildings, and different landscapes are fine; the same recognisable subject category repeated is not.
- All credits consolidated in one credits.html page for the whole site, not repeated per day.

## Hero Image Standard
- Hero images must display consistently and professionally across desktop, tablet, phone, and printed output.
- Every day page hero must use the shared hero container structure and shared dimensions defined in the project stylesheet.
- Hero images must completely fill the hero container with `width: 100%`, `height: 100%`, `object-fit: cover`, and `display: block`.
- Hero images must never be stretched or distorted, and must not leave blank or uncovered areas.
- Do not rely on the intrinsic dimensions of the source image to determine the displayed hero height.
- Use a consistent desktop hero aspect ratio across all day pages.
- Define appropriate responsive hero proportions or heights for tablet and phone layouts.
- Preserve a suitable and consistent hero proportion in the print stylesheet.
- Do not use the same centred crop automatically for every image. Inspect each hero image individually and set an appropriate `object-position` so the important subject remains visible at desktop, tablet, and phone widths.
- Page-specific focal positioning should be implemented through a maintainable hook such as a CSS custom property, class, or data attribute rather than duplicated hero CSS.
- Replace a hero image only when the important subject cannot be retained satisfactorily across desktop, tablet, phone, and print crops because of excessive empty space, poor composition, an edge-positioned subject, or insufficient resolution.
- Any replacement hero image must depict a location, subject, or experience included in that day's itinerary; comply with the Wikimedia Commons image requirements above; be suitable for responsive hero cropping; have sufficient resolution; use the project's existing image conventions; and be added to credits.html with complete attribution.

## Design System
- Typography: Fraunces (headers), Inter (body), IBM Plex Mono (GPS/data/meta lines).
- Color palette: Positano-inspired — royal blue, bright azure, red-orange, olive-lime, bright gold/yellow, warm off-white background. Palette can shift per region/day as long as the same card-coding logic and type system stay consistent.
- Card border color-coding: gold border = primary/best pick, yellow border = alternate, coral/red-orange border = budget option.
- Recurring "tessera" (mosaic tile) motif as small colored square accents — a nod to Ravenna's mosaic identity, carried through as the visual signature across all days.
- Full-bleed color bands (hero, photo-finale) must have zero side padding/margin at any screen width — content cards keep their own comfortable padding.

## Technical Requirements
- Must work well on: desktop browser, tablet (portrait & landscape), phone, and printed/bound hard copy (via Officeworks).
- Responsive: viewport meta tag required on every page; CSS reset (html, body { margin: 0; padding: 0; }) to prevent stray browser-default margins.
- Print: @page rule for A4 with 10mm left margin (binding gutter) and 5mm on the other three sides, matching Officeworks' bound-document specs. Keep bold colors for print (flat-rate color printing, ink coverage isn't a cost factor).
- File structure: shared /style-editorial.css used by all pages, one file per day in /days/dayN.html, root /index.html linking to all days, root /credits.html for all photo credits.

## Route Maps and POI Standard
- Route maps exist to help the traveller understand the day at a glance. They are not navigation tools.
- A traveller should be able to understand the overall shape of the day within five seconds of looking at the map.
- The map should communicate the start location, destination, recommended route, optional route(s), major geographical relationships, and all POIs.
- The map should not attempt to replace a live navigation app.
- Design priorities, in order: clarity, geographic accuracy, readability in print, consistency across all days, visual appeal.
- If there is a conflict between completeness and readability, preserve readability by using numbered markers and the legend rather than adding labels or other clutter.
- Every day must include a real geographic orientation map derived from real map data, not a schematic substitute.
- Map assets must be generated at sufficient pixel density for their maximum desktop and print display size. Generated raster maps should normally use at least 2x output density relative to their intended layout size, and pages must display them at the intended CSS dimensions so browsers downsample rather than enlarge them.
- Maps must never be enlarged beyond their intended effective resolution. Route lines, POI markers, leader lines, marker numbers, map titles, attributions, and route legends must remain crisp on large desktop screens and in A4 print/PDF output.
- Route overlays must be rendered with antialiased strokes, rounded caps, and rounded joins. If the generator produces raster maps, route lines should be drawn on a higher-resolution overlay and downsampled with a high-quality filter before compositing so bends and dashed segments do not appear jagged or blocky.
- Generated map UI must use the project's editorial palette, not bright generic GIS colours. Use named palette constants in the generator for route roles, POI marker roles, marker borders, legend panels, legend text, leader lines, and attribution so future maps automatically match the Italy Road Trip Companion visual system.
- The map is for orientation only. Organic Maps links/buttons provide the primary POI and routing experience. Smaller Google Maps fallback links must remain available for devices without Organic Maps and for traffic-aware routing.
- Every POI included in that day's visible content must appear on the map. Do not omit cafés, restaurants, shops, historic sites, parking, accommodation, viewpoints, beaches, optional stops, or other named practical stops merely to reduce map clutter.
- POIs must use compact numbered markers rather than full text labels on the map. Do not place full POI names directly on the map.
- Prefer rounded-square numbered markers for generated bitmap maps, because they keep single- and double-digit numbers centered and avoid ragged small-circle edges in print.
- When many POIs belong to one dense stop or walking core, group them as a clean chronological marker stack, grid, or inset connected to one geographic anchor. Avoid fan-shaped leader-line bursts, many crossing lines, overlapping markers, or a line running behind the numbered markers.
- Clustering is permitted only for genuinely close POIs. It must not conceal meaningful geographic separation: different towns, route endpoints, optional-route destinations, and major destinations must be shown individually at or immediately adjacent to their real locations. Geographic accuracy takes priority over visual neatness, while readability takes priority over forcing every marker directly onto the same small area.
- The numbered markers in the legend must visually match the marker colors used on the map.
- Every numbered marker must have exactly one matching legend entry beneath the map, and every legend entry must correspond to a visible marker.
- Every legend entry must include the marker number, POI name, POI type, practical navigation address, and verified decimal GPS coordinates.
- Coordinates must identify the practical arrival point a traveller should use, such as the entrance, parking lot, trailhead, reception, public viewpoint access, or other navigable arrival point. Do not use a town centroid or generic building centroid when a more practical arrival point is available.
- Every new or modified POI must be independently verified before the page is considered complete.
- Preferred verification sources, in order:
  1. Official venue website
  2. Official tourism website
  3. Official municipal website
  4. OpenStreetMap object data
  5. Other reputable mapping sources only if necessary
- Do not rely solely on previously stored coordinates, old page content, or earlier generated map data when adding or modifying POIs.
- Every page must validate that every POI appears on the map, every POI appears in the legend, numbering is unique, marker and legend numbering match, addresses are complete, coordinates are verified, Organic Maps links use those verified coordinates where available, and Google Maps fallback links continue to function.
- The reusable map generator configuration for each POI should store, at minimum, number, name, latitude, longitude, address, type, optional status where relevant, and verification/source notes sufficient for later audit.

## Printable Edition (print-all.html)
- print-all.html is a **generated file** — built by scripts/build-print-all.py by stitching together days/day1.html through days/day21.html (the full 21-day trip) and credits.html into one continuous, print-ready document. Never hand-edit it; edit the source day pages/credits.html instead and regenerate.
- It is auto-regenerated locally by the pre-commit hook (`scripts/pre-commit-hook.sh`) whenever a day page, `credits.html`, or `style-editorial.css` is staged for commit — the hook rebuilds and stages it. If Python, Beautiful Soup, or lxml is unavailable, the commit is blocked rather than allowing a stale `print-all.html`.
- As a backstop, it is also rebuilt in CI by .github/workflows/build-print-all.yml on every push to main that touches those same files, in case someone commits with `--no-verify` or without the hook installed; CI pushes a follow-up commit if the rebuilt file differs.
- scripts/build-print-all.py also accepts `--start`/`--end`/`--output`/`--title` flags to build a partial edition covering a specific day range without touching print-all.html — print-stage3.html (Days 14–21 only) is generated this way. Unlike print-all.html, partial editions are not auto-regenerated by the hook or CI; rebuild them manually after editing an affected day page.
- index.html links to it from the site footer as "Printable Edition (all days)".

## Known Issues / History
- GitHub Pages build source must be on the "main" branch specifically (an earlier mismatch with "master" caused the live site to show a blank placeholder for a while).
