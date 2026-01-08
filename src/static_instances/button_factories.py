from src.datatypes.button import Button
import src.static_instances.buttons as buttons
import src.static_instances.actions as actions


def buttons_factory_main(client):
    return [
        buttons.button_main_1,
        buttons.button_main_2,
        buttons.button_main_q,
    ]


def buttons_factory_channels(client):
    result = []
    channels = client.state.get("channels", [])

    for i, ch in enumerate(channels, 1):
        result.append(
            Button(
                key=str(i),
                label=f"{i}) {ch['title']}",
                action=actions.action_channels_index(i - 1),
            )
        )

    result.append(buttons.button_channels_b)
    return result
