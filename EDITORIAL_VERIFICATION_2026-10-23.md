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

## Photograph source ledger
- Tokyo nightlife city photograph: https://commons.wikimedia.org/wiki/File:Night_life_in_Tokyo,_Japan_(54412959018).jpg — Romain Guy, CC0.
- Walking in Shibuya city photograph: https://commons.wikimedia.org/wiki/File:Walk_in_Shibuya.jpg — Syced, CC0.
- Both serve as independent editorial street photography. Neither is presented as a venue photograph.

## Not yet verified
- Real-world walking routes: transitions, sequence, walking times, entrance restrictions, business hours and accessibility.
- Browser-rendered layout, images loading, console errors and interactive behavior at 320 / 390 / 768 / 1280 widths **have not yet been independently checked**.
- The English descriptions for the remaining 520 listings, price/reservation/access coverage, individual SEO pages and AI concierge are not complete.

## Suggested review
1. Unzip the draft branch and open `tokyo-guide_2.html` in a browser; review editorial pace and mobile layout.
2. Check the English descriptions against source links and validate route selections on a map.
3. Run `node --test tests/editorial-smoke.mjs` to perform read-only syntax/data and route-reference checks.
4. After browser QA and editorial review, decide whether to merge. **Do not merge or deploy without owner authorization.**
