---
name: india-evisa-report-sync
description: Sync, audit, and report India e-Visa information from official government sources into internal Google Sheets and Google Docs. Use when checking India e-Visa categories, required documents, validity, timing guidance, or country-specific fees; when comparing an internal price sheet against the official India e-Visa site/PDFs; when creating a dated update tab (for example `25Mar26`); or when preparing a manager-friendly summary report with a linked detailed pricing sheet.
---

# India eVisa Report Sync

## Overview

Use this skill to turn the official India e-Visa website into a clean internal deliverable:
- a dated Google Sheet tab cloned from `Base` and updated with official pricing
- a Google Docs summary for management
- a clear explanation of what changed, what stayed the same, and what remains unverified

Read `references/official-sources.md` first if you need the exact source structure or wording rules.
Read `references/field-rules.md` when matching visa types, fee columns, or country names.

## Workflow

### 1. Collect source data from the official site

Use the official e-Visa page as the primary source:
- `https://indianvisaonline.gov.in/evisa/tvoa.html`

Use direct HTML fetch + DOM parsing for this site. Do **not** default to heavy browser automation unless the source structure changes.

From the HTML, extract:
- visa category list
- per-visa validity / entries / stay notes
- required documents block
- general advisory / timing notes
- linked PDF fee tables

### 2. Pull fee data from the linked official PDFs

Current core fee PDFs:
- e-Tourist fee PDF
- other e-Visa fee PDF (Business / Medical / Medical Attendant / Ayush / Ayush Attendant / Conference)

Parse the PDFs and normalize country names before comparing against internal sheets.

Important:
- official fees are **country/territory-specific**
- `00` means the official fee shown is zero
- zero fee is **not automatically the same thing as visa-free entry**
- if Sheets renders `00` as `0`, keep the meaning but explain it clearly in the report if needed

### 3. Compare against the internal sheet

When the user provides an internal Google Sheet:
1. inspect the `Base` tab first
2. preserve all values that do **not** change
3. create a new dated tab from `Base`
4. update only the values that differ from the official source
5. apply **bold** formatting only to changed price cells

Do not wipe the whole tab with a brand-new normalized matrix if the user's intent is “compare + update Base style”. The internal sheet layout is the canonical display format.

### 4. Handle incomplete official coverage carefully

If the official source set clearly covers some fee groups but not others:
- update only the fee groups supported by the official source
- leave unsupported columns unchanged
- explicitly state that those columns were retained pending further verification

For the March 2026 workflow, the official fee docs clearly covered:
- e-Tourist
- e-Business
- e-Medical
- e-Medical Attendant
- e-Ayush
- e-Ayush Attendant
- e-Conference

If `Student` or `Transit` fees are not clearly published in the same official source set, keep the internal values unchanged and say so in the report.

### 5. Write the management report in Google Docs

Structure the report for executives:
- title
- date
- source link
- executive summary
- changed pricing summary
- visa categories
- per-visa requirements / validity / notes
- processing-time guidance
- link to the detailed sheet tab
- caveats / unresolved items

Formatting rules:
- use headers generously
- bold key takeaways, caveats, and counts
- italicize only for subtle emphasis
- keep the tone concise and managerial
- summarize changes before forcing the reader into the sheet

### 6. Use precise wording

Prefer these phrases:
- “official fee is 0 USD”
- “official source currently shows zero fee”
- “internal value retained pending further official verification”
- “not clearly published in the official source set reviewed”

Avoid these unless separately verified:
- “visa-free”
- “free visa”
- “no visa required”

## Daily-run checklist

When doing recurring checks:
1. fetch current HTML from the official page
2. confirm the fee PDF links are still the same
3. parse fee PDFs
4. compare against the current `Base`-derived sheet layout
5. create a new dated tab
6. keep unchanged values intact
7. bold only changed values
8. refresh the Google Docs summary
9. call out any schema/source changes immediately

## Known lessons from the March 2026 run

- This site was not anti-bot difficult; the hard part was reconciliation, not crawling.
- `web_fetch` alone was too shallow for the full report; direct HTML parsing was better.
- Browser snapshot was useful for orientation, not for the main extraction path.
- PDF parsing was required for pricing.
- Country-name normalization is mandatory before sheet comparison.
- Replacing the entire internal table made the output worse; preserving unchanged internal values was the correct behavior.

## Resources

### references/
- `official-sources.md` — source inventory and extraction strategy
- `field-rules.md` — wording rules, fee interpretation, and matching rules

### scripts/
Bundled scripts are working patterns copied from the March 2026 implementation:
- `india_evisa_update_report.py`
- `format_india_evisa_doc.py`
- `fix_25mar26_sheet_format.py`

Treat them as implementation references. Copy/adapt them rather than assuming their hardcoded IDs or dates fit a new run.
