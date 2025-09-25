from .base_node import BaseNode
from ..workflow.state import ChatState
import re

class InputPreprocessingNode(BaseNode):
    def __init__(self):
        pass

    def run(self, state: ChatState) -> ChatState:
        print('')
        print('>> Input Preprocessing: ')

        user_input = state['user_input']
        print(f'Old Input: ${user_input}')

        user_input = re.sub(r'\s+', ' ', user_input)
        user_input = re.sub(r"[^a-zA-Z0-9\s.,!?àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", "", user_input, flags=re.IGNORECASE)
        user_input = re.sub(r"([.,!?])\1+", r"\1", user_input)
        
        state['user_input'] = user_input
        print(f'New Input: ${user_input}')
        print('')

        return state