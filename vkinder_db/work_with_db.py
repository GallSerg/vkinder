import os
import sqlalchemy as sq
from model_db import create_tables
from dotenv.main import load_dotenv
from sqlalchemy.orm import sessionmaker
from model_db import History, User, Photo, Favourites

def connect_db():
    load_dotenv()
    password = os.environ['db_pass']
    DSN = f'postgresql://postgres:{password}@localhost:5432/vkinder'
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, engine

class Database():

    def history(self):
        query = session.query(History.vk_id).select_from(History)
        return [i[0] for i in query]

if __name__ == '__main__':

    session, engine = connect_db()

    create_tables(engine)

    test = Database()

    print(test.history())