import json
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
DOC_ID = '1AMteb8SlOBQbWgves_slAMh_REvJ02gzbTmKseM-4wU'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1hlS093IYraw-xq7EGU2MFXgzIucZd-gVUykXUwVpJOM/edit#gid=211181409'


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


def get_doc(doc_id):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')


def doc_batch_update(doc_id, requests):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def main():
    lines = [
        'BÁO CÁO ETA SRI LANKA',
        'Bản tóm tắt quản trị dựa trên các nguồn ETA public chính thức',
        '',
        'Ngày lập: 26/03/2026',
        'Tên miền official chính: https://www.eta.gov.lk/',
        f'Sheet phí chi tiết: {SHEET_URL}',
        '',
        '1. TÓM TẮT ĐIỀU HÀNH',
        '',
        'Báo cáo này tổng hợp thông tin ETA Sri Lanka từ các trang public chính thức, theo hướng đủ an toàn để dùng nội bộ. Nội dung đã được rà soát chéo giữa nhiều trang ETA official và được viết theo nguyên tắc thận trọng để tránh kết luận quá mức ở những điểm mà chính nguồn official còn chưa thống nhất.',
        '',
        'Các điểm chính:',
        '- Sri Lanka ETA là cơ chế chấp thuận trước chuyến đi cho các nhu cầu short visit.',
        '- Các nhóm ETA chính xác nhận được trên site: Tourist, Business, Transit.',
        '- Cấu trúc phí ETA chuẩn được công bố khá rõ cho SAARC, all other countries và trẻ em dưới 12 tuổi.',
        '- Homepage alert hiện có cơ chế fee-free / visa-free đặc biệt cho China, India, Indonesia, Russia, Thailand, Malaysia và Japan, nhưng các đối tượng này vẫn được hướng dẫn phải xin ETA trước khi đi.',
        '- Quy định Business ETA chưa đồng nhất hoàn toàn giữa các trang official; số lần nhập cảnh và điều kiện nộp hồ sơ cần được diễn giải cẩn thận.',
        '',
        '2. NHÓM ETA XÁC NHẬN ĐƯỢC',
        '',
        '- Tourist',
        '- Business',
        '- Transit',
        '',
        '3. HIỆU LỰC, NHẬP CẢNH, THỜI GIAN LƯU TRÚ',
        '',
        '- Tourist ETA nhìn chung được mô tả là 30 ngày với double entry.',
        '- Transit ETA được mô tả là miễn phí và có thời hạn tối đa 2 ngày.',
        '- Official pages cho biết người có ETA có thể nhập cảnh Sri Lanka trong vòng 3 tháng kể từ ngày cấp.',
        '- Official pages cũng cho biết thời gian lưu trú ban đầu được cấp là 30 ngày từ ngày đến và có thể gia hạn lên đến 6 tháng.',
        '- Riêng Business ETA đang có sự không thống nhất giữa các trang: có chỗ nói double entry, có chỗ nói multiple entry trong 30 ngày.',
        '',
        '4. HỒ SƠ / ĐIỀU KIỆN CƠ BẢN KHI NHẬP CẢNH',
        '',
        '- Hộ chiếu còn hạn ít nhất 6 tháng tính từ ngày nhập cảnh.',
        '- Vé khứ hồi hoặc onward ticket.',
        '- Chứng minh đủ tài chính cho thời gian lưu trú.',
        '- Với Transit ETA, official site có nhắc rõ cần documentary proof.',
        '- Với business travel, site có nhắc cần hồ sơ/chứng từ liên quan để chứng minh mục đích công tác.',
        '',
        '5. TÓM TẮT PHÍ OFFICIAL',
        '',
        'Cấu trúc phí ETA chuẩn theo official fee page:',
        '- SAARC: Tourist US$20 / Business US$30 / Transit Free.',
        '- All other countries: Tourist US$50 / Business US$55 / Transit Free.',
        '- Trẻ em dưới 12 tuổi: Free trong bảng ETA fee chính.',
        '- On arrival: Tourist SAARC US$25 / Tourist other countries US$60 / Transit Free.',
        '- On-arrival business fee hiện chưa có số rõ; fee page đang hiển thị ô gạch (----).',
        '',
        '6. CƠ CHẾ ĐẶC BIỆT / NGOẠI LỆ CẦN LƯU Ý',
        '',
        '- Homepage alert hiện cho thấy cơ chế fee-free / visa-free cho China, India, Indonesia, Russia, Thailand, Malaysia và Japan.',
        '- Tuy nhiên, cùng alert đó vẫn hướng dẫn các đối tượng này phải xin ETA trước khi đi.',
        '- Vì vậy, hệ thống nội bộ không nên rút gọn thành “không cần ETA”.',
        '',
        '7. CẢNH BÁO QA QUAN TRỌNG',
        '',
        '- Không nên ghi cứng rằng 7 quốc gia nêu trên là hoàn toàn visa-free theo nghĩa không cần làm gì trước chuyến đi.',
        '- Không nên ghi rằng 7 quốc gia đó không cần ETA.',
        '- Không nên ghi rằng Business ETA luôn online, luôn double entry, hoặc luôn multiple entry.',
        '- Không nên xem on-arrival ETA là lộ trình mặc định; official site mô tả đây chỉ là limited facility.',
        '- Khi đọc fee table cần đối chiếu cùng homepage alerts, vì alert có thể override fee chuẩn cho một số quốc tịch cụ thể.',
        '',
        '8. CÂU CHỮ KHUYẾN NGHỊ KHI ĐƯA VÀO HỆ THỐNG',
        '',
        '- Nên dùng: “Theo ETA site official của Sri Lanka, hiện có cơ chế fee-free / visa-free đặc biệt cho 7 quốc tịch, nhưng các đối tượng này vẫn được yêu cầu xin ETA trước chuyến đi.”',
        '- Nên dùng: “Business ETA cần được rà soát cẩn thận do các trang official đang có wording chưa thống nhất về số lần nhập cảnh và kênh nộp hồ sơ.”',
        '- Nên dùng: “Khái niệm validity của ETA trên site cần được hiểu tách biệt giữa thời gian dùng ETA trước khi nhập cảnh, thời gian lưu trú được cấp khi tới nơi, và khả năng gia hạn.”',
        '',
        '9. DELIVERABLES',
        '',
        f'- Sheet phí chi tiết: {SHEET_URL}',
        '- Workbook này được trình bày theo phong cách vận hành giống file India, nhưng cấu trúc dữ liệu đã được điều chỉnh để phù hợp logic official của Sri Lanka (group-based pricing + special-country exceptions).',
    ]

    text = '\n'.join(lines)
    doc = get_doc(DOC_ID)
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
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line[:2].isdigit() and '. ' in line:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_2'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('Các điểm chính:') or line.startswith('Cấu trúc phí ETA chuẩn'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('- Nên dùng:') or line.startswith('- Không nên ghi'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})

    doc_batch_update(DOC_ID, requests)
    print(json.dumps({'doc_url': f'https://docs.google.com/document/d/{DOC_ID}/edit', 'requests_sent': len(requests)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
