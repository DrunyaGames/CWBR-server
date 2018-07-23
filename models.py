from itsdangerous import JSONWebSignatureSerializer, BadSignature
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, create_engine
from easy_tcp.server import protocol
from tools import random_hex
from config import secret_key
from errors import AuthError
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

    def __init__(cls, proto=None, game=None, **kwargs):
        super().__init__(**kwargs)
        cls.proto = proto
        cls.game = game
        cls.send = proto.send if proto else None

    def init(cls, proto: protocol, game):
        cls.proto = proto
        cls.game = game
        cls.send = proto.send

    @classmethod
    def from_session(mcs, sign):
        try:
            json = serializer.loads(sign)
        except BadSignature:
            raise AuthError
        return session.query(mcs).filter_by(id=json['user_id']).first()

    def add_cat(cls, cat):
        cls.cats.append(cat)
        session.add(cat)
        session.commit()

    # noinspection PyTypeChecker
    def dump(cls):
        dump = dict(user_id=cls.id, name=cls.name, rights=cls.rights)
        dump['session'] = serializer.dumps(dump).decode()
        dump['cats'] = [cat.dump() for cat in cls.cats]
        return dump

    def __repr__(self):
        return '<User: name=%s id=%s>' % (self.name, self.id)


class Cat(Base):
    __tablename__ = 'cat'

    id = Column(Integer, primary_key=True, autoincrement=True)
    power = Column(Integer, nullable=False)
    name = Column(String)
    color = Column(String)
    tum = Column(Boolean, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="cats")

    # noinspection PyArgumentList
    def __init__(cls, **kwargs):
        super().__init__(**kwargs)
        cls.color = random_hex() if not cls.color else kwargs['color']
        cls.name = random.choice(names) if not cls.name else cls.name

    def dump(cls):
        return {
            'id': cls.id,
            'name': cls.name,
            'color': cls.color,
            'power': cls.power,
            'tum': cls.tum,
            'owner_id': cls.owner_id
        }

    def __repr__(self):
        return '<Cat: color=%s power=%s' % (self.color, self.power)


class Item(Base):
    __tablename__ = 'items'

    unique_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="inventory")

    __mapper_args__ = {'polymorphic_on': id}


class Chest(Item):

    item_id = '1'

    __mapper_args__ = {'polymorphic_identity': item_id}


if __name__ == '__main__':
    pass
    Base.metadata.create_all(engine)
    session.commit()

    # user = User(name='admin', password='1234', inventory=[
    #     Chest()
    # ])
    # session.add(user)
    # session.commit()
