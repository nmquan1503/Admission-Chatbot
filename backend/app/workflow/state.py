from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.schema import Document
from .question_type import QuestionType

class ChatState(TypedDict):
    user_input: str
    ai_response: str
    messages: List[BaseMessage]
    retrieved_docs: str
    summary: str
    question_type: QuestionType
    session_id: str