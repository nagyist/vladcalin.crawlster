Writing a crawler
=================

In order to write a crawler, we need to define two main componets:

- the crawler logic that is implemented by subclassing :py:class:`Crawlster`
- the item definition and handling that is implemented by subclassing :py:class:`ResultHandler`

In order to generate a crawler stub, run the command

::

    python -m crawlster crawlername [--author="My Name"]

This command will generate in the current working directory a script ``crawlername_crawler.py`` which can be used
as a starting point for our web crawler.

Basic usage
-----------




Defining the result model
-------------------------


Advanced features
-----------------
