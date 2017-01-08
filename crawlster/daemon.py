import abc
import datetime
import time
import multiprocessing

import cronex


class RunRule(abc.ABC):
    @abc.abstractmethod
    def should_run(self, last_run):
        pass


class PeriodicRun(RunRule):
    def __init__(self, days=None, hours=None, minutes=None, seconds=None):
        self.interval = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    def should_run(self, last_run):
        if not last_run:
            return True
        now = datetime.datetime.now()
        return now - last_run >= self.interval


class CrontabRule(RunRule):
    def __init__(self, crontab_expression):
        self.crontab = cronex.CronExpression(crontab_expression)

    def should_run(self, last_run):
        return self.crontab.check_trigger(time.gmtime(time.time())[:5])


def run_crawler(crawler_class):
    crawler_class().start()

class CrawlsterDaemon(object):
    def __init__(self, processes=1):
        self._crawlers = []
        self.pool = multiprocessing.Pool(processes=processes)

    def add_crawler(self, crawler_class, rule):
        self._crawlers.append([rule, crawler_class, None])  # rule, crawler_class, last_run

    def _run_crawler(self, crawler_class):
        print("Running {}".format(crawler_class.__name__))
        crawler_class().start()

    def start(self):
        while True:
            for i in range(len(self._crawlers)):
                rule, crawler, last_run = self._crawlers[i]
                print(rule, crawler, last_run)
                if rule.should_run(last_run):
                    print("apply_async")
                    self.pool.apply_async(run_crawler, args=(crawler,))
                    self._crawlers[i][2] = datetime.datetime.now()
            print("sleeping")
            time.sleep(60)
