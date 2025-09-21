from .base_node import BaseNode
from ..retriever.retriever import Retriever
from ..workflow.state import ChatState

class DocRetrieverNode(BaseNode):
    def __init__(self, retriever: Retriever):
        self.retriever = retriever
    
    def run(self, state: ChatState) -> ChatState:

        print('')
        print('>> Doc Retriever:')

        retriever_input = state['summary'] + '\n' + state['user_input']
        print(f' - Retriever input: {retriever_input}')

        docs = self.retriever.invoke(retriever_input)

        retrieved_docs = ''
        for doc in docs:
            cur = ''
            metadata = doc.metadata
            if 'years' in metadata:
                years = metadata['years']
                if years:
                    cur += 'Năm: ' + ', '.join(str(y) for y in years) + '\n'
            if 'source' in metadata:
                source = metadata['source']
                if source:
                    cur += 'Nguồn: ' + str(source) + '\n'
            if 'page_number' in metadata:
                cur += 'Trang ' + str(metadata['page_number']) + '\n'
            if 'headings' in metadata:
                headings = metadata['headings']
                if headings:
                    cur += 'Phần: ' + ' > '.join(headings) + '\n'
            if 'title' in metadata:
                title = metadata['title']
                if title:
                    cur += 'Tiêu đề: ' + str(title) + '\n'
            cur += 'Nội dung: ' + doc.page_content + '\n'

            retrieved_docs += cur + '\n'
            
        print(f' - Retrieved documents: {retrieved_docs}')
        print('')

        state['retrieved_docs'] = retrieved_docs

        return state