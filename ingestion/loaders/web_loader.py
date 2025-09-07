import requests
from bs4 import BeautifulSoup, Tag
from .base_loader import BaseLoader
import re
from typing import List, Dict

class WebLoader(BaseLoader):
    
    def load(self, source: str, metadata: dict=None, **kwargs):
        main_tagnames = kwargs.get('main_tagnames', None)
        main_classnames = kwargs.get('main_classnames', None)
        title_tagnames = kwargs.get('title_tagnames', None)
        title_classnames = kwargs.get('title_classnames', None)
        pagination_bar_tagnames = kwargs.get('pagination_bar_tagnames', None)
        pagination_bar_classnames = kwargs.get('pagination_bar_classnames', None)
        article_title_tagnames = kwargs.get('article_title_tagnames', None)
        article_title_classnames = kwargs.get('article_title_classnames', None)

        try:
            response = requests.get(source, timeout=5)
        except requests.exceptions.RequestException as e:
            print(e)
            return {
                'content': None, 
                'metadata': None 
            }
        
        html = BeautifulSoup(response.text, 'html.parser')
        
        if main_tagnames and main_classnames:
            main = html.find(main_tagnames, class_=main_classnames)
        else:
            main = html.find('body')
        
        if pagination_bar_tagnames and pagination_bar_classnames:
            self.remove_pagination_bar(
                main=main,
                bar_tagnames=pagination_bar_tagnames,
                bar_classnames=pagination_bar_classnames
            )
        
        if title_tagnames and title_classnames:
            new_metadata = self.extract_metadata(
                main=main,
                title_tagnames=title_tagnames,
                title_classnames=title_classnames
            )
        else:
            new_metadata = None
        
        if article_title_tagnames and article_title_classnames:
            self.handle_articles(
                main=main,
                title_tagnames=article_title_tagnames,
                title_classnames=article_title_classnames
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
            metadata = self.merge_metadata(metadata, new_metadata)

        return {
            'content': content,
            'metadata': metadata
        }

    def extract_metadata(
        self,
        main: Tag,
        title_tagnames: str | List[str],
        title_classnames: str | List[str],
    ) -> Dict:
        title = main.find(title_tagnames, class_=title_classnames)

        if not title:
            return None
        
        text = title.get_text(separator=' ')
        years = re.findall(r'20\d{2}', text)

        if not years:
            return None
        
        years = [int(year) for year in years]

        return {
            'years': years
        }
        

    def remove_pagination_bar(
        self,
        main: Tag,
        bar_tagnames: str | List[str],
        bar_classnames: str | List[str]
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
        title_tagnames: str | List[str],
        title_classnames: str | List[str]
    ) -> None:
        article_tags = main.find_all('article')
        for article_tag in article_tags:
            title = article_tag.find(title_tagnames, class_=title_classnames)
            a_tag = title.find('a')
            text = a_tag.get_text(strip=True, separator=' ')
            link = a_tag.get('href')
            if link:
                text += f' ({link})'
            p_tag = Tag(name='p')
            p_tag.string = text
            article_tag.replace_with(p_tag)
    
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

            

        
        