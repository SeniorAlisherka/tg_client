def choice_dispatcher(client, menu_name, choice):
    func_name = f"on_{menu_name}_{choice}"
    choice_handler = globals().get(func_name)

    if choice_handler:
        choice_handler(client)
    else:
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
    channels = client.state.get("channels", [])

    print("\nChannels:")
    for i, ch in enumerate(channels, 1):
        print(f"{i}) {ch['title']}")
    print("b) Back")

    choice = input("> ").strip().lower()
    choice_dispatcher(client, "menu_channels", choice)


def on_menu_channels_b(client):
    client.menu = "menu_main"
    client.menu_event.set()
