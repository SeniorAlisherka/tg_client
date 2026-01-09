# src/static_instances/extra_handlers.py
from src.datatypes.extra_handler import ExtraHandler
from src.static_instances import extra_handler_actions as actions


user_main_1 = ExtraHandler("main_1", actions.user_main_1)
chats_main_2 = ExtraHandler("main_2", actions.chats_main_2)
chat_main_2 = ExtraHandler("main_2", actions.chat_main_2)

supergroupFullInfo_channel_2 = ExtraHandler(
    "channel_2", actions.supergroupFullInfo_channel_2
)
chatMembers_channel_2 = ExtraHandler("channel_2", actions.chatMembers_channel_2)
error_channel_2 = ExtraHandler("channel_2", actions.error_channel_2)
