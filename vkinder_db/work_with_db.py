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

    # Проверка на уникальность юзера
    def uniq_user(self, user_vk_id):
        query = session.query(User.user_vk_id).filter(
            User.user_vk_id == user_vk_id)
        return len([i[0] for i in query]) == 0

    # Добавление нового юзера и возврат его идентификатора
    def add_user(self, user_vk_id, first_name, last_name, city, age, gender):
        if self.uniq_user(user_vk_id):
            new_user = User(user_vk_id=user_vk_id, first_name=first_name,
                            last_name=last_name, city=city, age=age,
                            gender=gender)
            session.add(new_user)
            session.commit()

            return new_user.id


    # Получение истории просмотров:
    def history(self):
        query = session.query(History.vk_id).select_from(History)
        return [i[0] for i in query]

    # добавление в историю просмотров,
    def add_history(self, user_id, vk_id):
        session.add(History(user_id=user_id, vk_id=vk_id))
        session.commit()

    # добавление в избранное и возврат идентификатора
    def add_favourites(self, first_name, last_name, vk_link, user_id):
        new_favourites = Favourites(first_name=first_name, last_name=last_name,
                                    vk_link=vk_link, user_id=user_id)
        session.add(new_favourites)
        session.commit()
        return new_favourites.id

    # Добавление ссылок на фото в отдельную таблицу
    def add_photo(self, fav_id, photo_list: list):
        for item in photo_list:
            session.add(Photo(fav_id=fav_id, photo_link=item))
            session.commit()

if __name__ == '__main__':

    session, engine = connect_db()

    create_tables(engine)

    test = Database()
