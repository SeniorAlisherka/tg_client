# src/static_instances/button_actions.py
from src.static_instances import helpers
from src.static_instances import menus


def main_1(client):
    client.send({"@type": "getMe", "@extra": {"@type": "main_1"}})


def main_2(client):
    # client.send({"@type": "getChats", "limit": 100000, "@extra": {"@type": "main_2"}})
    in_development_text = (
        "\n⚠️ The Channels feature is under development and may not work as expected.\n"
        "Please use Supergroups feature instead for now.\n"
    )
    print(in_development_text)
    client.menu_event.set()


def main_3(client):
    client.send({"@type": "getChats", "limit": 100000, "@extra": {"@type": "main_3"}})


def main_4(client):
    help_text = (
        "\nThis app looks for missing students or nonames in any supergroup.\n"
        "To do that you need to go to supergroups tabs, select the desired supergroup "
        "and then press the corresponding button.\n\n"
        "If you cannot find your group in supergroups tabs, it means it is a basic group.\n"
        "To upgrade a basic group to a supergroup, you need to go to the group settings "
        'in Telegram app and just press "Topics" once (no need to create them).\n'
        "After that, go back to the main menu of this app and re-enter the supergroups tab.\n\n"
        "To add a new program, you need to do the following ONCE:\n"
        "1) Choose your supergroup.\n"
        '2) Press "Chat ID" button and copy the chat ID.\n'
        '3) In your Google Sheet list called "IDS", add a new row with the '
        "program name in the first column and the copied chat ID in the second column.\n"
        "4) Add all students of the program to your contacts in Telegram app.\n"
        "Another feature you can use is syncing contacts usernames to Google Sheet. To do that, just press the corresponding button in the main menu.\n"
    )

    print(help_text)
    client.menu_event.set()


def main_5(client):
    client.state["contacts_to_process"] = []
    client.state["contacts_data"] = []
    client.state["pending"] = 0

    client.send(
        {
            "@type": "getContacts",
            "@extra": {"@type": "main_5"},
        }
    )


def main_q(client):
    client.send({"@type": "close"})


def channels_b(client):
    client.set_menu(menus.main)


def channels_index(index):
    def _action(client):
        channels = client.state["channels"]
        client.state["current_channel"] = channels[index]
        ch = channels[index]
        menus.channel.title = f"Channel {ch['title']}:"
        client.set_menu(menus.channel)

    return _action


def channel_1(client):
    channel = client.state["current_channel"]
    chat_id = channel["id"]
    print(f"\nChat ID: {chat_id}")
    client.menu_event.set()


def channel_2(client):

    channel = client.state["current_channel"]
    chat_id = channel["id"]
    names = helpers.fetch_google_sheet_names(chat_id)

    if not names:
        print("\nNo valid students found in Google Sheet for this channel.")
        client.menu_event.set()
        return

    client.state["member_search"] = {
        "names": names,
        "index": 0,
        "missing": [],
        "chat_id": chat_id,
    }

    # for long tasks with cancel use current_task_id to track and avoid stale responses
    # and start cancel listener (but not here, rather when we approve taht we have rights
    # to view members)
    client.current_task_id += 1
    client.start_cancel_listener()
    helpers.send_next_member_search(client, client.state["member_search"])


def channel_b(client):
    main_2(client)  # not just set menu because channels may have changed


def supergroups_index(index):
    def _action(client):
        supergroups = client.state["supergroups"]
        client.state["current_supergroup"] = supergroups[index]
        sg = supergroups[index]
        menus.supergroup.title = f"Supergroup {sg['title']}:"
        client.set_menu(menus.supergroup)

    return _action


def supergroups_b(client):
    client.set_menu(menus.main)


def supergroup_1(client):
    chat = client.state["current_supergroup"]
    chat_id = chat["id"]
    print(f"\nChat ID: {chat_id}")
    client.menu_event.set()


def supergroup_2(client):
    sg = client.state["current_supergroup"]
    supergroup_id = sg["type"]["supergroup_id"]

    # Ask TDLib for supergroup info (to get member_count)
    client.send(
        {
            "@type": "getSupergroup",
            "supergroup_id": supergroup_id,
            "@extra": {"@type": "supergroup_2"},
        }
    )


def supergroup_3(client):
    sg = client.state["current_supergroup"]
    supergroup_id = sg["type"]["supergroup_id"]

    client.state["non_contacts"] = []
    client.state["user_ids"] = []

    client.send(
        {
            "@type": "getSupergroup",
            "supergroup_id": supergroup_id,
            "@extra": {"@type": "supergroup_3"},
        }
    )


def supergroup_b(client):
    main_3(client)  # not just set menu because supergroups may have changed
