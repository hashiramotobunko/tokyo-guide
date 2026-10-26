# Encounter Japan — editorial pilot verification
Status: **Draft branch only**, checked 2026-10-23

## What was implemented
- The existing 526 venues and Google Maps link values remain unchanged between `main` and this PR branch. Compared the 526 name+Maps pairs in order: **526/526 identical**.
- Unified region, area, category, interest and Japanese/English keyword filtering. State can be shared in the URL, including sort direction; browser back and forward are handled.
- Three **draft thematic neighborhood collections** built from source listings, not invented locations:
  1. Jimbocho: MAIDENS SHOP JIMBOCHO / MIZUNO TOKYO / 三燈舎
  2. Shibuya: Hi-Fi Disco Bar Chaos / MUSIC BAR BOUNCE / THE MUSIC BAR -CAVE SHIBUYA-
  3. Kyoto Higashiyama: 清水寺 / 八坂神社 / 南座 / 甘味どころ ぎをん 小森
- English descriptions for **six** carefully selected listings, each with an explicit source link. This is an editorial pilot; **the other 520 have not acquired authored English introductions.**
- Initial browser-local saved addresses and short share links, with no account requirement.

## Claim-by-claim source ledger (checked 2026-10-23)
| Listing | Scope of English claim | Source |
|---|---|---|
| MAIDENS SHOP JIMBOCHO | Fashion/vintage selection, coffee stand, Sarugakucho location | https://maidens-shop.jp/2026/03/06/177/ |
| MIZUNO TOKYO | Kanda-Ogawamachi sporting equipment and clothing flagship | https://jpn.mizuno.com/shop/globalflag_tokyo_en |
| 三燈舎 | South Indian Kerala-style meals and tiffin; meaning of Santosham | https://santosham.tokyo/about |
| 清水寺 | The stage's purpose in worship | https://www.kiyomizudera.or.jp/en/learn/ |
| 南座 | Kyoto's historic theater and kabuki traditions | https://www.kyoto-kankou.or.jp/info_search/3696 |
| 甘味どころ ぎをん 小森 | Traditional sweets, machiya and former teahouse | https://www.kyoto-kankou.or.jp/info_search/7745 |

These links substantiate concise editorial copy, **not** real-time operating status.

## Original illustration asset ledger
- `assets/editorial/night-street.svg` — original vector illustration of a **fictional** Tokyo record-bar street, late-Showa/city-pop sensibility. Used for the hero, secondary story, and Shibuya walking-idea card. Not a photograph of a recommended business.
- `assets/editorial/day-bookshop.svg` — original vector illustration of a **fictional** city bookshop and cafe, used for the first editorial story and Jimbocho card.
- Both are included as text-based SVGs in the draft PR. The earlier CC0 photos were removed from the HTML; the site no longer loads third-party photograph URLs for these sections.
- The owner's approved **raster** city-pop illustrations have been preserved separately in `ENCOUNTER_JAPAN_CITYPOP_ART_ASSETS_2026-10-23.zip`. They are **not uploaded to the repository** due to the current connector's binary-file transfer limit. For exact reproduction, upload the optimized AVIF images using a native git workflow and replace the SVG sources after visual review.
- Illustrator inspirations refer to an **era and general visual vocabulary**, not imitation of a specific living illustrator.

## Instagram
- A validated, optional profile link mechanism is included in header and footer. Since no owner-confirmed Instagram handle/URL was provided, `EJ_INSTAGRAM_URL` is empty and **no clickable link is shown**. Supply the real profile URL before enabling it.

## Not yet verified
- Real-world walking routes: transitions, sequence, walking times, entrance restrictions, business hours and accessibility.
- Browser-rendered layout, images loading, console errors and interactive behavior at 320 / 390 / 768 / 1280 widths **have not yet been independently checked**.
- The English descriptions for the remaining 520 listings, price/reservation/access coverage, individual SEO pages and AI concierge are not complete.

## Suggested review
1. Unzip the draft branch and open `tokyo-guide_2.html` in a browser; review editorial pace and mobile layout.
2. Check the English descriptions against source links and validate route selections on a map.
3. Run `node --test tests/editorial-smoke.mjs` to perform read-only syntax/data and route-reference checks.
4. After browser QA and editorial review, decide whether to merge. **Do not merge or deploy without owner authorization.**

## 2026-10-26 follow-on editorial verification (Draft)
These are fixed, source-checked English introductions; they do not confirm today's access, prices, reservations, exhibitions, or opening hours.

| Listing | Fixed editorial fact checked | Official source |
|---|---|---|
| 東京国立博物館 | 1872 origins and 1882 move to Ueno | https://www.tnm.jp/modules/r_free_page/index.php?id=143&lang=en |
| 国立西洋美術館 | Le Corbusier's 1959 main building and forecourt | https://www.nmwa.go.jp/en/about/building.html |
| 東京都美術館 | 1926 establishment and exhibitions | https://www.tobikan.jp/en/ |
| 明治神宮 | 1920 founding, forest and seasonal schedule | https://www.meijijingu.or.jp/en/about/ |

English intros now have ten editorial records, not 526. The separate practical visitor data remains limited to the original six pilot destinations, with field-level source/date labels and a prompt to recheck. All ten walking ideas remain **DRAFT**; no ground-truth walking distances or hours have been asserted.
