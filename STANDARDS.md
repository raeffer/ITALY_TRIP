## A Note on What Belongs Here

This file documents facts about the PROJECT ITSELF — content rules, design system, file structure, project history — that stay true no matter which AI tool or app someone uses to work on it. It should NOT contain instructions specific to one app or interface (e.g. how to configure a particular tool's settings, that tool's bugs or workarounds). If a note is really about troubleshooting a specific app rather than the project, it doesn't belong in this file.

## Content Philosophy
- This is a decision-making travel companion, not a guidebook — practical, honest, for reading in a moving car.
- Every day follows this structure: Theme, Overview (with a routing note checking what's actually on the road between stops, not just the destination), Stops, Coffee, Pasticceria, Lunch/Dinner, Local Speciality, What to Buy, Hidden Gem, Cool/Interesting/Quirky, Accommodation, If Time Is Tight, If You've Got Half a Day, Skip It, Today's Winners, Road Trip Score.
- Sourcing priority: Italian tourism sites, comune/Pro Loco sites, Slow Food, Gambero Rosso, Italian food writers first. English-language sites only to sanity-check major attractions aren't missed.
- Honesty over polish: flag mixed reviews, closures on the actual travel date, genuine gaps (e.g. "no real $$$ option exists here"), and conflicting information rather than forcing a confident-sounding but shaky recommendation.
- "Cool, Interesting & Quirky" is a menu to browse, not a mandatory itinerary — use what fits the day.

## Photo Standards
- Only Creative Commons / properly licensed photos (Wikimedia Commons primarily), always with photographer name and license credited in credits.html.
- MANDATORY before using any photo: actually open and view the image itself to confirm it shows the real, recognizable subject — not a texture, crop, or unrelated detail (this was learned after a "Guaita Tower" photo turned out to be a close-up of a door).
- Every day page must include a minimum of 3 inline images integrated naturally throughout the content.
- Every day page must include a minimum of 3 gallery images at the end of the page.
- Gallery images should be different from the inline images wherever practical.
- Images must relate directly to locations, food, experiences, or quirky points of interest featured on that day's itinerary.
- Prioritize variety across the page, including where appropriate: local food, local life, quirky details, architecture, scenery, viewpoints, and cultural experiences.
- Avoid pages consisting primarily of panoramas or exterior building shots.
- Images should enhance the storytelling and decision-making value of the guide, not simply decorate it.
- The end-of-day photo-finale section must show completely different subject matter than anything pictured inline earlier on that same page wherever practical — no repeats of the same subject, even as a different image of it.
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
- File structure: shared /style.css used by all pages, one file per day in /days/dayN.html, root /index.html linking to all days, root /credits.html for all photo credits.

## Working Efficiently (for any AI assistant on this project)

- Don't use the browser tool to screenshot or self-verify visual changes (phone/tablet/desktop views, print previews). Make the change, state clearly what was changed, and let the human check visually and report back if something's wrong.
- Don't re-read whole files to double-check before AND after making an edit — read once, edit, done.
- Don't go fix or investigate things that weren't explicitly asked for. If something else looks worth fixing, mention it in one line and wait for direction rather than acting on it.
- Keep responses short: a brief confirmation of what changed, not a detailed walkthrough of reasoning or process.
- For photo verification: one check is enough (confirm subject matches + license on the real source page) — don't cross-verify the same photo a second way.
- When given a fix, assume the human will visually confirm it themselves — don't spend extra steps trying to prove it worked before reporting back.

## Known Issues / History
- GitHub Pages build source must be on the "main" branch specifically (an earlier mismatch with "master" caused the live site to show a blank placeholder for a while).
