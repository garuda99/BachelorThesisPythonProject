# The exception will be thrown if the request is not valid
class ValidationException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.errorCode = error_code
        super(ValidationException, self).__init__(message)
