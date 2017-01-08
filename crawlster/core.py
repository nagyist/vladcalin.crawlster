from multiprocessing.pool import ThreadPool
import re
import queue
import threading
import time

import requests
import bs4

from crawlster.util import get_logger

DEFAULT_LOGGER = get_logger("default")


class Crawlster(object):
    start_steps = []  # a list of tuples (url, handler)
    worker_threads = 1

    logger = DEFAULT_LOGGER

    def __init__(self):
        self.queue = queue.Queue()
        self.worker_is_busy = [threading.Event() for _ in range(self.worker_threads)]
        self.worker_pool = self.get_worker_pool()

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
        self.logger.debug("Scheduling {} with {} and {}".format(step_func.__name__, args, kwargs))
        self.queue.put((step_func, args, kwargs))

    def worker_main(self, job_queue, is_busy):
        self.logger.debug("Started worker with TID={}".format(threading.get_ident()))
        while True:
            is_busy.clear()

            try:
                func, args, kwargs = job_queue.get(block=False, timeout=0.5)
            except queue.Empty:
                continue

            is_busy.set()
            self.logger.info("Processing {} with {} and {}".format(func.__name__, args, kwargs))
            try:
                self.process_job(func, args, kwargs)
            except Exception as e:
                self.logger.error("[x] Job raised exception: {}".format(e))

    def process_job(self, func, args, kwargs):
        func(*args, **kwargs)

    def is_running(self):
        all_workers_idle = [not flag.is_set() for flag in self.worker_is_busy]
        return self.queue.empty() and all(all_workers_idle)

    def start(self):
        self.start_workers()
        self.schedule_start_steps()
        while self.is_running():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                pass

    def urlget(self, url, method="get", **kwargs):
        method = getattr(self.http_session, method)
        return method(url, **kwargs)

    def parse_html(self, content):
        return bs4.BeautifulSoup(content, "html.parser")
