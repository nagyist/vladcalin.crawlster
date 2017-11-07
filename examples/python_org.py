import pprint

from crawlster.core import Crawlster
from crawlster.config import Configuration
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

    item_handler = LogItemHandler()

    def step_start(self, url):
        data = self.http.make_request('get', url)
        if not data:
            return
        self.urls.mark_seen(url)
        hrefs = self.extract.css(data.content, 'a', attr='href')
        base = self.urls.get_base(url)
        full_links = self.urls.join_paths(base, hrefs)
        for link in full_links:
            if '#' in link:
                continue
            self.schedule(self.process_page, link)

    def process_page(self, url):
        resp = self.http.get(url)
        if not self.looks_like_module_page(resp.content):
            return
        module_name = self.extract.css(resp.content,
                                       'h1 a.reference.internal code span')
        return {'name': module_name.text}

    def looks_like_module_page(self, page_content):
        return b'Source code:' in page_content


if __name__ == '__main__':
    crawler = PythonOrgCrawler()
    crawler.start()
    pprint.pprint(crawler.stats.dump())
