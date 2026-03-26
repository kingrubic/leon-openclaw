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
