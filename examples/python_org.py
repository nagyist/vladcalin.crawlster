import time

from crawlster.core import Crawlster
from crawlster.config import Configuration


class PythonOrgCrawler(Crawlster):
    config = Configuration({
        'core.start_step': 'step_start',
        'core.start_urls': ['https://python.org'],
        'log.level': 'debug'
    })

    def step_start(self, url):
        page = self.requests.session.get(url)
        print(page)


if __name__ == '__main__':
    PythonOrgCrawler().start()
