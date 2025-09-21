from .base_node import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..config import settings
from ..workflow.question_type import QuestionType
from ..workflow.state import ChatState

class IntentClassificationNode(BaseNode):
    def __init__(self, model_name: str):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        intents = [type.value for type in QuestionType]
        self.intents_str = ' hoặc '.join(intents)

        self.prompt = ChatPromptTemplate.from_template(
            """
                Tóm tắt hội thoại: {summary}

                Câu hỏi của người dùng: {user_input}

                Phân loại intent và trả lời chỉ 1 trong các lựa chọn sau đây: {intents_str}
                
                Không trả lời câu hỏi, chỉ trả về intent.
            """
        )
        self.chain = self.prompt | self.llm
    
    def run(self, state: ChatState) -> ChatState:
        
        print('')
        print('>> Intent classification: ')

        intent = self.chain.invoke({
            'summary': state['summary'],
            'user_input': state['user_input'],
            'intents_str': self.intents_str
        }).content.strip()

        print(f' - Intent: {intent}')

        for type in QuestionType:
            if intent == type.value:
                
                state['question_type'] = type
                print(f' - Type: {type.name}')
                print('')
                
                return state
        
        state['question_type'] = QuestionType.UNKNOWN
        print(' - Type: UNKNOWN')
        print('')

        return state
