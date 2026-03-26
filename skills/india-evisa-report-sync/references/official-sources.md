# Official sources

## Primary page
- `https://indianvisaonline.gov.in/evisa/tvoa.html`

Use this page for:
- visa category list
- validity / entry / stay notes
- required documents
- advisory and application-timing guidance
- links to fee PDFs

## Fee PDFs used in the March 2026 workflow
- `https://indianvisaonline.gov.in/evisa/images/Etourist_fee_final.pdf`
- `https://indianvisaonline.gov.in/evisa/images/eTV_revised_fee_final.pdf`

## Best extraction path
1. Fetch HTML directly.
2. Parse DOM for category blocks and documents.
3. Parse the linked PDFs for pricing.
4. Compare against the internal Google Sheet.
5. Write the result to a dated tab + manager summary doc.

## Why this path works
- The site is largely server-rendered.
- Important content is present in raw HTML.
- Pricing is not fully embedded in visible text; PDFs must be parsed.
- Anti-bot resistance was low in the March 2026 run.

## Red flags to watch for in future runs
- renamed fee PDF URLs
- changed DOM ids/classes for visa detail blocks
- fee tables moved out of PDF into another format
- new e-Visa categories added without corresponding internal columns
- wording changes that make `00` or `N/A` ambiguous
