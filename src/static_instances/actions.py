from src.static_instances import menus


def action_main_1(client):
    client.send({"@type": "getMe", "@extra": "button_main_1"})


def action_main_2(client):
    client.send({"@type": "getChats", "limit": 100000, "@extra": "button_main_2"})


def action_main_q(client):
    client.send({"@type": "close"})


def action_channels_b(client):
    client.set_menu(menus.menu_main)


def action_channels_index(index):
    def _action(client):
        channels = client.state.get("channels", [])
        if 0 <= index < len(channels):
            client.state["current_channel"] = channels[index]
        client.set_menu(menus.menu_channels)  # for now we just go back to channels menu

    return _action
