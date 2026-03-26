# Official sources

## Primary domain
- `https://www.eta.gov.lk/`

## Public pages used in the March 2026 workflow
- `https://www.eta.gov.lk/slvisa/visainfo/center.jsp?locale=en_US`
- `https://www.eta.gov.lk/slvisa/visainfo/shortvisit.jsp?locale=en_US`
- `https://www.eta.gov.lk/slvisa/visainfo/apply.jsp?locale=en_US`
- `https://www.eta.gov.lk/slvisa/visainfo/fees.jsp?locale=en_US`
- `https://www.eta.gov.lk/slvisa/visainfo/faq.jsp?locale=en_US`
- homepage alerts on `https://www.eta.gov.lk/slvisa/`

## What each page is best for
- `center.jsp` -> ETA overview, stay-duration framing
- `shortvisit.jsp` -> visit categories, tourist/business/transit descriptions, some entry wording
- `apply.jsp` -> application channels, core requirements, some validity wording, payment notes
- `fees.jsp` -> standard fee structure
- `faq.jsp` -> extra clarifications, but also wording that can conflict with other pages
- homepage alerts -> special regimes / overrides / temporary policy notices

## Extraction strategy
1. Read homepage alerts first.
2. Read the five public info pages above.
3. Extract fee structure from `fees.jsp`.
4. Cross-check every fee interpretation against homepage alerts.
5. Build the workbook around group-based pricing, not country-by-country logic.

## Important source behavior
- Public pages are server-rendered and fetchable directly.
- The site is not JS-heavy for info extraction.
- The hardest part is policy inconsistency, not technical scraping.
