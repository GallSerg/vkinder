import os
import sqlalchemy as sq
from dotenv.main import load_dotenv
from sqlalchemy.orm import sessionmaker
from vkinder_db.model_db import History, User, Photo, Favourites


def connect_db():
    """ Connecting to the database. """
    load_dotenv()
    password = os.environ['db_pass']
    DSN = f'postgresql://postgres:{password}@localhost:5432/vkinder'
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, engine


class Database:

    def __init__(self, session):
        self.session = session

    def user_id(self, user_vk_id):
        """
        Accepts the user's page id and returns its ID in the database.
        """

        query = self.session.query(User.id).filter(User.user_vk_id == user_vk_id)

        return int([i for i in query][0][0])

    def check_user(self, user_vk_id):
        """
        Checking for the uniqueness of the user by the page id.
        Accepts the page id, returns True or False.
        """

        query = self.session.query(User.user_vk_id)

        return user_vk_id in [i[0] for i in query]

    def add_user(self, user_vk_id, first_name, last_name, city, age, gender):
        """
        Accepts user_vk_id, first_name, last_name, city, age,
        gender and adds to the database.
        """

        if not self.check_user(user_vk_id):
            new_user = User(
                user_vk_id=user_vk_id, first_name=first_name,
                last_name=last_name, city=city, age=age,
                gender=gender, offset=0)
            self.session.add(new_user)
            self.session.commit()

    def offset(self, user_vk_id):
        """
        Offset by user search.
        """
        query = self.session.query(User.offset).filter(
            User.user_vk_id == user_vk_id)
        return [item[0] for item in query][0]

    def update_offset(self, user_vk_id):
        """
        Updating the user search offset.
        """
        self.session.query(User).filter(User.user_vk_id == user_vk_id).update(
            {User.offset: User.offset + 1})
        self.session.commit()

    def check_history(self, user_vk_id, vk_id):
        """
        Accepts the user's page id and returns a list of viewed pages
        from the database.
        """

        id = self.user_id(user_vk_id)
        query = self.session.query(History.vk_id).filter(History.user_id == id)

        return vk_id in [i[0] for i in query]


    def last_histoty(self, user_vk_id):
        """
        Show the last entry from the user's history.
        """

        id = self.user_id(user_vk_id)
        query = self.session.query(History.vk_id).filter(History.user_id == id)

        return [vk_id[0] for vk_id in query][-1]


    def add_history(self, user_vk_id, vk_id):
        """
        Accepts the user's page id and the id of the viewed page,
        adds an entry to the browsing history.
        """

        id = self.user_id(user_vk_id)
        self.session.add(History(user_id=id, vk_id=vk_id))
        self.session.commit()


    def check_favourites(self, user_vk_id, vk_link):
        """
        Checking for a link in favorites. Accepts a link to the page of the
        viewed person and the user's page id. Returns True or False.
        """

        id = self.user_id(user_vk_id)
        query = self.session.query(
            Favourites.vk_link).filter(Favourites.user_id == id)

        return vk_link in [i[0] for i in query]


    def add_favourites(
            self, user_vk_id, first_name, last_name, vk_link, photo_list):
        """
        Accepts data about the viewed person (first_name, last_name,
        vk_link and a list of links to photos) and adds it to the database.
        """

        if not self.check_favourites(user_vk_id, vk_link):
            id = self.user_id(user_vk_id)
            new_favourites = Favourites(
                first_name=first_name, last_name=last_name,
                vk_link=vk_link, user_id=id)

            self.session.add(new_favourites)
            self.session.commit()
            fav_id = new_favourites.id

            for item in photo_list:
                self.session.add(Photo(fav_id=fav_id, photo_link=item))
                self.session.commit()


    def show_favourites(self, user_vk_id):
        """
        The output of favorites by the user's page id. Return a list
        with basic information and a list with links to photos.
        """

        user_id = self.user_id(user_vk_id)

        query_info = self.session.query(
            Favourites.id,
            Favourites.first_name,
            Favourites.last_name,
            Favourites.vk_link).filter(Favourites.user_id == user_id)

        favourites_list = [item for item in query_info]

        fav_ids = [elem[0] for elem in favourites_list]

        photo_list = []
        for id in fav_ids:
            query_photo = self.session.query(
                Photo.photo_link).filter(Photo.fav_id == id)
            photo_list.append([item[0] for item in query_photo])

        return favourites_list, photo_list


