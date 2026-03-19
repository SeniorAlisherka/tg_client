# src/static_instances/extra_handlers.py
from src.datatypes.extra_handler import ExtraHandler
import src.static_instances.extra_handler_actions as extra_handler_actions


user_main_1 = ExtraHandler("main_1", extra_handler_actions.user_main_1)
chats_main_2 = ExtraHandler("main_2", extra_handler_actions.chats_main_2)
chat_main_2 = ExtraHandler("main_2", extra_handler_actions.chat_main_2)
chats_main_3 = ExtraHandler("main_3", extra_handler_actions.chats_main_3)
chat_main_3 = ExtraHandler("main_3", extra_handler_actions.chat_main_3)
users_main_5 = ExtraHandler("main_5", extra_handler_actions.users_main_5)
user_main_5 = ExtraHandler("main_5", extra_handler_actions.user_main_5)


chatMembers_channel_2 = ExtraHandler(
    "channel_2", extra_handler_actions.chatMembers_channel_2
)
error_channel_2 = ExtraHandler("channel_2", extra_handler_actions.error_channel_2)

chatMembers_supergroup_2 = ExtraHandler(
    "supergroup_2", extra_handler_actions.chatMembers_supergroup_2
)
users_supergroup_2 = ExtraHandler(
    "supergroup_2",
    extra_handler_actions.users_supergroup_2,
)
user_supergroup_2 = ExtraHandler(
    "supergroup_2", extra_handler_actions.user_supergroup_2
)
supergroup_supergroup_2 = ExtraHandler(
    "supergroup_2", extra_handler_actions.supergroup_supergroup_2
)
supergroup_supergroup_3 = ExtraHandler(
    "supergroup_3",
    extra_handler_actions.supergroup_supergroup_3,
)
chatMembers_supergroup_3 = ExtraHandler(
    "supergroup_3",
    extra_handler_actions.chatMembers_supergroup_3,
)
user_supergroup_3 = ExtraHandler(
    "supergroup_3",
    extra_handler_actions.user_supergroup_3,
)
