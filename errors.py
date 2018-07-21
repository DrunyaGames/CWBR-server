from easy_tcp.errors import BaseError


class AuthError(BaseError):
    message = 'Authentication required'
    code = '002'


class BadLogin(AuthError):
    message = 'Bad login or password OR You already logged in'
    code = '003'


class RegError(BaseError):
    message = 'Name already registered'
    code = '004'


class PermissionsError(BaseError):
    message = 'Not enough rights'
    code = '005'


class GameError(BaseError):
    message = ''
    code = '200'


class ModeError(GameError):
    message = 'Incorrect mode'
    code = '201'
