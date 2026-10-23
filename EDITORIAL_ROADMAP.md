# Encounter Japan — Editorial Product Roadmap (2026-10-23)

## Intent
Make this a distinctly authored independent Japan culture publication, not a restaurant directory in fashionable clothing. An address database is infrastructure; stories, neighborhood point of view, photos, and carefully chosen routes are the front door.

## Owner's priorities (in this order)
1. **English venue introductions and area search** — Each entry needs a *fact-grounded* English deck or description, suitable for human editorial review. Do not generate invented atmosphere, awards, popularity, owner stories, prices, or opening conditions. Preserve Japanese name and Maps URL. Support stable region/area+text filtering, shareable queries, backwards/forwards state.
2. **Theme- and area-based walking routes** — Individual route pages with introductory story, real stops, maps, route verification statuses. Pending confirmation of identity, order, walkability and current hours: clearly DRAFT, and suppress distance/minute estimates.
3. **Price, reservations, access** — Per-field source URL, checked date, verification state and optional display. Never infer absent data.
4. **Saved places and sharing** — Local favorites with explicit share link. No user accounts without owner approval; don't transmit saved interests automatically.
5. **Original photography and mobile** — Human-led photo art direction; verify licensing. Avoid passing generic Tokyo imagery off as specific shops. Strong responsive editorial hierarchy from 320px up.
6. **Individual SEO-oriented pages** — Genuine per-place pages and neighborhood pages with unique factual and editorial copy, appropriate canonicals/sitemaps/structured data. No auto-generated duplicate/doorway pages and no unapproved production changes.
7. **AI concierge** — Future phase: recommendations based on verified guide inventory, transparent reasoning, no fake venue logistics, source-based current data, and cost/privacy controls.

## Current code branch status
- Draft PR #1 is **a design/prototype**, NOT production publication.
- Current main branch is one legacy HTML page with a 526-entry dataset; it is *not* the Claude standalone preview.
- Branch now includes experimental photographic editorial feature sections using licensed CC0 city images, with source links and clear non-venue context.
- Adds a browser-local saved-address list and link sharing; needs mobile/functional browser QA.
- Contains draft walking prompts; *not yet* researched full itineraries.
- English introductions for all 526 entries, sourced practical details, SEO detail routes, and AI concierge are **not implemented**.
- Do not merge or deploy this branch before visual, accessibility, and functionality acceptance tests.

## Quality gates before production
- 526 entry count and original names/categories/Maps URLs identical to approved baseline or explicitly reconciled.
- No deleted entities reintroduced; keep L146 桃花林 / L241 中華そば 多賀野 / L507 Freehouse THE YEAST; exclude L221/L401 and 富ヶ谷スプリングス.
- Verify load, image sources, link functionality, accessibility, mobile widths 320/390/768/1280, filter actions, saved/share behavior, browser history.
- New narrative prose must be clearly distinguished from sourced venue claims.
- Do not directly push/merge main, modify DNS, change SEO canonicals or brand/domain, or publish before explicit owner authorization.
