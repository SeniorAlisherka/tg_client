# src/static_instances/button_actions.py
from src.static_instances import helpers
from src.static_instances import menus


def main_1(client):
    client.send({"@type": "getMe", "@extra": {"@type": "main_1"}})


def main_2(client):
    client.send({"@type": "getChats", "limit": 100000, "@extra": {"@type": "main_2"}})


def main_q(client):
    client.send({"@type": "close"})


def channels_b(client):
    client.set_menu(menus.main)


def channels_index(index):
    def _action(client):
        channels = client.state.get("channels", [])
        if 0 <= index < len(channels):
            client.state["current_channel"] = channels[index]
        ch = channels[index]
        menus.channel.title = f"Channel {ch['title']}:"
        client.set_menu(menus.channel)

    return _action


def channel_1(client):
    channel = client.state.get("current_channel")
    supergroup_id = channel["type"]["supergroup_id"]
    print(f"\nSupergroup ID: {supergroup_id}")
    client.menu_event.set()


def channel_2(client):

    channel = client.state.get("current_channel")
    supergroup_id = channel["type"]["supergroup_id"]
    names = helpers.fetch_google_sheet_names(supergroup_id)

    if not names:
        print("\nNo valid students found in Google Sheet for this channel.")
        client.menu_event.set()
        return

    client.state["member_search"] = {
        "names": names,
        "index": 0,
        "missing": [],
        "supergroup_id": supergroup_id,
    }

    # for long tasks with cancel use current_task_id to track and avoid stale responses
    # and start cancel listener (but not here, rather when we approve taht we have rights
    # to view members)
    client.current_task_id += 1
    client.send(
        {
            "@type": "getSupergroupFullInfo",
            "supergroup_id": supergroup_id,
            "@extra": {"@type": "channel_2", "task_id": client.current_task_id},
        }
    )


def channel_b(client):
    client.set_menu(menus.channels)
