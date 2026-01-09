# src/static_instances/extra_handler_actions.py
from src.static_instances import menus
from src.static_instances.helpers import send_next_member_search


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


def supergroupFullInfo_channel_2(client, event):
    if not event["can_get_members"]:
        print("\nYou don't have rights to get members.")
        client.menu_event.set()
        return

    state = client.state["member_search"]
    client.start_cancel_listener()
    send_next_member_search(client, state)


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
    send_next_member_search(client, state)


def error_channel_2(client, event):
    message = event["message"]
    print("\n🛑 Error fetching channel info or members:", message)
    client.send({"@type": "close"})
