from .base_node import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..config import settings
from ..workflow.state import ChatState

class FAQAnswerNode(BaseNode):
    def __init__(self, model_name: str):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.prompt = ChatPromptTemplate.from_template(
            """
                Bạn là trợ lý tuyển sinh của trường đại học Công Nghệ - Đại học Quốc gia Hà Nội.
                
                Thông tin tham khảo:
                {info}
                
                Tóm tắt hội thoại:
                {summary}

                Câu hỏi của người dùng:
                {user_input}

                Hãy trả lời ngắn gọn, chính xác, chỉ dựa trên thông tin tham khảo. 
                Nếu câu trả lời không có trong tài liệu, hãy trả lời: "Thông tin chưa có sẵn".
                Không thêm thông tin ngoài tài liệu.
            """
        )

        self.chain = self.prompt | self.llm

    def run(self, state: ChatState) -> ChatState:

        print('')
        print('>> FAQ Answer: ')

        response = self.chain.invoke({
            'info': state['retrieved_docs'],
            'summary': state['summary'],
            'user_input': state['user_input']
        }).content

        print(f' - AI response: {response}')
        print('')

        state['ai_response'] = response
        return state