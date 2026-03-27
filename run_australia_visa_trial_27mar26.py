import json
import urllib.parse
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
OAUTH_CLIENT_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.oauth-client.json'
TODAY_TAB = '27Mar26'
DATE_TEXT = '27 Mar 2026'
DATE_VI = '27/03/2026'

SHEET_TITLE = 'Australia visa monitoring'
DOC_TITLE = f'Australia visa trial report - {DATE_TEXT}'

ROWS = [
    ['Visa / stream', 'Purpose / use case', 'Stay / validity', 'Cost', 'Processing times', 'Application channel', 'Key eligibility / docs cues', 'Important notes', 'Official source'],
    ['ETA (subclass 601)', 'Du lịch, thăm thân, cruise, một số business visitor activities', 'Hiệu lực đi nhiều lần trong 12 tháng; ở tối đa 3 tháng mỗi lần nhập cảnh', 'AUD20 service charge qua Australian ETA app; không có charge ETA nào khác được nêu trên page', 'Official page nói trong đa số trường hợp kết quả được thông báo ngay; có thể lâu hơn nếu khai sai hoặc cần thêm thông tin', 'Bắt buộc qua Australian ETA app', 'Phải ở ngoài Australia khi apply; phải có ETA-eligible passport; cần dùng app; nên chưa đặt travel arrangements trước khi được grant', 'Passport holder châu Âu có thể phù hợp hơn với eVisitor 651; page nhấn mạnh không phải visa cho công dân Australia', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/electronic-travel-authority-601'],
    ['eVisitor (subclass 651)', 'Du lịch, thăm thân, cruise, business visitor activities; có thể study/train tối đa 3 tháng trong một số trường hợp', 'Hiệu lực đi nhiều lần trong 12 tháng; ở tối đa 3 tháng mỗi lần nhập cảnh', 'Free', 'Official page chỉ dẫn dùng visa processing time guide tool; không nêu con số tĩnh trên page snapshot hôm nay', 'Online', 'Phải ở ngoài Australia khi apply; phải là công dân và giữ passport hợp lệ của quốc gia đủ điều kiện eVisitor', 'Không áp dụng cho công dân Australia', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/evisitor-651'],
    ['Visitor 600 - Tourist stream (apply outside Australia)', 'Du lịch, cruise, thăm gia đình/bạn bè', 'Ở tối đa 12 tháng', 'From AUD200.00', 'Official page chỉ dẫn dùng visa processing time guide tool; không nêu con số tĩnh trên page snapshot hôm nay', 'Online / visa application flow', 'Có đủ tiền cho thời gian lưu trú; không làm việc; phải ở ngoài Australia khi apply và khi có quyết định; passport hợp lệ', 'Áp dụng cho applicant ở ngoài Australia', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/tourist-stream-overseas'],
    ['Visitor 600 - Business Visitor stream', 'Thăm Úc vì mục đích business ngắn hạn: general business/employment enquiries, negotiate contracts, conference/trade fair', 'Ở tối đa 3 tháng', 'AUD200.00', 'Official page chỉ dẫn dùng visa processing time guide tool; không nêu con số tĩnh trên page snapshot hôm nay', 'Online / visa application flow', 'Genuine business visitor; phải ở ngoài Australia khi apply và khi quyết định; có thể cần health exams / hồ sơ bổ trợ theo case', 'Page có note về new visa arrangements cho ASEAN / Timor-Leste và cảnh báo visa hopping sang Student program', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/business-visitor-stream'],
    ['Visitor 600 - Sponsored Family stream', 'Thăm thân theo diện có sponsor, thường là thành viên gia đình tại Australia', 'Ở tối đa 12 tháng', 'AUD200.00; có thể yêu cầu sponsor nộp security bond', 'Official page chỉ dẫn dùng visa processing time guide tool; không nêu con số tĩnh trên page snapshot hôm nay', 'Online / visa application flow', 'Cần có sponsor; phải là visitor thực sự; có thể phát sinh health exams / hồ sơ bổ trợ', 'Security bond là biến số nghiệp vụ quan trọng cần kiểm case-by-case', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/sponsored-family-stream'],
    ['Visitor 600 - Frequent Traveller stream', 'Du lịch hoặc business visitor activities cho nhóm quốc tịch được nêu trên page', 'Visa có thể grant tới 10 năm; ở tối đa 3 tháng mỗi lần nhập cảnh', 'AUD1,480.00', 'Processing times unavailable trên page hôm nay', 'Online / visa application flow', 'Chỉ cho công dân của: China, Brunei, Cambodia, Philippines, Laos, Indonesia, Malaysia, Singapore, Thailand, Vietnam, Timor-Leste', 'Không phải stream phổ quát; giới hạn theo quốc tịch được page liệt kê', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/frequent-traveller-stream'],
    ['Transit visa (subclass 771)', 'Quá cảnh Australia hoặc vào Australia bằng đường hàng không trước khi lên tàu với Maritime Crew Visa', 'Không quá 72 giờ', 'Free', 'Official page chỉ dẫn dùng visa processing time guide tool; không nêu con số tĩnh trên page snapshot hôm nay', 'Visa application flow', 'Phải ở ngoài Australia; có booking confirmed đi tiếp trong 72 giờ; có giấy tờ để vào nước đến', 'Nếu đang ở sân bay <8 giờ và không rời sân bay thì có thể thuộc diện TWOV, nhưng phải kiểm airport/transit conditions thật kỹ', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771'],
    ['Transit without a visa (TWOV) - exception regime', 'Ngoại lệ quá cảnh không cần visa trong một số case đủ điều kiện', 'Trong 8 giờ, không rời airport transit lounge, không cần clear immigration', 'N/A', 'N/A', 'Không phải visa riêng; là transit exception', 'Chỉ cho eligible countries / passport statuses; phải có vé confirmed đi nước thứ ba trong 8 giờ; nếu phải lấy hành lý / đổi terminal / clear immigration thì cần visa', 'Không nên diễn giải TWOV thành rule chung cho mọi transit case', 'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771/travellers-eligible-to-transit-without-visa'],
]

SOURCE_URLS = [
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/electronic-travel-authority-601',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/evisitor-651',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/tourist-stream-overseas',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/business-visitor-stream',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/sponsored-family-stream',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/visitor-600/frequent-traveller-stream',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771/travellers-eligible-to-transit-without-visa',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/transit-771/transit-facilities-at-australian-airports',
    'https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-processing-times/global-visa-processing-times',
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


def http_json(url, method='GET', data=None):
    headers = {
        'Authorization': f'Bearer {access_token()}',
        'Content-Type': 'application/json; charset=utf-8',
    }
    body = None if data is None else json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers=headers, method=method)
    with urlopen(req, timeout=120) as resp:
        raw = resp.read().decode('utf-8')
        return json.loads(raw) if raw else {}


def create_sheet(title):
    return http_json('https://sheets.googleapis.com/v4/spreadsheets', method='POST', data={'properties': {'title': title}})


def batch_update_sheet(spreadsheet_id, requests):
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate', method='POST', data={'requests': requests})


def update_values(spreadsheet_id, tab, values):
    rng = f'{tab}!A1:I{len(values)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{urllib.parse.quote(rng)}?valueInputOption=RAW'
    return http_json(url, method='PUT', data={'range': rng, 'majorDimension': 'ROWS', 'values': values})


def create_doc(title):
    return http_json('https://www.googleapis.com/drive/v3/files', method='POST', data={'name': title, 'mimeType': 'application/vnd.google-apps.document'})


def get_doc(doc_id):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}')


def doc_batch_update(doc_id, requests):
    return http_json(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', method='POST', data={'requests': requests})


def setup_sheet(spreadsheet_id):
    meta = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}')
    default_sheet_id = meta['sheets'][0]['properties']['sheetId']
    requests = [
        {'updateSheetProperties': {'properties': {'sheetId': default_sheet_id, 'title': 'Base'}, 'fields': 'title'}},
        {'duplicateSheet': {'sourceSheetId': default_sheet_id, 'newSheetName': TODAY_TAB, 'insertSheetIndex': 1}},
    ]
    batch_update_sheet(spreadsheet_id, requests)
    meta = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}')
    title_to_id = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    for tab in ['Base', TODAY_TAB]:
        update_values(spreadsheet_id, tab, ROWS)
    format_reqs = []
    for tab in ['Base', TODAY_TAB]:
        sid = title_to_id[tab]
        format_reqs.extend([
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 9}, 'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.82, 'green': 0.89, 'blue': 0.95}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'WRAP', 'textFormat': {'bold': True, 'fontSize': 10}}}, 'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat.bold,textFormat.fontSize)'}},
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': len(ROWS), 'startColumnIndex': 0, 'endColumnIndex': 9}, 'cell': {'userEnteredFormat': {'verticalAlignment': 'TOP', 'wrapStrategy': 'WRAP', 'textFormat': {'fontSize': 10}}}, 'fields': 'userEnteredFormat(verticalAlignment,wrapStrategy,textFormat.fontSize)'}},
            {'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}}, 'fields': 'gridProperties.frozenRowCount'}},
            {'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1}, 'properties': {'pixelSize': 58}, 'fields': 'pixelSize'}},
            {'updateBorders': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': len(ROWS), 'startColumnIndex': 0, 'endColumnIndex': 9}, 'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}, 'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}}},
        ])
        widths = {0: 220, 1: 220, 2: 210, 3: 150, 4: 220, 5: 165, 6: 250, 7: 260, 8: 330}
        for col, width in widths.items():
            format_reqs.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': col, 'endIndex': col + 1}, 'properties': {'pixelSize': width}, 'fields': 'pixelSize'}})
    batch_update_sheet(spreadsheet_id, format_reqs)
    return title_to_id[TODAY_TAB]


def build_doc_lines(sheet_url):
    lines = [
        'BÁO CÁO THEO DÕI VISA ÚC',
        '',
        '1. TÓM TẮT THAY ĐỔI SO VỚI HÔM QUA',
        '',
        'Chưa có baseline Australia của hôm qua trong hệ thống nội bộ cho scope 601 / 651 / 600 / 771. Báo cáo hôm nay được dùng làm bản baseline đầu tiên.',
        '',
        '2. TÓM TẮT THAY ĐỔI TRONG 7 NGÀY QUA',
        '',
        'Chưa đủ chuỗi dữ liệu nội bộ 7 ngày cho Australia trong scope này. Báo cáo hôm nay là mốc baseline để bắt đầu theo dõi biến động hằng ngày.',
        '',
        '3. TÓM TẮT THAY ĐỔI TỪ ĐẦU THÁNG',
        '',
        'Chưa có dữ liệu nội bộ được chuẩn hóa từ đầu tháng cho Australia trong scope 601 / 651 / 600 / 771. Từ ngày mai có thể bắt đầu so sánh day-over-day, rolling 7 days, và month-to-date trên cùng format.',
        '',
        '4. CÁC LOẠI VISA HIỆN HÀNH',
        '',
        '- ETA 601: multiple-entry trong 12 tháng, ở tối đa 3 tháng mỗi lần, dùng cho du lịch / thăm thân / cruise / một số business visitor activities; apply qua Australian ETA app; page nêu service charge AUD20.',
        '- eVisitor 651: multiple-entry trong 12 tháng, ở tối đa 3 tháng mỗi lần, free, áp dụng cho passport/quốc tịch đủ điều kiện eVisitor; có thể study/train tối đa 3 tháng trong một số trường hợp.',
        '- Visitor 600: nhóm visa visitor có nhiều stream. Trong scope thử hôm nay em theo dõi các stream chính liên quan nghiệp vụ short-stay: Tourist stream (outside Australia), Business Visitor stream, Sponsored Family stream, Frequent Traveller stream.',
        '- Visitor 600 Tourist stream (outside Australia): ở tối đa 12 tháng; from AUD200.00; dùng cho du lịch / cruise / thăm thân khi apply từ ngoài Australia.',
        '- Visitor 600 Business Visitor stream: ở tối đa 3 tháng; AUD200.00; dùng cho business visit ngắn hạn như enquiry, đàm phán hợp đồng, conference / trade fair.',
        '- Visitor 600 Sponsored Family stream: ở tối đa 12 tháng; AUD200.00; có thể yêu cầu sponsor nộp security bond; phù hợp hồ sơ thăm thân có bảo lãnh.',
        '- Visitor 600 Frequent Traveller stream: chỉ áp dụng cho nhóm quốc tịch được page nêu; visa có thể grant tới 10 năm; ở tối đa 3 tháng mỗi lần nhập cảnh; phí AUD1,480.00.',
        '- Transit 771: free; ở không quá 72 giờ; dùng cho case quá cảnh hoặc vào Úc bằng đường hàng không trước khi join tàu với Maritime Crew visa.',
        '- TWOV không phải visa riêng mà là ngoại lệ quá cảnh không cần visa trong một số case đủ điều kiện. Nếu phải clear immigration, lấy hành lý, hoặc đổi terminal theo cách phải ra khỏi transit lounge thì cần xem lại khả năng phải có visa.',
        '',
        'Chi tiết phí, stay, application channel, cues hồ sơ và link nguồn nằm trong sheet chi tiết:',
        sheet_url,
        '',
        '5. GHI CHÚ QUAN TRỌNG',
        '',
        '- Home Affairs không hiển thị sẵn processing time dạng số cố định trên hầu hết các page thuộc scope hôm nay; đa số page chỉ dẫn sang visa processing time guide tool. Vì vậy không nên tự điền số ngày xử lý cứng nếu chưa query trực tiếp tool đó theo đúng visa type/stream/date.',
        '- ETA 601 page nêu rằng trong đa số trường hợp có thể có kết quả ngay, nhưng vẫn cảnh báo có thể lâu hơn nếu khai chưa đúng hoặc cần thêm thông tin; không nên hứa same-day approval như một cam kết tuyệt đối.',
        '- Visitor 600 Frequent Traveller stream không phải route phổ quát; chỉ dành cho nhóm quốc tịch được official page liệt kê.',
        '- Sponsored Family stream có biến số security bond; đây là điểm nghiệp vụ cần giữ caveat thay vì báo giá như fee trọn gói cố định.',
        '- Transit 771 cần đọc cùng với TWOV rule và airport transit facilities. Có case không cần visa nếu transit dưới 8 giờ và không rời sân bay, nhưng airport limitations có thể vẫn khiến traveler phải clear immigration và do đó cần visa.',
        '- Trên một số trang Visitor 600 có note về new visa arrangements cho ASEAN / Timor-Leste và cảnh báo visa hopping sang Student program. Hôm nay em mới ghi nhận sự tồn tại của official notices này; chưa đưa kết luận sâu hơn vì cần scope nghiệp vụ xác định mức độ liên quan.',
        '- Hôm nay em chưa thấy dấu hiệu economic / political shock note nào được official visa pages trong scope này nêu riêng như một thay đổi tức thời ảnh hưởng trực tiếp đến policy của 601 / 651 / 600 / 771.',
        '',
        '6. NGUỒN THÔNG TIN',
        '',
    ]
    for url in SOURCE_URLS:
        lines.append(f'- {url}')
    lines.extend([
        '',
        '7. TECHNICAL CHANGELOG',
        '',
        '- Đây là lần baseline đầu tiên cho Australia scope 601 / 651 / 600 / 771 nên chưa có diff kỹ thuật với report hôm trước.',
        '- Home Affairs render một số dữ liệu quan trọng của Visitor 600 bằng JS trên page, nên bản thử hôm nay phải kiểm tra trực tiếp ở rendered page để lấy đúng cost hiển thị hiện hành.',
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
        if line == 'BÁO CÁO THEO DÕI VISA ÚC':
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'TITLE', 'alignment': 'CENTER'}, 'fields': 'namedStyleType,alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
        elif line[:2].isdigit() and '. ' in line:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1', 'spaceAbove': {'magnitude': 14, 'unit': 'PT'}, 'spaceBelow': {'magnitude': 4, 'unit': 'PT'}}, 'fields': 'namedStyleType,spaceAbove,spaceBelow'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.12, 'green': 0.33, 'blue': 0.53}}}}, 'fields': 'bold,foregroundColor'}})
    doc_batch_update(doc_id, requests)


def main():
    refresh_access_token_if_needed()
    sheet = create_sheet(SHEET_TITLE)
    spreadsheet_id = sheet['spreadsheetId']
    gid = setup_sheet(spreadsheet_id)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={gid}'
    doc = create_doc(DOC_TITLE)
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    lines = build_doc_lines(sheet_url)
    write_doc(doc_id, lines)
    print(json.dumps({
        'doc_url': doc_url,
        'sheet_url': sheet_url,
        'summary_vi': 'Đã dựng baseline thử cho Australia scope 601 / 651 / 600 / 771. Vì đây là bản đầu tiên nên chưa có thay đổi so với hôm qua để so sánh; report tập trung khóa source official, các loại visa hiện hành, mức phí hiển thị, stay/validity, các lưu ý về processing-time tool, security bond, frequent traveller nationality scope, và caveat TWOV/transit.',
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
