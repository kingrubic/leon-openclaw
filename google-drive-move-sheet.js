const fs = require('fs');
const path = require('path');

const tokenPath = path.join(__dirname, 'google-credentials', 'kenyaimmigration-org.tokens.json');
const SHEET_ID = '1RXBMCo9UYYsFbXNrS1XpmgxoUUdBcN--NbydYPqjSGw';
const FOLDER_NAME = 'Cào web visa';

function loadAccessToken() {
  const raw = fs.readFileSync(tokenPath, 'utf8');
  const json = JSON.parse(raw);
  if (!json.token || !json.token.access_token) {
    throw new Error('Missing access_token in token file');
  }
  return json.token.access_token;
}

async function gfetch(url, options = {}) {
  const accessToken = loadAccessToken();
  const res = await fetch(url, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    throw new Error(`Drive API error (${res.status}): ${JSON.stringify(data)}`);
  }
  return data;
}

async function createFolder() {
  return gfetch('https://www.googleapis.com/drive/v3/files', {
    method: 'POST',
    body: JSON.stringify({
      name: FOLDER_NAME,
      mimeType: 'application/vnd.google-apps.folder',
    }),
  });
}

async function getFileParents(fileId) {
  return gfetch(`https://www.googleapis.com/drive/v3/files/${fileId}?fields=id,name,parents`);
}

async function moveFile(fileId, newParentId, existingParents = []) {
  const params = new URLSearchParams({
    addParents: newParentId,
    removeParents: existingParents.join(','),
    fields: 'id,name,parents',
  });

  return gfetch(`https://www.googleapis.com/drive/v3/files/${fileId}?${params.toString()}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  });
}

async function main() {
  const folder = await createFolder();
  const file = await getFileParents(SHEET_ID);
  const existingParents = file.parents || [];
  const moved = await moveFile(SHEET_ID, folder.id, existingParents);

  console.log(JSON.stringify({
    createdFolder: folder,
    originalFile: file,
    movedFile: moved,
  }, null, 2));
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
