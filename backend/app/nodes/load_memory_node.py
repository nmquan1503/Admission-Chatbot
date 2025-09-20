from .base_node import BaseNode
from ..memory.chat_memory import ChatMemory
from ..workflow.state import ChatState

class LoadMemoryNode(BaseNode):
    def __init__(self, memory: ChatMemory):
        self.memory = memory
    
    def run(self, state: ChatState) -> ChatState:
        current = self.memory.get_memory(state['session_id'])
        messages = ''
        for msg in current['buffer'].messages:
            if msg.type == 'human':
                messages += f'Người dùng: {msg.content}\n'
            elif msg.type == 'ai':
                messages += f'AI: {msg.content}\n'
            else:
                messages += f'{msg.type}: {msg.content}\n'
        state['messages'] = messages
        state['summary'] = current['summary']
        print('-' * 50)
        print('>> Load Memory:')
        print(state['messages'])
        print(f"Summary: {state['summary']}")
        return state
