class Button:
    def __init__(self, key, label, action):
        self.key = key
        self.label = label
        self.action = action

    def matches(self, choice):
        return choice == self.key

    def execute(self, client):
        self.action(client)
