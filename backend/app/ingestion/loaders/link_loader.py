import json
import requests
from bs4 import BeautifulSoup
from collections import deque
from .base_loader import BaseLoader
from typing import List
from langchain.schema import Document

class LinkLoader(BaseLoader):
    def __init__(
        self,
        file_path: str
    ):
        super().__init__()
        self.file_path = file_path
    
    def load(self) -> List[Document]:
        stack = deque()
        loaded = set()
        docs = []

        with open(self.file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            pending_links = config.get('pending', [])
            ignore_links = config.get('ignore', [])
            title_tagnames = config.get('title_tagnames', [])
            title_classnames = config.get('title_classnames', [])
            main_tagnames = config.get('main_tagnames', [])
            main_classnames = config.get('main_classnames', [])
            base_url = config.get('base', '')
            stack.extend([{
                'link': link,
                'categories': []
            } for link in pending_links])
            loaded.update(ignore_links)

        while stack:
            item = stack.pop()
            link = item['link']
            print(link)
            categories = item['categories']
            if link in loaded:
                continue
            loaded.add(link)
            try:
                res = requests.get(link, timeout=5)
            except requests.exceptions.RequestException as e:
                print(e)
                continue
            if res.url != link:
                link = res.url
                if link in loaded:
                    continue
                loaded.add(link)

            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            main = soup.find(main_tagnames, class_=main_classnames)
            if not main:
                continue
            title = None
            if title_tagnames and title_classnames:
                title_tag = main.find(title_tagnames, class_=title_classnames)
                if title_tag:
                    title = title_tag.get_text(strip=True, separator=' ')
            
            if categories and title == categories[-1]:
                del categories[-1]
            
            docs.append(Document(
                page_content=link,
                metadata={
                    'categories': categories
                }
            ))
            categories = categories + [title]
            a_tags = main.find_all('a')
            for a_tag in a_tags:
                href = a_tag.get('href')
                if href and href.startswith(base_url) and href not in loaded:
                    stack.append({
                        'link': href,
                        'categories': categories
                    })

        return docs