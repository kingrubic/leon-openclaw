---
name: kenya-eta-report-sync
description: Sync, audit, and report Kenya eTA information from the official Kenya eTA website into internal Google Sheets, Google Docs, or manager-facing updates. Use when checking Kenya eTA categories, fees, processing, validity, required documents, exemptions, nationality eligibility, or application workflow; when building or updating a Kenya visa/eTA tracker; or when doing recurring QA on https://etakenya.go.ke/.
---

# Kenya eTA Report Sync

## Overview

Use this skill to turn official Kenya eTA public information into a repeatable internal deliverable with:
- one Base-style Google Sheet or dated tab for operational use
- one Vietnamese Google Docs summary for management
- a clear source-backed separation between confirmed rules, exemption carve-outs, and risky interpretations
- a stable workflow so future runs do not need to rediscover the Kenya site structure

Read `references/source-map.md` first for the crawl order and trusted pages.
Read `references/qa-rules.md` before writing conclusions, sheet labels, or management wording.

## Workflow

### 1. Start with the official Kenya eTA public site only

Primary domain:
- `https://etakenya.go.ke/`

Prefer direct HTML fetch / source inspection first.
This site is server-rendered enough for public-content extraction and does **not** require heavy browser automation for the main research path.

Use browser automation only when needed for:
- confirming accordion content in FAQ pages
- checking text rendered after user interaction
- validating application-step wording in `/form/...` routes

### 2. Build the official fact set in this order

Use this order unless the user explicitly narrows scope:
1. `eligibility`
2. `general-information`
3. `faqs`
4. `form/apply/start`
5. `form/apply/how-to-apply?type=tourist`
6. `form/apply/how-to-apply?type=diplomats`
7. `terms-and-conditions`
8. `privacy-policy`

Collect these field groups separately:
- eTA product/category name
- stated purpose / intended traveler type
- fee shown on the public site
- processing guidance
- validity window before travel
- stay/admission wording at entry
- required documents
- exemption / eTA-not-required regimes
- special passport / diplomatic carve-outs
- family / business / medical / conference supporting-document rules
- application-channel notes and status-tracking flow

### 3. Keep four concepts separate

Do **not** collapse these into one sentence:
- **eTA validity for travel**
- **processing time**
- **permission to board/travel**
- **actual period of stay / admissibility decided at entry**

Current official wording makes this especially important:
- public site says tourist-facing eTA is valid for travel within **90 days from issuance**
- public site says processing is generally **3 working days / 72 hours**
- public site also says urgent / expedited processing exists
- public site says final admissibility and duration of stay are decided at the **point of entry**

### 4. Treat product categories carefully

As of the March 2026 Kenya crawl, the public eligibility page shows these public-facing products:
- `Transit eTA` — price shown as `USD 20`
- `Standard eTA` — price shown as `USD 30`
- `One Year Multi-Entry eTA` — price shown as `USD 300`
- `Five Year Multi-Entry eTA` — price shown as `USD 185`
- `East African Tourist eTA` — shown as `COMING SOON`

Handling rules:
- keep the label exactly as shown on the site
- do not rename `Standard eTA` to “tourist visa” unless the user explicitly wants internal relabeling
- keep `East African Tourist eTA` as unavailable / coming soon unless later pages show active application support
- explicitly note that `Five Year Multi-Entry eTA` is currently described for **American nationals** on the public page

### 5. Handle exemptions and nationality regimes conservatively

Kenya eTA has a broad exemption structure.
Do **not** oversimplify it into a single “visa-free” or “no eTA” statement.

Split exemption findings into these buckets:
- Kenyan citizens / residency / re-entry-pass holders
- EAC partner-state citizens with stated stay limit
- named 90-day nationality exemptions
- named 60-day African-country exemptions
- airside transit / same-aircraft / same-ship / crew / refueling carve-outs
- official laissez-passer / organization-business exemptions
- diplomatic / official / service passport carve-outs for specific countries
- military carve-out

If using the country eligibility table from `/eligibility`, treat it as a strong public operational source, but cross-check summary statements against the exemption list on `general-information` or `form/apply/how-to-apply` before making broad claims.

### 6. Build the sheet in operational style, not over-normalized style

If the user asks for a sheet update:
- inspect the existing `Base` tab first
- clone `Base` into a dated tab
- preserve unchanged structure and unchanged values
- update only fields that materially differ from the official Kenya source set
- bold only cells with changed operational values

Recommended column groups for Kenya if building from scratch:
- product / category
- purpose
- fee
- processing
- validity before travel
- entry pattern
- stay / admission note
- required documents
- eligibility / nationality scope
- exemptions / carve-outs
- notes / caveats

Do **not** force every exemption into the same structure as the fee-based eTA products. A separate exemptions section or tab is often cleaner.

### 7. Write the management report in Vietnamese

Use this fixed section order unless the user explicitly overrides it:
1. `TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA`
2. `TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA`
3. `TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG`
4. `CÁC LOẠI ETA / DIỆN NHẬP CẢNH HIỆN HÀNH`
5. `GHI CHÚ QUAN TRỌNG`
6. `NGUỒN THÔNG TIN`
7. `TECHNICAL CHANGELOG`

Report rules:
- Vietnamese first
- headings should be real headings in Google Docs
- no `EXECUTIVE SUMMARY` unless explicitly requested
- no `TÓM TẮT THAY ĐỔI SO VỚI BASE / ĐẦU VÀO NỘI BỘ` unless explicitly requested
- if there is no fee / validity / processing / document / exemption / eligibility / wording change vs yesterday, write exactly: `Không phát hiện sự thay đổi so với báo cáo hôm qua`
- keep business-relevant changes in sections 1/2/3
- move formatting-only or render-only differences into `TECHNICAL CHANGELOG`
- section 4 should summarize active eTA products, exemptions, documents, processing, and validity/stay distinctions
- section 5 should highlight risky interpretation areas such as exemption wording, point-of-entry discretion, and category-specific supporting documents
- section 6 must list all official URLs reviewed

### 8. Default QA before final delivery

Before finalizing any report or sheet, verify all of the following:
- fee values still match the live eligibility page
- product names still match the live eligibility page
- `processing time` has not been confused with `validity`
- `valid for travel within 90 days` has not been confused with `length of stay`
- no row says `visa-free` unless the official page clearly says that and it remains consistent with the exemption list
- country-table conclusions do not contradict the exemption list pages
- diplomatic fee statements are clearly separated from diplomat application requirements
- `East African Tourist eTA` is still marked `COMING SOON` unless officially changed

### 9. Summary-tracker update rule

After the report and sheet pass QA, update the central summary workbook before sending the completion message:
- summary workbook: `Tổng hợp báo cáo Visa`
- spreadsheet id: `1XHtNTEb8XXyCrQcWYYMsK8lu0DZ2Jynmp8SlXJVI1Ag`
- add one row per completed report run
- keep `Thay đổi so với báo cáo trước?` to only two values: `Không` or `Có`
- if the run is a baseline / first report and there is no substantive comparison yet, still use `Không`
- use `Ghi chú thêm` only when useful for caveats

Completion message rule:
- send only these user-facing items at the end:
  1. Link tổng hợp
  2. Link docs
  3. Link sheet
  4. one short Vietnamese change summary
- if there is no substantive change, use exactly: `Không có thay đổi so với báo cáo trước`

## Writing rules

Prefer wording like:
- `Theo website eTA official của Kenya...`
- `official public page currently shows...`
- `valid for travel within 90 days from issuance`
- `duration of stay is determined at the point of entry`
- `ETA not required under the listed exemption regime`
- `expedited processing option is shown on the official site`
- `country eligibility table currently shows...`

Avoid flat or risky wording like:
- `Kenya tourist visa is 90 days`
- `được ở Kenya 90 ngày` unless the source explicitly says that for the exact category
- `mọi khách quá cảnh đều cần Transit eTA`
- `mọi nhà ngoại giao đều được miễn eTA`
- `East African Tourist eTA đang mở`
- `visa-free` as a blanket synonym for all `ETA not required` cases

## Daily-run checklist

1. Re-read `eligibility` first.
2. Re-check public product cards and fee values.
3. Re-check `general-information` and `how-to-apply` exemption list.
4. Re-check FAQ answers for processing, fee, tracking, group, and document wording.
5. Re-check `/form/apply/start` for application routing and exempt-country list behavior.
6. Compare against the existing Base-style sheet or prior report.
7. Classify diffs into policy/business vs technical-only.
8. Update the Vietnamese management report using the fixed section order.
9. If no policy-relevant change vs yesterday, write exactly: `Không phát hiện sự thay đổi so với báo cáo hôm qua`.
10. Put rendering-only diffs into `TECHNICAL CHANGELOG`.
11. Call out any contradiction between the country table and exemption pages explicitly.

## Known March 2026 lessons

- The Kenya site is publicly crawlable with direct HTML/source inspection.
- Pages are rendered with Phoenix LiveView assets, but public info pages are still readable from fetched HTML.
- FAQ answers can be easier to confirm with DOM inspection because accordion content is present but not always obvious in plain extraction.
- The difficult part is not anti-bot scraping; it is keeping `fee`, `processing`, `validity`, `stay`, and `exemption` concepts separate.
- The exemption list is broad and can be misreported if you rely only on a single country-table snapshot.
- The product list includes both fee-based eTA products and large non-eTA exemption regimes; do not merge them into one flat table without notes.

## Resources

### references/
- `source-map.md` — official Kenya source inventory and crawl order
- `qa-rules.md` — interpretation traps, wording safeguards, and sheet/report QA rules
