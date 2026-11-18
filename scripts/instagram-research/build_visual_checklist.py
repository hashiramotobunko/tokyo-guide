#!/usr/bin/env python3
"""Build the worklist for checking the still-ambiguous rows by eye on Instagram (v2).

Candidate accounts are taken only from places where a real handle was harvested:
the row's own evidence URL, the handles stage 1, 2 and 6 pulled out of actual links
on pages, and a short hand-checked list of accounts seen in search results. The
first version of this sheet parsed handles out of the prose of each row's reason,
which produced fragments and English words; nothing is parsed from prose here.

Each row also carries the 526-row ledger id it corresponds to, so the 74 rows of
the 557-row audit list can be told apart from the 68 of the published 526.
"""
import json, re
from pathlib import Path

from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = Path(__file__).parent
SRC = Path("/Users/hashiramototetsuya/仕事/Coding仕様書/tokyo_guide_maps_link_review_unified_557_instagram.xlsx")
OUT = SRC.with_name("tokyo_guide_instagram_目視確認リスト_v2.xlsx")

IG = "https://www.instagram.com/"
HANDLE = re.compile(r"^(?=.*[A-Za-z])[A-Za-z0-9._]{3,30}$")
PUBLISHER = {
    "hamoni_jp", "san_tatsu", "rurubuandmore", "rurubuplus", "timeouttokyo_jp", "aumo_odekake",
    "admatic_official", "tvtokyo_pr", "bs7ch_pr", "hitosara_official", "macaroni_news",
    "sauna_ikitai", "mapple_net", "tabelog_official", "retty_official", "hotpepper_gourmet",
    "gnavi_official", "jalan_net", "walkerplus", "ozmall_official", "makuake_official",
    "gendai_media", "note_official", "yomuno_official", "kinarino_official", "savor_japan",
    "inshokucom_journal", "tokyoweekender", "voyapon", "cotaru", "tablecheck_global",
    "instagram", "l.instagram",
}
#媒体・プラットフォーム側のアカウントは施設の候補ではないので名前に含む語でも弾く
PUBLISHER_SUBSTR = ("timeout", "hamoni", "retty", "tabelog", "gnavi", "hotpepper", "jalan",
                    "rurubu", "kinarino", "yomuno", "savor", "inshoku", "voyapon", "cotaru",
                    "tablecheck", "walkerplus", "ozmall", "makuake", "mapple", "icotto",
                    "aumo", "co_trip", "cotrip", "enjoytokyo", "weekender", "macaroni",
                    "epark", "omakaseje", "waraku", "agora_jp", "tabearuki", "_official_jp")

CLASS = {
    "A": "A 候補あり・プロフィールに所在地が無い",
    "B": "B 候補が複数あり現行が不明",
    "C": "C 店主・店長の個人アカウントのみ",
    "D": "D 当該支店のアカウントが無い",
    "E": "E アカウントの所在地が台帳と不一致",
    "F": "F 施設自身のアカウントが確認できていない",
    "G": "G 候補アカウントが見つかっていない",
}
ORDER = ["A", "B", "E", "D", "C", "F", "G"]
TODO = {
    "A": "候補アカウントを開き、プロフィール・ハイライト・固定投稿・直近の投稿のどこかに、照合材料の住所・最寄駅・電話番号・区名が出ているかを見る。一致すれば公式と確認。別の場所が書かれていればNG。",
    "B": "候補が複数あるので、各アカウントの最終投稿日・プロフィールのリンク先・フォロワー数を見比べ、現在運用されている方を特定する。両方生きている場合は店名表記が正式名と一致する方を優先。",
    "C": "原則不採用の分類。ただし施設自身（公式サイト・店頭・公式の案内）がこのアカウントを公式窓口として明示している場合に限り採用を検討する。明示の有無とその出所を根拠欄に記録し、判定は『要方針判断』を選ぶ。",
    "D": "ブランド側アカウントの投稿・ハイライト・プロフィールのリンク先に、この支店の告知や店舗一覧があるかを見る。支店が明記されていればブランド共通アカウントとして採用可（種別はブランド共通）。",
    "E": "アカウントが示す所在地と台帳の住所が食い違っている。移転したのか、別店舗なのか、台帳側の住所が古いのかを投稿履歴で確認する。",
    "F": "施設自身のアカウントが公開情報から見つかっていない行。候補は関連施設や運営者のものなので、施設自身のアカウントが別に存在しないかを確認する。見つからなければ『公開情報では確認できず』を選ぶ（存在しないとは断定しない）。",
    "G": "まず店名での検索をやり直す（表記ゆれ・英字表記・旧店名）。見つかったらプロフィールの所在地が照合材料と一致するかを見る。",
}
NO_ADDR_TODO = ("照合材料の住所が台帳に無い行。住所での照合はできないので、店名・業種・エリアの一致に加えて、"
                "プロフィールに出ている電話番号・最寄駅・店舗一覧・公式サイトへのリンクなど、"
                "この施設だと特定できる記載があるかを見る。特定できる記載が無ければ『公開情報では確認できず』を選ぶ。")

OVERRIDE = {
    "L120": "F", "L136": "F", "L139": "F", "L142": "F", "L457": "F", "L376": "F", "L547": "F",
    "L151": "E", "L357": "D", "L347": "G", "L475": "E",
}
# accounts seen in this project's own search results but not harvested from a link;
# every one was read in a search result page title during the research
EXTRA_CANDS = {
    "L022": ["tokyo.tonkatsu.gavuu"], "L087": ["amam_dacotan_omotesando", "amam_dacotan_omotedando"],
    "L097": ["niihao_kamata"], "L120": ["yasukuni.official", "yasukunijinja"],
    "L136": ["meijijingu.wedding"], "L139": ["yasukuni.official"], "L151": ["akaiheya16"],
    "L322": ["santora_ramen", "sugaraaa_santora"], "L346": ["shogunburger", "shogunburger_hokkaido"],
    "L357": ["hama_ginza"], "L376": ["asakusapelicancafe"], "L475": ["chedihanshin"],
    "L495": ["kitatougarashi"], "L547": ["hakuba_kurashita_carstay", "hakuba_kurashita_camp"],
    "L080": ["horn.tokyo"], "L391": ["medikasoba.kin_gyo"], "L305": ["nadoya.katte", "nadoya.jp"],
    "L400": ["codies.burger"], "L298": ["1500_millecinquecento"],
}
# addresses and telephone numbers found for rows the audit list leaves blank;
# all from secondary pages, so the sheet says so
FOUND_CONTACT = {
    "L150": ("東京都港区北青山2-14-4 THE AOYAMA GRAND HOTEL 20階 / 電話 03-6271-5429", "二次情報（施設紹介ページ）"),
    "L007": ("東京都中野区東中野1-57-2 柴沼ビル1F / 電話 03-3371-5746", "二次情報（グルメ媒体）"),
    "L144": ("東京都港区芝公園2-2-10 / 電話 03-3434-8180", "二次情報（口コミサイト）"),
}
NO_CONTACT_NOTE = {
    "L027": "店名『麻布苑』での住所・電話は公開情報から確認できなかった（近い名称の別店『焼肉苑 麻布十番店』が存在するため混同に注意）。",
}
NOTE = {
    "L347": "この行のGoogleマップのピンが、台帳側の「ビフテキのカワムラ 銀座」とは別の場所を指している。銀座の「かわむら」は同名の別店（ステーキ店）の可能性があるため、まずどちらの店かを確定する。",
    "L087": "2アカウントとも住所は北青山3-7-6で一致している。どちらが現行かだけを見れば足りる。",
    "L298": "食べログ掲載の候補 1500_millecinquecento を含めて確認する。",
}


def main() -> int:
    wb_src = load_workbook(SRC, read_only=True)
    ws = wb_src["557件統合監査"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    head = rows[0]
    body = [r for r in rows[1:] if any(c is not None for c in r)]
    I = {k: head.index(k) for k in ("掲載ID", "施設名（訂正提案反映）", "掲載地域", "エリア", "カテゴリ",
                                    "Instagram判定", "Instagram根拠", "Instagram根拠URL",
                                    "住所参考（過去の独立結果）", "原記録URL（監査証跡）", "台帳との突合方法")}

    # handles harvested from real links, by ledger id and by audit row
    harvest: dict[str, list[tuple[str, str]]] = {}
    for f, origin in (("stage1_results.json", "施設自身のサイトから採取"),
                      ("stage2_results.json", "媒体ページから採取")):
        p = HERE / f
        if not p.exists():
            continue
        for r in json.loads(p.read_text(encoding="utf-8")):
            for key, note in (("candidates", origin), ("weak_candidates", "媒体ページに掲載（施設のものとは限らない）")):
                for c in r.get(key, []):
                    harvest.setdefault(r["id"], []).append((c["handle"].lower(), note))
    s6 = {}
    for r in json.loads((HERE / "stage6_results.json").read_text(encoding="utf-8")):
        for key, o in (("candidates", "監査リストの出典ページ（施設自身のページ）から採取"),
                       ("weak_candidates", "監査リストの出典ページに掲載（施設のものとは限らない）")):
            for c in r.get(key, []):
                s6.setdefault(r["id"], []).append((c["handle"].lower(), o))

    items = []
    for r in body:
        if not str(r[I["Instagram判定"]]).startswith("AMBIGUOUS"):
            continue
        lid = r[I["掲載ID"]]
        ev = str(r[I["Instagram根拠"]] or "")
        join = str(r[I["台帳との突合方法"]] or "")
        m = re.search(r"（(L\d+)）", join)
        ledger_id = m.group(1) if m else ("－（557件のみ）" if "新規" in join else "")

        cands: list[tuple[str, str]] = []

        def add(h: str, origin: str) -> None:
            h = h.strip().lower()
            if not HANDLE.match(h) or h in PUBLISHER:
                return
            if any(w in h for w in PUBLISHER_SUBSTR):
                return
            if any(h == c[0] for c in cands):
                return
            cands.append((h, origin))

        url = str(r[I["Instagram根拠URL"]] or "")
        if url.startswith(IG):
            add(url[len(IG):].strip("/"), "この行の根拠URL")
        for h, o in harvest.get(ledger_id, []):
            add(h, o)
        for h, o in s6.get(lid, []):
            add(h, o)
        for h in EXTRA_CANDS.get(lid, []):
            add(h, "調査中に検索結果で確認")

        e = ev.lower()
        cls = OVERRIDE.get(lid)
        if cls is None:
            if "proprietor" in e or "manager's" in e or "personal account" in e:
                cls = "C"
            elif "two accounts" in e or "near-identical" in e:
                cls = "B"
            elif "rather than" in e and "places it" in e:
                cls = "E"
            elif "no account for the" in e and ("branch" in e or "main shop" in e):
                cls = "D"
            elif "no account of its own" in e:
                cls = "F"
            elif cands:
                cls = "A"
            else:
                cls = "G"

        addr = (r[I["住所参考（過去の独立結果）"]] or "").strip()
        addr_src = "監査リストの住所参考" if addr else ""
        if not addr and lid in FOUND_CONTACT:
            addr, addr_src = FOUND_CONTACT[lid]
        todo = TODO[cls]
        if not addr:
            todo = NO_ADDR_TODO + " " + todo
        if lid in NO_CONTACT_NOTE:
            todo = NO_CONTACT_NOTE[lid] + " " + todo
        if lid in NOTE:
            todo = NOTE[lid] + " " + todo

        items.append({"cls": cls, "id": lid, "ledger": ledger_id, "name": r[I["施設名（訂正提案反映）"]],
                      "region": r[I["掲載地域"]], "area": r[I["エリア"]], "cat": r[I["カテゴリ"]],
                      "addr": addr, "addr_src": addr_src, "cands": cands[:3], "todo": todo,
                      "why": ev, "maps": r[I["原記録URL（監査証跡）"]] or ""})
    items.sort(key=lambda x: (ORDER.index(x["cls"]), x["region"] != "Tokyo", x["area"] or "", x["id"]))

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "目視確認リスト"
    cols = ["作業No", "分類", "監査ID(557)", "台帳ID(526)", "526件に掲載", "施設名", "地域", "エリア", "カテゴリ",
            "照合材料（住所・電話）", "照合材料の出所", "候補1", "候補1の出所", "候補2", "候補2の出所",
            "候補3", "候補3の出所", "確認すべき点",
            "【入力】判定", "【入力】確定アカウント", "【入力】確認できた根拠", "【入力】確認日",
            "これまでに調べたこと（保留理由）", "Google Maps URL"]
    widths = [7, 30, 12, 12, 11, 30, 9, 16, 14, 40, 20, 34, 22, 34, 22, 34, 22, 62,
              22, 22, 40, 13, 80, 44]
    green = {cols.index(c) + 1 for c in cols if c.startswith("【入力】")}
    ws1.append(cols)
    for i, c in enumerate(ws1[1], start=1):
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F6F43" if i in green else "151513")
        c.alignment = Alignment(vertical="center", wrap_text=True)
    thin = Side(style="thin", color="DDDDDD")
    for n, it in enumerate(items, start=1):
        cand_cells = []
        for k in range(3):
            if k < len(it["cands"]):
                cand_cells += [f"{IG}{it['cands'][k][0]}/", it["cands"][k][1]]
            else:
                cand_cells += ["", ""]
        ws1.append([n, CLASS[it["cls"]], it["id"], it["ledger"],
                    "掲載" if it["ledger"].startswith("L") else "対象外",
                    it["name"], it["region"], it["area"], it["cat"], it["addr"], it["addr_src"],
                    *cand_cells, it["todo"], "", "", "", "", it["why"], it["maps"]])
        row = ws1.max_row
        for col in (12, 14, 16, len(cols)):
            c = ws1.cell(row=row, column=col)
            if isinstance(c.value, str) and c.value.startswith("http"):
                c.hyperlink = c.value
                c.font = Font(color="0563C1", underline="single")
        for col in (10, 18, 23):
            ws1.cell(row=row, column=col).alignment = Alignment(wrap_text=True, vertical="top")
        for col in green:
            ws1.cell(row=row, column=col).fill = PatternFill("solid", fgColor="EAF5EF")
        for col in range(1, len(cols) + 1):
            ws1.cell(row=row, column=col).border = Border(bottom=thin)
    for i, w in enumerate(widths, start=1):
        ws1.column_dimensions[get_column_letter(i)].width = w
    ws1.freeze_panes = "F2"
    ws1.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws1.max_row}"
    dv = DataValidation(
        type="list",
        formula1='"公式と確認,別の店・非公式と判明,公開情報では確認できず,要方針判断"',
        allow_blank=True)
    dv.promptTitle = "判定"
    dv.prompt = "見た結果を選んでください。『公開情報では確認できず』は存在しないという意味ではありません。"
    ws1.add_data_validation(dv)
    dv.add(f"S2:S{ws1.max_row}")

    # the correspondence between the two lists, spelled out
    ws3 = wb.create_sheet("557件と526件の対応")
    pub = [i for i in items if i["ledger"].startswith("L")]
    only = [i for i in items if not i["ledger"].startswith("L")]
    ws3.append(["区分", "件数", "意味"])
    ws3.append(["このリストの行数（557件監査リストの保留）", len(items),
                "557件監査リスト側でAMBIGUOUSと判定されている行の数"])
    ws3.append(["うち 公開サイト526件にも掲載（台帳の保留と同一）", len(pub),
                "526件台帳のAMBIGUOUS 68件と1対1で対応する行。台帳ID(526)列に対応IDを記載"])
    ws3.append(["うち 557件監査リストにのみ存在", len(only),
                "監査リストが526件に追加した施設。公開サイトには出ていないため、確認結果は監査リスト側にのみ反映される"])
    ws3.append(["", "", ""])
    from collections import Counter as _C
    led = _C(r["status"] for r in json.loads((HERE / "ledger.json").read_text(encoding="utf-8")))
    aud = _C(str(r[I["Instagram判定"]]).split("（")[0] for r in body)
    ws3.append(["参考：526件台帳の現在の内訳", "",
                f"VERIFIED {led['VERIFIED']}／AMBIGUOUS {led['AMBIGUOUS']}／NOT_FOUND {led['NOT_FOUND']}"])
    ws3.append(["参考：557件監査リストの現在の内訳", "",
                f"VERIFIED {aud['VERIFIED']}／AMBIGUOUS {aud['AMBIGUOUS']}／NOT_FOUND {aud['NOT_FOUND']}"])
    ws3.append(["差の理由", "",
                "557件は526件に31施設を加えた監査用の台帳で、重複掲載の行も含むため件数が一致しない。"
                "公開サイトの掲載対象は526件のみ"])
    ws3.append(["", "", ""])
    ws3.append(["557件のみの行（対象外）", "", "、".join(f"{i['id']} {i['name']}" for i in only)])
    ws3.column_dimensions["A"].width = 46
    ws3.column_dimensions["B"].width = 10
    ws3.column_dimensions["C"].width = 100
    for row in range(1, ws3.max_row + 1):
        ws3.cell(row=row, column=1).font = Font(bold=True)
        ws3.cell(row=row, column=3).alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws3[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="151513")

    ws2 = wb.create_sheet("使い方・判定基準")
    rows2 = [
        ("このリストは何か",
         f"557件監査リストのうち、Instagramの公式アカウントを未ログインの調査では確定できなかった{len(items)}件です。"
         f"うち{len(pub)}件は公開サイト526件の保留68件と同一の施設、{len(only)}件は監査リストにのみある施設です。"
         "対応関係は『557件と526件の対応』シートに整理しています。"),
        ("v2で直したこと",
         "初版は各行の保留理由の文章から候補アカウント名を機械的に拾っていたため、"
         "『Second』『account』『none』のような文章の一部や、"
         "『medikasoba』『nadoya』『codies』のような途中で切れたアカウント名が候補欄に混入していました。"
         "v2では文章からの抽出をやめ、実際のリンクから採取した候補と、調査中に検索結果で確認した候補のみを掲載し、"
         "各候補に『どこから得た候補か』を併記しています。"),
        ("作業のしかた",
         "分類Aから順に並べてあります。Aは候補アカウントを開いて照合材料と一致するか見るだけなので最も速く、"
         "下に行くほど判断が重くなります。候補1〜3のURLをクリックしてアカウントを開き、"
         "『確認すべき点』の観点で見て、緑色の4列に記入してください。"),
        ("判定の選択肢",
         "公式と確認＝この施設の公式アカウントだと確認できた／別の店・非公式と判明＝候補は別の店か非公式だった／"
         "公開情報では確認できず＝見ても確認できなかった（アカウントが存在しないという断定ではありません）／"
         "要方針判断＝採否が方針の問題（分類Cなど）。"),
        ("「公式と確認」の条件",
         "次のどちらかが満たせれば確認済みとして台帳に反映できます。(1) 施設自身のウェブサイトのページから"
         "そのアカウントへリンクがある。(2) アカウント自身のプロフィール・ハイライト・固定投稿に施設名があり、"
         "かつ住所・最寄駅・電話番号・区名のいずれかが照合材料と一致している。"),
        ("照合材料が空欄の行",
         "住所が台帳に無い行があります。これらは住所照合ができないため、『確認すべき点』に"
         "住所以外（電話番号・最寄駅・店舗一覧・公式サイトへのリンク）で特定する手順を書いています。"
         "今回あらためて調べて住所・電話が見つかった3件（The Top.／レストラン イト／タイごはん 泉州屋台）は"
         "二次情報であることを明記して記載しました。麻布苑は公開情報から確認できませんでした。"),
        ("分類Cの扱い",
         "店主・店長の個人アカウントは原則不採用です。ただし施設自身（公式サイト・店頭・公式の案内）が"
         "そのアカウントを公式窓口として明示している場合に限り、明示の有無と出所を根拠欄に記録のうえ"
         "個別に採用可否を判断します。判定欄は『要方針判断』を選んでください。"),
        ("分類Fの扱い",
         "施設自身のアカウントが公開情報から見つかっていない行です。『存在しない』とは断定せず、"
         "確認できなかった場合は『公開情報では確認できず』を選んでください。"),
        ("採用していない根拠",
         "店名が同じだけ、フォロワーが多いだけ、第三者のまとめ記事に載っているだけ、写真が似ているだけ、"
         "の4つは根拠として採用していません。『根拠』欄にはプロフィールのどこに何と書いてあったかを"
         "一行で書いていただけると、そのまま台帳の根拠列に転記できます。"),
        ("戻していただいたあと",
         "記入後のファイルを渡していただければ、判定を台帳・サイトデータ・557件リストに反映し、"
         "テストと表示確認までやり直します。526件に掲載の行だけが公開サイトに反映されます。"),
        ("件数", f"{len(items)}件（v2作成日 2026-10-29）"),
    ]
    for r in rows2:
        ws2.append(list(r))
    ws2.column_dimensions["A"].width = 30
    ws2.column_dimensions["B"].width = 118
    for row in range(1, ws2.max_row + 1):
        ws2.cell(row=row, column=1).font = Font(bold=True)
        ws2.cell(row=row, column=1).alignment = Alignment(vertical="top")
        ws2.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(OUT)
    from collections import Counter
    print("written:", OUT)
    print("rows:", len(items), "| 526掲載:", len(pub), "| 557のみ:", len(only))
    for c, n in sorted(Counter(i["cls"] for i in items).items()):
        print(f"  {CLASS[c]}: {n}")
    print("候補ゼロの行:", [(i["id"], i["name"]) for i in items if not i["cands"]])
    print("照合材料が空の行:", [(i["id"], i["name"]) for i in items if not i["addr"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
