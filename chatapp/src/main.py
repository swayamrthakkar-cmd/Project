import json

import flet as ft
import httpx
import websockets

SERVER = "127.0.0.1:8000"  # on a phone, use your PC's LAN IP, e.g. 192.168.1.20:8000
HTTP = f"http://{SERVER}"
WS = f"ws://{SERVER}"


async def main(page: ft.Page):
    page.title = "Chat"

    # ---------- login screen ----------
    username = ft.TextField(label="Username", autofocus=True)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    status = ft.Text(color=ft.Colors.RED)

    async def auth(endpoint: str):
        status.value = ""
        name = (username.value or "").strip()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    f"{HTTP}/{endpoint}",
                    json={"username": name, "password": password.value or ""},
                )
        except httpx.HTTPError:
            status.value = "Can't reach the server"
            page.update()
            return
        if r.status_code != 200:
            detail = r.json().get("detail", "Something went wrong")
            status.value = detail if isinstance(detail, str) else "Check username (3-20 letters/numbers) and password (6+ chars)"
            page.update()
            return
        show_chat(r.json()["token"], name)

    async def do_login(e):
        await auth("login")

    async def do_register(e):
        await auth("register")

    def show_login():
        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Text("Welcome", size=28, weight=ft.FontWeight.BOLD),
                    username,
                    password,
                    ft.Row([ft.Button("Log in", on_click=do_login),
                            ft.TextButton("Create account", on_click=do_register)]),
                    status,
                ],
                spacing=15,
            )
        )

    # ---------- chat screen ----------
    def show_chat(token: str, me: str):
        page.clean()
        messages = ft.ListView(expand=True, spacing=8, auto_scroll=True)
        box = ft.TextField(hint_text="Type a message...", expand=True)
        conn = {}

        async def listen():
            try:
                async with websockets.connect(f"{WS}/ws?token={token}") as ws:
                    conn["ws"] = ws
                    async for raw in ws:
                        m = json.loads(raw)
                        mine = m["user"] == me
                        messages.controls.append(
                            ft.Text(
                                f'{"You" if mine else m["user"]}: {m["text"]}',
                                weight=ft.FontWeight.BOLD if mine else None,
                            )
                        )
                        page.update()
            except Exception:
                pass
            conn.pop("ws", None)
            messages.controls.append(ft.Text("Disconnected", italic=True))
            page.update()

        async def send(e):
            text = (box.value or "").strip()
            ws = conn.get("ws")
            if not text or ws is None:
                return
            await ws.send(json.dumps({"text": text}))
            box.value = ""
            page.update()

        box.on_submit = send
        page.add(messages, ft.Row([box, ft.IconButton(icon=ft.Icons.SEND, on_click=send)]))
        page.run_task(listen)

    show_login()


ft.run(main)