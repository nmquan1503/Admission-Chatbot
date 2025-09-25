from .base_node import BaseNode
from ..workflow.state import ChatState
import re

class ResponsePostprocessingNode(BaseNode):
    def __init__(self):
        pass

    def run(self, state: ChatState) -> ChatState:

        print('')
        print('>>Response Postprocessing: ')

        response = state['ai_response']
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        response = response.strip()
        
        state['ai_response'] = response
    
        print(f'New response: ${response}')
        print('')

        return state
