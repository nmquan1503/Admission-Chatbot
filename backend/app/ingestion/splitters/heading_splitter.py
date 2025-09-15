from .base_splitter import BaseSplitter
from langchain.schema import Document
from typing import List, Optional, Dict, Any
import re

class HeadingSplitter(BaseSplitter):
    def __init__(self):
        super().__init__()
        
    def split(self, docs: List[Document]) -> List[Document]:
        new_docs = []
        cur_headings = []
        cur_content = ''
        for doc in docs:
            content = doc.page_content
            metadata = doc.metadata
            lines = content.split('\n')
            for line in lines:
                type = self.check_heading(line)
                if type == 0:
                    cur_content += line + '\n'
                else:
                    chunk = self.make_chunk(cur_content, metadata, cur_headings)
                    if chunk:
                        new_docs.append(chunk)
                    cur_content = ''
                    colon_id = line.find(':')
                    if colon_id > 0:
                        heading = line[:colon_id]
                        cur_content += line[colon_id + 1:] + '\n'
                    else:
                        heading = line
                    if type > len(cur_headings):
                        cur_headings = cur_headings + [''] * (type - 1 - len(cur_headings)) + [heading]
                    else:
                        cur_headings = cur_headings[:type - 1] + [heading]
            chunk = self.make_chunk(cur_content, metadata, cur_headings)
            if chunk:
                new_docs.append(chunk)
            cur_content = ''
        chunk_index = 0
        total_chunks = len(new_docs)
        for doc in new_docs:
            doc.metadata['chunk_index'] = chunk_index
            doc.metadata['total_chunks'] = total_chunks
            chunk_index += 1

        return new_docs

    def make_chunk(
        self, 
        content: str, 
        metadata: Dict[str, Any], 
        headings: List[str],
    ) -> Optional[Document]:
        content = content.strip()
        if not content:
            return None
        metadata = metadata.copy()
        headings = [heading for heading in headings if heading]
        if headings:
            metadata['headings'] = headings
        else:
            metadata.pop('headings', None)
        doc = Document(
            page_content=content,
            metadata = metadata
        )
        return doc
    
    def check_heading(self, line: str) -> int:
        line = line.strip()
        if not line:
            return 0
        if re.match(r'^[IVX]+\.\s+', line):
            return 1
        
        space_id = line.find(' ')
        if space_id > 0:
            sub = line[:space_id]
            if sub[-1] == '.':
                parts = sub[:-1].split('.')
            else:
                parts = sub.split('.')
            for i in range(len(parts)):
                try:
                    parts[i] = int(parts[i])
                except ValueError:
                    return 0
            if len(parts) == 1:
                if sub[-1] == '.':
                    return 2
            elif len(parts) == 2:
                if sub[-1] == '.':
                    return 3
            elif len(parts) == 3:
                return 4

        return 0