import abc


class ResultHandler(abc.ABC):
    fields = {}

    def handle_values(self, **kwargs):
        values = {}
        for key, value in kwargs.items():
            try:
                casted_value = self.fields[key](value)
            except Exception as e:
                print(e)
                return False
            else:
                values[key] = casted_value
        self.save_result(**values)
        return True

    @abc.abstractmethod
    def save_result(self, **values):
        pass
