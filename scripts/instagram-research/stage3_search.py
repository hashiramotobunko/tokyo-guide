#!/usr/bin/env python3
"""Stage 3 - search the open web, venue by venue, for an Instagram profile.

For every listing still unresolved we run name+place queries against a search
engine and keep only results that are an Instagram *profile* page. The title and
snippet a search engine stores for a profile page is the profile's own bio - the
name, the pinned address, the phone number - which is the one piece of the
profile we can read while Instagram's login wall blocks the page itself.

Nothing is judged here: this stage only collects, with the query and the snippet
kept alongside every candidate so the judgement can be made and shown later.
No API cost; plain HTTP, paced so as not to hammer the engine.
"""
import json, random, re, sys, time, html
from pathlib import Path
from urllib.parse import unquote, parse_qs, urlparse

import httpx

HERE = Path(__file__).parent
CACHE = HERE / "stage3_cache.json"
OUT = HERE / "stage3_results.json"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

PROFILE = re.compile(
    r"^https?://(?:www\.)?instagram\.com/((?!p/|reel/|reels/|tv/|stories/|explore/|accounts/"
    r"|directory/|about/|developer/|legal/|privacy/|web/|graphql)[A-Za-z0-9._]{2,30})/?(?:\?|$)", re.I)

AREA_JA = {
 "Adachi":"足立","Akasaka":"赤坂","Akasaka-Mitsuke":"赤坂見附","Akihabara":"秋葉原","Aoyama":"青山",
 "Asahikawa":"旭川","Asakusa":"浅草","Ashiya":"芦屋","Azabu":"麻布","Azabudai":"麻布台",
 "Bubaigawara":"分倍河原","Chitose-Funabashi":"千歳船橋","Chiyo":"千代","Chuo":"中央","Daikanyama":"代官山",
 "Ebara-Nakanobu":"荏原中延","Ebisu":"恵比寿","Edogawabashi":"江戸川橋","Eifukucho":"永福町",
 "Fukushima-Osaka":"福島","Funabashi":"船橋","Funabori":"船堀","Ginza":"銀座","Gotanda":"五反田",
 "Gotanda / Osaki":"五反田","Hakuba":"白馬","Harajuku":"原宿","Higashi-Nakano":"東中野","Higashi-Ogu":"東尾久",
 "Higashiyama":"東山","Hokkaido":"北海道","Hongo":"本郷","Honmoku":"本牧","Horikiri-Shobuen":"堀切菖蒲園",
 "Ikegami":"池上","Ise":"伊勢","Ishiwara":"石原","Itoshima":"糸島","Jimbocho":"神保町","Jujo":"十条",
 "Kagurazaka":"神楽坂","Kamata":"蒲田","Kameido":"亀戸","Kamigyo":"上京","Kamiitabashi":"上板橋",
 "Kanda":"神田","Kasumigaseki":"霞ヶ関","Kawaramachi":"河原町","Kiba":"木場","Kichijoji":"吉祥寺",
 "Kita":"北","Kita-Sando":"北参道","Kitahorie":"北堀江","Kiyosumi-Shirakawa":"清澄白河","Kobe":"神戸",
 "Koenji":"高円寺","Koiwa":"小岩","Komaba":"駒場","Kumamoto":"熊本","Kyoto":"京都","Marunouchi":"丸の内",
 "Matsudo":"松戸","Meguro":"目黒","Minami-Rinkan":"南林間","Minami-Senju":"南千住","Mitaka":"三鷹",
 "Miyazaki":"宮崎","Monzen-Nakacho":"門前仲町","Musashi-Kosugi":"武蔵小杉","Musashi-Koyama":"武蔵小山",
 "Nagatacho":"永田町","Nagoya":"名古屋","Naha":"那覇","Nakagyo":"中京","Nakameguro":"中目黒","Nakano":"中野",
 "Nakano-Fujimicho":"中野富士見町","Namba":"難波","Nihonbashi":"日本橋","Ningyocho":"人形町","Nippori":"日暮里",
 "Nishi-Azabu":"西麻布","Nishi-Funabashi":"西船橋","Nishi-Shinjuku":"西新宿","Nogata":"野方","Ochiai":"落合",
 "Ofunato":"大船渡","Ogikubo":"荻窪","Okachimachi":"御徒町","Ome":"青梅","Omori":"大森","Omotesando":"表参道",
 "Onna":"恩納","Otaru":"小樽","Oyama":"大山","Roppongi":"六本木","Sakurajosui":"桜上水","Sakyo":"左京",
 "Sangenjaya":"三軒茶屋","Sangubashi":"参宮橋","Sapporo":"札幌","Setagaya":"世田谷","Shibakoen":"芝公園",
 "Shibuya":"渋谷","Shimbashi":"新橋","Shimogyo":"下京","Shimokitazawa":"下北沢","Shimotakaido":"下高井戸",
 "Shin-Sakuradai":"新桜台","Shin-Takashimadaira":"新高島平","Shinjuku":"新宿","Tachikawa":"立川",
 "Takanawa":"高輪","Takanawadai":"高輪台","Tamachi / Mita":"田町","Tenjin-Minami":"天神","Tenma":"天満",
 "Tomigaya":"富ヶ谷","Toranomon":"虎ノ門","Toride":"取手","Toyama":"富山","Tsuruhashi":"鶴橋","Ueno":"上野",
 "Ueno-Sakuragi":"上野桜木","Uguisudani":"鶯谷","Ukyo":"右京","Yokosuka":"横須賀","Yotsuya":"四谷",
 "Yoyogi":"代々木","Yoyogi-Hachiman":"代々木八幡","Yoyogi-Uehara":"代々木上原",
}
CITY_JA = {
 "Tokyo":"東京","Kyoto":"京都","Osaka":"大阪","Hokkaido":"北海道","Chiba":"千葉","Fukuoka":"福岡",
 "Nagano":"長野","Hyogo":"兵庫","Okinawa":"沖縄","Aichi":"愛知","Kanagawa":"神奈川","Yokohama":"横浜",
 "Mie":"三重","Ibaraki":"茨城","Iwate":"岩手","Kumamoto":"熊本","Miyazaki":"宮崎","Tochigi":"栃木",
 "Toyama":"富山",
}
CAT_JA = {
 "Sushi":"寿司","Ramen":"ラーメン","Tsukemen":"つけ麺","Soba":"そば","Izakaya":"居酒屋","Bar":"バー",
 "Bar / Music":"バー","Bar / Sake":"日本酒","Bar / Whisky":"バー","Bar / Wine":"ワインバー",
 "Café":"カフェ","Café / Tea":"カフェ","Bakery":"ベーカリー","Bakery / Café":"ベーカリー",
 "Curry":"カレー","Chinese":"中華","Chinese / Gyoza":"餃子","Yakitori":"焼鳥","Yakiniku":"焼肉",
 "Tempura":"天ぷら","Tonkatsu":"とんかつ","Unagi":"うなぎ","Kaiseki":"懐石","Japanese":"日本料理",
 "Italian":"イタリアン","Bistro / French":"フレンチ","Steak":"ステーキ","Burger":"ハンバーガー",
 "Diner / Teishoku":"定食","Yoshoku":"洋食","Thai":"タイ料理","Jingisukan":"ジンギスカン",
 "Sweets":"スイーツ","Onsen":"温泉","Sento":"銭湯","Hotel":"ホテル","Museum":"美術館","Shrine":"神社",
 "Temple":"寺","Park & Garden":"庭園","Shopping":"ショップ","Shopping Street":"商店街",
 "Restaurant / Bar":"レストラン","Activity":"","Landmark":"","Monument":"","Sightseeing":"",
}


def load(p, d):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else d


class Engine:
    """DuckDuckGo's HTML endpoint, paced and backed off."""

    def __init__(self):
        self.client = httpx.Client(headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.9"},
                                   follow_redirects=True, timeout=30.0)
        self.wait = 2.2

    def search(self, q: str) -> dict:
        for attempt in range(6):
            time.sleep(self.wait + random.uniform(0, 1.3))
            try:
                r = self.client.post("https://html.duckduckgo.com/html/",
                                     data={"q": q, "kl": "jp-jp"})
            except Exception as exc:
                self.wait = min(self.wait * 1.6, 25)
                continue
            if r.status_code == 200 and "result__a" in r.text:
                self.wait = max(2.2, self.wait * 0.9)
                return {"status": 200, "results": self.parse(r.text)}
            if r.status_code == 200:          # a real "no results" page
                return {"status": 200, "results": []}
            self.wait = min(self.wait * 2.0 + 3, 70)
            print(f"    throttled ({r.status_code}), wait now {self.wait:.0f}s", flush=True)
        return {"status": "RATE_LIMITED", "results": []}

    @staticmethod
    def parse(t: str) -> list[dict]:
        blocks = re.split(r'<div class="result[ "]', t)
        out = []
        for b in blocks:
            a = re.search(r'class="result__a" href="([^"]+)"[^>]*>(.*?)</a>', b, re.S)
            if not a:
                continue
            href = html.unescape(a.group(1))
            if href.startswith("//duckduckgo.com/l/") or href.startswith("/l/"):
                qs = parse_qs(urlparse("https:" + href if href.startswith("//") else "https://duckduckgo.com" + href).query)
                href = unquote(qs.get("uddg", [""])[0])
            s = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', b, re.S)
            out.append({
                "url": href,
                "title": html.unescape(re.sub(r"<[^>]+>", "", a.group(2))).strip(),
                "snippet": html.unescape(re.sub(r"<[^>]+>", "", s.group(1))).strip() if s else "",
            })
        return out


def queries(row: dict) -> list[str]:
    name = row["name"].strip()
    area = AREA_JA.get(row["area"], "")
    city = CITY_JA.get(row["region"], "")
    cat = CAT_JA.get(row["cat"], "")
    qs = []
    if area:
        qs.append(f'site:instagram.com "{name}" {area}')
        qs.append(f'"{name}" {area} instagram')
    qs.append(f'site:instagram.com "{name}" {city} {cat}'.rstrip())
    if row.get("name_en"):
        en = re.sub(r"\s*\(.*?\)\s*", "", row["name_en"]).strip()
        if en and en.lower() != name.lower():
            qs.append(f'site:instagram.com "{en}" {area or city}')
    seen, keep = set(), []
    for q in qs:
        if q not in seen:
            seen.add(q)
            keep.append(q)
    return keep


def main() -> int:
    led = load(HERE / "ledger.json", [])
    todo = [r for r in led if r["status"] == "NOT_FOUND"]
    cache = load(CACHE, {})
    done = load(OUT, {})
    eng = Engine()
    print(f"stage 3: {len(todo)} listings, {len(done)} already searched", flush=True)

    for n, row in enumerate(todo, 1):
        if row["id"] in done:
            continue
        found, tried = [], []
        for q in queries(row):
            if q in cache:
                res = cache[q]
            else:
                res = eng.search(q)
                cache[q] = res
                CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            tried.append({"q": q, "status": res["status"], "n": len(res["results"])})
            for item in res["results"]:
                m = PROFILE.match(item["url"])
                if not m:
                    continue
                h = m.group(1).lower().strip(".")
                found.append({"handle": h, "title": item["title"], "snippet": item["snippet"], "query": q})
            if found:
                break
        done[row["id"]] = {"id": row["id"], "name": row["name"], "queries": tried, "candidates": found}
        OUT.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        mark = f"{len(found)} cand" if found else "-"
        print(f"[{n}/{len(todo)}] {row['id']} {row['name'][:26]:<26} {mark}", flush=True)

    hit = sum(1 for v in done.values() if v["candidates"])
    print(f"\nsearched: {len(done)}   with at least one profile candidate: {hit}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
