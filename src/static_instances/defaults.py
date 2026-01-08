from src.static_instances import helpers


def default_updateAuthorizationState(client, event):
    state = event["authorization_state"]["@type"]

    if state == "authorizationStateClosed":
        helpers.helper_auth_closed(client, event)

    elif state == "authorizationStateWaitTdlibParameters":
        helpers.helper_auth_wait_params(client, event)

    elif state == "authorizationStateWaitPhoneNumber":
        helpers.helper_auth_wait_phone(client, event)

    elif state == "authorizationStateWaitOtherDeviceConfirmation":
        helpers.helper_auth_wait_qr(client, event)

    elif state == "authorizationStateWaitPassword":
        helpers.helper_auth_wait_password(client, event)

    elif state == "authorizationStateReady":
        helpers.helper_auth_ready(client, event)

    elif state == "authorizationStateClosing":
        helpers.helper_auth_closing(client, event)

    elif state == "authorizationStateLoggingOut":
        helpers.helper_auth_logging_out(client, event)

    else:
        print("\nUnhandled authorization state:", event)


def default_authorizationStateWaitPassword(client, event):
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


def default_error(client, event):
    code = event["code"]
    message = event["message"]

    if code == 429:
        helpers.helper_error_rate_limit(client, event)

    elif message == "PASSWORD_HASH_INVALID":
        helpers.helper_error_invalid_password(client, event)

    else:
        print("\nUnhandled TDLib error:", event)
        client.menu_event.set()


def default_user(client, event):
    client.menu_event.set()


def default_chats(client, event):
    pass


def default_chat(client, event):
    pass


def default_supergroup(client, event):
    pass


def default_supergroupFullInfo(client, event):
    pass


def default_chatMembers(client, event):
    pass
