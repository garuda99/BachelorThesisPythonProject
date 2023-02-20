# The exception will be thrown if one DB row was expected but multiple were returned by the request
class TooLargeResultException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.errorCode = error_code
        super(TooLargeResultException, self).__init__(message)
