const fs = require('fs');
const path = require('path');

const SHEET_ID = '1YySvoWArHO69Yyv6CLV6Du44o8aX0OArtzqy9WQf2FQ';
const RANGE = process.argv[2] || 'Sheet1!A1:Z20';

const tokenPath = path.join(__dirname, 'google-credentials', 'kenyaimmigration-org.tokens.json');

function loadAccessToken() {
  const raw = fs.readFileSync(tokenPath, 'utf8');
  const json = JSON.parse(raw);
  if (!json.token || !json.token.access_token) {
    throw new Error('Missing access_token in token file');
  }
  return json.token.access_token;
}

async function main() {
  const accessToken = loadAccessToken();
  const url = new URL(`https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${encodeURIComponent(RANGE)}`);

  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Non-JSON response: ${text}`);
  }

  if (!res.ok) {
    throw new Error(`Sheets API error (${res.status}): ${JSON.stringify(data)}`);
  }

  console.log(JSON.stringify(data, null, 2));
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
