

class BaseError(Exception):
    message = 'Base error'
    code = '000'


class BadRequest(BaseError):
    message = 'Bad request'
    code = '001'


class AuthError(BaseError):
    message = 'Authentication required'
    code = '002'


class BadLogin(AuthError):
    message = 'Bad login or password'
    code = '003'


class RegError(BaseError):
    message = 'Name already registered'
    code = '004'


class PermissionsError(BaseError):
    message = 'Not enough rights'
    code = '005'
