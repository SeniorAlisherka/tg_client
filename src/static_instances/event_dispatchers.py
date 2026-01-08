from src.datatypes.event_dispatcher import EventDispatcher
from src.static_instances import default_handlers
from src.static_instances import extra_handlers


updateAuthorizationState = EventDispatcher(
    extra_handlers=[],
    default_handler=default_handlers.updateAuthorizationState,
)

authorizationStateWaitPassword = EventDispatcher(
    extra_handlers=[],
    default_handler=default_handlers.authorizationStateWaitPassword,
)

error = EventDispatcher(
    extra_handlers=[extra_handlers.error_channel_2],
    default_handler=default_handlers.error,
)

user = EventDispatcher(
    extra_handlers=[extra_handlers.user_main_1],
    default_handler=default_handlers.user,
)

chats = EventDispatcher(
    extra_handlers=[extra_handlers.chats_main_2],
    default_handler=default_handlers.chats,
)

chat = EventDispatcher(
    extra_handlers=[extra_handlers.chat_main_2],
    default_handler=default_handlers.chat,
)

supergroupFullInfo = EventDispatcher(
    extra_handlers=[extra_handlers.supergroupFullInfo_channel_2],
    default_handler=default_handlers.supergroupFullInfo,
)

chatMembers = EventDispatcher(
    extra_handlers=[extra_handlers.chatMembers_channel_2],
    default_handler=default_handlers.chatMembers,
)
