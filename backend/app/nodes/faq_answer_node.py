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

                Thông tin tham khảo (vui lòng chỉ dùng thông tin này để trả lời):
                {info}

                Tóm tắt hội thoại trước (nếu có):
                {summary}

                Câu hỏi của người dùng:
                {user_input}

                Quy tắc trả lời:
                1. Dựa trên thông tin trong phần "Thông tin tham khảo", bạn có thể suy luận để trả lời nếu cần.
                2. Không thêm bất kỳ thông tin nào ngoài tài liệu.
                3. Nếu câu hỏi không thể trả lời dù suy luận từ tài liệu, hãy trả lời chính xác: "Thông tin chưa có sẵn".
                4. Trả lời ngắn gọn, súc tích, dễ hiểu.
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