from crawlster.config import Configuration
from crawlster.core import Crawlster


def test_crawler_init():
    class MyCrawler(Crawlster):
        config = Configuration({
            'core.start_step': 'step_start',
            'core.start_urls': ['https://python.org']
        })

        def step_start(self, url):
            pass

    crawler = MyCrawler()
    crawler.start()

    assert False
