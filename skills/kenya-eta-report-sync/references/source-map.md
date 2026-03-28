# Kenya eTA Source Map

Use this file first.

## Primary domain
- `https://etakenya.go.ke/`

## Core official public pages

Start here, in this order:

1. Eligibility / product cards / country eligibility table  
   `https://etakenya.go.ke/eligibility`

2. General information / official rule framing / exemption list  
   `https://etakenya.go.ke/general-information`

3. FAQ / operational clarifications  
   `https://etakenya.go.ke/faqs`

4. Application start / traveler-type routing / exempt-country view  
   `https://etakenya.go.ke/form/apply/start`

5. How to apply — tourist / visitor flow  
   `https://etakenya.go.ke/form/apply/how-to-apply?type=tourist`

6. How to apply — diplomat flow  
   `https://etakenya.go.ke/form/apply/how-to-apply?type=diplomats`

7. Terms and conditions / refund + editability rules  
   `https://etakenya.go.ke/terms-and-conditions`

8. Privacy policy / document categories + data-processing wording  
   `https://etakenya.go.ke/privacy-policy`

## What each page is best for

- `eligibility` -> public product names, price points, category descriptions, country-level eligibility statuses
- `general-information` -> official eTA definition, processing guidance, point-of-entry discretion, exemption list
- `faqs` -> operational clarifications like per-person application, processing, fees, tracking, and standard-vs-expedited wording
- `form/apply/start` -> traveler-type routing, exempt-country list view, official start-of-application framing
- `form/apply/how-to-apply?type=tourist` -> core document checklist, 90-day travel-validity wording, business/family/diplomatic supporting-doc rules, long exemption list
- `form/apply/how-to-apply?type=diplomats` -> diplomat application route; currently same core content as tourist page but still worth re-checking
- `terms-and-conditions` -> non-refundable fee rule, correction-before-submission rule, post-submission risk
- `privacy-policy` -> full data categories, supporting-document types, formal legal wording, inability to delete submitted data

## Public product/fare snapshot confirmed in March 2026 crawl

From `eligibility`:
- `Transit eTA` -> `USD 20`
- `Standard eTA` -> `USD 30`
- `One Year Multi-Entry eTA` -> `USD 300`
- `Five Year Multi-Entry eTA` -> `USD 185`
- `East African Tourist eTA` -> `COMING SOON`

## Important public wording confirmed in March 2026 crawl

- eTA applications are usually processed in `3 days`
- site also shows a faster / urgent / expedited route
- application should be submitted `at least 2 weeks prior to travel` on general-information page
- tourist-facing how-to-apply page says the eTA is `valid for travel within 90 days from the date of issuance`
- duration of stay is determined at the point of entry
- final admissibility is determined at the point of entry

## Extraction strategy

1. Fetch the core pages directly as HTML first.
2. Parse visible text from server-rendered content.
3. Use DOM inspection or browser evaluation only for accordion answers or route-specific UI text.
4. Build one fact set for fee-based eTA products.
5. Build a separate fact set for exemptions and `ETA not required` regimes.
6. Cross-check the country table against the exemption pages before writing broad conclusions.

## Technical notes

- Site uses Phoenix LiveView assets (`/assets/app.js`) but public content is still extractable from the fetched HTML.
- Public info pages are not meaningfully blocked for direct fetch in normal use.
- Browser automation is optional support, not the default extraction path.
- FAQ content may be easiest to verify via DOM because accordion answers are present but not always cleanly surfaced by lightweight extractors.
