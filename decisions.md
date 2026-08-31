# Decisions

Dated log of decisions made in this repository and the reasoning behind them. Newest entries first. Append-only — each entry is a record of what was true at the time and is never rewritten or deleted, even after it's superseded.

## 2026-08-31 — Import all 301 POIs once, while retaining daily recovery files

The user chose a one-time full-itinerary bookmark import instead of repeating the import at the start of every day. The index now provides `assets/maps/italy-trip-all-pois.kml`, built directly from the 21 audited daily KML files. Its 301 bookmark names are prefixed with the full-trip day and daily marker number (for example, `D07-12 — Trabocco Pesce Palombo`) so repeated accommodation, arrival, and town names remain distinguishable inside one Organic Maps bookmark collection.

The combined file is deliberately flat rather than nested into 21 KML folders. This gives up folder-based day grouping in exchange for the simplest import structure—the same flat placemark structure already proven on the user's Android phone—and avoids depending on how Organic Maps interprets nested KML folders. The day prefix supplies the grouping context in every search result and bookmark label.

The 21 daily KML files remain available as smaller recovery or selective re-import options. `scripts/build-all-pois-kml.py` generates the combined file deterministically, validates the expected 301-entry total, and the pre-commit hook regenerates and stages it whenever a daily KML or its generator changes. A separate verification confirmed valid XML, 301 unique names, and exact ordered coordinate agreement with all daily sources.

## 2026-08-31 — CONTENT-to-site sync check respects the Stage 2 day offset

The coordinate-audit commit was correctly accompanied by edits to the matching live pages, but the pre-commit hook demanded the wrong files: for example, a change under `CONTENT.md` Day 4 (the fourth day of Stage 2) demanded `days/day4.html` instead of the actual full-trip page, `days/day7.html`. `CONTENT.md` covers Stage 2 as local Days 1–10, while the site numbers them as full-trip Days 4–13.

The hook now adds the required three-day offset before checking staged HTML files. The content-sync requirement remains fail-closed; only its mapping to the real page topology changed. Bypassing the hook or staging unrelated pages merely to satisfy it was rejected because either would conceal the underlying enforcement bug.

## 2026-08-31 — POI coordinate audit uses real arrivals, not invented precision

Audited all itinerary POIs after the user asked for deep research into missing coordinates. Every entry already had numbers, but 37 were suspect because they were town centres, shared landmarks, street segments, or stale business locations rather than dependable arrivals. Corrected or replaced those records using current official addresses first, then named OpenStreetMap objects or independent GPS sources. Generator data, all daily KMLs, aggregate Organic Maps links, and page legends must carry the same coordinate; an automated cross-output check now passes for all 301 POIs.

Do not invent doorway precision where the evidence only supports an address-level arrival. Friggitoria Maramimmo and Roberti Store therefore remain explicitly described as Termoli street-address arrivals. Broad destinations such as Rione Monti and the Sassi remain intentional area anchors, while named buildings and businesses use building/storefront coordinates where supported.

The audit also found two data-quality problems that coordinate checks alone would have missed. Caffè Pasticceria Mimì's former premises were demolished, so the stop was replaced by Magic Pasticcio, a current registered Africanetto di Persiceto producer. Pasticceria Bolcato and Dolce Bassano are separate businesses at separate addresses, so the previously merged entry was split; this raises the itinerary total from 300 to 301 POIs. The trade-off is one additional bookmark and a few deliberately less precise address-level pins, in exchange for never sending the traveller confidently to the wrong place.

## 2026-08-31 — Imported bookmarks and stable Organic Maps route legs rolled out to all 21 days

The user confirmed on the real Android phone that Day 12's imported KML bookmarks remained visible when the stable Trani-to-Bari Organic Maps route was opened. This solves the POI-visibility problem that neither Google Maps nor Organic Maps' ordinary driving style solved: the guide's points are persistent bookmarks, not native POIs that the navigation style can hide.

Rolled the confirmed pattern out across the full trip. Each day now has a downloadable KML collection generated in the same order from its numbered POI legend, for 300 bookmark placemarks across 21 files. Each of the 34 existing Google route choices is mirrored inside a collapsed Organic Maps section as stable two-point legs, for 100 leg links total. The leg sequences, route modes, and stop order come from the existing complete-route buttons; name-based stops are resolved to the verified coordinates already stored in the same day's guide, and coordinate-based stops retain their exact coordinates. The unsupported `/v2/dir` and `/v2/nav` formats are not used.

This gives up single-tap multi-stop navigation in Organic Maps: after reaching a stop, the traveller must return to the guide and open the next leg. That extra tap is accepted because it preserves every ordered stop, keeps the 300 guide POIs visible, and works in the installed stable app. The original Google complete-route buttons remain visible fallbacks for traffic and one-link whole-route navigation. The existing Organic Maps overview and individual pin links also remain available.

## 2026-08-31 — Test imported Day 12 bookmarks as the POI-visible navigation workaround

The stable Organic Maps two-point route link successfully opened the Trani-to-Bari route on the user's Android phone, but starting the driving route still hid the ordinary POIs. This is caused by Organic Maps' simplified vehicle-navigation map style, so changing the route URL cannot restore the rich native POI layer.

The user approved a second Day 12 pilot: import the day's 20 numbered POIs once as a KML bookmark list, then open the same stable Organic Maps route. Imported bookmarks are persistent map overlays rather than ordinary POIs and may therefore remain visible in the simplified navigation style. Day 12 provides the download and route as an explicit two-step test while retaining every existing Google route button. Do not roll this out to the other days until the user confirms on the real phone that the imported bookmark pins remain visible during active navigation. If confirmed, the stable route format still requires multi-stop days to be split into individual legs.

## 2026-08-30 — Organic Maps v2 route rollout reverted after stable-app failure; POIs remain Organic Maps, routes return to Google

The user tested a deployed route link on their Android phone. Organic Maps opened but displayed “Loading Bookmarks — The file type is not recognized by the app” and showed the full `https://omaps.app/v2/dir?...` URL. This proves the stable installed app does not recognize the v2 route format. The format appears in Organic Maps' current development API documentation, but it was not listed in the July 23 stable release and cannot be treated as a released capability. Structural URL validation and a successful HTTP response were insufficient tests; this feature required an actual stable-app test before rollout.

Removed every v2 route URL. The 34 ordered route-navigation buttons are restored to their original, proven Google Maps URLs. The 96 individual v2 destination links now use the already-confirmed Organic Maps v1 pin format with the same verified coordinates; their Google navigation links remain beside them. The one optional Teatro Olimpico link remains an Organic Maps search because its coordinate is deliberately not part of the verified map data. The 21 all-POI Organic Maps overview buttons and the custom OpenStreetMap/OSRM orientation maps are unchanged.

Organic Maps' legacy route format was not substituted because it accepts only a start and destination. Using it for this project would silently remove ordered intermediate stops from most driving days, which is more dangerous than clearly keeping Google as the live navigator. Organic Maps remains the primary POI-browsing map, where the user has confirmed it works and prefers its presentation; Google remains the live route navigator until a stable Organic Maps release supports and passes an on-phone multi-stop deep-link trial.

## 2026-08-30 — Organic Maps made the primary POI and navigation experience; Google retained as fallback

The user preferred Organic Maps' denser, clearer POI presentation to Google Maps and asked to use it for the project's map functions without losing Google's practical traffic and no-app fallback. The existing 21 all-POI overview buttons remain on Organic Maps. All 34 route buttons were converted from Google Maps name-based URLs to Organic Maps' current `https://omaps.app/v2/dir` format, using the verified coordinates already stored in the route-map configuration and preserving each route's origin, destination, ordered intermediate stops, and driving/walking mode. All 97 individual destination links now open an Organic Maps route from the device's current position to the verified POI coordinate where one exists. Day 1's optional Teatro Olimpico link uses a location-centred Organic Maps search because the page explicitly treats it as unverified and does not include it in the numbered map data.

Every original Google URL remains available as a smaller fallback link. This intentionally gives up a slightly simpler interface in exchange for live-traffic routing, compatibility when Organic Maps is not installed, and a recovery path if the recently introduced v2 route-link format is not supported by an outdated app. The traveller should update Organic Maps before the trip. The custom OpenStreetMap/OSRM orientation-map images remain unchanged because they serve the website and printable edition rather than live navigation.

## 2026-08-26 — `poi-legend` names hyperlinked back to their content sections, across all 21 days

User asked for the names in each day's numbered `poi-legend` (the list under the orientation-map image) to jump to the fuller write-up about that POI elsewhere on the page. Built a matching script rather than hand-editing 21 files: it assigns each content card (`<div class="name">`) a slug id, then resolves every legend entry to a target card and wraps its name in `<a href="#id">`.

Two different matching strategies were needed, discovered mid-way through:
- **Days 4–8** already carry an explicit, authoritative cross-reference: each content card embeds `<span class="poi-ref">N</span>` where N is that POI's position number in the legend `<ol>`. Used that directly (ordinal position → `poi-ref` number → card) instead of guessing from text. Two source-data bugs surfaced and were fixed here rather than routed around: (1) a stray duplicate card in Day 8 (`Trattoria Paolucci` vs `Trattoria Paolucci, Lanciano`) and one in Day 5 (`Caffè Cavour` vs `Caffè Cavour, Fano`) both declared the same `poi-ref` number — resolved by preferring whichever candidate's name exactly matches the legend text, logged in the script's report as `AMBIGUOUS` so it's visible rather than silently guessed.
- **Days 1–3 and 9–21** have no `poi-ref` markers, so matching falls back to text: exact name match first, then bidirectional prefix/substring containment (handles cases like legend "Cittadella — Camminamento di Ronda" matching card "Cittadella"), then — only if that fails — a search for the legend entry's core name inside each card's own text block (handles sub-mentions with no dedicated card of their own, e.g. Day 2's "Castello Superiore, Marostica," only described inside the Marostica card's bullet list). A legend entry naming two POIs joined by " & " or " / " is split and each half linked separately, but only when *both* halves independently resolve to distinct cards — otherwise (e.g. a single business name that happens to contain "&", like "L.AB Pastry & Coffee") the whole string is treated as one name, to avoid a wrong split.

Two structural bugs were caught and fixed before any file was trusted, both by testing on a working copy first and inspecting a full `legend name → matched card` report, not just link counts:
1. A content card's fallback-search window (the block of text scanned for a sub-mention) was originally bounded only by the *next* card or end-of-file. For the very last card on a page, that window silently swept past the `poi-legend` block itself and into unrelated later sections (a planner-UI checkbox label, an unrelated "if you've got half a day" blurb) — both produced false matches. Fixed by also capping every card's window at the `poi-legend` start and the next `<div class="section` boundary.
2. `<span class="tag">...</span>` badge text (e.g. "Coffee / aperitivo, Piazza Garibaldi 39") and `poi-ref` numbers were leaking into the cleaned name used for slugs and matching, corrupting both (e.g. producing an id like `poi-tempio-ossario-cool-interesting-quirky`, and breaking exact-match lookups). Fixed by stripping both before cleaning.

Every legend entry left unlinked was checked against the actual page source and confirmed to have no dedicated content card — mostly cross-day references (another day's accommodation, mentioned only because it's this day's start/end point) or terms genuinely mentioned in more than one card's text (left unlinked rather than guessed, e.g. Day 9's "Palazzo d'Avalos" appears in both the Vasto card and the separate Loggia Amblingh card).

Verified before committing: every generated `href="#poi-..."` resolves to an existing `id="poi-..."` in the same file, no duplicate ids, and `<a>`/`</a>` counts balance — across all 21 files, not spot-checked.

`print-all.html` and `print-stage3.html` regenerated via `scripts/build-print-all.py` from the updated day pages.

## 2026-08-25 — Organic Maps rollout confirmed working, applied to all 21 days

User confirmed on their phone (Organic Maps installed) that Day 2's trial `omaps.app/map?...` button opened the app directly and showed all pins with no route drawn, as intended. Rolled the same generation approach out to the remaining 20 days' "View Today's Places" / "View All Options" buttons, extracting name+GPS pairs from each page's own `poi-legend` in document order. Day 2's regenerated output was byte-identical to the already-committed trial version, confirming the generation script is deterministic and consistent with the manual build used for the trial.

This link only works correctly on a device with Organic Maps installed (Android/iOS App Links interception — see the previous entry for why). Without the app, it reproduces the same broken single-pin result seen in the original desktop-browser test. This is accepted as the tradeoff for a genuine pins-only view; the Google-based "Navigate ..." buttons on each page are unaffected and remain the way to get real turn-by-turn driving directions without any app dependency.

`print-all.html` and `print-stage3.html` regenerated via `scripts/build-print-all.py` from the updated day pages.

## 2026-08-25 — Day 2's overview button switched to Organic Maps (`omaps.app/map`), pending on-phone confirmation

User wants "View Today's Places" to show pins only, no route — the whole point of the button, and something no Google Maps link format actually does (confirmed by testing: comma-list search, `maps/dir` waypoints, and a pipe-separated `q=` all either fail outright or force a drawn route). Organic Maps has a documented multi-point format for exactly this: `om://map?v=1&ll=lat,lng&n=Name&ll=lat,lng&n=Name...`, and a matching web link at `https://omaps.app/map?...`.

Tested the web link directly in a desktop browser first: it failed, showing one garbled pin off the coast of Gabon. Root-caused by reading `organicmaps/url-processor` (the actual Cloudflare Worker source behind `omaps.app`, MIT licensed, on GitHub) — it has no server-side route for `/map` at all; only a single-point "ge0" short-link decoder. A `/map` request that reaches the server (i.e. arrives from a browser/device with no Organic Maps app installed) falls through into that decoder and gets misinterpreted, producing a bogus single point. This is a design constraint, not a bug we can route around: the multi-point format only works via Android/iOS **App Links** interception, confirmed by that same repo's `assetlinks.json` declaring `delegate_permission/common.handle_all_urls` for `app.organicmaps` — meaning the OS hands any `omaps.app` URL straight to the installed app before it would ever reach that broken server-side handler.

Also confirmed via the Android manifest in `organicmaps/organicmaps` (`supports-screens largeScreens/xlargeScreens="true"`, no telephony/GPS/WiFi hardware required, and a comment explicitly protecting Samsung DeX mode) that the app installs and runs on Android tablets, e.g. a Galaxy Tab, not just phones.

Day 2's button (`days/day2.html`) was switched to this `omaps.app/map?...` link, built from the same `poi-legend` GPS+name data as the earlier Google-based rebuild, as a live test — the user has Organic Maps installed on their phone and will access it through the deployed itinerary there. **Not yet confirmed working** — a device without the app (or one where App Links isn't correctly registered) will reproduce the same broken single-pin failure seen in the desktop browser test. If confirmed working on-device, roll out to all 21 days the same way `decisions.md`'s prior 2026-08-25 entries did for the Google-based version; if it fails even with the app installed, fall back to building a self-contained Leaflet/OpenStreetMap page instead (discussed, not yet started).

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
