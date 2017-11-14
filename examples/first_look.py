import crawlster
from crawlster.handlers import JsonLinesHandler


class MyCrawler(crawlster.Crawlster):
    config = crawlster.Configuration({
        'core.start_urls': ['https://www.python.org/events/'],
        'core.start_step': 'step_start'
    })
    item_handler = JsonLinesHandler('items.jsonl')

    def step_start(self, url):
        resp = self.http.get(url)
        events = self.extract.css(resp.text, 'h3.event-title a', content=True)
        for event_name in events:
            self.submit_item({'event': event_name})


if __name__ == '__main__':
    crawler = MyCrawler()
    crawler.start()
    print(crawler.stats.dump())
