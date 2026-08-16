# Pillar B LP measurement deployment — 2026-08-16

## Purpose

Make the existing LP record source-attributed funnel events without adding a dashboard, backend, product, or scheduler.

## Scope completed in this repository

- Added `lp_view`, `affiliate_click`, and `list_signup` event handling in `track.js`.
- Preserved legacy `?v=` to A8 `id1` behavior.
- Added `source_id` attribution; an explicit `source_id` takes priority for LP event attribution.
- Added `measurement.config.json` as the GA4 integration boundary. It contains no Measurement ID.
- Prevented arbitrary URL query strings from being sent to GA4; events include only `source_id` and `page_path`.
- Marked both list-registration links with `data-list-signup="true"`.

## Measurement state

- `measurement.config.json` has an empty `measurement_id`.
- Therefore, GA4 delivery is **unobserved**, not observed zero. The LP dispatches no external GA4 event until a valid `G-...` ID is configured.
- Required one-time configuration: choose/create the GA4 web data stream for `https://interhiro.github.io/ec-hitori-tools/`, place its public Measurement ID in `measurement.config.json`, deploy, and register `source_id` as an event-scoped custom dimension.

## Photo funnel experiment

The experiment has **not started**. Its baseline and blocking conditions are recorded in `../shimayama-ops/state/market_contact_ledger.csv`:

- Photo Short `Aar-5wMqVI0`: public, 1,850 views and 1 like at `2026-08-16T05:44:12Z`.
- Matching long form `fiS_R3IkQg4`: public, 1 view.
- Start is blocked until the YouTube related-video and source-tagged long-form LP link are public, and GA4 is configured and receiving events.
- Evaluation date: 2026-08-23. No outcome is claimed before that date.

## Verification

- `python3 -m pytest -q`
- `node tests/track.test.js`
- `python3 build.py`
- `python3 articles_build.py`

## Next actions

1. Configure the GA4 Measurement ID and `source_id` custom dimension.
2. Apply and verify the pending YouTube path edits.
3. Start the seven-day experiment only after both conditions are live.
