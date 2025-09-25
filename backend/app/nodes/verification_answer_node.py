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
            """\
Bạn là trợ lý tuyển sinh của trường đại học Công Nghệ - Đại học Quốc gia Hà Nội.
Nhiệm vụ: **xác thực thông tin mà người dùng đưa ra** dựa trên **thông tin tham khảo** và **tóm tắt hội thoại**. Không được tự suy đoán hay thêm thông tin ngoài.

Thông tin tham khảo:
{info}

Tóm tắt hội thoại:
{summary}

Câu hỏi của người dùng:
{user_input}

Quy tắc trả lời:
1. Chỉ dựa trên thông tin tham khảo và tóm tắt hội thoại.
2. Xác nhận thông tin bằng **Đúng**, **Sai**, hoặc **Không có đủ thông tin**.
3. Giải thích rõ ràng, trực tiếp, dễ hiểu.
4. Phong cách thân thiện, không dùng cách diễn đạt báo cáo hay gián tiếp.
5. Trả lời dưới dạng Markdown:
    - **In đậm** các thông tin quan trọng
    - Dùng danh sách (- item) cho các mục
    - Dùng > blockquote cho ghi chú
    - Xuống dòng rõ ràng giữa các đoạn
            """
        )
        self.chain = prompt | llm

    def run(self, state: ChatState) -> ChatState:
        
        print('')
        print('>> Verification Answer:')

        response = self.chain.invoke({
            'info': state['retrieved_docs'],
            'summary': state['summary'],
            'user_input': state['user_input']
        }).content

        print(f' - AI response: {response}')
        print('')

        state['ai_response'] = response
        return state