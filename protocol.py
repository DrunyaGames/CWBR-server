from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message
from models import User, session
from game import Game
from errors import *

server = ServerFactory()


def check_rights(rights):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not protocol.user:
                raise AuthError
            if protocol.user.rights < rights:
                raise PermissionsError
            return func(*args, **kwargs)

        return wrapper

    return decorator


@server.handle('auth')
def auth(name: str, password: str) -> User:
    if protocol.user:
        raise BadLogin
    user = session.query(User).filter_by(name=name, password=password).first()
    if not user:
        raise BadLogin
    user.init(protocol, game)
    protocol.user = user
    protocol.send(Message('auth_ok', user.dump()))
    return user


@server.handle('reg')
def reg(name: str, password: str) -> User:
    if protocol.user or len(name) < 4 or len(password) < 4:
        raise BadLogin
    _user = session.query(User).filter_by(name=name).first()
    if _user:
        raise RegError
    user = User(protocol, game, name=name, password=password)
    session.add(user)
    session.commit()
    protocol.user = user
    protocol.send(Message('reg_ok', user.dump()))
    return user


@server.handle('session_auth')
def session_auth(sign: str) -> User:
    if protocol.user:
        raise BadLogin
    user = User.from_session(sign)
    protocol.user = user
    return user


@check_rights(1)
@server.handle('find_new_cat')
def find_cat(mode: str):
    game.user_wait(protocol.user, mode)


@check_rights(2)
@server.handle('check')
def test():
    protocol.send(Message('test'))


if __name__ == '__main__':
    game = Game()
    server.run()
