# Encounter Japan — City-pop Illustration Pass (2026-10-23)

## Art direction

Owner approved **original late-Showa city-pop-inspired urban editorial art**, with modern Tokyo streets, music bars, books, coffee, architectural geometry, clean lines, luminous dusk color, and refined fashion mood.

This is **not a request to copy Eizin Suzuki or any other individual illustrator**. Avoid recognizable compositions, color-map cloning, signatures, specific trademarked storefront graphics, album covers, or copyrighted Maps/business photographs.

## Implemented in this draft PR

- Current source includes independently drawn `assets/editorial/night-street.svg`, `assets/editorial/day-bookshop.svg` and `assets/editorial/rooftop-citypop.svg`, each expressly labeled an imagined scene. The third art piece now provides a distinct illustration for the second editorial story.
- Hero, editorial stories, and themed walking panels integrate those SVG assets.
- The hero and page compositions received a further magazine-cover composition pass, reducing the symmetrical pitch-deck feel. Responsive CSS overrides cover desktop, tablet, and narrow mobile widths.
- Data not touched: approved **526 names** and **526 Google Maps destination URLs** remain unchanged.
- Existing Instagram hook is intentionally disabled via `EJ_INSTAGRAM_URL = ""` until the owner supplies the real profile URL. Do **not** guess a social account.

## User-approved generated illustrations (local preview asset package)

A separate **local** artifact named `ENCOUNTER_JAPAN_CITYPOP_IMAGE_PREVIEW_2026-10-23.zip` combines three generated city-pop artwork images with a self-contained site-preview HTML, using the owner's existing 526-entry prototype:

- `雨の東京_ムーンライトレコードバー.png` → the Tokyo night/record-bar mood.
- `本とコーヒーの東京散歩.png` → the Tokyo books/coffee street mood.
- `夕暮れのシティポップ_ルーフトップ.png` → the city music/lounge mood.

Important: these **generated raster images are not yet present in this GitHub repository**. The GitHub connector in the current session supports UTF-8 file updates and base64 Git blobs, but had no direct binary-container-file upload. The SVG assets in the PR are separate illustrations rather than raster replicas.

To put the approved high-resolution art online, add optimized WebP/AVIF versions of these images as actual Git blobs, update the three page references, retain visible captions identifying them as imaginative artwork, and verify source and licensing provenance. Do not use a generic Tokyo illustration as evidence of a specific venue's exact physical appearance.

Do not label any artwork as an authentic exterior, a real menu item, a current event, or a verified store interior.

## Verification status

- Static parity: 526 entries and 526 Google Maps URL occurrences maintained after the CSS-only PR change.
- The tested local ZIP `ENCOUNTER_JAPAN_CITYPOP_TESTED_PREVIEW_2026-10-23.zip` includes three raster illustration assets and a 526-link HTML preview, plus browser QA results and comparative screenshots. In that **local copy**, 320, 390, 768 and 1280px had no horizontal overflow and no page-level JS errors when rendered via injected content with History APIs stubbed for the sandbox; searching 多賀野, 0 results, reset and switching to Kyoto were confirmed at 390px. This QA **does not verify GitHub's separate SVG implementation**.
- Direct navigation to a sandbox/local URL is blocked (ERR_BLOCKED_BY_ADMINISTRATOR), but a **rendered browser QA workaround succeeded on the separate local image-preview HTML** using `page.set_content` and inline images. The exact GitHub SVG version has **not been independently rendered in a browser** here.
- A separate QA pass is required after the raster files are committed; check mobile overflow, visual readability, source loading, asset compression, alternate text, and accessibility.
- Instagram is still waiting for an actual authorized account URL.

## Release gate

This PR is **Draft**, without merges or deployment. Do not change production branding, canonical URLs, DNS, or live content on the strength of this prototype alone.
