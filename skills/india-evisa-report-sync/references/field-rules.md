# Field rules

## Fee interpretation
- `00` = official source shows zero fee.
- Do **not** automatically rewrite that as “visa-free”.
- If Google Sheets renders `00` as `0`, explain the meaning in the report when relevant.
- `N/A` should be preserved only when the internal sheet intentionally uses it and the current official source set does not support a safer replacement.

## Sheet update rules
- Use `Base` as the presentation template.
- Create a dated tab from `Base`.
- Keep unchanged values unchanged.
- Update only cells that differ from the official source.
- Bold only changed values.
- If a fee group is not clearly covered by the official source set, retain the internal value and disclose that decision in the report.

## Report wording rules
Prefer:
- “official fee currently shows 0 USD”
- “internal value retained pending further official verification”
- “not clearly published in the official source set reviewed”
- “country/territory-specific pricing”

Avoid unless separately verified:
- “visa-free”
- “free visa”
- “no visa required”

## Report structure rules
Use this section order by default:
1. `TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA`
2. `TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA`
3. `TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG`
4. `CÁC LOẠI VISA HIỆN HÀNH`
5. `GHI CHÚ QUAN TRỌNG`
6. `NGUỒN THÔNG TIN`
7. `TECHNICAL CHANGELOG`

Default rules:
- Do not include `EXECUTIVE SUMMARY` unless explicitly requested.
- Do not include `TÓM TẮT THAY ĐỔI SO VỚI BASE / ĐẦU VÀO NỘI BỘ` unless explicitly requested.
- If there is no fee / policy / document / validity / entry-rule change vs yesterday, write exactly: `Không phát hiện sự thay đổi so với báo cáo hôm qua`.
- Put formatting-only or rendering-only differences such as `0 -> 00` into `TECHNICAL CHANGELOG`, not into the main business-change summary.
- In `NGUỒN THÔNG TIN`, list all reviewed official HTML pages, subpages, and PDFs.

## Country-name normalization examples
Common mismatches encountered in the March 2026 run:
- `Bosnia & Herzegovina` -> `Bosnia and Herzegovina`
- `Cameroon Republic` -> `Cameroon`
- `Cote D'Ivoire` -> `Ivory Coast`
- `Cayman Island` -> `Cayman Islands`
- `Gambia` -> `Gambia, The`
- `Republic Of Korea` -> `Korea, South`
- `Saint Christopher And Nevis` -> `Saint Kitts and Nevis`
- `Saint Vincent And The Grenadines` -> `Saint Vincent & the Grenadines`
- `Vatican City - Holy See` -> `Vatican City`
- `Niue Island` -> `Niue`
- `Trinidad And Tobago` -> `Trinidad and Tobago`

## Known official coverage caveat from March 2026
The reviewed official source set clearly covered fees for:
- Tourist
- Business
- Medical
- Medical Attendant
- Ayush
- Ayush Attendant
- Conference

It did **not** clearly provide a same-source fee table for:
- Student
- Transit

In that case, keep the internal values unless a newer official source is found.
