from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from errors import *
import json


engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Message:

    def __init__(self, message_type: str, data=None):
        self.type = message_type
        self.data = data if data else {}

    @classmethod
    def from_json(cls, message: bytes):
        try:
            message_dict = json.loads(message.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise BadRequest
        message_type = message_dict.get('type')
        if not message_type:
            raise BadRequest
        return cls(message_type, message_dict.get('data'))

    def dump(self):
        return json.dumps({
            'type': self.type,
            'data': self.data
        })


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, default=0)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    rights = Column(Integer, default=1)
    cats = relationship('Cat', back_populates='owner')

    def __init__(cls, proto=None, **kwargs):
        super().__init__(**kwargs)
        cls.proto = proto
        cls.send = proto.send


class Cat(Base):
    __tablename__ = 'cat'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="cats")
