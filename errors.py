from easy_tcp.errors import BaseError


class AuthError(BaseError):
    message = 'Authentication required'
    code = '100'


class BadLogin(AuthError):
    message = 'Bad login or password OR You already logged in'
    code = '101'


class RegError(AuthError):
    message = 'Name already registered'
    code = '102'


class PermissionsError(BaseError):
    message = 'Not enough rights'
    code = '103'


class GameError(BaseError):
    message = ''
    code = '200'


class ModeError(GameError):
    message = 'Incorrect mode'
    code = '201'
