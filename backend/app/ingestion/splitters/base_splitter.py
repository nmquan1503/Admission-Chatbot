from abc import ABC, abstractmethod
from langchain.schema import Document
from typing import List

class BaseSplitter(ABC):

    def __init__(self):
        pass
    
    @abstractmethod
    def split(self, docs: List[Document]) -> List[Document]:
        pass