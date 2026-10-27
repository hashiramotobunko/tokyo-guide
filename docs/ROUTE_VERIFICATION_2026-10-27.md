# Walking routes — verification record, 2026-10-27

Scope: the ten DRAFT routes (35 stops) in `tokyo-guide_2.html`. Machine-readable version: `data/route-verification.js` (`window.EJ_ROUTE_FIELD_V1`).

## Method and its limits
| Check | How it was done | Status |
|---|---|---|
| ① Official name and address | Official site or association page where one exists; otherwise dated directory listing | Recorded per stop in `data/visitor-essentials.js` |
| ② Google Maps URL points to the right venue | Each listing's **existing** Maps link was opened in a browser; the resolved place name and coordinates were recorded (`mapsResolved`, `lat`, `lon`) | 35/35 resolved to the intended venue |
| ③ Same-name / moved / in-building confusion | Address compared with the official page; notes recorded (e.g. Santosham is 2F of the Komuro Bldg; Mizuho's Waseda namesake is unrelated; The Great Burger's Shibuya Stream branch is a different shop) | No mismatches found |
| ④⑥ Walking route and distance | OSRM (OpenStreetMap foot profile) between the resolved coordinates; distance stored per leg; **all 25 legs** read on the Google Maps walking preview and the preview minutes stored as `gmin` / `gchk` | Map estimates only |
| ⑤ Stop order | All permutations compared on OSRM distance, then opening windows applied | 4 routes reordered (below) |
| ⑦ Steps, slopes, closures | Only what official pages state (Kiyomizu slopes and no-step route; Takeshita bollards 11:00–18:00; Kiyomizu street closure 8:00–19:00). Not surveyed. | Partial |
| ⑧ Same-day feasibility by hours | Opening windows from the essentials layer | See per-route notes |
| ⑨ Accessibility | Official statements only (Kiyomizu, Minamiza, NMWA, Meiji Jingu wheelchairs, Ueno Park parking) | 6 stops with official info |
| ⑩ Editorial meaning | Written per route (`whyWalk`, `whyTogether`, `culture` with sources) | Done |

**Nothing was walked on the ground.** Every route stays `fieldVerified:false` and is labelled “DRAFT · MAP-CHECKED · NOT FIELD-WALKED”. Google Maps was used manually through its normal web interface (one page per listing, one direction preview per leg: 25 previews); no scraping or unofficial API.

Google Maps walking-preview minutes per leg (read from the preview, 2026-10-27): Jimbocho 9+3; Shibuya 14+3; Higashiyama 19+8+6; Ueno 6+6+11; Kiyosumi 1+5; Harajuku 21+2+10; Ebisu 4+6; Koenji 3+6+7; Shinjuku 1+1+1; Namba 6+3. Route cards show these minutes next to the OSRM distance, labelled as a map check only.

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

## Leg re-check (2026-10-27)
All 25 legs were compared: OSRM distance ÷ Google preview minutes. Twelve legs fall outside 55–110 m/min or differ by 5 min or more from an 80 m/min estimate and now carry `disc:true` with a note; the route card shows “⚠ map figures disagree, treat as rough” on those legs and a count in the “Checked so far” table. Nothing was corrected by hand. Flagged: Jimbocho MAIDENS→Mizuno; Higashiyama Kiyomizu→Yasaka, Yasaka→Minamiza; all three Ueno legs (museum pins sit inside large grounds); Kiyosumi Yonemoto→First Crop; all three Harajuku legs (Meiji Jingu pin is the inner shrine); Shinjuku Gifuya→Shimonya; Namba Jiyuken→Ebisubashi. Likely cause in every case: the Google Maps pin for a park, shrine or museum is far from the entrance actually used, so the OSRM path and the preview path differ. Slope, stairs and crossings were not assessed for any leg.

### Second read of the 12 flagged legs (2026-10-27, later the same day)
Each flagged leg was opened again in the Google Maps walking preview (English interface, same pin coordinates). Every minute figure matched the stored value (9, 19, 8, 6, 6, 11, 1, 21, 2, 10, 1, 6). The preview's own labels show what each pin is: Kiyomizu-dera resolves to “Kairo” (a corridor inside the grounds), Yasaka Shrine to “Honden” (main hall), Tokyo National Museum to its museum shop, Meiji Jingu to the inner sanctuary “Honden”, Takeshita Street to a pin at 1-9 Jingumae. These labels are stored per leg (`gpinFrom`, `gpinTo`, `gchk2`) and printed under the leg on the route card, so a reader knows the minutes start inside the grounds, not at the gate. The OSRM distance is kept but labelled a rough estimate. Entrances, gates, stairs and crossings were not checked on foot.

## How the route card reads now (2026-10-27, evening)
Traveller-first order: eyebrow and status label, title, intro, the “why walk here” paragraph, a facts line (number of stops, distance on the map marked rough where any leg is flagged, and a walking-time sentence that always says “by map preview — not walked, allow extra”), then the numbered stops. Each stop shows its name, English name, category, the editorial note, an hours/closing line with status and date, three status chips, a “Checked details & sources” panel and the Google Maps / official links. Between stops a short leg line gives the map-preview minutes, the distance (or “distance unconfirmed” on flagged legs) and a Directions link to Google Maps walking directions between the two pins. Everything else — the “Checked so far” table, how each stop was matched, how each leg was measured, pin names, re-read dates, the reorder note and the caution — sits inside a collapsed “Route verification details” panel. “Before you go” (why these stops together, check-before-you-go closures, transit, sourced background) is a second collapsed panel.

## Still open
- On-foot verification of all ten sequences (stairs, crossings, night access, actual minutes).
- Official hours for 17 of 35 stops (31 have hours from some source); accessibility information for 29 of 35 stops.
- The 12 flagged legs need a walk before the minutes are trusted.
- A Japanese-speaking phone check for the eight small bars/shops with no web presence.
