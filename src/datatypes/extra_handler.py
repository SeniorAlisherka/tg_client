# src/datatypes/extra_handler.py
class ExtraHandler:
    def __init__(self, extra_type: str, extra_handler_action):
        self.extra_type = extra_type
        self.extra_handler_action = extra_handler_action

    def matches(self, extra) -> bool:
        return extra["@type"] == self.extra_type

    def handle(self, client, event):
        self.extra_handler_action(client, event)
