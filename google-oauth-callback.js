const http = require('http');
const { URL } = require('url');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const CALLBACK_PATH = '/oauth/callback';
const TOKEN_URL = 'https://oauth2.googleapis.com/token';

const credentialsPath = path.join(__dirname, 'google-credentials', 'kenyaimmigration-org.oauth-client.json');
const tokenOutPath = path.join(__dirname, 'google-credentials', 'kenyaimmigration-org.tokens.json');

function loadCredentials() {
  const raw = fs.readFileSync(credentialsPath, 'utf8');
  const json = JSON.parse(raw);
  if (!json.web) throw new Error('Expected OAuth client JSON with top-level "web" key');
  return json.web;
}

async function exchangeCodeForToken({ code, client_id, client_secret, redirect_uri }) {
  const body = new URLSearchParams({
    code,
    client_id,
    client_secret,
    redirect_uri,
    grant_type: 'authorization_code',
  });

  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  });

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error(`Token endpoint returned non-JSON response: ${text}`);
  }

  if (!res.ok) {
    throw new Error(`Token exchange failed (${res.status}): ${JSON.stringify(data)}`);
  }

  return data;
}

const server = http.createServer(async (req, res) => {
  try {
    const requestUrl = new URL(req.url, `http://localhost:${PORT}`);

    if (requestUrl.pathname !== CALLBACK_PATH) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Not found');
      return;
    }

    const error = requestUrl.searchParams.get('error');
    const code = requestUrl.searchParams.get('code');
    const scope = requestUrl.searchParams.get('scope');

    if (error) {
      res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(`OAuth error: ${error}`);
      console.error('OAuth error:', error);
      return;
    }

    if (!code) {
      res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Missing code');
      console.error('Missing code in callback URL');
      return;
    }

    const creds = loadCredentials();
    const redirect_uri = `http://localhost:${PORT}${CALLBACK_PATH}`;
    const tokenData = await exchangeCodeForToken({
      code,
      client_id: creds.client_id,
      client_secret: creds.client_secret,
      redirect_uri,
    });

    const payload = {
      created_at: new Date().toISOString(),
      scope,
      redirect_uri,
      token: tokenData,
    };

    fs.writeFileSync(tokenOutPath, JSON.stringify(payload, null, 2));

    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`
      <html>
        <body style="font-family: sans-serif; padding: 24px;">
          <h2>Google OAuth thành công</h2>
          <p>Token đã được lưu vào:</p>
          <pre>${tokenOutPath}</pre>
          <p>Anh có thể đóng tab này.</p>
        </body>
      </html>
    `);

    console.log('OAuth success. Token saved to:', tokenOutPath);
    console.log('Granted scope:', scope || '(not returned)');

    setTimeout(() => server.close(() => process.exit(0)), 500);
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`Internal error: ${err.message}`);
    console.error(err);
  }
});

server.listen(PORT, () => {
  const redirectUri = `http://localhost:${PORT}${CALLBACK_PATH}`;
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  const creds = loadCredentials();

  authUrl.searchParams.set('client_id', creds.client_id);
  authUrl.searchParams.set('redirect_uri', redirectUri);
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('scope', 'https://www.googleapis.com/auth/spreadsheets.readonly');
  authUrl.searchParams.set('access_type', 'offline');
  authUrl.searchParams.set('prompt', 'consent');

  console.log('Google OAuth callback server is running.');
  console.log('Authorized redirect URI must include:', redirectUri);
  console.log('Open this URL in your browser:');
  console.log(authUrl.toString());
});
