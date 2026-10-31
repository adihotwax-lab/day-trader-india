# Kite authentication backend

This FastAPI service completes the official Kite Connect login handshake. It stores the access token in a local SQLite database on the server and never returns the token from an HTTP endpoint. It has no order-placement routes.

## Environment variables

- `KITE_API_KEY`: Kite Connect app API key
- `KITE_API_SECRET`: Kite Connect app API secret (server-side only)
- `TOKEN_DB_PATH`: persistent SQLite file path; default `./data/kite_session.sqlite3`

Do not commit `.env`, credentials, or the SQLite database. Use your hosting provider's encrypted environment-variable settings and a persistent disk/volume for `TOKEN_DB_PATH`.

## Run locally

```bash
python -m pip install -r requirements-india.txt
uvicorn backend.kite_auth:app --host 127.0.0.1 --port 8000
```

Set the Kite Developer Console Redirect URL to the exact public HTTPS URL of this service followed by `/kite/callback`, for example `https://YOUR-HOST.example/kite/callback`. Do not use the example literally. Leave Postback URL blank because this project does not place orders.

Open `https://YOUR-HOST.example/kite/login` to start the official Zerodha login. After successful login, Zerodha redirects to `/kite/callback`; the server exchanges the short-lived request token and stores the access token. Check `/kite/health` and `/kite/session-status` (the latter reveals only whether a session exists).

Kite access tokens expire daily and must be regenerated through the normal login flow. Use a persistent private server; do not deploy this as a public static website or embed the API secret in an iPad/browser app.

## Deployment safety

Use HTTPS. Restrict access to the service to your own use at the hosting/network layer where possible. Keep the SQLite database on a private persistent volume with restrictive file permissions. Never enable order APIs or add order-placement endpoints to this service.

## Deploy on Railway

1. Create a Railway project and deploy this GitHub repository, selecting branch `india-nse-paper`.
2. Add a persistent Railway Volume mounted at `/data`.
3. Add service variables `TOKEN_DB_PATH=/data/kite_session.sqlite3`, `PAPER_MODE=true`, and `LIVE_ORDERS_ENABLED=false`.
4. After the first successful deployment, generate a Railway public HTTPS domain.
5. Set the Kite Developer Console Redirect URL to `https://YOUR-RAILWAY-DOMAIN/kite/callback` (replace with the exact generated domain).
6. Add `KITE_API_KEY` and `KITE_API_SECRET` as Railway service variables only. Never put them in GitHub files or chat.
7. Redeploy if needed, then visit `/health` and `/kite/login` on the generated domain.

Do not add `KITE_ACCESS_TOKEN` as a static variable: the backend stores the daily token in the persistent SQLite database after the official login callback.
