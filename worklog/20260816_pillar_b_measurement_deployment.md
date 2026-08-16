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

## Measurement state (updated 2026-08-16, unblocked)

GA4 is configured and **verified receiving events**.

- Property: `ec-hitori-tools (Pillar B LP)` / `550092132`, under the existing `合同会社島山` account.
- Data stream: `ec-hitori-tools LP` / `15444689586` for `https://interhiro.github.io/ec-hitori-tools/`.
- Measurement ID `G-M8MXQJLYFS` is set in `measurement.config.json` and deployed to GitHub Pages.
- `source_id` is registered as an **event-scoped** custom dimension.
- Receiver-side verification: loading the LP sent `en=lp_view` with `ep.source_id=yt_short_photo_aar5wmqvi0` to `g/collect`, and GA4 Realtime showed `lp_view=3` with 1 active user. One collect request returned HTTP 503; because the events landed in Realtime this is treated as transient. This traffic was Claude's own verification, not organic.

## Photo funnel experiment

The experiment **started on 2026-08-16**. Both YouTube path changes are public:

- Long form `fiS_R3IkQg4`: description LP link now carries `&source_id=yt_short_photo_aar5wmqvi0`; confirmed over unauthenticated HTTP.
- Short `Aar-5wMqVI0`: description now links directly to `watch?v=fiS_R3IkQg4`; confirmed over unauthenticated HTTP.
- **Still manual:** the YouTube Studio Shorts "related video" setting has no YouTube Data API field, so it was not applied. The description link is the substitute. Setting it in Studio would strengthen the path.

Baseline at go-live (`2026-08-16T07:29:03Z`): Short `Aar-5wMqVI0` 1,850 views / 1 like; long form `fiS_R3IkQg4` 1 view / 0 likes. GA4 funnel counts start at 0 today — this is start-of-observation, not observed zero.

`affiliate_click` was deliberately not exercised: clicking our own A8 link would pollute the ASP-side measurement. Its logic is covered by the 19 passing `tests/track.test.js` cases.

Evaluation date: 2026-08-23. No outcome is claimed before that date.

## Verification

- `python3 -m pytest -q`
- `node tests/track.test.js`
- `python3 build.py`
- `python3 articles_build.py`

## Next actions

1. (Shimayama, optional) Set the Shorts "related video" on `Aar-5wMqVI0` to `fiS_R3IkQg4` in YouTube Studio — not reachable via the Data API.
2. On 2026-08-23, read GA4 for `lp_view` / `affiliate_click` / `list_signup` broken down by `source_id`, read A8 clicks and conversions by `id1=ec-tips-09`, and re-measure both videos. Record the result in `../shimayama-ops/state/market_contact_ledger.csv`.
3. Keep `source_id` values distinct per path so future arms stay separable.
