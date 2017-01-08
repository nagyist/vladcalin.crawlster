from multiprocessing.pool import ThreadPool
import re
import queue
import threading
import time
import traceback

import requests
import bs4

from crawlster.util import get_logger

DEFAULT_LOGGER = get_logger("default")


class Crawlster(object):
    start_steps = []  # a list of tuples (url, handler)
    worker_threads = 1
    result_handlers = []

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

    logger = DEFAULT_LOGGER

    def __init__(self):
        self.queue = queue.Queue()
        self.worker_is_busy = [threading.Event() for _ in range(self.worker_threads)]
        self.worker_pool = self.get_worker_pool()
        self._regex_cache = {}

        # available utility attributes
        self.http_session = requests.session()

    def get_worker_pool(self):
        return [
            threading.Thread(target=self.worker_main,
                             kwargs={"job_queue": self.queue, "is_busy": self.worker_is_busy[i]})
            for i in range(self.worker_threads)]

    def start_workers(self):
        self.logger.debug("Starting workers")
        for worker in self.worker_pool:
            worker.daemon = True
            worker.start()

    def schedule_start_steps(self):
        for url, handler_name in self.start_steps:
            self.schedule(getattr(self, handler_name), url)

    def schedule(self, step_func, *args, **kwargs):
        self.queue.put((step_func, args, kwargs))

    def worker_main(self, job_queue, is_busy):
        self.logger.debug("Started worker with TID={}".format(threading.get_ident()))
        while True:

            try:
                func, args, kwargs = job_queue.get(block=False, timeout=0.5)
            except queue.Empty:
                continue

            self.logger.info("Processing {} with {} and {}".format(func.__name__, args, kwargs))
            try:
                self.process_job(func, args, kwargs)
            except Exception as e:
                self.logger.error("[x] Job raised exception: {}".format(e))
                self.logger.error("Args: {}, Kwargs: {}".format(args, kwargs))
                self.logger.error(traceback.format_exc())
            job_queue.task_done()

    def process_job(self, func, args, kwargs):
        func(*args, **kwargs)

    def is_running(self):
        all_workers_idle = [not flag.is_set() for flag in self.worker_is_busy]
        return self.queue.empty() and all(all_workers_idle)

    def start(self):
        self.start_workers()
        self.schedule_start_steps()
        self.queue.join()

    def submit_result(self, **kwargs):
        self.logger.warning("Got result: {}".format(kwargs))
        for handler_class in self.result_handlers:
            if handler_class().handle_values(**kwargs):
                self.logger.debug("Handler {} took care of it!".format(handler_class.__name__))
            else:
                self.logger.debug("Handler {} said it can't be done".format(handler_class.__name__))

    def urlget(self, url, method="get", **kwargs):
        # handle headers
        headers = {
            "User-Agent": self.user_agent
        }
        for k, v in kwargs.pop("headers", {}):
            headers[k] = v

        # get callable
        method = getattr(self.http_session, method)
        return method(url, headers=headers, **kwargs)

    def regex_search(self, pattern, text, flags=None):
        pattern_key = "{}${}".format(pattern, flags)
        if pattern_key not in self._regex_cache:
            compiled = re.compile(pattern, flags=flags)
            self._regex_cache[pattern_key] = compiled
        else:
            compiled = self._regex_cache[pattern_key]
        return compiled.search(text)

    def parse_html(self, content):
        return bs4.BeautifulSoup(content, "html.parser")
