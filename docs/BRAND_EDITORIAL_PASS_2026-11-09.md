# Encounter Japan — brand and editorial pass (2026-11-09)

Status: review branch only. No merge to `main`, publication, DNS change, canonical-domain change, or site-wide rename.

## What changed

- Added `about.html` as a full editorial About page, not an operator profile.
- Expressed **Shakedown Street** as the project's way of looking at a city, explicitly not as a confirmed site rename.
- Used **STAY CURIOUS. STAY HUNGRY.** as the closing brand statement.
- Kept the site name **Encounter Japan** in titles, metadata, navigation, and wordmarks.
- Added About entry points in the desktop navigation, home-page manifesto, closing block, and footer.
- Rebuilt the four-way home-page index as an uneven editorial sequence rather than four equal cards.
- Reworked the original illustrations into a black, asymmetrical spread with one dominant plate and one overlapping plate. The artwork remains labelled as illustration in alt text and is never presented as a real venue.
- Reframed the route section as **FOLLOW THE THREAD**. Each route now presents its editorial reason in a dedicated **Why this walk** block before the practical facts and stops.
- Added visible route numbering and deliberately varied route offsets while keeping the source details, status chips, directions, filters, and verification panels intact.

## What did not change

- 526 approved listings, their names, order, and Google Maps URLs.
- 10 routes, 35 stops, and route-verification records.
- Region, neighbourhood, keyword, Japanese/English search, themes, saved places, and shareable URL state.
- Visitor essentials and Instagram verification layers.
- Existing public canonical URLs and deployment settings.

## Verification

- Static and data checks: **66 passed, 0 failed**.
- Data guard compared the current branch with `origin/main`: all 526 names and Google Maps URLs are identical and in the same order.
- Browser checks at 320, 390, 768, and 1280 px:
  - no horizontal overflow;
  - no page script errors;
  - every photograph and illustration decoded;
  - About has no overflow and both images load at every width;
  - all 21 regions remain available;
  - Japanese search, theme filtering, route filtering, URL state, Visitor essentials, source citations, and map directions remain operable.

The responsive browser test can use a non-default local preview with `EJ_TEST_BASE_URL`, avoiding collisions with another local server.

## Review items still open

- Confirm the final product name before any global rename or domain work. This pass deliberately keeps Encounter Japan.
- Decide whether **Shakedown Street** should remain an editorial idea, become an issue/series title, or eventually become the product name.
- The three approved city-pop illustrations remain the current artwork set. A future art commission could broaden the places and cultural subjects represented, but it is not required for this pass.
- The 10 routes remain map-checked drafts and are still not field-walked.
- Instagram research holds, visitor-data caveats, and the existing workflow-scope patch remain as documented in the current PR.
