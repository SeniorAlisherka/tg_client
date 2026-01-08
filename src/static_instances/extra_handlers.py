from src.static_instances import menus
from src.static_instances.helpers import helper_send_next_member_search


def extra_handler_button_main_1(client, event):
    print(f"\n👤 Logged in as {event['first_name']} {event.get('last_name', '')}")
    client.menu_event.set()


def extra_handler_button_main_2(client, event):
    client.state["channels"] = []
    client.state["pending"] = len(event["chat_ids"])

    for chat_id in event["chat_ids"]:
        client.send(
            {
                "@type": "getChat",
                "chat_id": chat_id,
                "@extra": "button_main_2",
            }
        )


def extra_handler_button_main_2_chat(client, event):
    chat_type = event["type"]

    if chat_type["@type"] == "chatTypeSupergroup" and chat_type["is_channel"]:
        client.state["channels"].append(event)

    client.state["pending"] -= 1

    if client.state["pending"] == 0:
        client.set_menu(menus.menu_channels)


def extra_handler_menu_channel_1(client, event):
    print(f"\nMembers: {event['member_count']}")
    client.menu_event.set()


def extra_handler_button_channel_3(client, event):
    if not event["can_get_members"]:
        print("\nYou don't have rights to get members.")
        client.menu_event.set()
        return

    state = client.state["member_search"]
    helper_send_next_member_search(client, state)


def extra_handler_button_channel_3_members(client, event):
    state = client.state["member_search"]

    members = event["members"]
    member = members[0] if members else None

    if not member:
        state["missing"].append(state["names"][state["index"]])

    state["index"] += 1
    print(f"\nChecked {state['index']} of {len(state['names'])}...")
    helper_send_next_member_search(client, state)
