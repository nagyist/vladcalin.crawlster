Submitting results
==================

Submitting results is done via the :py:meth:`crawlster.Crawlster.submit_item`
method. The single argument must be a :py:class:`dict` that represents the item.

After being submitted, the item will be passed through all the defined item
handlers.

.. seealso::

   The module reference for :py:mod:`crawlster.handlers` for more details and
   all the available item handler classes.
