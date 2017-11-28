Configuration
=============

Configuration is managed via the ``config`` attribute of the crawler class.

The following configuration methods are available:

- :py:class:`crawlster.config.Configuration` - the most basic configuration where you
  specify the configuration directly into your crawler
- :py:class:`crawlster.config.JsonConfiguration` - manage configuration from a JSON file.


Configuration keys
------------------

Configuration keys are populated from all helpers when the crawling starts.

The following configuration keys are the default:

- ``core.start_step`` - the name of the method where the crawling process
  starts. Defaults to ``start_step``.
- ``core.start_urls`` - a list of urls that will be firstly processed in the
  start step.
- ``core.workers`` - the number of worker threads to be used. Defaults to
  the number of CPU core.

Each helper defines some extra configuration options, usually under the name
``helper_name.option_name``.

Examples
--------

The basic configuration:

::

    config = Configuration({
        'core.start_step': 'my_custom_step',
        'core.workers': 10,
        'core.start_urls': ['http://example.com', 'http://example2.com']
    })

Json configuration:

::

    config = JsonConfiguration('config.json')

    # config.json

    {
        "core.start_step": "my_custom_step",
        "core.workers": 10,
        "core.start_urls": ["http://example.com", "http://example2.com"]
    }
