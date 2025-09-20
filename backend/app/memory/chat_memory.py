from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from typing import Dict

class ChatMemory:
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.store : Dict[str, Dict] = {}
    
    def get_memory(self, session_id: str) -> Dict:
        if session_id not in self.store:
            self.store[session_id] = {
                'buffer': ChatMessageHistory(),
                'summary': ''
            }
        return self.store[session_id]
    
    def save_memory(self, session_id: str, user_input: str, ai_response: str, summary: str):
        if session_id not in self.store:
            self.store[session_id] = {
                'buffer': ChatMessageHistory(),
                'summary': summary
            }
        self.store[session_id]['buffer'].add_user_message(user_input)
        self.store[session_id]['buffer'].add_ai_message(ai_response)

    def clear_memory(self, session_id: str):
        if session_id in self.store:
            self.store[session_id]['buffer'].clear()
            self.store[session_id]['summary'] = ''
    
    def delete_memory(self, session_id: str):
        self.store.pop(session_id, None)