# src/static_instances/button_factories.py
from src.datatypes.button import Button
import src.static_instances.buttons as buttons
import src.static_instances.button_actions as button_actions


def main(client):
    return [
        buttons.main_1,
        buttons.main_2,
        buttons.main_3,
        buttons.main_4,
        buttons.main_q,
    ]


def channels(client):
    result = []
    channels = client.state["channels"]

    for i, ch in enumerate(channels, 1):
        result.append(
            Button(
                key=str(i),
                label=f"{i}) {ch['title']}",
                button_action=button_actions.channels_index(i - 1),
            )
        )

    result.append(buttons.channels_b)
    return result


def channel(client):
    return [
        buttons.channel_1,
        buttons.channel_2,
        buttons.channel_b,
    ]


def supergroups(client):
    result = []
    supergroups = client.state["supergroups"]

    for i, sg in enumerate(supergroups, 1):
        result.append(
            Button(
                key=str(i),
                label=f"{i}) {sg['title']}",
                button_action=button_actions.supergroups_index(i - 1),
            )
        )

    result.append(buttons.supergroups_b)
    return result


def supergroup(client):
    return [
        buttons.supergroup_1,
        buttons.supergroup_2,
        buttons.supergroup_3,
        buttons.supergroup_b,
    ]
