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
class Scraper:
    url: str = None
    site_name: str = None
    page_title: str = None
    endless_scroll: bool = False
    endless_scroll_time: int = 5
    driver: WebDriver = None
    html_obj: HTML = None

    def __post_init__(self):
        if self.page_title and self.site_name == 'dubawa':
            self.url = f'https://dubawa.org/{slugify(self.page_title)}'

        if self.page_title and self.site_name == 'africacheck':
            self.url = f'https://africacheck.org/fact-checks/reports/{slugify(self.page_title)}'

        if self.page_title and self.site_name == 'thecable':
            self.url = f'https://www.thecable.ng/{slugify(self.page_title)}'

        if self.page_title and self.site_name == 'factcheckghana':
            self.url = f'https://www.fact-checkghana.com/{slugify(self.page_title)}'

        if not self.page_title or not self.url:
            raise Exception(f'page title or url required')

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

    def extract_element_text(self, element_id):
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id, first=True)
        if not el:
            return ''
        return el.text

    def extract_element_src(self, element_id):
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id, first=True)
        if not el:
            return ''
        return el.attrs['src']

    def dubawa_extract_claim(self, element_id):
        """
        returns a list of claims
        """
        claim_list = []
        html_obj = self.get_html_obj()
        el = html_obj.find(element_id)
        for claim in el:
            claim_list.append(claim.text)
        return claim_list

    def dubawa_extract_verdicts(self) -> dict:
        html_obj = self.get_html_obj()
        verdict_dataset = {}
        verdict_list = []
        verdict_tag = []
        verdicts_key = html_obj.find('.has-background')
        verdicts_value = html_obj.find('.alignright img')

        for i, v_strong in enumerate(verdicts_key):
            if i % 2 != 0:
                key = v_strong.text
                verdict_list.append(key)
        for src in verdicts_value:
            image = src.attrs['src'].lower()
            verdict = image.split('/')[-1].split('-')[0]
            verdict_tag.append(verdict)
        verdict_tag = list(set(verdict_tag))
        for i, key in enumerate(verdict_list):
            try:
                verdict_dataset[key] = verdict_tag[i]
            except:
                pass
        return verdict_dataset

    def dubawa_scrape(self):
        html_obj = self.get_html_obj()
        title = self.extract_element_text('.post-title')
        author = self.extract_element_text('.author-name')
        page_date = self.extract_element_text('.date')
        page_banner = self.extract_element_src('.wp-post-image')
        claim = self.dubawa_extract_claim(
            '.has-cyan-bluish-gray-background-color')
        verdicts = self.dubawa_extract_verdicts()
        return {
            'title': title,
            'author': author,
            'page_date': page_date,
            'page_banner': page_banner,
            'claim': claim,
            'verdicts': verdicts
        }

    def factcheckghana_extract_claim(self, element_id):
        """
        returns a list of claims
        """
        html_obj = self.get_html_obj()
        claim_list = []
        claim = self.extract_element_text(html_obj, element_id)
        claim_list.append(claim)
        return claim_list

    def factcheckghana_extract_verdicts(self) -> dict:
        verdicts_dict = {}
        html_obj = self.get_html_obj()
        g_verdict = html_obj.find('.tdb-title-text', first=True).text
        for word in slugify(g_verdict.lower()).split('-'):
            if word == 'factbox' or word == 'fact' or word == 'facts':
                verdicts_dict['fact'] = 'True'
            elif word == 'false' or word == 'not':
                verdicts_dict['false'] = 'False'
            elif word == 'misleading':
                verdicts_dict['misleading'] = 'Misleading'
        return verdicts_dict

    def factcheckghana_scrape(self):
        html_obj = self.get_html_obj()
        title = self.extract_element_text('.tdb-title-text')
        author = self.extract_element_text('.tdb-author-name')
        page_date = self.extract_element_text('.entry-date')
        page_banner = self.extract_element_src('.entry-thumb')
        claim = self.factcheckghana_extract_claim('.tdb-block-inner p strong')
        verdicts = self.factcheckghana_extract_verdicts()
        return {
            'title': title,
            'author': author,
            'page_date': page_date,
            'page_banner': page_banner,
            'claim': claim,
            'verdicts': verdicts
        }
