from .base_node import BaseNode
from ..memory.chat_memory import ChatMemory
from ..workflow.state import ChatState

class LoadMemoryNode(BaseNode):
    def __init__(self, memory: ChatMemory):
        self.memory = memory
    
    def run(self, state: ChatState) -> ChatState:

        print('')
        print('>> Load Memory: ')

        history = self.memory.get_memory(state['session_id'])

        if not history:
            print('History is None')
            print('')
            return state
        
        state['messages'] = history['buffer'].messages
        state['summary'] = history['summary']

        # messages = ''
        # for msg in history['buffer'].messages:
        #     if msg.type == 'human':
        #         messages += f'Người dùng: {msg.content}\n'
        #     elif msg.type == 'ai':
        #         messages += f'AI: {msg.content}\n'
        #     else:
        #         messages += f'{msg.type}: {msg.content}\n'
        # print(f' - Messages:')
        print(f'Summary: ${state['summary']}')
        print('')
        
        return state
