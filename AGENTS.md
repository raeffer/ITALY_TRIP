# Italy Road Trip Companion — Agent Guide

## Project

A 21-day Italy road trip companion site — one static HTML page per day (`days/dayN.html`), a shared stylesheet, a generated printable edition, and a single photo-credits page. The trip is presented in three stages (see `index.html` for the live grouping).

## Where the real information lives

- **Current repository status and open work:** read `build-status.md`.
- **Dated log of past decisions and the reasoning behind them:** read `decisions.md`.
- **Content, design, and photo standards:** read `standing-directives.md`. This is the repo's durable, tool-agnostic rules file (its own header describes it as facts about the project itself that hold regardless of which AI tool is used) — read it in full before starting any work, not just when a specific rule seems relevant.
- **Day-by-day research content (Days 1–13):** read `CONTENT.md` — the source of research for Days 1–13, which must stay mirrored into each day's HTML page in `/days/` per `standing-directives.md`'s content-sync rule.
- **Stage 3 day-by-day research and status:** read `STAGE3_CONTENT.md`.

Don't duplicate any of those here — go read the file itself.

## Standing instructions

- Before starting any new work, verify anything in this file against the actual repo state (file contents, `git status`, `git log`) rather than trusting it blindly. If something here conflicts with what you find, flag the conflict rather than silently picking one version.
- Whenever a meaningful piece of work finishes, update `build-status.md` in the same commit, before reporting the work as done. Rewrite stale sections in place rather than appending to them — `build-status.md` should always read as current, not as a running log. Anything that records a past decision, a past incident, or reasoning that no longer describes the present belongs in `decisions.md` instead, as a new dated entry at the top — never rewrite or delete an existing `decisions.md` entry.
- A fresh session must read this file, `build-status.md`, and `standing-directives.md` in full before doing anything else in this repo. Verify all of them against actual repo state rather than trusting them blindly.
