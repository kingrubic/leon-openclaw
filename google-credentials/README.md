# Google credentials

## kenyaimmigration-org

OAuth client credentials saved at:

- `google-credentials/kenyaimmigration-org.oauth-client.json`

Security notes:
- Contains a Google OAuth `client_secret`
- Do not commit this file to public repositories
- Prefer referencing via environment variables or local secret mounts

Common environment variables:

```env
GOOGLE_CLIENT_ID=317047000223-3g4va9qp9dcsc623svqlpkr4tdha00cl.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
GOOGLE_PROJECT_ID=kenyaimmigration-org
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_CERTS_URL=https://www.googleapis.com/oauth2/v1/certs
```

## Local OAuth callback helper

Created helper script:

- `google-oauth-callback.js`

Usage:

```bash
node google-oauth-callback.js
```

Before running, ensure the OAuth client in Google Cloud has this exact redirect URI:

```text
http://localhost:3000/oauth/callback
```

When the script starts, it prints a Google OAuth URL. Open it in the browser, sign in, and approve access.

On success, tokens will be saved to:

- `google-credentials/kenyaimmigration-org.tokens.json`

That token file is sensitive and should not be committed.
