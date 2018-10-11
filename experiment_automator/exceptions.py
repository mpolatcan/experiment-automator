class ConfigNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)


class WorkingDirectoryDoesNotExistException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ImageUploaderException(Exception):
    def __init__(self, message):
        super().__init__(message)


class OAuthException(Exception):
    def __init__(self, message):
        super().__init__(message)