import qrcode


def helper_dispatch_extra(client, event, extras_dict):
    extra = event.get("@extra")
    handler = extras_dict.get(extra)

    if handler:
        handler(client, event)
    else:
        print("\nUnhandled extra:", extra)
        client.menu_event.set()


def helper_auth_closed(client, event):
    print("\n🛑 TDLib closed cleanly.")
    client.closed.set()


def helper_auth_wait_params(client, event):
    client.send(
        {
            "@type": "setTdlibParameters",
            "database_directory": "./logs/tdlib_data",
            "api_id": client.api_id,
            "api_hash": client.api_hash,
            "system_language_code": "en",
            "device_model": "Desktop",
            "application_version": "1.0",
        }
    )


def helper_auth_wait_phone(client, event):
    client.send(
        {
            "@type": "requestQrCodeAuthentication",
            "other_user_ids": [],
        }
    )


def helper_auth_wait_qr(client, event):
    link = event["authorization_state"]["link"]
    print("\nScan this QR code:\n")

    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make()
    qr.print_ascii()


def helper_auth_wait_password(client, event):
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


def helper_auth_ready(client, event):
    print("\n✅ Authorized")
    client.authorized.set()
    client.auth_done.set()


def helper_auth_closing(client, event):
    print("\n🛑 TDLib is closing...")


def helper_auth_logging_out(client, event):
    print("\n🛑 Logging out...")


def helper_error_invalid_password(client, event):
    print("\n❌ Incorrect password. Please try again.")
    client.send({"@type": "getAuthorizationState"})


def helper_error_rate_limit(client, event):
    print(f"\n⏳{event['message']} seconds")
    client.auth_done.set()
    client.send({"@type": "close"})


def helper_send_next_member_search(client, state):
    if state["index"] == len(state["names"]):
        missing = state["missing"]

        if not missing:
            print("\nNo missing members.")
        else:
            print("\nMissing members:")
            for name in missing:
                print(name)
            print(f"\nTotal missing: {len(missing)}")

        client.menu_event.set()
        return

    name = state["names"][state["index"]]
    client.send(
        {
            "@type": "getSupergroupMembers",
            "supergroup_id": state["supergroup_id"],
            "filter": {
                "@type": "supergroupMembersFilterContacts",
                "query": name,
            },
            "offset": 0,
            "limit": 1,
            "@extra": "button_channel_3",
        }
    )
