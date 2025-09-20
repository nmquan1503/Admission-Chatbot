from .base_node import BaseNode
from ..retriever.retriever import Retriever
from ..workflow.state import ChatState

class DocRetrieverNode(BaseNode):
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
    
    def run(self, state: ChatState) -> ChatState:
        retriever_input = state['summary'] + '\n' + state['user_input']
        docs = self.retriever.invoke(retriever_input)
        info = ''
        for doc in docs:
            cur = ''
            metadata = doc.metadata
            print(metadata)
            if 'years' in metadata:
                years = metadata['years']
                if years:
                    cur += 'Năm: ' + ', '.join(str(y) for y in years) + '\n'
            # if 'source' in metadata:
            #     source = metadata['source']
            #     if source:
            # #         cur += 'Nguồn: ' + source + '\n'
            # if 'page_number' in metadata:
            #     cur += 'Trang ' + metadata['page_number'] + '\n'
            if 'headings' in metadata:
                headings = metadata['headings']
                if headings:
                    cur += 'Phần: ' + ' > '.join(headings) + '\n'
            # if 'title' in metadata:
            #     title = metadata['title']
            #     if title:
            #         cur += 'Tiêu đề: ' + title + '\n'
            cur += 'Nội dung: ' + doc.page_content + '\n'

            info += cur + '\n'
            
        state['retrieved_docs'] = info
        print('-' * 50)
        print('>> Document Retriever: ')
        print(info)
        print
        return state