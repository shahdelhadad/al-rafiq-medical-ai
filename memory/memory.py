class ConversationMemory:
    def __init__(self):
        self.chat_history = []

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def get_history(self):
        return self.chat_history
