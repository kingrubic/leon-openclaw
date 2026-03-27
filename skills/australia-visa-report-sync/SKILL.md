---
name: australia-visa-report-sync
description: Sync, audit, and report Australia visitor and short-stay visa information from official Australian government sources into internal summaries, trackers, or manager-facing reports. Use when checking Australia visitor visa products (especially Visitor 600, eVisitor 651, ETA 601, Transit 771, Medical Treatment 602), building or updating an Australia visa sheet/doc, doing source QA on Australia visa wording, or monitoring recent visa-related news from australia.com and Executive Traveller as secondary sources that must be cross-checked against Home Affairs.
---

# Australia Visa Report Sync

Use this skill to produce repeatable Australia visa research without re-discovering the workflow.

## Core rule

Treat **Department of Home Affairs** as the primary source of truth.

Use secondary sources such as **australia.com** and **Executive Traveller** only for supplementary travel/news context. Never let them override Home Affairs wording.

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

Choose the smallest useful output:

- internal tracker rows
- concise brief
- manager-ready memo
- QA note with risky claims to avoid

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
