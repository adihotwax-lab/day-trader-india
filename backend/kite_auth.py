"""Kite Connect login and callback service.

Secrets and access tokens are read from environment variables and never returned
by HTTP endpoints. This service intentionally exposes no order-placement routes.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from kiteconnect import KiteConnect

APP_TITLE = "India Paper Trader - Kite Auth"
app = FastAPI(title=APP_TITLE, docs_url=None, redoc_url=None)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _db_path() -> Path:
    path = Path(os.getenv("TOKEN_DB_PATH", "./data/kite_session.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    try:
        os.chmod(_db_path(), 0o600)
    except OSError:
        pass
    conn.execute("CREATE TABLE IF NOT EXISTS kite_session (id INTEGER PRIMARY KEY CHECK (id = 1), access_token TEXT NOT NULL, user_id TEXT, login_time TEXT)")
    conn.commit()
    return conn


def _kite() -> KiteConnect:
    return KiteConnect(api_key=_required_env("KITE_API_KEY"))


def _store_session(data: dict[str, Any]) -> None:
    conn = _connect_db()
    try:
        conn.execute(
            "INSERT INTO kite_session (id, access_token, user_id, login_time) VALUES (1, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET access_token=excluded.access_token, user_id=excluded.user_id, login_time=excluded.login_time",
            (data["access_token"], data.get("user_id"), data.get("login_time")),
        )
        conn.commit()
    finally:
        conn.close()


def _session_exists() -> bool:
    conn = _connect_db()
    try:
        return conn.execute("SELECT 1 FROM kite_session WHERE id=1").fetchone() is not None
    finally:
        conn.close()


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "service": "kite-auth", "paper_mode": True, "live_orders_enabled": False}


@app.get("/kite/login")
def login() -> RedirectResponse:
    """Send the user to Zerodha's official Kite login page."""
    try:
        login_url = _kite().login_url()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Kite login is not configured") from exc
    return RedirectResponse(login_url, status_code=302)


@app.get("/kite/callback", response_class=HTMLResponse)
def callback(
    request_token: str | None = Query(default=None),
    status: str | None = Query(default=None),
    action: str | None = Query(default=None),
) -> HTMLResponse:
    """Exchange the short-lived request token and store the access token server-side."""
    if status != "success" or action not in (None, "login") or not request_token:
        raise HTTPException(status_code=400, detail="Kite login was not completed. Start again at /kite/login.")
    try:
        kite = _kite()
        session = kite.generate_session(request_token, api_secret=_required_env("KITE_API_SECRET"))
        _store_session(session)
    except Exception as exc:
        # Never include request_token, API secret, access token, or provider response in the page/log.
        raise HTTPException(status_code=400, detail="Kite authentication failed. Start a fresh login and try again.") from exc
    return HTMLResponse("""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'></head><body><h2>Kite login successful</h2><p>Your session is stored securely on the backend. You can close this page.</p></body></html>""")


@app.get("/kite/session-status")
def session_status() -> dict[str, bool | str]:
    """Expose only whether a token exists; never return the token itself."""
    return {"authenticated": _session_exists(), "paper_mode": True}
