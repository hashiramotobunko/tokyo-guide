# Visitor essentials — research record and how to resume, 2026-10-27

## What exists now
| File | Role |
|---|---|
| `data/visitor-essentials.js` | Independent practical-information layer (`window.EJ_ESSENTIALS_V1`). One record per researched place, keyed `city|<Google Maps place id>` taken from the listing's own URL, so same-name venues cannot collide. Each field: type, value, source URL, source type, verification status, checked date, method, optional conflicting value and note. |
| `data/route-verification.js` | Route editorial text, destination identity, legs and evidence (`window.EJ_ROUTE_FIELD_V1`). |
| `data/research-ledger.json` | 526 rows, one per approved listing, with batch, status and field counts. Rebuilt by `node scripts/build_research_ledger.mjs`; existing `notes` are preserved. |
| `scripts/check_source_links.mjs` | Manual network check that every cited URL still answers. |
| `tests/essentials-layer.test.mjs` | Guards the layer: keys resolve to exactly one listing, displayed values carry sources and dates, unverified fields carry no value, routes stay inside one area, ledger covers 526. |

The page loads the two data files as plain scripts, so double-clicking `tokyo-guide_2.html` still works. The 526 listings in `const DATA` were not modified.

## Verification statuses
| `stat` | Meaning | Shown on the page? |
|---|---|---|
| `official` | Read on the venue's own site, a public authority, tourism board or the alley/street association | Yes, with “Official source” |
| `secondary` | Dated media, directory, booking-platform or review-site listing | Yes, with “Secondary source” and the source type |
| `conflict` | Two sources disagree; both values stored | Yes, both values, “Sources disagree” |
| `unverified` | Looked for, not found or not confirmable | No value; counted and listed as “Not yet confirmed” |
| `n-a` | Does not apply (e.g. admission to a public street) | No |

Nothing is inferred from venue type. Google Maps category or hours were **not** used as a source.

## Counts (2026-10-27)
| Measure | Count |
|---|---|
| Listings processed (researched) | 36 of 526 (35 route stops + Tsutenkaku) |
| Records with at least one official field | 19 |
| Records with secondary information only | 13 |
| Records with nothing confirmable | 4 (Yonemoto Coffee, Soul Sonic Boogie, MOD'Z, bar dop) |
| Fields recorded | 165 (official 80 · secondary 43 · conflict 4 · unverified 36 · not applicable 2) |
| Official website found | 23 of 36 |
| Conflicting-source fields | 4 (First Crop hours, Spincoaster cover, Kameya hours, Ootako hours) |
| Not started | 490 |

Re-verification of the eight pre-existing records (TNM, NMWA, Tobikan, Kiyomizu, Meiji Jingu, Tsutenkaku, MAIDENS, Mizuno): all re-read on 2026-10-27. Changes found: TNM now lists card/e-money payment and a security-screening notice; NMWA lists a 2027 collection closure; Tobikan's HTML guide was unavailable (503) so its hours come from the museum's access PDF; Kiyomizu's regular closing time (18:00 / 18:30) was found on the open-hours notice; Meiji Jingu's November gate times were added.

## Flags for the owner
| Place | Flag |
|---|---|
| 東京都美術館 | Official site returned HTTP 503 all day; hours taken from `guide_access.pdf` — recheck when the site is back |
| 日本酒あさって | A feature article suggested the building may limit how long the bar stays; unconfirmed |
| First Crop Coffee Japan Roastery | Opening days disagree between sources |
| そば処かめや 新宿店 | Association listing is from March 2021 and conflicts with a later article |
| 四文屋 思い出横丁店 | Association listing is from March 2021 |
| 瑞穂 | Hours come from a 2022 article |
| 本家大たこ 道頓堀本店 | Opening time differs between listings |
| 自由軒 | Tempozan branch closed 27 Sep 2026 (the listed Namba shop is unaffected) |
No closure or relocation suspicion was found for any of the 36 researched listings.

## Resuming the remaining 490
1. `data/research-ledger.json` → take rows with `status:"not-started"`, lowest `batch` first (batch 2 = 101 museums, temples, shrines, landmarks, parks, baths, venues; batch 3 = 389 food, drink and shops).
2. For each: find the official site (search engine, then the venue's own SNS), read hours / closed days / fees / booking / payment / access / language / accessibility / notices; record one field per item with its URL and today's date; mark `unverified` where nothing is found and `conflict` where sources disagree.
3. Append the record to `data/visitor-essentials.js`, run `node scripts/build_research_ledger.mjs`, then `node --test tests/*.test.mjs tests/*smoke.mjs`.
4. Never edit `const DATA`; never delete a listing — a suspected closure is a `flags` entry on the record.
