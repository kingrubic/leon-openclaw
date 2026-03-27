import json
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from pypdf import PdfReader

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
OAUTH_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.oauth-client.json'
SPREADSHEET_ID = '1K3Z-Wf-KBKbMVhxzLDJDhfNgrriEiB6C9c2BkptAa_I'
SOURCE_URL = 'https://indianvisaonline.gov.in/evisa/tvoa.html'
TODAY_TAB = '27Mar26'
YESTERDAY_TAB = '25Mar26'
YESTERDAY_DOC_ID = '1QSTJBmVOhSTuPIot-AyjnFYKVvbxIg8ke2gWsrVAP7U'
DOC_TITLE = 'India e-Visa daily report - 27 Mar 2026'
RUN_DATE_TEXT = '27 Mar 2026'
EMAIL_TO = 'bob.ng@mobcec.com'


def load_token_data():
    return json.loads(TOKEN_PATH.read_text())


def save_token_data(data):
    TOKEN_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def refresh_access_token():
    token_data = load_token_data()
    oauth = json.loads(OAUTH_PATH.read_text())['web']
    body = urlencode({
        'client_id': oauth['client_id'],
        'client_secret': oauth['client_secret'],
        'refresh_token': token_data['token']['refresh_token'],
        'grant_type': 'refresh_token',
    }).encode('utf-8')
    req = Request(
        oauth['token_uri'],
        data=body,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        method='POST',
    )
    with urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
    token_data['token']['access_token'] = payload['access_token']
    token_data['token']['expires_in'] = payload.get('expires_in', token_data['token'].get('expires_in'))
    save_token_data(token_data)
    return payload['access_token']


def http_json(url, method='GET', data=None, auth=True):
    access_token = refresh_access_token() if auth else None
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    if auth:
        headers['Authorization'] = f'Bearer {access_token}'
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def http_text(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=120) as resp:
        return resp.read().decode('utf-8', 'ignore')


def fetch_pdf_text(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=120) as resp:
        data = resp.read()
    reader = PdfReader(BytesIO(data))
    return '\n'.join(page.extract_text() or '' for page in reader.pages)


def normalize_spaces(text):
    return re.sub(r'\s+', ' ', text).strip()


def parse_pdf_rows(text, expected_numeric_cols):
    lines = [normalize_spaces(line) for line in text.splitlines()]
    rows = []
    buffer = ''

    def try_parse(buf):
        tokens = buf.split()
        if len(tokens) < expected_numeric_cols + 1:
            return None
        tail = tokens[-expected_numeric_cols:]
        if not all(re.fullmatch(r'(?:\d+|-)', t) for t in tail):
            return None
        country = ' '.join(tokens[:-expected_numeric_cols]).strip()
        if not country:
            return None
        return country, tail

    for line in lines:
        if not line:
            continue
        if line.startswith('Country/Territory Wise') or line.startswith('Sl No') or line.startswith('Sl') or line.startswith('Note:'):
            continue
        numeric_only = bool(re.fullmatch(r'(?:\d+|-)\s+(?:\d+|-)\s+(?:\d+|-)\s+(?:\d+|-)(?:\s+(?:\d+|-))?(?:\s+(?:\d+|-))?', line))
        if buffer and numeric_only:
            buffer = f'{buffer} {line}'.strip()
            parsed = try_parse(buffer)
            if parsed:
                rows.append(parsed)
                buffer = ''
            continue
        if re.match(r'^\d+\s+', line):
            if buffer:
                parsed = try_parse(buffer)
                if parsed:
                    rows.append(parsed)
                buffer = ''
            buffer = re.sub(r'^\d+\s+', '', line)
            parsed = try_parse(buffer)
            if parsed:
                rows.append(parsed)
                buffer = ''
        elif buffer:
            buffer = f'{buffer} {line}'.strip()
            parsed = try_parse(buffer)
            if parsed:
                rows.append(parsed)
                buffer = ''
    if buffer:
        parsed = try_parse(buffer)
        if parsed:
            rows.append(parsed)
    return rows


def canonical_country(name):
    name = normalize_spaces(name)
    lower = name.lower()
    alias = {
        'bosnia & herzegovina': 'Bosnia and Herzegovina',
        'cameroon republic': 'Cameroon',
        "cote d'ivoire": 'Ivory Coast',
        'cayman island': 'Cayman Islands',
        'gambia': 'Gambia, The',
        'republic of korea': 'Korea, South',
        'saint christopher and nevis': 'Saint Kitts and Nevis',
        'saint vincent and the grenadines': 'Saint Vincent & the Grenadines',
        'turks and caicos': 'Turks and Caicos Island',
        'vatican city - holy see': 'Vatican City',
        'niger republic': 'Niger',
        'micronesia': 'Micronesia, Federated States of',
        'niue island': 'Niue',
        'papua new guinea': 'Papua New Guinea',
        'east timor': 'East Timor',
        'trinidad and tobago': 'Trinidad and Tobago',
    }
    return alias.get(lower, name)


def build_fee_maps(pdf_links):
    tourist_rows = parse_pdf_rows(fetch_pdf_text(pdf_links['tourist']), 4)
    other_rows = parse_pdf_rows(fetch_pdf_text(pdf_links['other']), 6)
    tourist_map = {}
    for country, vals in tourist_rows:
        tourist_map[canonical_country(country)] = {
            'tourist_30': f'{vals[0]} (Apr-Jun) / {vals[1]} (Jul-Mar)',
            'tourist_1y': vals[2],
            'tourist_5y': vals[3],
        }
    other_map = {}
    for country, vals in other_rows:
        other_map[canonical_country(country)] = {
            'business': vals[0],
            'medical': vals[1],
            'medical_attendant': vals[2],
            'ayush': vals[3],
            'ayush_attendant': vals[4],
            'conference': vals[5],
        }
    return tourist_map, other_map


def extract_visa_details():
    html = http_text(SOURCE_URL)
    soup = BeautifulSoup(html, 'html.parser')
    categories = [a.get_text(' ', strip=True) for a in soup.select('.new-categories li a')]
    details = {}
    for div in soup.find_all('div', class_='visa-detail-t'):
        h2 = div.find('h2')
        if not h2:
            continue
        title = normalize_spaces(h2.get_text(' ', strip=True))
        bullets = []
        for li in div.find_all('li', recursive=True):
            txt = normalize_spaces(li.get_text(' ', strip=True))
            if txt and txt not in bullets:
                bullets.append(txt)
        details[title] = bullets

    docs = {}
    docs_root = soup.find('ul', class_='below-docs-re')
    if docs_root:
        for li in docs_root.find_all('li', recursive=False):
            raw_title = normalize_spaces(str(li.contents[0])) if li.contents else ''
            title = normalize_spaces(re.sub(r'^For\s+', '', BeautifulSoup(raw_title, 'html.parser').get_text(' ', strip=True)))
            sub = li.find('ul')
            docs[title] = [normalize_spaces(x.get_text(' ', strip=True)) for x in sub.find_all('li', recursive=False)] if sub else []

    pdf_links = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = normalize_spaces(a.get_text(' ', strip=True)).lower()
        if 'fee' in href.lower() or 'fee' in text:
            if href.startswith('http'):
                full = href
            elif href.startswith('/'):
                full = 'https://indianvisaonline.gov.in' + href
            else:
                full = 'https://indianvisaonline.gov.in/evisa/' + href.lstrip('./')
            if 'etourist_fee' in href.lower() or 'tourist' in href.lower():
                pdf_links['tourist'] = full
            elif 'revised_fee' in href.lower() or 'etv' in href.lower() or 'business' in text or 'medical' in text:
                pdf_links['other'] = full
    common_notes = [
        'Không có emergency fee / express fee theo advisory trên trang official.',
        'Phí e-Visa phụ thuộc country/territory và cộng thêm bank transaction charge 3%.',
        'Phí đã nộp là non-refundable, không phụ thuộc ETA được grant hay bị từ chối.',
        'e-Visa không extendable, không convertible, không dùng cho Protected/Restricted/Cantonment Areas nếu chưa có phép riêng.',
        'Người nộp phải upload ảnh chân dung nền trắng và trang bio hộ chiếu; tài liệu bổ sung phải bằng tiếng Anh.',
    ]
    processing_notes = [
        'Trang nguồn không công bố một SLA cấp ETA thống nhất cho mọi loại visa.',
        'Official guidance yêu cầu nộp online tối thiểu 4 ngày trước ngày đến đối với e-Tourist và e-Business.',
        'Đối với e-Medical, e-Medical Attendant và e-Conference: nộp tối thiểu 4 ngày trước ngày đến, trong cửa sổ 120 ngày.',
        'Nếu tài liệu/hình ảnh chưa đạt, email yêu cầu re-upload thường được gửi trong vòng 24 giờ sau khi hồ sơ được scrutinized.',
    ]
    return categories, details, docs, common_notes, processing_notes, pdf_links


def get_sheet_meta():
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}')


def get_sheet_id(title):
    meta = get_sheet_meta()
    for s in meta['sheets']:
        if s['properties']['title'] == title:
            return s['properties']['sheetId']
    raise KeyError(title)


def get_sheet_values(sheet_title):
    rng = f'{sheet_title}!A1:J500'
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}')['values']


def duplicate_base_sheet(new_title):
    meta = get_sheet_meta()
    titles = {s['properties']['title'] for s in meta['sheets']}
    if new_title in titles:
        raise RuntimeError(f'Sheet already exists: {new_title}')
    base = next(s for s in meta['sheets'] if s['properties']['title'] == 'Base')
    body = {'requests': [{'duplicateSheet': {'sourceSheetId': base['properties']['sheetId'], 'newSheetName': new_title, 'insertSheetIndex': base['properties']['index'] + 1}}]}
    resp = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data=body)
    return resp['replies'][0]['duplicateSheet']['properties']['sheetId']


def update_sheet_values(sheet_title, values):
    rng = f'{sheet_title}!A1:J{len(values)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}?valueInputOption=RAW'
    body = {'range': rng, 'majorDimension': 'ROWS', 'values': values}
    return http_json(url, method='PUT', data=body)


def clear_extra_rows(sheet_title, start_row):
    rng = f'{sheet_title}!A{start_row}:J500'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}:clear'
    return http_json(url, method='POST', data={})


def batch_update_sheet(requests):
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data={'requests': requests})


def compare_against_base(base_values, tourist_map, other_map):
    header = (base_values[0] + [''] * 10)[:10]
    new_rows = [header]
    changes = []
    changed_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
    col_names = {1: 'Tourist 30 ngày', 2: 'Tourist 1 năm', 3: 'Tourist 5 năm', 4: 'Business', 5: 'Medical', 6: 'Ayush', 7: 'Conference', 8: 'Student', 9: 'Transit'}
    for row in base_values[1:]:
        if not row or not row[0].strip():
            continue
        row = (row + [''] * 10)[:10]
        country = row[0].strip()
        updated = list(row)
        tourist = tourist_map.get(country)
        other = other_map.get(country)
        if tourist:
            updated[1] = tourist['tourist_30']
            updated[2] = tourist['tourist_1y']
            updated[3] = tourist['tourist_5y']
        if other:
            updated[4] = other['business']
            updated[5] = other['medical']
            updated[6] = other['ayush']
            updated[7] = other['conference']
        for idx in range(1, 10):
            if row[idx].strip() != updated[idx].strip():
                changed_counts[idx] += 1
                changes.append({'country': country, 'column': col_names[idx], 'old': row[idx].strip(), 'new': updated[idx].strip()})
        new_rows.append(updated)
    return new_rows, changes, changed_counts


def compare_rows(old_rows, new_rows):
    old_map = {r[0].strip(): (r + [''] * 10)[:10] for r in old_rows[1:] if r and r[0].strip()}
    new_map = {r[0].strip(): (r + [''] * 10)[:10] for r in new_rows[1:] if r and r[0].strip()}
    col_names = {1: 'Tourist 30 ngày', 2: 'Tourist 1 năm', 3: 'Tourist 5 năm', 4: 'Business', 5: 'Medical', 6: 'Ayush', 7: 'Conference', 8: 'Student', 9: 'Transit'}
    diffs = []
    for country in sorted(set(old_map) | set(new_map)):
        o = old_map.get(country, [''] * 10)
        n = new_map.get(country, [''] * 10)
        for idx in range(1, 10):
            if o[idx].strip() != n[idx].strip():
                diffs.append({'country': country, 'column': col_names[idx], 'old': o[idx].strip(), 'new': n[idx].strip()})
    return diffs


def reset_and_bold_changed_cells(sheet_id, new_rows, changes_from_base):
    requests = [{
        'repeatCell': {
            'range': {'sheetId': sheet_id, 'startRowIndex': 1, 'endRowIndex': len(new_rows), 'startColumnIndex': 1, 'endColumnIndex': 10},
            'cell': {'userEnteredFormat': {'textFormat': {'bold': False}}},
            'fields': 'userEnteredFormat.textFormat.bold'
        }
    }]
    col_index = {'Tourist 30 ngày': 1, 'Tourist 1 năm': 2, 'Tourist 5 năm': 3, 'Business': 4, 'Medical': 5, 'Ayush': 6, 'Conference': 7, 'Student': 8, 'Transit': 9}
    country_to_row = {row[0]: idx for idx, row in enumerate(new_rows[1:], start=1) if row and row[0]}
    for item in changes_from_base:
        row_idx = country_to_row[item['country']]
        col_idx = col_index[item['column']]
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sheet_id, 'startRowIndex': row_idx, 'endRowIndex': row_idx + 1, 'startColumnIndex': col_idx, 'endColumnIndex': col_idx + 1},
                'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        })
    batch_update_sheet(requests)


def get_doc_text(doc_id):
    doc = http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')
    parts = []
    for el in doc.get('body', {}).get('content', []):
        para = el.get('paragraph')
        if not para:
            continue
        for pe in para.get('elements', []):
            tr = pe.get('textRun')
            if tr and 'content' in tr:
                parts.append(tr['content'])
    return ''.join(parts)


def create_doc(title):
    return http_json('https://www.googleapis.com/drive/v3/files', method='POST', data={'name': title, 'mimeType': 'application/vnd.google-apps.document'})


def doc_batch_update(doc_id, requests):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def build_change_section(vs_yesterday_changes, pdf_links, yesterday_doc_text, categories, details):
    lines = []
    lines.append('**Kết quả đối chiếu so với hôm qua:**')
    if not vs_yesterday_changes:
        lines.append('- **Không ghi nhận thay đổi giá nào so với tab hôm qua (`25Mar26`) trên các cột phí được official source set công bố rõ.**')
    else:
        lines.append(f'- **Ghi nhận {len(vs_yesterday_changes)} ô giá thay đổi so với tab hôm qua.**')
        for item in vs_yesterday_changes[:15]:
            lines.append(f"- {item['country']}: {item['column']} đổi từ {item['old']} -> {item['new']}")
    if SOURCE_URL in yesterday_doc_text:
        lines.append('- Nguồn chính đối chiếu vẫn là cùng trang official India e-Visa, không có dấu hiệu đổi nguồn gốc báo cáo.')
    if 'Student e-Visa' in yesterday_doc_text and 'Transit eVisa' in yesterday_doc_text:
        lines.append('- **Student e-Visa và Transit eVisa vẫn chưa có fee table được công bố rõ trong cùng bộ nguồn official đang review; nội bộ tiếp tục giữ nguyên giá ở hai cột này.**')
    lines.append(f"- PDF phí đang dùng hôm nay: Tourist = {pdf_links.get('tourist', 'N/A')} ; Other e-Visa = {pdf_links.get('other', 'N/A')}")
    lines.append(f"- Số category e-Visa đọc được từ HTML hôm nay: **{len(categories)}**; chưa thấy dấu hiệu thêm/bớt nhóm sản phẩm so với logic báo cáo hôm qua.")
    return lines


def build_doc_lines(sheet_url, yesterday_sheet_url, categories, details, docs, common_notes, processing_notes, pdf_links, changes_from_base, changed_counts, vs_yesterday_changes, yesterday_doc_text):
    ordered_titles = [
        'e-Tourist Visa', 'e-Business Visa', 'e-Conference Visa', 'e-Medical Visa', 'e-Medical Attendent Visa',
        'e-Ayush Visa', 'e-Ayush Attendent Visa', 'e-Student Visa', 'e-Student Dependent Visa', 'e-Transit Visa',
        'e-Mountaineering Visa', 'e-Film Visa', 'e-Entry Visa', 'e-Production Investment Visa'
    ]
    lines = [
        'INDIA E-VISA DAILY REPORT',
        'Báo cáo đối chiếu hàng ngày từ nguồn official India e-Visa',
        '',
        f'Ngày lập: {RUN_DATE_TEXT}',
        f'Nguồn chính: {SOURCE_URL}',
        f'Tab giá hôm nay: {sheet_url}',
        f'Tab giá hôm qua: {yesterday_sheet_url}',
        '',
        '1. EXECUTIVE SUMMARY',
        '',
        'Mục tiêu: rà soát lại nguồn official India e-Visa, cập nhật tab giá ngày mới theo đúng format nội bộ, và tóm tắt những gì thay đổi so với hôm qua cho cấp quản lý.',
        '',
        'Kết luận nhanh:',
        f'- Đã tạo tab mới **{TODAY_TAB}** bằng cách clone từ **Base** rồi cập nhật theo nguồn official hiện hành.',
        f'- Tổng số ô khác **Base** và được bôi đậm trong tab mới: **{len(changes_from_base)}**.',
        f'- Tổng số ô khác so với tab hôm qua **{YESTERDAY_TAB}**: **{len(vs_yesterday_changes)}**.',
        '- **`00` / `0` trong bảng phí official được hiểu là official fee currently shows zero, không tự động suy ra visa-free entry.**',
        '- **Student e-Visa và Transit eVisa vẫn không có fee table được công bố rõ trong cùng bộ nguồn official đang review; nội bộ giữ nguyên giá ở 2 cột này.**',
        '',
        '2. THAY ĐỔI SO VỚI HÔM QUA',
        '',
    ]
    lines.extend(build_change_section(vs_yesterday_changes, pdf_links, yesterday_doc_text, categories, details))
    lines.extend(['', '3. TÓM TẮT THAY ĐỔI SO VỚI BASE / ĐẦU VÀO NỘI BỘ', ''])
    nonzero = [f"- {name}: **{count}** dòng thay đổi" for name, count in [('Tourist 30 ngày', changed_counts[1]), ('Tourist 1 năm', changed_counts[2]), ('Tourist 5 năm', changed_counts[3]), ('Business', changed_counts[4]), ('Medical', changed_counts[5]), ('Ayush', changed_counts[6]), ('Conference', changed_counts[7]), ('Student', changed_counts[8]), ('Transit', changed_counts[9])] if count]
    lines.extend(nonzero or ['- Không phát hiện thay đổi nào so với Base.'])
    lines.extend(['', '4. CÁC LOẠI E-VISA OFFICIAL ĐANG HIỂN THỊ', ''])
    lines.extend([f'- {c}' for c in categories])
    lines.extend(['', '5. THÔNG TIN CHI TIẾT THEO TỪNG LOẠI VISA', ''])
    for title in ordered_titles:
        lines.append(title)
        lines.append('Thông tin chính:')
        for b in details.get(title, []):
            lines.append(f'- {b}')
        lines.append('Hồ sơ cần thiết:')
        docs_key = 'e-Medical Attendant Visa' if title == 'e-Medical Attendent Visa' else 'e-Ayush Attendant Visa' if title == 'e-Ayush Attendent Visa' else title
        visa_docs = docs.get(docs_key, [])
        if visa_docs:
            lines.extend([f'- {d}' for d in visa_docs])
        else:
            lines.append('- Chưa thấy block hồ sơ riêng trên trang; tối thiểu vẫn cần ảnh chân dung và trang bio hộ chiếu theo hướng dẫn chung.')
        lines.append('')
    lines.extend(['6. LƯU Ý QUAN TRỌNG', ''])
    lines.extend([f'- {x}' for x in common_notes])
    lines.extend([
        '- Applicant cần kiểm tra ETA ở trạng thái **GRANTED** trước khi khởi hành.',
        '- Nếu dùng hộ chiếu mới nhưng ETA cấp trên hộ chiếu cũ, phải mang theo cả hai hộ chiếu trong trường hợp áp dụng.',
        '',
        '7. THỜI GIAN XỬ LÝ / PROCESSING GUIDANCE',
        ''
    ])
    lines.extend([f'- {x}' for x in processing_notes])
    lines.extend([
        '',
        '8. GHI CHÚ RIÊNG VỀ BẢNG PHÍ',
        '',
        f'- PDF phí tourist đang dùng: {pdf_links.get("tourist", "N/A")}',
        f'- PDF phí other e-Visa đang dùng: {pdf_links.get("other", "N/A")}',
        '- Nhóm official fee hiện được đối chiếu rõ: e-Tourist, e-Business, e-Medical, e-Medical Attendant, e-Ayush, e-Ayush Attendant, e-Conference.',
        '- **Student e-Visa và Transit eVisa chưa được official source set hiện tại công bố fee table đủ rõ để update an toàn; giá nội bộ được giữ nguyên.**',
        '',
        '9. KẾT LUẬN',
        '',
        '- Hôm nay trọng tâm là xác minh thay đổi so với hôm qua; kết quả là không nên thổi phồng nếu official source chưa đổi rõ.',
        '- Khi cần xem chi tiết theo từng quốc tịch, ưu tiên mở tab sheet đính kèm thay vì đọc report như bảng giá đầy đủ.',
    ])
    return lines


def apply_doc_format(doc_id, lines):
    text = '\n'.join(lines)
    requests = [{'insertText': {'location': {'index': 1}, 'text': text}}]
    starts = []
    idx = 1
    for line in lines:
        starts.append(idx)
        idx += len(line) + 1
    for i, line in enumerate(lines):
        start = starts[i]
        end = start + len(line)
        if i == 0:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'TITLE', 'alignment': 'CENTER'}, 'fields': 'namedStyleType,alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
        elif i == 1:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'alignment': 'CENTER'}, 'fields': 'alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})
        elif re.fullmatch(r'\d+\. .*', line) or re.fullmatch(r'[A-Z0-9 .\-()]+', line):
            # format numbered all-caps section headings strongly
            if line and (re.fullmatch(r'\d+\. .*', line) or (line.isupper() and len(line) < 80)):
                requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}})
                requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        if '**' in line:
            # remove markdown markers by bolding enclosed ranges later is cumbersome; leave plain text markers absent by preprocessing elsewhere
            pass
    doc_batch_update(doc_id, requests)


def strip_bold_markers(lines):
    clean = []
    spans = []
    for line in lines:
        out = ''
        i = 0
        line_spans = []
        while i < len(line):
            if line.startswith('**', i):
                j = line.find('**', i + 2)
                if j != -1:
                    start = len(out)
                    out += line[i + 2:j]
                    end = len(out)
                    line_spans.append((start, end))
                    i = j + 2
                    continue
            out += line[i]
            i += 1
        clean.append(out)
        spans.append(line_spans)
    return clean, spans


def apply_bold_spans(doc_id, clean_lines, spans):
    requests = []
    starts = []
    idx = 1
    for line in clean_lines:
        starts.append(idx)
        idx += len(line) + 1
    for i, line_spans in enumerate(spans):
        for s, e in line_spans:
            requests.append({'updateTextStyle': {'range': {'startIndex': starts[i] + s, 'endIndex': starts[i] + e}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
    if requests:
        doc_batch_update(doc_id, requests)


def main():
    base_values = get_sheet_values('Base')
    yesterday_values = get_sheet_values(YESTERDAY_TAB)
    yesterday_sheet_id = get_sheet_id(YESTERDAY_TAB)
    yesterday_sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={yesterday_sheet_id}'
    yesterday_doc_text = get_doc_text(YESTERDAY_DOC_ID)

    categories, details, docs, common_notes, processing_notes, pdf_links = extract_visa_details()
    if 'tourist' not in pdf_links or 'other' not in pdf_links:
        raise RuntimeError(f'Could not find required fee PDFs on source page: {pdf_links}')
    tourist_map, other_map = build_fee_maps(pdf_links)
    new_rows, changes_from_base, changed_counts = compare_against_base(base_values, tourist_map, other_map)
    vs_yesterday_changes = compare_rows(yesterday_values, new_rows)

    new_sheet_id = duplicate_base_sheet(TODAY_TAB)
    update_sheet_values(TODAY_TAB, new_rows)
    clear_extra_rows(TODAY_TAB, len(new_rows) + 1)
    reset_and_bold_changed_cells(new_sheet_id, new_rows, changes_from_base)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={new_sheet_id}'

    doc = create_doc(DOC_TITLE)
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    lines = build_doc_lines(sheet_url, yesterday_sheet_url, categories, details, docs, common_notes, processing_notes, pdf_links, changes_from_base, changed_counts, vs_yesterday_changes, yesterday_doc_text)
    clean_lines, spans = strip_bold_markers(lines)
    apply_doc_format(doc_id, clean_lines)
    apply_bold_spans(doc_id, clean_lines, spans)

    email_subject = f'India e-Visa daily report sync - {RUN_DATE_TEXT}'
    if not vs_yesterday_changes:
        email_summary = 'Hôm nay không ghi nhận thay đổi giá nào so với tab hôm qua trên các cột phí được nguồn official công bố rõ. Student e-Visa và Transit eVisa vẫn chưa có fee table được công bố rõ trong cùng bộ nguồn official nên tiếp tục giữ nguyên giá nội bộ.'
    else:
        first = vs_yesterday_changes[:5]
        bits = '; '.join([f"{x['country']} - {x['column']}: {x['old']} -> {x['new']}" for x in first])
        email_summary = f'Hôm nay ghi nhận {len(vs_yesterday_changes)} ô thay đổi so với hôm qua: {bits}. Student e-Visa và Transit eVisa vẫn chưa có fee table được công bố rõ trong cùng bộ nguồn official nên tiếp tục giữ nguyên giá nội bộ.'

    print(json.dumps({
        'doc_url': doc_url,
        'sheet_url': sheet_url,
        'sheet_tab': TODAY_TAB,
        'vs_yesterday_changes_count': len(vs_yesterday_changes),
        'vs_yesterday_changes_sample': vs_yesterday_changes[:15],
        'changes_from_base_count': len(changes_from_base),
        'changed_counts_from_base': changed_counts,
        'pdf_links': pdf_links,
        'email_to': EMAIL_TO,
        'email_subject': email_subject,
        'email_summary_vi': email_summary,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
