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

## Counts (2026-10-27, after commit 6e5cfec)
| Measure | Count |
|---|---|
| Listings researched (record in the data layer) | **526 of 526** |
| Records with at least one official-source field | 150 |
| Records with secondary sources only (dated media, directories, booking platforms, review sites, associations) | 233 |
| Records with nothing confirmable (every field unverified, no value shown) | 143 — mostly small bars, izakaya and neighbourhood eateries with no web presence beyond Google Maps, plus 15 official sites that could not be read (429 rate-limit, 503, DNS or TLS failures) |
| Records holding a conflict field (sources disagree; both values stored) | 34 |
| Fields recorded | 1,768 (official 490 · secondary 637 · conflict 38 · unverified 588 · not applicable 15) |
| Official website recorded | 174 |
| Unique source URLs cited | 458 |

### Coverage by item (records with a value / of which from an official source)
| Item | Any source | Official |
|---|---|---|
| Opening hours | 288 | 105 |
| Closing days | 199 | 59 |
| Fees / admission | 68 | 44 |
| Reservation | 76 | 37 |
| Payment | 65 | 15 |
| Access | 191 | 85 |
| Accessibility / step-free | 28 | 26 |
| English / language support | 10 | 10 |

"526 researched" is not "526 complete": 383 records show at least one confirmed value; 143 show only "not yet confirmed" lines with the reason.

### How the research was done
Batch 1 (36 route stops + Tsutenkaku), batch 2 (101 museums, temples, shrines, landmarks, parks, baths, venues) and batch 3–4 (389 food, drink and shops) were each searched by name and area, then the best page found was opened and read before anything was recorded: official site > public authority / tourism board > booking platform (Ikyu, Hot Pepper, TableCheck, Hitosara, Gurunavi) > dated media or directory > review site. No value was taken from a search snippet alone and no official domain was guessed; where a guessed-domain attempt from an earlier pass failed, the record says so. Quality pass on 2026-10-27 re-read 22 records against official pages (Tokyo Metropolitan Art Museum guide, Okura Toh-Ka-Lin, Daikokuya Asahikawa, Unagi Akimoto, Hashimoto, Sekaido, Shake Shack Gaien, Yanaka Cemetery / Tokyo Parks Association, Sapporo Tourism Association for Aji no Sanpei) and replaced the two dead citations (Kinarino article, Toei 2021 PDF).

Re-verification of the 36 batch-1 records on 2026-10-27: Yonemoto Coffee (official 7:30–20:00), MOD'Z (official, closed Sun) and bar dop (official 19:00–2:00) moved from unverified to official; Soul Sonic Boogie, Ootako, Kameya, First Crop and Spincoaster keep both disagreeing values as `conflict`; Tobikan's hours now come from the museum's HTML guide (read 2026-10-27) including 2026–27 maintenance closures.

## Conflicting sources — how they are handled (2026-10-27)
34 records had a field where two sources disagreed. Official pages were re-read where reachable: bar dop and SOUND BAR MOD'Z now show the official hours with the Instagram variant as a note; 銀座うかい亭's two tables both sit on the official page and are shown as such with the phone number; 亀戸餃子, 八方の湯 and みなぴりかの湯 carry notes explaining the likely cause. The remaining 32 records keep both values. On the page a conflict field now reads, for example, “Hours vary by source — please confirm before visiting.” with a collapsed “See both sources and dates” panel holding both values, their source links, source types and checked dates; the status chip on route cards reads “confirm ahead”. The Visitor essentials section leads with a one-line traveller explanation, the legend, and search and region entry points; the research counts moved into a collapsed “How this information was gathered” panel; the A–Z index of every destination with checked information stays available in a collapsed panel. No value was picked by guesswork.

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
| 15 official sites unreadable on 2026-10-27 | peterluger.co.jp, steak.co.jp (Jackie's), ippodo-tea.co.jp (429); glico.com, daikakuji.or.jp, theobroma.co.jp (503); nodaiwa.co.jp, tomiokahachimangu.or.jp (connection refused); ryoanji.jp, sanjusangendo.jp, toyokawainari-tokyo.jp, kanda-matsuya.jp (TLS configuration); mortons.jp, shogunburger.com (domain gone); takashimaya.co.jp Kyoto hours page (timeout) — secondary values kept, flagged |
| Area filed vs official address | 元祖らーめん大栄 (Kamigyo, filed Sakyo), にこみ鈴や and 花もも (Nakagyo, filed Kamigyo), 開運中華 慶修 (Tokiwadai, filed Kamiitabashi), malca and misola (Gaienmae / omakase, filed Omotesando-Aoyama café), ステーキハウス エメラルド (found in Kitanakagusuku, filed Onna) — listings left unchanged |
| Secondary values older than 2021 | マザー (2020), 三ん寅 (2020), 中華屋 啓ちゃん (2019), パン・デ・フィロゾフ (2017), ドゥワンチャン (2019), 炭火焼肉 深山 (2020) — shown with their dates |
| 鈴の湯 / 橘湯 / 今井湯 | Appear to be Kawasaki (Nakahara) bathhouses; the ward's Feb 2025 PDF lists their hours but could not be text-extracted here |
| Wakiya 一笑美茶樓 | Official notice: temporarily closed for rebuilding from 16 Oct 2026 |
| 道頓堀グリコサイン | Sign renewal works announced from Dec 2026 |
| 東京ミッドタウン | Official notice: facility closure 21–23 Nov 2026 |
| 青山グランドホテル (川上庵の建物) | Official data-breach notice on the hotel site |
| 思い出横丁の各店 | Association listings dated 2021; treated as secondary |
| 成蔵 / 不二 / étéco / BAKER Aoyagi / 分とく山 / 秋本 / 明寂 / おさめ / ASO | Official address is in a neighbouring area to the one the listing is filed under (南阿佐ヶ谷 / 池尻大橋 / 池ノ上 / 東北沢 / 南麻布 / 麹町 / 西麻布 / 目白 / 代官山); listing left unchanged, flagged for the owner |
Apart from the Wakiya rebuilding closure above, no closure or relocation suspicion was found among the 371 researched listings; no listing was removed or edited.

## What a human still has to do
1. Phone or visit the 143 venues with nothing confirmable (list: ledger rows whose record has no valued field); most are small bars and izakaya in Tokyo (85), Hokkaido (17), Osaka (10), Kyoto (9).
2. Re-open the 15 unreadable official sites from a normal browser and replace the secondary values.
3. Decide the 34 conflict records (both values are shown to readers until an editor picks one).
4. Walk the ten routes; the 12 legs flagged `disc` are where the map figures disagree most.
5. Apply `docs/patches/0001-editorial-checks-data-triggers.patch` so CI also runs on `data/**` and `scripts/**` changes (needs the `workflow` scope; see PR body).

To add or correct records: write a batch JSON, run `node scripts/add_essentials_records.mjs batch.json` (merges into `data/visitor-essentials.json`, regenerates `data/visitor-essentials.js` and the ledger), then `node --test tests/*.test.mjs tests/*smoke.mjs`. Never edit `const DATA`; never delete a listing — a suspected closure is a flag on the record.
