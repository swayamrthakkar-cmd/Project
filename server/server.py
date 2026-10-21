import hashlib
import hmac
import secrets
import sqlite3
import time
from contextlib import closing

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel, Field

DB = "chat.db"
app = FastAPI()


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


with closing(db()) as c:
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
        salt BLOB NOT NULL, pw_hash BLOB NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(
        token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created REAL NOT NULL);
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY, username TEXT NOT NULL,
        text TEXT NOT NULL, ts REAL NOT NULL);
    """)
    c.commit()


class Creds(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    password: str = Field(min_length=6, max_length=128)


def hash_pw(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)


def new_token(conn, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", (token, user_id, time.time()))
    conn.commit()
    return token


@app.post("/register")
def register(creds: Creds):
    salt = secrets.token_bytes(16)
    with closing(db()) as c:
        try:
            cur = c.execute(
                "INSERT INTO users(username, salt, pw_hash) VALUES (?, ?, ?)",
                (creds.username, salt, hash_pw(creds.password, salt)),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Username already taken")
        return {"token": new_token(c, cur.lastrowid)}


@app.post("/login")
def login(creds: Creds):
    with closing(db()) as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (creds.username,)).fetchone()
        if not row or not hmac.compare_digest(row["pw_hash"], hash_pw(creds.password, row["salt"])):
            raise HTTPException(401, "Wrong username or password")
        return {"token": new_token(c, row["id"])}


clients: set[WebSocket] = set()


async def broadcast(msg: dict):
    for ws in list(clients):
        try:
            await ws.send_json(msg)
        except Exception:
            clients.discard(ws)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = ""):
    with closing(db()) as c:
        row = c.execute(
            "SELECT u.username FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token=?",
            (token,),
        ).fetchone()
    if not row:
        await ws.close(code=1008)
        return
    user = row["username"]

    await ws.accept()
    clients.add(ws)
    try:
        with closing(db()) as c:
            history = c.execute(
                "SELECT username, text, ts FROM "
                "(SELECT * FROM messages ORDER BY id DESC LIMIT 50) ORDER BY id"
            ).fetchall()
        for m in history:
            await ws.send_json({"user": m["username"], "text": m["text"], "ts": m["ts"]})

        while True:
            data = await ws.receive_json()
            text = str(data.get("text", "")).strip()[:1000]
            if not text:
                continue
            msg = {"user": user, "text": text, "ts": time.time()}
            with closing(db()) as c:
                c.execute("INSERT INTO messages(username, text, ts) VALUES (?, ?, ?)",
                          (msg["user"], msg["text"], msg["ts"]))
                c.commit()
            await broadcast(msg)
    except Exception:
        pass
    finally:
        clients.discard(ws)