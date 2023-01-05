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
        if self.page_title and self.site_name == 'dubawa':
            self.page_title = self.extract_element_title(self)
            self.url = f'https://dubawa.org/{self.page_title}'

        if self.site_name and self.site_name == 'africacheck':
            self.page_title = slugify(self.page_title)
            self.url = f'https://africacheck.org/fact-checks/reports/{self.page_title}'

        if self.site_name and self.site_name == 'cableng':
            self.site_name = site_name
            self.page_title = slugify(self.page_title)
            self.url = f'https://www.thecable.ng/{self.page_title}'

        # if self.site_name and self.site_name == 'afpfactcheck':
        #     self.page_title = slugify(self.page_title)
        #     self.url = f'https://www.thecable.ng/{self.page_title}'

        if self.site_name and self.site_name == 'factcheckghana':
            self.page_title = slugify(self.page_title)
            self.url = f'https://www.fact-checkghana.com/{self.page_title}'

        if not self.site_name or self.url:
            raise Exception('Site name or url required')

    def get_driver(self):
        if self.driver is None:
            user_agent = get_user_agent()
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={user_agent}')
            driver = webdriver.Chrome(options=options)
            self.driver = driver
        return self.driver

    def perform_endless_scroll(self, driver=None):
        if driver is None:
            return
        if self.endless_scroll:
            current_height = driver.execute_script(
                'return document.body.scrollHeight')
            while True:
                driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(self.endless_scroll_time)
                iter_height = driver.execute_script(
                    'return document.body.scrollHeight')
                if current_height == iter_height:
                    break
                current_height = iter_height
        return
    
    def get(self):
        driver = self.get_driver()
        driver.get(self.url)
        if self.endless_scroll:
            self.perform_endless_scroll(driver=driver)
        else:
            time.sleep(10)
        return driver.page_source
    
    def get_html_obj(self):
        if self.html_obj is None:
            html_str = self.get()
            self.html_obj = HTML(html=html_str)
        return self.html_obj
    
    def extract_element_title(self, element_class):
        el = ''
        html_obj = self.get_html_obj()
        if self.site_name == 'dubawa':
            element_class = '.post-title'
            el = html_obj.find(element_class, first=True)
        if self.site_name == 'africacheck':
            element_class = '.page-title'
            el = html_obj.find(element_class, first=True)
        if self.site_name == 'cableng':
            element_class = '.article-title'
            el = html_obj.find(element_class, first=True)
        if self.site_name == 'factcheckghana':
            element_class = '.tdb-title-text'
            el = html_obj.find(element_class, first=True)
        if self.site_name == '':
            return el
        return el.text
