# Encounter Japan — four visitor features, implementation record
Date: 2026-10-24
Status: **Draft PR #1 only. Not published or merged.**

## Four functions now integrated with the 526-item original HTML guide

### ① Region & neighborhood discovery
- `#ej-region-select` and `#ej-area-select`, dynamically derived from real data; includes record counts.
- Japanese name, English alias, category and existing source-backed English notes all searchable in `#ej-search`.
- Combined city, area, category, type, mood, sort and text-search state; URL query sharing and browser back/forward handling.
- Clear filters button and zero-result messaging; no alternate fabricated list.

### ② Thematic & neighborhood walking ideas
- Ten **editorial draft** collections, 35 real registered stops, covering Tokyo, Kyoto and Osaka. Each stop resolves to a place in the same stated city and area.
- Route filters by city (Tokyo/Kyoto/Osaka), editorial theme (night, coffee, food, culture) and neighborhood dropdown.
- Every route has individual stop links plus a multi-stop Google Maps **walking route preview**, which the visitor must check for correct name matching, walking safety, order, hours, accessibility, time and distance.
- `Copy route link` allows sharing an individual editorial collection.
- Never claim a walking route has been field-verified; no duration/distance assertion.

### ③ Practical visitor details
- `Visitor essentials` expands on every source listing with known area/city and its existing Google Maps link.
- Six names now have venue-specific practical content with source URLs and checked dates:
  - 東京国立博物館 — https://www.tnm.jp/modules/r_free_page/index.php?id=113
  - 国立西洋美術館 — https://www.nmwa.go.jp/en/visit/
  - 東京都美術館 — https://www.tobikan.jp/guide/
  - 清水寺 — https://www.kiyomizudera.or.jp/en/faq/
  - 明治神宮 — https://www.meijijingu.or.jp/sanpai/2.php
  - 通天閣 — https://www.tsutenkaku.co.jp/annai/
- Clickable featured sources/venues bring the visitor directly to the listing and its details.
- Unknown pricing, reservation requirement, payment, language availability or hours are **not invented**. Remaining 520 locations have no individually researched price/reservation/hour claims.
- These are checked source excerpts, not real-time opening or bookability confirmations.

### ④ Theme / mood discovery
- Six objective, category-derived themes: After dark; Coffee & sweets; Art & heritage; Japanese food; Style & design; Take it slow.
- The theme combines with region, neighborhood and text, and is shareable in the query URL.
- Subjective or condition-dependent descriptors (quiet, romantic, open late, good for kids) are **not automatically asserted**.

## Integrity checks performed
- Inline JavaScript source parsed successfully.
- Exact `const DATA` block compared with `main`: byte-for-byte unchanged.
- 526 entries and 526 unique original Google Maps links preserved; 522 `/maps/place/` and four previously accepted `/maps/search/?api=1&query=` URLs.
- All 35 route stops mapped to existing approved places in their stated area; no orphan stop.
- All four navigation sections, feature DOM controls and handlers confirmed present.
- Added/updated `tests/four-features-smoke.mjs` and `tests/editorial-smoke.mjs`. These are **committed but not yet executed in CI**.

## Remaining checks before release
1. Run `node --test tests/*.mjs` in a checked-out branch.
2. Render and test the **exact** branch HTML in browser at 320/390/768/1280px; verify keyboard/touch navigation, share/back behavior, map-route opening, visual design and no horizontal scroll.
3. Verify chosen Google Maps multi-stop directions resolve all waypoints correctly; until then labels remain DRAFT.
4. Gradually fill price/reservation/access sources for more of the 526 entries, with dates. No auto-populated speculative facts.
5. Check the owner's actual Instagram profile URL before enabling its existing placeholder.
6. Receive explicit release approval before merge, push to main, or deploy.

## Review in 30 seconds
GitHub PR: https://github.com/hashiramotobunko/tokyo-guide/pull/1
Branch ZIP: https://github.com/hashiramotobunko/tokyo-guide/archive/refs/heads/design/encounter-fashion-direction-20261023.zip

Unzip and double-click `tokyo-guide_2.html`. Click the four large links near the top:
- FIND A NEIGHBORHOOD → area/region search
- FOLLOW AN IDEA → walking routes
- PLAN YOUR VISIT → practical visitor info
- GO BY FEELING → mood search

**No production deployment performed.**
