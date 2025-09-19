from .base_loader import BaseLoader
import pdfplumber
from pdfplumber.page import Page
from pdfplumber.table import Table
from langchain.schema import Document
from typing import List, Dict, Any, Union, Optional, Tuple
import re

class PDFLoader(BaseLoader):
    def __init__(self):
        pass
    
    def load(
        self,
        path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        with pdfplumber.open(path) as pdf:
            year = None
            if pdf.metadata.get('CreationDate'):
                year_str = pdf.metadata['CreationDate'][2:6]
                try:
                    year = int(year_str)
                except ValueError:
                    pass
            total_pages = len(pdf.pages)
            docs = []
            last_table_row = None
            for page_number, page in enumerate(pdf.pages):
                text, last_table_row = self.read_page(
                    page=page, 
                    prev_table_row=last_table_row, 
                    return_last_table_row=True
                )
                metadata = self.merge_metadata(metadata, {
                    'source': path,
                    'page_number': page_number + 1,
                    'total_pages': total_pages
                })
                if year:
                    metadata['years'] = [year]
                docs.append(Document(
                    page_content=text,
                    metadata=metadata
                ))

            return docs


    def read_page(
        self, 
        page: Page, 
        prev_table_row: Optional[List[str]] = None,
        return_last_table_row: bool = False
    ) -> str:
        tables = page.find_tables()
        words = page.extract_words()
        elements = {}
        for word in words:
            bottom = int(word['bottom'] / 3)
            isTableBlock = False
            for table in tables:
                if bottom >= table.bbox[1] / 3 and bottom <= table.bbox[3] / 3:
                    isTableBlock = True
                    break
            if not isTableBlock:
                if bottom in elements:
                    elements[bottom]['data'].append(word)
                else:
                    elements[bottom] = {
                        'type': 'line',
                        'data': [word]
                    }
        for table in tables:
            bottom = int(table.bbox[3] / 3)
            elements[bottom] = {
                'type': 'table',
                'data': table
            }

        text = ''
        lines = []

        last_table_row = None
        for key in sorted(elements.keys()):
            if elements[key]['type'] == 'line':
                lines.append(elements[key]['data'])
            elif elements[key]['type'] == 'table':
                text += self.read_lines(lines) + '\n'
                lines = []
                table = elements[key]['data']
                if return_last_table_row:
                    table_text, last_table_row = self.read_table(
                        table, 
                        prev_row=prev_table_row,
                        return_last_row=True
                    )
                    text += table_text + '\n'
                else:
                    text += self.read_table(table, prev_row=prev_table_row) + '\n'
            
            if prev_table_row:
                prev_table_row=None
        
        text += self.read_lines(lines)
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        if return_last_table_row:
            return text, last_table_row

        return text
    
    def read_lines(self, lines: List[List[Dict[str, Any]]]) -> str:
        lines = [sorted(line, key=lambda word: word['x0']) for line in lines]
        lines = [' '.join([word['text'] for word in line]) for line in lines]
        return self.merge_lines(lines)

    def merge_lines(self, lines: List[str]) -> str:
        for i, line in enumerate(lines):
            if i == 0 or not line:
                continue
            if line.startswith(('a)', 'b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)')):
                lines[i - 1] = lines[i - 1] + '\n'
                continue
            first_char = line[0]
            if first_char.islower():
                lines[i - 1] = lines[i - 1] + ' '
            else:
                lines[i - 1] = lines[i - 1] + '\n'

        return ''.join(lines)

    def read_table(
        self, 
        table: Table, 
        prev_row: Optional[List[str]] = None,
        return_last_row = False
    ) -> Union[str, Tuple[str, List[str]]]:
        
        table = table.extract()
        
        R = len(table)
        C = len(table[0])

        if C == 1:
            lines = [row[0] for row in table]
            lines = [line for line in lines if line]
            text = self.merge_lines(lines)
            if return_last_row:
                return text, []
            return text
        
        header = self.extract_header(table)
        
        if len(header) == 0:
            table = [[item for item in row if item] for row in table]
            lines = [' '.join(row) for row in table]
            text = self.merge_lines(lines)
            if return_last_row:
                return text, []
            return text

        content = table[len(header):]

        header = [' - '.join([row[c].replace('\n', ' ').strip() for row in header]) for c in range(C)]
        
        matched = sum([1 for item in content[0] if item is None]) > 0
        
        if not matched:
            for c in range(C):
                if content[0][c] == '':
                    content[0][c] = None
        
        start_row = 0
        if prev_row:
            content = [prev_row] + content
            start_row = 1

        for r in range(start_row, len(content)):
            checksum = sum(1 for word in content[r] if word)
            if checksum == 1:
                for word in content[r]:
                    if word:
                        content[r] = [word]
                        break
                continue
            for c in range(C):
                if content[r][c] not in ['', None, '-']:
                    content[r][c] = content[r][c].replace('\n', ' ')
                    continue
                elif content[r][c] == None and r > 0:
                    content[r][c] = content[r - 1][c]
                else:
                    content[r][c] = ''

        text = ''

        for r in range(start_row, len(content)):
            if len(content[r]) == 1:
                text += content[r][0] + '\n'
                continue
            line = ''
            for c in range(C):
                if content[r][c]:
                    line += f'{header[c]}: {content[r][c]}; '
            line = line.strip()
            if line:
                text += line + '\n'
        
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        if return_last_row:
            return text, content[-1]
        return text
    
    def extract_header(self, table: List[List[Optional[str]]]) -> List[List[str]]:
        C = len(table[0])
        encoded_header = []
        for r, row in enumerate(table):
            encoded_row = [0 for _ in range(C)]
            end = False
            for c, word in enumerate(row):
                if word:
                    encoded_row[c] = 1
                elif r == 0:
                    if c == 0:
                        end = True
                        break
                    encoded_row[c] = encoded_row[c - 1] + 1
                elif c == 0:
                    encoded_row[c] = encoded_header[r - 1][c]
                else:
                    encoded_row[c] = encoded_row[c - 1] + 1
                    if encoded_row[c] > encoded_header[r - 1][c]:
                        end = True
                        break
            if end:
                break
            if len(encoded_header) > 0:
                if encoded_row == encoded_header[-1]:
                    return []
            encoded_header.append(encoded_row)
            if sum(encoded_row) == C:
                break
        if len(encoded_header) == 0:
            return ''
        decoded_header = [['' for _ in range(C)] for _ in range(len(encoded_header))]
        for r, encoded_row in enumerate(encoded_header):
            for c, code in enumerate(encoded_row):
                if code == 1:
                    decoded_header[r][c] = table[r][c]
                    if not decoded_header[r][c]:
                        decoded_header[r][c] = decoded_header[r - 1][c]
                else:
                    decoded_header[r][c] = decoded_header[r][c - 1]
        return decoded_header
                    