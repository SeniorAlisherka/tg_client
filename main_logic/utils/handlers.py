import sys
import json
import qrcode

_THIS_MODULE = sys.modules[__name__]


def on_authorizationStateClosed(client, event):
    print("🛑 TDLib closed cleanly.")
    client.closed.set()


def on_updateAuthorizationState(client, event):
    state = event["authorization_state"]["@type"]
    handler = getattr(_THIS_MODULE, f"on_{state}", None)
    if handler:
        handler(client, event)
    else:
        print(f"Unhandled auth state: {json.dumps(event, indent=2)}")


def on_authorizationStateWaitTdlibParameters(client, event):
    client.send(
        {
            "@type": "setTdlibParameters",
            "database_directory": "./logs/tdlib_data",
            "files_directory": "./logs/tdlib_files",
            "api_id": client.api_id,
            "api_hash": client.api_hash,
            "system_language_code": "en",
            "device_model": "Desktop",
            "application_version": "1.0",
        }
    )


def on_authorizationStateWaitPhoneNumber(client, event):
    # Start QR authentication instead of phone auth
    client.send(
        {
            "@type": "requestQrCodeAuthentication",
            "other_user_ids": [],
        }
    )


def on_authorizationStateWaitOtherDeviceConfirmation(client, event):

    link = event["authorization_state"]["link"]

    print("\nScan this QR code in Telegram Desktop or Mobile:\n")

    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make()
    qr.print_ascii()


def on_authorizationStateWaitPassword(client, event):
    hint = event["authorization_state"].get("password_hint", "")
    if hint:
        print(f"Password hint: {hint}")

    password = input("Enter Telegram password: ")

    client.send(
        {
            "@type": "checkAuthenticationPassword",
            "password": password,
        }
    )


def on_authorizationStateClosing(client, event):
    print("🛑 TDLib is closing...")


def on_authorizationStateLoggingOut(client, event):
    print("🛑 Logging out...")


def on_authorizationStateReady(client, event):
    print("✅ Authorized")
    client.authorized.set()


def on_user(client, event):
    if event.get("@extra") == "_menu_main":
        print(
            f"\n👤 Logged in as {event['first_name']} " f"{event.get('last_name', '')}"
        )
        client.got_response.set()


def on_error(client, event):
    code = event.get("code")
    message = event.get("message")

    handler = getattr(_THIS_MODULE, f"on_{message}", None)
    if handler:
        handler(client, event)
    else:
        print(f"Unhandled TDLib error: {event}")


def on_chats(client, event):
    extra = event.get("@extra")

    if extra:
        handler = getattr(
            _THIS_MODULE,
            f"on_chats_{extra}",
            None,
        )
        if handler:
            handler(client, event)


def on_chats__menu_main_2(client, event):
    client.channels = []
    client.pending_channels = len(event["chat_ids"])

    for chat_id in event["chat_ids"]:
        client.send({"@type": "getChat", "chat_id": chat_id, "@extra": "_menu_main_2"})


def on_chat(client, event):
    extra = event.get("@extra")

    if extra:
        handler = getattr(
            _THIS_MODULE,
            f"on_chat_{extra}",
            None,
        )
        if handler:
            handler(client, event)


def on_chat__menu_main_2(client, event):
    chat_type = event.get("type", {})
    if (
        chat_type.get("@type") == "chatTypeSupergroup"
        and chat_type.get("is_channel") is True
    ):
        client.channels.append(event)

    client.pending_channels -= 1

    if client.pending_channels == 0:
        client.got_response.set()


# example error handler
def on_PHONE_NUMBER_INVALID(client, event):
    print("Phone number is invalid. Please try again.")
