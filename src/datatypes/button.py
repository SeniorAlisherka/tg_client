class Button:
    def __init__(self, key, label, button_action):
        self.key = key
        self.label = label
        self.button_action = button_action

    def matches(self, choice):
        return choice == self.key

    def execute(self, client):
        self.button_action(client)
