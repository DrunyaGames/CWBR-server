

class BaseError(Exception):
    message = 'Base error'
    code = '000'

    def __init__(self, message=None, code=None):
        self.message = message if message else self.message
        self.code = code if code else self.code


class BadRequest(BaseError):
    message = 'Bad request'
    code = '001'


class UnhandledRequest(BaseError):
    message = 'Unhandled Request'
    code = '002'
