from itsdangerous import JSONWebSignatureSerializer, BadSignature
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, create_engine
from easy_tcp.models import Message
from tools import random_hex
from config import secret_key
from errors import AuthError
from traceback import print_exc
import random

engine = create_engine('sqlite:///db.sqlite', echo=False)
serializer = JSONWebSignatureSerializer(secret_key)
Session = sessionmaker(bind=engine)
Base = declarative_base()

session = Session()

names = [
    'Барсик',
    'Пушок',
    'Порошок',
    'Гнум',
    'Снежок',
    'Коса',
    'Рефрижератор',
    'Огонёк',
    'Рыжик',
    'Чума',
    'Кот бледный',
]


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    rights = Column(Integer, default=1)
    cats = relationship('Cat', back_populates='owner')
    inventory = relationship('Item', back_populates='owner', enable_typechecks=False)
    deferred_messages = relationship('DeferredMessage', back_populates='owner')

    is_mining = Column(Boolean)

    def __init__(cls, proto=None, game=None, **kwargs):
        super().__init__(**kwargs)
        cls.proto = proto
        cls.game = game
        cls.send = proto.send if proto else None
        cls.is_mining = False

    def init(cls, proto, game):
        cls.proto = proto
        cls.game = game

    def send(cls, message):
        if not cls.proto.connected:
            return  # TODO: deferred_messages
            # return cls.deferred_messages.append(json.dumps(DeferredMessage(message.dump())))
        try:
            cls.proto.send(message)
        except:
            print_exc()

    @classmethod
    def from_session(mcs, sign):
        try:
            _json = serializer.loads(sign)
        except BadSignature:
            raise AuthError
        return session.query(mcs).filter_by(id=_json['user_id']).first()

    def add_cat(cls, cat):
        cls.cats.append(cat)
        session.add(cat)
        session.commit()

    # noinspection PyTypeChecker
    def send_deferred_messages(cls):
        for msg in cls.deferred_messages:
            cls.send(Message.from_json(msg))
        cls.deferred_messages.clear()

    # noinspection PyTypeChecker
    def dump(cls):
        dump = dict(user_id=cls.id, name=cls.name, rights=cls.rights)
        dump['session'] = serializer.dumps(dump).decode()
        dump['cats'] = [cat.dump() for cat in cls.cats]
        dump['is_mining'] = cls.is_mining
        return dump

    def __repr__(self):
        return '<User: name=%s id=%s>' % (self.name, self.id)


class Cat(Base):
    __tablename__ = 'cat'

    default_colors = [
        '#616161',
        '#ffffff',
        '#90a4ad',
        '#795547',
        '#fc9107',
        '#fef9c2',
        '#212121',
        '#ba5f28',
        '#ada2ba'
    ]

    id = Column(Integer, primary_key=True, autoincrement=True)
    power = Column(Integer, nullable=False)
    name = Column(String)
    color = Column(String)
    tum = Column(Boolean)
    tail = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="cats")

    def __init__(cls, **kwargs):
        super().__init__(**kwargs)
        cls.name = random.choice(names) if not cls.name else cls.name

        cls.tum = True if random.randint(1, 100) < 30 else False
        cls.tail = True if random.randint(1, 100) < 20 else False

        if not cls.color:
            if cls.power >= 10 and random.randint(1, 100) < 80:
                cls.color = random_hex()
            else:
                cls.color = random.choice(cls.default_colors)

    def dump(cls):
        return {
            'id': cls.id,
            'name': cls.name,
            'color': cls.color,
            'power': cls.power,
            'tum': cls.tum,
            'tail': cls.tail,
            'owner_id': cls.owner_id
        }

    def __repr__(self):
        return '<Cat: color=%s power=%s' % (self.color, self.power)


class DeferredMessage(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="deferred_messages")

    def __init__(cls, data, **kwargs):
        super().__init__(**kwargs)
        cls.data = data

    def dump(cls):
        return cls.data


class Item(Base):
    __tablename__ = 'items'

    unique_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="inventory")

    __mapper_args__ = {'polymorphic_on': id}


class LootBox(Item):
    item_id = '1'
    __mapper_args__ = {'polymorphic_identity': item_id}


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    # user = User(name='admin', password='1234', inventory=[
    #     Chest()
    # ])
    # session.add(user)
