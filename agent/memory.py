class Memory:
    def __init__(self):
        self.history = []

    def add_conversation(self, conversation):
        self.history.append(conversation)

    def get_history(self):
        return self.history