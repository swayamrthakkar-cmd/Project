import flet as ft

from swaychat_notifications import SwaychatNotifications


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(

                ft.Container(height=150, width=300, alignment = ft.Alignment.CENTER, bgcolor=ft.Colors.PURPLE_200, content=SwaychatNotifications(
                    tooltip="My new SwaychatNotifications Control tooltip",
                    value = "My new SwaychatNotifications Flet Control",
                ),),

    )


ft.run(main)
