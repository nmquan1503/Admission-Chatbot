from abc import ABC, abstractmethod
from ..workflow.state import ChatState

class BaseNode:

    @abstractmethod
    def run(self, state: ChatState) -> ChatState:
        pass