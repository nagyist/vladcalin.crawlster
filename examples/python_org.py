import pprint

from crawlster.core import Crawlster
from crawlster.config import Configuration
from crawlster.handlers.jsonl import JsonLinesHandler
from crawlster.handlers.log_handler import LogItemHandler


class PythonOrgCrawler(Crawlster):
    """
    This is an example crawler used to crawl info about all the Python modules
    """
    config = Configuration({
        'core.start_step': 'step_start',
        'core.start_urls': [
            'https://docs.python.org/3/library/index.html'],
        'log.level': 'debug',
        'pool.workers': 3
    })

    item_handler = [LogItemHandler(), JsonLinesHandler('pymodules.jsonl')]

    def step_start(self, url):
        data = self.http.get(url)
        if not data:
            return
        self.urls.mark_seen(url)
        hrefs = self.extract.css(data.content, 'a', attr='href')
        self.log.warning(hrefs)
        full_links = self.urls.join_paths(url, hrefs)
        self.log.warning(full_links)
        for link in full_links:
            if '#' in link:
                continue
            self.schedule(self.process_page, link)

    def process_page(self, url):
        if not self.urls.can_crawl(url):
            return
        resp = self.http.get(url)
        self.urls.mark_seen(url)
        if not self.looks_like_module_page(resp.content):
            return
        module_name = self.extract.css(resp.content,
                                       'h1 a.reference.internal code span')
        for res in module_name:
            self.submit_item({'name': res.text, 'url': url})

    def looks_like_module_page(self, page_content):
        return b'Source code:' in page_content


if __name__ == '__main__':
    crawler = PythonOrgCrawler()
    crawler.start()
    pprint.pprint(crawler.stats.dump())
