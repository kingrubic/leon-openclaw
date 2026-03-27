import json
import re
import urllib.parse
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
OAUTH_CLIENT_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.oauth-client.json'
DATE_TEXT = '27 Mar 2026'
DATE_VI = '27/03/2026'
TODAY_TAB = '27Mar26'
SUMMARY_SHEET_ID = '1XHtNTEb8XXyCrQcWYYMsK8lu0DZ2Jynmp8SlXJVI1Ag'
SUMMARY_TAB = 'Sheet1'
SUMMARY_LINK = f'https://docs.google.com/spreadsheets/d/{SUMMARY_SHEET_ID}/edit#gid=0'
WORKBOOK_TITLE = 'Indonesia Visa - Official Tracker'
DOC_TITLE = f'Indonesia visa trial report - {DATE_TEXT}'
COUNTRY_AUSTRALIA = '46283cb1-d406-47c1-86fd-8c308ffa173a'
VISA_SELECTION_URL = 'https://evisa.imigrasi.go.id/web/visa-selection/data'

PARENT_ACTIVITIES = {
    'General, Family, or Social': 'd5bc2168-2f4a-4396-8eae-3d895a0508e9',
    'Investment, Business, or Government': 'f7a8ac1d-a71f-45d3-919f-985e295533f2',
}

TRACKED_ACTIVITIES = {
    'Tourism, Family Visit, and Transit': 'f0c05fe2-f8d6-4bf1-904c-9fa5a694162f',
    'Business, Meeting, and Goods Purchasing': 'a28fb987-2d56-4e92-aa34-aaaadb831fae',
    'Government Business': '287a2fba-9d96-44da-a91d-e69b07bbd44b',
}

TRACKED_VISAS = [
    'B1 - Tourist (Visa On Arrival)',
    'C1 - Tourist Single Entry Visitor Visa -  60 Days',
    'D1 - Tourist Multiple Entry Visa (1 Year)',
    'D1 - Tourist Multiple Entry Visa (2 Years)',
    'D1 - Tourist Multiple Entry Visa (5 Years)',
    'C2 - Business Single Entry Visa',
    'D2 - Business Multiple Entry Visa (1 Year)',
    'D2 - Business Multiple Entry Visa (2 Years)',
    'D2 - Business Multiple Entry Visa (5 Years)',
    'B4 - Government Business (Visa On Arrival)',
    'C4 - Government Business',
    'D4 - Government Business Multiple Entry Visa (1 Year)',
    'D4 - Government Business Multiple Entry Visa (2 Years)',
]

PRESS_LINKS = [
    'https://www.indonesia.travel/',
    'https://www.thejakartapost.com/',
]

SOURCE_URLS = [
    'https://evisa.imigrasi.go.id/',
    'https://evisa.imigrasi.go.id/web/visa-selection',
    'https://evisa.imigrasi.go.id/web/visa-selection/data',
    'https://evisa.imigrasi.go.id/front/info/evoa',
    'https://evisa.imigrasi.go.id/front/register',
]


def load_json(path):
    return json.loads(path.read_text())


def refresh_access_token_if_needed():
    data = load_json(TOKEN_PATH)
    token = data['token']
    refresh_token = token.get('refresh_token')
    if not refresh_token:
        return
    creds = load_json(OAUTH_CLIENT_PATH)['web']
    body = urllib.parse.urlencode({
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }).encode('utf-8')
    req = Request('https://oauth2.googleapis.com/token', data=body, headers={'Content-Type': 'application/x-www-form-urlencoded'}, method='POST')
    with urlopen(req, timeout=120) as resp:
        refreshed = json.loads(resp.read().decode('utf-8'))
    token['access_token'] = refreshed['access_token']
    token['expires_in'] = refreshed.get('expires_in', token.get('expires_in'))
    token['token_type'] = refreshed.get('token_type', token.get('token_type'))
    token['scope'] = refreshed.get('scope', token.get('scope'))
    data['token'] = token
    TOKEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def access_token():
    return load_json(TOKEN_PATH)['token']['access_token']


def google_json(url, method='GET', data=None):
    headers = {
        'Authorization': f'Bearer {access_token()}',
        'Content-Type': 'application/json; charset=utf-8',
    }
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def form_post(url, data):
    req = Request(url, data=urllib.parse.urlencode(data).encode('utf-8'), headers={
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    })
    with urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def clean_html(html):
    text = unescape(html or '')
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_activity_map():
    activity_map = {}
    for parent_name, parent_id in PARENT_ACTIVITIES.items():
        result = form_post(VISA_SELECTION_URL, {'parent_id': parent_id, 'step': '0'})
        for item in result.get('data', []):
            activity_map[item['name']] = item['id']
    return activity_map


def get_visa_options(activity_id):
    result = form_post(VISA_SELECTION_URL, {'activity_id': activity_id, 'country_id': COUNTRY_AUSTRALIA, 'step': '1'})
    return result.get('data', []), result.get('all', [])


def get_visa_detail(visa_type_id):
    result = form_post(VISA_SELECTION_URL, {'visa_type_id': visa_type_id, 'step': '2'})
    data = result['data']
    visa = data['visaType'][0]
    stays = []
    for stay in data.get('limitedStay', []):
        unit = json.loads(stay['name'])['en']
        if int(stay['value']) > 1:
            if unit == 'DAY':
                unit = 'DAYS'
            elif unit == 'YEAR':
                unit = 'YEARS'
            elif unit == 'MONTH':
                unit = 'MONTHS'
        stays.append(f"{stay['value']} {unit}")
    visa['stays'] = stays
    visa['term_text'] = clean_html(visa.get('term', ''))
    return visa


def build_rows(visa_data):
    rows = [[
        'Visa / stream', 'Purpose / use case', 'Stay / validity', 'Cost', 'Processing times',
        'Application channel', 'Key eligibility / docs cues', 'Important notes', 'Official source'
    ]]
    for item in visa_data:
        rows.append([
            item['name'],
            item['desc'],
            item['stay_validity'],
            item['cost'],
            item['processing'],
            item['channel'],
            item['docs'],
            item['notes'],
            item['source'],
        ])
    return rows


def ensure_workbook():
    q = urllib.parse.urlencode({
        'q': f"name = '{WORKBOOK_TITLE}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        'fields': 'files(id,name)'
    })
    found = google_json(f'https://www.googleapis.com/drive/v3/files?{q}')
    files = found.get('files', [])
    if files:
        return files[0]['id']
    created = google_json('https://sheets.googleapis.com/v4/spreadsheets', method='POST', data={'properties': {'title': WORKBOOK_TITLE}})
    ssid = created['spreadsheetId']
    meta = google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}')
    default_id = meta['sheets'][0]['properties']['sheetId']
    google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}:batchUpdate', method='POST', data={'requests': [
        {'updateSheetProperties': {'properties': {'sheetId': default_id, 'title': 'Base'}, 'fields': 'title'}},
        {'duplicateSheet': {'sourceSheetId': default_id, 'newSheetName': TODAY_TAB, 'insertSheetIndex': 1}},
    ]})
    return ssid


def ensure_tab(ssid, title):
    meta = google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}')
    ids = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    if title not in ids:
        google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}:batchUpdate', method='POST', data={'requests': [
            {'duplicateSheet': {'sourceSheetId': ids['Base'], 'newSheetName': title, 'insertSheetIndex': len(ids)}}
        ]})
        meta = google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}')
        ids = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    return ids


def update_values(ssid, tab, rows):
    rng = f'{tab}!A1:I{len(rows)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}/values/{urllib.parse.quote(rng)}?valueInputOption=RAW'
    return google_json(url, method='PUT', data={'range': rng, 'majorDimension': 'ROWS', 'values': rows})


def format_sheet(ssid, tabs, row_count):
    reqs = []
    widths = {0: 250, 1: 240, 2: 220, 3: 155, 4: 210, 5: 165, 6: 250, 7: 260, 8: 330}
    for tab, sid in tabs.items():
        if tab not in ('Base', TODAY_TAB):
            continue
        reqs.extend([
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 9}, 'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.82, 'green': 0.89, 'blue': 0.95}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'WRAP', 'textFormat': {'bold': True, 'fontSize': 10}}}, 'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat.bold,textFormat.fontSize)'}},
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': row_count, 'startColumnIndex': 0, 'endColumnIndex': 9}, 'cell': {'userEnteredFormat': {'verticalAlignment': 'TOP', 'wrapStrategy': 'WRAP', 'textFormat': {'fontSize': 10}}}, 'fields': 'userEnteredFormat(verticalAlignment,wrapStrategy,textFormat.fontSize)'}},
            {'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}}, 'fields': 'gridProperties.frozenRowCount'}},
            {'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1}, 'properties': {'pixelSize': 58}, 'fields': 'pixelSize'}},
            {'updateBorders': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': row_count, 'startColumnIndex': 0, 'endColumnIndex': 9}, 'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}, 'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}}},
        ])
        for col, width in widths.items():
            reqs.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': col, 'endIndex': col + 1}, 'properties': {'pixelSize': width}, 'fields': 'pixelSize'}})
    google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{ssid}:batchUpdate', method='POST', data={'requests': reqs})


def create_doc():
    created = google_json('https://www.googleapis.com/drive/v3/files', method='POST', data={'name': DOC_TITLE, 'mimeType': 'application/vnd.google-apps.document'})
    return created['id']


def get_doc(doc_id):
    return google_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')


def update_doc(doc_id, lines):
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
    section_heads = {line for line in lines if line[:2].isdigit() and '. ' in line}
    bold_labels = {
        'B1 - Tourist (Visa On Arrival)',
        'C1 - Tourist Single Entry Visitor Visa - 60 Days',
        'D1 - Tourist Multiple Entry Visa (1 Year)',
        'D1 - Tourist Multiple Entry Visa (2 Years)',
        'D1 - Tourist Multiple Entry Visa (5 Years)',
        'C2 - Business Single Entry Visa',
        'D2 - Business Multiple Entry Visa (1 Year)',
        'D2 - Business Multiple Entry Visa (2 Years)',
        'D2 - Business Multiple Entry Visa (5 Years)',
        'B4 - Government Business (Visa On Arrival)',
        'C4 - Government Business',
        'D4 - Government Business Multiple Entry Visa (1 Year)',
        'D4 - Government Business Multiple Entry Visa (2 Years)',
        'Web chính phủ',
        'Link báo chí',
    }
    for i, line in enumerate(lines):
        start = starts[i]
        end = start + len(line)
        if line == 'BÁO CÁO THEO DÕI VISA INDONESIA':
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'TITLE', 'alignment': 'CENTER'}, 'fields': 'namedStyleType,alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 22, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
        elif line.startswith('Scope trial:') or line.startswith('Ngày chạy baseline:'):
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'alignment': 'CENTER'}, 'fields': 'alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.35, 'green': 0.35, 'blue': 0.35}}}}, 'fields': 'italic,foregroundColor'}})
        elif line in section_heads:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.12, 'green': 0.33, 'blue': 0.53}}}}, 'fields': 'bold,foregroundColor'}})
        elif line in bold_labels:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('Kết luận chính:') or line.startswith('Sheet chi tiết phí / stay / channel / notes:'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
    phrases = ['Không phát hiện tin tức mới liên quan đến Visa trong 7 ngày gần nhất.', 'IDR 1,000,000', 'IDR 2,000,000', 'IDR 3,000,000', 'IDR 4,000,000', 'Rp500.000', '60 Days', '30 days', '1 Year', '2 Years', '5 Years']
    for phrase in phrases:
        start_at = 0
        while True:
            pos = text.find(phrase, start_at)
            if pos == -1:
                break
            requests.append({'updateTextStyle': {'range': {'startIndex': 1 + pos, 'endIndex': 1 + pos + len(phrase)}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
            start_at = pos + len(phrase)
    google_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def build_lines(sheet_url):
    return [
        'BÁO CÁO THEO DÕI VISA INDONESIA',
        'Scope trial: B1 / C1 / D1 / C2 / D2 / B4 / C4 / D4 trên cổng eVisa Indonesia',
        f'Ngày chạy baseline: {DATE_VI}',
        '',
        '1. TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA',
        '',
        'Kết luận chính: Chưa có baseline Indonesia của hôm qua trong hệ thống nội bộ cho scope trial này.',
        'Báo cáo hôm nay được dùng làm bản baseline đầu tiên.',
        '',
        '2. TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA',
        '',
        'Kết luận chính: Chưa đủ chuỗi dữ liệu nội bộ 7 ngày cho Indonesia trong scope này.',
        'Báo cáo hôm nay là mốc baseline để bắt đầu theo dõi biến động hằng ngày.',
        '',
        '3. TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG',
        '',
        'Kết luận chính: Chưa có dữ liệu nội bộ được chuẩn hóa từ đầu tháng cho Indonesia trong scope trial này.',
        'Từ ngày mai có thể bắt đầu so sánh day-over-day, rolling 7 days, và month-to-date trên cùng format.',
        '',
        '4. CÁC LOẠI VISA HIỆN HÀNH',
        '',
        'B1 - Tourist (Visa On Arrival)',
        '- Stay: up to 30 days, extendable for another 30 days.',
        '- Cost: Rp500.000.',
        '- Use case: du lịch, thăm thân, business discussion / negotiation / ký kết, site visit, và một số medical-related activities theo wording official.',
        '- Caveat: official B1 wording hiện rộng hơn tên “Tourist”, nên không nên diễn giải chỉ dùng cho du lịch thuần túy.',
        '',
        'C1 - Tourist Single Entry Visitor Visa - 60 Days',
        '- Stay: up to 60 days, extendable.',
        '- Cost: IDR 1,000,000.',
        '- Processing: most tourist visas are processed within 5 working days theo wording trên term detail đã lấy hôm nay.',
        '- Use case: tourism, visiting friends or family, transit, và tham gia MICE với tư cách participant theo wording official.',
        '',
        'D1 - Tourist Multiple Entry Visa (1 Year)',
        '- Validity / stay: valid 1 year; up to 60 days per entry.',
        '- Cost: IDR 3,000,000.',
        '- Use case: tourism / visiting friends or family / MICE participant.',
        '',
        'D1 - Tourist Multiple Entry Visa (2 Years)',
        '- Validity / stay: valid 2 years; up to 60 days per entry.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'D1 - Tourist Multiple Entry Visa (5 Years)',
        '- Validity / stay: valid 5 years; up to 60 days per entry.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'C2 - Business Single Entry Visa',
        '- Stay: up to 60 days, extendable.',
        '- Cost: IDR 2,000,000.',
        '- Use case: business, meetings, goods purchasing, checking goods/site, discussion, negotiation, signing contracts.',
        '',
        'D2 - Business Multiple Entry Visa (1 Year)',
        '- Validity / stay: valid 1 year; up to 60 days per entry.',
        '- Cost: IDR 4,000,000.',
        '- Use case: recurring business visit under official D2 wording.',
        '',
        'D2 - Business Multiple Entry Visa (2 Years)',
        '- Validity / stay: valid 2 years; up to 60 days per entry.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'D2 - Business Multiple Entry Visa (5 Years)',
        '- Validity / stay: valid 5 years; up to 60 days per entry.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'B4 - Government Business (Visa On Arrival)',
        '- Stay: up to 30 days, extendable for another 30 days.',
        '- Cost: Rp500.000.',
        '- Use case: government business; official term also still mentions tourism / visiting friends or family as allowed related activities in the pulled wording.',
        '',
        'C4 - Government Business',
        '- Stay: up to 60 days, extendable.',
        '- Cost: IDR 2,000,000.',
        '- Use case: official government duties.',
        '',
        'D4 - Government Business Multiple Entry Visa (1 Year)',
        '- Validity / stay: valid 1 year; up to 60 days per entry according to current selector detail set.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'D4 - Government Business Multiple Entry Visa (2 Years)',
        '- Validity / stay: valid 2 years; up to 60 days per entry according to current selector detail set.',
        '- Cost: fee captured in sheet from official selector detail set used today.',
        '',
        'Sheet chi tiết phí / stay / channel / notes:',
        sheet_url,
        '',
        '5. TIN TỨC VISA TỪ BÁO CHÍ',
        '',
        'Không phát hiện tin tức mới liên quan đến Visa trong 7 ngày gần nhất.',
        '',
        '6. GHI CHÚ QUAN TRỌNG',
        '',
        '- MOLINA / eVisa Indonesia có endpoint dữ liệu nội bộ khá hữu ích tại /web/visa-selection/data; trial hôm nay dùng dữ liệu đó kết hợp với trang FAQ eVOA để lấy product map nhanh hơn so với click tay.',
        '- B1/B4 là các route Visa On Arrival; wording official hiện cho phép nhiều hoạt động hơn tên gọi ngắn của visa. Khi tư vấn cần bám đúng “with this visa you can” thay vì suy diễn từ label.',
        '- C1/C2/C4 hiện cho thấy stay up to 60 days và extendable trên detail official đã pull hôm nay.',
        '- D-series multiple-entry đang cho thấy logic valid 1/2/5 years với stay up to 60 days per entry. Cần tiếp tục QA kỹ phí 2 năm / 5 năm ở các lần chạy sau để khóa wording và fee table gọn hơn.',
        '- Wording về validity period và period of stay trên Indonesia site cần tách bạch rõ; ít nhất eVOA info page nêu Visitor Visa validity 90 days nhưng stay chỉ 30 days.',
        '- Một số visa type yêu cầu guarantor; trial hôm nay ưu tiên các route public dễ theo dõi daily trước.',
        '',
        '7. NGUỒN THÔNG TIN',
        '',
        'Web chính phủ',
        '- https://evisa.imigrasi.go.id/',
        '- https://evisa.imigrasi.go.id/web/visa-selection',
        '- https://evisa.imigrasi.go.id/web/visa-selection/data',
        '- https://evisa.imigrasi.go.id/front/info/evoa',
        '- https://evisa.imigrasi.go.id/front/register',
        '',
        'Link báo chí',
        '- https://www.indonesia.travel/',
        '- https://www.thejakartapost.com/',
        '',
        '8. TECHNICAL CHANGELOG',
        '',
        '- Đây là baseline đầu tiên cho Indonesia nên chưa có diff kỹ thuật với report hôm trước.',
        '- Trial hôm nay dùng country selector Australia để kiểm route public đủ điều kiện và lấy product map ban đầu; scope daily sau này có thể cần mở thêm logic country-specific nếu nghiệp vụ muốn theo dõi khác biệt theo quốc tịch.',
    ]


def update_summary_tracker(doc_url, sheet_url, summary_text):
    rng = f'{SUMMARY_TAB}!A1:H20'
    data = google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SUMMARY_SHEET_ID}/values/{urllib.parse.quote(rng)}')
    values = data.get('values', [])
    next_row = len(values) + 1
    row = [[str(next_row - 1), '27 Mar 26', '10:04', 'Indonesia', doc_url, sheet_url, 'Không', summary_text]]
    put_rng = f'{SUMMARY_TAB}!A{next_row}:H{next_row}'
    google_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SUMMARY_SHEET_ID}/values/{urllib.parse.quote(put_rng)}?valueInputOption=RAW', method='PUT', data={'range': put_rng, 'majorDimension': 'ROWS', 'values': row})


def main():
    refresh_access_token_if_needed()
    get_activity_map()
    visa_map = {}
    for act_name, act_id in TRACKED_ACTIVITIES.items():
        data, _ = get_visa_options(act_id)
        for item in data:
            if item['name'] in TRACKED_VISAS:
                visa_map[item['name']] = item['id']
    visa_data = []
    order = [name for name in TRACKED_VISAS if name in visa_map]
    for name in order:
        detail = get_visa_detail(visa_map[name])
        term_text = detail['term_text']
        cost = 'Needs extraction re-check'
        m = re.search(r'Cost\s+([^\.]+?)(?:\s+With this visa|\s+Processing Time|$)', term_text, re.I)
        if m:
            cost = m.group(1).strip()
        processing = 'Not stated in captured detail'
        pm = re.search(r'Processing Time\s+(.+?)\s+With this visa', term_text, re.I)
        if pm:
            processing = pm.group(1).strip()
        elif 'Visa On Arrival' in name:
            processing = 'On-arrival route / no separate e-visa processing-time wording captured for this trial row'
        stay_validity = ''
        if 'Multiple Entry Visa (1 Year)' in name:
            stay_validity = 'Valid 1 year; up to 60 days per entry'
        elif 'Multiple Entry Visa (2 Years)' in name:
            stay_validity = 'Valid 2 years; up to 60 days per entry'
        elif 'Multiple Entry Visa (5 Years)' in name:
            stay_validity = 'Valid 5 years; up to 60 days per entry'
        elif '30' in term_text and 'extendable for another 30 days' in term_text:
            stay_validity = 'Up to 30 days; extendable for another 30 days'
        elif detail['stays']:
            stay_validity = ', '.join(detail['stays']) + ('; extendable' if 'Extendable' in term_text or 'extendable' in term_text else '')
        else:
            stay_validity = 'Need re-check'
        docs = 'Passport valid at least 6 months; additional docs depend on visa type and channel.'
        if 'Document Requirement' in term_text:
            docs = term_text.split('Document Requirement', 1)[1][:280].strip()
        notes = 'Official detail captured from visa selector.'
        if detail.get('is_arrival'):
            notes = 'Visa On Arrival route; check eligible nationality and port-of-entry handling each run.'
        if detail.get('is_multiple_entry'):
            notes = 'Multiple-entry product; keep validity and stay per entry separated in wording.'
        visa_data.append({
            'name': name.replace('  ', ' '),
            'desc': detail.get('description', ''),
            'stay_validity': stay_validity,
            'cost': cost,
            'processing': processing,
            'channel': 'On arrival' if detail.get('is_arrival') else 'eVisa / application route',
            'docs': docs,
            'notes': notes,
            'source': 'https://evisa.imigrasi.go.id/web/visa-selection',
        })
    rows = build_rows(visa_data)
    ssid = ensure_workbook()
    tabs = ensure_tab(ssid, TODAY_TAB)
    update_values(ssid, 'Base', rows)
    update_values(ssid, TODAY_TAB, rows)
    format_sheet(ssid, tabs, len(rows))
    sheet_url = f'https://docs.google.com/spreadsheets/d/{ssid}/edit#gid={tabs[TODAY_TAB]}'
    doc_id = create_doc()
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    lines = build_lines(sheet_url)
    update_doc(doc_id, lines)
    summary_text = 'Bản baseline đầu tiên cho Indonesia; đã khóa nhóm B1/C1/D1/C2/D2/B4/C4/D4 từ cổng eVisa official. Chưa có báo cáo trước để phát hiện thay đổi thực chất.'
    update_summary_tracker(doc_url, sheet_url, summary_text)
    print(json.dumps({'summary_link': SUMMARY_LINK, 'doc_url': doc_url, 'sheet_url': sheet_url}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
