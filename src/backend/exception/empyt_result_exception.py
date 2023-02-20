# thanks to https://stackoverflow.com/a/1319675 and https://stackoverflow.com/a/10270732 for providing an example of
# how to create custom exceptions

# The exception that will be thrown if a database request does not return anything
class EmptyResultException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.errorCode = error_code
        super(EmptyResultException, self).__init__(message)
