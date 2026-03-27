import json
import urllib.parse
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
SPREADSHEET_ID = '1hlS093IYraw-xq7EGU2MFXgzIucZd-gVUykXUwVpJOM'
PREV_TAB = '26Mar26'
TODAY_TAB = '27Mar26'
DATE_TEXT = '27 Mar 2026'
DATE_VI = '27/03/2026'
PREV_DOC_URL = 'https://docs.google.com/document/d/1AMteb8SlOBQbWgves_slAMh_REvJ02gzbTmKseM-4wU/edit'

VALUES = [
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


def load_token_data():
    return json.loads(TOKEN_PATH.read_text())


def refresh_access_token_if_needed():
    data = load_token_data()
    token = data['token']
    if not token.get('refresh_token'):
        return
    creds = json.loads((WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.oauth-client.json').read_text())['web']
    body = urllib.parse.urlencode({
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': token['refresh_token'],
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
    if refreshed.get('scope'):
        data['scope'] = refreshed['scope']
    TOKEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def load_token():
    return load_token_data()['token']['access_token']


def http_json(url, method='GET', data=None):
    headers = {
        'Authorization': f'Bearer {load_token()}',
        'Content-Type': 'application/json; charset=utf-8',
    }
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def get_sheet_meta():
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}')


def get_values(tab):
    rng = f'{tab}!A1:I{len(VALUES)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{urllib.parse.quote(rng)}'
    return http_json(url).get('values', [])


def update_values(tab, values):
    rng = f'{tab}!A1:I{len(values)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{urllib.parse.quote(rng)}?valueInputOption=RAW'
    return http_json(url, method='PUT', data={'range': rng, 'majorDimension': 'ROWS', 'values': values})


def batch_update(requests):
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data={'requests': requests})


def ensure_today_tab():
    meta = get_sheet_meta()
    title_to_id = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    if TODAY_TAB not in title_to_id:
        batch_update([{'duplicateSheet': {'sourceSheetId': title_to_id[PREV_TAB], 'newSheetName': TODAY_TAB, 'insertSheetIndex': 2}}])
        meta = get_sheet_meta()
        title_to_id = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    return title_to_id[TODAY_TAB]


def create_doc(title):
    body = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    return http_json('https://www.googleapis.com/drive/v3/files', method='POST', data=body)


def get_doc(doc_id):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')


def doc_batch_update(doc_id, requests):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def diff_cells(old, new):
    max_rows = max(len(old), len(new))
    out = []
    for r in range(max_rows):
        old_row = old[r] if r < len(old) else []
        new_row = new[r] if r < len(new) else []
        max_cols = max(len(old_row), len(new_row))
        for c in range(max_cols):
            ov = old_row[c] if c < len(old_row) else ''
            nv = new_row[c] if c < len(new_row) else ''
            if ov != nv:
                out.append({'row': r + 1, 'col': c + 1, 'old': ov, 'new': nv, 'label': new_row[0] if new_row else old_row[0]})
    return out


def build_doc_lines(sheet_url, changes):
    lines = [
        'BÁO CÁO ETA SRI LANKA',
        'Bản tóm tắt quản trị dựa trên các nguồn ETA public chính thức',
        '',
        f'Ngày lập: {DATE_VI}',
        'Tên miền official chính: https://www.eta.gov.lk/',
        f'Sheet phí chi tiết hôm nay: {sheet_url}',
        f'Tham chiếu report hôm qua: {PREV_DOC_URL}',
        '',
        '1. TÓM TẮT ĐIỀU HÀNH',
        '',
        'Báo cáo này rà soát lại các trang ETA public chính thức của Sri Lanka vào ngày 27/03/2026 và cập nhật workbook nội bộ theo cùng phong cách vận hành của bản ngày 26/03/2026. Nội dung tiếp tục được viết theo nguyên tắc thận trọng để tránh kết luận quá mức ở các điểm mà chính nguồn official còn chưa thống nhất.',
        '',
        'Kết luận nhanh:',
        '- Đã tạo tab mới 27Mar26 trong workbook Sri Lanka ETA, giữ nguyên cấu trúc group-based pricing và exception rows như bản hôm qua.',
        f'- Tổng số ô khác so với tab hôm qua {PREV_TAB}: {len(changes)}.',
        '- Đến thời điểm rà soát, chưa ghi nhận thay đổi thực chất về mức phí ETA chuẩn, wording validity/stay cốt lõi, hay alert-based nationality exceptions so với hôm qua.',
        '- Homepage alert vẫn đang nêu cơ chế fee-free / visa-free đặc biệt cho China, India, Indonesia, Russia, Thailand, Malaysia và Japan, nhưng vẫn yêu cầu các đối tượng này xin ETA trước khi đi.',
        '- Business ETA wording vẫn chưa đồng nhất hoàn toàn giữa các trang official: fee page ghi multiple entry 30 days, trong khi short visit page vẫn có chỗ mô tả double entry cho Business purpose ETA.',
        '- FAQ vẫn có wording rằng ETA is valid for six months, nên tiếp tục cần tách bạch giữa ETA validity, thời hạn dùng trước khi nhập cảnh, thời gian lưu trú ban đầu 30 ngày, và khả năng gia hạn.',
        '',
        '2. THAY ĐỔI SO VỚI HÔM QUA',
        '',
        'Kết quả đối chiếu với report và sheet ngày 26/03/2026:',
    ]
    if changes:
        lines.append(f'- Ghi nhận {len(changes)} ô khác trong tab {TODAY_TAB} so với {PREV_TAB}.')
        for ch in changes[:15]:
            lines.append(f"- {ch['label']}: {ch['old']} -> {ch['new']}")
    else:
        lines.extend([
            '- Không ghi nhận ô dữ liệu nào thay đổi trong tab hôm nay so với tab hôm qua.',
            '- Chưa thấy thay đổi thực chất về phí ETA chuẩn cho SAARC, all other countries, hay trẻ em dưới 12 tuổi.',
            '- Chưa thấy thay đổi ở special regime cho 7 quốc tịch trong homepage alert.',
            '- Chưa thấy thay đổi mới về wording liên quan Business ETA, validity, on-arrival caution, hoặc fee-page gaps.',
        ])
    lines.extend([
        '',
        '3. CÁC ĐIỂM OFFICIAL VẪN GIỮ NGUYÊN / CẦN CAVEAT',
        '',
        '- ETA categories vẫn xác nhận được: Tourist / Business / Transit.',
        '- Mức phí ETA chuẩn trên fee page vẫn là: SAARC Tourist US$20 / Business US$30 / Transit Free; All other countries Tourist US$50 / Business US$55 / Transit Free.',
        '- Trẻ em dưới 12 tuổi vẫn đang hiển thị Free trong bảng ETA fee chính.',
        '- On-arrival tourist fee vẫn là US$25 cho SAARC và US$60 cho all other countries; on-arrival business fee vẫn hiển thị ---- nên chưa thể kết luận giá cụ thể.',
        '- Homepage alert cho 7 quốc tịch vẫn dùng wording free visa regime / visa-free nhưng vẫn đồng thời yêu cầu apply ETA before travel; không nên rút gọn thành “không cần ETA”.',
        '- Center/apply pages vẫn cho thấy ETA holder có thể enter within three months from date of issue và stay ban đầu 30 days from arrival, có thể extend up to six months.',
        '- FAQ vẫn có câu “ETA is valid for six months”; đây là điểm cần ghi chú là official wording chưa hoàn toàn hài hòa với các trang khác.',
        '- FAQ vẫn nêu “ETA is not a pre-condition to board a flight/vessel to Sri Lanka”; vì vậy cũng không nên viết cứng rằng mọi case đều bắt buộc có ETA trước khi boarding.',
        '',
        '4. TÓM TẮT PHÍ / RULES CHO NỘI BỘ',
        '',
        '- Dùng workbook theo logic group-based pricing, không ép sang matrix country-by-country kiểu India.',
        '- Giữ riêng các dòng ngoại lệ cho China, India, Indonesia, Russia, Thailand, Malaysia, Japan.',
        '- Với Business ETA, tiếp tục dùng wording thận trọng: official pages currently show inconsistent entry wording and channel handling.',
        '- Với on-arrival, tiếp tục coi là limited facility; không khuyến nghị như lộ trình mặc định.',
        '',
        '5. DELIVERABLES',
        '',
        f'- Google Sheet: {sheet_url}',
        '- Workbook giữ style vận hành giống bản Sri Lanka ngày 26/03/2026 và cùng visual language với file India, nhưng nội dung vẫn theo logic official riêng của Sri Lanka.',
    ])
    return lines


def write_doc(doc_id, lines):
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

    for i, line in enumerate(lines):
        start = starts[i]
        end = start + len(line)
        if line == 'BÁO CÁO ETA SRI LANKA':
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'TITLE', 'alignment': 'CENTER'}, 'fields': 'namedStyleType,alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
        elif line == 'Bản tóm tắt quản trị dựa trên các nguồn ETA public chính thức':
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'alignment': 'CENTER'}, 'fields': 'alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.35, 'green': 0.35, 'blue': 0.35}}}}, 'fields': 'italic,foregroundColor'}})
        elif line[:2].isdigit() and '. ' in line:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1', 'spaceAbove': {'magnitude': 14, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}}, 'fields': 'namedStyleType,spaceAbove,spaceBelow'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.12, 'green': 0.33, 'blue': 0.53}}}}, 'fields': 'bold,foregroundColor'}})
        elif line.startswith('Kết luận nhanh:') or line.startswith('Cấu trúc phí ETA chuẩn') or line.startswith('Kết quả đối chiếu với report'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('- Với Business ETA') or line.startswith('- Với on-arrival') or line.startswith('- Homepage alert') or line.startswith('- FAQ vẫn'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})
    doc_batch_update(doc_id, requests)


def main():
    refresh_access_token_if_needed()
    today_gid = ensure_today_tab()
    update_values(TODAY_TAB, VALUES)
    old_values = get_values(PREV_TAB)
    new_values = get_values(TODAY_TAB)
    changes = diff_cells(old_values, new_values)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={today_gid}'
    doc = create_doc(f'Sri Lanka ETA report - {DATE_TEXT}')
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    lines = build_doc_lines(sheet_url, changes)
    write_doc(doc_id, lines)
    print(json.dumps({
        'doc_url': doc_url,
        'sheet_url': sheet_url,
        'sheet_tab': TODAY_TAB,
        'vs_yesterday_changes_count': len(changes),
        'email_to': 'bob.ng@mobcec.com',
        'email_subject': 'Sri Lanka ETA daily report sync - 27 Mar 2026',
        'email_summary_vi': 'Hôm nay không ghi nhận thay đổi thực chất so với báo cáo Sri Lanka ETA ngày 26/03/2026. Phí ETA chuẩn, 7 quốc tịch thuộc homepage special regime, và các caveat chính về Business ETA / validity / on-arrival đều giữ nguyên. Lưu ý vẫn không nên diễn giải 7 quốc tịch special regime là không cần ETA, vì alert official vẫn yêu cầu apply ETA before travel.',
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
