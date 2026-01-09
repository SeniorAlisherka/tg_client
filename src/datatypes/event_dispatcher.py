# src/datatypes/event_dispatcher.py
class EventDispatcher:
    def __init__(self, extra_handlers, default_handler):
        self.extra_handlers = extra_handlers
        self.default_handler = default_handler

    def handle_event(self, client, event):
        extra = event.get("@extra")

        if extra:
            for extra_handler in self.extra_handlers:
                if extra_handler.matches(extra):
                    extra_handler.handle(client, event)
                    return
            print(f"\nWarning: No extra_handler found for {event}")
            client.auth_done.set()
            client.send({"@type": "close"})
            return

        self.default_handler(client, event)
