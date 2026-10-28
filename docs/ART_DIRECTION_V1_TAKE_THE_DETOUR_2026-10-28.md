# Art direction v1 — “TAKE THE DETOUR / 定番の、その先へ。”

Implementation of the ChatGPT art-direction study 01 (`Encounter_Japan_Art_Direction_Study_01`)
on the live Encounter Japan page. 2026-10-28.

Reference material used: `index.html` (prototype), `ART_DIRECTION_v1_JA.txt`,
`PHOTO_CREDITS_FROM_ORIGINAL_JA.txt`, `side_by_side_preview.jpg`, `concept-320/390/768/1280*.png`.

## What changed

| Area | Before | Now |
|---|---|---|
| Hero | “BEYOND THE OBVIOUS” over an SVG city-pop illustration (`night-street.svg`) | “TAKE / **THE** / DETOUR.” over a **photograph** of a Shibuya backstreet; media block 62 % × 86 % right, title overlapping it, outlined third line, orange photo tag |
| Palette | `#fff` paper, `#111` ink, `#ff5900` | paper **#FAF9F5**, ink **#151513**, acid **#FF5000** (tokens `--td-*`, and the `--ej-*` tokens retuned to the same values) |
| Ticker | — | orange 64 px marquee (BOOKSHOPS / ALLEYS / GOOD COFFEE …) |
| Opener | “Make your own way” + a rotated giant **526** | “Places are the beginning. Not the whole story.” — the count moved out of the top of the page into Discover, per the study (“数だけを自慢しない”) |
| Place study | illustration + “THE BEST PART IS THE DETOUR.” | Jimbocho **photograph**, screen-blended `01.`, “LOST IN THE MARGINS.” and a button into the real Jimbocho listings |
| Walks | white cards with illustration backgrounds | dark spread “WALK / OFF / SCRIPT.” with the Dotonbori and Sannenzaka **photographs**, the orange `TAKE THE LONG WAY ↗` sticker and links into the real routes and areas |
| Second story / mixtape | two more full-bleed illustrations | removed as lead visuals; one illustration stays as a small supporting motif with an explanatory line, one stays inside Field notes |
| Discover | “Find your place.” | “FIND / YOUR / **OWN.**” + `[02 / DISCOVER] Where shall we begin?` above the unchanged controls |
| Close | — | orange “THERE / IS / MORE.” block |
| Footer | one line | two-column credits block with photographer, licence, date and crop note |

Section order, anchors (`#top`, `#stories`, `#browse`, `#fieldnotes`, `#visitor-info`, `#mood`)
and every JavaScript hook were kept, so deep links and shared URLs still resolve.

## Photographs — licences re-checked 2026-10-28

All four are stored in this repository under `assets/photos/` (two widths each, cropped and
resized with `sips`). Nothing is hotlinked; a regression test fails the build if an `<img src>`
ever points at an external host again.

| File | Place / date | Photographer | Licence | Commons file page |
|---|---|---|---|---|
| `shibuya-1800.jpg`, `-900.jpg` | Shibuya backstreet, Tokyo · 2017-12-30 | Giuseppe Milo | CC BY 3.0 | `File:Shibuya_Tokyo_Color_Street_Photography_(240747567).jpeg` |
| `jimbocho-1400.jpg`, `-700.jpg` | Jimbōchō Book Town, Tokyo · 2025-04-11 | Olaf2 | CC BY-SA 4.0 | `File:Jimbōchō_Book_Town_2025_02.jpg` |
| `kyoto-1400.jpg`, `-700.jpg` | Sannenzaka, Higashiyama, Kyoto · 2009-07-30 | Andrea Schaffer | CC BY 2.0 | `File:Sannenzaka_street,_Kyoto_(3811257874).jpg` |
| `osaka-1600.jpg`, `-800.jpg` | Dōtonbori at night, Osaka · 2018-04-09 | Ajay Suresh | CC BY 2.0 | `File:Dontonbori_Street_at_Night_-_Osaka_(41441002704).jpg` |

Checked through the Commons API: every file is `AttributionRequired: true`, `Restrictions:` empty,
all four licences allow commercial use and modification. The crops are adaptations; the CC BY-SA 4.0
file (Jimbōchō) therefore carries a ShareAlike note in the footer. Each photograph is captioned as
neighbourhood atmosphere — never as a photograph of a listed venue.

The prototype referenced these files directly from `upload.wikimedia.org`. Captured from the
prototype on 2026-10-28, two of the four did not load and silently fell back to the old concept
illustrations; that is exactly the failure this implementation removes.

## What was deliberately not copied from the prototype

- The prototype’s four-item demo search. The real search (526 listings, 21 regions, areas,
  keywords, six themes, saved places, shareable URLs) is untouched underneath the new type.
- The prototype’s single-page scope. Field notes (10 routes / 35 stops), Visitor essentials
  (383 sourced destinations) and the listing grid keep their structure and only take the new
  palette, pill controls and type.

## Deviations from the reference, and why

1. **Mobile `DETOUR.`** — the study prints the third line in solid ink over the photograph, where it
   is close to unreadable. It keeps the ink fill but gains a 1.2 px paper stroke, so the silhouette
   is the same and the word is legible.
2. **Discover is one column, not the prototype’s two.** The production controls (region, area,
   keyword, six themes, reset, result count) do not fit the demo’s controls/results split, and the
   results live in `<main>` outside the header. The editorial head and the 4 px rule were kept.
3. **The “four ways in” index and the “go by feeling” dark list were kept**; the study does not have
   them, and removing working navigation was out of scope.
4. **`526` still appears** — in the Discover subhead and inside the page, not as the hero statement.

## Verification

- `node --test tests/data-guard.test.mjs tests/four-core-features.test.mjs tests/four-features-smoke.mjs tests/editorial-smoke.mjs tests/essentials-layer.test.mjs` → **59 pass / 0 fail**, including the
  byte-for-byte data guard on the 526 names and Google Maps URLs.
- `node tests/visitor-browser.mjs` at **320 / 390 / 768 / 1280** → no horizontal overflow, no page
  errors, 21 regions, Japanese search, themes, route filter, 383 essentials shortcuts.
  New assertions: the hero headline *must* overlap the photograph, the reading copy must not leave
  the viewport, and **every image must actually decode** — a fallback-only page fails.
- Hands-on checks: the Jimbocho button → 8 Jimbocho listings, the sticker → Kyoto / Higashiyama (11),
  the spread link → Osaka / Namba (7); `?area=…` deep links, browser Back and `#route-…` all work;
  526 `.place-map` links all resolve to Google Maps.
- Screenshots: `artifacts/screenshots/take-the-detour-2026-10-28/` (before and after, four widths,
  plus `00-side-by-side.jpg`).
