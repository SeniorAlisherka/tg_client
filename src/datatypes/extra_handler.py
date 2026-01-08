class ExtraHandler:
    def __init__(self, extra: str, extra_handler_action):
        self.extra = extra
        self.extra_handler_action = extra_handler_action

    def matches(self, extra: str) -> bool:
        return self.extra == extra

    def handle(self, client, event):
        self.extra_handler_action(client, event)
