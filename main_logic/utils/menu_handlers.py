import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def choice_dispatcher(client, menu_name, choice):
    func_name = f"on_{menu_name}_{choice}"
    choice_handler = globals().get(func_name)

    if choice_handler:
        choice_handler(client)
        return

    if choice.isdigit():
        numeric_handler = globals().get(f"on_{menu_name}_index")
        if numeric_handler:
            numeric_handler(client, int(choice) - 1)
            return

    print("\nInvalid choice")
    client.menu_event.set()


def on_menu_main(client):
    print("\nMain menu:")
    print("1) Who am I?")
    print("2) Channels")
    print("q) Quit")

    choice = input("> ").strip().lower()
    choice_dispatcher(client, "menu_main", choice)


def on_menu_main_1(client):
    client.send(
        {
            "@type": "getMe",
            "@extra": "menu_main_1",
        }
    )


def on_menu_main_2(client):
    client.menu = "menu_channels"
    client.send(
        {
            "@type": "getChats",
            "limit": 100000,
            "@extra": "menu_main_2",
        }
    )


def on_menu_main_q(client):
    client.send({"@type": "close"})


def on_menu_channels(client):
    channels = client.state["channels"]

    print("\nChannels:")
    for i, ch in enumerate(channels, 1):
        print(f"{i}) {ch['title']}")
    print("b) Back")

    choice = input("> ").strip().lower()
    choice_dispatcher(client, "menu_channels", choice)


def on_menu_channels_b(client):
    client.menu = "menu_main"
    client.menu_event.set()


def on_menu_channels_index(client, index):
    channels = client.state["channels"]
    if 0 <= index < len(channels):
        client.state["current_channel"] = channels[index]
        client.menu = "menu_channel"
        client.menu_event.set()
        return

    print("\nInvalid choice")
    client.menu_event.set()


def on_menu_channel(client):
    channel = client.state["current_channel"]

    title = channel["title"]
    print(f"\nChannel: {title}")
    print("1) Member count")
    print("2) Channel ID")
    print("3) Check members list from sheet")
    print("b) Back")

    choice = input("> ").strip().lower()
    choice_dispatcher(client, "menu_channel", choice)


def on_menu_channel_1(client):
    channel = client.state["current_channel"]

    chat_type = channel["type"]
    supergroup_id = chat_type["supergroup_id"]

    client.send(
        {
            "@type": "getSupergroup",
            "supergroup_id": supergroup_id,
            "@extra": "menu_channel_1",
        }
    )


def on_menu_channel_2(client):
    channel = client.state["current_channel"]
    supergroup_id = channel["type"]["supergroup_id"]
    print(f"\nChannel ID: {channel['id']}")
    print(f"Supergroup ID: {supergroup_id}")
    client.menu_event.set()


def on_menu_channel_3(client):
    channel = client.state["current_channel"]
    supergroup_id = channel["type"]["supergroup_id"]

    try:
        rows = _load_sheet_rows()
    except Exception as exc:
        print(f"\nFailed to load Google Sheet: {exc}")
        client.menu_event.set()
        return

    if rows is None:
        print("\nGoogle sheet is empty.")
        client.menu_event.set()
        return

    target_id = str(supergroup_id)
    names = []
    for row in rows:
        if len(row) < 2:
            print("\n Check the Google Sheet for incomplete rows.")
            continue
        full_name = str(row[0]).strip()
        row_id = str(row[1]).strip()
        if row_id == target_id and full_name:
            names.append(full_name)
    if not names:
        print("\nNo matching students for this channel.")
        client.menu_event.set()
        return

    client.state["member_search"] = {
        "supergroup_id": supergroup_id,
        "names": names,
        "index": 0,
        "missing": [],
    }
    client.send(
        {
            "@type": "getSupergroupFullInfo",
            "supergroup_id": supergroup_id,
            "@extra": "menu_channel_3",
        }
    )


def _load_sheet_rows():
    json_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    spreadsheet_id = os.getenv("GOOGLE_USERS_SPREADSHEET_ID")
    sheet_range = os.getenv("GOOGLE_USERS_SHEET_RANGE")

    creds = Credentials.from_service_account_file(
        json_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=sheet_range)
        .execute()
    )
    return result.get("values", [])


def on_menu_channel_b(client):
    client.menu = "menu_channels"
    client.menu_event.set()
