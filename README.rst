crawlster
=========

.. image:: https://readthedocs.org/projects/crawlster/badge/?version=latest
   :target: http://crawlster.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

A simple crawler framework

.. note::

    This is a work in progress



Features:

- HTTP crawling
- Various data extraction methods (regex, css selectors, xpath)
- Very configurable and extensible


What is crawlster?
------------------

Crawlster is a web crawling library designed to save precious development
time. It is very extensible and provides many shortcuts for the most common
tasks in a web crawler, such as HTTP request sending and parsing and info
extraction.


Installation
------------

From PyPi:

::

    pip install crawlster


From source:

::

    git clone https://github.com/vladcalin/crawlster.git
    cd crawlster
    python setup.py install


Quick example
-------------

This is the hello world equivalent for this library:

::

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

Running the above code will fetch the event names from python.org and save them
in a ``items.jsonl`` file in the current directory.

Let's see what did we do there:

::

    import crawlster
    from crawlster.handlers import JsonLinesHandler

We import the crawlster module and the JsonLinesHandler that will be used to
save the items to the ``items.jsonl`` file

::

    class MyCrawler(crawlster.Crawlster):

We subclass the :py:class:`Crawlester` base class to create a crawler.

::

    config = crawlster.Configuration({
        'core.start_urls': ['https://www.python.org/events/'],
        'core.start_step': 'step_start'
    })

We declare the configuration for the crawler. The ``core.start_urls`` must
be a list of urls with which the crawling will start and ``core.start_step``
must be the name of the method that will first be invoked.

::

    def step_start(self, url):

We declare the ``step_start`` handler. The first step will always receive a
url from which it should start fetching and parsing the response. This method
will be called once for every starting url provided by ``core.start_urls``.

::

    resp = self.http.get(url)

We make a GET request to that url by using the ``.http`` helper. We will talk
about helpers later.

::

    events = self.extract.css(resp.text, 'h3.event-title a', content=True)

We extract the event titles by using the ``.extract`` helper. This helper provides
a convenient way to parse and extract data from a http document using query selectors.
By passing ``content=True`` we receive only the text/content from the selected
elements (not passing content will cause it to return the whole elements as a list
of strings and there is an extra ``attr`` keyword argument with which we specify that
we are interested only in the value of a certain attribute.

::

    for event_name in events:
        self.submit_item({'event': event_name})

For every result extracted, we submit it as an item. Every item is a ``dict``
instance and we use the ``submit_item`` method of ``crawlster.Crawlster`` base
class to submit it. Every item pushed through this method is then pushed to the
item handlers (``JsonLinesHandler`` in our case).

::

    if __name__ == '__main__':
        crawler = MyCrawler()
        crawler.start()
        print(crawler.stats.dump())

Here we start the crawler and wait for it to finish. In the end, we can
access a variety of crawling stats, such as how many requests were made, how
many items were submitted, how long the crawl took and others.

For more advanced usage, consult the documentation.

Helpers
-------

A helper is a utility class that provides certain functionality. The ``Crawlster``
class requires the ``.log``, ``.stats``, ``.http`` and ``.queue`` helpers
to be provided (and are by default) for internal behaviour. These are called
*core helpers*

Also, besides the core helpers, the ``Crawlster`` class also provides the ``.urls``,
``.extract`` and ``.regex`` helpers for common tasks.

You can also create other helpers and attach them to the crawler to enhance it.
