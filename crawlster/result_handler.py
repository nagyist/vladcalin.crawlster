import json
import threading
import abc


class ResultHandler(abc.ABC):
    """
    The base class for result handlers
    """

    @abc.abstractmethod
    def can_handle(self, result):
        """
        Verifies whether it can handle the data

        :param result: a dict with the result
        :return: boolean
        """
        pass

    @abc.abstractmethod
    def save_result(self, result):
        """
        Handles the specific result.

        :param result: a dict with the result
        :return:
        """
        pass


class JsonLinesHandler(ResultHandler):
    def __init__(self, filename):
        """
        Writes the results to a file as json structures, one json per line.

        :param filename: the json filename
        """
        self.filename = filename
        self.file_lock = threading.Lock()

    def save_result(self, result):
        with self.file_lock:
            with open(self.filename, "a") as f:
                f.write(json.dumps(result, default=lambda x: str(x)))
                f.write("\n")

    def can_handle(self, result):
        return True
