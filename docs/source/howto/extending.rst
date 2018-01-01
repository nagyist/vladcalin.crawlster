Extending the crawler with helpers
==================================

The ``crawlster`` library makes very easy to extend the functionality
of the crawler through helpers. A helper is only a utility class that is
attached to the crawler instance.

Core helpers:

- :py:class:`crawlster.helpers.RequestsHelper` available as ``http``.
- :py:class:`crawlster.helpers.UrlsHelper` available as ``urls``.
- :py:class:`crawlster.helpers.ExtractHelper` available as ``extract``.
- :py:class:`crawlster.helpers.StatsHelper` available as ``stats``.
- :py:class:`crawlster.helpers.LoggingHelper` available as ``log``.
- :py:class:`crawlster.helpers.QueueHelper` available as ``queue``.
- :py:class:`crawlster.helpers.RegexHelper` available as ``regex``.


Create your own helper
----------------------

In order to create your own helper to enhance your crawler with super powers
you need to subclass the :py:class:`crawlster.helpers.BaseHelper` base class.

Then you can start implementing the functionality you need.


Methods
-------

There is no required method that has to be overwritten, but there are some
methods that can be overwritten to act as hooks. So far the only two
available hooks are

- :py:meth:`crawlster.helpers.BaseHelper.initialize` that performs actions
  on crawler start.
- :py:meth:`crawlster.helpers.BaseHelper.finalize` that performs actions
  on crawler stop (when there are no more items to process).


Configuration
-------------

Helpers can take advantage of the configuration system the library provides by
providing the ``config_options`` attribute, a mapping of option name and
option value.


Attributes
----------

The two attributes that are available inside the helper are
``config`` and ``crawler``.

The ``config`` attribute will hold the ``Configuration`` instance used to
initialize the crawler. You can get values from the configuration using
the ``self.config.get(option_name)`` method.

The ``crawler`` attribute holds the current crawler instance through which
the helper can access other helpers. Although it is recommended to make
the helper as independent as possible, sometimes you would need to use
the functionality already provided by some already existent helper (stats
aggregation, logging, etc).

Attaching the helper to the crawler
-----------------------------------

In the crawler definition, provide the helper instance as a class attribute


::

    class MyCrawler(Crawlster):

        my_helper = MyHelperClass()

    # ...

    def some_step(self, url):
        # ...
        self.my_helper.do_amazing_things()
        # ...

