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
            """\
Bạn là trợ lý tuyển sinh của trường đại học Công Nghệ - Đại học Quốc gia Hà Nội.
Nhiệm vụ: trả lời câu hỏi của người dùng dựa trên **thông tin tham khảo** và **tóm tắt hội thoại trước**.

Thông tin tham khảo (Chỉ dùng thông tin này để trả lời):
{info}

Tóm tắt hội thoại trước (nếu có):
{summary}

Câu hỏi của người dùng:
{user_input}

Quy tắc trả lời:
1. Chỉ dựa trên thông tin tham khảo và tóm tắt, KHÔNG thêm thông tin ngoài.
2. Nếu không thể trả lời, trả lời: "Thông tin chưa có sẵn".
3. Gắn link chính xác nếu có, nếu không chắc thì bỏ qua.
4. Nói chuyện thân thiện với người dùng.
5. Trả lời dưới dạng Markdown:
    - **In đậm** các thông tin quan trọng
    - Dùng danh sách (- item) cho các mục
    - Dùng > blockquote cho ghi chú
    - Xuống dòng rõ ràng giữa các đoạn
6. Trả lời ngắn gọn, súc tích, dễ hiểu.
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