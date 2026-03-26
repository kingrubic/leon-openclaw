import json
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
TODAY_TAB = '26Mar26'


def load_token():
    data = json.loads(TOKEN_PATH.read_text())
    token = data['token']
    if token.get('access_token'):
        return token['access_token']
    raise RuntimeError('Missing access token')


def refresh_access_token_if_needed():
    data = json.loads(TOKEN_PATH.read_text())
    token = data['token']
    if not token.get('refresh_token'):
        return
    creds = json.loads((WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.oauth-client.json').read_text())['web']
    body = {
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': token['refresh_token'],
        'grant_type': 'refresh_token',
    }
    import urllib.parse
    req = Request(
        'https://oauth2.googleapis.com/token',
        data=urllib.parse.urlencode(body).encode('utf-8'),
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    with urlopen(req, timeout=120) as resp:
        refreshed = json.loads(resp.read().decode('utf-8'))
    token['access_token'] = refreshed['access_token']
    token['expires_in'] = refreshed.get('expires_in', token.get('expires_in'))
    token['token_type'] = refreshed.get('token_type', token.get('token_type'))
    token['scope'] = refreshed.get('scope', token.get('scope'))
    data['token'] = token
    if refreshed.get('scope'):
        data['scope'] = refreshed['scope']
    TOKEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def http_json(url, method='GET', data=None):
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8',
    }
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def create_spreadsheet(title):
    body = {
        'properties': {'title': title},
        'sheets': [
            {'properties': {'title': 'Base'}},
        ]
    }
    return http_json('https://sheets.googleapis.com/v4/spreadsheets', method='POST', data=body)


def batch_update_sheet(spreadsheet_id, requests):
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate', method='POST', data={'requests': requests})


def update_values(spreadsheet_id, rng, values):
    from urllib.parse import quote
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{quote(rng)}?valueInputOption=RAW'
    return http_json(url, method='PUT', data={'range': rng, 'majorDimension': 'ROWS', 'values': values})


def create_doc(title):
    body = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    return http_json('https://www.googleapis.com/drive/v3/files', method='POST', data=body)


def get_doc(doc_id):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')


def doc_batch_update(doc_id, requests):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def build_sheet_values():
    return [
        ['Nationality / Group', 'Tourist ETA (online / mission / DI&E)', 'Business ETA (online / mission / DI&E)', 'Transit ETA', 'Tourist ETA (on arrival)', 'Business ETA (on arrival)', 'Transit ETA (on arrival)', 'Validity / Entry', 'Key Notes'],
        ['SAARC countries', 'US$20', 'US$30', 'Free', 'US$25', '----', 'Free', 'Tourist 30 days / Business 30 days / Transit 2 days', 'Official fee page shows standard SAARC ETA fees.'],
        ['All other countries', 'US$50', 'US$55', 'Free', 'US$60', '----', 'Free', 'Tourist 30 days / Business 30 days / Transit 2 days', 'Official fee page shows standard non-SAARC ETA fees.'],
        ['Children under 12 (any nationality)', 'Free', 'Free', 'Free', 'Free', '----', 'Free', 'Short visit ETA categories', 'Fee page shows free pricing across main ETA categories; apply policy interpretation carefully by travel case.'],
        ['China', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['India', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['Indonesia', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['Russia', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['Thailand', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['Malaysia', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
        ['Japan', 'Free of charge under homepage special regime', 'Needs case-by-case validation', 'Not separately stated', 'Not relied upon', 'Not relied upon', 'Not relied upon', '30-day free visa period / double-entry tourist wording on homepage alert', 'Homepage alert says travelers should still apply for ETA before travel.'],
    ]


def apply_basic_sheet_format(spreadsheet_id, sheet_id, row_count, col_count):
    requests = [
        {'duplicateSheet': {'sourceSheetId': sheet_id, 'newSheetName': TODAY_TAB, 'insertSheetIndex': 1}},
        {'repeatCell': {'range': {'sheetId': sheet_id, 'startRowIndex': 0, 'endRowIndex': 1}, 'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.86, 'green': 0.92, 'blue': 0.98}, 'textFormat': {'bold': True}}}, 'fields': 'userEnteredFormat(backgroundColor,textFormat.bold)'}},
        {'autoResizeDimensions': {'dimensions': {'sheetId': sheet_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': col_count}}},
        {'updateSheetProperties': {'properties': {'sheetId': sheet_id, 'gridProperties': {'frozenRowCount': 1}}, 'fields': 'gridProperties.frozenRowCount'}},
    ]
    batch_update_sheet(spreadsheet_id, requests)
    meta = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}')
    today_id = next(s['properties']['sheetId'] for s in meta['sheets'] if s['properties']['title'] == TODAY_TAB)
    requests2 = [
        {'repeatCell': {'range': {'sheetId': today_id, 'startRowIndex': 0, 'endRowIndex': 1}, 'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.86, 'green': 0.92, 'blue': 0.98}, 'textFormat': {'bold': True}}}, 'fields': 'userEnteredFormat(backgroundColor,textFormat.bold)'}},
        {'autoResizeDimensions': {'dimensions': {'sheetId': today_id, 'dimension': 'COLUMNS', 'startIndex': 0, 'endIndex': col_count}}},
        {'updateSheetProperties': {'properties': {'sheetId': today_id, 'gridProperties': {'frozenRowCount': 1}}, 'fields': 'gridProperties.frozenRowCount'}},
        {'updateCells': {'range': {'sheetId': today_id, 'startRowIndex': 1, 'startColumnIndex': 0}, 'rows': [], 'fields': 'userEnteredFormat.textFormat.bold'}},
    ]
    batch_update_sheet(spreadsheet_id, requests2)
    return today_id


def build_doc_lines(sheet_url):
    return [
        'SRI LANKA ETA REPORT',
        'Management summary based on official public ETA sources only',
        '',
        'Date: 26 Mar 2026',
        'Primary official domain: https://www.eta.gov.lk/',
        f'Detailed fee sheet: {sheet_url}',
        '',
        '1. EXECUTIVE SUMMARY',
        '',
        'This report summarizes the current Sri Lanka ETA public information suitable for internal operational use. The content has been QA-reviewed against multiple official ETA pages and is written conservatively to avoid overstatement where the official site is internally inconsistent.',
        '',
        'Key takeaways:',
        '- Sri Lanka ETA is the official pre-travel authorization framework for short tourist, business, and transit visits.',
        '- Core ETA categories confirmed on the site: Tourist, Business, Transit.',
        '- Standard ETA fee structure is clearly published for SAARC countries, all other countries, and children under 12.',
        '- A homepage alert currently shows a fee-free / visa-free special regime for China, India, Indonesia, Russia, Thailand, Malaysia, and Japan, but those travelers are still instructed to obtain ETA before travel.',
        '- Business ETA rules are not fully harmonized across the official pages; entry type and channel eligibility require cautious wording.',
        '',
        '2. CONFIRMED ETA CATEGORIES',
        '',
        '- Tourist',
        '- Business',
        '- Transit',
        '',
        '3. VALIDITY, ENTRY, AND STAY',
        '',
        '- Tourist ETA is generally described as 30 days with double entry.',
        '- Transit ETA is described as free and valid for up to 2 days.',
        '- Official pages state ETA holders may enter Sri Lanka within 3 months from date of issue.',
        '- Official pages also state the stay granted is initially limited to 30 days from arrival and may be extended up to 6 months.',
        '- Business ETA wording is inconsistent across pages: some official pages say double entry, while others say multiple entry for 30 days.',
        '',
        '4. REQUIRED DOCUMENTS / PORT-OF-ENTRY CONDITIONS',
        '',
        '- Passport valid for at least 6 months from date of arrival.',
        '- Confirmed return / onward ticket.',
        '- Sufficient funds for the stay.',
        '- Documentary proof is explicitly mentioned for Transit ETA.',
        '- Relevant documentary proof of business intent is mentioned for business travel.',
        '',
        '5. OFFICIAL FEE SUMMARY',
        '',
        'Standard ETA fee structure from the official fee page:',
        '- SAARC: Tourist US$20 / Business US$30 / Transit Free.',
        '- All other countries: Tourist US$50 / Business US$55 / Transit Free.',
        '- Children under 12: Free in the main ETA fee table.',
        '- On arrival: Tourist SAARC US$25 / Tourist other countries US$60 / Transit Free.',
        '- On-arrival business fee is not clearly stated; the fee page shows dashed cells (----).',
        '',
        '6. SPECIAL REGIME / EXCEPTION ALERT',
        '',
        '- The homepage alert currently indicates a fee-free / visa-free regime for China, India, Indonesia, Russia, Thailand, Malaysia, and Japan.',
        '- However, the same alert still instructs those travelers to apply for ETA before travel.',
        '- Therefore, internal systems should not simplify this rule into “no ETA required.”',
        '',
        '7. IMPORTANT QA CAVEATS',
        '',
        '- Do not state that the seven highlighted nationalities are fully visa-free without qualification.',
        '- Do not state that no ETA is needed for those seven nationalities.',
        '- Do not state that business ETA is always online, always double entry, or always multiple entry.',
        '- Do not rely on on-arrival ETA as the default recommendation; the site presents it as a limited facility.',
        '- Read the fee table together with homepage alerts, because alerts may override standard fee assumptions for specific nationalities.',
        '',
        '8. RECOMMENDED INTERNAL WORDING',
        '',
        '- Use: “The official ETA site currently shows a fee-free / visa-free special regime for seven nationalities, while still instructing those travelers to obtain ETA before travel.”',
        '- Use: “Business-visit handling requires careful review because official pages contain inconsistent wording on entry count and application channel.”',
        '- Use: “ETA validity and stay wording should be interpreted carefully because the site mixes the pre-travel validity window, stay granted on arrival, and extension concepts.”',
        '',
        '9. DELIVERABLES',
        '',
        f'- Detailed pricing workbook: {sheet_url}',
        '- This workbook is structured in the same operational style as the India sheet, but adapted to Sri Lanka’s fee logic (group-based pricing plus special-country exceptions).',
    ]


def format_doc(doc_id, lines):
    text = '\n'.join(lines)
    doc = get_doc(doc_id)
    end_idx = doc['body']['content'][-1]['endIndex']
    requests = []
    if end_idx > 2:
        requests.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_idx - 1}}})
    requests.append({'insertText': {'location': {'index': 1}, 'text': text}})
    idx = 1
    starts = []
    for line in lines:
        starts.append(idx)
        idx += len(line) + 1
    h1 = {'SRI LANKA ETA REPORT'}
    h2 = {line for line in lines if line[:2].isdigit() and '. ' in line}
    for i, line in enumerate(lines):
        start = starts[i]
        end = start + len(line)
        if line in h1:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line in h2:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_2'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('Key takeaways:') or line.startswith('Standard ETA fee structure'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('- Do not state') or line.startswith('- Use:'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})
    doc_batch_update(doc_id, requests)


def main():
    refresh_access_token_if_needed()
    values = build_sheet_values()
    spreadsheet = create_spreadsheet('Sri Lanka ETA - Official Fee Tracker')
    spreadsheet_id = spreadsheet['spreadsheetId']
    base_id = spreadsheet['sheets'][0]['properties']['sheetId']
    update_values(spreadsheet_id, 'Base!A1:I{}'.format(len(values)), values)
    today_id = apply_basic_sheet_format(spreadsheet_id, base_id, len(values), len(values[0]))
    update_values(spreadsheet_id, f'{TODAY_TAB}!A1:I{len(values)}', values)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={today_id}'

    doc = create_doc('Sri Lanka ETA report - 26 Mar 2026')
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    lines = build_doc_lines(sheet_url)
    format_doc(doc_id, lines)

    print(json.dumps({'sheet_url': sheet_url, 'doc_url': doc_url, 'spreadsheet_id': spreadsheet_id, 'doc_id': doc_id}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
