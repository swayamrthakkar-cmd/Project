import asyncio

import flet as ft
import httpx

API_BASE = "https://swayamthakkar.pythonanywhere.com/api"
POLL_SECONDS = 2
REQUEST_TIMEOUT = 12.0


async def main(page: ft.Page):
    page.title = "SwayChat"

    # Window sizing is useful on desktop; iOS will use its normal screen size.
    try:
        page.window.width = 700
        page.window.height = 780
    except (AttributeError, TypeError):
        pass

    client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)

    app_state = {
        "closed": False,
        "chat_open": False,
        "session_token": None,
        "chat_generation": 0,
    }

    def set_status(control, message, color=None):
        control.value = message
        if color is not None:
            control.color = color
        page.update()

    username = ft.TextField(
        label="Username",
        autofocus=True,
        max_length=20,
        autocorrect=False,
        capitalization=ft.TextCapitalization.NONE,
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        max_length=128,
    )

    auth_status = ft.Text()

    async def return_to_login(message="Session expired. Please log in again."):
        """Invalidate the current local session and show the login screen."""
        app_state["chat_open"] = False
        app_state["session_token"] = None
        password.value = ""
        set_status(auth_status, message, ft.Colors.RED)
        show_login()

    async def auth(endpoint: str):
        auth_status.value = ""

        name = (username.value or "").strip()
        pw = password.value or ""

        if not (3 <= len(name) <= 20):
            set_status(
                auth_status,
                "Username must be 3-20 characters.",
                ft.Colors.RED,
            )
            return

        if not (6 <= len(pw) <= 128):
            set_status(
                auth_status,
                "Password must be 6-128 characters.",
                ft.Colors.RED,
            )
            return

        login_button.disabled = True
        register_button.disabled = True
        auth_status.value = "Connecting..."
        auth_status.color = ft.Colors.BLUE
        page.update()

        try:
            response = await client.post(
                f"{API_BASE}/{endpoint}",
                json={"username": name, "password": pw},
            )

            try:
                data = response.json()
            except ValueError:
                data = {}

            # Accept any successful 2xx response, not just HTTP 200.
            if not 200 <= response.status_code < 300:
                detail = data.get(
                    "detail",
                    f"Server returned HTTP {response.status_code}.",
                )
                set_status(auth_status, str(detail), ft.Colors.RED)
                return

            session_token = data.get("token")
            if not session_token:
                set_status(
                    auth_status,
                    "Server response did not contain a session token.",
                    ft.Colors.RED,
                )
                return

            app_state["session_token"] = session_token
            await show_chat(session_token, name)

        except httpx.TimeoutException:
            set_status(
                auth_status,
                "The server took too long to respond. Try again.",
                ft.Colors.RED,
            )
        except httpx.HTTPError:
            set_status(
                auth_status,
                "Could not reach the server. Check your connection and try again.",
                ft.Colors.RED,
            )
        finally:
            login_button.disabled = False
            register_button.disabled = False
            page.update()

    async def do_login(e):
        await auth("login")

    async def do_register(e):
        await auth("register")

    login_button = ft.Button("Log in", on_click=do_login)
    register_button = ft.TextButton("Create account", on_click=do_register)

    def show_login():
        app_state["chat_open"] = False
        page.clean()
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "SwayChat",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text("Sign in or create an account"),
                        username,
                        password,
                        ft.Row(
                            [login_button, register_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        auth_status,
                    ],
                    spacing=16,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    width=380,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        )
        page.update()

    async def show_chat(token: str, me: str):
        app_state["chat_generation"] += 1
        generation = app_state["chat_generation"]
        app_state["chat_open"] = True

        messages_view = ft.ListView(
            expand=True,
            spacing=8,
            auto_scroll=True,
        )
        message_box = ft.TextField(
            hint_text="Type a message...",
            expand=True,
            shift_enter=True,
            multiline=False,
        )
        chat_status = ft.Text(size=12)
        headers = {"Authorization": f"Bearer {token}"}

        state = {
            "last_id": 0,
            "active": True,
        }
        poll_lock = asyncio.Lock()

        def is_current_chat():
            return (
                state["active"]
                and app_state["chat_open"]
                and app_state["chat_generation"] == generation
                and not app_state["closed"]
            )

        def make_message(item):
            author = item.get("user", "Unknown")
            body = item.get("text", "")
            return ft.Container(
                content=ft.Text(
                    f'{"You" if author == me else author}: {body}',
                    weight=(
                        ft.FontWeight.BOLD
                        if author == me
                        else ft.FontWeight.NORMAL
                    ),
                    selectable=True,
                ),
                padding=8,
                border_radius=8,
            )

        async def fetch_new():
            async with poll_lock:
                if not is_current_chat():
                    return

                try:
                    response = await client.get(
                        f"{API_BASE}/messages",
                        params={"after": state["last_id"]},
                        headers=headers,
                    )
                except (httpx.HTTPError, ValueError):
                    # Keep polling; a temporary network issue should not crash the app.
                    return

                if not is_current_chat():
                    return

                if response.status_code == 401:
                    state["active"] = False
                    await return_to_login()
                    return

                if response.status_code != 200:
                    return

                try:
                    new_messages = response.json()
                except ValueError:
                    return

                if not isinstance(new_messages, list):
                    return

                changed = False
                for item in new_messages:
                    if not isinstance(item, dict):
                        continue
                    try:
                        message_id = int(item.get("id", 0))
                    except (TypeError, ValueError):
                        continue

                    if message_id <= state["last_id"]:
                        continue

                    messages_view.controls.append(make_message(item))
                    state["last_id"] = message_id
                    changed = True

                if changed and is_current_chat():
                    page.update()

        async def poll():
            while is_current_chat():
                await fetch_new()
                if is_current_chat():
                    await asyncio.sleep(POLL_SECONDS)

        async def send_message(e):
            if not is_current_chat():
                return

            body = (message_box.value or "").strip()
            if not body:
                return

            message_box.disabled = True
            page.update()

            try:
                response = await client.post(
                    f"{API_BASE}/send",
                    json={"text": body},
                    headers=headers,
                )

                if response.status_code == 401:
                    state["active"] = False
                    await return_to_login()
                    return

                if not 200 <= response.status_code < 300:
                    try:
                        detail = response.json().get(
                            "detail",
                            "Message failed to send.",
                        )
                    except (ValueError, AttributeError):
                        detail = "Message failed to send."

                    chat_status.value = str(detail)
                    chat_status.color = ft.Colors.RED
                    return

                message_box.value = ""
                chat_status.value = ""
                # Fetch immediately so the sent message appears without waiting
                # for the next polling interval.
                await fetch_new()

            except httpx.TimeoutException:
                chat_status.value = "The server took too long to respond. Try again."
                chat_status.color = ft.Colors.RED
            except httpx.HTTPError:
                chat_status.value = "Network error: message was not sent."
                chat_status.color = ft.Colors.RED
            finally:
                # Do not update controls from an old chat screen after logout.
                if is_current_chat():
                    message_box.disabled = False
                    page.update()

        async def logout(e):
            if not is_current_chat():
                return

            state["active"] = False
            app_state["chat_open"] = False
            app_state["session_token"] = None
            password.value = ""

            try:
                await client.post(
                    f"{API_BASE}/logout",
                    headers=headers,
                )
            except httpx.HTTPError:
                # Local logout still succeeds if the server cannot be reached.
                pass

            show_login()

        message_box.on_submit = send_message

        page.clean()
        page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                f"SwayChat — signed in as {me}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.TextButton("Log out", on_click=logout),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    messages_view,
                    chat_status,
                    ft.Row(
                        [
                            message_box,
                            ft.IconButton(
                                icon=ft.Icons.SEND,
                                tooltip="Send message",
                                on_click=send_message,
                            ),
                        ]
                    ),
                ],
                expand=True,
                spacing=10,
            )
        )
        page.update()

        # Load the latest messages before starting background polling.
        await fetch_new()

        if is_current_chat():
            messages_view.auto_scroll = True
            page.update()
            page.run_task(poll)

    def on_disconnect(e):
        app_state["closed"] = True
        app_state["chat_open"] = False
        app_state["session_token"] = None

    page.on_disconnect = on_disconnect
    show_login()

    try:
        # Keep the app alive until Flet cancels the main task.
        await asyncio.Event().wait()
    finally:
        app_state["closed"] = True
        app_state["chat_open"] = False
        app_state["session_token"] = None
        await client.aclose()


ft.run(main)
