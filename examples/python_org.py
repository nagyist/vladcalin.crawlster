import pprint

from crawlster.core import Crawlster
from crawlster.config import Configuration
from crawlster.handlers.log_handler import LogItemHandler


class PythonOrgCrawler(Crawlster):
    config = Configuration({
        'core.start_step': 'step_start',
        'core.start_urls': [
            'https://www.python.org/downloads/'],
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
            if self.urls.has_extension(link, (
                    'exe', 'tar.gz', 'tgz', 'tar.xz', 'pkg', 'chm', 'zip',)):
                self.schedule(self.process_download, link)

    def process_download(self, link):
        if link.endswith('.exe'):
            raise ValueError('Invalid extension')
        return {
            'url': link,
            'type': link.split('.')[-1]
        }


if __name__ == '__main__':
    crawler = PythonOrgCrawler()
    crawler.start()
    pprint.pprint(crawler.stats.dump())
