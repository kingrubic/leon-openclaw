---
name: sri-lanka-eta-report-sync
description: Sync, audit, and report Sri Lanka ETA information from official government sources into internal Google Sheets and Google Docs. Use when checking Sri Lanka ETA categories, validity, entry rules, fee tables, special nationality regimes, application conditions, or advisories; when building a company-facing report from https://www.eta.gov.lk/; when creating a Base-style workbook plus dated tab in the same presentation style as the India report; or when daily monitoring is needed with strict QA around contradictions on the official site.
---

# Sri Lanka ETA Report Sync

## Overview

Use this skill to turn Sri Lanka ETA official public information into a management-ready deliverable with:
- one Google Sheet workbook in the same operational style as the India workbook
- one Google Docs summary in Vietnamese for leadership
- explicit QA notes where the official Sri Lanka site is inconsistent

Read `references/official-sources.md` first for the source map.
Read `references/qa-rules.md` before writing conclusions or system-facing wording.

## Workflow

### 1. Collect only official public sources first

Primary domain:
- `https://www.eta.gov.lk/`

Key public pages used in the March 2026 run:
- `center.jsp?locale=en_US`
- `shortvisit.jsp?locale=en_US`
- `apply.jsp?locale=en_US`
- `fees.jsp?locale=en_US`
- `faq.jsp?locale=en_US`
- homepage alerts on `/slvisa/`

Prefer direct HTML fetch and parsing. Do not start with browser automation unless the site blocks direct extraction or the needed content is missing.

### 2. Separate high-confidence facts from risky claims

This source is usable, but not fully internally consistent.

Before writing the report, split findings into:
- confirmed facts repeated or clearly shown across official pages
- contradictory items that need caveats
- special homepage alerts that may override standard fee assumptions

### 3. Build the fee model carefully

Sri Lanka does **not** behave like the India country-by-country fee sheet.

The working fee structure is grouped mainly by:
- SAARC countries
- all other countries
- children under 12
- on-arrival cases
- special nationality regime noted on homepage alerts

Do not force this into an India-style country-by-country matrix if the official source does not support that structure.

### 4. Create the sheet in India-style presentation, not India-style logic

Required presentation pattern:
- a `Base` tab
- a dated working tab copied from `Base`
- readable operational layout
- same visual language as the India workbook where practical

But adapt the content model to Sri Lanka:
- use nationality groups where official pricing is group-based
- create explicit rows for special-country exceptions when homepage alerts justify it
- keep a notes column for caveats and overrides

### 5. Write the report in Vietnamese

Default audience is Vietnamese management.

Report requirements:
- Vietnamese first
- headings visible and strong
- executive summary near the top
- clear fee summary
- clear caveats
- no overclaiming

Keep English only for necessary visa/ETA terminology where precision matters.

### 6. Mandatory QA rules

Always caveat these areas unless the official site becomes fully consistent:
- “visa-free” vs “still must apply for ETA”
- business ETA entry count
- business ETA online availability vs mission/DI&E wording
- ETA validity vs stay duration vs extension wording
- on-arrival payment wording and business on-arrival fee gaps

If homepage alerts conflict with standard fee tables, mention that alerts may override the standard fee page for affected nationalities.

## Safe wording rules

Prefer wording like:
- “Theo ETA site official của Sri Lanka...”
- “official pages currently show...”
- “special fee-free / visa-free regime, while still instructing travelers to obtain ETA before travel”
- “business ETA wording is not fully harmonized across official pages”
- “limited on-arrival facility”

Avoid flat claims like:
- “không cần ETA”
- “business ETA luôn multiple entry”
- “business ETA luôn double entry”
- “ETA luôn phải có trước khi boarding”
- “on-arrival mặc định dùng được cho mọi case”

## Daily-run checklist

1. Read homepage alerts first.
2. Re-read key ETA info pages.
3. Re-check the fee page.
4. Compare alert exceptions against the standard fee table.
5. Update the Sri Lanka workbook.
6. Keep the layout stable for internal readers.
7. Update the Vietnamese management report.
8. Call out any contradiction or override explicitly.

## Known March 2026 lessons

- The site is not hard to crawl technically.
- The difficult part is policy interpretation and contradiction handling.
- Homepage alerts can materially change the meaning of the standard fee table.
- “Visa-free” language on the site does not automatically mean “no ETA required”.
- A notes / caveat column in the sheet is essential.

## Resources

### references/
- `official-sources.md` — official ETA source map and extraction targets
- `qa-rules.md` — contradiction handling, wording rules, and report safeguards

### scripts/
Use these as implementation references from the March 2026 run:
- `sri_lanka_eta_report.py`
- `format_sri_lanka_sheet_like_india.py`
- `translate_sri_lanka_doc_vi.py`
- `polish_sri_lanka_doc_headings.py`

These scripts include hardcoded document IDs and file IDs from the original run. Re-check IDs before reuse.
