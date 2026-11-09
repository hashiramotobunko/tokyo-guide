#!/usr/bin/env python3
"""Stage 1 - harvest Instagram links from the venues' own websites.

No API cost: plain HTTP. For every candidate page on the venue's own domain we
fetch the page (and its site root), then record every instagram.com/<handle>
link found there. The page that carries the link IS the evidence.
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import httpx

HERE = Path(__file__).parent
TARGETS = HERE / "targets.json"
OUT = HERE / "stage1_results.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

# instagram.com/<handle> - reject content and system paths, keep profiles only
IG = re.compile(
    r"https?://(?:www\.)?instagram\.com/((?!p/|reel/|reels/|tv/|stories/|explore/|accounts/|directory/|about/|developer/|legal/|privacy/)"
    r"[A-Za-z0-9._]{1,30})/?",
    re.I,
)
NOT_A_HANDLE = {"instagram", "explore", "accounts", "p", "reel", "reels", "tv", "stories", "direct", "challenge"}


def handles_in(html: str) -> list[str]:
    out = []
    for m in IG.finditer(html):
        h = m.group(1).strip(".").lower()
        if h and h not in NOT_A_HANDLE and not h.isdigit():
            out.append(h)
    return list(dict.fromkeys(out))


def fetch(client: httpx.Client, url: str) -> tuple[object, str]:
    """Return (status or error name, html). TLS problems are recorded, not bypassed."""
    try:
        r = client.get(url, follow_redirects=True, timeout=20.0)
        ctype = r.headers.get("content-type", "")
        if "html" not in ctype and "text" not in ctype:
            return r.status_code, ""
        return r.status_code, r.text[:400_000]
    except Exception as exc:  # network, TLS, DNS, timeout
        return type(exc).__name__, ""


def work(target: dict) -> dict:
    found: list[dict] = []
    tried: list[dict] = []
    with httpx.Client(headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"}) as client:
        pages: list[str] = []
        for u in target["official_urls"]:
            pages.append(u)
            parts = urlparse(u)
            root = f"{parts.scheme}://{parts.netloc}/"
            if root not in pages:
                pages.append(root)
        for url in pages[:6]:
            status, html = fetch(client, url)
            tried.append({"url": url, "status": status})
            if not html:
                continue
            for h in handles_in(html):
                found.append({"handle": h, "evidence_url": url, "method": "linked-from-own-site"})
    return {
        "id": target["id"],
        "pages_tried": tried,
        "candidates": found,
        "seed_instagram": target.get("seed_instagram", []),
    }


def main() -> int:
    targets = json.loads(TARGETS.read_text(encoding="utf-8"))
    todo = [t for t in targets if t["official_urls"]]
    print(f"stage 1: fetching sites for {len(todo)} of {len(targets)} venues", flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        for i, res in enumerate(pool.map(work, todo), 1):
            results.append(res)
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}", flush=True)

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    hit = [r for r in results if r["candidates"]]
    reach = sum(1 for r in results if any(p["status"] == 200 for p in r["pages_tried"]))
    print(f"\nsites reachable : {reach}/{len(todo)}")
    print(f"with an Instagram link on their own site: {len(hit)}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
