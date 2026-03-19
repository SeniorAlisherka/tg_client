# src/static_instances/extra_handler_actions.py
from src.static_instances import menus
from src.static_instances import helpers
import pydoc


def user_main_1(client, event):
    print(f"\n👤 Logged in as {event['first_name']} {event['last_name']}")
    client.menu_event.set()


def users_main_5(client, event):
    contacts_ids = event["user_ids"]

    if not contacts_ids:
        print("\nNo contacts found.")
        client.menu_event.set()
        return

    client.state["contacts_to_process"] = contacts_ids
    client.state["pending"] = len(contacts_ids)
    client.state["contacts_data"] = []

    for user_id in contacts_ids:
        client.send(
            {
                "@type": "getUser",
                "user_id": user_id,
                "@extra": {"@type": "main_5"},
            }
        )


def user_main_5(client, event):
    first_name = event["first_name"]
    username = event.get("usernames", {}).get("active_usernames", [None])[0]

    if first_name and username:
        client.state["contacts_data"].append(
            {
                "first_name": first_name,
                "username": username,
            }
        )

    client.state["pending"] -= 1

    if client.state["pending"] > 0:
        return

    helpers.update_google_sheet_usernames(client.state["contacts_data"])
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

    # Mark non-missing registered students in sheet as present_in_channel=true
    helpers.set_present_in_channel_for_chat(current_chat_id, missing_students)

    lines = []
    lines.append("\nMissing students:")

    for name in missing_students:
        lines.append(name)

    lines.append(f"\nTotal missing students: {len(missing_students)}")

    pydoc.pager("\n".join(lines))
    client.menu_event.set()


def supergroup_supergroup_3(client, event):
    supergroup_id = event["id"]
    member_count = event["member_count"]
    limit = 200

    client.state["user_ids"] = []
    client.state["pending"] = (member_count + limit - 1) // limit

    for offset in range(0, member_count, limit):
        client.send(
            {
                "@type": "getSupergroupMembers",
                "supergroup_id": supergroup_id,
                "offset": offset,
                "limit": limit,
                "@extra": {"@type": "supergroup_3"},
            }
        )


def supergroup_supergroup_4(client, event):
    supergroup_id = event["id"]
    member_count = event["member_count"]
    limit = 200

    client.state["user_ids"] = []
    client.state["pending"] = (member_count + limit - 1) // limit

    for offset in range(0, member_count, limit):
        client.send(
            {
                "@type": "getSupergroupMembers",
                "supergroup_id": supergroup_id,
                "offset": offset,
                "limit": limit,
                "@extra": {"@type": "supergroup_4"},
            }
        )


def chatMembers_supergroup_3(client, event):
    for member in event["members"]:
        client.state["user_ids"].append(member["member_id"]["user_id"])

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.state["pending"] = len(client.state["user_ids"])
        for user_id in client.state["user_ids"]:
            client.send(
                {
                    "@type": "getUser",
                    "user_id": user_id,
                    "@extra": {"@type": "supergroup_3"},
                }
            )


def chatMembers_supergroup_4(client, event):
    for member in event["members"]:
        client.state["user_ids"].append(member["member_id"]["user_id"])

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.state["pending"] = len(client.state["user_ids"])
        for user_id in client.state["user_ids"]:
            client.send(
                {
                    "@type": "getUser",
                    "user_id": user_id,
                    "@extra": {"@type": "supergroup_4"},
                }
            )


def user_supergroup_3(client, event):
    if not event["is_contact"]:
        client.state["non_contacts"].append(
            {
                "first_name": event["first_name"],
                "last_name": event["last_name"],
                "usernames": event.get("usernames", {}).get("active_usernames", []),
                "phone_number": event["phone_number"],
            }
        )

    client.state["pending"] -= 1

    if client.state["pending"] != 0:
        return

    # === DONE ===
    non_contacts = client.state["non_contacts"]

    lines = []

    lines.append("\nNon-contact members:")

    for u in non_contacts:
        name = f"{u['first_name']} {u['last_name']}".strip()
        username = "@" + u["usernames"][0] if u["usernames"] else "—"
        phone = u["phone_number"] or "—"

        lines.append("────────────────────────────")
        lines.append(f"👤 {name}")
        lines.append(f"🔗 {username}")
        lines.append(f"📞 {phone}")

    lines.append(f"\nTotal non-contacts: {len(non_contacts)}")

    pydoc.pager("\n".join(lines))

    client.menu_event.set()


def user_supergroup_4(client, event):
    if event["is_contact"]:
        first_name = event["first_name"]
        # collect contact members by first_name
        client.state.setdefault("contacts", []).append(first_name)

    client.state["pending"] -= 1

    if client.state["pending"] != 0:
        return

    contact_names = set(client.state["contacts"])
    sheet_rows = helpers.load_google_users()
    sheet_lookup = helpers.build_sheet_lookup(sheet_rows)

    chat_id = str(client.state["current_supergroup"]["id"])
    extra = []

    for name in sorted(contact_names):
        if (name, chat_id) not in sheet_lookup:
            extra.append(name)

    lines = []
    lines.append("\nExtra contacts in this group (Лишние контакты):")

    if extra:
        for name in extra:
            lines.append(name)
    else:
        lines.append("None. All contact names are accounted for in Google Sheet.")

    lines.append(f"\nTotal extra contacts: {len(extra)}")

    pydoc.pager("\n".join(lines))
    client.menu_event.set()
