#!/usr/bin/env python3

from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
import re

@dataclass
class AdvancedSearchType:
    SKRIPSI: int = 4
    THESIS: int = 5
    TA: int = 6
    # ... and so on

class OpenLibrary:
    base_url: str = "https://openlibrary.telkomuniversity.ac.id"
    
    def __init__(self):
        self.session = requests.Session()

    def get_all_data_from_range_date(self, **search_options) -> str:
        response = self.session.post(f'{self.base_url}/home/catalog.html', data=search_options)
        response.raise_for_status()

        return response.text
    
    def get_pagination(self, content: str) -> list:
        parsed = BeautifulSoup(content, "html.parser")
        
        paginations = parsed \
            .find("div", class_="pagination-imtelkom") \
            .find_all("li")
        
        result = [] 
        
        for page in paginations:
            url = self.base_url + page.find('a')['href']
            if url not in result:
                result.append(url)
                
        return result
    
    def get_search_result(self, content: str) -> list:
        paginations = self.get_pagination(content)
        
        results = []
        
        for pagination in paginations:
            content = self.session.get(pagination).text
            
            parsed = BeautifulSoup(content, "html.parser")
                
            search_results = parsed.find("div", class_="row row-imtelkom") \
                                   .find("div", class_="col-md-9") \
                                   .find_all("div", class_="col-md-6 col-sm-6 col-xs-12")
            
            pages = []
            
            for result in search_results:
                result_url = result \
                                .find('div', class_='media-body') \
                                .find('h4', class_='media-heading') \
                                .find('a') \
                                .get('href')
                
                pages.append(self.base_url + result_url)
                    
            results.extend(pages)
                    
        return results
    
    def parse_results(self, content: str) -> set:
        urls = self.get_search_result(content)
        length = len(urls)
        
        for i in range(len(urls)):            
            response = self.session.get(urls[i]).text
            
            yield i+1, length, self.parse_result(response)
            
    def parse_result(self, content):
        parsed = BeautifulSoup(content, "html.parser")
        
        header = parsed \
                    .find("div", class_="page-header page-header-imtelkom") \
                    .find("h1") \
                    .find(text=True, recursive=False)
        
        result = {}
        result["title"] = header

        catalog_attributes = parsed.find_all("div", class_="catalog-attributes")
        
        subject = catalog_attributes[0] \
                    .find("div", class_="col-md-3 col-sm-8 col-xs-12") \
                    .find_all("p")[-1] \
                    .get_text() \
                    .strip()
                    
        result["subject"] = self.remove_html_tags(subject)

        abstract = catalog_attributes[0] \
                    .find("div", class_="col-md-7 col-sm-12 col-xs-12") \
                    .find("p") \
                    .find_all("p")
        
        keywords = abstract[-1].get_text().strip()
        
        abstract = abstract[:-1]
        abstract = "\n".join([a.get_text().strip() for a in abstract])

        result["abstract"] = self.remove_html_tags(abstract)
        result["keywords"] = self.remove_html_tags(keywords)

        authors_info, publisher_info, _ = catalog_attributes[1].find_all("div", class_="col-md-4 col-sm-4 col-xs-12")  
        
        get_table_row = lambda elm: elm.find("table").find_all("tr")
        parse_elm = lambda elm: elm.find_all("td")[1].get_text().strip()
        
        author, type, lecturer, translator = get_table_row(authors_info)
        publisher_name, publisher_city, publish_year = get_table_row(publisher_info)

        result["author"] = parse_elm(author)
        result["lecturer"] = parse_elm(lecturer)
        result["publisher"] = parse_elm(publisher_name)
        result["publish_year"] = parse_elm(publish_year)
        
        return result
    
    def remove_html_tags(self, text: str) -> str:
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
