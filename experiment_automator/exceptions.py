class ConfigNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WorkdirDoesNotExistException(Exception):
    def __init__(self, message):
        super().__init__(message)