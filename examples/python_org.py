import time

from crawlster.core import Crawlster
from crawlster.config import Configuration


class PythonOrgCrawler(Crawlster):
    config = Configuration({
        'core.start_step': 'step_start',
        'core.start_urls': ['https://python.org'],
        'log.level': 'debug',
        'pool.workers': 3
    })

    def step_start(self, url):
        page = self.http.make_request('get', url)
        time.sleep(0.7)
        links = self.extract.css(page.content, 'a', attr='href')
        base = self.urls.get_base(url)
        full_links = self.urls.join_paths(base, links)
        for link in full_links:
            self.schedule(self.process_sublink, link)

    def process_sublink(self, url):
        print(url)


if __name__ == '__main__':
    PythonOrgCrawler().start()
