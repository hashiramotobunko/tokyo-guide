# Walking routes — verification record, 2026-10-27

Scope: the ten DRAFT routes (35 stops) in `tokyo-guide_2.html`. Machine-readable version: `data/route-verification.js` (`window.EJ_ROUTE_FIELD_V1`).

## Method and its limits
| Check | How it was done | Status |
|---|---|---|
| ① Official name and address | Official site or association page where one exists; otherwise dated directory listing | Recorded per stop in `data/visitor-essentials.js` |
| ② Google Maps URL points to the right venue | Each listing's **existing** Maps link was opened in a browser; the resolved place name and coordinates were recorded (`mapsResolved`, `lat`, `lon`) | 35/35 resolved to the intended venue |
| ③ Same-name / moved / in-building confusion | Address compared with the official page; notes recorded (e.g. Santosham is 2F of the Komuro Bldg; Mizuho's Waseda namesake is unrelated; The Great Burger's Shibuya Stream branch is a different shop) | No mismatches found |
| ④⑥ Walking route and distance | OSRM (OpenStreetMap foot profile) between the resolved coordinates; minutes = distance ÷ 80 m/min; 5 legs cross-checked with the Google Maps walking preview | Map estimates only |
| ⑤ Stop order | All permutations compared on OSRM distance, then opening windows applied | 4 routes reordered (below) |
| ⑦ Steps, slopes, closures | Only what official pages state (Kiyomizu slopes and no-step route; Takeshita bollards 11:00–18:00; Kiyomizu street closure 8:00–19:00). Not surveyed. | Partial |
| ⑧ Same-day feasibility by hours | Opening windows from the essentials layer | See per-route notes |
| ⑨ Accessibility | Official statements only (Kiyomizu, Minamiza, NMWA, Meiji Jingu wheelchairs, Ueno Park parking) | 6 stops with official info |
| ⑩ Editorial meaning | Written per route (`whyWalk`, `whyTogether`, `culture` with sources) | Done |

**Nothing was walked on the ground.** Every route stays `fieldVerified:false` and is labelled “DRAFT · MAP-CHECKED · NOT FIELD-WALKED”. Google Maps was used manually through its normal web interface (one page per listing, five direction previews); no scraping or unofficial API.

Google Maps walking-preview spot checks (read from the preview, 2026-10-27): Kiyomizu-dera → Yasaka 19 min; TNM → Shinobazu Pond 13 min; Meiji Jingu (Honden) → Takeshita St 19 min; CAVE → Chaos 17 min; Ebisubashi → Jiyuken 6 min. OSRM distances for the same legs: 1,993 m / 1,500 m / 2,671 m / 1,292 m (two legs) / 1,019 m.

## Per-route results
| Route (city / area) | Stops | OSRM total | Order | Hours official / any | Access info | Open issues |
|---|---|---|---|---|---|---|
| Jimbocho (Tokyo) | 3 | 1,488 m | kept (shorter loop noted) | 3 / 3 | 0 | Payment and English support unknown for all three |
| Shibuya (Tokyo) | 3 | 1,292 m | **reordered** CAVE → Bounce → Chaos (was 1,936 m, started at the venue that opens last) | 1 / 2 | 0 | Bounce hours unknown; both Maruyamacho bars are 2F, no step-free info |
| Higashiyama (Kyoto) | 4 | 3,754 m | kept (tearoom-before-theatre would be 4,051 m) | 2 / 3 | 2 | Kiyomizu fee only from secondary sources; Komori hours from directories |
| Ueno (Tokyo) | 4 | 3,526 m | kept (reverse saves ~100 m) | 4 / 4 | 3 | Tobikan site returned 503 all day; its hours come from the museum's own PDF |
| Kiyosumi-Shirakawa (Tokyo) | 3 | 726 m | kept | 0 / 2 | 0 | Yonemoto hours not found; First Crop sources disagree |
| Harajuku (Tokyo) | 4 | 4,253 m | **reordered** Meiji Jingu → Mizuho → Great Burger → Takeshita (was 4,288 m with the sell-out shop third) | 3 / 4 | 2 | Mizuho hours are from a 2022 article |
| Ebisu (Tokyo) | 3 | 892 m | kept (already shortest) | 1 / 1 | 0 | Soul Sonic Boogie and MOD'Z: nothing confirmable found |
| Koenji (Tokyo) | 4 | 1,481 m | **reordered** Shichimencho → dop → Asatte → Kidofuji (was 2,018 m; diner closes 19:00) | 0 / 2 | 0 | bar dop and Kidofuji hours unknown; Asatte lease rumour unconfirmed |
| Shinjuku (Tokyo) | 4 | 337 m | kept | 2 / 4 | 0 | Kameya and Shimonya listings date from March 2021; Kameya hours conflict |
| Namba (Osaka) | 3 | 1,205 m | **reordered** Jiyuken → Ebisubashi → Ootako (was 3,713 m by OSRM and doubled back; curry closes 20:00) | 1 / 2 | 0 | Ootako opening time differs between listings |

“Hours official / any” counts stops whose opening hours come from an official-grade source / from any dated source (official, secondary or conflicting). All ten routes are inside a single city and a single neighbourhood; the test `tests/essentials-layer.test.mjs` enforces this.

## Destination identification (35/35)
Every stop's existing Google Maps link resolved to the expected venue. Resolved names are stored as `mapsResolved` (for example 三燈舎 → “Santosham”, ソウルソニックブギー恵比寿 → “BAR SOUL SONIC BOOGIE EBISU”, 米本珈琲 清澄白河 → “Yonemoto Coffee Flagship Store Kiyosumi-Shirakawa”). No listing URL was changed.

## Still open
- On-foot verification of all ten sequences (stairs, crossings, night access, actual minutes).
- Official hours for 13 stops (see table), accessibility for 29 stops.
- A Japanese-speaking phone check for the eight small bars/shops with no web presence.
