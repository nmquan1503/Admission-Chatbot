import requests
from bs4 import BeautifulSoup, Tag
from .base_loader import BaseLoader
import re
from typing import List, Dict, Any, Optional
from langchain.schema import Document

class WebLoader(BaseLoader):

    def __init__(
        self, 
        url: str, 
        metadata: Optional[Dict[str, Any]]=None,
        **kwargs
    ):
        super().__init__()
        self.url = url
        self.metadata = metadata
        self.main_tagnames = kwargs.get('main_tagnames', None)
        self.main_classnames = kwargs.get('main_classnames', None)
        self.title_tagnames = kwargs.get('title_tagnames', None)
        self.title_classnames = kwargs.get('title_classnames', None)
        self.pagination_bar_tagnames = kwargs.get('pagination_bar_tagnames', None)
        self.pagination_bar_classnames = kwargs.get('pagination_bar_classnames', None)
        self.article_title_tagnames = kwargs.get('article_title_tagnames', None)
        self.article_title_classnames = kwargs.get('article_title_classnames', None)
    
    def load(self) -> List[Document]:
        try:
            response = requests.get(self.url, timeout=5)
        except requests.exceptions.RequestException as e:
            print(e)
            return []
        
        html = BeautifulSoup(response.text, 'html.parser')
        
        if self.main_tagnames and self.main_classnames:
            main = html.find(self.main_tagnames, class_=self.main_classnames)
        else:
            main = html.find('body')
        
        if self.pagination_bar_tagnames and self.pagination_bar_classnames:
            self.remove_pagination_bar(
                main=main,
                bar_tagnames=self.pagination_bar_tagnames,
                bar_classnames=self.pagination_bar_classnames
            )
        
        if self.title_tagnames and self.title_classnames:
            title = main.find(self.title_tagnames, class_=self.title_classnames)
            new_metadata = self.extract_metadata(title=title.get_text(strip=True, separator=' '))
            title.decompose()
        else:
            new_metadata = None
        
        self.handle_iframes(main=main)

        if self.article_title_tagnames and self.article_title_classnames:
            self.handle_articles(
                main=main,
                title_tagnames=self.article_title_tagnames,
                title_classnames=self.article_title_classnames
            )
        
        self.handle_a_tags(main=main)

        self.handle_tables(main=main)

        self.convert_to_p(
            main=main,
            tagnames=['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']
        )

        content = main.get_text(strip=True, separator='\n')
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\n+', '\n', content)

        if new_metadata:
            self.metadata = self.merge_metadata(self.metadata, new_metadata)

        return [Document(
            page_content=content,
            metadata=self.metadata
        )]

    def extract_metadata(
        self,
        title: str,
    ) -> Optional[Dict[str, Any]]:
        if not title:
            return None
        
        metadata = {
            'title': title
        }

        years = re.findall(r'20\d{2}', title)
        if not years:
            return metadata
        years = [int(year) for year in years]
        metadata['years'] = years
        
        return metadata

    def remove_pagination_bar(
        self,
        main: Tag,
        bar_tagnames: List[str],
        bar_classnames: List[str]
    ) -> None:
        pagnination_bar = main.find(bar_tagnames, class_=bar_classnames)
        if pagnination_bar:
            pagnination_bar.decompose()
    
    def handle_tables(
        self,
        main: Tag,
    ) -> None:
        table_tags = main.find_all('table')
        if not table_tags:
            return
        for table_tag in table_tags:
            blocks = [[block for block in row.find_all('td')] for row in table_tag.find_all('tr')]
            R = len(blocks)
            C = sum([int(block.get('colspan')) if block.get('colspan') else 1 for block in blocks[0]])
            all_texts = [['' for _ in range(C)] for _ in range(R)]
            num_header_row = max([int(block.get('colspan', 1)) for block in blocks[0]])
            for row_id, row in enumerate(blocks):
                col_id = 0
                while col_id < C:
                    if not all_texts[row_id][col_id]:
                        break
                    col_id += 1

                for block in row:
                    rowspan = int(block.get('rowspan', 1))
                    colspan = int(block.get('colspan', 1))
                    text = block.get_text(strip=True, separator=', ')
                    text = text.replace(':', ' - ')
                    text = re.sub(r'\s+', ' ', text)
                    for i in range(rowspan):
                        for j in range(colspan):
                            all_texts[row_id + i][col_id + j] = text
                    col_id += colspan
            
            header = all_texts[:num_header_row]
            header = [' - '.join(list(dict.fromkeys(items))) for items in zip(*header)]
            body = all_texts[num_header_row:]

            text = ''

            for row in body:
                row_text = ''
                for col_id, col in enumerate(row):
                    row_text += f'{header[col_id]} : {col}; '
                text += row_text.strip() + '\n'
            
            p_tag = Tag(name='p')
            p_tag.string = text

            table_tag.replace_with(p_tag)
    
    def handle_a_tags(
        self,
        main: Tag
    ) -> None:
        a_tags = main.find_all('a')
        for a_tag in a_tags:
            href = a_tag.get('href')
            text = a_tag.get_text(strip=True, separator=' ')
            if href:
                if href.endswith(('.jpg', '.png')):
                    a_tag.decompose()
                else:
                    text += f' ({href})'
            span_tag = Tag(name='span')
            span_tag.string = text

            a_tag.replace_with(span_tag)

    def handle_articles(
        self,
        main: Tag,
        title_tagnames: List[str],
        title_classnames: List[str]
    ) -> None:
        article_tags = main.find_all('article')
        for article_tag in article_tags:
            title = article_tag.find(title_tagnames, class_=title_classnames)
            if not title:
                continue
            a_tag = title.find('a')
            if not a_tag:
                continue
            text = a_tag.get_text(strip=True, separator=' ')
            link = a_tag.get('href')
            if link:
                text += f' ({link})'
            p_tag = Tag(name='p')
            p_tag.string = text
            article_tag.replace_with(p_tag)
    
    def handle_iframes(
        self,
        main: Tag,    
    ):
        iframes = main.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            text = iframe.get_text(strip=True, separator=' - ')
            if not src:
                iframe.decompose()
            else:
                p_tag = Tag(name='p')
                p_tag.string = f'Video ( {src} )'
                iframe.replace_with(p_tag)

    def convert_to_p(
        self,
        main: Tag, 
        tagnames: List[str]
    ) -> None:
        tags = main.find_all(tagnames)
        if not tags:
            return
        for tag in tags:
            text = tag.get_text(separator=' ', strip=True)
            p_tag = Tag(name='p')
            p_tag.string = text
            tag.replace_with(p_tag)

            

        
        