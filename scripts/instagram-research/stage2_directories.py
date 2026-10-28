#!/usr/bin/env python3
"""Stage 2 - reach the venue's own site through the directory pages we already cite.

Still no API cost. For venues with no Instagram candidate yet, we read the
directory / media pages the existing research layer already recorded, follow the
outbound link that looks like the venue's own website, and look for an Instagram
link there.

Guard against following the wrong link: a discovered site only counts if the
venue's own name appears on the page that carries the Instagram link. An
Instagram URL printed on a directory page is kept separately as a weak candidate
- a directory is not the venue's own page, so it never yields VERIFIED.
"""
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

HERE = Path(__file__).parent
REPO = Path("/Users/hashiramototetsuya/Documents/Claude_新規事業/tokyo-guide")
OUT = HERE / "stage2_results.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"

IG = re.compile(
    r"https?://(?:www\.)?instagram\.com/((?!p/|reel/|reels/|tv/|stories/|explore/|accounts/|directory/|about/|developer/|legal/|privacy/)"
    r"[A-Za-z0-9._]{1,30})/?",
    re.I,
)
NOT_A_HANDLE = {"instagram", "explore", "accounts", "p", "reel", "reels", "tv", "stories", "direct", "challenge"}
HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)

# never treated as the venue's own website
NOT_OWN = {
    "tabelog.com", "s.tabelog.com", "retty.me", "r.gnavi.co.jp", "gnavi.co.jp", "www.hotpepper.jp",
    "hitosara.com", "restaurant.ikyu.com", "www.ikyu.com", "aumo.jp", "www.walkerplus.com",
    "rurubu.jp", "san-tatsu.jp", "hamoni.jp", "www.timeout.jp", "www.jalan.net",
    "travel.rakuten.co.jp", "www.tripadvisor.jp", "www.tripadvisor.com", "www.ozmall.co.jp",
    "loco.yahoo.co.jp", "map.yahoo.co.jp", "www.google.com", "maps.google.com", "google.com",
    "goo.gl", "maps.app.goo.gl", "www.facebook.com", "facebook.com", "twitter.com", "x.com",
    "www.youtube.com", "youtube.com", "www.instagram.com", "instagram.com", "line.me",
    "page.line.me", "lin.ee", "ja.wikipedia.org", "en.wikipedia.org", "www.amazon.co.jp",
    "apps.apple.com", "play.google.com", "www.tiktok.com", "note.com", "ameblo.jp",
    "www.yelp.com", "foursquare.com", "tablecheck.com", "www.tablecheck.com", "toreta.in",
    "booking.com", "www.booking.com", "www.agoda.com", "www.expedia.co.jp", "pokeapi.co",
    "www.pinterest.jp", "b.hatena.ne.jp", "getpocket.com", "www.addtoany.com",
}
JUNK_SUBSTR = ("doubleclick", "googletagmanager", "google-analytics", "gstatic", "cloudflare",
               "adservice", "criteo", "yimg.jp", "ssl.gstatic", "fonts.googleapis", "cdn.")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[\s　・･'\"’”!！\-－—–/／（）()【】\[\]]", "", s)


def handles_in(html: str) -> list[str]:
    out = []
    for m in IG.finditer(html):
        h = m.group(1).strip(".").lower()
        if h and h not in NOT_A_HANDLE and not h.isdigit():
            out.append(h)
    return list(dict.fromkeys(out))


def fetch(client: httpx.Client, url: str) -> tuple[object, str]:
    try:
        r = client.get(url, follow_redirects=True, timeout=20.0)
        ctype = r.headers.get("content-type", "")
        if "html" not in ctype and "text" not in ctype:
            return r.status_code, ""
        return r.status_code, r.text[:500_000]
    except Exception as exc:
        return type(exc).__name__, ""


def candidate_sites(page_url: str, html: str) -> list[str]:
    """Outbound links from a directory page that could be the venue's own site."""
    here = urlparse(page_url).netloc.lower()
    seen, out = set(), []
    for href in HREF.findall(html):
        href = unescape(href).strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        url = urljoin(page_url, href)
        if not url.startswith("http"):
            continue
        host = urlparse(url).netloc.lower()
        if not host or host == here or host in NOT_OWN:
            continue
        if any(j in host for j in JUNK_SUBSTR):
            continue
        root = f"{urlparse(url).scheme}://{host}/"
        if root in seen:
            continue
        seen.add(root)
        out.append(root)
    return out[:8]


def work(item: dict) -> dict:
    target, sources = item["target"], item["sources"]
    names = [norm(target["name"])]
    if target["name_en"]:
        names.append(norm(target["name_en"]))
    names = [n for n in names if len(n) >= 2]

    tried, found, weak = [], [], []
    with httpx.Client(headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"}) as client:
        sites: list[str] = []
        for src in sources[:4]:
            status, html = fetch(client, src)
            tried.append({"url": src, "status": status, "role": "directory"})
            if not html:
                continue
            for h in handles_in(html):
                weak.append({"handle": h, "evidence_url": src, "method": "printed-on-directory-page"})
            for site in candidate_sites(src, html):
                if site not in sites:
                    sites.append(site)

        for site in sites[:5]:
            status, html = fetch(client, site)
            tried.append({"url": site, "status": status, "role": "candidate-own-site"})
            if not html:
                continue
            text = norm(re.sub(r"<[^>]+>", " ", html))
            if not any(n in text for n in names):
                continue  # the venue's name is not on this page: not its site
            for h in handles_in(html):
                found.append({"handle": h, "evidence_url": site, "method": "linked-from-own-site-via-directory"})
    return {"id": target["id"], "pages_tried": tried, "candidates": found, "weak_candidates": weak}


def main() -> int:
    targets = {t["id"]: t for t in json.loads((HERE / "targets.json").read_text(encoding="utf-8"))}
    ledger = json.loads((HERE / "ledger.json").read_text(encoding="utf-8"))
    need = [r["id"] for r in ledger if r["status"] == "NOT_FOUND"]

    ess = {r["key"]: r for r in json.loads((REPO / "data/visitor-essentials.json").read_text(encoding="utf-8"))["records"]}
    todo = []
    for tid in need:
        t = targets[tid]
        rec = ess.get(f"{t['region']}|{t['place_key']}")
        srcs: list[str] = []
        if rec:
            for f in rec.get("fields", []):
                s = f.get("src", "")
                if s.startswith("http") and "instagram.com" not in s and s not in srcs:
                    srcs.append(s)
        if srcs:
            todo.append({"target": t, "sources": srcs})

    print(f"stage 2: {len(todo)} of {len(need)} unresolved venues have a directory/media page to follow", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        for i, res in enumerate(pool.map(work, todo), 1):
            results.append(res)
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}", flush=True)

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    hit = [r for r in results if r["candidates"]]
    weak = [r for r in results if not r["candidates"] and r["weak_candidates"]]
    print(f"\nreached the venue's own site AND found Instagram there: {len(hit)}")
    print(f"only an Instagram printed on a directory page (weak): {len(weak)}")
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
