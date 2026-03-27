# Australia Visa Deliverable Patterns

Use the smallest deliverable that answers the request.

## Pattern 1: Internal tracker row set

Use when the user wants structured operational data.

Suggested columns:

- Product
- Purpose
- Stay period
- Where applicant must be
- Fee wording
- Entry wording
- Key limitation
- QA note
- Source URL

## Pattern 2: Manager-ready summary

Use when the user wants a concise business-facing memo.

For the approved Australia daily-report flow, default to this structure instead:

1. TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA
2. TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA
3. TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG
4. CÁC LOẠI VISA HIỆN HÀNH
5. TIN TỨC VISA TỪ BÁO CHÍ
6. GHI CHÚ QUAN TRỌNG
7. NGUỒN THÔNG TIN
8. TECHNICAL CHANGELOG

Formatting reminders:
- sections 1..8 are real Google Docs headings
- visa/stream labels are bold only, not headings
- section 7 splits sources into `Web chính phủ` and `Link báo chí`

Keep it short. Prefer bullets over long paragraphs.

## Pattern 3: QA memo

Use when reviewing a draft prepared elsewhere.

Recommended structure:

- Safe to state confidently
- High-risk wording to avoid
- Ambiguities that must be caveated
- Source-risk assessment
- Suggested replacement wording

## Pattern 4: No-update note

Use when the 7-day news scan finds nothing actionable.

Suggested wording:

- `No relevant new visa or entry-rule items were found in the last 7 days on the approved secondary sources.`
- `Current reporting should remain anchored to Department of Home Affairs pages.`

## Output discipline

- Do not pad the report when no meaningful change exists.
- If secondary monitoring finds nothing, say so plainly.
- If an item is interesting but not authoritative, label it as secondary reporting.
