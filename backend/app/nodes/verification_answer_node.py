from .base_node import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..config import settings
from ..workflow.state import ChatState

class VerificationAnswerNode(BaseNode):
    def __init__(self, model_name: str):
        llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        prompt = ChatPromptTemplate.from_template(
            """
                Bạn là trợ lý tuyển sinh của trường đại học Công Nghệ - Đại học Quốc gia Hà Nội. Nhiệm vụ của bạn là xác thực thông tin mà người dùng đưa ra.

                Thông tin tham khảo:
                {info}

                Tóm tắt hội thoại:
                {summary}

                Câu hỏi của người dùng:
                {user_input}

                Hãy xác nhận thông tin trên (Đúng / Sai / Không có đủ thông tin) và giải thích dựa trên dữ liệu tham khảo.

                Lưu ý: Không thêm thông tin ngoài dữ liệu tham khảo, chỉ giải thích dựa trên dữ liệu đó.
            """
        )
        self.chain = prompt | llm

    def run(self, state: ChatState) -> ChatState:
        print('-' * 50)
        print('>> Verification Answer:')
        print(state['ai_response'])
        return state
        response = self.chain.invoke({
            'info': state['retrieved_docs'],
            'summary': state['summary'],
            'user_input': state['user_input']
        }).content
        state['ai_response'] = response
        return state