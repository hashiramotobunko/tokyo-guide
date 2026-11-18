#!/usr/bin/env python3
"""Stage 6 - a third pass over the rows still ambiguous, using the audit list's own sources.

The 557-row Maps audit list carries, per row, an address from earlier independent
research and sometimes an external source URL. Those source URLs are new material
this project has not read before. For each ambiguous row we read the given page,
follow the outbound link that looks like the venue's own website, and look for an
Instagram link there - the same admissible evidence as stage 1 (a link on a page of
the venue's own). An Instagram handle merely printed on a directory page is kept
separately as a weak candidate and never yields VERIFIED.
"""
import json, re, unicodedata
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

HERE = Path(__file__).parent
OUT = HERE / "stage6_results.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

IG = re.compile(
    r"https?://(?:www\.)?instagram\.com/((?!p/|reel/|reels/|tv/|stories/|explore/|accounts/|directory/|about/|developer/|legal/|privacy/)"
    r"[A-Za-z0-9._]{1,30})/?", re.I)
NOT_A_HANDLE = {"instagram", "explore", "accounts", "p", "reel", "reels", "tv", "stories", "direct", "challenge"}
HREF = re.compile(r'href=["\']([^"\']+)["\']', re.I)
NOT_OWN = {
    "tabelog.com", "s.tabelog.com", "retty.me", "r.gnavi.co.jp", "gnavi.co.jp", "www.hotpepper.jp",
    "hitosara.com", "restaurant.ikyu.com", "www.ikyu.com", "aumo.jp", "www.walkerplus.com",
    "rurubu.jp", "san-tatsu.jp", "hamoni.jp", "www.timeout.jp", "www.jalan.net", "timeout.jp",
    "travel.rakuten.co.jp", "www.tripadvisor.jp", "www.tripadvisor.com", "www.ozmall.co.jp",
    "loco.yahoo.co.jp", "map.yahoo.co.jp", "www.google.com", "maps.google.com", "google.com",
    "goo.gl", "maps.app.goo.gl", "www.facebook.com", "facebook.com", "twitter.com", "x.com",
    "www.youtube.com", "youtube.com", "www.instagram.com", "instagram.com", "line.me",
    "page.line.me", "lin.ee", "ja.wikipedia.org", "en.wikipedia.org", "www.amazon.co.jp",
    "apps.apple.com", "play.google.com", "www.tiktok.com", "note.com", "ameblo.jp",
    "www.yelp.com", "foursquare.com", "tablecheck.com", "www.tablecheck.com", "toreta.in",
    "booking.com", "www.booking.com", "www.agoda.com", "www.expedia.co.jp", "savorjapan.com",
    "kinarino.jp", "yomuno.jp", "www.makuake.com", "makuake.com", "intojapanwaraku.com",
    "www.tokyoweekender.com", "tokyoweekender.com", "www.inshokuten.com", "inshokuten.com",
    "voyapon.com", "www.cotaru.co", "cotaru.co", "www.pinterest.jp", "b.hatena.ne.jp",
}
JUNK = ("doubleclick", "googletagmanager", "google-analytics", "gstatic", "cloudflare",
        "adservice", "criteo", "yimg.jp", "fonts.googleapis", "recaptcha", "cdn.")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
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
        if not host or host == here or host in NOT_OWN or any(j in host for j in JUNK):
            continue
        root = f"{urlparse(url).scheme}://{host}/"
        if root in seen:
            continue
        seen.add(root)
        out.append(root)
    return out[:10]


def work(item: dict) -> dict:
    names = [norm(item["name"])]
    extra = re.sub(r"[（(].*?[)）]", "", item["name"])
    if norm(extra) not in names:
        names.append(norm(extra))
    names = [n for n in names if len(n) >= 2]

    tried, found, weak = [], [], []
    with httpx.Client(headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"}) as client:
        sites: list[str] = []
        for src in item["sources"]:
            host = urlparse(src).netloc.lower()
            status, html = fetch(client, src)
            own = host not in NOT_OWN and not any(j in host for j in JUNK)
            tried.append({"url": src, "status": status, "role": "own-site" if own else "directory"})
            if not html:
                continue
            hs = handles_in(html)
            if own:
                text = norm(re.sub(r"<[^>]+>", " ", html))
                named = any(n in text for n in names)
                for h in hs:
                    found.append({"handle": h, "evidence_url": src,
                                  "method": "linked-from-own-site", "name_on_page": named})
            else:
                for h in hs:
                    weak.append({"handle": h, "evidence_url": src, "method": "printed-on-directory-page"})
                for s in candidate_sites(src, html):
                    if s not in sites:
                        sites.append(s)

        for site in sites[:6]:
            status, html = fetch(client, site)
            tried.append({"url": site, "status": status, "role": "candidate-own-site"})
            if not html:
                continue
            text = norm(re.sub(r"<[^>]+>", " ", html))
            if not any(n in text for n in names):
                continue
            for h in handles_in(html):
                found.append({"handle": h, "evidence_url": site,
                              "method": "linked-from-own-site-via-directory", "name_on_page": True})
    return {"id": item["id"], "name": item["name"], "pages_tried": tried,
            "candidates": found, "weak_candidates": weak}


def main() -> int:
    todo = json.loads((HERE / "stage6_queue.json").read_text(encoding="utf-8"))
    print(f"stage 6: reading sources for {len(todo)} rows", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, res in enumerate(pool.map(work, todo), 1):
            results.append(res)
            if i % 10 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    hit = [r for r in results if r["candidates"]]
    print(f"\nrows with an Instagram link on a page of the venue's own: {len(hit)}")
    for r in hit:
        print("  ", r["id"], r["name"], "->", sorted({c["handle"] for c in r["candidates"]}))
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
