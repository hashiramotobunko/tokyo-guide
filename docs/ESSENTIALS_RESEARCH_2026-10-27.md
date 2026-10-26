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

## Counts (2026-10-27, after batch 3 commit 37fc88b)
| Measure | Count |
|---|---|
| Listings processed (researched) | 371 of 526 (batch 1: 36 route stops + Tsutenkaku; batch 2: all 101 museums, temples, shrines, landmarks, parks, baths and venues; batch 3: 234 of 389 food, drink and shop listings) |
| Records with at least one official field | 139 |
| Records with secondary information only | 143 |
| Records with nothing confirmable (every field unverified) | 89 — mostly small bars, izakaya and neighbourhood eateries whose official pages could not be reached (domain not found, 404, 429 rate limiting) or that have no web presence |
| Fields recorded | 1,246 (official 451 · secondary 312 · conflict 31 · unverified 437 · not applicable 15) |
| Official website found | 170 of 371 |
| Records with a conflicting-source field | 30 (both values stored, shown as "Sources disagree") |
| Not started | 155 (Tokyo 87, Hokkaido 28, Kyoto 21, Osaka 14, other prefectures 5 or fewer each) |

Re-verification of the 36 batch-1 records on 2026-10-27: Yonemoto Coffee (official 7:30–20:00), MOD'Z (official, closed Sun) and bar dop (official 19:00–2:00) moved from unverified to official; Soul Sonic Boogie, Ootako, Kameya, First Crop and Spincoaster keep both disagreeing values as `conflict`; Tobikan's HTML guide was still 503 so its hours come from the museum's own access PDF; TNM now lists card/e-money payment and a security-screening notice; NMWA lists a 2027 collection closure; Kiyomizu's regular closing time (18:00 / 18:30) and Meiji Jingu's November gate times were added.

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
| Wakiya 一笑美茶樓 | Official notice: temporarily closed for rebuilding from 16 Oct 2026 |
| 道頓堀グリコサイン | Sign renewal works announced from Dec 2026 |
| 東京ミッドタウン | Official notice: facility closure 21–23 Nov 2026 |
| 青山グランドホテル (川上庵の建物) | Official data-breach notice on the hotel site |
| 思い出横丁の各店 | Association listings dated 2021; treated as secondary |
| 成蔵 / 不二 / étéco / BAKER Aoyagi / 分とく山 / 秋本 / 明寂 / おさめ / ASO | Official address is in a neighbouring area to the one the listing is filed under (南阿佐ヶ谷 / 池尻大橋 / 池ノ上 / 東北沢 / 南麻布 / 麹町 / 西麻布 / 目白 / 代官山); listing left unchanged, flagged for the owner |
Apart from the Wakiya rebuilding closure above, no closure or relocation suspicion was found among the 371 researched listings; no listing was removed or edited.

## Resuming the remaining 155
1. `data/research-ledger.json` → take rows with `status:"not-started"`, lowest `batch` first (batch 2 is complete; the 155 left are all batch 3 food, drink and shop listings).
2. For each: find the official site (search engine, then the venue's own SNS), read hours / closed days / fees / booking / payment / access / language / accessibility / notices; record one field per item with its URL and today's date; mark `unverified` where nothing is found and `conflict` where sources disagree.
3. Put the records in a batch JSON and run `node scripts/add_essentials_records.mjs batch.json` (merges into `data/visitor-essentials.json`, regenerates `data/visitor-essentials.js` and the ledger), then `node --test tests/*.test.mjs tests/*smoke.mjs`.
4. Never edit `const DATA`; never delete a listing — a suspected closure is a `flags` entry on the record.
