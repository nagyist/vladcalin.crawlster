from queue import Queue, LifoQueue
from .base import BaseHelper


class QueueHelper(BaseHelper):
    def __init__(self, strategy='fifo'):
        super(QueueHelper, self).__init__()
        if strategy == 'fifo':
            self.queue = Queue()
        elif strategy == 'lifo':
            self.queue = LifoQueue()

    def put(self, item):
        self.queue.put(item)

    def get(self):
        return self.queue.get()

    def get_nowait(self):
        return self.queue.get_nowait()

    def join(self):
        self.queue.join()

    def task_done(self):
        self.queue.task_done()
