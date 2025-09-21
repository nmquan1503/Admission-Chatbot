from ..retriever.retriever import Retriever
from ..memory.chat_memory import ChatMemory
from ..workflow.workflow import Workflow
from ..workflow.state import ChatState
from ..ingestion.vector_stores.weaviate_vector_store import WeaviateVectorStore
from ..ingestion.embedders.hugging_face_embedder import HuggingFaceEmbedder
from ..config import settings

class Chatbot:
    def __init__(self):
        self.memory = ChatMemory()
        self.embedder = HuggingFaceEmbedder(settings.HUGGING_FACE_EMBEDDER_CONFIG['model_name'])
        self.vector_store = WeaviateVectorStore(
            host=settings.WEAVIATE_CONFIG['host'],
            port=settings.WEAVIATE_CONFIG['port'],
            grpc_port=settings.WEAVIATE_CONFIG['grpc_port'],
            collection_name=settings.WEAVIATE_CONFIG['collection_name']
        )
        self.retriever = Retriever(
            embedder=self.embedder,
            vector_store=self.vector_store
        )
        self.workflow = Workflow(
            retriever=self.retriever,
            memory=self.memory
        )
        self.compiled = self.workflow.compile()
    
    def chat(self, session_id: str, user_input: str) -> str:
        print('-' * 50)
        print(f'>> Session id: {session_id}')
        print('')
        state: ChatState = {
            'user_input': user_input,
            'session_id': session_id,
        }
        state = self.compiled.invoke(state)
        return state['ai_response']

    def close(self):
        self.vector_store.close()