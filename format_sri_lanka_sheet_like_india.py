import json
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
SPREADSHEET_ID = '1hlS093IYraw-xq7EGU2MFXgzIucZd-gVUykXUwVpJOM'
TARGET_TABS = ['Base', '26Mar26']


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


def get_sheet_meta():
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}')


def batch_update(requests):
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data={'requests': requests})


def main():
    meta = get_sheet_meta()
    title_to_id = {s['properties']['title']: s['properties']['sheetId'] for s in meta['sheets']}
    requests = []

    for title in TARGET_TABS:
        sid = title_to_id[title]
        # Header style like India sheet
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 9},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.82, 'green': 0.89, 'blue': 0.95},
                        'horizontalAlignment': 'CENTER',
                        'verticalAlignment': 'MIDDLE',
                        'wrapStrategy': 'WRAP',
                        'textFormat': {'bold': True, 'fontSize': 10}
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat.bold,textFormat.fontSize)'
            }
        })
        # Body cells wrap and vertical align top
        requests.append({
            'repeatCell': {
                'range': {'sheetId': sid, 'startRowIndex': 1, 'endRowIndex': 100, 'startColumnIndex': 0, 'endColumnIndex': 9},
                'cell': {
                    'userEnteredFormat': {
                        'verticalAlignment': 'TOP',
                        'wrapStrategy': 'WRAP',
                        'textFormat': {'fontSize': 10}
                    }
                },
                'fields': 'userEnteredFormat(verticalAlignment,wrapStrategy,textFormat.fontSize)'
            }
        })
        # Freeze header row
        requests.append({
            'updateSheetProperties': {
                'properties': {'sheetId': sid, 'gridProperties': {'frozenRowCount': 1}},
                'fields': 'gridProperties.frozenRowCount'
            }
        })
        # Set row heights for readability
        requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': sid, 'dimension': 'ROWS', 'startIndex': 0, 'endIndex': 1},
                'properties': {'pixelSize': 54},
                'fields': 'pixelSize'
            }
        })
        # Column widths closer to India-style operational sheet
        widths = {
            0: 180,
            1: 170,
            2: 170,
            3: 120,
            4: 150,
            5: 150,
            6: 140,
            7: 190,
            8: 300,
        }
        for col, width in widths.items():
            requests.append({
                'updateDimensionProperties': {
                    'range': {'sheetId': sid, 'dimension': 'COLUMNS', 'startIndex': col, 'endIndex': col + 1},
                    'properties': {'pixelSize': width},
                    'fields': 'pixelSize'
                }
            })
        # Add borders to visible data area
        requests.append({
            'updateBorders': {
                'range': {'sheetId': sid, 'startRowIndex': 0, 'endRowIndex': 20, 'startColumnIndex': 0, 'endColumnIndex': 9},
                'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}},
                'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}},
                'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}},
                'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.75, 'green': 0.75, 'blue': 0.75}},
                'innerHorizontal': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}},
                'innerVertical': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.86, 'green': 0.86, 'blue': 0.86}}
            }
        })

    batch_update(requests)
    print(json.dumps({
        'spreadsheet_url': f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit',
        'tabs_formatted': TARGET_TABS,
        'requests_sent': len(requests)
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
