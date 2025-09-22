from .base_loader import BaseLoader
from typing import Dict, Optional, Any, List
from langchain.schema import Document
import json
import re

class FAQLoader(BaseLoader):
    def __init__(self):
        pass

    def load(self,
        path: str, 
        metadata: Optional[Dict[str, Any]]=None,
    ) -> List[Document]:
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
            docs = []
            for item in items:
                content = f"Question: {item['q']}\nAnswer: {item['a']}"
                years = re.findall(r'20\d{2}', content)
                if years:
                    years.append(item['year'])
                else:
                    years = [item['year']]
                item_metadata = self.merge_metadata(metadata, {
                    'years': years,
                    'source': item['source']
                })
                docs.append(Document(
                    page_content=content,
                    metadata=item_metadata
                ))
            return docs