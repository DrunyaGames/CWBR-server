from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, String, Integer, ForeignKey, create_engine


engine = create_engine('sqlite:///db.sqlite', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


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

    # noinspection PyTypeChecker
    def dump(cls):
        return {
            'user_id': cls.id,
            'name': cls.name,
            'rights': cls.rights,
            'cats': [cat.dump() for cat in cls.cats]
        }


class Cat(Base):
    __tablename__ = 'cat'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="cats")

    def dump(cls):
        return {
            'id': cls.id,
            'owner_id': cls.owner_id
        }


if __name__ == '__main__':
    Base.metadata.create_all(engine)
