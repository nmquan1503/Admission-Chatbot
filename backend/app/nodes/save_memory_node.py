from .base_node import BaseNode
from ..memory.chat_memory import ChatMemory
from ..workflow.state import ChatState

class SaveMemoryNode(BaseNode):
    def __init__(self, memory: ChatMemory):
        self.memory = memory

    def run(self, state: ChatState) -> ChatState:
        self.memory.save_memory(
            session_id=state['session_id'],
            user_input=state['user_input'],
            ai_response=state['ai_response'],
            summary=state['summary']
        )
        print('-' * 50)
        print('>> Save Memory')
        return state