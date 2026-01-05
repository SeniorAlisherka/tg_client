import sys
import json
import qrcode

_THIS_MODULE = sys.modules[__name__]


def extra_dispatcher(prefix, client, event):
    """
    Dispatch event based on its @extra field.
    If no extra field returns false else true
    (even if extra is not handled properly).
    """
    extra = event.get("@extra")
    if not extra:
        return False

    func_name = f"{prefix}_{extra}"
    extra_handler = globals().get(func_name)

    if extra_handler:
        extra_handler(client, event)
        return True

    print("\nUnhandled extra:", extra)
    client.menu_event.set()
    return True


def on_updateAuthorizationState(client, event):
    state = event["authorization_state"]["@type"]
    state_handler = getattr(_THIS_MODULE, f"on_state_{state}", None)
    if state_handler:
        state_handler(client, event)
    else:
        print(f"\nUnhandled auth state: {json.dumps(event, indent=2)}")


def on_state_authorizationStateClosed(client, event):
    print("\n🛑 TDLib closed cleanly.")
    client.closed.set()


def on_state_authorizationStateWaitTdlibParameters(client, event):
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


def on_state_authorizationStateWaitPhoneNumber(client, event):
    # Start QR authentication instead of phone auth
    client.send(
        {
            "@type": "requestQrCodeAuthentication",
            "other_user_ids": [],
        }
    )


def on_state_authorizationStateWaitOtherDeviceConfirmation(client, event):

    link = event["authorization_state"]["link"]

    print("\nScan this QR code in Telegram Desktop or Mobile:\n")

    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make()
    qr.print_ascii()


def on_state_authorizationStateWaitPassword(client, event):
    hint = event["authorization_state"].get("password_hint", "")
    if hint:
        print(f"\nPassword hint: {hint}")

    password = input("\nEnter Telegram password: ")

    client.send(
        {
            "@type": "checkAuthenticationPassword",
            "password": password,
        }
    )


def on_state_authorizationStateClosing(client, event):
    print("\n🛑 TDLib is closing...")


def on_state_authorizationStateLoggingOut(client, event):
    print("\n🛑 Logging out...")


def on_state_authorizationStateReady(client, event):
    print("\n✅ Authorized")
    client.authorized.set()
    client.auth_done.set()


def on_user(client, event):
    if not extra_dispatcher("on_user", client, event):
        pass


def on_user_menu_main_1(client, event):
    print(f"\n👤 Logged in as {event['first_name']} " f"{event.get('last_name', '')}")
    client.menu_event.set()


def on_error(client, event):
    code = event.get("code")
    message = event.get("message")

    # Try code-based handler first
    error_handler = getattr(_THIS_MODULE, f"on_error_{code}", None)

    # Fallback to message-based handler
    if not error_handler:
        error_handler = getattr(_THIS_MODULE, f"on_error_{message}", None)

    if error_handler:
        error_handler(client, event)
    else:
        client.menu_event.set()
        print(f"\nUnhandled TDLib error: {event}")


def on_error_PASSWORD_HASH_INVALID(client, event):
    print("\n❌ Incorrect password. Please try again.")
    client.send({"@type": "getAuthorizationState"})


def on_error_429(client, event):
    message = event.get("message", "")
    print(f"\n⏳{message} seconds")

    client.auth_done.set()  # unblock run()
    # always auth_done.set() if you send closing before auth is finished
    client.send({"@type": "close"})


def on_authorizationStateWaitPassword(client, event):
    hint = event.get("password_hint", "")
    if hint:
        print(f"\nPassword hint: {hint}")

    password = input("\nEnter Telegram password: ")

    client.send(
        {
            "@type": "checkAuthenticationPassword",
            "password": password,
        }
    )


def on_chats(client, event):
    if not extra_dispatcher("on_chats", client, event):
        pass


def on_chats_menu_main_2(client, event):
    client.state["channels"] = []
    client.state["pending"] = len(event["chat_ids"])

    for chat_id in event["chat_ids"]:
        client.send(
            {
                "@type": "getChat",
                "chat_id": chat_id,
                "@extra": "menu_main_2",
            }
        )


def on_chat(client, event):
    if not extra_dispatcher("on_chat", client, event):
        pass


def on_chat_menu_main_2(client, event):
    chat_type = event.get("type", {})

    if chat_type.get("@type") == "chatTypeSupergroup" and chat_type.get("is_channel"):
        client.state["channels"].append(event)

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.menu = "menu_channels"
        client.menu_event.set()
