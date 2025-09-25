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

        state['ai_response'] = """\
Xin lỗi, tôi không có thông tin cho câu hỏi này vì nó không liên quan đến Trường Đại học Công Nghệ - Đại học Quốc gia Hà Nội.  
Bạn có thể tham khảo các kênh hỗ trợ chính thức của trường để được tư vấn chi tiết:

- 🌐 Website: [tuyensinh.uet.vnu.edu.vn](https://tuyensinh.uet.vnu.edu.vn)
- 📞 SĐT Phòng Đào Tạo: 024.3754 7865 | 0334.924.224
- 📧 Email: [TuyensinhDHCN@vnu.edu.vn](mailto:TuyensinhDHCN@vnu.edu.vn)
- 👍 Fanpage: [TVTS.UET.VNU](https://www.facebook.com/TVTS.UET.VNU)
- 💬 Nhóm hỗ trợ tuyển sinh: [uet.tvts group](https://www.facebook.com/groups/uet.tvts)

Hy vọng những thông tin này sẽ giúp bạn nhận được sự hỗ trợ nhanh chóng!
        """

        return state