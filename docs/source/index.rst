Welcome to crawlster's documentation!
=====================================

.. include:: ../../README.rst

Helpers
-------

A helper is a utility class that provides certain functionality. The ``Crawlster``
class requires the ``.log``, ``.stats``, ``.http`` and ``.queue`` helpers
to be provided (and are by default) for internal behaviour. These are called
*core helpers*

Also, besides the core helpers, the ``Crawlster`` class also provides the ``.urls``,
``.extract`` and ``.regex`` helpers for common tasks.

You can also create other helpers and attach them to the crawler to enhance it.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial
   howto/index
   modules/index
   contributing

.. include:: ../../changelog.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
