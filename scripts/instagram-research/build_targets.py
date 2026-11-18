#!/usr/bin/env python3
"""Build the 526-row research target list.

Source of truth: publish526_2026-10-22/deliverable/FINAL_APPLIED_526.csv
(verified byte-identical to the live site's DATA: names, Google Maps URLs, order).
Candidate official URLs are joined in from the repo's own research layer
(data/visitor-essentials.json) - we never invent one.
"""
import csv, json, re, sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path("/Users/hashiramototetsuya/Documents/Claude_新規事業/tokyo-guide")
MASTER = REPO / "publish526_2026-10-22/deliverable/FINAL_APPLIED_526.csv"
ESSENTIALS = REPO / "data/visitor-essentials.json"
OUT = Path(__file__).parent / "targets.json"

# Aggregators / directories / review sites: never treated as the venue's own site.
DIRECTORY_HOSTS = {
    "retty.me", "tabelog.com", "s.tabelog.com", "r.gnavi.co.jp", "www.hotpepper.jp",
    "hitosara.com", "restaurant.ikyu.com", "www.ikyu.com", "aumo.jp", "www.walkerplus.com",
    "rurubu.jp", "san-tatsu.jp", "hamoni.jp", "www.timeout.jp", "www.jalan.net",
    "travel.rakuten.co.jp", "www.tripadvisor.jp", "www.tripadvisor.com", "maps.google.com",
    "www.google.com", "goo.gl", "maps.app.goo.gl", "tabechoku.com", "www.ozmall.co.jp",
    "www.hotpepper.jp", "loco.yahoo.co.jp", "www.facebook.com", "ja.wikipedia.org",
    "en.wikipedia.org", "twitter.com", "x.com", "www.youtube.com",
}

PLACE_ID = re.compile(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)")


def place_key(url: str) -> str:
    m = PLACE_ID.search(url)
    return m.group(1) if m else ""


def is_own_site(url: str) -> bool:
    if not url.startswith("http"):
        return False
    host = urlparse(url).netloc.lower()
    if host in DIRECTORY_HOSTS:
        return False
    # an Instagram URL is a candidate handle, not a website to crawl for links
    return "instagram.com" not in host


def main() -> int:
    rows = list(csv.DictReader(MASTER.open(encoding="utf-8-sig")))
    if len(rows) != 526:
        sys.exit(f"expected 526 master rows, got {len(rows)}")

    ess = {r["key"]: r for r in json.loads(ESSENTIALS.read_text(encoding="utf-8"))["records"]}

    targets = []
    for row in rows:
        key = f"{row['region']}|{place_key(row['url'])}"
        rec = ess.get(key)
        sites, seeds = [], []
        if rec:
            if rec.get("website"):
                (seeds if "instagram.com" in rec["website"] else sites).append(rec["website"])
            for f in rec.get("fields", []):
                src = f.get("src", "")
                if f.get("st") == "official" and src.startswith("http"):
                    sites.append(src)
                elif "instagram.com" in src:
                    seeds.append(src)
        targets.append({
            "id": f"L{int(row['live_order']):03d}",
            "live_order": int(row["live_order"]),
            "place_key": place_key(row["url"]),
            "name": row["name"],
            "name_en": row["en"],
            "region": row["region"],
            "area": row["area"],
            "cat": row["cat"],
            "maps_url": row["url"],
            # candidate pages on the venue's own domain, de-duplicated, order preserved
            "official_urls": list(dict.fromkeys(u for u in sites if is_own_site(u))),
            # Instagram URLs the existing research layer already recorded
            "seed_instagram": list(dict.fromkeys(seeds)),
        })

    OUT.write_text(json.dumps(targets, ensure_ascii=False, indent=1), encoding="utf-8")
    with_site = sum(1 for t in targets if t["official_urls"])
    with_seed = sum(1 for t in targets if t["seed_instagram"])
    print(f"targets: {len(targets)}")
    print(f"  with at least one own-domain URL: {with_site}")
    print(f"  with an Instagram URL already recorded: {with_seed}")
    print(f"  with neither (search needed): {sum(1 for t in targets if not t['official_urls'] and not t['seed_instagram'])}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
