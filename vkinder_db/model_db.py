from dotenv.main import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

# функция подключения к базе данных vkinder
def connect_db():
    load_dotenv()
    password = os.environ['db_pass']
    DSN = f'postgresql://postgres:{password}@localhost:5432/vkinder'
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, engine


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, primary_key=True)
    firs_name = sq.Column(sq.Text, nullable=False)
    last_name = sq.Column(sq.Text, nullable=False)
    city = sq.Column(sq.Text, nullable=False)
    gender = sq.Column(sq.Text, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)

class History(Base):
    __tablename__ = 'history'

    vk_id = sq.Column(sq.Text, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'))
    user = relationship(User, backref='user')

class Favourites(Base):
    __tablename__ = 'favourites'

    fav_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.Text, nullable=False)
    last_name = sq.Column(sq.Text, nullable=False)
    vk_link = sq.Column(sq.Text, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'))
    user = relationship(User, backref='user')

class Photo(Base):
    __tablename__ = 'photo'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    photo_link = sq.Column(sq.Text, nullable=False)
    fav_id = sq.Column(sq.Integer, sq.ForeignKey('favourites.fav_id'))
    favourites = relationship(Favourites, backref='favourites')


def create_tables(engine):
    Base.metadata.create_all(engine)

if __name__ == '__main__':

    session, engine = connect_db()

    create_tables(engine)