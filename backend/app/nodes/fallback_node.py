from .base_node import BaseNode
from ..workflow.state import ChatState
from ..workflow.question_type import QuestionType

class FallbackNode(BaseNode):
    def __init__(self):
        pass

    def run(self, state: ChatState) -> ChatState:
        
        print('')
        print('>> Fallback')
        print('')

        state['ai_response'] = """
            Rất tiếc, tôi chưa thể hiểu rõ câu hỏi của bạn. 
            Để được hỗ trợ chi tiết hơn, bạn có thể tham khảo các kênh chính thức của trường:

            - 🌐 Website: https://tuyensinh.uet.vnu.edu.vn
            - 📞 SĐT Phòng Đào Tạo: 024.3754 7865 | 0334.924.224
            - 📧 Email: TuyensinhDHCN@vnu.edu.vn
            - 👍 Fanpage: https://www.facebook.com/TVTS.UET.VNU
            - 💬 Nhóm hỗ trợ tuyển sinh: https://www.facebook.com/groups/uet.tvts

            Hy vọng những thông tin này sẽ giúp bạn nhận được sự hỗ trợ nhanh chóng!
        """

        return state