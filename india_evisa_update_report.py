import json
import re
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from pypdf import PdfReader

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
SPREADSHEET_ID = '1K3Z-Wf-KBKbMVhxzLDJDhfNgrriEiB6C9c2BkptAa_I'
NEW_SHEET_TITLE = '25Mar26'
SOURCE_URL = 'https://indianvisaonline.gov.in/evisa/tvoa.html'
TOURIST_PDF = 'https://indianvisaonline.gov.in/evisa/images/Etourist_fee_final.pdf'
OTHER_PDF = 'https://indianvisaonline.gov.in/evisa/images/eTV_revised_fee_final.pdf'


def load_token():
    return json.loads(TOKEN_PATH.read_text())['token']['access_token']


def http_json(url, method='GET', data=None):
    token = load_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json; charset=utf-8',
    }
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        text = resp.read().decode('utf-8')
        return json.loads(text) if text else {}


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
    if lower in alias:
        return alias[lower]
    return name


def build_fee_maps():
    tourist_rows = parse_pdf_rows(fetch_pdf_text(TOURIST_PDF), 4)
    other_rows = parse_pdf_rows(fetch_pdf_text(OTHER_PDF), 6)

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


def get_sheet_values(sheet_title='Base'):
    rng = f'{sheet_title}!A1:Z500'
    from urllib.parse import quote
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}'
    return http_json(url)['values']


def get_sheet_meta():
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}')


def ensure_unique_sheet_title(title):
    meta = get_sheet_meta()
    existing = {s['properties']['title'] for s in meta['sheets']}
    if title not in existing:
        return title
    i = 2
    while f'{title}_{i}' in existing:
        i += 1
    return f'{title}_{i}'


def duplicate_base_sheet(new_title):
    meta = get_sheet_meta()
    base = next(s for s in meta['sheets'] if s['properties']['title'] == 'Base')
    body = {
        'requests': [
            {
                'duplicateSheet': {
                    'sourceSheetId': base['properties']['sheetId'],
                    'newSheetName': new_title,
                    'insertSheetIndex': base['properties']['index'] + 1,
                }
            }
        ]
    }
    resp = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data=body)
    return resp['replies'][0]['duplicateSheet']['properties']['sheetId']


def update_sheet_values(sheet_title, values):
    from urllib.parse import quote
    rng = f'{sheet_title}!A1:J{len(values)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}?valueInputOption=RAW'
    body = {'range': rng, 'majorDimension': 'ROWS', 'values': values}
    return http_json(url, method='PUT', data=body)


def clear_extra_rows(sheet_title, start_row):
    from urllib.parse import quote
    rng = f'{sheet_title}!A{start_row}:J500'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote(rng)}:clear'
    return http_json(url, method='POST', data={})


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
    for li in docs_root.find_all('li', recursive=False):
        raw_title = normalize_spaces(str(li.contents[0])) if li.contents else ''
        title = normalize_spaces(re.sub(r'^For\s+', '', BeautifulSoup(raw_title, 'html.parser').get_text(' ', strip=True)))
        sub = li.find('ul')
        docs[title] = [normalize_spaces(x.get_text(' ', strip=True)) for x in sub.find_all('li', recursive=False)] if sub else []

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

    return categories, details, docs, common_notes, processing_notes


def compare_and_build_rows(base_values, tourist_map, other_map):
    header = base_values[0][:10]
    new_rows = [header]
    changes = []
    missing_official_fee = []
    column_names = {
        1: 'Tourist 30 ngày',
        2: 'Tourist 1 năm',
        3: 'Tourist 5 năm',
        4: 'Business',
        5: 'Medical',
        6: 'Ayush',
        7: 'Conference',
        8: 'Student',
        9: 'Transit',
    }
    changed_counts = {column_names[k]: 0 for k in column_names}

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
        else:
            missing_official_fee.append((country, 'tourist'))

        if other:
            updated[4] = other['business']
            updated[5] = other['medical']
            updated[6] = other['ayush']
            updated[7] = other['conference']
        else:
            missing_official_fee.append((country, 'other'))

        # student & transit kept from Base because current source page + linked fee PDFs do not clearly publish those fee tables.

        for idx in range(1, 10):
            old = row[idx].strip()
            new = updated[idx].strip()
            if old != new:
                changed_counts[column_names[idx]] += 1
                changes.append({'country': country, 'column': column_names[idx], 'old': old, 'new': new})

        new_rows.append(updated)

    return new_rows, changes, changed_counts, missing_official_fee


def make_change_summary(changes, limit=15):
    lines = []
    for item in changes[:limit]:
        lines.append(f"- {item['country']}: {item['column']} đổi từ {item['old']} -> {item['new']}")
    return lines


def create_doc(title):
    data = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    return http_json('https://www.googleapis.com/drive/v3/files', method='POST', data=data)


def write_doc(doc_id, text):
    body = {
        'requests': [
            {'insertText': {'location': {'index': 1}, 'text': text}}
        ]
    }
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data=body)


def main():
    base_values = get_sheet_values('Base')
    tourist_map, other_map = build_fee_maps()
    categories, details, docs, common_notes, processing_notes = extract_visa_details()
    new_rows, changes, changed_counts, missing_fee = compare_and_build_rows(base_values, tourist_map, other_map)

    sheet_title = ensure_unique_sheet_title(NEW_SHEET_TITLE)
    sheet_id = duplicate_base_sheet(sheet_title)
    update_sheet_values(sheet_title, new_rows)
    clear_extra_rows(sheet_title, len(new_rows) + 1)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={sheet_id}'

    doc_title = 'India e-Visa report - 26 Mar 2026'
    doc = create_doc(doc_title)
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'

    changed_columns_text = '\n'.join([f"- {k}: {v} dòng thay đổi" for k, v in changed_counts.items() if v]) or '- Không phát hiện thay đổi.'
    sample_changes_text = '\n'.join(make_change_summary(changes, 20)) or '- Không phát hiện thay đổi.'

    categories_text = '\n'.join([f'- {c}' for c in categories])

    detail_sections = []
    ordered_titles = [
        'e-Tourist Visa', 'e-Business Visa', 'e-Conference Visa', 'e-Medical Visa', 'e-Medical Attendent Visa',
        'e-Ayush Visa', 'e-Ayush Attendent Visa', 'e-Student Visa', 'e-Student Dependent Visa', 'e-Transit Visa',
        'e-Mountaineering Visa', 'e-Film Visa', 'e-Entry Visa', 'e-Production Investment Visa'
    ]
    for title in ordered_titles:
        bullets = details.get(title, [])
        doc_key = title.replace('e-', 'e-')
        docs_key = title
        if title == 'e-Medical Attendent Visa':
            docs_key = 'e-Medical Attendant Visa'
        elif title == 'e-Ayush Attendent Visa':
            docs_key = 'e-Ayush Attendant Visa'
        visa_docs = docs.get(docs_key, [])
        section = [title]
        section.append('Thông tin chính:')
        for b in bullets:
            section.append(f'- {b}')
        section.append('Hồ sơ cần thiết:')
        if visa_docs:
            for d in visa_docs:
                section.append(f'- {d}')
        else:
            section.append('- Chưa thấy mục hồ sơ riêng trong block tài liệu của trang này; tối thiểu vẫn cần ảnh và trang bio hộ chiếu theo hướng dẫn chung.')
        detail_sections.append('\n'.join(section))

    notes_text = '\n'.join([f'- {x}' for x in common_notes])
    processing_text = '\n'.join([f'- {x}' for x in processing_notes])

    report = f"India e-Visa report\nNgày lập: 26 Mar 2026\nNguồn chính: {SOURCE_URL}\n\n1) Các loại visa chính phủ đang cung cấp\n{categories_text}\n\n2) Giá chi tiết\n- Em đã tạo sheet đối chiếu / update tại: {sheet_url}\n- Em duplicate từ tab Base sang tab {sheet_title} rồi cập nhật lại theo bảng phí official hiện hành.\n- Lưu ý quan trọng: phí official là country/territory-specific; phí 30-day e-Tourist hiện tách theo mùa Apr-Jun và Jul-Mar.\n- Bank transaction charge 3% được official note là cộng thêm trên phí e-Visa áp dụng.\n\nTóm tắt thay đổi trước khi mở sheet chi tiết:\n{changed_columns_text}\n\nVí dụ các thay đổi tiêu biểu:\n{sample_changes_text}\n\n3) Hồ sơ cần thiết, lưu ý và hiệu lực theo từng loại visa\n\n" + "\n\n".join(detail_sections) + f"\n\n4) Lưu ý chung khi xin visa\n{notes_text}\n\n5) Thời gian trả visa dự kiến\n{processing_text}\n\n6) Ghi chú riêng về bảng giá\n- Hai tài liệu phí official được link trực tiếp từ trang e-Visa hiện mới thể hiện rõ phí cho e-Tourist, e-Business, e-Medical, e-Medical Attendant, e-Ayush, e-Ayush Attendant và e-Conference.\n- Riêng cột Student e-Visa và Transit eVisa trong file Base không thấy bảng phí tương ứng được công bố rõ trong chính nguồn official vừa đối chiếu, nên em giữ nguyên giá ở hai cột này trong tab {sheet_title} chờ xác minh thêm nếu anh muốn em đào sâu tiếp.\n- Nếu cần, em có thể làm thêm vòng 2 để truy tiếp nguồn official cho Student / Transit hoặc chuẩn hóa lại cả workbook theo format mới.\n\nLink tài liệu này: {doc_url}\n"

    write_doc(doc_id, report)

    print(json.dumps({
        'doc_url': doc_url,
        'sheet_url': sheet_url,
        'sheet_title': sheet_title,
        'sheet_id': sheet_id,
        'changes_count': len(changes),
        'changed_counts': changed_counts,
        'sample_changes': changes[:10],
        'missing_fee_samples': missing_fee[:10],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
