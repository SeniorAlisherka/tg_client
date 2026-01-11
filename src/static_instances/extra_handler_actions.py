# src/static_instances/extra_handler_actions.py
from src.static_instances import menus
from src.static_instances import helpers


def user_main_1(client, event):
    print(f"\n👤 Logged in as {event['first_name']} {event.get('last_name', '')}")
    client.menu_event.set()


def chats_main_2(client, event):
    client.state["channels"] = []
    client.state["pending"] = len(event["chat_ids"])

    for chat_id in event["chat_ids"]:
        client.send(
            {
                "@type": "getChat",
                "chat_id": chat_id,
                "@extra": {"@type": "main_2"},
            }
        )


def chat_main_2(client, event):
    chat_type = event["type"]

    if chat_type["@type"] == "chatTypeSupergroup" and chat_type["is_channel"]:
        client.state["channels"].append(event)

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.set_menu(menus.channels)


def chats_main_3(client, event):
    client.state["supergroups"] = []
    client.state["pending"] = len(event["chat_ids"])

    for chat_id in event["chat_ids"]:
        client.send(
            {
                "@type": "getChat",
                "chat_id": chat_id,
                "@extra": {"@type": "main_3"},
            }
        )


def chat_main_3(client, event):
    chat_type = event["type"]

    if chat_type["@type"] == "chatTypeSupergroup" and not chat_type["is_channel"]:
        client.state["supergroups"].append(event)

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.set_menu(menus.supergroups)


def chatMembers_channel_2(client, event):
    extra = event["@extra"]

    if extra["task_id"] != client.current_task_id:
        return  # stale response, ignore
    if client.is_current_task_cancelled():
        return  # task was cancelled

    state = client.state["member_search"]

    members = event["members"]
    member = members[0] if members else None

    if not member:
        state["missing"].append(state["names"][state["index"]])

    state["index"] += 1
    print(
        f"Checked {state['index']} of {len(state['names'])}... (press c + Enter to cancel)"
    )
    helpers.send_next_member_search(client, state)


def error_channel_2(client, event):
    message = event["message"]
    message = event["message"]

    if message == "Member list is inaccessible":
        print("\n🚫 You don't have permission to view members of this chat.")
        print("   (Admin rights are required for channels.)")

        client.stop_cancel_listener()
        client.ask_for_enter()
        return

    print("\n🛑 Error fetching channel info or members:", message)
    client.send({"@type": "close"})


def supergroup_supergroup_2(client, event):
    supergroup_id = event["id"]
    member_count = event["member_count"]

    limit = 200

    client.state["user_ids"] = []
    client.state["pending"] = (member_count + limit - 1) // limit
    if client.state["pending"] == 0:
        print("\nNo members in this supergroup.")
        client.menu_event.set()
        return
    for offset in range(0, member_count, limit):
        client.send(
            {
                "@type": "getSupergroupMembers",
                "supergroup_id": supergroup_id,
                "offset": offset,
                "limit": limit,
                "@extra": {"@type": "supergroup_2"},
            }
        )


def chatMembers_supergroup_2(client, event):
    members = event["members"]

    for member in members:
        client.state["user_ids"].append(member["member_id"]["user_id"])

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.send(
            {
                "@type": "getContacts",
                "@extra": {"@type": "supergroup_2"},
            }
        )


def users_supergroup_2(client, event):
    contacts_ids = event["user_ids"]
    group_members_ids = client.state["user_ids"]

    missing_ids = [uid for uid in contacts_ids if uid not in group_members_ids]

    if not missing_ids:
        print("\n✅ All your contacts are in this supergroup.")
        client.menu_event.set()
        return

    client.state["names"] = []
    client.state["pending"] = len(missing_ids)

    for user_id in missing_ids:
        client.send(
            {
                "@type": "getUser",
                "user_id": user_id,
                "@extra": {"@type": "supergroup_2"},
            }
        )


def user_supergroup_2(client, event):
    client.state["names"].append(event["first_name"])
    client.state["pending"] -= 1

    if client.state["pending"] != 0:
        return

    # === ALL CONTACTS RESOLVED ===

    sheet_rows = helpers.load_google_users()
    sheet_lookup = helpers.build_sheet_lookup(sheet_rows)
    if not sheet_lookup:
        print("\nNo valid entries found in Google Sheet.")
        client.menu_event.set()
        return

    current_chat_id = str(client.state["current_supergroup"]["id"])
    missing_students = []

    for name in client.state["names"]:
        # student is missing if he exists in the sheet for this chat
        if (name, current_chat_id) in sheet_lookup:
            missing_students.append(name)

    print("\nMissing students:")
    for name in missing_students:
        print(name)

    print(f"\nTotal missing students: {len(missing_students)}")
    client.menu_event.set()
