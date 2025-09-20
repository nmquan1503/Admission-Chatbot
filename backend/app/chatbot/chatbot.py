from ..retriever.retriever import Retriever
from ..memory.chat_memory import ChatMemory
from ..workflow.workflow import Workflow
from ..workflow.state import ChatState

class Chatbot:
    def __init__(
        self,
        memory: ChatMemory,
        retriever: Retriever
    ):
        workflow = Workflow(memory, retriever)
        self.compiled = workflow.compile()
    
    def chat(self, session_id: str, user_input: str) -> str:
        state: ChatState = {
            'user_input': user_input,
            'session_id': session_id
        }

        state = self.compiled.invoke(state)
        return state['ai_response']