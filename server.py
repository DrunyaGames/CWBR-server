from twisted.internet.protocol import Protocol, Factory, error
from twisted.internet.address import IPv4Address
from twisted.python import failure
from twisted.internet import reactor
from models import User, Session, Message, Base, engine
from config import *
from errors import *
import logging

session = Session()
connectionDone = failure.Failure(error.ConnectionDone())


def error_cache(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except BaseError as ex:
            self.send_error_message(ex)

    return wrapper


class UserProtocol(Protocol):

    def __init__(self, address: IPv4Address, server):
        self.address = address
        self.log = logging.getLogger(repr((address.host, address.port)))
        self.log.info('User connected')
        self.server = server

        self.user = None

    @error_cache
    def dataReceived(self, data: bytes):
        self.log.debug('Message %s' % data)
        message = Message.from_json(data)

        if message.type == 'auth':
            self.auth(message.data['name'], message.data['password'])

        if message.type == 'reg':
            self.reg(message.data['name'], message.data['password'])

    def connectionLost(self, reason=connectionDone):
        try:
            self.server.remove(self)
        except ValueError:
            pass
        self.log.info('Disconnected')

    def send_error_message(self, exception):
        self.send(Message('error', {
            'code': exception.code,
            'message': exception.message
        }))

    def send(self, data: Message):
        self.transport.write(data.dump().encode('utf-8'))

    def auth(self, name: str, password: str) -> User:
        user = session.query(User).filter_by(name=name, password=password).first()
        if not user:
            raise BadLogin
        user.proto = self
        self.user = user
        return user

    def reg(self, name: str, password: str) -> User:
        user = session.query(User).filter_by(name=name).first()
        if user:
            raise RegError
        user = User(self, name=name, password=password)
        session.add(user)
        session.commit()
        self.user = user
        return user


class ServerFactory(Factory):
    handlers = []

    def buildProtocol(self, addr: tuple) -> UserProtocol:
        proto = self.protocol(addr, self)
        self.handlers.append(proto)
        return proto


def main():
    factory = ServerFactory()
    factory.protocol = UserProtocol
    reactor.listenTCP(PORT, factory)
    log.info('Start server at %s' % PORT)
    reactor.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)-24s [LINE:%(lineno)-3s]# %(levelname)-8s [%(asctime)s]  %(message)s')
    log = logging.getLogger('GLOBAL')
    Base.metadata.create_all(engine)
    main()
