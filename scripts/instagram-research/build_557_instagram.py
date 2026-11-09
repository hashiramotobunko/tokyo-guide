#!/usr/bin/env python3
"""Add the Instagram research columns to the 557-row Maps audit workbook.

The audit list and this project's 526-row ledger number their rows differently,
so the two are joined on the Google Maps place id in the audit URL, and on name +
region where a row carries a Maps search URL instead of a pin. The 30 venues the
audit list adds beyond the 526 were researched separately (stage5_new557.json)
with the same rule: an account is recorded only when its own profile places the
venue where the list places it.
"""
import json, re, unicodedata
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HERE = Path(__file__).parent
SRC = Path("/Users/hashiramototetsuya/仕事/Coding仕様書/tokyo_guide_maps_link_review_unified_557.xlsx")
OUT = SRC.with_name("tokyo_guide_maps_link_review_unified_557_instagram.xlsx")

NEW = ["Instagram URL", "Instagramアカウント名", "アカウント種別", "確認根拠", "Instagram判定",
       "Instagram根拠", "Instagram根拠URL", "Instagram調査日", "台帳との突合方法"]
WIDTHS = [38, 24, 13, 12, 14, 70, 44, 14, 26]
FILL = {"VERIFIED": PatternFill("solid", fgColor="FFEADB"),
        "AMBIGUOUS": PatternFill("solid", fgColor="FFF6E0"),
        "NOT_FOUND": PatternFill("solid", fgColor="F1F0EC"),
        "未調査": PatternFill("solid", fgColor="F1F0EC")}
JA = {"VERIFIED": "VERIFIED（確認済）", "AMBIGUOUS": "AMBIGUOUS（保留）", "NOT_FOUND": "NOT_FOUND（該当なし）"}
TYPE_JA = {"store": "店舗専用", "brand": "ブランド共通", "": ""}
BASIS_JA = {"own-site": "自社サイトにリンク", "profile": "プロフィール照合", "": ""}
PID = re.compile(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
    return re.sub(r"[\s　・･'\"’”!！\-－—–/／（）()【】\[\]]", "", s)


def main() -> int:
    ledger = json.loads((HERE / "ledger.json").read_text(encoding="utf-8"))
    by_pid = {r["place_key"]: r for r in ledger if r["place_key"]}
    by_name = {}
    for r in ledger:
        by_name.setdefault((norm(r["name"]), r["region"]), r)
    extra = {r["id"]: r for r in json.loads((HERE / "stage5_new557.json").read_text(encoding="utf-8"))}

    wb = load_workbook(SRC)
    ws = wb["557件統合監査"]
    head = [c.value for c in ws[1]]
    i_id = head.index("掲載ID") + 1
    i_name = head.index("施設名（訂正提案反映）") + 1
    i_reg = head.index("掲載地域") + 1
    i_url = head.index("原記録URL（監査証跡）") + 1

    info: dict[str, list] = {}
    counts = {"place id": 0, "name": 0, "new": 0}
    for row in range(2, ws.max_row + 1):
        pid_match = PID.search(ws.cell(row=row, column=i_url).value or "")
        lid = ws.cell(row=row, column=i_id).value
        rec = by_pid.get(pid_match.group(1)) if pid_match else None
        how = "ledger: Google Maps place id"
        if rec is None:
            rec = by_name.get((norm(ws.cell(row=row, column=i_name).value),
                               ws.cell(row=row, column=i_reg).value))
            how = "ledger: 施設名＋地域"
        if rec is not None:
            counts["place id" if how.endswith("place id") else "name"] += 1
            info[lid] = [
                rec["instagram_url"], rec["instagram_username"], TYPE_JA.get(rec["account_type"], rec["account_type"]),
                BASIS_JA.get(rec["basis"], rec["basis"]), JA.get(rec["status"], rec["status"]),
                rec["evidence"], rec["evidence_url"], rec["checked_at"], f"{how}（{rec['id']}）",
            ]
            continue
        e = extra.get(f"557:{lid}")
        counts["new"] += 1
        if e is None:
            info[lid] = ["", "", "", "", "未調査", "この行は台帳に対応する調査記録がなく、今回の個別調査にも含まれていません。", "", "", "未突合"]
        elif e["v"] == "V":
            h = e["h"]
            info[lid] = [f"https://www.instagram.com/{h}/", h, TYPE_JA.get(e.get("t", "store"), "店舗専用"),
                         BASIS_JA["profile"], JA["VERIFIED"], e["note"],
                         f"https://www.instagram.com/{h}/", "2026-10-29", "今回の新規個別調査"]
        elif e["v"] == "A":
            info[lid] = ["", "", "", "", JA["AMBIGUOUS"], e["note"],
                         f"https://www.instagram.com/{e['h']}/" if e.get("h") else "", "2026-10-29", "今回の新規個別調査"]
        else:
            info[lid] = ["", "", "", "", JA["NOT_FOUND"], e["note"], "", "2026-10-29", "今回の新規個別調査"]

    for sheet in ("557件統合監査", "優先確認"):
        w = wb[sheet]
        h = [c.value for c in w[1]]
        base = len(h)
        c_id = h.index("掲載ID") + 1
        for j, name in enumerate(NEW, start=1):
            cell = w.cell(row=1, column=base + j, value=name)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="151513")
            cell.alignment = Alignment(vertical="center")
            w.column_dimensions[get_column_letter(base + j)].width = WIDTHS[j - 1]
        for row in range(2, w.max_row + 1):
            lid = w.cell(row=row, column=c_id).value
            vals = info.get(lid)
            if not vals:
                continue
            for j, v in enumerate(vals, start=1):
                c = w.cell(row=row, column=base + j, value=v)
                if isinstance(v, str) and v.startswith("http"):
                    c.hyperlink = v
                    c.font = Font(color="0563C1", underline="single")
            st = w.cell(row=row, column=base + 5)
            key = str(st.value or "").split("（")[0]
            if key in FILL:
                st.fill = FILL[key]
                st.font = Font(bold=True)
            w.cell(row=row, column=base + 6).alignment = Alignment(wrap_text=True, vertical="top")

    # a summary sheet of its own, so the workbook explains the added columns
    from collections import Counter
    st = Counter(v[4] for v in info.values())
    s = wb.create_sheet("Instagram調査サマリー")
    rows = [
        ("対象行", ws.max_row - 1),
        ("VERIFIED（公式アカウント確認済）", st.get(JA["VERIFIED"], 0)),
        ("AMBIGUOUS（候補はあるが公式性・所在地が未確定）", st.get(JA["AMBIGUOUS"], 0)),
        ("NOT_FOUND（アカウントが見つからない／存在しない）", st.get(JA["NOT_FOUND"], 0)),
        ("未調査", st.get("未調査", 0)),
        ("", ""),
        ("VERIFIEDの条件", "次のいずれか。(1) 施設自身のウェブサイトのページからそのアカウントへリンクがある。(2) アカウント自身のプロフィールが施設名を名乗り、この台帳と同じ場所（住所・最寄駅・区名・市名）を示している。推測でURLを記載した行は一つもありません。"),
        ("アカウント種別", "店舗専用＝その店舗・支店自身のアカウント。ブランド共通＝複数店舗や運営者で共有しているアカウント。複数行が同じアカウントを使う場合は自動的にブランド共通に分類しています。"),
        ("確認根拠", "自社サイトにリンク＝経路(1)。プロフィール照合＝経路(2)。"),
        ("台帳との突合方法", "ledger: Google Maps place id＝監査URL内の0x識別子で526件台帳と一致。ledger: 施設名＋地域＝URLが検索形式のため名称と地域で一致。今回の新規個別調査＝526件台帳に無い施設で、今回あらためて個別検索した行。"),
        ("採用しなかったもの", "店主・店長の個人アカウント、プロフィールに所在地の記載が無いアカウント、所在地が台帳と食い違うアカウント、該当支店のアカウントが存在しない場合はいずれも保留にし、その理由をInstagram根拠列に記載しています。"),
        ("調査日", "2026-10-29"),
    ]
    for r in rows:
        s.append(list(r))
    s.column_dimensions["A"].width = 46
    s.column_dimensions["B"].width = 110
    for row in range(1, s.max_row + 1):
        s.cell(row=row, column=1).font = Font(bold=True)
        s.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(OUT)
    print("written:", OUT)
    print("join:", counts)
    print("status:", dict(st))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
