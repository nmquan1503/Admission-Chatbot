from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..config import settings
from .base_node import BaseNode
from ..workflow.state import ChatState

class SummaryNode(BaseNode):
    def __init__(self, model_name: str):
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        self.prompt = ChatPromptTemplate.from_template(
            """
                Bạn là trợ lý AI trong lĩnh vực tư vấn tuyển sinh. Nhiệm vụ của bạn là tóm tắt hội thoại giữa người dùng và AI.

                Hội thoại:
                {chat_history}

                Yêu cầu tóm tắt:
                - Giữ các ý chính của người dùng và phản hồi của AI.
                - Tóm tắt ngắn gọn, 1–2 câu, bỏ các câu chào hỏi hoặc cảm ơn.
                - Chỉ tóm tắt dựa trên hội thoại, không thêm thông tin mới.
                - Xuất ra văn bản tự nhiên, dễ đọc.
            """
        )
        self.chain = self.prompt | self.llm
    
    def run(self, state: ChatState) -> ChatState:

        print('')
        print('>> Summary: ')

        his = state['summary']
        messages = state['messages']
        if len(messages) >= 2:
            his += '\n'
            for msg in messages[-2:]:
                if msg.type == 'human':
                    his += f'Người dùng: {msg.content}\n'
                elif msg.type == 'ai':
                    his += f'AI: {msg.content}\n'
                else:
                    his += f'{msg.type}: {msg.content}\n'
            print(f' - Summary input: {his}')

            summary = self.chain.invoke({
                'chat_history': his
            })

            print(f' - Current summary: {summary}')
        else:
            summary = his
            print('No messages')
        
        print('')
        state['summary'] = summary
        return state