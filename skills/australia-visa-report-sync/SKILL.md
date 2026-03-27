---
name: australia-visa-report-sync
description: Sync, audit, and report Australia visitor and short-stay visa information from official Australian government sources into internal summaries, trackers, or manager-facing reports. Use when checking Australia visitor visa products (especially Visitor 600, eVisitor 651, ETA 601, Transit 771, Medical Treatment 602), building or updating an Australia visa sheet/doc, doing source QA on Australia visa wording, or monitoring recent visa-related news from australia.com and Executive Traveller as secondary sources that must be cross-checked against Home Affairs.
---

# Australia Visa Report Sync

Use this skill to produce repeatable Australia visa research without re-discovering the workflow.

## Core rule

Treat **Department of Home Affairs** as the primary source of truth.

Use secondary sources such as **australia.com** and **Executive Traveller** only for supplementary travel/news context. Never let them override Home Affairs wording.

## Approved operating scope

Default daily-report scope approved by Anh Bảo on 2026-03-27:
- `ETA 601`
- `eVisitor 651`
- `Visitor 600`
- `Transit 771`

Unless the user expands scope, keep the daily workflow anchored to those products/streams.

## Workflow

### 1. Decide the job type

Classify the request before collecting data:

- **Official product sync**: extract or refresh visa product facts from Home Affairs pages.
- **QA / wording audit**: check whether draft statements overclaim or blur stream-specific rules.
- **Recent-news check**: scan allowed secondary sources for the last 7 days, then cross-check anything important against Home Affairs.
- **Manager summary / sheet-doc update**: convert validated facts into a concise business-facing deliverable.

### 2. Start with the official source map

Read `references/source-map.md`.

Use the Home Affairs pages there as the initial crawl list. Prefer product pages over generic summaries when there is any conflict.

### 3. Extract official facts product-by-product

For each visa product or stream, capture only the fields that matter operationally:

- product name
- visa subclass / stream
- main purpose
- where the applicant must be when applying / when decided
- stay period
- entry pattern only if the page states it clearly
- official fee wording exactly as shown (for example `from AUD 200` vs `AUD 200`)
- application channel constraints
- warnings / limitations
- unresolved ambiguities

Keep **stay period**, **visa validity**, and **number of entries** separate. Do not collapse them into one sentence.

### 4. Split confirmed facts from unresolved points

Maintain two buckets while researching:

- **Confirmed from official page**
- **Needs caveat / cross-check**

Immediately flag items like:

- nationality / passport eligibility lists not yet captured
- tool-based processing times that were not snapshotted live
- wording that says `up to` rather than guaranteed duration
- grant-dependent entry counts
- fees that vary by stream, location, or applicant status

### 5. Run QA before writing the final report

Read `references/qa-checklist.md`.

Apply that checklist to every summary paragraph, table row, and heading. Rewrite any line that sounds broader or firmer than the source allows.

### 6. Only then check secondary news sources

Use secondary sources only after the official baseline is clear.

Default scope:

- `australia.com`
- `executivetraveller.com`
- window: last 7 days unless the user asks otherwise

Output for this step should be simple:

- no relevant new items found, or
- relevant item found → summarize it as secondary reporting and cross-check against Home Affairs before treating it as fact

### 7. Produce the deliverable

For the approved Australia daily-report workflow, use this fixed report order unless the user explicitly overrides it:
1. `TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA`
2. `TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA`
3. `TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG`
4. `CÁC LOẠI VISA HIỆN HÀNH`
5. `TIN TỨC VISA TỪ BÁO CHÍ`
6. `GHI CHÚ QUAN TRỌNG`
7. `NGUỒN THÔNG TIN`
8. `TECHNICAL CHANGELOG`

Formatting rules approved by Anh Bảo:
- sections `1..8` must be real Google Docs headings
- visa / stream labels such as `ETA 601`, `eVisitor 651`, `Visitor 600 - Business Visitor stream`, `Transit 771`, `TWOV` should be bold only, not headings
- bold key operational facts for business readers

Business rules:
- if there is no substantive change vs yesterday in fee, policy wording, validity, stay, entry rules, documents, nationality exceptions, or other policy-relevant content, section 1 must say exactly: `Không phát hiện sự thay đổi so với báo cáo hôm qua`
- technical-only diffs belong in `TECHNICAL CHANGELOG`, not in the business-change summary
- section 5 scans only the approved secondary sources `https://www.australia.com/` and `https://www.executivetraveller.com/` for the last 7 days unless the user changes the scope
- if section 5 finds no visa-related item, write exactly: `Không phát hiện tin tức mới liên quan đến Visa trong 7 ngày gần nhất`
- section 7 must split sources into two subgroups: `Web chính phủ` and `Link báo chí`

Workbook rule:
- use the existing Google Sheet workbook `Australia Visa - Official Tracker`
- create/update dated tabs inside that workbook for each run
- do **not** create a new spreadsheet file unless the user explicitly asks

QA finalization and summary-tracker update:
- after the report and sheet pass QA, update the central summary workbook before sending the completion message
- summary workbook: `Tổng hợp báo cáo Visa`
- spreadsheet id: `1XHtNTEb8XXyCrQcWYYMsK8lu0DZ2Jynmp8SlXJVI1Ag`
- add one row per completed report run
- keep `Thay đổi so với báo cáo trước?` to only two values: `Không` or `Có`
- if the run is a baseline / first report and there is no substantive change comparison yet, still use `Không` for that column to keep the summary simple
- put extra context in `Ghi chú thêm` only when helpful

Completion message rule:
- send only these user-facing items at the end:
  1. Link tổng hợp
  2. Link docs
  3. Link sheet
  4. one short Vietnamese change summary
- if there is no substantive change, use exactly: `Không có thay đổi so với báo cáo trước`

Read `references/deliverable-patterns.md` when drafting the final output.

## Writing rules

- Attribute factual statements to **Australian Department of Home Affairs** when useful.
- Prefer `up to`, `may be granted`, `depending on the grant`, and similar precise wording when the source does.
- Do not write `Australia tourist visa is 12 months` as a blanket statement.
- Do not merge **Visitor 600**, **eVisitor 651**, and **ETA 601** into one generic product.
- Do not claim a fixed processing time unless it was collected from the official processing-time tool at that time.
- Do not present australia.com as an immigration authority.
- Do not use Executive Traveller as the sole basis for legal/policy statements.

## High-value defaults learned from prior runs

- **Visitor visa 600** is the main visitor backbone and must be handled stream-by-stream.
- **ETA 601** and **eVisitor 651** are passport-eligibility-dependent pathways, not universal visitor options.
- **Business Visitor** wording is easy to overstate; be careful with work rights and entry-count claims.
- Secondary-source monitoring often returns **no actionable visa-policy change**; report that plainly instead of padding.

## References

- `references/source-map.md` — official source list and crawl order
- `references/qa-checklist.md` — risky wording traps and QA rules
- `references/deliverable-patterns.md` — compact output patterns for trackers and summaries
