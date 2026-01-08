from src.static_instances import helpers


def updateAuthorizationState(client, event):
    state = event["authorization_state"]["@type"]

    if state == "authorizationStateClosed":
        helpers.auth_closed(client, event)

    elif state == "authorizationStateWaitTdlibParameters":
        helpers.auth_wait_params(client, event)

    elif state == "authorizationStateWaitPhoneNumber":
        helpers.auth_wait_phone(client, event)

    elif state == "authorizationStateWaitOtherDeviceConfirmation":
        helpers.auth_wait_qr(client, event)

    elif state == "authorizationStateWaitPassword":
        helpers.auth_wait_password(client, event)

    elif state == "authorizationStateReady":
        helpers.auth_ready(client, event)

    elif state == "authorizationStateClosing":
        helpers.auth_closing(client, event)

    elif state == "authorizationStateLoggingOut":
        helpers.auth_logging_out(client, event)

    else:
        helpers.unhandled_authorization_state(client, event)


def authorizationStateWaitPassword(client, event):
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


def error(client, event):
    code = event["code"]
    message = event["message"]

    if code == 429:
        helpers.error_rate_limit(client, event)

    elif message == "PASSWORD_HASH_INVALID":
        helpers.error_invalid_password(client, event)

    elif message == "Request aborted":
        helpers.error_request_aborted(client, event)

    else:
        helpers.unhandled_error(client, event)


def user(client, event):
    pass


def chats(client, event):
    pass


def chat(client, event):
    pass


def supergroup(client, event):
    pass


def supergroupFullInfo(client, event):
    pass


def chatMembers(client, event):
    pass
