# Kenya eTA QA Rules

## High-risk interpretation areas

### 1. Validity vs stay vs admissibility
Do not compress these into one rule.

Keep separate:
- eTA valid for travel within 90 days from issuance
- processing time
- right to board / travel after approval
- actual duration of stay decided at point of entry
- final admissibility decided at point of entry

Unsafe example:
- `Kenya eTA cho ở 90 ngày`

Safer example:
- `Trang official hiện ghi eTA có hiệu lực để thực hiện chuyến đi trong vòng 90 ngày kể từ ngày cấp; thời gian lưu trú thực tế do cơ quan nhập cảnh quyết định tại cửa khẩu.`

### 2. `ETA not required` is not always the same as a simple “visa-free” statement
The Kenya public site mixes:
- explicit exemptions
- nationality-duration carve-outs
- transit / crew / same-ship / refueling carve-outs
- official-passport / laissez-passer regimes

Do not flatten all of these into a single `visa-free` label unless the exact official wording supports it.

Preferred wording:
- `official site currently lists this case under the eTA-exempt / ETA not required regime`
- `thuộc diện không cần eTA theo danh sách miễn trừ official`

### 3. Country table vs exemption list
If the country eligibility table and the long exemption list lead to a broad conclusion, cross-check before reporting.

Priority for interpretation:
1. exemption list pages (`general-information`, `how-to-apply`)
2. product cards and page-level notes on `eligibility`
3. country table row

If there is tension, mention the tension instead of hiding it.

### 4. Diplomatic wording trap
The FAQ says diplomats are generally required to complete an eTA, but standard eTA payment may be waived for diplomats.
Do not rewrite that as:
- `diplomats are exempt from eTA`
- `diplomats travel free without application`

Preferred wording:
- `travellers in the diplomatic category still need to complete the eTA flow; the FAQ states standard eTA payment is not required for diplomats, while faster service may still be chosen.`

### 5. Processing wording trap
The site currently shows both:
- general processing around 3 days / 72 hours / 3 working days
- expedited / urgent processing option

Do not promise instant approval as the default.
Do not replace `generally processed` with `guaranteed`.

### 6. Product-card trap
Do not change official product names casually.
Use exactly what the site shows unless the user explicitly wants an internal alias.

Especially preserve:
- `Standard eTA`
- `Transit eTA`
- `One Year Multi-Entry eTA`
- `Five Year Multi-Entry eTA`
- `East African Tourist eTA`

### 7. East African Tourist eTA status
If the site still says `COMING SOON`, treat it as unavailable / not yet active.
Do not write that it is currently open for application unless the official routes clearly change.

## Sheet rules

- Keep fee-based products and exemption regimes conceptually separate.
- If using one sheet, include a strong notes/caveat column.
- If updating an existing Base tab, preserve layout and unchanged values.
- Bold only materially changed operational cells.
- Do not erase caveat text just to make rows look cleaner.
- Prefer separate sections for:
  - fee-based eTA categories
  - exemption categories
  - supporting-document rules

## Report rules

- Write for Vietnamese leadership first.
- Use strong headings.
- Default section order:
  1. `TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA`
  2. `TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA`
  3. `TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG`
  4. `CÁC LOẠI ETA / DIỆN NHẬP CẢNH HIỆN HÀNH`
  5. `GHI CHÚ QUAN TRỌNG`
  6. `NGUỒN THÔNG TIN`
  7. `TECHNICAL CHANGELOG`
- Do not include `EXECUTIVE SUMMARY` unless explicitly requested.
- Do not include `TÓM TẮT THAY ĐỔI SO VỚI BASE / ĐẦU VÀO NỘI BỘ` unless explicitly requested.
- If there is no fee / policy / validity / processing / document / exemption / eligibility change vs yesterday, write exactly: `Không phát hiện sự thay đổi so với báo cáo hôm qua`.
- Put formatting-only or rendering-only diffs into `TECHNICAL CHANGELOG`.
- List all official URLs reviewed in `NGUỒN THÔNG TIN`.

## Safe claims from the March 2026 crawl

Generally safe to state if unchanged on re-check:
- all visitors including infants and children need approved eTA before travel unless exempt
- processing is generally around 3 working days / 72 hours
- site recommends applying at least 2 weeks before travel
- eTA is valid for travel within 90 days from issuance
- admissibility and stay are determined at the point of entry
- each traveler needs their own eTA even in a group
- core document set includes passport, photo/selfie, contact details, itinerary, and accommodation
- business and family travel require additional supporting documents
- standard public fee floor starts at `USD 30`; transit shows `USD 20`

## Claims to avoid stating flatly

- `Kenya tourist visa is valid for 90 days stay`
- `all transit passengers need Transit eTA`
- `all diplomats are eTA-exempt`
- `East African Tourist eTA is active`
- `ETA not required` always equals `visa-free`
- `processing is guaranteed in exactly 72 hours`
