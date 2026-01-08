class Menu:
    def __init__(self, title, buttons_factory):
        self.title = title
        self.buttons_factory = buttons_factory
        self.buttons = []

    def render(self, client):
        print(f"\n{self.title}")
        self.buttons = self.buttons_factory(client)
        for button in self.buttons:
            print(button.label)

    def handle_choice(self, client, choice):
        for button in self.buttons:
            if button.matches(choice):
                button.execute(client)
                return

        print("\nInvalid choice")
        client.menu_event.set()
