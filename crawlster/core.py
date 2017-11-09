import datetime
import queue
import threading

import time

from crawlster.config import ConfigurationError
from crawlster.handlers.stream import StreamItemHandler
from crawlster.helpers.extract import ExtractHelper
from crawlster.helpers.log import LoggingHelper
from crawlster.helpers import UrlsHelper, RegexHelper
from crawlster.exceptions import get_full_error_msg
from crawlster.helpers.queue import QueueHelper
from crawlster.helpers.request import RequestsHelper
from crawlster.helpers.stats import StatsHelper


class Job(object):
    TYPE_FUNC = 'func'
    TYPE_EXIT = 'exit'

    def __init__(self, type, func, args, kwargs):
        self.type = type
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        if self.type == self.TYPE_FUNC:
            msg = "Job(type={type}, func={func}, args={args}, kwargs={kwargs}"
            return msg.format(type=self.type, func=self.func.__name__,
                              args=self.args, kwargs=self.kwargs)
        elif self.type == self.TYPE_EXIT:
            return "Job(type={type})".format(type=self.type)


class Crawlster(object):
    """Base class for web crawlers

    Any crawler must subclass this and provide a valid Configuration object
    as the config class attribute.

    """
    # constants
    HELPER_FLAG = 'is_helper'
    # stats
    STAT_ITEMS = 'items'
    STAT_ERRORS = 'errors'
    STAT_START_TIME = 'time.start'
    STAT_FINISH_TIME = 'time.finish'
    STAT_DURATION = 'time.duration'

    # the configuration object
    config = None

    # Helpers
    # =======
    # we directly attach them because we want the nice auto complete
    # features of IDEs

    # Core helpers. They must always be provided
    stats = StatsHelper()
    log = LoggingHelper()
    http = RequestsHelper()
    queue = QueueHelper(strategy='lifo')
    # Various utility helpers
    urls = UrlsHelper()
    regex = RegexHelper()
    extract = ExtractHelper()

    # a single item handler or a list/tuple of them
    item_handler = StreamItemHandler()

    def __init__(self):
        """Initializes the crawler"""
        if self.config is None:
            raise ConfigurationError(get_full_error_msg('missing_config'))

        self.pool = None
        self.inject_helpers()
        self.inject_handlers()
        self.log.info('Initializing context')
        self.init_context()
        self.log.info('Context initialized')

    def inject_helpers(self):
        """Injects and initializes all the known helpers"""
        for helper in self.iter_helpers():
            self.inject_config_and_crawler(helper)

    def inject_handlers(self):
        """Injects and initializes all the known item handlers"""
        for handler in self.iter_item_handlers():
            self.inject_config_and_crawler(handler)

    def iter_helpers(self):
        """Iterates through all the item handlers"""
        for attrname in dir(self):
            attr_obj = getattr(self, attrname)
            if hasattr(attr_obj, self.HELPER_FLAG) and \
                    getattr(attr_obj, self.HELPER_FLAG):
                yield attr_obj

    def iter_item_handlers(self):
        """Iterates through all the known item handlers"""
        if isinstance(self.item_handler, (list, tuple)):
            for handler in self.item_handler:
                yield handler
        else:
            yield self.item_handler

    def inject_config_and_crawler(self, to_be_injected):
        """Injects the config instance and crawler instance into the object

        The crawler instance will be accessible through the .crawler attribute,
        the config instance will be accessible through the .config attribute.
        After injection, the .initialize() is called to perform the init
        actions.

        Args:
            to_be_injected (object which has initialize()):
                An object in which will be injected the config and crawler
                attributes. Must have an .initialize() method
        """
        to_be_injected.config = self.config
        to_be_injected.crawler = self
        to_be_injected.initialize()

    def init_context(self):
        """Initializes the crawler context (the queue and the worker pool)"""
        # prepare queue
        self.pool = self.get_pool()

    def get_pool(self):
        """Creates and returns the worker pool"""
        workers = self.config.get('pool.workers')
        pool = []
        for _ in range(workers):
            pool.append(threading.Thread(target=self.worker))
        return pool

    def start(self):
        """Starts crawling based on the config"""
        start_func_name = self.config.get('core.start_step')
        self.stats.set(self.STAT_START_TIME, datetime.datetime.now())
        func = getattr(self, start_func_name, None)
        if not func:
            raise ConfigurationError(
                'Could not find start step: {}'.format(start_func_name))
        start_urls = self.config.get('core.start_urls')
        # putting initial processing jobs into queue
        for start_url in start_urls:
            self.queue.put(Job(Job.TYPE_FUNC, func, (start_url,), {}))
        # start workers
        for worker_thread in self.pool:
            worker_thread.start()
        self.queue.join()
        self.log.info('Finished')
        self.log.debug('Signaling workers to stop')
        for _ in range(len(self.pool)):
            self.queue.put(Job(Job.TYPE_EXIT, None, None, None))
        # updating stats
        finish = datetime.datetime.now()
        self.stats.set(self.STAT_FINISH_TIME, finish)
        start = self.stats.get(self.STAT_START_TIME)
        duration = (finish - start).total_seconds()
        self.stats.set(self.STAT_DURATION, duration)
        self.finalize()

    def worker(self):
        """Worker body that executes the jobs"""
        work_queue = self.queue
        while True:
            try:
                job = work_queue.get_nowait()
            except queue.Empty:
                job = None
            if not job:
                time.sleep(0.2)
                continue
            self.log.debug('Got job: {}'.format(job))
            if job.type == Job.TYPE_EXIT:
                self.log.info('Received exit notification. Worker is exiting')
                work_queue.task_done()
                return
            self.process_job(job)
            work_queue.task_done()

    def process_job(self, job):
        """Processes a single job and enqueues the results"""
        self.log.debug('Processing job: {}'.format(job))
        try:
            next_item = job.func(*job.args, **job.kwargs)
        except Exception as e:
            self.log.error(str(e))
            self.stats.add(self.STAT_ERRORS, {
                'func': job.func.__name__,
                'args': job.args,
                'kwargs': job.kwargs,
                'exception': e
            })
            return
        if not next_item:
            return
        if isinstance(next_item, dict):
            # is an item/result
            self.submit_item(next_item)
        elif isinstance(next_item, Job):
            # is a job instance, must be further processes
            self.queue.put(next_item)
        elif isinstance(next_item, tuple):
            # is a tuple of callable, args, kwargs
            self.queue.put(self.make_job_from_item(next_item))

    def make_job_from_item(self, next_item):
        """Wraps returned item from job into a Job object"""
        return Job(Job.TYPE_FUNC, next_item[0], next_item[1], next_item[2])

    def schedule(self, func, *args, **kwargs):
        """Schedules the next tep to be executed by workers"""
        job = self.make_job_from_item((func, args, kwargs))
        self.queue.put(job)

    def submit_item(self, item):
        """Submit an item to be handled by the item handlers

        Args:
            item (dict):
                The item that has to be processed
        """
        self.log.debug('Submitted item {}'.format(item))
        self.stats.incr(self.STAT_ITEMS)
        if isinstance(self.item_handler, (list, tuple)):
            for handler in self.item_handler:
                handler.handle(item)
        else:
            self.item_handler.handle(item)

    def finalize(self):
        """Performs the finalize action on all item handlers and helpers"""
        for handler in self.iter_item_handlers():
            handler.finalize()
        for helper in self.iter_helpers():
            helper.finalize()
