from itsdangerous import JSONWebSignatureSerializer, BadSignature
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from tools import random_hex
from config import secret_key
from errors import AuthError


engine = create_engine('sqlite:///db.sqlite', echo=False)
serializer = JSONWebSignatureSerializer(secret_key)
Session = sessionmaker(bind=engine)
Base = declarative_base()

session = Session()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    rights = Column(Integer, default=1)
    cats = relationship('Cat', back_populates='owner')

    def __init__(cls, proto=None, game=None, **kwargs):
        super().__init__(**kwargs)
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
        dump = {
            'user_id': cls.id,
            'name': cls.name,
            'rights': cls.rights,
            'cats': [cat.dump() for cat in cls.cats]
        }
        dump['session'] = serializer.dumps(dump).decode()
        return dump

    def __repr__(self):
        return '<User: name=%s id=%s>' % (self.name, self.id)


class Cat(Base):
    __tablename__ = 'cat'

    id = Column(Integer, primary_key=True, autoincrement=True, default=0)
    power = Column(Integer)
    name = Column(String)
    color = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="cats")

    # noinspection PyArgumentList
    def __init__(cls, **_):
        super().__init__()
        cls.color = random_hex()

    def dump(cls):
        return {
            'id': cls.id,
            'name': cls.name,
            'color': cls.color,
            'power': cls.power,
            'owner_id': cls.owner_id
        }


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session.commit()
