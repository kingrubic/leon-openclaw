# Australia Visa Source Map

Use this file first.

## Primary sources: Australian Government / Home Affairs

Start here, in this order:

1. ImmiAccount / official online entry point  
   `https://online.immi.gov.au/`

2. Visitor visa finder / category landing page  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-finder/visit`

3. Visitor visa (subclass 600)  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600`

4. eVisitor (subclass 651)  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/evisitor-651`

5. Electronic Travel Authority (subclass 601)  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/electronic-travel-authority-601`

6. Transit visa (subclass 771)  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771`

7. Medical Treatment visa (subclass 602)  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/medical-treatment-602`

8. Global visa processing times tool / guidance page  
   `https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-processing-times/global-visa-processing-times`

## Secondary sources: use only after official extraction

1. Tourism Australia  
   `https://www.australia.com/`

2. Executive Traveller  
   `https://www.executivetraveller.com/`

## Crawl order by task

### A. Official product sync

1. Open the visitor landing page.
2. Visit each product page relevant to the request.
3. Extract stream-specific facts.
4. Check processing-times guidance only if the user asked for it.

### B. QA audit

1. Re-open the exact product pages cited in the draft.
2. Verify whether each claim is:
   - directly stated,
   - implied but risky,
   - unsupported.
3. Rewrite broad claims into precise Home Affairs-style wording.

### C. Recent-news check

1. Search the last 7 days on australia.com and Executive Traveller.
2. Ignore evergreen pages unless the user explicitly asked for reference pages.
3. If a news item appears important, verify whether Home Affairs reflects the same change.

## Notes learned from prior runs

- Prefer direct product pages over general travel explainers.
- Treat processing-time guidance as a live, tool-based reference rather than a permanent fact.
- Nationality/passport eligibility for ETA/eVisitor can be the most important unresolved gap; flag it if not fully captured.
- If a page says `from AUD ...`, preserve the `from` wording.
