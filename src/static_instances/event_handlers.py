from src.static_instances import extra_handlers
from src.static_instances import helpers
from src.static_instances import defaults


def event_handler_updateAuthorizationState(client, event):
    extras_dict = {}

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_updateAuthorizationState(client, event)


def event_handler_authorizationStateWaitPassword(client, event):
    extras_dict = {}

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_authorizationStateWaitPassword(client, event)


def event_handler_error(client, event):
    extras_dict = {}

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_error(client, event)


def event_handler_user(client, event):
    extras_dict = {
        "button_main_1": extra_handlers.extra_handler_button_main_1,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_user(client, event)


def event_handler_chats(client, event):
    extras_dict = {
        "button_main_2": extra_handlers.extra_handler_button_main_2,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_chats(client, event)


def event_handler_chat(client, event):
    extras_dict = {
        "button_main_2": extra_handlers.extra_handler_button_main_2_chat,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_chat(client, event)


def event_handler_supergroup(client, event):
    extras_dict = {
        "menu_channel_1": extra_handlers.extra_handler_menu_channel_1,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_supergroup(client, event)


def event_handler_supergroupFullInfo(client, event):
    extras_dict = {
        "button_channel_3": extra_handlers.extra_handler_button_channel_3,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_supergroupFullInfo(client, event)


def event_handler_chatMembers(client, event):
    extras_dict = {
        "button_channel_3": extra_handlers.extra_handler_button_channel_3_members,
    }

    extra = event.get("@extra")
    if extra:
        helpers.helper_dispatch_extra(client, event, extras_dict)
    else:
        defaults.default_chatMembers(client, event)
