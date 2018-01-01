Tutorial
========

We will build a crawler from scratch in which we will use all the major
features of this framework. We are going to write a crawler for the python.org
documentation which will extract items containing the name of the module and
the url for the documentation of that module for all standard libs.

You can find the example in ``examples/python_org.py``.

Firstly, import the required modules

::

    from crawlster import Crawlster, start, Configuration
    from crawlster.handlers.jsonl import JsonLinesHandler
    from crawlster.handlers.log_handler import LogItemHandler



- :py:class:`crawlster.Crawlster` is the base class which the our crawler will inherit
- :py:func:`crawlster.start` is a decorator for specifying the first step that will be
  executed
- :py:class:`crawlster.handlers.JsonLinesHandler` is the item handler that will write all found
  items (results) to a json files, one per line
- :py:class:`crawlster.handlers.LogItemHandler` is the item handler that will write all found
  items to the console

Next, we need to start implementing the crawler class and configure it

::

    class PythonOrgCrawler(Crawlster):
    """
    This is an example crawler used to crawl info about all the Python modules
    """
    item_handler = [LogItemHandler(),
                    JsonLinesHandler('items.jsonl')]

Here, we subclass the ``Crawlster`` base class and provide the ``item_handler``
attribute as a list of item handlers. When we submit an item, it will pe passed
to each item handler in the order they are defined.

Next, we will start implementing the start step

::

    @start
    def step_start(self, url):
        data = self.http.get(url)
        if not data:
            return

Here we decorate the ``step_start`` method to be used as entry point for the
crawling process, then we fetch the start url using the core ``http`` helper
(see :py:class:`crawlster.helpers.RequestsHelper`). If data is ``None`` it means
the request failed, so we return immediately.

Then we parse and extract data from the response

::

        self.urls.mark_seen(url)
        hrefs = self.extract.css(data.body, 'a', attr='href')
        full_links = self.urls.multi_join(url, hrefs)

Here, with the ``urls`` core helper we mark the url as being seen so that it will
not be processed multiple times (the python docs contain a lot of cross references
between pages). Read more on it on :py:class:`crawlster.helpers.UrlsHelper`.

Then we go on an extract from the body only the content of the ``href`` attributes
of all ``a`` elements. The ``extract`` helper provides the ``css`` method which we
use to select all relevant elements from the content of the page (the anchors) and
then return only the part that we need, the ``href`` attribute.

After that, there is a high chance that all the extracted content are the paths
of the final url (eg. ``/path/to/some/page.html``) and we need to convert them to
full url (``https://python.org/path/to/some/page.html``). The ``urls`` helper
has a method which performs urljoins on elements from a list at once.

Next we need to schedule the next steps in the crawling process

::

    for link in full_links:
        if '#' in link:
            continue
        self.schedule(self.process_page, link)

For each extracted link, we send it to ``self.process_page`` to process it.
We do that using the :py:meth:`crawlster.Crawlster.schedule` method because
all steps are executed in parallel, inside workers that run in separate threads.

Next, we need a way to tell if the current page represents a module reference page.

::

    def looks_like_module_page(self, page_content):
        return b'Source code:' in page_content

I know, kind of lame but hey... it does the job!

Next, we do all the request fetching thing again, in the next step's method

::

    def process_page(self, url):
        if not self.urls.can_crawl(url):
            return
        resp = self.http.get(url)
        self.urls.mark_seen(url)

This time we check of the current page can be crawler (in other words, if it has
been already crawled). We don't want to get stuck in an infinite loop because
of the numerous cross references between pages.

Then, we check if the page is a module reference page using the method
defined earlier

::

        module_name = self.extract.css(resp.body,
                                       'h1 a.reference.internal code span',
                                       content=True)
        if not module_name:
            return
        self.submit_item({'name': module_name[0], 'url': url})

So what happens here is that we extract only the content from the elements.
In some cases, that elements does not exist, so we skip the page as it is not
a valid module page (eg. https://docs.python.org/3/library/idle.html ).

When finding a module name, we submit it and send it through the item handlers
with the :py:meth:`crawlster.Crawlster.submit_item` method.

The crawler class is done!

All that is left to do is starting it:

::

    if __name__ == '__main__':
        crawler = PythonOrgCrawler(Configuration({
            "core.start_urls": [
                "https://docs.python.org/3/library/index.html"
            ],
            "log.level": "debug",
            "pool.workers": 3,
        }))
        crawler.start()
        pprint.pprint(crawler.stats.dump())

There, we initialize the ``PythonOrgCrawler`` with a configuration.

- ``core.start_urls`` is a list of starting urls. The start step will be called
  once for each item in this list.
- ``log.level`` will set the logging level so that we'll see more in the console
  when we run the crawler.
- ``pool.workers`` will set the worker thread pool's size. For this example, a
  concurrency level of 3 is more than enough.

By calling the :py:meth:`crawlster.Crawlster.start` method we start the
crawling process and after that we we'll print some nice stats about what happened.

Now go to a terminal, and assuming you wrote the crawler in a ``python_org.py`` file,
run:

::

    python python_org.py

Now all should work and after approx. 15 seconds, it should finish.

There should be stats printed in console

::

    {'http.download': 16373171,
     'http.requests': 300,
     'http.upload': 0,
     'items': 185,
     'time.duration': 14.879282,
     'time.finish': datetime.datetime(2018, 1, 1, 17, 39, 5, 917190),
     'time.start': datetime.datetime(2018, 1, 1, 17, 38, 51, 37908)}

and the results should be in the ``items.jsonl`` file in the current directory

::

    (crawlster) vladcalin@mylaptop ~/crawlster $ tail items.jsonl
    {"name": "calendar", "url": "https://docs.python.org/3/library/calendar.html"}
    {"name": "struct", "url": "https://docs.python.org/3/library/struct.html"}
    {"name": "stringprep", "url": "https://docs.python.org/3/library/stringprep.html"}
    {"name": "textwrap", "url": "https://docs.python.org/3/library/textwrap.html"}
    {"name": "difflib", "url": "https://docs.python.org/3/library/difflib.html"}
    {"name": "collections", "url": "https://docs.python.org/3/library/collections.html"}
    {"name": "codecs", "url": "https://docs.python.org/3/library/codecs.html"}
    {"name": "string", "url": "https://docs.python.org/3/library/string.html"}
    {"name": "re", "url": "https://docs.python.org/3/library/re.html"}
    {"name": "datetime", "url": "https://docs.python.org/3/library/datetime.html"}

That's all! Have fun crawling (in a responsible manner)!

Here's the whole crawler code after putting everything together:

::

    import pprint

    from crawlster import Crawlster, start, JsonConfiguration, Configuration
    from crawlster.handlers.jsonl import JsonLinesHandler
    from crawlster.handlers.log_handler import LogItemHandler


    class PythonOrgCrawler(Crawlster):
        """
        This is an example crawler used to crawl info about all the Python modules
        """
        item_handler = [LogItemHandler(),
                        JsonLinesHandler('items.jsonl')]

        @start
        def step_start(self, url):
            data = self.http.get(url)
            if not data:
                return
            self.urls.mark_seen(url)
            hrefs = self.extract.css(data.body, 'a', attr='href')
            full_links = self.urls.multi_join(url, hrefs)
            for link in full_links:
                if '#' in link:
                    continue
                self.schedule(self.process_page, link)

        def process_page(self, url):
            if not self.urls.can_crawl(url):
                return
            resp = self.http.get(url)
            self.urls.mark_seen(url)
            if not self.looks_like_module_page(resp.body):
                return
            module_name = self.extract.css(resp.body,
                                           'h1 a.reference.internal code span',
                                           content=True)
            if not module_name:
                return
            self.submit_item({'name': module_name[0], 'url': url})

        def looks_like_module_page(self, page_content):
            return b'Source code:' in page_content


    if __name__ == '__main__':
        crawler = PythonOrgCrawler(Configuration({
            "core.start_urls": [
                "https://docs.python.org/3/library/index.html"
            ],
            "log.level": "debug",
            "pool.workers": 3,
        }))
        crawler.start()
        pprint.pprint(crawler.stats.dump())

