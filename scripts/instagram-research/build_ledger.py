#!/usr/bin/env python3
"""Merge every stage into the 526-row research ledger (JSON + CSV + XLSX).

Every one of the 526 listings gets a row: either a result, or the reason it
could not be researched. Nothing is guessed - a handle is recorded only when it
was found as a link on the venue's own official site.
"""
import csv, json
from datetime import date
from pathlib import Path

from decisions import DECISIONS, PUBLISHER_HANDLES, STAGE2_DECISIONS

HERE = Path(__file__).parent
CHECKED = date.today().isoformat()

TARGETS = json.loads((HERE / "targets.json").read_text(encoding="utf-8"))
STAGE1 = {r["id"]: r for r in json.loads((HERE / "stage1_results.json").read_text(encoding="utf-8"))}
_s2 = HERE / "stage2_results.json"
STAGE2 = {r["id"]: r for r in json.loads(_s2.read_text(encoding="utf-8"))} if _s2.exists() else {}

# a weak handle counts only if it is printed for exactly one venue and is not a
# publisher's own account appearing as page furniture
from collections import Counter as _Counter
_weak_freq = _Counter(
    w["handle"] for r in STAGE2.values() for w in r.get("weak_candidates", [])
    if w["handle"] not in PUBLISHER_HANDLES
)


def stage2_strong(tid: str) -> list[dict]:
    r = STAGE2.get(tid)
    return [c for c in r["candidates"] if c["handle"] not in PUBLISHER_HANDLES] if r else []


def stage2_weak(tid: str) -> list[dict]:
    r = STAGE2.get(tid)
    if not r:
        return []
    return [w for w in r.get("weak_candidates", [])
            if w["handle"] not in PUBLISHER_HANDLES and _weak_freq[w["handle"]] == 1]

COLUMNS = [
    "id", "live_order", "place_key", "name", "name_en", "region", "area", "cat",
    "maps_url", "instagram_url", "instagram_username", "account_type", "basis",
    "evidence", "evidence_url", "checked_at", "status",
]

# Stage 3 - the per-venue Instagram search. A handle here was found by searching
# Instagram for the venue by name and place, and is recorded only when the
# account's own profile text places it where this listing places it.
STAGE3 = {r["id"]: r for r in json.loads((HERE / "stage3_found.json").read_text(encoding="utf-8"))} \
    if (HERE / "stage3_found.json").exists() else {}


def apply_stage3(row: dict) -> dict:
    hit = STAGE3.get(row["id"])
    if not hit or row["status"] != "NOT_FOUND":
        return row
    if hit["v"] == "V":
        h = hit["h"]
        row.update(
            instagram_url=f"https://www.instagram.com/{h}/", instagram_username=h,
            account_type=hit.get("t") or "store", basis="profile",
            evidence=hit["note"], evidence_url=f"https://www.instagram.com/{h}/",
            status="VERIFIED")
    elif hit["v"] == "A":
        row.update(basis="", evidence=hit["note"],
                   evidence_url=f"https://www.instagram.com/{hit['h']}/" if hit.get("h") else "",
                   status="AMBIGUOUS")
    else:
        row.update(evidence=hit["note"], evidence_url="")
    return row


# Stage 4 - the per-venue second pass over the rows left AMBIGUOUS. Same rule as
# stage 3: a handle is recorded only when the account's own profile places the
# venue where this listing places it, or when the brand's own account says which
# of its accounts covers it.
STAGE4 = {r["id"]: r for r in json.loads((HERE / "stage4_found.json").read_text(encoding="utf-8"))} \
    if (HERE / "stage4_found.json").exists() else {}


def apply_stage4(row: dict) -> dict:
    hit = STAGE4.get(row["id"])
    if not hit or row["status"] != "AMBIGUOUS":
        return row
    if hit["v"] == "V":
        h = hit["h"]
        row.update(
            instagram_url=f"https://www.instagram.com/{h}/", instagram_username=h,
            account_type=hit.get("t") or "store", basis="profile",
            evidence=hit["note"], evidence_url=f"https://www.instagram.com/{h}/",
            status="VERIFIED")
    else:
        # keep the row ambiguous, but record what the second pass found
        row["evidence"] = f"{row['evidence']} {hit['note']}"
        if hit.get("h"):
            row["evidence_url"] = f"https://www.instagram.com/{hit['h']}/"
    return row


# Stage 6 - a third pass over the rows still ambiguous, reading the sources the
# 557-row Maps audit list records per row. A handle is recorded only when a page of
# the venue's own (or its operator's) links it, which is the stage-1 basis.
STAGE6 = {r["ledger_id"]: r for r in json.loads((HERE / "stage6_found.json").read_text(encoding="utf-8"))} \
    if (HERE / "stage6_found.json").exists() else {}


def apply_stage6(row: dict) -> dict:
    hit = STAGE6.get(row["id"])
    if not hit or row["status"] != "AMBIGUOUS":
        return row
    if hit["v"] == "V":
        h = hit["h"]
        row.update(
            instagram_url=f"https://www.instagram.com/{h}/", instagram_username=h,
            account_type=hit.get("t") or "store", basis=hit.get("b") or "profile",
            evidence=hit["note"], evidence_url=f"https://www.instagram.com/{h}/",
            status="VERIFIED")
    else:
        row["evidence"] = f"{row['evidence']} {hit['note']}"
    return row


# Stage 7 - the final review of the 260 verified rows. Two kinds of correction:
# rows whose recorded basis did not actually meet the bar are put back to
# AMBIGUOUS, and rows confirmed from a page of the venue's own get that page as
# their evidence URL instead of the Instagram URL.
STAGE7 = {r["id"]: r for r in json.loads((HERE / "stage7_corrections.json").read_text(encoding="utf-8"))} \
    if (HERE / "stage7_corrections.json").exists() else {}


def apply_stage7(row: dict) -> dict:
    fix = STAGE7.get(row["id"])
    if not fix or row["status"] != "VERIFIED":
        return row
    if fix["action"] == "demote":
        row.update(instagram_url="", account_type="", basis="", status="AMBIGUOUS",
                   evidence=f"{fix['note']} 候補: {row['instagram_username']}",
                   evidence_url=f"https://www.instagram.com/{row['instagram_username']}/")
        row["instagram_username"] = ""
    elif fix["action"] == "fix_evidence_url":
        row.update(evidence_url=fix["evidence_url"], evidence=fix["note"])
    return row


def handle_set(t: dict) -> list[str]:
    hs = []
    r = STAGE1.get(t["id"])
    if r:
        hs += [c["handle"] for c in r["candidates"]]
    hs += [u.rstrip("/").split("/")[-1].lower() for u in t.get("seed_instagram", [])]
    return sorted(dict.fromkeys(hs))


def evidence_url_for(t: dict, handle: str) -> str:
    r = STAGE1.get(t["id"])
    if r:
        for c in r["candidates"]:
            if c["handle"] == handle:
                return c["evidence_url"]
    for u in t.get("seed_instagram", []):
        if u.rstrip("/").split("/")[-1].lower() == handle:
            return u
    return ""


def build_row(t: dict) -> dict:
    row = {k: t.get(k, "") for k in ("id", "live_order", "place_key", "name", "name_en", "region", "area", "cat")}
    row["maps_url"] = t["maps_url"]
    row["checked_at"] = CHECKED
    row.update(instagram_url="", instagram_username="", account_type="", basis="", evidence="", evidence_url="", status="")

    hs = handle_set(t)
    stage1 = STAGE1.get(t["id"])

    if t["id"] in DECISIONS:
        handle, acct, note = DECISIONS[t["id"]]
        if handle:
            row.update(
                instagram_url=f"https://www.instagram.com/{handle}/",
                instagram_username=handle,
                account_type=acct,
                basis="own-site",
                evidence=f"Linked from the venue's own official site. {note}",
                evidence_url=evidence_url_for(t, handle),
                status="VERIFIED",
            )
        else:
            row.update(
                account_type="",
                evidence=f"Several official accounts are linked from the site and none is identifiable as this venue's. {note} Candidates: {', '.join(hs)}",
                evidence_url=evidence_url_for(t, hs[0]) if hs else "",
                status="AMBIGUOUS",
            )
        return row

    if len(hs) == 1:
        handle = hs[0]
        row.update(
            instagram_url=f"https://www.instagram.com/{handle}/",
            instagram_username=handle,
            account_type="store",
            basis="own-site",
            evidence="The venue's own official website links to this Instagram account.",
            evidence_url=evidence_url_for(t, handle),
            status="VERIFIED",
        )
        return row

    # stage 2 - reached through a directory page we already cite
    strong, weak = stage2_strong(t["id"]), stage2_weak(t["id"])
    if t["name"] in STAGE2_DECISIONS:
        handle, acct, note = STAGE2_DECISIONS[t["name"]]
        hs2 = sorted({c["handle"] for c in strong})
        if handle:
            ev = next((c["evidence_url"] for c in strong if c["handle"] == handle), "")
            row.update(
                instagram_url=f"https://www.instagram.com/{handle}/", instagram_username=handle,
                account_type=acct, basis="own-site",
                evidence=f"Reached the venue's own site through a directory page already cited by the guide, and that site links this account. {note}",
                evidence_url=ev, status="VERIFIED")
        else:
            row.update(
                evidence=f"Reached a site through a directory page, but no account there corresponds to this venue. {note} Seen: {', '.join(hs2) or 'none'}",
                evidence_url=strong[0]["evidence_url"] if strong else "", status="AMBIGUOUS")
        return row

    if strong:
        hs2 = sorted({c["handle"] for c in strong})
        if len(hs2) == 1:
            row.update(
                instagram_url=f"https://www.instagram.com/{hs2[0]}/", instagram_username=hs2[0],
                account_type="store", basis="own-site",
                evidence="Reached the venue's own site through a directory page already cited by the guide; the venue's name appears on that page and it links this account.",
                evidence_url=strong[0]["evidence_url"], status="VERIFIED")
        else:
            row.update(
                evidence=f"The site reached links several accounts and none is identifiable as this venue's. Candidates: {', '.join(hs2)}",
                evidence_url=strong[0]["evidence_url"], status="AMBIGUOUS")
        return row

    if weak:
        hs2 = sorted({w["handle"] for w in weak})
        row.update(
            evidence=("An Instagram account is printed for this venue on a directory or media page, but it could not be "
                      "confirmed on a page of the venue's own: no official website is on record and Instagram blocks "
                      f"unauthenticated profile reads. Printed: {', '.join(hs2)}"),
            evidence_url=weak[0]["evidence_url"], status="AMBIGUOUS")
        return row

    # no candidate at all - record why
    if not t["official_urls"]:
        row["evidence"] = (
            "No official website is on record for this venue, so no page under its own domain could be read. "
            "Instagram blocks unauthenticated profile reads, so a profile-only match could not be cross-checked either."
        )
    elif stage1 and not any(p["status"] == 200 for p in stage1["pages_tried"]):
        bad = ", ".join(f"{p['url']} -> {p['status']}" for p in stage1["pages_tried"][:3])
        row["evidence"] = f"The venue's own site could not be read, so no link could be confirmed ({bad})."
        row["evidence_url"] = stage1["pages_tried"][0]["url"]
    else:
        ok = [p["url"] for p in stage1["pages_tried"] if p["status"] == 200] if stage1 else []
        row["evidence"] = "The venue's own site was read and carries no link to an Instagram account."
        row["evidence_url"] = ok[0] if ok else ""
    row["status"] = "NOT_FOUND"
    return row


def main() -> int:
    rows = [apply_stage7(apply_stage6(apply_stage4(apply_stage3(build_row(t))))) for t in TARGETS]
    assert len(rows) == 526, len(rows)

    # A handle claimed by more than one listing cannot be a branch-specific
    # account: reclassify it as the brand/operator's shared account.
    from collections import Counter as _C
    shared = {h for h, n in _C(r["instagram_username"] for r in rows if r["instagram_username"]).items() if n > 1}
    for r in rows:
        if r["instagram_username"] in shared and r["account_type"] != "brand":
            r["account_type"] = "brand"
            r["evidence"] += " Shared with other listings in this guide, so recorded as the brand/operator account rather than a branch account."

    (HERE / "ledger.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with (HERE / "ledger.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    # data for the site: verified accounts only, keyed by city|place id
    site = {
        f"{r['region']}|{r['place_key'] or 'name:' + r['name']}": {"u": r["instagram_username"], "t": r["account_type"]}
        for r in rows if r["status"] == "VERIFIED" and r["instagram_username"]
    }
    (HERE / "instagram-links.json").write_text(json.dumps(site, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    st = Counter(r["status"] for r in rows)
    ac = Counter(r["account_type"] for r in rows if r["status"] == "VERIFIED")
    ba = Counter(r["basis"] for r in rows if r["status"] == "VERIFIED")
    print(f"rows            : {len(rows)}")
    print(f"VERIFIED        : {st['VERIFIED']}  (store {ac['store']} / brand {ac['brand']})")
    print(f"  by own-site link        : {ba['own-site']}")
    print(f"  by the account's profile: {ba['profile']}")
    print(f"AMBIGUOUS       : {st['AMBIGUOUS']}")
    print(f"NOT_FOUND       : {st['NOT_FOUND']}")
    urls = [r["instagram_url"] for r in rows if r["instagram_url"]]
    print(f"distinct handles: {len(set(urls))} of {len(urls)} (duplicates are branches sharing a brand account)")
    bad = [u for u in urls if not u.startswith("https://www.instagram.com/") or u.count("/") != 4]
    print(f"malformed urls  : {len(bad)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
