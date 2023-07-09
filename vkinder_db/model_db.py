import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class History(Base):
    __tablename__ = 'history'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Text, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))

class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_vk_id = sq.Column(sq.Integer, nullable=False)
    first_name = sq.Column(sq.Text, nullable=False)
    last_name = sq.Column(sq.Text, nullable=False)
    city = sq.Column(sq.Text, nullable=False)
    gender = sq.Column(sq.Text, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    offset = sq.Column(sq.Integer, nullable=False)
    history_conn = relationship(History, backref='history')

class Favourites(Base):
    __tablename__ = 'favourites'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.Text, nullable=False)
    last_name = sq.Column(sq.Text, nullable=False)
    vk_link = sq.Column(sq.Text, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))
    favourites_conn = relationship(User, backref='user')

class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    photo_link = sq.Column(sq.Text, nullable=False)
    fav_id = sq.Column(sq.Integer, sq.ForeignKey('favourites.id'))
    photo_conn = relationship(Favourites, backref='favourites')


def create_tables(engine):
    Base.metadata.create_all(engine)