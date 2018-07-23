from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message
from models import User, Cat, session
from game import Game
from errors import *

server = ServerFactory()

users = []


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
@server.handle('mine_new_cat')
def find_cat(mode: str):
    game.user_wait(protocol.user, mode)


@check_rights(1)
@server.handle('change_cat_name')
def change_name(name: str, cat_id):
    if 15 > len(name) > 1:
        cat = session.query(Cat).filter_by(id=cat_id).first()
        cat.name = name
        session.commit()


@check_rights(5)
@server.handle('add_cat')
def add_cat(power: int, color=None, name=None):
    protocol.user.add_cat(Cat(power=power, color=color, name=name))


if __name__ == '__main__':
    game = Game()
    server.run()
