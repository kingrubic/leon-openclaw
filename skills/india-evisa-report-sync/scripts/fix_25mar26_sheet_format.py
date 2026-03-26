import json
import importlib.util
from pathlib import Path
from urllib.request import Request, urlopen

WORKSPACE = Path('/Users/admin/.openclaw/workspace')
TOKEN_PATH = WORKSPACE / 'google-credentials' / 'kenyaimmigration-org.tokens.json'
SPREADSHEET_ID = '1K3Z-Wf-KBKbMVhxzLDJDhfNgrriEiB6C9c2BkptAa_I'
SHEET_TITLE = '25Mar26'


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


def quote_range(rng: str):
    from urllib.parse import quote
    return quote(rng)


def get_values(sheet_title='Base'):
    rng = f'{sheet_title}!A1:J500'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote_range(rng)}'
    return http_json(url)['values']


def update_values(sheet_title, values):
    rng = f'{sheet_title}!A1:J{len(values)}'
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{quote_range(rng)}?valueInputOption=RAW'
    body = {'range': rng, 'majorDimension': 'ROWS', 'values': values}
    return http_json(url, method='PUT', data=body)


def get_sheet_id(title):
    meta = http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}')
    for s in meta['sheets']:
        if s['properties']['title'] == title:
            return s['properties']['sheetId']
    raise ValueError(f'Sheet not found: {title}')


def batch_update(requests):
    body = {'requests': requests}
    return http_json(f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}:batchUpdate', method='POST', data=body)


def main():
    spec = importlib.util.spec_from_file_location('evisa', '/Users/admin/.openclaw/workspace/india_evisa_update_report.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    base_values = get_values('Base')
    tourist_map, other_map = mod.build_fee_maps()
    new_rows, changes, changed_counts, missing_fee = mod.compare_and_build_rows(base_values, tourist_map, other_map)
    update_values(SHEET_TITLE, new_rows)

    sheet_id = get_sheet_id(SHEET_TITLE)

    # Reset bold for the whole data area except header.
    requests = [
        {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': 1,
                    'endRowIndex': len(new_rows),
                    'startColumnIndex': 1,
                    'endColumnIndex': 10,
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': False
                        }
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        }
    ]

    column_index = {
        'Tourist 30 ngày': 1,
        'Tourist 1 năm': 2,
        'Tourist 5 năm': 3,
        'Business': 4,
        'Medical': 5,
        'Ayush': 6,
        'Conference': 7,
        'Student': 8,
        'Transit': 9,
    }

    country_to_row = {}
    for idx, row in enumerate(new_rows[1:], start=1):
        if row and row[0]:
            country_to_row[row[0]] = idx

    for item in changes:
        row_idx = country_to_row[item['country']]
        col_idx = column_index[item['column']]
        requests.append({
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': row_idx,
                    'endRowIndex': row_idx + 1,
                    'startColumnIndex': col_idx,
                    'endColumnIndex': col_idx + 1,
                },
                'cell': {
                    'userEnteredFormat': {
                        'textFormat': {
                            'bold': True
                        }
                    }
                },
                'fields': 'userEnteredFormat.textFormat.bold'
            }
        })

    batch_update(requests)

    print(json.dumps({
        'sheet_title': SHEET_TITLE,
        'sheet_id': sheet_id,
        'rows_written': len(new_rows),
        'changes_bolded': len(changes),
        'changed_counts': changed_counts,
        'sheet_url': f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={sheet_id}'
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
