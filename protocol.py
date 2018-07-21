from easy_tcp.server import ServerFactory, protocol
from easy_tcp.models import Message
from models import User, session
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
    user.proto = protocol
    protocol.user = user
    protocol.send(Message('auth_ok', user.dump()))
    return user


@server.handle('reg')
def reg(name: str, password: str) -> User:
    if protocol.user:
        raise BadLogin
    _user = session.query(User).filter_by(name=name).first()
    if _user:
        raise RegError
    user = User(protocol, name=name, password=password)
    session.add(user)
    session.commit()
    protocol.user = user
    protocol.send(Message('reg_ok', user.dump()))
    return user


@check_rights(2)
@server.handle('check')
def test():
    protocol.send(Message('test'))


if __name__ == '__main__':
    server.run()
