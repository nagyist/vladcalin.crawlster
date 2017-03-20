from multiprocessing.pool import ThreadPool
import urllib.parse
import re
import queue
import threading
import time
import traceback
import os

import requests
import bs4

from crawlster.util import get_logger

DEFAULT_LOGGER = get_logger("default")


class Crawlster(object):
    start_steps = []  # a list of tuples (url, handler)
    worker_threads = os.cpu_count()
    result_handlers = []

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
                 "(KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

    logger = DEFAULT_LOGGER

    def __init__(self):
        self.queue = queue.Queue()
        self.worker_is_busy = [threading.Event() for _ in range(self.worker_threads)]
        self.worker_pool = self.get_worker_pool()
        self._regex_cache = {}

        self._result_count = 0
        self._start_time = time.time()
        self._finish_time = None
        self._is_running = False

        # available utility attributes
        self.http_session = requests.session()

    def start(self):
        self._is_running = True
        self.start_workers()
        self.schedule_start_steps()
        self.queue.join()
        self._finish_time = time.time()
        self._is_running = False

    def schedule(self, step_func, *args, **kwargs):
        self.queue.put((step_func, args, kwargs))

    def submit_result(self, **kwargs):
        self.logger.warning("Got result: {}".format(kwargs))
        for result_handler in self.result_handlers:
            if result_handler.can_handle(kwargs):
                result_handler.save_result(kwargs)
            self._result_count += 1

    def urlget(self, url, method="get", **kwargs):
        # handle headers
        headers = {
            "User-Agent": self.user_agent
        }
        for k, v in kwargs.pop("headers", {}).items():
            headers[k] = v

        # get callable
        method = getattr(self.http_session, method)
        return method(url, headers=headers, **kwargs)

    def regex_search(self, pattern, text, flags=0):
        compiled = self._get_cached_regex(flags, pattern)
        return compiled.search(text)

    def regex_split(self, pattern, text, flags=0):
        compiled = self._get_cached_regex(flags, pattern)
        return compiled.split(text)

    def regex_findall(self, pattern, text, flags=0):
        compiled = self._get_cached_regex(flags, pattern)
        return compiled.findall(text)

    def parse_html(self, content):
        return bs4.BeautifulSoup(content, "html.parser")

    def urljoin(self, root, to_join):
        return urllib.parse.urljoin(root, to_join)

    def get_parsed_content(self, url, method="get", body=None):
        data = self.urlget(url, method=method, data=body)
        return self.parse_html(data.text)

    @property
    def result_count(self):
        return self._result_count

    @property
    def is_running(self):
        return self._is_running

    @property
    def run_time(self):
        if self.is_running:
            raise RuntimeError("Still running")
        return self._finish_time - self._start_time

    def get_worker_pool(self):
        return [
            threading.Thread(target=self.worker_main,
                             kwargs={"job_queue": self.queue}) for _ in range(self.worker_threads)]

    def start_workers(self):
        self.logger.debug("Starting workers")
        for worker in self.worker_pool:
            worker.daemon = True
            worker.start()

    def schedule_start_steps(self):
        for url, handler_name in self.start_steps:
            self.schedule(getattr(self, handler_name), url)

    def worker_main(self, job_queue):
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

    def _get_cached_regex(self, flags, pattern):
        pattern_key = "{}${}".format(pattern, flags)
        if pattern_key not in self._regex_cache:
            compiled = re.compile(pattern, flags=flags)
            self._regex_cache[pattern_key] = compiled
        else:
            compiled = self._regex_cache[pattern_key]
        return compiled
