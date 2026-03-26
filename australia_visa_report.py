import json
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
TODAY_TAB = '26Mar26'


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


def create_spreadsheet(title):
    body = {'properties': {'title': title}, 'sheets': [{'properties': {'title': 'Base'}}]}
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
        ['Sản phẩm visa', 'Mục đích chính', 'Thời gian lưu trú', 'Điều kiện nộp', 'Phí official', 'Nhập cảnh', 'Điểm nổi bật', 'Cảnh báo / Lưu ý'],
        ['Visitor visa (subclass 600) – Tourist stream (outside Australia)', 'Du lịch, cruise, thăm thân', 'Tối đa 12 tháng; grant có thể là 3, 6 hoặc 12 tháng', 'Phải ở ngoài Australia khi nộp và khi được quyết định', 'Từ AUD 200', 'Tùy grant', 'Nhóm visitor linh hoạt nhất cho khách ngoài Australia', 'Không nên viết cứng là ai cũng được 12 tháng; official chỉ nói up to 12 months.'],
        ['Visitor visa (subclass 600) – Tourist stream (in Australia)', 'Du lịch / thăm thân khi đang ở Australia', 'Tối đa 12 tháng', 'Phải đang ở Australia khi nộp và khi được quyết định', 'Từ AUD 500', 'Tùy grant', 'Áp dụng cho người đã ở Australia', 'Không dùng cho business visitor hoặc medical treatment.'],
        ['Visitor visa (subclass 600) – Business Visitor stream', 'Hoạt động business visitor', 'Tối đa 3 tháng', 'Phải ở ngoài Australia khi nộp và khi được quyết định', 'AUD 200', 'Có thể single hoặc multiple tùy grant', 'Không được work hoặc sell goods/services', 'Không nên viết cứng là luôn multiple entry.'],
        ['Visitor visa (subclass 600) – Frequent Traveller stream', 'Du lịch và/hoặc business visitor activities', 'Tối đa 3 tháng mỗi lần nhập cảnh', 'Chỉ cho một số quốc tịch châu Á xác định', 'AUD 1,480', 'Visa validity có thể tới 10 năm', 'Dành cho China, Brunei, Cambodia, Philippines, Laos, Indonesia, Malaysia, Singapore, Thailand, Vietnam, Timor Leste', 'Processing times unavailable theo official page.'],
        ['Visitor visa (subclass 600) – Sponsored Family stream', 'Thăm thân có bảo lãnh', 'Tối đa 12 tháng', 'Có thể yêu cầu eligible family member bảo lãnh', 'AUD 200', 'Tùy grant', 'Có thể yêu cầu security bond', 'Sponsor phải là Australian citizen hoặc permanent resident đủ điều kiện.'],
        ['Visitor visa (subclass 600) – Approved Destination Status stream', 'Tour theo chương trình ADS', 'Theo grant letter', 'Áp dụng cho công dân PRC đi tour qua đại lý được phê duyệt', 'AUD 200', 'Theo grant', 'Stream chuyên biệt cho tour đoàn', 'Đối tượng rất hẹp, không nên suy rộng.'],
        ['eVisitor (subclass 651)', 'Du lịch, thăm thân, một số business visitor activities', 'Tối đa 3 tháng mỗi lần', 'Phải nộp từ ngoài Australia; chỉ áp dụng cho một số hộ chiếu đủ điều kiện', 'Free', 'Theo grant', 'Có thể học/train tối đa 3 tháng trong một số trường hợp', 'Danh sách nước đủ điều kiện phụ thuộc hộ chiếu; cần kiểm tra official list trước khi tư vấn.'],
        ['ETA (subclass 601)', 'Du lịch, thăm thân, một số business visitor activities', 'Tối đa 3 tháng mỗi lần', 'Phải nộp từ ngoài Australia; phải dùng Australian ETA app; cần eligible passport', 'Không có visa charge, nhưng có AUD 20 service charge qua app', 'Theo grant', 'Trong đa số trường hợp kết quả có thể ra ngay', 'Không nên đặt chuyến đi trước khi ETA được grant.'],
        ['Transit visa (subclass 771)', 'Quá cảnh qua Australia', 'Không quá 72 giờ', 'Phải ở ngoài Australia; cần onward booking + giấy tờ nhập cảnh nước tiếp theo', 'Free', 'Theo nhu cầu transit', 'Mục đích rất rõ, time-boxed', 'Nếu là crew thì có thể cần Maritime Crew visa thay vì 771.'],
        ['Medical Treatment visa (subclass 602)', 'Điều trị y tế / tư vấn y khoa / hiến tạng / đi cùng hỗ trợ', 'Tạm thời', 'Có thể nộp ngoài hoặc trong Australia tùy case', 'Free nếu nộp ngoài Australia; nộp trong Australia có thể có phí', 'Có thể single hoặc multiple', 'Nhóm visitor-adjacent, không phải du lịch thuần', 'Phí in-Australia chưa được trích sạch trong lượt rà soát này.'],
    ]


def apply_sheet_format(spreadsheet_id, base_id, col_count):
    req = [
        {'duplicateSheet': {'sourceSheetId': base_id, 'newSheetName': TODAY_TAB, 'insertSheetIndex': 1}},
    ]
    batch_update_sheet(spreadsheet_id, req)
    meta = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}')
    ids = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}

    requests = []
    for sid in [ids['Base'], ids[TODAY_TAB]]:
        requests.extend([
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': col_count}, 'cell': {'userEnteredFormat': {'backgroundColor': {'red': 0.82, 'green': 0.89, 'blue': 0.95}, 'horizontalAlignment': 'CENTER', 'verticalAlignment': 'MIDDLE', 'wrapStrategy': 'WRAP', 'textFormat': {'bold': True, 'fontSize': 10}}}, 'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat.bold,textFormat.fontSize)'}},
            {'repeatCell': {'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': 50, 'startColumnIndex': 0, 'endColumnIndex': col_count}, 'cell': {'userEnteredFormat': {'verticalAlignment': 'TOP', 'wrapStrategy': 'WRAP', 'textFormat': {'fontSize': 10}}}, 'fields': 'userEnteredFormat(verticalAlignment,wrapStrategy,textFormat.fontSize)'}},
            {'updateSheetProperties': {'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}}, 'fields': 'gridProperties.frozenRowCount'}},
            {'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1}, 'properties': {'pixelSize': 54}, 'fields': 'pixelSize'}},
            {'updateBorders': {'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 30, 'startColumnIndex': 0, 'endColumnIndex': col_count}, 'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}}, 'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}, 'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}}},
        ])
        widths = [240, 180, 170, 220, 120, 130, 200, 280]
        for i, w in enumerate(widths):
            requests.append({'updateDimensionProperties': {'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': i, 'endIndex': i + 1}, 'properties': {'pixelSize': w}, 'fields': 'pixelSize'}})
    batch_update_sheet(spreadsheet_id, requests)
    return ids[TODAY_TAB]


def build_doc_lines(sheet_url):
    return [
        'BÁO CÁO VISA ÚC',
        'Bản tóm tắt quản trị dựa trên nguồn official của Department of Home Affairs và phần theo dõi news 7 ngày gần nhất',
        '',
        'Ngày lập: 26/03/2026',
        'Nguồn chính phủ chính: https://immi.homeaffairs.gov.au/ và hệ sinh thái https://online.immi.gov.au/',
        f'Sheet vận hành chi tiết: {sheet_url}',
        '',
        'PHẦN A – THÔNG TIN CHÍNH PHỦ',
        '',
        '1. TÓM TẮT ĐIỀU HÀNH',
        '',
        'Đối với nhóm visitor / short-stay, Australia có nhiều sản phẩm visa/authorisation khác nhau thay vì một sản phẩm chung. Vì vậy, khi đưa lên hệ thống, cần phân biệt rõ sản phẩm theo mục đích, nơi nộp hồ sơ, điều kiện hộ chiếu, thời gian lưu trú và cảnh báo hạn chế.',
        '',
        'Các điểm chính:',
        '- Visitor visa (subclass 600) là nhóm visitor linh hoạt và bao phủ rộng nhất.',
        '- eVisitor 651 và ETA 601 là các kênh điện tử phụ thuộc mạnh vào điều kiện quốc tịch/hộ chiếu.',
        '- ETA 601 thường cho kết quả rất nhanh trong đa số trường hợp, nhưng không nên đặt chuyến đi trước khi ETA được grant.',
        '- Business Visitor không cho phép work hoặc sell goods/services.',
        '- Processing time nên được diễn giải theo official processing-time guide; không nên viết cứng một con số chung nếu chưa snapshot từ tool tại thời điểm báo cáo.',
        '',
        '2. CÁC NHÓM SẢN PHẨM VISITOR CHÍNH',
        '',
        '- Visitor visa (subclass 600) – Tourist stream (outside Australia)',
        '- Visitor visa (subclass 600) – Tourist stream (in Australia)',
        '- Visitor visa (subclass 600) – Business Visitor stream',
        '- Visitor visa (subclass 600) – Frequent Traveller stream',
        '- Visitor visa (subclass 600) – Sponsored Family stream',
        '- Visitor visa (subclass 600) – Approved Destination Status stream',
        '- eVisitor (subclass 651)',
        '- ETA (subclass 601)',
        '- Transit visa (subclass 771)',
        '- Medical Treatment visa (subclass 602)',
        '',
        '3. ĐIỂM CẦN LƯU Ý VỀ ĐIỀU KIỆN / MỤC ĐÍCH / PHÍ',
        '',
        '- Visitor 600 Tourist stream (outside Australia): stay có thể tới 12 tháng, nhưng Home Affairs nói rõ grant có thể là 3, 6 hoặc 12 tháng; không nên viết cứng ai cũng được 12 tháng.',
        '- Visitor 600 Tourist stream (in Australia): cũng có thể tới 12 tháng, nhưng chỉ áp dụng khi người nộp đang ở Australia.',
        '- Business Visitor stream: stay tối đa 3 tháng; không được work hoặc sell goods/services; entry count có thể single hoặc multiple tùy grant.',
        '- Frequent Traveller stream: một số quốc tịch châu Á nhất định; visa validity có thể tới 10 năm; mỗi lần stay tối đa 3 tháng; phí AUD 1,480.',
        '- eVisitor 651: free, nhưng chỉ áp dụng cho một số passport đủ điều kiện và phải nộp từ ngoài Australia.',
        '- ETA 601: không có visa charge nhưng có AUD 20 service charge qua Australian ETA app; chỉ áp dụng cho eligible passport và phải nộp từ ngoài Australia.',
        '- Transit 771: free, tối đa 72 giờ, cần onward booking và giấy tờ nhập cảnh nước tiếp theo.',
        '',
        '4. CẢNH BÁO QA QUAN TRỌNG',
        '',
        '- Không nên gộp Visitor 600, eVisitor 651 và ETA 601 thành cùng một nhóm “visa du lịch Úc” vì điều kiện áp dụng khác nhau rõ rệt.',
        '- Không nên viết “visa du lịch Úc là 12 tháng” như một kết luận cứng.',
        '- Không nên viết “Business Visitor được multiple entry” như điều chắc chắn; official wording là phụ thuộc grant.',
        '- Không nên ghi processing time là X ngày/tuần nếu chưa lấy snapshot cụ thể từ processing-time guide tại đúng thời điểm báo cáo.',
        '- Không nên dùng australia.com làm nguồn chính cho quy định visa.',
        '',
        '5. CÂU CHỮ KHUYẾN NGHỊ KHI ĐƯA VÀO HỆ THỐNG',
        '',
        '- Nên dùng: “Theo Australian Department of Home Affairs...”',
        '- Nên dùng: “Visitor visa (subclass 600) gồm nhiều stream, và điều kiện khác nhau theo từng stream.”',
        '- Nên dùng: “Home Affairs cho biết stay có thể up to 12 months đối với một số stream visitor nhất định.”',
        '- Nên dùng: “eVisitor 651 và ETA 601 phụ thuộc eligibility theo passport/quốc tịch; cần kiểm tra official criteria trước khi tư vấn.”',
        '',
        'PHẦN B – TIN TỨC / BÁO CHÍ LIÊN QUAN VISA (7 NGÀY GẦN NHẤT)',
        '',
        '1. KẾT QUẢ RÀ SOÁT 7 NGÀY GẦN NHẤT',
        '',
        '- australia.com: không ghi nhận tin mới liên quan visa / entry rules trong 7 ngày gần nhất. Site này chủ yếu phù hợp làm nguồn tourism/trip-planning, không phải nguồn policy/news mạnh cho visa.',
        '- executivetraveller.com: không ghi nhận bài mới liên quan visa / entry rules / immigration trong 7 ngày gần nhất.',
        '',
        '2. GHI CHÚ NGUỒN TIN',
        '',
        '- australia.com chỉ nên dùng làm nguồn tham khảo bổ sung về travel guidance, không nên dùng làm nguồn chính cho quy định visa.',
        '- Executive Traveller có thể dùng như nguồn media/travel-news phụ trợ, nhưng nếu có bài liên quan visa thì vẫn phải cross-check lại với Home Affairs trước khi đưa vào báo cáo chính thức.',
        '',
        '3. KẾT LUẬN CHO BẢN ÚC HÔM NAY',
        '',
        '- Bản cập nhật hôm nay chủ yếu dựa trên nguồn official của Department of Home Affairs.',
        '- Trong 7 ngày gần nhất, chưa ghi nhận tin báo chí mới từ 2 nguồn anh chỉ định đủ mạnh để làm thay đổi nội dung policy/visa summary hiện tại.',
        '',
        'DELIVERABLES',
        '',
        f'- Sheet vận hành chi tiết: {sheet_url}',
        '- Sheet được trình bày theo phong cách giống India/Sri Lanka, nhưng logic dữ liệu được điều chỉnh cho đúng cấu trúc visitor products của Australia.',
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
    for i, line in enumerate(lines):
        start = starts[i]
        end = start + len(line)
        if line == 'BÁO CÁO VISA ÚC':
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'TITLE', 'alignment': 'CENTER'}, 'fields': 'namedStyleType,alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 20, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
        elif line.startswith('Bản tóm tắt quản trị'):
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'alignment': 'CENTER'}, 'fields': 'alignment'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'italic': True}, 'fields': 'italic'}})
        elif line.startswith('PHẦN A') or line.startswith('PHẦN B'):
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_1', 'spaceAbove': {'magnitude': 16, 'unit': 'PT'}}, 'fields': 'namedStyleType,spaceAbove'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True, 'foregroundColor': {'color': {'rgbColor': {'red': 0.12, 'green': 0.33, 'blue': 0.53}}}}, 'fields': 'bold,foregroundColor'}})
        elif line[:2].isdigit() and '. ' in line:
            requests.append({'updateParagraphStyle': {'range': {'startIndex': start, 'endIndex': end}, 'paragraphStyle': {'namedStyleType': 'HEADING_2'}, 'fields': 'namedStyleType'}})
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
        elif line.startswith('Các điểm chính:'):
            requests.append({'updateTextStyle': {'range': {'startIndex': start, 'endIndex': end}, 'textStyle': {'bold': True}, 'fields': 'bold'}})
    doc_batch_update(doc_id, requests)


def main():
    values = build_sheet_values()
    spreadsheet = create_spreadsheet('Australia Visa - Official Tracker')
    spreadsheet_id = spreadsheet['spreadsheetId']
    base_id = spreadsheet['sheets'][0]['properties']['sheetId']
    update_values(spreadsheet_id, f'Base!A1:H{len(values)}', values)
    today_id = apply_sheet_format(spreadsheet_id, base_id, len(values[0]))
    update_values(spreadsheet_id, f'{TODAY_TAB}!A1:H{len(values)}', values)
    sheet_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={today_id}'

    doc = create_doc('Australia visa report - 26 Mar 2026')
    doc_id = doc['id']
    doc_url = f'https://docs.google.com/document/d/{doc_id}/edit'
    format_doc(doc_id, build_doc_lines(sheet_url))

    print(json.dumps({'sheet_url': sheet_url, 'doc_url': doc_url, 'spreadsheet_id': spreadsheet_id, 'doc_id': doc_id}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
