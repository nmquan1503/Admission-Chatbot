from typing import TypedDict, List, Dict, Literal
from enum import Enum
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.schema import Document
from langgraph.graph import StateGraph, START, END
from ..nodes.doc_retriever_node import DocRetrieverNode
from ..nodes.fallback_node import FallbackNode
from ..nodes.faq_answer_node import FAQAnswerNode
from ..nodes.intent_classification_node import IntentClassificationNode
from ..nodes.load_memory_node import LoadMemoryNode
from ..nodes.summary_node import SummaryNode
from ..nodes.verification_answer_node import VerificationAnswerNode
from ..nodes.save_memory_node import SaveMemoryNode
from ..memory.chat_memory import ChatMemory
from ..retriever.retriever import Retriever
from ..config import settings
from .state import ChatState
from .question_type import QuestionType

class Workflow(StateGraph):
    def __init__(
        self,
        memory: ChatMemory,
        retriever: Retriever
    ):
        super().__init__(ChatState)
        self.load_memory_node = LoadMemoryNode(memory=memory)
        self.save_memory_node = SaveMemoryNode(memory=memory)
        self.doc_retriever_node = DocRetrieverNode(retriever=retriever)
        self.faq_answer_node = FAQAnswerNode(model_name=settings.ANSWER_MODEL_NAME)
        self.verification_answer_node = VerificationAnswerNode(model_name=settings.ANSWER_MODEL_NAME)
        self.intent_classification_node = IntentClassificationNode(model_name=settings.INTENT_CLASSIFICATION_MODEL_NAME)
        self.fallback_node = FallbackNode()
        self.summary_node = SummaryNode(model_name=settings.SUMMARY_MODEL_NAME)

        self.add_node('load_memory', self.load_memory_node.run)
        self.add_node('save_memory', self.save_memory_node.run)
        self.add_node('doc_retriever', self.doc_retriever_node.run)
        self.add_node('faq_answer', self.faq_answer_node.run)
        self.add_node('verification_answer', self.verification_answer_node.run)
        self.add_node('intent_classification', self.intent_classification_node.run)
        self.add_node('fallback', self.fallback_node.run)
        self.add_node('summary', self.summary_node.run)
        
        self.add_edge(START, 'load_memory')
        self.add_conditional_edges(
            'load_memory',
            lambda state: 'messages' in state.keys(),
            {
                True: 'summary',
                False: END
            }
        )
        self.add_edge('summary', 'doc_retriever')
        self.add_conditional_edges(
            'doc_retriever',
            lambda state: bool(state['retrieved_docs']),
            {
                True: 'intent_classification',
                False: 'fallback'
            }
        )
        self.add_conditional_edges(
            'intent_classification',
            self._choose_answer_node,
            {
                'faq': 'faq_answer',
                'verification': 'verification_answer',
                'fallback': 'fallback'
            }
        )
        self.add_edge('fallback', 'save_memory')
        self.add_edge('faq_answer', 'save_memory')
        self.add_edge('verification_answer', 'save_memory')
        self.add_edge('save_memory', END)

    def _choose_answer_node(self, state: ChatState) -> Literal['faq', 'verification', 'fallback']:
        type = state['question_type']
        if type == QuestionType.INFORMATION_SEARCH:
            return 'faq'
        if type == QuestionType.FACT_VERIFICATION:
            return 'verification'
        return 'fallback'