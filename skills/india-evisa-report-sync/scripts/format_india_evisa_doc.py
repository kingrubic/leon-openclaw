import json
from pathlib import Path
import importlib.util
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
DOC_ID = '1QSTJBmVOhSTuPIot-AyjnFYKVvbxIg8ke2gWsrVAP7U'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1K3Z-Wf-KBKbMVhxzLDJDhfNgrriEiB6C9c2BkptAa_I/edit#gid=731861942'
SOURCE_URL = 'https://indianvisaonline.gov.in/evisa/tvoa.html'


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
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def get_doc_end_index(doc_id):
    doc = http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')
    return doc['body']['content'][-1]['endIndex']


def main():
    spec = importlib.util.spec_from_file_location('m', '/Users/admin/.openclaw/workspace/india_evisa_update_report.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    base_values = m.get_sheet_values('Base')
    tourist_map, other_map = m.build_fee_maps()
    categories, details, docs, common_notes, processing_notes = m.extract_visa_details()
    new_rows, changes, changed_counts, missing_fee = m.compare_and_build_rows(base_values, tourist_map, other_map)

    ordered_titles = [
        'e-Tourist Visa', 'e-Business Visa', 'e-Conference Visa', 'e-Medical Visa', 'e-Medical Attendent Visa',
        'e-Ayush Visa', 'e-Ayush Attendent Visa', 'e-Student Visa', 'e-Student Dependent Visa', 'e-Transit Visa',
        'e-Mountaineering Visa', 'e-Film Visa', 'e-Entry Visa', 'e-Production Investment Visa'
    ]

    lines = []
    heading1_lines = []
    heading2_lines = []
    bold_prefixes = []
    italic_phrases = []

    def add(line=''):
        lines.append(line)

    def add_h1(text):
        heading1_lines.append(len(lines))
        lines.append(text)

    def add_h2(text):
        heading2_lines.append(len(lines))
        lines.append(text)

    add_h1('INDIA E-VISA REPORT')
    add('Báo cáo đối chiếu thông tin e-Visa official của Ấn Độ')
    add('')
    add('Ngày lập: 26 Mar 2026')
    add(f'Nguồn chính: {SOURCE_URL}')
    add(f'Bảng giá chi tiết đã cập nhật: {SHEET_URL}')
    add('')

    add_h2('1. EXECUTIVE SUMMARY')
    add('')
    add('Mục tiêu: rà soát thông tin e-Visa của Ấn Độ trên nguồn official, đối chiếu với bảng giá hiện có, và cập nhật lại sheet để phục vụ theo dõi nội bộ.')
    add('')
    add('Kết quả chính:')
    add(f'- Đã tạo tab mới tên 25Mar26 trong file sheet để lưu bảng giá update.')
    add(f'- Đã phát hiện thay đổi ở 7 nhóm phí chính: Tourist 30 ngày, Tourist 1 năm, Tourist 5 năm, Business, Medical, Ayush, Conference.')
    add(f'- Tổng số ô giá thay đổi so với tab Base: {len(changes)}.')
    add('- Hai cột Student e-Visa và Transit eVisa hiện chưa thấy bảng phí tương ứng được công bố rõ trong chính bộ nguồn official đang link từ trang e-Visa, nên tạm thời vẫn giữ nguyên theo tab Base.')
    add('- Phí official là country/territory-specific và bank transaction charge 3% được tính thêm trên mức phí áp dụng.')
    add('')
    add('Tóm tắt số dòng thay đổi theo từng nhóm giá:')
    for k, v in changed_counts.items():
        if v:
            add(f'- {k}: {v} dòng thay đổi')
    add('')
    add('Ví dụ thay đổi tiêu biểu:')
    for item in changes[:12]:
        add(f"- {item['country']}: {item['column']} đổi từ {item['old']} -> {item['new']}")
    add('')

    add_h2('2. CÁC LOẠI E-VISA CHÍNH PHỦ ẤN ĐỘ ĐANG CUNG CẤP')
    add('')
    for c in categories:
        add(f'- {c}')
    add('')

    add_h2('3. GIÁ CHI TIẾT VÀ CÁCH ĐỌC BẢNG GIÁ')
    add('')
    add('Điểm cần lưu ý trước khi mở bảng giá chi tiết:')
    add('- Giá không cố định chung cho tất cả quốc tịch; mức phí phụ thuộc vào country/territory của người nộp hồ sơ.')
    add('- Đối với e-Tourist 30 ngày, nguồn official hiện tách thành 2 mức theo mùa: Apr-Jun và Jul-Mar.')
    add('- Official note nêu rõ bank transaction charge 3% được cộng thêm trên phí e-Visa áp dụng.')
    add('- Phí đã nộp là non-refundable và không phụ thuộc việc ETA được grant hay bị từ chối.')
    add('')
    add(f'Link bảng giá chi tiết: {SHEET_URL}')
    add('')

    add_h2('4. THÔNG TIN CHI TIẾT THEO TỪNG LOẠI VISA')
    add('')

    for title in ordered_titles:
        add_h2(title)
        add('')
        add('Thông tin chính:')
        for b in details.get(title, []):
            add(f'- {b}')
        add('')
        add('Hồ sơ cần thiết:')
        docs_key = title
        if title == 'e-Medical Attendent Visa':
            docs_key = 'e-Medical Attendant Visa'
        elif title == 'e-Ayush Attendent Visa':
            docs_key = 'e-Ayush Attendant Visa'
        visa_docs = docs.get(docs_key, [])
        if visa_docs:
            for d in visa_docs:
                add(f'- {d}')
        else:
            add('- Chưa thấy mục hồ sơ riêng trong block tài liệu của trang này; tối thiểu vẫn cần ảnh chân dung và trang bio hộ chiếu theo hướng dẫn chung.')
        add('')

    add_h2('5. LƯU Ý QUAN TRỌNG KHI NỘP HỒ SƠ')
    add('')
    for note in common_notes:
        add(f'- {note}')
    add('- Applicant phải mang theo bản copy ETA khi đi lại và cần kiểm tra trạng thái ETA là GRANTED trước khi khởi hành.')
    add('- e-Visa không áp dụng cho việc vào Protected / Restricted / Cantonment Areas nếu chưa có phép riêng.')
    add('- Nếu dùng hộ chiếu mới nhưng ETA cấp trên hộ chiếu cũ, người đi phải mang theo cả hộ chiếu cũ lẫn hộ chiếu mới trong trường hợp áp dụng.')
    add('')

    add_h2('6. THỜI GIAN XỬ LÝ / TRẢ VISA DỰ KIẾN')
    add('')
    for item in processing_notes:
        add(f'- {item}')
    add('- Nói cách khác, nguồn official hiện thiên về mốc nộp hồ sơ tối thiểu hơn là cam kết một SLA cấp ETA cố định cho mọi loại visa.')
    add('')

    add_h2('7. KẾT LUẬN VÀ KIẾN NGHỊ')
    add('')
    add('- Về mặt cấu trúc visa và điều kiện hồ sơ, trang official hiện khá rõ và đủ để dùng làm nguồn tham chiếu chính.')
    add('- Về mặt giá, phần update lần này đã xử lý chắc tay cho các nhóm phí đã có bảng official đi kèm.')
    add('- Riêng Student e-Visa và Transit eVisa, nếu cần chốt tuyệt đối cho báo cáo cuối cùng, nên làm thêm một vòng xác minh riêng trên nguồn official bổ sung.')
    add('')
    add('Tài liệu này phù hợp để cấp quản lý đọc nhanh; khi cần xem giá chi tiết theo từng quốc tịch, vui lòng mở link sheet đính kèm.')
    add('')

    text = '\n'.join(lines)

    end_index = get_doc_end_index(DOC_ID)
    requests = []
    if end_index > 2:
        requests.append({'deleteContentRange': {'range': {'startIndex': 1, 'endIndex': end_index - 1}}})
    requests.append({'insertText': {'location': {'index': 1}, 'text': text}})

    # Compute line start indices after insertion
    starts = []
    idx = 1
    for line in lines:
        starts.append(idx)
        idx += len(line) + 1

    for line_no in heading1_lines:
        start = starts[line_no]
        end = start + len(lines[line_no])
        requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}})
        requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})

    for line_no in heading2_lines:
        start = starts[line_no]
        end = start + len(lines[line_no])
        requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_2'}, 'fields': 'namedStyleType'}})
        requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})

    # Bold prefixes before ':' for cleaner executive style
    for i, line in enumerate(lines):
        if ': ' in line and not line.startswith('http'):
            prefix = line.split(':', 1)[0] + ':'
            if len(prefix) > 1 and len(prefix) < len(line):
                start = starts[i]
                end = start + len(prefix)
                requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})

        # inline markdown-ish *...* => italic/bold emphasis by converting markers away later not supported simply
        # apply italic to full line if wrapped with *...*
        if line.startswith('*') and line.endswith('*') and len(line) > 2:
            start = starts[i]
            end = start + len(line)
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})

    # Slight emphasis for the final note line
    final_line_no = len(lines) - 2
    start = starts[final_line_no]
    end = start + len(lines[final_line_no])
    requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'italic': True}, 'fields': 'bold,italic'}})

    http_json(f'https://docs.googleapis.com/v1/documents/{DOC_ID}:batchUpdate', method='POST', data={'requests': requests})
    print(json.dumps({'doc_url': f'https://docs.google.com/document/d/{DOC_ID}/edit', 'requests_sent': len(requests)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
