# src/static_instances/helpers.py
import os
import qrcode
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from src.utils.paths import app_root_dir, app_support_dir
from getpass import getpass


def fetch_google_sheet_names(chat_id):

    service_account_json = app_root_dir() / os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.getenv("GOOGLE_USERS_SPREADSHEET_ID")
    sheet_range = os.getenv("GOOGLE_USERS_SHEET_RANGE")

    creds = Credentials.from_service_account_file(
        service_account_json,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    response = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_range)
        .execute()
    )

    values = response.get("values", [])
    names = []
    filter_id = chat_id

    for row in values:
        if len(row) != 2:
            print("Skipping invalid row in Google Sheet:", row)
            continue
        row_name = row[0].strip()
        row_chat_id = row[1].strip()
        if row_name in ("", "#N/A") or row_chat_id in ("", "#N/A"):
            print("Skipping invalid row in Google Sheet:", row)
            continue

        if str(row_chat_id) != str(filter_id):
            continue

        names.append(row_name)

    return names


def auth_closed(client, event):
    print("\n🛑 TDLib closed cleanly.")
    client.auth_done.set()
    client.closed.set()


def auth_wait_params(client, event):
    tdlib_data_dir = app_support_dir("TG Client") / "tdlib_data"
    client.send(
        {
            "@type": "setTdlibParameters",
            "database_directory": str(tdlib_data_dir),
            "api_id": client.api_id,
            "api_hash": client.api_hash,
            "system_language_code": "en",
            "device_model": "Desktop",
            "application_version": "1.0",
        }
    )


def auth_wait_phone(client, event):
    client.send(
        {
            "@type": "requestQrCodeAuthentication",
            "other_user_ids": [],
        }
    )


def auth_wait_qr(client, event):
    link = event["authorization_state"]["link"]
    print("\nScan this QR code:\n")

    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make()
    qr.print_ascii(tty=True)


def auth_wait_password(client, event):
    hint = event["authorization_state"].get("password_hint", "")
    if hint:
        print(f"\nPassword hint: {hint}")

    password = getpass("\nEnter Telegram password: ")
    client.send(
        {
            "@type": "checkAuthenticationPassword",
            "password": password,
        }
    )


def auth_ready(client, event):
    print("\n✅ Authorized")
    client.authorized.set()
    client.auth_done.set()


def auth_closing(client, event):
    print("\n🛑 TDLib is closing...")


def auth_logging_out(client, event):
    print("\n🛑 Logging out...")


def error_invalid_password(client, event):
    print("\n❌ Incorrect password. Please try again.")
    client.send({"@type": "getAuthorizationState"})


def error_rate_limit(client, event):
    print(f"\n⏳{event['message']} seconds")
    client.auth_done.set()
    client.send({"@type": "close"})


def error_request_aborted(client, event):
    print(f"\n⏳Request aborted")
    client.auth_done.set()
    client.send({"@type": "close"})


def error_auth_key_unregistered(client, event):
    print("\n❌ You did not complete the authorization.")
    client.auth_done.set()


def unhandled_authorization_state(client, event):
    print("\nUnhandled authorization state:", event)
    client.auth_done.set()
    client.send({"@type": "close"})


def unhandled_error(client, event):
    print("\nUnhandled TDLib error:", event)
    client.auth_done.set()
    client.send({"@type": "close"})


def send_next_member_search(client, state):

    if state["index"] == len(state["names"]):

        missing = state["missing"]

        if not missing:
            print("\nNo missing members.")
        else:
            print("\nMissing members:")
            for name in missing:
                print(name)
            print(f"\nTotal missing: {len(missing)}")
        client.stop_cancel_listener()
        client.ask_for_enter()  # to unblock the waiting cancel listener
        # no need to set menu_event, when cancel_listener stops, menu_event is set
        return

    name = state["names"][state["index"]]
    client.send(
        {
            "@type": "searchChatMembers",
            "chat_id": state["chat_id"],
            "filter": {"@type": "chatMembersFilterContacts"},
            "query": name,
            "limit": 1,
            "@extra": {
                "@type": "channel_2",
                "task_id": client.current_task_id,
            },
            # everywhere along the task use current_task_id to avoid stale responses too
        }
    )


def load_google_users():
    creds = Credentials.from_service_account_file(
        app_root_dir() / os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    service = build("sheets", "v4", credentials=creds)

    sheet = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=os.environ["GOOGLE_USERS_SPREADSHEET_ID"],
            range=os.environ["GOOGLE_USERS_SHEET_RANGE"],
        )
        .execute()
    )

    return sheet.get("values", [])


def update_google_sheet_usernames(contacts_data):
    if not contacts_data:
        print("\nNo contacts_data with usernames to sync.")
        return

    sheet_rows = load_google_users()
    if not sheet_rows:
        print("\nNo values found in Google Sheet.")
        return

    spreadsheet_id = os.getenv("GOOGLE_USERS_SPREADSHEET_ID")
    sheet_range = os.getenv("GOOGLE_USERS_SHEET_RANGE")
    sheet_name = sheet_range.split("!")[0]

    updates = []

    for idx, row in enumerate(sheet_rows, start=1):
        if idx == 1 or len(row) < 1:
            continue

        sheet_name_value = row[0].strip()

        for contact in contacts_data:
            contact_name = contact["first_name"]
            username = contact["username"]

            if sheet_name_value == contact_name:
                updates.append(
                    {
                        "range": f"{sheet_name}!E{idx}",
                        "values": [[username]],
                    }
                )
                break

    if not updates:
        print("No matches found.")
        return

    creds = Credentials.from_service_account_file(
        app_root_dir() / os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds)

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "RAW",
            "data": updates,
        },
    ).execute()

    print(f"Updated {len(updates)} usernames.")


def build_sheet_lookup(rows):
    lookup = set()

    for row in rows:
        if len(row) < 2:
            continue

        name = row[0].strip()
        chat_id = row[1].strip()

        lookup.add((name, chat_id))

    return lookup


def set_present_in_channel_for_chat(current_chat_id, missing_students):
    """Marks non-missing students as present_in_channel=true in the Google Sheet."""
    sheet_rows = load_google_users()
    if not sheet_rows:
        print("No values found in Google Sheet for updating present_in_channel.")
        return

    spreadsheet_id = os.getenv("GOOGLE_USERS_SPREADSHEET_ID")
    sheet_range = os.getenv("GOOGLE_USERS_SHEET_RANGE")
    if not spreadsheet_id or not sheet_range:
        print(
            "Missing Google Sheets env vars for update: GOOGLE_USERS_SPREADSHEET_ID or GOOGLE_USERS_SHEET_RANGE"
        )
        return

    sheet_name = sheet_range.split("!")[0]

    updates = []

    for idx, row in enumerate(sheet_rows, start=1):
        if idx == 1:
            continue  # skip header row

        if len(row) < 2:
            continue

        row_chat_id = row[1].strip()
        if str(row_chat_id) != str(current_chat_id):
            continue

        row_name = row[0].strip()
        if not row_name or row_name in missing_students:
            continue

        updates.append(
            {
                "range": f"{sheet_name}!D{idx}",
                "majorDimension": "ROWS",
                "values": [["true"]],
            }
        )

    if not updates:
        # print("No non-missing students to mark present_in_channel for this chat.")
        return

    creds = Credentials.from_service_account_file(
        app_root_dir() / os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    service = build("sheets", "v4", credentials=creds)

    body = {
        "valueInputOption": "RAW",
        "data": updates,
    }

    response = (
        service.spreadsheets()
        .values()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
    )

    # print(f"Updated present_in_channel for {len(updates)} rows in Google Sheet.")
