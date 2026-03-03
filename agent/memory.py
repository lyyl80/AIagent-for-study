class Memory:
    def __init__(self):
        self.history = []

    def add_conversation(self, conversation):
        self.history.append(conversation)

    def get_recent_conversations(self, n=5):
        return self.history[-n:]