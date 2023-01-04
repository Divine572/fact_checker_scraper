import time
from dataclasses import dataclass
from fake_useragent import UserAgent



import re
from requests_html import HTML
from slugify import slugify


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


def get_user_agent():
    return UserAgent(verify_ssl=False).random





@dataclass
class Scrapper:
    url: str = None
    site_name: str = None
    page_title: str = None
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    driver: WebDriver = None
    html_obj: HTML = None
    
    def __init__(self):
        if self.site_name == 'dubawa':
            self.page_title = slugify(self.page_title)
            self.url = f'https://dubawa.org/{self.page_title}'
            
        if self.site_name == 'africacheck':
            self.page_title = slugify(self.page_title)
            self.url = f'https://africacheck.org/fact-checks/reports/{self.page_title}'
            
        if self.site_name == 'cableng':
            self.page_title = slugify(self.page_title)
            self.url = f'https://www.thecable.ng/{self.page_title}'
            
        # if self.site_name == 'afpfactcheck':
        #     self.page_title = slugify(self.page_title)
        #     self.url = f'https://www.thecable.ng/{self.page_title}'
        
        if self.site_name == 'factcheckghana':
            self.page_title = slugify(self.page_title)
            self.url = f'https://www.fact-checkghana.com/{self.page_title}'
            
        
        if not self.site_name or self.url:
            raise Exception('Site name or url required')
        
        
        
