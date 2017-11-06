import queue
import threading

import time

from crawlster.config import ConfigurationError
from crawlster.helpers.extract import ExtractHelper
from crawlster.helpers.log import LoggingHelper
from crawlster.helpers import UrlsHelper, RegexHelper
from crawlster.exceptions import get_full_error_msg
from crawlster.helpers.request import RequestsHelper


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
    HELPER_FLAG = 'is_helper'

    config = None

    # Helpers
    # we directly attach them because we want the nice auto complete
    # features of IDEs
    urls = UrlsHelper()
    regex = RegexHelper()
    log = LoggingHelper()
    http = RequestsHelper()
    extract = ExtractHelper()

    def __init__(self):
        """Initializes the crawler"""
        if self.config is None:
            raise ConfigurationError(get_full_error_msg('missing_config'))

        self.queue = None
        self.pool = None
        self.inject_config_into_helpers()
        self.log.info('Initializing context')
        self.init_context()
        self.log.info('Context initialized')

    def inject_config_into_helpers(self):
        """Injects the current config into all helpers"""
        for attrname in dir(self):
            attr_obj = getattr(self, attrname)
            if hasattr(attr_obj, self.HELPER_FLAG) and \
                    getattr(attr_obj, self.HELPER_FLAG):
                attr_obj.config = self.config
                attr_obj.initialize()

    def init_context(self):
        """Initializes the crawler context (the queue and the worker pool)"""
        # prepare queue
        self.queue = self.get_queue()
        self.pool = self.get_pool()

    def get_queue(self):
        """Creates and returns the job queue"""
        self.log.debug('Creating the task queue')
        return queue.Queue()

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
        next_item = job.func(*job.args, **job.kwargs)
        if not next_item:
            return
        self.queue.put(self.make_job_from_item(next_item))

    def make_job_from_item(self, next_item):
        """Wraps returned item from job into a Job object"""
        return Job(Job.TYPE_FUNC, next_item[0], next_item[1], next_item[2])

    def schedule(self, func, *args, **kwargs):
        job = self.make_job_from_item((func, args, kwargs))
        self.queue.put(job)
